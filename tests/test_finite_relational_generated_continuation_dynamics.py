from __future__ import annotations

from pathlib import Path

from omega.adapters.finite_relational.generated_continuation_dynamics import (
    COMPONENTS,
    HORIZONS,
    VERDICTS,
    compatibility_search,
    deformation_distribution_study,
    generated_continuation_dynamics_summary,
    generated_system_records,
    jointly_realizable,
    nonflag_search_rows,
    shared_action_assignments,
)
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_generated_continuation_dynamics import (
    render_report,
    run_generated_continuation_dynamics,
)


def test_shared_action_manifest_is_exhaustive_and_deterministic() -> None:
    first = shared_action_assignments()
    second = shared_action_assignments()

    assert len(first) == 216
    assert first == second
    assert len({assignment.assignment_id for assignment in first}) == 216


def test_generated_compatibility_is_downward_closed() -> None:
    study = compatibility_search()

    assert study["downward_closure_failures"] == []
    assert study["intersection_correspondence_failures"] == []
    assert study["cases"]["GN2_downward_closure"] is True


def test_generated_hollow_witness_has_complete_one_skeleton() -> None:
    study = compatibility_search()
    hollow = study["hollow"]

    assert hollow["allowed_actions"] == {
        "A": ["a0", "a1"],
        "B": ["a0", "a2"],
        "C": ["a1", "a2"],
    }
    assert hollow["one_skeleton"] == [["A", "B"], ["A", "C"], ["B", "C"]]
    assert hollow["maximal_faces"] == [["A", "B"], ["A", "C"], ["B", "C"]]
    assert hollow["is_flag"] is False


def test_matched_filled_control_changes_only_triple_intersection() -> None:
    study = compatibility_search()
    hollow = study["hollow"]
    filled = study["filled"]

    assert study["cases"]["GN4_matched_filled_control"] is True
    assert filled["is_flag"] is True
    assert filled["maximal_faces"] == [["A", "B", "C"]]
    assert hollow["kernel_sizes"]["A+B+C"] == 0
    assert filled["kernel_sizes"]["A+B+C"] == 1


def test_same_action_quantifier_and_deadlock_controls_pass() -> None:
    study = compatibility_search()

    assert study["independent_action_triple_realizable"] is True
    assert study["deadlock_singleton_realizable"] is False
    assert study["relabeling_preserved"] is True
    assert study["bridge_faces_equal"] is True


def test_nonflag_search_rows_are_reconstructible() -> None:
    rows = nonflag_search_rows()

    assert len(rows) == 216
    assert (
        sum(bool(row["is_hollow"]) for row in rows)
        == compatibility_search()["hollow_assignment_count"]
    )
    assert (
        sum(bool(row["is_filled"]) for row in rows)
        == compatibility_search()["filled_assignment_count"]
    )


def test_deformation_generator_manifest_and_classes_are_retained() -> None:
    study = deformation_distribution_study()
    manifest = study["manifest"]

    assert manifest["class_counts"] == {
        "complete": 5832,
        "reversible": 288,
        "absorbing": 440,
    }
    assert len(tuple(generated_system_records())) == 5832
    assert len(manifest["manifest_digest"]) == 64


def test_deformation_distributions_reconstruct_at_every_horizon() -> None:
    study = deformation_distribution_study()
    rows = study["distribution_rows"]

    assert len(rows) == 9
    assert {row["horizon"] for row in rows} == set(HORIZONS)
    for row in rows:
        assert (
            sum(int(row[f"structural_{verdict}_count"]) for verdict in VERDICTS)
            == row["structural_edge_count"]
        )
        assert (
            abs(sum(float(row[f"structural_{verdict}_share"]) for verdict in VERDICTS) - 1.0)
            < 1e-12
        )


def test_deformation_sensitivity_controls_pass() -> None:
    study = deformation_distribution_study()

    assert study["duplicate_action_control"]["structural_verdicts_preserved"]
    assert study["duplicate_action_control"]["action_weight_changed"]
    assert study["relabeling_control"]["preserved"]
    assert study["reverse_edge_control"]["synthetic_reverse_excluded"]
    assert set(study["retained_classifier_verdicts"]) == set(VERDICTS)


def test_summary_prices_results_without_thermodynamic_claim() -> None:
    summary = generated_continuation_dynamics_summary()

    assert summary["verdict"] == "retained"
    assert all(summary["case_results"].values())
    assert summary["evidence_classification"]["constructive_strictness"] == [
        "GN3_generated_nonflag",
        "GN4_matched_filled_control",
    ]
    assert summary["evidence_classification"]["risky_generated_result"] == ["DD2_distributions"]
    assert "thermodynamic arrow" in summary["not_claimed"]


def test_validation_retains_all_preregistered_outputs(tmp_path: Path) -> None:
    result = run_generated_continuation_dynamics(out_root=tmp_path)

    assert result["status"] == "PASS"
    run_root = Path(str(result["run_root"]))
    expected = {
        "summary.json",
        "case_results.csv",
        "generator_manifest.csv",
        "nonflag_search.csv",
        "nonflag_witness.json",
        "deformation_distribution.csv",
        "deformation_system_summary.csv",
        "sensitivity_results.csv",
        "report.md",
    }
    assert {path.name for path in run_root.iterdir()} == expected
    assert len(read_csv(run_root / "nonflag_search.csv")) == 216
    assert len(read_csv(run_root / "deformation_distribution.csv")) == 9
    assert len(read_csv(run_root / "deformation_system_summary.csv")) == (5832 * len(HORIZONS))

    report = render_report(result)
    assert "Generated Continuation Dynamics v0 Report" in report
    assert "Graph direction is not a thermodynamic orientation." in report


def test_generated_hollow_triple_is_not_jointly_realizable() -> None:
    hollow_id = compatibility_search()["hollow"]["assignment_id"]
    hollow = next(
        assignment
        for assignment in shared_action_assignments()
        if assignment.assignment_id == hollow_id
    )

    assert not jointly_realizable(hollow, frozenset(COMPONENTS))
