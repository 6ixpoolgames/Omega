from pathlib import Path

from omega.adapters.finite_relational import generate_closure_discovery_v2
from omega.validation.finite_relational_closure_discovery_v2 import (
    render_report,
    run_finite_relational_closure_discovery_v2,
)


REQUIRED_FAMILY_IDS = {
    "step_lifting_seed_graph_sweep",
    "observed_word_seed_graph_sweep",
    "constant_seed_control",
}


def test_closure_discovery_v2_covers_richer_fact_families() -> None:
    families = generate_closure_discovery_v2()
    by_id = {family.family_id: family for family in families}

    assert set(by_id) == REQUIRED_FAMILY_IDS
    assert by_id["step_lifting_seed_graph_sweep"].summary()["case_count"] == 64
    assert by_id["observed_word_seed_graph_sweep"].summary()["case_count"] == 64
    assert by_id["constant_seed_control"].summary()["case_count"] == 4

    step_family = by_id["step_lifting_seed_graph_sweep"]
    assert step_family.dynamic_surplus_cases
    assert step_family.unclassified_dynamic_profile_cases
    assert step_family.collapse_cases

    observed_family = by_id["observed_word_seed_graph_sweep"]
    assert observed_family.dynamic_surplus_cases
    assert not observed_family.unclassified_dynamic_profile_cases
    assert observed_family.collapse_cases

    control_family = by_id["constant_seed_control"]
    assert not control_family.dynamic_surplus_cases
    assert len(control_family.collapse_cases) == 4


def test_closure_discovery_v2_validation_retains_report(tmp_path: Path) -> None:
    result = run_finite_relational_closure_discovery_v2(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["family_count"] == 3
    assert result["case_count"] == 132
    assert result["dynamic_surplus_case_count"] == 101
    assert result["unclassified_dynamic_profile_case_count"] == 36
    assert result["collapse_case_count"] == 31
    assert result["constant_control_collapsed"] is True
    assert (
        result["aggregate"]["unclassified_dynamic_profile_surplus_fact_count"]
        == 120
    )
    assert result["aggregate"]["seed_forced_structural_surplus_fact_count"] == 330

    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()
    report = render_report(result)
    assert "Finite Relational Closure Discovery v2" in report
    assert "Cases: 132" in report
    assert "Dynamic-surplus cases: 101" in report
    assert "Unclassified dynamic-profile cases: 36" in report
    assert "Constant control collapsed: True" in report
    for family in result["families"]:
        family_dir = Path(str(family["output"]))
        assert (family_dir / "family_summary.json").exists()
        assert (family_dir / "cases.json").exists()
        assert family["representative_cases"]
        for case in family["representative_cases"]:
            out_dir = Path(str(case["output"]))
            assert (out_dir / "case.json").exists()
            assert (out_dir / "summary.json").exists()
