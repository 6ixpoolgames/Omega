from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .coupled import CoupledProbeResult
from .util import read_csv, safe_token, write_csv, write_json


@dataclass(frozen=True)
class CoupledSpoolResult:
    pair_id: str
    spool_dir: str
    node_file: str
    edge_file: str
    profile_file: str
    marginal_file: str
    residual_file: str
    marginal_projection_file: str
    internal_cap_file: str
    reconstruction_audit_file: str
    artifact_completeness_file: str
    manifest_file: str
    node_rows: int
    edge_rows: int
    profile_rows: int
    marginal_rows: int
    residual_rows: int
    marginal_projection_rows: int
    internal_cap_rows: int


def write_pair_spool(
    *,
    out_dir: Path,
    result: CoupledProbeResult,
    reconstruction_rows: list[dict[str, object]],
    completeness_rows: list[dict[str, object]],
    csv_output_mode: str,
    gzip_compresslevel: int,
) -> CoupledSpoolResult:
    pair_rel_dir = Path("coupled_pair_spool") / safe_token(result.pair_id)
    pair_dir = out_dir / pair_rel_dir
    node_file = write_spool_csv(out_dir, pair_rel_dir, "coupled_joint_frontier_nodes_by_horizon.csv", result.node_rows, csv_output_mode, gzip_compresslevel)
    edge_file = write_spool_csv(out_dir, pair_rel_dir, "coupled_joint_frontier_edges_by_step.csv", result.edge_rows, csv_output_mode, gzip_compresslevel)
    profile_file = write_spool_csv(out_dir, pair_rel_dir, "coupled_joint_frontier_profile_by_horizon.csv", result.profile_rows, csv_output_mode, gzip_compresslevel)
    marginal_file = write_spool_csv(out_dir, pair_rel_dir, "coupled_marginal_retention_by_horizon.csv", result.marginal_rows, csv_output_mode, gzip_compresslevel)
    residual_file = write_spool_csv(out_dir, pair_rel_dir, "coupled_joint_vs_product_residual_by_horizon.csv", result.residual_rows, csv_output_mode, gzip_compresslevel)
    projection_file = write_spool_csv(out_dir, pair_rel_dir, "coupled_marginal_projection_delta_by_horizon.csv", result.marginal_projection_rows, csv_output_mode, gzip_compresslevel)
    cap_file = write_spool_csv(out_dir, pair_rel_dir, "coupled_internal_frontier_cap_events.csv", result.internal_cap_rows, csv_output_mode, gzip_compresslevel)
    audit_file = write_spool_csv(out_dir, pair_rel_dir, "coupled_reconstruction_audit_summary.csv", reconstruction_rows, csv_output_mode, gzip_compresslevel)
    completeness_file = write_spool_csv(out_dir, pair_rel_dir, "coupled_artifact_completeness_summary.csv", completeness_rows, csv_output_mode, gzip_compresslevel)
    spool = CoupledSpoolResult(
        pair_id=result.pair_id,
        spool_dir=path_token(pair_rel_dir),
        node_file=node_file,
        edge_file=edge_file,
        profile_file=profile_file,
        marginal_file=marginal_file,
        residual_file=residual_file,
        marginal_projection_file=projection_file,
        internal_cap_file=cap_file,
        reconstruction_audit_file=audit_file,
        artifact_completeness_file=completeness_file,
        manifest_file=path_token(pair_rel_dir / "pair_spool_manifest.json"),
        node_rows=len(result.node_rows),
        edge_rows=len(result.edge_rows),
        profile_rows=len(result.profile_rows),
        marginal_rows=len(result.marginal_rows),
        residual_rows=len(result.residual_rows),
        marginal_projection_rows=len(result.marginal_projection_rows),
        internal_cap_rows=len(result.internal_cap_rows),
    )
    write_json(
        pair_dir / "pair_spool_manifest.json",
        {
            "pair_id": result.pair_id,
            "spool_dir": spool.spool_dir,
            "csv_output_mode": csv_output_mode,
            "gzip_compresslevel": gzip_compresslevel,
            "files": {
                "nodes": node_file,
                "edges": edge_file,
                "profile": profile_file,
                "marginal_retention": marginal_file,
                "joint_vs_product_residual": residual_file,
                "marginal_projection_delta": projection_file,
                "internal_cap_events": cap_file,
                "reconstruction_audit": audit_file,
                "artifact_completeness": completeness_file,
            },
            "row_counts": {
                "nodes": spool.node_rows,
                "edges": spool.edge_rows,
                "profile": spool.profile_rows,
                "marginal_retention": spool.marginal_rows,
                "joint_vs_product_residual": spool.residual_rows,
                "marginal_projection_delta": spool.marginal_projection_rows,
                "internal_cap_events": spool.internal_cap_rows,
            },
        },
    )
    return spool


def write_spool_csv(
    out_dir: Path,
    pair_rel_dir: Path,
    logical_name: str,
    rows: list[dict[str, object]],
    csv_output_mode: str,
    gzip_compresslevel: int,
) -> str:
    logical_path = path_token(pair_rel_dir / logical_name)
    physical_names = expand_csv_output_files([logical_path], csv_output_mode)
    for physical_name in physical_names:
        write_csv(out_dir / physical_name, rows, gzip_compresslevel=gzip_compresslevel)
    return primary_csv_artifact_name(logical_path, csv_output_mode)


def read_spooled_rows(out_dir: Path, spools: list[CoupledSpoolResult], file_attr: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for spool in spools:
        rows.extend(read_csv(out_dir / str(getattr(spool, file_attr))))
    return rows


def spooled_raw_topology_manifest_rows(
    spools: list[CoupledSpoolResult],
    row_kind: str,
    csv_output_mode: str,
    gzip_compresslevel: int,
) -> list[dict[str, object]]:
    if row_kind == "nodes":
        logical_name = "coupled_joint_frontier_nodes_by_horizon.csv"
        file_attr = "node_file"
        row_attr = "node_rows"
    elif row_kind == "edges":
        logical_name = "coupled_joint_frontier_edges_by_step.csv"
        file_attr = "edge_file"
        row_attr = "edge_rows"
    else:
        raise ValueError(f"unsupported spooled row kind: {row_kind}")
    return [
        {
            "logical_artifact_name": logical_name,
            "physical_artifact_name": getattr(spool, file_attr),
            "artifact_storage_kind": "worker_spooled_csv",
            "spool_index": index,
            "spool_count": len(spools),
            "spool_pair_count": 1,
            "row_count": getattr(spool, row_attr),
            "pair_id": spool.pair_id,
            "first_pair_id": spool.pair_id,
            "last_pair_id": spool.pair_id,
            "csv_output_mode": csv_output_mode,
            "gzip_compresslevel": gzip_compresslevel,
        }
        for index, spool in enumerate(spools)
    ]


def pair_spool_manifest_rows(spools: list[CoupledSpoolResult]) -> list[dict[str, object]]:
    return [
        {
            "pair_id": spool.pair_id,
            "spool_dir": spool.spool_dir,
            "node_file": spool.node_file,
            "edge_file": spool.edge_file,
            "profile_file": spool.profile_file,
            "marginal_file": spool.marginal_file,
            "residual_file": spool.residual_file,
            "marginal_projection_file": spool.marginal_projection_file,
            "internal_cap_file": spool.internal_cap_file,
            "reconstruction_audit_file": spool.reconstruction_audit_file,
            "artifact_completeness_file": spool.artifact_completeness_file,
            "manifest_file": spool.manifest_file,
            "node_rows": spool.node_rows,
            "edge_rows": spool.edge_rows,
            "profile_rows": spool.profile_rows,
            "marginal_rows": spool.marginal_rows,
            "residual_rows": spool.residual_rows,
            "marginal_projection_rows": spool.marginal_projection_rows,
            "internal_cap_rows": spool.internal_cap_rows,
        }
        for spool in spools
    ]


def aggregate_reconstruction_audit_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, int]] = {}
    for row in rows:
        name = str(row.get("audit_name", ""))
        if not name:
            continue
        bucket = grouped.setdefault(name, {"checked": 0, "failed": 0, "skipped": 0})
        bucket["checked"] += int_value(row.get("checked_items", 0))
        bucket["failed"] += int_value(row.get("failed_items", 0))
        bucket["skipped"] += int_value(row.get("skipped_items", 0))
    return [
        audit_result(name, checked=values["checked"], failed=values["failed"], skipped=values["skipped"])
        for name, values in sorted(grouped.items())
    ]


def aggregate_artifact_completeness_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], int] = {}
    for row in rows:
        key = (
            str(row.get("artifact_name", "")),
            str(row.get("status_field", "")),
            str(row.get("artifact_status", "")),
        )
        if not key[0]:
            continue
        grouped[key] = grouped.get(key, 0) + int_value(row.get("row_count", 0))
    return [
        {
            "artifact_name": artifact_name,
            "status_field": status_field,
            "artifact_status": artifact_status,
            "row_count": row_count,
        }
        for (artifact_name, status_field, artifact_status), row_count in sorted(grouped.items())
    ]


def spooled_output_files(spools: list[CoupledSpoolResult]) -> list[str]:
    files: list[str] = []
    for spool in spools:
        files.extend([
            spool.node_file,
            spool.edge_file,
            spool.profile_file,
            spool.marginal_file,
            spool.residual_file,
            spool.marginal_projection_file,
            spool.internal_cap_file,
            spool.reconstruction_audit_file,
            spool.artifact_completeness_file,
            spool.manifest_file,
        ])
    return files


def spooled_row_counts(spools: list[CoupledSpoolResult], row_counts: dict[str, int]) -> dict[str, int]:
    counts = dict(row_counts)
    for spool in spools:
        counts[spool.node_file] = spool.node_rows
        counts[spool.edge_file] = spool.edge_rows
        counts[spool.profile_file] = spool.profile_rows
        counts[spool.marginal_file] = spool.marginal_rows
        counts[spool.residual_file] = spool.residual_rows
        counts[spool.marginal_projection_file] = spool.marginal_projection_rows
        counts[spool.internal_cap_file] = spool.internal_cap_rows
        counts[spool.reconstruction_audit_file] = 3
        counts[spool.artifact_completeness_file] = 7
    return counts


def audit_result(audit_name: str, *, checked: int, failed: int, skipped: int) -> dict[str, object]:
    if failed > 0:
        status = "FAIL"
    elif checked == 0 and skipped > 0:
        status = "NO_COMPLETE_ROWS"
    elif skipped > 0:
        status = "PASS_WITH_SKIPS"
    else:
        status = "PASS"
    return {
        "audit_name": audit_name,
        "status": status,
        "checked_items": checked,
        "failed_items": failed,
        "skipped_items": skipped,
    }


def expand_csv_output_files(logical_names: list[str], csv_output_mode: str) -> list[str]:
    if csv_output_mode == "plain":
        return list(logical_names)
    if csv_output_mode == "gzip":
        return [f"{name}.gz" for name in logical_names]
    if csv_output_mode == "both":
        return [item for name in logical_names for item in (name, f"{name}.gz")]
    raise ValueError(f"unknown csv output mode: {csv_output_mode}")


def primary_csv_artifact_name(logical_name: str, csv_output_mode: str) -> str:
    if csv_output_mode == "gzip":
        return f"{logical_name}.gz"
    return logical_name


def int_value(value: object) -> int:
    if value in {"", None}:
        return 0
    return int(float(str(value)))


def path_token(path: Path) -> str:
    return path.as_posix()

