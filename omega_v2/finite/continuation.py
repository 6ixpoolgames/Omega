"""Finite-horizon continuation observables."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Generic, Iterable

from omega_v2.finite.abstraction import (
    abstract_policy,
    audit_predicate_factorization,
    build_quotient_kernel,
)
from omega_v2.finite.model import (
    AbstractStateT,
    ActionT,
    ControlledMarkovSystem,
    DeterministicPolicy,
    StateAggregation,
    StateT,
    fraction_text,
)


def bounded_hit_probability(
    system: ControlledMarkovSystem[StateT, ActionT],
    policy: DeterministicPolicy[StateT, ActionT],
    target_states: Iterable[StateT],
    *,
    start: StateT,
    horizon: int,
) -> Fraction:
    """Probability of hitting a target at or before a finite horizon."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    policy.validate(system)
    system.require_state(start)
    target = frozenset(target_states)
    if not target <= set(system.states):
        raise ValueError("target set contains an unknown state")

    profile = {
        state: Fraction(1) if state in target else Fraction(0)
        for state in system.states
    }
    for _step in range(horizon):
        next_profile: dict[StateT, Fraction] = {}
        for state in system.states:
            if state in target:
                next_profile[state] = Fraction(1)
                continue
            action = policy.action_at(state)
            next_profile[state] = sum(
                (
                    mass * profile[successor]
                    for successor, mass in system.distribution(state, action).rows
                ),
                Fraction(0),
            )
        profile = next_profile
    return profile[start]


def safe_through_horizon_probability(
    system: ControlledMarkovSystem[StateT, ActionT],
    policy: DeterministicPolicy[StateT, ActionT],
    safe_states: Iterable[StateT],
    *,
    start: StateT,
    horizon: int,
) -> Fraction:
    """Probability that every state through the finite horizon is safe."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    policy.validate(system)
    system.require_state(start)
    safe = frozenset(safe_states)
    if not safe <= set(system.states):
        raise ValueError("safe set contains an unknown state")

    profile = {
        state: Fraction(1) if state in safe else Fraction(0)
        for state in system.states
    }
    for _step in range(horizon):
        next_profile: dict[StateT, Fraction] = {}
        for state in system.states:
            if state not in safe:
                next_profile[state] = Fraction(0)
                continue
            action = policy.action_at(state)
            next_profile[state] = sum(
                (
                    mass * profile[successor]
                    for successor, mass in system.distribution(state, action).rows
                ),
                Fraction(0),
            )
        profile = next_profile
    return profile[start]


@dataclass(frozen=True)
class ContinuationMismatch(Generic[StateT, AbstractStateT]):
    concrete_state: StateT
    abstract_state: AbstractStateT
    concrete_probability: Fraction
    quotient_probability: Fraction

    def as_dict(self) -> dict[str, object]:
        return {
            "concrete_state": repr(self.concrete_state),
            "abstract_state": repr(self.abstract_state),
            "concrete_probability": fraction_text(self.concrete_probability),
            "quotient_probability": fraction_text(self.quotient_probability),
        }


@dataclass(frozen=True)
class ContinuationTransportAudit(Generic[StateT, AbstractStateT]):
    target_factors: bool
    horizon: int
    agrees: bool
    mismatches: tuple[ContinuationMismatch[StateT, AbstractStateT], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "target_factors": self.target_factors,
            "horizon": self.horizon,
            "agrees": self.agrees,
            "mismatch_count": len(self.mismatches),
            "mismatches": [mismatch.as_dict() for mismatch in self.mismatches],
        }


def audit_bounded_hit_transport(
    system: ControlledMarkovSystem[StateT, ActionT],
    aggregation: StateAggregation[StateT, AbstractStateT],
    policy: DeterministicPolicy[StateT, ActionT],
    concrete_target_states: Iterable[StateT],
    *,
    horizon: int,
) -> ContinuationTransportAudit[StateT, AbstractStateT]:
    """Compare bounded target-hit probabilities before and after aggregation."""

    concrete_target = frozenset(concrete_target_states)
    if not concrete_target <= set(system.states):
        raise ValueError("target set contains an unknown concrete state")
    target_audit = audit_predicate_factorization(
        aggregation,
        lambda state: state in concrete_target,
    )
    if not target_audit.factors:
        return ContinuationTransportAudit(
            target_factors=False,
            horizon=horizon,
            agrees=False,
            mismatches=(),
        )

    quotient = build_quotient_kernel(system, aggregation)
    quotient_policy = abstract_policy(system, aggregation, policy)
    abstract_target = frozenset(
        aggregation.image(state) for state in concrete_target
    )
    mismatches: list[ContinuationMismatch[StateT, AbstractStateT]] = []
    quotient_probabilities = {
        abstract_state: bounded_hit_probability(
            quotient,
            quotient_policy,
            abstract_target,
            start=abstract_state,
            horizon=horizon,
        )
        for abstract_state in quotient.states
    }
    for concrete_state in system.states:
        abstract_state = aggregation.image(concrete_state)
        concrete_probability = bounded_hit_probability(
            system,
            policy,
            concrete_target,
            start=concrete_state,
            horizon=horizon,
        )
        quotient_probability = quotient_probabilities[abstract_state]
        if concrete_probability != quotient_probability:
            mismatches.append(
                ContinuationMismatch(
                    concrete_state=concrete_state,
                    abstract_state=abstract_state,
                    concrete_probability=concrete_probability,
                    quotient_probability=quotient_probability,
                )
            )
    return ContinuationTransportAudit(
        target_factors=True,
        horizon=horizon,
        agrees=not mismatches,
        mismatches=tuple(mismatches),
    )
