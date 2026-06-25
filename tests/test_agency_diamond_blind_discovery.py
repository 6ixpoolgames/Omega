from __future__ import annotations

import json

from omega.agency_diamond.blind_discovery import (
    BLIND_HORIZONS,
    BLIND_SEEDS,
    REQUIRED_HOLDOUT_CLASSES,
    blind_cases,
    blind_discovery_summary,
    evaluate_blind_cases,
)
from omega.agency_diamond.run_blind_discovery import run_blind_discovery
from omega.validation.agency_diamond_blind_discovery import (
    run_agency_diamond_blind_discovery,
)


def test_blind_pool_has_no_expected_class_labels():
    cases = blind_cases()

    assert len(cases) == len(BLIND_SEEDS)
    assert all("expected_class" not in case.generator_knobs for case in cases)
    assert all(case.system.system_id.startswith("blind_seed") for case in cases)

    metrics = evaluate_blind_cases()
    assert len(metrics) == len(BLIND_SEEDS) * len(BLIND_HORIZONS)


def test_blind_discovery_summary_passes_decision_gate():
    summary = blind_discovery_summary()

    assert summary["status"] == "PASS"
    assert summary["case_counts"] == {
        "systems": 60,
        "metric_cases": 300,
    }
    assert REQUIRED_HOLDOUT_CLASSES <= set(summary["classification_counts"])
    assert all(summary["decision_gate"].values())


def test_blind_discovery_derives_clusters_and_counterexamples():
    summary = blind_discovery_summary()

    assert summary["derived_clusters"]["cluster_count"] >= 8
    assert summary["baseline_collision_count"] >= 20
    assert all(summary["required_baseline_collision_status"].values())
    assert all(witness["passed"] for witness in summary["counterexample_search"])
    assert {
        witness["name"]
        for witness in summary["counterexample_search"]
    } == {
        "blind_recurrence_does_not_imply_feedback_advantage",
        "blind_control_does_not_imply_feedback_advantage",
        "blind_feedback_does_not_imply_reflexive_maintenance",
        "blind_live_success_scalar_does_not_determine_joint_effect",
    }


def test_blind_discovery_ablation_and_negative_retention():
    summary = blind_discovery_summary()

    assert all(summary["ablation_probes"]["probe_status"].values())
    assert {
        witness["name"]
        for witness in summary["ablation_probes"]["witnesses"]
    } == {
        "blind_observation_ablation_reduces_feedback",
        "blind_fixed_policy_ablation_reduces_feedback",
        "blind_action_choice_ablation_removes_control",
        "blind_channel_ablation_reduces_reflexive_maintenance",
        "blind_joint_ablation_changes_joint_effect",
    }
    assert all(summary["negative_result_retention"]["retention_status"].values())
    assert "collapse_alerts" in summary["negative_result_retention"]


def test_blind_discovery_runner_and_validation_entrypoint_write_artifacts(tmp_path):
    summary = run_blind_discovery(tmp_path / "manual")
    assert summary["status"] == "PASS"
    assert (tmp_path / "manual" / "summary.json").exists()
    assert (tmp_path / "manual" / "report.md").exists()

    validation = run_agency_diamond_blind_discovery(out_root=tmp_path / "validation")
    assert validation["status"] == "PASS"
    summary_path = next((tmp_path / "validation").glob("*/summary.json"))
    retained = json.loads(summary_path.read_text(encoding="utf-8"))
    assert retained["status"] == "PASS"
