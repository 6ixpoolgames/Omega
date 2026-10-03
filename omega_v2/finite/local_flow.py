"""Finite local Markov dynamics and unaggregated continuation diagnostics.

Rows of Q and K are initial states; columns are successor states. Reservoir
channels remain separate for dissipation. This is a classical open-system
adapter, not a microscopic bath model or a proposed scalar lushness measure.
"""

from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm


@dataclass(frozen=True)
class Flip:
    target: int
    rate: float
    drive: float = 0.0
    parents: tuple[int, ...] = ()
    truth: int = 0
    gate: int | None = None


def entropy(p):
    p = np.asarray(p)
    positive = p[p > 0]
    return float(-np.sum(positive * np.log2(positive)))


def mutual(p):
    return entropy(p.sum(axis=0)) + entropy(p.sum(axis=1)) - entropy(p)


class LocalFlow:
    def __init__(self, n, channels, energy=None):
        self.n = n
        self.states = np.arange(1 << n)
        self.bits = (self.states[:, None] >> np.arange(n)) & 1
        self.channels = tuple(channels)
        self.energy = np.zeros(1 << n) if energy is None else np.asarray(energy, dtype=float)
        if self.energy.shape != (1 << n,) or not np.isfinite(self.energy).all():
            raise ValueError("Finite energy required for every state")
        self.rates = []
        self.q = np.zeros((1 << n, 1 << n))
        for c in self.channels:
            if c.target in c.parents or c.gate == c.target:
                raise ValueError("Target and gate predicates must not change during reverse flip")
            indices = (c.target,) + c.parents + (() if c.gate is None else (c.gate,))
            if any(i < 0 or i >= n for i in indices) or c.rate <= 0 or not np.isfinite(c.drive):
                raise ValueError("Invalid local mechanism")
            y = self.states ^ (1 << c.target)
            code = sum(self.bits[:, p] << k for k, p in enumerate(c.parents))
            desired = (c.truth >> code) & 1
            direction = np.where(self.bits[:, c.target] != desired, 1, -1)
            rate = c.rate * np.exp((c.drive * direction - self.energy[y] + self.energy) / 2)
            if c.gate is not None:
                rate *= self.bits[:, c.gate]
            self.rates.append(rate)
            self.q[self.states, y] += rate
        self.rates = np.asarray(self.rates)
        np.fill_diagonal(self.q, -self.q.sum(axis=1))
        a = self.q.T.copy()
        a[-1] = 1
        rhs = np.zeros(1 << n)
        rhs[-1] = 1
        self.pi = np.linalg.solve(a, rhs)
        if np.min(self.pi) <= 0 or abs(self.pi.sum() - 1) > 1e-9:
            raise ValueError("Stationary solution must be positive; no clipping or dropped states")
        self.frames = {}
        for mask in range(1 << n):
            indices = [i for i in range(n) if mask & (1 << i)]
            code = sum(self.bits[:, i] << j for j, i in enumerate(indices))
            code = np.broadcast_to(code, self.states.shape).astype(int)
            self.frames[mask] = np.eye(1 << len(indices))[code]

    def kernel(self, t):
        if t < 0:
            raise ValueError("Nonnegative lag required")
        k = expm(self.q * t)
        if np.min(k) < -1e-12 or np.max(abs(k.sum(axis=1) - 1)) > 1e-9:
            raise ValueError("Transition kernel failed numerical stochasticity check")
        return k

    def thermodynamics(self):
        ep = 0.0
        activity = 0.0
        for c, rate in zip(self.channels, self.rates, strict=True):
            y = self.states ^ (1 << c.target)
            f = self.pi * rate
            rev = f[y]
            selected = (f > 0) & (rev > 0)
            ep += 0.5 * np.sum((f[selected] - rev[selected]) * np.log(f[selected] / rev[selected]))
            activity += f.sum()
        return {"entropy_production_nats_per_time": float(ep), "activity_per_time": float(activity)}

    def signed_flow(self):
        """Contribution of flips in F to dI(F:F-complement)/dt, in bits/time."""
        full = (1 << self.n) - 1
        values = []
        for mask in range(1 << self.n):
            mf, mc = self.frames[mask], self.frames[full ^ mask]
            pf, pc = self.pi @ mf, self.pi @ mc
            local = np.log2(self.pi) - np.log2(mf @ pf) - np.log2(mc @ pc)
            flow = 0.0
            for c, rate in zip(self.channels, self.rates, strict=True):
                if mask & (1 << c.target):
                    y = self.states ^ (1 << c.target)
                    flow += np.dot(self.pi * rate, local[y] - local)
            values.append(float(flow))
        return values

    def profiles(self, t, preparation=None):
        """Keep storage, incremental prediction and physical-kernel response apart.

        Response pairs x with x^i. Contexts are weighted by actual stationary
        (or cut-conditioned) flux of the undriven local flip mechanism. Skipping
        that flip is a counterfactual reference, not a second sampled trajectory.
        The array is an unsigned response contrast, not a harm/goodness score.
        """
        p = self.pi if preparation is None else np.asarray(preparation, dtype=float)
        if np.min(p) < 0 or abs(p.sum() - 1) > 1e-10:
            raise ValueError("Normalized preparation required")
        k = self.kernel(t)
        full = (1 << self.n) - 1
        held, response, memory, incremental = [], [], [], []
        event_weights, event_rates = [], []
        for i in range(self.n):
            indices = [
                a
                for a, c in enumerate(self.channels)
                if c.target == i and c.drive == 0 and not c.parents and c.gate is None
            ]
            if not indices:
                raise ValueError("Response profile requires a native undriven flip at every site")
            flux = p * self.rates[indices].sum(axis=0)
            event_rates.append(float(flux.sum()))
            event_weights.append(flux / flux.sum())
        for m in self.frames.values():
            future = k @ m
            joint = p[:, None] * future
            memory.append(mutual(m.T @ joint))
            held.append([mutual(self.frames[1 << i].T @ joint) for i in range(self.n)])
            response.append(
                [
                    float(
                        np.dot(
                            event_weights[i],
                            0.5 * abs(future - future[self.states ^ (1 << i)]).sum(axis=1),
                        )
                    )
                    for i in range(self.n)
                ]
            )
        for i in range(self.n):
            rest = self.frames[full ^ (1 << i)]
            joint = p[:, None] * (k @ rest)
            # A=current site, C=current rest, B=future rest: I(A;B|C).
            incremental.append(
                entropy(p) + entropy(rest.T @ joint) - entropy(p @ rest) - entropy(joint)
            )
        return {
            "lag": t,
            "held_bits": held,
            "flip_response_tv": response,
            "memory_bits": memory,
            "incremental_bits": incremental,
            "native_flip_rate": event_rates,
        }
