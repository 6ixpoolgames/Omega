from pathlib import Path

from omega.contextual_future_fields.run_witnesses import run_contextual_future_fields
from omega.contextual_future_fields.witnesses import (
    compatibility_thickness_kernel_witnesses,
    contextual_future_field_summary,
    density_deformation_witnesses,
    holonomy_witnesses,
    parity_no_global_extension_witness,
)
from omega.validation.contextual_future_fields import (
    run_contextual_future_fields_validation,
)


def test_parity_no_global_extension_has_local_sections_and_no_global_assignment() -> None:
    witness = parity_no_global_extension_witness()
    assert witness["status"] == "PASS"
    assert witness["decision_gate"]["local_contexts_nonempty"]
    assert witness["decision_gate"]["overlap_supports_agree"]
    assert witness["decision_gate"]["overlap_distributions_agree"]
    assert witness["decision_gate"]["no_global_extension"]
    assert witness["global_assignments"] == []


def test_holonomy_witnesses_keep_proxy_but_change_continuation_profile() -> None:
    result = holonomy_witnesses()
    assert result["status"] == "PASS"
    assert all(result["decision_gate"].values())
    witnesses = {witness["name"]: witness for witness in result["witnesses"]}

    lossy = witnesses["same_proxy_lossy_holonomy"]
    assert lossy["proxy_returned"]
    assert lossy["holonomy_nontrivial"]
    assert set(lossy["changed_continuation_coordinates"]) == {
        "oversight",
        "interpretability",
    }
    assert lossy["initial_continuation_thickness"] == "3"
    assert lossy["final_continuation_thickness"] == "1"

    twist = witnesses["same_proxy_orientation_twist"]
    assert twist["proxy_returned"]
    assert twist["holonomy_nontrivial"]
    assert set(twist["changed_continuation_coordinates"]) == {
        "route_left",
        "route_right",
    }
    assert twist["initial_continuation_thickness"] == twist["final_continuation_thickness"]


def test_compatibility_thickness_kernel_has_psd_and_non_psd_controls() -> None:
    result = compatibility_thickness_kernel_witnesses()
    assert result["status"] == "PASS"
    assert all(result["decision_gate"].values())

    certified = result["certified_overlap"]
    assert certified["construction"] == "certified_overlap_gram_kernel"
    assert certified["psd"]
    assert certified["rank"] > 0

    non_psd = result["non_psd_control"]
    assert non_psd["symmetric"]
    assert non_psd["nonnegative_diagonal"]
    assert not non_psd["psd"]
    assert any(minor["determinant"] == "-1" for minor in non_psd["principal_minors"])


def test_density_deformation_separates_diagonal_and_compatibility_change() -> None:
    result = density_deformation_witnesses()
    assert result["status"] == "PASS"
    assert all(result["decision_gate"].values())
    witnesses = {witness["name"]: witness for witness in result["witnesses"]}

    compatibility_damage = witnesses["diagonal_preserved_compatibility_damage"]
    assert compatibility_damage["psd_preserved"]
    assert compatibility_damage["diagonal_preserved"]
    assert not compatibility_damage["off_diagonal_preserved"]
    assert compatibility_damage["off_diagonal_changes"][0]["delta"] == "-1"

    diagonal_thinning = witnesses["diagonal_thickness_thinning_without_offdiag_change"]
    assert diagonal_thinning["psd_preserved"]
    assert not diagonal_thinning["diagonal_preserved"]
    assert diagonal_thinning["off_diagonal_preserved"]
    assert diagonal_thinning["diagonal_changes"][0]["delta"] == "-1"


def test_contextual_future_field_summary_and_runners_retain_outputs(tmp_path: Path) -> None:
    summary = contextual_future_field_summary()
    assert summary["status"] == "PASS"
    assert all(summary["decision_gate"].values())

    direct = run_contextual_future_fields(tmp_path / "direct")
    assert direct["status"] == "PASS"
    assert (tmp_path / "direct" / "summary.json").exists()
    assert (tmp_path / "direct" / "report.md").exists()

    validation = run_contextual_future_fields_validation(out_root=tmp_path / "validation")
    assert validation["status"] == "PASS"
    run_dirs = [path for path in (tmp_path / "validation").iterdir() if path.is_dir()]
    assert len(run_dirs) == 1
    assert (run_dirs[0] / "summary.json").exists()
    assert (run_dirs[0] / "report.md").exists()
