"""Run the Future Field Atlas Phase 0/1 instrument smoke.

The runner is intentionally thin. Generation, frontier unfolding, topology
mapping, transport construction, and recovery analysis live in separate modules.
"""

from __future__ import annotations

import argparse
import signal
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, ThreadPoolExecutor, as_completed, wait
from pathlib import Path
from typing import Callable, Iterable

from .analyzer import (
    rank_boundary_geometry_by_horizon,
    rank_boundary_geometry_by_horizon_pair,
    selection_operator_geometry_summary,
)
from .contracts import CLAIM_BOUNDARY, FrontierScanSpec, ScanBundle, ScanTask, instrument_metadata
from .generator import DEFAULT_SELECTION_OPERATORS, build_generated_conditions, select_start_states
from .manifests import condition_identity_manifest_rows, formal_spec_manifest_rows, scan_manifest_rows
from .mapper import map_scan
from .reconstruction import reconstruction_audit_rows
from .scanner import scan_task
from .transport import (
    adjacent_transport_matrices,
    flow_composition_residual_rows,
    matrix_manifest_rows,
    multiscale_transport_matrices,
    write_sparse_npz,
)
from .util import csv_row_count, safe_token, state_id, utc_now, write_csv, write_json


STOP_REQUESTED = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Future Field Atlas Phase 0/1 smoke.")
    parser.add_argument("--out", type=Path, default=Path("results/future_field_atlas/phase0_1_smoke"))
    parser.add_argument("--groups", type=int, default=1)
    parser.add_argument("--design-groups", type=int, default=None, help="Alias for --groups.")
    parser.add_argument("--fresh-seeds-per-group", type=int, default=1)
    parser.add_argument("--base-seed", type=int, default=44_001)
    parser.add_argument("--start-samples-list", type=str, default="1")
    parser.add_argument("--horizon-max", type=int, default=128)
    parser.add_argument("--horizon-schedule", type=str, default="dense_to_32_plus_h128")
    parser.add_argument("--horizon-pairs", type=str, default="")
    parser.add_argument("--macro-invariant-kind", type=str, default="symbol_histogram_distance")
    parser.add_argument("--macro-invariant-beta-list", type=str, default="0.10")
    parser.add_argument("--rank-boundary-k", type=int, default=3)
    parser.add_argument(
        "--selection-operators",
        type=str,
        default=",".join(DEFAULT_SELECTION_OPERATORS),
        help="Comma-separated operator specs such as rank_prefix:m=3 or rank_subset:m=4:retain=1|2|3:remove=4.",
    )
    parser.add_argument("--max-frontier-nodes-per-horizon", type=int, default=512)
    parser.add_argument("--max-frontier-edges-per-step", type=int, default=2048)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--checkpoint-every-scans", type=int, default=2)
    parser.add_argument("--max-runtime-seconds", type=int, default=1800)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=30)
    parser.add_argument(
        "--csv-output-mode",
        choices=("plain", "gzip", "both"),
        default="gzip",
        help="Write primary CSV artifacts as plain .csv, gzip .csv.gz, or both.",
    )
    parser.add_argument("--gzip-compresslevel", type=int, default=1)
    parser.add_argument(
        "--transport-output-mode",
        choices=("adjacent_only", "selected_multiscale", "full"),
        default="selected_multiscale",
        help="Control multiscale transport retention. Adjacent matrices are always emitted.",
    )
    parser.add_argument(
        "--composition-residual-mode",
        choices=("none", "selected", "full"),
        default="selected",
        help="Control transport composition residual audits.",
    )
    parser.add_argument(
        "--raw-topology-output-mode",
        choices=("sharded", "consolidated", "both"),
        default="sharded",
        help="Write high-volume node/edge topology as sharded files, consolidated files, or both.",
    )
    parser.add_argument("--raw-topology-shard-scan-count", type=int, default=8)
    parser.add_argument("--artifact-write-workers", type=int, default=8)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    install_signal_handlers()
    started_perf = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    groups = int(args.design_groups) if args.design_groups is not None else int(args.groups)
    horizon_schedule = parse_horizon_schedule(args.horizon_schedule, args.horizon_max)
    horizon_pairs = parse_horizon_pairs(args.horizon_pairs, args.horizon_max)
    validate_transport_modes(args.transport_output_mode, args.composition_residual_mode)
    start_samples = max(parse_int_list(args.start_samples_list) or [1])
    macro_betas = tuple(parse_float_list(args.macro_invariant_beta_list) or [0.10])
    selection_operators = tuple(item.strip() for item in args.selection_operators.split(",") if item.strip())
    config = {
        **instrument_metadata(),
        **vars(args),
        "groups_resolved": groups,
        "start_samples": start_samples,
        "horizon_schedule_resolved": list(horizon_schedule),
        "horizon_pairs_resolved": [f"{left}->{right}" for left, right in horizon_pairs],
        "macro_invariant_betas": list(macro_betas),
        "selection_operators_resolved": list(selection_operators),
    }
    write_json(args.out / "future_field_atlas_run_config.json", config)
    conditions = build_generated_conditions(
        groups=groups,
        fresh_seeds_per_group=args.fresh_seeds_per_group,
        selection_operators=selection_operators,
        macro_invariant_kind=args.macro_invariant_kind,
        macro_invariant_betas=macro_betas,
        rank_boundary_k=args.rank_boundary_k,
        base_seed=args.base_seed,
    )
    tasks = build_scan_tasks(
        conditions=conditions,
        start_samples=start_samples,
        horizon_max=args.horizon_max,
        horizon_schedule=horizon_schedule,
        max_frontier_nodes_per_horizon=args.max_frontier_nodes_per_horizon,
        max_frontier_edges_per_step=args.max_frontier_edges_per_step,
    )
    status: dict[str, object] = {
        **instrument_metadata(),
        "status": "RUNNING",
        "started_utc": utc_now(),
        "out_dir": str(args.out),
        "conditions": len(conditions),
        "scans_requested": len(tasks),
        "scans_submitted": 0,
        "scans_completed": 0,
        "scans_cancelled": 0,
        "workers": max(1, args.workers),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(args.out / "future_field_atlas_status.json", status)
    completed, errors, progress = run_tasks(args, tasks, status, started_perf)
    write_all_outputs(
        args.out,
        completed,
        errors,
        progress,
        status,
        started_perf,
        horizon_pairs,
        args.csv_output_mode,
        args.gzip_compresslevel,
        args.raw_topology_output_mode,
        args.raw_topology_shard_scan_count,
        args.artifact_write_workers,
        args.transport_output_mode,
        args.composition_residual_mode,
    )


def build_scan_tasks(
    *,
    conditions: Iterable[object],
    start_samples: int,
    horizon_max: int,
    horizon_schedule: tuple[int, ...],
    max_frontier_nodes_per_horizon: int,
    max_frontier_edges_per_step: int,
) -> list[ScanTask]:
    tasks: list[ScanTask] = []
    frontier_scan = FrontierScanSpec(
        frontier_scan_id=f"frontier_scan__{safe_token(str(horizon_schedule))}__H{horizon_max}",
        frontier_expansion_rule_id="iterated_selected_successor_image",
        horizon_schedule_id=f"explicit_horizon_schedule__{safe_token(str(horizon_schedule))}",
        horizon_schedule=horizon_schedule,
        horizon_max=horizon_max,
        node_artifact_retention_policy=(
            f"sorted_prefix_limit_{max_frontier_nodes_per_horizon}"
            if max_frontier_nodes_per_horizon > 0 else "complete"
        ),
        edge_artifact_retention_policy=(
            f"sorted_prefix_limit_{max_frontier_edges_per_step}"
            if max_frontier_edges_per_step > 0 else "complete"
        ),
        frontier_scan_params_json=safe_frontier_scan_params_json(
            horizon_schedule=horizon_schedule,
            horizon_max=horizon_max,
            max_frontier_nodes_per_horizon=max_frontier_nodes_per_horizon,
            max_frontier_edges_per_step=max_frontier_edges_per_step,
        ),
        max_frontier_nodes_per_horizon=max_frontier_nodes_per_horizon,
        max_frontier_edges_per_step=max_frontier_edges_per_step,
    )
    for condition in conditions:
        starts = select_start_states(condition, start_samples)  # type: ignore[arg-type]
        for start_index, start in enumerate(starts):
            scan_id = (
                f"{condition.spec.condition_id}__start{start_index:02d}__"  # type: ignore[attr-defined]
                f"{safe_token(state_id(start))}"
            )
            tasks.append(
                ScanTask(
                    scan_id=scan_id,
                    condition=condition,  # type: ignore[arg-type]
                    frontier_scan=frontier_scan,
                    start_index=start_index,
                    start_state=start,
                )
            )
    return tasks


def safe_frontier_scan_params_json(
    *,
    horizon_schedule: tuple[int, ...],
    horizon_max: int,
    max_frontier_nodes_per_horizon: int,
    max_frontier_edges_per_step: int,
) -> str:
    from .util import canonical_json

    return canonical_json({
        "frontier_expansion_rule_id": "iterated_selected_successor_image",
        "horizon_schedule": list(horizon_schedule),
        "horizon_max": horizon_max,
        "node_artifact_retention_policy": (
            f"sorted_prefix_limit_{max_frontier_nodes_per_horizon}"
            if max_frontier_nodes_per_horizon > 0 else "complete"
        ),
        "edge_artifact_retention_policy": (
            f"sorted_prefix_limit_{max_frontier_edges_per_step}"
            if max_frontier_edges_per_step > 0 else "complete"
        ),
        "max_frontier_nodes_per_horizon": max_frontier_nodes_per_horizon,
        "max_frontier_edges_per_step": max_frontier_edges_per_step,
    })


def run_one(task: ScanTask) -> ScanBundle:
    try:
        raw = scan_task(task)
        mapped = map_scan(raw, task.condition)
        return ScanBundle(mapped=mapped, errors=[])
    except Exception as exc:  # noqa: BLE001
        return ScanBundle(
            mapped=None,  # type: ignore[arg-type]
            errors=[{
                "scan_id": task.scan_id,
                "condition_id": task.condition.spec.condition_id,
                "error": repr(exc),
            }],
        )


def run_tasks(
    args: argparse.Namespace,
    tasks: list[ScanTask],
    status: dict[str, object],
    started_perf: float,
) -> tuple[list[object], list[dict[str, object]], list[dict[str, object]]]:
    completed: list[object] = []
    errors: list[dict[str, object]] = []
    progress: list[dict[str, object]] = []
    pending = list(tasks)
    last_checkpoint = 0
    if max(1, args.workers) == 1:
        for task in pending:
            if should_stop(args, started_perf):
                status["status"] = "PARTIAL_TIME_LIMIT_REACHED" if not STOP_REQUESTED else "PARTIAL_INTERRUPTED"
                break
            bundle = run_one(task)
            if bundle.mapped is not None:
                completed.append(bundle.mapped)
            errors.extend(bundle.errors)
            status["scans_submitted"] = int(status["scans_submitted"]) + 1
            status["scans_completed"] = len(completed)
            if len(completed) - last_checkpoint >= max(1, args.checkpoint_every_scans):
                progress.append(progress_row(status, started_perf, completed, errors))
                last_checkpoint = len(completed)
                write_partial(args.out, status, progress, errors, started_perf)
        if status.get("status") == "RUNNING":
            status["status"] = "COMPLETED"
            status["finalization_reason"] = "all_scans_completed"
        progress.append(progress_row(status, started_perf, completed, errors))
        write_partial(args.out, status, progress, errors, started_perf)
        return completed, errors, progress

    futures = {}
    executor = ProcessPoolExecutor(max_workers=max(1, args.workers))
    try:
        while pending or futures:
            if should_stop(args, started_perf):
                status["status"] = "PARTIAL_TIME_LIMIT_REACHED" if not STOP_REQUESTED else "PARTIAL_INTERRUPTED"
                status["finalization_reason"] = "shutdown_cushion_or_signal"
                break
            while pending and len(futures) < max(1, args.workers):
                task = pending.pop(0)
                futures[executor.submit(run_one, task)] = task
                status["scans_submitted"] = int(status["scans_submitted"]) + 1
            done, _not_done = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                task = futures.pop(future)
                try:
                    bundle = future.result()
                except Exception as exc:  # noqa: BLE001
                    bundle = ScanBundle(
                        mapped=None,  # type: ignore[arg-type]
                        errors=[{"scan_id": task.scan_id, "condition_id": task.condition.spec.condition_id, "error": repr(exc)}],
                    )
                if bundle.mapped is not None:
                    completed.append(bundle.mapped)
                errors.extend(bundle.errors)
                status["scans_completed"] = len(completed)
                if len(completed) - last_checkpoint >= max(1, args.checkpoint_every_scans):
                    progress.append(progress_row(status, started_perf, completed, errors))
                    last_checkpoint = len(completed)
                    write_partial(args.out, status, progress, errors, started_perf)
    finally:
        if futures:
            for future in futures:
                future.cancel()
            status["scans_cancelled"] = len(futures)
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    if status.get("status") == "RUNNING":
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "all_scans_completed"
    progress.append(progress_row(status, started_perf, completed, errors))
    write_partial(args.out, status, progress, errors, started_perf)
    return completed, errors, progress


def should_stop(args: argparse.Namespace, started_perf: float) -> bool:
    if STOP_REQUESTED:
        return True
    elapsed = time.perf_counter() - started_perf
    return elapsed >= max(0, args.max_runtime_seconds - args.shutdown_cushion_seconds)


def write_partial(
    out_dir: Path,
    status: dict[str, object],
    progress: list[dict[str, object]],
    errors: list[dict[str, object]],
    started_perf: float,
) -> None:
    status["elapsed_seconds"] = round(time.perf_counter() - started_perf, 3)
    write_json(out_dir / "future_field_atlas_status.json", status)
    write_csv(out_dir / "future_field_atlas_progress.csv", progress, gzip_compresslevel=1)
    write_csv(out_dir / "future_field_atlas_errors.csv", errors, gzip_compresslevel=1)


def write_all_outputs(
    out_dir: Path,
    scans: list[object],
    errors: list[dict[str, object]],
    progress: list[dict[str, object]],
    status: dict[str, object],
    started_perf: float,
    horizon_pairs: tuple[tuple[int, int], ...],
    csv_output_mode: str,
    gzip_compresslevel: int,
    raw_topology_output_mode: str,
    raw_topology_shard_scan_count: int,
    artifact_write_workers: int,
    transport_output_mode: str,
    composition_residual_mode: str,
) -> None:
    finalization_timings: dict[str, float] = {}
    phase_started = time.perf_counter()
    mapped_scans = list(scans)
    node_rows = [row for scan in mapped_scans for row in scan.raw.node_rows]  # type: ignore[attr-defined]
    edge_rows = [row for scan in mapped_scans for row in scan.raw.edge_rows]  # type: ignore[attr-defined]
    profile_rows = [row for scan in mapped_scans for row in scan.profile_rows]  # type: ignore[attr-defined]
    membership_rows = [row for scan in mapped_scans for row in scan.membership_rows]  # type: ignore[attr-defined]
    boundary_rows = [row for scan in mapped_scans for row in scan.boundary_rows]  # type: ignore[attr-defined]
    finalization_timings["flatten_rows"] = round(time.perf_counter() - phase_started, 3)

    phase_started = time.perf_counter()
    adjacent = adjacent_transport_matrices(mapped_scans)  # type: ignore[arg-type]
    finalization_timings["adjacent_transport_matrices"] = round(time.perf_counter() - phase_started, 3)

    phase_started = time.perf_counter()
    multiscale_pairs = multiscale_pairs_for_modes(
        horizon_pairs,
        transport_output_mode,
        composition_residual_mode,
    )
    multiscale = multiscale_transport_matrices(mapped_scans, multiscale_pairs)  # type: ignore[arg-type]
    finalization_timings["multiscale_transport_matrices"] = round(time.perf_counter() - phase_started, 3)

    phase_started = time.perf_counter()
    residual_triples = composition_triples_for_mode(horizon_pairs, composition_residual_mode)
    residual_rows = (
        []
        if composition_residual_mode == "none"
        else flow_composition_residual_rows(multiscale, residual_triples)
    )
    residual_triple_count: object = "full" if residual_triples is None else len(residual_triples)
    finalization_timings["composition_residuals"] = round(time.perf_counter() - phase_started, 3)

    phase_started = time.perf_counter()
    operator_geometry_summary = selection_operator_geometry_summary(mapped_scans)  # type: ignore[arg-type]
    rank_boundary_rows = rank_boundary_geometry_by_horizon(mapped_scans)  # type: ignore[arg-type]
    boundary_pair_rows = rank_boundary_geometry_by_horizon_pair(mapped_scans, horizon_pairs)  # type: ignore[arg-type]
    spec_manifest_rows = formal_spec_manifest_rows(mapped_scans)  # type: ignore[arg-type]
    condition_identity_rows = condition_identity_manifest_rows(mapped_scans)  # type: ignore[arg-type]
    scan_manifest = scan_manifest_rows(mapped_scans)  # type: ignore[arg-type]
    adjacent_manifest = matrix_manifest_rows(adjacent)
    multiscale_manifest = matrix_manifest_rows(multiscale)
    reconstruction_rows = reconstruction_audit_rows(
        node_rows=node_rows,
        edge_rows=edge_rows,
        profile_rows=profile_rows,
        rank_boundary_rows=boundary_rows,
        adjacent_manifest_rows=adjacent_manifest,
        adjacent_matrices=adjacent,
        operator_geometry_rows=operator_geometry_summary,
        condition_identity_rows=condition_identity_rows,
        scan_manifest_rows=scan_manifest,
    )
    completeness_rows = artifact_completeness_rows(
        node_rows=node_rows,
        edge_rows=edge_rows,
        profile_rows=profile_rows,
    )
    finalization_timings["summaries_manifests_audits"] = round(time.perf_counter() - phase_started, 3)

    csv_output_files = [
        "formal_spec_manifest.csv",
        "condition_identity_manifest.csv",
        "scan_manifest.csv",
        "frontier_profile_by_horizon.csv",
        "frontier_membership_timeseries.csv",
        "rank_boundary_geometry_by_horizon.csv",
        "raw_transport_matrices_adjacent_manifest.csv",
        "raw_transport_matrices_multiscale_manifest.csv",
        "transport_flow_composition_residuals.csv",
        "selection_operator_geometry_summary.csv",
        "rank_boundary_geometry_by_horizon_summary.csv",
        "rank_boundary_geometry_by_horizon_pair.csv",
        "reconstruction_audit_summary.csv",
        "artifact_completeness_summary.csv",
    ]
    raw_topology_files = [
        "frontier_nodes_by_horizon.csv",
        "frontier_edges_by_step.csv",
    ]
    raw_shard_manifest_files = [
        "frontier_nodes_by_horizon_shard_manifest.csv",
        "frontier_edges_by_step_shard_manifest.csv",
    ]
    if raw_topology_output_mode in {"consolidated", "both"}:
        csv_output_files.extend(raw_topology_files)
    if raw_topology_output_mode in {"sharded", "both"}:
        csv_output_files.extend(raw_shard_manifest_files)

    phase_started = time.perf_counter()
    node_shard_manifest: list[dict[str, object]] = []
    edge_shard_manifest: list[dict[str, object]] = []
    if raw_topology_output_mode in {"sharded", "both"}:
        node_shard_manifest, edge_shard_manifest = write_raw_topology_shards(
            out_dir=out_dir,
            mapped_scans=mapped_scans,
            csv_output_mode=csv_output_mode,
            shard_scan_count=raw_topology_shard_scan_count,
            gzip_compresslevel=gzip_compresslevel,
            artifact_write_workers=artifact_write_workers,
        )
    finalization_timings["raw_topology_shard_writes"] = round(time.perf_counter() - phase_started, 3)

    csv_row_counts = {
        "formal_spec_manifest.csv": len(spec_manifest_rows),
        "condition_identity_manifest.csv": len(condition_identity_rows),
        "scan_manifest.csv": len(scan_manifest),
        "frontier_nodes_by_horizon.csv": len(node_rows),
        "frontier_edges_by_step.csv": len(edge_rows),
        "frontier_profile_by_horizon.csv": len(profile_rows),
        "frontier_membership_timeseries.csv": len(membership_rows),
        "rank_boundary_geometry_by_horizon.csv": len(boundary_rows),
        "frontier_nodes_by_horizon_shard_manifest.csv": len(node_shard_manifest),
        "frontier_edges_by_step_shard_manifest.csv": len(edge_shard_manifest),
        "raw_transport_matrices_adjacent_manifest.csv": len(adjacent_manifest),
        "raw_transport_matrices_multiscale_manifest.csv": len(multiscale_manifest),
        "transport_flow_composition_residuals.csv": len(residual_rows),
        "selection_operator_geometry_summary.csv": len(operator_geometry_summary),
        "rank_boundary_geometry_by_horizon_summary.csv": len(rank_boundary_rows),
        "rank_boundary_geometry_by_horizon_pair.csv": len(boundary_pair_rows),
        "reconstruction_audit_summary.csv": len(reconstruction_rows),
        "artifact_completeness_summary.csv": len(completeness_rows),
    }
    output_files = [
        "future_field_atlas_manifest.json",
        "future_field_atlas_run_config.json",
        "future_field_atlas_status.json",
        "future_field_atlas_progress.csv",
        "future_field_atlas_errors.csv",
        "future_field_atlas_report.md",
        "raw_transport_matrices_adjacent.npz",
        "raw_transport_matrices_multiscale.npz",
    ]
    output_files.extend(expand_csv_output_files(csv_output_files, csv_output_mode))
    if raw_topology_output_mode in {"sharded", "both"}:
        output_files.extend(
            str(row["physical_artifact_name"])
            for row in node_shard_manifest + edge_shard_manifest
        )
        for row in node_shard_manifest + edge_shard_manifest:
            csv_row_counts[str(row["physical_artifact_name"])] = int(row["row_count"])
    csv_write_jobs = [
        ("formal_spec_manifest.csv", spec_manifest_rows),
        ("condition_identity_manifest.csv", condition_identity_rows),
        ("scan_manifest.csv", scan_manifest),
        ("frontier_profile_by_horizon.csv", profile_rows),
        ("frontier_membership_timeseries.csv", membership_rows),
        ("rank_boundary_geometry_by_horizon.csv", boundary_rows),
        ("raw_transport_matrices_adjacent_manifest.csv", adjacent_manifest),
        ("raw_transport_matrices_multiscale_manifest.csv", multiscale_manifest),
        ("transport_flow_composition_residuals.csv", residual_rows),
        ("selection_operator_geometry_summary.csv", operator_geometry_summary),
        ("rank_boundary_geometry_by_horizon_summary.csv", rank_boundary_rows),
        ("rank_boundary_geometry_by_horizon_pair.csv", boundary_pair_rows),
        ("reconstruction_audit_summary.csv", reconstruction_rows),
        ("artifact_completeness_summary.csv", completeness_rows),
    ]
    if raw_topology_output_mode in {"consolidated", "both"}:
        csv_write_jobs.extend([
            ("frontier_nodes_by_horizon.csv", node_rows),
            ("frontier_edges_by_step.csv", edge_rows),
        ])
    if raw_topology_output_mode in {"sharded", "both"}:
        csv_write_jobs.extend([
            ("frontier_nodes_by_horizon_shard_manifest.csv", node_shard_manifest),
            ("frontier_edges_by_step_shard_manifest.csv", edge_shard_manifest),
        ])
    phase_started = time.perf_counter()
    write_output_artifacts_parallel(
        out_dir=out_dir,
        csv_write_jobs=csv_write_jobs,
        npz_write_jobs=[
            ("raw_transport_matrices_adjacent.npz", adjacent),
            ("raw_transport_matrices_multiscale.npz", multiscale),
        ],
        csv_output_mode=csv_output_mode,
        gzip_compresslevel=gzip_compresslevel,
        artifact_write_workers=artifact_write_workers,
    )
    finalization_timings["parallel_artifact_writes"] = round(time.perf_counter() - phase_started, 3)
    status["completed_utc"] = utc_now()
    status["elapsed_seconds"] = round(time.perf_counter() - started_perf, 3)
    status["frontier_node_rows"] = len(node_rows)
    status["frontier_edge_rows"] = len(edge_rows)
    status["selection_operator_geometry_rows"] = len(operator_geometry_summary)
    status["reconstruction_audit_passed"] = int(all(row.get("status") == "PASS" for row in reconstruction_rows))
    status["artifact_completeness_statuses"] = ",".join(
        sorted({str(row["artifact_status"]) for row in completeness_rows})
    )
    status["csv_output_mode"] = csv_output_mode
    status["gzip_compresslevel"] = gzip_compresslevel
    status["raw_topology_output_mode"] = raw_topology_output_mode
    status["artifact_write_workers"] = artifact_write_workers
    status["transport_output_mode"] = transport_output_mode
    status["composition_residual_mode"] = composition_residual_mode
    status["multiscale_transport_pair_count"] = len(multiscale_pairs)
    status["composition_residual_triple_count"] = residual_triple_count
    status["finalization_timings_json"] = finalization_timings
    write_partial(out_dir, status, progress, errors, started_perf)
    write_report(
        out_dir,
        status,
        operator_geometry_summary,
        reconstruction_rows,
        completeness_rows,
        csv_output_mode,
        raw_topology_output_mode,
        transport_output_mode,
        composition_residual_mode,
        finalization_timings,
    )
    manifest = {
        **instrument_metadata(),
        "run_status": status.get("status"),
        "csv_output_mode": csv_output_mode,
        "gzip_compresslevel": gzip_compresslevel,
        "raw_topology_output_mode": raw_topology_output_mode,
        "transport_output_mode": transport_output_mode,
        "composition_residual_mode": composition_residual_mode,
        "multiscale_transport_pair_count": len(multiscale_pairs),
        "composition_residual_triple_count": residual_triple_count,
        "artifact_write_workers": artifact_write_workers,
        "raw_topology_shard_scan_count": raw_topology_shard_scan_count,
        "finalization_timings_json": finalization_timings,
        "started_utc": status.get("started_utc"),
        "completed_utc": status.get("completed_utc"),
        "seed_policy": "deterministic base_seed plus group/fresh-seed offsets",
        "substrate_count": len({scan.raw.spec.substrate_id for scan in mapped_scans}),  # type: ignore[attr-defined]
        "frontier_count": len(mapped_scans),
        "horizon_schedule": sorted({row["horizon"] for row in profile_rows}) if profile_rows else [],
        "formal_spec_manifest": primary_csv_artifact_name("formal_spec_manifest.csv", csv_output_mode),
        "condition_identity_manifest": primary_csv_artifact_name("condition_identity_manifest.csv", csv_output_mode),
        "scan_manifest": primary_csv_artifact_name("scan_manifest.csv", csv_output_mode),
        "reconstruction_audit_summary": primary_csv_artifact_name("reconstruction_audit_summary.csv", csv_output_mode),
        "artifact_completeness_summary": primary_csv_artifact_name("artifact_completeness_summary.csv", csv_output_mode),
        "output_files": [
            {
                "file": name,
                "exists": True if name == "future_field_atlas_manifest.json" else (out_dir / name).exists(),
                "row_count": output_row_count(out_dir, name, csv_row_counts),
            }
            for name in output_files
        ],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(out_dir / "future_field_atlas_manifest.json", manifest)


def write_report(
    out_dir: Path,
    status: dict[str, object],
    operator_geometry_rows: list[dict[str, object]],
    reconstruction_rows: list[dict[str, object]],
    completeness_rows: list[dict[str, object]],
    csv_output_mode: str,
    raw_topology_output_mode: str,
    transport_output_mode: str,
    composition_residual_mode: str,
    finalization_timings: dict[str, float],
) -> None:
    deterministic = [
        row for row in operator_geometry_rows
        if str(row.get("operator_rank_boundary_distance", "")) != ""
    ]
    near_zero = [
        row for row in deterministic
        if float(row.get("operator_rank_boundary_distance", 1.0)) <= 0.05
    ]
    lines = [
        "# Future Field Atlas Phase 0/1 Smoke",
        "",
        f"Status: {status.get('status', '')}",
        f"Elapsed seconds: {status.get('elapsed_seconds', '')}",
        "",
        "Claim boundary: instrumentation only. No Omega, agency, identity, valuerhood, value, candidate-promotion, holdout, or graph-causality claim.",
        "",
        "## Readout",
        "",
        (
            "Raw topology produced near-zero operator rank-boundary distance in "
            f"{len(near_zero)} of {len(deterministic)} deterministic operator summaries."
        ),
        "",
        "## Reconstruction Audits",
        "",
        *[
            f"- `{row['audit_name']}`: {row['status']} ({row['checked_items']} checked, {row['failed_items']} failed)"
            for row in reconstruction_rows
        ],
        "",
        "## Artifact Completeness",
        "",
        *[
            f"- `{row['artifact_name']}` / `{row['artifact_status']}`: {row['row_count']} rows"
            for row in completeness_rows
        ],
        "",
        "The report-level read uses continuous rank-boundary geometry metrics. It does not use the old response taxonomy.",
        "",
        "## Storage",
        "",
        f"- CSV output mode: `{csv_output_mode}`",
        f"- Raw topology output mode: `{raw_topology_output_mode}`",
        f"- Transport output mode: `{transport_output_mode}`",
        f"- Composition residual mode: `{composition_residual_mode}`",
        f"- Multiscale transport pair count: `{status.get('multiscale_transport_pair_count', '')}`",
        f"- Composition residual triple count: `{status.get('composition_residual_triple_count', '')}`",
        f"- Gzip compression level: `{status.get('gzip_compresslevel', '')}`",
        f"- Artifact write workers: `{status.get('artifact_write_workers', '')}`",
        "",
        "## Finalization Timings",
        "",
        *[
            f"- `{name}`: {seconds}s"
            for name, seconds in finalization_timings.items()
        ],
        "",
        "## Primary Artifacts",
        "",
        *raw_topology_report_artifacts(raw_topology_output_mode, csv_output_mode),
        f"- `{csv_artifact_display_name('frontier_profile_by_horizon.csv', csv_output_mode)}`",
        f"- `{csv_artifact_display_name('formal_spec_manifest.csv', csv_output_mode)}`",
        f"- `{csv_artifact_display_name('condition_identity_manifest.csv', csv_output_mode)}`",
        f"- `{csv_artifact_display_name('scan_manifest.csv', csv_output_mode)}`",
        f"- `{csv_artifact_display_name('rank_boundary_geometry_by_horizon.csv', csv_output_mode)}`",
        "- `raw_transport_matrices_adjacent.npz`",
        "- `raw_transport_matrices_multiscale.npz`",
        f"- `{csv_artifact_display_name('selection_operator_geometry_summary.csv', csv_output_mode)}`",
        f"- `{csv_artifact_display_name('reconstruction_audit_summary.csv', csv_output_mode)}`",
        f"- `{csv_artifact_display_name('artifact_completeness_summary.csv', csv_output_mode)}`",
    ]
    (out_dir / "future_field_atlas_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv_artifact(
    out_dir: Path,
    logical_name: str,
    rows: list[dict[str, object]],
    csv_output_mode: str,
    gzip_compresslevel: int,
) -> None:
    for name in expand_csv_output_files([logical_name], csv_output_mode):
        write_csv(out_dir / name, rows, gzip_compresslevel=gzip_compresslevel)


def write_output_artifacts_parallel(
    *,
    out_dir: Path,
    csv_write_jobs: list[tuple[str, list[dict[str, object]]]],
    npz_write_jobs: list[tuple[str, list[object]]],
    csv_output_mode: str,
    gzip_compresslevel: int,
    artifact_write_workers: int,
) -> None:
    jobs: list[Callable[[], None]] = []
    for logical_name, rows in csv_write_jobs:
        jobs.append(
            lambda logical_name=logical_name, rows=rows: write_csv_artifact(
                out_dir,
                logical_name,
                rows,
                csv_output_mode,
                gzip_compresslevel,
            )
        )
    for name, matrices in npz_write_jobs:
        jobs.append(lambda name=name, matrices=matrices: write_sparse_npz(out_dir / name, matrices))  # type: ignore[arg-type]
    run_parallel_jobs(jobs, artifact_write_workers)


def write_raw_topology_shards(
    *,
    out_dir: Path,
    mapped_scans: list[object],
    csv_output_mode: str,
    shard_scan_count: int,
    gzip_compresslevel: int,
    artifact_write_workers: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    shard_size = max(1, int(shard_scan_count))
    chunks = [mapped_scans[index:index + shard_size] for index in range(0, len(mapped_scans), shard_size)]
    node_manifest: list[dict[str, object]] = []
    edge_manifest: list[dict[str, object]] = []
    jobs: list[Callable[[], None]] = []
    for logical_name, directory_name, row_attr, manifest_rows in (
        ("frontier_nodes_by_horizon.csv", "frontier_nodes_by_horizon_shards", "node_rows", node_manifest),
        ("frontier_edges_by_step.csv", "frontier_edges_by_step_shards", "edge_rows", edge_manifest),
    ):
        shard_count = len(chunks)
        for shard_index, chunk in enumerate(chunks):
            row_count = sum(len(getattr(scan.raw, row_attr)) for scan in chunk)  # type: ignore[attr-defined]
            first_scan_id = str(chunk[0].raw.scan_id) if chunk else ""  # type: ignore[attr-defined]
            last_scan_id = str(chunk[-1].raw.scan_id) if chunk else ""  # type: ignore[attr-defined]
            base_name = f"{directory_name}/part-{shard_index:05d}.csv"
            physical_names = expand_csv_output_files([base_name], csv_output_mode)
            for physical_name in physical_names:
                manifest_rows.append({
                    "logical_artifact_name": logical_name,
                    "physical_artifact_name": physical_name,
                    "artifact_storage_kind": "sharded_csv",
                    "shard_index": shard_index,
                    "shard_count": shard_count,
                    "shard_scan_count": len(chunk),
                    "row_count": row_count,
                    "first_scan_id": first_scan_id,
                    "last_scan_id": last_scan_id,
                    "csv_output_mode": csv_output_mode,
                    "gzip_compresslevel": gzip_compresslevel,
                })
                jobs.append(
                    lambda physical_name=physical_name, chunk=tuple(chunk), row_attr=row_attr: write_scan_row_shard(
                        out_dir,
                        physical_name,
                        chunk,
                        row_attr,
                        gzip_compresslevel,
                    )
                )
    run_parallel_jobs(jobs, artifact_write_workers)
    return node_manifest, edge_manifest


def write_scan_row_shard(
    out_dir: Path,
    physical_name: str,
    scans: tuple[object, ...],
    row_attr: str,
    gzip_compresslevel: int,
) -> None:
    rows = [row for scan in scans for row in getattr(scan.raw, row_attr)]  # type: ignore[attr-defined]
    write_csv(out_dir / physical_name, rows, gzip_compresslevel=gzip_compresslevel)


def run_parallel_jobs(jobs: list[Callable[[], None]], artifact_write_workers: int) -> None:
    if not jobs:
        return
    workers = max(1, min(len(jobs), int(artifact_write_workers)))
    if workers == 1:
        for job in jobs:
            job()
        return
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(job) for job in jobs]
        for future in as_completed(futures):
            future.result()


def expand_csv_output_files(logical_names: list[str], csv_output_mode: str) -> list[str]:
    if csv_output_mode == "plain":
        return list(logical_names)
    if csv_output_mode == "gzip":
        return [f"{name}.gz" for name in logical_names]
    if csv_output_mode == "both":
        return [item for name in logical_names for item in (name, f"{name}.gz")]
    raise ValueError(f"unknown csv output mode: {csv_output_mode}")


def csv_artifact_display_name(logical_name: str, csv_output_mode: str) -> str:
    if csv_output_mode == "gzip":
        return f"{logical_name}.gz"
    if csv_output_mode == "both":
        return f"{logical_name} / {logical_name}.gz"
    return logical_name


def raw_topology_report_artifacts(raw_topology_output_mode: str, csv_output_mode: str) -> list[str]:
    lines: list[str] = []
    if raw_topology_output_mode in {"sharded", "both"}:
        lines.extend([
            f"- `{csv_artifact_display_name('frontier_nodes_by_horizon_shard_manifest.csv', csv_output_mode)}`",
            "- `frontier_nodes_by_horizon_shards/part-*.csv[.gz]`",
            f"- `{csv_artifact_display_name('frontier_edges_by_step_shard_manifest.csv', csv_output_mode)}`",
            "- `frontier_edges_by_step_shards/part-*.csv[.gz]`",
        ])
    if raw_topology_output_mode in {"consolidated", "both"}:
        lines.extend([
            f"- `{csv_artifact_display_name('frontier_nodes_by_horizon.csv', csv_output_mode)}`",
            f"- `{csv_artifact_display_name('frontier_edges_by_step.csv', csv_output_mode)}`",
        ])
    return lines


def primary_csv_artifact_name(logical_name: str, csv_output_mode: str) -> str:
    if csv_output_mode == "gzip":
        return f"{logical_name}.gz"
    return logical_name


def output_row_count(out_dir: Path, name: str, csv_row_counts: dict[str, int]) -> int | str:
    if name in csv_row_counts:
        return csv_row_counts[name]
    logical_name = name.removesuffix(".gz") if name.endswith(".csv.gz") else name
    if logical_name in csv_row_counts:
        return csv_row_counts[logical_name]
    if name.endswith((".csv", ".csv.gz")):
        return csv_row_count(out_dir / name)
    return ""


def artifact_completeness_rows(
    *,
    node_rows: list[dict[str, object]],
    edge_rows: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for artifact_name, artifact_rows, status_field in (
        ("frontier_nodes_by_horizon.csv", node_rows, "node_artifact_status"),
        ("frontier_edges_by_step.csv", edge_rows, "edge_artifact_status"),
        ("frontier_profile_by_horizon.csv", profile_rows, "feature_status"),
    ):
        counts: dict[str, int] = {}
        for row in artifact_rows:
            status = str(row.get(status_field, "complete") or "complete")
            counts[status] = counts.get(status, 0) + 1
        for artifact_status, count in sorted(counts.items()):
            rows.append({
                "artifact_name": artifact_name,
                "status_field": status_field,
                "artifact_status": artifact_status,
                "row_count": count,
            })
    return rows


def progress_row(
    status: dict[str, object],
    started_perf: float,
    completed: list[object],
    errors: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "timestamp_utc": utc_now(),
        "elapsed_seconds": round(time.perf_counter() - started_perf, 3),
        "status": status.get("status", ""),
        "scans_submitted": status.get("scans_submitted", 0),
        "scans_completed": len(completed),
        "errors": len(errors),
    }


def parse_horizon_schedule(raw: str, horizon_max: int) -> tuple[int, ...]:
    token = str(raw or "").strip()
    if token in {"", "dense_to_32_plus_h128"}:
        values = list(range(0, min(32, horizon_max) + 1))
        values.extend([48, 64, 96, 128])
        return tuple(sorted({value for value in values if value <= horizon_max}))
    if token == "dense":
        return tuple(range(0, horizon_max + 1))
    return tuple(sorted({int(item.strip()) for item in token.split(",") if item.strip() and int(item.strip()) <= horizon_max}))


def parse_horizon_pairs(raw: str, horizon_max: int) -> tuple[tuple[int, int], ...]:
    if str(raw or "").strip():
        pairs: list[tuple[int, int]] = []
        for token in str(raw).split(","):
            item = token.strip()
            if not item:
                continue
            left, right = item.split("->", 1)
            pair = (int(left), int(right))
            if 0 <= pair[0] < pair[1] <= horizon_max:
                pairs.append(pair)
        return tuple(pairs)
    default = ((0, 1), (1, 2), (2, 4), (4, 8), (8, 16), (16, 24), (24, 32), (32, 48), (48, 64), (64, 96), (96, 128))
    return tuple(pair for pair in default if pair[1] <= horizon_max)


def validate_transport_modes(transport_output_mode: str, composition_residual_mode: str) -> None:
    if transport_output_mode == "adjacent_only" and composition_residual_mode != "none":
        raise ValueError("adjacent_only transport requires --composition-residual-mode none")
    if transport_output_mode != "full" and composition_residual_mode == "full":
        raise ValueError("full composition residuals require --transport-output-mode full")


def multiscale_pairs_for_modes(
    horizon_pairs: tuple[tuple[int, int], ...],
    transport_output_mode: str,
    composition_residual_mode: str,
) -> tuple[tuple[int, int], ...]:
    if transport_output_mode == "adjacent_only":
        return tuple()
    if transport_output_mode == "full":
        return expand_horizon_pair_closure(horizon_pairs)
    pairs = set(horizon_pairs)
    if composition_residual_mode == "selected":
        for source_h, _mid_h, target_h in selected_composition_triples(horizon_pairs):
            pairs.add((source_h, _mid_h))
            pairs.add((_mid_h, target_h))
            pairs.add((source_h, target_h))
    return tuple(sorted(pairs))


def composition_triples_for_mode(
    horizon_pairs: tuple[tuple[int, int], ...],
    composition_residual_mode: str,
) -> tuple[tuple[int, int, int], ...] | None:
    if composition_residual_mode == "none":
        return tuple()
    if composition_residual_mode == "full":
        return None
    return selected_composition_triples(horizon_pairs)


def selected_composition_triples(
    horizon_pairs: tuple[tuple[int, int], ...],
) -> tuple[tuple[int, int, int], ...]:
    horizons = sorted({value for pair in horizon_pairs for value in pair})
    return tuple(
        (horizons[index], horizons[index + 1], horizons[index + 2])
        for index in range(max(0, len(horizons) - 2))
    )


def expand_horizon_pair_closure(horizon_pairs: tuple[tuple[int, int], ...]) -> tuple[tuple[int, int], ...]:
    horizons = sorted({value for pair in horizon_pairs for value in pair})
    return tuple(
        (left, right)
        for left_index, left in enumerate(horizons)
        for right in horizons[left_index + 1 :]
        if left < right
    )


def parse_int_list(raw: str) -> list[int]:
    return [int(item.strip()) for item in str(raw or "").split(",") if item.strip()]


def parse_float_list(raw: str) -> list[float]:
    return [float(item.strip()) for item in str(raw or "").split(",") if item.strip()]


def handle_stop(_signum: int, _frame: object) -> None:
    global STOP_REQUESTED
    STOP_REQUESTED = True


def install_signal_handlers() -> None:
    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        signum = getattr(signal, name, None)
        if signum is not None:
            signal.signal(signum, handle_stop)


if __name__ == "__main__":
    main()
