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
from dataclasses import replace
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any

import numpy as np

from .landscape import exact_frontier
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
from .spectral_types import MatrixCounts, MatrixKey, SpectralMatrix
from .transition_energy_substrates import generate_job_baseline_system


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
    "spectral_shuffle_family_gate_summary.csv",
    "spectral_shuffle_failure_anatomy.csv",
    "spectral_control_repair_smoke_report.md",
    "spectral_selection_evaluation_partition_summary.csv",
    "spectral_subspace_transfer_diagnostic.csv",
    "spectral_subspace_distributedness_diagnostic.csv",
    "spectral_subspace_control_alignment.csv",
    "spectral_next_action_fork.csv",
    "spectral_readiness_levels.csv",
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
    parser.add_argument("--label-shuffle-min-percentile", type=float, default=0.80)
    parser.add_argument("--context-shuffle-min-percentile", type=float, default=0.80)
    parser.add_argument("--horizon-shuffle-min-percentile", type=float, default=0.80)
    parser.add_argument("--min-shuffle-families-passed", type=int, default=2)
    parser.add_argument("--shuffle-family-min-pass-fraction", type=float, default=0.50)
    parser.add_argument("--shuffle-family-min-median-percentile", type=float, default=0.80)
    parser.add_argument("--shuffle-family-catastrophic-min-percentile", type=float, default=0.50)
    parser.add_argument("--high-loading-top-k-items", type=int, default=24)
    parser.add_argument("--high-loading-candidate-pool-multiplier", type=int, default=8)
    parser.add_argument("--high-loading-min-seed-count", type=int, default=2)
    parser.add_argument("--high-loading-min-shuffle-survival-count", type=int, default=1)
    parser.add_argument("--high-loading-min-matrix-recurrence", type=int, default=1)
    parser.add_argument("--selection-evaluation-split", action="store_true")
    parser.add_argument("--selection-partition-fraction", type=float, default=0.50)
    parser.add_argument("--selection-partition-seed", type=str, default="stage_b2_spectral_partition_v1")
    parser.add_argument("--ablation-random-replicates", type=int, default=5)
    parser.add_argument("--ablation-specific-min-random-stds", type=float, default=1.0)
    parser.add_argument("--ablation-min-effect-metrics", type=int, default=2)
    parser.add_argument("--ablation-max-coverage-loss", type=float, default=0.60)
    parser.add_argument("--random-matching-min-quality", type=float, default=0.60)
    parser.add_argument("--subspace-transfer-min-alignment", type=float, default=0.50)
    parser.add_argument("--subspace-control-replicates", type=int, default=3)
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
    baseline = generate_job_baseline_system(job, params, seed)  # type: ignore[arg-type]
    control = make_stage_b2_control_system(baseline, job, seed, params)  # type: ignore[arg-type]
    probe, alphabet_size, probe_group = build_probe(control, str(job["probe_key"]), str(job["source_probe_family"]))
    starts = [control.states[(seed + i * 17) % len(control.states)] for i in range(int(job["start_samples"]))]
    windows = job_windows(job)
    horizons = sorted({h for window in windows for h in window})
    contexts: list[dict[str, object]] = []
    rows: list[dict[str, object]] = []
    row_kind = "baseline" if job.get("actual_control_name") == BASELINE_CONTROL else "mechanism_control"
    common = common_condition_fields(job, baseline.system_id, control.system_id, baseline.metadata)
    for start_index, start in enumerate(starts):
        frontiers = {h: exact_frontier(control, start, h) for h in horizons}
        for ha, hb in windows:
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


def job_windows(job: dict[str, object]) -> tuple[tuple[int, int], ...]:
    raw = job.get("horizon_pairs")
    if not raw:
        return WINDOWS
    out: list[tuple[int, int]] = []
    for item in raw:  # type: ignore[assignment]
        if isinstance(item, str):
            left, right = item.split("->", 1)
            out.append((int(left), int(right)))
        else:
            left, right = item  # type: ignore[misc]
            out.append((int(left), int(right)))
    return tuple(out) or WINDOWS


def common_condition_fields(
    job: dict[str, object],
    baseline_system_id: str,
    control_system_id: str,
    baseline_metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    keys = (
        "condition_id",
        "substrate_family",
        "substrate_variant",
        "transition_energy_family",
        "transition_energy_form",
        "potential_beta",
        "potential_smoothness",
        "potential_scale",
        "budget_kind",
        "budget_weight",
        "macro_invariant_kind",
        "macro_invariant_beta",
        "equivalent_beta_target",
        "max_entropy_sampler_draws",
        "max_entropy_delta_match_error_max",
        "asymmetry_alpha",
        "asymmetry_field_seed",
        "asymmetry_field_smoothness",
        "asymmetry_field_scale",
        "alpha_beta_pair",
        "transition_roughness_strength",
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
    out = {key: job.get(key, "") for key in keys} | {"baseline_system_id": baseline_system_id, "control_system_id": control_system_id}
    if baseline_metadata:
        metadata_keys = (
            "potential_neighbor_correlation",
            "potential_mean",
            "potential_std",
            "potential_min",
            "potential_max",
            "budget_mean",
            "budget_std",
            "budget_min",
            "budget_max",
            "budget_delta_mean",
            "macro_invariant_kind",
            "macro_invariant_beta",
            "macro_invariant_mean",
            "macro_invariant_std",
            "macro_invariant_min",
            "macro_invariant_max",
            "macro_invariant_delta_mean",
            "macro_invariant_value_distribution",
            "macro_invariant_delta_distribution",
            "equivalent_beta_target",
            "max_entropy_family",
            "max_entropy_constraint_profile",
            "max_entropy_sampler_status",
            "max_entropy_sampler_draws",
            "max_entropy_sampler_best_draw_index",
            "max_entropy_sampler_weight_iterations",
            "max_entropy_equivalent_beta_target",
            "max_entropy_target_marginal_applied",
            "max_entropy_calibration_family",
            "max_entropy_calibration_edge_count",
            "macro_invariant_delta_match_metric",
            "macro_invariant_delta_match_error",
            "macro_invariant_delta_match_tolerance",
            "macro_invariant_delta_target_distribution",
            "macro_invariant_delta_observed_distribution",
            "max_entropy_locality_violation_count",
            "max_entropy_out_degree_violation_count",
            "max_entropy_empty_successor_source_count",
            "max_entropy_reversibility_fraction_requested",
            "max_entropy_reversibility_fraction_applied",
            "asymmetry_field_seed",
            "asymmetry_field_smoothness",
            "asymmetry_field_scale",
            "asymmetry_alpha",
            "asymmetry_field_mean",
            "asymmetry_field_std",
            "asymmetry_field_min",
            "asymmetry_field_max",
            "asymmetry_delta_mean",
            "asymmetry_delta_distribution",
            "asymmetry_neighbor_correlation",
            "alpha_beta_pair",
            "interaction_read",
            "selected_energy_mean",
            "selected_energy_std",
            "mean_out_degree",
            "edge_count",
        )
        for key in metadata_keys:
            out[key] = baseline_metadata.get(key, "")
        for key in ("transition_energy_family", "transition_energy_form"):
            if not out.get(key):
                out[key] = baseline_metadata.get(key, "")
    return out


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
    selection_counts = counts
    evaluation_counts = counts
    selection_matrices = matrices
    evaluation_matrices = matrices
    partition_meta = {
        "partition_axis": "same_sample",
        "partition_balance": "",
        "selection_context_count": sum(bucket.contexts for bucket in counts.values()),
        "evaluation_context_count": sum(bucket.contexts for bucket in counts.values()),
        "selection_item_mass": sum(bucket.raw_item_mass for bucket in counts.values()),
        "evaluation_item_mass": sum(bucket.raw_item_mass for bucket in counts.values()),
    }
    selection_eval_status = "same_sample_exploratory"
    if getattr(args, "selection_evaluation_split", False):
        selection_counts, evaluation_counts, partition_meta = partition_matrix_counts(counts, args)
        selection_matrices = build_spectral_matrices(selection_counts, args)
        evaluation_matrices = build_spectral_matrices(evaluation_counts, args)
        selection_eval_status = "computed"
    selection_summary = matrix_summary_rows(selection_matrices, args)
    selection_summary_by_id = {str(row.get("matrix_id")): row for row in selection_summary}
    evaluation_by_id = {matrix.matrix_id: matrix for matrix in evaluation_matrices}
    target_pool = selection_matrices
    if getattr(args, "selection_evaluation_split", False):
        overlap_pool = [matrix for matrix in selection_matrices if matrix.matrix_id in evaluation_by_id]
        if overlap_pool:
            target_pool = overlap_pool
    target = prep_target_matrices(target_pool, selection_summary_by_id, args)
    evaluation_target = [evaluation_by_id[matrix.matrix_id] for matrix in target if matrix.matrix_id in evaluation_by_id]
    if getattr(args, "selection_evaluation_split", False) and not evaluation_target:
        selection_eval_status = "insufficient_evaluation_partition"
    label_rows = shuffle_smoke_rows("label_shuffle", target, counts, matrices, summary_by_id, args)
    context_rows = shuffle_smoke_rows("context_shuffle", target, counts, matrices, summary_by_id, args)
    horizon_rows = shuffle_smoke_rows("horizon_order_shuffle", target, counts, matrices, summary_by_id, args)
    control_summary = spectral_control_repair_summary(label_rows, context_rows, horizon_rows)
    shuffle_anatomy = shuffle_failure_anatomy_rows(control_summary, target, summary_by_id, args)
    loading_rows, loading_summary, candidate_rows = high_loading_rows(target, selection_counts, control_summary, args)
    mapping_rows, mapping_coverage = item_mapping_rows(loading_rows, counts, args)
    subspace_rows = subspace_transfer_rows(target, evaluation_target, args)
    distributed_rows = subspace_distributedness_rows(target, args)
    subspace_control_rows = subspace_control_alignment_rows(target, evaluation_target, evaluation_counts, evaluation_matrices, args)
    if not getattr(args, "selection_evaluation_split", False):
        high_ablation, random_ablation, low_mid_ablation, ablation_manifest = [], [], [], []
        ablation_decision = [{
            "decision_class": "same_sample_ablation_exploratory",
            "ablation_failure_reason": "selection_evaluation_split_required_for_readiness",
            "high_loading_drop_fraction_mean": "",
            "matched_random_drop_fraction_mean": "",
            "matrix_count": 0,
            "random_replicate_rows": 0,
            "random_matching": "not_run_without_selection_evaluation_split",
        }]
    elif selection_eval_status == "insufficient_evaluation_partition":
        high_ablation, random_ablation, low_mid_ablation, ablation_manifest = [], [], [], []
        ablation_decision = [{
            "decision_class": "selection_evaluation_split_insufficient",
            "ablation_failure_reason": "evaluation_partition_missing_target_matrices",
            "high_loading_drop_fraction_mean": "",
            "matched_random_drop_fraction_mean": "",
            "matrix_count": 0,
            "random_replicate_rows": 0,
            "random_matching": "item_count_and_baseline_flow_count_greedy",
        }]
    else:
        high_ablation, random_ablation, low_mid_ablation, ablation_manifest, ablation_decision = item_ablation_rows(evaluation_target, evaluation_counts, loading_rows, args)
        ablation_decision = add_subspace_read_to_ablation_decision(ablation_decision, subspace_rows)
    perturbation = tiny_channel_perturbation_rows(
        jobs,
        loading_rows,
        mapping_rows,
        args,
        control_summaries,
        components,
        selected_syndromes,
    ) if should_run_tiny_perturbation(control_summary, mapping_coverage, ablation_decision, args) else tiny_perturbation_placeholder_rows()
    readiness_rows = readiness_level_rows(control_summary, mapping_coverage, ablation_decision, perturbation["summary"], selection_eval_status, args)
    decision_classes = channel_prep_decision_classes(control_summary, mapping_coverage, ablation_decision, perturbation["summary"], readiness_rows, args)
    readiness_map = {str(row.get("readiness_key")): int(float_or_zero(row.get("ready"))) for row in readiness_rows}
    next_action_rows = next_action_fork_rows(control_summary, mapping_coverage, ablation_decision, subspace_rows, subspace_control_rows, args)
    next_action = str(next_action_rows[0].get("next_action_fork", "write_spectral_measurement_limits_note")) if next_action_rows else "write_spectral_measurement_limits_note"
    status.update({
        "channel_prep_status": "COMPLETED" if status.get("status") == "COMPLETED" else status.get("status"),
        "runner_contract_status": "runner_contract_passed",
        "spectral_shuffle_control_status": shuffle_status(control_summary, args),
        "item_mapping_status": mapping_status(mapping_coverage, args.mapping_mass_threshold),
        "item_ablation_status": ablation_decision[0].get("decision_class", "high_loading_ablation_random_equivalent") if ablation_decision else "high_loading_ablation_random_equivalent",
        "tiny_channel_perturbation_status": tiny_perturbation_status(perturbation["summary"]),
        "selection_evaluation_split_enabled": bool(getattr(args, "selection_evaluation_split", False)),
        "selection_evaluation_split_status": selection_eval_status,
        "selection_partition_axis": partition_meta.get("partition_axis", ""),
        "selection_partition_balance": partition_meta.get("partition_balance", ""),
        "selection_context_count": partition_meta.get("selection_context_count", ""),
        "evaluation_context_count": partition_meta.get("evaluation_context_count", ""),
        "selection_item_mass": partition_meta.get("selection_item_mass", ""),
        "evaluation_item_mass": partition_meta.get("evaluation_item_mass", ""),
        "selection_partition_fraction": getattr(args, "selection_partition_fraction", ""),
        "selection_partition_seed": getattr(args, "selection_partition_seed", ""),
        "label_shuffle_min_percentile": getattr(args, "label_shuffle_min_percentile", ""),
        "context_shuffle_min_percentile": getattr(args, "context_shuffle_min_percentile", ""),
        "horizon_shuffle_min_percentile": getattr(args, "horizon_shuffle_min_percentile", ""),
        "min_shuffle_families_passed": getattr(args, "min_shuffle_families_passed", ""),
        "shuffle_family_min_pass_fraction": getattr(args, "shuffle_family_min_pass_fraction", ""),
        "shuffle_family_min_median_percentile": getattr(args, "shuffle_family_min_median_percentile", ""),
        "shuffle_family_catastrophic_min_percentile": getattr(args, "shuffle_family_catastrophic_min_percentile", ""),
        "ablation_specific_min_random_stds": getattr(args, "ablation_specific_min_random_stds", ""),
        "ablation_min_effect_metrics": getattr(args, "ablation_min_effect_metrics", ""),
        "ablation_max_coverage_loss": getattr(args, "ablation_max_coverage_loss", ""),
        "random_matching_min_quality": getattr(args, "random_matching_min_quality", ""),
        "subspace_transfer_min_alignment": getattr(args, "subspace_transfer_min_alignment", ""),
        "selection_matrix_count": len(selection_matrices),
        "evaluation_matrix_count": len(evaluation_matrices),
        "selection_evaluation_target_overlap_count": len(evaluation_target),
        "high_loading_candidate_pool_rows": len(candidate_rows),
        "stable_high_loading_selected_rows": len(loading_rows),
        "stable_high_loading_matrix_count": sum(1 for row in loading_summary if row.get("selection_read") == "stable_items_selected"),
        "shuffle_replicates_completed": sum(1 for row in label_rows + context_rows + horizon_rows if row.get("shuffle_status") == "computed"),
        "high_loading_items_exported": len(loading_rows),
        "item_sets_mapped": len(mapping_coverage),
        "ablation_jobs_completed": len(high_ablation) + len(random_ablation) + len(low_mid_ablation),
        "perturbation_jobs_completed": sum(1 for row in perturbation["manifest"] if row.get("perturbation_status") == "computed"),
        "blocking_reason": channel_blocking_reason(readiness_rows, ablation_decision),
        "ablation_failure_reason": ablation_decision[0].get("ablation_failure_reason", "") if ablation_decision else "",
        "subspace_transfer_status": ablation_decision[0].get("subspace_transfer_status", "subspace_transfer_not_computed") if ablation_decision else "subspace_transfer_not_computed",
        "subspace_item_read": ablation_decision[0].get("subspace_item_read", "subspace_transfer_not_computed") if ablation_decision else "subspace_transfer_not_computed",
        "subspace_distributedness_read": aggregate_distributedness_read(distributed_rows),
        "subspace_control_alignment_status": aggregate_subspace_control_status(subspace_control_rows),
        "next_action_fork": next_action,
        "ablation_random_matching": ablation_decision[0].get("random_matching", "matrix_context_count_mass_greedy") if ablation_decision else "matrix_context_count_mass_greedy",
        "control_comparison_scope": "direct_stage_b2_plus_prep_shuffle_controls",
        "label_shuffled_controls_completed": True,
        "context_shuffled_controls_completed": True,
        "horizon_order_shuffled_controls_completed": True,
        "frontier_size_matched_controls_completed": False,
        "probe_marginal_controls_completed": False,
        "decision_classes": ";".join(decision_classes),
        "ready_for_larger_spectral_control_run": readiness_map.get("ready_for_larger_spectral_control_run", 0),
        "ready_for_larger_analysis_only_channel_run": readiness_map.get("ready_for_larger_analysis_only_channel_run", 0),
        "ready_for_tiny_graph_channel_perturbation": readiness_map.get("ready_for_tiny_graph_channel_perturbation", 0),
        "ready_for_larger_graph_channel_run": readiness_map.get("ready_for_larger_graph_channel_run", 0),
        "ready_for_24h_run": readiness_map.get("ready_for_larger_graph_channel_run", 0),
    })
    if int(status.get("ready_for_larger_graph_channel_run", 0)):
        status["branch_recommendation"] = "recommend_larger_graph_channel_run"
    elif int(status.get("ready_for_tiny_graph_channel_perturbation", 0)):
        status["branch_recommendation"] = "recommend_tiny_graph_channel_perturbation"
    elif int(status.get("ready_for_larger_analysis_only_channel_run", 0)):
        status["branch_recommendation"] = "recommend_ablation_repair_analysis_only_run"
    elif int(status.get("ready_for_larger_spectral_control_run", 0)):
        status["branch_recommendation"] = "recommend_larger_spectral_control_only_run"
    else:
        status["branch_recommendation"] = "recommend_spectral_channel_repair_before_large_run"
    write_csv(out_dir / "spectral_channel_prep_errors.csv", errors)
    write_csv(out_dir / "spectral_channel_prep_progress_checkpoints.csv", checkpoints)
    write_csv(out_dir / "spectral_label_shuffle_smoke.csv", label_rows)
    write_csv(out_dir / "spectral_context_shuffle_smoke.csv", context_rows)
    write_csv(out_dir / "spectral_horizon_shuffle_smoke.csv", horizon_rows)
    write_csv(out_dir / "spectral_control_repair_smoke_summary.csv", control_summary)
    write_csv(out_dir / "spectral_shuffle_family_gate_summary.csv", shuffle_family_summary(control_summary, args))
    write_csv(out_dir / "spectral_shuffle_failure_anatomy.csv", shuffle_anatomy)
    write_csv(out_dir / "spectral_selection_evaluation_partition_summary.csv", partition_summary_rows(selection_counts, evaluation_counts, partition_meta))
    write_csv(out_dir / "spectral_subspace_transfer_diagnostic.csv", subspace_rows)
    write_csv(out_dir / "spectral_subspace_distributedness_diagnostic.csv", distributed_rows)
    write_csv(out_dir / "spectral_subspace_control_alignment.csv", subspace_control_rows)
    write_csv(out_dir / "spectral_next_action_fork.csv", next_action_rows)
    write_csv(out_dir / "spectral_readiness_levels.csv", readiness_rows)
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


def subspace_transfer_rows(
    selection_target: list[SpectralMatrix],
    evaluation_target: list[SpectralMatrix],
    args: argparse.Namespace,
) -> list[dict[str, object]]:
    evaluation_by_id = {matrix.matrix_id: matrix for matrix in evaluation_target}
    rows: list[dict[str, object]] = []
    threshold = float(getattr(args, "subspace_transfer_min_alignment", 0.50))
    for selection_matrix in selection_target:
        evaluation_matrix = evaluation_by_id.get(selection_matrix.matrix_id)
        payload = alignment_payload(selection_matrix, evaluation_matrix, args.top_k)
        alignment = float_or_zero(payload.get("top_k_subspace_alignment"))
        status = str(payload.get("alignment_status", "comparison_matrix_unavailable"))
        rows.append({
            **key_row(selection_matrix.key),
            "matrix_id": selection_matrix.matrix_id,
            "selection_context_count": selection_matrix.contexts,
            "evaluation_context_count": evaluation_matrix.contexts if evaluation_matrix else 0,
            **payload,
            "subspace_transfer_threshold": threshold,
            "subspace_transfer_read": "subspace_transfers" if status == "computed" and alignment >= threshold else "subspace_does_not_transfer",
        })
    if not rows:
        rows.append({
            "matrix_id": "",
            "alignment_status": "comparison_matrix_unavailable",
            "top_k_subspace_alignment": "",
            "aligned_item_count": 0,
            "subspace_transfer_threshold": threshold,
            "subspace_transfer_read": "subspace_transfer_not_computed",
        })
    return rows


def shuffle_failure_anatomy_rows(
    control_summary: list[dict[str, object]],
    target: list[SpectralMatrix],
    summary_by_id: dict[str, dict[str, object]],
    args: argparse.Namespace,
) -> list[dict[str, object]]:
    matrix_by_id = {matrix.matrix_id: matrix for matrix in target}
    rows: list[dict[str, object]] = []
    for row in control_summary:
        matrix_id = str(row.get("matrix_id", ""))
        matrix = matrix_by_id.get(matrix_id)
        summary = summary_by_id.get(matrix_id, {})
        family = str(row.get("shuffle_kind", ""))
        percentile = float_or_zero(row.get("observed_percentile_vs_shuffle"))
        threshold = shuffle_family_threshold(family, args)
        catastrophic_floor = float(getattr(args, "shuffle_family_catastrophic_min_percentile", 0.50))
        rows.append({
            **key_subset(row),
            "matrix_id": matrix_id,
            "shuffle_family": family,
            "shuffle_control_category": shuffle_control_category(family),
            "family_required_for_control_gate": int(shuffle_family_required(family)),
            "observed_percentile_vs_shuffle": percentile,
            "matrix_shuffle_passed": int(percentile >= threshold),
            "catastrophic_fail_flag": int(percentile < catastrophic_floor),
            "threshold": threshold,
            "catastrophic_floor": catastrophic_floor,
            "item_count": len(matrix.items) if matrix else summary.get("item_count", ""),
            "coverage": summary.get("item_mass_coverage", matrix.item_mass_covered / max(1, matrix.item_mass_total) if matrix else ""),
            "positive_spectral_mass": summary.get("positive_spectral_mass", row.get("observed_positive_spectral_mass", "")),
            "effective_rank": summary.get("effective_rank", ""),
            "blocking_reason": "" if percentile >= threshold and percentile >= catastrophic_floor else shuffle_family_blocker([percentile], int(percentile >= threshold), percentile, int(percentile < catastrophic_floor), 1.0, threshold),
        })
    return rows


def subspace_distributedness_rows(target: list[SpectralMatrix], args: argparse.Namespace) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for matrix in target:
        weights = subspace_loading_weights(matrix, args.top_k)
        total = float(np.sum(weights))
        if total <= 1e-12 or not matrix.items:
            rows.append({
                **key_row(matrix.key),
                "matrix_id": matrix.matrix_id,
                "item_count": len(matrix.items),
                "distributedness_read": "diffuse_noise_like",
                "loading_entropy": 0.0,
                "loading_entropy_fraction": 0.0,
                "effective_contributing_items": 0.0,
                "participation_ratio": 0.0,
                "top_item_mass_share": 0.0,
                "top_5_item_mass_share": 0.0,
                "top_20_item_mass_share": 0.0,
            })
            continue
        probs = np.asarray(weights, dtype=np.float64) / total
        ordered = sorted((float(value) for value in probs), reverse=True)
        entropy = -sum(value * math.log(value) for value in ordered if value > 1e-12)
        entropy_fraction = entropy / max(1e-9, math.log(max(2, len(ordered))))
        effective_items = math.exp(entropy)
        participation = 1.0 / max(1e-12, sum(value * value for value in ordered))
        top1 = ordered[0] if ordered else 0.0
        top5 = sum(ordered[:5])
        top20 = sum(ordered[:20])
        rows.append({
            **key_row(matrix.key),
            "matrix_id": matrix.matrix_id,
            "item_count": len(matrix.items),
            "positive_spectral_mass": float(np.sum(matrix.eigvals[matrix.eigvals > 0])) if matrix.eigvals.size else 0.0,
            "loading_entropy": entropy,
            "loading_entropy_fraction": entropy_fraction,
            "effective_contributing_items": effective_items,
            "participation_ratio": participation,
            "top_item_mass_share": top1,
            "top_5_item_mass_share": top5,
            "top_20_item_mass_share": top20,
            "distributedness_read": distributedness_class(top1, top5, top20, effective_items, entropy_fraction, len(ordered)),
        })
    return rows


def subspace_loading_weights(matrix: SpectralMatrix, top_k: int) -> np.ndarray:
    if matrix.eigvecs.size == 0 or not matrix.items:
        return np.zeros(0, dtype=np.float64)
    weights = np.zeros(len(matrix.items), dtype=np.float64)
    ordered = np.argsort(matrix.eigvals)[::-1]
    positive_modes = [idx for idx in ordered if matrix.eigvals[idx] > 0][:top_k]
    for mode_index in positive_modes:
        vector = matrix.eigvecs[:, mode_index]
        weights += abs(float(matrix.eigvals[mode_index])) * (vector ** 2)
    return weights


def distributedness_class(top1: float, top5: float, top20: float, effective_items: float, entropy_fraction: float, item_count: int) -> str:
    if top1 >= 0.35 or effective_items <= 3:
        return "item_local"
    if top5 >= 0.65 or effective_items <= 10:
        return "cluster_local"
    if entropy_fraction >= 0.90 and effective_items >= 0.50 * max(1, item_count):
        return "diffuse_noise_like"
    if top20 < 0.80 and effective_items >= 10:
        return "distributed"
    return "cluster_local"


def aggregate_distributedness_read(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "subspace_distributedness_not_computed"
    counts = Counter(str(row.get("distributedness_read", "")) for row in rows)
    return counts.most_common(1)[0][0] if counts else "subspace_distributedness_not_computed"


def subspace_control_alignment_rows(
    selection_target: list[SpectralMatrix],
    evaluation_target: list[SpectralMatrix],
    evaluation_counts: dict[MatrixKey, MatrixCounts],
    evaluation_matrices: list[SpectralMatrix],
    args: argparse.Namespace,
) -> list[dict[str, object]]:
    evaluation_by_id = {matrix.matrix_id: matrix for matrix in evaluation_target}
    context_pool = shuffled_context_pool(evaluation_matrices, evaluation_counts)
    rows: list[dict[str, object]] = []
    for selection_matrix in selection_target:
        evaluation_matrix = evaluation_by_id.get(selection_matrix.matrix_id)
        actual = alignment_payload(selection_matrix, evaluation_matrix, args.top_k)
        actual_alignment = float_or_zero(actual.get("top_k_subspace_alignment"))
        bucket = evaluation_counts.get(evaluation_matrix.key) if evaluation_matrix else None
        for family in ("label_shuffle", "context_shuffle", "horizon_order_shuffle", "random_subspace_baseline"):
            values: list[float] = []
            statuses: list[str] = []
            for replicate in range(max(1, int(getattr(args, "subspace_control_replicates", 3)))):
                rng = random.Random(stable_seed(f"subspace_control|{family}|{selection_matrix.matrix_id}|{replicate}"))
                if family == "random_subspace_baseline":
                    payload = random_subspace_alignment_payload(selection_matrix, evaluation_matrix, args.top_k, rng)
                else:
                    payload = shuffled_subspace_alignment_payload(selection_matrix, evaluation_matrix, bucket, context_pool, family, args, rng)
                statuses.append(str(payload.get("alignment_status", "")))
                if payload.get("alignment_status") == "computed":
                    values.append(float_or_zero(payload.get("top_k_subspace_alignment")))
            mean_value = mean(values) if values else 0.0
            max_value = max(values) if values else 0.0
            std_value = pstdev(values) if len(values) > 1 else 0.0
            above = actual.get("alignment_status") == "computed" and values and actual_alignment > max_value
            rows.append({
                **key_row(selection_matrix.key),
                "matrix_id": selection_matrix.matrix_id,
                "control_family": family,
                "control_category": shuffle_control_category(family),
                "actual_selection_evaluation_alignment": actual_alignment if actual.get("alignment_status") == "computed" else "",
                "actual_alignment_status": actual.get("alignment_status", ""),
                "control_alignment_mean": mean_value if values else "",
                "control_alignment_std": std_value if values else "",
                "control_alignment_max": max_value if values else "",
                "control_computed_replicates": len(values),
                "subspace_transfer_above_control": int(bool(above)),
                "subspace_control_read": "subspace_transfer_above_controls" if above else "subspace_transfer_control_equivalent",
                "control_statuses": ";".join(sorted(set(statuses))),
            })
    if not rows:
        rows.append({"matrix_id": "", "control_family": "", "subspace_control_read": "subspace_control_alignment_not_computed"})
    return rows


def shuffled_subspace_alignment_payload(
    selection_matrix: SpectralMatrix,
    evaluation_matrix: SpectralMatrix | None,
    bucket: MatrixCounts | None,
    context_pool: dict[tuple[object, ...], list[tuple[str, tuple[str, ...]]]],
    family: str,
    args: argparse.Namespace,
    rng: random.Random,
) -> dict[str, object]:
    if evaluation_matrix is None or bucket is None:
        return {"alignment_status": "comparison_matrix_unavailable", "top_k_subspace_alignment": "", "aligned_item_count": 0}
    if family == "label_shuffle":
        contexts = label_shuffled_contexts(bucket, rng)
    elif family == "context_shuffle":
        contexts = sampled_contexts(context_pool.get(context_shuffle_key(evaluation_matrix.key), []), len(bucket.context_items), rng)
    else:
        contexts = sampled_contexts(context_pool.get(horizon_shuffle_key(evaluation_matrix.key), []), len(bucket.context_items), rng)
    control = spectral_matrix_from_contexts(evaluation_matrix.key, contexts, args)
    return alignment_payload(selection_matrix, control, args.top_k)


def spectral_matrix_from_contexts(key: MatrixKey, contexts: list[tuple[str, tuple[str, ...]]], args: argparse.Namespace) -> SpectralMatrix | None:
    bucket = MatrixCounts.empty()
    for context_id, items in contexts:
        add_partition_context(bucket, context_id, items)
    matrices = build_spectral_matrices({key: bucket}, args)
    return matrices[0] if matrices else None


def random_subspace_alignment_payload(
    selection_matrix: SpectralMatrix,
    evaluation_matrix: SpectralMatrix | None,
    top_k: int,
    rng: random.Random,
) -> dict[str, object]:
    common = sorted(set(selection_matrix.items) & (set(evaluation_matrix.items) if evaluation_matrix else set(selection_matrix.items)))
    if len(common) < max(2, top_k):
        return {"alignment_status": "insufficient_common_items", "top_k_subspace_alignment": "", "aligned_item_count": len(common)}
    left_sub = submatrix(selection_matrix, common)
    left_vals, left_vecs = np.linalg.eigh(left_sub)
    k = min(top_k, len(common), left_vecs.shape[1])
    u = left_vecs[:, np.argsort(np.abs(left_vals))[-k:]]
    random_matrix = np.asarray([[rng.gauss(0.0, 1.0) for _col in range(k)] for _row in range(len(common))], dtype=np.float64)
    q, _r = np.linalg.qr(random_matrix)
    v = q[:, :k]
    alignment = float(np.linalg.norm(u.T @ v, ord="fro") ** 2 / max(1, k))
    return {"alignment_status": "computed", "top_k_subspace_alignment": alignment, "aligned_item_count": len(common)}


def aggregate_subspace_control_status(rows: list[dict[str, object]]) -> str:
    computed = [row for row in rows if row.get("actual_alignment_status") == "computed" and int(float_or_zero(row.get("control_computed_replicates"))) > 0]
    if not computed:
        return "subspace_control_alignment_not_computed"
    structure = [row for row in computed if row.get("control_category") == "structure_destroying_control"]
    basis = structure or computed
    passed = sum(1 for row in basis if int(float_or_zero(row.get("subspace_transfer_above_control"))) == 1)
    return "subspace_transfer_above_controls" if passed >= max(1, math.ceil(len(basis) / 2)) else "subspace_transfer_control_equivalent"


def next_action_fork_rows(
    control_summary: list[dict[str, object]],
    mapping_coverage: list[dict[str, object]],
    ablation_decision: list[dict[str, object]],
    subspace_rows: list[dict[str, object]],
    subspace_control_rows: list[dict[str, object]],
    args: argparse.Namespace,
) -> list[dict[str, object]]:
    shuffle_read = shuffle_status(control_summary, args)
    mapping_read = mapping_status(mapping_coverage, args.mapping_mass_threshold)
    ablation_read = str(ablation_decision[0].get("decision_class", "")) if ablation_decision else ""
    subspace_read = subspace_transfer_status(subspace_rows)
    control_read = aggregate_subspace_control_status(subspace_control_rows)
    if shuffle_read != "spectral_shuffle_controls_passed":
        action = "repair_shuffle_controls"
        reason = "structure_destroying_shuffle_controls_not_passed"
    elif subspace_read == "subspace_transfers" and control_read == "subspace_transfer_above_controls" and ablation_read != "high_loading_ablation_specific":
        action = "run_subspace_ablation_smoke"
        reason = "subspace_transfers_above_controls_but_items_not_specific"
    elif ablation_read != "high_loading_ablation_specific":
        action = "run_item_ablation_repair"
        reason = "item_local_ablation_not_specific"
    elif mapping_read != "spectral_item_mapping_adequate":
        action = "write_spectral_measurement_limits_note"
        reason = "mapping_insufficient_for_graph_path"
    elif ablation_read == "high_loading_ablation_specific":
        action = "prepare_graph_perturbation_spec"
        reason = "controls_mapping_and_item_ablation_passed"
    else:
        action = "write_spectral_measurement_limits_note"
        reason = "no_interpretable_next_experimental_path"
    return [{
        "next_action_fork": action,
        "fork_reason": reason,
        "shuffle_status": shuffle_read,
        "mapping_status": mapping_read,
        "ablation_status": ablation_read,
        "subspace_transfer_status": subspace_read,
        "subspace_control_alignment_status": control_read,
    }]


def subspace_transfer_status(rows: list[dict[str, object]]) -> str:
    computed = [row for row in rows if row.get("alignment_status") == "computed"]
    if not computed:
        return "subspace_transfer_not_computed"
    transfers = [row for row in computed if row.get("subspace_transfer_read") == "subspace_transfers"]
    return "subspace_transfers" if len(transfers) >= max(1, math.ceil(len(computed) / 2)) else "subspace_does_not_transfer"


def add_subspace_read_to_ablation_decision(
    ablation_decision: list[dict[str, object]],
    subspace_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    status = subspace_transfer_status(subspace_rows)
    out: list[dict[str, object]] = []
    for row in ablation_decision:
        decision = str(row.get("decision_class", "high_loading_ablation_random_equivalent"))
        if decision == "high_loading_ablation_specific" and status == "subspace_transfers":
            combined = "item_specific_and_subspace_transfers"
        elif decision != "high_loading_ablation_specific" and status == "subspace_transfers":
            combined = "subspace_transfers_but_items_not_specific"
        elif status == "subspace_does_not_transfer":
            combined = "subspace_does_not_transfer"
        else:
            combined = "subspace_transfer_not_computed"
        out.append({**row, "subspace_transfer_status": status, "subspace_item_read": combined})
    return out


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
            control_matrix = spectral_matrix_from_contexts(matrix.key, contexts, args)
            alignment = alignment_payload(matrix, control_matrix, args.top_k)
            rows.append({
                **key_row(matrix.key),
                "matrix_id": matrix.matrix_id,
                "shuffle_kind": shuffle_kind,
                "replicate": replicate,
                "observed_positive_spectral_mass": observed.get("positive_spectral_mass", ""),
                "shuffle_positive_spectral_mass": payload["positive_spectral_mass"],
                "observed_effective_rank": observed.get("effective_rank", ""),
                "shuffle_effective_rank": payload["effective_rank"],
                "observed_top1_participation": observed.get("participation_ratio_top_modes", ""),
                "shuffle_top1_participation": payload["top1_participation"],
                "observed_topk_alignment": 1.0 if matrix.items else "",
                "shuffle_topk_alignment": alignment.get("top_k_subspace_alignment", ""),
                "shuffle_topk_alignment_status": alignment.get("alignment_status", ""),
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


def partition_matrix_counts(
    counts: dict[MatrixKey, MatrixCounts],
    args: argparse.Namespace,
) -> tuple[dict[MatrixKey, MatrixCounts], dict[MatrixKey, MatrixCounts], dict[str, object]]:
    selection: dict[MatrixKey, MatrixCounts] = defaultdict(MatrixCounts.empty)
    evaluation: dict[MatrixKey, MatrixCounts] = defaultdict(MatrixCounts.empty)
    fraction = max(0.05, min(0.95, float_or_zero(getattr(args, "selection_partition_fraction", 0.5))))
    salt = str(getattr(args, "selection_partition_seed", "stage_b2_spectral_partition_v1"))
    axis, axis_index = choose_partition_axis(counts)
    assignments = partition_value_assignments(counts, axis, axis_index, fraction, salt)
    for key, bucket in counts.items():
        for context_id, items in bucket.context_items:
            partition_value = context_partition_value(context_id, axis_index) if axis_index is not None else context_id
            target = selection if assignments.get(partition_value, True) else evaluation
            add_partition_context(target[key], context_id, items)
    if split_matrix_count(selection, evaluation) == 0 and axis != "context_hash":
        selection = defaultdict(MatrixCounts.empty)
        evaluation = defaultdict(MatrixCounts.empty)
        axis, axis_index = "context_hash", None
        assignments = partition_value_assignments(counts, axis, axis_index, fraction, salt)
        for key, bucket in counts.items():
            for context_id, items in bucket.context_items:
                target = selection if assignments.get(context_id, True) else evaluation
                add_partition_context(target[key], context_id, items)
    selection_contexts = sum(bucket.contexts for bucket in selection.values())
    evaluation_contexts = sum(bucket.contexts for bucket in evaluation.values())
    selection_mass = sum(bucket.raw_item_mass for bucket in selection.values())
    evaluation_mass = sum(bucket.raw_item_mass for bucket in evaluation.values())
    total_contexts = selection_contexts + evaluation_contexts
    meta = {
        "partition_axis": axis,
        "partition_balance": selection_contexts / max(1, total_contexts),
        "selection_context_count": selection_contexts,
        "evaluation_context_count": evaluation_contexts,
        "selection_item_mass": selection_mass,
        "evaluation_item_mass": evaluation_mass,
    }
    return selection, evaluation, meta


def split_matrix_count(selection: dict[MatrixKey, MatrixCounts], evaluation: dict[MatrixKey, MatrixCounts]) -> int:
    return sum(
        1
        for key in set(selection) | set(evaluation)
        if selection.get(key, MatrixCounts.empty()).contexts > 0 and evaluation.get(key, MatrixCounts.empty()).contexts > 0
    )


def partition_value_assignments(
    counts: dict[MatrixKey, MatrixCounts],
    axis: str,
    axis_index: int | None,
    fraction: float,
    salt: str,
) -> dict[str, bool]:
    values = sorted({
        context_partition_value(context_id, axis_index) if axis_index is not None else context_id
        for bucket in counts.values()
        for context_id, _items in bucket.context_items
    })
    if len(values) <= 1:
        return {value: stable_partition_fraction(f"{axis}|{value}", salt) < fraction for value in values}
    ordered = sorted(values, key=lambda value: stable_partition_fraction(f"{axis}|{value}", salt))
    selection_count = min(len(values) - 1, max(1, round(len(values) * fraction)))
    return {value: index < selection_count for index, value in enumerate(ordered)}


def choose_partition_axis(counts: dict[MatrixKey, MatrixCounts]) -> tuple[str, int | None]:
    candidates = (
        ("group_id", 1),
        ("seed", 2),
        ("start_index", 4),
        ("probe_key", 3),
        ("flow_mode", 6),
    )
    context_ids = [context_id for bucket in counts.values() for context_id, _items in bucket.context_items]
    for axis, index in candidates:
        values = {context_partition_value(context_id, index) for context_id in context_ids}
        if len(values) >= 2:
            return axis, index
    return "context_hash", None


def context_partition_value(context_id: str, index: int) -> str:
    parts = str(context_id).split("|")
    return parts[index] if len(parts) > index else ""


def partition_summary_rows(
    selection_counts: dict[MatrixKey, MatrixCounts],
    evaluation_counts: dict[MatrixKey, MatrixCounts],
    partition_meta: dict[str, object],
) -> list[dict[str, object]]:
    rows = [{
        "partition_axis": partition_meta.get("partition_axis", ""),
        "partition_balance": partition_meta.get("partition_balance", ""),
        "selection_context_count": partition_meta.get("selection_context_count", ""),
        "evaluation_context_count": partition_meta.get("evaluation_context_count", ""),
        "selection_item_mass": partition_meta.get("selection_item_mass", ""),
        "evaluation_item_mass": partition_meta.get("evaluation_item_mass", ""),
        "partition_read": "computed" if float_or_zero(partition_meta.get("selection_context_count")) > 0 and float_or_zero(partition_meta.get("evaluation_context_count")) > 0 else "insufficient",
    }]
    keys = sorted(set(selection_counts) | set(evaluation_counts), key=lambda key: matrix_id_for_key(key))
    for key in keys:
        selection = selection_counts.get(key, MatrixCounts.empty())
        evaluation = evaluation_counts.get(key, MatrixCounts.empty())
        rows.append({
            **key_row(key),
            "matrix_id": matrix_id_for_key(key),
            "partition_axis": partition_meta.get("partition_axis", ""),
            "selection_context_count": selection.contexts,
            "evaluation_context_count": evaluation.contexts,
            "selection_item_mass": selection.raw_item_mass,
            "evaluation_item_mass": evaluation.raw_item_mass,
            "partition_read": "matrix_split_available" if selection.contexts > 0 and evaluation.contexts > 0 else "matrix_split_insufficient",
        })
    return rows


def add_partition_context(bucket: MatrixCounts, context_id: str, items: tuple[str, ...]) -> None:
    unique = tuple(sorted(set(items)))
    if not unique:
        return
    bucket.contexts += 1
    bucket.raw_item_mass += len(unique)
    bucket.context_items.append((context_id, unique))
    bucket.item_counts.update(unique)
    for index, left in enumerate(unique):
        for right in unique[index + 1:]:
            bucket.pair_counts[(left, right)] += 1


def stable_partition_fraction(context_id: object, salt: str) -> float:
    value = 0
    for char in f"{salt}|{context_id}":
        value = (value * 131 + ord(char)) % 1_000_003
    return value / 1_000_003


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
        return {"status": "insufficient_items", "item_count": len(retained), "positive_spectral_mass": 0.0, "effective_rank": 0.0, "spectral_gap_k": 0.0, "top1_participation": 0.0}
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
    eigvals, eigvecs = np.linalg.eigh(matrix)
    positive = eigvals[eigvals > 0]
    absvals = np.abs(eigvals)
    top_index = int(np.argmax(absvals)) if absvals.size else 0
    return {
        "status": "computed",
        "item_count": len(items),
        "positive_spectral_mass": float(np.sum(positive)) if positive.size else 0.0,
        "effective_rank": effective_rank(absvals),
        "spectral_gap_k": spectral_gap(absvals, args.top_k),
        "top1_participation": participation_ratio(eigvecs[:, top_index]) if eigvecs.size else 0.0,
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
        for rank, row in enumerate(selected, start=1):
            row["selection_status"] = "stable_selected"
            row["selection_partition"] = "selection"
            row["loading_rank"] = rank
        rows.extend(selected)
        loading_score_sum = sum(float_or_zero(row.get("loading_score")) for row in selected)
        loading_score_max = max((float_or_zero(row.get("loading_score")) for row in selected), default=0.0)
        summaries.append({
            **key_row(matrix.key),
            "matrix_id": matrix.matrix_id,
            "positive_mode_count_used": len([idx for idx in np.argsort(matrix.eigvals)[::-1] if matrix.eigvals[idx] > 0][: args.top_k]),
            "candidate_pool_count": len(enriched),
            "stable_candidate_count": len(stable),
            "high_loading_item_count": len(selected),
            "high_loading_item_mass": sum(float_or_zero(row.get("item_mass")) for row in selected),
            "high_loading_score_sum": loading_score_sum,
            "high_loading_score_max": loading_score_max,
            "high_loading_top_score_fraction": loading_score_max / max(1e-9, loading_score_sum),
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
            "mapped_realized_edge_count": edge_count,
            "realized_edge_sample_json": json.dumps((bucket.item_edge_samples.get(item, []) if bucket else [])[:8], sort_keys=True),
            "mapped_item_mass": mapped_mass,
            "mapping_status": status,
        })
    coverage: list[dict[str, object]] = []
    for (matrix_id,), items in group_by(rows, ("matrix_id",)).items():
        total_mass = sum(float_or_zero(row.get("item_mass")) for row in items)
        mapped_mass = sum(float_or_zero(row.get("mapped_item_mass")) for row in items)
        mapped_count = sum(1 for row in items if row.get("mapping_status") == "mapped_to_realized_edges")
        mapped_realized_edge_count = sum(int(float_or_zero(row.get("mapped_realized_edge_count"))) for row in items if row.get("mapping_status") == "mapped_to_realized_edges")
        first = items[0] if items else {}
        fraction = mapped_mass / max(1.0, total_mass)
        coverage.append({
            **key_subset(first),
            "matrix_id": matrix_id,
            "mapped_item_count": mapped_count,
            "mapped_realized_edge_count": mapped_realized_edge_count,
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
        observed = spectral_metrics_for_matrix(matrix, args.top_k)
        high_payload = spectral_payload_from_contexts(bucket.context_items, args, high_items)
        base = {
            **key_row(matrix.key),
            "matrix_id": matrix.matrix_id,
            "removed_item_count": len(high_items),
            **{f"observed_{key}": value for key, value in observed.items()},
        }
        high_rows.append(ablation_metric_row(
            {
                **base,
                "ablation_kind": "high_loading",
            },
            observed,
            high_payload,
            high_items,
            bucket,
        ))
        manifest.append({
            **base,
            "ablation_kind": "high_loading",
            "removed_items_json": json.dumps(sorted(high_items)[:64]),
            "removed_item_mass": removed_item_mass(bucket, high_items),
            "coverage_loss_after_ablation": coverage_loss_after_ablation(bucket, high_items),
        })
        candidates = [item for item in matrix.items if item not in high_items]
        for replicate in range(max(1, args.ablation_random_replicates)):
            rng = random.Random(stable_seed(f"ablation|{matrix.matrix_id}|{replicate}"))
            random_items, matching = matched_random_item_set(candidates, selected_rows, bucket, baseline_bucket, rng)
            payload = spectral_payload_from_contexts(bucket.context_items, args, random_items)
            random_rows.append(ablation_metric_row(
                {
                    **base,
                    "ablation_kind": "frequency_baseline_flow_matched_random",
                    "replicate": replicate,
                    "matching_method": "matrix_context_count_mass_greedy",
                    "matching_preserved_fields": "matrix_family;condition_id;probe_key;flow_mode;horizon_band;item_count_bin;baseline_flow_count_bin;context_count_bin",
                    "matching_quality": matching.get("matching_quality", ""),
                    "matching_quality_read": matching.get("matching_quality_read", ""),
                    "removed_items_json": json.dumps(sorted(random_items)[:64]),
                },
                observed,
                payload,
                random_items,
                bucket,
            ))
        low_items = set(candidates[-min(len(high_items), len(candidates)):]) if candidates else set()
        payload = spectral_payload_from_contexts(bucket.context_items, args, low_items)
        low_rows.append(ablation_metric_row(
            {
                **base,
                "ablation_kind": "low_mid_loading",
            },
            observed,
            payload,
            low_items,
            bucket,
        ))
    decision_rows = [ablation_decision_row(high_rows, random_rows, low_rows, args)]
    return high_rows, random_rows, low_rows, manifest, decision_rows


def spectral_metrics_for_matrix(matrix: SpectralMatrix, top_k: int) -> dict[str, float]:
    eigvals = matrix.eigvals
    positive = eigvals[eigvals > 0]
    absvals = np.abs(eigvals)
    top_index = int(np.argmax(absvals)) if absvals.size else 0
    return {
        "positive_spectral_mass": float(np.sum(positive)) if positive.size else 0.0,
        "effective_rank": effective_rank(absvals),
        "spectral_gap_k": spectral_gap(absvals, top_k),
        "top1_participation": participation_ratio(matrix.eigvecs[:, top_index]) if matrix.eigvecs.size else 0.0,
    }


def ablation_metric_row(
    base: dict[str, object],
    observed: dict[str, float],
    payload: dict[str, object],
    removed_items: set[str],
    bucket: MatrixCounts,
) -> dict[str, object]:
    positive_drop = observed["positive_spectral_mass"] - float_or_zero(payload.get("positive_spectral_mass"))
    effective_rank_drop = observed["effective_rank"] - float_or_zero(payload.get("effective_rank"))
    gap_drop = observed["spectral_gap_k"] - float_or_zero(payload.get("spectral_gap_k"))
    participation_change = abs(observed["top1_participation"] - float_or_zero(payload.get("top1_participation")))
    return {
        **base,
        "removed_item_mass": removed_item_mass(bucket, removed_items),
        "coverage_loss_after_ablation": coverage_loss_after_ablation(bucket, removed_items),
        "ablated_positive_spectral_mass": payload.get("positive_spectral_mass", 0.0),
        "positive_spectral_mass_drop": positive_drop,
        "positive_spectral_mass_drop_fraction": positive_drop / max(1e-9, observed["positive_spectral_mass"]),
        "ablated_effective_rank": payload.get("effective_rank", 0.0),
        "effective_rank_drop": effective_rank_drop,
        "effective_rank_drop_fraction": effective_rank_drop / max(1e-9, observed["effective_rank"]),
        "ablated_spectral_gap_k": payload.get("spectral_gap_k", 0.0),
        "spectral_gap_drop": gap_drop,
        "spectral_gap_drop_fraction": gap_drop / max(1e-9, observed["spectral_gap_k"]),
        "ablated_top1_participation": payload.get("top1_participation", 0.0),
        "top1_participation_change": participation_change,
        "top1_participation_change_fraction": participation_change / max(1e-9, observed["top1_participation"]),
        "ablation_status": payload.get("status", ""),
    }


def removed_item_mass(bucket: MatrixCounts, removed_items: set[str]) -> int:
    return sum(bucket.item_counts.get(item, 0) for item in removed_items)


def coverage_loss_after_ablation(bucket: MatrixCounts, removed_items: set[str]) -> float:
    return removed_item_mass(bucket, removed_items) / max(1, bucket.raw_item_mass)


def ablation_decision_row(
    high_rows: list[dict[str, object]],
    random_rows: list[dict[str, object]],
    low_rows: list[dict[str, object]],
    args: argparse.Namespace,
) -> dict[str, object]:
    metric_fields = (
        "positive_spectral_mass_drop_fraction",
        "effective_rank_drop_fraction",
        "top1_participation_change_fraction",
    )
    high_delta = metric_mean(high_rows, "positive_spectral_mass_drop_fraction")
    random_delta_mean = metric_mean(random_rows, "positive_spectral_mass_drop_fraction")
    random_delta_std = metric_std(random_rows, "positive_spectral_mass_drop_fraction")
    random_delta_max = metric_max(random_rows, "positive_spectral_mass_drop_fraction")
    low_delta = metric_mean(low_rows, "positive_spectral_mass_drop_fraction")
    matching_quality = metric_mean(random_rows, "matching_quality") if random_rows else 0.0
    coverage_loss = metric_mean(high_rows, "coverage_loss_after_ablation")
    metric_wins = 0
    metric_reads: list[str] = []
    has_ablation_rows = bool(high_rows and random_rows)
    for field in metric_fields:
        high_value = metric_mean(high_rows, field)
        random_mean = metric_mean(random_rows, field)
        random_std = metric_std(random_rows, field)
        random_max = metric_max(random_rows, field)
        passed = has_ablation_rows and (
            high_value > random_max
            or (high_value > 0.0 and high_value >= random_mean + float(getattr(args, "ablation_specific_min_random_stds", 1.0)) * random_std)
        )
        metric_wins += int(passed)
        metric_reads.append(f"{field}:{'pass' if passed else 'fail'}")
    positive_specific = has_ablation_rows and (
        high_delta > random_delta_max
        or (high_delta > 0.0 and high_delta >= random_delta_mean + float(getattr(args, "ablation_specific_min_random_stds", 1.0)) * random_delta_std)
    )
    direction_match = int(high_delta > random_delta_mean and high_delta > low_delta)
    failure_reasons: list[str] = []
    if not high_rows or not random_rows:
        decision = "high_loading_ablation_insufficient"
        failure_reasons.append("ablation_rows_missing")
    elif matching_quality < float(getattr(args, "random_matching_min_quality", 0.60)):
        decision = "random_matching_weak_underdetermined"
        failure_reasons.append("random_matching_weak")
    elif coverage_loss > float(getattr(args, "ablation_max_coverage_loss", 0.60)):
        decision = "coverage_loss_too_high"
        failure_reasons.append("coverage_loss_too_high")
    elif positive_specific and metric_wins >= int(getattr(args, "ablation_min_effect_metrics", 2)):
        decision = "high_loading_ablation_specific"
    elif metric_wins == 1:
        decision = "single_metric_ablation_hint"
        failure_reasons.append("high_loading_delta_only_beat_random_on_one_metric")
    else:
        decision = "high_loading_ablation_random_equivalent"
        if high_delta <= random_delta_max:
            failure_reasons.append("high_loading_delta_le_random_max")
        if metric_wins < int(getattr(args, "ablation_min_effect_metrics", 2)):
            failure_reasons.append("insufficient_metric_specificity")
    return {
        "decision_class": decision,
        "ablation_failure_reason": ";".join(failure_reasons),
        "high_loading_delta": high_delta,
        "random_delta_mean": random_delta_mean,
        "random_delta_std": random_delta_std,
        "random_delta_max": random_delta_max,
        "matched_random_drop_fraction_std": random_delta_std,
        "matched_random_drop_fraction_max": random_delta_max,
        "low_loading_delta": low_delta,
        "high_loading_minus_random_mean": high_delta - random_delta_mean,
        "high_loading_over_random_ratio": high_delta / max(1e-9, random_delta_mean),
        "ablation_direction_match": direction_match,
        "coverage_loss_after_ablation": coverage_loss,
        "metric_specificity_wins": metric_wins,
        "effect_metric_count": metric_wins,
        "metric_specificity_reads": ";".join(metric_reads),
        "matching_quality": matching_quality,
        "random_matching_quality": matching_quality,
        "random_matching": "matrix_context_count_mass_greedy",
        "high_loading_drop_fraction_mean": high_delta,
        "matched_random_drop_fraction_mean": random_delta_mean,
        "matrix_count": len(high_rows),
        "random_replicate_rows": len(random_rows),
    }


def metric_mean(rows: list[dict[str, object]], field: str) -> float:
    values = [float_or_zero(row.get(field)) for row in rows if row.get(field) != ""]
    return mean(values) if values else 0.0


def metric_std(rows: list[dict[str, object]], field: str) -> float:
    values = [float_or_zero(row.get(field)) for row in rows if row.get(field) != ""]
    return pstdev(values) if len(values) > 1 else 0.0


def metric_max(rows: list[dict[str, object]], field: str) -> float:
    values = [float_or_zero(row.get(field)) for row in rows if row.get(field) != ""]
    return max(values) if values else 0.0


def matched_random_item_set(
    candidates: list[str],
    selected_rows: list[dict[str, object]],
    bucket: MatrixCounts,
    baseline_bucket: MatrixCounts | None,
    rng: random.Random,
) -> tuple[set[str], dict[str, object]]:
    available = set(candidates)
    selected: set[str] = set()
    candidate_items = list(available)
    qualities: list[float] = []
    stats = item_context_stats(bucket)
    for row in sorted(selected_rows, key=lambda item: float_or_zero(item.get("item_count")), reverse=True):
        if not candidate_items:
            break
        target_count = max(1.0, float_or_zero(row.get("item_count")))
        target_baseline = max(0.0, float_or_zero(row.get("baseline_flow_item_count")))
        target_contexts = max(1.0, float_or_zero(row.get("context_count")))
        scored = []
        for item in candidate_items:
            item_count = max(1.0, bucket.item_counts.get(item, 0))
            baseline_count = baseline_bucket.item_counts.get(item, 0) if baseline_bucket else item_count
            context_count = max(1.0, float_or_zero(stats.get(item, {}).get("context_count")))
            score = abs(math.log(item_count / target_count))
            score += 0.75 * abs(math.log((baseline_count + 1.0) / (target_baseline + 1.0)))
            score += 0.50 * abs(math.log(context_count / target_contexts))
            score += rng.random() * 1e-6
            scored.append((score, item))
        scored.sort(key=lambda pair: pair[0])
        best_score, chosen = scored[0]
        selected.add(chosen)
        qualities.append(max(0.0, 1.0 - best_score / 4.0))
        candidate_items.remove(chosen)
    quality = (mean(qualities) if qualities else 0.0) * (len(selected) / max(1, len(selected_rows)))
    return selected, {
        "matching_quality": quality,
        "matching_quality_read": "matching_strong" if quality >= 0.60 else "matching_weak",
    }


def should_run_tiny_perturbation(
    control_summary: list[dict[str, object]],
    mapping_coverage: list[dict[str, object]],
    ablation_decision: list[dict[str, object]],
    args: argparse.Namespace,
) -> bool:
    return (
        shuffle_status(control_summary, args) == "spectral_shuffle_controls_passed"
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
    baseline = generate_job_baseline_system(job, params, seed)  # type: ignore[arg-type]
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
    common = common_condition_fields(job, baseline.system_id, perturbed.system_id, baseline.metadata)
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
    readiness_rows: list[dict[str, object]],
    args: argparse.Namespace | None = None,
) -> list[str]:
    classes = ["runner_contract_passed"]
    classes.append(shuffle_status(control_summary, args))
    classes.append(mapping_status(mapping_coverage, float(getattr(args, "mapping_mass_threshold", 0.30)) if args is not None else 0.30))
    classes.append(ablation_decision[0].get("decision_class", "high_loading_ablation_random_equivalent") if ablation_decision else "high_loading_ablation_random_equivalent")
    if ablation_decision and ablation_decision[0].get("subspace_item_read"):
        classes.append(str(ablation_decision[0].get("subspace_item_read")))
    classes.append(tiny_perturbation_status(perturbation_summary))
    classes.extend(str(row.get("readiness_key")) for row in readiness_rows if int(float_or_zero(row.get("ready"))) == 1)
    if not any(str(row.get("readiness_key")) == "ready_for_larger_graph_channel_run" and int(float_or_zero(row.get("ready"))) == 1 for row in readiness_rows):
        classes.append("not_ready_repair_required")
    return [str(item) for item in classes]


def readiness_level_rows(
    control_summary: list[dict[str, object]],
    mapping_coverage: list[dict[str, object]],
    ablation_decision: list[dict[str, object]],
    perturbation_summary: list[dict[str, object]],
    selection_eval_status: str,
    args: argparse.Namespace | None = None,
) -> list[dict[str, object]]:
    shuffle_pass = shuffle_status(control_summary, args) == "spectral_shuffle_controls_passed"
    mapping_pass = mapping_status(mapping_coverage, float(getattr(args, "mapping_mass_threshold", 0.30)) if args is not None else 0.30) == "spectral_item_mapping_adequate"
    split_pass = selection_eval_status == "computed"
    ablation_pass = bool(ablation_decision) and ablation_decision[0].get("decision_class") == "high_loading_ablation_specific"
    tiny_pass = tiny_perturbation_status(perturbation_summary) == "tiny_channel_perturbation_implemented"
    rows = [
        readiness_row("ready_for_larger_spectral_control_run", shuffle_pass, "structure_shuffle_controls_passed", "structure_shuffle_controls_not_passed"),
        readiness_row("ready_for_larger_analysis_only_channel_run", shuffle_pass and mapping_pass and split_pass, "shuffle_mapping_and_split_passed", first_blocker((shuffle_pass, "structure_shuffle_failed"), (mapping_pass, "mapping_failed"), (split_pass, "selection_evaluation_split_required"))),
        readiness_row("ready_for_tiny_graph_channel_perturbation", shuffle_pass and mapping_pass and split_pass and ablation_pass, "ablation_specific_on_evaluation_partition", first_blocker((shuffle_pass, "structure_shuffle_failed"), (mapping_pass, "mapping_failed"), (split_pass, "selection_evaluation_split_required"), (ablation_pass, str(ablation_decision[0].get("ablation_failure_reason", "ablation_not_specific")) if ablation_decision else "ablation_not_specific"))),
        readiness_row("ready_for_larger_graph_channel_run", shuffle_pass and mapping_pass and split_pass and ablation_pass and tiny_pass, "tiny_targeted_vs_random_perturbation_passed", first_blocker((shuffle_pass, "structure_shuffle_failed"), (mapping_pass, "mapping_failed"), (split_pass, "selection_evaluation_split_required"), (ablation_pass, "ablation_not_specific"), (tiny_pass, "tiny_perturbation_not_passed"))),
    ]
    return rows


def channel_blocking_reason(readiness_rows: list[dict[str, object]], ablation_decision: list[dict[str, object]]) -> str:
    ablation_reason = str(ablation_decision[0].get("ablation_failure_reason", "")) if ablation_decision else ""
    for row in readiness_rows:
        if int(float_or_zero(row.get("ready"))) == 0:
            reason = str(row.get("readiness_reason", ""))
            if reason == "ablation_not_specific" and ablation_reason:
                return ablation_reason
            return reason
    return ""


def readiness_row(key: str, ready: bool, pass_reason: str, block_reason: str) -> dict[str, object]:
    return {
        "readiness_key": key,
        "ready": int(ready),
        "readiness_reason": pass_reason if ready else block_reason,
    }


def first_blocker(*checks: tuple[bool, str]) -> str:
    for passed, reason in checks:
        if not passed:
            return reason
    return ""


def shuffle_status(control_summary: list[dict[str, object]], args: argparse.Namespace | None = None) -> str:
    if not control_summary:
        return "spectral_shuffle_controls_control_equivalent"
    family_rows = shuffle_family_summary(control_summary, args)
    required_rows = [row for row in family_rows if int(row.get("family_required_for_control_gate", 1)) == 1]
    if required_rows:
        required_passed = all(int(row.get("family_passed", 0)) == 1 for row in required_rows)
        catastrophic = any(int(row.get("catastrophic_fail_count", 0)) > 0 for row in required_rows)
        return "spectral_shuffle_controls_passed" if required_passed and not catastrophic else "spectral_shuffle_controls_control_equivalent"
    passed = sum(int(row.get("family_passed", 0)) for row in family_rows)
    required = int(getattr(args, "min_shuffle_families_passed", 2)) if args is not None else 2
    return "spectral_shuffle_controls_passed" if passed >= required else "spectral_shuffle_controls_control_equivalent"


def shuffle_family_summary(control_summary: list[dict[str, object]], args: argparse.Namespace | None = None) -> list[dict[str, object]]:
    thresholds = {
        "label_shuffle": float(getattr(args, "label_shuffle_min_percentile", 0.80)) if args is not None else 0.80,
        "context_shuffle": float(getattr(args, "context_shuffle_min_percentile", 0.80)) if args is not None else 0.80,
        "horizon_order_shuffle": float(getattr(args, "horizon_shuffle_min_percentile", 0.80)) if args is not None else 0.80,
    }
    grouped = group_by(control_summary, ("shuffle_kind",))
    rows: list[dict[str, object]] = []
    for family, threshold in thresholds.items():
        items = grouped.get((family,), [])
        percentiles = [float_or_zero(row.get("observed_percentile_vs_shuffle")) for row in items if row.get("observed_percentile_vs_shuffle") != ""]
        pass_count = sum(1 for value in percentiles if value >= threshold)
        pass_fraction = pass_count / max(1, len(percentiles))
        median_percentile = median(percentiles) if percentiles else 0.0
        min_percentile = min(percentiles) if percentiles else 0.0
        catastrophic_floor = float(getattr(args, "shuffle_family_catastrophic_min_percentile", 0.50)) if args is not None else 0.50
        catastrophic_count = sum(1 for value in percentiles if value < catastrophic_floor)
        min_pass_fraction = float(getattr(args, "shuffle_family_min_pass_fraction", 0.50)) if args is not None else 0.50
        min_median = float(getattr(args, "shuffle_family_min_median_percentile", threshold)) if args is not None else threshold
        family_passed = bool(percentiles) and pass_fraction >= min_pass_fraction and median_percentile >= min_median and catastrophic_count == 0
        rows.append({
            "shuffle_family": family,
            "shuffle_control_category": shuffle_control_category(family),
            "family_required_for_control_gate": int(shuffle_family_required(family)),
            "threshold": threshold,
            "replicate_count": sum(int(float_or_zero(row.get("replicate_count"))) for row in items),
            "primary_context_count": len(percentiles),
            "passed_context_count": pass_count,
            "pass_fraction": pass_fraction,
            "median_observed_percentile": median_percentile,
            "min_observed_percentile": min_percentile,
            "catastrophic_floor": catastrophic_floor,
            "catastrophic_fail_count": catastrophic_count,
            "catastrophic_fail_flag": int(catastrophic_count > 0),
            "family_passed": int(family_passed),
            "blocking_reason": "" if family_passed else shuffle_family_blocker(percentiles, pass_fraction, median_percentile, catastrophic_count, min_pass_fraction, min_median),
        })
    return rows


def shuffle_family_threshold(family: str, args: argparse.Namespace | None = None) -> float:
    if family == "label_shuffle":
        return float(getattr(args, "label_shuffle_min_percentile", 0.80)) if args is not None else 0.80
    if family == "context_shuffle":
        return float(getattr(args, "context_shuffle_min_percentile", 0.80)) if args is not None else 0.80
    if family == "horizon_order_shuffle":
        return float(getattr(args, "horizon_shuffle_min_percentile", 0.80)) if args is not None else 0.80
    return 0.80


def shuffle_control_category(family: str) -> str:
    if family == "label_shuffle":
        return "label_interpretation_control"
    if family == "random_subspace_baseline":
        return "random_subspace_control"
    return "structure_destroying_control"


def shuffle_family_required(family: str) -> bool:
    return shuffle_control_category(family) == "structure_destroying_control"


def shuffle_family_blocker(
    percentiles: list[float],
    pass_fraction: float,
    median_percentile: float,
    catastrophic_count: int,
    min_pass_fraction: float,
    min_median: float,
) -> str:
    if not percentiles:
        return "no_primary_contexts"
    if catastrophic_count:
        return "primary_context_below_catastrophic_floor"
    if pass_fraction < min_pass_fraction:
        return "pass_fraction_below_threshold"
    if median_percentile < min_median:
        return "median_percentile_below_threshold"
    return "family_failed"


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
        f"Failure reason: `{row.get('ablation_failure_reason', '')}`.",
        f"High-loading delta: `{float_or_zero(row.get('high_loading_delta', row.get('high_loading_drop_fraction_mean'))):.4f}`.",
        f"Random mean/std/max: `{float_or_zero(row.get('random_delta_mean', row.get('matched_random_drop_fraction_mean'))):.4f}` / `{float_or_zero(row.get('random_delta_std')):.4f}` / `{float_or_zero(row.get('random_delta_max')):.4f}`.",
        f"Low-loading delta: `{float_or_zero(row.get('low_loading_delta')):.4f}`.",
        f"Metric specificity wins: `{row.get('metric_specificity_wins', '')}`.",
        f"Matching quality: `{float_or_zero(row.get('matching_quality')):.3f}`.",
        f"Coverage loss after ablation: `{float_or_zero(row.get('coverage_loss_after_ablation')):.3f}`.",
        f"Subspace/item read: `{row.get('subspace_item_read', '')}`.",
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
        "## Readiness Levels",
        "",
        f"Decision classes: `{status.get('decision_classes')}`.",
        f"Larger spectral controls ready: `{status.get('ready_for_larger_spectral_control_run')}`.",
        f"Larger analysis-only channel diagnostics ready: `{status.get('ready_for_larger_analysis_only_channel_run')}`.",
        f"Tiny graph-channel perturbation ready: `{status.get('ready_for_tiny_graph_channel_perturbation')}`.",
        f"Larger graph-channel run ready: `{status.get('ready_for_larger_graph_channel_run')}`.",
        "",
        "## Blockers / Repairs Required",
        "",
    ]
    if int(status.get("ready_for_larger_graph_channel_run", 0)):
        lines.append("No graph-channel prep blocker was detected by this smoke. Treat this as readiness for a larger exploratory run, not as a positive theory result.")
    else:
        lines.append("The larger graph-channel run remains blocked until the failed prep stage is repaired and reviewed.")
        if status.get("item_ablation_status") != "high_loading_ablation_specific":
            lines.append(f"Primary ablation blocker: `{status.get('ablation_failure_reason')}`.")
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
        f"Ablation failure reason: `{ablation_decision[0].get('ablation_failure_reason', '') if ablation_decision else ''}`.",
        f"Subspace/item read: `{ablation_decision[0].get('subspace_item_read', '') if ablation_decision else ''}`.",
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
