from pathlib import Path

from omega.adapters.finite_relational import generate_closure_discovery
from omega.validation.finite_relational_closure_discovery import (
    render_report,
    run_finite_relational_closure_discovery,
)


REQUIRED_FAMILY_IDS = {
    "predicate_seed_partition_sweep",
    "reachability_seed_graph_sweep",
    "viability_seed_graph_sweep",
}


def test_closure_discovery_covers_expected_families_without_expected_surplus() -> None:
    families = generate_closure_discovery()
    by_id = {family.family_id: family for family in families}

    assert set(by_id) == REQUIRED_FAMILY_IDS
    assert by_id["predicate_seed_partition_sweep"].summary()["case_count"] == 8
    assert by_id["reachability_seed_graph_sweep"].summary()["case_count"] == 64
    assert by_id["viability_seed_graph_sweep"].summary()["case_count"] == 64

    for family in families:
        assert family.nonconstant_surplus_cases
        assert family.collapse_cases
        assert family.summary()["search_space"]["expected_surplus_predeclared"] is False
        for case in family.cases:
            assert case.model.get("audits", []) == []
            assert case.observed["missing_expected_surplus_target_facts"] == []
            assert case.observed["missing_expected_nonconstant_surplus_target_facts"] == []
            assert case.observed["present_expected_absent_surplus_target_facts"] == []
            assert (
                case.observed[
                    "present_expected_absent_nonconstant_surplus_target_facts"
                ]
                == []
            )


def test_closure_discovery_classifies_positive_and_collapse_controls() -> None:
    families = generate_closure_discovery()
    by_id = {family.family_id: family for family in families}

    predicate_family = by_id["predicate_seed_partition_sweep"]
    assert len(predicate_family.nonconstant_surplus_cases) == 6
    assert len(predicate_family.collapse_cases) == 2

    for family in families:
        positive = family.nonconstant_surplus_cases[0]
        collapse = family.collapse_cases[0]

        assert positive.classification == "nonconstant_surplus"
        assert positive.observed["nonconstant_surplus_target_facts"]
        assert positive.observed["admissible_presentation_count"] > 0

        assert collapse.classification == "collapse"
        assert collapse.observed["nonconstant_surplus_target_facts"] == []
        assert collapse.observed["admissible_presentation_count"] > 0


def test_closure_discovery_validation_retains_summaries_and_representatives(
    tmp_path: Path,
) -> None:
    result = run_finite_relational_closure_discovery(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["family_count"] == len(REQUIRED_FAMILY_IDS)
    assert result["case_count"] == 136
    assert result["nonconstant_surplus_case_count"] == 50
    assert result["collapse_case_count"] == 86
    assert result["all_families_have_positive_and_collapse_controls"] is True
    assert result["nonconstant_surplus_case_count"] > 0
    assert result["collapse_case_count"] > 0

    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()
    report = render_report(result)
    assert "Cases: 136" in report
    assert "Nonconstant-surplus cases: 50" in report
    assert "Collapse cases: 86" in report
    for family in result["families"]:
        family_dir = Path(str(family["output"]))
        assert (family_dir / "family_summary.json").exists()
        assert (family_dir / "cases.json").exists()
        assert family["representative_cases"]
        for case in family["representative_cases"]:
            out_dir = Path(str(case["output"]))
            assert (out_dir / "model.json").exists()
            assert (out_dir / "model_digest.txt").exists()
            assert (out_dir / "observed_closure.json").exists()
            assert (out_dir / "summary.json").exists()
