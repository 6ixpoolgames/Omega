"""Compact retention summaries for Future Field Atlas run directories.

The runner emits reconstructible raw topology. This utility is the local data
retention layer: it records the small facts needed to audit a run before raw
pair spools are archived or deleted.
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Iterable

from .util import read_csv, utc_now, write_csv, write_json


COMPACT_ARTIFACTS = {
    "coupled_future_field_atlas_status.json",
    "coupled_future_field_atlas_run_config.json",
    "future_field_atlas_rebuild_contract.json",
    "coupled_future_field_atlas_manifest.json",
    "coupled_pair_spool_manifest.csv.gz",
    "coupled_joint_frontier_nodes_by_horizon_spool_manifest.csv.gz",
    "coupled_joint_frontier_edges_by_step_spool_manifest.csv.gz",
    "coupled_joint_frontier_profile_by_horizon.csv.gz",
    "coupled_joint_vs_product_residual_by_horizon.csv.gz",
    "coupled_marginal_retention_by_horizon.csv.gz",
    "coupled_marginal_projection_delta_by_horizon.csv.gz",
    "coupled_reconstruction_audit_summary.csv.gz",
    "coupled_artifact_completeness_summary.csv.gz",
    "coupled_medium_scale_readiness_summary.csv.gz",
    "coupled_internal_frontier_cap_events.csv.gz",
}


RAW_SPOOL_DIR = "coupled_pair_spool"


@dataclass(frozen=True)
class RetentionBundle:
    run_dir: Path
    bundle_dir: Path
    summary: dict[str, object]
    deletion_plan: dict[str, object]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize and optionally prune Future Field Atlas run data.")
    parser.add_argument("--run", type=Path, required=True, help="Run directory to summarize.")
    parser.add_argument(
        "--bundle-out",
        type=Path,
        default=None,
        help="Output directory for compact bundle. Default: <run>/_retention_summary.",
    )
    parser.add_argument(
        "--delete-raw-spools",
        action="store_true",
        help="Delete worker-spooled raw topology after the compact bundle is written.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow raw-spool deletion even when retention recommendation is not delete_raw_spools_allowed.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bundle = build_retention_bundle(
        run_dir=args.run,
        bundle_out=args.bundle_out,
        delete_raw_spools=bool(args.delete_raw_spools),
        force=bool(args.force),
    )
    print(json.dumps(bundle.summary, indent=2, sort_keys=True, default=str))


def build_retention_bundle(
    *,
    run_dir: Path,
    bundle_out: Path | None = None,
    delete_raw_spools: bool = False,
    force: bool = False,
) -> RetentionBundle:
    run_dir = run_dir.resolve()
    if not run_dir.exists() or not run_dir.is_dir():
        raise NotADirectoryError(run_dir)
    bundle_dir = (bundle_out or (run_dir / "_retention_summary")).resolve()
    if not is_relative_to(bundle_dir, run_dir) and bundle_out is None:
        raise ValueError(f"refusing default bundle outside run directory: {bundle_dir}")
    bundle_dir.mkdir(parents=True, exist_ok=True)

    status = read_json(run_dir / "coupled_future_field_atlas_status.json")
    config = read_json(run_dir / "coupled_future_field_atlas_run_config.json")
    rebuild = read_json(run_dir / "future_field_atlas_rebuild_contract.json")
    spool_rows = read_csv(run_dir / "coupled_pair_spool_manifest.csv.gz")
    artifact_rows = read_csv(run_dir / "coupled_artifact_completeness_summary.csv.gz")
    audit_rows = read_csv(run_dir / "coupled_reconstruction_audit_summary.csv.gz")
    readiness_rows = read_csv(run_dir / "coupled_medium_scale_readiness_summary.csv.gz")

    pair_skew_rows = pair_skew_summary(run_dir, spool_rows)
    metric_rows = metric_summary_rows(run_dir)
    inventory_rows = artifact_inventory(run_dir)
    summary = run_summary(
        run_dir=run_dir,
        bundle_dir=bundle_dir,
        status=status,
        config=config,
        rebuild=rebuild,
        spool_rows=spool_rows,
        pair_skew_rows=pair_skew_rows,
        artifact_rows=artifact_rows,
        audit_rows=audit_rows,
        readiness_rows=readiness_rows,
        inventory_rows=inventory_rows,
        metric_rows=metric_rows,
    )
    deletion_plan = raw_deletion_plan(run_dir, status=status, readiness_rows=readiness_rows)
    summary["deletion_recommendation"] = deletion_plan["recommendation"]
    summary["raw_delete_candidate_bytes"] = deletion_plan["raw_delete_candidate_bytes"]
    summary["raw_delete_candidate_gib"] = deletion_plan["raw_delete_candidate_gib"]

    write_json(bundle_dir / "retained_run_summary.json", summary)
    write_json(bundle_dir / "retained_deletion_plan.json", deletion_plan)
    write_csv(bundle_dir / "retained_pair_skew.csv.gz", pair_skew_rows)
    write_csv(bundle_dir / "retained_metric_summary.csv.gz", metric_rows)
    write_csv(bundle_dir / "retained_artifact_inventory.csv.gz", inventory_rows)
    copy_compact_artifacts(run_dir, bundle_dir)
    write_markdown(bundle_dir / "retained_run_summary.md", summary, deletion_plan)

    if delete_raw_spools:
        allowed = deletion_plan["recommendation"] == "delete_raw_spools_allowed"
        if not allowed and not force:
            raise RuntimeError(
                "raw spool deletion blocked by recommendation; rerun with --force if this is intentional"
            )
        delete_raw_paths(run_dir, deletion_plan)
        deletion_record = {
            "deleted_utc": utc_now(),
            "deleted_paths": deletion_plan["raw_delete_candidate_paths"],
            "deleted_bytes_estimate": deletion_plan["raw_delete_candidate_bytes"],
            "summary_bundle": str(bundle_dir),
        }
        write_json(run_dir / "RAW_TOPOLOGY_DELETED.json", deletion_record)
        summary["raw_spools_deleted"] = 1
        write_json(bundle_dir / "retained_run_summary.json", summary)
        write_markdown(bundle_dir / "retained_run_summary.md", summary, deletion_plan)
    return RetentionBundle(run_dir=run_dir, bundle_dir=bundle_dir, summary=summary, deletion_plan=deletion_plan)


def run_summary(
    *,
    run_dir: Path,
    bundle_dir: Path,
    status: dict[str, object],
    config: dict[str, object],
    rebuild: dict[str, object],
    spool_rows: list[dict[str, object]],
    pair_skew_rows: list[dict[str, object]],
    artifact_rows: list[dict[str, object]],
    audit_rows: list[dict[str, object]],
    readiness_rows: list[dict[str, object]],
    inventory_rows: list[dict[str, object]],
    metric_rows: list[dict[str, object]],
) -> dict[str, object]:
    readiness = readiness_rows[0] if readiness_rows else {}
    git = rebuild.get("git") if isinstance(rebuild.get("git"), dict) else {}
    total_size = sum(int_value(row.get("size_bytes")) for row in inventory_rows)
    edge_rows = int_value(status.get("joint_edge_rows"))
    node_rows = int_value(status.get("joint_node_rows"))
    pair_count = len(spool_rows)
    heaviest_pair = max(pair_skew_rows, key=lambda row: int_value(row.get("edge_rows")), default={})
    return {
        "created_utc": utc_now(),
        "run_dir": str(run_dir),
        "bundle_dir": str(bundle_dir),
        "run_name": run_dir.name,
        "instrument_name": status.get("instrument_name", ""),
        "instrument_version": status.get("instrument_version", ""),
        "runner_version": rebuild.get("runner_version", ""),
        "source_git_commit": git.get("source_commit", rebuild.get("git_commit", "")),
        "source_git_branch": git.get("source_branch", rebuild.get("git_branch", "")),
        "source_git_dirty": git.get("source_dirty", rebuild.get("git_dirty", "")),
        "status": status.get("status", ""),
        "started_utc": status.get("started_utc", ""),
        "completed_utc": status.get("completed_utc", ""),
        "elapsed_seconds": float_value(status.get("elapsed_seconds")),
        "workers": int_value(status.get("workers")),
        "horizon_max": int_value(config.get("horizon_max")),
        "pair_count_requested": int_value(status.get("pair_count_requested")),
        "pair_count_realized": int_value(status.get("pair_count_realized")),
        "coupled_pairs_completed": int_value(status.get("coupled_pairs_completed")),
        "coupled_pairs_failed": int_value(status.get("coupled_pairs_failed")),
        "internal_cap_events": int_value(status.get("internal_cap_events")),
        "artifact_completeness_statuses": status.get("artifact_completeness_statuses", ""),
        "audit_status_counts_json": status.get("audit_status_counts_json", {}),
        "reconstruction_audit_clean_pass": int_value(status.get("reconstruction_audit_clean_pass")),
        "medium_sweep_interpretation_allowed": int_value(status.get("medium_sweep_interpretation_allowed")),
        "raw_topology_output_mode": status.get("raw_topology_output_mode", config.get("raw_topology_output_mode", "")),
        "csv_output_mode": status.get("csv_output_mode", config.get("csv_output_mode", "")),
        "gzip_compresslevel": int_value(status.get("gzip_compresslevel", config.get("gzip_compresslevel"))),
        "joint_edge_rows": edge_rows,
        "joint_node_rows": node_rows,
        "profile_rows": int_value(status.get("profile_rows")),
        "residual_rows": int_value(status.get("residual_rows")),
        "marginal_rows": int_value(status.get("marginal_rows")),
        "marginal_projection_rows": int_value(status.get("marginal_projection_rows")),
        "pair_spool_count": pair_count,
        "heaviest_pair_id": heaviest_pair.get("pair_id", ""),
        "heaviest_pair_edge_rows": int_value(heaviest_pair.get("edge_rows")),
        "heaviest_pair_edge_share": float_value(heaviest_pair.get("edge_row_share")),
        "total_output_size_bytes": total_size,
        "total_output_size_gib": round(total_size / (1024**3), 6),
        "complete_rows": int_value(readiness.get("complete_rows")),
        "truncated_noninterpretable_rows": int_value(readiness.get("truncated_noninterpretable_rows")),
        "readiness_recommendation": readiness.get("recommendation", ""),
        "claim_boundary": status.get("claim_boundary", ""),
        "compact_artifact_count": len([row for row in inventory_rows if int_value(row.get("compact_retention_artifact")) == 1]),
        "metric_summary_rows": len(metric_rows),
        "artifact_summary_rows": len(artifact_rows),
        "audit_summary_rows": len(audit_rows),
    }


def pair_skew_summary(run_dir: Path, spool_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    total_edges = sum(int_value(row.get("edge_rows")) for row in spool_rows)
    total_nodes = sum(int_value(row.get("node_rows")) for row in spool_rows)
    rows: list[dict[str, object]] = []
    for row in spool_rows:
        spool_rel = Path(str(row.get("spool_dir", "")))
        spool_dir = run_dir / spool_rel
        size_bytes = directory_size_bytes(spool_dir) if spool_dir.exists() else 0
        edge_rows = int_value(row.get("edge_rows"))
        node_rows = int_value(row.get("node_rows"))
        rows.append(
            {
                "pair_id": row.get("pair_id", ""),
                "spool_dir": row.get("spool_dir", ""),
                "node_rows": node_rows,
                "edge_rows": edge_rows,
                "node_row_share": safe_fraction(node_rows, total_nodes),
                "edge_row_share": safe_fraction(edge_rows, total_edges),
                "spool_size_bytes": size_bytes,
                "spool_size_gib": round(size_bytes / (1024**3), 6),
                "internal_cap_rows": int_value(row.get("internal_cap_rows")),
            }
        )
    return sorted(rows, key=lambda item: int_value(item.get("edge_rows")), reverse=True)


def metric_summary_rows(run_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    rows.extend(
        summarize_numeric_columns(
            artifact="coupled_joint_vs_product_residual_by_horizon.csv.gz",
            table=read_csv(run_dir / "coupled_joint_vs_product_residual_by_horizon.csv.gz"),
            columns=[
                "joint_support_residual_fraction",
                "product_joint_support_count",
                "coupled_joint_support_count",
                "joint_support_symmetric_difference_count",
            ],
            group_fields=("feature_status",),
        )
    )
    rows.extend(
        summarize_numeric_columns(
            artifact="coupled_marginal_retention_by_horizon.csv.gz",
            table=read_csv(run_dir / "coupled_marginal_retention_by_horizon.csv.gz"),
            columns=[
                "A_marginal_retention_fraction",
                "B_marginal_retention_fraction",
                "joint_retention_fraction",
                "joint_product_state_count",
                "joint_coupled_state_count",
            ],
            group_fields=("feature_status",),
        )
    )
    rows.extend(
        summarize_numeric_columns(
            artifact="coupled_marginal_projection_delta_by_horizon.csv.gz",
            table=read_csv(run_dir / "coupled_marginal_projection_delta_by_horizon.csv.gz"),
            columns=[
                "marginal_retention_fraction",
                "marginal_symmetric_difference_fraction",
                "product_missing_from_coupled_count",
                "coupled_missing_from_product_count",
            ],
            group_fields=("feature_status", "projected_field"),
        )
    )
    rows.extend(
        summarize_numeric_columns(
            artifact="coupled_joint_frontier_profile_by_horizon.csv.gz",
            table=read_csv(run_dir / "coupled_joint_frontier_profile_by_horizon.csv.gz"),
            columns=[
                "joint_frontier_state_count",
                "joint_frontier_edge_count",
                "A_marginal_state_count",
                "B_marginal_state_count",
                "joint_density_vs_marginal_product",
            ],
            group_fields=("feature_status", "joint_scan_mode"),
        )
    )
    return rows


def summarize_numeric_columns(
    *,
    artifact: str,
    table: list[dict[str, object]],
    columns: Iterable[str],
    group_fields: tuple[str, ...],
) -> list[dict[str, object]]:
    grouped: dict[tuple[str, ...], list[dict[str, object]]] = {}
    for row in table:
        key = tuple(str(row.get(field, "")) for field in group_fields)
        grouped.setdefault(key, []).append(row)
    rows: list[dict[str, object]] = []
    for key, group_rows in sorted(grouped.items()):
        group_values = dict(zip(group_fields, key))
        for column in columns:
            values = [float_value(row.get(column)) for row in group_rows if is_numberish(row.get(column))]
            if not values:
                continue
            rows.append(
                {
                    "artifact": artifact,
                    **group_values,
                    "metric": column,
                    "count": len(values),
                    "min": min(values),
                    "mean": mean(values),
                    "max": max(values),
                    "last": values[-1],
                }
            )
    return rows


def artifact_inventory(run_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(item for item in run_dir.rglob("*") if item.is_file()):
        if "_retention_summary" in path.parts:
            continue
        rel = path.relative_to(run_dir).as_posix()
        rows.append(
            {
                "relative_path": rel,
                "size_bytes": path.stat().st_size,
                "size_mib": round(path.stat().st_size / (1024**2), 6),
                "compact_retention_artifact": int(rel in COMPACT_ARTIFACTS),
                "raw_spool_artifact": int(rel.startswith(f"{RAW_SPOOL_DIR}/")),
            }
        )
    return rows


def raw_deletion_plan(run_dir: Path, *, status: dict[str, object], readiness_rows: list[dict[str, object]]) -> dict[str, object]:
    raw_spool_dir = run_dir / RAW_SPOOL_DIR
    paths = [raw_spool_dir] if raw_spool_dir.exists() else []
    bytes_to_delete = sum(directory_size_bytes(path) for path in paths)
    readiness = readiness_rows[0] if readiness_rows else {}
    clean = (
        status.get("status") == "COMPLETED"
        and int_value(status.get("coupled_pairs_failed")) == 0
        and int_value(status.get("internal_cap_events")) == 0
        and int_value(status.get("reconstruction_audit_clean_pass")) == 1
        and int_value(status.get("medium_sweep_interpretation_allowed")) == 1
        and int_value(readiness.get("audits_FAIL")) == 0
        and int_value(readiness.get("audits_NO_COMPLETE_ROWS")) == 0
    )
    if not paths:
        recommendation = "no_raw_spools_present"
    elif clean:
        recommendation = "delete_raw_spools_allowed"
    else:
        recommendation = "retain_raw_spools_until_audit_resolved"
    return {
        "created_utc": utc_now(),
        "recommendation": recommendation,
        "raw_delete_candidate_paths": [str(path) for path in paths],
        "raw_delete_candidate_bytes": bytes_to_delete,
        "raw_delete_candidate_gib": round(bytes_to_delete / (1024**3), 6),
        "blocking_fields": {
            "status": status.get("status", ""),
            "coupled_pairs_failed": int_value(status.get("coupled_pairs_failed")),
            "internal_cap_events": int_value(status.get("internal_cap_events")),
            "reconstruction_audit_clean_pass": int_value(status.get("reconstruction_audit_clean_pass")),
            "medium_sweep_interpretation_allowed": int_value(status.get("medium_sweep_interpretation_allowed")),
            "audits_FAIL": int_value(readiness.get("audits_FAIL")),
            "audits_NO_COMPLETE_ROWS": int_value(readiness.get("audits_NO_COMPLETE_ROWS")),
        },
    }


def copy_compact_artifacts(run_dir: Path, bundle_dir: Path) -> None:
    for relative in sorted(COMPACT_ARTIFACTS):
        source = run_dir / relative
        if not source.exists():
            continue
        target = bundle_dir / "compact_artifacts" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def delete_raw_paths(run_dir: Path, deletion_plan: dict[str, object]) -> None:
    for path_text in deletion_plan.get("raw_delete_candidate_paths", []):
        path = Path(str(path_text)).resolve()
        if not is_relative_to(path, run_dir):
            raise ValueError(f"refusing to delete outside run directory: {path}")
        if path.exists():
            shutil.rmtree(path)


def write_markdown(path: Path, summary: dict[str, object], deletion_plan: dict[str, object]) -> None:
    lines = [
        f"# Retained Run Summary: {summary.get('run_name', '')}",
        "",
        "## Status",
        "",
        "```text",
        f"status: {summary.get('status', '')}",
        f"horizon_max: {summary.get('horizon_max', '')}",
        f"pairs completed: {summary.get('coupled_pairs_completed', '')} / {summary.get('pair_count_realized', '')}",
        f"pair failures: {summary.get('coupled_pairs_failed', '')}",
        f"internal_cap_events: {summary.get('internal_cap_events', '')}",
        f"audits: {summary.get('audit_status_counts_json', '')}",
        f"medium_sweep_interpretation_allowed: {summary.get('medium_sweep_interpretation_allowed', '')}",
        "```",
        "",
        "## Output",
        "",
        "```text",
        f"edge rows: {summary.get('joint_edge_rows', '')}",
        f"node rows: {summary.get('joint_node_rows', '')}",
        f"total output GiB: {summary.get('total_output_size_gib', '')}",
        f"raw delete candidate GiB: {summary.get('raw_delete_candidate_gib', '')}",
        f"heaviest pair edge share: {summary.get('heaviest_pair_edge_share', '')}",
        f"heaviest pair edge rows: {summary.get('heaviest_pair_edge_rows', '')}",
        "```",
        "",
        "## Deletion recommendation",
        "",
        "```text",
        f"recommendation: {deletion_plan.get('recommendation', '')}",
        f"candidate paths: {deletion_plan.get('raw_delete_candidate_paths', [])}",
        "```",
        "",
        "## Claim boundary",
        "",
        "```text",
        str(summary.get("claim_boundary", "")),
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def directory_size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def int_value(value: object) -> int:
    if value in {"", None}:
        return 0
    return int(float(str(value)))


def float_value(value: object) -> float:
    if value in {"", None}:
        return 0.0
    return float(str(value))


def is_numberish(value: object) -> bool:
    if value in {"", None}:
        return False
    try:
        float(str(value))
    except ValueError:
        return False
    return True


def safe_fraction(numerator: int, denominator: int) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0


if __name__ == "__main__":
    main()
