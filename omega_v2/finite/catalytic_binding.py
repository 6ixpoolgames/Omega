"""Reversible, conformation-dependent assistance between neighboring bonds.

Four identical internal-state particles occupy five sites. An existing bond
whose endpoints have equal internal bits supplies an additional pathway for
a neighboring fuel-assisted bond reaction. Both directions receive the same
kinetic prefactor; the equilibrium law and state energies are unchanged.
"""

import numpy as np
from scipy.linalg import expm
from scipy.sparse import bmat, coo_matrix, csr_matrix
from scipy.sparse.linalg import expm_multiply

from omega_v2.finite.spatial_binding import SpatialBinding


class CatalyticBinding(SpatialBinding):
    particles = 4

    def __init__(self, barrier=1.0, mobility=1.0, capacity=3):
        if barrier < 0:
            raise ValueError("Nonnegative catalytic barrier reduction required")
        super().__init__(capacity=capacity, mobility=mobility)
        self.parameters["catalytic_barrier_reduction"] = barrier
        self.base_channels = len(self.channel_names)
        self.catalytic_pairs = [
            (edge, neighbor)
            for edge in range(4)
            for neighbor in (edge - 1, edge + 1)
            if 0 <= neighbor < 4
        ]
        added_rates, added_targets = [], []
        for edge, neighbor in self.catalytic_pairs:
            occupied = (self.states[:, edge] >= 0) & (self.states[:, edge + 1] >= 0)
            aligned = self.states[:, neighbor] == self.states[:, neighbor + 1]
            bound = (self.states[:, 5] & (1 << neighbor)) != 0
            # For one catalyst, background plus this path gives exp(barrier)
            # times the background rate. Two catalysts provide parallel paths.
            added_rates.append(
                self.rates[13 + edge] * np.expm1(barrier) * occupied * aligned * bound
            )
            added_targets.append(self.targets[13 + edge].copy())
            self.channel_names.append(f"catalytic_bond_{edge}_via_{neighbor}")
        self.rates = np.vstack((self.rates, added_rates))
        self.targets = np.vstack((self.targets, added_targets))
        self.q = np.zeros_like(self.q)
        for rates, targets in zip(self.rates, self.targets, strict=True):
            self.q[self.ids, targets] += rates
        np.fill_diagonal(self.q, -self.q.sum(axis=1))
        old = self.rewards
        self.rewards = np.zeros((len(self.ids), 8))
        self.rewards[:, :6] = old
        for c in range(self.base_channels, len(self.rates)):
            df = self.fuel[self.targets[c]] - self.fuel
            self.rewards[:, 0] += self.rates[c] * (df < 0)
            self.rewards[:, 1] += self.rates[c] * (df > 0)
            self.rewards[:, 6] += self.rates[c] * (df < 0)
            self.rewards[:, 7] += self.rates[c] * (df > 0)
        self.reward_names += ["catalytic_assembly_subset", "catalytic_disassembly_subset"]
        self._cache, self._propagation_cache, self._hit_cache = {}, {}, {}

    def initial(self, kind):
        if kind == "equilibrium":
            return self.pi.copy()
        configs = {
            "dispersed": ((0, 1, 3, 4), 0),
            "contact_unbound": ((0, 1, 2, 3), 0),
            "seeded": ((0, 1, 2, 3), 1),
            "assembled": ((0, 1, 2, 3), 7),
        }
        occupied, bonds = configs[kind]
        p = np.zeros(len(self.ids))
        for bits in range(16):
            cells = [-1] * 5
            for j, site in enumerate(occupied):
                cells[site] = (bits >> j) & 1
            p[self.index[(*cells, bonds, self.capacity - bonds.bit_count())]] = 1 / 16
        return p

    def frame_columns(self):
        frames = super().frame_columns()
        for edge in range(4):
            frames[len(frames)] = [5 + edge]
            frames[len(frames)] = [5 + edge, 9]
        frames[len(frames)] = [5, 6, 7, 8]
        frames[len(frames)] = [5, 6, 7, 8, 9]
        return frames

    def evolution(self, t):
        # Dense kernels are used only for the two response lags.
        if t < 0:
            raise ValueError("Nonnegative time required")
        if t not in self._cache:
            k = expm(t * self.q)
            if k.min() < -1e-12 or np.max(abs(k.sum(axis=1) - 1)) > 1e-9:
                raise ValueError("Invalid kernel; no clipping")
            self._cache[t] = (k, None)
        return self._cache[t]

    def advance(self, p, t):
        return expm_multiply(csr_matrix(self.q.T) * t, p)

    def charges(self, t):
        if t not in self._propagation_cache:
            n = len(self.ids)
            augmented = bmat(
                [[csr_matrix(self.q), csr_matrix(self.rewards)], [None, csr_matrix((8, 8))]],
                format="csr",
            )
            basis = np.zeros((n + 8, 8))
            basis[n:] = np.eye(8)
            self._propagation_cache[t] = expm_multiply(augmented * t, basis)[:n]
        return self._propagation_cache[t]

    def hitting(self, event, t):
        if event not in ("tetramer", "edge0"):
            raise ValueError(event)
        key = (event, t)
        if key not in self._hit_cache:
            target = self.bond_count == 3 if event == "tetramer" else (self.states[:, 5] & 1) != 0
            killed = csr_matrix(self.q * (~target[:, None]))
            self._hit_cache[key] = expm_multiply(killed * t, target.astype(float))
        return self._hit_cache[key]

    def two_stage_generator(self):
        """Diagnostic monitor: e0 assists e1, then that still-present e1 assists e2.

        A loss of e1 before the second step resets the monitor. Flag 2 means
        the sequence has happened. Marginal physical dynamics remains Q.
        This is a path observation, not a physical register or a value target.
        """
        n = len(self.ids)
        first = self.channel_names.index("catalytic_bond_1_via_0")
        second = self.channel_names.index("catalytic_bond_2_via_1")
        rows, cols, rates = [], [], []
        for flag in range(3):
            for c in range(len(self.rates)):
                x = np.flatnonzero(self.rates[c])
                y = self.targets[c, x]
                next_flag = np.full(len(x), flag)
                forward = self.fuel[y] < self.fuel[x]
                if flag == 0 and c == first:
                    next_flag[forward] = 1
                if flag == 1:
                    next_flag[(self.states[y, 5] & 2) == 0] = 0
                    if c == second:
                        next_flag[forward] = 2
                rows.extend((flag * n + x).tolist())
                cols.extend((next_flag * n + y).tolist())
                rates.extend(self.rates[c, x].tolist())
        q = coo_matrix((rates, (rows, cols)), shape=(3 * n, 3 * n)).tocsr()
        q.setdiag(-np.asarray(q.sum(axis=1)).ravel())
        return q

    def breakdown(self, p, edge=0):
        c = 9 + edge
        flux = p * self.rates[c] * ((self.states[:, 5] & (1 << edge)) != 0)
        rate = float(flux.sum())
        if rate == 0:
            raise ValueError("No native breakdowns in this law")
        before = flux / rate
        after = np.bincount(self.targets[c], weights=before, minlength=len(p))
        return {"rate": rate, "before": before, "after": after}

    def snapshot(self, p):
        result = super().snapshot(p)
        result["tetramer_probability"] = float(p[self.bond_count == 3].sum())
        result["bond_probabilities"] = (p @ self.values[:, 5:9]).tolist()
        result["catalytic_formation_rate"] = float(p @ self.rewards[:, 6])
        result["catalytic_reversal_rate"] = float(p @ self.rewards[:, 7])
        return result
