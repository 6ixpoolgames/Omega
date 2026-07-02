"""Strictness witnesses for finite agency-diamond profile axes."""

from __future__ import annotations

from typing import Any

from omega.agency_diamond.examples import cooperative_controller, dominant_horizon_controller
from omega.agency_diamond.metrics import DiamondMetrics, evaluate_system


CLAIM_BOUNDARY = (
    "Finite agency-diamond strictness witness only. This does not detect agency, "
    "identity, value, valuerhood, moral standing, or Omega validation. It only "
    "shows that one own-maintenance scalar does not determine joint-continuation "
    "effect in the declared finite battery."
)


def own_maintenance_joint_effect_strictness(*, horizon: int = 1) -> dict[str, Any]:
    """Compare same own live-maintenance score with different joint effects."""

    positive = evaluate_system(
        cooperative_controller(),
        horizon=horizon,
        case_id=f"cooperative_joint_positive_h{horizon}",
    )
    negative = evaluate_system(
        dominant_horizon_controller(),
        horizon=horizon,
        case_id=f"dominant_joint_negative_h{horizon}",
    )
    decision_gate = {
        "same_live_maintenance_score": (
            positive.live_maintenance_score == negative.live_maintenance_score
        ),
        "positive_joint_effect_positive": (
            positive.joint_effect_delta is not None
            and positive.joint_effect_delta > 0
        ),
        "negative_joint_effect_negative": (
            negative.joint_effect_delta is not None
            and negative.joint_effect_delta < 0
        ),
        "joint_effects_differ": positive.joint_effect_delta
        != negative.joint_effect_delta,
    }
    return {
        "name": "same_own_live_maintenance_different_joint_effect",
        "status": "PASS" if all(decision_gate.values()) else "FAIL",
        "claim_boundary": CLAIM_BOUNDARY,
        "horizon": horizon,
        "description": (
            "Two declared finite systems both maintain their own live target with "
            "score 1, while one expands the declared joint-safe surface and the "
            "other contracts it."
        ),
        "positive_case": _strictness_row(positive),
        "negative_case": _strictness_row(negative),
        "decision_gate": decision_gate,
        "non_claims": [
            "not a complete own-maintenance profile",
            "not a moral valence theorem",
            "not agency detection",
            "not empirical validation",
        ],
    }


def _strictness_row(metric: DiamondMetrics) -> dict[str, Any]:
    return {
        "case_id": metric.case_id,
        "system_id": metric.system_id,
        "family": metric.family,
        "classification": metric.classification,
        "live_maintenance_score": str(metric.live_maintenance_score),
        "replay_maintenance_score": str(metric.replay_maintenance_score),
        "feedback_advantage": str(metric.feedback_advantage),
        "joint_live_score": (
            None if metric.joint_live_score is None else str(metric.joint_live_score)
        ),
        "joint_replay_score": (
            None if metric.joint_replay_score is None else str(metric.joint_replay_score)
        ),
        "joint_effect_delta": (
            None if metric.joint_effect_delta is None else str(metric.joint_effect_delta)
        ),
    }
