"""Exact finite path laws and information-loss audits."""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Generic, Hashable, TypeVar

from omega_v2.finite.model import (
    AbstractStateT,
    ActionT,
    ControlledMarkovSystem,
    DeterministicPolicy,
    FiniteDistribution,
    FinitePath,
    OutcomeT,
    StateAggregation,
    StateT,
    fraction_text,
)


KeyT = TypeVar("KeyT", bound=Hashable)


def finite_path_law(
    system: ControlledMarkovSystem[StateT, ActionT],
    policy: DeterministicPolicy[StateT, ActionT],
    initial: FiniteDistribution[StateT],
    *,
    horizon: int,
) -> FiniteDistribution[FinitePath[StateT, ActionT]]:
    """Enumerate the exact path law under a stationary deterministic policy."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    policy.validate(system)
    if not set(initial.support) <= set(system.states):
        raise ValueError("initial distribution references an unknown state")

    frontier: dict[FinitePath[StateT, ActionT], Fraction] = {
        FinitePath(states=(state,), actions=()): mass for state, mass in initial.rows
    }
    for _step in range(horizon):
        next_frontier: dict[FinitePath[StateT, ActionT], Fraction] = {}
        for path, prefix_mass in frontier.items():
            action = policy.action_at(path.end)
            for target, transition_mass in system.distribution(path.end, action).rows:
                extended = FinitePath(
                    states=path.states + (target,),
                    actions=path.actions + (action,),
                )
                next_frontier[extended] = (
                    next_frontier.get(extended, Fraction(0))
                    + prefix_mass * transition_mass
                )
        frontier = next_frontier
    return FiniteDistribution.from_mapping(frontier)


def path_probability(
    system: ControlledMarkovSystem[StateT, ActionT],
    policy: DeterministicPolicy[StateT, ActionT],
    initial: FiniteDistribution[StateT],
    path: FinitePath[StateT, ActionT],
) -> Fraction:
    """Return the exact probability of one policy-consistent path."""

    policy.validate(system)
    if path.start not in initial.support:
        return Fraction(0)
    mass = initial.probability(path.start)
    for index, action in enumerate(path.actions):
        source = path.states[index]
        target = path.states[index + 1]
        if source not in system.states or target not in system.states:
            return Fraction(0)
        if policy.action_at(source) != action:
            return Fraction(0)
        mass *= system.distribution(source, action).probability(target)
        if mass == 0:
            return Fraction(0)
    return mass


def abstract_path(
    path: FinitePath[StateT, ActionT],
    aggregation: StateAggregation[StateT, AbstractStateT],
) -> FinitePath[AbstractStateT, ActionT]:
    """Map every state of a path through a state aggregation."""

    return FinitePath(
        states=tuple(aggregation.image(state) for state in path.states),
        actions=path.actions,
    )


def pushforward_path_law(
    law: FiniteDistribution[FinitePath[StateT, ActionT]],
    aggregation: StateAggregation[StateT, AbstractStateT],
) -> FiniteDistribution[FinitePath[AbstractStateT, ActionT]]:
    return law.pushforward(lambda path: abstract_path(path, aggregation))


def event_probability(
    law: FiniteDistribution[OutcomeT],
    event: Callable[[OutcomeT], bool],
) -> Fraction:
    """Return the exact mass of a finite event."""

    return sum(
        (mass for outcome, mass in law.rows if event(outcome)),
        Fraction(0),
    )


def total_variation_distance(
    left: FiniteDistribution[OutcomeT],
    right: FiniteDistribution[OutcomeT],
) -> Fraction:
    """Exact total-variation distance between finite laws."""

    outcomes = tuple(dict.fromkeys((*left.support, *right.support)))
    return Fraction(1, 2) * sum(
        (
            abs(left.probability(outcome) - right.probability(outcome))
            for outcome in outcomes
        ),
        Fraction(0),
    )


def kl_divergence(
    left: FiniteDistribution[OutcomeT],
    right: FiniteDistribution[OutcomeT],
) -> float | None:
    """Return KL(left || right), or ``None`` when it is infinite."""

    if any(
        left.probability(outcome) > 0 and right.probability(outcome) == 0
        for outcome in left.support
    ):
        return None
    divergence = sum(
        float(mass) * math.log(float(mass / right.probability(outcome)))
        for outcome, mass in left.rows
    )
    return 0.0 if abs(divergence) < 1e-15 else divergence


@dataclass(frozen=True)
class LawComparison(Generic[OutcomeT]):
    """Exact finite-law comparison with KL retained as a diagnostic."""

    total_variation: Fraction
    kl_left_to_right: float | None
    support_equal: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "total_variation": fraction_text(self.total_variation),
            "kl_left_to_right": self.kl_left_to_right,
            "kl_is_infinite": self.kl_left_to_right is None,
            "support_equal": self.support_equal,
        }


def compare_laws(
    left: FiniteDistribution[OutcomeT],
    right: FiniteDistribution[OutcomeT],
) -> LawComparison[OutcomeT]:
    return LawComparison(
        total_variation=total_variation_distance(left, right),
        kl_left_to_right=kl_divergence(left, right),
        support_equal=set(left.support) == set(right.support),
    )


@dataclass(frozen=True)
class LikelihoodRatioWitness(Generic[OutcomeT, KeyT]):
    """Failure of conditional-law equality within one aggregate fiber."""

    aggregate_outcome: KeyT
    concrete_outcome: OutcomeT
    left_point_mass: Fraction
    right_point_mass: Fraction
    left_fiber_mass: Fraction
    right_fiber_mass: Fraction

    def as_dict(self) -> dict[str, object]:
        return {
            "aggregate_outcome": repr(self.aggregate_outcome),
            "concrete_outcome": repr(self.concrete_outcome),
            "left_point_mass": fraction_text(self.left_point_mass),
            "right_point_mass": fraction_text(self.right_point_mass),
            "left_fiber_mass": fraction_text(self.left_fiber_mass),
            "right_fiber_mass": fraction_text(self.right_fiber_mass),
        }


@dataclass(frozen=True)
class LikelihoodRatioSufficiencyAudit(Generic[OutcomeT, KeyT]):
    """Finite sufficiency audit for distinguishing two laws after aggregation."""

    sufficient: bool
    aggregate_fiber_count: int
    witnesses: tuple[LikelihoodRatioWitness[OutcomeT, KeyT], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "sufficient": self.sufficient,
            "aggregate_fiber_count": self.aggregate_fiber_count,
            "witness_count": len(self.witnesses),
            "witnesses": [witness.as_dict() for witness in self.witnesses],
        }


def audit_likelihood_ratio_sufficiency(
    left: FiniteDistribution[OutcomeT],
    right: FiniteDistribution[OutcomeT],
    aggregation: Callable[[OutcomeT], KeyT],
) -> LikelihoodRatioSufficiencyAudit[OutcomeT, KeyT]:
    """Check exact conditional-law equality inside every aggregate fiber.

    The cross-multiplied condition handles zero masses without dividing:

    ``P(x) Q(fiber) = Q(x) P(fiber)``.
    """

    left_aggregate = left.pushforward(aggregation)
    right_aggregate = right.pushforward(aggregation)
    outcomes = tuple(dict.fromkeys((*left.support, *right.support)))
    witnesses: list[LikelihoodRatioWitness[OutcomeT, KeyT]] = []
    for outcome in outcomes:
        aggregate_outcome = aggregation(outcome)
        left_point = left.probability(outcome)
        right_point = right.probability(outcome)
        left_fiber = left_aggregate.probability(aggregate_outcome)
        right_fiber = right_aggregate.probability(aggregate_outcome)
        if left_point * right_fiber != right_point * left_fiber:
            witnesses.append(
                LikelihoodRatioWitness(
                    aggregate_outcome=aggregate_outcome,
                    concrete_outcome=outcome,
                    left_point_mass=left_point,
                    right_point_mass=right_point,
                    left_fiber_mass=left_fiber,
                    right_fiber_mass=right_fiber,
                )
            )
    return LikelihoodRatioSufficiencyAudit(
        sufficient=not witnesses,
        aggregate_fiber_count=len(set(left_aggregate.support) | set(right_aggregate.support)),
        witnesses=tuple(witnesses),
    )


@dataclass(frozen=True)
class ActionInvolution(Generic[ActionT]):
    """An explicit involutive action map for finite path reversal."""

    rows: tuple[tuple[ActionT, ActionT], ...]

    def __post_init__(self) -> None:
        sources = tuple(source for source, _target in self.rows)
        if not sources or len(sources) != len(set(sources)):
            raise ValueError("action involution rows must be nonempty and functional")
        action_map = dict(self.rows)
        if set(action_map) != set(action_map.values()):
            raise ValueError("action involution must be a permutation")
        if any(action_map[action_map[action]] != action for action in action_map):
            raise ValueError("action map must be involutive")

    @property
    def action_map(self) -> dict[ActionT, ActionT]:
        return dict(self.rows)

    def validate(self, actions: tuple[ActionT, ...]) -> None:
        if not set(actions) <= set(self.action_map):
            raise ValueError("action involution is undefined on an observed action")

    def reverse(
        self,
        path: FinitePath[StateT, ActionT],
    ) -> FinitePath[StateT, ActionT]:
        return FinitePath(
            states=tuple(reversed(path.states)),
            actions=tuple(self.action_map[action] for action in reversed(path.actions)),
        )


def pull_back_reversed_path_law(
    reverse_law: FiniteDistribution[FinitePath[StateT, ActionT]],
    action_involution: ActionInvolution[ActionT],
) -> FiniteDistribution[FinitePath[StateT, ActionT]]:
    """Express a reverse-process law on the forward path coordinates."""

    if not reverse_law.rows:
        raise ValueError("reverse path law must be nonempty")
    actions = tuple(
        dict.fromkeys(action for path, _mass in reverse_law.rows for action in path.actions)
    )
    if actions:
        action_involution.validate(actions)
    return reverse_law.pushforward(action_involution.reverse)
