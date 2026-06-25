from __future__ import annotations

import json

from omega.agency_diamond.challenge import (
    CHALLENGE_HORIZONS,
    GRAMMARS,
    HOLDOUT_SEEDS,
    REQUIRED_HOLDOUT_CLASSES,
    TRAIN_SEEDS,
    challenge_cases,
    challenge_summary,
    evaluate_challenge_cases,
)
from omega.agency_diamond.run_challenge import run_challenge
from omega.validation.agency_diamond_challenge import run_agency_diamond_challenge


def test_challenge_generator_schedule_is_frozen_and_nonempty():
    cases = challenge_cases()

    assert len(cases) == len(GRAMMARS) * (len(TRAIN_SEEDS) + len(HOLDOUT_SEEDS))
    assert {case.split for case in cases} == {"train", "holdout"}
    assert {case.grammar for case in cases} == set(GRAMMARS)
    assert all(case.system.system_id.startswith("challenge_") for case in cases)

    metrics = evaluate_challenge_cases()
    assert len(metrics) == len(cases) * len(CHALLENGE_HORIZONS)


def test_challenge_summary_passes_holdout_decision_gate():
    summary = challenge_summary()

    assert summary["status"] == "PASS"
    assert summary["case_counts"] == {
        "systems": 42,
        "metric_cases": 210,
        "train_metric_cases": 90,
        "holdout_metric_cases": 120,
    }
    assert REQUIRED_HOLDOUT_CLASSES <= set(summary["holdout_classification_counts"])
    assert all(summary["decision_gate"].values())
    assert not summary["collapse_alerts"]


def test_challenge_counterexample_search_and_baselines_are_derived_from_holdout():
    summary = challenge_summary()

    assert summary["baseline_collision_count"] >= 20
    assert all(summary["required_baseline_collision_status"].values())
    assert all(witness["passed"] for witness in summary["counterexample_search"])
    assert {
        witness["name"] for witness in summary["counterexample_search"]
    } == {
        "generated_recurrence_does_not_imply_feedback_advantage",
        "generated_control_does_not_imply_feedback_advantage",
        "generated_feedback_does_not_imply_reflexive_maintenance",
        "generated_live_success_does_not_determine_joint_effect",
    }


def test_challenge_transport_invariance_controls_pass():
    summary = challenge_summary()
    transport = summary["transport"]

    assert transport["all_transport_checks_passed"] is True
    assert transport["checks"] == {
        "relabel_profiles_preserved": True,
        "identity_presentations_preserve_profiles": True,
        "quotient_controls_passed": True,
    }
    assert len(transport["relabel_reports"]) == 12


def test_challenge_runner_and_validation_entrypoint_write_artifacts(tmp_path):
    summary = run_challenge(tmp_path / "manual")
    assert summary["status"] == "PASS"
    assert (tmp_path / "manual" / "summary.json").exists()
    assert (tmp_path / "manual" / "report.md").exists()

    validation = run_agency_diamond_challenge(out_root=tmp_path / "validation")
    assert validation["status"] == "PASS"
    summary_path = next((tmp_path / "validation").glob("*/summary.json"))
    retained = json.loads(summary_path.read_text(encoding="utf-8"))
    assert retained["status"] == "PASS"
