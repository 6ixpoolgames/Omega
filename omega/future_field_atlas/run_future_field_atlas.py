"""Run the Future Field Atlas Phase 0/1 instrument smoke.

The runner is intentionally thin. Generation, frontier unfolding, topology
mapping, transport construction, and recovery analysis live in separate modules.
"""

from __future__ import annotations

import argparse
import signal
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from typing import Iterable

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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    install_signal_handlers()
    started_perf = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    groups = int(args.design_groups) if args.design_groups is not None else int(args.groups)
    horizon_schedule = parse_horizon_schedule(args.horizon_schedule, args.horizon_max)
    horizon_pairs = parse_horizon_pairs(args.horizon_pairs, args.horizon_max)
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
    write_all_outputs(args.out, completed, errors, progress, status, started_perf, horizon_pairs)


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
    write_csv(out_dir / "future_field_atlas_progress.csv", progress)
    write_csv(out_dir / "future_field_atlas_errors.csv", errors)


def write_all_outputs(
    out_dir: Path,
    scans: list[object],
    errors: list[dict[str, object]],
    progress: list[dict[str, object]],
    status: dict[str, object],
    started_perf: float,
    horizon_pairs: tuple[tuple[int, int], ...],
) -> None:
    mapped_scans = list(scans)
    node_rows = [row for scan in mapped_scans for row in scan.raw.node_rows]  # type: ignore[attr-defined]
    edge_rows = [row for scan in mapped_scans for row in scan.raw.edge_rows]  # type: ignore[attr-defined]
    profile_rows = [row for scan in mapped_scans for row in scan.profile_rows]  # type: ignore[attr-defined]
    membership_rows = [row for scan in mapped_scans for row in scan.membership_rows]  # type: ignore[attr-defined]
    boundary_rows = [row for scan in mapped_scans for row in scan.boundary_rows]  # type: ignore[attr-defined]
    adjacent = adjacent_transport_matrices(mapped_scans)  # type: ignore[arg-type]
    multiscale_pairs = expand_horizon_pair_closure(horizon_pairs)
    multiscale = multiscale_transport_matrices(mapped_scans, multiscale_pairs)  # type: ignore[arg-type]
    residual_rows = flow_composition_residual_rows(multiscale)
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

    output_files = [
        "future_field_atlas_manifest.json",
        "future_field_atlas_run_config.json",
        "future_field_atlas_status.json",
        "future_field_atlas_progress.csv",
        "future_field_atlas_errors.csv",
        "future_field_atlas_report.md",
        "formal_spec_manifest.csv",
        "condition_identity_manifest.csv",
        "scan_manifest.csv",
        "frontier_nodes_by_horizon.csv",
        "frontier_edges_by_step.csv",
        "frontier_profile_by_horizon.csv",
        "frontier_membership_timeseries.csv",
        "rank_boundary_geometry_by_horizon.csv",
        "raw_transport_matrices_adjacent.npz",
        "raw_transport_matrices_adjacent_manifest.csv",
        "raw_transport_matrices_multiscale.npz",
        "raw_transport_matrices_multiscale_manifest.csv",
        "transport_flow_composition_residuals.csv",
        "selection_operator_geometry_summary.csv",
        "rank_boundary_geometry_by_horizon_summary.csv",
        "rank_boundary_geometry_by_horizon_pair.csv",
        "reconstruction_audit_summary.csv",
        "artifact_completeness_summary.csv",
    ]
    write_csv(out_dir / "formal_spec_manifest.csv", spec_manifest_rows)
    write_csv(out_dir / "condition_identity_manifest.csv", condition_identity_rows)
    write_csv(out_dir / "scan_manifest.csv", scan_manifest)
    write_csv(out_dir / "frontier_nodes_by_horizon.csv", node_rows)
    write_csv(out_dir / "frontier_edges_by_step.csv", edge_rows)
    write_csv(out_dir / "frontier_profile_by_horizon.csv", profile_rows)
    write_csv(out_dir / "frontier_membership_timeseries.csv", membership_rows)
    write_csv(out_dir / "rank_boundary_geometry_by_horizon.csv", boundary_rows)
    write_sparse_npz(out_dir / "raw_transport_matrices_adjacent.npz", adjacent)
    write_csv(out_dir / "raw_transport_matrices_adjacent_manifest.csv", adjacent_manifest)
    write_sparse_npz(out_dir / "raw_transport_matrices_multiscale.npz", multiscale)
    write_csv(out_dir / "raw_transport_matrices_multiscale_manifest.csv", multiscale_manifest)
    write_csv(out_dir / "transport_flow_composition_residuals.csv", residual_rows)
    write_csv(out_dir / "selection_operator_geometry_summary.csv", operator_geometry_summary)
    write_csv(out_dir / "rank_boundary_geometry_by_horizon_summary.csv", rank_boundary_rows)
    write_csv(out_dir / "rank_boundary_geometry_by_horizon_pair.csv", boundary_pair_rows)
    write_csv(out_dir / "reconstruction_audit_summary.csv", reconstruction_rows)
    write_csv(out_dir / "artifact_completeness_summary.csv", completeness_rows)
    status["completed_utc"] = utc_now()
    status["elapsed_seconds"] = round(time.perf_counter() - started_perf, 3)
    status["frontier_node_rows"] = len(node_rows)
    status["frontier_edge_rows"] = len(edge_rows)
    status["selection_operator_geometry_rows"] = len(operator_geometry_summary)
    status["reconstruction_audit_passed"] = int(all(row.get("status") == "PASS" for row in reconstruction_rows))
    status["artifact_completeness_statuses"] = ",".join(
        sorted({str(row["artifact_status"]) for row in completeness_rows})
    )
    write_partial(out_dir, status, progress, errors, started_perf)
    write_report(out_dir, status, operator_geometry_summary, reconstruction_rows, completeness_rows)
    manifest = {
        **instrument_metadata(),
        "run_status": status.get("status"),
        "started_utc": status.get("started_utc"),
        "completed_utc": status.get("completed_utc"),
        "seed_policy": "deterministic base_seed plus group/fresh-seed offsets",
        "substrate_count": len({scan.raw.spec.substrate_id for scan in mapped_scans}),  # type: ignore[attr-defined]
        "frontier_count": len(mapped_scans),
        "horizon_schedule": sorted({row["horizon"] for row in profile_rows}) if profile_rows else [],
        "formal_spec_manifest": "formal_spec_manifest.csv",
        "condition_identity_manifest": "condition_identity_manifest.csv",
        "scan_manifest": "scan_manifest.csv",
        "reconstruction_audit_summary": "reconstruction_audit_summary.csv",
        "artifact_completeness_summary": "artifact_completeness_summary.csv",
        "output_files": [
            {
                "file": name,
                "exists": True if name == "future_field_atlas_manifest.json" else (out_dir / name).exists(),
                "row_count": csv_row_count(out_dir / name) if name.endswith(".csv") else "",
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
        "## Primary Artifacts",
        "",
        "- `frontier_nodes_by_horizon.csv`",
        "- `frontier_edges_by_step.csv`",
        "- `frontier_profile_by_horizon.csv`",
        "- `formal_spec_manifest.csv`",
        "- `condition_identity_manifest.csv`",
        "- `scan_manifest.csv`",
        "- `rank_boundary_geometry_by_horizon.csv`",
        "- `raw_transport_matrices_adjacent.npz`",
        "- `raw_transport_matrices_multiscale.npz`",
        "- `selection_operator_geometry_summary.csv`",
        "- `reconstruction_audit_summary.csv`",
        "- `artifact_completeness_summary.csv`",
    ]
    (out_dir / "future_field_atlas_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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
