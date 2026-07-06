from pathlib import Path

from omega.adapters.finite_relational.joint_recovery_compatibility import (
    compatible_joint_recovery_case,
    compatible_vs_interfering_witness,
    identical_joint_recovery_control,
    individual_difference_control,
    interfering_joint_recovery_case,
    joint_recovery_compatibility_summary,
    joint_recovery_compatible,
    recovery_profile,
)
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_joint_recovery_compatibility import (
    render_report,
    run_finite_relational_joint_recovery_compatibility,
)


def test_candidate_holds_individual_surface_fixed() -> None:
    witness = compatible_vs_interfering_witness()

    assert witness["marginal_scalar_controls_equal"] is True
    assert witness["full_vector_census_equal"] is True
    assert witness["span_equivalent"] is True
    assert witness["span_rank_separates"] is False
    assert witness["individual_recovery_profiles_equal"] is True


def test_joint_recovery_separates_compatible_and_interfering_couplings() -> None:
    compatible = recovery_profile(compatible_joint_recovery_case())
    interfering = recovery_profile(interfering_joint_recovery_case())
    witness = compatible_vs_interfering_witness()

    assert compatible.all_individual_recovery_succeeds is True
    assert interfering.all_individual_recovery_succeeds is True
    assert compatible.joint_recovery_succeeds is True
    assert interfering.joint_recovery_succeeds is False
    assert interfering.joint_missing_fact_ids == ("B_recovery_fact",)
    assert joint_recovery_compatible(compatible_joint_recovery_case()) is True
    assert joint_recovery_compatible(interfering_joint_recovery_case()) is False
    assert witness["joint_recovery_separates"] is True


def test_negative_controls_prevent_overreading() -> None:
    identical = identical_joint_recovery_control()
    individual_difference = individual_difference_control()

    assert identical["individual_recovery_profiles_equal"] is True
    assert identical["joint_recovery_separates"] is False
    assert identical["same_individual_and_joint_recovery_determine_profile"] is True
    assert individual_difference["individual_recovery_profiles_equal"] is False
    assert individual_difference["not_credited_as_joint_only"] is True


def test_joint_recovery_compatibility_summary_retains_separated_verdict() -> None:
    summary = joint_recovery_compatibility_summary()

    assert summary["protocol_doc"] == (
        "docs/research_notes/omega_theory/joint_recovery_compatibility_protocol_v0.md"
    )
    assert summary["verdict"] == "separated"
    assert summary["candidate_pair"]["individual_recovery_profiles_equal"] is True
    assert summary["candidate_pair"]["joint_recovery_separates"] is True
    assert summary["negative_controls"]["negative_controls_pass"] is True
    assert "moral aggregation" in summary["not_claimed"]
    assert "patienthood" in summary["not_claimed"]


def test_joint_recovery_compatibility_validation_retains_report(tmp_path: Path) -> None:
    result = run_finite_relational_joint_recovery_compatibility(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["verdict"] == "separated"
    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()

    control_rows = read_csv(run_root / "control_comparison.csv")
    assert control_rows
    assert {row["holds"] for row in control_rows} == {"True"}

    profile_rows = read_csv(run_root / "joint_recovery_profiles.csv")
    assert {row["joint_recovery_succeeds"] for row in profile_rows} == {"False", "True"}

    report = render_report(result)
    assert "Joint Recovery Compatibility v0 Report" in report
    assert "Verdict: separated" in report
    assert "Individual recovery profiles equal: True" in report
