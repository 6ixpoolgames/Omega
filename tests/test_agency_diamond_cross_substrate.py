from __future__ import annotations

import json

from omega.agency_diamond.cross_substrate import (
    CROSS_SUBSTRATE_HORIZONS,
    HOLDOUT_SEEDS,
    MODES_BY_SUBSTRATE,
    REQUIRED_HOLDOUT_CLASSES,
    SUBSTRATES,
    TRAIN_SEEDS,
    cross_substrate_cases,
    cross_substrate_summary,
    evaluate_cross_substrate_cases,
)
from omega.agency_diamond.run_cross_substrate import run_cross_substrate
from omega.validation.agency_diamond_cross_substrate import (
    run_agency_diamond_cross_substrate,
)


def test_cross_substrate_generator_schedule_is_frozen_and_nonempty():
    cases = cross_substrate_cases()
    mode_count = sum(len(modes) for modes in MODES_BY_SUBSTRATE.values())

    assert len(cases) == mode_count * (len(TRAIN_SEEDS) + len(HOLDOUT_SEEDS))
    assert {case.split for case in cases} == {"train", "holdout"}
    assert {case.substrate for case in cases} == set(SUBSTRATES)
    assert all(case.system.system_id.startswith("cross_") for case in cases)

    metrics = evaluate_cross_substrate_cases()
    assert len(metrics) == len(cases) * len(CROSS_SUBSTRATE_HORIZONS)


def test_cross_substrate_summary_passes_decision_gate():
    summary = cross_substrate_summary()

    assert summary["status"] == "PASS"
    assert summary["case_counts"] == {
        "systems": 40,
        "metric_cases": 200,
        "train_metric_cases": 80,
        "holdout_metric_cases": 120,
    }
    assert REQUIRED_HOLDOUT_CLASSES <= set(summary["holdout_classification_counts"])
    assert set(summary["holdout_classification_by_substrate"]) == set(SUBSTRATES)
    assert all(summary["decision_gate"].values())
    assert not summary["collapse_alerts"]


def test_cross_substrate_adversarial_probes_are_derived_from_holdout():
    summary = cross_substrate_summary()

    assert all(summary["adversarial"]["probe_status"].values())
    assert {
        witness["name"]
        for witness in summary["adversarial"]["witnesses"]
    } == {
        "cross_substrate_same_substrate_separates_feedback",
        "cross_substrate_control_without_feedback_found",
        "cross_substrate_feedback_without_reflexive_found",
        "cross_substrate_joint_sign_not_live_success",
        "cross_substrate_recurrence_not_feedback",
    }
    assert all(witness["passed"] for witness in summary["counterexample_search"])
    assert all(summary["required_baseline_collision_status"].values())


def test_cross_substrate_transport_controls_pass():
    transport = cross_substrate_summary()["transport"]

    assert transport["all_transport_checks_passed"] is True
    assert transport["checks"] == {
        "relabel_profiles_preserved": True,
        "identity_presentations_preserve_profiles": True,
        "quotient_controls_passed": True,
    }
    assert len(transport["relabel_reports"]) == 18
    assert transport["identity_report_count"] == 18


def test_cross_substrate_runner_and_validation_entrypoint_write_artifacts(tmp_path):
    summary = run_cross_substrate(tmp_path / "manual")
    assert summary["status"] == "PASS"
    assert (tmp_path / "manual" / "summary.json").exists()
    assert (tmp_path / "manual" / "report.md").exists()

    validation = run_agency_diamond_cross_substrate(out_root=tmp_path / "validation")
    assert validation["status"] == "PASS"
    summary_path = next((tmp_path / "validation").glob("*/summary.json"))
    retained = json.loads(summary_path.read_text(encoding="utf-8"))
    assert retained["status"] == "PASS"
