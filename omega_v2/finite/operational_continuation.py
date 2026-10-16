"""Exact finite team continuations and catalogue-relative response emulation.

Controllers see only their declared observation and memory. Program selection
precedes the input. No random policy mixture or branchwise selector is supplied.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from omega_v2.finite.controllers import FiniteStateController
from omega_v2.finite.model import ControlledMarkovSystem, FiniteDistribution, FinitePath

Team = tuple[FiniteStateController, ...]


def team_id(team: Team) -> str:
    return "|".join(controller.controller_id for controller in team)


@dataclass(frozen=True)
class Run:
    path: FinitePath
    observations: tuple[tuple[Hashable, ...], ...]
    memories: tuple[tuple[Hashable, ...], ...]
    cost: int
    censored: bool

    @property
    def elapsed(self) -> int:
        return self.path.horizon


@dataclass(frozen=True)
class Experiment:
    """An installed finite apparatus and explicit admissible controller catalogue."""

    name: str
    system: ControlledMarkovSystem
    preparations: Mapping[str, FiniteDistribution]
    teams: tuple[Team, ...]
    terminals: frozenset[Hashable]
    costs: Mapping[tuple[Hashable, tuple, Hashable], int]
    horizon: int
    budget: int

    def __post_init__(self) -> None:
        if not isinstance(self.horizon, int) or self.horizon < 0:
            raise ValueError("horizon must be a nonnegative integer")
        if not isinstance(self.budget, int) or self.budget < 0:
            raise ValueError("budget must be a nonnegative integer")
        if not self.preparations:
            raise ValueError("input preparations must be nonempty")
        if not self.terminals <= set(self.system.states):
            raise ValueError("unknown terminal state")
        if any(not isinstance(p, Fraction) for *_row, p in self.system.transitions):
            raise ValueError("transition probabilities must be exact Fractions")
        required_costs = {(s, a, t) for s, a, t, _p in self.system.transitions}
        if set(self.costs) != required_costs:
            raise ValueError("costs must cover exactly the supported transitions")
        if any(not isinstance(c, int) or c < 0 for c in self.costs.values()):
            raise ValueError("costs must be nonnegative integer tokens")
        for distribution in self.preparations.values():
            if not set(distribution.support) <= set(self.system.states):
                raise ValueError("preparation references unknown state")
            if any(not isinstance(p, Fraction) for _s, p in distribution.rows):
                raise ValueError("preparation probabilities must be exact Fractions")
        identifiers = tuple(team_id(team) for team in self.teams)
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("team identifiers must be unique")
        if any(not isinstance(action, tuple) for action in self.system.actions):
            raise ValueError("joint actions must be tuples")
        arities = {len(action) for action in self.system.actions}
        if len(arities) != 1 or next(iter(arities)) == 0:
            raise ValueError("actions must be nonempty tuples of one fixed arity")
        for team in self.teams:
            if {len(team)} != arities:
                raise ValueError("team size must match joint-action arity")
            for i, controller in enumerate(team):
                if set(controller.observation_map) != set(self.system.states):
                    raise ValueError("local observation must cover every world state")
                local_actions = {action[i] for action in self.system.actions}
                if not set(controller.policy_map.values()) <= local_actions:
                    raise ValueError("controller references an unknown local action")
            # A tuple of individually legal commands must have a modeled joint law.
            for joint in product(*(set(c.policy_map.values()) for c in team)):
                if joint not in self.system.actions:
                    raise ValueError("missing joint-action law")


def reactive_teams(
    observations: tuple[Mapping[Hashable, Hashable], ...],
    menus: tuple[Mapping[Hashable, tuple[Hashable, ...]], ...],
) -> tuple[Team, ...]:
    """Enumerate local tables, not full-state tables. Records live in world states.

    Completeness is only over these declared reactive tables. Models using this
    helper must justify that their physically retained records suffice.
    """

    if not observations or len(observations) != len(menus):
        raise ValueError("one observation map and menu per controller is required")
    local_families = []
    for i, (observation, menu) in enumerate(zip(observations, menus, strict=True)):
        keys = tuple(dict.fromkeys(observation.values()))
        if set(menu) != set(keys) or any(not menu[key] for key in keys):
            raise ValueError("menus must be nonempty and total on local observations")
        if any(len(menu[key]) != len(set(menu[key])) for key in keys):
            raise ValueError("local menu actions must be unique")
        local_families.append(tuple(
            FiniteStateController(
                controller_id=f"c{i}-{j}",
                memory_states=(0,),
                initial_memory=0,
                observation_rows=tuple(observation.items()),
                update_rows=tuple((0, key, 0) for key in keys),
                policy_rows=tuple((0, key, action) for key, action in zip(
                    keys, choices, strict=True
                )),
            )
            for j, choices in enumerate(product(*(menu[key] for key in keys)))
        ))
    return tuple(product(*local_families))


def rollout(experiment: Experiment, team: Team, input_id: str) -> FiniteDistribution[Run]:
    """Retain full paths, failures and horizon censoring under one installed team."""

    if team not in experiment.teams:
        raise ValueError("team is not in the admitted catalogue")
    paths = {
        Run(
            FinitePath((state,), ()),
            tuple(() for _c in team),
            tuple((c.initial_memory,) for c in team),
            0,
            state not in experiment.terminals,
        ): mass
        for state, mass in experiment.preparations[input_id].rows
    }
    for _step in range(experiment.horizon):
        extended: dict[Run, Fraction] = {}
        for run, mass in paths.items():
            state = run.path.end
            if state in experiment.terminals:
                extended[run] = extended.get(run, Fraction(0)) + mass
                continue
            observed = tuple(c.observe(state) for c in team)
            actions = tuple(
                c.action(memory[-1], obs)
                for c, memory, obs in zip(team, run.memories, observed, strict=True)
            )
            next_memories = tuple(
                history + (c.update(history[-1], obs),)
                for c, history, obs in zip(team, run.memories, observed, strict=True)
            )
            for target, probability in experiment.system.distribution(state, actions).rows:
                successor = Run(
                    FinitePath(run.path.states + (target,), run.path.actions + (actions,)),
                    tuple(h + (o,) for h, o in zip(run.observations, observed, strict=True)),
                    next_memories,
                    run.cost + experiment.costs[(state, actions, target)],
                    target not in experiment.terminals,
                )
                extended[successor] = extended.get(successor, Fraction(0)) + mass * probability
        paths = extended
    return FiniteDistribution.from_mapping(paths)


@dataclass(frozen=True)
class Evaluated:
    experiment: Experiment
    laws: Mapping[str, Mapping[str, FiniteDistribution[Run]]]
    rejected: Mapping[str, int]


def evaluate(experiment: Experiment) -> Evaluated:
    laws, rejected = {}, {}
    for team in experiment.teams:
        responses = {q: rollout(experiment, team, q) for q in experiment.preparations}
        maximum_cost = max(run.cost for law in responses.values() for run in law.support)
        if maximum_cost > experiment.budget:
            rejected[team_id(team)] = maximum_cost
        else:
            laws[team_id(team)] = responses
    return Evaluated(experiment, laws, rejected)


def achievement(
    evaluated: Evaluated,
    input_weights: FiniteDistribution[str],
    tasks: Mapping[str, Callable[[str, Run], bool]],
) -> dict[str, Fraction] | None:
    """Optimize whole policies, with a declared physical input law, once per task."""

    if set(input_weights.support) != set(evaluated.experiment.preparations):
        raise ValueError("input law must cover exactly the declared inputs")
    if any(not isinstance(p, Fraction) for _q, p in input_weights.rows):
        raise ValueError("input probabilities must be exact Fractions")
    if not tasks:
        raise ValueError("task family must be nonempty")
    if not evaluated.laws:
        return None
    return {
        name: max(
            sum((
                weight * mass
                for q, weight in input_weights.rows
                for run, mass in laws[q].rows
                if task(q, run)
            ), Fraction(0))
            for laws in evaluated.laws.values()
        )
        for name, task in tasks.items()
    }


def profile_verdict(left: Mapping, right: Mapping) -> str:
    if not left or set(left) != set(right):
        raise ValueError("profiles require the same nonempty task family")
    l_ge = all(left[k] >= right[k] for k in left)
    r_ge = all(right[k] >= left[k] for k in left)
    if l_ge and r_ge:
        return "equivalent"
    if l_ge:
        return "left_strict"
    if r_ge:
        return "right_strict"
    return "incomparable"


@dataclass(frozen=True)
class ResponseCatalogue:
    frame: str
    inputs: tuple[str, ...]
    horizon: int
    budget: int
    signatures: Mapping[str, tuple[frozenset, ...]]


def project(
    evaluated: Evaluated, *, frame: str, readout: Callable[[str, Run], Hashable]
) -> ResponseCatalogue:
    """Project laws without discarding the underlying evaluated history evidence."""

    if not frame:
        raise ValueError("a declared response frame is required")
    inputs = tuple(sorted(evaluated.experiment.preparations))
    return ResponseCatalogue(
        frame, inputs, evaluated.experiment.horizon, evaluated.experiment.budget,
        {
            policy: tuple(
                frozenset(laws[q].pushforward(lambda run, q=q: readout(q, run)).rows)
                for q in inputs
            )
            for policy, laws in evaluated.laws.items()
        },
    )


def emulate(source: ResponseCatalogue, target: ResponseCatalogue) -> dict:
    """For each target policy choose a source witness BEFORE the external input."""

    if (source.frame, source.inputs, source.horizon, source.budget) != (
        target.frame, target.inputs, target.horizon, target.budget
    ):
        raise ValueError("emulation requires matched frames, inputs, horizons and budgets")
    if not source.signatures or not target.signatures:
        return {"status": "unavailable", "witnesses": {}, "failures": {}}
    witnesses, failures = {}, {}
    for target_policy, signature in target.signatures.items():
        matching = next((
            p for p, response in source.signatures.items() if response == signature
        ), None)
        if matching is not None:
            witnesses[target_policy] = matching
        else:
            failures[target_policy] = {
                p: next(
                    q for q, actual, expected in zip(
                        source.inputs, response, signature, strict=True
                    ) if actual != expected
                )
                for p, response in source.signatures.items()
            }
    return {
        "status": "holds" if not failures else "fails",
        "witnesses": witnesses,
        "failures": failures,
    }
