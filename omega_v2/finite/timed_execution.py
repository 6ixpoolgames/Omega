"""Finite guarded exponential races and a deliberately provisional timing extent.

The complete process and its timing-volume summary are different objects.
This module never selects policies, removes failed outcomes, or sums horizons.
"""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from math import factorial, prod

import numpy as np
from scipy.linalg import expm

State = tuple[tuple[str, int], ...]
Law = dict[State, Fraction]
Cost = tuple[int, int]


def state(**registers: int) -> State:
    return tuple(sorted(registers.items()))


@dataclass(frozen=True)
class Transition:
    name: str
    guard: State
    writes: State
    rate: Fraction = Fraction(1)
    cost: Cost = (1, 1)

    def __post_init__(self):
        if self.rate <= 0:
            raise ValueError("rates must be positive")
        if any(c < 0 for c in self.cost):
            raise ValueError("costs must be nonnegative")
        for pairs in (self.guard, self.writes):
            if len(dict(pairs)) != len(pairs):
                raise ValueError("duplicate register")

    @property
    def footprint(self) -> frozenset[str]:
        return frozenset(k for k, _ in self.guard + self.writes)

    def enabled(self, source: State) -> bool:
        registers = dict(source)
        return all(registers.get(k) == v for k, v in self.guard)

    def fire(self, source: State) -> State:
        if not self.enabled(source):
            raise ValueError("disabled transition")
        registers = dict(source)
        if not set(dict(self.writes)) <= set(registers):
            raise ValueError("update introduces an undeclared register")
        registers.update(self.writes)
        return tuple(sorted(registers.items()))


@dataclass(frozen=True)
class Net:
    transitions: tuple[Transition, ...]

    def __post_init__(self):
        if len({t.name for t in self.transitions}) != len(self.transitions):
            raise ValueError("transition names must be unique")

    def enabled(self, source: State) -> tuple[Transition, ...]:
        return tuple(t for t in self.transitions if t.enabled(source))

    def exit_rate(self, source: State) -> Fraction:
        return sum((t.rate for t in self.enabled(source)), Fraction())


@dataclass(frozen=True)
class Path:
    states: tuple[State, ...]
    events: tuple[Transition, ...]
    initial_mass: Fraction

    @property
    def cost(self) -> Cost:
        return tuple(sum(t.cost[i] for t in self.events) for i in range(2))


def validate_law(law: Law) -> None:
    if not law or sum(law.values()) != 1 or any(p <= 0 for p in law.values()):
        raise ValueError("initial law must have positive masses summing to one")


def enumerate_paths(net: Net, initial: Law, physical_event_bound: int) -> list[Path]:
    """All prefixes, including the empty one; the bound must exhaust the physics."""
    validate_law(initial)
    if physical_event_bound < 0:
        raise ValueError("negative bound")
    frontier = [Path((s,), (), p) for s, p in initial.items()]
    paths = []
    for n in range(physical_event_bound + 1):
        paths.extend(frontier)
        successors = []
        for path in frontier:
            enabled = net.enabled(path.states[-1])
            if n == physical_event_bound and enabled:
                raise ValueError("event bound would discard physical continuations")
            for event in enabled:
                successors.append(Path(
                    path.states + (event.fire(path.states[-1]),),
                    path.events + (event,), path.initial_mass,
                ))
        frontier = successors
    return paths


def canonical_word(events: tuple[Transition, ...]) -> tuple[str, ...]:
    """Lexicographically least topological order of the dependence poset.

    Occurrences with intersecting footprints retain their chronological order.
    This groups presentations only; their distinct firing times are integrated.
    """
    predecessors = [
        {i for i in range(j) if events[i].footprint & event.footprint}
        for j, event in enumerate(events)
    ]
    remaining, emitted, answer = set(range(len(events))), set(), []
    while remaining:
        available = [j for j in remaining if predecessors[j] <= emitted]
        chosen = min(available, key=lambda j: (events[j].name, j))
        answer.append(events[chosen].name)
        emitted.add(chosen)
        remaining.remove(chosen)
    return tuple(answer)


@cache
def _ordered_kernel(exits: tuple[Fraction, ...], horizon: float) -> float:
    """Integral over the ordered simplex, including final no-firing survival."""
    matrix = np.diag([-float(rate) for rate in exits])
    for i in range(len(exits) - 1):
        matrix[i, i + 1] = 1.0
    return float(expm(matrix * horizon)[0, -1])


def path_probability(net: Net, path: Path, horizon: float) -> float:
    if not np.isfinite(horizon) or horizon < 0:
        raise ValueError("horizon must be finite and nonnegative")
    exits = tuple(net.exit_rate(s) for s in path.states)
    coefficient = path.initial_mass * prod((t.rate for t in path.events), start=Fraction(1))
    return float(coefficient) * _ordered_kernel(exits, float(horizon))


def timing_profile(net: Net, paths: list[Path], horizon: float) -> dict:
    classes = defaultdict(list)
    for path in paths:
        classes[path.states[0], canonical_word(path.events)].append(path)
    bound = max(len(p.events) for p in paths)
    volumes, weighted, counts = [0.0] * (bound + 1), [0.0] * (bound + 1), [0.0] * (bound + 1)
    rows = []
    for (initial, word), members in sorted(classes.items()):
        n = len(word)
        probability = sum(path_probability(net, p, horizon) for p in members)
        volume = len(members) * horizon**n / factorial(n)
        volumes[n] += volume
        weighted[n] += probability * volume
        counts[n] += probability
        rows.append({"initial": initial, "word": word, "presentations": len(members),
                     "probability": probability, "timing_volume": volume})
    return {"H": horizon, "V": volumes, "L": weighted, "count_law": counts,
            "mass": sum(counts), "classes": rows}


def endpoint_from_paths(net: Net, paths: list[Path], horizon: float) -> dict[State, float]:
    result = defaultdict(float)
    for path in paths:
        result[path.states[-1]] += path_probability(net, path, horizon)
    return dict(result)


def reachable_states(net: Net, starts) -> tuple[State, ...]:
    seen, pending = set(starts), deque(starts)
    while pending:
        source = pending.popleft()
        for event in net.enabled(source):
            target = event.fire(source)
            if target not in seen:
                seen.add(target)
                pending.append(target)
    return tuple(sorted(seen))


def generator(net: Net, starts) -> tuple[tuple[State, ...], np.ndarray]:
    states = reachable_states(net, starts)
    index = {s: i for i, s in enumerate(states)}
    matrix = np.zeros((len(states), len(states)))
    for s, i in index.items():
        for event in net.enabled(s):
            rate = float(event.rate)
            matrix[i, i] -= rate
            matrix[i, index[event.fire(s)]] += rate
    return states, matrix


def endpoint_from_matrix(net: Net, initial: Law, horizon: float, *, cut=None) -> dict[State, float]:
    """Independent state-space propagation, optionally through an intermediate cut."""
    states, matrix = generator(net, initial)
    probabilities = np.array([float(initial.get(s, 0)) for s in states])
    if cut is None:
        probabilities = probabilities @ expm(horizon * matrix)
    else:
        if not 0 <= cut <= horizon:
            raise ValueError("cut outside horizon")
        probabilities = probabilities @ expm(cut * matrix) @ expm((horizon - cut) * matrix)
    return dict(zip(states, map(float, probabilities), strict=True))


def jump_law(net: Net, initial: Law, events: int) -> Law:
    """Exact rational state law after a stated number of physical firings."""
    law = initial
    for _ in range(events):
        result = defaultdict(Fraction)
        for source, mass in law.items():
            enabled = net.enabled(source)
            total = sum((t.rate for t in enabled), Fraction())
            if not total:
                raise ValueError("requested boundary lies after absorption")
            for event in enabled:
                result[event.fire(source)] += mass * event.rate / total
        law = dict(result)
    return law


def condition_on(law: Law, records: tuple[str, ...]) -> dict[tuple[int, ...], tuple[Fraction, Law]]:
    groups = defaultdict(dict)
    for s, p in law.items():
        record = tuple(dict(s)[key] for key in records)
        groups[record][s] = p
    return {record: (sum(group.values()), {s: p / sum(group.values()) for s, p in group.items()})
            for record, group in groups.items()}


def marginal(law, registers: tuple[str, ...]) -> dict[tuple[int, ...], Fraction | float]:
    result = {}
    for s, mass in law.items():
        key = tuple(dict(s)[name] for name in registers)
        result[key] = result.get(key, 0) + mass
    return result


def hitting_probability(net: Net, paths: list[Path], horizon: float,
                        predicate: Callable[[State], bool]) -> float:
    return sum(path_probability(net, path, horizon) for path in paths
               if any(predicate(s) for s in path.states))


def closed_region(net: Net, states: tuple[State, ...], predicate: Callable[[State], bool]) -> bool:
    return all(predicate(event.fire(s)) for s in states if predicate(s) for event in net.enabled(s))
