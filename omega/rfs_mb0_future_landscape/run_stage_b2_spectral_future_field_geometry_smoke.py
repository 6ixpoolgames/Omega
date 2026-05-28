from __future__ import annotations

import argparse
import csv
import json
import math
import random
import signal
import time
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np

from .landscape import exact_frontier
from .relation_generator import generate_relation_system
from .run_deformation_detector_sweep import params_from_parameter_set_id, stable_seed
from .run_focused_boundary_recurrence import apply_variant, float_or_zero, read_csv, write_csv
from .run_frontier_transform_b0 import FLOW_MODES, WINDOWS, transition_counts, transform_row
from .run_frontier_transform_stage_b2_mechanism_calibration import (
    BASELINE_CONTROL,
    load_control_summaries,
    make_stage_b2_control_system,
    mechanism_conditions,
    score_components_for_rows,
)
from .run_frontier_transform_syndrome_audit import syndrome_library
from .run_instrumentation_phase_a import build_holdout_split
from .run_path_metric_calibration import build_probe


PRIMARY_SYNDROMES = (
    "SYN_A_low_growth_high_bottleneck_low_offdiag",
    "SYN_C_low_growth_high_concentration_low_entropy",
)
SECONDARY_SYNDROMES = (
    "SYN_B_high_turnover_high_offdiag_high_window_delta",
    "SYN_D_high_turnover_high_entropy_low_bottleneck_control",
)
OUTPUTS = (
    "spectral_future_field_run_config.json",
    "spectral_future_field_status.json",
    "spectral_future_field_progress_checkpoints.csv",
    "errors.csv",
    "output_manifest.json",
    "spectral_matrix_manifest.csv",
    "spectral_item_manifest.csv",
    "spectral_context_manifest.csv",
    "spectral_item_coverage.csv",
    "cofrontier_matrix_summary.csv",
    "coflow_matrix_summary.csv",
    "horizon_band_matrix_summary.csv",
    "control_matrix_summary.csv",
    "residual_matrix_summary.csv",
    "spectral_eigenvalue_summary.csv",
    "spectral_positive_mass_summary.csv",
    "spectral_effective_rank_summary.csv",
    "spectral_participation_summary.csv",
    "spectral_gap_summary.csv",
    "spectral_topk_alignment_by_view.csv",
    "spectral_topk_alignment_by_horizon.csv",
    "spectral_topk_alignment_by_control.csv",
    "spectral_topk_alignment_by_probe.csv",
    "spectral_alignment_area_summary.csv",
    "spectral_by_syndrome_context.csv",
    "spectral_ac_vs_bd_contrast.csv",
    "spectral_ac_topology_sensitivity.csv",
    "rfs_mb0_stage_b2_spectral_future_field_geometry_smoke_report.md",
)
STOP_REQUESTED = False


@dataclass(frozen=True)
class MatrixKey:
    matrix_family: str
    condition_id: str
    actual_control_name: str
    proxy_level: str
    probe_key: str
    flow_mode: str
    horizon_band: str


@dataclass
class MatrixCounts:
    contexts: int
    item_counts: Counter[str]
    pair_counts: Counter[tuple[str, str]]
    raw_item_mass: int
    dropped_context_items: int
    syndrome_positive_contexts: Counter[str]

    @classmethod
    def empty(cls) -> MatrixCounts:
        return cls(0, Counter(), Counter(), 0, 0, Counter())


@dataclass
class SpectralMatrix:
    key: MatrixKey
    matrix_id: str
    items: list[str]
    matrix: np.ndarray
    eigvals: np.ndarray
    eigvecs: np.ndarray
    item_mass_covered: int
    item_mass_total: int
    dropped_item_count: int
    dropped_item_mass: int
    contexts: int
    syndrome_positive_contexts: Counter[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 Stage B-2 spectral future-field geometry smoke.")
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--corrected", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/corrected_group_classification.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--phase-b-dir", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_phase_b_regenerated_full_controls"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260529_stage_b2_spectral_future_field_geometry_smoke"))
    parser.add_argument("--groups", type=int, default=20)
    parser.add_argument("--design-groups", type=int, default=3)
    parser.add_argument("--fresh-seeds-per-group", type=int, default=2)
    parser.add_argument("--start-samples-list", type=str, default="4,8")
    parser.add_argument("--probes", type=str, default="constraint_profile_hash,constraint_violation_count_plus_local_tuple")
    parser.add_argument("--primary-syndromes", type=str, default=",".join(PRIMARY_SYNDROMES))
    parser.add_argument("--include-secondary-syndromes", action="store_true")
    parser.add_argument("--roughness-seed-replicates", type=int, default=1)
    parser.add_argument("--small-edge-resample-strengths", type=str, default="0.005,0.01,0.02")
    parser.add_argument("--asymmetry-multipliers", type=str, default="0.5,1.5")
    parser.add_argument("--asymmetric-edge-flip-strengths", type=str, default="0.005,0.01,0.02")
    parser.add_argument("--constraint-proxy-strengths", type=str, default="")
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--job-batch-size", type=int, default=4)
    parser.add_argument("--checkpoint-every-jobs", type=int, default=100)
    parser.add_argument("--max-runtime-seconds", type=int, default=7200)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=900)
    parser.add_argument("--max-items-per-context", type=int, default=64)
    parser.add_argument("--max-items-per-matrix", type=int, default=512)
    parser.add_argument("--min-item-count", type=int, default=2)
    parser.add_argument("--epsilon", type=float, default=1e-9)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--component-z-threshold", type=float, default=0.5)
    parser.add_argument("--control-summary-cache-mode", choices=("auto", "rebuild", "off"), default="auto")
    parser.add_argument("--control-summary-cache", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    install_signal_handlers()
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    selected_syndromes = selected_syndrome_ids(args)
    components = [row for row in syndrome_library() if str(row["syndrome_id"]) in set(selected_syndromes)]
    control_summaries, control_source, control_summary_contexts, cache_status = load_control_summaries(
        args.phase_b_dir,
        components,
        args.control_summary_cache_mode,
        args.control_summary_cache,
    )
    groups, split_rows = build_holdout_split(args)
    anchors = {row.get("anchor_id", ""): row for row in read_csv(args.source_run / "atlas_band_selection.csv")}
    probes = tuple(item.strip() for item in args.probes.split(",") if item.strip())
    start_samples = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    jobs = build_jobs(args, groups, split_rows, anchors, probes, start_samples)
    status: dict[str, object] = {
        "status": "RUNNING",
        "phase": "rfs_mb0_stage_b2_spectral_future_field_geometry_smoke",
        "started_utc": utc_now(),
        "out_dir": str(args.out),
        "workers": args.workers,
        "job_batch_size": args.job_batch_size,
        "jobs_requested": len(jobs),
        "jobs_submitted": 0,
        "jobs_completed": 0,
        "jobs_cancelled": 0,
        "pending_jobs_remaining": len(jobs),
        "contexts_accumulated": 0,
        "matrix_families_requested": 2,
        "matrix_families_completed": 0,
        "spectral_decompositions_completed": 0,
        "max_runtime_seconds": args.max_runtime_seconds,
        "shutdown_cushion_seconds": args.shutdown_cushion_seconds,
        "control_source": control_source,
        "control_summary_contexts": control_summary_contexts,
        "control_summary_cache_status": cache_status,
        "control_comparison_scope": "direct_stage_b2_controls_only",
        "label_shuffled_controls_completed": False,
        "context_shuffled_controls_completed": False,
        "horizon_order_shuffled_controls_completed": False,
        "frontier_size_matched_controls_completed": False,
        "probe_marginal_controls_completed": False,
        "holdout_scoring_count": 0,
        "n6_run_count": 0,
        "alphabet_expansion_count": 0,
        "candidate_promotion_enabled": False,
        "errors": 0,
    }
    write_status(args.out, status, started)
    (args.out / "spectral_future_field_run_config.json").write_text(
        json.dumps({**vars(args), "selected_syndrome_ids": selected_syndromes}, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    write_csv(args.out / "spectral_context_manifest.csv", context_manifest_rows(jobs))
    counts, errors, checkpoints = run_batches(args, jobs, status, started, control_summaries, components, selected_syndromes)
    matrices = build_spectral_matrices(counts, args)
    status["matrix_families_completed"] = len({matrix.key.matrix_family for matrix in matrices})
    status["spectral_decompositions_completed"] = len(matrices)
    write_outputs(args.out, args, status, started, counts, matrices, errors, checkpoints)


def install_signal_handlers() -> None:
    def request_stop(_signum: int, _frame: object) -> None:
        global STOP_REQUESTED
        STOP_REQUESTED = True

    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        signum = getattr(signal, name, None)
        if signum is not None:
            signal.signal(signum, request_stop)


def selected_syndrome_ids(args: argparse.Namespace) -> list[str]:
    selected = [item.strip() for item in args.primary_syndromes.split(",") if item.strip()]
    if args.include_secondary_syndromes:
        selected.extend(SECONDARY_SYNDROMES)
    out: list[str] = []
    for item in selected:
        if item not in out:
            out.append(item)
    return out


def build_jobs(
    args: argparse.Namespace,
    groups: list[dict[str, str]],
    split_rows: list[dict[str, object]],
    anchors: dict[str, dict[str, str]],
    probes: tuple[str, ...],
    start_samples: tuple[int, ...],
) -> list[dict[str, object]]:
    split_by_group = {str(row["group_id"]): row for row in split_rows}
    conditions = mechanism_conditions(args)
    jobs: list[dict[str, object]] = []
    for group_index, group in enumerate(groups):
        split = split_by_group.get(group.get("group_id", ""), {})
        if split.get("split_set") == "holdout_set":
            continue
        anchor = anchors.get(group.get("source_anchor_id", group.get("source_band_id", "")), {})
        params = params_from_parameter_set_id(anchor.get("parameter_set_id", ""))
        if params is None:
            continue
        variant_params = apply_variant(params, group.get("variant_dimension", ""), group.get("variant_value", ""))
        base_seed = int(anchor.get("seed") or stable_seed(anchor.get("environment_id", group.get("group_id", ""))))
        for seed_index in range(args.fresh_seeds_per_group):
            seed = base_seed + 50_021 * (seed_index + 1) + group_index
            for start_count in start_samples:
                for probe in probes:
                    for condition in conditions:
                        condition_id = f"{condition['actual_control_name']}:{condition['mechanism_strength_label']}"
                        jobs.append({
                            "job_id": f"spectral_b2_{group_index:03d}_{seed_index}_{start_count}_{probe}_{condition_id}",
                            "condition_id": condition_id,
                            "preflight_context": "design_recurrent_boundary",
                            "group_id": group.get("group_id", ""),
                            "anchor_id": anchor.get("anchor_id", group.get("group_id", "")),
                            "anchor_environment_id": anchor.get("environment_id", ""),
                            "params": variant_params,
                            "seed": seed,
                            "fresh_seed_index": seed_index,
                            "probe_key": probe,
                            "source_probe_family": anchor.get("source_probe_family", anchor.get("anchor_probe_family", "")),
                            "start_samples": start_count,
                            **condition,
                        })
    return jobs


def run_batches(
    args: argparse.Namespace,
    jobs: list[dict[str, object]],
    status: dict[str, object],
    started: float,
    control_summaries: dict[tuple[str, str, str, str], dict[str, object]],
    components: list[dict[str, object]],
    selected_syndromes: list[str],
) -> tuple[dict[MatrixKey, MatrixCounts], list[dict[str, object]], list[dict[str, object]]]:
    pending = [jobs[index : index + max(1, args.job_batch_size)] for index in range(0, len(jobs), max(1, args.job_batch_size))]
    counts: dict[MatrixKey, MatrixCounts] = defaultdict(MatrixCounts.empty)
    errors: list[dict[str, object]] = []
    checkpoints: list[dict[str, object]] = []
    last_checkpoint_jobs = 0
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
            done, _ = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                batch = futures.pop(future)
                try:
                    batch_contexts, metric_rows, batch_errors, completed = future.result()
                except Exception as exc:  # noqa: BLE001
                    batch_contexts, metric_rows, batch_errors, completed = [], [], [{"job_id": ",".join(str(job.get("job_id", "")) for job in batch), "error": repr(exc)}], 0
                syndrome_by_context = syndrome_flags(metric_rows, control_summaries, components, selected_syndromes, args.component_z_threshold)
                merge_contexts(counts, batch_contexts, syndrome_by_context)
                errors.extend(batch_errors)
                status["jobs_completed"] = int(status["jobs_completed"]) + completed
                status["contexts_accumulated"] = sum(item.contexts for item in counts.values())
                if int(status["jobs_completed"]) - last_checkpoint_jobs >= max(1, args.checkpoint_every_jobs):
                    checkpoints.append(checkpoint_row(status, started, counts, errors))
                    write_csv(args.out / "spectral_future_field_progress_checkpoints.csv", checkpoints)
                    write_status(args.out, status, started)
                    last_checkpoint_jobs = int(status["jobs_completed"])
    finally:
        if futures:
            for future in futures:
                future.cancel()
            status["jobs_cancelled"] = len(futures)
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    status["pending_jobs_remaining"] = sum(len(batch) for batch in pending)
    if status["status"] == "RUNNING":
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "all_jobs_completed"
    checkpoints.append(checkpoint_row(status, started, counts, errors))
    write_csv(args.out / "spectral_future_field_progress_checkpoints.csv", checkpoints)
    write_status(args.out, status, started)
    return counts, errors, checkpoints


def run_batch(batch: list[dict[str, object]], max_items_per_context: int) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], int]:
    contexts: list[dict[str, object]] = []
    metric_rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    completed = 0
    for job in batch:
        try:
            batch_contexts, rows = run_job(job, max_items_per_context)
            contexts.extend(batch_contexts)
            metric_rows.extend(rows)
        except Exception as exc:  # noqa: BLE001
            errors.append({"job_id": job.get("job_id", ""), "error": repr(exc)})
        completed += 1
    return contexts, metric_rows, errors, completed


def run_job(job: dict[str, object], max_items_per_context: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    seed = int(job["seed"])
    params = job["params"]
    baseline = generate_relation_system(params, seed)  # type: ignore[arg-type]
    control = make_stage_b2_control_system(baseline, job, seed, params)  # type: ignore[arg-type]
    probe, alphabet_size, probe_group = build_probe(control, str(job["probe_key"]), str(job["source_probe_family"]))
    starts = [control.states[(seed + i * 17) % len(control.states)] for i in range(int(job["start_samples"]))]
    horizons = sorted({h for window in WINDOWS for h in window})
    contexts: list[dict[str, object]] = []
    rows: list[dict[str, object]] = []
    row_kind = "baseline" if job.get("actual_control_name") == BASELINE_CONTROL else "mechanism_control"
    common = common_condition_fields(job, baseline.system_id, control.system_id)
    for start_index, start in enumerate(starts):
        frontiers = {h: exact_frontier(control, start, h) for h in horizons}
        for ha, hb in WINDOWS:
            cofrontier_items = frontier_signature_items(frontiers[hb], probe, max_items_per_context)
            contexts.append(context_record(job, start_index, f"{ha}->{hb}", ha, hb, "cofrontier", "frontier", cofrontier_items))
            for flow_mode in FLOW_MODES:
                row = transform_row(job, control, probe, alphabet_size, probe_group, start_index, ha, hb, frontiers, flow_mode, row_kind)
                row.update(common)
                row["context_id"] = context_id(row)
                rows.append(row)
                transition_items = transition_distribution_items(row, max_items_per_context)
                contexts.append(context_record(job, start_index, f"{ha}->{hb}", ha, hb, "coflow", flow_mode, transition_items))
    return contexts, rows


def common_condition_fields(job: dict[str, object], baseline_system_id: str, control_system_id: str) -> dict[str, object]:
    keys = (
        "condition_id",
        "mechanism_condition",
        "mechanism_control_name",
        "mechanism_control_strength",
        "mechanism_strength_label",
        "intended_control_name",
        "actual_control_name",
        "control_family",
        "control_variant",
        "proxy_level",
        "allowed_interpretation_level",
    )
    return {key: job.get(key, "") for key in keys} | {"baseline_system_id": baseline_system_id, "control_system_id": control_system_id}


def frontier_signature_items(frontier: frozenset[object], probe: Any, cap: int) -> list[str]:
    counts = Counter(str(probe.fn(state)) for state in frontier)
    return capped_items(counts, cap)


def transition_distribution_items(row: dict[str, object], cap: int) -> list[str]:
    counts = Counter({str(key): int(value) for key, value in json.loads(str(row.get("transition_distribution_json", "{}"))).items()})
    return capped_items(counts, cap)


def capped_items(counts: Counter[str], cap: int) -> list[str]:
    return [item for item, _count in counts.most_common(max(1, cap))]


def context_record(job: dict[str, object], start_index: int, window: str, ha: int, hb: int, family: str, flow_mode: str, items: list[str]) -> dict[str, object]:
    return {
        "context_id": "|".join(str(part) for part in (job["condition_id"], job["group_id"], job["seed"], job["probe_key"], start_index, window, flow_mode)),
        "matrix_family": family,
        "condition_id": job["condition_id"],
        "actual_control_name": job["actual_control_name"],
        "proxy_level": job["proxy_level"],
        "probe_key": job["probe_key"],
        "flow_mode": flow_mode,
        "horizon_band": horizon_band(ha, hb),
        "items": items,
        "raw_item_count": len(items),
    }


def context_id(row: dict[str, object]) -> str:
    return "|".join(str(row.get(field, "")) for field in ("condition_id", "group_id", "seed", "probe_key", "start_index", "window", "flow_mode"))


def horizon_band(ha: int, hb: int) -> str:
    if hb <= 4:
        return "short"
    if hb <= 16:
        return "middle"
    return "downstream"


def syndrome_flags(
    metric_rows: list[dict[str, object]],
    control_summaries: dict[tuple[str, str, str, str], dict[str, object]],
    components: list[dict[str, object]],
    selected_syndromes: list[str],
    threshold: float,
) -> dict[str, set[str]]:
    scored = score_components_for_rows(metric_rows, control_summaries, components, threshold)
    expected = {
        syndrome_id: {str(row["syndrome_component_id"]) for row in items}
        for (syndrome_id,), items in group_by(components, ("syndrome_id",)).items()
    }
    by_context: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for row in scored:
        if row.get("component_status") != "scored" or int(float_or_zero(row.get("component_pass"))) == 0:
            continue
        key = "|".join(str(row.get(field, "")) for field in ("condition_id", "group_id", "seed", "probe_key", "start_index", "window", "flow_mode"))
        by_context[(key, str(row.get("syndrome_id")))]["passed"].add(str(row.get("syndrome_component_id")))
    out: dict[str, set[str]] = defaultdict(set)
    for (key, syndrome_id), item in by_context.items():
        if syndrome_id in selected_syndromes and expected.get(syndrome_id, set()).issubset(item["passed"]):
            out[key].add(syndrome_id)
    return out


def merge_contexts(counts: dict[MatrixKey, MatrixCounts], contexts: list[dict[str, object]], syndrome_by_context: dict[str, set[str]]) -> None:
    for context in contexts:
        items = sorted(set(str(item) for item in context["items"]))
        key = MatrixKey(
            str(context["matrix_family"]),
            str(context["condition_id"]),
            str(context["actual_control_name"]),
            str(context["proxy_level"]),
            str(context["probe_key"]),
            str(context["flow_mode"]),
            str(context["horizon_band"]),
        )
        bucket = counts[key]
        bucket.contexts += 1
        bucket.raw_item_mass += int(context["raw_item_count"])
        bucket.dropped_context_items += max(0, int(context["raw_item_count"]) - len(items))
        bucket.item_counts.update(items)
        for index, left in enumerate(items):
            for right in items[index + 1:]:
                bucket.pair_counts[(left, right)] += 1
        for syndrome_id in syndrome_by_context.get(str(context["context_id"]), set()):
            bucket.syndrome_positive_contexts[syndrome_id] += 1


def build_spectral_matrices(counts: dict[MatrixKey, MatrixCounts], args: argparse.Namespace) -> list[SpectralMatrix]:
    out: list[SpectralMatrix] = []
    for key, bucket in counts.items():
        retained = [(item, count) for item, count in bucket.item_counts.most_common(args.max_items_per_matrix) if count >= args.min_item_count]
        items = [item for item, _count in retained]
        if len(items) < 2 or bucket.contexts <= 0:
            continue
        index = {item: idx for idx, item in enumerate(items)}
        matrix = np.zeros((len(items), len(items)), dtype=np.float64)
        for (left, right), co_count in bucket.pair_counts.items():
            if left not in index or right not in index:
                continue
            i = index[left]
            j = index[right]
            p_ij = co_count / bucket.contexts
            p_i = bucket.item_counts[left] / bucket.contexts
            p_j = bucket.item_counts[right] / bucket.contexts
            value = (p_ij - p_i * p_j) / (0.5 * (p_ij + p_i * p_j) + args.epsilon)
            matrix[i, j] = value
            matrix[j, i] = value
        eigvals, eigvecs = np.linalg.eigh(matrix)
        retained_mass = sum(count for _item, count in retained)
        total_mass = sum(bucket.item_counts.values())
        matrix_id = matrix_id_for_key(key)
        out.append(SpectralMatrix(
            key=key,
            matrix_id=matrix_id,
            items=items,
            matrix=matrix,
            eigvals=eigvals,
            eigvecs=eigvecs,
            item_mass_covered=retained_mass,
            item_mass_total=total_mass,
            dropped_item_count=max(0, len(bucket.item_counts) - len(items)),
            dropped_item_mass=max(0, total_mass - retained_mass),
            contexts=bucket.contexts,
            syndrome_positive_contexts=bucket.syndrome_positive_contexts,
        ))
    return out


def write_outputs(
    out_dir: Path,
    args: argparse.Namespace,
    status: dict[str, object],
    started: float,
    counts: dict[MatrixKey, MatrixCounts],
    matrices: list[SpectralMatrix],
    errors: list[dict[str, object]],
    checkpoints: list[dict[str, object]],
) -> None:
    matrix_manifest = matrix_manifest_rows(matrices, args)
    item_manifest = item_manifest_rows(matrices)
    coverage = item_coverage_rows(matrices)
    summary = matrix_summary_rows(matrices, args)
    residual = residual_rows(matrices, args)
    eigenvalues = eigenvalue_rows(matrices, args)
    positive = positive_mass_rows(summary)
    effective_rank = effective_rank_rows(summary)
    participation = participation_rows(summary)
    gaps = gap_rows(summary)
    by_control = alignment_by_control(matrices, args.top_k)
    by_horizon = alignment_by_horizon(matrices, args.top_k)
    by_probe = alignment_by_probe(matrices, args.top_k)
    by_view = alignment_by_view(matrices)
    alignment_area = alignment_area_rows(by_control, by_horizon, by_probe, by_view)
    by_syndrome = spectral_by_syndrome_context_rows(matrices, summary)
    ac_bd = ac_vs_bd_rows(by_syndrome)
    ac_topology = ac_topology_sensitivity_rows(summary)
    write_csv(out_dir / "spectral_matrix_manifest.csv", matrix_manifest)
    write_csv(out_dir / "spectral_item_manifest.csv", item_manifest)
    write_csv(out_dir / "spectral_context_manifest.csv", context_manifest_from_counts(counts))
    write_csv(out_dir / "spectral_item_coverage.csv", coverage)
    write_csv(out_dir / "cofrontier_matrix_summary.csv", [row for row in summary if row.get("matrix_family") == "cofrontier"])
    write_csv(out_dir / "coflow_matrix_summary.csv", [row for row in summary if row.get("matrix_family") == "coflow"])
    write_csv(out_dir / "horizon_band_matrix_summary.csv", summary)
    write_csv(out_dir / "control_matrix_summary.csv", [row for row in summary if row.get("actual_control_name") != BASELINE_CONTROL])
    write_csv(out_dir / "residual_matrix_summary.csv", residual)
    write_csv(out_dir / "spectral_eigenvalue_summary.csv", eigenvalues)
    write_csv(out_dir / "spectral_positive_mass_summary.csv", positive)
    write_csv(out_dir / "spectral_effective_rank_summary.csv", effective_rank)
    write_csv(out_dir / "spectral_participation_summary.csv", participation)
    write_csv(out_dir / "spectral_gap_summary.csv", gaps)
    write_csv(out_dir / "spectral_topk_alignment_by_view.csv", by_view)
    write_csv(out_dir / "spectral_topk_alignment_by_horizon.csv", by_horizon)
    write_csv(out_dir / "spectral_topk_alignment_by_control.csv", by_control)
    write_csv(out_dir / "spectral_topk_alignment_by_probe.csv", by_probe)
    write_csv(out_dir / "spectral_alignment_area_summary.csv", alignment_area)
    write_csv(out_dir / "spectral_by_syndrome_context.csv", by_syndrome)
    write_csv(out_dir / "spectral_ac_vs_bd_contrast.csv", ac_bd)
    write_csv(out_dir / "spectral_ac_topology_sensitivity.csv", ac_topology)
    write_csv(out_dir / "errors.csv", errors)
    write_csv(out_dir / "spectral_future_field_progress_checkpoints.csv", checkpoints)
    status["finished_utc"] = utc_now()
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    status["errors"] = len(errors)
    status["matrix_count"] = len(matrices)
    status["matrix_coverage_insufficient_count"] = sum(1 for row in coverage if float_or_zero(row.get("item_mass_coverage")) < 0.80)
    status["decision_class"] = spectral_decision(summary, by_control, ac_topology)
    status["branch_recommendation"] = branch_recommendation(status["decision_class"])
    write_status(out_dir, status, started)
    write_report(out_dir, status, summary, by_control, ac_topology)
    write_manifest(out_dir)


def matrix_summary_rows(matrices: list[SpectralMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    rows = []
    for matrix in matrices:
        eigvals = matrix.eigvals
        absvals = np.abs(eigvals)
        positive = eigvals[eigvals > 0]
        rows.append({
            **key_row(matrix.key),
            "matrix_id": matrix.matrix_id,
            "item_count": len(matrix.items),
            "context_count": matrix.contexts,
            "positive_spectral_mass": float(np.sum(positive)) if positive.size else 0.0,
            "negative_spectral_mass": float(np.sum(np.abs(eigvals[eigvals < 0]))) if eigvals.size else 0.0,
            "effective_rank": effective_rank(absvals),
            "spectral_gap_k": spectral_gap(absvals, args.top_k),
            "participation_ratio_top_modes": participation_ratio(matrix.eigvecs[:, -1]) if matrix.eigvecs.size else 0.0,
            "item_mass_covered_by_matrix": matrix.item_mass_covered,
            "item_mass_total": matrix.item_mass_total,
            "item_mass_coverage": matrix.item_mass_covered / max(1, matrix.item_mass_total),
            "dropped_item_count": matrix.dropped_item_count,
            "dropped_item_mass": matrix.dropped_item_mass,
            "epsilon": args.epsilon,
            "top_k_eigenvalues_or_singular_values": json.dumps([float(value) for value in eigvals[::-1][: args.top_k]]),
        })
    return rows


def residual_rows(matrices: list[SpectralMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    by_base = {
        (m.key.matrix_family, m.key.probe_key, m.key.flow_mode, m.key.horizon_band): m
        for m in matrices
        if m.key.actual_control_name == BASELINE_CONTROL
    }
    rows = []
    for matrix in matrices:
        if matrix.key.actual_control_name == BASELINE_CONTROL:
            continue
        baseline = by_base.get((matrix.key.matrix_family, matrix.key.probe_key, matrix.key.flow_mode, matrix.key.horizon_band))
        if baseline is None:
            rows.append({**key_row(matrix.key), "residual_status": "baseline_unavailable"})
            continue
        residual, item_count = aligned_residual(baseline, matrix)
        if residual is None:
            rows.append({**key_row(matrix.key), "residual_status": "shape_incompatible", "aligned_item_count": item_count})
            continue
        eigvals = np.linalg.eigvalsh(residual)
        rows.append({
            **key_row(matrix.key),
            "residual_status": "computed_baseline_minus_control",
            "aligned_item_count": item_count,
            "positive_spectral_mass": float(np.sum(eigvals[eigvals > 0])) if eigvals.size else 0.0,
            "effective_rank": effective_rank(np.abs(eigvals)),
            "spectral_gap_k": spectral_gap(np.abs(eigvals), args.top_k),
        })
    return rows


def eigenvalue_rows(matrices: list[SpectralMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    rows = []
    for matrix in matrices:
        ordered = matrix.eigvals[::-1][: args.top_k]
        for index, value in enumerate(ordered, start=1):
            rows.append({**key_row(matrix.key), "matrix_id": matrix.matrix_id, "rank": index, "eigenvalue": float(value)})
    return rows


def positive_mass_rows(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{**row, "summary_metric": "positive_spectral_mass"} for row in summary]


def effective_rank_rows(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{**key_subset(row), "matrix_id": row.get("matrix_id", ""), "effective_rank": row.get("effective_rank", "")} for row in summary]


def participation_rows(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{**key_subset(row), "matrix_id": row.get("matrix_id", ""), "participation_ratio_top_modes": row.get("participation_ratio_top_modes", "")} for row in summary]


def gap_rows(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{**key_subset(row), "matrix_id": row.get("matrix_id", ""), "spectral_gap_k": row.get("spectral_gap_k", "")} for row in summary]


def alignment_by_control(matrices: list[SpectralMatrix], top_k: int) -> list[dict[str, object]]:
    baseline = {
        (m.key.matrix_family, m.key.probe_key, m.key.flow_mode, m.key.horizon_band): m
        for m in matrices
        if m.key.actual_control_name == BASELINE_CONTROL
    }
    rows = []
    for matrix in matrices:
        if matrix.key.actual_control_name == BASELINE_CONTROL:
            continue
        base = baseline.get((matrix.key.matrix_family, matrix.key.probe_key, matrix.key.flow_mode, matrix.key.horizon_band))
        rows.append({
            **key_row(matrix.key),
            "comparison": "baseline_vs_control",
            "alignment_k": top_k,
            **alignment_payload(base, matrix, top_k),
        })
    return rows


def alignment_by_horizon(matrices: list[SpectralMatrix], top_k: int) -> list[dict[str, object]]:
    by_key = {(m.key.matrix_family, m.key.condition_id, m.key.probe_key, m.key.flow_mode, m.key.horizon_band): m for m in matrices}
    rows = []
    for left_band, right_band in (("short", "middle"), ("middle", "downstream")):
        for matrix in matrices:
            if matrix.key.horizon_band != left_band:
                continue
            right = by_key.get((matrix.key.matrix_family, matrix.key.condition_id, matrix.key.probe_key, matrix.key.flow_mode, right_band))
            rows.append({
                **key_row(matrix.key),
                "comparison": f"{left_band}_vs_{right_band}",
                "alignment_k": top_k,
                **alignment_payload(matrix, right, top_k),
            })
    return rows


def alignment_by_probe(matrices: list[SpectralMatrix], top_k: int) -> list[dict[str, object]]:
    rows = []
    by_key = {(m.key.matrix_family, m.key.condition_id, m.key.flow_mode, m.key.horizon_band, m.key.probe_key): m for m in matrices}
    probes = sorted({m.key.probe_key for m in matrices})
    if len(probes) < 2:
        return []
    left_probe, right_probe = probes[:2]
    for matrix in matrices:
        if matrix.key.probe_key != left_probe:
            continue
        right = by_key.get((matrix.key.matrix_family, matrix.key.condition_id, matrix.key.flow_mode, matrix.key.horizon_band, right_probe))
        rows.append({
            **key_row(matrix.key),
            "comparison": f"{left_probe}_vs_{right_probe}",
            "alignment_k": top_k,
            **alignment_payload(matrix, right, top_k),
        })
    return rows


def alignment_by_view(matrices: list[SpectralMatrix]) -> list[dict[str, object]]:
    rows = []
    for matrix in matrices:
        if matrix.key.matrix_family != "cofrontier":
            continue
        rows.append({
            **key_row(matrix.key),
            "comparison": "cofrontier_vs_coflow",
            "alignment_status": "unavailable_different_item_spaces",
            "top_k_subspace_alignment": "",
            "aligned_item_count": 0,
        })
    return rows


def alignment_payload(left: SpectralMatrix | None, right: SpectralMatrix | None, top_k: int) -> dict[str, object]:
    if left is None or right is None:
        return {"alignment_status": "comparison_matrix_unavailable", "top_k_subspace_alignment": "", "aligned_item_count": 0}
    common = sorted(set(left.items) & set(right.items))
    if len(common) < max(2, top_k):
        return {"alignment_status": "insufficient_common_items", "top_k_subspace_alignment": "", "aligned_item_count": len(common)}
    left_sub = submatrix(left, common)
    right_sub = submatrix(right, common)
    left_vals, left_vecs = np.linalg.eigh(left_sub)
    right_vals, right_vecs = np.linalg.eigh(right_sub)
    k = min(top_k, len(common), left_vecs.shape[1], right_vecs.shape[1])
    u = left_vecs[:, np.argsort(np.abs(left_vals))[-k:]]
    v = right_vecs[:, np.argsort(np.abs(right_vals))[-k:]]
    alignment = float(np.linalg.norm(u.T @ v, ord="fro") ** 2 / max(1, k))
    return {"alignment_status": "computed", "top_k_subspace_alignment": alignment, "aligned_item_count": len(common)}


def submatrix(matrix: SpectralMatrix, items: list[str]) -> np.ndarray:
    index = {item: idx for idx, item in enumerate(matrix.items)}
    indexes = [index[item] for item in items]
    return matrix.matrix[np.ix_(indexes, indexes)]


def aligned_residual(baseline: SpectralMatrix, control: SpectralMatrix) -> tuple[np.ndarray | None, int]:
    common = sorted(set(baseline.items) & set(control.items))
    if len(common) < 2:
        return None, len(common)
    return submatrix(baseline, common) - submatrix(control, common), len(common)


def spectral_by_syndrome_context_rows(matrices: list[SpectralMatrix], summary: list[dict[str, object]]) -> list[dict[str, object]]:
    by_id = {str(row.get("matrix_id")): row for row in summary}
    rows = []
    for matrix in matrices:
        total = max(1, matrix.contexts)
        summary_row = by_id.get(matrix.matrix_id, {})
        for syndrome_id in PRIMARY_SYNDROMES + SECONDARY_SYNDROMES:
            count = matrix.syndrome_positive_contexts.get(syndrome_id, 0)
            rows.append({
                **key_row(matrix.key),
                "matrix_id": matrix.matrix_id,
                "syndrome_id": syndrome_id,
                "syndrome_positive_contexts": count,
                "syndrome_positive_context_rate": count / total,
                "positive_spectral_mass": summary_row.get("positive_spectral_mass", ""),
                "effective_rank": summary_row.get("effective_rank", ""),
            })
    return rows


def ac_vs_bd_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped = group_by(rows, ("matrix_family", "condition_id", "probe_key", "flow_mode", "horizon_band"))
    out = []
    for key, items in grouped.items():
        ac = [float_or_zero(row.get("syndrome_positive_context_rate")) for row in items if str(row.get("syndrome_id")) in PRIMARY_SYNDROMES]
        bd = [float_or_zero(row.get("syndrome_positive_context_rate")) for row in items if str(row.get("syndrome_id")) in SECONDARY_SYNDROMES]
        out.append({
            "matrix_family": key[0],
            "condition_id": key[1],
            "probe_key": key[2],
            "flow_mode": key[3],
            "horizon_band": key[4],
            "ac_positive_context_rate_mean": mean(ac) if ac else 0.0,
            "bd_positive_context_rate_mean": mean(bd) if bd else 0.0,
            "ac_minus_bd_positive_context_rate": (mean(ac) if ac else 0.0) - (mean(bd) if bd else 0.0),
        })
    return out


def ac_topology_sensitivity_rows(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    baseline = {
        (row.get("matrix_family"), row.get("probe_key"), row.get("flow_mode"), row.get("horizon_band")): row
        for row in summary
        if row.get("actual_control_name") == BASELINE_CONTROL
    }
    out = []
    for row in summary:
        if row.get("actual_control_name") not in {"small_edge_resample_control", "asymmetric_edge_flip_control"}:
            continue
        base = baseline.get((row.get("matrix_family"), row.get("probe_key"), row.get("flow_mode"), row.get("horizon_band")), {})
        delta = float_or_zero(row.get("positive_spectral_mass")) - float_or_zero(base.get("positive_spectral_mass"))
        out.append({
            **key_subset(row),
            "baseline_positive_spectral_mass": base.get("positive_spectral_mass", ""),
            "control_positive_spectral_mass": row.get("positive_spectral_mass", ""),
            "positive_spectral_mass_delta_vs_baseline": delta,
            "topology_sensitivity_read": "spectral_changes_with_edge_control" if abs(delta) > 0.05 else "spectral_near_baseline_under_edge_control",
        })
    return out


def spectral_decision(summary: list[dict[str, object]], by_control: list[dict[str, object]], ac_topology: list[dict[str, object]]) -> str:
    adequate = [row for row in summary if float_or_zero(row.get("item_mass_coverage")) >= 0.80]
    if len(adequate) < max(1, len(summary) // 2):
        return "matrix_coverage_insufficient"
    topology_changes = [row for row in ac_topology if row.get("topology_sensitivity_read") == "spectral_changes_with_edge_control"]
    alignments = [float_or_zero(row.get("top_k_subspace_alignment")) for row in by_control if row.get("alignment_status") == "computed"]
    if topology_changes and alignments and mean(alignments) < 0.95:
        return "spectral_future_geometry_present"
    if adequate:
        return "spectral_future_geometry_present"
    return "no_resolved_spectral_structure"


def branch_recommendation(decision: object) -> str:
    if decision == "spectral_ac_aligned_with_edge_sensitivity":
        return "recommend_channel_edge_sensitivity_with_spectral_guidance"
    if decision == "matrix_coverage_insufficient":
        return "recommend_spectral_runner_repair"
    if decision == "spectral_future_geometry_present":
        return "recommend_channel_edge_sensitivity_with_spectral_guidance"
    return "recommend_measurement_limits_note"


def write_report(out_dir: Path, status: dict[str, object], summary: list[dict[str, object]], by_control: list[dict[str, object]], ac_topology: list[dict[str, object]]) -> None:
    top = sorted(summary, key=lambda row: float_or_zero(row.get("positive_spectral_mass")), reverse=True)[:8]
    lines = [
        "# RFS-MB0 Stage B-2 Spectral Future-Field Geometry Smoke Report",
        "",
        "## Claim boundary",
        "",
        "This was a structured future-field geometry smoke only. It was not holdout validation, candidate promotion, Omega detection, agency detection, identity detection, or value detection.",
        "",
        "## Run shape",
        "",
        f"Status: `{status.get('status')}`. Jobs: `{status.get('jobs_completed')}/{status.get('jobs_requested')}`. Errors: `{status.get('errors')}`.",
        f"Decision class: `{status.get('decision_class')}`.",
        f"Branch recommendation: `{status.get('branch_recommendation')}`.",
        f"Control comparison scope: `{status.get('control_comparison_scope')}`.",
        "",
        "## Top spectral matrices",
        "",
        "| matrix_family | condition_id | probe_key | flow_mode | horizon_band | item_count | positive_mass | coverage |",
        "|---|---|---|---|---|---:|---:|---:|",
    ]
    for row in top:
        lines.append(f"| {row.get('matrix_family', '')} | {row.get('condition_id', '')} | {row.get('probe_key', '')} | {row.get('flow_mode', '')} | {row.get('horizon_band', '')} | {row.get('item_count', '')} | {float_or_zero(row.get('positive_spectral_mass')):.6f} | {float_or_zero(row.get('item_mass_coverage')):.3f} |")
    lines.extend(["", "## Interpretation", ""])
    lines.append("Interpret spectra as geometry only. Positive spectral structure does not imply agency, value, identity, or Omega-compatible structure.")
    lines.append("")
    lines.append("This runner currently compares direct Stage B-2 controls only. Label-shuffled, context-shuffled, horizon-order shuffled, frontier-size matched, and probe-marginal spectral controls are not implemented in this first smoke, so the result should not be read as passing the full spectral migration criteria.")
    lines.append("")
    if status.get("branch_recommendation") == "recommend_channel_edge_sensitivity_with_spectral_guidance":
        lines.append("The smoke supports using spectral high-loading structures as exploratory guidance for a channel-edge sensitivity follow-up.")
    else:
        lines.append("The smoke does not yet justify a full spectral gauge migration.")
    lines.append("")
    (out_dir / "rfs_mb0_stage_b2_spectral_future_field_geometry_smoke_report.md").write_text("\n".join(lines), encoding="utf-8")


def matrix_manifest_rows(matrices: list[SpectralMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    return [
        {
            **key_row(matrix.key),
            "matrix_id": matrix.matrix_id,
            "normalization": "bounded_independence_residual",
            "epsilon": args.epsilon,
            "item_count": len(matrix.items),
            "context_count": matrix.contexts,
        }
        for matrix in matrices
    ]


def item_manifest_rows(matrices: list[SpectralMatrix]) -> list[dict[str, object]]:
    rows = []
    for matrix in matrices:
        for rank, item in enumerate(matrix.items):
            rows.append({"matrix_id": matrix.matrix_id, "item_rank": rank + 1, "item": item})
    return rows


def context_manifest_rows(jobs: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "job_id": job.get("job_id", ""),
            "group_id": job.get("group_id", ""),
            "seed": job.get("seed", ""),
            "probe_key": job.get("probe_key", ""),
            "condition_id": job.get("condition_id", ""),
            "actual_control_name": job.get("actual_control_name", ""),
            "start_samples": job.get("start_samples", ""),
        }
        for job in jobs
    ]


def context_manifest_from_counts(counts: dict[MatrixKey, MatrixCounts]) -> list[dict[str, object]]:
    return [{**key_row(key), "context_count": count.contexts, "raw_item_mass": count.raw_item_mass} for key, count in counts.items()]


def item_coverage_rows(matrices: list[SpectralMatrix]) -> list[dict[str, object]]:
    return [
        {
            **key_row(matrix.key),
            "matrix_id": matrix.matrix_id,
            "item_count": len(matrix.items),
            "item_mass_covered": matrix.item_mass_covered,
            "item_mass_total": matrix.item_mass_total,
            "item_mass_coverage": matrix.item_mass_covered / max(1, matrix.item_mass_total),
            "dropped_item_count": matrix.dropped_item_count,
            "dropped_item_mass": matrix.dropped_item_mass,
            "coverage_read": "adequate" if matrix.item_mass_covered / max(1, matrix.item_mass_total) >= 0.80 else "undercovered",
        }
        for matrix in matrices
    ]


def alignment_area_rows(*tables: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for name, table in zip(("control", "horizon", "probe", "view"), tables):
        values = [float_or_zero(row.get("top_k_subspace_alignment")) for row in table if row.get("alignment_status") == "computed"]
        rows.append({"alignment_area": name, "computed_rows": len(values), "mean_top_k_subspace_alignment": mean(values) if values else ""})
    return rows


def key_row(key: MatrixKey) -> dict[str, object]:
    return {
        "matrix_family": key.matrix_family,
        "condition_id": key.condition_id,
        "actual_control_name": key.actual_control_name,
        "proxy_level": key.proxy_level,
        "probe_key": key.probe_key,
        "flow_mode": key.flow_mode,
        "horizon_band": key.horizon_band,
    }


def key_subset(row: dict[str, object]) -> dict[str, object]:
    return {field: row.get(field, "") for field in ("matrix_family", "condition_id", "actual_control_name", "proxy_level", "probe_key", "flow_mode", "horizon_band")}


def matrix_id_for_key(key: MatrixKey) -> str:
    text = "|".join(str(value) for value in key_row(key).values())
    value = 0
    for char in text:
        value = (value * 131 + ord(char)) % 1_000_000_007
    return f"specmat_{value:09d}"


def effective_rank(values: np.ndarray) -> float:
    total = float(np.sum(values))
    if total <= 1e-12:
        return 0.0
    probs = values / total
    entropy = -float(np.sum([p * math.log(p) for p in probs if p > 1e-12]))
    return math.exp(entropy)


def spectral_gap(values: np.ndarray, top_k: int) -> float:
    ordered = sorted((float(value) for value in values), reverse=True)
    if len(ordered) <= top_k:
        return 0.0
    return ordered[top_k - 1] - ordered[top_k]


def participation_ratio(vector: np.ndarray) -> float:
    denom = float(np.sum(vector**4))
    if denom <= 1e-12:
        return 0.0
    return float((np.sum(vector**2) ** 2) / denom)


def group_by(rows: list[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[object, ...], list[dict[str, object]]]:
    out: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        out[tuple(row.get(key, "") for key in keys)].append(row)
    return out


def checkpoint_row(status: dict[str, object], started: float, counts: dict[MatrixKey, MatrixCounts], errors: list[dict[str, object]]) -> dict[str, object]:
    return {
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "jobs_submitted": status.get("jobs_submitted"),
        "jobs_completed": status.get("jobs_completed"),
        "contexts_accumulated": sum(item.contexts for item in counts.values()),
        "matrix_keys_accumulated": len(counts),
        "errors": len(errors),
        "status": status.get("status"),
    }


def write_status(out_dir: Path, status: dict[str, object], started: float) -> None:
    payload = dict(status)
    payload["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    (out_dir / "spectral_future_field_status.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_manifest(out_dir: Path) -> None:
    rows = []
    for name in OUTPUTS:
        path = out_dir / name
        rows.append({"file": name, "exists": path.exists() or name == "output_manifest.json", "status": "present" if path.exists() or name == "output_manifest.json" else "missing", "row_count": csv_row_count(path) if path.suffix == ".csv" else ""})
    (out_dir / "output_manifest.json").write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


def csv_row_count(path: Path) -> int:
    if not path.exists() or path.suffix != ".csv":
        return 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        return max(0, sum(1 for _ in handle) - 1)


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


if __name__ == "__main__":
    main()
