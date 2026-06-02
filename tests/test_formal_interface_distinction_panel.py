from __future__ import annotations

import json
from pathlib import Path

from omega.future_field_atlas.formal_interface_distinction_panel import (
    LabeledRun,
    Thresholds,
    build_panel,
)
from omega.future_field_atlas.util import read_csv, write_csv, write_json


def test_formal_interface_panel_emits_missing_cells_and_measures(tmp_path: Path) -> None:
    product = write_retained_run(
        tmp_path / "product",
        joint_selection_family="product",
        coupling_strength=0.0,
        operator_family="rank_boundary_mismatch_penalized_joint_selector",
        operator_id="product-op",
        rows=[
            metric_row("pair005", 64, residual=0.0, a_ret=1.0, b_ret=1.0, joint_ret=1.0, joint_count=100, a_count=10, b_count=10),
            metric_row("pair000", 64, residual=0.0, a_ret=1.0, b_ret=1.0, joint_ret=1.0, joint_count=100, a_count=10, b_count=10),
        ],
    )
    rank = write_retained_run(
        tmp_path / "rank",
        joint_selection_family="rank_order_boundary",
        coupling_strength=0.0,
        operator_family="rank_order_boundary_alignment_joint_selector",
        operator_id="rank-op",
        rows=[
            metric_row("pair005", 64, residual=0.72, a_ret=1.0, b_ret=1.0, joint_ret=0.32, joint_count=32, a_count=10, b_count=10),
            metric_row("pair000", 64, residual=0.08, a_ret=1.0, b_ret=1.0, joint_ret=0.92, joint_count=92, a_count=10, b_count=10),
        ],
    )

    out = tmp_path / "panel"
    manifest = build_panel(
        out_dir=out,
        runs=[
            LabeledRun("product_selector", product),
            LabeledRun("rank_order_boundary", rank),
        ],
        pairs=["pair005", "pair000"],
        operator_labels=["product_selector", "rank_order_boundary", "scalar_mismatch_0.020"],
        thresholds=Thresholds(),
        write_report=True,
    )

    assert manifest["cell_count_requested"] == 6
    assert manifest["cell_count_available"] == 4
    missing = read_csv(out / "formal_interface_missing_cells.csv")
    assert {(row["pair_id"], row["operator_label"], row["cell_status"]) for row in missing} == {
        ("pair005", "scalar_mismatch_0.020", "missing_not_run"),
        ("pair000", "scalar_mismatch_0.020", "missing_not_run"),
    }
    retention = read_csv(out / "joint_vs_marginal_distinction_retention.csv")
    final_pair005_rank = [
        row
        for row in retention
        if row["pair_id"] == "pair005" and row["operator_label"] == "rank_order_boundary"
    ][0]
    assert final_pair005_rank["signature_class"] == "marginal_preserving_joint_restrictive"
    assert float(final_pair005_rank["joint_density_vs_marginal_product"]) == 0.32
    deltas = read_csv(out / "operator_reference_delta_by_horizon.csv")
    residual_delta = [
        row
        for row in deltas
        if row["comparison_id"] == "rank_order_boundary_vs_product_selector"
        and row["pair_id"] == "pair005"
        and row["metric_name"] == "joint_support_residual_fraction"
    ][0]
    assert residual_delta["both_cells_available"] == "1"
    assert float(residual_delta["delta"]) == 0.72
    assert "not a proto-valuer" in (out / "formal_interface_report.md").read_text(encoding="utf-8")


def test_formal_interface_panel_blocks_failed_gates(tmp_path: Path) -> None:
    blocked = write_retained_run(
        tmp_path / "blocked",
        joint_selection_family="rank_order_boundary",
        coupling_strength=0.0,
        operator_family="rank_order_boundary_alignment_joint_selector",
        operator_id="rank-op",
        rows=[
            metric_row("pair005", 64, residual=0.72, a_ret=1.0, b_ret=1.0, joint_ret=0.32, joint_count=32, a_count=10, b_count=10),
        ],
        internal_cap_events=1,
    )

    out = tmp_path / "panel"
    build_panel(
        out_dir=out,
        runs=[LabeledRun("rank_order_boundary", blocked)],
        pairs=["pair005"],
        operator_labels=["rank_order_boundary"],
        thresholds=Thresholds(),
        write_report=False,
    )

    missing = read_csv(out / "formal_interface_missing_cells.csv")
    assert missing[0]["cell_status"] == "blocked_by_gate"
    measures = read_csv(out / "distinction_measure_by_horizon.csv")
    assert {row["binary_status"] for row in measures} == {"not_available_from_retained_inputs"}


def write_retained_run(
    path: Path,
    *,
    joint_selection_family: str,
    coupling_strength: float,
    operator_family: str,
    operator_id: str,
    rows: list[dict[str, object]],
    internal_cap_events: int = 0,
) -> Path:
    path.mkdir(parents=True)
    write_json(
        path / "coupled_future_field_atlas_status.json",
        {
            "status": "COMPLETED",
            "coupled_pairs_failed": 0,
            "internal_cap_events": internal_cap_events,
            "medium_sweep_interpretation_allowed": 1,
        },
    )
    write_json(
        path / "coupled_future_field_atlas_run_config.json",
        {
            "joint_selection_family": joint_selection_family,
            "coupling_strength": coupling_strength,
        },
    )
    write_csv(
        path / "coupled_artifact_completeness_summary.csv.gz",
        [{"artifact_name": "compact", "artifact_status": "complete", "row_count": len(rows)}],
    )
    write_csv(
        path / "coupled_reconstruction_audit_summary.csv.gz",
        [{"audit_name": "compact_reconstructs", "status": "PASS", "checked_items": len(rows), "failed_items": 0, "skipped_items": 0}],
    )
    write_csv(
        path / "coupled_medium_scale_readiness_summary.csv.gz",
        [{"medium_sweep_interpretation_allowed": 1}],
    )
    write_csv(
        path / "coupled_operator_manifest.csv.gz",
        [
            {
                "coupled_operator_id": operator_id,
                "coupled_operator_family": operator_family,
                "joint_selection_family": joint_selection_family,
                "coupling_strength": coupling_strength,
                "joint_effective_out_degree": 4,
            }
        ],
    )
    write_csv(
        path / "coupled_condition_manifest.csv.gz",
        [
            {
                "pair_id": row["pair_id"],
                "joint_selection_family": joint_selection_family,
                "coupling_strength": coupling_strength,
            }
            for row in rows
        ],
    )
    write_csv(
        path / "coupled_joint_vs_product_residual_by_horizon.csv.gz",
        [
            {
                "pair_id": row["pair_id"],
                "horizon": row["horizon"],
                "feature_status": "complete",
                "product_joint_support_count": row["product_joint_support_count"],
                "coupled_joint_support_count": row["coupled_joint_support_count"],
                "joint_support_symmetric_difference_count": row["joint_support_symmetric_difference_count"],
                "joint_support_residual_fraction": row["joint_support_residual_fraction"],
            }
            for row in rows
        ],
    )
    write_csv(
        path / "coupled_marginal_retention_by_horizon.csv.gz",
        [
            {
                "pair_id": row["pair_id"],
                "horizon": row["horizon"],
                "feature_status": "complete",
                "A_product_marginal_count": row["A_product_marginal_count"],
                "A_coupled_marginal_count": row["A_coupled_marginal_count"],
                "A_marginal_retention_fraction": row["A_marginal_retention_fraction"],
                "B_product_marginal_count": row["B_product_marginal_count"],
                "B_coupled_marginal_count": row["B_coupled_marginal_count"],
                "B_marginal_retention_fraction": row["B_marginal_retention_fraction"],
                "joint_product_state_count": row["joint_product_state_count"],
                "joint_coupled_state_count": row["joint_coupled_state_count"],
                "joint_retention_fraction": row["joint_retention_fraction"],
            }
            for row in rows
        ],
    )
    return path


def metric_row(
    pair_id: str,
    horizon: int,
    *,
    residual: float,
    a_ret: float,
    b_ret: float,
    joint_ret: float,
    joint_count: int,
    a_count: int,
    b_count: int,
) -> dict[str, object]:
    full_pair = f"{pair_id}__synthetic"
    product_count = a_count * b_count
    return {
        "pair_id": full_pair,
        "horizon": horizon,
        "product_joint_support_count": product_count,
        "coupled_joint_support_count": joint_count,
        "joint_support_symmetric_difference_count": int(product_count * residual),
        "joint_support_residual_fraction": residual,
        "A_product_marginal_count": a_count,
        "A_coupled_marginal_count": a_count,
        "A_marginal_retention_fraction": a_ret,
        "B_product_marginal_count": b_count,
        "B_coupled_marginal_count": b_count,
        "B_marginal_retention_fraction": b_ret,
        "joint_product_state_count": product_count,
        "joint_coupled_state_count": joint_count,
        "joint_retention_fraction": joint_ret,
    }
