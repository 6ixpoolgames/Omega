from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_compression_score_different_merge_soundness import (
    SOUND_ABSTRACTION,
    UNSOUND_ABSTRACTION,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_compression_score_different_merge_soundness_witness(tmp_path: Path) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_compression_score_different_merge_soundness"
    assert result["compression_scores_matched"] is True
    assert result["sound_abstraction_merge_sound"] is True
    assert result["unsound_abstraction_merge_sound"] is False
    assert result["sound_abstraction_unsound_merge_count"] == 0
    assert result["unsound_abstraction_unsound_merge_count"] == 2

    comparison = read_csv(out / "compression_comparison.csv")
    assert comparison
    assert {row["matched"] for row in comparison} == {"1"}


def test_unsound_abstraction_merges_blocked_pairs(tmp_path: Path) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    audit_rows = read_csv(out / "merge_soundness_audit.csv")
    unsound_failures = [
        row for row in audit_rows
        if row["abstraction_id"] == UNSOUND_ABSTRACTION and row["unsound_merge"] == "1"
    ]
    sound_failures = [
        row for row in audit_rows
        if row["abstraction_id"] == SOUND_ABSTRACTION and row["unsound_merge"] == "1"
    ]

    assert not sound_failures
    assert {
        (row["left_fragment"], row["right_fragment"])
        for row in unsound_failures
    } == {("00", "10"), ("01", "11")}
    assert {row["audit_status"] for row in unsound_failures} == {"FAIL"}

    profile = {
        (row["left_fragment"], row["right_fragment"]): row
        for row in read_csv(out / "exact_profile_pairs.csv")
    }
    assert profile[("00", "10")]["exact_blocks_merge"] == "1"
    assert profile[("01", "11")]["exact_blocks_merge"] == "1"

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert "optimal compression" in summary["not_claimed"]
