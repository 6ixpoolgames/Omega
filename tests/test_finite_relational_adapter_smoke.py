from pathlib import Path

from omega.validation.finite_relational_adapter_smoke import run_finite_relational_adapter_smoke


def test_finite_relational_adapter_smoke_retains_all_fixture_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_adapter_smoke(out_root=tmp_path, skip_pytest=True)

    assert result["status"] == "PASS"
    assert result["fixture_count"] == 15
    assert result["ir_fixture_count"] == 11
    assert result["derived_graph_fixture_count"] == 3
    assert result["finite_grid_fixture_count"] == 1
    assert result["focused_pytest"] == "skipped"
    for fixture in result["ir_fixtures"]:
        assert fixture["all_passed"] is True
        assert Path(str(fixture["output"])).exists()
    for fixture in result["derived_graph_fixtures"]:
        assert fixture["all_passed"] is True
        assert Path(str(fixture["output"])).exists()
    for fixture in result["finite_grid_fixtures"]:
        assert fixture["all_passed"] is True
        assert Path(str(fixture["output"])).exists()
