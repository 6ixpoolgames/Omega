from pathlib import Path

from omega.adapters.finite_relational.relational_composability import (
    blocked_pair_ensemble,
    compatibility_profile,
    compatible_pair_ensemble,
    compatible_vs_blocked_witness,
    identical_coupling_control,
    relational_composability_summary,
)
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_composability import (
    render_report,
    run_finite_relational_composability,
)


def test_compatible_and_blocked_hold_individual_surface_fixed() -> None:
    witness = compatible_vs_blocked_witness()

    assert witness["marginal_scalar_controls_equal"] is True
    assert witness["full_vector_census_equal"] is True
    assert witness["span_equivalent"] is True
    assert witness["span_rank_separates"] is False


def test_compatibility_profile_separates_same_individuals() -> None:
    compatible = compatibility_profile(compatible_pair_ensemble())
    blocked = compatibility_profile(blocked_pair_ensemble())
    witness = compatible_vs_blocked_witness()

    assert compatible.compatible_pair_count == 1
    assert blocked.compatible_pair_count == 0
    assert compatible.max_compatible_component_size == 2
    assert blocked.max_compatible_component_size == 1
    assert compatible.all_vectors_jointly_compatible is True
    assert blocked.all_vectors_jointly_compatible is False
    assert witness["compatibility_separates"] is True


def test_identical_coupling_control_prevents_overreading() -> None:
    control = identical_coupling_control()

    assert control["full_vector_census_equal"] is True
    assert control["span_equivalent"] is True
    assert control["compatibility_profiles_equal"] is True
    assert control["full_vectors_and_coupling_determine_profile"] is True


def test_relational_composability_summary_retains_separated_verdict() -> None:
    summary = relational_composability_summary()

    assert summary["protocol_doc"] == "docs/research_notes/omega_theory/relational_composability_protocol_v0.md"
    assert summary["verdict"] == "separated"
    assert summary["candidate_pair"]["full_vector_census_equal"] is True
    assert summary["candidate_pair"]["span_equivalent"] is True
    assert summary["candidate_pair"]["compatibility_separates"] is True
    assert summary["negative_controls"]["negative_controls_pass"] is True
    assert "population ethics" in summary["not_claimed"]
    assert "plurality theory" in summary["not_claimed"]


def test_relational_composability_validation_retains_report(tmp_path: Path) -> None:
    result = run_finite_relational_composability(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["verdict"] == "separated"
    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()

    control_rows = read_csv(run_root / "control_comparison.csv")
    assert control_rows
    assert {row["holds"] for row in control_rows} == {"True"}

    profile_rows = read_csv(run_root / "compatibility_profiles.csv")
    assert {row["compatible_pair_count"] for row in profile_rows} == {"0", "1"}

    report = render_report(result)
    assert "Relational Composability v0 Report" in report
    assert "Verdict: separated" in report
    assert "Pure span equivalent: True" in report
