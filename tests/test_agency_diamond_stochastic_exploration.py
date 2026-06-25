from pathlib import Path

from omega.agency_diamond.run_stochastic_exploration import run_stochastic_exploration
from omega.agency_diamond.stochastic_exploration import (
    calibration_phase_summary,
    cross_substrate_stochastic_summary,
    heldout_search_summary,
    heldout_stochastic_cases,
    stochastic_exploration_summary,
)
from omega.validation.agency_diamond_stochastic_exploration import (
    run_agency_diamond_stochastic_exploration,
)


def test_heldout_search_has_no_expected_class_labels_and_discovers_profiles() -> None:
    cases = heldout_stochastic_cases()
    assert cases
    assert all("expected_class" not in case.generator_knobs for case in cases)
    assert all(case.generator_knobs["has_expected_class_label"] is False for case in cases)

    summary = heldout_search_summary()
    assert summary["status"] == "PASS"
    assert all(summary["decision_gate"].values())
    assert summary["derived_clusters"]["cluster_count"] >= 5
    assert summary["classification_counts"]["feedback_advantage"] > 0
    assert summary["classification_counts"]["reflexive_maintenance"] > 0
    assert summary["classification_counts"]["dominant_joint_contraction"] > 0


def test_cross_substrate_stochastic_profiles_have_independent_witnesses() -> None:
    summary = cross_substrate_stochastic_summary()
    assert summary["status"] == "PASS"
    assert all(summary["decision_gate"].values())
    assert set(summary["classification_by_substrate"]) == {
        "boolean",
        "grid",
        "resource",
    }
    assert all(len(counts) >= 2 for counts in summary["classification_by_substrate"].values())
    assert all(witness["passed"] for witness in summary["witnesses"])


def test_calibration_phase_sweeps_find_regions_and_monotone_curves() -> None:
    summary = calibration_phase_summary()
    assert summary["status"] == "PASS"
    assert all(summary["decision_gate"].values())
    assert summary["thresholds"]["first_positive_feedback_reliability"] == "1/5"
    assert summary["thresholds"]["first_positive_repair_reliability"] == "1/5"
    assert summary["thresholds"]["first_negative_joint_risk"] == "0"
    assert len(summary["curves"]["feedback_reliability"]) >= 5
    assert len(summary["curves"]["joint_risk"]) >= 5


def test_stochastic_exploration_runner_and_validation_retain_outputs(tmp_path: Path) -> None:
    summary = stochastic_exploration_summary()
    assert summary["status"] == "PASS"
    assert all(summary["decision_gate"].values())

    direct = run_stochastic_exploration(tmp_path / "direct")
    assert direct["status"] == "PASS"
    assert (tmp_path / "direct" / "summary.json").exists()
    assert (tmp_path / "direct" / "report.md").exists()

    validation = run_agency_diamond_stochastic_exploration(
        out_root=tmp_path / "validation"
    )
    assert validation["status"] == "PASS"
    run_dirs = [path for path in (tmp_path / "validation").iterdir() if path.is_dir()]
    assert len(run_dirs) == 1
    assert (run_dirs[0] / "summary.json").exists()
    assert (run_dirs[0] / "report.md").exists()
