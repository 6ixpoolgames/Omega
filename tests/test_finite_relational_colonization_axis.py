from pathlib import Path

from omega.adapters.finite_relational.colonization_axis import (
    HORIZONS,
    basin_system,
    branching_system,
    colonization_axis_summary,
    colonization_refines,
    control_panel,
    control_panels_match,
    profile_summary,
    scalar_shadow_check,
)
from omega.future_field_atlas.util import read_csv
from omega.validation.finite_relational_colonization_axis import (
    render_report,
    run_finite_relational_colonization_axis,
)


def test_colonization_candidate_pair_matches_control_panel() -> None:
    branching = branching_system()
    basin = basin_system()

    assert HORIZONS == (1, 2, 3)
    assert len(branching.states) <= 12
    assert len(basin.states) <= 12
    assert control_panels_match(branching, basin)

    left = control_panel(branching)
    right = control_panel(basin)
    assert left["viable_state_count"] == 4
    assert left["viable_word_counts"] == {"1": 2, "2": 4, "3": 8}
    assert left["viable_word_counts"] == right["viable_word_counts"]
    assert left["recurrence_class_count"] == right["recurrence_class_count"] == 1
    assert left["own_maintenance_score"] == right["own_maintenance_score"] == 0
    assert left["leading_lambda_proxy"] == right["leading_lambda_proxy"] == "2"


def test_colonization_order_separates_matched_pair() -> None:
    branching = branching_system()
    basin = basin_system()

    left_profile = profile_summary(branching)
    right_profile = profile_summary(basin)
    assert left_profile["has_two_level_surplus_chain"] is True
    assert right_profile["has_two_level_surplus_chain"] is False

    assert colonization_refines(branching, basin)["refines"] is True
    assert colonization_refines(basin, branching)["refines"] is False


def test_colonization_demotion_gauntlet_targets_are_retained() -> None:
    summary = colonization_axis_summary()

    assert summary["verdict"] == "separated"
    assert summary["candidate_pair"]["control_panel_equal"] is True
    assert summary["candidate_pair"]["left_refines_right"]["refines"] is True
    assert summary["candidate_pair"]["right_refines_left"]["refines"] is False

    gauntlet = summary["demotion_gauntlet"]
    assert gauntlet["lens_presentation_audit"]["registered_chains_certified"] is True
    assert gauntlet["lens_presentation_audit"]["strict_surplus_has_chain_transport"] is True
    assert gauntlet["converse_witness_attempt"]["same_colonization_profile"] is True
    assert gauntlet["converse_witness_attempt"]["joint_behavior_differs"] is True
    assert gauntlet["scalar_shadow_check"]["scalar_equal"] is True
    assert gauntlet["scalar_shadow_check"]["order_separates"] is True
    assert gauntlet["gauntlet_passes"] is True


def test_scalar_shadow_pair_has_same_scalar_summaries_but_order_separates() -> None:
    shadow = scalar_shadow_check()

    assert shadow["left_signature"] == "1-3-6"
    assert shadow["right_signature"] == "1-2-6"
    assert shadow["scalar_equal"] is True
    assert shadow["left_scalar"] == shadow["right_scalar"]
    assert shadow["order_separates"] is True


def test_colonization_axis_validation_retains_report(tmp_path: Path) -> None:
    result = run_finite_relational_colonization_axis(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["verdict"] == "separated"
    run_root = Path(str(result["run_root"]))
    assert (run_root / "summary.json").exists()
    assert (run_root / "report.md").exists()

    control_rows = read_csv(run_root / "control_panel_comparison.csv")
    assert control_rows
    assert {row["holds"] for row in control_rows} == {"True"}

    report = render_report(result)
    assert "Colonization Axis v0 Discovery Report" in report
    assert "Verdict: separated" in report
    assert "global lens-invariance theorem" in report
