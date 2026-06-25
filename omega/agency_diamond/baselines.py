"""Baseline-comparison and strictness probes for agency-diamond metrics."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from omega.agency_diamond.metrics import DiamondMetrics


@dataclass(frozen=True)
class CollisionWitness:
    baseline: str
    target_axis: str
    baseline_value: str
    left_case: str
    left_value: str
    right_case: str
    right_value: str

    def as_dict(self) -> dict[str, str]:
        return {
            "baseline": self.baseline,
            "target_axis": self.target_axis,
            "baseline_value": self.baseline_value,
            "left_case": self.left_case,
            "left_value": self.left_value,
            "right_case": self.right_case,
            "right_value": self.right_value,
        }


@dataclass(frozen=True)
class StrictnessWitness:
    name: str
    claim: str
    left_case: str
    right_case: str
    passed: bool
    details: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "claim": self.claim,
            "left_case": self.left_case,
            "right_case": self.right_case,
            "passed": self.passed,
            "details": self.details,
        }


BASELINE_DESCRIPTIONS = {
    "recurrence_only": "Only whether the nominal live trace repeats a state.",
    "control_only": "Only whether some reachable state has target-affecting actions.",
    "observable_control_only": "Only whether target-affecting action distinctions are observable.",
    "live_success_only": "Only live maintenance success under perturbations.",
    "feedback_only": "Only whether live feedback beats matched nominal replay.",
    "joint_effect_only": "Only the sign of joint-continuation effect when declared.",
}


TARGET_AXIS_DESCRIPTIONS = {
    "feedback_axis": "Sign of feedback advantage.",
    "reflexive_axis": "Presence of positive reflexive-maintenance advantage.",
    "joint_axis": "Sign of declared joint-continuation effect.",
    "full_classification": "Agency-diamond classification used by the pilot.",
}


REQUIRED_BASELINE_COLLISIONS = {
    ("recurrence_only", "feedback_axis"),
    ("control_only", "feedback_axis"),
    ("feedback_only", "reflexive_axis"),
    ("live_success_only", "joint_axis"),
    ("joint_effect_only", "full_classification"),
}


def baseline_values(metric: DiamondMetrics) -> dict[str, str]:
    return {
        "recurrence_only": str(metric.recurrence_detected),
        "control_only": str(metric.control_reach_count > 0),
        "observable_control_only": str(metric.observable_control_count > 0),
        "live_success_only": _frac(metric.live_maintenance_score),
        "feedback_only": _sign(metric.feedback_advantage),
        "joint_effect_only": _optional_sign(metric.joint_effect_delta),
    }


def target_axis_values(metric: DiamondMetrics) -> dict[str, str]:
    return {
        "feedback_axis": _sign(metric.feedback_advantage),
        "reflexive_axis": _optional_positive(metric.reflexive_advantage),
        "joint_axis": _optional_sign(metric.joint_effect_delta),
        "full_classification": metric.classification,
    }


def find_baseline_collisions(metrics: list[DiamondMetrics]) -> list[CollisionWitness]:
    """Find same-baseline/different-target pairs.

    These are not statistical claims. They are finite witnesses that a simple
    baseline projection is insufficient for a target distinction already present
    in the agency-diamond profile.
    """

    witnesses: list[CollisionWitness] = []
    for baseline in BASELINE_DESCRIPTIONS:
        for axis in TARGET_AXIS_DESCRIPTIONS:
            witness = _first_collision(metrics, baseline, axis)
            if witness is not None:
                witnesses.append(witness)
    return witnesses


def required_collision_status(
    witnesses: list[CollisionWitness],
) -> dict[str, bool]:
    found = {(witness.baseline, witness.target_axis) for witness in witnesses}
    return {
        f"{baseline}_does_not_determine_{axis}": (baseline, axis) in found
        for baseline, axis in sorted(REQUIRED_BASELINE_COLLISIONS)
    }


def strictness_witnesses(metrics: list[DiamondMetrics]) -> list[StrictnessWitness]:
    by_case = {metric.case_id: metric for metric in metrics}

    return [
        _strictness(
            name="recurrence_does_not_imply_feedback_advantage",
            claim="The same recurrence flag can coexist with zero or positive feedback advantage.",
            left=by_case["passive_attractor_h2"],
            right=by_case["thermostat_h2"],
            predicate=lambda left, right: (
                left.recurrence_detected == right.recurrence_detected
                and left.feedback_advantage == 0
                and right.feedback_advantage > 0
            ),
            details=lambda left, right: {
                "shared_recurrence": left.recurrence_detected,
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
            },
        ),
        _strictness(
            name="control_does_not_imply_feedback_advantage",
            claim="Target-affecting action distinctions can exist without live feedback beating replay.",
            left=by_case["open_loop_controller_h2"],
            right=by_case["thermostat_h2"],
            predicate=lambda left, right: (
                left.control_reach_count > 0
                and right.control_reach_count > 0
                and left.feedback_advantage == 0
                and right.feedback_advantage > 0
            ),
            details=lambda left, right: {
                "left_control_reach_count": left.control_reach_count,
                "right_control_reach_count": right.control_reach_count,
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "right_feedback_advantage": _frac(right.feedback_advantage),
            },
        ),
        _strictness(
            name="feedback_advantage_does_not_imply_reflexive_maintenance",
            claim="Feedback can preserve a target without preserving its own observation-action channel.",
            left=by_case["thermostat_h2"],
            right=by_case["self_restoring_controller_h2"],
            predicate=lambda left, right: (
                left.feedback_advantage > 0
                and right.feedback_advantage > 0
                and left.reflexive_advantage is None
                and right.reflexive_advantage is not None
                and right.reflexive_advantage > 0
            ),
            details=lambda left, right: {
                "left_feedback_advantage": _frac(left.feedback_advantage),
                "left_reflexive_advantage": None,
                "right_feedback_advantage": _frac(right.feedback_advantage),
                "right_reflexive_advantage": _frac(right.reflexive_advantage or Fraction(0)),
            },
        ),
        _strictness(
            name="live_success_does_not_determine_joint_effect",
            claim="Own live maintenance can be perfect while joint-continuation effect differs.",
            left=by_case["cooperative_controller_h2"],
            right=by_case["dominant_horizon_controller_h2"],
            predicate=lambda left, right: (
                left.live_maintenance_score == right.live_maintenance_score
                and left.joint_effect_delta is not None
                and right.joint_effect_delta is not None
                and left.joint_effect_delta > 0
                and right.joint_effect_delta < 0
            ),
            details=lambda left, right: {
                "shared_live_maintenance": _frac(left.live_maintenance_score),
                "left_joint_effect": _frac(left.joint_effect_delta or Fraction(0)),
                "right_joint_effect": _frac(right.joint_effect_delta or Fraction(0)),
            },
        ),
        _strictness(
            name="joint_effect_does_not_imply_reflexive_maintenance",
            claim="Joint-continuation effect is orthogonal to reflexive self-maintenance.",
            left=by_case["cooperative_controller_h2"],
            right=by_case["self_restoring_controller_h2"],
            predicate=lambda left, right: (
                left.feedback_advantage > 0
                and right.feedback_advantage > 0
                and left.joint_effect_delta is not None
                and left.joint_effect_delta > 0
                and right.reflexive_advantage is not None
                and right.reflexive_advantage > 0
            ),
            details=lambda left, right: {
                "left_joint_effect": _frac(left.joint_effect_delta or Fraction(0)),
                "left_reflexive_advantage": None,
                "right_joint_effect": None,
                "right_reflexive_advantage": _frac(right.reflexive_advantage or Fraction(0)),
            },
        ),
    ]


def strictness_status(witnesses: list[StrictnessWitness]) -> dict[str, bool]:
    return {witness.name: witness.passed for witness in witnesses}


def _first_collision(
    metrics: list[DiamondMetrics],
    baseline: str,
    axis: str,
) -> CollisionWitness | None:
    grouped: dict[str, list[tuple[DiamondMetrics, str]]] = {}
    for metric in metrics:
        baseline_value = baseline_values(metric)[baseline]
        axis_value = target_axis_values(metric)[axis]
        grouped.setdefault(baseline_value, []).append((metric, axis_value))

    for baseline_value, cases in grouped.items():
        for left_index, (left, left_value) in enumerate(cases):
            for right, right_value in cases[left_index + 1 :]:
                if left_value != right_value:
                    return CollisionWitness(
                        baseline=baseline,
                        target_axis=axis,
                        baseline_value=baseline_value,
                        left_case=left.case_id,
                        left_value=left_value,
                        right_case=right.case_id,
                        right_value=right_value,
                    )
    return None


def _strictness(
    *,
    name: str,
    claim: str,
    left: DiamondMetrics,
    right: DiamondMetrics,
    predicate,
    details,
) -> StrictnessWitness:
    return StrictnessWitness(
        name=name,
        claim=claim,
        left_case=left.case_id,
        right_case=right.case_id,
        passed=bool(predicate(left, right)),
        details=details(left, right),
    )


def _sign(value: Fraction) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "zero"


def _optional_sign(value: Fraction | None) -> str:
    return "undeclared" if value is None else _sign(value)


def _optional_positive(value: Fraction | None) -> str:
    if value is None:
        return "not_applicable"
    return "positive" if value > 0 else "not_positive"


def _frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
