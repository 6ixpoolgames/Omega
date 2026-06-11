from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_frontier_morphology_different_loss_profile import (
    FLIP_V_CHANNEL,
    PRESERVE_V_CHANNEL,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_frontier_morphology_different_loss_profile_witness(tmp_path: Path) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_frontier_morphology_different_declared_loss_profile"
    assert result["morphology_controls_hold"] is True
    assert result["loss_profile_differs"] is True
    assert result["all_expected_relations_hold"] is True
    assert result["preserve_loss_signature"] == "10:0;11:0"
    assert result["flip_loss_signature"] == "10:1;11:1"
    assert result["preserve_loss_count"] == 0
    assert result["flip_loss_count"] == 2

    comparison = read_csv(out / "baseline_comparison.csv")
    assert comparison
    assert {row["relation_holds"] for row in comparison} == {"1"}


def test_frontier_morphology_matches_while_declared_loss_differs(tmp_path: Path) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    morphology = {row["channel_id"]: row for row in read_csv(out / "frontier_morphology_by_channel.csv")}
    assert morphology[PRESERVE_V_CHANNEL]["global_target_support"] == "00;01;10;11"
    assert morphology[FLIP_V_CHANNEL]["global_target_support"] == "00;01;10;11"
    assert morphology[PRESERVE_V_CHANNEL]["frontier_morphology_signature"] == (
        morphology[FLIP_V_CHANNEL]["frontier_morphology_signature"]
    )
    assert morphology[PRESERVE_V_CHANNEL]["viable_target_count_multiset"] == "0;0;2;2"
    assert morphology[FLIP_V_CHANNEL]["viable_target_count_multiset"] == "0;0;2;2"

    loss_rows = read_csv(out / "loss_profile_by_source.csv")
    loss = {
        (row["channel_id"], row["source_state"]): row
        for row in loss_rows
        if row["source_declared_viable"] == "1"
    }
    assert loss[(PRESERVE_V_CHANNEL, "10")]["declared_horizon_loss"] == "0"
    assert loss[(PRESERVE_V_CHANNEL, "11")]["declared_horizon_loss"] == "0"
    assert loss[(FLIP_V_CHANNEL, "10")]["declared_horizon_loss"] == "1"
    assert loss[(FLIP_V_CHANNEL, "11")]["declared_horizon_loss"] == "1"

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert "real irreversibility" in summary["not_claimed"]
