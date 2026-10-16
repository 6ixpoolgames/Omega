"""Exact finite cost-vector chains: finite paths and eventual first hitting.

No simulation, scalar cost aggregation, or conditioning away failed paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from omega_v2.finite.model import FiniteDistribution

F = Fraction
ZERO_COST = (0, 0, 0)


def add_cost(left, right):
    return tuple(a + b for a, b in zip(left, right, strict=True))


@dataclass(frozen=True)
class Chain:
    states: tuple
    initial: object
    rows: dict
    outcomes: dict
    terminals: frozenset

    def __post_init__(self):
        states = set(self.states)
        if not states or len(states) != len(self.states) or self.initial not in states:
            raise ValueError("unique states and a valid initial state required")
        if set(self.rows) != states or set(self.outcomes) != states or not self.terminals <= states:
            raise ValueError("total chain rows and outcomes required")
        for state, law in self.rows.items():
            for (target, cost), p in law.rows:
                if target not in states or not isinstance(p, F):
                    raise ValueError("known targets and exact rational probabilities required")
                if len(cost) != 3 or any(type(c) is not int or c < 0 for c in cost):
                    raise ValueError("three nonnegative integer cost coordinates required")
            if state in self.terminals and law.mass_map != {(state, ZERO_COST): F(1)}:
                raise ValueError("terminal rows must stop with zero costs")

    def transition(self, state):
        return self.rows[state].pushforward(lambda edge: edge[0])


def _horizon(value):
    if type(value) is not int or value < 0:
        raise ValueError("horizon must be a nonnegative integer")


def propagate(chain: Chain, horizon: int):
    """Marginal state laws and expected cost vectors at all deadlines."""
    _horizon(horizon)
    law = FiniteDistribution.point_mass(chain.initial)
    cost = (F(0), F(0), F(0))
    result = [{"law": law, "expected_cost": cost}]
    for _ in range(horizon):
        masses = {}
        increments = [F(0), F(0), F(0)]
        for state, p in law.rows:
            for (target, charge), q in chain.rows[state].rows:
                masses[target] = masses.get(target, F(0)) + p * q
                for i in range(3):
                    increments[i] += p * q * charge[i]
        law = FiniteDistribution.from_mapping(masses)
        cost = add_cost(cost, increments)
        result.append({"law": law, "expected_cost": cost})
    return result


@dataclass(frozen=True)
class Path:
    states: tuple
    cost: tuple
    charges: tuple = ()


def full_paths(chain: Chain, horizon: int):
    """Independent short-path reference, preserving stopped and live paths."""
    _horizon(horizon)
    paths = {Path((chain.initial,), ZERO_COST): F(1)}
    for _ in range(horizon):
        extended = {}
        for path, p in paths.items():
            state = path.states[-1]
            if state in chain.terminals:
                extended[path] = extended.get(path, F(0)) + p
                continue
            for (target, charge), q in chain.rows[state].rows:
                next_path = Path(path.states + (target,), add_cost(path.cost, charge), path.charges + (charge,))
                extended[next_path] = extended.get(next_path, F(0)) + p * q
        paths = extended
    return FiniteDistribution.from_mapping(paths)


def joint_cost_law(chain: Chain, horizon: int):
    """State/cost dynamic program, checked against complete short paths."""
    _horizon(horizon)
    masses = {(chain.initial, ZERO_COST): F(1)}
    for _ in range(horizon):
        extended = {}
        for (state, cost), p in masses.items():
            for (target, charge), q in chain.rows[state].rows:
                key = (target, add_cost(cost, charge))
                extended[key] = extended.get(key, F(0)) + p * q
        masses = extended
    return FiniteDistribution.from_mapping(masses)


def possible_targets(states, successors, targets):
    reached = set(targets)
    if not reached <= set(states):
        raise ValueError("unknown target")
    while True:
        added = {s for s in states if any(t in reached for t in successors[s])} - reached
        if not added:
            return frozenset(reached)
        reached.update(added)


def _solve(matrix, rhs):
    """Rational Gaussian elimination; singular inputs fail closed."""
    rows = [list(row) + [value] for row, value in zip(matrix, rhs, strict=True)]
    for col in range(len(rows)):
        pivot = next((i for i in range(col, len(rows)) if rows[i][col]), None)
        if pivot is None:
            raise ValueError("singular hitting system")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [value / divisor for value in rows[col]]
        for i in range(len(rows)):
            if i != col:
                factor = rows[i][col]
                rows[i] = [a - factor * b for a, b in zip(rows[i], rows[col], strict=True)]
    return [row[-1] for row in rows]


def hitting_analysis(chain: Chain, targets: frozenset):
    """Eventual probabilities and E[T 1{T<infinity}], then conditional means.

    Exclude states without a path to the target before solving. Their hitting
    probability and weighted time are zero, including non-target closed classes.
    Targets have first-hitting time zero regardless of their outgoing edges.
    """
    transitions = {s: chain.transition(s).mass_map for s in chain.states}
    possible = possible_targets(chain.states, transitions, targets)
    transient = tuple(s for s in chain.states if s in possible and s not in targets)
    matrix = [[F(int(s == t)) - transitions[s].get(t, F(0)) for t in transient] for s in transient]
    rhs = [sum((p for t, p in transitions[s].items() if t in targets), F(0)) for s in transient]
    hit = {s: F(int(s in targets)) for s in chain.states}
    hit.update(zip(transient, _solve(matrix, rhs), strict=True))
    weighted_time = {s: F(0) for s in chain.states}
    weighted_time.update(zip(transient, _solve(matrix, [hit[s] for s in transient]), strict=True))
    residuals = {}
    results = {}
    for s in chain.states:
        residuals[s] = (F(0), F(0)) if s in targets else (
            hit[s] - sum((p * hit[t] for t, p in transitions[s].items()), F(0)),
            weighted_time[s] - hit[s] - sum((p * weighted_time[t] for t, p in transitions[s].items()), F(0)),
        )
        results[s] = {"probability": hit[s], "weighted_time": weighted_time[s],
                      "mean": weighted_time[s] if hit[s] == 1 else "infinity",
                      "conditional_mean": weighted_time[s] / hit[s] if hit[s] else None}
    return {"initial": results[chain.initial], "states": results, "possible": possible,
            "almost_sure": frozenset(s for s in chain.states if hit[s] == 1), "residuals": residuals}
