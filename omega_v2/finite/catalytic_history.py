"""An observer of catalytic-production ancestry; no change to physical rates.

Marks identify a historical relation, not a new physical attribute or resource.
The original bond moves with its component, and loses its original status on
dissolution. A bond formed through a marked catalytic pathway is a descendant.
Unassisted reassembly is not assigned that ancestry. Other kinds of causal
influence (including shared-fuel effects) are outside this specific observer.
"""

from collections import deque

import numpy as np
from scipy.sparse import bmat, coo_matrix, csr_matrix, eye
from scipy.sparse.linalg import expm_multiply


class CatalyticHistory:
    def __init__(self, model, initial=None, original_edge=0):
        self.model = model
        self.physical_initial = model.initial("seeded") if initial is None else initial.copy()
        original = 1 << original_edge
        support = np.flatnonzero(self.physical_initial)
        if np.any((model.states[support, 5] & original) == 0):
            raise ValueError("The original bond must exist throughout the preparation")
        self.states, self.index = [], {}
        pending = deque()

        def intern(state):
            if state not in self.index:
                self.index[state] = len(self.states)
                self.states.append(state)
                pending.append(state)
            return self.index[state]

        initial_rows = [
            (intern((int(x), original, 0, 0)), self.physical_initial[x]) for x in support
        ]
        sources, targets, channels, rates, rewards = [], [], [], [], []
        self.active = [np.flatnonzero(model.rates[:, x]) for x in model.ids]
        while pending:
            state = pending.popleft()
            row = self.index[state]
            x, root, descendants, history = state
            reward = np.zeros(6)
            for c in self.active[x]:
                y = int(model.targets[c, x])
                rate = model.rates[c, x]
                new_root, new_desc, new_history, increments = self.step(
                    x, root, descendants, history, int(c), y
                )
                target = intern((y, new_root, new_desc, new_history))
                sources.append(row)
                targets.append(target)
                channels.append(c)
                rates.append(rate)
                reward += rate * increments
            rewards.append(reward)
        self.states = np.asarray(self.states, dtype=int)
        self.physical = self.states[:, 0]
        self.original_present = self.states[:, 1] != 0
        self.descendants_present = self.states[:, 2] != 0
        self.lineage_present = self.original_present | self.descendants_present
        self.event_sources = np.asarray(sources, dtype=np.int32)
        self.event_targets = np.asarray(targets, dtype=np.int32)
        self.event_channels = np.asarray(channels, dtype=np.int16)
        self.event_rates = np.asarray(rates)
        self.q = coo_matrix(
            (rates, (sources, targets)), shape=(len(self.states), len(self.states))
        ).tocsr()
        self.q.setdiag(-np.asarray(self.q.sum(axis=1)).ravel())
        self.initial = np.zeros(len(self.states))
        for row, weight in initial_rows:
            self.initial[row] = weight
        self.resource_rates = model.rewards[self.physical]
        self.history_rates = np.asarray(rewards)
        self.history_columns = [
            "original_assisted_formations",
            "descendant_assisted_formations",
            "original_assisted_reversals",
            "descendant_assisted_reversals",
            "original_dissolutions",
            "descendant_dissolutions",
        ]
        self._integrator = None

    def step(self, x, root, descendants, history, channel, y):
        m = self.model
        r, d, h = root, descendants, history
        counts = np.zeros(6)
        name = m.channel_names[channel]
        if name.startswith("move_"):
            _, start, size, delta = name.split("_")
            start, size, delta = int(start), int(size), int(delta)
            internal = sum(1 << e for e in range(start, start + size - 1))

            def move(mask):
                part = mask & internal
                return (mask & ~internal) | (part << 1 if delta == 1 else part >> 1)

            r, d = move(r), move(d)
        else:
            remaining = int(m.states[y, 5])
            r, d = r & remaining, d & remaining
            counts[4] = (root & ~remaining).bit_count()
            counts[5] = (descendants & ~remaining).bit_count()
            if channel >= m.base_channels:
                edge, neighbor = m.catalytic_pairs[channel - m.base_channels]
                parent_root, parent_desc = (
                    bool(root & (1 << neighbor)),
                    bool(descendants & (1 << neighbor)),
                )
                forward = m.fuel[y] < m.fuel[x]
                if forward and (parent_root or parent_desc):
                    d |= 1 << edge
                    h = max(h, 1 if parent_root else 2)
                    counts[0 if parent_root else 1] += 1
                elif not forward and (parent_root or parent_desc):
                    counts[2 if parent_root else 3] += 1
        return r, d, h, counts

    def physical_law(self, law):
        return np.bincount(self.physical, weights=law, minlength=len(self.model.ids))

    def evolve(self, law, time):
        """Return current history law and its state-occupation integral."""
        if self._integrator is None:
            n = len(self.states)
            self._integrator = bmat(
                [[self.q.T, None], [eye(n, format="csr"), csr_matrix((n, n))]], format="csr"
            )
        n = len(law)
        result = expm_multiply(self._integrator * time, np.concatenate((law, np.zeros(n))))
        return result[:n], result[n:]

    def summary(self, law, occupation):
        descendant_count = np.array([int(d).bit_count() for d in self.states[:, 2]])
        enabled_descendant_count = np.zeros(len(law))
        for edge in range(4):
            aligned = (
                self.model.states[self.physical, edge] == self.model.states[self.physical, edge + 1]
            )
            enabled_descendant_count += ((self.states[:, 2] & (1 << edge)) != 0) & aligned
        return {
            "original_survival": float(law @ self.original_present),
            "descendant_presence": float(law @ self.descendants_present),
            "descendants_after_original_loss": float(
                law @ (~self.original_present & self.descendants_present)
            ),
            "production_lineage_presence": float(law @ self.lineage_present),
            "original_bond_time": float(occupation @ self.original_present),
            "production_lineage_time": float(occupation @ self.lineage_present),
            "post_original_descendant_time": float(
                occupation @ (~self.original_present & self.descendants_present)
            ),
            "ever_descendant": float(law @ (self.states[:, 3] >= 1)),
            "ever_descendant_assisted_formation": float(law @ (self.states[:, 3] == 2)),
            "descendant_bonds_mean": float(law @ descendant_count),
            "aligned_descendant_bonds_mean": float(law @ enabled_descendant_count),
            "physical_snapshot": self.model.snapshot(self.physical_law(law)),
            "resource_profile": (occupation @ self.resource_rates).tolist(),
            "history_event_counts": (occupation @ self.history_rates).tolist(),
        }

    def lumping_error(self):
        """All histories with the same physical state must have the same future Q."""
        n, physical_n = len(self.states), len(self.model.ids)
        projection = coo_matrix(
            (np.ones(n), (np.arange(n), self.physical)), shape=(n, physical_n)
        ).tocsr()
        delta = self.q @ projection - csr_matrix(self.model.q)[self.physical]
        return float(np.max(abs(delta.data))) if delta.nnz else 0.0

    def no_descendant_formation_generator(self):
        """Killed law for the event 'a descendant catalyzes a formation'."""
        m = self.model
        src, dst = self.event_sources, self.event_targets
        selected = np.zeros(len(src), dtype=bool)
        forward = m.fuel[self.physical[dst]] < m.fuel[self.physical[src]]
        for c, (_, neighbor) in enumerate(m.catalytic_pairs, m.base_channels):
            selected |= (
                (self.event_channels == c)
                & forward
                & ((self.states[src, 2] & (1 << neighbor)) != 0)
            )
        removed = coo_matrix(
            (self.event_rates[selected], (src[selected], dst[selected])), shape=self.q.shape
        ).tocsr()
        return self.q - removed
