from __future__ import annotations

import json
from pathlib import Path

from omega.future_field_atlas.util import read_csv
from omega.stochastic_distinction_channel.registry_first_probe import run_registry_first_probe


def test_registry_first_probe_freezes_digest_before_scoring(tmp_path: Path) -> None:
    out = tmp_path / "registry_first"

    result = run_registry_first_probe(out_dir=out)

    digest = json.loads((out / "registry_digest.json").read_text(encoding="utf-8"))
    assert digest["digest_available_before_scoring"] is True
    assert result["registry_digest"] == digest["registry_digest"]

    scoring_order = read_csv(out / "scoring_order_audit.csv")
    assert scoring_order
    assert {row["status"] for row in scoring_order} == {"PASS"}
    assert scoring_order[-1]["stage_name"] == "scoring"

    scored_files = [
        "registered_recovery_by_distinction.csv",
        "existence_recovery_by_distinction.csv",
        "optimized_recovery_diagnostic.csv",
        "provenance_gap_by_distinction.csv",
        "theorem_transfer_readiness.csv",
    ]
    for name in scored_files:
        rows = read_csv(out / name)
        assert rows, name
        assert {row["registry_digest"] for row in rows} == {digest["registry_digest"]}


def test_registry_first_probe_separates_registered_existence_and_optimized(tmp_path: Path) -> None:
    out = tmp_path / "registry_first"
    run_registry_first_probe(out_dir=out)

    gap_rows = read_csv(out / "provenance_gap_by_distinction.csv")
    bad_declared = one_gap(gap_rows, "identity_channel", "reg_bad_declared_D_A_E_A")
    assert bad_declared["registered_recovery"] == "0"
    assert bad_declared["existence_recovery"] == "1"
    assert bad_declared["optimized_recovery"] == "1"
    assert bad_declared["theorem_transfer_class"] == "existence_capacity_only"
    assert bad_declared["blocked_reason"] == "declared_registry_did_not_recover"

    empty_registry = one_gap(gap_rows, "identity_channel", "reg_empty_D_joint_E_joint")
    assert empty_registry["registered_recovery"] == "0"
    assert empty_registry["existence_recovery"] == "1"
    assert empty_registry["registered_vs_existence_gap"] == "1"

    good_registry = one_gap(gap_rows, "identity_channel", "reg_declared_D_joint_E_joint")
    assert good_registry["declared_registered_recovery"] == "1"
    assert good_registry["theorem_transfer_class"] == "declared_registered_recovery_ready"

    optimized = read_csv(out / "optimized_recovery_diagnostic.csv")
    assert optimized
    assert {row["theorem_transfer_class"] for row in optimized} == {"optimized_diagnostic_only"}
    assert {row["recovery_provenance_class"] for row in optimized} == {"optimized_diagnostic"}


def test_registry_first_probe_retains_cascade_path_evidence(tmp_path: Path) -> None:
    out = tmp_path / "registry_first"
    result = run_registry_first_probe(out_dir=out)

    path_rows = read_csv(out / "path_ensemble_rows.csv")
    assert path_rows
    assert result["cascade_evidence_status"] == "path_rows_retained"

    summary = read_csv(out / "cascade_evidence_summary.csv")
    assert summary
    assert {row["cascade_evidence_status"] for row in summary} == {"path_rows_retained"}
    assert {row["theorem_transfer_eligible"] for row in summary} == {"1"}
    assert all(int(row["composite_error_mass"]) <= int(row["bound_rhs_error_mass"]) for row in summary)

    readiness = read_csv(out / "theorem_transfer_readiness.csv")
    cascade_ready = [row for row in readiness if row["readiness_axis"] == "cascade_union_bound_ready"][0]
    assert cascade_ready["status"] == "ready"
    optimized_only = [row for row in readiness if row["readiness_axis"] == "optimized_diagnostic_only"][0]
    assert optimized_only["recovery_provenance_class"] == "optimized_diagnostic"


def test_registry_first_probe_natural_weights_and_coverage_controls(tmp_path: Path) -> None:
    out = tmp_path / "registry_first"
    run_registry_first_probe(out_dir=out)

    natural = read_csv(out / "natural_weight_equivalence_audit.csv")
    assert natural
    assert {row["probability_semantics_status"] for row in natural} == {
        "natural_weight_exact_probability_equivalent"
    }
    assert {row["row_weight_total_constancy"] for row in natural} == {"constant"}

    coverage = read_csv(out / "decoder_registry_coverage_audit.csv")
    empty = [row for row in coverage if row["registry_id"] == "reg_empty_D_joint_E_joint"][0]
    assert empty["coverage_status"] == "empty_registry_control"

    bundle = json.loads((out / "registry_first_formal_consumption_bundle.json").read_text(encoding="utf-8"))
    assert bundle["overall_status"] == "registry_first_theorem_transfer_ready"


def test_registry_first_probe_medium_panel_expands_gap_surface(tmp_path: Path) -> None:
    out = tmp_path / "registry_first_medium"

    result = run_registry_first_probe(out_dir=out, panel="medium")

    assert result["panel"] == "medium"
    assert int(result["channel_count"]) > 5

    manifest = json.loads((out / "registry_first_probe_manifest.json").read_text(encoding="utf-8"))
    assert manifest["panel"] == "medium"
    assert manifest["row_counts"]["channel_manifest.csv"] == result["channel_count"]

    channels = read_csv(out / "channel_manifest.csv")
    channel_ids = {row["channel_id"] for row in channels}
    assert "swap_bits_channel" in channel_ids
    assert "joint_cycle_channel" in channel_ids
    assert "independent_bit_noise_81_9_9_1_channel" in channel_ids

    gap_rows = read_csv(out / "provenance_gap_by_distinction.csv")
    assert len(gap_rows) > 35
    swap_a = one_gap(gap_rows, "swap_bits_channel", "reg_declared_D_A_E_A")
    assert swap_a["registered_recovery"] == "0"
    assert swap_a["existence_recovery"] == "0"
    assert swap_a["optimized_recovery"] == "1"
    assert swap_a["theorem_transfer_class"] == "optimized_diagnostic_only"

    readiness = read_csv(out / "theorem_transfer_readiness.csv")
    optimized = [row for row in readiness if row["readiness_axis"] == "optimized_diagnostic_only"][0]
    assert optimized["status"] == "ready"


def one_gap(rows: list[dict[str, str]], channel_id: str, registry_id: str) -> dict[str, str]:
    matches = [
        row for row in rows if row["channel_id"] == channel_id and row["registry_id"] == registry_id
    ]
    assert len(matches) == 1
    return matches[0]
