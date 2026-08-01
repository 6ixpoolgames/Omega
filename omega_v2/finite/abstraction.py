"""Finite state aggregation for controlled Markov systems."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Callable, Generic

from omega_v2.finite.model import (
    AbstractStateT,
    ActionT,
    ControlledMarkovSystem,
    DeterministicPolicy,
    FiniteDistribution,
    FinitePath,
    StateAggregation,
    StateT,
    fraction_text,
)
from omega_v2.finite.path_laws import (
    finite_path_law,
    pushforward_path_law,
    total_variation_distance,
)


@dataclass(frozen=True)
class LumpabilityWitness(Generic[StateT, AbstractStateT, ActionT]):
    source_block: AbstractStateT
    left_state: StateT
    right_state: StateT
    action: ActionT
    target_block: AbstractStateT
    left_mass: Fraction
    right_mass: Fraction

    @property
    def absolute_discrepancy(self) -> Fraction:
        return abs(self.left_mass - self.right_mass)

    def as_dict(self) -> dict[str, object]:
        return {
            "source_block": repr(self.source_block),
            "left_state": repr(self.left_state),
            "right_state": repr(self.right_state),
            "action": repr(self.action),
            "target_block": repr(self.target_block),
            "left_mass": fraction_text(self.left_mass),
            "right_mass": fraction_text(self.right_mass),
            "absolute_discrepancy": fraction_text(self.absolute_discrepancy),
        }


@dataclass(frozen=True)
class RepresentativeDiscrepancy(Generic[StateT, AbstractStateT, ActionT]):
    source_block: AbstractStateT
    left_state: StateT
    right_state: StateT
    action: ActionT
    total_variation: Fraction

    def as_dict(self) -> dict[str, object]:
        return {
            "source_block": repr(self.source_block),
            "left_state": repr(self.left_state),
            "right_state": repr(self.right_state),
            "action": repr(self.action),
            "total_variation": fraction_text(self.total_variation),
        }


@dataclass(frozen=True)
class ActionwiseLumpabilityAudit(Generic[StateT, AbstractStateT, ActionT]):
    aggregation_id: str
    strongly_lumpable: bool
    witnesses: tuple[LumpabilityWitness[StateT, AbstractStateT, ActionT], ...]
    representative_discrepancies: tuple[
        RepresentativeDiscrepancy[StateT, AbstractStateT, ActionT], ...
    ]
    maximum_total_variation_discrepancy: Fraction

    def as_dict(self) -> dict[str, object]:
        return {
            "aggregation_id": self.aggregation_id,
            "strongly_lumpable": self.strongly_lumpable,
            "witness_count": len(self.witnesses),
            "witnesses": [witness.as_dict() for witness in self.witnesses],
            "representative_discrepancies": [
                discrepancy.as_dict() for discrepancy in self.representative_discrepancies
            ],
            "maximum_total_variation_discrepancy": fraction_text(
                self.maximum_total_variation_discrepancy
            ),
        }


def aggregate_successor_distribution(
    system: ControlledMarkovSystem[StateT, ActionT],
    aggregation: StateAggregation[StateT, AbstractStateT],
    state: StateT,
    action: ActionT,
) -> FiniteDistribution[AbstractStateT]:
    """Push one concrete transition row to aggregate states."""

    aggregation.validate_source(system)
    return system.distribution(state, action).pushforward(aggregation.image)


def audit_actionwise_lumpability(
    system: ControlledMarkovSystem[StateT, ActionT],
    aggregation: StateAggregation[StateT, AbstractStateT],
) -> ActionwiseLumpabilityAudit[StateT, AbstractStateT, ActionT]:
    """Check strong lumpability for every action with exact witnesses."""

    aggregation.validate_source(system)
    witnesses: list[LumpabilityWitness[StateT, AbstractStateT, ActionT]] = []
    discrepancies: list[RepresentativeDiscrepancy[StateT, AbstractStateT, ActionT]] = []
    maximum = Fraction(0)
    for source_block in aggregation.target_states:
        for left_state, right_state in combinations(aggregation.fiber(source_block), 2):
            for action in system.actions:
                left = aggregate_successor_distribution(
                    system,
                    aggregation,
                    left_state,
                    action,
                )
                right = aggregate_successor_distribution(
                    system,
                    aggregation,
                    right_state,
                    action,
                )
                discrepancy = total_variation_distance(left, right)
                discrepancies.append(
                    RepresentativeDiscrepancy(
                        source_block=source_block,
                        left_state=left_state,
                        right_state=right_state,
                        action=action,
                        total_variation=discrepancy,
                    )
                )
                maximum = max(maximum, discrepancy)
                for target_block in aggregation.target_states:
                    left_mass = left.probability(target_block)
                    right_mass = right.probability(target_block)
                    if left_mass != right_mass:
                        witnesses.append(
                            LumpabilityWitness(
                                source_block=source_block,
                                left_state=left_state,
                                right_state=right_state,
                                action=action,
                                target_block=target_block,
                                left_mass=left_mass,
                                right_mass=right_mass,
                            )
                        )
    return ActionwiseLumpabilityAudit(
        aggregation_id=aggregation.aggregation_id,
        strongly_lumpable=not witnesses,
        witnesses=tuple(witnesses),
        representative_discrepancies=tuple(discrepancies),
        maximum_total_variation_discrepancy=maximum,
    )


def build_quotient_kernel(
    system: ControlledMarkovSystem[StateT, ActionT],
    aggregation: StateAggregation[StateT, AbstractStateT],
    *,
    system_id: str | None = None,
) -> ControlledMarkovSystem[AbstractStateT, ActionT]:
    """Construct the representative-independent quotient kernel."""

    audit = audit_actionwise_lumpability(system, aggregation)
    if not audit.strongly_lumpable:
        first = audit.witnesses[0]
        raise ValueError(
            "state aggregation is not action-wise strongly lumpable: "
            f"{first.left_state!r} and {first.right_state!r} assign "
            f"{fraction_text(first.left_mass)} and {fraction_text(first.right_mass)} "
            f"to block {first.target_block!r} under action {first.action!r}"
        )

    transitions: list[tuple[AbstractStateT, ActionT, AbstractStateT, Fraction]] = []
    for source_block in aggregation.target_states:
        representative = aggregation.fiber(source_block)[0]
        for action in system.actions:
            row = aggregate_successor_distribution(
                system,
                aggregation,
                representative,
                action,
            )
            transitions.extend(
                (source_block, action, target_block, mass)
                for target_block, mass in row.rows
            )
    return ControlledMarkovSystem(
        system_id=system_id or f"{system.system_id}__quotient__{aggregation.aggregation_id}",
        states=aggregation.target_states,
        actions=system.actions,
        transitions=tuple(transitions),
    )


@dataclass(frozen=True)
class PolicyFactorizationWitness(Generic[StateT, AbstractStateT, ActionT]):
    source_block: AbstractStateT
    left_state: StateT
    right_state: StateT
    left_action: ActionT
    right_action: ActionT

    def as_dict(self) -> dict[str, object]:
        return {
            "source_block": repr(self.source_block),
            "left_state": repr(self.left_state),
            "right_state": repr(self.right_state),
            "left_action": repr(self.left_action),
            "right_action": repr(self.right_action),
        }


@dataclass(frozen=True)
class PolicyFactorizationAudit(Generic[StateT, AbstractStateT, ActionT]):
    factors: bool
    witnesses: tuple[PolicyFactorizationWitness[StateT, AbstractStateT, ActionT], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "factors": self.factors,
            "witness_count": len(self.witnesses),
            "witnesses": [witness.as_dict() for witness in self.witnesses],
        }


def audit_policy_factorization(
    system: ControlledMarkovSystem[StateT, ActionT],
    aggregation: StateAggregation[StateT, AbstractStateT],
    policy: DeterministicPolicy[StateT, ActionT],
) -> PolicyFactorizationAudit[StateT, AbstractStateT, ActionT]:
    """Check whether a policy is constant on every state fiber."""

    aggregation.validate_source(system)
    policy.validate(system)
    witnesses: list[PolicyFactorizationWitness[StateT, AbstractStateT, ActionT]] = []
    for source_block in aggregation.target_states:
        states = aggregation.fiber(source_block)
        left_state = states[0]
        left_action = policy.action_at(left_state)
        for right_state in states[1:]:
            right_action = policy.action_at(right_state)
            if left_action != right_action:
                witnesses.append(
                    PolicyFactorizationWitness(
                        source_block=source_block,
                        left_state=left_state,
                        right_state=right_state,
                        left_action=left_action,
                        right_action=right_action,
                    )
                )
    return PolicyFactorizationAudit(factors=not witnesses, witnesses=tuple(witnesses))


def abstract_policy(
    system: ControlledMarkovSystem[StateT, ActionT],
    aggregation: StateAggregation[StateT, AbstractStateT],
    policy: DeterministicPolicy[StateT, ActionT],
    *,
    policy_id: str | None = None,
) -> DeterministicPolicy[AbstractStateT, ActionT]:
    audit = audit_policy_factorization(system, aggregation, policy)
    if not audit.factors:
        raise ValueError("policy does not factor through the state aggregation")
    return DeterministicPolicy(
        policy_id=policy_id or f"{policy.policy_id}__{aggregation.aggregation_id}",
        rows=tuple(
            (target, policy.action_at(aggregation.fiber(target)[0]))
            for target in aggregation.target_states
        ),
    )


@dataclass(frozen=True)
class PredicateFactorizationWitness(Generic[StateT, AbstractStateT]):
    source_block: AbstractStateT
    left_state: StateT
    right_state: StateT
    left_value: bool
    right_value: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "source_block": repr(self.source_block),
            "left_state": repr(self.left_state),
            "right_state": repr(self.right_state),
            "left_value": self.left_value,
            "right_value": self.right_value,
        }


@dataclass(frozen=True)
class PredicateFactorizationAudit(Generic[StateT, AbstractStateT]):
    factors: bool
    witnesses: tuple[PredicateFactorizationWitness[StateT, AbstractStateT], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "factors": self.factors,
            "witness_count": len(self.witnesses),
            "witnesses": [witness.as_dict() for witness in self.witnesses],
        }


def audit_predicate_factorization(
    aggregation: StateAggregation[StateT, AbstractStateT],
    predicate: Callable[[StateT], bool],
) -> PredicateFactorizationAudit[StateT, AbstractStateT]:
    """Check whether a state predicate is constant on each aggregation fiber."""

    witnesses: list[PredicateFactorizationWitness[StateT, AbstractStateT]] = []
    for source_block in aggregation.target_states:
        states = aggregation.fiber(source_block)
        left_state = states[0]
        left_value = predicate(left_state)
        for right_state in states[1:]:
            right_value = predicate(right_state)
            if left_value != right_value:
                witnesses.append(
                    PredicateFactorizationWitness(
                        source_block=source_block,
                        left_state=left_state,
                        right_state=right_state,
                        left_value=left_value,
                        right_value=right_value,
                    )
                )
    return PredicateFactorizationAudit(factors=not witnesses, witnesses=tuple(witnesses))


@dataclass(frozen=True)
class SupportFailure(Generic[StateT, AbstractStateT, ActionT]):
    direction: str
    concrete_state: StateT
    action: ActionT
    abstract_target: AbstractStateT
    concrete_target: StateT | None

    def as_dict(self) -> dict[str, object]:
        return {
            "direction": self.direction,
            "concrete_state": repr(self.concrete_state),
            "action": repr(self.action),
            "abstract_target": repr(self.abstract_target),
            "concrete_target": None
            if self.concrete_target is None
            else repr(self.concrete_target),
        }


@dataclass(frozen=True)
class SupportBisimulationAudit(Generic[StateT, AbstractStateT, ActionT]):
    forward: bool
    back: bool
    failures: tuple[SupportFailure[StateT, AbstractStateT, ActionT], ...]

    @property
    def bisimilar(self) -> bool:
        return self.forward and self.back

    def as_dict(self) -> dict[str, object]:
        return {
            "forward": self.forward,
            "back": self.back,
            "bisimilar": self.bisimilar,
            "failure_count": len(self.failures),
            "failures": [failure.as_dict() for failure in self.failures],
        }


def audit_support_bisimulation(
    concrete: ControlledMarkovSystem[StateT, ActionT],
    abstract: ControlledMarkovSystem[AbstractStateT, ActionT],
    aggregation: StateAggregation[StateT, AbstractStateT],
) -> SupportBisimulationAudit[StateT, AbstractStateT, ActionT]:
    """Audit action-labelled forward and back support clauses."""

    aggregation.validate_source(concrete)
    if abstract.states != aggregation.target_states:
        raise ValueError("abstract state order must match aggregation target states")
    if abstract.actions != concrete.actions:
        raise ValueError("v0 support audit requires a common action alphabet")
    failures: list[SupportFailure[StateT, AbstractStateT, ActionT]] = []
    forward = True
    back = True
    for state in concrete.states:
        source_block = aggregation.image(state)
        for action in concrete.actions:
            abstract_targets = abstract.support_successors(source_block, action)
            for concrete_target in concrete.support_successors(state, action):
                target_block = aggregation.image(concrete_target)
                if target_block not in abstract_targets:
                    forward = False
                    failures.append(
                        SupportFailure(
                            direction="forward",
                            concrete_state=state,
                            action=action,
                            abstract_target=target_block,
                            concrete_target=concrete_target,
                        )
                    )
            for target_block in abstract_targets:
                if not any(
                    aggregation.image(concrete_target) == target_block
                    for concrete_target in concrete.support_successors(state, action)
                ):
                    back = False
                    failures.append(
                        SupportFailure(
                            direction="back",
                            concrete_state=state,
                            action=action,
                            abstract_target=target_block,
                            concrete_target=None,
                        )
                    )
    return SupportBisimulationAudit(
        forward=forward,
        back=back,
        failures=tuple(failures),
    )


def pushforward_initial_distribution(
    initial: FiniteDistribution[StateT],
    aggregation: StateAggregation[StateT, AbstractStateT],
) -> FiniteDistribution[AbstractStateT]:
    if not set(initial.support) <= set(aggregation.source_states):
        raise ValueError("initial distribution references an unknown source state")
    return initial.pushforward(aggregation.image)


@dataclass(frozen=True)
class PathMassMismatch(Generic[AbstractStateT, ActionT]):
    path: FinitePath[AbstractStateT, ActionT]
    pushed_mass: Fraction
    quotient_mass: Fraction

    def as_dict(self) -> dict[str, object]:
        return {
            "states": [repr(state) for state in self.path.states],
            "actions": [repr(action) for action in self.path.actions],
            "pushed_mass": fraction_text(self.pushed_mass),
            "quotient_mass": fraction_text(self.quotient_mass),
        }


@dataclass(frozen=True)
class PathLawTransportAudit(Generic[AbstractStateT, ActionT]):
    commutes: bool
    horizon: int
    concrete_path_count: int
    abstract_path_count: int
    total_variation: Fraction
    mismatches: tuple[PathMassMismatch[AbstractStateT, ActionT], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "commutes": self.commutes,
            "horizon": self.horizon,
            "concrete_path_count": self.concrete_path_count,
            "abstract_path_count": self.abstract_path_count,
            "total_variation": fraction_text(self.total_variation),
            "mismatch_count": len(self.mismatches),
            "mismatches": [mismatch.as_dict() for mismatch in self.mismatches],
        }


def audit_path_law_pushforward(
    system: ControlledMarkovSystem[StateT, ActionT],
    aggregation: StateAggregation[StateT, AbstractStateT],
    policy: DeterministicPolicy[StateT, ActionT],
    initial: FiniteDistribution[StateT],
    *,
    horizon: int,
) -> PathLawTransportAudit[AbstractStateT, ActionT]:
    """Compare the full pushed concrete path law with the quotient path law."""

    quotient = build_quotient_kernel(system, aggregation)
    quotient_policy = abstract_policy(system, aggregation, policy)
    concrete_law = finite_path_law(system, policy, initial, horizon=horizon)
    pushed_law = pushforward_path_law(concrete_law, aggregation)
    quotient_law = finite_path_law(
        quotient,
        quotient_policy,
        pushforward_initial_distribution(initial, aggregation),
        horizon=horizon,
    )
    all_paths = tuple(dict.fromkeys((*pushed_law.support, *quotient_law.support)))
    mismatches = tuple(
        PathMassMismatch(
            path=path,
            pushed_mass=pushed_law.probability(path),
            quotient_mass=quotient_law.probability(path),
        )
        for path in all_paths
        if pushed_law.probability(path) != quotient_law.probability(path)
    )
    distance = total_variation_distance(pushed_law, quotient_law)
    return PathLawTransportAudit(
        commutes=not mismatches and distance == 0,
        horizon=horizon,
        concrete_path_count=len(concrete_law.support),
        abstract_path_count=len(quotient_law.support),
        total_variation=distance,
        mismatches=mismatches,
    )
