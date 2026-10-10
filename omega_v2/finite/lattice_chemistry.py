"""Small reversible 2D reaction/assembly substrate, with an ideal finite fuel pool.

Particle IDs are bookkeeping only. Geometry and conformation determine rates.
See lattice_chemistry_protocol_v0.md for the physical approximations and sources.
"""

from dataclasses import asdict, dataclass
from itertools import pairwise
from math import exp, lgamma, log

import numpy as np


@dataclass(frozen=True)
class Parameters:
    side: int = 8
    particles: int = 16
    capacity: int = 16
    bond_strength: float = 2.0
    exposed_energy: float = 0.75
    fuel_energy: float = 4.0
    catalytic_barrier: float = 0.0
    diffusion: float = 1.0
    switching: float = 0.2
    thermal_binding: float = 0.2
    fuel_binding: float = 0.5
    mobility_exponent: float = 1.0

    def __post_init__(self):
        if self.side < 2 or not 1 <= self.particles <= self.side**2 or self.capacity < 1:
            raise ValueError("Invalid lattice, particle count or inventory capacity")
        if any(not np.isfinite(v) for v in asdict(self).values()):
            raise ValueError("Finite parameters required")
        if min(self.bond_strength, self.catalytic_barrier, self.diffusion,
               self.switching, self.thermal_binding, self.fuel_binding,
               self.mobility_exponent) < 0:
            raise ValueError("Nonnegative strengths and kinetic prefactors required")


@dataclass
class State:
    positions: list[tuple[int, int]]
    internal: list[int]
    bonds: set[tuple[int, int]]
    fuel: int

    def copy(self):
        return State(self.positions.copy(), self.internal.copy(), self.bonds.copy(), self.fuel)

    def key(self):
        return tuple(self.positions), tuple(self.internal), tuple(sorted(self.bonds)), self.fuel

    def record(self):
        return {"positions": self.positions, "internal": self.internal,
                "bonds": sorted(self.bonds), "fuel": self.fuel}


@dataclass(frozen=True)
class Event:
    kind: str
    members: tuple[int, ...]
    rate: float
    direction: tuple[int, int] = (0, 0)
    catalyst: tuple[int, ...] = ()

    def record(self, time):
        return [time, self.kind, self.members, self.direction, self.catalyst, self.rate]


def logistic(delta):
    """Bounded thermal rate factor f(d)/f(-d)=exp(-d), energies in kBT."""
    if delta >= 0:
        x = exp(-delta)
        return x / (1 + x)
    return 1 / (1 + exp(delta))


class LatticeChemistry:
    def __init__(self, parameters=None):
        self.p = Parameters() if parameters is None else parameters

    def initial(self, seed, preparation="dispersed"):
        rng = np.random.default_rng(seed)
        sites = [(x, y) for x in range(self.p.side) for y in range(self.p.side)]
        if preparation == "seeded":
            if self.p.particles < 4:
                raise ValueError("Seeded preparation needs four particles")
            c = (self.p.side - 2) // 2
            positions = [(c, c), (c + 1, c), (c, c + 1), (c + 1, c + 1)]
            sites = [s for s in sites if s not in positions]
        elif preparation == "dispersed":
            positions = []
        else:
            raise ValueError(preparation)
        chosen = rng.choice(len(sites), self.p.particles - len(positions), replace=False)
        positions += [sites[int(i)] for i in chosen]
        internal = rng.integers(0, 2, self.p.particles).tolist()
        bonds = set()
        if preparation == "seeded":
            internal[:4] = [1] * 4
            bonds.add((0, 1))
        return State(positions, internal, bonds, self.p.capacity)

    def validate(self, state):
        assert len(state.positions) == len(state.internal) == self.p.particles
        assert len(set(state.positions)) == self.p.particles
        assert all(0 <= x < self.p.side and 0 <= y < self.p.side for x, y in state.positions)
        assert all(s in (0, 1) for s in state.internal)
        assert 0 <= state.fuel <= self.p.capacity
        for i, j in state.bonds:
            assert 0 <= i < j < self.p.particles
            assert sum(abs(a - b) for a, b in zip(state.positions[i], state.positions[j])) == 1

    def bond_energy(self, state, i, j):
        return -self.p.bond_strength * (0.5 + 0.5 * state.internal[i] * state.internal[j])

    def energy(self, state):
        return (self.p.exposed_energy * sum(state.internal)
                + sum(self.bond_energy(state, i, j) for i, j in state.bonds)
                + self.p.fuel_energy * state.fuel)

    def free_energy(self, state):
        b, f = self.p.capacity, state.fuel
        log_multiplicity = lgamma(b + 1) - lgamma(f + 1) - lgamma(b - f + 1)
        return self.energy(state) - log_multiplicity

    def components(self, state):
        neighbors = [set() for _ in state.positions]
        for i, j in state.bonds:
            neighbors[i].add(j)
            neighbors[j].add(i)
        unseen, result = set(range(self.p.particles)), []
        while unseen:
            stack, component = [min(unseen)], []
            unseen.remove(stack[0])
            while stack:
                i = stack.pop()
                component.append(i)
                for j in sorted(neighbors[i] & unseen):
                    unseen.remove(j)
                    stack.append(j)
            result.append(tuple(sorted(component)))
        return result

    def contacts(self, state, occupied):
        result = []
        for i, (x, y) in enumerate(state.positions):
            for pos in ((x + 1, y), (x, y + 1)):
                if pos in occupied:
                    result.append(tuple(sorted((i, occupied[pos]))))
        return sorted(result)

    def catalysts(self, state, i, j, occupied):
        """Opposite active bond on a unit plaquette; unchanged by target binding."""
        xi, yi = state.positions[i]
        xj, yj = state.positions[j]
        dx, dy = xj - xi, yj - yi
        result = []
        for ox, oy in ((-dy, dx), (dy, -dx)):
            k, ell = occupied.get((xi + ox, yi + oy)), occupied.get((xj + ox, yj + oy))
            if k is None or ell is None:
                continue
            pair = tuple(sorted((k, ell)))
            if pair in state.bonds and state.internal[k] == state.internal[ell] == 1:
                result.append(pair)
        return sorted(result)

    def events(self, state):
        p = self.p
        occupied = {pos: i for i, pos in enumerate(state.positions)}
        result = []
        for i, s in enumerate(state.internal):
            delta = p.exposed_energy * (1 - 2 * s)
            for a, b in state.bonds:
                if i == a or i == b:
                    j = b if i == a else a
                    delta -= 0.5 * p.bond_strength * (1 - 2 * s) * state.internal[j]
            if p.switching:
                result.append(Event("switch", (i,), p.switching * logistic(delta)))
        for pair in self.contacts(state, occupied):
            i, j = pair
            bound = pair in state.bonds
            energy = self.bond_energy(state, i, j)
            if p.thermal_binding:
                result.append(Event("thermal", pair,
                                    p.thermal_binding * logistic(-energy if bound else energy)))
            available = p.capacity - state.fuel if bound else state.fuel
            if available and p.fuel_binding:
                delta = p.fuel_energy - energy if bound else energy - p.fuel_energy
                base = p.fuel_binding * available / p.capacity * logistic(delta)
                result.append(Event("fuel", pair, base))
                if p.catalytic_barrier:
                    for catalyst in self.catalysts(state, i, j, occupied):
                        result.append(Event("catalytic", pair,
                                            base * np.expm1(p.catalytic_barrier),
                                            catalyst=catalyst))
        for component in self.components(state):
            members = set(component)
            for direction in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                dx, dy = direction
                targets = [(state.positions[i][0] + dx, state.positions[i][1] + dy)
                           for i in component]
                allowed = all(0 <= x < p.side and 0 <= y < p.side
                              and ((x, y) not in occupied or occupied[(x, y)] in members)
                              for x, y in targets)
                if allowed and p.diffusion:
                    result.append(Event("move", component,
                                        p.diffusion / len(component)**p.mobility_exponent, direction))
        return result

    def apply(self, state, event):
        if event.kind == "move":
            dx, dy = event.direction
            for i in event.members:
                x, y = state.positions[i]
                state.positions[i] = (x + dx, y + dy)
        elif event.kind == "switch":
            state.internal[event.members[0]] ^= 1
        else:
            pair = event.members
            bound = pair in state.bonds
            if bound:
                state.bonds.remove(pair)
            else:
                state.bonds.add(pair)
            if event.kind in ("fuel", "catalytic"):
                state.fuel += 1 if bound else -1

    def snapshot(self, state):
        components = self.components(state)
        sizes = [len(c) for c in components]
        occupied = {pos: i for i, pos in enumerate(state.positions)}
        contacts = self.contacts(state, occupied)
        return {"bonds": len(state.bonds), "fuel": state.fuel,
                "exposed": sum(state.internal), "components": len(sizes),
                "largest": max(sizes), "bonded_particles": sum(n for n in sizes if n > 1),
                "cycles": len(state.bonds) - self.p.particles + len(sizes),
                "contacts": len(contacts), "energy": self.energy(state),
                "free_energy_of_state": self.free_energy(state),
                "template_opportunities": sum(len(self.catalysts(state, i, j, occupied))
                                              for i, j in contacts if (i, j) not in state.bonds)}

    def simulate(self, initial, seed, cuts=(0, 1, 5, 10, 20), event_limit=1_000_000):
        if not cuts or cuts[0] < 0 or any(a >= b for a, b in pairwise(cuts)):
            raise ValueError("Strictly increasing, nonnegative cuts required")
        self.validate(initial)
        state, rng = initial.copy(), np.random.default_rng(seed)
        counts = {key: 0 for key in ("thermal_forward", "thermal_reverse", "fuel_forward",
                                    "fuel_reverse", "catalytic_forward", "catalytic_reverse",
                                    "switch", "move")}
        logs, snapshots = [], []
        depth = {pair: 0 for pair in state.bonds}
        max_depth, time, cut = 0, 0.0, 0
        first_catalysis = None
        while cut < len(cuts):
            events = self.events(state)
            rates = np.array([e.rate for e in events])
            total = float(rates.sum())
            next_time = time + rng.exponential(1 / total) if total else float("inf")
            while cut < len(cuts) and cuts[cut] <= next_time:
                snapshots.append({"time": cuts[cut], **self.snapshot(state), **counts,
                                  "max_construction_depth": max_depth,
                                  "live_construction_depth": max(depth.values(), default=0)})
                cut += 1
            if cut == len(cuts):
                break
            if len(logs) >= event_limit:
                raise RuntimeError("Event limit reached; run is incomplete, not discarded")
            event = events[min(int(np.searchsorted(np.cumsum(rates), rng.random() * total)),
                               len(events) - 1)]
            pair = event.members
            if event.kind in ("thermal", "fuel", "catalytic"):
                bound = pair in state.bonds
                counts[event.kind + ("_reverse" if bound else "_forward")] += 1
                if bound:
                    del depth[pair]
                else:
                    depth[pair] = depth[event.catalyst] + 1 if event.catalyst else 0
                    max_depth = max(max_depth, depth[pair])
                    if event.catalyst and first_catalysis is None:
                        first_catalysis = next_time
            else:
                counts[event.kind] += 1
            self.apply(state, event)
            logs.append(event.record(next_time))
            time = next_time
        self.validate(state)
        assert initial.fuel - state.fuel == (counts["fuel_forward"] + counts["catalytic_forward"]
                                             - counts["fuel_reverse"] - counts["catalytic_reverse"])
        assert len(state.bonds) - len(initial.bonds) == sum(
            counts[k + "_forward"] - counts[k + "_reverse"]
            for k in ("thermal", "fuel", "catalytic"))
        return {"parameters": asdict(self.p), "seed": seed, "initial": initial.record(),
                "final": state.record(), "snapshots": snapshots, "events": logs,
                "first_catalytic_construction": first_catalysis,
                "event_columns": ["time", "kind", "members", "direction", "catalyst", "rate"]}


def balance_residual(model, state):
    """Check every represented reaction/move against its own physical reverse."""
    residual = 0.0
    for event in model.events(state):
        after = state.copy()
        model.apply(after, event)
        reverse_direction = tuple(-x for x in event.direction)
        reverse = [e for e in model.events(after)
                   if e.kind == event.kind and e.members == event.members
                   and e.catalyst == event.catalyst and e.direction == reverse_direction]
        if len(reverse) != 1:
            raise AssertionError(f"Missing or ambiguous reverse: {event}")
        err = log(event.rate / reverse[0].rate) + model.free_energy(after) - model.free_energy(state)
        residual = max(residual, abs(err))
    return residual
