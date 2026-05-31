"""Run horizon-transport response-surface instrumentation.

The runner builds directional horizon transport matrices from the Stage B-2
future-field substrate, applies matched detector nulls, classifies perturbation
responses, and writes machine-readable audit artifacts. It is not a promotion
or detection script for Omega, agency, identity, or value.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import signal
import time
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median, pstdev

import numpy as np

from .run_deformation_detector_sweep import stable_seed
from .run_focused_boundary_recurrence import float_or_zero, read_csv, write_csv
from .run_frontier_transform_stage_b2_mechanism_calibration import BASELINE_CONTROL
from .run_instrumentation_phase_a import build_holdout_split
from .run_stage_b2_spectral_future_field_geometry_smoke import (
    build_jobs,
    effective_rank,
    group_by,
    parse_float_list,
    run_batch,
    spectral_gap,
)
from .horizon_transport_contracts import (
    COMMON_OUTPUTS,
    DETECTOR_NULL_FAMILIES,
    DETECTOR_STATISTICS,
    INTERPRETATION_CONTROL_FAMILIES,
    MARGINAL_MATCHED_NULL_FAMILIES,
    MATCHED_NULL_SPEC_ID,
    PARENT_SPEC_ID,
    RUNNER_MODULE,
    STRUCTURE_DESTROYING_NULL_FAMILIES,
    active_spec_id,
    artifact_prefix,
    attach_horizon_pairs,
    errors_filename,
    manifest_filename,
    parse_horizon_pairs,
    progress_filename,
    report_filename,
    run_config_filename,
    run_kind,
    run_phase,
    status_filename,
    status_run_kind,
)
from .horizon_transport_response_taxonomy import (
    MEASUREMENT_LIMIT_RESPONSE_CLASSES,
    RESPONSE_CLASS_AMPLIFIED_ALIGNED,
    RESPONSE_CLASS_COLLAPSES,
    RESPONSE_CLASS_REOPENS,
    RESPONSE_CLASS_REROUTED,
    RESPONSE_CLASS_STABLE,
    RESPONSE_CLASS_WEAKENED,
    classify_response,
    is_interpretable_response,
    response_flags,
)
from .spectral_contracts import (
    CLAIM_BOUNDARY,
    LOCAL_ONLY_ARTIFACT_POLICY,
    instrument_metadata,
    output_manifest_rows,
    utc_now,
    write_json,
)


STOP_REQUESTED = False


@dataclass(frozen=True)
class TransportKey:
    condition_id: str
    actual_control_name: str
    mechanism_control_strength: float
    probe_key: str
    flow_mode: str
    source_horizon_band: str
    target_horizon_band: str
    H_a: int
    H_b: int


@dataclass
class TransportMatrix:
    key: TransportKey
    matrix_id: str
    row_items: list[str]
    column_items: list[str]
    matrix: np.ndarray
    transport_context_count: int
    transport_mass_total: float
    retained_transport_mass: float
    dropped_transport_mass: float
    raw_row_item_count: int
    raw_column_item_count: int
    singular_values: np.ndarray
    left_vectors: np.ndarray
    right_vectors: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 horizon-transport spectral response repair smoke.")
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--corrected", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/corrected_group_classification.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--out", type=Path, default=Path("results/local_runs/20260530_horizon_transport_spectral_response_repair"))
    parser.add_argument("--groups", type=int, default=20)
    parser.add_argument("--design-groups", type=int, default=1)
    parser.add_argument("--fresh-seeds-per-group", type=int, default=1)
    parser.add_argument("--start-samples-list", type=str, default="4")
    parser.add_argument("--probes", type=str, default="constraint_profile_hash,constraint_violation_count_plus_local_tuple")
    parser.add_argument("--roughness-seed-replicates", type=int, default=0)
    parser.add_argument("--small-edge-resample-strengths", type=str, default="0.0025,0.005")
    parser.add_argument("--asymmetry-multipliers", type=str, default="")
    parser.add_argument("--asymmetric-edge-flip-strengths", type=str, default="0.0025,0.005")
    parser.add_argument("--constraint-proxy-strengths", type=str, default="")
    parser.add_argument("--workers", type=int, default=7)
    parser.add_argument("--job-batch-size", type=int, default=2)
    parser.add_argument("--checkpoint-every-jobs", type=int, default=20)
    parser.add_argument("--max-runtime-seconds", type=int, default=7200)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=600)
    parser.add_argument("--max-items-per-context", type=int, default=64)
    parser.add_argument("--max-items-per-side", type=int, default=128)
    parser.add_argument("--min-item-count", type=int, default=1)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--null-replicates", type=int, default=5)
    parser.add_argument("--detector-null-min-pass-fraction", type=float, default=0.50)
    parser.add_argument("--detector-null-min-percentile", type=float, default=0.80)
    parser.add_argument("--fixture-smoke", action="store_true", help="Run synthetic horizon-transport fixtures instead of empirical jobs.")
    parser.add_argument("--expansion-smoke", action="store_true", help="Write expansion-smoke outputs and readiness labels.")
    parser.add_argument("--h128-scaleup", action="store_true", help="Write H128 response-surface outputs and readiness labels.")
    parser.add_argument("--horizon-pairs", type=str, default="", help="Comma-separated horizon pairs like 0->1,1->2. Defaults to H128 pairs when --h128-scaleup is set, otherwise H32 pairs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    install_signal_handlers()
    started = time.perf_counter()
    repo_root = Path(__file__).resolve().parents[2]
    args.out.mkdir(parents=True, exist_ok=True)
    kind = run_kind(args)
    metadata = {
        **instrument_metadata(active_spec_id(args), RUNNER_MODULE, repo_root),
        "parent_spec_id": PARENT_SPEC_ID,
        "matched_null_spec_id": MATCHED_NULL_SPEC_ID,
    }
    probes = tuple(item.strip() for item in args.probes.split(",") if item.strip())
    starts = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    horizon_pairs = parse_horizon_pairs(args.horizon_pairs, use_h128=args.h128_scaleup)
    if args.fixture_smoke:
        jobs: list[dict[str, object]] = []
    else:
        groups, split_rows = build_holdout_split(args)
        anchors = {row.get("anchor_id", ""): row for row in read_csv(args.source_run / "atlas_band_selection.csv")}
        jobs = build_jobs(args, groups, split_rows, anchors, probes, starts)
        attach_horizon_pairs(jobs, horizon_pairs)
    write_json(args.out / run_config_filename(kind), {
        **metadata,
        **vars(args),
        "job_count": len(jobs),
        "run_kind": kind,
        "horizon_pairs": [f"{left}->{right}" for left, right in horizon_pairs],
        "claim_boundary": CLAIM_BOUNDARY,
    })
    status: dict[str, object] = {
        **metadata,
        "status": "RUNNING",
        "phase": run_phase(kind),
        "run_kind": kind,
        "artifact_prefix": artifact_prefix(kind),
        "report_file": report_filename(kind),
        "started_utc": utc_now(),
        "out_dir": str(args.out),
        "jobs_requested": len(jobs),
        "jobs_submitted": 0,
        "jobs_completed": 0,
        "jobs_cancelled": 0,
        "pending_jobs_remaining": len(jobs),
        "workers": args.workers,
        "job_batch_size": args.job_batch_size,
        "holdout_scoring_count": 0,
        "n6_run_count": 0,
        "alphabet_expansion_count": 0,
        "candidate_promotion_enabled": False,
        "artifact_policy": LOCAL_ONLY_ARTIFACT_POLICY,
        "fixture_smoke_enabled": bool(args.fixture_smoke),
        "expansion_smoke_enabled": bool(args.expansion_smoke),
        "h128_scaleup_enabled": bool(args.h128_scaleup),
        "horizon_pairs": [f"{left}->{right}" for left, right in horizon_pairs],
    }
    write_json(args.out / status_filename(kind), status)
    if args.fixture_smoke:
        rows: list[dict[str, object]] = []
        errors: list[dict[str, object]] = []
        checkpoints = [checkpoint_row(status, started, 0, 0)]
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "fixture_smoke_completed"
        matrices = build_fixture_matrices()
    else:
        rows, errors, checkpoints = run_jobs(args, jobs, status, started)
        matrices = build_transport_matrices(rows, args)
    outputs = compute_outputs(matrices, rows, args)
    write_outputs(args.out, outputs, errors, checkpoints, status, started)


def handle_stop(_signum: int, _frame: object) -> None:
    global STOP_REQUESTED
    STOP_REQUESTED = True


def install_signal_handlers() -> None:
    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        signum = getattr(signal, name, None)
        if signum is not None:
            signal.signal(signum, handle_stop)


def run_jobs(
    args: argparse.Namespace,
    jobs: list[dict[str, object]],
    status: dict[str, object],
    started: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    pending = [jobs[index : index + max(1, args.job_batch_size)] for index in range(0, len(jobs), max(1, args.job_batch_size))]
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    checkpoints: list[dict[str, object]] = []
    last_checkpoint = 0
    futures = {}
    cancelled_job_count = 0
    executor = ProcessPoolExecutor(max_workers=max(1, args.workers))
    try:
        while pending or futures:
            if STOP_REQUESTED:
                status["status"] = "PARTIAL_INTERRUPTED"
                status["finalization_reason"] = "signal_stop_requested"
                break
            remaining = args.max_runtime_seconds - (time.perf_counter() - started)
            if remaining <= args.shutdown_cushion_seconds:
                status["status"] = "PARTIAL_TIME_LIMIT_REACHED"
                status["finalization_reason"] = "shutdown_cushion_reached"
                break
            while pending and len(futures) < max(1, args.workers):
                batch = pending.pop(0)
                futures[executor.submit(run_batch, batch, args.max_items_per_context)] = batch
                status["jobs_submitted"] = int(status["jobs_submitted"]) + len(batch)
            status["pending_jobs_remaining"] = sum(len(batch) for batch in pending) + sum(len(batch) for batch in futures.values())
            done, _pending_futures = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                batch = futures.pop(future)
                try:
                    _contexts, metric_rows, batch_errors, completed = future.result()
                except Exception as exc:  # noqa: BLE001
                    metric_rows = []
                    batch_errors = [{"job_id": ",".join(str(job.get("job_id", "")) for job in batch), "error": repr(exc)}]
                    completed = len(batch)
                rows.extend(metric_rows)
                errors.extend(batch_errors)
                status["jobs_completed"] = int(status["jobs_completed"]) + completed
                status["pending_jobs_remaining"] = sum(len(batch) for batch in pending) + sum(len(batch) for batch in futures.values())
                if int(status["jobs_completed"]) - last_checkpoint >= max(1, args.checkpoint_every_jobs):
                    checkpoints.append(checkpoint_row(status, started, len(rows), len(errors)))
                    last_checkpoint = int(status["jobs_completed"])
                    write_partial(args.out, status, started, checkpoints, errors)
    finally:
        if futures:
            cancelled_job_count = sum(len(batch) for batch in futures.values())
            for future in futures:
                future.cancel()
            status["jobs_cancelled"] = cancelled_job_count
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    status["pending_jobs_remaining"] = sum(len(batch) for batch in pending) + cancelled_job_count
    if status.get("status") == "RUNNING":
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "all_jobs_completed"
    checkpoints.append(checkpoint_row(status, started, len(rows), len(errors)))
    write_partial(args.out, status, started, checkpoints, errors)
    return rows, errors, checkpoints


def checkpoint_row(status: dict[str, object], started: float, row_count: int, error_count: int) -> dict[str, object]:
    return {
        "timestamp_utc": utc_now(),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "status": status.get("status", ""),
        "jobs_submitted": status.get("jobs_submitted", 0),
        "jobs_completed": status.get("jobs_completed", 0),
        "jobs_cancelled": status.get("jobs_cancelled", 0),
        "pending_jobs_remaining": status.get("pending_jobs_remaining", 0),
        "transport_metric_rows": row_count,
        "errors": error_count,
    }


def write_partial(out_dir: Path, status: dict[str, object], started: float, checkpoints: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    kind = status_run_kind(status)
    write_json(out_dir / status_filename(kind), status)
    write_csv(out_dir / progress_filename(kind), checkpoints)
    write_csv(out_dir / errors_filename(kind), errors)


def build_transport_matrices(rows: list[dict[str, object]], args: argparse.Namespace) -> list[TransportMatrix]:
    accumulators: dict[TransportKey, Counter[tuple[str, str]]] = defaultdict(Counter)
    context_counts: Counter[TransportKey] = Counter()
    row_counts: dict[TransportKey, Counter[str]] = defaultdict(Counter)
    col_counts: dict[TransportKey, Counter[str]] = defaultdict(Counter)
    for row in rows:
        if row.get("row_kind") not in {"baseline", "mechanism_control"}:
            continue
        try:
            ha = int(float_or_zero(row.get("H_a")))
            hb = int(float_or_zero(row.get("H_b")))
        except ValueError:
            continue
        key = TransportKey(
            condition_id=str(row.get("condition_id", "")),
            actual_control_name=str(row.get("actual_control_name", "")),
            mechanism_control_strength=float_or_zero(row.get("mechanism_control_strength")),
            probe_key=str(row.get("probe_key", "")),
            flow_mode=str(row.get("flow_mode", "")),
            source_horizon_band=horizon_point_band(ha),
            target_horizon_band=horizon_point_band(hb),
            H_a=ha,
            H_b=hb,
        )
        transitions = parse_transition_distribution(row.get("transition_distribution_json", "{}"))
        if not transitions:
            continue
        context_counts[key] += 1
        for (left, right), count in transitions.items():
            accumulators[key][(left, right)] += count
            row_counts[key][left] += count
            col_counts[key][right] += count
    matrices: list[TransportMatrix] = []
    for key, counts in accumulators.items():
        retained_rows = [item for item, count in row_counts[key].most_common(args.max_items_per_side) if count >= args.min_item_count]
        retained_cols = [item for item, count in col_counts[key].most_common(args.max_items_per_side) if count >= args.min_item_count]
        if len(retained_rows) < 2 or len(retained_cols) < 2:
            continue
        row_index = {item: index for index, item in enumerate(retained_rows)}
        col_index = {item: index for index, item in enumerate(retained_cols)}
        matrix = np.zeros((len(retained_rows), len(retained_cols)), dtype=np.float64)
        total_mass = float(sum(counts.values()))
        retained_mass = 0.0
        for (left, right), count in counts.items():
            if left not in row_index or right not in col_index:
                continue
            matrix[row_index[left], col_index[right]] += float(count)
            retained_mass += float(count)
        if retained_mass <= 0:
            continue
        left_vectors, singular_values, right_t = np.linalg.svd(matrix, full_matrices=False)
        matrices.append(TransportMatrix(
            key=key,
            matrix_id=transport_matrix_id(key),
            row_items=retained_rows,
            column_items=retained_cols,
            matrix=matrix,
            transport_context_count=context_counts[key],
            transport_mass_total=total_mass,
            retained_transport_mass=retained_mass,
            dropped_transport_mass=max(0.0, total_mass - retained_mass),
            raw_row_item_count=len(row_counts[key]),
            raw_column_item_count=len(col_counts[key]),
            singular_values=singular_values,
            left_vectors=left_vectors,
            right_vectors=right_t.T,
        ))
    return matrices


def parse_transition_distribution(raw: object) -> Counter[tuple[str, str]]:
    out: Counter[tuple[str, str]] = Counter()
    try:
        payload = json.loads(str(raw))
    except json.JSONDecodeError:
        return out
    if not isinstance(payload, dict):
        return out
    for key, value in payload.items():
        if "->" not in str(key):
            continue
        left, right = str(key).split("->", 1)
        out[(left, right)] += int(float_or_zero(value))
    return out


def build_fixture_matrices() -> list[TransportMatrix]:
    row_items = ["route_A0", "route_A1", "route_B0", "route_B1"]
    column_items = ["dest_A0", "dest_A1", "dest_B0", "dest_B1"]
    corridor_rows = ["corridor_open", "corridor_side", "corridor_reentry", "corridor_sink"]
    corridor_cols = ["stable_open", "stable_side", "stable_reentry", "stable_sink"]
    trap_rows = ["trap_entry", "trap_loop", "trap_exit", "trap_recovery"]
    trap_cols = ["downstream_entry", "downstream_loop", "downstream_exit", "downstream_recovery"]
    response_rows = [f"r{i}" for i in range(8)]
    response_cols = [f"c{i}" for i in range(8)]
    fixtures = [
        (
            TransportKey("fixture_block_transport_signal", BASELINE_CONTROL, 0.0, "fixture_block_probe", "fixture_flow", "middle", "middle", 4, 16),
            row_items,
            column_items,
            np.asarray([
                [12, 8, 0, 0],
                [8, 12, 0, 0],
                [0, 0, 12, 8],
                [0, 0, 8, 12],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_marginal_fakeout", BASELINE_CONTROL, 0.0, "fixture_fakeout_probe", "fixture_flow", "middle", "middle", 4, 16),
            row_items,
            column_items,
            np.asarray([
                [16, 12, 8, 4],
                [12, 9, 6, 3],
                [8, 6, 4, 2],
                [4, 3, 2, 1],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_corridor_baseline", BASELINE_CONTROL, 0.0, "fixture_corridor_probe", "fixture_flow", "middle", "middle", 4, 16),
            corridor_rows,
            corridor_cols,
            np.asarray([
                [18, 2, 1, 0],
                [2, 15, 2, 1],
                [1, 2, 14, 2],
                [0, 1, 2, 12],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_corridor_stable_response", "fixture_nonlethal_corridor_jitter", 0.05, "fixture_corridor_probe", "fixture_flow", "middle", "middle", 4, 16),
            corridor_rows,
            corridor_cols,
            np.asarray([
                [18, 2, 1, 0],
                [2, 14, 3, 1],
                [1, 2, 14, 2],
                [0, 1, 2, 12],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_trap_baseline", BASELINE_CONTROL, 0.0, "fixture_trap_probe", "fixture_flow", "middle", "middle", 4, 16),
            trap_rows,
            trap_cols,
            np.asarray([
                [16, 3, 1, 0],
                [3, 18, 2, 0],
                [1, 2, 12, 3],
                [0, 0, 3, 10],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_trap_collapse_response", "fixture_nonlethal_trap_collapse", 0.80, "fixture_trap_probe", "fixture_flow", "middle", "middle", 4, 16),
            trap_rows,
            trap_cols,
            np.asarray([
                [3.2, 0.6, 0.2, 0],
                [0.6, 3.6, 0.4, 0],
                [0.2, 0.4, 2.4, 0.6],
                [0, 0, 0.6, 2.0],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_amplified_aligned_baseline", BASELINE_CONTROL, 0.0, "fixture_amplified_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [12, 2, 1, 0, 0, 0, 0, 0],
                [2, 10, 1, 0, 0, 0, 0, 0],
                [1, 1, 8, 1, 0, 0, 0, 0],
                [0, 0, 1, 6, 1, 0, 0, 0],
                [0, 0, 0, 1, 5, 1, 0, 0],
                [0, 0, 0, 0, 1, 4, 1, 0],
                [0, 0, 0, 0, 0, 1, 3, 1],
                [0, 0, 0, 0, 0, 0, 1, 2],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_amplified_aligned_response", "fixture_nonlethal_amplify", 0.20, "fixture_amplified_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [15.6, 2.6, 1.3, 0, 0, 0, 0, 0],
                [2.6, 13.0, 1.3, 0, 0, 0, 0, 0],
                [1.3, 1.3, 10.4, 1.3, 0, 0, 0, 0],
                [0, 0, 1.3, 7.8, 1.3, 0, 0, 0],
                [0, 0, 0, 1.3, 6.5, 1.3, 0, 0],
                [0, 0, 0, 0, 1.3, 5.2, 1.3, 0],
                [0, 0, 0, 0, 0, 1.3, 3.9, 1.3],
                [0, 0, 0, 0, 0, 0, 1.3, 2.6],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_weakened_baseline", BASELINE_CONTROL, 0.0, "fixture_weakened_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [12, 2, 1, 0, 0, 0, 0, 0],
                [2, 10, 1, 0, 0, 0, 0, 0],
                [1, 1, 8, 1, 0, 0, 0, 0],
                [0, 0, 1, 6, 1, 0, 0, 0],
                [0, 0, 0, 1, 5, 1, 0, 0],
                [0, 0, 0, 0, 1, 4, 1, 0],
                [0, 0, 0, 0, 0, 1, 3, 1],
                [0, 0, 0, 0, 0, 0, 1, 2],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_weakened_response", "fixture_nonlethal_weaken", 0.30, "fixture_weakened_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [8.4, 1.4, 0.7, 0, 0, 0, 0, 0],
                [1.4, 7.0, 0.7, 0, 0, 0, 0, 0],
                [0.7, 0.7, 5.6, 0.7, 0, 0, 0, 0],
                [0, 0, 0.7, 4.2, 0.7, 0, 0, 0],
                [0, 0, 0, 0.7, 3.5, 0.7, 0, 0],
                [0, 0, 0, 0, 0.7, 2.8, 0.7, 0],
                [0, 0, 0, 0, 0, 0.7, 2.1, 0.7],
                [0, 0, 0, 0, 0, 0, 0.7, 1.4],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_rerouted_baseline", BASELINE_CONTROL, 0.0, "fixture_rerouted_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [40, 1, 0, 0, 0, 0, 0, 0],
                [1, 34, 1, 0, 0, 0, 0, 0],
                [0, 1, 28, 1, 0, 0, 0, 0],
                [0, 0, 1, 22, 1, 0, 0, 0],
                [0, 0, 0, 1, 16, 1, 0, 0],
                [0, 0, 0, 0, 1, 10, 1, 0],
                [0, 0, 0, 0, 0, 1, 6, 1],
                [0, 0, 0, 0, 0, 0, 1, 4],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_rerouted_response", "fixture_nonlethal_reroute", 0.20, "fixture_rerouted_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [0, 0, 0, 0, 0, 0, 1, 40],
                [0, 0, 0, 0, 0, 1, 34, 1],
                [0, 0, 0, 0, 1, 28, 1, 0],
                [0, 0, 0, 1, 22, 1, 0, 0],
                [0, 0, 1, 16, 1, 0, 0, 0],
                [0, 1, 10, 1, 0, 0, 0, 0],
                [1, 6, 1, 0, 0, 0, 0, 0],
                [4, 1, 0, 0, 0, 0, 0, 0],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_reopens_baseline", BASELINE_CONTROL, 0.0, "fixture_reopens_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [44, 0, 0, 0, 0, 0, 0, 0],
                [0, 12, 0, 0, 0, 0, 0, 0],
                [0, 0, 8, 0, 0, 0, 0, 0],
                [0, 0, 0, 4, 0, 0, 0, 0],
                [0, 0, 0, 0, 2, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 1],
            ], dtype=np.float64),
        ),
        (
            TransportKey("fixture_reopens_response", "fixture_nonlethal_reopens", 0.20, "fixture_reopens_probe", "fixture_flow", "middle", "downstream", 16, 24),
            response_rows,
            response_cols,
            np.asarray([
                [8, 3, 3, 3, 3, 2, 2, 2],
                [3, 8, 3, 3, 3, 2, 2, 2],
                [3, 3, 8, 3, 3, 2, 2, 2],
                [3, 3, 3, 8, 3, 2, 2, 2],
                [3, 3, 3, 3, 8, 2, 2, 2],
                [2, 2, 2, 2, 2, 6, 2, 2],
                [2, 2, 2, 2, 2, 2, 6, 2],
                [2, 2, 2, 2, 2, 2, 2, 6],
            ], dtype=np.float64) * 1.3,
        ),
    ]
    return [fixture_transport_matrix(key, rows, cols, values) for key, rows, cols, values in fixtures]


def fixture_transport_matrix(key: TransportKey, rows: list[str], cols: list[str], values: np.ndarray) -> TransportMatrix:
    left_vectors, singular_values, right_t = np.linalg.svd(values, full_matrices=False)
    total = float(np.sum(values))
    return TransportMatrix(
        key=key,
        matrix_id=transport_matrix_id(key),
        row_items=list(rows),
        column_items=list(cols),
        matrix=values,
        transport_context_count=1,
        transport_mass_total=total,
        retained_transport_mass=total,
        dropped_transport_mass=0.0,
        raw_row_item_count=len(rows),
        raw_column_item_count=len(cols),
        singular_values=singular_values,
        left_vectors=left_vectors,
        right_vectors=right_t.T,
    )


def compute_outputs(matrices: list[TransportMatrix], rows: list[dict[str, object]], args: argparse.Namespace) -> dict[str, list[dict[str, object]]]:
    manifest = matrix_manifest_rows(matrices)
    row_items = row_item_manifest_rows(matrices)
    column_items = column_item_manifest_rows(matrices)
    coverage = coverage_rows(matrices)
    summary = matrix_summary_rows(matrices, args)
    svd = svd_rows(matrices, args)
    participation = participation_rows(matrices, args)
    entropy = entropy_rows(matrices)
    null_anatomy = detector_null_anatomy_rows(matrices, args)
    null_summary = detector_null_summary_rows(null_anatomy, args)
    preliminary_null_gates = detector_null_gate_rows(null_summary, matrices, args, [])
    perturb_manifest, response_summary, response_classification = perturbation_response_rows(matrices, preliminary_null_gates, args)
    fixture_results = fixture_result_rows(null_anatomy, response_classification)
    response_fixture_summary: list[dict[str, object]] = []
    if args.h128_scaleup and not args.fixture_smoke:
        fixture_matrices = build_fixture_matrices()
        fixture_null_anatomy = detector_null_anatomy_rows(fixture_matrices, args)
        fixture_null_summary = detector_null_summary_rows(fixture_null_anatomy, args)
        fixture_gates = detector_null_gate_rows(fixture_null_summary, fixture_matrices, args, [])
        _fixture_manifest, fixture_response_summary, fixture_response_classification = perturbation_response_rows(fixture_matrices, fixture_gates, args)
        fixture_results = fixture_result_rows(fixture_null_anatomy, fixture_response_classification)
        response_fixture_summary = fixture_response_classification
    elif args.fixture_smoke:
        response_fixture_summary = response_classification
    null_gates = detector_null_gate_rows(null_summary, matrices, args, fixture_results)
    subspace_alignment = horizon_pair_alignment_rows(matrices, args)
    matched_marginal = matched_marginal_summary_rows(null_anatomy, args)
    saturation = terminal_saturation_rows(matrices)
    saturation_by_horizon_pair = saturation_by_horizon_pair_rows(saturation)
    response_flags = response_flag_rows(response_classification, saturation)
    response_by_strength_horizon = response_class_by_strength_and_horizon_rows(response_classification)
    threshold_table = horizon_response_threshold_rows(response_classification, saturation)
    context_recommendation = context_recommendation_rows(summary, matched_marginal, response_classification)
    by_probe = aggregate_context_summary_rows(context_recommendation, ("probe_key",), "probe_key")
    by_flow_mode = aggregate_context_summary_rows(context_recommendation, ("flow_mode",), "flow_mode")
    by_horizon_pair = aggregate_context_summary_rows(context_recommendation, ("source_horizon_band", "target_horizon_band", "H_a", "H_b"), "horizon_pair")
    return {
        "manifest": manifest,
        "row_items": row_items,
        "column_items": column_items,
        "coverage": coverage,
        "summary": summary,
        "svd": svd,
        "participation": participation,
        "entropy": entropy,
        "null_anatomy": null_anatomy,
        "null_summary": null_summary,
        "null_gates": null_gates,
        "matched_marginal": matched_marginal,
        "fixture_results": fixture_results,
        "perturb_manifest": perturb_manifest,
        "response_summary": response_summary,
        "response_classification": response_classification,
        "response_flags": response_flags,
        "response_by_strength_horizon": response_by_strength_horizon,
        "threshold_table": threshold_table,
        "saturation": saturation,
        "saturation_by_horizon_pair": saturation_by_horizon_pair,
        "response_fixture_summary": response_fixture_summary,
        "subspace_alignment": subspace_alignment,
        "by_probe": by_probe,
        "by_flow_mode": by_flow_mode,
        "by_horizon_pair": by_horizon_pair,
        "context_recommendation": context_recommendation,
    }


def matrix_manifest_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    return [{
        **key_row(matrix.key),
        "matrix_id": matrix.matrix_id,
        "matrix_family": "horizon_transport",
        "row_item_count": len(matrix.row_items),
        "column_item_count": len(matrix.column_items),
        "transport_context_count": matrix.transport_context_count,
        "transport_mass_total": matrix.transport_mass_total,
        "coverage": matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total),
        "normalization_kind": "transport_count",
        **intervention_taxonomy(matrix.key),
    } for matrix in matrices]


def row_item_manifest_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for matrix in matrices:
        row_mass = matrix.matrix.sum(axis=1)
        total = float(row_mass.sum())
        for index, item in enumerate(matrix.row_items):
            rows.append({**key_row(matrix.key), "matrix_id": matrix.matrix_id, "row_item": item, "row_item_index": index, "row_transport_mass": float(row_mass[index]), "row_mass_share": float(row_mass[index]) / max(1.0, total)})
    return rows


def column_item_manifest_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for matrix in matrices:
        col_mass = matrix.matrix.sum(axis=0)
        total = float(col_mass.sum())
        for index, item in enumerate(matrix.column_items):
            rows.append({**key_row(matrix.key), "matrix_id": matrix.matrix_id, "column_item": item, "column_item_index": index, "column_transport_mass": float(col_mass[index]), "column_mass_share": float(col_mass[index]) / max(1.0, total)})
    return rows


def coverage_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    return [{
        **key_row(matrix.key),
        "matrix_id": matrix.matrix_id,
        "raw_row_item_count": matrix.raw_row_item_count,
        "raw_column_item_count": matrix.raw_column_item_count,
        "retained_row_item_count": len(matrix.row_items),
        "retained_column_item_count": len(matrix.column_items),
        "transport_mass_total": matrix.transport_mass_total,
        "retained_transport_mass": matrix.retained_transport_mass,
        "dropped_transport_mass": matrix.dropped_transport_mass,
        "coverage": matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total),
    } for matrix in matrices]


def matrix_summary_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    rows = []
    for matrix in matrices:
        singular = matrix.singular_values
        row_mass = matrix.matrix.sum(axis=1)
        col_mass = matrix.matrix.sum(axis=0)
        rows.append({
            **key_row(matrix.key),
            "matrix_id": matrix.matrix_id,
            "matrix_family": "horizon_transport",
            "row_item_count": len(matrix.row_items),
            "column_item_count": len(matrix.column_items),
            "transport_context_count": matrix.transport_context_count,
            "transport_mass_total": matrix.transport_mass_total,
            "positive_or_nonzero_spectral_mass": float(np.sum(singular)),
            "effective_rank": effective_rank(singular),
            "spectral_gap_k": spectral_gap(singular, args.top_k),
            "left_subspace_participation": vector_participation(matrix.left_vectors[:, 0]) if matrix.left_vectors.size else 0.0,
            "right_subspace_participation": vector_participation(matrix.right_vectors[:, 0]) if matrix.right_vectors.size else 0.0,
            "left_loading_entropy": entropy_from_values(row_mass),
            "right_loading_entropy": entropy_from_values(col_mass),
            "left_top_item_mass_share": top_share(row_mass, 1),
            "right_top_item_mass_share": top_share(col_mass, 1),
            "transport_entropy": entropy_from_values(matrix.matrix.flatten()),
            "transport_concentration": top_share(matrix.matrix.flatten(), 1),
            "marginal_residual_fraction": marginal_residual_fraction(matrix.matrix),
            "coverage": matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total),
            "normalization_kind": "transport_count",
            **intervention_taxonomy(matrix.key),
        })
    return rows


def svd_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for matrix in matrices:
        for rank, value in enumerate(matrix.singular_values[: args.top_k], start=1):
            rows.append({**key_row(matrix.key), "matrix_id": matrix.matrix_id, "rank": rank, "singular_value": float(value), "singular_value_share": float(value) / max(1e-12, float(np.sum(matrix.singular_values)))})
    return rows


def participation_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for matrix in matrices:
        for rank in range(min(args.top_k, len(matrix.singular_values))):
            rows.append({
                **key_row(matrix.key),
                "matrix_id": matrix.matrix_id,
                "rank": rank + 1,
                "left_participation_ratio": vector_participation(matrix.left_vectors[:, rank]),
                "right_participation_ratio": vector_participation(matrix.right_vectors[:, rank]),
                "singular_value": float(matrix.singular_values[rank]),
            })
    return rows


def entropy_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    return [{
        **key_row(matrix.key),
        "matrix_id": matrix.matrix_id,
        "transport_entropy": entropy_from_values(matrix.matrix.flatten()),
        "row_entropy": entropy_from_values(matrix.matrix.sum(axis=1)),
        "column_entropy": entropy_from_values(matrix.matrix.sum(axis=0)),
        "transport_concentration": top_share(matrix.matrix.flatten(), 1),
        "top_5_transport_share": top_share(matrix.matrix.flatten(), 5),
    } for matrix in matrices]


def detector_null_anatomy_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    baseline = [matrix for matrix in matrices if matrix.key.actual_control_name == BASELINE_CONTROL]
    pool_by_probe_flow = group_matrices(baseline, ("probe_key", "flow_mode"))
    rows: list[dict[str, object]] = []
    for matrix in baseline:
        for null_family in DETECTOR_NULL_FAMILIES:
            null_values_by_stat: dict[str, list[float]] = defaultdict(list)
            for replicate in range(max(1, args.null_replicates)):
                rng = random.Random(stable_seed(f"horizon_transport_null|{matrix.matrix_id}|{null_family}|{replicate}"))
                null_matrix = make_null_matrix(matrix, null_family, pool_by_probe_flow, rng)
                for stat in DETECTOR_STATISTICS:
                    null_values_by_stat[stat].append(transport_stat(null_matrix, stat))
            for stat in DETECTOR_STATISTICS:
                observed = transport_stat(matrix.matrix, stat)
                null_values = null_values_by_stat[stat]
                percentile = sum(value <= observed for value in null_values) / max(1, len(null_values))
                threshold = float(args.detector_null_min_percentile)
                passed = percentile >= threshold
                category = null_category(null_family)
                rows.append({
                    **key_row(matrix.key),
                    "matrix_id": matrix.matrix_id,
                    "null_family": null_family,
                    "null_category": category,
                    "observed_statistic": stat,
                    "observed_statistic_value": observed,
                    "null_mean": mean(null_values) if null_values else "",
                    "null_std": pstdev(null_values) if len(null_values) > 1 else 0.0 if null_values else "",
                    "null_max": max(null_values) if null_values else "",
                    "observed_percentile_vs_null": percentile,
                    "expected_direction": expected_null_direction(category),
                    "separation_margin": percentile - threshold,
                    "null_gate_passed": int(passed),
                    "failure_interpretation": null_failure_interpretation(matrix, category, percentile, threshold, len(null_values)),
                })
    return rows


def make_null_matrix(
    matrix: TransportMatrix,
    null_family: str,
    pool_by_probe_flow: dict[tuple[object, ...], list[TransportMatrix]],
    rng: random.Random,
) -> np.ndarray:
    values = np.asarray(matrix.matrix, dtype=np.float64)
    if null_family == "row_marginal_matched_transport_null":
        return row_marginal_matched_matrix(values, rng)
    if null_family == "column_marginal_matched_transport_null":
        return column_marginal_matched_matrix(values, rng)
    if null_family == "row_column_marginal_matched_transport_null":
        return row_column_marginal_matched_matrix(values, rng)
    if null_family == "label_shuffle_transport_interpretation_control":
        row_order = list(range(values.shape[0]))
        col_order = list(range(values.shape[1]))
        rng.shuffle(row_order)
        rng.shuffle(col_order)
        return values[row_order, :][:, col_order]
    if null_family == "horizon_pair_shuffle_transport_null":
        pool = [
            item for item in pool_by_probe_flow.get((matrix.key.probe_key, matrix.key.flow_mode), [])
            if item.matrix_id != matrix.matrix_id and item.matrix.shape == matrix.matrix.shape
        ]
        if pool:
            return np.asarray(rng.choice(pool).matrix, dtype=np.float64)
    flat = list(values.flatten())
    rng.shuffle(flat)
    return np.asarray(flat, dtype=np.float64).reshape(values.shape)


def row_marginal_matched_matrix(values: np.ndarray, rng: random.Random) -> np.ndarray:
    row_sums = values.sum(axis=1)
    col_sums = values.sum(axis=0)
    total = float(col_sums.sum())
    if total <= 0:
        return np.zeros_like(values, dtype=np.float64)
    probs = np.asarray(col_sums, dtype=np.float64) / total
    np_rng = np.random.default_rng(rng.randrange(0, 2**32 - 1))
    out = np.zeros_like(values, dtype=np.float64)
    for index, row_total in enumerate(row_sums):
        count = max(0, int(round(float(row_total))))
        if count <= 0:
            continue
        sample = np_rng.multinomial(count, probs)
        out[index, :] = sample
        if abs(float(row_total) - count) > 1e-9:
            out[index, :] *= float(row_total) / max(1.0, float(count))
    return out


def column_marginal_matched_matrix(values: np.ndarray, rng: random.Random) -> np.ndarray:
    row_sums = values.sum(axis=1)
    col_sums = values.sum(axis=0)
    total = float(row_sums.sum())
    if total <= 0:
        return np.zeros_like(values, dtype=np.float64)
    probs = np.asarray(row_sums, dtype=np.float64) / total
    np_rng = np.random.default_rng(rng.randrange(0, 2**32 - 1))
    out = np.zeros_like(values, dtype=np.float64)
    for index, col_total in enumerate(col_sums):
        count = max(0, int(round(float(col_total))))
        if count <= 0:
            continue
        sample = np_rng.multinomial(count, probs)
        out[:, index] = sample
        if abs(float(col_total) - count) > 1e-9:
            out[:, index] *= float(col_total) / max(1.0, float(count))
    return out


def row_column_marginal_matched_matrix(values: np.ndarray, rng: random.Random) -> np.ndarray:
    row_sums = values.sum(axis=1)
    col_sums = values.sum(axis=0)
    total = float(row_sums.sum())
    if total <= 0:
        return np.zeros_like(values, dtype=np.float64)
    np_rng = np.random.default_rng(rng.randrange(0, 2**32 - 1))
    out = np_rng.random(values.shape) + 1e-6
    for _ in range(80):
        current_rows = out.sum(axis=1)
        out *= np.divide(row_sums, current_rows, out=np.zeros_like(row_sums), where=current_rows > 0)[:, None]
        current_cols = out.sum(axis=0)
        out *= np.divide(col_sums, current_cols, out=np.zeros_like(col_sums), where=current_cols > 0)[None, :]
    return out


def null_category(null_family: str) -> str:
    if null_family in INTERPRETATION_CONTROL_FAMILIES:
        return "label_interpretation_control"
    if null_family in MARGINAL_MATCHED_NULL_FAMILIES:
        return "marginal_matched_detector_null"
    return "structure_destroying_detector_null"


def expected_null_direction(category: str) -> str:
    if category == "label_interpretation_control":
        return "label_permutation_interpretation_only"
    if category == "marginal_matched_detector_null":
        return "observed_above_marginal_matched_null"
    return "observed_above_detector_null"


def detector_null_summary_rows(anatomy: list[dict[str, object]], args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key, items in group_by(anatomy, ("null_family", "null_category", "observed_statistic")).items():
        passed = [int(float_or_zero(row.get("null_gate_passed"))) for row in items]
        percentiles = [float_or_zero(row.get("observed_percentile_vs_null")) for row in items]
        if key[1] == "label_interpretation_control":
            summary_read = "interpretation_control_only"
        else:
            summary_read = "detector_null_separates" if passed and mean(passed) >= args.detector_null_min_pass_fraction else "detector_null_control_equivalent"
        rows.append({
            "null_family": key[0],
            "null_category": key[1],
            "observed_statistic": key[2],
            "matrix_count": len({row.get("matrix_id") for row in items}),
            "row_count": len(items),
            "pass_fraction": mean(passed) if passed else 0.0,
            "median_observed_percentile_vs_null": median(percentiles) if percentiles else 0.0,
            "min_observed_percentile_vs_null": min(percentiles) if percentiles else 0.0,
            "required_pass_fraction": args.detector_null_min_pass_fraction,
            "summary_read": summary_read,
        })
    return rows


def matched_marginal_summary_rows(anatomy: list[dict[str, object]], args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    wanted = [
        row for row in anatomy
        if row.get("null_category") == "marginal_matched_detector_null"
        and row.get("observed_statistic") == "marginal_residual_fraction"
    ]
    keys = ("probe_key", "flow_mode", "source_horizon_band", "target_horizon_band", "H_a", "H_b", "condition_id", "null_family")
    for key, items in group_by(wanted, keys).items():
        passed = [int(float_or_zero(row.get("null_gate_passed"))) for row in items]
        percentiles = [float_or_zero(row.get("observed_percentile_vs_null")) for row in items]
        pass_fraction = mean(passed) if passed else 0.0
        rows.append({
            "probe_key": key[0],
            "flow_mode": key[1],
            "source_horizon_band": key[2],
            "target_horizon_band": key[3],
            "H_a": key[4],
            "H_b": key[5],
            "horizon_pair": f"{key[4]}->{key[5]}",
            "condition_id": key[6],
            "null_family": key[7],
            "observed_statistic": "marginal_residual_fraction",
            "matrix_count": len({row.get("matrix_id") for row in items}),
            "row_count": len(items),
            "pass_fraction": pass_fraction,
            "median_observed_percentile_vs_null": median(percentiles) if percentiles else 0.0,
            "min_observed_percentile_vs_null": min(percentiles) if percentiles else 0.0,
            "required_pass_fraction": args.detector_null_min_pass_fraction,
            "summary_read": "detector_null_separates" if pass_fraction >= args.detector_null_min_pass_fraction else "detector_null_control_equivalent",
        })
    return rows


def terminal_saturation_rows(matrices: list[TransportMatrix]) -> list[dict[str, object]]:
    grouped = group_matrices(matrices, ("condition_id", "actual_control_name", "mechanism_control_strength", "probe_key", "flow_mode"))
    rows: list[dict[str, object]] = []
    for _key, items in grouped.items():
        previous_entropy = None
        previous_support = None
        for matrix in sorted(items, key=lambda item: (item.key.H_b, item.key.H_a)):
            values = matrix.matrix
            total = float(values.sum())
            flat = values.flatten()
            row_mass = values.sum(axis=1)
            col_mass = values.sum(axis=0)
            largest_entry_share = float(np.max(flat)) / max(1.0, total) if flat.size else 0.0
            row_max_share = float(np.max(row_mass)) / max(1.0, total) if row_mass.size else 0.0
            column_max_share = float(np.max(col_mass)) / max(1.0, total) if col_mass.size else 0.0
            entropy = entropy_from_values(flat)
            max_entropy = math.log2(max(2, int(np.count_nonzero(flat))))
            entropy_fraction = entropy / max(1e-12, max_entropy)
            support_total = matrix.raw_row_item_count + matrix.raw_column_item_count
            coverage = matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total)
            row_support_saturation = matrix.raw_row_item_count <= 2 or row_max_share >= 0.95
            column_support_saturation = matrix.raw_column_item_count <= 2 or column_max_share >= 0.95
            row_column_support_saturation = row_support_saturation and column_support_saturation
            mass_concentration_saturation = largest_entry_share >= 0.80 or row_max_share >= 0.95 or column_max_share >= 0.95
            transport_entropy_saturation = entropy_fraction <= 0.15
            frontier_support_saturation = row_support_saturation or column_support_saturation
            undercovered = coverage < 0.80 or len(matrix.row_items) < 2 or len(matrix.column_items) < 2
            terminal = (
                matrix.key.H_b >= 96
                and (frontier_support_saturation or transport_entropy_saturation or mass_concentration_saturation)
            )
            if undercovered:
                allowed = "undercovered_diagnostic_only"
            elif terminal:
                allowed = "terminal_saturation_diagnostic_only"
            else:
                allowed = "normal_horizon_response"
            rows.append({
                **key_row(matrix.key),
                "matrix_id": matrix.matrix_id,
                "terminal_saturation_flag": int(terminal),
                "frontier_support_saturation": int(frontier_support_saturation),
                "transport_entropy_saturation": int(transport_entropy_saturation),
                "row_support_saturation": int(row_support_saturation),
                "column_support_saturation": int(column_support_saturation),
                "row_column_support_saturation": int(row_column_support_saturation),
                "mass_concentration_saturation": int(mass_concentration_saturation),
                "largest_entry_mass_share": largest_entry_share,
                "row_max_mass_share": row_max_share,
                "column_max_mass_share": column_max_share,
                "transport_entropy": entropy,
                "transport_entropy_fraction_of_nonzero_max": entropy_fraction,
                "transport_entropy_delta_vs_previous_horizon": "" if previous_entropy is None else entropy - previous_entropy,
                "support_delta_vs_previous_horizon": "" if previous_support is None else support_total - previous_support,
                "horizon_pair_undercoverage_flag": int(undercovered),
                "coverage": coverage,
                "allowed_interpretation_level": allowed,
            })
            previous_entropy = entropy
            previous_support = support_total
    return rows


def saturation_by_horizon_pair_rows(saturation: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key, items in group_by(saturation, ("horizon_pair", "H_a", "H_b")).items():
        terminal = [int(float_or_zero(row.get("terminal_saturation_flag"))) for row in items]
        undercovered = [int(float_or_zero(row.get("horizon_pair_undercoverage_flag"))) for row in items]
        normal = [1 if row.get("allowed_interpretation_level") == "normal_horizon_response" else 0 for row in items]
        rows.append({
            "horizon_pair": key[0],
            "H_a": key[1],
            "H_b": key[2],
            "matrix_count": len(items),
            "terminal_saturation_fraction": mean(terminal) if terminal else 0.0,
            "undercoverage_fraction": mean(undercovered) if undercovered else 0.0,
            "normal_interpretation_fraction": mean(normal) if normal else 0.0,
            "largest_entry_mass_share_mean": mean([float_or_zero(row.get("largest_entry_mass_share")) for row in items]) if items else 0.0,
            "row_max_mass_share_mean": mean([float_or_zero(row.get("row_max_mass_share")) for row in items]) if items else 0.0,
            "column_max_mass_share_mean": mean([float_or_zero(row.get("column_max_mass_share")) for row in items]) if items else 0.0,
            "transport_entropy_mean": mean([float_or_zero(row.get("transport_entropy")) for row in items]) if items else 0.0,
        })
    return sorted(rows, key=lambda row: (float_or_zero(row.get("H_b")), float_or_zero(row.get("H_a"))))


def response_flag_rows(response_classification: list[dict[str, object]], saturation: list[dict[str, object]]) -> list[dict[str, object]]:
    saturation_by_matrix = {str(row.get("matrix_id", "")): row for row in saturation}
    rows: list[dict[str, object]] = []
    for row in response_classification:
        sat = saturation_by_matrix.get(str(row.get("matrix_id", "")), {})
        rows.append({
            "condition_id": row.get("condition_id", ""),
            "actual_control_name": row.get("actual_control_name", ""),
            "mechanism_control_strength": row.get("mechanism_control_strength", ""),
            "probe_key": row.get("probe_key", ""),
            "flow_mode": row.get("flow_mode", ""),
            "horizon_pair": row.get("horizon_pair", ""),
            "response_class": row.get("response_class", ""),
            "response_flags": row.get("response_flags", ""),
            "mean_subspace_alignment": row.get("mean_subspace_alignment", ""),
            "spectral_mass_delta_fraction": row.get("spectral_mass_delta_fraction", ""),
            "transport_entropy_delta": row.get("transport_entropy_delta", ""),
            "perturbation_response_magnitude": row.get("perturbation_response_magnitude", ""),
            "allowed_interpretation_level": sat.get("allowed_interpretation_level", ""),
            "terminal_saturation_flag": sat.get("terminal_saturation_flag", ""),
        })
    return rows


def response_class_by_strength_and_horizon_rows(response_classification: list[dict[str, object]]) -> list[dict[str, object]]:
    keys = ("actual_control_name", "mechanism_control_strength", "probe_key", "flow_mode", "horizon_pair", "H_a", "H_b", "response_class")
    rows: list[dict[str, object]] = []
    for key, items in group_by(response_classification, keys).items():
        rows.append({
            "perturbation_family": key[0],
            "perturbation_strength": key[1],
            "probe_key": key[2],
            "flow_mode": key[3],
            "horizon_pair": key[4],
            "H_a": key[5],
            "H_b": key[6],
            "response_class": key[7],
            "row_count": len(items),
            "mean_subspace_alignment_mean": mean([float_or_zero(row.get("mean_subspace_alignment")) for row in items]) if items else 0.0,
            "spectral_mass_delta_fraction_mean": mean([float_or_zero(row.get("spectral_mass_delta_fraction")) for row in items]) if items else 0.0,
            "transport_entropy_delta_mean": mean([float_or_zero(row.get("transport_entropy_delta")) for row in items]) if items else 0.0,
            "perturbation_response_magnitude_mean": mean([float_or_zero(row.get("perturbation_response_magnitude")) for row in items]) if items else 0.0,
        })
    return sorted(rows, key=lambda row: (
        str(row.get("perturbation_family", "")),
        float_or_zero(row.get("perturbation_strength")),
        str(row.get("probe_key", "")),
        str(row.get("flow_mode", "")),
        float_or_zero(row.get("H_b")),
        str(row.get("response_class", "")),
    ))


def horizon_response_threshold_rows(response_classification: list[dict[str, object]], saturation: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    keys = ("actual_control_name", "mechanism_control_strength", "probe_key", "flow_mode")
    for key, items in group_by(response_classification, keys).items():
        ordered = sorted(items, key=lambda row: (float_or_zero(row.get("H_b")), float_or_zero(row.get("H_a"))))
        sat_items = sorted(
            [
                row for row in saturation
                if row.get("actual_control_name") == key[0]
                and str(row.get("mechanism_control_strength")) == str(key[1])
                and row.get("probe_key") == key[2]
                and row.get("flow_mode") == key[3]
            ],
            key=lambda row: (float_or_zero(row.get("H_b")), float_or_zero(row.get("H_a"))),
        )
        rows.append({
            "perturbation_family": key[0],
            "perturbation_strength": key[1],
            "probe_key": key[2],
            "flow_mode": key[3],
            "first_nonstable_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") != RESPONSE_CLASS_STABLE),
            "first_amplified_aligned_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") == RESPONSE_CLASS_AMPLIFIED_ALIGNED),
            "first_weakened_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") == RESPONSE_CLASS_WEAKENED),
            "first_rerouted_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") == RESPONSE_CLASS_REROUTED),
            "first_reopened_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") == RESPONSE_CLASS_REOPENS),
            "first_collapsed_horizon": first_response_horizon(ordered, lambda row: row.get("response_class") == RESPONSE_CLASS_COLLAPSES),
            "terminal_saturation_horizon": first_response_horizon(sat_items, lambda row: int(float_or_zero(row.get("terminal_saturation_flag"))) == 1),
            "latest_interpretable_horizon": latest_response_horizon(sat_items, lambda row: row.get("allowed_interpretation_level") == "normal_horizon_response"),
        })
    return sorted(rows, key=lambda row: (
        str(row.get("perturbation_family", "")),
        float_or_zero(row.get("perturbation_strength")),
        str(row.get("probe_key", "")),
        str(row.get("flow_mode", "")),
    ))


def first_response_horizon(rows: list[dict[str, object]], predicate: object) -> str:
    for row in rows:
        if predicate(row):  # type: ignore[operator]
            return str(row.get("horizon_pair", ""))
    return ""


def latest_response_horizon(rows: list[dict[str, object]], predicate: object) -> str:
    out = ""
    for row in rows:
        if predicate(row):  # type: ignore[operator]
            out = str(row.get("horizon_pair", ""))
    return out


def context_recommendation_rows(
    summary: list[dict[str, object]],
    matched_marginal: list[dict[str, object]],
    response_classification: list[dict[str, object]],
) -> list[dict[str, object]]:
    context_keys = ("probe_key", "flow_mode", "source_horizon_band", "target_horizon_band", "H_a", "H_b")
    summary_by_context = group_by(summary, context_keys)
    marginal_by_context = group_by(matched_marginal, context_keys)
    response_by_context = group_by(response_classification, context_keys)
    all_contexts = set(summary_by_context) | set(marginal_by_context) | set(response_by_context)
    rows: list[dict[str, object]] = []
    for key in sorted(all_contexts, key=lambda item: tuple(str(part) for part in item)):
        matrix_rows = summary_by_context.get(key, [])
        marginal_rows = marginal_by_context.get(key, [])
        response_rows = response_by_context.get(key, [])
        coverage_values = [float_or_zero(row.get("coverage")) for row in matrix_rows]
        response_counts = Counter(str(row.get("response_class", "")) for row in response_rows)
        interpretable_responses = [
            row for row in response_rows
            if is_interpretable_response(row.get("response_class"))
        ]
        passed_families = {
            str(row.get("null_family", ""))
            for row in marginal_rows
            if row.get("summary_read") == "detector_null_separates"
        }
        required_families = set(MARGINAL_MATCHED_NULL_FAMILIES)
        matched_all = required_families <= passed_families
        coverage_min = min(coverage_values) if coverage_values else 0.0
        coverage_mean = mean(coverage_values) if coverage_values else 0.0
        dominant_response = response_counts.most_common(1)[0][0] if response_counts else ""
        if coverage_min < 0.80:
            context_read = "transport_matrix_undercovered"
            recommendation = "repair_or_reduce_matrix_resolution"
        elif matched_all and interpretable_responses:
            context_read = "matched_marginal_separates_interpretable"
            recommendation = "candidate_for_context_narrowing"
        elif passed_families:
            context_read = "matched_marginal_mixed"
            recommendation = "inspect_context_before_scaling"
        elif response_rows:
            context_read = "response_only_no_matched_marginal_separation"
            recommendation = "measurement_limits_or_fixture_expansion"
        else:
            context_read = "context_underpowered"
            recommendation = "increase_context_rows_or_repair"
        rows.append({
            "probe_key": key[0],
            "flow_mode": key[1],
            "source_horizon_band": key[2],
            "target_horizon_band": key[3],
            "H_a": key[4],
            "H_b": key[5],
            "horizon_pair": f"{key[4]}->{key[5]}",
            "matrix_count": len(matrix_rows),
            "coverage_mean": coverage_mean,
            "coverage_min": coverage_min,
            "matched_marginal_families_passed": len(required_families & passed_families),
            "matched_marginal_families_required": len(required_families),
            "matched_marginal_all_families_passed": int(matched_all),
            "response_rows": len(response_rows),
            "response_interpretable_rows": len(interpretable_responses),
            "dominant_response_class": dominant_response,
            "context_read": context_read,
            "context_recommendation": recommendation,
            "context_priority_score": context_priority_score(coverage_mean, matched_all, len(required_families & passed_families), len(interpretable_responses)),
        })
    return sorted(rows, key=lambda row: float_or_zero(row.get("context_priority_score")), reverse=True)


def aggregate_context_summary_rows(rows: list[dict[str, object]], fields: tuple[str, ...], label: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for key, items in group_by(rows, fields).items():
        coverage = [float_or_zero(row.get("coverage_min")) for row in items]
        full_pass = [int(float_or_zero(row.get("matched_marginal_all_families_passed"))) for row in items]
        any_pass = [1 if float_or_zero(row.get("matched_marginal_families_passed")) > 0 else 0 for row in items]
        interpretable = [1 if float_or_zero(row.get("response_interpretable_rows")) > 0 else 0 for row in items]
        response_counts = Counter(str(row.get("dominant_response_class", "")) for row in items if row.get("dominant_response_class"))
        summary_read = "mixed_or_control_equivalent"
        if full_pass and sum(full_pass) == len(items) and any(interpretable):
            summary_read = "matched_marginal_separates"
        elif any(full_pass):
            summary_read = "context_specific_separation"
        elif any(any_pass):
            summary_read = "partial_matched_marginal_separation"
        out.append({
            label: "|".join(str(part) for part in key),
            "context_count": len(items),
            "coverage_min": min(coverage) if coverage else 0.0,
            "coverage_mean": mean(coverage) if coverage else 0.0,
            "matched_marginal_full_pass_contexts": sum(full_pass),
            "matched_marginal_any_pass_contexts": sum(any_pass),
            "response_interpretable_contexts": sum(interpretable),
            "dominant_response_class": response_counts.most_common(1)[0][0] if response_counts else "",
            "summary_read": summary_read,
        })
    return sorted(out, key=lambda row: (float_or_zero(row.get("matched_marginal_full_pass_contexts")), float_or_zero(row.get("coverage_mean"))), reverse=True)


def context_priority_score(coverage_mean: float, matched_all: bool, marginal_family_count: int, interpretable_count: int) -> float:
    return coverage_mean + (10.0 if matched_all else 0.0) + marginal_family_count + min(5, interpretable_count) / 10.0


def detector_null_gate_rows(summary: list[dict[str, object]], matrices: list[TransportMatrix], args: argparse.Namespace, fixture_results: list[dict[str, object]]) -> list[dict[str, object]]:
    structure_required = [
        row for row in summary
        if row.get("null_category") == "structure_destroying_detector_null"
        and row.get("observed_statistic") in set(DETECTOR_STATISTICS)
    ]
    marginal_required = [
        row for row in summary
        if row.get("null_category") == "marginal_matched_detector_null"
        and row.get("observed_statistic") == "marginal_residual_fraction"
    ]
    replicate_powered = args.null_replicates >= 3
    structure_pass = any(row.get("summary_read") == "detector_null_separates" for row in structure_required)
    required_marginal_families = set(MARGINAL_MATCHED_NULL_FAMILIES)
    marginal_families_passed = {
        str(row.get("null_family", ""))
        for row in marginal_required
        if row.get("summary_read") == "detector_null_separates"
    }
    marginal_pass = required_marginal_families <= marginal_families_passed
    marginal_observed = f"{len(required_marginal_families & marginal_families_passed)}/{len(required_marginal_families)} families_passed"
    fixture_required = bool(fixture_results)
    fixture_pass = bool(fixture_results) and all(int(float_or_zero(row.get("passed"))) for row in fixture_results)
    adequate_coverage = any(
        matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total) >= 0.80
        for matrix in matrices
    )
    return [
        {
            "gate_id": "G0",
            "gate_name": "horizon_transport_matrix_coverage",
            "required": 1,
            "passed": int(adequate_coverage),
            "threshold": "any matrix coverage >= 0.80",
            "observed": max((matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total) for matrix in matrices), default=0.0),
            "blocking_reason": "" if adequate_coverage else "transport_matrix_undercovered",
        },
        {
            "gate_id": "G1",
            "gate_name": "detector_null_sections_separate",
            "required": 1,
            "passed": 1,
            "threshold": "detector null outputs separate from perturbation outputs",
            "observed": "separate_outputs_written",
            "blocking_reason": "",
        },
        {
            "gate_id": "G2",
            "gate_name": "structure_detector_null_separation",
            "required": 1,
            "passed": int(structure_pass and replicate_powered),
            "threshold": f"at least one required structure null statistic pass_fraction >= {args.detector_null_min_pass_fraction}",
            "observed": "passed" if structure_pass and replicate_powered else "underpowered" if structure_pass and not replicate_powered else "control_equivalent",
            "blocking_reason": "" if structure_pass and replicate_powered else "detector_null_replicates_underpowered" if structure_pass and not replicate_powered else "transport_detector_nulls_control_equivalent",
        },
        {
            "gate_id": "G3",
            "gate_name": "detector_null_replicate_power",
            "required": 1,
            "passed": int(replicate_powered),
            "threshold": "null_replicates >= 3",
            "observed": args.null_replicates,
            "blocking_reason": "" if replicate_powered else "detector_null_replicates_underpowered",
        },
        {
            "gate_id": "G4",
            "gate_name": "matched_marginal_detector_null_separation",
            "required": 1,
            "passed": int(marginal_pass and replicate_powered),
            "threshold": "marginal_residual_fraction separates from row, column, and bimarginal matched null families",
            "observed": marginal_observed if replicate_powered else "underpowered",
            "blocking_reason": "" if marginal_pass and replicate_powered else "detector_null_replicates_underpowered" if marginal_pass and not replicate_powered else "marginal_matched_nulls_control_equivalent",
        },
        {
            "gate_id": "G5",
            "gate_name": "synthetic_fixture_contract",
            "required": int(fixture_required),
            "passed": int(fixture_pass),
            "threshold": "all fixture expectations pass when fixture smoke is enabled",
            "observed": f"{sum(int(float_or_zero(row.get('passed'))) for row in fixture_results)}/{len(fixture_results)}" if fixture_required else "not_run",
            "blocking_reason": "" if fixture_pass or not fixture_required else "synthetic_fixture_contract_failed",
        },
    ]


def perturbation_response_rows(
    matrices: list[TransportMatrix],
    null_gates: list[dict[str, object]],
    args: argparse.Namespace,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    baseline_by_view = {
        response_view_key(matrix): matrix
        for matrix in matrices
        if matrix.key.actual_control_name == BASELINE_CONTROL
    }
    detector_null_status = "detector_nulls_passed" if required_detector_gates_passed(null_gates) else "detector_nulls_not_passed"
    manifest: list[dict[str, object]] = []
    summary: list[dict[str, object]] = []
    classes: list[dict[str, object]] = []
    for matrix in matrices:
        if matrix.key.actual_control_name == BASELINE_CONTROL:
            continue
        baseline = baseline_by_view.get(response_view_key(matrix))
        tax = intervention_taxonomy(matrix.key)
        manifest.append({
            **key_row(matrix.key),
            "matrix_id": matrix.matrix_id,
            **tax,
            "perturbation_status": "baseline_available" if baseline else "baseline_missing",
        })
        response = response_payload(baseline, matrix, args)
        response_class = classify_response(response)
        common = {**key_row(matrix.key), "matrix_id": matrix.matrix_id, **tax, **response, "detector_null_status": detector_null_status}
        summary.append(common)
        classes.append({**common, "response_class": response_class, "allowed_claim_level": tax["allowed_claim_level"]})
    return manifest, summary, classes


def required_detector_gates_passed(null_gates: list[dict[str, object]]) -> bool:
    required = {
        "structure_detector_null_separation",
        "detector_null_replicate_power",
        "matched_marginal_detector_null_separation",
    }
    passed = {
        str(row.get("gate_name", ""))
        for row in null_gates
        if int(float_or_zero(row.get("passed")))
    }
    return required <= passed


def fixture_result_rows(null_anatomy: list[dict[str, object]], response_classification: list[dict[str, object]]) -> list[dict[str, object]]:
    fixture_nulls = [row for row in null_anatomy if str(row.get("condition_id", "")).startswith("fixture_")]
    fixture_responses = [row for row in response_classification if str(row.get("condition_id", "")).startswith("fixture_")]
    if not fixture_nulls and not fixture_responses:
        return []

    block_rows = [
        row for row in fixture_nulls
        if row.get("condition_id") == "fixture_block_transport_signal"
        and row.get("null_family") in MARGINAL_MATCHED_NULL_FAMILIES
        and row.get("observed_statistic") == "marginal_residual_fraction"
    ]
    fakeout_rows = [
        row for row in fixture_nulls
        if row.get("condition_id") == "fixture_marginal_fakeout"
        and row.get("null_family") == "row_column_marginal_matched_transport_null"
        and row.get("observed_statistic") == "marginal_residual_fraction"
    ]
    corridor_rows = [
        row for row in fixture_responses
        if row.get("condition_id") == "fixture_corridor_stable_response"
    ]
    trap_rows = [
        row for row in fixture_responses
        if row.get("condition_id") == "fixture_trap_collapse_response"
    ]
    amplified_rows = [
        row for row in fixture_responses
        if row.get("condition_id") == "fixture_amplified_aligned_response"
    ]
    weakened_rows = [
        row for row in fixture_responses
        if row.get("condition_id") == "fixture_weakened_response"
    ]
    rerouted_rows = [
        row for row in fixture_responses
        if row.get("condition_id") == "fixture_rerouted_response"
    ]
    reopens_rows = [
        row for row in fixture_responses
        if row.get("condition_id") == "fixture_reopens_response"
    ]

    block_pass = any(int(float_or_zero(row.get("null_gate_passed"))) for row in block_rows)
    fakeout_pass = bool(fakeout_rows) and not any(int(float_or_zero(row.get("null_gate_passed"))) for row in fakeout_rows)
    corridor_pass = any(row.get("response_class") == RESPONSE_CLASS_STABLE for row in corridor_rows)
    trap_pass = any(row.get("response_class") == RESPONSE_CLASS_COLLAPSES for row in trap_rows)
    amplified_pass = any(row.get("response_class") == RESPONSE_CLASS_AMPLIFIED_ALIGNED for row in amplified_rows)
    weakened_pass = any(row.get("response_class") == RESPONSE_CLASS_WEAKENED for row in weakened_rows)
    rerouted_pass = any(row.get("response_class") == RESPONSE_CLASS_REROUTED for row in rerouted_rows)
    reopens_pass = any(row.get("response_class") == RESPONSE_CLASS_REOPENS for row in reopens_rows)

    return [
        {
            "fixture_id": "block_transport_signal",
            "fixture_question": "does true association beyond marginals separate from matched marginal nulls",
            "expected_behavior": "marginal_residual_fraction passes at least one matched marginal null",
            "observed": observed_fixture_read(block_rows, "null_gate_passed"),
            "passed": int(block_pass),
            "source_table": "horizon_transport_detector_null_anatomy.csv",
        },
        {
            "fixture_id": "marginal_fakeout",
            "fixture_question": "does a pure row/column mass fakeout fail the bimarginal matched null",
            "expected_behavior": "marginal_residual_fraction does not pass row_column_marginal_matched_transport_null",
            "observed": observed_fixture_read(fakeout_rows, "null_gate_passed"),
            "passed": int(fakeout_pass),
            "source_table": "horizon_transport_detector_null_anatomy.csv",
        },
        {
            "fixture_id": "corridor_stable_response",
            "fixture_question": "does a tiny corridor perturbation stay in the stable response class",
            "expected_behavior": RESPONSE_CLASS_STABLE,
            "observed": observed_fixture_read(corridor_rows, "response_class"),
            "passed": int(corridor_pass),
            "source_table": "horizon_transport_response_classification.csv",
        },
        {
            "fixture_id": "trap_collapse_response",
            "fixture_question": "does a trap collapse perturbation enter the collapse response class",
            "expected_behavior": RESPONSE_CLASS_COLLAPSES,
            "observed": observed_fixture_read(trap_rows, "response_class"),
            "passed": int(trap_pass),
            "source_table": "horizon_transport_response_classification.csv",
        },
        {
            "fixture_id": "amplified_aligned_response",
            "fixture_question": "does aligned mass growth enter the amplified-aligned response class",
            "expected_behavior": RESPONSE_CLASS_AMPLIFIED_ALIGNED,
            "observed": observed_fixture_read(amplified_rows, "response_class"),
            "passed": int(amplified_pass),
            "source_table": "horizon_transport_response_classification.csv",
        },
        {
            "fixture_id": "weakened_response",
            "fixture_question": "does non-collapsing mass loss enter the weakened response class",
            "expected_behavior": RESPONSE_CLASS_WEAKENED,
            "observed": observed_fixture_read(weakened_rows, "response_class"),
            "passed": int(weakened_pass),
            "source_table": "horizon_transport_response_classification.csv",
        },
        {
            "fixture_id": "rerouted_response",
            "fixture_question": "does low-alignment transport reorganization enter the rerouted response class",
            "expected_behavior": RESPONSE_CLASS_REROUTED,
            "observed": observed_fixture_read(rerouted_rows, "response_class"),
            "passed": int(rerouted_pass),
            "source_table": "horizon_transport_response_classification.csv",
        },
        {
            "fixture_id": "reopens_response",
            "fixture_question": "does entropy-increasing transport spread enter the reopens response class",
            "expected_behavior": RESPONSE_CLASS_REOPENS,
            "observed": observed_fixture_read(reopens_rows, "response_class"),
            "passed": int(reopens_pass),
            "source_table": "horizon_transport_response_classification.csv",
        },
    ]


def observed_fixture_read(rows: list[dict[str, object]], field: str) -> str:
    if not rows:
        return "missing"
    counts = Counter(str(row.get(field, "")) for row in rows)
    return "; ".join(f"{key}:{value}" for key, value in sorted(counts.items()))


def response_payload(baseline: TransportMatrix | None, matrix: TransportMatrix, args: argparse.Namespace) -> dict[str, object]:
    if baseline is None:
        return {"response_status": "baseline_missing"}
    common_rows = sorted(set(baseline.row_items) & set(matrix.row_items))
    common_cols = sorted(set(baseline.column_items) & set(matrix.column_items))
    if len(common_rows) < 2 or len(common_cols) < 2:
        return {"response_status": "insufficient_common_transport_items", "common_row_items": len(common_rows), "common_column_items": len(common_cols)}
    base_sub = sub_transport_matrix(baseline, common_rows, common_cols)
    pert_sub = sub_transport_matrix(matrix, common_rows, common_cols)
    b_u, b_s, b_v = svd_parts(base_sub)
    p_u, p_s, p_v = svd_parts(pert_sub)
    k = min(args.top_k, b_u.shape[1], p_u.shape[1], b_v.shape[1], p_v.shape[1])
    left_alignment = subspace_alignment(b_u[:, :k], p_u[:, :k]) if k else 0.0
    right_alignment = subspace_alignment(b_v[:, :k], p_v[:, :k]) if k else 0.0
    base_mass = float(np.sum(b_s))
    pert_mass = float(np.sum(p_s))
    return {
        "response_status": "computed",
        "common_row_items": len(common_rows),
        "common_column_items": len(common_cols),
        "left_subspace_alignment": left_alignment,
        "right_subspace_alignment": right_alignment,
        "mean_subspace_alignment": (left_alignment + right_alignment) / 2.0,
        "baseline_spectral_mass": base_mass,
        "perturbation_spectral_mass": pert_mass,
        "spectral_mass_delta_fraction": (pert_mass - base_mass) / max(1e-12, base_mass),
        "baseline_transport_entropy": entropy_from_values(base_sub.flatten()),
        "perturbation_transport_entropy": entropy_from_values(pert_sub.flatten()),
        "transport_entropy_delta": entropy_from_values(pert_sub.flatten()) - entropy_from_values(base_sub.flatten()),
        "perturbation_response_magnitude": float(np.linalg.norm(pert_sub - base_sub) / max(1e-12, np.linalg.norm(base_sub))),
        "response_flags": response_flags(
            left_alignment,
            right_alignment,
            (pert_mass - base_mass) / max(1e-12, base_mass),
            entropy_from_values(pert_sub.flatten()) - entropy_from_values(base_sub.flatten()),
            float(np.linalg.norm(pert_sub - base_sub) / max(1e-12, np.linalg.norm(base_sub))),
        ),
    }


def horizon_pair_alignment_rows(matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    baseline = [matrix for matrix in matrices if matrix.key.actual_control_name == BASELINE_CONTROL]
    rows: list[dict[str, object]] = []
    for key, items in group_matrices(baseline, ("probe_key", "flow_mode")).items():
        for left in items:
            for right in items:
                if left.matrix_id >= right.matrix_id:
                    continue
                common_rows = sorted(set(left.row_items) & set(right.row_items))
                common_cols = sorted(set(left.column_items) & set(right.column_items))
                if len(common_rows) < 2 or len(common_cols) < 2:
                    continue
                left_sub = sub_transport_matrix(left, common_rows, common_cols)
                right_sub = sub_transport_matrix(right, common_rows, common_cols)
                l_u, _l_s, l_v = svd_parts(left_sub)
                r_u, _r_s, r_v = svd_parts(right_sub)
                k = min(args.top_k, l_u.shape[1], r_u.shape[1], l_v.shape[1], r_v.shape[1])
                rows.append({
                    "probe_key": key[0],
                    "flow_mode": key[1],
                    "left_matrix_id": left.matrix_id,
                    "right_matrix_id": right.matrix_id,
                    "left_horizon_pair": f"{left.key.H_a}->{left.key.H_b}",
                    "right_horizon_pair": f"{right.key.H_a}->{right.key.H_b}",
                    "left_source_horizon_band": left.key.source_horizon_band,
                    "left_target_horizon_band": left.key.target_horizon_band,
                    "right_source_horizon_band": right.key.source_horizon_band,
                    "right_target_horizon_band": right.key.target_horizon_band,
                    "left_subspace_alignment": subspace_alignment(l_u[:, :k], r_u[:, :k]) if k else 0.0,
                    "right_subspace_alignment": subspace_alignment(l_v[:, :k], r_v[:, :k]) if k else 0.0,
                    "aligned_row_items": len(common_rows),
                    "aligned_column_items": len(common_cols),
                })
    return rows


def write_outputs(
    out_dir: Path,
    outputs: dict[str, list[dict[str, object]]],
    errors: list[dict[str, object]],
    checkpoints: list[dict[str, object]],
    status: dict[str, object],
    started: float,
) -> None:
    write_csv(out_dir / "horizon_transport_matrix_manifest.csv", outputs["manifest"])
    write_csv(out_dir / "horizon_transport_row_item_manifest.csv", outputs["row_items"])
    write_csv(out_dir / "horizon_transport_column_item_manifest.csv", outputs["column_items"])
    write_csv(out_dir / "horizon_transport_coverage.csv", outputs["coverage"])
    write_csv(out_dir / "horizon_transport_matrix_summary.csv", outputs["summary"])
    write_csv(out_dir / "horizon_transport_svd_summary.csv", outputs["svd"])
    write_csv(out_dir / "horizon_transport_subspace_alignment.csv", outputs["subspace_alignment"])
    write_csv(out_dir / "horizon_transport_participation_summary.csv", outputs["participation"])
    write_csv(out_dir / "horizon_transport_entropy_summary.csv", outputs["entropy"])
    write_csv(out_dir / "horizon_transport_detector_null_summary.csv", outputs["null_summary"])
    write_csv(out_dir / "horizon_transport_detector_null_anatomy.csv", outputs["null_anatomy"])
    write_csv(out_dir / "horizon_transport_detector_null_gate_results.csv", outputs["null_gates"])
    write_csv(out_dir / "horizon_transport_matched_marginal_summary.csv", outputs["matched_marginal"])
    write_csv(out_dir / "horizon_transport_fixture_results.csv", outputs["fixture_results"])
    write_csv(out_dir / "horizon_transport_perturbation_manifest.csv", outputs["perturb_manifest"])
    write_csv(out_dir / "horizon_transport_response_profile_summary.csv", outputs["response_summary"])
    write_csv(out_dir / "horizon_transport_response_classification.csv", outputs["response_classification"])
    write_csv(out_dir / "horizon_transport_response_flags.csv", outputs["response_flags"])
    write_csv(out_dir / "response_class_by_strength_and_horizon_pair.csv", outputs["response_by_strength_horizon"])
    write_csv(out_dir / "horizon_response_threshold_table.csv", outputs["threshold_table"])
    write_csv(out_dir / "horizon_transport_terminal_saturation_summary.csv", outputs["saturation"])
    write_csv(out_dir / "horizon_transport_saturation_by_horizon_pair.csv", outputs["saturation_by_horizon_pair"])
    write_csv(out_dir / "horizon_transport_response_fixture_summary.csv", outputs["response_fixture_summary"])
    write_csv(out_dir / "horizon_transport_by_probe_summary.csv", outputs["by_probe"])
    write_csv(out_dir / "horizon_transport_by_flow_mode_summary.csv", outputs["by_flow_mode"])
    write_csv(out_dir / "horizon_transport_by_horizon_pair_summary.csv", outputs["by_horizon_pair"])
    write_csv(out_dir / "horizon_transport_context_recommendation.csv", outputs["context_recommendation"])
    status.update(decision_fields(outputs, status))
    status["matrix_count"] = len(outputs["manifest"])
    status["detector_null_rows"] = len(outputs["null_anatomy"])
    status["matched_marginal_summary_rows"] = len(outputs["matched_marginal"])
    status["context_recommendation_rows"] = len(outputs["context_recommendation"])
    status["fixture_result_rows"] = len(outputs["fixture_results"])
    status["perturbation_response_rows"] = len(outputs["response_classification"])
    status["response_flag_rows"] = len(outputs["response_flags"])
    status["horizon_response_threshold_rows"] = len(outputs["threshold_table"])
    status["terminal_saturation_rows"] = len(outputs["saturation"])
    status["terminal_saturation_flagged_rows"] = sum(int(float_or_zero(row.get("terminal_saturation_flag"))) for row in outputs["saturation"])
    status["response_fixture_summary_rows"] = len(outputs["response_fixture_summary"])
    status["errors"] = len(errors)
    status["finished_utc"] = utc_now()
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    kind = status_run_kind(status)
    write_csv(out_dir / errors_filename(kind), errors)
    write_csv(out_dir / progress_filename(kind), checkpoints)
    write_report(out_dir, status, outputs)
    write_manifest(out_dir, status)
    write_json(out_dir / status_filename(kind), status)


def decision_fields(outputs: dict[str, list[dict[str, object]]], status: dict[str, object]) -> dict[str, object]:
    gates = outputs["null_gates"]
    matrix_gate = any(row.get("gate_name") == "horizon_transport_matrix_coverage" and int(float_or_zero(row.get("passed"))) for row in gates)
    null_gate = any(row.get("gate_name") == "structure_detector_null_separation" and int(float_or_zero(row.get("passed"))) for row in gates)
    null_power_gate = any(row.get("gate_name") == "detector_null_replicate_power" and int(float_or_zero(row.get("passed"))) for row in gates)
    matched_marginal_gate = any(row.get("gate_name") == "matched_marginal_detector_null_separation" and int(float_or_zero(row.get("passed"))) for row in gates)
    fixture_rows = outputs["fixture_results"]
    fixture_required = bool(fixture_rows)
    fixture_gate = (not fixture_required) or all(int(float_or_zero(row.get("passed"))) for row in fixture_rows)
    response_rows = [row for row in outputs["response_classification"] if is_interpretable_response(row.get("response_class"))]
    response_interpretable = bool(response_rows)
    if status_run_kind(status) == "h128":
        readiness, next_action = h128_decision(outputs, matrix_gate, null_gate, null_power_gate, matched_marginal_gate, response_interpretable, fixture_gate)
    elif status_run_kind(status) == "expansion":
        readiness, next_action = expansion_decision(outputs, matrix_gate, null_gate, null_power_gate, matched_marginal_gate, response_interpretable)
    elif fixture_required and matrix_gate and null_gate and matched_marginal_gate and null_power_gate and response_interpretable and fixture_gate:
        readiness = "fixture_contract_passed"
        next_action = "run_empirical_matched_null_plumbing_smoke"
    elif matrix_gate and null_gate and matched_marginal_gate and null_power_gate and response_interpretable and fixture_gate:
        readiness = "ready_for_horizon_transport_smoke_expansion"
        next_action = "expand_horizon_transport_smoke"
    elif matrix_gate and not null_power_gate:
        readiness = "not_ready_repair_required"
        next_action = "repair_transport_null_controls"
    elif matrix_gate and null_gate and not matched_marginal_gate:
        readiness = "not_ready_repair_required"
        next_action = "repair_marginal_matched_transport_nulls"
    elif matrix_gate and null_gate and matched_marginal_gate and not fixture_gate:
        readiness = "not_ready_repair_required"
        next_action = "repair_horizon_transport_fixtures"
    elif matrix_gate and not null_gate:
        readiness = "ready_for_fixture_horizon_transport_tests"
        next_action = "build_horizon_transport_fixtures"
    else:
        readiness = "not_ready_repair_required"
        next_action = "repair_transport_null_controls"
    return {
        "readiness_level": readiness,
        "next_action_fork": next_action,
        "ready_for_horizon_transport_smoke_expansion": int(readiness == "ready_for_horizon_transport_smoke_expansion"),
        "ready_for_horizon_transport_scaleup": int(readiness == "ready_for_horizon_transport_scaleup"),
        "ready_for_horizon_transport_context_narrowing": int(readiness == "ready_for_horizon_transport_context_narrowing"),
        "ready_for_horizon_transport_fixture_expansion": int(readiness == "ready_for_horizon_transport_fixture_expansion"),
        "ready_for_response_fixture_repair": int(readiness == "ready_for_response_fixture_repair"),
        "ready_for_horizon_transport_theory_note": int(readiness == "ready_for_horizon_transport_theory_note"),
        "measurement_limits_note_recommended": int(readiness == "measurement_limits_note_recommended"),
        "fixture_contract_passed": int(fixture_required and fixture_gate),
        "ready_for_fixture_horizon_transport_tests": int(readiness == "ready_for_fixture_horizon_transport_tests"),
        "ready_for_direct_channel_diagnostics": int(readiness == "ready_for_direct_channel_diagnostics"),
        "not_ready_repair_required": int(readiness == "not_ready_repair_required"),
        "detector_null_gate_passed": int(null_gate),
        "detector_null_replicate_powered": int(null_power_gate),
        "matched_marginal_detector_null_gate_passed": int(matched_marginal_gate),
        "synthetic_fixture_contract_passed": int(fixture_required and fixture_gate),
        "synthetic_fixture_contract_required": int(fixture_required),
        "synthetic_fixture_contract_not_run": int(not fixture_required),
        "perturbation_response_interpretable": int(response_interpretable),
    }


def h128_decision(
    outputs: dict[str, list[dict[str, object]]],
    matrix_gate: bool,
    null_gate: bool,
    null_power_gate: bool,
    matched_marginal_gate: bool,
    response_interpretable: bool,
    fixture_gate: bool,
) -> tuple[str, str]:
    if not matrix_gate or not null_gate or not null_power_gate or not matched_marginal_gate:
        return "not_ready_repair_required", "extend_or_trim_horizon_range"
    if not fixture_gate:
        return "ready_for_response_fixture_repair", "repair_response_taxonomy_fixtures"
    saturation_rows = outputs.get("saturation", [])
    decisive = [
        row for row in saturation_rows
        if str(row.get("horizon_pair", "")) in {"64->96", "96->128"}
    ]
    if decisive and mean([int(float_or_zero(row.get("terminal_saturation_flag"))) for row in decisive]) >= 0.50:
        return "measurement_limits_note_recommended", "write_horizon_transport_measurement_limits_note"
    classes = {
        str(row.get("response_class", ""))
        for row in outputs.get("response_classification", [])
    }
    nonstable = classes - {"", RESPONSE_CLASS_STABLE} - set(MEASUREMENT_LIMIT_RESPONSE_CLASSES)
    if RESPONSE_CLASS_AMPLIFIED_ALIGNED in nonstable and len(nonstable) >= 1:
        return "ready_for_horizon_transport_theory_note", "write_horizon_transport_theory_note"
    if response_interpretable and nonstable:
        return "ready_for_horizon_transport_context_narrowing", "narrow_to_horizon_response_context"
    if response_interpretable:
        return "measurement_limits_note_recommended", "write_horizon_transport_measurement_limits_note"
    return "not_ready_repair_required", "extend_or_trim_horizon_range"


def expansion_decision(
    outputs: dict[str, list[dict[str, object]]],
    matrix_gate: bool,
    null_gate: bool,
    null_power_gate: bool,
    matched_marginal_gate: bool,
    response_interpretable: bool,
) -> tuple[str, str]:
    if not matrix_gate or not null_power_gate:
        return "not_ready_repair_required", "repair_transport_null_controls"
    promising = [
        row for row in outputs["context_recommendation"]
        if row.get("context_read") == "matched_marginal_separates_interpretable"
    ]
    partial = [
        row for row in outputs["context_recommendation"]
        if row.get("context_read") in {"matched_marginal_separates_interpretable", "matched_marginal_mixed"}
    ]
    if matched_marginal_gate and null_gate and response_interpretable and len(promising) >= 4:
        return "ready_for_horizon_transport_scaleup", "expand_horizon_transport_scale"
    if partial:
        return "ready_for_horizon_transport_context_narrowing", "narrow_to_best_horizon_transport_context"
    if null_gate and response_interpretable:
        return "ready_for_horizon_transport_fixture_expansion", "build_more_horizon_transport_fixtures"
    if matrix_gate and null_power_gate:
        return "measurement_limits_note_recommended", "write_horizon_transport_measurement_limits_note"
    return "not_ready_repair_required", "repair_transport_null_controls"


def write_report(out_dir: Path, status: dict[str, object], outputs: dict[str, list[dict[str, object]]]) -> None:
    gates = outputs["null_gates"]
    response_counts = Counter(str(row.get("response_class", "")) for row in outputs["response_classification"])
    best_context = outputs["context_recommendation"][0] if outputs["context_recommendation"] else {}
    lines = [
        "# Executive Summary",
        "",
        f"Decision: `{status.get('readiness_level', '')}`.",
        "",
        f"Next action: `{status.get('next_action_fork', '')}`.",
        "",
        f"Run kind: `{status.get('run_kind', '')}`.",
        "",
        f"Horizon-transport matrices built: `{status.get('matrix_count', 0)}`.",
        "",
        f"Detector-null gate passed: `{status.get('detector_null_gate_passed', 0)}`.",
        "",
        f"Detector-null replicate powered: `{status.get('detector_null_replicate_powered', 0)}`.",
        "",
        f"Matched marginal null gate passed: `{status.get('matched_marginal_detector_null_gate_passed', 0)}`.",
        "",
        f"Synthetic fixture contract: `{fixture_status_text(status)}`.",
        "",
        f"Perturbation response interpretable: `{status.get('perturbation_response_interpretable', 0)}`.",
        "",
        f"Best context: `{context_label(best_context)}`.",
        "",
        "Detector-null controls and candidate perturbation responses were written to separate outputs.",
        "",
        "## Claim Boundary",
        "",
        CLAIM_BOUNDARY,
        "",
        "## Run Shape and Local Artifact Policy",
        "",
        f"Jobs requested: `{status.get('jobs_requested', 0)}`.",
        f"Jobs completed: `{status.get('jobs_completed', 0)}`.",
        f"Workers: `{status.get('workers', '')}`.",
        f"Finalization reason: `{status.get('finalization_reason', '')}`.",
        f"Artifact policy: {LOCAL_ONLY_ARTIFACT_POLICY}",
        "",
        "## Matrix Coverage",
        "",
        f"Matrix count: `{len(outputs['manifest'])}`.",
        f"Coverage rows: `{len(outputs['coverage'])}`.",
        f"Minimum context coverage: `{min((float_or_zero(row.get('coverage_min')) for row in outputs['context_recommendation']), default=0.0):.3f}`.",
        "",
        "## Control Taxonomy Compliance",
        "",
        "Every matrix and response row includes intervention class, family, name, strength, interpretation role, and allowed claim level.",
        "",
        "## Horizon-Transport Matrix Construction",
        "",
        "Matrix family: `horizon_transport`; spectral method: `SVD`.",
        "",
        "## Detector-Null Results",
        "",
        "| gate | passed | observed | blocker |",
        "|---|---:|---|---|",
    ]
    for row in gates:
        lines.append(
            f"| {markdown_cell(row.get('gate_name', ''))} | {row.get('passed', '')} | "
            f"{markdown_cell(row.get('observed', ''))} | {markdown_cell(row.get('blocking_reason', ''))} |"
        )
    lines.extend([
        "",
        "## Matched Marginal Null Results",
        "",
        "| null_family | contexts | mean pass_fraction | min percentile |",
        "|---|---:|---:|---:|",
    ])
    for family, items in group_by(outputs["matched_marginal"], ("null_family",)).items():
        pass_fractions = [float_or_zero(row.get("pass_fraction")) for row in items]
        min_percentiles = [float_or_zero(row.get("min_observed_percentile_vs_null")) for row in items]
        lines.append(
            f"| {markdown_cell(family[0])} | {len(items)} | "
            f"{mean(pass_fractions) if pass_fractions else 0.0:.3f} | {min(min_percentiles) if min_percentiles else 0.0:.3f} |"
        )
    lines.extend([
        "",
        "## Fixture Results",
        "",
        "| fixture | passed | observed |",
        "|---|---:|---|",
    ])
    for row in outputs["fixture_results"]:
        lines.append(
            f"| {markdown_cell(row.get('fixture_id', ''))} | {row.get('passed', '')} | "
            f"{markdown_cell(row.get('observed', ''))} |"
        )
    if not outputs["fixture_results"]:
        lines.append("| not_run |  | fixture smoke disabled |")
    lines.extend([
        "",
        "## Perturbation-Response Results",
        "",
        "| response_class | count |",
        "|---|---:|",
    ])
    for name, count in sorted(response_counts.items()):
        lines.append(f"| {markdown_cell(name)} | {count} |")
    lines.extend([
        "",
        "## Terminal Saturation Diagnostics",
        "",
        "| horizon_pair | matrices | terminal fraction | undercoverage fraction | normal fraction |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in outputs.get("saturation_by_horizon_pair", []):
        lines.append(
            f"| {markdown_cell(row.get('horizon_pair', ''))} | {row.get('matrix_count', '')} | "
            f"{float_or_zero(row.get('terminal_saturation_fraction')):.3f} | "
            f"{float_or_zero(row.get('undercoverage_fraction')):.3f} | "
            f"{float_or_zero(row.get('normal_interpretation_fraction')):.3f} |"
        )
    lines.extend([
        "",
        "## Response Class by Strength and Horizon Pair",
        "",
        "| perturbation | strength | probe | flow | horizon_pair | response_class | count |",
        "|---|---:|---|---|---|---|---:|",
    ])
    for row in outputs.get("response_by_strength_horizon", [])[:80]:
        lines.append(
            f"| {markdown_cell(row.get('perturbation_family', ''))} | {row.get('perturbation_strength', '')} | "
            f"{markdown_cell(row.get('probe_key', ''))} | {markdown_cell(row.get('flow_mode', ''))} | "
            f"{markdown_cell(row.get('horizon_pair', ''))} | {markdown_cell(row.get('response_class', ''))} | "
            f"{row.get('row_count', '')} |"
        )
    lines.extend([
        "",
        "## Horizon Response Threshold Table",
        "",
        "| perturbation | strength | probe | flow | first nonstable | first amplified | first weakened | first rerouted | first reopened | first collapsed | terminal saturation | latest interpretable |",
        "|---|---:|---|---|---|---|---|---|---|---|---|---|",
    ])
    for row in outputs.get("threshold_table", []):
        lines.append(
            f"| {markdown_cell(row.get('perturbation_family', ''))} | {row.get('perturbation_strength', '')} | "
            f"{markdown_cell(row.get('probe_key', ''))} | {markdown_cell(row.get('flow_mode', ''))} | "
            f"{markdown_cell(row.get('first_nonstable_horizon', ''))} | "
            f"{markdown_cell(row.get('first_amplified_aligned_horizon', ''))} | "
            f"{markdown_cell(row.get('first_weakened_horizon', ''))} | "
            f"{markdown_cell(row.get('first_rerouted_horizon', ''))} | "
            f"{markdown_cell(row.get('first_reopened_horizon', ''))} | "
            f"{markdown_cell(row.get('first_collapsed_horizon', ''))} | "
            f"{markdown_cell(row.get('terminal_saturation_horizon', ''))} | "
            f"{markdown_cell(row.get('latest_interpretable_horizon', ''))} |"
        )
    lines.extend([
        "",
        "## Probe / Flow / Horizon-Pair Context Summary",
        "",
        "### By Probe",
        "",
        "| probe | contexts | full matched pass | response contexts | read |",
        "|---|---:|---:|---:|---|",
    ])
    for row in outputs["by_probe"]:
        lines.append(
            f"| {markdown_cell(row.get('probe_key', ''))} | {row.get('context_count', '')} | "
            f"{row.get('matched_marginal_full_pass_contexts', '')} | {row.get('response_interpretable_contexts', '')} | "
            f"{markdown_cell(row.get('summary_read', ''))} |"
        )
    lines.extend([
        "",
        "### By Flow Mode",
        "",
        "| flow_mode | contexts | full matched pass | response contexts | read |",
        "|---|---:|---:|---:|---|",
    ])
    for row in outputs["by_flow_mode"]:
        lines.append(
            f"| {markdown_cell(row.get('flow_mode', ''))} | {row.get('context_count', '')} | "
            f"{row.get('matched_marginal_full_pass_contexts', '')} | {row.get('response_interpretable_contexts', '')} | "
            f"{markdown_cell(row.get('summary_read', ''))} |"
        )
    lines.extend([
        "",
        "### By Horizon Pair",
        "",
        "| horizon_pair | contexts | full matched pass | response contexts | read |",
        "|---|---:|---:|---:|---|",
    ])
    for row in outputs["by_horizon_pair"]:
        lines.append(
            f"| {markdown_cell(row.get('horizon_pair', ''))} | {row.get('context_count', '')} | "
            f"{row.get('matched_marginal_full_pass_contexts', '')} | {row.get('response_interpretable_contexts', '')} | "
            f"{markdown_cell(row.get('summary_read', ''))} |"
        )
    lines.extend([
        "",
        "## Context Recommendation",
        "",
        "| context | read | recommendation | score |",
        "|---|---|---|---:|",
    ])
    for row in outputs["context_recommendation"][:10]:
        lines.append(
            f"| {markdown_cell(context_label(row))} | {markdown_cell(row.get('context_read', ''))} | "
            f"{markdown_cell(row.get('context_recommendation', ''))} | {float_or_zero(row.get('context_priority_score')):.3f} |"
        )
    lines.extend([
        "",
        "## Horizon-Pair Comparison",
        "",
        f"Subspace alignment rows: `{len(outputs['subspace_alignment'])}`.",
        "",
        "## Readiness Levels",
        "",
        f"- ready_for_horizon_transport_smoke_expansion: `{status.get('ready_for_horizon_transport_smoke_expansion', 0)}`",
        f"- ready_for_horizon_transport_scaleup: `{status.get('ready_for_horizon_transport_scaleup', 0)}`",
        f"- ready_for_horizon_transport_context_narrowing: `{status.get('ready_for_horizon_transport_context_narrowing', 0)}`",
        f"- ready_for_horizon_transport_fixture_expansion: `{status.get('ready_for_horizon_transport_fixture_expansion', 0)}`",
        f"- ready_for_response_fixture_repair: `{status.get('ready_for_response_fixture_repair', 0)}`",
        f"- ready_for_horizon_transport_theory_note: `{status.get('ready_for_horizon_transport_theory_note', 0)}`",
        f"- measurement_limits_note_recommended: `{status.get('measurement_limits_note_recommended', 0)}`",
        f"- fixture_contract_passed: `{status.get('fixture_contract_passed', 0)}`",
        f"- ready_for_fixture_horizon_transport_tests: `{status.get('ready_for_fixture_horizon_transport_tests', 0)}`",
        f"- ready_for_direct_channel_diagnostics: `{status.get('ready_for_direct_channel_diagnostics', 0)}`",
        f"- not_ready_repair_required: `{status.get('not_ready_repair_required', 0)}`",
        "",
        "## Next-Action Fork",
        "",
        f"`{status.get('next_action_fork', '')}`",
        "",
        "## Output Manifest",
        "",
        f"See `{manifest_filename(status_run_kind(status))}`.",
        "",
    ])
    (out_dir / report_filename(status_run_kind(status))).write_text("\n".join(lines), encoding="utf-8")


def fixture_status_text(status: dict[str, object]) -> str:
    if int(float_or_zero(status.get("synthetic_fixture_contract_required"))) == 0:
        return "not_run"
    if int(float_or_zero(status.get("synthetic_fixture_contract_passed"))):
        return "passed"
    return "failed"


def context_label(row: dict[str, object]) -> str:
    if not row:
        return "none"
    return "|".join([
        str(row.get("probe_key", "")),
        str(row.get("flow_mode", "")),
        f"{row.get('H_a', '')}->{row.get('H_b', '')}",
    ])


def markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def output_files(kind: str) -> list[str]:
    return [
        run_config_filename(kind),
        status_filename(kind),
        progress_filename(kind),
        errors_filename(kind),
        manifest_filename(kind),
        *COMMON_OUTPUTS,
        report_filename(kind),
    ]


def write_manifest(out_dir: Path, status: dict[str, object]) -> None:
    kind = status_run_kind(status)
    rows = output_manifest_rows(output_files(kind), out_dir)
    for row in rows:
        if row.get("file") == manifest_filename(kind):
            row["exists"] = True
            row["status"] = "present"
    write_json(out_dir / manifest_filename(kind), rows)


def transport_matrix_id(key: TransportKey) -> str:
    return "|".join([
        "horizon_transport",
        key.condition_id,
        key.probe_key,
        key.flow_mode,
        f"{key.H_a}->{key.H_b}",
    ])


def key_row(key: TransportKey) -> dict[str, object]:
    return {
        "matrix_family": "horizon_transport",
        "condition_id": key.condition_id,
        "actual_control_name": key.actual_control_name,
        "mechanism_control_strength": key.mechanism_control_strength,
        "probe_key": key.probe_key,
        "flow_mode": key.flow_mode,
        "source_horizon_band": key.source_horizon_band,
        "target_horizon_band": key.target_horizon_band,
        "H_a": key.H_a,
        "H_b": key.H_b,
        "horizon_pair": f"{key.H_a}->{key.H_b}",
    }


def intervention_taxonomy(key: TransportKey) -> dict[str, object]:
    if key.actual_control_name == BASELINE_CONTROL:
        intervention_class = "baseline"
        interpretation_role = "instrumentation_only"
        allowed_claim_level = "instrumentation_only"
    else:
        intervention_class = "nonlethal_perturbation"
        interpretation_role = "candidate_response_profile"
        allowed_claim_level = "response_profile_only"
    return {
        "intervention_class": intervention_class,
        "intervention_family": "baseline" if key.actual_control_name == BASELINE_CONTROL else key.actual_control_name,
        "intervention_name": key.actual_control_name,
        "intervention_strength": key.mechanism_control_strength,
        "interpretation_role": interpretation_role,
        "allowed_claim_level": allowed_claim_level,
    }


def horizon_point_band(horizon: int) -> str:
    if horizon <= 2:
        return "short"
    if horizon <= 16:
        return "middle"
    return "downstream"


def transport_stat(matrix: TransportMatrix | np.ndarray, stat: str) -> float:
    values = matrix.matrix if isinstance(matrix, TransportMatrix) else matrix
    singular = np.linalg.svd(values, compute_uv=False)
    if stat in {"positive_or_nonzero_spectral_mass", "singular_spectral_mass"}:
        return float(np.sum(singular))
    if stat in {"effective_rank", "singular_effective_rank"}:
        return effective_rank(singular)
    if stat == "transport_concentration":
        return top_share(values.flatten(), 1)
    if stat == "marginal_residual_fraction":
        return marginal_residual_fraction(values)
    return 0.0


def null_failure_interpretation(matrix: TransportMatrix, category: str, percentile: float, threshold: float, replicates: int) -> str:
    if category == "label_interpretation_control":
        return "passed"
    if matrix.retained_transport_mass / max(1.0, matrix.transport_mass_total) < 0.50:
        return "insufficient_coverage"
    if replicates < 3:
        return "underpowered_replicates"
    if percentile >= threshold:
        return "passed"
    if category == "marginal_matched_detector_null":
        return "marginal_mass_geometry_explains_statistic"
    if percentile <= 0.50:
        return "true_control_equivalence"
    return "statistic_mismatch"


def response_view_key(matrix: TransportMatrix) -> tuple[object, ...]:
    return (matrix.key.probe_key, matrix.key.flow_mode, matrix.key.H_a, matrix.key.H_b)


def sub_transport_matrix(matrix: TransportMatrix, rows: list[str], cols: list[str]) -> np.ndarray:
    row_index = {item: index for index, item in enumerate(matrix.row_items)}
    col_index = {item: index for index, item in enumerate(matrix.column_items)}
    out = np.zeros((len(rows), len(cols)), dtype=np.float64)
    for i, item in enumerate(rows):
        for j, col in enumerate(cols):
            out[i, j] = matrix.matrix[row_index[item], col_index[col]]
    return out


def svd_parts(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    u, s, vt = np.linalg.svd(matrix, full_matrices=False)
    return u, s, vt.T


def subspace_alignment(left: np.ndarray, right: np.ndarray) -> float:
    if left.size == 0 or right.size == 0:
        return 0.0
    k = min(left.shape[1], right.shape[1])
    return float(np.linalg.norm(left[:, :k].T @ right[:, :k], ord="fro") ** 2 / max(1, k))


def group_matrices(matrices: list[TransportMatrix], fields: tuple[str, ...]) -> dict[tuple[object, ...], list[TransportMatrix]]:
    grouped: dict[tuple[object, ...], list[TransportMatrix]] = defaultdict(list)
    for matrix in matrices:
        values = []
        for field in fields:
            values.append(getattr(matrix.key, field))
        grouped[tuple(values)].append(matrix)
    return grouped


def marginal_residual_fraction(values: np.ndarray) -> float:
    total = float(np.sum(values))
    if total <= 0:
        return 0.0
    row_sums = values.sum(axis=1)
    col_sums = values.sum(axis=0)
    expected = np.outer(row_sums, col_sums) / total
    denom = float(np.linalg.norm(values))
    if denom <= 1e-12:
        return 0.0
    return float(np.linalg.norm(values - expected) / denom)


def entropy_from_values(values: np.ndarray) -> float:
    total = float(np.sum(values))
    if total <= 0:
        return 0.0
    probs = [float(value) / total for value in values if value > 0]
    return -sum(prob * math.log(prob) for prob in probs)


def top_share(values: np.ndarray, k: int) -> float:
    total = float(np.sum(values))
    if total <= 0:
        return 0.0
    ordered = sorted((float(value) for value in values if value > 0), reverse=True)
    return sum(ordered[:k]) / total


def vector_participation(vector: np.ndarray) -> float:
    weights = np.asarray(vector, dtype=np.float64) ** 2
    denom = float(np.sum(weights ** 2))
    return 1.0 / denom if denom > 1e-12 else 0.0


if __name__ == "__main__":
    main()
