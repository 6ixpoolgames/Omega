"""Exact finite controlled Markov models.

The stochastic system stores dynamics only. Observations, predicates, and
interpretations are supplied separately by consumers.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Generic, Hashable, Iterable, Mapping, TypeVar


OutcomeT = TypeVar("OutcomeT", bound=Hashable)
MappedOutcomeT = TypeVar("MappedOutcomeT", bound=Hashable)
StateT = TypeVar("StateT", bound=Hashable)
AbstractStateT = TypeVar("AbstractStateT", bound=Hashable)
ActionT = TypeVar("ActionT", bound=Hashable)


def fraction_text(value: Fraction) -> str:
    """Return an exact stable representation of a rational number."""

    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


@dataclass(frozen=True)
class FiniteDistribution(Generic[OutcomeT]):
    """A normalized finite probability distribution with exact rational mass."""

    rows: tuple[tuple[OutcomeT, Fraction], ...]

    def __post_init__(self) -> None:
        if not self.rows:
            raise ValueError("a finite distribution must have nonempty support")
        outcomes = tuple(outcome for outcome, _mass in self.rows)
        if len(outcomes) != len(set(outcomes)):
            raise ValueError("a finite distribution cannot repeat an outcome")
        if any(mass <= 0 for _outcome, mass in self.rows):
            raise ValueError("finite distribution masses must be strictly positive")
        if sum((mass for _outcome, mass in self.rows), Fraction(0)) != 1:
            raise ValueError("finite distribution masses must sum exactly to one")

    @classmethod
    def point_mass(cls, outcome: OutcomeT) -> FiniteDistribution[OutcomeT]:
        return cls(rows=((outcome, Fraction(1)),))

    @classmethod
    def from_mapping(
        cls,
        masses: Mapping[OutcomeT, Fraction],
    ) -> FiniteDistribution[OutcomeT]:
        if any(mass < 0 for mass in masses.values()):
            raise ValueError("finite distribution masses must be nonnegative")
        return cls(rows=tuple((outcome, mass) for outcome, mass in masses.items() if mass > 0))

    @property
    def support(self) -> tuple[OutcomeT, ...]:
        return tuple(outcome for outcome, _mass in self.rows)

    @property
    def mass_map(self) -> dict[OutcomeT, Fraction]:
        return dict(self.rows)

    def probability(self, outcome: OutcomeT) -> Fraction:
        return self.mass_map.get(outcome, Fraction(0))

    def pushforward(
        self,
        mapping: Callable[[OutcomeT], MappedOutcomeT],
    ) -> FiniteDistribution[MappedOutcomeT]:
        masses: dict[MappedOutcomeT, Fraction] = {}
        for outcome, mass in self.rows:
            target = mapping(outcome)
            masses[target] = masses.get(target, Fraction(0)) + mass
        return FiniteDistribution.from_mapping(masses)


TransitionRow = tuple[StateT, ActionT, StateT, Fraction]


@dataclass(frozen=True)
class ControlledMarkovSystem(Generic[StateT, ActionT]):
    """A total finite action-indexed Markov kernel."""

    system_id: str
    states: tuple[StateT, ...]
    actions: tuple[ActionT, ...]
    transitions: tuple[TransitionRow[StateT, ActionT], ...]

    def __post_init__(self) -> None:
        if not self.system_id:
            raise ValueError("system_id must be nonempty")
        if not self.states or len(self.states) != len(set(self.states)):
            raise ValueError("states must be nonempty and unique")
        if not self.actions or len(self.actions) != len(set(self.actions)):
            raise ValueError("actions must be nonempty and unique")

        state_set = set(self.states)
        action_set = set(self.actions)
        seen: set[tuple[StateT, ActionT, StateT]] = set()
        grouped: dict[tuple[StateT, ActionT], dict[StateT, Fraction]] = {
            (state, action): {} for state in self.states for action in self.actions
        }
        for source, action, target, probability in self.transitions:
            if source not in state_set or target not in state_set:
                raise ValueError("transition references an unknown state")
            if action not in action_set:
                raise ValueError("transition references an unknown action")
            key = (source, action, target)
            if key in seen:
                raise ValueError("transition rows must be unique")
            if probability <= 0:
                raise ValueError("stored transition probabilities must be positive")
            seen.add(key)
            grouped[(source, action)][target] = probability

        for state in self.states:
            for action in self.actions:
                row = grouped[(state, action)]
                if not row:
                    raise ValueError(f"transition row {(state, action)!r} must be nonempty")
                if sum(row.values(), Fraction(0)) != 1:
                    raise ValueError(
                        f"transition row {(state, action)!r} must sum exactly to one"
                    )

    def distribution(
        self,
        state: StateT,
        action: ActionT,
    ) -> FiniteDistribution[StateT]:
        self.require_state(state)
        self.require_action(action)
        return FiniteDistribution(
            rows=tuple(
                (target, probability)
                for source, candidate_action, target, probability in self.transitions
                if source == state and candidate_action == action
            )
        )

    def support_successors(
        self,
        state: StateT,
        action: ActionT,
    ) -> frozenset[StateT]:
        return frozenset(self.distribution(state, action).support)

    def require_state(self, state: StateT) -> None:
        if state not in self.states:
            raise KeyError(state)

    def require_action(self, action: ActionT) -> None:
        if action not in self.actions:
            raise KeyError(action)


PolicyRow = tuple[StateT, ActionT]


@dataclass(frozen=True)
class DeterministicPolicy(Generic[StateT, ActionT]):
    """A stationary deterministic policy."""

    policy_id: str
    rows: tuple[PolicyRow[StateT, ActionT], ...]

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id must be nonempty")
        states = tuple(state for state, _action in self.rows)
        if len(states) != len(set(states)):
            raise ValueError("policy rows must have unique states")

    @property
    def action_map(self) -> dict[StateT, ActionT]:
        return dict(self.rows)

    def validate(self, system: ControlledMarkovSystem[StateT, ActionT]) -> None:
        if set(self.action_map) != set(system.states):
            raise ValueError("policy must be total on the system state set")
        if any(action not in system.actions for _state, action in self.rows):
            raise ValueError("policy references an unknown action")

    def action_at(self, state: StateT) -> ActionT:
        try:
            return self.action_map[state]
        except KeyError as exc:
            raise KeyError(state) from exc


@dataclass(frozen=True, order=True)
class FinitePath(Generic[StateT, ActionT]):
    """A finite state-action path."""

    states: tuple[StateT, ...]
    actions: tuple[ActionT, ...]

    def __post_init__(self) -> None:
        if not self.states:
            raise ValueError("a finite path must contain at least one state")
        if len(self.states) != len(self.actions) + 1:
            raise ValueError("a path with n actions must contain n + 1 states")

    @property
    def horizon(self) -> int:
        return len(self.actions)

    @property
    def start(self) -> StateT:
        return self.states[0]

    @property
    def end(self) -> StateT:
        return self.states[-1]


StateMapRow = tuple[StateT, AbstractStateT]


@dataclass(frozen=True)
class StateAggregation(Generic[StateT, AbstractStateT]):
    """A surjective map from concrete states to aggregate states."""

    aggregation_id: str
    source_states: tuple[StateT, ...]
    target_states: tuple[AbstractStateT, ...]
    rows: tuple[StateMapRow[StateT, AbstractStateT], ...]

    def __post_init__(self) -> None:
        if not self.aggregation_id:
            raise ValueError("aggregation_id must be nonempty")
        if not self.source_states or len(self.source_states) != len(set(self.source_states)):
            raise ValueError("source states must be nonempty and unique")
        if not self.target_states or len(self.target_states) != len(set(self.target_states)):
            raise ValueError("target states must be nonempty and unique")
        sources = tuple(source for source, _target in self.rows)
        if len(sources) != len(set(sources)):
            raise ValueError("state aggregation must be functional")
        if set(sources) != set(self.source_states):
            raise ValueError("state aggregation must be total on source states")
        targets = tuple(target for _source, target in self.rows)
        if not set(targets) <= set(self.target_states):
            raise ValueError("state aggregation references an unknown target state")
        if set(targets) != set(self.target_states):
            raise ValueError("state aggregation must be surjective")

    @property
    def state_map(self) -> dict[StateT, AbstractStateT]:
        return dict(self.rows)

    def image(self, state: StateT) -> AbstractStateT:
        try:
            return self.state_map[state]
        except KeyError as exc:
            raise KeyError(state) from exc

    def fiber(self, target: AbstractStateT) -> tuple[StateT, ...]:
        if target not in self.target_states:
            raise KeyError(target)
        return tuple(state for state, image in self.rows if image == target)

    def validate_source(self, system: ControlledMarkovSystem[StateT, ActionT]) -> None:
        if set(self.source_states) != set(system.states):
            raise ValueError("aggregation source states must match the system state set")

    def preimage(self, targets: Iterable[AbstractStateT]) -> frozenset[StateT]:
        selected = frozenset(targets)
        if not selected <= set(self.target_states):
            raise ValueError("preimage target set contains an unknown aggregate state")
        return frozenset(state for state, target in self.rows if target in selected)
