from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_reachability_different_recovery import (
    ERASE_CHANNEL,
    PRESERVE_CHANNEL,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_reachability_different_recovery_witness(tmp_path: Path) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_reachability_different_declared_recovery"
    assert result["baseline_controls_matched"] is True
    assert result["preserve_channel_exact_declared_recovery"] is True
    assert result["erase_channel_exact_declared_recovery"] is False

    comparison = read_csv(out / "baseline_comparison.csv")
    assert comparison
    assert {row["matched"] for row in comparison} == {"1"}
    assert {
        row["metric"]
        for row in comparison
    } >= {
        "edge_count",
        "global_target_support",
        "global_target_support_size",
        "per_source_reachable_count_signature",
        "per_source_entropy_bits_signature",
    }

    recovery = {row["channel_id"]: row for row in read_csv(out / "declared_recovery_by_channel.csv")}
    assert recovery[PRESERVE_CHANNEL]["recovery_status"] == "declared_recovery_pass"
    assert recovery[ERASE_CHANNEL]["recovery_status"] == "declared_recovery_fail"
    assert recovery[ERASE_CHANNEL]["ambiguous_target_observations"] == "0->{0,1};1->{0,1}"


def test_same_reachability_witness_artifacts_are_exact_and_bounded(tmp_path: Path) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    support_edges = read_csv(out / "support_edges.csv")
    assert len(support_edges) == 16
    assert {row["edge_probability"] for row in support_edges} == {"1/2"}
    assert {row["per_source_support_count"] for row in support_edges} == {"2"}

    baseline = {row["channel_id"]: row for row in read_csv(out / "reachability_baseline_by_channel.csv")}
    assert baseline[PRESERVE_CHANNEL]["global_target_support"] == "00;01;10;11"
    assert baseline[ERASE_CHANNEL]["global_target_support"] == "00;01;10;11"
    assert baseline[PRESERVE_CHANNEL]["per_source_reachable_count_signature"] == (
        baseline[ERASE_CHANNEL]["per_source_reachable_count_signature"]
    )
    assert baseline[PRESERVE_CHANNEL]["per_source_entropy_bits_signature"] == (
        baseline[ERASE_CHANNEL]["per_source_entropy_bits_signature"]
    )

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert summary["witness_status"] == "same_reachability_different_declared_recovery"
    assert "Omega validation" in summary["not_claimed"]
    assert (out / "witness_report.md").exists()
