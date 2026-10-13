"""Small reactive lattice gas: identical mobile bits, bonds and finite fuel.

The five-site reflecting line has three indistinguishable occupied sites.
Internal binary states move with particles. A bonded connected component
translates rigidly with diffusivity mobility / component size. This is a
declared coarse reaction/motion model with an implicit bath and well-mixed
fuel pool, not microscopic molecular dynamics.
"""

from itertools import combinations, product
from math import comb

import numpy as np
from scipy.linalg import expm


class SpatialBinding:
    sites = 5
    particles = 3

    def __init__(self, capacity=3, mobility=1.0, mu=4.0, assembly=0.25, thermal_bond=0.02):
        self.capacity, self.mobility, self.mu = capacity, mobility, mu
        self.parameters = {
            "capacity": capacity,
            "mobility": mobility,
            "mu": mu,
            "assembly": assembly,
            "thermal_bond": thermal_bond,
            "spin_noise": 0.05,
            "exchange": 1.0,
        }
        states = []
        for occupied in combinations(range(self.sites), self.particles):
            edges = [i for i in range(4) if i in occupied and i + 1 in occupied]
            for spins in product((0, 1), repeat=self.particles):
                cells = [-1] * self.sites
                for i, bit in zip(occupied, spins, strict=True):
                    cells[i] = bit
                for subset in range(1 << len(edges)):
                    bonds = sum(1 << edge for k, edge in enumerate(edges) if subset & (1 << k))
                    states.extend((*cells, bonds, f) for f in range(capacity + 1))
        self.states = np.array(states, dtype=int)
        self.index = {tuple(state): i for i, state in enumerate(states)}
        self.ids = np.arange(len(states))
        self.fuel = self.states[:, -1]
        self.bond_count = np.array([int(b).bit_count() for b in self.states[:, 5]])
        self.energy = mu * (self.fuel + self.bond_count)
        self.values = np.column_stack(
            (self.states[:, :5] + 1, (self.states[:, 5, None] >> np.arange(4)) & 1, self.fuel)
        )
        self.primitive_names = (
            [f"site_{i}" for i in range(5)] + [f"bond_{i}_{i + 1}" for i in range(4)] + ["fuel"]
        )
        moves = [
            (start, size, delta)
            for size in (1, 2, 3)
            for start in range(6 - size)
            for delta in (-1, 1)
            if 0 <= start + delta and start + size + delta <= 5
        ]
        self.channel_names = (
            [f"flip_{i}" for i in range(5)]
            + [f"exchange_{i}_{i + 1}" for i in range(4)]
            + [f"thermal_bond_{i}_{i + 1}" for i in range(4)]
            + [f"fuel_bond_{i}_{i + 1}" for i in range(4)]
            + [f"move_{start}_{size}_{delta}" for start, size, delta in moves]
        )
        self.rates = np.zeros((len(self.channel_names), len(states)))
        self.targets = np.tile(self.ids, (len(self.channel_names), 1))

        def put(channel, x, state, rate):
            self.targets[channel, x] = self.index[tuple(state)]
            self.rates[channel, x] = rate

        for x, state in enumerate(self.states):
            cells, bonds, f = state[:5], int(state[5]), int(state[6])
            for i in range(5):
                if cells[i] >= 0:
                    y = state.copy()
                    y[i] ^= 1
                    put(i, x, y, 0.05)
            for i in range(4):
                if min(cells[i], cells[i + 1]) < 0:
                    continue
                if cells[i] != cells[i + 1]:
                    y = state.copy()
                    y[i], y[i + 1] = cells[i + 1], cells[i]
                    put(5 + i, x, y, 1.0)
                formed = bool(bonds & (1 << i))
                y = state.copy()
                y[5] ^= 1 << i
                put(9 + i, x, y, thermal_bond * np.exp(mu * (1 if formed else -1) / 2))
                stock = capacity - f if formed else f
                if stock:
                    y[6] += 1 if formed else -1
                    put(13 + i, x, y, assembly * stock)
            for channel, (start, size, delta) in enumerate(moves, 17):
                end = start + size
                internal = sum(1 << i for i in range(start, end - 1))
                if np.any(cells[start:end] < 0) or bonds & internal != internal:
                    continue
                if (start > 0 and bonds & (1 << (start - 1))) or (
                    end < 5 and bonds & (1 << (end - 1))
                ):
                    continue
                entering = start - 1 if delta == -1 else end
                if cells[entering] >= 0:
                    continue
                y = state.copy()
                y[start:end] = -1
                y[start + delta : end + delta] = cells[start:end]
                shifted = internal >> 1 if delta == -1 else internal << 1
                y[5] = (bonds ^ internal) | shifted
                put(channel, x, y, mobility / size)
        self.q = np.zeros((len(states), len(states)))
        for rates, targets in zip(self.rates, self.targets, strict=True):
            self.q[self.ids, targets] += rates
        np.fill_diagonal(self.q, -self.q.sum(axis=1))
        self.pi = np.array([comb(capacity, int(f)) for f in self.fuel]) * np.exp(-self.energy)
        self.pi /= self.pi.sum()
        self.rewards = np.zeros((len(states), 6))
        self.reward_names = [
            "fuel_assembly",
            "fuel_disassembly",
            "thermal_assembly",
            "thermal_disassembly",
            "translation",
            "spin_exchange",
        ]
        for c in range(13, 17):
            df = self.fuel[self.targets[c]] - self.fuel
            self.rewards[:, 0] += self.rates[c] * (df < 0)
            self.rewards[:, 1] += self.rates[c] * (df > 0)
        for c in range(9, 13):
            db = self.bond_count[self.targets[c]] - self.bond_count
            self.rewards[:, 2] += self.rates[c] * (db > 0)
            self.rewards[:, 3] += self.rates[c] * (db < 0)
        self.rewards[:, 4] = self.rates[17:].sum(axis=0)
        self.rewards[:, 5] = self.rates[5:9].sum(axis=0)
        self._cache = {}

    def initial(self, kind):
        if kind == "equilibrium":
            return self.pi.copy()
        if kind not in ("dispersed", "contact_unbound", "assembled"):
            raise ValueError(kind)
        occupied = (0, 2, 4) if kind == "dispersed" else (1, 2, 3)
        bonds = 6 if kind == "assembled" else 0
        f = self.capacity - bonds.bit_count()
        p = np.zeros(len(self.ids))
        for spins in product((0, 1), repeat=3):
            cells = [-1] * 5
            for i, bit in zip(occupied, spins, strict=True):
                cells[i] = bit
            p[self.index[(*cells, bonds, f)]] = 1 / 8
        return p

    def frame_columns(self):
        # Every subset of the five sites, optionally including shared fuel.
        # Bond variables are observed when both endpoints lie in the fragment.
        # Edge-only or boundary-crossing-bond readers are outside this family.
        return {
            mask: [i for i in range(5) if mask & (1 << i)]
            + [5 + i for i in range(4) if mask & (3 << i) == (3 << i)]
            + ([9] if mask & 32 else [])
            for mask in range(64)
        }

    def evolution(self, t):
        if t < 0:
            raise ValueError("Nonnegative time required")
        if t not in self._cache:
            n = len(self.ids)
            augmented = np.zeros((n + 6, n + 6))
            augmented[:n, :n], augmented[:n, n:] = self.q, self.rewards
            result = expm(t * augmented)
            k = result[:n, :n]
            if k.min() < -1e-12 or np.max(abs(k.sum(axis=1) - 1)) > 1e-9:
                raise ValueError("Invalid numerical kernel; no clipping")
            self._cache[t] = k, result[:n, n:]
        return self._cache[t]

    def snapshot(self, p):
        positive = p > 0
        return {
            "fuel_mean": float(p @ self.fuel),
            "bonds_mean": float(p @ self.bond_count),
            "stored_energy": float(p @ self.energy),
            "free_energy_nats": float(
                np.sum(p[positive] * np.log(p[positive] / self.pi[positive]))
            ),
            "activity": float(p @ self.rates.sum(axis=0)),
            "occupied_sites": (p @ (self.states[:, :5] >= 0)).tolist(),
        }
