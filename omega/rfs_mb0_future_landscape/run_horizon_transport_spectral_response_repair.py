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
from .spectral_contracts import (
    CLAIM_BOUNDARY,
    LOCAL_ONLY_ARTIFACT_POLICY,
    instrument_metadata,
    output_manifest_rows,
    utc_now,
    write_json,
)


SPEC_ID = "docs/RFS_MB0_HORIZON_TRANSPORT_SPECTRAL_RESPONSE_REPAIR_SPEC.md"
RUNNER_MODULE = "omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair"
STOP_REQUESTED = False

OUTPUTS = (
    "horizon_transport_repair_run_config.json",
    "horizon_transport_repair_status.json",
    "horizon_transport_repair_progress_checkpoints.csv",
    "horizon_transport_repair_errors.csv",
    "horizon_transport_repair_output_manifest.json",
    "horizon_transport_matrix_manifest.csv",
    "horizon_transport_row_item_manifest.csv",
    "horizon_transport_column_item_manifest.csv",
    "horizon_transport_coverage.csv",
    "horizon_transport_matrix_summary.csv",
    "horizon_transport_svd_summary.csv",
    "horizon_transport_subspace_alignment.csv",
    "horizon_transport_participation_summary.csv",
    "horizon_transport_entropy_summary.csv",
    "horizon_transport_detector_null_summary.csv",
    "horizon_transport_detector_null_anatomy.csv",
    "horizon_transport_detector_null_gate_results.csv",
    "horizon_transport_perturbation_manifest.csv",
    "horizon_transport_response_profile_summary.csv",
    "horizon_transport_response_classification.csv",
    "rfs_mb0_horizon_transport_spectral_response_repair_result.md",
)


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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)
    started = time.perf_counter()
    repo_root = Path(__file__).resolve().parents[2]
    args.out.mkdir(parents=True, exist_ok=True)
    metadata = instrument_metadata(SPEC_ID, RUNNER_MODULE, repo_root)
    probes = tuple(item.strip() for item in args.probes.split(",") if item.strip())
    starts = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    groups, split_rows = build_holdout_split(args)
    anchors = {row.get("anchor_id", ""): row for row in read_csv(args.source_run / "atlas_band_selection.csv")}
    jobs = build_jobs(args, groups, split_rows, anchors, probes, starts)
    write_json(args.out / "horizon_transport_repair_run_config.json", {
        **metadata,
        **vars(args),
        "job_count": len(jobs),
        "claim_boundary": CLAIM_BOUNDARY,
    })
    status: dict[str, object] = {
        **metadata,
        "status": "RUNNING",
        "phase": "rfs_mb0_horizon_transport_spectral_response_repair",
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
    }
    write_json(args.out / "horizon_transport_repair_status.json", status)
    rows, errors, checkpoints = run_jobs(args, jobs, status, started)
    matrices = build_transport_matrices(rows, args)
    outputs = compute_outputs(matrices, rows, args)
    write_outputs(args.out, outputs, errors, checkpoints, status, started)


def handle_stop(_signum: int, _frame: object) -> None:
    global STOP_REQUESTED
    STOP_REQUESTED = True


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
            done, _pending_futures = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                batch = futures.pop(future)
                try:
                    _contexts, metric_rows, batch_errors, completed = future.result()
                except Exception as exc:  # noqa: BLE001
                    metric_rows, batch_errors, completed = [], [{"job_id": ",".join(str(job.get("job_id", "")) for job in batch), "error": repr(exc)}], 0
                rows.extend(metric_rows)
                errors.extend(batch_errors)
                status["jobs_completed"] = int(status["jobs_completed"]) + completed
                if int(status["jobs_completed"]) - last_checkpoint >= max(1, args.checkpoint_every_jobs):
                    checkpoints.append(checkpoint_row(status, started, len(rows), len(errors)))
                    last_checkpoint = int(status["jobs_completed"])
                    write_partial(args.out, status, started, checkpoints, errors)
    finally:
        if futures:
            for future in futures:
                future.cancel()
            status["jobs_cancelled"] = len(futures)
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    status["pending_jobs_remaining"] = sum(len(batch) for batch in pending)
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
    write_json(out_dir / "horizon_transport_repair_status.json", status)
    write_csv(out_dir / "horizon_transport_repair_progress_checkpoints.csv", checkpoints)
    write_csv(out_dir / "horizon_transport_repair_errors.csv", errors)


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
    null_gates = detector_null_gate_rows(null_summary, matrices, args)
    perturb_manifest, response_summary, response_classification = perturbation_response_rows(matrices, null_gates, args)
    subspace_alignment = horizon_pair_alignment_rows(matrices, args)
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
        "perturb_manifest": perturb_manifest,
        "response_summary": response_summary,
        "response_classification": response_classification,
        "subspace_alignment": subspace_alignment,
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
    statistics = ("positive_or_nonzero_spectral_mass", "effective_rank", "transport_concentration")
    for matrix in baseline:
        for null_family in ("context_shuffle_transport_null", "horizon_pair_shuffle_transport_null", "label_shuffle_transport_interpretation_control"):
            null_values_by_stat: dict[str, list[float]] = defaultdict(list)
            for replicate in range(max(1, args.null_replicates)):
                rng = random.Random(stable_seed(f"horizon_transport_null|{matrix.matrix_id}|{null_family}|{replicate}"))
                null_matrix = make_null_matrix(matrix, null_family, pool_by_probe_flow, rng)
                for stat in statistics:
                    null_values_by_stat[stat].append(transport_stat(null_matrix, stat))
            for stat in statistics:
                observed = transport_stat(matrix.matrix, stat)
                null_values = null_values_by_stat[stat]
                percentile = sum(value <= observed for value in null_values) / max(1, len(null_values))
                threshold = float(args.detector_null_min_percentile)
                passed = percentile >= threshold
                category = "label_interpretation_control" if null_family.startswith("label") else "structure_destroying_detector_null"
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
                    "expected_direction": "observed_above_detector_null" if category != "label_interpretation_control" else "label_permutation_interpretation_only",
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


def detector_null_summary_rows(anatomy: list[dict[str, object]], args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key, items in group_by(anatomy, ("null_family", "null_category", "observed_statistic")).items():
        passed = [int(float_or_zero(row.get("null_gate_passed"))) for row in items]
        percentiles = [float_or_zero(row.get("observed_percentile_vs_null")) for row in items]
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
            "summary_read": "detector_null_separates" if passed and mean(passed) >= args.detector_null_min_pass_fraction else "detector_null_control_equivalent",
        })
    return rows


def detector_null_gate_rows(summary: list[dict[str, object]], matrices: list[TransportMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    required = [
        row for row in summary
        if row.get("null_category") == "structure_destroying_detector_null"
        and row.get("observed_statistic") in {"positive_or_nonzero_spectral_mass", "effective_rank", "transport_concentration"}
    ]
    replicate_powered = args.null_replicates >= 3
    any_required_pass = any(row.get("summary_read") == "detector_null_separates" for row in required)
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
            "passed": int(any_required_pass and replicate_powered),
            "threshold": f"at least one required structure null statistic pass_fraction >= {args.detector_null_min_pass_fraction}",
            "observed": "passed" if any_required_pass and replicate_powered else "underpowered" if any_required_pass and not replicate_powered else "control_equivalent",
            "blocking_reason": "" if any_required_pass and replicate_powered else "detector_null_replicates_underpowered" if any_required_pass and not replicate_powered else "transport_detector_nulls_control_equivalent",
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
    detector_null_status = "detector_nulls_passed" if any(row.get("gate_name") == "structure_detector_null_separation" and int(float_or_zero(row.get("passed"))) for row in null_gates) else "detector_nulls_not_passed"
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
    }


def classify_response(row: dict[str, object]) -> str:
    if row.get("response_status") != "computed":
        return "transport_resolution_mismatch"
    alignment = float_or_zero(row.get("mean_subspace_alignment"))
    mass_delta = float_or_zero(row.get("spectral_mass_delta_fraction"))
    entropy_delta = float_or_zero(row.get("transport_entropy_delta"))
    if alignment >= 0.80 and abs(mass_delta) <= 0.15:
        return "transport_stable"
    if mass_delta <= -0.50:
        return "transport_collapses"
    if mass_delta <= -0.15:
        return "transport_weakened"
    if alignment < 0.50 and mass_delta > -0.15:
        return "transport_rerouted"
    if entropy_delta >= 0.20:
        return "transport_reopens"
    return "transport_control_equivalent"


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
    write_csv(out_dir / "horizon_transport_perturbation_manifest.csv", outputs["perturb_manifest"])
    write_csv(out_dir / "horizon_transport_response_profile_summary.csv", outputs["response_summary"])
    write_csv(out_dir / "horizon_transport_response_classification.csv", outputs["response_classification"])
    status.update(decision_fields(outputs))
    status["matrix_count"] = len(outputs["manifest"])
    status["detector_null_rows"] = len(outputs["null_anatomy"])
    status["perturbation_response_rows"] = len(outputs["response_classification"])
    status["errors"] = len(errors)
    status["finished_utc"] = utc_now()
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    write_csv(out_dir / "horizon_transport_repair_errors.csv", errors)
    write_csv(out_dir / "horizon_transport_repair_progress_checkpoints.csv", checkpoints)
    write_report(out_dir, status, outputs)
    write_manifest(out_dir)
    write_json(out_dir / "horizon_transport_repair_status.json", status)


def decision_fields(outputs: dict[str, list[dict[str, object]]]) -> dict[str, object]:
    gates = outputs["null_gates"]
    matrix_gate = any(row.get("gate_name") == "horizon_transport_matrix_coverage" and int(float_or_zero(row.get("passed"))) for row in gates)
    null_gate = any(row.get("gate_name") == "structure_detector_null_separation" and int(float_or_zero(row.get("passed"))) for row in gates)
    null_power_gate = any(row.get("gate_name") == "detector_null_replicate_power" and int(float_or_zero(row.get("passed"))) for row in gates)
    response_rows = [row for row in outputs["response_classification"] if row.get("response_class") not in {"transport_resolution_mismatch", "transport_response_underpowered"}]
    response_interpretable = bool(response_rows)
    if matrix_gate and null_gate and null_power_gate and response_interpretable:
        readiness = "ready_for_horizon_transport_smoke_expansion"
        next_action = "expand_horizon_transport_smoke"
    elif matrix_gate and not null_power_gate:
        readiness = "not_ready_repair_required"
        next_action = "repair_transport_null_controls"
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
        "ready_for_fixture_horizon_transport_tests": int(readiness == "ready_for_fixture_horizon_transport_tests"),
        "ready_for_direct_channel_diagnostics": 0,
        "not_ready_repair_required": int(readiness == "not_ready_repair_required"),
        "detector_null_gate_passed": int(null_gate),
        "detector_null_replicate_powered": int(null_power_gate),
        "perturbation_response_interpretable": int(response_interpretable),
    }


def write_report(out_dir: Path, status: dict[str, object], outputs: dict[str, list[dict[str, object]]]) -> None:
    gates = outputs["null_gates"]
    response_counts = Counter(str(row.get("response_class", "")) for row in outputs["response_classification"])
    lines = [
        "# Executive Summary",
        "",
        f"Decision: `{status.get('readiness_level', '')}`.",
        "",
        f"Next action: `{status.get('next_action_fork', '')}`.",
        "",
        f"Horizon-transport matrices built: `{status.get('matrix_count', 0)}`.",
        "",
        f"Detector-null gate passed: `{status.get('detector_null_gate_passed', 0)}`.",
        "",
        f"Detector-null replicate powered: `{status.get('detector_null_replicate_powered', 0)}`.",
        "",
        f"Perturbation response interpretable: `{status.get('perturbation_response_interpretable', 0)}`.",
        "",
        "Detector-null controls and candidate perturbation responses were written to separate outputs.",
        "",
        f"Artifact policy: {LOCAL_ONLY_ARTIFACT_POLICY}",
        "",
        "## Claim Boundary",
        "",
        CLAIM_BOUNDARY,
        "",
        "## Control Taxonomy Compliance",
        "",
        "Every matrix and response row includes intervention class, family, name, strength, interpretation role, and allowed claim level.",
        "",
        "## Horizon-Transport Matrix Construction",
        "",
        f"Matrix count: `{len(outputs['manifest'])}`.",
        f"Coverage rows: `{len(outputs['coverage'])}`.",
        "",
        "## Detector-Null Results",
        "",
        "| gate | passed | observed | blocker |",
        "|---|---:|---|---|",
    ]
    for row in gates:
        lines.append(f"| {row.get('gate_name', '')} | {row.get('passed', '')} | {row.get('observed', '')} | {row.get('blocking_reason', '')} |")
    lines.extend([
        "",
        "## Perturbation-Response Results",
        "",
        "| response_class | count |",
        "|---|---:|",
    ])
    for name, count in sorted(response_counts.items()):
        lines.append(f"| {name} | {count} |")
    lines.extend([
        "",
        "## Horizon-Pair Comparison",
        "",
        f"Subspace alignment rows: `{len(outputs['subspace_alignment'])}`.",
        "",
        "## Readiness Levels",
        "",
        f"- ready_for_horizon_transport_smoke_expansion: `{status.get('ready_for_horizon_transport_smoke_expansion', 0)}`",
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
        "See `horizon_transport_repair_output_manifest.json`.",
        "",
    ])
    (out_dir / "rfs_mb0_horizon_transport_spectral_response_repair_result.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest(out_dir: Path) -> None:
    rows = output_manifest_rows(list(OUTPUTS), out_dir)
    for row in rows:
        if row.get("file") == "horizon_transport_repair_output_manifest.json":
            row["exists"] = True
            row["status"] = "present"
    write_json(out_dir / "horizon_transport_repair_output_manifest.json", rows)


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
        "probe_key": key.probe_key,
        "flow_mode": key.flow_mode,
        "source_horizon_band": key.source_horizon_band,
        "target_horizon_band": key.target_horizon_band,
        "H_a": key.H_a,
        "H_b": key.H_b,
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
    if stat == "positive_or_nonzero_spectral_mass":
        return float(np.sum(singular))
    if stat == "effective_rank":
        return effective_rank(singular)
    if stat == "transport_concentration":
        return top_share(values.flatten(), 1)
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
