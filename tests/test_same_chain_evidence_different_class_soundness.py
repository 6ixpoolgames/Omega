from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_chain_evidence_different_class_soundness import (
    INVALID_CLASS,
    VALID_CLASS,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_chain_evidence_different_class_soundness_witness(tmp_path: Path) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_chain_evidence_different_class_soundness"
    assert result["baseline_controls_matched"] is True
    assert result["valid_class_declared_chain_edges_pass"] is True
    assert result["invalid_class_declared_chain_edges_pass"] is True
    assert result["valid_class_sound"] is True
    assert result["invalid_class_sound"] is False
    assert result["valid_class_unsound_pair_count"] == 0
    assert result["invalid_class_unsound_pair_count"] == 1

    comparison = read_csv(out / "baseline_comparison.csv")
    assert comparison
    assert {row["matched"] for row in comparison} == {"1"}
    assert {
        row["metric"]
        for row in comparison
    } == {
        "member_count",
        "declared_chain_edge_count",
        "internal_pair_count",
        "chain_connected",
    }


def test_chain_evidence_does_not_license_full_class_soundness(tmp_path: Path) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    chain_edges = read_csv(out / "declared_chain_edges.csv")
    assert {row["chain_edge_status"] for row in chain_edges} == {"PASS"}
    assert {
        (row["proposed_class_id"], row["left_fragment"], row["right_fragment"])
        for row in chain_edges
    } == {
        (VALID_CLASS, "v0", "v1"),
        (VALID_CLASS, "v1", "v2"),
        (INVALID_CLASS, "i0", "i1"),
        (INVALID_CLASS, "i1", "i2"),
    }

    soundness_rows = read_csv(out / "class_soundness_audit.csv")
    invalid_failures = [
        row for row in soundness_rows
        if row["proposed_class_id"] == INVALID_CLASS
        and row["class_soundness_status"] == "FAIL"
    ]
    valid_failures = [
        row for row in soundness_rows
        if row["proposed_class_id"] == VALID_CLASS
        and row["class_soundness_status"] == "FAIL"
    ]

    assert not valid_failures
    assert [
        (row["left_fragment"], row["right_fragment"])
        for row in invalid_failures
    ] == [("i0", "i2")]

    profile = {
        (row["left_fragment"], row["right_fragment"]): row
        for row in read_csv(out / "exact_profile_pairs.csv")
    }
    assert profile[("i0", "i2")]["exact_blocks_merge"] == "1"
    assert profile[("i0", "i1")]["exact_allows_merge"] == "1"
    assert profile[("i1", "i2")]["exact_allows_merge"] == "1"

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert summary["witness_status"] == "same_chain_evidence_different_class_soundness"
    assert "transitivity" in summary["not_claimed"]
    assert "cluster validity" in summary["not_claimed"]
    assert (out / "witness_report.md").exists()
