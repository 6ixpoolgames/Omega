from __future__ import annotations

import json
from pathlib import Path

from omega.baseline_witnesses.same_coarse_bisimulation_different_consequence_profile import (
    D_PANEL,
    N_PANEL,
    run_witness,
)
from omega.future_field_atlas.util import read_csv


def test_same_coarse_bisimulation_different_consequence_profile_witness(
    tmp_path: Path,
) -> None:
    out = tmp_path / "witness"

    result = run_witness(out_dir=out)

    assert result["witness_status"] == "same_coarse_bisimulation_different_consequence_profile"
    assert result["baseline_controls_matched"] is True
    assert result["expanded_profile_counts_matched"] is True
    assert result["expanded_profile_signatures_differ"] is True
    assert result["declared_d_allowed_pair_signature"] == "00,01;10,11"
    assert result["declared_n_allowed_pair_signature"] == "00,10;01,11"

    comparison = read_csv(out / "baseline_comparison.csv")
    assert comparison
    assert {row["matched"] for row in comparison} == {"1"}
    assert {
        row["metric"]
        for row in comparison
    } == {
        "coarse_block_count",
        "coarse_block_size_signature",
        "coarse_partition_signature",
        "expanded_allowed_pair_count",
        "expanded_blocked_pair_count",
        "expanded_pair_count",
        "state_count",
        "transition_edge_count",
    }


def test_expanded_panel_declaration_changes_exact_profile(tmp_path: Path) -> None:
    out = tmp_path / "witness"
    run_witness(out_dir=out)

    coarse_rows = read_csv(out / "coarse_partition.csv")
    assert {
        row["coarse_partition_signature"]
        for row in coarse_rows
    } == {"coarse_all_states:00;01;10;11"}
    assert {
        row["coarse_block_size_signature"]
        for row in coarse_rows
    } == {"4"}

    profile_rows = read_csv(out / "exact_profile_pairs.csv")
    by_panel = {
        panel: [
            row for row in profile_rows
            if row["expanded_panel_id"] == panel
        ]
        for panel in (D_PANEL, N_PANEL)
    }
    assert {len(rows) for rows in by_panel.values()} == {6}
    assert {
        sum(1 for row in rows if row["exact_allows_merge"] == "1")
        for rows in by_panel.values()
    } == {2}
    assert {
        tuple(
            (row["left_state"], row["right_state"])
            for row in rows
            if row["exact_allows_merge"] == "1"
        )
        for rows in by_panel.values()
    } == {
        (("00", "01"), ("10", "11")),
        (("00", "10"), ("01", "11")),
    }

    profile_difference = read_csv(out / "profile_difference.csv")
    assert profile_difference
    assert {row["matched"] for row in profile_difference} == {"0"}

    summary = json.loads((out / "witness_summary.json").read_text(encoding="utf-8"))
    assert summary["witness_status"] == "same_coarse_bisimulation_different_consequence_profile"
    assert "arbitrary post-hoc panel validity" in summary["not_claimed"]
    assert "bisimulation novelty" in summary["not_claimed"]
    assert (out / "witness_report.md").exists()
