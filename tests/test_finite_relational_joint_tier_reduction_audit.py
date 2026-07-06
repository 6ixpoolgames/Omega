from pathlib import Path

from omega.adapters.finite_relational.joint_tier_reduction_audit import (
    colonization_reduction_attempt,
    joint_recovery_reduction_attempt,
    joint_tier_reduction_audit_summary,
    planted_null_results,
    relational_composability_reduction_attempt,
)
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_joint_tier_reduction_audit import (
    render_report,
    run_finite_relational_joint_tier_reduction_audit,
)


def test_planted_nulls_reduce_against_declared_bases() -> None:
    results = planted_null_results()

    assert len(results) == 4
    assert {result.verdict for result in results} == {"reduces"}
    assert all(result.passes for result in results)
    assert {result.instrument for result in results} == {
        "ensemble_span",
        "relational_composability",
        "joint_recovery_compatibility",
        "colonization_axis",
    }


def test_relational_reduction_blocks_edge_count_and_degree_only() -> None:
    attempt = relational_composability_reduction_attempt()

    assert attempt.passes is True
    assert attempt.verdict == "survives_simple_graph_scalar_reduction"
    assert attempt.evidence["same_compatible_pair_count"] is True
    assert attempt.evidence["same_degree_sequence"] is True
    assert attempt.evidence["component_structure_separates"] is True


def test_colonization_reduction_keeps_lens_debt_open() -> None:
    attempt = colonization_reduction_attempt()

    assert attempt.passes is True
    assert attempt.verdict == "survives_scalar_shadow_reduction_lens_debt_open"
    assert attempt.evidence["control_panel_equal"] is True
    assert attempt.evidence["scalar_shadow_equal"] is True
    assert attempt.evidence["scalar_shadow_order_separates"] is True
    assert "lens invariance" in attempt.evidence["lens_debt"]


def test_joint_recovery_is_bridge_not_independent_axis() -> None:
    attempt = joint_recovery_reduction_attempt()

    assert attempt.passes is True
    assert attempt.verdict == "bridge_not_independent_axis"
    assert attempt.evidence["individual_recovery_profiles_equal"] is True
    assert attempt.evidence["joint_recovery_separates"] is True


def test_joint_tier_reduction_audit_summary_calibrates() -> None:
    summary = joint_tier_reduction_audit_summary()

    assert summary["protocol_doc"] == (
        "docs/research_notes/omega_theory/joint_tier_reduction_audit_protocol_v0.md"
    )
    assert summary["verdict"] == "calibrated"
    assert summary["planted_nulls_pass"] is True
    assert summary["reduction_attempts_pass"] is True
    assert "CompensationClaim / NOLP verdicts" in summary["not_attacked_this_round"]
    assert "population ethics" in summary["not_claimed"]


def test_joint_tier_reduction_audit_validation_retains_report(tmp_path: Path) -> None:
    result = run_finite_relational_joint_tier_reduction_audit(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["verdict"] == "calibrated"
    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()

    null_rows = read_csv(run_root / "planted_nulls.csv")
    assert {row["verdict"] for row in null_rows} == {"reduces"}

    reduction_rows = read_csv(run_root / "reduction_attempts.csv")
    assert {row["passes"] for row in reduction_rows} == {"True"}

    report = render_report(result)
    assert "Joint-Tier Reduction Audit v0 Report" in report
    assert "Verdict: calibrated" in report
    assert "bridge rather than an independent axis" in report
