"""Exact bounded continuation graphs and conventional prediction references.

No learning or novelty claim: C1 interns the same bounded behavior classes as
the independent pairwise partition-refinement implementation below.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from itertools import product

from omega_v2.finite.model import FiniteDistribution
from omega_v2.finite.operational_continuation import Experiment, Team, evaluate, team_id

F = Fraction


@dataclass(frozen=True)
class Interface:
    observations: tuple[Mapping[Hashable, Hashable], ...]
    atoms: Mapping[Hashable, Hashable]

    def validate(self, experiment: Experiment) -> None:
        states = set(experiment.system.states)
        if set(self.atoms) != states:
            raise ValueError("atoms must cover exactly the world states")
        if len(self.observations) != len(experiment.system.actions[0]):
            raise ValueError("one observation map per local controller is required")
        if any(set(obs) != states for obs in self.observations):
            raise ValueError("observations must cover exactly the world states")
        for team in experiment.teams:
            if any(c.observation_map != obs for c, obs in zip(
                team, self.observations, strict=True
            )):
                raise ValueError("all teams must share the declared observation interface")
        for value in (*self.atoms.values(), *(v for obs in self.observations for v in obs.values())):
            hash(value)


@dataclass(frozen=True)
class Label:
    terminal: bool
    observations: tuple[Hashable, ...]
    atom: Hashable


@dataclass(frozen=True)
class Node:
    label: Label
    # At depth h, targets are node indices in layer h-1. Costs label edges.
    branches: tuple[tuple[tuple, FiniteDistribution], ...]


@dataclass(frozen=True)
class Graph:
    layers: tuple[tuple[Node, ...], ...]
    decoding: tuple[Mapping[Hashable, int], ...]
    preparations: Mapping[str, FiniteDistribution]
    teams: tuple[Team, ...]
    actions: tuple[tuple, ...]
    budget: int

    @property
    def horizon(self) -> int:
        return len(self.layers) - 1


def _labels(e: Experiment, interface: Interface) -> dict[Hashable, Label]:
    interface.validate(e)
    return {
        s: Label(s in e.terminals, tuple(obs[s] for obs in interface.observations), interface.atoms[s])
        for s in e.system.states
    }


def build_c1(e: Experiment, interface: Interface) -> Graph:
    """Intern identical nodes, separately at each remaining horizon."""
    labels = _labels(e, interface)
    layers, decoding = [], []
    for h in range(e.horizon + 1):
        nodes, interned, mapping = [], {}, {}
        for s in e.system.states:
            branches = []
            if h and not labels[s].terminal:
                for action in e.system.actions:
                    masses = {}
                    for t, p in e.system.distribution(s, action).rows:
                        key = (e.costs[s, action, t], decoding[h - 1][t])
                        masses[key] = masses.get(key, F(0)) + p
                    branches.append((action, FiniteDistribution(tuple(sorted(masses.items())))))
            node = Node(labels[s], tuple(branches))
            if node not in interned:
                interned[node] = len(nodes)
                nodes.append(node)
            mapping[s] = interned[node]
        layers.append(tuple(nodes))
        decoding.append(mapping)
    return Graph(tuple(layers), tuple(decoding), {
        q: law.pushforward(decoding[-1].__getitem__) for q, law in e.preparations.items()
    }, e.teams, e.system.actions, e.budget)


def bounded_partitions(e: Experiment, interface: Interface) -> tuple[dict, ...]:
    """Conventional pairwise refinement; does not call C1 or intern Node objects.

    Compare mass on every (cost, previous block) cell for every action. Block
    numbers are local implementation details, not cross-world signatures.
    """
    labels = _labels(e, interface)
    partitions = []
    for h in range(e.horizon + 1):
        vectors = {}
        if h:
            for s in e.system.states:
                if labels[s].terminal:
                    continue
                for a in e.system.actions:
                    vector = {}
                    for source, action, target, probability in e.system.transitions:
                        if source == s and action == a:
                            cell = (e.costs[source, action, target], partitions[h - 1][target])
                            vector[cell] = vector.get(cell, F(0)) + probability
                    vectors[s, a] = vector
        representatives, partition = [], {}
        for s in e.system.states:
            for block, representative in enumerate(representatives):
                if labels[s] == labels[representative] and (
                    h == 0 or labels[s].terminal or all(
                        vectors[s, a] == vectors[representative, a] for a in e.system.actions
                    )
                ):
                    partition[s] = block
                    break
            else:
                partition[s] = len(representatives)
                representatives.append(s)
        partitions.append(partition)
    return tuple(partitions)


def build_quotient(e: Experiment, interface: Interface) -> Graph:
    """Materialize the conventional partition quotient, including its decoder."""
    partitions = bounded_partitions(e, interface)
    labels = _labels(e, interface)
    layers = []
    for h, partition in enumerate(partitions):
        representatives = {block: s for s, block in reversed(tuple(partition.items()))}
        nodes = []
        for block in range(len(representatives)):
            s = representatives[block]
            branches = []
            if h and not labels[s].terminal:
                for action in e.system.actions:
                    law = e.system.distribution(s, action).pushforward(
                        lambda t, s=s, action=action, h=h: (e.costs[s, action, t], partitions[h - 1][t])
                    )
                    branches.append((action, FiniteDistribution(tuple(sorted(law.rows)))))
            nodes.append(Node(labels[s], tuple(branches)))
        layers.append(tuple(nodes))
    return Graph(tuple(layers), partitions, {
        q: law.pushforward(partitions[-1].__getitem__) for q, law in e.preparations.items()
    }, e.teams, e.system.actions, e.budget)


def same_partitions(left: tuple[Mapping, ...], right: tuple[Mapping, ...]) -> bool:
    if len(left) != len(right):
        return False
    return all(set(a) == set(b) and all(
        (a[s] == a[t]) == (b[s] == b[t]) for s, t in product(a, repeat=2)
    ) for a, b in zip(left, right, strict=True))


@dataclass(frozen=True)
class Trace:
    atoms: tuple[Hashable, ...]
    actions: tuple[tuple, ...]
    observations: tuple[tuple[Hashable, ...], ...]
    memories: tuple[tuple[Hashable, ...], ...]
    cost: int
    censored: bool

    @property
    def elapsed(self) -> int:
        return len(self.actions)


@dataclass(frozen=True)
class Prediction:
    laws: Mapping[str, Mapping[str, FiniteDistribution[Trace]]]
    rejected: Mapping[str, int]
    cache_entries: int = 0


def reference_prediction(e: Experiment, interface: Interface) -> Prediction:
    interface.validate(e)
    full = evaluate(e)
    return Prediction({
        policy: {q: law.pushforward(lambda r: Trace(
            tuple(interface.atoms[s] for s in r.path.states), r.path.actions,
            r.observations, r.memories, r.cost, r.censored,
        )) for q, law in responses.items()} for policy, responses in full.laws.items()
    }, full.rejected)


def _admit(responses: dict, budget: int) -> Prediction:
    admitted, rejected = {}, {}
    for policy, laws in responses.items():
        worst = max(trace.cost for law in laws.values() for trace in law.support)
        if worst > budget:
            rejected[policy] = worst
        else:
            admitted[policy] = laws
    return Prediction(admitted, rejected)


def predict_graph(graph: Graph) -> Prediction:
    """Forward traversal; query execution has no access to the original kernel."""
    responses = {}
    for team in graph.teams:
        laws = {}
        for q, preparation in graph.preparations.items():
            paths = {}
            for index, p in preparation.rows:
                label = graph.layers[-1][index].label
                trace = Trace((label.atom,), (), tuple(() for _ in team),
                              tuple((c.initial_memory,) for c in team), 0, not label.terminal)
                paths[index, trace] = p
            for h in range(graph.horizon, 0, -1):
                extended = {}
                for (index, trace), mass in paths.items():
                    # Stopped paths carry no node index; they require no later layer.
                    if not trace.censored:
                        key = (None, trace)
                        extended[key] = extended.get(key, F(0)) + mass
                        continue
                    node = graph.layers[h][index]
                    observed = node.label.observations
                    action = tuple(c.action(m[-1], o) for c, m, o in zip(
                        team, trace.memories, observed, strict=True
                    ))
                    memories = tuple(m + (c.update(m[-1], o),) for c, m, o in zip(
                        team, trace.memories, observed, strict=True
                    ))
                    for (cost, target), probability in dict(node.branches)[action].rows:
                        label = graph.layers[h - 1][target].label
                        successor = Trace(
                            trace.atoms + (label.atom,), trace.actions + (action,),
                            tuple(history + (o,) for history, o in zip(
                                trace.observations, observed, strict=True
                            )), memories, trace.cost + cost, not label.terminal,
                        )
                        key = (target, successor)
                        extended[key] = extended.get(key, F(0)) + mass * probability
                paths = extended
            masses = {}
            for (_index, trace), probability in paths.items():
                masses[trace] = masses.get(trace, F(0)) + probability
            laws[q] = FiniteDistribution.from_mapping(masses)
        responses[team_id(team)] = laws
    return _admit(responses, graph.budget)


def predict_memoized(e: Experiment, interface: Interface) -> Prediction:
    """Ordinary dynamic programming on original states and local memories.

    Cache full suffix laws, not scalar job answers. Budget is applied afterwards
    to all paths; no cost pruning or missing task-monitor state is hidden here.
    """
    interface.validate(e)
    responses, cache_entries = {}, 0
    for team in e.teams:
        @cache
        def suffix(state, h, memories, team=team):
            if h == 0 or state in e.terminals:
                return FiniteDistribution.point_mass(Trace(
                    (interface.atoms[state],), (), tuple(() for _ in team),
                    tuple((m,) for m in memories), 0, state not in e.terminals,
                ))
            observed = tuple(c.observe(state) for c in team)
            action = tuple(c.action(m, o) for c, m, o in zip(team, memories, observed, strict=True))
            updated = tuple(c.update(m, o) for c, m, o in zip(team, memories, observed, strict=True))
            masses = {}
            for target, p in e.system.distribution(state, action).rows:
                for tail, probability in suffix(target, h - 1, updated).rows:
                    trace = Trace(
                        (interface.atoms[state],) + tail.atoms, (action,) + tail.actions,
                        tuple((o,) + history for o, history in zip(observed, tail.observations, strict=True)),
                        tuple((m,) + history for m, history in zip(memories, tail.memories, strict=True)),
                        e.costs[state, action, target] + tail.cost, tail.censored,
                    )
                    masses[trace] = masses.get(trace, F(0)) + p * probability
            return FiniteDistribution.from_mapping(masses)

        laws = {}
        for q, preparation in e.preparations.items():
            masses = {}
            for state, p in preparation.rows:
                for trace, probability in suffix(state, e.horizon, tuple(c.initial_memory for c in team)).rows:
                    masses[trace] = masses.get(trace, F(0)) + p * probability
            laws[q] = FiniteDistribution.from_mapping(masses)
        responses[team_id(team)] = laws
        cache_entries += suffix.cache_info().currsize
        suffix.cache_clear()
    prediction = _admit(responses, e.budget)
    return Prediction(prediction.laws, prediction.rejected, cache_entries)


def same_predictions(left: Prediction, right: Prediction) -> bool:
    return left.rejected == right.rejected and set(left.laws) == set(right.laws) and all(
        set(left.laws[p]) == set(right.laws[p]) and all(
            left.laws[p][q].mass_map == right.laws[p][q].mass_map for q in left.laws[p]
        ) for p in left.laws
    )


def best_probability(prediction: Prediction, weights: FiniteDistribution,
                     task: Callable[[str, Trace], bool]) -> tuple[Fraction | None, str | None]:
    """Choose one whole program before the input; return its checkable witness."""
    if any(not isinstance(p, F) for _q, p in weights.rows):
        raise ValueError("input probabilities must be exact Fractions")
    if not prediction.laws:
        return None, None
    if any(set(laws) != set(weights.support) for laws in prediction.laws.values()):
        raise ValueError("input law must cover exactly the predicted inputs")
    scores = {
        policy: sum((weight * p for q, weight in weights.rows
                     for trace, p in laws[q].rows if task(q, trace)), F(0))
        for policy, laws in prediction.laws.items()
    }
    witness = max(scores, key=scores.__getitem__)
    return scores[witness], witness


def compatible_range(models: Mapping[str, Mapping[str, Fraction]],
                     evidence: Mapping[str, Fraction], query: str) -> dict:
    """Version-space diagnostic over an explicit finite hypothesis class only."""
    if not models or any(query not in model or not set(evidence) <= set(model) for model in models.values()):
        raise ValueError("models must cover the query and evidence")
    if any(not isinstance(p, F) or not 0 <= p <= 1
           for p in (*evidence.values(), *(p for m in models.values() for p in m.values()))):
        raise ValueError("responses must be exact probabilities")
    compatible = tuple(name for name, model in models.items()
                       if all(model[q] == p for q, p in evidence.items()))
    if not compatible:
        return {"status": "inconsistent", "models": (), "lower": None, "upper": None}
    values = [models[name][query] for name in compatible]
    lo, hi = min(values), max(values)
    return {"status": "identified" if lo == hi else "unknown", "models": compatible,
            "lower": lo, "upper": hi}


def cost_record(extraction_cpu_ns: int, prediction_cpu_ns: int) -> dict[str, int]:
    if min(extraction_cpu_ns, prediction_cpu_ns) < 0:
        raise ValueError("CPU durations must be nonnegative")
    return {"extraction_cpu_ns": extraction_cpu_ns, "prediction_cpu_ns": prediction_cpu_ns,
            "total_cpu_ns": extraction_cpu_ns + prediction_cpu_ns}
