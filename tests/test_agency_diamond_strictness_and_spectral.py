from pathlib import Path

from omega.agency_diamond.run_spectral import run_spectral
from omega.agency_diamond.spectral import (
    live_policy_spectral_profile,
    spectral_pilot_summary,
)
from omega.agency_diamond.strictness import own_maintenance_joint_effect_strictness
from omega.agency_diamond.examples import driven_cycle, self_restoring_controller
from omega.validation.agency_diamond_spectral import run_agency_diamond_spectral


def test_same_own_live_maintenance_does_not_determine_joint_effect() -> None:
    result = own_maintenance_joint_effect_strictness(horizon=1)

    assert result["status"] == "PASS"
    assert all(result["decision_gate"].values())
    assert result["positive_case"]["live_maintenance_score"] == "1"
    assert result["negative_case"]["live_maintenance_score"] == "1"
    assert result["positive_case"]["joint_effect_delta"] == "1"
    assert result["negative_case"]["joint_effect_delta"] == "-1"


def test_spectral_phase_is_detector_coordinate_not_sufficient_condition() -> None:
    driven = live_policy_spectral_profile(driven_cycle())
    reflexive = live_policy_spectral_profile(self_restoring_controller())
    result = spectral_pilot_summary(horizon=3)

    assert driven.complex_mode_count > 0
    assert reflexive.complex_mode_count == 0
    assert result["status"] == "PASS"
    assert result["decision_gate"]["complex_phase_not_sufficient_for_deformer_profile"]
    assert result["decision_gate"]["reflexive_profile_not_dependent_on_complex_phase"]


def test_agency_diamond_spectral_runner_and_validation_retain_outputs(
    tmp_path: Path,
) -> None:
    direct = run_spectral(tmp_path / "direct")
    assert direct["status"] == "PASS"
    assert (tmp_path / "direct" / "summary.json").exists()
    assert (tmp_path / "direct" / "report.md").exists()

    validation = run_agency_diamond_spectral(out_root=tmp_path / "validation")
    assert validation["status"] == "PASS"
    run_dirs = [path for path in (tmp_path / "validation").iterdir() if path.is_dir()]
    assert len(run_dirs) == 1
    assert (run_dirs[0] / "summary.json").exists()
    assert (run_dirs[0] / "report.md").exists()
