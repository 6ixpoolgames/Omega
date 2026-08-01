"""Executable Alpha-Omega foundation over finite controlled dynamics.

The module keeps four layers separate:

* exact rational controlled kernels and finite path laws;
* action-labelled support and presentation contracts;
* finite-state controller feature profiles;
* witness-retaining May-realization fibers.

It is instrumentation and theorem support. It does not define value, standing,
personhood, consciousness, moral license, or a preferred physical orientation.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Any, Iterable, Mapping

from omega.adapters.finite_relational.dynamic_continuation_profiles import (
    Action,
    AtomRow,
    FiniteControlSystem,
    State,
)
from omega.adapters.finite_relational.generated_continuation_dynamics import (
    COMPONENTS,
    SHARED_ACTIONS,
    SharedActionAssignment,
)
from omega.adapters.finite_relational.stochastic_recovery import fraction_to_text


PROTOCOL_DOC = "docs/research_notes/omega_v2/alpha_omega_foundation_protocol_v0.md"

WeightRow = tuple[State, Action, State, Fraction]
InitialRow = tuple[State, Fraction]
PolicyRow = tuple[State, Action]
ObservationRow = tuple[State, str]
UpdateRow = tuple[str, str, str]
ControllerPolicyRow = tuple[str, str, Action]
Family = frozenset[str]


# Exact finite dynamics and oriented path laws.


def _require_distribution(
    rows: Iterable[tuple[str, Fraction]],
    *,
    label: str,
) -> tuple[tuple[str, Fraction], ...]:
    retained = tuple(rows)
    if not retained:
        raise ValueError(f"{label} must be nonempty")
    keys = tuple(key for key, _weight in retained)
    if len(keys) != len(set(keys)):
        raise ValueError(f"{label} contains duplicate outcomes")
    if any(weight <= 0 for _key, weight in retained):
        raise ValueError(f"{label} weights must be strictly positive")
    if sum((weight for _key, weight in retained), Fraction(0)) != 1:
        raise ValueError(f"{label} weights must sum exactly to one")
    return retained


@dataclass(frozen=True)
class FiniteControlledKernel:
    """A finite controlled stochastic kernel with exact rational weights."""

    system_id: str
    states: tuple[State, ...]
    actions: tuple[Action, ...]
    transitions: tuple[WeightRow, ...]
    atoms: tuple[AtomRow, ...] = ()

    def __post_init__(self) -> None:
        if not self.system_id:
            raise ValueError("system_id must be nonempty")
        if not self.states or len(self.states) != len(set(self.states)):
            raise ValueError("states must be nonempty and unique")
        if not self.actions or len(self.actions) != len(set(self.actions)):
            raise ValueError("actions must be nonempty and unique")

        state_set = set(self.states)
        action_set = set(self.actions)
        keys: set[tuple[State, Action, State]] = set()
        grouped: dict[tuple[State, Action], list[tuple[State, Fraction]]] = {
            (state, action): [] for state in self.states for action in self.actions
        }
        for source, action, target, weight in self.transitions:
            if source not in state_set or target not in state_set:
                raise ValueError("transition contains an unknown state")
            if action not in action_set:
                raise ValueError("transition contains an unknown action")
            key = (source, action, target)
            if key in keys:
                raise ValueError("transition rows must be unique")
            keys.add(key)
            grouped[(source, action)].append((target, weight))

        for state in self.states:
            for action in self.actions:
                _require_distribution(
                    grouped[(state, action)],
                    label=f"transition distribution for {(state, action)!r}",
                )

        atom_states = tuple(state for state, _state_atoms in self.atoms)
        if len(atom_states) != len(set(atom_states)):
            raise ValueError("each state may have at most one atom row")
        unknown_atom_states = set(atom_states) - state_set
        if unknown_atom_states:
            raise ValueError(f"atom rows contain unknown states: {sorted(unknown_atom_states)}")

    @property
    def atom_map(self) -> dict[State, frozenset[str]]:
        declared = dict(self.atoms)
        return {state: frozenset(declared.get(state, frozenset())) for state in self.states}

    def distribution(self, state: State, action: Action) -> dict[State, Fraction]:
        self._require_state(state)
        self._require_action(action)
        return {
            target: weight
            for source, candidate_action, target, weight in self.transitions
            if source == state and candidate_action == action
        }

    def support_successors(self, state: State, action: Action) -> frozenset[State]:
        return frozenset(self.distribution(state, action))

    def support_system(self, *, system_id: str | None = None) -> FiniteControlSystem:
        return FiniteControlSystem(
            system_id=system_id or f"{self.system_id}__support",
            states=self.states,
            actions=self.actions,
            transitions=tuple(
                (source, action, target)
                for source, action, target, _weight in self.transitions
            ),
            atoms=self.atoms,
        )

    def _require_state(self, state: State) -> None:
        if state not in self.states:
            raise KeyError(state)

    def _require_action(self, action: Action) -> None:
        if action not in self.actions:
            raise KeyError(action)


@dataclass(frozen=True)
class DeterministicPolicy:
    """A total stationary deterministic policy."""

    policy_id: str
    rows: tuple[PolicyRow, ...]

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must be nonempty")
        states = tuple(state for state, _action in self.rows)
        if len(states) != len(set(states)):
            raise ValueError("policy contains duplicate state rows")

    @property
    def action_map(self) -> dict[State, Action]:
        return dict(self.rows)

    def validate(self, kernel: FiniteControlledKernel) -> None:
        if set(self.action_map) != set(kernel.states):
            raise ValueError("policy must be total on kernel states")
        unknown = {
            state: action
            for state, action in self.rows
            if action not in kernel.actions
        }
        if unknown:
            raise ValueError(f"policy uses unknown actions: {unknown}")

    def action_at(self, state: State) -> Action:
        try:
            return self.action_map[state]
        except KeyError as exc:
            raise KeyError(state) from exc


@dataclass(frozen=True, order=True)
class FinitePath:
    """A finite controlled path with explicit states and actions."""

    states: tuple[State, ...]
    actions: tuple[Action, ...]

    def __post_init__(self) -> None:
        if not self.states:
            raise ValueError("a path must contain at least one state")
        if len(self.states) != len(self.actions) + 1:
            raise ValueError("a path with n actions must contain n + 1 states")

    @property
    def horizon(self) -> int:
        return len(self.actions)

    @property
    def start(self) -> State:
        return self.states[0]

    @property
    def end(self) -> State:
        return self.states[-1]

    def canonical_id(self) -> str:
        payload = json.dumps(
            {"states": self.states, "actions": self.actions},
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def validate(
        self,
        kernel: FiniteControlledKernel,
        policy: DeterministicPolicy | None = None,
    ) -> None:
        if policy is not None:
            policy.validate(kernel)
        for state in self.states:
            kernel._require_state(state)
        for index, action in enumerate(self.actions):
            kernel._require_action(action)
            source = self.states[index]
            target = self.states[index + 1]
            if policy is not None and policy.action_at(source) != action:
                raise ValueError("path action does not match the supplied policy")
            if target not in kernel.support_successors(source, action):
                raise ValueError("path contains a zero-probability transition")


@dataclass(frozen=True)
class PathReversal:
    """An explicit involutive action relabeling used when reversing paths."""

    convention_id: str
    action_rows: tuple[tuple[Action, Action], ...]

    def __post_init__(self) -> None:
        if not self.convention_id:
            raise ValueError("convention_id must be nonempty")
        sources = tuple(source for source, _target in self.action_rows)
        if len(sources) != len(set(sources)):
            raise ValueError("path-reversal action map must be functional")
        action_map = dict(self.action_rows)
        if set(action_map) != set(action_map.values()):
            raise ValueError("path-reversal action map must be a permutation")
        if any(action_map[action_map[action]] != action for action in action_map):
            raise ValueError("path-reversal action map must be involutive")

    @property
    def action_map(self) -> dict[Action, Action]:
        return dict(self.action_rows)

    def validate(
        self,
        forward: FiniteControlledKernel,
        reverse: FiniteControlledKernel,
    ) -> None:
        if forward.states != reverse.states:
            raise ValueError("v0 path reversal requires a common ordered state type")
        if set(forward.actions) != set(reverse.actions):
            raise ValueError("forward and reverse kernels require the same action set")
        if set(self.action_map) != set(forward.actions):
            raise ValueError("path-reversal action map must be total")

    def reverse(self, path: FinitePath) -> FinitePath:
        return FinitePath(
            states=tuple(reversed(path.states)),
            actions=tuple(self.action_map[action] for action in reversed(path.actions)),
        )


@dataclass(frozen=True)
class DirectionalityProfile:
    """Finite path-law comparison against an explicit reversed law."""

    profile_id: str
    horizon: int
    reversal_convention: str
    reciprocal_support: bool
    support_mismatch_count: int
    total_variation: float
    kl_forward_to_reversed: float | None

    @property
    def statistically_directional(self) -> bool:
        return self.total_variation > 1e-12

    @property
    def kl_is_infinite(self) -> bool:
        return self.kl_forward_to_reversed is None

    def as_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "horizon": self.horizon,
            "reversal_convention": self.reversal_convention,
            "reciprocal_support": self.reciprocal_support,
            "support_mismatch_count": self.support_mismatch_count,
            "total_variation": self.total_variation,
            "kl_forward_to_reversed": self.kl_forward_to_reversed,
            "kl_is_infinite": self.kl_is_infinite,
            "statistically_directional": self.statistically_directional,
        }


def validate_initial_distribution(
    kernel: FiniteControlledKernel,
    initial: tuple[InitialRow, ...],
) -> None:
    _require_distribution(initial, label="initial distribution")
    unknown = set(state for state, _weight in initial) - set(kernel.states)
    if unknown:
        raise ValueError(f"initial distribution contains unknown states: {sorted(unknown)}")


def finite_path_law(
    kernel: FiniteControlledKernel,
    policy: DeterministicPolicy,
    initial: tuple[InitialRow, ...],
    *,
    horizon: int,
) -> dict[FinitePath, Fraction]:
    """Enumerate the exact finite path law induced by a stationary policy."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    policy.validate(kernel)
    validate_initial_distribution(kernel, initial)
    frontier: dict[FinitePath, Fraction] = {
        FinitePath(states=(state,), actions=()): weight for state, weight in initial
    }
    for _step in range(horizon):
        next_frontier: dict[FinitePath, Fraction] = {}
        for path, prefix_weight in frontier.items():
            action = policy.action_at(path.end)
            for target, transition_weight in kernel.distribution(path.end, action).items():
                extended = FinitePath(
                    states=path.states + (target,),
                    actions=path.actions + (action,),
                )
                next_frontier[extended] = (
                    next_frontier.get(extended, Fraction(0))
                    + prefix_weight * transition_weight
                )
        frontier = next_frontier
    if sum(frontier.values(), Fraction(0)) != 1:
        raise AssertionError("finite path law failed to normalize")
    return frontier


def path_probability(
    kernel: FiniteControlledKernel,
    policy: DeterministicPolicy,
    initial: tuple[InitialRow, ...],
    path: FinitePath,
) -> Fraction:
    """Return the exact probability of one policy-consistent finite path."""

    policy.validate(kernel)
    validate_initial_distribution(kernel, initial)
    initial_map = dict(initial)
    if path.start not in initial_map:
        return Fraction(0)
    try:
        path.validate(kernel, policy)
    except ValueError:
        return Fraction(0)
    weight = initial_map[path.start]
    for index, action in enumerate(path.actions):
        weight *= kernel.distribution(path.states[index], action).get(
            path.states[index + 1],
            Fraction(0),
        )
    return weight


def residual_continuation_law(
    kernel: FiniteControlledKernel,
    policy: DeterministicPolicy,
    prefix: FinitePath,
    *,
    remaining_horizon: int,
) -> dict[FinitePath, Fraction]:
    """Return the Markov residual law from the endpoint of a live prefix."""

    if remaining_horizon < 0:
        raise ValueError("remaining_horizon must be nonnegative")
    prefix.validate(kernel, policy)
    return finite_path_law(
        kernel,
        policy,
        ((prefix.end, Fraction(1)),),
        horizon=remaining_horizon,
    )


def compare_oriented_path_laws(
    *,
    profile_id: str,
    forward_kernel: FiniteControlledKernel,
    forward_policy: DeterministicPolicy,
    forward_initial: tuple[InitialRow, ...],
    reverse_kernel: FiniteControlledKernel,
    reverse_policy: DeterministicPolicy,
    reverse_initial: tuple[InitialRow, ...],
    reversal: PathReversal,
    horizon: int,
) -> DirectionalityProfile:
    """Compare a forward path law with the pullback of a reverse path law."""

    reversal.validate(forward_kernel, reverse_kernel)
    forward_law = finite_path_law(
        forward_kernel,
        forward_policy,
        forward_initial,
        horizon=horizon,
    )
    reverse_law = finite_path_law(
        reverse_kernel,
        reverse_policy,
        reverse_initial,
        horizon=horizon,
    )
    reverse_pulled_back: dict[FinitePath, Fraction] = {}
    for reverse_path, probability in reverse_law.items():
        forward_key = reversal.reverse(reverse_path)
        reverse_pulled_back[forward_key] = (
            reverse_pulled_back.get(forward_key, Fraction(0)) + probability
        )

    all_paths = set(forward_law) | set(reverse_pulled_back)
    mismatch_count = sum(
        1
        for path in all_paths
        if (forward_law.get(path, Fraction(0)) > 0)
        != (reverse_pulled_back.get(path, Fraction(0)) > 0)
    )
    total_variation = 0.5 * sum(
        abs(float(forward_law.get(path, Fraction(0)) - reverse_pulled_back.get(path, Fraction(0))))
        for path in all_paths
    )
    positive_support_mismatch = any(
        probability > 0 and reverse_pulled_back.get(path, Fraction(0)) == 0
        for path, probability in forward_law.items()
    )
    if positive_support_mismatch:
        divergence: float | None = None
    else:
        divergence = sum(
            float(probability)
            * math.log(float(probability / reverse_pulled_back[path]))
            for path, probability in forward_law.items()
            if probability > 0
        )
        if abs(divergence) < 1e-15:
            divergence = 0.0
    return DirectionalityProfile(
        profile_id=profile_id,
        horizon=horizon,
        reversal_convention=reversal.convention_id,
        reciprocal_support=mismatch_count == 0,
        support_mismatch_count=mismatch_count,
        total_variation=total_variation,
        kl_forward_to_reversed=divergence,
    )


# Support-only continuation operators.


def support_equivalent(
    left: FiniteControlledKernel,
    right: FiniteControlledKernel,
) -> bool:
    if left.states != right.states or left.actions != right.actions:
        return False
    return all(
        left.support_successors(state, action)
        == right.support_successors(state, action)
        for state in left.states
        for action in left.actions
    )


def support_predecessor(
    kernel: FiniteControlledKernel,
    candidate: Iterable[State],
    *,
    robust: bool,
) -> frozenset[State]:
    target = frozenset(candidate)
    if not target <= set(kernel.states):
        raise ValueError("candidate predecessor set contains unknown states")
    if robust:
        return frozenset(
            state
            for state in kernel.states
            if any(
                kernel.support_successors(state, action)
                and kernel.support_successors(state, action) <= target
                for action in kernel.actions
            )
        )
    return frozenset(
        state
        for state in kernel.states
        if any(
            kernel.support_successors(state, action) & target
            for action in kernel.actions
        )
    )


def bounded_support_reachability(
    kernel: FiniteControlledKernel,
    starts: Iterable[State],
    *,
    horizon: int,
) -> frozenset[State]:
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    reached = set(starts)
    if not reached <= set(kernel.states):
        raise ValueError("start set contains unknown states")
    frontier = set(reached)
    for _step in range(horizon):
        frontier = {
            target
            for state in frontier
            for action in kernel.actions
            for target in kernel.support_successors(state, action)
        }
        reached.update(frontier)
    return frozenset(reached)


def robust_support_viability_kernel(
    kernel: FiniteControlledKernel,
    safe_states: Iterable[State],
) -> frozenset[State]:
    retained = frozenset(safe_states)
    if not retained <= set(kernel.states):
        raise ValueError("safe set contains unknown states")
    while True:
        next_retained = frozenset(
            state
            for state in retained
            if any(
                kernel.support_successors(state, action)
                and kernel.support_successors(state, action) <= retained
                for action in kernel.actions
            )
        )
        if next_retained == retained:
            return retained
        retained = next_retained


def _powerset(items: tuple[str, ...]) -> tuple[frozenset[str], ...]:
    return tuple(
        frozenset(candidate)
        for size in range(len(items) + 1)
        for candidate in combinations(items, size)
    )


def support_blindness_audit(
    left: FiniteControlledKernel,
    right: FiniteControlledKernel,
    *,
    max_horizon: int,
) -> dict[str, Any]:
    """Exhaust all finite support observables declared by the protocol."""

    if max_horizon < 0:
        raise ValueError("max_horizon must be nonnegative")
    if left.states != right.states or left.actions != right.actions:
        raise ValueError("support audit requires common ordered states and actions")
    support_matches = support_equivalent(left, right)
    predecessor_failures: list[dict[str, Any]] = []
    viability_failures: list[dict[str, Any]] = []
    reachability_failures: list[dict[str, Any]] = []
    subsets = _powerset(left.states)
    for subset in subsets:
        for robust in (False, True):
            left_pre = support_predecessor(left, subset, robust=robust)
            right_pre = support_predecessor(right, subset, robust=robust)
            if left_pre != right_pre:
                predecessor_failures.append(
                    {
                        "candidate": sorted(subset),
                        "robust": robust,
                        "left": sorted(left_pre),
                        "right": sorted(right_pre),
                    }
                )
        left_viable = robust_support_viability_kernel(left, subset)
        right_viable = robust_support_viability_kernel(right, subset)
        if left_viable != right_viable:
            viability_failures.append(
                {
                    "safe": sorted(subset),
                    "left": sorted(left_viable),
                    "right": sorted(right_viable),
                }
            )
    for state in left.states:
        for horizon in range(max_horizon + 1):
            left_reach = bounded_support_reachability(left, (state,), horizon=horizon)
            right_reach = bounded_support_reachability(right, (state,), horizon=horizon)
            if left_reach != right_reach:
                reachability_failures.append(
                    {
                        "state": state,
                        "horizon": horizon,
                        "left": sorted(left_reach),
                        "right": sorted(right_reach),
                    }
                )
    return {
        "support_equivalent": support_matches,
        "subset_count": len(subsets),
        "checked_horizons": max_horizon + 1,
        "predecessor_failures": predecessor_failures,
        "viability_failures": viability_failures,
        "reachability_failures": reachability_failures,
        "all_support_observables_equal": (
            support_matches
            and not predecessor_failures
            and not viability_failures
            and not reachability_failures
        ),
    }


# Functional presentation contracts.


@dataclass(frozen=True)
class FunctionalPresentation:
    """A total functional map between action-labelled support systems."""

    presentation_id: str
    concrete: FiniteControlSystem
    abstract: FiniteControlSystem
    state_rows: tuple[tuple[State, State], ...]
    action_rows: tuple[tuple[Action, Action], ...]

    def __post_init__(self) -> None:
        if not self.presentation_id:
            raise ValueError("presentation_id must be nonempty")
        concrete_states = tuple(source for source, _target in self.state_rows)
        concrete_actions = tuple(source for source, _target in self.action_rows)
        if len(concrete_states) != len(set(concrete_states)):
            raise ValueError("state presentation must be functional")
        if len(concrete_actions) != len(set(concrete_actions)):
            raise ValueError("action presentation must be functional")
        if set(concrete_states) != set(self.concrete.states):
            raise ValueError("state presentation must be total on concrete states")
        if set(concrete_actions) != set(self.concrete.actions):
            raise ValueError("action presentation must be total on concrete actions")
        unknown_states = set(dict(self.state_rows).values()) - set(self.abstract.states)
        unknown_actions = set(dict(self.action_rows).values()) - set(self.abstract.actions)
        if unknown_states:
            raise ValueError(f"presentation maps to unknown abstract states: {unknown_states}")
        if unknown_actions:
            raise ValueError(f"presentation maps to unknown abstract actions: {unknown_actions}")

    @property
    def state_map(self) -> dict[State, State]:
        return dict(self.state_rows)

    @property
    def action_map(self) -> dict[Action, Action]:
        return dict(self.action_rows)

    @property
    def state_surjective(self) -> bool:
        return set(self.state_map.values()) == set(self.abstract.states)

    @property
    def action_surjective(self) -> bool:
        return set(self.action_map.values()) == set(self.abstract.actions)

    @property
    def state_bijective(self) -> bool:
        return self.state_surjective and len(self.state_rows) == len(self.abstract.states)

    @property
    def action_bijective(self) -> bool:
        return self.action_surjective and len(self.action_rows) == len(self.abstract.actions)

    def atom_respect_failures(self) -> tuple[dict[str, Any], ...]:
        return tuple(
            {
                "concrete_state": state,
                "abstract_state": self.state_map[state],
                "concrete_atoms": sorted(self.concrete.atoms_at(state)),
                "abstract_atoms": sorted(self.abstract.atoms_at(self.state_map[state])),
            }
            for state in self.concrete.states
            if self.concrete.atoms_at(state)
            != self.abstract.atoms_at(self.state_map[state])
        )

    def forward_failures(self) -> tuple[dict[str, Any], ...]:
        abstract_edges = set(self.abstract.transitions)
        return tuple(
            {
                "concrete_edge": [source, action, target],
                "missing_abstract_edge": [
                    self.state_map[source],
                    self.action_map[action],
                    self.state_map[target],
                ],
            }
            for source, action, target in self.concrete.transitions
            if (
                self.state_map[source],
                self.action_map[action],
                self.state_map[target],
            )
            not in abstract_edges
        )

    def back_failures(self) -> tuple[dict[str, Any], ...]:
        failures: list[dict[str, Any]] = []
        for source in self.concrete.states:
            abstract_source = self.state_map[source]
            for q_source, q_action, q_target in self.abstract.transitions:
                if q_source != abstract_source:
                    continue
                lifts = tuple(
                    (x_source, action, target)
                    for x_source, action, target in self.concrete.transitions
                    if x_source == source
                    and self.action_map[action] == q_action
                    and self.state_map[target] == q_target
                )
                if not lifts:
                    failures.append(
                        {
                            "concrete_source": source,
                            "abstract_edge": [q_source, q_action, q_target],
                        }
                    )
        return tuple(failures)

    def audit(self) -> dict[str, Any]:
        atom_failures = self.atom_respect_failures()
        forward_failures = self.forward_failures()
        back_failures = self.back_failures()
        atom_respects = not atom_failures
        forward = not forward_failures
        back = not back_failures
        surjective = self.state_surjective and self.action_surjective
        return {
            "presentation_id": self.presentation_id,
            "state_surjective": self.state_surjective,
            "action_surjective": self.action_surjective,
            "state_bijective": self.state_bijective,
            "action_bijective": self.action_bijective,
            "atom_respects": atom_respects,
            "forward": forward,
            "back": back,
            "forward_simulation": atom_respects and forward,
            "reflection": atom_respects and back,
            "functional_bisimulation": atom_respects and forward and back and surjective,
            "isomorphism": (
                atom_respects
                and forward
                and back
                and self.state_bijective
                and self.action_bijective
            ),
            "atom_failure_count": len(atom_failures),
            "forward_failure_count": len(forward_failures),
            "back_failure_count": len(back_failures),
            "atom_failures": list(atom_failures),
            "forward_failures": list(forward_failures),
            "back_failures": list(back_failures),
        }


# Candidate finite-state controllers and operational feature profiles.


@dataclass(frozen=True)
class FiniteStateController:
    """A total deterministic Mealy-style controller over world observations."""

    controller_id: str
    memory_states: tuple[str, ...]
    initial_memory: str
    observation_rows: tuple[ObservationRow, ...]
    update_rows: tuple[UpdateRow, ...]
    policy_rows: tuple[ControllerPolicyRow, ...]

    def __post_init__(self) -> None:
        if not self.controller_id:
            raise ValueError("controller_id must be nonempty")
        if not self.memory_states or len(self.memory_states) != len(set(self.memory_states)):
            raise ValueError("memory states must be nonempty and unique")
        if self.initial_memory not in self.memory_states:
            raise ValueError("initial memory must be declared")
        observation_states = tuple(state for state, _observation in self.observation_rows)
        if len(observation_states) != len(set(observation_states)):
            raise ValueError("world observation map must be functional")
        if any(not observation for _state, observation in self.observation_rows):
            raise ValueError("observations must be nonempty")

        observations = set(dict(self.observation_rows).values())
        update_keys = tuple(
            (memory, observation) for memory, observation, _target in self.update_rows
        )
        policy_keys = tuple(
            (memory, observation) for memory, observation, _action in self.policy_rows
        )
        required = {
            (memory, observation)
            for memory in self.memory_states
            for observation in observations
        }
        if len(update_keys) != len(set(update_keys)) or set(update_keys) != required:
            raise ValueError("controller update must be total and deterministic")
        if len(policy_keys) != len(set(policy_keys)) or set(policy_keys) != required:
            raise ValueError("controller policy must be total and deterministic")
        unknown_targets = {
            target for _memory, _observation, target in self.update_rows
        } - set(self.memory_states)
        if unknown_targets:
            raise ValueError(f"controller update has unknown memory targets: {unknown_targets}")

    @property
    def observation_map(self) -> dict[State, str]:
        return dict(self.observation_rows)

    @property
    def update_map(self) -> dict[tuple[str, str], str]:
        return {
            (memory, observation): target
            for memory, observation, target in self.update_rows
        }

    @property
    def policy_map(self) -> dict[tuple[str, str], Action]:
        return {
            (memory, observation): action
            for memory, observation, action in self.policy_rows
        }

    def validate(self, kernel: FiniteControlledKernel) -> None:
        if set(self.observation_map) != set(kernel.states):
            raise ValueError("controller observation map must be total on world states")
        unknown_actions = set(self.policy_map.values()) - set(kernel.actions)
        if unknown_actions:
            raise ValueError(f"controller policy contains unknown actions: {unknown_actions}")

    def observe(self, state: State) -> str:
        try:
            return self.observation_map[state]
        except KeyError as exc:
            raise KeyError(state) from exc

    def update(self, memory: str, observation: str) -> str:
        try:
            return self.update_map[(memory, observation)]
        except KeyError as exc:
            raise KeyError((memory, observation)) from exc

    def action(self, memory: str, observation: str) -> Action:
        try:
            return self.policy_map[(memory, observation)]
        except KeyError as exc:
            raise KeyError((memory, observation)) from exc


@dataclass(frozen=True, order=True)
class ClosedLoopNode:
    world_state: State
    memory_state: str


@dataclass(frozen=True)
class ProcessFeatureProfile:
    """Operational process features, deliberately short of valuerhood."""

    controller_id: str
    reachable_node_count: int
    reachable_memory_count: int
    causal_deformer: bool
    endogenous_record_selector: bool
    persistent_closed_loop: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "controller_id": self.controller_id,
            "reachable_node_count": self.reachable_node_count,
            "reachable_memory_count": self.reachable_memory_count,
            "causal_deformer": self.causal_deformer,
            "endogenous_record_selector": self.endogenous_record_selector,
            "persistent_closed_loop": self.persistent_closed_loop,
            "valuer_declared": False,
        }


def closed_loop_successors(
    kernel: FiniteControlledKernel,
    controller: FiniteStateController,
    node: ClosedLoopNode,
) -> frozenset[ClosedLoopNode]:
    controller.validate(kernel)
    observation = controller.observe(node.world_state)
    action = controller.action(node.memory_state, observation)
    return frozenset(
        ClosedLoopNode(
            world_state=target,
            memory_state=controller.update(
                node.memory_state,
                controller.observe(target),
            ),
        )
        for target in kernel.support_successors(node.world_state, action)
    )


def reachable_closed_loop_nodes(
    kernel: FiniteControlledKernel,
    controller: FiniteStateController,
    initial_world_states: Iterable[State],
) -> frozenset[ClosedLoopNode]:
    controller.validate(kernel)
    initial_states = frozenset(initial_world_states)
    if not initial_states or not initial_states <= set(kernel.states):
        raise ValueError("initial world-state support must be nonempty and declared")
    reached = {
        ClosedLoopNode(state, controller.initial_memory) for state in initial_states
    }
    queue = deque(reached)
    while queue:
        node = queue.popleft()
        for target in closed_loop_successors(kernel, controller, node):
            if target not in reached:
                reached.add(target)
                queue.append(target)
    return frozenset(reached)


def _has_reachable_cycle(
    adjacency: Mapping[ClosedLoopNode, frozenset[ClosedLoopNode]],
) -> bool:
    for start in adjacency:
        frontier = list(adjacency[start])
        seen: set[ClosedLoopNode] = set()
        while frontier:
            node = frontier.pop()
            if node == start:
                return True
            if node in seen:
                continue
            seen.add(node)
            frontier.extend(adjacency.get(node, frozenset()))
    return False


def process_feature_profile(
    kernel: FiniteControlledKernel,
    controller: FiniteStateController,
    *,
    initial_world_states: Iterable[State],
) -> ProcessFeatureProfile:
    """Audit causal effect, endogenous record use, and closed-loop persistence."""

    reached = reachable_closed_loop_nodes(kernel, controller, initial_world_states)
    adjacency = {
        node: closed_loop_successors(kernel, controller, node) for node in reached
    }
    causal_deformer = False
    for node in reached:
        observation = controller.observe(node.world_state)
        selected = controller.action(node.memory_state, observation)
        selected_distribution = kernel.distribution(node.world_state, selected)
        if any(
            kernel.distribution(node.world_state, alternative) != selected_distribution
            for alternative in kernel.actions
        ):
            causal_deformer = True
            break

    endogenous_record_selector = any(
        left.world_state == right.world_state
        and left.memory_state != right.memory_state
        and controller.action(
            left.memory_state,
            controller.observe(left.world_state),
        )
        != controller.action(
            right.memory_state,
            controller.observe(right.world_state),
        )
        for left, right in combinations(sorted(reached), 2)
    )
    return ProcessFeatureProfile(
        controller_id=controller.controller_id,
        reachable_node_count=len(reached),
        reachable_memory_count=len({node.memory_state for node in reached}),
        causal_deformer=causal_deformer,
        endogenous_record_selector=endogenous_record_selector,
        persistent_closed_loop=_has_reachable_cycle(adjacency),
    )


# Witness-retaining May-realization fibers.


@dataclass(frozen=True)
class CandidateRealizationClass:
    """Incidence columns with the same complete finite witness signature.

    This quotient is valid only for the v0 realization object, where a
    candidate has no structure beyond its complete incidence column. It is not
    an operational-process identity or fungibility criterion.
    """

    class_id: str
    members: tuple[str, ...]
    witness_ids: tuple[str, ...]

    def structural_payload(self) -> dict[str, Any]:
        return {
            "class_id": self.class_id,
            "witness_ids": list(self.witness_ids),
        }


@dataclass(frozen=True)
class FamilyFiber:
    """One finite candidate family together with all of its witnesses."""

    family: tuple[str, ...]
    witness_ids: tuple[str, ...]

    @property
    def nonempty(self) -> bool:
        return bool(self.witness_ids)

    def as_dict(self) -> dict[str, Any]:
        return {
            "family": list(self.family),
            "witness_ids": list(self.witness_ids),
            "nonempty": self.nonempty,
        }


@dataclass(frozen=True)
class FiniteRealizationSpace:
    """A finite witness-to-candidate incidence relation."""

    space_id: str
    candidate_ids: tuple[str, ...]
    witness_ids: tuple[str, ...]
    incidence_rows: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.space_id:
            raise ValueError("space_id must be nonempty")
        if len(self.candidate_ids) != len(set(self.candidate_ids)):
            raise ValueError("candidate identifiers must be unique")
        if len(self.witness_ids) != len(set(self.witness_ids)):
            raise ValueError("witness identifiers must be unique")
        if len(self.incidence_rows) != len(set(self.incidence_rows)):
            raise ValueError("incidence rows must be unique")
        unknown_candidates = {
            candidate for candidate, _witness in self.incidence_rows
        } - set(self.candidate_ids)
        unknown_witnesses = {
            witness for _candidate, witness in self.incidence_rows
        } - set(self.witness_ids)
        if unknown_candidates:
            raise ValueError(f"incidence has unknown candidates: {unknown_candidates}")
        if unknown_witnesses:
            raise ValueError(f"incidence has unknown witnesses: {unknown_witnesses}")

    def witnesses_for(self, candidate_id: str) -> frozenset[str]:
        if candidate_id not in self.candidate_ids:
            raise KeyError(candidate_id)
        return frozenset(
            witness
            for candidate, witness in self.incidence_rows
            if candidate == candidate_id
        )

    def realization_classes(self) -> tuple[CandidateRealizationClass, ...]:
        grouped: dict[tuple[str, ...], list[str]] = {}
        for candidate in self.candidate_ids:
            signature = tuple(sorted(self.witnesses_for(candidate)))
            grouped.setdefault(signature, []).append(candidate)
        classes = []
        for witness_ids, members in grouped.items():
            payload = json.dumps(
                {"witness_ids": witness_ids},
                sort_keys=True,
                separators=(",", ":"),
            )
            class_id = f"candidate:{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]}"
            classes.append(
                CandidateRealizationClass(
                    class_id=class_id,
                    members=tuple(sorted(members)),
                    witness_ids=witness_ids,
                )
            )
        return tuple(sorted(classes, key=lambda candidate_class: candidate_class.class_id))

    def quotient_omega(self) -> "DecoratedMayOmega":
        return DecoratedMayOmega.from_realization_space(self)


@dataclass(frozen=True)
class DecoratedMayOmega:
    """The complete finite May-realization object after exact duplicate quotient."""

    omega_id: str
    candidate_classes: tuple[CandidateRealizationClass, ...]
    witness_ids: tuple[str, ...]
    fibers: tuple[FamilyFiber, ...]

    @classmethod
    def from_realization_space(
        cls,
        space: FiniteRealizationSpace,
    ) -> "DecoratedMayOmega":
        candidate_classes = space.realization_classes()
        class_ids = tuple(
            candidate_class.class_id for candidate_class in candidate_classes
        )
        signature_map = {
            candidate_class.class_id: frozenset(candidate_class.witness_ids)
            for candidate_class in candidate_classes
        }
        fibers: list[FamilyFiber] = []
        for family in _powerset(class_ids):
            witnesses = set(space.witness_ids)
            for candidate_class in family:
                witnesses.intersection_update(signature_map[candidate_class])
            fibers.append(
                FamilyFiber(
                    family=tuple(sorted(family)),
                    witness_ids=tuple(sorted(witnesses)),
                )
            )
        return cls(
            omega_id=f"omega:{space.space_id}",
            candidate_classes=candidate_classes,
            witness_ids=space.witness_ids,
            fibers=tuple(sorted(fibers, key=lambda fiber: (len(fiber.family), fiber.family))),
        )

    @property
    def class_ids(self) -> tuple[str, ...]:
        return tuple(
            candidate_class.class_id for candidate_class in self.candidate_classes
        )

    def fiber(self, family: Iterable[str]) -> FamilyFiber:
        family_tuple = tuple(sorted(set(family)))
        if not set(family_tuple) <= set(self.class_ids):
            raise ValueError("family contains an unknown candidate class")
        try:
            return next(fiber for fiber in self.fibers if fiber.family == family_tuple)
        except StopIteration as exc:
            raise AssertionError("complete finite fiber table is missing a family") from exc

    def compatible_families(self) -> tuple[tuple[str, ...], ...]:
        return tuple(fiber.family for fiber in self.fibers if fiber.nonempty)

    def maximal_faces(self) -> tuple[tuple[str, ...], ...]:
        compatible = tuple(
            frozenset(family)
            for family in self.compatible_families()
            if family
        )
        maximal = tuple(
            family
            for family in compatible
            if not any(family < other for other in compatible)
        )
        return tuple(sorted((tuple(sorted(face)) for face in maximal)))

    def downward_closure_failures(self) -> tuple[dict[str, Any], ...]:
        compatible = set(self.compatible_families())
        failures = []
        for family in compatible:
            for subset in _powerset(tuple(family)):
                subset_tuple = tuple(sorted(subset))
                if subset_tuple not in compatible:
                    failures.append(
                        {
                            "family": list(family),
                            "missing_subset": list(subset_tuple),
                        }
                    )
        return tuple(failures)

    def restriction_failures(self) -> tuple[dict[str, Any], ...]:
        """Check antitone fiber inclusion, identity, and composition."""

        failures: list[dict[str, Any]] = []
        family_sets = [frozenset(fiber.family) for fiber in self.fibers]
        for small in family_sets:
            small_witnesses = set(self.fiber(small).witness_ids)
            if set(self.fiber(small).witness_ids) != small_witnesses:
                failures.append({"kind": "identity", "family": sorted(small)})
            for large in family_sets:
                if not small <= large:
                    continue
                large_witnesses = set(self.fiber(large).witness_ids)
                if not large_witnesses <= small_witnesses:
                    failures.append(
                        {
                            "kind": "antitone",
                            "small": sorted(small),
                            "large": sorted(large),
                        }
                    )
                for largest in family_sets:
                    if not large <= largest:
                        continue
                    direct = set(self.fiber(largest).witness_ids) & small_witnesses
                    via_large = (
                        set(self.fiber(largest).witness_ids)
                        & large_witnesses
                        & small_witnesses
                    )
                    if direct != via_large:
                        failures.append(
                            {
                                "kind": "composition",
                                "small": sorted(small),
                                "large": sorted(large),
                                "largest": sorted(largest),
                            }
                        )
        return tuple(failures)

    def structural_payload(self) -> dict[str, Any]:
        """Payload excluding duplicate presentation member names."""

        return {
            "candidate_classes": [
                candidate_class.structural_payload()
                for candidate_class in self.candidate_classes
            ],
            "witness_ids": list(self.witness_ids),
            "fibers": [fiber.as_dict() for fiber in self.fibers],
            "maximal_faces": [list(face) for face in self.maximal_faces()],
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "omega_id": self.omega_id,
            "candidate_classes": [
                {
                    **candidate_class.structural_payload(),
                    "members": list(candidate_class.members),
                }
                for candidate_class in self.candidate_classes
            ],
            "witness_ids": list(self.witness_ids),
            "fibers": [fiber.as_dict() for fiber in self.fibers],
            "compatible_families": [
                list(family) for family in self.compatible_families()
            ],
            "maximal_faces": [list(face) for face in self.maximal_faces()],
            "downward_closure_failures": list(self.downward_closure_failures()),
            "restriction_failures": list(self.restriction_failures()),
        }


def realization_space_from_assignment(
    assignment: SharedActionAssignment,
    *,
    duplicate_candidate: str | None = None,
) -> FiniteRealizationSpace:
    candidate_ids = list(COMPONENTS)
    incidence = [
        (component, f"history:{action}")
        for component in COMPONENTS
        for action in SHARED_ACTIONS
        if action in assignment.allowed_for(component)
    ]
    if duplicate_candidate is not None:
        if duplicate_candidate not in COMPONENTS:
            raise ValueError("duplicate candidate must name a retained component")
        duplicate_id = f"{duplicate_candidate}_copy"
        candidate_ids.append(duplicate_id)
        incidence.extend(
            (duplicate_id, f"history:{action}")
            for action in SHARED_ACTIONS
            if action in assignment.allowed_for(duplicate_candidate)
        )
    return FiniteRealizationSpace(
        space_id=(
            assignment.assignment_id
            if duplicate_candidate is None
            else f"{assignment.assignment_id}__duplicate_{duplicate_candidate}"
        ),
        candidate_ids=tuple(candidate_ids),
        witness_ids=tuple(f"history:{action}" for action in SHARED_ACTIONS),
        incidence_rows=tuple(incidence),
    )


# Preregistered finite fixtures and retained summary.


def _one_action_policy(
    kernel: FiniteControlledKernel,
    *,
    policy_id: str,
    action: Action,
) -> DeterministicPolicy:
    return DeterministicPolicy(
        policy_id=policy_id,
        rows=tuple((state, action) for state in kernel.states),
    )


def cycle_kernel(
    *,
    system_id: str,
    clockwise_weight: Fraction,
) -> FiniteControlledKernel:
    if clockwise_weight <= 0 or clockwise_weight >= 1:
        raise ValueError("cycle weights must retain reciprocal support")
    states = ("s0", "s1", "s2")
    counterclockwise_weight = 1 - clockwise_weight
    transitions: list[WeightRow] = []
    for index, state in enumerate(states):
        transitions.extend(
            (
                (
                    state,
                    "advance",
                    states[(index + 1) % len(states)],
                    clockwise_weight,
                ),
                (
                    state,
                    "advance",
                    states[(index - 1) % len(states)],
                    counterclockwise_weight,
                ),
            )
        )
    return FiniteControlledKernel(
        system_id=system_id,
        states=states,
        actions=("advance",),
        transitions=tuple(transitions),
    )


def cycle_directionality_profile(
    kernel: FiniteControlledKernel,
    *,
    horizon: int,
) -> DirectionalityProfile:
    policy = _one_action_policy(
        kernel,
        policy_id=f"{kernel.system_id}__policy",
        action="advance",
    )
    stationary = tuple(
        (state, Fraction(1, len(kernel.states))) for state in kernel.states
    )
    reversal = PathReversal(
        convention_id="identity-action_path-reversal",
        action_rows=(("advance", "advance"),),
    )
    return compare_oriented_path_laws(
        profile_id=f"{kernel.system_id}__directionality",
        forward_kernel=kernel,
        forward_policy=policy,
        forward_initial=stationary,
        reverse_kernel=kernel,
        reverse_policy=policy,
        reverse_initial=stationary,
        reversal=reversal,
        horizon=horizon,
    )


def probabilistic_nonreturn_fixture() -> dict[str, Any]:
    kernel = FiniteControlledKernel(
        system_id="finite_horizon_probabilistic_nonreturn",
        states=("origin", "away"),
        actions=("advance",),
        transitions=(
            ("origin", "advance", "away", Fraction(1)),
            ("away", "advance", "origin", Fraction(1, 10)),
            ("away", "advance", "away", Fraction(9, 10)),
        ),
    )
    policy = _one_action_policy(kernel, policy_id="nonreturn_policy", action="advance")
    law = finite_path_law(
        kernel,
        policy,
        (("origin", Fraction(1)),),
        horizon=2,
    )
    return_probability = sum(
        probability for path, probability in law.items() if path.end == "origin"
    )
    return {
        "return_probability_at_horizon_2": fraction_to_text(return_probability),
        "nonreturn_probability_at_horizon_2": fraction_to_text(1 - return_probability),
        "support_return_possible": "origin"
        in bounded_support_reachability(kernel, ("away",), horizon=1),
    }


def _policy_contraction_kernel() -> FiniteControlledKernel:
    states = ("open", "left", "right", "sink")
    transitions: list[WeightRow] = [
        ("open", "preserve", "left", Fraction(1, 2)),
        ("open", "preserve", "right", Fraction(1, 2)),
        ("left", "preserve", "open", Fraction(1)),
        ("right", "preserve", "open", Fraction(1)),
        ("sink", "preserve", "sink", Fraction(1)),
    ]
    transitions.extend(
        (state, "collapse", "sink", Fraction(1)) for state in states
    )
    return FiniteControlledKernel(
        system_id="policy_induced_functional_contraction",
        states=states,
        actions=("preserve", "collapse"),
        transitions=tuple(transitions),
        atoms=(
            ("open", frozenset({"live"})),
            ("left", frozenset({"live"})),
            ("right", frozenset({"live"})),
        ),
    )


def policy_contraction_fixture() -> dict[str, Any]:
    kernel = _policy_contraction_kernel()
    preserve_policy = _one_action_policy(
        kernel,
        policy_id="preserve_policy",
        action="preserve",
    )
    collapse_policy = _one_action_policy(
        kernel,
        policy_id="collapse_policy",
        action="collapse",
    )
    initial = (("open", Fraction(1)),)
    preserve_law = finite_path_law(
        kernel,
        preserve_policy,
        initial,
        horizon=2,
    )
    collapse_law = finite_path_law(
        kernel,
        collapse_policy,
        initial,
        horizon=2,
    )
    live_states = frozenset({"open", "left", "right"})
    viable = robust_support_viability_kernel(kernel, live_states)
    return {
        "preserve_path_support_size": len(preserve_law),
        "collapse_path_support_size": len(collapse_law),
        "preserve_terminal_states": sorted({path.end for path in preserve_law}),
        "collapse_terminal_states": sorted({path.end for path in collapse_law}),
        "live_viability_kernel": sorted(viable),
        "collapse_forecloses_live_support": all(
            path.end == "sink" for path in collapse_law
        ),
    }


def support_reachability_closure(
    kernel: FiniteControlledKernel,
    state: State,
) -> frozenset[State]:
    return bounded_support_reachability(
        kernel,
        (state,),
        horizon=len(kernel.states),
    )


def support_irreversible_pairs(
    kernel: FiniteControlledKernel,
) -> tuple[tuple[State, State], ...]:
    closures = {
        state: support_reachability_closure(kernel, state) for state in kernel.states
    }
    return tuple(
        (left, right)
        for left in kernel.states
        for right in kernel.states
        if right in closures[left] and left not in closures[right]
    )


def absorbing_control_fixture() -> dict[str, Any]:
    kernel = _policy_contraction_kernel()
    irreversible_pairs = support_irreversible_pairs(kernel)
    return {
        "irreversible_pair_count": len(irreversible_pairs),
        "irreversible_pairs": [list(pair) for pair in irreversible_pairs],
        "diagnostic_only": True,
    }


def residual_continuation_fixture() -> dict[str, Any]:
    kernel = cycle_kernel(
        system_id="residual_continuation_cycle",
        clockwise_weight=Fraction(3, 4),
    )
    policy = _one_action_policy(
        kernel,
        policy_id="residual_continuation_policy",
        action="advance",
    )
    prefix = FinitePath(states=("s0", "s1"), actions=("advance",))
    residual = residual_continuation_law(
        kernel,
        policy,
        prefix,
        remaining_horizon=2,
    )
    return {
        "prefix_end": prefix.end,
        "remaining_horizon": 2,
        "path_count": len(residual),
        "total_probability": fraction_to_text(
            sum(residual.values(), Fraction(0))
        ),
        "all_paths_start_at_prefix_end": all(
            path.start == prefix.end for path in residual
        ),
    }


def directionality_fixture_ladder(*, horizon: int = 3) -> dict[str, Any]:
    balanced = cycle_kernel(
        system_id="directionally_null_cycle",
        clockwise_weight=Fraction(1, 2),
    )
    biased = cycle_kernel(
        system_id="biased_reciprocal_support_cycle",
        clockwise_weight=Fraction(3, 4),
    )
    null_profile = cycle_directionality_profile(balanced, horizon=horizon)
    biased_profile = cycle_directionality_profile(biased, horizon=horizon)
    reversal = PathReversal(
        convention_id="identity-action_path-reversal",
        action_rows=(("advance", "advance"),),
    )
    sample_path = FinitePath(
        states=("s0", "s1", "s2"),
        actions=("advance", "advance"),
    )
    return {
        "reversal_round_trip": (
            reversal.reverse(reversal.reverse(sample_path)) == sample_path
        ),
        "null": null_profile.as_dict(),
        "biased_reciprocal": biased_profile.as_dict(),
        "residual_continuation": residual_continuation_fixture(),
        "probabilistic_nonreturn": probabilistic_nonreturn_fixture(),
        "policy_contraction": policy_contraction_fixture(),
        "support_asymmetric_absorbing": absorbing_control_fixture(),
    }


def support_blindness_fixture(*, horizon: int = 3) -> dict[str, Any]:
    balanced = cycle_kernel(
        system_id="support_blind_balanced",
        clockwise_weight=Fraction(1, 2),
    )
    biased = cycle_kernel(
        system_id="support_blind_biased",
        clockwise_weight=Fraction(3, 4),
    )
    audit = support_blindness_audit(balanced, biased, max_horizon=horizon)
    balanced_profile = cycle_directionality_profile(balanced, horizon=horizon)
    biased_profile = cycle_directionality_profile(biased, horizon=horizon)
    return {
        **audit,
        "balanced_directionality": balanced_profile.as_dict(),
        "biased_directionality": biased_profile.as_dict(),
        "directionality_separates": (
            balanced_profile.statistically_directional is False
            and biased_profile.statistically_directional is True
        ),
    }


def _relabel_support_system(
    system: FiniteControlSystem,
    *,
    state_mapping: Mapping[State, State],
    action_mapping: Mapping[Action, Action],
    system_id: str,
) -> FiniteControlSystem:
    return system.relabel(
        state_mapping=state_mapping,
        action_mapping=action_mapping,
        system_id=system_id,
    )


def presentation_fixture_suite(*, horizon: int = 3) -> dict[str, Any]:
    biased_kernel = cycle_kernel(
        system_id="presentation_biased_cycle",
        clockwise_weight=Fraction(3, 4),
    )
    concrete_cycle = biased_kernel.support_system()
    state_mapping = {"s0": "q0", "s1": "q1", "s2": "q2"}
    action_mapping = {"advance": "tick"}
    relabeled_cycle = _relabel_support_system(
        concrete_cycle,
        state_mapping=state_mapping,
        action_mapping=action_mapping,
        system_id="relabeled_cycle",
    )
    exact = FunctionalPresentation(
        presentation_id="exact_relabeling",
        concrete=concrete_cycle,
        abstract=relabeled_cycle,
        state_rows=tuple(state_mapping.items()),
        action_rows=tuple(action_mapping.items()),
    ).audit()

    duplicate_concrete = FiniteControlSystem(
        system_id="duplicate_concrete",
        states=("root", "p1", "p2"),
        actions=("go", "stay"),
        transitions=(
            ("root", "go", "p1"),
            ("root", "go", "p2"),
            ("p1", "stay", "p1"),
            ("p2", "stay", "p2"),
        ),
        atoms=(
            ("root", frozenset({"root"})),
            ("p1", frozenset({"persistent"})),
            ("p2", frozenset({"persistent"})),
        ),
    )
    duplicate_abstract = FiniteControlSystem(
        system_id="duplicate_abstract",
        states=("root", "p"),
        actions=("go", "stay"),
        transitions=(
            ("root", "go", "p"),
            ("p", "stay", "p"),
        ),
        atoms=(
            ("root", frozenset({"root"})),
            ("p", frozenset({"persistent"})),
        ),
    )
    duplicate = FunctionalPresentation(
        presentation_id="bisimilar_duplicate_quotient",
        concrete=duplicate_concrete,
        abstract=duplicate_abstract,
        state_rows=(("root", "root"), ("p1", "p"), ("p2", "p")),
        action_rows=(("go", "go"), ("stay", "stay")),
    ).audit()

    forward_concrete = FiniteControlSystem(
        system_id="forward_failure_concrete",
        states=("x", "y"),
        actions=("go",),
        transitions=(("x", "go", "y"),),
    )
    forward_abstract = FiniteControlSystem(
        system_id="forward_failure_abstract",
        states=("q", "r"),
        actions=("go",),
        transitions=(),
    )
    forward_failure = FunctionalPresentation(
        presentation_id="forward_failure",
        concrete=forward_concrete,
        abstract=forward_abstract,
        state_rows=(("x", "q"), ("y", "r")),
        action_rows=(("go", "go"),),
    ).audit()

    back_concrete = FiniteControlSystem(
        system_id="back_failure_concrete",
        states=("x", "y"),
        actions=("go",),
        transitions=(),
    )
    back_abstract = FiniteControlSystem(
        system_id="back_failure_abstract",
        states=("q", "r"),
        actions=("go",),
        transitions=(("q", "go", "r"),),
    )
    back_failure = FunctionalPresentation(
        presentation_id="back_failure",
        concrete=back_concrete,
        abstract=back_abstract,
        state_rows=(("x", "q"), ("y", "r")),
        action_rows=(("go", "go"),),
    ).audit()

    atom_concrete = FiniteControlSystem(
        system_id="atom_failure_concrete",
        states=("x",),
        actions=("stay",),
        transitions=(("x", "stay", "x"),),
        atoms=(("x", frozenset({"live"})),),
    )
    atom_abstract = FiniteControlSystem(
        system_id="atom_failure_abstract",
        states=("q",),
        actions=("stay",),
        transitions=(("q", "stay", "q"),),
    )
    atom_failure = FunctionalPresentation(
        presentation_id="atom_failure",
        concrete=atom_concrete,
        abstract=atom_abstract,
        state_rows=(("x", "q"),),
        action_rows=(("stay", "stay"),),
    ).audit()

    collapsed_support = FiniteControlSystem(
        system_id="collapsed_cycle_support",
        states=("q",),
        actions=("advance",),
        transitions=(("q", "advance", "q"),),
    )
    grain_hiding_presentation = FunctionalPresentation(
        presentation_id="support_bisimulation_hides_weighted_grain",
        concrete=concrete_cycle,
        abstract=collapsed_support,
        state_rows=(("s0", "q"), ("s1", "q"), ("s2", "q")),
        action_rows=(("advance", "advance"),),
    ).audit()
    collapsed_kernel = FiniteControlledKernel(
        system_id="collapsed_cycle_kernel",
        states=("q",),
        actions=("advance",),
        transitions=(("q", "advance", "q", Fraction(1)),),
    )
    concrete_directionality = cycle_directionality_profile(
        biased_kernel,
        horizon=horizon,
    )
    abstract_directionality = cycle_directionality_profile(
        collapsed_kernel,
        horizon=horizon,
    )
    return {
        "exact_relabeling": exact,
        "bisimilar_duplicate": duplicate,
        "forward_failure": forward_failure,
        "back_failure": back_failure,
        "atom_failure": atom_failure,
        "weighted_grain_hidden": {
            "presentation": grain_hiding_presentation,
            "concrete_directionality": concrete_directionality.as_dict(),
            "abstract_directionality": abstract_directionality.as_dict(),
            "support_bisimulation_passes": grain_hiding_presentation[
                "functional_bisimulation"
            ],
            "weighted_directionality_changes": (
                concrete_directionality.statistically_directional
                and not abstract_directionality.statistically_directional
            ),
        },
    }


def _passive_kernel(*, inject_agent_label: bool) -> FiniteControlledKernel:
    return FiniteControlledKernel(
        system_id=(
            "passive_labeled_kernel" if inject_agent_label else "passive_kernel"
        ),
        states=("rest",),
        actions=("a", "b"),
        transitions=(
            ("rest", "a", "rest", Fraction(1)),
            ("rest", "b", "rest", Fraction(1)),
        ),
        atoms=(
            (("rest", frozenset({"agent"})),)
            if inject_agent_label
            else ()
        ),
    )


def _singleton_controller(
    kernel: FiniteControlledKernel,
    *,
    controller_id: str,
    selected_action: Action,
) -> FiniteStateController:
    return FiniteStateController(
        controller_id=controller_id,
        memory_states=("m",),
        initial_memory="m",
        observation_rows=tuple((state, "present") for state in kernel.states),
        update_rows=(("m", "present", "m"),),
        policy_rows=(("m", "present", selected_action),),
    )


def _record_selector_kernel() -> FiniteControlledKernel:
    states = (
        "start",
        "alpha",
        "beta",
        "hub",
        "good_alpha",
        "good_beta",
        "bad",
    )
    actions = ("wait", "choose_alpha", "choose_beta")
    transitions: list[WeightRow] = []
    for action in actions:
        transitions.extend(
            (
                ("start", action, "alpha", Fraction(1, 2)),
                ("start", action, "beta", Fraction(1, 2)),
                ("alpha", action, "hub", Fraction(1)),
                ("beta", action, "hub", Fraction(1)),
                ("good_alpha", action, "start", Fraction(1)),
                ("good_beta", action, "start", Fraction(1)),
                ("bad", action, "start", Fraction(1)),
            )
        )
    transitions.extend(
        (
            ("hub", "wait", "bad", Fraction(1)),
            ("hub", "choose_alpha", "good_alpha", Fraction(1)),
            ("hub", "choose_beta", "good_beta", Fraction(1)),
        )
    )
    return FiniteControlledKernel(
        system_id="record_selector_world",
        states=states,
        actions=actions,
        transitions=tuple(transitions),
        atoms=(
            ("alpha", frozenset({"branch:alpha"})),
            ("beta", frozenset({"branch:beta"})),
            ("hub", frozenset({"decision"})),
        ),
    )


def _memoryless_effectful_controller(
    kernel: FiniteControlledKernel,
) -> FiniteStateController:
    return FiniteStateController(
        controller_id="effectful_memoryless",
        memory_states=("m",),
        initial_memory="m",
        observation_rows=tuple((state, "present") for state in kernel.states),
        update_rows=(("m", "present", "m"),),
        policy_rows=(("m", "present", "choose_alpha"),),
    )


def _record_sensitive_controller(
    kernel: FiniteControlledKernel,
) -> FiniteStateController:
    observation_rows = tuple(
        (
            state,
            "alpha"
            if state == "alpha"
            else "beta"
            if state == "beta"
            else "neutral",
        )
        for state in kernel.states
    )
    memory_states = ("neutral", "saw_alpha", "saw_beta")
    observations = ("alpha", "beta", "neutral")
    update_rows = tuple(
        (
            memory,
            observation,
            "saw_alpha"
            if observation == "alpha"
            else "saw_beta"
            if observation == "beta"
            else memory,
        )
        for memory in memory_states
        for observation in observations
    )
    policy_rows = tuple(
        (
            memory,
            observation,
            "choose_alpha"
            if memory == "saw_alpha"
            else "choose_beta"
            if memory == "saw_beta"
            else "wait",
        )
        for memory in memory_states
        for observation in observations
    )
    return FiniteStateController(
        controller_id="record_sensitive_selector",
        memory_states=memory_states,
        initial_memory="neutral",
        observation_rows=observation_rows,
        update_rows=update_rows,
        policy_rows=policy_rows,
    )


def process_fixture_suite() -> dict[str, Any]:
    passive_kernel = _passive_kernel(inject_agent_label=False)
    passive_controller = _singleton_controller(
        passive_kernel,
        controller_id="passive_pattern",
        selected_action="a",
    )
    passive = process_feature_profile(
        passive_kernel,
        passive_controller,
        initial_world_states=("rest",),
    )

    labeled_kernel = _passive_kernel(inject_agent_label=True)
    labeled_controller = _singleton_controller(
        labeled_kernel,
        controller_id="presentation_injected_agent_label",
        selected_action="a",
    )
    labeled = process_feature_profile(
        labeled_kernel,
        labeled_controller,
        initial_world_states=("rest",),
    )

    selector_kernel = _record_selector_kernel()
    memoryless = process_feature_profile(
        selector_kernel,
        _memoryless_effectful_controller(selector_kernel),
        initial_world_states=("start",),
    )
    record_sensitive = process_feature_profile(
        selector_kernel,
        _record_sensitive_controller(selector_kernel),
        initial_world_states=("start",),
    )

    def structural_features(profile: ProcessFeatureProfile) -> tuple[bool, bool, bool]:
        return (
            profile.causal_deformer,
            profile.endogenous_record_selector,
            profile.persistent_closed_loop,
        )

    return {
        "passive": passive.as_dict(),
        "effectful_memoryless": memoryless.as_dict(),
        "record_sensitive": record_sensitive.as_dict(),
        "injected_label": labeled.as_dict(),
        "injected_label_changes_features": (
            structural_features(passive) != structural_features(labeled)
        ),
    }


def hollow_triangle_assignment() -> SharedActionAssignment:
    return SharedActionAssignment(
        (
            ("A", ("a0", "a1")),
            ("B", ("a0", "a2")),
            ("C", ("a1", "a2")),
        )
    )


def omega_fixture_suite() -> dict[str, Any]:
    assignment = hollow_triangle_assignment()
    base_space = realization_space_from_assignment(assignment)
    duplicate_space = realization_space_from_assignment(
        assignment,
        duplicate_candidate="A",
    )
    omega = base_space.quotient_omega()
    duplicate_omega = duplicate_space.quotient_omega()
    class_by_member = {
        member: candidate_class.class_id
        for candidate_class in omega.candidate_classes
        for member in candidate_class.members
    }
    singleton_fibers = {
        component: omega.fiber((class_by_member[component],)).witness_ids
        for component in COMPONENTS
    }
    pair_fibers = {
        "+".join(pair): omega.fiber(
            tuple(class_by_member[component] for component in pair)
        ).witness_ids
        for pair in combinations(COMPONENTS, 2)
    }
    triple_family = tuple(class_by_member[component] for component in COMPONENTS)
    triple_fiber = omega.fiber(triple_family).witness_ids
    base_payload = omega.structural_payload()
    duplicate_payload = duplicate_omega.structural_payload()
    return {
        "assignment_id": assignment.assignment_id,
        "expected_generated_assignment_id": (
            "shared_A_a0-a1__B_a0-a2__C_a1-a2"
        ),
        "candidate_class_count": len(omega.candidate_classes),
        "raw_candidate_count": len(base_space.candidate_ids),
        "duplicate_raw_candidate_count": len(duplicate_space.candidate_ids),
        "duplicate_quotient_class_count": len(duplicate_omega.candidate_classes),
        "singleton_fibers": {
            family: list(witnesses) for family, witnesses in singleton_fibers.items()
        },
        "pair_fibers": {
            family: list(witnesses) for family, witnesses in pair_fibers.items()
        },
        "triple_fiber": list(triple_fiber),
        "all_singletons_nonempty": all(singleton_fibers.values()),
        "all_pairs_nonempty": all(pair_fibers.values()),
        "triple_empty": not triple_fiber,
        "maximal_faces": [list(face) for face in omega.maximal_faces()],
        "maximal_face_count": len(omega.maximal_faces()),
        "greatest_face_exists": len(omega.maximal_faces()) == 1,
        "downward_closure_failures": list(omega.downward_closure_failures()),
        "restriction_failures": list(omega.restriction_failures()),
        "duplicate_structural_payload_equal": base_payload == duplicate_payload,
        "omega": omega.as_dict(),
        "duplicate_omega": duplicate_omega.as_dict(),
    }


def alpha_omega_foundation_summary(*, horizon: int = 3) -> dict[str, Any]:
    directionality = directionality_fixture_ladder(horizon=horizon)
    support = support_blindness_fixture(horizon=horizon)
    presentations = presentation_fixture_suite(horizon=horizon)
    processes = process_fixture_suite()
    omega = omega_fixture_suite()

    case_results = {
        "directionally_null_reversible": (
            directionality["null"]["statistically_directional"] is False
            and directionality["null"]["kl_forward_to_reversed"] == 0.0
        ),
        "biased_reciprocal_support": (
            directionality["biased_reciprocal"]["statistically_directional"] is True
            and directionality["biased_reciprocal"]["reciprocal_support"] is True
        ),
        "residual_continuation_law": (
            directionality["residual_continuation"]["total_probability"] == "1"
            and directionality["residual_continuation"][
                "all_paths_start_at_prefix_end"
            ]
            is True
            and directionality["residual_continuation"]["remaining_horizon"] == 2
        ),
        "finite_horizon_probabilistic_nonreturn": (
            directionality["probabilistic_nonreturn"][
                "return_probability_at_horizon_2"
            ]
            == "1/10"
            and directionality["probabilistic_nonreturn"]["support_return_possible"]
            is True
        ),
        "policy_induced_functional_contraction": (
            directionality["policy_contraction"][
                "collapse_forecloses_live_support"
            ]
            is True
            and directionality["policy_contraction"]["preserve_path_support_size"]
            > directionality["policy_contraction"]["collapse_path_support_size"]
        ),
        "support_asymmetric_diagnostic": (
            directionality["support_asymmetric_absorbing"][
                "irreversible_pair_count"
            ]
            > 0
            and directionality["support_asymmetric_absorbing"]["diagnostic_only"]
            is True
        ),
        "support_blindness": (
            support["all_support_observables_equal"] is True
            and support["directionality_separates"] is True
        ),
        "presentation_contracts": (
            presentations["exact_relabeling"]["isomorphism"] is True
            and presentations["bisimilar_duplicate"]["functional_bisimulation"]
            is True
            and presentations["forward_failure"]["forward_failure_count"] > 0
            and presentations["back_failure"]["back_failure_count"] > 0
            and presentations["atom_failure"]["atom_failure_count"] > 0
            and presentations["weighted_grain_hidden"][
                "support_bisimulation_passes"
            ]
            is True
            and presentations["weighted_grain_hidden"][
                "weighted_directionality_changes"
            ]
            is True
        ),
        "candidate_process_filtration": (
            processes["passive"]["causal_deformer"] is False
            and processes["effectful_memoryless"]["causal_deformer"] is True
            and processes["effectful_memoryless"]["endogenous_record_selector"]
            is False
            and processes["record_sensitive"]["endogenous_record_selector"] is True
            and processes["record_sensitive"]["persistent_closed_loop"] is True
            and processes["injected_label_changes_features"] is False
        ),
        "decorated_may_omega": (
            omega["assignment_id"] == omega["expected_generated_assignment_id"]
            and omega["all_singletons_nonempty"] is True
            and omega["all_pairs_nonempty"] is True
            and omega["triple_empty"] is True
            and omega["maximal_face_count"] == 3
            and omega["greatest_face_exists"] is False
            and not omega["downward_closure_failures"]
            and not omega["restriction_failures"]
            and omega["duplicate_structural_payload_equal"] is True
        ),
    }
    kill_conditions = {
        "inconsistent_path_reversal": (
            not directionality["reversal_round_trip"]
            or directionality["null"]["reversal_convention"]
            != directionality["biased_reciprocal"]["reversal_convention"]
        ),
        "support_only_separates_equal_support": (
            not support["all_support_observables_equal"]
        ),
        "weights_discarded_before_directionality": (
            not support["directionality_separates"]
        ),
        "bisimulation_missing_required_clause": (
            presentations["forward_failure"]["functional_bisimulation"]
            or presentations["back_failure"]["functional_bisimulation"]
            or presentations["atom_failure"]["functional_bisimulation"]
        ),
        "injected_label_creates_process_evidence": processes[
            "injected_label_changes_features"
        ],
        "fibers_replaced_by_graph": not bool(omega["omega"]["fibers"]),
        "duplicate_candidate_inflates_omega": (
            not omega["duplicate_structural_payload_equal"]
        ),
        "pairwise_treated_as_joint": not omega["triple_empty"],
        "maximal_face_selected": "selected_face" in omega["omega"],
    }
    retained = all(case_results.values()) and not any(kill_conditions.values())
    return {
        "status": "PASS" if retained else "REVIEW",
        "verdict": "retained" if retained else "partial",
        "protocol_doc": PROTOCOL_DOC,
        "horizon": horizon,
        "case_results": case_results,
        "kill_conditions": kill_conditions,
        "directionality": directionality,
        "support_blindness": support,
        "presentations": presentations,
        "processes": processes,
        "omega": omega,
        "primary_claim": (
            "Finite oriented path laws, support-only continuation operators, "
            "presentation contracts, process feature profiles, and a "
            "witness-retaining May-Omega object coexist in one audited adapter."
        ),
        "not_claimed": (
            "value",
            "standing",
            "personhood",
            "consciousness",
            "moral agency",
            "thermodynamic universality",
            "preferred physical orientation",
            "normative allegiance",
            "lushness as an imperative",
            "Omega as a realized moral object",
        ),
    }


def directionality_rows(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    directionality = summary["directionality"]
    return [
        {
            "case": case,
            "horizon": profile["horizon"],
            "reciprocal_support": profile["reciprocal_support"],
            "total_variation": profile["total_variation"],
            "kl_forward_to_reversed": profile["kl_forward_to_reversed"],
            "statistically_directional": profile["statistically_directional"],
        }
        for case, profile in (
            ("null", directionality["null"]),
            ("biased_reciprocal", directionality["biased_reciprocal"]),
        )
    ]


def process_rows(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    processes = summary["processes"]
    return [
        {
            "case": case,
            "controller_id": profile["controller_id"],
            "reachable_node_count": profile["reachable_node_count"],
            "reachable_memory_count": profile["reachable_memory_count"],
            "causal_deformer": profile["causal_deformer"],
            "endogenous_record_selector": profile["endogenous_record_selector"],
            "persistent_closed_loop": profile["persistent_closed_loop"],
            "valuer_declared": profile["valuer_declared"],
        }
        for case, profile in (
            ("passive", processes["passive"]),
            ("effectful_memoryless", processes["effectful_memoryless"]),
            ("record_sensitive", processes["record_sensitive"]),
            ("injected_label", processes["injected_label"]),
        )
    ]


def presentation_rows(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    presentations = summary["presentations"]
    cases = (
        ("exact_relabeling", presentations["exact_relabeling"]),
        ("bisimilar_duplicate", presentations["bisimilar_duplicate"]),
        ("forward_failure", presentations["forward_failure"]),
        ("back_failure", presentations["back_failure"]),
        ("atom_failure", presentations["atom_failure"]),
        (
            "weighted_grain_hidden",
            presentations["weighted_grain_hidden"]["presentation"],
        ),
    )
    return [
        {
            "case": case,
            "atom_respects": audit["atom_respects"],
            "forward": audit["forward"],
            "back": audit["back"],
            "forward_simulation": audit["forward_simulation"],
            "reflection": audit["reflection"],
            "functional_bisimulation": audit["functional_bisimulation"],
            "isomorphism": audit["isomorphism"],
        }
        for case, audit in cases
    ]


def omega_fiber_rows(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "family": "+".join(fiber["family"]) or "empty",
            "family_size": len(fiber["family"]),
            "witness_count": len(fiber["witness_ids"]),
            "witness_ids": "|".join(fiber["witness_ids"]),
            "nonempty": fiber["nonempty"],
        }
        for fiber in summary["omega"]["omega"]["fibers"]
    ]
