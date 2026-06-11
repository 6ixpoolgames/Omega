from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_control_reach_different_declared_recovery import (
    DECLARED_SYSTEM,
    NUISANCE_SYSTEM,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_control_reach_different_declared_recovery_witness(
    tmp_path: Path,
) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_control_reach_different_declared_recovery"
    assert result["reach_controls_hold"] is True
    assert result["all_expected_relations_hold"] is True
    assert result["global_target_support"] == "00;01;10;11"
    assert result["per_source_reachable_target_count_signature"] == "00:2;01:2;10:2;11:2"
    assert result["declared_system_exact_declared_recovery"] is True
    assert result["nuisance_system_exact_declared_recovery"] is False

    comparison = read_csv(out / "baseline_comparison.csv")
    assert comparison
    assert {row["relation_holds"] for row in comparison} == {"1"}
    assert {row["metric"] for row in comparison} == {
        "source_count",
        "control_count",
        "transition_edge_count",
        "deterministic_transition",
        "global_target_support_size",
        "global_target_support",
        "per_source_reachable_target_count_signature",
        "target_count_by_control_signature",
        "target_control_bits_by_control_signature",
        "declared_recovery_signature",
    }


def test_control_reach_summary_does_not_license_declared_recovery(
    tmp_path: Path,
) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    reach = {row["system_id"]: row for row in read_csv(out / "control_reach_by_system.csv")}
    assert reach[DECLARED_SYSTEM]["global_target_support"] == "00;01;10;11"
    assert reach[NUISANCE_SYSTEM]["global_target_support"] == "00;01;10;11"
    assert reach[DECLARED_SYSTEM]["per_source_reachable_target_count_signature"] == (
        reach[NUISANCE_SYSTEM]["per_source_reachable_target_count_signature"]
    )
    assert reach[DECLARED_SYSTEM]["target_count_by_control_signature"] == (
        reach[NUISANCE_SYSTEM]["target_count_by_control_signature"]
    )
    assert reach[DECLARED_SYSTEM]["target_control_bits_by_control_signature"] == (
        "drive_0:0;drive_1:1"
    )

    recovery = {
        row["system_id"]: row for row in read_csv(out / "declared_recovery_by_system.csv")
    }
    assert recovery[DECLARED_SYSTEM]["recovery_status"] == "declared_recovery_pass"
    assert recovery[NUISANCE_SYSTEM]["recovery_status"] == "declared_recovery_fail"
    assert recovery[NUISANCE_SYSTEM]["ambiguous_target_observations"] == "0->{0,1};1->{0,1}"

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert summary["witness_status"] == "same_control_reach_different_declared_recovery"
    assert "full controllability" in summary["not_claimed"]
    assert "control synthesis" in summary["not_claimed"]
