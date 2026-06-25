"""Synthetic exact-rational stochastic examples for agency-diamond pilots."""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from omega.agency_diamond.challenge import SearchWitness
from omega.agency_diamond.stochastic_metrics import (
    StochasticDiamondMetrics,
    coherence_reports,
    evaluate_stochastic_system,
)
from omega.agency_diamond.stochastic_model import (
    Action,
    State,
    StochasticControlledSystem,
)


STOCHASTIC_HORIZONS = (1, 2, 3, 4)
STOCHASTIC_BLIND_SEEDS = tuple(range(2201, 2241))
REQUIRED_STOCHASTIC_CLASSES = {
    "passive_or_driven_recurrence",
    "control_without_feedback_advantage",
    "feedback_advantage",
    "reflexive_maintenance",
    "dominant_joint_contraction",
}


@dataclass(frozen=True)
class StochasticBlindCase:
    seed: int
    system: StochasticControlledSystem
    generator_knobs: dict[str, object]


def stochastic_null_battery() -> tuple[StochasticControlledSystem, ...]:
    return (
        _passive_persistence(),
        _passive_recurrence(),
        _control_without_feedback(),
        _feedback_advantage(),
        _reflexive_maintenance(),
        _joint_contraction(),
    )


def stochastic_blind_cases() -> tuple[StochasticBlindCase, ...]:
    return tuple(_generated_case(seed=seed) for seed in STOCHASTIC_BLIND_SEEDS)


def evaluate_stochastic_null_battery() -> list[StochasticDiamondMetrics]:
    return [
        evaluate_stochastic_system(
            system,
            horizon=horizon,
            case_id=f"null__{system.system_id}_h{horizon}",
        )
        for system in stochastic_null_battery()
        for horizon in STOCHASTIC_HORIZONS
    ]


def evaluate_stochastic_blind_cases() -> list[StochasticDiamondMetrics]:
    return [
        evaluate_stochastic_system(
            case.system,
            horizon=horizon,
            case_id=f"blind__seed{case.seed}_h{horizon}",
        )
        for case in stochastic_blind_cases()
        for horizon in STOCHASTIC_HORIZONS
    ]


def stochastic_pilot_summary() -> dict[str, Any]:
    null_metrics = evaluate_stochastic_null_battery()
    blind_cases = stochastic_blind_cases()
    blind_metrics = evaluate_stochastic_blind_cases()
    all_metrics = null_metrics + blind_metrics
    search = stochastic_counterexample_search(blind_metrics)
    coherence = stochastic_coherence_summary(tuple(case.system for case in blind_cases))
    negative = stochastic_negative_retention(blind_metrics)
    clusters = stochastic_cluster_summary(blind_metrics)
    class_set = set(metric.classification for metric in blind_metrics)

    gates = {
        "blind_pool_has_no_expected_class_labels": all(
            "expected_class" not in case.generator_knobs for case in blind_cases
        ),
        "multiple_classes_discovered": len(class_set) >= 5,
        "required_classes_discovered": REQUIRED_STOCHASTIC_CLASSES <= class_set,
        "stochasticity_present": all(metric.stochasticity_detected for metric in all_metrics),
        "counterexample_search_witnesses_found": all(witness.passed for witness in search),
        "coherence_has_positive_and_negative_controls": coherence[
            "has_lumpable_and_non_lumpable"
        ],
        "negative_results_retained": all(negative["retention_status"].values()),
    }

    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "generator": {
            "blind_seed_count": len(STOCHASTIC_BLIND_SEEDS),
            "blind_seeds": list(STOCHASTIC_BLIND_SEEDS),
            "horizons": list(STOCHASTIC_HORIZONS),
            "surface": (
                "Exact-rational stochastic controlled systems generated from "
                "structural knobs; no expected class labels are declared."
            ),
        },
        "case_counts": {
            "null_systems": len(stochastic_null_battery()),
            "blind_systems": len(blind_cases),
            "null_metric_cases": len(null_metrics),
            "blind_metric_cases": len(blind_metrics),
        },
        "null_classification_counts": _classification_counts(null_metrics),
        "blind_classification_counts": _classification_counts(blind_metrics),
        "axis_distribution": stochastic_axis_distribution(blind_metrics),
        "derived_clusters": clusters,
        "counterexample_search": [witness.as_dict() for witness in search],
        "coherence": coherence,
        "negative_result_retention": negative,
        "decision_gate": gates,
    }


def stochastic_coherence_summary(
    systems: tuple[StochasticControlledSystem, ...],
) -> dict[str, Any]:
    reports = [
        report
        for system in systems
        for report in coherence_reports(system)
    ]
    lumpable = [report for report in reports if report.strongly_lumpable]
    non_lumpable = [report for report in reports if not report.strongly_lumpable]
    return {
        "report_count": len(reports),
        "strongly_lumpable_count": len(lumpable),
        "non_lumpable_count": len(non_lumpable),
        "has_lumpable_and_non_lumpable": bool(lumpable and non_lumpable),
        "representative_lumpable": lumpable[0].as_dict() if lumpable else None,
        "representative_non_lumpable": non_lumpable[0].as_dict() if non_lumpable else None,
    }


def stochastic_counterexample_search(
    metrics: list[StochasticDiamondMetrics],
) -> list[SearchWitness]:
    return [
        _metric_pair_search(
            metrics,
            name="stochastic_recurrence_does_not_imply_feedback_advantage",
            left_pred=lambda m: m.recurrence_detected and m.feedback_advantage == 0,
            right_pred=lambda m: m.recurrence_detected and m.feedback_advantage > 0,
            details=lambda left, right: {
                "shared_recurrence": True,
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
            },
        ),
        _metric_pair_search(
            metrics,
            name="stochastic_control_does_not_imply_feedback_advantage",
            left_pred=lambda m: m.control_reach_count > 0 and m.feedback_advantage == 0,
            right_pred=lambda m: m.control_reach_count > 0 and m.feedback_advantage > 0,
            details=lambda left, right: {
                "left_control_reach_count": left.control_reach_count,
                "right_control_reach_count": right.control_reach_count,
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
            },
        ),
        _metric_pair_search(
            metrics,
            name="stochastic_feedback_does_not_imply_reflexive_maintenance",
            left_pred=lambda m: m.feedback_advantage > 0
            and not _positive_optional(m.reflexive_advantage),
            right_pred=lambda m: m.feedback_advantage > 0
            and _positive_optional(m.reflexive_advantage),
            details=lambda left, right: {
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "left_reflexive_advantage": _optional_frac(left.reflexive_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
                "right_reflexive_advantage": _optional_frac(right.reflexive_advantage),
            },
        ),
        _same_live_score_joint_search(metrics),
    ]


def stochastic_negative_retention(metrics: list[StochasticDiamondMetrics]) -> dict[str, Any]:
    retained = {
        "passive_or_driven_recurrence": _maybe_metric(
            _first_metric(metrics, lambda m: m.classification == "passive_or_driven_recurrence")
        ),
        "control_without_feedback": _maybe_metric(
            _first_metric(
                metrics,
                lambda m: m.control_reach_count > 0 and m.feedback_advantage == 0,
            )
        ),
        "feedback_without_reflexive": _maybe_metric(
            _first_metric(
                metrics,
                lambda m: m.feedback_advantage > 0
                and not _positive_optional(m.reflexive_advantage),
            )
        ),
        "negative_joint_effect": _maybe_metric(
            _first_metric(
                metrics,
                lambda m: m.joint_effect_delta is not None and m.joint_effect_delta < 0,
            )
        ),
    }
    return {
        "retained": retained,
        "retention_status": {name: value is not None for name, value in retained.items()},
    }


def stochastic_cluster_summary(metrics: list[StochasticDiamondMetrics]) -> dict[str, Any]:
    grouped: dict[str, list[StochasticDiamondMetrics]] = defaultdict(list)
    for metric in metrics:
        grouped[_metric_signature(metric)].append(metric)
    clusters = []
    for signature, cases in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        clusters.append(
            {
                "signature": signature,
                "count": len(cases),
                "representative": cases[0].case_id,
                "classifications": dict(
                    sorted(Counter(metric.classification for metric in cases).items())
                ),
            }
        )
    return {
        "cluster_count": len(clusters),
        "clusters": clusters,
    }


def stochastic_axis_distribution(
    metrics: list[StochasticDiamondMetrics],
) -> dict[str, dict[str, int]]:
    return {
        "control": _count_by(metrics, lambda m: "positive" if m.control_reach_count > 0 else "zero"),
        "observable_control": _count_by(
            metrics,
            lambda m: "positive" if m.observable_control_count > 0 else "zero",
        ),
        "feedback": _count_by(metrics, lambda m: _sign(m.feedback_advantage)),
        "reflexive": _count_by(metrics, lambda m: _optional_positive(m.reflexive_advantage)),
        "joint": _count_by(metrics, lambda m: _optional_sign(m.joint_effect_delta)),
        "stochasticity": _count_by(
            metrics,
            lambda m: "present" if m.stochasticity_detected else "absent",
        ),
    }


def _generated_case(*, seed: int) -> StochasticBlindCase:
    rng = random.Random(seed * 11400714819323198485)
    template_index = seed % 6
    if template_index == 0:
        system = _passive_recurrence(seed=seed, probability=_probability(rng, 1, 3))
    elif template_index == 1:
        system = _control_without_feedback(seed=seed, success=_probability(rng, 2, 5))
    elif template_index == 2:
        system = _feedback_advantage(seed=seed, success=_probability(rng, 3, 5))
    elif template_index == 3:
        system = _reflexive_maintenance(seed=seed, success=_probability(rng, 3, 5))
    elif template_index == 4:
        system = _joint_contraction(
            seed=seed,
            live_joint_risk=Fraction(1),
            success=Fraction(4, 5),
        )
    else:
        system = _joint_positive(seed=seed, success=Fraction(4, 5))
    knobs = {
        "seed": seed,
        "template_index": template_index,
        "probability_denominator": "bounded rational from seed",
        "has_expected_class_label": False,
    }
    return StochasticBlindCase(seed=seed, system=system, generator_knobs=knobs)


def _passive_persistence(*, seed: int | None = None) -> StochasticControlledSystem:
    sid = "passive_persistence" if seed is None else f"blind_passive_persistence_{seed}"
    states = ("home", "safe", "loss")
    actions = ("a0", "a1")
    scenarios = ("nominal", "noise")
    transition = _same_action_kernel(
        states,
        actions,
        {
            "home": _row(states, {"safe": Fraction(4, 5), "loss": Fraction(1, 5)}),
            "safe": _row(states, {"safe": Fraction(1)}),
            "loss": _row(states, {"loss": Fraction(1)}),
        },
    )
    return _system(
        sid=sid,
        family="stochastic_passive",
        description="Noisy passive persistence with no action-distinct future profile.",
        states=states,
        actions=actions,
        scenarios=scenarios,
        starts={"nominal": "home", "noise": "home"},
        transition={scenario: transition for scenario in scenarios},
        observe={state: "same" for state in states},
        observations=("same",),
        live_policy={"same": "a0"},
        target_states=frozenset({"safe"}),
        viable_states=frozenset({"home", "safe"}),
        channel_states=frozenset({"safe"}),
    )


def _passive_recurrence(
    *,
    seed: int | None = None,
    probability: Fraction = Fraction(1, 2),
) -> StochasticControlledSystem:
    sid = "passive_recurrence" if seed is None else f"blind_passive_recurrence_{seed}"
    states = ("home", "safe", "loss")
    actions = ("a0", "a1")
    scenarios = ("nominal", "noise")
    transition = _same_action_kernel(
        states,
        actions,
        {
            "home": _row(
                states,
                {
                    "home": probability,
                    "safe": Fraction(1) - probability,
                },
            ),
            "safe": _row(states, {"safe": Fraction(1)}),
            "loss": _row(states, {"loss": Fraction(1)}),
        },
    )
    return _system(
        sid=sid,
        family="stochastic_recurrence",
        description="Positive-probability recurrence without action-sensitive feedback.",
        states=states,
        actions=actions,
        scenarios=scenarios,
        starts={"nominal": "home", "noise": "home"},
        transition={scenario: transition for scenario in scenarios},
        observe={state: "same" for state in states},
        observations=("same",),
        live_policy={"same": "a0"},
        target_states=frozenset({"safe", "home"}),
        viable_states=frozenset({"home", "safe"}),
        channel_states=frozenset({"home", "safe"}),
    )


def _control_without_feedback(
    *,
    seed: int | None = None,
    success: Fraction = Fraction(4, 5),
) -> StochasticControlledSystem:
    sid = "control_without_feedback" if seed is None else f"blind_control_{seed}"
    system = _two_need_system(
        sid=sid,
        family="stochastic_control_no_feedback",
        visible=False,
        success=success,
    )
    return system


def _feedback_advantage(
    *,
    seed: int | None = None,
    success: Fraction = Fraction(4, 5),
) -> StochasticControlledSystem:
    sid = "feedback_advantage" if seed is None else f"blind_feedback_{seed}"
    return _two_need_system(
        sid=sid,
        family="stochastic_feedback",
        visible=True,
        success=success,
    )


def _reflexive_maintenance(
    *,
    seed: int | None = None,
    success: Fraction = Fraction(4, 5),
) -> StochasticControlledSystem:
    sid = "reflexive_maintenance" if seed is None else f"blind_reflexive_{seed}"
    states = ("need0", "need1", "goal", "bad", "ch0", "ch1", "channel")
    actions = ("a0", "a1")
    scenarios = ("nominal", "p0", "p1", "ch0", "ch1")
    transition = {
        scenario: _need_channel_kernel(states, actions, success=success)
        for scenario in scenarios
    }
    observe = {
        "need0": "o0",
        "need1": "o1",
        "goal": "og",
        "bad": "ob",
        "ch0": "o0",
        "ch1": "o1",
        "channel": "og",
    }
    return _system(
        sid=sid,
        family="stochastic_reflexive",
        description="Noisy feedback where channel repair also requires live observation.",
        states=states,
        actions=actions,
        scenarios=scenarios,
        starts={"nominal": "need0", "p0": "need0", "p1": "need1", "ch0": "ch0", "ch1": "ch1"},
        transition=transition,
        observe=observe,
        observations=("o0", "o1", "og", "ob"),
        live_policy={"o0": "a0", "o1": "a1", "og": "a0", "ob": "a0"},
        target_states=frozenset({"goal", "channel"}),
        viable_states=frozenset({"need0", "need1", "goal", "ch0", "ch1", "channel"}),
        channel_states=frozenset({"channel"}),
        channel_challenge_scenarios=("ch0", "ch1"),
        presentations=_standard_presentations(states),
    )


def _joint_contraction(
    *,
    seed: int | None = None,
    live_joint_risk: Fraction = Fraction(4, 5),
    success: Fraction = Fraction(4, 5),
) -> StochasticControlledSystem:
    sid = "joint_contraction" if seed is None else f"blind_joint_negative_{seed}"
    return _joint_system(
        sid=sid,
        family="stochastic_joint_negative",
        live_joint_risk=live_joint_risk,
        cooperative=False,
        success=success,
    )


def _joint_positive(
    *,
    seed: int | None = None,
    success: Fraction = Fraction(4, 5),
) -> StochasticControlledSystem:
    sid = "joint_positive" if seed is None else f"blind_joint_positive_{seed}"
    return _joint_system(
        sid=sid,
        family="stochastic_joint_positive",
        live_joint_risk=Fraction(0),
        cooperative=True,
        success=success,
        target_includes_safe=True,
    )


def _two_need_system(
    *,
    sid: str,
    family: str,
    visible: bool,
    success: Fraction,
) -> StochasticControlledSystem:
    states = ("need0", "need1", "goal", "bad")
    actions = ("a0", "a1")
    scenarios = ("nominal", "p0", "p1")
    transition = {
        scenario: _need_kernel(states, actions, success=success)
        for scenario in scenarios
    }
    observe = {
        "need0": "o0" if visible else "same",
        "need1": "o1" if visible else "same",
        "goal": "og" if visible else "same",
        "bad": "ob" if visible else "same",
    }
    observations = ("o0", "o1", "og", "ob") if visible else ("same",)
    live_policy = (
        {"o0": "a0", "o1": "a1", "og": "a0", "ob": "a0"}
        if visible
        else {"same": "a0"}
    )
    return _system(
        sid=sid,
        family=family,
        description="Two hidden needs; live feedback helps only when observations split them.",
        states=states,
        actions=actions,
        scenarios=scenarios,
        starts={"nominal": "need0", "p0": "need0", "p1": "need1"},
        transition=transition,
        observe=observe,
        observations=observations,
        live_policy=live_policy,
        target_states=frozenset({"goal"}),
        viable_states=frozenset({"need0", "need1", "goal"}),
        channel_states=frozenset({"goal"}),
        presentations=_standard_presentations(states),
    )


def _joint_system(
    *,
    sid: str,
    family: str,
    live_joint_risk: Fraction,
    cooperative: bool,
    success: Fraction = Fraction(1),
    target_includes_safe: bool = False,
) -> StochasticControlledSystem:
    states = ("need0", "need1", "joint", "goal", "bad", "capture", "safe")
    actions = ("a0", "a1")
    scenarios = ("nominal", "p0", "p1", "joint")
    kernel = _need_kernel(states, actions, success=success)
    kernel["need1"]["a0"] = _row(states, {"safe": Fraction(1)})
    for action in actions:
        kernel["goal"][action] = _row(states, {"goal": Fraction(1)})
        kernel["bad"][action] = _row(states, {"bad": Fraction(1)})
        kernel["capture"][action] = _row(states, {"capture": Fraction(1)})
        kernel["safe"][action] = _row(states, {"safe": Fraction(1)})
    if cooperative:
        kernel["joint"]["a0"] = _row(states, {"safe": Fraction(1)})
        kernel["joint"]["a1"] = _row(states, {"capture": Fraction(1)})
        live_policy = {"o0": "a0", "o1": "a1", "oj": "a0", "og": "a0", "ob": "a0"}
    else:
        kernel["joint"]["a0"] = _row(states, {"safe": Fraction(1)})
        kernel["joint"]["a1"] = _row(
            states,
            {
                "capture": live_joint_risk,
                "safe": Fraction(1) - live_joint_risk,
            },
        )
        live_policy = {"o0": "a0", "o1": "a1", "oj": "a1", "og": "a0", "ob": "a0"}
    target_states = {"goal", "capture"}
    if target_includes_safe:
        target_states.add("safe")
    return _system(
        sid=sid,
        family=family,
        description="Own maintenance can coincide with positive or negative joint effect.",
        states=states,
        actions=actions,
        scenarios=scenarios,
        starts={"nominal": "need0", "p0": "need0", "p1": "need1", "joint": "joint"},
        transition={scenario: kernel for scenario in scenarios},
        observe={
            "need0": "o0",
            "need1": "o1",
            "joint": "oj",
            "goal": "og",
            "bad": "ob",
            "capture": "og",
            "safe": "og",
        },
        observations=("o0", "o1", "oj", "og", "ob"),
        live_policy=live_policy,
        target_states=frozenset(target_states),
        viable_states=frozenset({"need0", "need1", "joint", "goal", "capture", "safe"}),
        channel_states=frozenset({"goal", "capture", "safe"}),
        joint_safe_states=(
            frozenset(states)
            if cooperative
            else frozenset({"need0", "need1", "joint", "goal", "safe"})
        ),
        presentations=_standard_presentations(states),
    )


def _need_kernel(
    states: tuple[State, ...],
    actions: tuple[Action, ...],
    *,
    success: Fraction,
) -> dict[State, dict[Action, dict[State, Fraction]]]:
    failure = Fraction(1) - success
    kernel = {
        state: {action: _row(states, {state: Fraction(1)}) for action in actions}
        for state in states
    }
    if "need0" in states:
        kernel["need0"] = {
            "a0": _row(states, {"goal": success, "bad": failure}),
            "a1": _row(states, {"bad": Fraction(1)}),
        }
    if "need1" in states:
        kernel["need1"] = {
            "a0": _row(states, {"bad": Fraction(1)}),
            "a1": _row(states, {"goal": success, "bad": failure}),
        }
    if "goal" in states:
        kernel["goal"] = {action: _row(states, {"goal": Fraction(1)}) for action in actions}
    if "bad" in states:
        kernel["bad"] = {action: _row(states, {"bad": Fraction(1)}) for action in actions}
    return kernel


def _need_channel_kernel(
    states: tuple[State, ...],
    actions: tuple[Action, ...],
    *,
    success: Fraction,
) -> dict[State, dict[Action, dict[State, Fraction]]]:
    kernel = _need_kernel(states, actions, success=success)
    failure = Fraction(1) - success
    kernel["ch0"] = {
        "a0": _row(states, {"channel": success, "bad": failure}),
        "a1": _row(states, {"bad": Fraction(1)}),
    }
    kernel["ch1"] = {
        "a0": _row(states, {"bad": Fraction(1)}),
        "a1": _row(states, {"channel": success, "bad": failure}),
    }
    kernel["channel"] = {action: _row(states, {"channel": Fraction(1)}) for action in actions}
    return kernel


def _same_action_kernel(
    states: tuple[State, ...],
    actions: tuple[Action, ...],
    rows: dict[State, dict[State, Fraction]],
) -> dict[State, dict[Action, dict[State, Fraction]]]:
    return {
        state: {action: dict(rows[state]) for action in actions}
        for state in states
    }


def _system(
    *,
    sid: str,
    family: str,
    description: str,
    states: tuple[State, ...],
    actions: tuple[Action, ...],
    scenarios: tuple[str, ...],
    starts: dict[str, State],
    transition: dict[str, dict[State, dict[Action, dict[State, Fraction]]]],
    observe: dict[State, str],
    observations: tuple[str, ...],
    live_policy: dict[str, Action],
    target_states: frozenset[State],
    viable_states: frozenset[State],
    channel_states: frozenset[State],
    channel_challenge_scenarios: tuple[str, ...] = (),
    joint_safe_states: frozenset[State] | None = None,
    presentations: dict[str, dict[State, str]] | None = None,
) -> StochasticControlledSystem:
    return StochasticControlledSystem(
        system_id=sid,
        family=family,
        description=description,
        states=states,
        actions=actions,
        observations=observations,
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts=starts,
        transition=transition,
        observe=observe,
        live_policy=live_policy,
        target_states=target_states,
        viable_states=viable_states,
        channel_states=channel_states,
        channel_challenge_scenarios=channel_challenge_scenarios,
        joint_safe_states=joint_safe_states,
        presentations=presentations or _standard_presentations(states),
    )


def _standard_presentations(states: tuple[State, ...]) -> dict[str, dict[State, str]]:
    return {
        "identity": {state: state for state in states},
        "coarse_need_merge": {
            state: (
                "need"
                if state in {"need0", "need1", "ch0", "ch1"}
                else "success"
                if state in {"goal", "channel", "capture", "safe"}
                else "failure"
                if state == "bad"
                else state
            )
            for state in states
        },
    }


def _row(states: tuple[State, ...], entries: dict[State, Fraction]) -> dict[State, Fraction]:
    row = {state: entries.get(state, Fraction(0)) for state in states}
    total = sum(row.values(), start=Fraction(0))
    if total != 1:
        raise ValueError(f"row sums to {total}, not 1: {entries}")
    return row


def _probability(rng: random.Random, low: int, high: int) -> Fraction:
    denominator = rng.choice((5, 8, 10))
    numerator = rng.randint(low, max(low, denominator - high))
    return Fraction(numerator, denominator)


def _classification_counts(metrics: list[StochasticDiamondMetrics]) -> dict[str, int]:
    return dict(sorted(Counter(metric.classification for metric in metrics).items()))


def _metric_pair_search(
    metrics: list[StochasticDiamondMetrics],
    *,
    name: str,
    left_pred,
    right_pred,
    details,
) -> SearchWitness:
    left = _first_metric(metrics, left_pred)
    right = _first_metric(metrics, right_pred)
    return SearchWitness(
        name=name,
        passed=left is not None and right is not None,
        left_case=None if left is None else left.case_id,
        right_case=None if right is None else right.case_id,
        details={} if left is None or right is None else details(left, right),
    )


def _first_metric(metrics: list[StochasticDiamondMetrics], predicate) -> StochasticDiamondMetrics | None:
    return next((metric for metric in metrics if predicate(metric)), None)


def _same_live_score_joint_search(metrics: list[StochasticDiamondMetrics]) -> SearchWitness:
    for left in metrics:
        if left.joint_effect_delta is None:
            continue
        for right in metrics:
            if right.case_id == left.case_id or right.joint_effect_delta is None:
                continue
            if (
                right.live_maintenance_probability == left.live_maintenance_probability
                and right.joint_effect_delta != left.joint_effect_delta
            ):
                return SearchWitness(
                    name="stochastic_live_success_scalar_does_not_determine_joint_effect",
                    passed=True,
                    left_case=left.case_id,
                    right_case=right.case_id,
                    details={
                        "shared_live_maintenance": _frac(left.live_maintenance_probability),
                        "left_joint_effect": _optional_frac(left.joint_effect_delta),
                        "right_joint_effect": _optional_frac(right.joint_effect_delta),
                    },
                )
    return SearchWitness(
        name="stochastic_live_success_scalar_does_not_determine_joint_effect",
        passed=False,
        left_case=None,
        right_case=None,
        details={},
    )


def _maybe_metric(metric: StochasticDiamondMetrics | None) -> dict[str, Any] | None:
    return None if metric is None else metric.as_dict()


def _metric_signature(metric: StochasticDiamondMetrics) -> str:
    return "|".join(
        (
            f"control:{'+' if metric.control_reach_count > 0 else '0'}",
            f"observable:{'+' if metric.observable_control_count > 0 else '0'}",
            f"feedback:{_sign(metric.feedback_advantage)}",
            f"reflexive:{_optional_positive(metric.reflexive_advantage)}",
            f"joint:{_optional_sign(metric.joint_effect_delta)}",
            f"recurrence:{metric.recurrence_detected}",
        )
    )


def _count_by(metrics: list[StochasticDiamondMetrics], key_fn) -> dict[str, int]:
    return dict(sorted(Counter(key_fn(metric) for metric in metrics).items()))


def _sign(value: Fraction) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "zero"


def _optional_sign(value: Fraction | None) -> str:
    return "none" if value is None else _sign(value)


def _positive_optional(value: Fraction | None) -> bool:
    return value is not None and value > 0


def _optional_positive(value: Fraction | None) -> str:
    if value is None:
        return "none"
    return "positive" if value > 0 else "nonpositive"


def _frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _optional_frac(value: Fraction | None) -> str | None:
    return None if value is None else _frac(value)
