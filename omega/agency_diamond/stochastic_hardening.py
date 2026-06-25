"""Hardening probes for the stochastic agency-diamond pilot.

The goal is deformer-oriented instrumentation, not agency detection.  These
checks ask whether the stochastic diamond profile resists simple false
positives, whether its axes are ablation-sensitive, and whether average-case
feedback survives a first robust ambiguity-set check.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Any

from omega.agency_diamond.challenge import SearchWitness
from omega.agency_diamond.stochastic_examples import (
    STOCHASTIC_HORIZONS,
    stochastic_blind_cases,
    stochastic_null_battery,
)
from omega.agency_diamond.stochastic_metrics import (
    StochasticDiamondMetrics,
    _fixed_sequence_event_probability_one,
    _fixed_sequence_safe_probability_one,
    _live_event_probability,
    _live_safe_probability,
    coherence_reports,
    evaluate_stochastic_system,
)
from omega.agency_diamond.stochastic_model import (
    Action,
    State,
    StochasticControlledSystem,
)


@dataclass(frozen=True)
class StochasticAblationWitness:
    name: str
    passed: bool
    source_case: str | None
    ablated_case: str | None
    details: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "source_case": self.source_case,
            "ablated_case": self.ablated_case,
            "details": self.details,
        }


@dataclass(frozen=True)
class RobustStochasticProfile:
    case_id: str
    system_id: str
    horizon: int
    live_worst_case: Fraction
    replay_worst_case: Fraction
    robust_feedback_advantage: Fraction
    live_by_scenario: dict[str, Fraction]
    best_replay_sequence: tuple[Action, ...]
    replay_by_scenario: dict[str, Fraction]
    reflexive_live_worst_case: Fraction | None = None
    reflexive_replay_worst_case: Fraction | None = None
    robust_reflexive_advantage: Fraction | None = None
    joint_live_worst_case: Fraction | None = None
    joint_replay_worst_case: Fraction | None = None
    robust_joint_effect_delta: Fraction | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "system_id": self.system_id,
            "horizon": self.horizon,
            "live_worst_case": _frac(self.live_worst_case),
            "replay_worst_case": _frac(self.replay_worst_case),
            "robust_feedback_advantage": _frac(self.robust_feedback_advantage),
            "live_by_scenario": _fraction_map(self.live_by_scenario),
            "best_replay_sequence": list(self.best_replay_sequence),
            "replay_by_scenario": _fraction_map(self.replay_by_scenario),
            "reflexive_live_worst_case": _optional_frac(self.reflexive_live_worst_case),
            "reflexive_replay_worst_case": _optional_frac(self.reflexive_replay_worst_case),
            "robust_reflexive_advantage": _optional_frac(self.robust_reflexive_advantage),
            "joint_live_worst_case": _optional_frac(self.joint_live_worst_case),
            "joint_replay_worst_case": _optional_frac(self.joint_replay_worst_case),
            "robust_joint_effect_delta": _optional_frac(self.robust_joint_effect_delta),
        }


def stochastic_hardening_summary() -> dict[str, Any]:
    blind_cases = stochastic_blind_cases()
    metrics = [
        evaluate_stochastic_system(
            case.system,
            horizon=horizon,
            case_id=f"blind__seed{case.seed}_h{horizon}",
        )
        for case in blind_cases
        for horizon in STOCHASTIC_HORIZONS
    ]
    false_positive = false_positive_search(metrics, tuple(case.system for case in blind_cases))
    ablations = stochastic_ablation_probe_summary(tuple(case.system for case in blind_cases))
    robust = robust_ambiguity_summary()
    gates = {
        "false_positive_search_passed": all(
            witness.passed for witness in false_positive["witnesses"]
        ),
        "ablation_probes_passed": all(ablations["probe_status"].values()),
        "robust_ambiguity_checks_passed": all(robust["hypothesis_status"].values()),
        "negative_controls_retained": bool(false_positive["retained_false_positive_controls"]),
    }
    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "claim_boundary": (
            "Exploratory finite stochastic deformer hardening only. These "
            "checks test false-positive controls, ablation sensitivity, and "
            "robust ambiguity-set profiles for the stochastic diamond. They "
            "do not detect agency, identity, value, valuerhood, or Omega, and "
            "do not validate empirical transition models."
        ),
        "false_positive_search": {
            "witnesses": [witness.as_dict() for witness in false_positive["witnesses"]],
            "retained_false_positive_controls": false_positive[
                "retained_false_positive_controls"
            ],
        },
        "ablation_probes": ablations,
        "robust_ambiguity": robust,
        "decision_gate": gates,
    }


def false_positive_search(
    metrics: list[StochasticDiamondMetrics],
    systems: tuple[StochasticControlledSystem, ...],
) -> dict[str, Any]:
    non_lumpable = next(
        (
            report
            for system in systems
            for report in coherence_reports(system)
            if not report.strongly_lumpable
        ),
        None,
    )
    witnesses = [
        _metric_witness(
            metrics,
            name="high_live_probability_does_not_imply_feedback_deformation",
            predicate=lambda m: m.live_maintenance_probability == 1
            and m.feedback_advantage == 0,
            details=lambda m: {
                "live_maintenance_probability": _frac(m.live_maintenance_probability),
                "feedback_advantage": _frac(m.feedback_advantage),
                "classification": m.classification,
            },
        ),
        _metric_witness(
            metrics,
            name="stochasticity_does_not_imply_controllable_deformation",
            predicate=lambda m: m.stochasticity_detected and m.control_reach_count == 0,
            details=lambda m: {
                "stochasticity_detected": m.stochasticity_detected,
                "control_reach_count": m.control_reach_count,
                "classification": m.classification,
            },
        ),
        _metric_witness(
            metrics,
            name="positive_feedback_does_not_imply_reflexive_deformation",
            predicate=lambda m: m.feedback_advantage > 0
            and not _positive_optional(m.reflexive_advantage),
            details=lambda m: {
                "feedback_advantage": _frac(m.feedback_advantage),
                "reflexive_advantage": _optional_frac(m.reflexive_advantage),
                "classification": m.classification,
            },
        ),
        SearchWitness(
            name="non_lumpable_presentation_blocks_stochastic_process_transport",
            passed=non_lumpable is not None,
            left_case=None,
            right_case=None,
            details={} if non_lumpable is None else non_lumpable.as_dict(),
        ),
        _metric_witness(
            metrics,
            name="positive_feedback_can_have_negative_joint_deformation",
            predicate=lambda m: m.feedback_advantage > 0
            and m.joint_effect_delta is not None
            and m.joint_effect_delta < 0,
            details=lambda m: {
                "feedback_advantage": _frac(m.feedback_advantage),
                "joint_effect_delta": _optional_frac(m.joint_effect_delta),
                "classification": m.classification,
            },
        ),
    ]
    retained = {
        "high_live_without_feedback": _maybe_metric(
            _first_metric(
                metrics,
                lambda m: m.live_maintenance_probability == 1 and m.feedback_advantage == 0,
            )
        ),
        "stochasticity_without_control": _maybe_metric(
            _first_metric(
                metrics,
                lambda m: m.stochasticity_detected and m.control_reach_count == 0,
            )
        ),
        "feedback_without_reflexive": _maybe_metric(
            _first_metric(
                metrics,
                lambda m: m.feedback_advantage > 0
                and not _positive_optional(m.reflexive_advantage),
            )
        ),
        "negative_joint_with_feedback": _maybe_metric(
            _first_metric(
                metrics,
                lambda m: m.feedback_advantage > 0
                and m.joint_effect_delta is not None
                and m.joint_effect_delta < 0,
            )
        ),
    }
    return {
        "witnesses": witnesses,
        "retained_false_positive_controls": retained,
    }


def stochastic_ablation_probe_summary(
    systems: tuple[StochasticControlledSystem, ...],
) -> dict[str, Any]:
    witnesses = [
        _ablation_witness(
            systems,
            name="stochastic_observation_ablation_reduces_feedback",
            transform=constant_observation_ablation,
            source_predicate=lambda m: m.feedback_advantage > 0,
            result_predicate=lambda original, ablated: ablated.feedback_advantage
            < original.feedback_advantage,
            details=lambda original, ablated: {
                "original_feedback": _frac(original.feedback_advantage),
                "ablated_feedback": _frac(ablated.feedback_advantage),
            },
        ),
        _ablation_witness(
            systems,
            name="stochastic_fixed_policy_ablation_reduces_feedback",
            transform=fixed_policy_ablation,
            source_predicate=lambda m: m.feedback_advantage > 0,
            result_predicate=lambda original, ablated: ablated.feedback_advantage
            < original.feedback_advantage,
            details=lambda original, ablated: {
                "original_feedback": _frac(original.feedback_advantage),
                "ablated_feedback": _frac(ablated.feedback_advantage),
            },
        ),
        _ablation_witness(
            systems,
            name="stochastic_action_choice_ablation_removes_control",
            transform=single_action_dynamics_ablation,
            source_predicate=lambda m: m.control_reach_count > 0,
            result_predicate=lambda _original, ablated: ablated.control_reach_count == 0,
            details=lambda original, ablated: {
                "original_control_reach_count": original.control_reach_count,
                "ablated_control_reach_count": ablated.control_reach_count,
            },
        ),
        _ablation_witness(
            systems,
            name="stochastic_channel_ablation_reduces_reflexive_maintenance",
            transform=break_channel_repair_ablation,
            source_predicate=lambda m: _positive_optional(m.reflexive_advantage),
            result_predicate=lambda original, ablated: (
                ablated.reflexive_advantage is None
                or ablated.reflexive_advantage < original.reflexive_advantage
            ),
            details=lambda original, ablated: {
                "original_reflexive": _optional_frac(original.reflexive_advantage),
                "ablated_reflexive": _optional_frac(ablated.reflexive_advantage),
            },
        ),
        _ablation_witness(
            systems,
            name="stochastic_joint_ablation_changes_joint_effect",
            transform=neutralize_joint_surface_ablation,
            source_predicate=lambda m: m.joint_effect_delta is not None
            and m.joint_effect_delta < 0,
            result_predicate=lambda original, ablated: ablated.joint_effect_delta
            != original.joint_effect_delta,
            details=lambda original, ablated: {
                "original_joint": _optional_frac(original.joint_effect_delta),
                "ablated_joint": _optional_frac(ablated.joint_effect_delta),
            },
        ),
    ]
    return {
        "probe_status": {witness.name: witness.passed for witness in witnesses},
        "witnesses": [witness.as_dict() for witness in witnesses],
    }


def robust_ambiguity_summary() -> dict[str, Any]:
    null = stochastic_null_battery()
    feedback = _first_system(null, lambda system: system.family == "stochastic_feedback")
    reflexive = _first_system(null, lambda system: system.family == "stochastic_reflexive")
    joint_negative = _first_system(
        null,
        lambda system: system.family == "stochastic_joint_negative",
    )
    fragile = fragile_average_feedback_system()
    profiles = {
        "robust_feedback_positive": robust_profile(feedback, horizon=1),
        "robust_reflexive_positive": robust_profile(reflexive, horizon=1),
        "fragile_average_feedback_not_robust": robust_profile(fragile, horizon=1),
        "robust_joint_contraction_retained": robust_profile(joint_negative, horizon=1),
    }
    fragile_average = evaluate_stochastic_system(
        fragile,
        horizon=1,
        case_id="fragile_average_feedback_h1",
    )
    hypotheses = {
        "robust_feedback_positive": profiles[
            "robust_feedback_positive"
        ].robust_feedback_advantage
        > 0,
        "robust_reflexive_positive": _positive_optional(
            profiles["robust_reflexive_positive"].robust_reflexive_advantage
        ),
        "average_feedback_can_fail_robust_gate": (
            fragile_average.feedback_advantage > 0
            and profiles[
                "fragile_average_feedback_not_robust"
            ].robust_feedback_advantage
            == 0
        ),
        "robust_joint_contraction_retained": (
            profiles["robust_joint_contraction_retained"].robust_joint_effect_delta
            is not None
            and profiles["robust_joint_contraction_retained"].robust_joint_effect_delta
            < 0
        ),
    }
    return {
        "profiles": {name: profile.as_dict() for name, profile in profiles.items()},
        "fragile_average_metric": fragile_average.as_dict(),
        "hypothesis_status": hypotheses,
    }


def robust_profile(
    system: StochasticControlledSystem,
    *,
    horizon: int,
) -> RobustStochasticProfile:
    perturbations = tuple(s for s in system.scenarios if s != system.nominal_scenario)
    live_by_scenario = {
        scenario: _live_event_probability(
            system,
            scenario=scenario,
            horizon=horizon,
            safe_states=system.viable_states,
            final_states=system.target_states,
        )
        for scenario in perturbations
    }
    best_sequence, replay_by_scenario = _best_open_loop_worst_case_event(
        system,
        scenarios=perturbations,
        horizon=horizon,
        safe_states=system.viable_states,
        final_states=system.target_states,
    )
    live_worst = min(live_by_scenario.values()) if live_by_scenario else Fraction(0)
    replay_worst = min(replay_by_scenario.values()) if replay_by_scenario else Fraction(0)

    if system.channel_challenge_scenarios:
        reflexive_live_by_scenario = {
            scenario: _live_event_probability(
                system,
                scenario=scenario,
                horizon=horizon,
                safe_states=system.viable_states,
                final_states=system.target_states & system.channel_states,
            )
            for scenario in system.channel_challenge_scenarios
        }
        _sequence, reflexive_replay_by_scenario = _best_open_loop_worst_case_event(
            system,
            scenarios=system.channel_challenge_scenarios,
            horizon=horizon,
            safe_states=system.viable_states,
            final_states=system.target_states & system.channel_states,
        )
        reflexive_live = min(reflexive_live_by_scenario.values())
        reflexive_replay = min(reflexive_replay_by_scenario.values())
        reflexive_advantage: Fraction | None = reflexive_live - reflexive_replay
    else:
        reflexive_live = None
        reflexive_replay = None
        reflexive_advantage = None

    if system.joint_safe_states is not None:
        joint_live_by_scenario = {
            scenario: _live_safe_probability(
                system,
                scenario=scenario,
                horizon=horizon,
                safe_states=system.joint_safe_states,
            )
            for scenario in perturbations
        }
        _sequence, joint_replay_by_scenario = _best_open_loop_worst_case_safe(
            system,
            scenarios=perturbations,
            horizon=horizon,
            safe_states=system.joint_safe_states,
        )
        joint_live = min(joint_live_by_scenario.values())
        joint_replay = min(joint_replay_by_scenario.values())
        joint_effect: Fraction | None = joint_live - joint_replay
    else:
        joint_live = None
        joint_replay = None
        joint_effect = None

    return RobustStochasticProfile(
        case_id=f"{system.system_id}_robust_h{horizon}",
        system_id=system.system_id,
        horizon=horizon,
        live_worst_case=live_worst,
        replay_worst_case=replay_worst,
        robust_feedback_advantage=live_worst - replay_worst,
        live_by_scenario=live_by_scenario,
        best_replay_sequence=best_sequence,
        replay_by_scenario=replay_by_scenario,
        reflexive_live_worst_case=reflexive_live,
        reflexive_replay_worst_case=reflexive_replay,
        robust_reflexive_advantage=reflexive_advantage,
        joint_live_worst_case=joint_live,
        joint_replay_worst_case=joint_replay,
        robust_joint_effect_delta=joint_effect,
    )


def constant_observation_ablation(
    system: StochasticControlledSystem,
) -> StochasticControlledSystem | None:
    action = system.actions[0]
    return replace(
        system,
        system_id=f"{system.system_id}__constant_observation",
        observations=("constant",),
        observe={state: "constant" for state in system.states},
        live_policy={"constant": action},
    )


def fixed_policy_ablation(
    system: StochasticControlledSystem,
) -> StochasticControlledSystem | None:
    action = system.actions[0]
    return replace(
        system,
        system_id=f"{system.system_id}__fixed_policy",
        live_policy={observation: action for observation in system.observations},
    )


def single_action_dynamics_ablation(
    system: StochasticControlledSystem,
) -> StochasticControlledSystem | None:
    base_action = system.actions[0]
    transition = {}
    for scenario, kernel in system.transition.items():
        transition[scenario] = {
            state: {
                action: dict(kernel[state][base_action])
                for action in system.actions
            }
            for state in system.states
        }
    return replace(
        system,
        system_id=f"{system.system_id}__single_action_dynamics",
        transition=transition,
    )


def break_channel_repair_ablation(
    system: StochasticControlledSystem,
) -> StochasticControlledSystem | None:
    if not system.channel_challenge_scenarios or "bad" not in system.states:
        return None
    transition = _copy_transition(system)
    bad_row = _row(system.states, {"bad": Fraction(1)})
    for scenario in system.channel_challenge_scenarios:
        start = system.scenario_starts[scenario]
        for action in system.actions:
            transition[scenario][start][action] = dict(bad_row)
    return replace(
        system,
        system_id=f"{system.system_id}__break_channel_repair",
        transition=transition,
    )


def neutralize_joint_surface_ablation(
    system: StochasticControlledSystem,
) -> StochasticControlledSystem | None:
    if system.joint_safe_states is None:
        return None
    return replace(
        system,
        system_id=f"{system.system_id}__neutral_joint_surface",
        joint_safe_states=frozenset(system.states),
    )


def fragile_average_feedback_system() -> StochasticControlledSystem:
    states = ("need0", "need1", "blocked", "goal", "bad")
    actions = ("a0", "a1")
    scenarios = ("nominal", "p0", "p1", "sabotage")
    success = Fraction(4, 5)
    fail = Fraction(1, 5)
    kernel = {
        state: {action: _row(states, {state: Fraction(1)}) for action in actions}
        for state in states
    }
    kernel["need0"] = {
        "a0": _row(states, {"goal": success, "bad": fail}),
        "a1": _row(states, {"bad": Fraction(1)}),
    }
    kernel["need1"] = {
        "a0": _row(states, {"bad": Fraction(1)}),
        "a1": _row(states, {"goal": success, "bad": fail}),
    }
    kernel["blocked"] = {
        "a0": _row(states, {"bad": Fraction(1)}),
        "a1": _row(states, {"bad": Fraction(1)}),
    }
    kernel["goal"] = {action: _row(states, {"goal": Fraction(1)}) for action in actions}
    kernel["bad"] = {action: _row(states, {"bad": Fraction(1)}) for action in actions}
    return StochasticControlledSystem(
        system_id="fragile_average_feedback",
        family="stochastic_robust_negative_control",
        description=(
            "Average-case live feedback beats open-loop replay, but one "
            "adversarial scenario destroys the robust worst-case advantage."
        ),
        states=states,
        actions=actions,
        observations=("o0", "o1", "oblock", "og", "ob"),
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={
            "nominal": "need0",
            "p0": "need0",
            "p1": "need1",
            "sabotage": "blocked",
        },
        transition={scenario: kernel for scenario in scenarios},
        observe={
            "need0": "o0",
            "need1": "o1",
            "blocked": "oblock",
            "goal": "og",
            "bad": "ob",
        },
        live_policy={"o0": "a0", "o1": "a1", "oblock": "a0", "og": "a0", "ob": "a0"},
        target_states=frozenset({"goal"}),
        viable_states=frozenset({"need0", "need1", "goal"}),
        channel_states=frozenset({"goal"}),
        presentations={
            "identity": {state: state for state in states},
            "need_merge": {
                state: "need" if state in {"need0", "need1"} else state
                for state in states
            },
        },
    )


def _ablation_witness(
    systems: tuple[StochasticControlledSystem, ...],
    *,
    name: str,
    transform,
    source_predicate,
    result_predicate,
    details,
) -> StochasticAblationWitness:
    for system in systems:
        for horizon in STOCHASTIC_HORIZONS:
            original = evaluate_stochastic_system(
                system,
                horizon=horizon,
                case_id=f"{system.system_id}_h{horizon}",
            )
            if not source_predicate(original):
                continue
            ablated_system = transform(system)
            if ablated_system is None:
                continue
            ablated = evaluate_stochastic_system(
                ablated_system,
                horizon=horizon,
                case_id=f"{ablated_system.system_id}_h{horizon}",
            )
            if result_predicate(original, ablated):
                return StochasticAblationWitness(
                    name=name,
                    passed=True,
                    source_case=original.case_id,
                    ablated_case=ablated.case_id,
                    details=details(original, ablated),
                )
    return StochasticAblationWitness(
        name=name,
        passed=False,
        source_case=None,
        ablated_case=None,
        details={},
    )


def _best_open_loop_worst_case_event(
    system: StochasticControlledSystem,
    *,
    scenarios: tuple[str, ...],
    horizon: int,
    safe_states: frozenset[State],
    final_states: frozenset[State],
) -> tuple[tuple[Action, ...], dict[str, Fraction]]:
    best_sequence: tuple[Action, ...] | None = None
    best_by_scenario: dict[str, Fraction] | None = None
    best_worst: Fraction | None = None
    for sequence in itertools.product(system.actions, repeat=horizon):
        by_scenario = {
            scenario: _fixed_sequence_event_probability_one(
                system,
                scenario=scenario,
                actions=tuple(sequence),
                safe_states=safe_states,
                final_states=final_states,
            )
            for scenario in scenarios
        }
        worst = min(by_scenario.values()) if by_scenario else Fraction(0)
        if best_worst is None or worst > best_worst:
            best_sequence = tuple(sequence)
            best_by_scenario = by_scenario
            best_worst = worst
    assert best_sequence is not None
    assert best_by_scenario is not None
    return best_sequence, best_by_scenario


def _best_open_loop_worst_case_safe(
    system: StochasticControlledSystem,
    *,
    scenarios: tuple[str, ...],
    horizon: int,
    safe_states: frozenset[State],
) -> tuple[tuple[Action, ...], dict[str, Fraction]]:
    best_sequence: tuple[Action, ...] | None = None
    best_by_scenario: dict[str, Fraction] | None = None
    best_worst: Fraction | None = None
    for sequence in itertools.product(system.actions, repeat=horizon):
        by_scenario = {
            scenario: _fixed_sequence_safe_probability_one(
                system,
                scenario=scenario,
                actions=tuple(sequence),
                safe_states=safe_states,
            )
            for scenario in scenarios
        }
        worst = min(by_scenario.values()) if by_scenario else Fraction(0)
        if best_worst is None or worst > best_worst:
            best_sequence = tuple(sequence)
            best_by_scenario = by_scenario
            best_worst = worst
    assert best_sequence is not None
    assert best_by_scenario is not None
    return best_sequence, best_by_scenario


def _metric_witness(
    metrics: list[StochasticDiamondMetrics],
    *,
    name: str,
    predicate,
    details,
) -> SearchWitness:
    metric = _first_metric(metrics, predicate)
    return SearchWitness(
        name=name,
        passed=metric is not None,
        left_case=None if metric is None else metric.case_id,
        right_case=None,
        details={} if metric is None else details(metric),
    )


def _first_metric(
    metrics: list[StochasticDiamondMetrics],
    predicate,
) -> StochasticDiamondMetrics | None:
    return next((metric for metric in metrics if predicate(metric)), None)


def _first_system(
    systems: tuple[StochasticControlledSystem, ...],
    predicate,
) -> StochasticControlledSystem:
    system = next((candidate for candidate in systems if predicate(candidate)), None)
    if system is None:
        raise ValueError("expected system was not found")
    return system


def _copy_transition(system: StochasticControlledSystem) -> dict[str, dict[str, dict[str, dict[str, Fraction]]]]:
    return {
        scenario: {
            state: {
                action: dict(row)
                for action, row in by_action.items()
            }
            for state, by_action in kernel.items()
        }
        for scenario, kernel in system.transition.items()
    }


def _row(states: tuple[State, ...], entries: dict[State, Fraction]) -> dict[State, Fraction]:
    row = {state: entries.get(state, Fraction(0)) for state in states}
    total = sum(row.values(), start=Fraction(0))
    if total != 1:
        raise ValueError(f"row sums to {total}, not 1: {entries}")
    return row


def _maybe_metric(metric: StochasticDiamondMetrics | None) -> dict[str, Any] | None:
    return None if metric is None else metric.as_dict()


def _positive_optional(value: Fraction | None) -> bool:
    return value is not None and value > 0


def _fraction_map(values: dict[str, Fraction]) -> dict[str, str]:
    return {key: _frac(value) for key, value in sorted(values.items())}


def _frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _optional_frac(value: Fraction | None) -> str | None:
    return None if value is None else _frac(value)
