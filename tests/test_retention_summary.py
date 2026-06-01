from __future__ import annotations

import json
from pathlib import Path

from omega.future_field_atlas.retention_summary import build_retention_bundle
from omega.future_field_atlas.util import write_csv, write_json


def test_retention_bundle_summarizes_worker_spool_run(tmp_path: Path) -> None:
    run = make_fake_coupled_run(tmp_path)

    bundle = build_retention_bundle(run_dir=run)

    assert bundle.summary["status"] == "COMPLETED"
    assert bundle.summary["pair_spool_count"] == 2
    assert bundle.summary["joint_edge_rows"] == 30
    assert bundle.summary["heaviest_pair_edge_rows"] == 20
    assert bundle.deletion_plan["recommendation"] == "delete_raw_spools_allowed"
    assert (run / "_retention_summary" / "retained_run_summary.json").exists()
    assert (run / "_retention_summary" / "retained_pair_skew.csv.gz").exists()
    assert (run / "_retention_summary" / "compact_artifacts" / "coupled_future_field_atlas_status.json").exists()
    assert (run / "coupled_pair_spool").exists()


def test_retention_bundle_can_delete_raw_spools_after_summary(tmp_path: Path) -> None:
    run = make_fake_coupled_run(tmp_path)

    bundle = build_retention_bundle(run_dir=run, delete_raw_spools=True)

    assert bundle.summary["raw_spools_deleted"] == 1
    assert not (run / "coupled_pair_spool").exists()
    deletion_record = json.loads((run / "RAW_TOPOLOGY_DELETED.json").read_text(encoding="utf-8"))
    assert deletion_record["deleted_bytes_estimate"] > 0
    assert (run / "_retention_summary" / "retained_run_summary.md").exists()


def make_fake_coupled_run(tmp_path: Path) -> Path:
    run = tmp_path / "coupled_fake"
    run.mkdir()
    write_json(
        run / "coupled_future_field_atlas_status.json",
        {
            "instrument_name": "future_field_atlas",
            "instrument_version": "test",
            "status": "COMPLETED",
            "started_utc": "2026-01-01T00:00:00Z",
            "completed_utc": "2026-01-01T00:01:00Z",
            "elapsed_seconds": 60,
            "workers": 2,
            "pair_count_requested": 2,
            "pair_count_realized": 2,
            "coupled_pairs_completed": 2,
            "coupled_pairs_failed": 0,
            "internal_cap_events": 0,
            "artifact_completeness_statuses": "complete",
            "audit_status_counts_json": {"PASS": 3, "FAIL": 0},
            "reconstruction_audit_clean_pass": 1,
            "medium_sweep_interpretation_allowed": 1,
            "raw_topology_output_mode": "worker_spool",
            "csv_output_mode": "gzip",
            "gzip_compresslevel": 1,
            "joint_edge_rows": 30,
            "joint_node_rows": 12,
            "profile_rows": 8,
            "residual_rows": 4,
            "marginal_rows": 4,
            "marginal_projection_rows": 8,
            "claim_boundary": "infrastructure only",
        },
    )
    write_json(run / "coupled_future_field_atlas_run_config.json", {"horizon_max": 4})
    write_json(run / "future_field_atlas_rebuild_contract.json", {"runner_version": "test", "git_commit": "abc", "git_dirty": 0})
    write_json(run / "coupled_future_field_atlas_manifest.json", {"manifest": "ok"})
    pair_rows = []
    for pair, edge_rows, node_rows in [("pair000", 10, 5), ("pair001", 20, 7)]:
        pair_dir = run / "coupled_pair_spool" / pair
        pair_dir.mkdir(parents=True)
        (pair_dir / "coupled_joint_frontier_edges_by_step.csv.gz").write_bytes(b"edge-bytes")
        (pair_dir / "coupled_joint_frontier_nodes_by_horizon.csv.gz").write_bytes(b"node-bytes")
        write_json(pair_dir / "pair_spool_manifest.json", {"pair_id": pair})
        pair_rows.append(
            {
                "pair_id": pair,
                "spool_dir": f"coupled_pair_spool/{pair}",
                "node_rows": node_rows,
                "edge_rows": edge_rows,
                "profile_rows": 4,
                "marginal_rows": 2,
                "residual_rows": 2,
                "marginal_projection_rows": 4,
                "internal_cap_rows": 0,
            }
        )
    write_csv(run / "coupled_pair_spool_manifest.csv.gz", pair_rows)
    write_csv(run / "coupled_joint_frontier_edges_by_step_spool_manifest.csv.gz", [{"row_count": 30}])
    write_csv(run / "coupled_joint_frontier_nodes_by_horizon_spool_manifest.csv.gz", [{"row_count": 12}])
    write_csv(
        run / "coupled_reconstruction_audit_summary.csv.gz",
        [
            {"audit_name": "profile", "status": "PASS", "checked_items": 4, "failed_items": 0, "skipped_items": 0},
            {"audit_name": "marginal", "status": "PASS", "checked_items": 4, "failed_items": 0, "skipped_items": 0},
            {"audit_name": "residual", "status": "PASS", "checked_items": 4, "failed_items": 0, "skipped_items": 0},
        ],
    )
    write_csv(
        run / "coupled_artifact_completeness_summary.csv.gz",
        [
            {"artifact_name": "nodes", "status_field": "status", "artifact_status": "complete", "row_count": 12},
            {"artifact_name": "edges", "status_field": "status", "artifact_status": "complete", "row_count": 30},
        ],
    )
    write_csv(
        run / "coupled_medium_scale_readiness_summary.csv.gz",
        [
            {
                "complete_rows": 100,
                "truncated_noninterpretable_rows": 0,
                "audits_FAIL": 0,
                "audits_NO_COMPLETE_ROWS": 0,
                "recommendation": "medium_sweep_infrastructure_ready",
            }
        ],
    )
    write_csv(
        run / "coupled_joint_vs_product_residual_by_horizon.csv.gz",
        [
            {
                "feature_status": "complete",
                "joint_support_residual_fraction": 0.0,
                "product_joint_support_count": 1,
                "coupled_joint_support_count": 1,
                "joint_support_symmetric_difference_count": 0,
            },
            {
                "feature_status": "complete",
                "joint_support_residual_fraction": 0.5,
                "product_joint_support_count": 4,
                "coupled_joint_support_count": 2,
                "joint_support_symmetric_difference_count": 2,
            },
        ],
    )
    write_csv(
        run / "coupled_marginal_retention_by_horizon.csv.gz",
        [
            {
                "feature_status": "complete",
                "A_marginal_retention_fraction": 1,
                "B_marginal_retention_fraction": 1,
                "joint_retention_fraction": 1,
                "joint_product_state_count": 1,
                "joint_coupled_state_count": 1,
            }
        ],
    )
    write_csv(
        run / "coupled_marginal_projection_delta_by_horizon.csv.gz",
        [
            {
                "feature_status": "complete",
                "projected_field": "A",
                "marginal_retention_fraction": 1,
                "marginal_symmetric_difference_fraction": 0,
                "product_missing_from_coupled_count": 0,
                "coupled_missing_from_product_count": 0,
            }
        ],
    )
    write_csv(
        run / "coupled_joint_frontier_profile_by_horizon.csv.gz",
        [
            {
                "feature_status": "complete",
                "joint_scan_mode": "coupled",
                "joint_frontier_state_count": 2,
                "joint_frontier_edge_count": 3,
                "A_marginal_state_count": 2,
                "B_marginal_state_count": 2,
                "joint_density_vs_marginal_product": 0.5,
            }
        ],
    )
    write_csv(run / "coupled_internal_frontier_cap_events.csv.gz", [])
    return run
