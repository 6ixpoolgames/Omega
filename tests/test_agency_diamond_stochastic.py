from fractions import Fraction
from pathlib import Path

from omega.agency_diamond.stochastic_examples import (
    REQUIRED_STOCHASTIC_CLASSES,
    STOCHASTIC_BLIND_SEEDS,
    stochastic_blind_cases,
    stochastic_counterexample_search,
    stochastic_null_battery,
    stochastic_pilot_summary,
)
from omega.agency_diamond.stochastic_metrics import (
    coherence_reports,
    evaluate_stochastic_system,
    strong_lumpability_report,
)
from omega.agency_diamond.stochastic_model import validate_stochastic_system
from omega.agency_diamond.run_stochastic import run_stochastic
from omega.validation.agency_diamond_stochastic import run_agency_diamond_stochastic


def test_stochastic_systems_are_exact_rational_and_valid() -> None:
    systems = stochastic_null_battery()
    assert systems
    for system in systems:
        validate_stochastic_system(system)
        for scenario in system.scenarios:
            for state in system.states:
                for action in system.actions:
                    row = system.transition[scenario][state][action]
                    assert all(isinstance(value, Fraction) for value in row.values())
                    assert sum(row.values(), start=Fraction(0)) == 1


def test_stochastic_metrics_separate_feedback_reflexive_and_joint_axes() -> None:
    metrics = [
        evaluate_stochastic_system(system, horizon=1)
        for system in stochastic_null_battery()
    ]
    classes = {metric.classification for metric in metrics}
    assert "feedback_advantage" in classes
    assert "reflexive_maintenance" in classes
    assert "dominant_joint_contraction" in classes
    feedback = next(metric for metric in metrics if metric.classification == "feedback_advantage")
    reflexive = next(metric for metric in metrics if metric.classification == "reflexive_maintenance")
    joint = next(metric for metric in metrics if metric.classification == "dominant_joint_contraction")
    assert feedback.feedback_advantage > 0
    assert reflexive.reflexive_advantage is not None
    assert reflexive.reflexive_advantage > 0
    assert joint.joint_effect_delta is not None
    assert joint.joint_effect_delta < 0


def test_stochastic_blind_generation_has_no_expected_labels() -> None:
    cases = stochastic_blind_cases()
    assert len(cases) == len(STOCHASTIC_BLIND_SEEDS)
    assert all("expected_class" not in case.generator_knobs for case in cases)
    assert all(case.generator_knobs["has_expected_class_label"] is False for case in cases)


def test_stochastic_pilot_summary_passes_gates_and_retains_controls() -> None:
    summary = stochastic_pilot_summary()
    assert summary["status"] == "PASS"
    assert all(summary["decision_gate"].values())
    assert REQUIRED_STOCHASTIC_CLASSES <= set(summary["blind_classification_counts"])
    assert summary["coherence"]["strongly_lumpable_count"] > 0
    assert summary["coherence"]["non_lumpable_count"] > 0
    assert all(summary["negative_result_retention"]["retention_status"].values())
    assert all(witness["passed"] for witness in summary["counterexample_search"])
    scalar = next(
        witness
        for witness in summary["counterexample_search"]
        if witness["name"] == "stochastic_live_success_scalar_does_not_determine_joint_effect"
    )
    assert scalar["left_case"] != scalar["right_case"]
    assert scalar["details"]["left_joint_effect"] != scalar["details"]["right_joint_effect"]


def test_stochastic_lumpability_has_positive_and_negative_controls() -> None:
    reports = [
        report
        for case in stochastic_blind_cases()
        for report in coherence_reports(case.system)
    ]
    assert any(report.strongly_lumpable for report in reports)
    assert any(not report.strongly_lumpable for report in reports)
    non_lumpable = next(report for report in reports if not report.strongly_lumpable)
    assert non_lumpable.witness_count > 0

    system = stochastic_null_battery()[2]
    identity = {state: state for state in system.states}
    identity_report = strong_lumpability_report(system, "identity", identity)
    assert identity_report.strongly_lumpable


def test_stochastic_counterexample_search_uses_distinct_scalar_cases() -> None:
    metrics = [
        evaluate_stochastic_system(case.system, horizon=1, case_id=f"seed{case.seed}")
        for case in stochastic_blind_cases()
    ]
    witnesses = stochastic_counterexample_search(metrics)
    scalar = next(
        witness
        for witness in witnesses
        if witness.name == "stochastic_live_success_scalar_does_not_determine_joint_effect"
    )
    assert scalar.passed
    assert scalar.left_case != scalar.right_case


def test_stochastic_validation_retains_outputs(tmp_path: Path) -> None:
    direct = run_stochastic(tmp_path / "direct")
    assert direct["status"] == "PASS"
    assert (tmp_path / "direct" / "summary.json").exists()
    assert (tmp_path / "direct" / "report.md").exists()

    validation = run_agency_diamond_stochastic(out_root=tmp_path / "validation")
    assert validation["status"] == "PASS"
    run_dirs = [path for path in (tmp_path / "validation").iterdir() if path.is_dir()]
    assert len(run_dirs) == 1
    assert (run_dirs[0] / "summary.json").exists()
    assert (run_dirs[0] / "report.md").exists()
