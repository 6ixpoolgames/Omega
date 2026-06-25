"""Exact-rational stochastic metrics for operational causal-diamond pilots."""

from __future__ import annotations

import itertools
from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping

from omega.agency_diamond.stochastic_model import (
    Action,
    Scenario,
    State,
    StochasticControlledSystem,
    StochasticEvaluationCase,
    live_action,
    point_mass,
    step_distribution,
    support_successors,
    validate_stochastic_system,
)


@dataclass(frozen=True)
class StochasticDiamondMetrics:
    case_id: str
    system_id: str
    family: str
    horizon: int
    classification: str
    control_reach_count: int
    observable_control_count: int
    operational_diamond_count: int
    control_reach_ratio: Fraction
    observability_ratio: Fraction
    live_maintenance_probability: Fraction
    replay_maintenance_probability: Fraction
    ablated_maintenance_probability: Fraction
    feedback_advantage: Fraction
    leverage_advantage: Fraction
    reflexive_live_probability: Fraction | None
    reflexive_replay_probability: Fraction | None
    reflexive_advantage: Fraction | None
    joint_live_probability: Fraction | None
    joint_replay_probability: Fraction | None
    joint_effect_delta: Fraction | None
    recurrence_detected: bool
    stochasticity_detected: bool
    best_replay_sequence: tuple[Action, ...]
    scenario_count: int
    perturbation_count: int
    channel_challenge_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "system_id": self.system_id,
            "family": self.family,
            "horizon": self.horizon,
            "classification": self.classification,
            "control_reach_count": self.control_reach_count,
            "observable_control_count": self.observable_control_count,
            "operational_diamond_count": self.operational_diamond_count,
            "control_reach_ratio": _frac(self.control_reach_ratio),
            "observability_ratio": _frac(self.observability_ratio),
            "live_maintenance_probability": _frac(self.live_maintenance_probability),
            "replay_maintenance_probability": _frac(self.replay_maintenance_probability),
            "ablated_maintenance_probability": _frac(self.ablated_maintenance_probability),
            "feedback_advantage": _frac(self.feedback_advantage),
            "leverage_advantage": _frac(self.leverage_advantage),
            "reflexive_live_probability": _maybe_frac(self.reflexive_live_probability),
            "reflexive_replay_probability": _maybe_frac(self.reflexive_replay_probability),
            "reflexive_advantage": _maybe_frac(self.reflexive_advantage),
            "joint_live_probability": _maybe_frac(self.joint_live_probability),
            "joint_replay_probability": _maybe_frac(self.joint_replay_probability),
            "joint_effect_delta": _maybe_frac(self.joint_effect_delta),
            "recurrence_detected": self.recurrence_detected,
            "stochasticity_detected": self.stochasticity_detected,
            "best_replay_sequence": list(self.best_replay_sequence),
            "scenario_count": self.scenario_count,
            "perturbation_count": self.perturbation_count,
            "channel_challenge_count": self.channel_challenge_count,
        }


@dataclass(frozen=True)
class LumpabilityReport:
    presentation_id: str
    strongly_lumpable: bool
    witness_count: int
    witnesses: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "presentation_id": self.presentation_id,
            "strongly_lumpable": self.strongly_lumpable,
            "witness_count": self.witness_count,
            "witnesses": list(self.witnesses),
        }


def evaluate_stochastic_case(case: StochasticEvaluationCase) -> StochasticDiamondMetrics:
    return evaluate_stochastic_system(
        case.system,
        horizon=case.horizon,
        case_id=case.case_id,
    )


def evaluate_stochastic_system(
    system: StochasticControlledSystem,
    *,
    horizon: int,
    case_id: str | None = None,
) -> StochasticDiamondMetrics:
    validate_stochastic_system(system)
    if horizon < 1:
        raise ValueError("horizon must be positive")

    case_id = case_id or f"{system.system_id}_h{horizon}"
    perturbations = tuple(s for s in system.scenarios if s != system.nominal_scenario)
    live_maintenance = _average_live_event_probability(
        system,
        scenarios=perturbations,
        horizon=horizon,
        safe_states=system.viable_states,
        final_states=system.target_states,
    )
    best_replay, replay_maintenance = _best_open_loop_event_probability(
        system,
        scenarios=perturbations,
        horizon=horizon,
        safe_states=system.viable_states,
        final_states=system.target_states,
    )
    ablated_maintenance = _fixed_sequence_event_probability(
        system,
        scenarios=perturbations,
        actions=tuple(system.actions[0] for _ in range(horizon)),
        safe_states=system.viable_states,
        final_states=system.target_states,
    )

    control_states = _support_reachable_states(system, horizon=horizon)
    controllable = {
        state for state in control_states if _state_has_control(system, state, horizon=horizon)
    }
    observable = {
        state
        for state in controllable
        if _state_has_observable_control(system, state, horizon=horizon)
    }
    diamond = controllable & observable

    if system.channel_challenge_scenarios:
        reflexive_live = _average_live_event_probability(
            system,
            scenarios=system.channel_challenge_scenarios,
            horizon=horizon,
            safe_states=system.viable_states,
            final_states=system.target_states & system.channel_states,
        )
        _reflexive_replay_sequence, reflexive_replay = _best_open_loop_event_probability(
            system,
            scenarios=system.channel_challenge_scenarios,
            horizon=horizon,
            safe_states=system.viable_states,
            final_states=system.target_states & system.channel_states,
        )
        reflexive_advantage: Fraction | None = reflexive_live - reflexive_replay
    else:
        reflexive_live = None
        reflexive_replay = None
        reflexive_advantage = None

    if system.joint_safe_states is not None:
        joint_live = _average_live_safe_probability(
            system,
            scenarios=perturbations,
            horizon=horizon,
            safe_states=system.joint_safe_states,
        )
        _joint_replay_sequence, joint_replay = _best_open_loop_safe_probability(
            system,
            scenarios=perturbations,
            horizon=horizon,
            safe_states=system.joint_safe_states,
        )
        joint_effect = joint_live - joint_replay
    else:
        joint_live = None
        joint_replay = None
        joint_effect = None

    recurrence = _has_positive_recurrence(system, horizon=horizon)
    feedback_advantage = live_maintenance - replay_maintenance
    classification = _classify(
        control_count=len(controllable),
        observable_count=len(observable),
        feedback_advantage=feedback_advantage,
        reflexive_advantage=reflexive_advantage,
        joint_effect=joint_effect,
        recurrence_detected=recurrence,
    )
    denominator = max(1, len(control_states))

    return StochasticDiamondMetrics(
        case_id=case_id,
        system_id=system.system_id,
        family=system.family,
        horizon=horizon,
        classification=classification,
        control_reach_count=len(controllable),
        observable_control_count=len(observable),
        operational_diamond_count=len(diamond),
        control_reach_ratio=Fraction(len(controllable), denominator),
        observability_ratio=Fraction(len(observable), max(1, len(controllable))),
        live_maintenance_probability=live_maintenance,
        replay_maintenance_probability=replay_maintenance,
        ablated_maintenance_probability=ablated_maintenance,
        feedback_advantage=feedback_advantage,
        leverage_advantage=live_maintenance - ablated_maintenance,
        reflexive_live_probability=reflexive_live,
        reflexive_replay_probability=reflexive_replay,
        reflexive_advantage=reflexive_advantage,
        joint_live_probability=joint_live,
        joint_replay_probability=joint_replay,
        joint_effect_delta=joint_effect,
        recurrence_detected=recurrence,
        stochasticity_detected=_has_nontrivial_probability(system),
        best_replay_sequence=best_replay,
        scenario_count=len(system.scenarios),
        perturbation_count=len(perturbations),
        channel_challenge_count=len(system.channel_challenge_scenarios),
    )


def strong_lumpability_report(
    system: StochasticControlledSystem,
    presentation_id: str,
    presentation: Mapping[State, str],
    *,
    max_witnesses: int = 8,
) -> LumpabilityReport:
    """Check stochastic block coherence for a state presentation.

    Strong lumpability requires merged representatives to induce the same
    probability distribution over presentation blocks for every action and
    scenario. This is the stochastic analogue of representative-wise process
    coherence; without it the abstract process can silently switch hidden
    representatives.
    """

    validate_stochastic_system(system)
    if set(presentation) != set(system.states):
        raise ValueError("presentation must map every declared state")

    blocks = sorted(set(presentation.values()))
    by_block: dict[str, list[State]] = {block: [] for block in blocks}
    for state in system.states:
        by_block[presentation[state]].append(state)

    witnesses: list[dict[str, Any]] = []
    for scenario in system.scenarios:
        for action in system.actions:
            for block, states in by_block.items():
                if len(states) < 2:
                    continue
                reference = _block_successor_distribution(
                    system,
                    scenario=scenario,
                    state=states[0],
                    action=action,
                    presentation=presentation,
                    blocks=blocks,
                )
                for state in states[1:]:
                    observed = _block_successor_distribution(
                        system,
                        scenario=scenario,
                        state=state,
                        action=action,
                        presentation=presentation,
                        blocks=blocks,
                    )
                    if observed != reference:
                        witnesses.append(
                            {
                                "scenario": scenario,
                                "action": action,
                                "block": block,
                                "left_state": states[0],
                                "right_state": state,
                                "left_distribution": {
                                    name: _frac(value) for name, value in reference.items()
                                },
                                "right_distribution": {
                                    name: _frac(value) for name, value in observed.items()
                                },
                            }
                        )
                        if len(witnesses) >= max_witnesses:
                            return LumpabilityReport(
                                presentation_id=presentation_id,
                                strongly_lumpable=False,
                                witness_count=len(witnesses),
                                witnesses=tuple(witnesses),
                            )

    return LumpabilityReport(
        presentation_id=presentation_id,
        strongly_lumpable=not witnesses,
        witness_count=len(witnesses),
        witnesses=tuple(witnesses),
    )


def coherence_reports(system: StochasticControlledSystem) -> list[LumpabilityReport]:
    if system.presentations is None:
        return []
    return [
        strong_lumpability_report(system, presentation_id=name, presentation=presentation)
        for name, presentation in sorted(system.presentations.items())
    ]


def _average_live_event_probability(
    system: StochasticControlledSystem,
    *,
    scenarios: tuple[Scenario, ...],
    horizon: int,
    safe_states: frozenset[State],
    final_states: frozenset[State],
) -> Fraction:
    if not scenarios:
        return Fraction(0)
    return sum(
        (
            _live_event_probability(
                system,
                scenario=scenario,
                horizon=horizon,
                safe_states=safe_states,
                final_states=final_states,
            )
            for scenario in scenarios
        ),
        start=Fraction(0),
    ) / len(scenarios)


def _average_live_safe_probability(
    system: StochasticControlledSystem,
    *,
    scenarios: tuple[Scenario, ...],
    horizon: int,
    safe_states: frozenset[State],
) -> Fraction:
    if not scenarios:
        return Fraction(0)
    return sum(
        (
            _live_safe_probability(
                system,
                scenario=scenario,
                horizon=horizon,
                safe_states=safe_states,
            )
            for scenario in scenarios
        ),
        start=Fraction(0),
    ) / len(scenarios)


def _live_event_probability(
    system: StochasticControlledSystem,
    *,
    scenario: Scenario,
    horizon: int,
    safe_states: frozenset[State],
    final_states: frozenset[State],
) -> Fraction:
    return _policy_event_probability(
        system,
        scenario=scenario,
        horizon=horizon,
        safe_states=safe_states,
        final_states=final_states,
        action_for_state=lambda state: live_action(system, state),
    )


def _live_safe_probability(
    system: StochasticControlledSystem,
    *,
    scenario: Scenario,
    horizon: int,
    safe_states: frozenset[State],
) -> Fraction:
    return _policy_safe_probability(
        system,
        scenario=scenario,
        horizon=horizon,
        safe_states=safe_states,
        action_for_state=lambda state: live_action(system, state),
    )


def _best_open_loop_event_probability(
    system: StochasticControlledSystem,
    *,
    scenarios: tuple[Scenario, ...],
    horizon: int,
    safe_states: frozenset[State],
    final_states: frozenset[State],
) -> tuple[tuple[Action, ...], Fraction]:
    best_sequence: tuple[Action, ...] | None = None
    best_score: Fraction | None = None
    for sequence in itertools.product(system.actions, repeat=horizon):
        score = _fixed_sequence_event_probability(
            system,
            scenarios=scenarios,
            actions=sequence,
            safe_states=safe_states,
            final_states=final_states,
        )
        if best_score is None or score > best_score:
            best_sequence = tuple(sequence)
            best_score = score
    assert best_sequence is not None
    assert best_score is not None
    return best_sequence, best_score


def _best_open_loop_safe_probability(
    system: StochasticControlledSystem,
    *,
    scenarios: tuple[Scenario, ...],
    horizon: int,
    safe_states: frozenset[State],
) -> tuple[tuple[Action, ...], Fraction]:
    best_sequence: tuple[Action, ...] | None = None
    best_score: Fraction | None = None
    for sequence in itertools.product(system.actions, repeat=horizon):
        score = _fixed_sequence_safe_probability(
            system,
            scenarios=scenarios,
            actions=sequence,
            safe_states=safe_states,
        )
        if best_score is None or score > best_score:
            best_sequence = tuple(sequence)
            best_score = score
    assert best_sequence is not None
    assert best_score is not None
    return best_sequence, best_score


def _fixed_sequence_event_probability(
    system: StochasticControlledSystem,
    *,
    scenarios: tuple[Scenario, ...],
    actions: tuple[Action, ...],
    safe_states: frozenset[State],
    final_states: frozenset[State],
) -> Fraction:
    if not scenarios:
        return Fraction(0)
    return sum(
        (
            _fixed_sequence_event_probability_one(
                system,
                scenario=scenario,
                actions=actions,
                safe_states=safe_states,
                final_states=final_states,
            )
            for scenario in scenarios
        ),
        start=Fraction(0),
    ) / len(scenarios)


def _fixed_sequence_safe_probability(
    system: StochasticControlledSystem,
    *,
    scenarios: tuple[Scenario, ...],
    actions: tuple[Action, ...],
    safe_states: frozenset[State],
) -> Fraction:
    if not scenarios:
        return Fraction(0)
    return sum(
        (
            _fixed_sequence_safe_probability_one(
                system,
                scenario=scenario,
                actions=actions,
                safe_states=safe_states,
            )
            for scenario in scenarios
        ),
        start=Fraction(0),
    ) / len(scenarios)


def _fixed_sequence_safe_probability_one(
    system: StochasticControlledSystem,
    *,
    scenario: Scenario,
    actions: tuple[Action, ...],
    safe_states: frozenset[State],
) -> Fraction:
    return _fixed_sequence_event_probability_one(
        system,
        scenario=scenario,
        actions=actions,
        safe_states=safe_states,
        final_states=frozenset(system.states),
    )


def _policy_event_probability(
    system: StochasticControlledSystem,
    *,
    scenario: Scenario,
    horizon: int,
    safe_states: frozenset[State],
    final_states: frozenset[State],
    action_for_state,
) -> Fraction:
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    if system.scenario_starts[scenario] not in safe_states:
        return Fraction(0)
    distribution = point_mass(system, system.scenario_starts[scenario])
    for _step in range(horizon):
        distribution = step_distribution(
            system,
            distribution,
            scenario=scenario,
            action_for_state=action_for_state,
        )
        distribution = {
            state: (mass if state in safe_states else Fraction(0))
            for state, mass in distribution.items()
        }
    return sum(
        (mass for state, mass in distribution.items() if state in final_states),
        start=Fraction(0),
    )


def _policy_safe_probability(
    system: StochasticControlledSystem,
    *,
    scenario: Scenario,
    horizon: int,
    safe_states: frozenset[State],
    action_for_state,
) -> Fraction:
    return _policy_event_probability(
        system,
        scenario=scenario,
        horizon=horizon,
        safe_states=safe_states,
        final_states=frozenset(system.states),
        action_for_state=action_for_state,
    )


def _fixed_sequence_event_probability_one(
    system: StochasticControlledSystem,
    *,
    scenario: Scenario,
    actions: tuple[Action, ...],
    safe_states: frozenset[State],
    final_states: frozenset[State],
) -> Fraction:
    if system.scenario_starts[scenario] not in safe_states:
        return Fraction(0)
    distribution = point_mass(system, system.scenario_starts[scenario])
    for action in actions:
        distribution = step_distribution(
            system,
            distribution,
            scenario=scenario,
            action_for_state=lambda _state, selected=action: selected,
        )
        distribution = {
            state: (mass if state in safe_states else Fraction(0))
            for state, mass in distribution.items()
        }
    return sum(
        (mass for state, mass in distribution.items() if state in final_states),
        start=Fraction(0),
    )


def _support_reachable_states(
    system: StochasticControlledSystem,
    *,
    horizon: int,
) -> set[State]:
    seen = set(system.scenario_starts.values())
    frontiers = {scenario: {start} for scenario, start in system.scenario_starts.items()}
    for _step in range(horizon):
        for scenario, frontier in list(frontiers.items()):
            next_frontier: set[State] = set()
            for state in frontier:
                for action in system.actions:
                    next_frontier.update(
                        support_successors(
                            system,
                            scenario=scenario,
                            state=state,
                            action=action,
                        )
                    )
            seen.update(next_frontier)
            frontiers[scenario] = next_frontier
    return seen


def _state_has_control(
    system: StochasticControlledSystem,
    state: State,
    *,
    horizon: int,
) -> bool:
    signatures = {
        tuple(
            _future_target_profile_after_action(
                system,
                state,
                action,
                scenario=scenario,
                horizon=horizon,
            )
            for scenario in system.scenarios
        )
        for action in system.actions
    }
    return len(signatures) > 1


def _state_has_observable_control(
    system: StochasticControlledSystem,
    state: State,
    *,
    horizon: int,
) -> bool:
    signatures: dict[tuple[Fraction, ...], set[tuple[tuple[str, str], ...]]] = {}
    for action in system.actions:
        target_signature = tuple(
            value
            for scenario in system.scenarios
            for value in _future_target_profile_after_action(
                system,
                state,
                action,
                scenario=scenario,
                horizon=horizon,
            )
        )
        observation_signature = tuple(
            item
            for scenario in system.scenarios
            for item in _future_observation_distribution_after_action(
                system,
                state,
                action,
                scenario=scenario,
                horizon=horizon,
            )
        )
        signatures.setdefault(target_signature, set()).add(observation_signature)
    if len(signatures) <= 1:
        return False
    all_observations = set().union(*signatures.values())
    return len(all_observations) > 1


def _future_target_profile_after_action(
    system: StochasticControlledSystem,
    state: State,
    action: Action,
    *,
    scenario: Scenario,
    horizon: int,
) -> tuple[Fraction, ...]:
    distribution = step_distribution(
        system,
        point_mass(system, state),
        scenario=scenario,
        action_for_state=lambda _state: action,
    )
    profile = [_target_mass(system, distribution)]
    for _step in range(max(0, horizon - 1)):
        distribution = step_distribution(
            system,
            distribution,
            scenario=scenario,
            action_for_state=lambda current: live_action(system, current),
        )
        profile.append(_target_mass(system, distribution))
    return tuple(profile)


def _future_observation_distribution_after_action(
    system: StochasticControlledSystem,
    state: State,
    action: Action,
    *,
    scenario: Scenario,
    horizon: int,
) -> tuple[tuple[str, str], ...]:
    distribution = step_distribution(
        system,
        point_mass(system, state),
        scenario=scenario,
        action_for_state=lambda _state: action,
    )
    for _step in range(max(0, horizon - 1)):
        distribution = step_distribution(
            system,
            distribution,
            scenario=scenario,
            action_for_state=lambda current: live_action(system, current),
        )
    by_observation = {observation: Fraction(0) for observation in system.observations}
    for state_name, mass in distribution.items():
        by_observation[system.observe[state_name]] += mass
    return tuple((observation, _frac(by_observation[observation])) for observation in system.observations)


def _target_mass(
    system: StochasticControlledSystem,
    distribution: Mapping[State, Fraction],
) -> Fraction:
    return sum(
        (mass for state, mass in distribution.items() if state in system.target_states),
        start=Fraction(0),
    )


def _has_positive_recurrence(
    system: StochasticControlledSystem,
    *,
    horizon: int,
) -> bool:
    start = system.scenario_starts[system.nominal_scenario]
    queue = deque([(start, (start,))])
    while queue:
        state, history = queue.popleft()
        if len(history) > horizon + 1:
            continue
        action = live_action(system, state)
        for target in support_successors(
            system,
            scenario=system.nominal_scenario,
            state=state,
            action=action,
        ):
            if target in history:
                return True
            queue.append((target, history + (target,)))
    return False


def _has_nontrivial_probability(system: StochasticControlledSystem) -> bool:
    for scenario in system.scenarios:
        for state in system.states:
            for action in system.actions:
                row = system.transition[scenario][state][action]
                positive = [value for value in row.values() if value > 0]
                if len(positive) > 1:
                    return True
    return False


def _block_successor_distribution(
    system: StochasticControlledSystem,
    *,
    scenario: Scenario,
    state: State,
    action: Action,
    presentation: Mapping[State, str],
    blocks: list[str],
) -> dict[str, Fraction]:
    result = {block: Fraction(0) for block in blocks}
    for target, probability in system.transition[scenario][state][action].items():
        result[presentation[target]] += probability
    return result


def _classify(
    *,
    control_count: int,
    observable_count: int,
    feedback_advantage: Fraction,
    reflexive_advantage: Fraction | None,
    joint_effect: Fraction | None,
    recurrence_detected: bool,
) -> str:
    if joint_effect is not None and joint_effect < 0:
        return "dominant_joint_contraction"
    if reflexive_advantage is not None and reflexive_advantage > 0:
        return "reflexive_maintenance"
    if feedback_advantage > 0 and observable_count > 0:
        return "feedback_advantage"
    if control_count > 0:
        return "control_without_feedback_advantage"
    if recurrence_detected:
        return "passive_or_driven_recurrence"
    return "passive_persistence"


def _frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _maybe_frac(value: Fraction | None) -> str | None:
    return None if value is None else _frac(value)
