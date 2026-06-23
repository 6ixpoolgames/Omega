from pathlib import Path

from omega.adapters.finite_relational import generate_source_parity_study
from omega.validation.finite_relational_source_parity import (
    run_finite_relational_source_parity,
)


REQUIRED_CASE_IDS = {
    "graph_grid_strict_asymmetry_parity",
    "graph_grid_recurrent_carrier_parity",
}


def test_source_parity_cases_compare_same_ir_surface() -> None:
    cases = generate_source_parity_study()
    by_id = {case.case_id: case for case in cases}

    assert set(by_id) == REQUIRED_CASE_IDS
    assert all(case.all_passed for case in cases)

    strict = by_id["graph_grid_strict_asymmetry_parity"].comparison
    assert strict["state_domain_match"] is True
    assert strict["relation_matches"] == {
        "next": True,
        "primitive_rel": True,
        "primitive_sep": True,
        "primitive_asym": True,
        "merge_separated": True,
    }
    assert strict["predicate_matches"] == {"safe": True}
    assert strict["function_matches"] == {"identity": True, "constant": True}
    assert strict["left_audit_findings"] == strict["right_audit_findings"]
    assert strict["left_audits_passed"] is True
    assert strict["right_audits_passed"] is True

    carrier = by_id["graph_grid_recurrent_carrier_parity"].comparison
    assert carrier["state_domain_match"] is True
    assert carrier["relation_matches"]["primitive_asym"] is True
    assert carrier["predicate_matches"] == {"safe": True, "carrier_0": True}
    assert carrier["function_matches"] == {"identity": True}
    assert carrier["left_audit_findings"]["carrier_0_certificate"] == "certified"
    assert carrier["right_audit_findings"]["carrier_0_certificate"] == "certified"


def test_source_parity_validation_retains_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_source_parity(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["case_count"] == len(REQUIRED_CASE_IDS)
    assert result["all_passed"] is True
    assert (Path(str(result["run_root"])) / "summary.json").exists()
    for case in result["cases"]:
        out_dir = Path(str(case["output"]))
        assert (out_dir / "left_source.json").exists()
        assert (out_dir / "right_source.json").exists()
        assert (out_dir / "left_compiled_model.json").exists()
        assert (out_dir / "right_compiled_model.json").exists()
        assert (out_dir / "comparison.json").exists()
        assert (out_dir / "summary.json").exists()
        assert (out_dir / "left_source_digest.txt").exists()
        assert (out_dir / "right_source_digest.txt").exists()
        assert (out_dir / "left_compiled_model_digest.txt").exists()
        assert (out_dir / "right_compiled_model_digest.txt").exists()
