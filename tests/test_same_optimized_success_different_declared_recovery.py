from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_optimized_success_different_declared_recovery import (
    DECLARED_CHANNEL,
    SHIFTED_CHANNEL,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_optimized_success_different_declared_recovery_witness(tmp_path: Path) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_optimized_success_different_declared_recovery"
    assert result["baseline_controls_matched"] is True
    assert result["same_optimized_success"] is True
    assert result["declared_channel_exact_declared_recovery"] is True
    assert result["shifted_channel_exact_declared_recovery"] is False
    assert result["declared_channel_exact_optimized_recovery"] is True
    assert result["shifted_channel_exact_optimized_recovery"] is True
    assert result["declared_channel_best_observation_id"] == "O_first"
    assert result["shifted_channel_best_observation_id"] == "O_second"

    comparison = read_csv(out / "baseline_comparison.csv")
    assert comparison
    assert {row["matched"] for row in comparison} == {"1"}


def test_optimized_success_does_not_license_declared_recovery(tmp_path: Path) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    declared = {row["channel_id"]: row for row in read_csv(out / "declared_recovery_by_channel.csv")}
    optimized = {row["channel_id"]: row for row in read_csv(out / "optimized_recovery_by_channel.csv")}

    assert declared[DECLARED_CHANNEL]["recovery_status"] == "declared_recovery_pass"
    assert declared[SHIFTED_CHANNEL]["recovery_status"] == "declared_recovery_fail"
    assert declared[SHIFTED_CHANNEL]["ambiguous_target_observations"] == "0->{0,1};1->{0,1}"

    assert optimized[DECLARED_CHANNEL]["optimized_status"] == "optimized_recovery_pass"
    assert optimized[SHIFTED_CHANNEL]["optimized_status"] == "optimized_recovery_pass"
    assert optimized[DECLARED_CHANNEL]["best_observation_id"] == "O_first"
    assert optimized[SHIFTED_CHANNEL]["best_observation_id"] == "O_second"

    panel = {
        (row["channel_id"], row["candidate_target_observation_id"]): row
        for row in read_csv(out / "optimized_panel_recovery_by_observation.csv")
    }
    assert panel[(DECLARED_CHANNEL, "O_first")]["exact_recovery"] == "1"
    assert panel[(DECLARED_CHANNEL, "O_second")]["exact_recovery"] == "0"
    assert panel[(SHIFTED_CHANNEL, "O_first")]["exact_recovery"] == "0"
    assert panel[(SHIFTED_CHANNEL, "O_second")]["exact_recovery"] == "1"

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert summary["witness_status"] == "same_optimized_success_different_declared_recovery"
    assert "semantic recovery" in summary["not_claimed"]
