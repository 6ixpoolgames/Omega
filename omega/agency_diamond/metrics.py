"""Metrics for the finite operational-causal-diamond pilot."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from omega.agency_diamond.model import (
    ControlledSystem,
    EvaluationCase,
    State,
    Trace,
    live_action,
    simulate_live,
    simulate_replay,
    validate_system,
)


@dataclass(frozen=True)
class DiamondMetrics:
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
    live_maintenance_score: Fraction
    replay_maintenance_score: Fraction
    ablated_maintenance_score: Fraction
    feedback_advantage: Fraction
    leverage_advantage: Fraction
    reflexive_live_score: Fraction | None
    reflexive_replay_score: Fraction | None
    reflexive_advantage: Fraction | None
    joint_live_score: Fraction | None
    joint_replay_score: Fraction | None
    joint_effect_delta: Fraction | None
    recurrence_detected: bool
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
            "live_maintenance_score": _frac(self.live_maintenance_score),
            "replay_maintenance_score": _frac(self.replay_maintenance_score),
            "ablated_maintenance_score": _frac(self.ablated_maintenance_score),
            "feedback_advantage": _frac(self.feedback_advantage),
            "leverage_advantage": _frac(self.leverage_advantage),
            "reflexive_live_score": _maybe_frac(self.reflexive_live_score),
            "reflexive_replay_score": _maybe_frac(self.reflexive_replay_score),
            "reflexive_advantage": _maybe_frac(self.reflexive_advantage),
            "joint_live_score": _maybe_frac(self.joint_live_score),
            "joint_replay_score": _maybe_frac(self.joint_replay_score),
            "joint_effect_delta": _maybe_frac(self.joint_effect_delta),
            "recurrence_detected": self.recurrence_detected,
            "scenario_count": self.scenario_count,
            "perturbation_count": self.perturbation_count,
            "channel_challenge_count": self.channel_challenge_count,
        }


def evaluate_case(case: EvaluationCase) -> DiamondMetrics:
    return evaluate_system(case.system, horizon=case.horizon, case_id=case.case_id)


def evaluate_system(
    system: ControlledSystem,
    *,
    horizon: int,
    case_id: str | None = None,
) -> DiamondMetrics:
    validate_system(system)
    if horizon < 1:
        raise ValueError("horizon must be positive")

    case_id = case_id or f"{system.system_id}_h{horizon}"
    perturbations = tuple(s for s in system.scenarios if s != system.nominal_scenario)
    nominal_trace = simulate_live(
        system,
        scenario=system.nominal_scenario,
        horizon=horizon,
    )
    replay_actions = nominal_trace.actions

    live_traces = [
        simulate_live(system, scenario=scenario, horizon=horizon)
        for scenario in perturbations
    ]
    replay_traces = [
        simulate_replay(system, scenario=scenario, replay_actions=replay_actions)
        for scenario in perturbations
    ]
    ablated_traces = [
        simulate_replay(
            system,
            scenario=scenario,
            replay_actions=tuple(system.actions[0] for _ in range(horizon)),
        )
        for scenario in perturbations
    ]

    live_maintenance = _score(live_traces, _maintains_target(system))
    replay_maintenance = _score(replay_traces, _maintains_target(system))
    ablated_maintenance = _score(ablated_traces, _maintains_target(system))

    control_states = _all_action_reachable_states(system, horizon=horizon)
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
        live_channel = [
            simulate_live(system, scenario=scenario, horizon=horizon)
            for scenario in system.channel_challenge_scenarios
        ]
        replay_channel = [
            simulate_replay(system, scenario=scenario, replay_actions=replay_actions)
            for scenario in system.channel_challenge_scenarios
        ]
        reflexive_live = _score(live_channel, _maintains_reflexive_channel(system))
        reflexive_replay = _score(replay_channel, _maintains_reflexive_channel(system))
        reflexive_advantage: Fraction | None = reflexive_live - reflexive_replay
    else:
        reflexive_live = None
        reflexive_replay = None
        reflexive_advantage = None

    if system.joint_safe_states is not None:
        live_joint = _score(live_traces, _maintains_joint(system))
        replay_joint = _score(replay_traces, _maintains_joint(system))
        joint_effect = live_joint - replay_joint
    else:
        live_joint = None
        replay_joint = None
        joint_effect = None

    classification = _classify(
        control_count=len(controllable),
        observable_count=len(observable),
        live_maintenance=live_maintenance,
        replay_maintenance=replay_maintenance,
        feedback_advantage=live_maintenance - replay_maintenance,
        reflexive_advantage=reflexive_advantage,
        joint_effect=joint_effect,
        recurrence_detected=_has_recurrence(nominal_trace),
    )

    denominator = max(1, len(control_states))
    return DiamondMetrics(
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
        live_maintenance_score=live_maintenance,
        replay_maintenance_score=replay_maintenance,
        ablated_maintenance_score=ablated_maintenance,
        feedback_advantage=live_maintenance - replay_maintenance,
        leverage_advantage=live_maintenance - ablated_maintenance,
        reflexive_live_score=reflexive_live,
        reflexive_replay_score=reflexive_replay,
        reflexive_advantage=reflexive_advantage,
        joint_live_score=live_joint,
        joint_replay_score=replay_joint,
        joint_effect_delta=joint_effect,
        recurrence_detected=_has_recurrence(nominal_trace),
        scenario_count=len(system.scenarios),
        perturbation_count=len(perturbations),
        channel_challenge_count=len(system.channel_challenge_scenarios),
    )


def _maintains_target(system: ControlledSystem):
    def check(trace: Trace) -> bool:
        return all(state in system.viable_states for state in trace.states) and (
            trace.final_state in system.target_states
        )

    return check


def _maintains_reflexive_channel(system: ControlledSystem):
    def check(trace: Trace) -> bool:
        return (
            all(state in system.viable_states for state in trace.states)
            and trace.final_state in system.target_states
            and trace.final_state in system.channel_states
        )

    return check


def _maintains_joint(system: ControlledSystem):
    if system.joint_safe_states is None:
        raise ValueError("system has no joint_safe_states")

    def check(trace: Trace) -> bool:
        return all(state in system.joint_safe_states for state in trace.states)

    return check


def _score(traces: list[Trace], predicate) -> Fraction:
    if not traces:
        return Fraction(0)
    return Fraction(sum(1 for trace in traces if predicate(trace)), len(traces))


def _all_action_reachable_states(system: ControlledSystem, *, horizon: int) -> set[State]:
    seen = set(system.scenario_starts.values())
    frontiers = {
        scenario: {start}
        for scenario, start in system.scenario_starts.items()
    }
    for _ in range(horizon):
        for scenario, frontier in list(frontiers.items()):
            next_frontier: set[State] = set()
            for state in frontier:
                for action in system.actions:
                    next_frontier.add(system.transition[scenario][state][action])
            seen.update(next_frontier)
            frontiers[scenario] = next_frontier
    return seen


def _state_has_control(system: ControlledSystem, state: State, *, horizon: int) -> bool:
    signatures = {
        tuple(
            _future_signature_after_action(
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
    system: ControlledSystem, state: State, *, horizon: int
) -> bool:
    signature_to_observations: dict[tuple[bool, ...], set[tuple[str, ...]]] = {}
    for action in system.actions:
        signature = tuple(
            bit
            for scenario in system.scenarios
            for bit in _future_signature_after_action(
                system,
                state,
                action,
                scenario=scenario,
                horizon=horizon,
            )
        )
        observations = tuple(
            obs
            for scenario in system.scenarios
            for obs in _future_observations_after_action(
                system,
                state,
                action,
                scenario=scenario,
                horizon=horizon,
            )
        )
        signature_to_observations.setdefault(signature, set()).add(observations)
    if len(signature_to_observations) <= 1:
        return False
    all_observations = set().union(*signature_to_observations.values())
    return len(all_observations) > 1


def _future_signature_after_action(
    system: ControlledSystem, state: State, action: str, *, scenario: str, horizon: int
) -> tuple[bool, ...]:
    current = system.transition[scenario][state][action]
    bits = [current in system.target_states]
    for _ in range(max(0, horizon - 1)):
        current = system.transition[scenario][current][live_action(system, current)]
        bits.append(current in system.target_states)
    return tuple(bits)


def _future_observations_after_action(
    system: ControlledSystem, state: State, action: str, *, scenario: str, horizon: int
) -> tuple[str, ...]:
    current = system.transition[scenario][state][action]
    observations = [system.observe[current]]
    for _ in range(max(0, horizon - 1)):
        current = system.transition[scenario][current][live_action(system, current)]
        observations.append(system.observe[current])
    return tuple(observations)


def _has_recurrence(trace: Trace) -> bool:
    return len(set(trace.states)) < len(trace.states)


def _classify(
    *,
    control_count: int,
    observable_count: int,
    live_maintenance: Fraction,
    replay_maintenance: Fraction,
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
    if recurrence_detected and live_maintenance >= replay_maintenance:
        return "passive_or_driven_recurrence"
    return "passive_persistence"


def _frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _maybe_frac(value: Fraction | None) -> str | None:
    return None if value is None else _frac(value)
