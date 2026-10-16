"""Finite fuel, assembled coupling and reversible local reactions.

State = (S,R,D,G,F); fuel plus spent fuel equals capacity. G is the physical
assembly state of the R->D coupling. The heat bath remains an implicit
temperature reservoir; this is not a closed microscopic quantum model.
"""

from math import comb

import numpy as np
from scipy.linalg import expm

from omega_v2.finite.local_flow import mutual


class FuelFlow:
    channel_names = (
        "thermal_S",
        "thermal_R",
        "thermal_D",
        "thermal_G",
        "copy_SR",
        "copy_RD",
        "assembly_G",
    )

    def __init__(self, capacity, assembly=1.0, damage=0.02, copying=0.25, mu=4.0):
        if capacity < 1 or any(v <= 0 for v in (assembly, damage, copying, mu)):
            raise ValueError("Positive finite parameters required")
        self.capacity, self.mu = capacity, mu
        self._evolution_cache, self._exhaustion_cache, self._response_cache = {}, {}, {}
        self.parameters = {
            "capacity": capacity,
            "assembly": assembly,
            "damage": damage,
            "copying": copying,
            "mu": mu,
            "source_noise": 0.1,
            "record_noise": 0.02,
        }
        self.ids = np.arange(16 * (capacity + 1))
        self.bits = (self.ids[:, None] >> np.arange(4)) & 1
        self.fuel = self.ids // 16
        self.values = np.column_stack((self.bits, self.fuel))
        self.energy = mu * (self.fuel + self.bits[:, 3])
        self.rates = np.zeros((7, len(self.ids)))
        self.targets = np.tile(self.ids, (7, 1))
        for x in self.ids:
            s, r, _d, g = self.bits[x]
            f = self.fuel[x]
            for i, rate in enumerate((0.1, 0.02, 0.02, damage)):
                self.targets[i, x] = x ^ (1 << i)
                self.rates[i, x] = rate if i < 3 else rate * np.exp(mu * (2 * g - 1) / 2)
            for channel, target, wanted, active in (
                (4, 1, s, True),
                (5, 2, r, bool(g)),
                (6, 3, 1, True),
            ):
                forward = self.bits[x, target] != wanted
                available = f if forward else capacity - f
                if active and available:
                    df = -1 if forward else 1
                    self.targets[channel, x] = (x ^ (1 << target)) + 16 * df
                    k = assembly if channel == 6 else copying
                    affinity = 0 if channel == 6 else mu * (1 if forward else -1)
                    self.rates[channel, x] = k * available * np.exp(affinity / 2)
        self.q = np.zeros((len(self.ids), len(self.ids)))
        for rate, target in zip(self.rates, self.targets, strict=True):
            self.q[self.ids, target] += rate
        np.fill_diagonal(self.q, -self.q.sum(axis=1))
        # Degeneracy of indistinguishable F/spent inventory is explicit.
        self.pi = np.array([comb(capacity, int(f)) for f in self.fuel]) * np.exp(-self.energy)
        self.pi /= self.pi.sum()
        self.frames = {}
        dimensions = (2, 2, 2, 2, capacity + 1)
        for mask in range(32):
            code, width = np.zeros(len(self.ids), dtype=int), 1
            for i, dim in enumerate(dimensions):
                if mask & (1 << i):
                    code += width * self.values[:, i]
                    width *= dim
            self.frames[mask] = np.eye(width)[code]
        self.rewards = np.zeros((len(self.ids), 4))
        for channel in (4, 5, 6):
            df = self.fuel[self.targets[channel]] - self.fuel
            offset = 2 if channel == 6 else 0
            self.rewards[:, offset] += self.rates[channel] * (df < 0)
            self.rewards[:, offset + 1] += self.rates[channel] * (df > 0)

    def initial(self, built):
        p = np.zeros(len(self.ids))
        for s in (0, 1):
            x = s * 7 + int(built) * 8 + 16 * (self.capacity - int(built))
            p[x] = 0.5
        return p

    def evolution(self, t):
        if t < 0:
            raise ValueError("Nonnegative time required")
        if t in self._evolution_cache:
            return self._evolution_cache[t]
        n = len(self.ids)
        aug = np.zeros((n + 4, n + 4))
        aug[:n, :n], aug[:n, n:] = self.q, self.rewards
        result = expm(t * aug)
        k, charges = result[:n, :n], result[:n, n:]
        if k.min() < -1e-12 or max(abs(k.sum(axis=1) - 1)) > 1e-9:
            raise ValueError("Numerical kernel error; no silent clipping")
        self._evolution_cache[t] = k, charges
        return k, charges

    def exhaustion_probability(self, t):
        # Absorption is ONLY for first hitting, not for actual continuation.
        if t < 0:
            raise ValueError("Nonnegative time required")
        if t in self._exhaustion_cache:
            return self._exhaustion_cache[t]
        killed = self.q.copy()
        killed[self.fuel == 0] = 0
        result = expm(t * killed)[:, self.fuel == 0].sum(axis=1)
        self._exhaustion_cache[t] = result
        return result

    def response_arrays(self, lag):
        if lag in self._response_cache:
            return self._response_cache[lag]
        k = self.evolution(lag)[0]
        arrays = []
        for m in self.frames.values():
            future = k @ m
            arrays.append(0.5 * abs(future[None, :, :] - future[self.targets]).sum(axis=2))
        result = np.asarray(arrays)
        self._response_cache[lag] = result
        return result

    def profiles(self, p, lag):
        k = self.evolution(lag)[0]
        flux = self.rates * p
        rate = flux.sum(axis=1)
        weights = np.divide(flux, rate[:, None], out=np.zeros_like(flux), where=rate[:, None] > 0)
        response = np.einsum("mcx,cx->mc", self.response_arrays(lag), weights)
        held = []
        for m in self.frames.values():
            joint = p[:, None] * (k @ m)
            held.append([mutual(self.frames[1 << i].T @ joint) for i in range(5)])
        return {
            "lag": lag,
            "held_bits": held,
            "reaction_response_tv": response.tolist(),
            "reaction_rates": rate.tolist(),
            "event_present": (rate > 0).tolist(),
        }

    def snapshot(self, p):
        positive = p > 0
        return {
            "fuel_mean": float(p @ self.fuel),
            "fuel_zero_probability": float(p[self.fuel == 0].sum()),
            "link_on_probability": float(p @ self.bits[:, 3]),
            "stored_energy": float(p @ self.energy),
            "nonequilibrium_free_energy_nats": float(
                np.sum(p[positive] * np.log(p[positive] / self.pi[positive]))
            ),
            "source_receiver_bits": mutual(self.frames[1].T @ (p[:, None] * self.frames[4])),
        }

    def breakdown_cut(self, p):
        flux = p * self.rates[3] * self.bits[:, 3]
        rate = float(flux.sum())
        if rate == 0:
            return {"rate": 0.0, "before": None, "after": None}
        before = flux / rate
        after = np.bincount(self.targets[3], weights=before, minlength=len(p))
        return {"rate": rate, "before": before, "after": after}
