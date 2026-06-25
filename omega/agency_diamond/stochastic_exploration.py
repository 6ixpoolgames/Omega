"""Exploratory stochastic deformer discovery beyond pinned fixtures.

This module extends the stochastic agency-diamond pilot in three bounded ways:

* held-out seeded search with no expected class labels on the run surface;
* cross-substrate stochastic profile checks over several source grammars;
* exact-rational calibration sweeps over reliability and joint-risk knobs.

The claim is deliberately narrow: these are synthetic finite diagnostics for
continuation deformation.  They do not detect agency, identity, value,
valuerhood, or Omega, and they do not validate empirical transition models.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from omega.agency_diamond.challenge import SearchWitness
from omega.agency_diamond.stochastic_examples import (
    STOCHASTIC_HORIZONS,
    _control_without_feedback,
    _feedback_advantage,
    _joint_contraction,
    _joint_positive,
    _passive_recurrence,
    _reflexive_maintenance,
    stochastic_counterexample_search,
)
from omega.agency_diamond.stochastic_metrics import (
    StochasticDiamondMetrics,
    evaluate_stochastic_system,
)
from omega.agency_diamond.stochastic_model import StochasticControlledSystem


HELDOUT_STOCHASTIC_SEEDS = tuple(range(3301, 3361))
CROSS_STOCHASTIC_SEEDS = (7101, 7103, 7109)
CALIBRATION_VALUES = (
    Fraction(0),
    Fraction(1, 5),
    Fraction(1, 2),
    Fraction(4, 5),
    Fraction(9, 10),
)
JOINT_RISK_VALUES = (
    Fraction(0),
    Fraction(1, 5),
    Fraction(2, 5),
    Fraction(4, 5),
    Fraction(1),
)
REQUIRED_EXPLORATION_CLASSES = {
    "passive_or_driven_recurrence",
    "control_without_feedback_advantage",
    "feedback_advantage",
    "reflexive_maintenance",
    "dominant_joint_contraction",
}
CROSS_SUBSTRATE_REQUIRED_CLASSES = REQUIRED_EXPLORATION_CLASSES - {
    "passive_or_driven_recurrence"
}


@dataclass(frozen=True)
class StochasticExplorationCase:
    split: str
    seed: int
    substrate: str
    system: StochasticControlledSystem
    generator_knobs: dict[str, object]


def stochastic_exploration_summary() -> dict[str, Any]:
    heldout = heldout_search_summary()
    cross = cross_substrate_stochastic_summary()
    calibration = calibration_phase_summary()
    gates = {
        "heldout_search_passed": heldout["status"] == "PASS",
        "cross_substrate_passed": cross["status"] == "PASS",
        "calibration_phase_passed": calibration["status"] == "PASS",
    }
    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "claim_boundary": (
            "Exploratory finite stochastic deformer discovery only. These "
            "checks test held-out non-predeclared search, cross-substrate "
            "profile transport, and exact-rational phase/calibration behavior. "
            "They do not detect agency, identity, value, valuerhood, or Omega, "
            "and do not validate empirical transition models."
        ),
        "heldout_search": heldout,
        "cross_substrate": cross,
        "calibration_phase": calibration,
        "decision_gate": gates,
    }


def heldout_stochastic_cases() -> tuple[StochasticExplorationCase, ...]:
    return tuple(_heldout_case(seed=seed) for seed in HELDOUT_STOCHASTIC_SEEDS)


def heldout_stochastic_metrics() -> list[StochasticDiamondMetrics]:
    return [
        evaluate_stochastic_system(
            case.system,
            horizon=horizon,
            case_id=f"{case.split}__seed{case.seed}_h{horizon}",
        )
        for case in heldout_stochastic_cases()
        for horizon in STOCHASTIC_HORIZONS
    ]


def heldout_search_summary() -> dict[str, Any]:
    cases = heldout_stochastic_cases()
    metrics = heldout_stochastic_metrics()
    counterexamples = stochastic_counterexample_search(metrics)
    classes = set(metric.classification for metric in metrics)
    clusters = _cluster_summary(metrics)
    gates = {
        "no_expected_class_labels": all(
            "expected_class" not in case.generator_knobs for case in cases
        ),
        "required_classes_discovered": REQUIRED_EXPLORATION_CLASSES <= classes,
        "multiple_metric_clusters": clusters["cluster_count"] >= 5,
        "counterexample_witnesses_found": all(
            witness.passed for witness in counterexamples
        ),
        "null_controls_retained": all(_heldout_null_controls(metrics).values()),
    }
    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "generator": {
            "seed_count": len(HELDOUT_STOCHASTIC_SEEDS),
            "seeds": list(HELDOUT_STOCHASTIC_SEEDS),
            "horizons": list(STOCHASTIC_HORIZONS),
            "surface": (
                "Held-out seeded stochastic systems. Generator knobs are retained, "
                "but expected outcome labels are not declared."
            ),
        },
        "case_counts": {
            "systems": len(cases),
            "metric_cases": len(metrics),
        },
        "classification_counts": _classification_counts(metrics),
        "axis_distribution": _axis_distribution(metrics),
        "derived_clusters": clusters,
        "counterexample_search": [witness.as_dict() for witness in counterexamples],
        "null_controls": _heldout_null_controls(metrics),
        "decision_gate": gates,
    }


def cross_substrate_stochastic_cases() -> tuple[StochasticExplorationCase, ...]:
    cases: list[StochasticExplorationCase] = []
    for seed in CROSS_STOCHASTIC_SEEDS:
        cases.extend(
            (
                _cross_case(
                    seed=seed,
                    substrate="boolean",
                    system=_feedback_advantage(
                        seed=seed,
                        success=_success_for(seed, offset=0),
                    ),
                    knobs={"source_grammar": "boolean_need_route"},
                ),
                _cross_case(
                    seed=seed,
                    substrate="boolean",
                    system=_reflexive_maintenance(
                        seed=seed,
                        success=_success_for(seed, offset=1),
                    ),
                    knobs={"source_grammar": "boolean_channel_repair"},
                ),
                _cross_case(
                    seed=seed,
                    substrate="grid",
                    system=_grid_feedback_system(seed=seed, visible=False),
                    knobs={"source_grammar": "grid_route", "observation_split": False},
                ),
                _cross_case(
                    seed=seed,
                    substrate="grid",
                    system=_grid_feedback_system(seed=seed, visible=True),
                    knobs={"source_grammar": "grid_route", "observation_split": True},
                ),
                _cross_case(
                    seed=seed,
                    substrate="resource",
                    system=_joint_positive(seed=seed, success=_success_for(seed, offset=2)),
                    knobs={"source_grammar": "resource_corridor"},
                ),
                _cross_case(
                    seed=seed,
                    substrate="resource",
                    system=_joint_contraction(
                        seed=seed,
                        live_joint_risk=Fraction(4, 5),
                        success=_success_for(seed, offset=3),
                    ),
                    knobs={"source_grammar": "resource_corridor"},
                ),
            )
        )
    return tuple(cases)


def cross_substrate_stochastic_metrics() -> list[StochasticDiamondMetrics]:
    return [
        evaluate_stochastic_system(
            case.system,
            horizon=horizon,
            case_id=f"{case.split}__{case.substrate}__seed{case.seed}_h{horizon}",
        )
        for case in cross_substrate_stochastic_cases()
        for horizon in STOCHASTIC_HORIZONS
    ]


def cross_substrate_stochastic_summary() -> dict[str, Any]:
    cases = cross_substrate_stochastic_cases()
    metrics = cross_substrate_stochastic_metrics()
    by_substrate = _classification_by_substrate(metrics)
    witnesses = _cross_substrate_witnesses(metrics)
    gates = {
        "multiple_substrates_tested": len(by_substrate) >= 3,
        "each_substrate_has_multiple_profiles": all(
            len(counts) >= 2 for counts in by_substrate.values()
        ),
        "required_classes_discovered": CROSS_SUBSTRATE_REQUIRED_CLASSES
        <= set(metric.classification for metric in metrics),
        "cross_substrate_witnesses_found": all(witness.passed for witness in witnesses),
    }
    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "generator": {
            "seeds": list(CROSS_STOCHASTIC_SEEDS),
            "horizons": list(STOCHASTIC_HORIZONS),
            "substrates": sorted({case.substrate for case in cases}),
        },
        "case_counts": {
            "systems": len(cases),
            "metric_cases": len(metrics),
        },
        "classification_counts": _classification_counts(metrics),
        "classification_by_substrate": by_substrate,
        "witnesses": [witness.as_dict() for witness in witnesses],
        "decision_gate": gates,
    }


def calibration_phase_summary() -> dict[str, Any]:
    feedback_curve = [
        _curve_point(
            knob="feedback_reliability",
            value=value,
            metric=evaluate_stochastic_system(
                _feedback_advantage(seed=9000 + index, success=value),
                horizon=1,
                case_id=f"calibration__feedback_{index}",
            ),
        )
        for index, value in enumerate(CALIBRATION_VALUES)
    ]
    reflexive_curve = [
        _curve_point(
            knob="repair_reliability",
            value=value,
            metric=evaluate_stochastic_system(
                _reflexive_maintenance(seed=9100 + index, success=value),
                horizon=1,
                case_id=f"calibration__reflexive_{index}",
            ),
        )
        for index, value in enumerate(CALIBRATION_VALUES)
    ]
    joint_curve = [
        _curve_point(
            knob="joint_risk",
            value=value,
            metric=evaluate_stochastic_system(
                _joint_contraction(
                    seed=9200 + index,
                    live_joint_risk=value,
                    success=Fraction(4, 5),
                ),
                horizon=1,
                case_id=f"calibration__joint_risk_{index}",
            ),
        )
        for index, value in enumerate(JOINT_RISK_VALUES)
    ]
    gates = {
        "feedback_has_zero_and_positive_regions": _has_zero_and_positive(
            feedback_curve,
            "feedback_advantage",
        ),
        "repair_has_zero_and_positive_regions": _has_zero_and_positive(
            reflexive_curve,
            "reflexive_advantage",
        ),
        "joint_high_risk_is_negative": _parse_fraction(
            joint_curve[-1]["joint_effect_delta"]
        )
        < 0,
        "joint_risk_changes_joint_effect": len(
            {point["joint_effect_delta"] for point in joint_curve}
        )
        > 1,
        "feedback_monotone_with_reliability": _nondecreasing(
            _parse_fraction(point["feedback_advantage"]) for point in feedback_curve
        ),
        "repair_monotone_with_reliability": _nondecreasing(
            _parse_fraction(point["reflexive_advantage"]) for point in reflexive_curve
        ),
        "joint_effect_nonincreasing_with_risk": _nonincreasing(
            _parse_fraction(point["joint_effect_delta"]) for point in joint_curve
        ),
    }
    return {
        "status": "PASS" if all(gates.values()) else "FAIL",
        "curves": {
            "feedback_reliability": feedback_curve,
            "repair_reliability": reflexive_curve,
            "joint_risk": joint_curve,
        },
        "thresholds": {
            "first_positive_feedback_reliability": _first_value_above(
                feedback_curve,
                "feedback_advantage",
            ),
            "first_positive_repair_reliability": _first_value_above(
                reflexive_curve,
                "reflexive_advantage",
            ),
            "first_negative_joint_risk": _first_value_below(
                joint_curve,
                "joint_effect_delta",
            ),
        },
        "decision_gate": gates,
    }


def _heldout_case(*, seed: int) -> StochasticExplorationCase:
    rng = random.Random(seed * 6364136223846793005)
    template = seed % 6
    success = _success_for(seed, offset=template)
    if template == 0:
        system = _passive_recurrence(seed=seed, probability=_probability(rng))
    elif template == 1:
        system = _control_without_feedback(seed=seed, success=success)
    elif template == 2:
        system = _feedback_advantage(seed=seed, success=success)
    elif template == 3:
        system = _reflexive_maintenance(seed=seed, success=success)
    elif template == 4:
        system = _joint_contraction(
            seed=seed,
            live_joint_risk=Fraction(4, 5),
            success=success,
        )
    else:
        system = _joint_positive(seed=seed, success=success)
    return StochasticExplorationCase(
        split="heldout",
        seed=seed,
        substrate="mixed",
        system=system,
        generator_knobs={
            "seed": seed,
            "template_index": template,
            "success_probability": _frac(success),
            "has_expected_class_label": False,
        },
    )


def _cross_case(
    *,
    seed: int,
    substrate: str,
    system: StochasticControlledSystem,
    knobs: dict[str, object],
) -> StochasticExplorationCase:
    data = {"seed": seed, "has_expected_class_label": False, **knobs}
    return StochasticExplorationCase(
        split="cross",
        seed=seed,
        substrate=substrate,
        system=system,
        generator_knobs=data,
    )


def _grid_feedback_system(*, seed: int, visible: bool) -> StochasticControlledSystem:
    states = ("home", "left_need", "right_need", "goal", "bad")
    actions = ("west", "east")
    scenarios = ("nominal", "left", "right")
    success = _success_for(seed, offset=5)
    failure = Fraction(1) - success
    row = _row
    transition = {
        state: {action: row(states, {state: Fraction(1)}) for action in actions}
        for state in states
    }
    transition["home"] = {
        "west": row(states, {"goal": success, "bad": failure}),
        "east": row(states, {"goal": success, "bad": failure}),
    }
    transition["left_need"] = {
        "west": row(states, {"goal": success, "bad": failure}),
        "east": row(states, {"bad": Fraction(1)}),
    }
    transition["right_need"] = {
        "west": row(states, {"bad": Fraction(1)}),
        "east": row(states, {"goal": success, "bad": failure}),
    }
    transition["goal"] = {
        action: row(states, {"goal": Fraction(1)}) for action in actions
    }
    transition["bad"] = {
        action: row(states, {"bad": Fraction(1)}) for action in actions
    }
    if visible:
        observations = ("ohome", "oleft", "oright", "ogoal", "obad")
        observe = {
            "home": "ohome",
            "left_need": "oleft",
            "right_need": "oright",
            "goal": "ogoal",
            "bad": "obad",
        }
        live_policy = {
            "ohome": "west",
            "oleft": "west",
            "oright": "east",
            "ogoal": "west",
            "obad": "west",
        }
    else:
        observations = ("ogrid",)
        observe = {state: "ogrid" for state in states}
        live_policy = {"ogrid": "west"}
    return StochasticControlledSystem(
        system_id=f"stochastic_cross_grid_{'visible' if visible else 'blind'}_{seed}",
        family="stochastic_cross_grid",
        description="Grid-route stochastic source grammar for deformer profile checks.",
        states=states,
        actions=actions,
        observations=observations,
        scenarios=scenarios,
        nominal_scenario="nominal",
        scenario_starts={
            "nominal": "home",
            "left": "left_need",
            "right": "right_need",
        },
        transition={scenario: transition for scenario in scenarios},
        observe=observe,
        live_policy=live_policy,
        target_states=frozenset({"goal"}),
        viable_states=frozenset({"home", "left_need", "right_need", "goal"}),
        channel_states=frozenset({"goal"}),
        presentations={
            "identity": {state: state for state in states},
            "need_merge": {
                state: "need" if state in {"left_need", "right_need"} else state
                for state in states
            },
        },
    )


def _cross_substrate_witnesses(
    metrics: list[StochasticDiamondMetrics],
) -> list[SearchWitness]:
    return [
        _pair_search(
            metrics,
            name="stochastic_cross_same_substrate_separates_feedback",
            left_pred=lambda m: m.feedback_advantage == 0,
            right_pred=lambda m: m.feedback_advantage > 0,
            same_substrate=True,
            details=lambda left, right: {
                "substrate": _substrate_of(left),
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
            },
        ),
        _pair_search(
            metrics,
            name="stochastic_cross_feedback_without_reflexive_and_with_reflexive",
            left_pred=lambda m: m.feedback_advantage > 0
            and not _positive_optional(m.reflexive_advantage),
            right_pred=lambda m: m.feedback_advantage > 0
            and _positive_optional(m.reflexive_advantage),
            same_substrate=False,
            details=lambda left, right: {
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "left_reflexive_advantage": _optional_frac(left.reflexive_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
                "right_reflexive_advantage": _optional_frac(right.reflexive_advantage),
            },
        ),
        _pair_search(
            metrics,
            name="stochastic_cross_joint_sign_not_live_success",
            left_pred=lambda m: m.live_maintenance_probability > 0
            and m.joint_effect_delta is not None
            and m.joint_effect_delta >= 0,
            right_pred=lambda m: m.live_maintenance_probability > 0
            and m.joint_effect_delta is not None
            and m.joint_effect_delta < 0,
            same_substrate=True,
            details=lambda left, right: {
                "substrate": _substrate_of(left),
                "left_live": _frac(left.live_maintenance_probability),
                "right_live": _frac(right.live_maintenance_probability),
                "left_joint": _optional_frac(left.joint_effect_delta),
                "right_joint": _optional_frac(right.joint_effect_delta),
            },
        ),
    ]


def _heldout_null_controls(metrics: list[StochasticDiamondMetrics]) -> dict[str, bool]:
    return {
        "control_without_feedback_retained": any(
            metric.control_reach_count > 0 and metric.feedback_advantage == 0
            for metric in metrics
        ),
        "feedback_without_reflexive_retained": any(
            metric.feedback_advantage > 0
            and not _positive_optional(metric.reflexive_advantage)
            for metric in metrics
        ),
        "negative_joint_retained": any(
            metric.joint_effect_delta is not None and metric.joint_effect_delta < 0
            for metric in metrics
        ),
    }


def _cluster_summary(metrics: list[StochasticDiamondMetrics]) -> dict[str, Any]:
    grouped: dict[str, list[StochasticDiamondMetrics]] = defaultdict(list)
    for metric in metrics:
        grouped[_metric_signature(metric)].append(metric)
    clusters = [
        {
            "signature": signature,
            "count": len(cases),
            "representative": cases[0].case_id,
            "classifications": dict(
                sorted(Counter(metric.classification for metric in cases).items())
            ),
        }
        for signature, cases in sorted(
            grouped.items(),
            key=lambda item: (-len(item[1]), item[0]),
        )
    ]
    return {"cluster_count": len(clusters), "clusters": clusters}


def _classification_counts(metrics: list[StochasticDiamondMetrics]) -> dict[str, int]:
    return dict(sorted(Counter(metric.classification for metric in metrics).items()))


def _classification_by_substrate(
    metrics: list[StochasticDiamondMetrics],
) -> dict[str, dict[str, int]]:
    by_substrate: dict[str, Counter[str]] = defaultdict(Counter)
    for metric in metrics:
        by_substrate[_substrate_of(metric)][metric.classification] += 1
    return {
        substrate: dict(sorted(counts.items()))
        for substrate, counts in sorted(by_substrate.items())
    }


def _axis_distribution(
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
    }


def _pair_search(
    metrics: list[StochasticDiamondMetrics],
    *,
    name: str,
    left_pred,
    right_pred,
    same_substrate: bool,
    details,
) -> SearchWitness:
    for left in metrics:
        if not left_pred(left):
            continue
        for right in metrics:
            if left.case_id == right.case_id or not right_pred(right):
                continue
            if same_substrate and _substrate_of(left) != _substrate_of(right):
                continue
            return SearchWitness(
                name=name,
                passed=True,
                left_case=left.case_id,
                right_case=right.case_id,
                details=details(left, right),
            )
    return SearchWitness(name=name, passed=False, left_case=None, right_case=None, details={})


def _curve_point(
    *,
    knob: str,
    value: Fraction,
    metric: StochasticDiamondMetrics,
) -> dict[str, Any]:
    return {
        "knob": knob,
        "value": _frac(value),
        "case_id": metric.case_id,
        "classification": metric.classification,
        "live_maintenance_probability": _frac(metric.live_maintenance_probability),
        "replay_maintenance_probability": _frac(metric.replay_maintenance_probability),
        "feedback_advantage": _frac(metric.feedback_advantage),
        "reflexive_advantage": _optional_frac(metric.reflexive_advantage),
        "joint_effect_delta": _optional_frac(metric.joint_effect_delta),
    }


def _has_zero_and_positive(curve: list[dict[str, Any]], key: str) -> bool:
    values = [_parse_fraction(point[key]) for point in curve if point[key] is not None]
    return any(value == 0 for value in values) and any(value > 0 for value in values)


def _has_zero_and_negative(curve: list[dict[str, Any]], key: str) -> bool:
    values = [_parse_fraction(point[key]) for point in curve if point[key] is not None]
    return any(value == 0 for value in values) and any(value < 0 for value in values)


def _first_value_above(curve: list[dict[str, Any]], key: str) -> str | None:
    for point in curve:
        if point[key] is not None and _parse_fraction(point[key]) > 0:
            return point["value"]
    return None


def _first_value_below(curve: list[dict[str, Any]], key: str) -> str | None:
    for point in curve:
        if point[key] is not None and _parse_fraction(point[key]) < 0:
            return point["value"]
    return None


def _nondecreasing(values) -> bool:
    sequence = list(values)
    return all(left <= right for left, right in zip(sequence, sequence[1:]))


def _nonincreasing(values) -> bool:
    sequence = list(values)
    return all(left >= right for left, right in zip(sequence, sequence[1:]))


def _parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def _success_for(seed: int, *, offset: int) -> Fraction:
    values = (Fraction(3, 5), Fraction(4, 5), Fraction(9, 10))
    return values[(seed + offset) % len(values)]


def _probability(rng: random.Random) -> Fraction:
    return rng.choice((Fraction(1, 5), Fraction(1, 2), Fraction(4, 5)))


def _row(states: tuple[str, ...], entries: dict[str, Fraction]) -> dict[str, Fraction]:
    row = {state: entries.get(state, Fraction(0)) for state in states}
    total = sum(row.values(), start=Fraction(0))
    if total != 1:
        raise ValueError(f"row sums to {total}, not 1: {entries}")
    return row


def _count_by(metrics: list[StochasticDiamondMetrics], key) -> dict[str, int]:
    return dict(sorted(Counter(key(metric) for metric in metrics).items()))


def _metric_signature(metric: StochasticDiamondMetrics) -> str:
    return "|".join(
        (
            f"control:{metric.control_reach_count > 0}",
            f"observable:{metric.observable_control_count > 0}",
            f"feedback:{_sign(metric.feedback_advantage)}",
            f"reflexive:{_optional_positive(metric.reflexive_advantage)}",
            f"joint:{_optional_sign(metric.joint_effect_delta)}",
            f"recurrence:{metric.recurrence_detected}",
        )
    )


def _substrate_of(metric: StochasticDiamondMetrics) -> str:
    parts = metric.case_id.split("__")
    return parts[1] if len(parts) > 2 else "unknown"


def _positive_optional(value: Fraction | None) -> bool:
    return value is not None and value > 0


def _sign(value: Fraction) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "zero"


def _optional_sign(value: Fraction | None) -> str:
    return "none" if value is None else _sign(value)


def _optional_positive(value: Fraction | None) -> str:
    if value is None:
        return "none"
    return "positive" if value > 0 else "nonpositive"


def _frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _optional_frac(value: Fraction | None) -> str | None:
    return None if value is None else _frac(value)
