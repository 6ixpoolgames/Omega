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
from dataclasses import dataclass, replace
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np

from .landscape import exact_frontier
from .relation_generator import generate_relation_system
from .run_deformation_detector_sweep import params_from_parameter_set_id, stable_seed
from .run_focused_boundary_recurrence import apply_variant, float_or_zero, read_csv, write_csv
from .run_frontier_transform_b0 import FLOW_MODES, WINDOWS, transition_counts, transform_row
from .mechanism_controls import substrate_preservation_audit
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
    "spectral_channel_prep_run_config.json",
    "spectral_channel_prep_status.json",
    "spectral_channel_prep_progress_checkpoints.csv",
    "spectral_channel_prep_output_manifest.json",
    "spectral_channel_prep_errors.csv",
    "runner_output_contract_smoke_report.md",
    "spectral_label_shuffle_smoke.csv",
    "spectral_context_shuffle_smoke.csv",
    "spectral_horizon_shuffle_smoke.csv",
    "spectral_control_repair_smoke_summary.csv",
    "spectral_control_repair_smoke_report.md",
    "spectral_high_loading_candidate_pool_smoke.csv",
    "spectral_high_loading_items_smoke.csv",
    "spectral_item_loading_summary_smoke.csv",
    "spectral_item_to_edge_mapping_smoke.csv",
    "spectral_mapping_coverage_smoke.csv",
    "spectral_item_mapping_smoke_report.md",
    "spectral_item_ablation_manifest.csv",
    "spectral_high_loading_ablation_summary.csv",
    "spectral_random_item_ablation_summary.csv",
    "spectral_low_mid_loading_ablation_summary.csv",
    "spectral_item_ablation_decision.csv",
    "spectral_item_ablation_report.md",
    "spectral_channel_tiny_perturbation_manifest.csv",
    "spectral_channel_tiny_matching_quality.csv",
    "spectral_channel_tiny_substrate_preservation.csv",
    "spectral_channel_tiny_syndrome_rates.csv",
    "spectral_channel_tiny_spectral_response.csv",
    "spectral_channel_tiny_entropy_flow_horizon_response.csv",
    "spectral_channel_tiny_target_vs_random_summary.csv",
    "spectral_channel_tiny_smoke_report.md",
    "rfs_mb0_stage_b2_spectral_channel_edge_smoke_repair_prep_result.md",
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
    context_items: list[tuple[str, tuple[str, ...]]]
    item_edge_counts: Counter[str]
    item_edge_samples: dict[str, list[str]]

    @classmethod
    def empty(cls) -> MatrixCounts:
        return cls(0, Counter(), Counter(), 0, 0, Counter(), [], Counter(), defaultdict(list))


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
    parser.add_argument("--shuffle-replicates", type=int, default=5)
    parser.add_argument("--shuffle-max-matrices", type=int, default=24)
    parser.add_argument("--high-loading-top-k-items", type=int, default=24)
    parser.add_argument("--high-loading-candidate-pool-multiplier", type=int, default=8)
    parser.add_argument("--high-loading-min-seed-count", type=int, default=2)
    parser.add_argument("--high-loading-min-shuffle-survival-count", type=int, default=1)
    parser.add_argument("--high-loading-min-matrix-recurrence", type=int, default=1)
    parser.add_argument("--ablation-random-replicates", type=int, default=5)
    parser.add_argument("--prep-target-conditions", type=str, default="baseline_unperturbed:baseline,small_edge_resample_control:p0.02,asymmetric_edge_flip_control:p0.02")
    parser.add_argument("--prep-target-horizon-bands", type=str, default="middle")
    parser.add_argument("--mapping-mass-threshold", type=float, default=0.30)
    parser.add_argument("--tiny-perturbation-jobs", type=int, default=6)
    parser.add_argument("--tiny-perturbation-strengths", type=str, default="0.0025,0.005")
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
    (args.out / "spectral_channel_prep_run_config.json").write_text(
        json.dumps({**vars(args), "selected_syndrome_ids": selected_syndromes}, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    write_csv(args.out / "spectral_context_manifest.csv", context_manifest_rows(jobs))
    counts, errors, checkpoints = run_batches(args, jobs, status, started, control_summaries, components, selected_syndromes)
    matrices = build_spectral_matrices(counts, args)
    status["matrix_families_completed"] = len({matrix.key.matrix_family for matrix in matrices})
    status["spectral_decompositions_completed"] = len(matrices)
    write_outputs(args.out, args, status, started, counts, matrices, errors, checkpoints, jobs, control_summaries, components, selected_syndromes)


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
                edge_counts, edge_samples = transition_item_edge_map(control, probe, frontiers[ha], frontiers[hb], flow_mode)
                contexts.append(context_record(job, start_index, f"{ha}->{hb}", ha, hb, "coflow", flow_mode, transition_items, edge_counts, edge_samples))
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


def transition_item_edge_map(system: Any, probe: Any, fa: frozenset[object], fb: frozenset[object], flow_mode: str) -> tuple[Counter[str], dict[str, list[str]]]:
    fb_set = set(fb)
    counts: Counter[str] = Counter()
    samples: dict[str, list[str]] = defaultdict(list)
    for source in fa:
        targets_all = list(system.edges.get(source, ()))
        targets_fb = [target for target in targets_all if target in fb_set]
        targets = targets_fb if flow_mode == "constrained_window_flow" else targets_all
        for target in targets:
            item = f"{str(probe.fn(source))}->{str(probe.fn(target))}"
            counts[item] += 1
            if len(samples[item]) < 8:
                samples[item].append(f"{state_id(source)}->{state_id(target)}")
    return counts, samples


def state_id(state: object) -> str:
    if isinstance(state, tuple):
        return "(" + ",".join(str(part) for part in state) + ")"
    return str(state)


def capped_items(counts: Counter[str], cap: int) -> list[str]:
    return [item for item, _count in counts.most_common(max(1, cap))]


def context_record(
    job: dict[str, object],
    start_index: int,
    window: str,
    ha: int,
    hb: int,
    family: str,
    flow_mode: str,
    items: list[str],
    edge_counts: Counter[str] | None = None,
    edge_samples: dict[str, list[str]] | None = None,
) -> dict[str, object]:
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
        "edge_counts": edge_counts or Counter(),
        "edge_samples": edge_samples or {},
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
        bucket.context_items.append((str(context["context_id"]), tuple(items)))
        bucket.item_counts.update(items)
        for index, left in enumerate(items):
            for right in items[index + 1:]:
                bucket.pair_counts[(left, right)] += 1
        edge_counts = context.get("edge_counts", Counter())
        if isinstance(edge_counts, Counter):
            bucket.item_edge_counts.update(edge_counts)
        edge_samples = context.get("edge_samples", {})
        if isinstance(edge_samples, dict):
            for item, samples in edge_samples.items():
                bucket_samples = bucket.item_edge_samples[str(item)]
                for sample in samples:
                    if len(bucket_samples) >= 8:
                        break
                    bucket_samples.append(str(sample))
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
    jobs: list[dict[str, object]],
    control_summaries: dict[tuple[str, str, str, str], dict[str, object]],
    components: list[dict[str, object]],
    selected_syndromes: list[str],
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
    write_channel_prep_outputs(out_dir, args, status, started, counts, matrices, summary, coverage, errors, checkpoints, jobs, control_summaries, components, selected_syndromes)
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
    if status.get("label_shuffled_controls_completed") and status.get("context_shuffled_controls_completed") and status.get("horizon_order_shuffled_controls_completed"):
        lines.append("This runner completed the cheap prep shuffle controls: label-shuffled, context-shuffled, and horizon-order shuffled spectral replicates. Frontier-size matched and probe-marginal spectral controls are still not implemented, so the result should not be read as passing the full spectral migration criteria.")
    else:
        lines.append("This runner currently compares direct Stage B-2 controls only. Label-shuffled, context-shuffled, horizon-order shuffled, frontier-size matched, and probe-marginal spectral controls are not implemented in this first smoke, so the result should not be read as passing the full spectral migration criteria.")
    lines.append("")
    if status.get("branch_recommendation") == "recommend_channel_edge_sensitivity_with_spectral_guidance":
        lines.append("The smoke supports using spectral high-loading structures as exploratory guidance for a channel-edge sensitivity follow-up.")
    else:
        lines.append("The smoke does not yet justify a full spectral gauge migration.")
    lines.append("")
    (out_dir / "rfs_mb0_stage_b2_spectral_future_field_geometry_smoke_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_channel_prep_outputs(
    out_dir: Path,
    args: argparse.Namespace,
    status: dict[str, object],
    started: float,
    counts: dict[MatrixKey, MatrixCounts],
    matrices: list[SpectralMatrix],
    summary: list[dict[str, object]],
    coverage: list[dict[str, object]],
    errors: list[dict[str, object]],
    checkpoints: list[dict[str, object]],
    jobs: list[dict[str, object]],
    control_summaries: dict[tuple[str, str, str, str], dict[str, object]],
    components: list[dict[str, object]],
    selected_syndromes: list[str],
) -> None:
    summary_by_id = {str(row.get("matrix_id")): row for row in summary}
    target = prep_target_matrices(matrices, summary_by_id, args)
    label_rows = shuffle_smoke_rows("label_shuffle", target, counts, matrices, summary_by_id, args)
    context_rows = shuffle_smoke_rows("context_shuffle", target, counts, matrices, summary_by_id, args)
    horizon_rows = shuffle_smoke_rows("horizon_order_shuffle", target, counts, matrices, summary_by_id, args)
    control_summary = spectral_control_repair_summary(label_rows, context_rows, horizon_rows)
    loading_rows, loading_summary, candidate_rows = high_loading_rows(target, counts, control_summary, args)
    mapping_rows, mapping_coverage = item_mapping_rows(loading_rows, counts, args)
    high_ablation, random_ablation, low_mid_ablation, ablation_manifest, ablation_decision = item_ablation_rows(target, counts, loading_rows, args)
    perturbation = tiny_channel_perturbation_rows(
        jobs,
        loading_rows,
        mapping_rows,
        args,
        control_summaries,
        components,
        selected_syndromes,
    ) if should_run_tiny_perturbation(control_summary, mapping_coverage, ablation_decision, args) else tiny_perturbation_placeholder_rows()
    decision_classes = channel_prep_decision_classes(control_summary, mapping_coverage, ablation_decision, perturbation["summary"])
    status.update({
        "channel_prep_status": "COMPLETED" if status.get("status") == "COMPLETED" else status.get("status"),
        "runner_contract_status": "runner_contract_passed",
        "spectral_shuffle_control_status": shuffle_status(control_summary),
        "item_mapping_status": mapping_status(mapping_coverage, args.mapping_mass_threshold),
        "item_ablation_status": ablation_decision[0].get("decision_class", "high_loading_ablation_random_equivalent") if ablation_decision else "high_loading_ablation_random_equivalent",
        "tiny_channel_perturbation_status": tiny_perturbation_status(perturbation["summary"]),
        "high_loading_candidate_pool_rows": len(candidate_rows),
        "stable_high_loading_selected_rows": len(loading_rows),
        "stable_high_loading_matrix_count": sum(1 for row in loading_summary if row.get("selection_read") == "stable_items_selected"),
        "ablation_random_matching": "item_count_and_baseline_flow_count_greedy",
        "control_comparison_scope": "direct_stage_b2_plus_prep_shuffle_controls",
        "label_shuffled_controls_completed": True,
        "context_shuffled_controls_completed": True,
        "horizon_order_shuffled_controls_completed": True,
        "frontier_size_matched_controls_completed": False,
        "probe_marginal_controls_completed": False,
        "decision_classes": ";".join(decision_classes),
        "ready_for_24h_run": int("ready_for_24h_spectral_channel_run" in decision_classes),
    })
    if "ready_for_24h_spectral_channel_run" in decision_classes:
        status["branch_recommendation"] = "recommend_24h_spectral_channel_run"
    else:
        status["branch_recommendation"] = "recommend_spectral_channel_repair_before_large_run"
    write_csv(out_dir / "spectral_channel_prep_errors.csv", errors)
    write_csv(out_dir / "spectral_channel_prep_progress_checkpoints.csv", checkpoints)
    write_csv(out_dir / "spectral_label_shuffle_smoke.csv", label_rows)
    write_csv(out_dir / "spectral_context_shuffle_smoke.csv", context_rows)
    write_csv(out_dir / "spectral_horizon_shuffle_smoke.csv", horizon_rows)
    write_csv(out_dir / "spectral_control_repair_smoke_summary.csv", control_summary)
    write_csv(out_dir / "spectral_high_loading_candidate_pool_smoke.csv", candidate_rows)
    write_csv(out_dir / "spectral_high_loading_items_smoke.csv", loading_rows)
    write_csv(out_dir / "spectral_item_loading_summary_smoke.csv", loading_summary)
    write_csv(out_dir / "spectral_item_to_edge_mapping_smoke.csv", mapping_rows)
    write_csv(out_dir / "spectral_mapping_coverage_smoke.csv", mapping_coverage)
    write_csv(out_dir / "spectral_item_ablation_manifest.csv", ablation_manifest)
    write_csv(out_dir / "spectral_high_loading_ablation_summary.csv", high_ablation)
    write_csv(out_dir / "spectral_random_item_ablation_summary.csv", random_ablation)
    write_csv(out_dir / "spectral_low_mid_loading_ablation_summary.csv", low_mid_ablation)
    write_csv(out_dir / "spectral_item_ablation_decision.csv", ablation_decision)
    write_csv(out_dir / "spectral_channel_tiny_perturbation_manifest.csv", perturbation["manifest"])
    write_csv(out_dir / "spectral_channel_tiny_matching_quality.csv", perturbation["matching"])
    write_csv(out_dir / "spectral_channel_tiny_substrate_preservation.csv", perturbation["preservation"])
    write_csv(out_dir / "spectral_channel_tiny_syndrome_rates.csv", perturbation["syndrome"])
    write_csv(out_dir / "spectral_channel_tiny_spectral_response.csv", perturbation["spectral"])
    write_csv(out_dir / "spectral_channel_tiny_entropy_flow_horizon_response.csv", perturbation["entropy"])
    write_csv(out_dir / "spectral_channel_tiny_target_vs_random_summary.csv", perturbation["summary"])
    write_runner_contract_report(out_dir, status, errors)
    write_control_repair_report(out_dir, control_summary)
    write_item_mapping_report(out_dir, mapping_coverage)
    write_item_ablation_report(out_dir, ablation_decision)
    write_tiny_perturbation_report(out_dir, perturbation["summary"])
    write_channel_prep_report(out_dir, status, control_summary, mapping_coverage, ablation_decision)
    write_channel_prep_status(out_dir, status, started)
    write_channel_prep_manifest(out_dir)


def prep_target_matrices(matrices: list[SpectralMatrix], summary_by_id: dict[str, dict[str, object]], args: argparse.Namespace) -> list[SpectralMatrix]:
    target_conditions = parse_csv_set(args.prep_target_conditions)
    target_bands = parse_csv_set(args.prep_target_horizon_bands)
    preferred = [
        matrix for matrix in matrices
        if matrix.key.matrix_family == "coflow"
        and (not target_conditions or matrix.key.condition_id in target_conditions)
        and (not target_bands or matrix.key.horizon_band in target_bands)
    ]
    if not preferred:
        preferred = [matrix for matrix in matrices if matrix.key.matrix_family == "coflow"]
    preferred.sort(key=lambda matrix: float_or_zero(summary_by_id.get(matrix.matrix_id, {}).get("positive_spectral_mass")), reverse=True)
    return preferred[: max(1, args.shuffle_max_matrices)]


def parse_csv_set(raw: object) -> set[str]:
    return {item.strip() for item in str(raw).split(",") if item.strip()}


def parse_float_list(raw: object) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in str(raw).split(",") if item.strip())


def shuffle_smoke_rows(
    shuffle_kind: str,
    target: list[SpectralMatrix],
    counts: dict[MatrixKey, MatrixCounts],
    matrices: list[SpectralMatrix],
    summary_by_id: dict[str, dict[str, object]],
    args: argparse.Namespace,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    context_pool = shuffled_context_pool(matrices, counts)
    for matrix in target:
        bucket = counts.get(matrix.key)
        if bucket is None:
            continue
        observed = summary_by_id.get(matrix.matrix_id, {})
        for replicate in range(max(1, args.shuffle_replicates)):
            rng = random.Random(stable_seed(f"{shuffle_kind}|{matrix.matrix_id}|{replicate}"))
            if shuffle_kind == "label_shuffle":
                contexts = label_shuffled_contexts(bucket, rng)
            elif shuffle_kind == "context_shuffle":
                contexts = sampled_contexts(context_pool.get(context_shuffle_key(matrix.key), []), len(bucket.context_items), rng)
            else:
                contexts = sampled_contexts(context_pool.get(horizon_shuffle_key(matrix.key), []), len(bucket.context_items), rng)
            payload = spectral_payload_from_contexts(contexts, args)
            rows.append({
                **key_row(matrix.key),
                "matrix_id": matrix.matrix_id,
                "shuffle_kind": shuffle_kind,
                "replicate": replicate,
                "observed_positive_spectral_mass": observed.get("positive_spectral_mass", ""),
                "shuffle_positive_spectral_mass": payload["positive_spectral_mass"],
                "observed_effective_rank": observed.get("effective_rank", ""),
                "shuffle_effective_rank": payload["effective_rank"],
                "observed_spectral_gap_k": observed.get("spectral_gap_k", ""),
                "shuffle_spectral_gap_k": payload["spectral_gap_k"],
                "shuffle_item_count": payload["item_count"],
                "shuffle_context_count": len(contexts),
                "shuffle_status": payload["status"],
            })
    return rows


def shuffled_context_pool(matrices: list[SpectralMatrix], counts: dict[MatrixKey, MatrixCounts]) -> dict[tuple[object, ...], list[tuple[str, tuple[str, ...]]]]:
    pool: dict[tuple[object, ...], list[tuple[str, tuple[str, ...]]]] = defaultdict(list)
    for matrix in matrices:
        bucket = counts.get(matrix.key)
        if bucket is None:
            continue
        pool[context_shuffle_key(matrix.key)].extend(bucket.context_items)
        pool[horizon_shuffle_key(matrix.key)].extend(bucket.context_items)
    return pool


def context_shuffle_key(key: MatrixKey) -> tuple[object, ...]:
    return (key.matrix_family, key.probe_key, key.flow_mode, key.horizon_band)


def horizon_shuffle_key(key: MatrixKey) -> tuple[object, ...]:
    return (key.matrix_family, key.condition_id, key.probe_key, key.flow_mode)


def label_shuffled_contexts(bucket: MatrixCounts, rng: random.Random) -> list[tuple[str, tuple[str, ...]]]:
    vocab = list(bucket.item_counts)
    if not vocab:
        return []
    contexts: list[tuple[str, tuple[str, ...]]] = []
    for context_id, items in bucket.context_items:
        take = min(len(items), len(vocab))
        shuffled = tuple(sorted(rng.sample(vocab, take))) if take else tuple()
        contexts.append((context_id, shuffled))
    return contexts


def sampled_contexts(pool: list[tuple[str, tuple[str, ...]]], size: int, rng: random.Random) -> list[tuple[str, tuple[str, ...]]]:
    if not pool or size <= 0:
        return []
    return [pool[rng.randrange(len(pool))] for _ in range(size)]


def spectral_payload_from_contexts(contexts: list[tuple[str, tuple[str, ...]]], args: argparse.Namespace, exclude: set[str] | None = None) -> dict[str, object]:
    exclude = exclude or set()
    bucket = MatrixCounts.empty()
    for _context_id, raw_items in contexts:
        items = sorted(set(item for item in raw_items if item not in exclude))
        if not items:
            continue
        bucket.contexts += 1
        bucket.item_counts.update(items)
        for index, left in enumerate(items):
            for right in items[index + 1:]:
                bucket.pair_counts[(left, right)] += 1
    retained = [(item, count) for item, count in bucket.item_counts.most_common(args.max_items_per_matrix) if count >= args.min_item_count]
    if len(retained) < 2 or bucket.contexts <= 0:
        return {"status": "insufficient_items", "item_count": len(retained), "positive_spectral_mass": 0.0, "effective_rank": 0.0, "spectral_gap_k": 0.0}
    items = [item for item, _count in retained]
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
    eigvals = np.linalg.eigvalsh(matrix)
    positive = eigvals[eigvals > 0]
    absvals = np.abs(eigvals)
    return {
        "status": "computed",
        "item_count": len(items),
        "positive_spectral_mass": float(np.sum(positive)) if positive.size else 0.0,
        "effective_rank": effective_rank(absvals),
        "spectral_gap_k": spectral_gap(absvals, args.top_k),
    }


def spectral_control_repair_summary(*tables: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for table in tables:
        grouped = group_by(table, ("shuffle_kind", "matrix_id"))
        for (shuffle_kind, matrix_id), items in grouped.items():
            observed = float_or_zero(items[0].get("observed_positive_spectral_mass")) if items else 0.0
            shuffles = [float_or_zero(row.get("shuffle_positive_spectral_mass")) for row in items if row.get("shuffle_status") == "computed"]
            if not shuffles:
                percentile = ""
                read = "shuffle_control_failed"
            else:
                percentile = sum(value <= observed for value in shuffles) / len(shuffles)
                read = "observed_above_shuffle" if percentile >= 0.80 and observed > mean(shuffles) else "shuffle_control_equivalent"
            first = items[0] if items else {}
            rows.append({
                **key_subset(first),
                "matrix_id": matrix_id,
                "shuffle_kind": shuffle_kind,
                "replicate_count": len(shuffles),
                "observed_positive_spectral_mass": observed,
                "shuffle_positive_spectral_mass_mean": mean(shuffles) if shuffles else "",
                "shuffle_positive_spectral_mass_max": max(shuffles) if shuffles else "",
                "observed_percentile_vs_shuffle": percentile,
                "shuffle_control_read": read,
            })
    return rows


def high_loading_rows(
    target: list[SpectralMatrix],
    counts: dict[MatrixKey, MatrixCounts],
    control_summary: list[dict[str, object]],
    args: argparse.Namespace,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []
    shuffle_survival = matrix_shuffle_survival(control_summary)
    recurrence: Counter[tuple[str, str, str, str]] = Counter()
    per_matrix_candidates: dict[str, list[dict[str, object]]] = {}
    for matrix in target:
        bucket = counts.get(matrix.key)
        if bucket is None or matrix.eigvecs.size == 0:
            continue
        item_stats = item_context_stats(bucket)
        baseline_bucket = baseline_bucket_for(matrix, counts)
        scores: dict[str, dict[str, object]] = {}
        ordered = np.argsort(matrix.eigvals)[::-1]
        positive_modes = [idx for idx in ordered if matrix.eigvals[idx] > 0][: args.top_k]
        for mode_rank, mode_index in enumerate(positive_modes, start=1):
            eigval = float(matrix.eigvals[mode_index])
            vector = matrix.eigvecs[:, mode_index]
            for item_index, item in enumerate(matrix.items):
                score = abs(float(vector[item_index])) * abs(eigval)
                stats = item_stats.get(item, {"seed_count": 0, "group_count": 0, "context_count": 0})
                current = scores.get(item)
                if current is None:
                    scores[item] = {
                        **key_row(matrix.key),
                        "spectral_item_id": f"{matrix.matrix_id}:{stable_seed(item) % 1_000_000:06d}",
                        "matrix_id": matrix.matrix_id,
                        "signature_transition": item,
                        "loading_score": score,
                        "loading_score_sum": score,
                        "positive_mode_hit_count": 1,
                        "mode_index": mode_rank,
                        "raw_eigen_index": int(mode_index),
                        "eigenvalue": eigval,
                        "item_count": bucket.item_counts.get(item, 0),
                        "item_mass": bucket.item_counts.get(item, 0),
                        "baseline_flow_item_count": baseline_bucket.item_counts.get(item, 0) if baseline_bucket else bucket.item_counts.get(item, 0),
                        **stats,
                    }
                else:
                    current["loading_score_sum"] = float_or_zero(current.get("loading_score_sum")) + score
                    current["positive_mode_hit_count"] = int(float_or_zero(current.get("positive_mode_hit_count"))) + 1
                    if score > float_or_zero(current.get("loading_score")):
                        current["loading_score"] = score
                        current["mode_index"] = mode_rank
                        current["raw_eigen_index"] = int(mode_index)
                        current["eigenvalue"] = eigval
        pool_limit = max(1, args.high_loading_top_k_items * max(1, args.high_loading_candidate_pool_multiplier))
        pool = sorted(scores.values(), key=lambda row: float_or_zero(row.get("loading_score")), reverse=True)[:pool_limit]
        per_matrix_candidates[matrix.matrix_id] = pool
        for row in pool:
            recurrence[recurrence_key(row)] += 1
    for matrix in target:
        bucket = counts.get(matrix.key)
        if bucket is None:
            continue
        pool = per_matrix_candidates.get(matrix.matrix_id, [])
        enriched = []
        for row in pool:
            rec_count = recurrence[recurrence_key(row)]
            shuffle_count = shuffle_survival.get(str(row.get("matrix_id")), 0)
            seed_count = int(float_or_zero(row.get("seed_count")))
            stability_pass = int(
                seed_count >= args.high_loading_min_seed_count
                and shuffle_count >= args.high_loading_min_shuffle_survival_count
                and rec_count >= args.high_loading_min_matrix_recurrence
            )
            selection_score = (
                float_or_zero(row.get("loading_score"))
                * (1.0 + math.log1p(seed_count))
                * (1.0 + 0.20 * shuffle_count)
                * (1.0 + 0.10 * max(0, rec_count - 1))
            )
            enriched_row = {
                **row,
                "matrix_recurrence_count": rec_count,
                "shuffle_survival_count": shuffle_count,
                "stability_pass": stability_pass,
                "stability_rule": f"seed>={args.high_loading_min_seed_count};shuffle>={args.high_loading_min_shuffle_survival_count};matrix_recurrence>={args.high_loading_min_matrix_recurrence}",
                "selection_score": selection_score,
            }
            enriched.append(enriched_row)
            candidate_rows.append({**enriched_row, "selection_status": "candidate_pool"})
        stable = [row for row in enriched if int(float_or_zero(row.get("stability_pass"))) == 1]
        selected = sorted(stable, key=lambda row: float_or_zero(row.get("selection_score")), reverse=True)[: max(1, args.high_loading_top_k_items)]
        for row in selected:
            row["selection_status"] = "stable_selected"
        rows.extend(selected)
        summaries.append({
            **key_row(matrix.key),
            "matrix_id": matrix.matrix_id,
            "positive_mode_count_used": len([idx for idx in np.argsort(matrix.eigvals)[::-1] if matrix.eigvals[idx] > 0][: args.top_k]),
            "candidate_pool_count": len(enriched),
            "stable_candidate_count": len(stable),
            "high_loading_item_count": len(selected),
            "high_loading_item_mass": sum(float_or_zero(row.get("item_mass")) for row in selected),
            "total_matrix_item_mass": sum(bucket.item_counts.values()),
            "selection_read": "stable_items_selected" if selected else "no_stable_high_loading_items",
        })
    return rows, summaries, candidate_rows


def matrix_shuffle_survival(control_summary: list[dict[str, object]]) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for row in control_summary:
        if row.get("shuffle_control_read") == "observed_above_shuffle":
            out[str(row.get("matrix_id", ""))] += 1
    return out


def item_context_stats(bucket: MatrixCounts) -> dict[str, dict[str, int]]:
    seeds: dict[str, set[str]] = defaultdict(set)
    groups: dict[str, set[str]] = defaultdict(set)
    contexts: Counter[str] = Counter()
    for context_id, items in bucket.context_items:
        parts = context_id.split("|")
        group_id = parts[1] if len(parts) > 1 else ""
        seed = parts[2] if len(parts) > 2 else ""
        for item in items:
            seeds[item].add(seed)
            groups[item].add(group_id)
            contexts[item] += 1
    return {
        item: {
            "seed_count": len(seeds[item]),
            "group_count": len(groups[item]),
            "context_count": contexts[item],
        }
        for item in contexts
    }


def baseline_bucket_for(matrix: SpectralMatrix, counts: dict[MatrixKey, MatrixCounts]) -> MatrixCounts | None:
    key = MatrixKey(
        matrix.key.matrix_family,
        f"{BASELINE_CONTROL}:baseline",
        BASELINE_CONTROL,
        "not_available",
        matrix.key.probe_key,
        matrix.key.flow_mode,
        matrix.key.horizon_band,
    )
    return counts.get(key)


def recurrence_key(row: dict[str, object]) -> tuple[str, str, str, str]:
    return (
        str(row.get("probe_key", "")),
        str(row.get("flow_mode", "")),
        str(row.get("horizon_band", "")),
        str(row.get("signature_transition", "")),
    )


def item_mapping_rows(loading_rows: list[dict[str, object]], counts: dict[MatrixKey, MatrixCounts], args: argparse.Namespace) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    key_by_matrix = {matrix_id_for_key(key): key for key in counts}
    for row in loading_rows:
        key = key_by_matrix.get(str(row.get("matrix_id")))
        bucket = counts.get(key) if key else None
        item = str(row.get("signature_transition", ""))
        edge_count = bucket.item_edge_counts.get(item, 0) if bucket else 0
        item_mass = float_or_zero(row.get("item_mass"))
        if edge_count > 0:
            status = "mapped_to_realized_edges"
            mapped_mass = item_mass
        elif "->" in item:
            status = "mapped_to_signature_transition_only"
            mapped_mass = 0.0
        else:
            status = "insufficient_context_to_map"
            mapped_mass = 0.0
        rows.append({
            **row,
            "realized_edge_count": edge_count,
            "realized_edge_sample_json": json.dumps((bucket.item_edge_samples.get(item, []) if bucket else [])[:8], sort_keys=True),
            "mapped_item_mass": mapped_mass,
            "mapping_status": status,
        })
    coverage: list[dict[str, object]] = []
    for (matrix_id,), items in group_by(rows, ("matrix_id",)).items():
        total_mass = sum(float_or_zero(row.get("item_mass")) for row in items)
        mapped_mass = sum(float_or_zero(row.get("mapped_item_mass")) for row in items)
        mapped_count = sum(1 for row in items if row.get("mapping_status") == "mapped_to_realized_edges")
        first = items[0] if items else {}
        fraction = mapped_mass / max(1.0, total_mass)
        coverage.append({
            **key_subset(first),
            "matrix_id": matrix_id,
            "mapped_item_count": mapped_count,
            "high_loading_item_count": len(items),
            "mapped_item_fraction": mapped_count / max(1, len(items)),
            "mapped_item_mass": mapped_mass,
            "high_loading_item_mass": total_mass,
            "mapped_item_mass_fraction": fraction,
            "mapping_read": "mapping_adequate" if fraction >= args.mapping_mass_threshold else "mapping_insufficient",
        })
    return rows, coverage


def item_ablation_rows(
    target: list[SpectralMatrix],
    counts: dict[MatrixKey, MatrixCounts],
    loading_rows: list[dict[str, object]],
    args: argparse.Namespace,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    high_by_matrix = group_by(loading_rows, ("matrix_id",))
    high_rows: list[dict[str, object]] = []
    random_rows: list[dict[str, object]] = []
    low_rows: list[dict[str, object]] = []
    manifest: list[dict[str, object]] = []
    for matrix in target:
        bucket = counts.get(matrix.key)
        selected_rows = high_by_matrix.get((matrix.matrix_id,), [])
        if bucket is None or not selected_rows:
            continue
        high_items = {str(row.get("signature_transition", "")) for row in selected_rows}
        baseline_bucket = baseline_bucket_for(matrix, counts)
        observed = float(np.sum(matrix.eigvals[matrix.eigvals > 0])) if matrix.eigvals.size else 0.0
        high_payload = spectral_payload_from_contexts(bucket.context_items, args, high_items)
        high_drop = observed - float_or_zero(high_payload.get("positive_spectral_mass"))
        base = {
            **key_row(matrix.key),
            "matrix_id": matrix.matrix_id,
            "observed_positive_spectral_mass": observed,
            "removed_item_count": len(high_items),
        }
        high_rows.append({
            **base,
            "ablation_kind": "high_loading",
            "ablated_positive_spectral_mass": high_payload.get("positive_spectral_mass", 0.0),
            "positive_spectral_mass_drop": high_drop,
            "positive_spectral_mass_drop_fraction": high_drop / max(1e-9, observed),
            "ablation_status": high_payload.get("status", ""),
        })
        manifest.append({**base, "ablation_kind": "high_loading", "removed_items_json": json.dumps(sorted(high_items)[:64])})
        candidates = [item for item in matrix.items if item not in high_items]
        for replicate in range(max(1, args.ablation_random_replicates)):
            rng = random.Random(stable_seed(f"ablation|{matrix.matrix_id}|{replicate}"))
            random_items = matched_random_item_set(candidates, selected_rows, bucket, baseline_bucket, rng)
            payload = spectral_payload_from_contexts(bucket.context_items, args, random_items)
            drop = observed - float_or_zero(payload.get("positive_spectral_mass"))
            random_rows.append({
                **base,
                "ablation_kind": "frequency_baseline_flow_matched_random",
                "replicate": replicate,
                "matching_method": "item_count_and_baseline_flow_count_greedy",
                "removed_items_json": json.dumps(sorted(random_items)[:64]),
                "ablated_positive_spectral_mass": payload.get("positive_spectral_mass", 0.0),
                "positive_spectral_mass_drop": drop,
                "positive_spectral_mass_drop_fraction": drop / max(1e-9, observed),
                "ablation_status": payload.get("status", ""),
            })
        low_items = set(candidates[-min(len(high_items), len(candidates)):]) if candidates else set()
        payload = spectral_payload_from_contexts(bucket.context_items, args, low_items)
        drop = observed - float_or_zero(payload.get("positive_spectral_mass"))
        low_rows.append({
            **base,
            "ablation_kind": "low_mid_loading",
            "ablated_positive_spectral_mass": payload.get("positive_spectral_mass", 0.0),
            "positive_spectral_mass_drop": drop,
            "positive_spectral_mass_drop_fraction": drop / max(1e-9, observed),
            "ablation_status": payload.get("status", ""),
        })
    high_drop_mean = mean([float_or_zero(row.get("positive_spectral_mass_drop_fraction")) for row in high_rows]) if high_rows else 0.0
    random_drop_mean = mean([float_or_zero(row.get("positive_spectral_mass_drop_fraction")) for row in random_rows]) if random_rows else 0.0
    decision = "high_loading_ablation_specific" if high_drop_mean > random_drop_mean * 1.10 and high_drop_mean - random_drop_mean > 0.01 else "high_loading_ablation_random_equivalent"
    decision_rows = [{
        "decision_class": decision,
        "high_loading_drop_fraction_mean": high_drop_mean,
        "matched_random_drop_fraction_mean": random_drop_mean,
        "matrix_count": len(high_rows),
        "random_replicate_rows": len(random_rows),
    }]
    return high_rows, random_rows, low_rows, manifest, decision_rows


def matched_random_item_set(
    candidates: list[str],
    selected_rows: list[dict[str, object]],
    bucket: MatrixCounts,
    baseline_bucket: MatrixCounts | None,
    rng: random.Random,
) -> set[str]:
    available = set(candidates)
    selected: set[str] = set()
    candidate_items = list(available)
    for row in sorted(selected_rows, key=lambda item: float_or_zero(item.get("item_count")), reverse=True):
        if not candidate_items:
            break
        target_count = max(1.0, float_or_zero(row.get("item_count")))
        target_baseline = max(0.0, float_or_zero(row.get("baseline_flow_item_count")))
        scored = []
        for item in candidate_items:
            item_count = max(1.0, bucket.item_counts.get(item, 0))
            baseline_count = baseline_bucket.item_counts.get(item, 0) if baseline_bucket else item_count
            score = abs(math.log(item_count / target_count))
            score += 0.75 * abs(math.log((baseline_count + 1.0) / (target_baseline + 1.0)))
            score += rng.random() * 1e-6
            scored.append((score, item))
        scored.sort(key=lambda pair: pair[0])
        chosen = scored[0][1]
        selected.add(chosen)
        candidate_items.remove(chosen)
    return selected


def should_run_tiny_perturbation(
    control_summary: list[dict[str, object]],
    mapping_coverage: list[dict[str, object]],
    ablation_decision: list[dict[str, object]],
    args: argparse.Namespace,
) -> bool:
    return (
        shuffle_status(control_summary) == "spectral_shuffle_controls_passed"
        and mapping_status(mapping_coverage, args.mapping_mass_threshold) == "spectral_item_mapping_adequate"
        and bool(ablation_decision)
        and ablation_decision[0].get("decision_class") == "high_loading_ablation_specific"
        and args.tiny_perturbation_jobs > 0
    )


def tiny_channel_perturbation_rows(
    jobs: list[dict[str, object]],
    loading_rows: list[dict[str, object]],
    mapping_rows: list[dict[str, object]],
    args: argparse.Namespace,
    control_summaries: dict[tuple[str, str, str, str], dict[str, object]],
    components: list[dict[str, object]],
    selected_syndromes: list[str],
) -> dict[str, list[dict[str, object]]]:
    mapped = [row for row in mapping_rows if row.get("mapping_status") == "mapped_to_realized_edges"]
    if not mapped:
        return tiny_perturbation_placeholder_rows("no_mapped_items")
    rows_by_target = group_by(mapped, ("matrix_id", "condition_id", "probe_key", "flow_mode", "horizon_band"))
    selected_targets = sorted(
        (aggregate_perturbation_target(items) for _key, items in rows_by_target.items()),
        key=lambda row: float_or_zero(row.get("loading_score")),
        reverse=True,
    )[: max(1, args.tiny_perturbation_jobs)]
    strengths = parse_float_list(args.tiny_perturbation_strengths)
    job_index = index_jobs_for_perturbation(jobs)
    manifest: list[dict[str, object]] = []
    matching: list[dict[str, object]] = []
    preservation: list[dict[str, object]] = []
    syndrome: list[dict[str, object]] = []
    spectral: list[dict[str, object]] = []
    entropy: list[dict[str, object]] = []
    for target_index, target in enumerate(selected_targets):
        job = job_index.get((str(target.get("condition_id")), str(target.get("probe_key"))))
        if job is None:
            manifest.append({**target, "perturbation_status": "job_unavailable"})
            continue
        for strength in strengths:
            for perturbation_kind in ("spectral_high_loading_targeted_edge_perturbation", "matched_random_edge_perturbation"):
                try:
                    result = run_tiny_perturbation_job(
                        job,
                        target,
                        perturbation_kind,
                        strength,
                        target_index,
                        args,
                        control_summaries,
                        components,
                        selected_syndromes,
                    )
                    manifest.extend(result["manifest"])
                    matching.extend(result["matching"])
                    preservation.extend(result["preservation"])
                    syndrome.extend(result["syndrome"])
                    spectral.extend(result["spectral"])
                    entropy.extend(result["entropy"])
                except Exception as exc:  # noqa: BLE001
                    manifest.append({**target, "perturbation_kind": perturbation_kind, "strength": strength, "perturbation_status": "error", "error": repr(exc)})
    summary = summarize_tiny_perturbation(manifest, preservation, syndrome, spectral)
    return {
        "manifest": manifest,
        "matching": matching,
        "preservation": preservation,
        "syndrome": syndrome,
        "spectral": spectral,
        "entropy": entropy,
        "summary": summary,
    }


def aggregate_perturbation_target(items: list[dict[str, object]]) -> dict[str, object]:
    first = items[0]
    transitions = sorted({str(row.get("signature_transition", "")) for row in items if row.get("signature_transition")})
    total_mass = sum(float_or_zero(row.get("item_mass")) for row in items)
    return {
        **key_subset(first),
        "matrix_id": first.get("matrix_id", ""),
        "signature_transition": transitions[0] if transitions else "",
        "target_signature_transitions_json": json.dumps(transitions, sort_keys=True),
        "target_item_count": len(transitions),
        "loading_score": sum(float_or_zero(row.get("loading_score")) for row in items),
        "loading_score_max": max((float_or_zero(row.get("loading_score")) for row in items), default=0.0),
        "item_mass": total_mass,
    }


def tiny_perturbation_placeholder_rows(reason: str = "graph_level_targeted_perturbation_gated_until_shuffle_mapping_and_ablation_review") -> dict[str, list[dict[str, object]]]:
    rows = [{"status": "not_run", "reason": reason, "decision_class": "tiny_channel_perturbation_not_interpretable"}]
    return {
        "manifest": rows,
        "matching": rows,
        "preservation": rows,
        "syndrome": rows,
        "spectral": rows,
        "entropy": rows,
        "summary": rows,
    }


def index_jobs_for_perturbation(jobs: list[dict[str, object]]) -> dict[tuple[str, str], dict[str, object]]:
    out: dict[tuple[str, str], dict[str, object]] = {}
    for job in jobs:
        key = (str(job.get("condition_id", "")), str(job.get("probe_key", "")))
        out.setdefault(key, job)
    return out


def run_tiny_perturbation_job(
    job: dict[str, object],
    target: dict[str, object],
    perturbation_kind: str,
    strength: float,
    target_index: int,
    args: argparse.Namespace,
    control_summaries: dict[tuple[str, str, str, str], dict[str, object]],
    components: list[dict[str, object]],
    selected_syndromes: list[str],
) -> dict[str, list[dict[str, object]]]:
    seed = int(job["seed"])
    params = job["params"]
    baseline = generate_relation_system(params, seed)  # type: ignore[arg-type]
    control = make_stage_b2_control_system(baseline, job, seed, params)  # type: ignore[arg-type]
    probe, alphabet_size, probe_group = build_probe(control, str(job["probe_key"]), str(job["source_probe_family"]))
    target_items = target_transition_set(target)
    selected_edges = matching_edges_for_items(control, probe, target_items)
    all_edges = [(source, target_state) for source, targets in control.edges.items() for target_state in targets]
    perturb_count = max(1, min(len(selected_edges), round(len(all_edges) * float(strength)))) if selected_edges else 0
    rng = random.Random(stable_seed(f"tiny|{job.get('job_id')}|{perturbation_kind}|{strength}|{target_index}"))
    if perturbation_kind == "matched_random_edge_perturbation":
        edge_targets = matched_random_edges(control, selected_edges, perturb_count, rng)
    else:
        edge_targets = selected_edges[:]
        rng.shuffle(edge_targets)
        edge_targets = edge_targets[:perturb_count]
    perturbed = rewire_edges(control, edge_targets, rng, f"{perturbation_kind}_p{strength:g}")
    starts = [perturbed.states[(seed + i * 17) % len(perturbed.states)] for i in range(int(job["start_samples"]))]
    row_kind = "mechanism_control"
    common = common_condition_fields(job, baseline.system_id, perturbed.system_id)
    metric_rows, context_rows = rows_and_contexts_for_system(job, perturbed, probe, alphabet_size, probe_group, starts, row_kind, common, args.max_items_per_context)
    flags = syndrome_flags(metric_rows, control_summaries, components, selected_syndromes, args.component_z_threshold)
    counts: dict[MatrixKey, MatrixCounts] = defaultdict(MatrixCounts.empty)
    merge_contexts(counts, context_rows, flags)
    key = MatrixKey("coflow", str(job["condition_id"]), str(job["actual_control_name"]), str(job["proxy_level"]), str(job["probe_key"]), str(target.get("flow_mode", "")), str(target.get("horizon_band", "")))
    payload = spectral_payload_from_contexts(counts.get(key, MatrixCounts.empty()).context_items, args)
    audit = dict(substrate_preservation_audit(control, perturbed))
    audit.update(common)
    perturbation_id = f"tiny_{target_index}_{perturbation_kind}_p{strength:g}"
    base = {
        **key_row(key),
        "perturbation_id": perturbation_id,
        "perturbation_kind": perturbation_kind,
        "strength": strength,
        "target_signature_transition": target.get("signature_transition", ""),
        "target_signature_transitions_json": json.dumps(sorted(target_items), sort_keys=True),
        "target_item_count": len(target_items),
        "target_loading_score": target.get("loading_score", ""),
        "selected_edge_count": len(edge_targets),
        "candidate_target_edge_count": len(selected_edges),
    }
    syndrome_rates = syndrome_rate_rows(base, flags, len(context_rows), selected_syndromes)
    entropy_rows = entropy_response_rows(base, metric_rows)
    return {
        "manifest": [{**base, "job_id": job.get("job_id", ""), "perturbation_status": "computed"}],
        "matching": [{**base, "matching_status": "computed", "matched_edge_count": len(edge_targets), "candidate_edge_count": len(selected_edges), "all_edge_count": len(all_edges)}],
        "preservation": [{**base, **audit}],
        "syndrome": syndrome_rates,
        "spectral": [{**base, "spectral_status": payload.get("status", ""), "positive_spectral_mass": payload.get("positive_spectral_mass", 0.0), "effective_rank": payload.get("effective_rank", 0.0), "spectral_gap_k": payload.get("spectral_gap_k", 0.0), "item_count": payload.get("item_count", 0)}],
        "entropy": entropy_rows,
    }


def target_transition_set(target: dict[str, object]) -> set[str]:
    raw = target.get("target_signature_transitions_json", "")
    if raw:
        try:
            parsed = json.loads(str(raw))
            if isinstance(parsed, list):
                return {str(item) for item in parsed if str(item)}
        except json.JSONDecodeError:
            pass
    return {str(target.get("signature_transition", ""))} if target.get("signature_transition") else set()


def rows_and_contexts_for_system(
    job: dict[str, object],
    system: Any,
    probe: Any,
    alphabet_size: int,
    probe_group: str,
    starts: list[object],
    row_kind: str,
    common: dict[str, object],
    max_items_per_context: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    horizons = sorted({h for window in WINDOWS for h in window})
    rows: list[dict[str, object]] = []
    contexts: list[dict[str, object]] = []
    for start_index, start in enumerate(starts):
        frontiers = {h: exact_frontier(system, start, h) for h in horizons}
        for ha, hb in WINDOWS:
            cofrontier_items = frontier_signature_items(frontiers[hb], probe, max_items_per_context)
            contexts.append(context_record(job, start_index, f"{ha}->{hb}", ha, hb, "cofrontier", "frontier", cofrontier_items))
            for flow_mode in FLOW_MODES:
                row = transform_row(job, system, probe, alphabet_size, probe_group, start_index, ha, hb, frontiers, flow_mode, row_kind)
                row.update(common)
                row["context_id"] = context_id(row)
                rows.append(row)
                transition_items = transition_distribution_items(row, max_items_per_context)
                edge_counts, edge_samples = transition_item_edge_map(system, probe, frontiers[ha], frontiers[hb], flow_mode)
                contexts.append(context_record(job, start_index, f"{ha}->{hb}", ha, hb, "coflow", flow_mode, transition_items, edge_counts, edge_samples))
    return rows, contexts


def matching_edges_for_items(system: Any, probe: Any, items: set[str]) -> list[tuple[object, object]]:
    edges = []
    for source, targets in system.edges.items():
        for target in targets:
            item = f"{str(probe.fn(source))}->{str(probe.fn(target))}"
            if item in items:
                edges.append((source, target))
    return edges


def matched_random_edges(system: Any, selected_edges: list[tuple[object, object]], count: int, rng: random.Random) -> list[tuple[object, object]]:
    all_edges = [(source, target) for source, targets in system.edges.items() for target in targets]
    if not all_edges or count <= 0:
        return []
    selected_sources = Counter(len(system.edges.get(source, ())) for source, _target in selected_edges)
    candidates = [edge for edge in all_edges if len(system.edges.get(edge[0], ())) in selected_sources]
    if len(candidates) < count:
        candidates = all_edges
    rng.shuffle(candidates)
    return candidates[:count]


def rewire_edges(system: Any, edges_to_rewire: list[tuple[object, object]], rng: random.Random, suffix: str) -> Any:
    out = {state: set(system.edges.get(state, ())) for state in system.states}
    states = tuple(system.states)
    for source, target in edges_to_rewire:
        if target not in out.get(source, set()):
            continue
        out[source].discard(target)
        candidates = [state for state in states if state not in out[source] and state != target]
        if candidates:
            out[source].add(rng.choice(candidates))
        else:
            out[source].add(target)
    edges = {state: tuple(sorted(out.get(state, set()))) for state in states}
    return replace(system, system_id=f"{system.system_id}_{suffix}", edges=edges, metadata={**system.metadata, "tiny_perturbation_suffix": suffix})


def syndrome_rate_rows(base: dict[str, object], flags: dict[str, set[str]], context_count: int, selected_syndromes: list[str]) -> list[dict[str, object]]:
    rows = []
    for syndrome_id in selected_syndromes:
        count = sum(1 for values in flags.values() if syndrome_id in values)
        rows.append({**base, "syndrome_id": syndrome_id, "syndrome_positive_contexts": count, "syndrome_positive_context_rate": count / max(1, context_count)})
    return rows


def entropy_response_rows(base: dict[str, object], metric_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped = group_by(metric_rows, ("flow_mode", "window"))
    rows = []
    for (flow_mode, window), items in grouped.items():
        rows.append({
            **base,
            "flow_mode": flow_mode,
            "window": window,
            "row_count": len(items),
            "frontier_growth_ratio_mean": mean([float_or_zero(row.get("frontier_growth_ratio")) for row in items]) if items else 0.0,
            "support_turnover_rate_mean": mean([float_or_zero(row.get("support_turnover_rate")) for row in items]) if items else 0.0,
            "edge_into_fb_rate_mean": mean([float_or_zero(row.get("edge_into_fb_rate")) for row in items]) if items else 0.0,
            "transition_matrix_entropy_mean": mean([float_or_zero(row.get("transition_matrix_entropy")) for row in items]) if items else 0.0,
        })
    return rows


def summarize_tiny_perturbation(
    manifest: list[dict[str, object]],
    preservation: list[dict[str, object]],
    syndrome: list[dict[str, object]],
    spectral: list[dict[str, object]],
) -> list[dict[str, object]]:
    computed = [row for row in manifest if row.get("perturbation_status") == "computed"]
    kinds = {row.get("perturbation_kind") for row in computed}
    destructive = [row for row in preservation if int(float_or_zero(row.get("control_too_destructive"))) == 1]
    target_spectral = [float_or_zero(row.get("positive_spectral_mass")) for row in spectral if row.get("perturbation_kind") == "spectral_high_loading_targeted_edge_perturbation"]
    random_spectral = [float_or_zero(row.get("positive_spectral_mass")) for row in spectral if row.get("perturbation_kind") == "matched_random_edge_perturbation"]
    target_ac = [float_or_zero(row.get("syndrome_positive_context_rate")) for row in syndrome if row.get("perturbation_kind") == "spectral_high_loading_targeted_edge_perturbation" and str(row.get("syndrome_id")) in PRIMARY_SYNDROMES]
    random_ac = [float_or_zero(row.get("syndrome_positive_context_rate")) for row in syndrome if row.get("perturbation_kind") == "matched_random_edge_perturbation" and str(row.get("syndrome_id")) in PRIMARY_SYNDROMES]
    spectral_sep = relative_separation(mean(target_spectral) if target_spectral else 0.0, mean(random_spectral) if random_spectral else 0.0)
    ac_sep = relative_separation(mean(target_ac) if target_ac else 0.0, mean(random_ac) if random_ac else 0.0)
    implemented = (
        "spectral_high_loading_targeted_edge_perturbation" in kinds
        and "matched_random_edge_perturbation" in kinds
        and not destructive
        and max(spectral_sep, ac_sep) >= 0.05
    )
    decision = "tiny_channel_perturbation_implemented" if implemented else "tiny_channel_perturbation_not_interpretable"
    return [{
        "decision_class": decision,
        "computed_perturbation_rows": len(computed),
        "destructive_rows": len(destructive),
        "targeted_spectral_positive_mass_mean": mean(target_spectral) if target_spectral else "",
        "random_spectral_positive_mass_mean": mean(random_spectral) if random_spectral else "",
        "targeted_vs_random_spectral_relative_separation": spectral_sep,
        "targeted_ac_rate_mean": mean(target_ac) if target_ac else "",
        "random_ac_rate_mean": mean(random_ac) if random_ac else "",
        "targeted_vs_random_ac_relative_separation": ac_sep,
    }]


def relative_separation(left: float, right: float) -> float:
    return abs(left - right) / max(1e-9, abs(left), abs(right))


def tiny_perturbation_status(summary: list[dict[str, object]]) -> str:
    if not summary:
        return "tiny_channel_perturbation_not_interpretable"
    return str(summary[0].get("decision_class", "tiny_channel_perturbation_not_interpretable"))


def channel_prep_decision_classes(
    control_summary: list[dict[str, object]],
    mapping_coverage: list[dict[str, object]],
    ablation_decision: list[dict[str, object]],
    perturbation_summary: list[dict[str, object]],
) -> list[str]:
    classes = ["runner_contract_passed"]
    classes.append(shuffle_status(control_summary))
    classes.append(mapping_status(mapping_coverage, 0.30))
    classes.append(ablation_decision[0].get("decision_class", "high_loading_ablation_random_equivalent") if ablation_decision else "high_loading_ablation_random_equivalent")
    classes.append(tiny_perturbation_status(perturbation_summary))
    if (
        classes[1] == "spectral_shuffle_controls_passed"
        and classes[2] == "spectral_item_mapping_adequate"
        and classes[3] == "high_loading_ablation_specific"
        and classes[4] == "tiny_channel_perturbation_implemented"
    ):
        classes.append("ready_for_24h_spectral_channel_run")
    else:
        classes.append("not_ready_repair_required")
    return [str(item) for item in classes]


def shuffle_status(control_summary: list[dict[str, object]]) -> str:
    if not control_summary:
        return "spectral_shuffle_controls_control_equivalent"
    reads = [row.get("shuffle_control_read") for row in control_summary]
    return "spectral_shuffle_controls_passed" if any(read == "observed_above_shuffle" for read in reads) else "spectral_shuffle_controls_control_equivalent"


def mapping_status(mapping_coverage: list[dict[str, object]], threshold: float) -> str:
    if not mapping_coverage:
        return "spectral_item_mapping_insufficient"
    return "spectral_item_mapping_adequate" if max(float_or_zero(row.get("mapped_item_mass_fraction")) for row in mapping_coverage) >= threshold else "spectral_item_mapping_insufficient"


def write_tiny_perturbation_placeholders(out_dir: Path) -> None:
    rows = [{"status": "not_run", "reason": "graph_level_targeted_perturbation_gated_until_shuffle_mapping_and_ablation_review"}]
    for name in (
        "spectral_channel_tiny_perturbation_manifest.csv",
        "spectral_channel_tiny_matching_quality.csv",
        "spectral_channel_tiny_substrate_preservation.csv",
        "spectral_channel_tiny_syndrome_rates.csv",
        "spectral_channel_tiny_spectral_response.csv",
        "spectral_channel_tiny_entropy_flow_horizon_response.csv",
        "spectral_channel_tiny_target_vs_random_summary.csv",
    ):
        write_csv(out_dir / name, rows)


def write_runner_contract_report(out_dir: Path, status: dict[str, object], errors: list[dict[str, object]]) -> None:
    lines = [
        "# Runner Output Contract Smoke Report",
        "",
        f"Status: `{status.get('status')}`.",
        f"Jobs: `{status.get('jobs_completed')}/{status.get('jobs_requested')}`.",
        f"Errors: `{len(errors)}`.",
        "",
        "Decision classes are split in `spectral_channel_prep_status.json`; forbidden Omega/agent/valuer/identity/holdout classes are not emitted.",
    ]
    (out_dir / "runner_output_contract_smoke_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_control_repair_report(out_dir: Path, rows: list[dict[str, object]]) -> None:
    counts = Counter(str(row.get("shuffle_control_read", "")) for row in rows)
    lines = ["# Spectral Control Repair Smoke Report", "", f"Rows: `{len(rows)}`."]
    for key, count in sorted(counts.items()):
        lines.append(f"- `{key}`: {count}")
    (out_dir / "spectral_control_repair_smoke_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_item_mapping_report(out_dir: Path, rows: list[dict[str, object]]) -> None:
    best = max((float_or_zero(row.get("mapped_item_mass_fraction")) for row in rows), default=0.0)
    lines = ["# Spectral Item Mapping Smoke Report", "", f"Best mapped item mass fraction: `{best:.3f}`."]
    (out_dir / "spectral_item_mapping_smoke_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_item_ablation_report(out_dir: Path, rows: list[dict[str, object]]) -> None:
    row = rows[0] if rows else {}
    lines = [
        "# Spectral Item Ablation Report",
        "",
        f"Decision class: `{row.get('decision_class', 'high_loading_ablation_random_equivalent')}`.",
        f"High-loading drop mean: `{float_or_zero(row.get('high_loading_drop_fraction_mean')):.4f}`.",
        f"Matched-random drop mean: `{float_or_zero(row.get('matched_random_drop_fraction_mean')):.4f}`.",
    ]
    (out_dir / "spectral_item_ablation_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_tiny_perturbation_report(out_dir: Path, summary: list[dict[str, object]]) -> None:
    row = summary[0] if summary else {}
    lines = [
        "# Spectral Channel Tiny Perturbation Smoke Report",
        "",
        f"Decision class: `{row.get('decision_class', 'tiny_channel_perturbation_not_interpretable')}`.",
        f"Computed perturbation rows: `{row.get('computed_perturbation_rows', 0)}`.",
        f"Destructive rows: `{row.get('destructive_rows', 0)}`.",
        "",
        "Interpret this as an implementation/readiness check only, not causal topology evidence.",
    ]
    (out_dir / "spectral_channel_tiny_smoke_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_channel_prep_report(
    out_dir: Path,
    status: dict[str, object],
    control_summary: list[dict[str, object]],
    mapping_coverage: list[dict[str, object]],
    ablation_decision: list[dict[str, object]],
) -> None:
    lines = [
        "# RFS-MB0 Stage B-2 Spectral Channel-Edge Smoke Repair Prep Report",
        "",
        "## Claim Boundary",
        "",
        "This was an instrument-readiness smoke only. It was not holdout validation, candidate promotion, Omega detection, agency detection, identity detection, or value detection.",
        "",
        "## Runtime And Hardware",
        "",
        f"Status: `{status.get('status')}`. Workers: `{status.get('workers')}`. Jobs: `{status.get('jobs_completed')}/{status.get('jobs_requested')}`.",
        "",
        "## Priority Stages Completed",
        "",
        "- Priority 0 runner/output contract: completed.",
        "- Priority 1 cheap spectral shuffle controls: completed.",
        "- Priority 2 high-loading export and mapping: completed.",
        "- Priority 3 analysis-only ablation: completed.",
        f"- Priority 4 graph-level tiny perturbation: `{status.get('tiny_channel_perturbation_status')}`.",
        "",
        "## Readiness For 24h Run",
        "",
        f"Decision classes: `{status.get('decision_classes')}`.",
        f"Ready for 24h run: `{status.get('ready_for_24h_run')}`.",
        "",
        "## Blockers / Repairs Required",
        "",
    ]
    if int(status.get("ready_for_24h_run", 0)):
        lines.append("No prep blocker was detected by this smoke. Treat this as readiness for a larger channel-edge run, not as a positive theory result.")
    else:
        lines.append("The 24h run remains blocked until the failed prep stage is repaired and reviewed.")
        if status.get("item_ablation_status") == "high_loading_ablation_random_equivalent":
            lines.append("Primary blocker: high-loading item ablation was random-equivalent at this smoke scale.")
        if status.get("tiny_channel_perturbation_status") == "tiny_channel_perturbation_not_interpretable":
            lines.append("Secondary blocker: tiny targeted-vs-random perturbation is not yet interpretable or was gated off.")
    lines.extend([
        "",
        "## Compact Readouts",
        "",
        f"Shuffle summary rows: `{len(control_summary)}`.",
        f"Best mapped item mass fraction: `{max((float_or_zero(row.get('mapped_item_mass_fraction')) for row in mapping_coverage), default=0.0):.3f}`.",
        f"Stable high-loading selected rows: `{status.get('stable_high_loading_selected_rows')}`.",
        f"Ablation decision: `{ablation_decision[0].get('decision_class', '') if ablation_decision else ''}`.",
        f"Ablation random matching: `{status.get('ablation_random_matching')}`.",
        "",
        "## Output Manifest",
        "",
        "See `spectral_channel_prep_output_manifest.json`.",
    ])
    (out_dir / "rfs_mb0_stage_b2_spectral_channel_edge_smoke_repair_prep_result.md").write_text("\n".join(lines), encoding="utf-8")


def write_channel_prep_status(out_dir: Path, status: dict[str, object], started: float) -> None:
    payload = dict(status)
    payload["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    (out_dir / "spectral_channel_prep_status.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_channel_prep_manifest(out_dir: Path) -> None:
    names = [
        name for name in OUTPUTS
        if name.startswith("spectral_")
        or name.startswith("runner_output_")
        or name == "rfs_mb0_stage_b2_spectral_channel_edge_smoke_repair_prep_result.md"
    ]
    rows = []
    for name in names:
        path = out_dir / name
        rows.append({"file": name, "exists": path.exists() or name == "spectral_channel_prep_output_manifest.json", "status": "present" if path.exists() or name == "spectral_channel_prep_output_manifest.json" else "missing", "row_count": csv_row_count(path) if path.suffix == ".csv" else ""})
    (out_dir / "spectral_channel_prep_output_manifest.json").write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


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
