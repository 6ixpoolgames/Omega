from pathlib import Path

from omega.adapters.finite_relational import generate_closure_attribution_v21
from omega.validation.finite_relational_closure_attribution_v21 import (
    render_report,
    run_finite_relational_closure_attribution_v21,
)


REQUIRED_FAMILY_IDS = {
    "current_v2_attribution",
    "heldout_n4_step_lifting_sample",
    "heldout_n4_observed_word_sample",
    "heldout_n4_constant_control",
}


def test_closure_attribution_v21_explains_current_and_heldout_surplus() -> None:
    families = generate_closure_attribution_v21()
    by_id = {family.family_id: family for family in families}

    assert set(by_id) == REQUIRED_FAMILY_IDS
    assert by_id["current_v2_attribution"].summary()["case_count"] == 132
    assert by_id["heldout_n4_step_lifting_sample"].summary()["case_count"] == 32
    assert by_id["heldout_n4_observed_word_sample"].summary()["case_count"] == 32
    assert by_id["heldout_n4_constant_control"].summary()["case_count"] == 8

    for family in families:
        assert family.summary()["residual_case_count"] == 0
        assert family.summary()["aggregate"]["residual_fact_count"] == 0

    current = by_id["current_v2_attribution"].summary()["aggregate"]
    assert current["bucket_counts"]["bounded_process_coherence_invariance"] == 120
    assert current["bucket_counts"]["step_implies_path_lifting"] == 294

    heldout_step = by_id["heldout_n4_step_lifting_sample"].summary()["aggregate"]
    assert heldout_step["bucket_counts"]["bounded_process_coherence_invariance"] == 82
    assert heldout_step["residual_fact_count"] == 0


def test_closure_attribution_v21_validation_retains_report(tmp_path: Path) -> None:
    result = run_finite_relational_closure_attribution_v21(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["family_count"] == 4
    assert result["case_count"] == 204
    assert result["residual_case_count"] == 0
    assert result["aggregate"]["residual_fact_count"] == 0
    assert (
        result["aggregate"]["bucket_counts"][
            "bounded_process_coherence_invariance"
        ]
        == 202
    )
    assert result["aggregate"]["bucket_counts"]["step_implies_path_lifting"] == 444

    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()
    report = render_report(result)
    assert "Finite Relational Closure Attribution v2.1" in report
    assert "Cases: 204" in report
    assert "Residual cases: 0" in report
    assert "Residual facts: 0" in report
    for family in result["families"]:
        family_dir = Path(str(family["output"]))
        assert (family_dir / "family_summary.json").exists()
        assert (family_dir / "cases.json").exists()
        assert family["representative_cases"]
        for case in family["representative_cases"]:
            out_dir = Path(str(case["output"]))
            assert (out_dir / "summary.json").exists()
            assert (out_dir / "attributions.json").exists()
