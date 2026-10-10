"""Ideal local fuel overlay for the existing reversible assembly layer.

Reservoir molecules have no excluded-volume interaction with building blocks.
Volumes, contact allocation and reversible diffusion are explicit. V=B recovers
the shared-pool concentrations under fast conditional mixing.
"""

from dataclasses import asdict, dataclass
from math import lgamma, log

import numpy as np

from omega_v2.finite.lattice_chemistry import Event, LatticeChemistry, State


@dataclass(frozen=True)
class Reservoir:
    grid: tuple[int, int] = (2, 1)
    transport: float = 1.0
    volumes: tuple[float, ...] = ()


@dataclass
class LocalState:
    positions: list[tuple[int, int]]
    internal: list[int]
    bonds: set[tuple[int, int]]
    fuels: list[int]
    wastes: list[int]

    @property
    def fuel(self):
        return sum(self.fuels)

    def copy(self):
        return LocalState(self.positions.copy(), self.internal.copy(), self.bonds.copy(),
                          self.fuels.copy(), self.wastes.copy())

    def key(self):
        return (tuple(self.positions), tuple(self.internal), tuple(sorted(self.bonds)),
                tuple(self.fuels), tuple(self.wastes))

    def record(self):
        return {"positions": self.positions, "internal": self.internal,
                "bonds": sorted(self.bonds), "fuel": self.fuel,
                "fuels": self.fuels, "wastes": self.wastes}

    def project(self):
        return State(self.positions.copy(), self.internal.copy(), self.bonds.copy(), self.fuel)


@dataclass(frozen=True)
class LocalEvent(Event):
    reservoir: tuple[int, ...] = ()
    species: str = ""


class CompartmentChemistry(LatticeChemistry):
    def __init__(self, parameters, reservoir=None):
        super().__init__(parameters)
        reservoir = Reservoir() if reservoir is None else reservoir
        nx, ny = reservoir.grid
        if (nx < 1 or ny < 1 or parameters.side % nx or parameters.side % ny
                or not np.isfinite(reservoir.transport) or reservoir.transport < 0):
            raise ValueError("Reservoir grid must tile lattice; transport finite and nonnegative")
        self.reservoir = reservoir
        self.volumes = (tuple(reservoir.volumes) if reservoir.volumes
                        else (parameters.capacity / (nx * ny),) * (nx * ny))
        if len(self.volumes) != nx * ny or any(v <= 0 or not np.isfinite(v)
                                               for v in self.volumes):
            raise ValueError("One finite positive volume per compartment required")
        self.edges = []
        for x in range(nx):
            for y in range(ny):
                for dx, dy in ((1, 0), (0, 1)):
                    if x + dx < nx and y + dy < ny:
                        self.edges.append((x * ny + y, (x + dx) * ny + y + dy))

    def compartment(self, position):
        nx, ny = self.reservoir.grid
        x, y = position
        return (x * nx // self.p.side) * ny + y * ny // self.p.side

    def lift(self, state, rng):
        probabilities = np.array(self.volumes) / sum(self.volumes)
        return LocalState(state.positions.copy(), state.internal.copy(), state.bonds.copy(),
                          rng.multinomial(state.fuel, probabilities).tolist(),
                          rng.multinomial(self.p.capacity - state.fuel, probabilities).tolist())

    def validate(self, state):
        super().validate(state)
        assert len(state.fuels) == len(state.wastes) == len(self.volumes)
        assert all(isinstance(n, (int, np.integer)) and n >= 0
                   for n in state.fuels + state.wastes)
        assert sum(state.fuels) + sum(state.wastes) == self.p.capacity

    def free_energy(self, state):
        return self.energy(state) + sum(
            lgamma(f + 1) + lgamma(w + 1) - (f + w) * log(v)
            for f, w, v in zip(state.fuels, state.wastes, self.volumes, strict=True))

    def events(self, state):
        # Reuse exactly the original reaction energy and template rules. Split
        # shared chemical propensity by the specified local concentrations.
        result = []
        for e in super().events(state):
            if e.kind not in ("fuel", "catalytic"):
                result.append(LocalEvent(**asdict(e)))
                continue
            bound = e.members in state.bonds
            counts = state.wastes if bound else state.fuels
            total = sum(counts)
            weights = {}
            for i in e.members:
                c = self.compartment(state.positions[i])
                weights[c] = weights.get(c, 0) + 0.5
            for c, weight in sorted(weights.items()):
                if counts[c]:
                    rate = e.rate * weight * counts[c] * self.p.capacity / (total*self.volumes[c])
                    result.append(LocalEvent(e.kind, e.members, rate, e.direction, e.catalyst,
                                             (c,)))
        mean_volume = sum(self.volumes) / len(self.volumes)
        for a, b in self.edges:
            for src, dst in ((a, b), (b, a)):
                for species, counts in (("F", state.fuels), ("W", state.wastes)):
                    rate = (self.reservoir.transport * mean_volume / self.volumes[src]
                            * counts[src])
                    if rate:
                        result.append(LocalEvent("hop", (), rate, reservoir=(src, dst),
                                                 species=species))
        return result

    def apply(self, state, event):
        if event.kind == "hop":
            src, dst = event.reservoir
            counts = state.fuels if event.species == "F" else state.wastes
            counts[src] -= 1
            counts[dst] += 1
        elif event.kind in ("fuel", "catalytic"):
            c, = event.reservoir
            if event.members in state.bonds:
                state.bonds.remove(event.members)
                state.wastes[c] -= 1
                state.fuels[c] += 1
            else:
                state.bonds.add(event.members)
                state.fuels[c] -= 1
                state.wastes[c] += 1
        else:
            super().apply(state, event)

    def initial(self, seed, preparation="dispersed"):
        return self.lift(super().initial(seed, preparation), np.random.default_rng(seed + 100000))

    def simulate(self, initial, seed, cuts=(0, 1, 5, 10, 20), event_limit=1_000_000):
        # The common atlas runner retains hops and complete local resource state.
        from omega_v2.finite.lattice_history_atlas import HistoryAtlas, simulate_history
        return simulate_history(HistoryAtlas(self), initial, seed, cuts, event_limit)
