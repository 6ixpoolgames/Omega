from pathlib import Path

from omega.adapters.finite_relational.ensemble_span import (
    compare_ensembles,
    coplanar_rank2_ensemble,
    correlated_addition_ensemble,
    determinant,
    diminishing_returns_witness,
    ensemble_span_summary,
    full_rank3_ensemble,
    full_vector_census_control,
    identical_vectors_control,
    larger_rank_robustness_witness,
    marginal_controls_match,
    marginal_summary,
    matrix_rank,
    orthogonal_addition_ensemble,
    orthogonal_ensemble,
    redundant_ensemble,
    span_includes,
    span_profile,
)
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_ensemble_span import (
    render_report,
    run_finite_relational_ensemble_span,
)


def test_exact_rank_and_determinant_helpers() -> None:
    assert matrix_rank(((1, 0), (1, 0))) == 1
    assert matrix_rank(((1, 0), (0, 1))) == 2
    assert determinant(((1, 1), (1, 1))) == 0
    assert determinant(((1, 0), (0, 1))) == 1


def test_redundant_and_orthogonal_match_marginal_scalar_controls() -> None:
    redundant = redundant_ensemble()
    orthogonal = orthogonal_ensemble()

    assert marginal_controls_match(redundant, orthogonal)
    assert marginal_summary(redundant).as_dict() == {
        "valuer_count": 2,
        "vector_dimension": 2,
        "per_valuer_l1_norms": [1, 1],
        "total_l1_amount": 2,
        "max_individual_l1_norm": 1,
    }


def test_redundant_vs_orthogonal_span_separates() -> None:
    redundant = redundant_ensemble()
    orthogonal = orthogonal_ensemble()
    comparison = compare_ensembles(redundant, orthogonal)

    assert comparison["marginal_scalar_controls_equal"] is True
    assert comparison["left_span_profile"]["rank"] == 1
    assert comparison["right_span_profile"]["rank"] == 2
    assert comparison["rank_separates"] is True
    assert comparison["left_span_includes_right"] is False
    assert comparison["right_span_includes_left"] is True
    assert comparison["full_vector_census_equal"] is False


def test_diminishing_returns_witness_separates_orientation_gain() -> None:
    witness = diminishing_returns_witness()

    assert witness["added_vector_l1_norms_equal"] is True
    assert witness["base_rank"] == 1
    assert witness["correlated_rank_gain"] == 0
    assert witness["orthogonal_rank_gain"] == 1
    assert span_profile(correlated_addition_ensemble()).rank == 1
    assert span_profile(orthogonal_addition_ensemble()).rank == 2


def test_larger_rank_robustness_witness_separates_after_matched_controls() -> None:
    witness = larger_rank_robustness_witness()

    assert marginal_controls_match(coplanar_rank2_ensemble(), full_rank3_ensemble())
    assert witness["marginal_scalar_controls_equal"] is True
    assert witness["left_span_profile"]["rank"] == 2
    assert witness["right_span_profile"]["rank"] == 3
    assert witness["rank_separates"] is True
    assert witness["left_span_includes_right"] is False
    assert witness["right_span_includes_left"] is True


def test_negative_controls_prevent_overreading() -> None:
    identical = identical_vectors_control()
    full_census = full_vector_census_control()

    assert identical["all_vectors_identical"] is True
    assert identical["rank_reduces_to_singleton_orientation"] is True
    assert full_census["full_vector_census_equal"] is True
    assert full_census["span_equivalent"] is True
    assert full_census["full_vector_census_determines_pure_span"] is True


def test_span_inclusion_order_is_exact() -> None:
    redundant = redundant_ensemble()
    orthogonal = orthogonal_ensemble()

    assert span_includes(orthogonal, redundant)
    assert not span_includes(redundant, orthogonal)
    assert span_includes(redundant, redundant)


def test_ensemble_span_summary_retains_separated_verdict() -> None:
    summary = ensemble_span_summary()

    assert summary["protocol_doc"] == "docs/research_notes/omega_theory/ensemble_span_protocol_v0.md"
    assert summary["verdict"] == "separated"
    assert summary["candidate_pair"]["marginal_scalar_controls_equal"] is True
    assert summary["candidate_pair"]["rank_separates"] is True
    assert summary["larger_rank_robustness"]["marginal_scalar_controls_equal"] is True
    assert summary["larger_rank_robustness"]["rank_separates"] is True
    assert summary["negative_controls"]["negative_controls_pass"] is True
    assert "population ethics" in summary["not_claimed"]
    assert "relational surplus" in summary["not_claimed"]


def test_ensemble_span_validation_retains_report(tmp_path: Path) -> None:
    result = run_finite_relational_ensemble_span(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["verdict"] == "separated"
    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()

    control_rows = read_csv(run_root / "marginal_control_comparison.csv")
    assert control_rows
    assert {row["holds"] for row in control_rows} == {"True"}

    span_rows = read_csv(run_root / "span_profiles.csv")
    assert {row["rank"] for row in span_rows} == {"1", "2"}

    report = render_report(result)
    assert "Ensemble Span v0 Report" in report
    assert "Verdict: separated" in report
    assert "Full-vector census determines pure span: True" in report
