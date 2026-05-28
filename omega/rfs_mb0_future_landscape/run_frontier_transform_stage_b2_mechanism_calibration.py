from __future__ import annotations

import argparse
import csv
import json
import pickle
import queue
import random
import signal
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import replace
from itertools import combinations
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from .mechanism_controls import (
    asymmetry_flip_sweep_control,
    constraint_resampled_generation_control,
    roughness_resampled_transform_control,
    substrate_preservation_audit,
)
from .relation_generator import RelationParams, generate_relation_system
from .run_deformation_detector_sweep import params_from_parameter_set_id, stable_seed
from .run_focused_boundary_recurrence import apply_variant, float_or_zero, read_csv, write_csv
from .run_frontier_transform_b0 import rows_for_starts
from .run_frontier_transform_syndrome_audit import (
    component_contexts,
    component_score_row,
    control_equivalence_read,
    control_context_key,
    joint_rate,
    marginal_preserving_syndrome_controls,
    percentile,
    percentile_from_sorted,
    stable_context_seed,
    syndrome_component_ablation,
    syndrome_library,
    syndrome_stage_a_decision,
    syndrome_vs_controls,
)
from .run_instrumentation_phase_a import build_holdout_split
from .run_path_metric_calibration import build_probe


BASELINE_CONTROL = "baseline_unperturbed"
PRIMARY_SYNDROMES = (
    "SYN_A_low_growth_high_bottleneck_low_offdiag",
    "SYN_C_low_growth_high_concentration_low_entropy",
)
SECONDARY_SYNDROMES = (
    "SYN_B_high_turnover_high_offdiag_high_window_delta",
    "SYN_D_high_turnover_high_entropy_low_bottleneck_control",
)
DIAGNOSTIC_PROBES = {"existing_low", "full_state_hash"}
STOP_REQUESTED = False

OUTPUTS = (
    "stage_b2_run_config.json",
    "stage_b2_job_manifest.csv",
    "stage_b2_progress_checkpoints.csv",
    "stage_b2_control_identity_audit.csv",
    "stage_b2_mechanism_control_system_manifest.csv",
    "stage_b2_substrate_preservation.csv",
    "stage_b2_metric_rows.csv",
    "stage_b2_metric_rows_audit_sample.csv",
    "stage_b2_component_scores.csv",
    "stage_b2_component_scores_audit_sample.csv",
    "stage_b2_syndrome_rates.csv",
    "stage_b2_dependency_scores.csv",
    "stage_b2_decision_summary.csv",
    "stage_b2_entropy_view_summary.csv",
    "stage_b2_flow_view_summary.csv",
    "stage_b2_horizon_view_summary.csv",
    "stage_b2_entropy_flow_horizon_overlay.csv",
    "stage_b2_corridor_trap_fakeout_summary.csv",
    "rfs_mb0_stage_b2_mechanism_calibration_and_gauge_overlay_report.md",
    "errors.csv",
    "status.json",
    "output_manifest.json",
)

METRIC_ROW_FIELDS = (
    "job_id",
    "row_kind",
    "preflight_context",
    "group_id",
    "seed",
    "fresh_seed_index",
    "start_index",
    "start_samples",
    "probe_key",
    "probe_group",
    "flow_mode",
    "window",
    "H_a",
    "H_b",
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
    "baseline_system_id",
    "control_system_id",
    "fa_state_count",
    "fb_state_count",
    "frontier_size_a",
    "frontier_size_b",
    "support_size_a",
    "support_size_b",
    "frontier_growth_ratio",
    "frontier_growth_delta",
    "support_turnover_rate",
    "support_persistence_rate",
    "new_signature_rate",
    "lost_signature_rate",
    "transition_matrix_entropy",
    "row_entropy_mean",
    "column_entropy_mean",
    "transition_matrix_sparsity",
    "transition_matrix_rank_proxy",
    "diagonal_persistence_mass",
    "off_diagonal_transform_mass",
    "frontier_bottleneck_index",
    "max_signature_flow_fraction",
    "top_k_flow_concentration",
    "window_metric_vector_l2_distance_to_previous",
    "window_metric_vector_l2_distance_to_next",
    "transition_matrix_js_to_previous_window",
    "transition_matrix_js_to_next_window",
    "signature_distribution_js_to_previous_window",
    "signature_distribution_js_to_next_window",
    "states_with_window_target",
    "states_without_window_target",
    "no_window_target_rate",
    "edge_count_total_from_fa",
    "edge_count_into_fb",
    "edge_into_fb_rate",
    "skipped_state_count",
)

COMPONENT_ROW_FIELDS = (
    "syndrome_id",
    "syndrome_component_id",
    "syndrome_selection_mode",
    "metric_family",
    "metric_name",
    "window",
    "H_a",
    "H_b",
    "flow_mode",
    "probe_key",
    "direction",
    "group_id",
    "seed",
    "fresh_seed_index",
    "start_index",
    "start_samples",
    "mechanism_condition",
    "mechanism_control_name",
    "mechanism_control_strength",
    "mechanism_strength_label",
    "condition_id",
    "intended_control_name",
    "actual_control_name",
    "control_family",
    "control_variant",
    "proxy_level",
    "allowed_interpretation_level",
    "baseline_system_id",
    "control_system_id",
    "component_status",
    "component_threshold",
    "observed_value",
    "control_mean",
    "control_std",
    "signed_z",
    "control_percentile",
    "component_pass",
    "control_count",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 Stage B-2 mechanism calibration and gauge-view overlay.")
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--corrected", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/corrected_group_classification.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--phase-b-dir", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_phase_b_regenerated_full_controls"))
    parser.add_argument("--stage-a-dir", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_desktop_frontier_transform_stage_a_regenerated_full_controls"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_stage_b2_mechanism_calibration_smoke"))
    parser.add_argument("--groups", type=int, default=20)
    parser.add_argument("--design-groups", type=int, default=1)
    parser.add_argument("--fresh-seeds-per-group", type=int, default=1)
    parser.add_argument("--start-samples-list", type=str, default="4")
    parser.add_argument("--probes", type=str, default="constraint_profile_hash,constraint_violation_count_plus_local_tuple")
    parser.add_argument("--primary-syndromes", type=str, default=",".join(PRIMARY_SYNDROMES))
    parser.add_argument("--include-secondary-syndromes", action="store_true")
    parser.add_argument("--roughness-seed-replicates", type=int, default=1)
    parser.add_argument("--small-edge-resample-strengths", type=str, default="0.001,0.0025,0.005,0.01")
    parser.add_argument("--asymmetry-multipliers", type=str, default="0.5,1.5")
    parser.add_argument("--asymmetric-edge-flip-strengths", type=str, default="0.005,0.01,0.02")
    parser.add_argument("--constraint-proxy-strengths", type=str, default="0.0025")
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--job-batch-size", type=int, default=4)
    parser.add_argument("--checkpoint-every-jobs", type=int, default=60)
    parser.add_argument("--max-runtime-seconds", type=int, default=1800)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=120)
    parser.add_argument("--component-z-threshold", type=float, default=0.5)
    parser.add_argument("--marginal-control-replicates", type=int, default=100)
    parser.add_argument("--marginal-control-seed", type=int, default=20260528)
    parser.add_argument("--output-profile", choices=("compact", "debug"), default="compact")
    parser.add_argument("--metric-output-mode", choices=("full", "audit_sample", "none"), default="full")
    parser.add_argument("--metric-audit-sample-rate", type=float, default=0.02)
    parser.add_argument("--metric-audit-sample-cap", type=int, default=50000)
    parser.add_argument("--component-output-mode", choices=("full", "audit_sample", "none"), default="audit_sample")
    parser.add_argument("--component-audit-sample-rate", type=float, default=0.02)
    parser.add_argument("--component-audit-sample-cap", type=int, default=50000)
    parser.add_argument("--marginal-output-mode", choices=("full", "summary"), default="summary")
    parser.add_argument("--control-summary-cache-mode", choices=("auto", "rebuild", "off"), default="auto")
    parser.add_argument("--control-summary-cache", type=Path, default=None)
    parser.add_argument("--track-frontier-preservation-metrics", action="store_true")
    parser.add_argument("--track-saturation-timing", action="store_true")
    return parser.parse_args()


def main() -> None:
    install_signal_handlers()
    args = parse_args()
    started = time.perf_counter()
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    args.out.mkdir(parents=True, exist_ok=True)
    selected_syndromes = selected_syndrome_ids(args)
    selected_components = [component for component in syndrome_library() if str(component["syndrome_id"]) in set(selected_syndromes)]
    control_summaries, control_source, control_summary_rows, control_summary_cache_status = load_control_summaries(
        args.phase_b_dir,
        selected_components,
        args.control_summary_cache_mode,
        args.control_summary_cache,
    )
    control_summary_load_seconds = round(time.perf_counter() - started, 3)
    groups, split_rows = build_holdout_split(args)
    anchors = {row.get("anchor_id", ""): row for row in read_csv(args.source_run / "atlas_band_selection.csv")}
    probes = tuple(item.strip() for item in args.probes.split(",") if item.strip())
    start_samples = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    jobs = build_jobs(args, groups, split_rows, anchors, probes, start_samples)
    status: dict[str, object] = {
        "status": "RUNNING",
        "phase": "rfs_mb0_stage_b2_mechanism_calibration_and_gauge_overlay",
        "started_utc": started_utc,
        "phase_b_dir": str(args.phase_b_dir),
        "stage_a_dir": str(args.stage_a_dir),
        "out_dir": str(args.out),
        "workers": args.workers,
        "job_batch_size": args.job_batch_size,
        "jobs_requested": len(jobs),
        "jobs_submitted": 0,
        "jobs_completed": 0,
        "jobs_cancelled": 0,
        "pending_jobs_remaining": len(jobs),
        "max_runtime_seconds": args.max_runtime_seconds,
        "shutdown_cushion_seconds": args.shutdown_cushion_seconds,
        "selected_syndrome_ids": selected_syndromes,
        "control_source": control_source,
        "control_summary_contexts": control_summary_rows,
        "control_summary_load_seconds": control_summary_load_seconds,
        "control_summary_cache_status": control_summary_cache_status,
        "new_systems_generated": 0,
        "holdout_scoring_count": 0,
        "n6_run_count": 0,
        "alphabet_expansion_count": 0,
        "promotion_enabled": False,
        "candidate_promotion_enabled": False,
        "candidate_detection_enabled": False,
        "holdout_detection_enabled": False,
        "output_profile": args.output_profile,
        "metric_output_mode": args.metric_output_mode,
        "metric_audit_sample_rate": args.metric_audit_sample_rate,
        "metric_audit_sample_cap": args.metric_audit_sample_cap,
        "component_output_mode": args.component_output_mode,
        "component_audit_sample_rate": args.component_audit_sample_rate,
        "component_audit_sample_cap": args.component_audit_sample_cap,
        "marginal_output_mode": args.marginal_output_mode,
        "track_frontier_preservation_metrics": bool(args.track_frontier_preservation_metrics),
        "track_saturation_timing": bool(args.track_saturation_timing),
        "streaming_writer_enabled": True,
    }
    write_csv(args.out / "stage_b2_job_manifest.csv", job_manifest_rows(jobs))
    (args.out / "stage_b2_run_config.json").write_text(json.dumps({**vars(args), "selected_syndrome_ids": selected_syndromes}, indent=2, sort_keys=True, default=str), encoding="utf-8")
    writer_fields: dict[str, tuple[str, ...]] = {}
    if args.metric_output_mode == "full":
        writer_fields["stage_b2_metric_rows.csv"] = METRIC_ROW_FIELDS
    elif args.metric_output_mode == "audit_sample":
        writer_fields["stage_b2_metric_rows_audit_sample.csv"] = METRIC_ROW_FIELDS
    if args.component_output_mode == "full":
        writer_fields["stage_b2_component_scores.csv"] = COMPONENT_ROW_FIELDS
    elif args.component_output_mode == "audit_sample":
        writer_fields["stage_b2_component_scores_audit_sample.csv"] = COMPONENT_ROW_FIELDS
    writer = StreamingCsvWriter(
        args.out,
        writer_fields,
    )
    writer.start()
    metric_stats = MetricStatsAccumulator(
        track_frontier_preservation=args.track_frontier_preservation_metrics,
        track_saturation_timing=args.track_saturation_timing,
    )
    component_stats = ComponentStatsAccumulator(selected_components)
    try:
        metric_rows, manifests, preservation, errors, checkpoints = run_batches(
            args,
            jobs,
            status,
            started,
            writer,
            metric_stats,
            component_stats,
            control_summaries,
            selected_components,
        )
    finally:
        writer.close()
    preservation = metric_stats.add_frontier_preservation_metrics(preservation)
    identity = control_identity_audit(manifests, preservation)
    syndrome_rates = component_stats.syndrome_rate_rows(selected_syndromes)
    dependency = dependency_score_rows(syndrome_rates, preservation, selected_syndromes, identity)
    decision = decision_summary_rows(dependency, selected_syndromes)
    entropy = metric_stats.entropy_view_summary()
    flow = metric_stats.flow_view_summary()
    horizon = metric_stats.horizon_view_summary()
    overlay = entropy_flow_horizon_overlay(entropy, flow, horizon)
    corridor = corridor_trap_fakeout_summary(decision, dependency, overlay)
    marginal = component_stats.marginal_preserving_syndrome_controls(max(20, args.marginal_control_replicates), args.marginal_control_seed, args.marginal_output_mode)
    ablation = component_stats.syndrome_component_ablation(marginal)
    vs_controls = component_stats.syndrome_vs_controls(marginal, ablation)
    if status["status"] == "RUNNING":
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "all_jobs_completed"
    status["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    status["metric_rows"] = metric_stats.total_rows
    status["control_rows"] = 0
    status["metric_rows_retained_in_memory"] = len(metric_rows)
    status["metric_audit_sample_rows"] = metric_stats.audit_sample_rows
    status["component_score_rows"] = component_stats.total_rows
    status["component_audit_sample_rows"] = component_stats.audit_sample_rows
    status["mechanism_control_systems_generated"] = sum(1 for row in manifests if row.get("actual_control_name") != BASELINE_CONTROL)
    status["syndrome_rate_rows"] = len(syndrome_rates)
    status["dependency_score_rows"] = len(dependency)
    status["decision_rows"] = len(decision)
    status["errors"] = len(errors)
    status["marginal_control_replicates"] = max(20, args.marginal_control_replicates)
    status["marginal_preserving_control_rows"] = len(marginal)
    write_final_outputs(args.out, status, checkpoints, identity, manifests, preservation, syndrome_rates, dependency, decision, entropy, flow, horizon, overlay, corridor, marginal, ablation, vs_controls, errors)


def install_signal_handlers() -> None:
    def request_stop(_signum: int, _frame: object) -> None:
        global STOP_REQUESTED
        STOP_REQUESTED = True

    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        signum = getattr(signal, name, None)
        if signum is not None:
            signal.signal(signum, request_stop)


class StreamingCsvWriter:
    def __init__(self, out_dir: Path, fields_by_name: dict[str, tuple[str, ...]]) -> None:
        self.out_dir = out_dir
        self.fields_by_name = fields_by_name
        self.queue: queue.Queue[tuple[str, list[dict[str, object]]] | None] = queue.Queue(maxsize=32)
        self.thread = threading.Thread(target=self._run, name="stage-b2-csv-writer", daemon=True)
        self.handles: dict[str, Any] = {}
        self.writers: dict[str, csv.DictWriter[str]] = {}
        self.error: BaseException | None = None

    def start(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        for name, fields in self.fields_by_name.items():
            handle = (self.out_dir / name).open("w", newline="", encoding="utf-8", buffering=1024 * 1024)
            writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
            writer.writeheader()
            self.handles[name] = handle
            self.writers[name] = writer
        self.thread.start()

    def write(self, name: str, rows: list[dict[str, object]]) -> None:
        if rows:
            self.queue.put((name, rows))

    def close(self) -> None:
        self.queue.put(None)
        self.thread.join()
        for handle in self.handles.values():
            handle.close()
        if self.error:
            raise self.error

    def _run(self) -> None:
        try:
            while True:
                item = self.queue.get()
                if item is None:
                    return
                name, rows = item
                writer = self.writers[name]
                writer.writerows(rows)
        except BaseException as exc:  # noqa: BLE001
            self.error = exc


class MetricStatsAccumulator:
    def __init__(self, track_frontier_preservation: bool = False, track_saturation_timing: bool = False) -> None:
        self.track_frontier_preservation = track_frontier_preservation
        self.track_saturation_timing = track_saturation_timing
        self.total_rows = 0
        self.audit_sample_rows = 0
        self.entropy_groups: dict[tuple[object, ...], dict[str, list[float]]] = defaultdict(metric_bucket)
        self.flow_groups: dict[tuple[object, ...], dict[str, list[float]]] = defaultdict(metric_bucket)
        self.horizon_groups: dict[tuple[object, ...], dict[str, list[float]]] = defaultdict(metric_bucket)
        self.baseline_rows: dict[tuple[object, ...], dict[str, object]] = {}
        self.pending_control_rows: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
        self.frontier_delta_sums: dict[object, list[float]] = defaultdict(lambda: [0.0, 0.0])
        self.support_delta_sums: dict[object, list[float]] = defaultdict(lambda: [0.0, 0.0])
        self.growth_by_context: dict[tuple[object, ...], list[tuple[int, float]]] = defaultdict(list)

    def add_rows(self, rows: list[dict[str, object]]) -> None:
        for row in rows:
            self.total_rows += 1
            band = horizon_band(row)
            entropy_key = tuple(row.get(field, "") for field in ("condition_id", "actual_control_name", "proxy_level", "probe_key", "flow_mode")) + (band,)
            flow_key = entropy_key
            horizon_key = tuple(row.get(field, "") for field in ("condition_id", "actual_control_name", "proxy_level")) + (band,)
            update_metric_bucket(self.entropy_groups[entropy_key], row, ("transition_matrix_entropy", "row_entropy_mean", "column_entropy_mean"))
            update_metric_bucket(self.flow_groups[flow_key], row, ("frontier_bottleneck_index", "top_k_flow_concentration", "off_diagonal_transform_mass", "edge_into_fb_rate", "states_without_window_target"))
            update_metric_bucket(self.horizon_groups[horizon_key], row, ("frontier_growth_ratio", "frontier_bottleneck_index", "transition_matrix_entropy", "support_turnover_rate"))
            self._add_preservation_row(row)

    def _add_preservation_row(self, row: dict[str, object]) -> None:
        if not self.track_frontier_preservation and not self.track_saturation_timing:
            return
        key = baseline_key(row)
        growth_context = (
            row.get("condition_id"),
            row.get("group_id"),
            row.get("seed"),
            row.get("probe_key"),
            row.get("start_samples"),
            row.get("start_index"),
            row.get("flow_mode"),
        )
        if self.track_saturation_timing:
            self.growth_by_context[growth_context].append((int(float_or_zero(row.get("H_a"))), float_or_zero(row.get("frontier_growth_ratio"))))
        if not self.track_frontier_preservation:
            return
        if row.get("actual_control_name") == BASELINE_CONTROL:
            self.baseline_rows[key] = row
            pending = self.pending_control_rows.pop(key, [])
            for control_row in pending:
                self._record_preservation_delta(row, control_row)
            return
        baseline = self.baseline_rows.get(key)
        if baseline is None:
            self.pending_control_rows[key].append(row)
            return
        self._record_preservation_delta(baseline, row)

    def _record_preservation_delta(self, baseline: dict[str, object], row: dict[str, object]) -> None:
        condition_id = row.get("condition_id", "")
        frontier_delta = abs(float_or_zero(row.get("frontier_size_b")) - float_or_zero(baseline.get("frontier_size_b"))) / max(1.0, float_or_zero(baseline.get("frontier_size_b")))
        support_delta = abs(float_or_zero(row.get("frontier_growth_ratio")) - float_or_zero(baseline.get("frontier_growth_ratio")))
        self.frontier_delta_sums[condition_id][0] += frontier_delta
        self.frontier_delta_sums[condition_id][1] += 1.0
        self.support_delta_sums[condition_id][0] += support_delta
        self.support_delta_sums[condition_id][1] += 1.0

    def add_frontier_preservation_metrics(self, preservation: list[dict[str, object]]) -> list[dict[str, object]]:
        for audit in preservation:
            condition_id = audit.get("condition_id", "")
            frontier_sum, frontier_count = self.frontier_delta_sums.get(condition_id, [0.0, 0.0])
            support_sum, support_count = self.support_delta_sums.get(condition_id, [0.0, 0.0])
            audit["frontier_size_profile_delta"] = frontier_sum / frontier_count if frontier_count else 0.0
            audit["support_growth_baseline_delta"] = support_sum / support_count if support_count else 0.0
            audit["saturation_timing_delta"] = self._saturation_timing_delta(condition_id)
            audit["control_destructiveness_score"] = max(float_or_zero(audit.get("control_destructiveness_score")), min(1.0, float_or_zero(audit["frontier_size_profile_delta"])))
            audit["control_too_destructive_flag"] = int(float_or_zero(audit.get("control_destructiveness_score")) > 0.50)
            audit["destructiveness_band"] = destructiveness_band(float_or_zero(audit.get("control_destructiveness_score")))
        return preservation

    def _saturation_timing_delta(self, condition_id: object) -> float:
        if not self.track_saturation_timing:
            return 0.0
        deltas = []
        suffix_to_baseline = {
            key[1:]: first_stable_window_from_pairs(values)
            for key, values in self.growth_by_context.items()
            if key[0] == f"{BASELINE_CONTROL}:baseline"
        }
        for key, values in self.growth_by_context.items():
            if key[0] != condition_id:
                continue
            baseline = suffix_to_baseline.get(key[1:])
            if baseline is None:
                continue
            deltas.append(abs(first_stable_window_from_pairs(values) - baseline))
        return mean(deltas) if deltas else 0.0

    def entropy_view_summary(self) -> list[dict[str, object]]:
        return view_rows(
            self.entropy_groups,
            ("condition_id", "actual_control_name", "proxy_level", "probe_key", "flow_mode", "horizon_band"),
            ("transition_matrix_entropy", "row_entropy_mean", "column_entropy_mean"),
        )

    def flow_view_summary(self) -> list[dict[str, object]]:
        return view_rows(
            self.flow_groups,
            ("condition_id", "actual_control_name", "proxy_level", "probe_key", "flow_mode", "horizon_band"),
            ("frontier_bottleneck_index", "top_k_flow_concentration", "off_diagonal_transform_mass", "edge_into_fb_rate", "states_without_window_target"),
        )

    def horizon_view_summary(self) -> list[dict[str, object]]:
        return view_rows(
            self.horizon_groups,
            ("condition_id", "actual_control_name", "proxy_level", "horizon_band"),
            ("frontier_growth_ratio", "frontier_bottleneck_index", "transition_matrix_entropy", "support_turnover_rate"),
        )


class ComponentStatsAccumulator:
    def __init__(self, components: list[dict[str, object]]) -> None:
        self.total_rows = 0
        self.audit_sample_rows = 0
        self.library_components = {
            syndrome_id: [str(row["syndrome_component_id"]) for row in sorted(items, key=lambda item: str(item["syndrome_component_id"]))]
            for (syndrome_id,), items in group_by(components, ("syndrome_id",)).items()
        }
        self.units: dict[tuple[object, ...], dict[tuple[object, ...], dict[str, int]]] = defaultdict(lambda: defaultdict(dict))
        self.context_counts: dict[tuple[object, ...], list[float]] = defaultdict(lambda: [0.0, 0.0])
        self.component_stats: dict[tuple[object, ...], dict[str, list[float]]] = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0, 0.0]))

    def add_rows(self, rows: list[dict[str, object]]) -> None:
        unit_components: dict[tuple[tuple[object, ...], tuple[object, ...]], dict[str, int]] = defaultdict(dict)
        for row in rows:
            self.total_rows += 1
            if row.get("component_status") != "scored":
                continue
            context_key = component_context_key_with_condition(row)
            unit_key = (
                row.get("group_id"),
                row.get("seed"),
                row.get("fresh_seed_index"),
                row.get("start_index"),
                row.get("start_samples"),
                row.get("window"),
            )
            component_id = str(row.get("syndrome_component_id"))
            passed = int(float_or_zero(row.get("component_pass")))
            unit_components[(context_key, unit_key)][component_id] = passed
            stats = self.component_stats[context_key][component_id]
            stats[0] += 1.0
            stats[1] += passed
            stats[2] += float_or_zero(row.get("signed_z"))
        for (context_key, _unit_key), unit in unit_components.items():
            syndrome_id = str(component_context_fields_from_key(context_key)["syndrome_id"])
            expected = self.library_components.get(syndrome_id, [])
            if expected and all(component_id in unit for component_id in expected):
                self.context_counts[context_key][0] += 1.0
                self.context_counts[context_key][1] += int(all(unit[component_id] for component_id in expected))

    def contexts(self) -> list[dict[str, object]]:
        out = []
        for context_key, counts in self.context_counts.items():
            context_fields = component_context_fields_from_key(context_key)
            expected = self.library_components.get(str(context_fields["syndrome_id"]), [])
            complete_count, joint_count = counts
            if complete_count <= 0 or not expected:
                continue
            component_rates = {}
            for component_id in expected:
                stats = self.component_stats[context_key].get(component_id, [0.0, 0.0, 0.0])
                component_rates[component_id] = stats[1] / stats[0] if stats[0] else 0.0
            out.append({
                **context_fields,
                "component_vectors": {},
                "component_marginal_rates": component_rates,
                "observed_joint_rate": joint_count / complete_count,
                "complete_unit_count": int(complete_count),
            })
        return out


def metric_bucket() -> dict[str, list[float]]:
    return defaultdict(lambda: [0.0, 0.0])  # type: ignore[return-value]


def update_metric_bucket(bucket: dict[str, list[float]], row: dict[str, object], metrics: tuple[str, ...]) -> None:
    for metric in metrics:
        if row.get(metric, "") == "":
            continue
        bucket[metric][0] += float_or_zero(row.get(metric))
        bucket[metric][1] += 1.0


def view_rows(groups: dict[tuple[object, ...], dict[str, list[float]]], keys: tuple[str, ...], metrics: tuple[str, ...]) -> list[dict[str, object]]:
    out = []
    for key, bucket in groups.items():
        row = {field: value for field, value in zip(keys, key)}
        row["rows"] = int(max((values[1] for values in bucket.values()), default=0.0))
        for metric in metrics:
            total, count = bucket.get(metric, [0.0, 0.0])
            row[f"{metric}_mean"] = total / count if count else ""
        out.append(row)
    return out


def first_stable_window_from_pairs(values: list[tuple[int, float]]) -> int:
    ordered = sorted(values, key=lambda item: item[0])
    for index, (_window, growth) in enumerate(ordered):
        if growth <= 1.05:
            return index
    return len(ordered)


def product(values: object) -> float:
    result = 1.0
    seen = False
    for value in values:  # type: ignore[assignment]
        seen = True
        result *= float_or_zero(value)
    return result if seen else 0.0


COMPONENT_CONTEXT_KEYS = (
    "condition_id",
    "mechanism_condition",
    "mechanism_control_name",
    "mechanism_control_strength",
    "mechanism_strength_label",
    "actual_control_name",
    "proxy_level",
    "allowed_interpretation_level",
    "syndrome_id",
    "probe_key",
    "flow_mode",
)


def component_context_key_with_condition(row: dict[str, object]) -> tuple[object, ...]:
    return tuple(row.get(field, "") for field in COMPONENT_CONTEXT_KEYS)


def component_context_key_from_fields(row: dict[str, object]) -> tuple[object, ...]:
    return tuple(row.get(field, "") for field in COMPONENT_CONTEXT_KEYS)


def component_context_fields_from_key(key: tuple[object, ...]) -> dict[str, object]:
    return {field: value for field, value in zip(COMPONENT_CONTEXT_KEYS, key)}


def context_summary_key(context: dict[str, object]) -> tuple[str, str, str, str]:
    return (
        str(context.get("condition_id", "")),
        str(context.get("syndrome_id", "")),
        str(context.get("probe_key", "")),
        str(context.get("flow_mode", "")),
    )


def marginal_control_summary_by_condition(rows: list[dict[str, object]]) -> dict[tuple[str, str, str, str], dict[str, object]]:
    out: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for key, items in group_by(rows, ("condition_id", "syndrome_id", "probe_key", "flow_mode")).items():
        if items and items[0].get("marginal_output_mode") == "summary":
            first = items[0]
            out[(str(key[0]), str(key[1]), str(key[2]), str(key[3]))] = {
                "observed_joint_rate": float_or_zero(first.get("observed_joint_rate")),
                "control_joint_rate_mean": float_or_zero(first.get("control_joint_rate_mean")),
                "joint_rate_excess": float_or_zero(first.get("joint_rate_excess")),
                "joint_rate_percentile": float_or_zero(first.get("joint_rate_percentile")),
                "replicate_count": int(float_or_zero(first.get("replicate_count"))),
                "complete_unit_count": int(float_or_zero(first.get("complete_unit_count"))),
            }
            continue
        controls_by_replicate = {
            int(float_or_zero(item.get("replicate_id"))): float_or_zero(item.get("control_joint_rate"))
            for item in items
        }
        controls = list(controls_by_replicate.values())
        first = items[0] if items else {}
        out[(str(key[0]), str(key[1]), str(key[2]), str(key[3]))] = {
            "observed_joint_rate": float_or_zero(first.get("observed_joint_rate")),
            "control_joint_rate_mean": mean(controls) if controls else 0.0,
            "joint_rate_excess": float_or_zero(first.get("observed_joint_rate")) - (mean(controls) if controls else 0.0),
            "joint_rate_percentile": float_or_zero(first.get("joint_rate_percentile")),
            "replicate_count": int(float_or_zero(first.get("replicate_count"))),
            "complete_unit_count": int(float_or_zero(first.get("complete_unit_count"))),
        }
    return out


def ablation_by_condition_context(rows: list[dict[str, object]]) -> dict[tuple[str, str, str, str], dict[str, object]]:
    out = {}
    for key, items in group_by(rows, ("condition_id", "syndrome_id", "probe_key", "flow_mode")).items():
        if items:
            out[(str(key[0]), str(key[1]), str(key[2]), str(key[3]))] = dict(items[0])
    return out

def component_stats_syndrome_rate_rows(self: ComponentStatsAccumulator, selected_syndromes: list[str]) -> list[dict[str, object]]:
    selected = set(selected_syndromes)
    out: list[dict[str, object]] = []
    for context in self.contexts():
        if selected and context["syndrome_id"] not in selected:
            continue
        out.append({
            "condition_id": context["condition_id"],
            "mechanism_condition": context["mechanism_condition"],
            "mechanism_control_name": context["mechanism_control_name"],
            "mechanism_control_strength": context["mechanism_control_strength"],
            "mechanism_strength_label": context["mechanism_strength_label"],
            "actual_control_name": context["actual_control_name"],
            "proxy_level": context["proxy_level"],
            "allowed_interpretation_level": context["allowed_interpretation_level"],
            "syndrome_id": context["syndrome_id"],
            "probe_key": context["probe_key"],
            "flow_mode": context["flow_mode"],
            "syndrome_rate": context["observed_joint_rate"],
            "complete_unit_count": context["complete_unit_count"],
            "component_marginal_rates_json": json.dumps(context["component_marginal_rates"], sort_keys=True),
        })
    return out


def component_stats_marginal_preserving_syndrome_controls(self: ComponentStatsAccumulator, replicates: int, seed: int, output_mode: str = "summary") -> list[dict[str, object]]:
    out = []
    for context in self.contexts():
        rng = random.Random(stable_context_seed(seed, f"{context['condition_id']}|{context['syndrome_id']}", context["probe_key"], context["flow_mode"]))
        controls = []
        component_rates = context["component_marginal_rates"]
        component_ids = list(component_rates)
        complete_units = int(float_or_zero(context["complete_unit_count"]))
        for _replicate_id in range(replicates):
            joint_hits = 0
            for _unit_index in range(max(1, complete_units)):
                joint_hits += int(all(rng.random() <= float_or_zero(component_rates[component_id]) for component_id in component_ids))
            controls.append(joint_hits / max(1, complete_units))
        observed = float(context["observed_joint_rate"])
        control_mean = mean(controls) if controls else 0.0
        percentile_value = percentile(observed, controls)
        summary_row = {
            "condition_id": context["condition_id"],
            "actual_control_name": context["actual_control_name"],
            "proxy_level": context["proxy_level"],
            "syndrome_id": context["syndrome_id"],
            "probe_key": context["probe_key"],
            "flow_mode": context["flow_mode"],
            "replicate_id": "",
            "component_id": "",
            "component_marginal_rate": "",
            "observed_joint_rate": observed,
            "control_joint_rate": "",
            "control_joint_rate_mean": control_mean,
            "joint_rate_excess": observed - control_mean,
            "joint_rate_percentile": percentile_value,
            "replicate_count": replicates,
            "complete_unit_count": context["complete_unit_count"],
            "control_family": "component_marginal_rate_preserving_syndrome_control_summary",
            "marginal_output_mode": "summary",
        }
        if output_mode == "summary":
            out.append(summary_row)
            continue
        for replicate_id, control_rate in enumerate(controls):
            for component_id in component_ids:
                out.append({
                    **summary_row,
                    "replicate_id": replicate_id,
                    "component_id": component_id,
                    "component_marginal_rate": context["component_marginal_rates"][component_id],
                    "control_joint_rate": control_rate,
                    "marginal_output_mode": "full",
                })
    return out


def component_stats_syndrome_component_ablation(self: ComponentStatsAccumulator, marginal_controls: list[dict[str, object]]) -> list[dict[str, object]]:
    control_summary = marginal_control_summary_by_condition(marginal_controls)
    out = []
    for context in self.contexts():
        key = context_summary_key(context)
        controls = control_summary.get(key, {})
        component_rates = context["component_marginal_rates"]
        component_ids = list(component_rates)
        full_score = float(context["observed_joint_rate"])
        best_single = max((component_rates[component_id] for component_id in component_ids), default=0.0)
        pair_scores = [product(component_rates[component_id] for component_id in pair) for pair in combinations(component_ids, 2)]
        best_pair = max(pair_scores, default=0.0)
        full_excess = float(controls.get("joint_rate_excess", 0.0) or 0.0)
        single_component_driven = int(full_excess > 0 and best_single >= 0.90 and best_pair <= full_score + 1e-12)
        decision = "single_component_driven_not_joint_syndrome" if single_component_driven else "joint_syndrome_not_single_component_driven"
        for removed in component_ids:
            kept = [component_id for component_id in component_ids if component_id != removed]
            out.append(
                {
                    "condition_id": context["condition_id"],
                    "actual_control_name": context["actual_control_name"],
                    "proxy_level": context["proxy_level"],
                    "syndrome_id": context["syndrome_id"],
                    "probe_key": context["probe_key"],
                    "flow_mode": context["flow_mode"],
                    "ablation_kind": "leave_one_component_out",
                    "component_removed": removed,
                    "component_subset_json": json.dumps(kept),
                    "full_syndrome_score": full_score,
                    "ablated_score": product(component_rates[component_id] for component_id in kept),
                    "best_single_component_score": best_single,
                    "best_pair_score": best_pair,
                    "single_component_explained_fraction": best_single / full_score if full_score > 0 else 0.0,
                    "joint_rate_excess": full_excess,
                    "joint_rate_percentile": controls.get("joint_rate_percentile", ""),
                    "decision_class": decision,
                    "complete_unit_count": context["complete_unit_count"],
                }
            )
    return out


def component_stats_syndrome_vs_controls(self: ComponentStatsAccumulator, marginal_controls: list[dict[str, object]], ablation_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    marginal_summary = marginal_control_summary_by_condition(marginal_controls)
    ablation_summary = ablation_by_condition_context(ablation_rows)
    out = []
    for context in self.contexts():
        key = context_summary_key(context)
        controls = marginal_summary.get(key, {})
        ablation = ablation_summary.get(key, {})
        component_stats = self.component_stats[component_context_key_from_fields(context)]
        total = sum(stats[0] for stats in component_stats.values())
        passed = sum(stats[1] for stats in component_stats.values())
        signed_z_sum = sum(stats[2] for stats in component_stats.values())
        marginal_available = bool(controls)
        observed_joint = float_or_zero(controls.get("observed_joint_rate"))
        control_mean = float_or_zero(controls.get("control_joint_rate_mean"))
        percentile_value = float_or_zero(controls.get("joint_rate_percentile"))
        apparent_joint_positive = marginal_available and observed_joint > control_mean and percentile_value >= 0.80 and str(context["probe_key"]) not in DIAGNOSTIC_PROBES
        out.append({
            "condition_id": context["condition_id"],
            "actual_control_name": context["actual_control_name"],
            "proxy_level": context["proxy_level"],
            "syndrome_id": context["syndrome_id"],
            "probe_key": context["probe_key"],
            "flow_mode": context["flow_mode"],
            "selection_mode": "preregistered",
            "readiness_allowed": int(str(context["probe_key"]) not in DIAGNOSTIC_PROBES),
            "component_rows": int(total),
            "scored_component_rows": int(total),
            "component_pass_rows": int(passed),
            "component_pass_rate": passed / max(1.0, total),
            "mean_signed_z": signed_z_sum / max(1.0, total),
            "observed_joint_rate": observed_joint,
            "component_marginal_preserving_control_mean": control_mean,
            "joint_rate_excess": observed_joint - control_mean,
            "joint_rate_percentile": percentile_value,
            "marginal_control_replicates": controls.get("replicate_count", ""),
            "single_component_ablation_decision": ablation.get("decision_class", ""),
            "control_equivalence_read": control_equivalence_read(apparent_joint_positive, marginal_available),
            "stage_a_decision_class": syndrome_stage_a_decision(apparent_joint_positive, ablation, marginal_available),
        })
    return out


ComponentStatsAccumulator.syndrome_rate_rows = component_stats_syndrome_rate_rows  # type: ignore[method-assign]
ComponentStatsAccumulator.marginal_preserving_syndrome_controls = component_stats_marginal_preserving_syndrome_controls  # type: ignore[method-assign]
ComponentStatsAccumulator.syndrome_component_ablation = component_stats_syndrome_component_ablation  # type: ignore[method-assign]
ComponentStatsAccumulator.syndrome_vs_controls = component_stats_syndrome_vs_controls  # type: ignore[method-assign]


def selected_syndrome_ids(args: argparse.Namespace) -> list[str]:
    selected = [item.strip() for item in args.primary_syndromes.split(",") if item.strip()]
    if args.include_secondary_syndromes:
        selected.extend(SECONDARY_SYNDROMES)
    seen: list[str] = []
    for item in selected:
        if item not in seen:
            seen.append(item)
    return seen


def load_control_summaries(
    phase_b_dir: Path,
    components: list[dict[str, object]],
    cache_mode: str,
    cache_path: Path | None,
) -> tuple[dict[tuple[str, str, str, str], dict[str, object]], str, int, str]:
    candidates = ("phase_b_stage_a_control_values.csv", "phase_b_design_control_rows.csv")
    path = next((phase_b_dir / name for name in candidates if (phase_b_dir / name).exists()), None)
    if path is None:
        return {}, "", 0, "missing_source"
    # Cache all preregistered syndrome metrics so primary-only and primary+secondary
    # runs can share one startup cache across a batched validation block.
    metrics = {str(component["metric_name"]) for component in syndrome_library()}
    metadata = control_summary_cache_metadata(path, metrics)
    resolved_cache = cache_path or (phase_b_dir / "stage_b2_control_summary_cache.pkl")
    if cache_mode != "off" and cache_mode != "rebuild" and resolved_cache.exists():
        try:
            with resolved_cache.open("rb") as handle:
                payload = pickle.load(handle)
            if payload.get("metadata") == metadata:
                summaries = payload.get("summaries", {})
                if isinstance(summaries, dict):
                    return summaries, path.name, len(summaries), f"loaded:{resolved_cache.name}"
        except Exception:
            pass
    raw: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            quality = row.get("control_quality") or row.get("control_status") or "computed"
            if quality in {"placeholder", "not_available"}:
                continue
            if row.get("control_name") == "probe_marginal_window_control":
                continue
            metric = row.get("metric_name", "")
            if metric not in metrics:
                continue
            key = (
                metric,
                row.get("probe_key", ""),
                row.get("flow_mode", ""),
                row.get("true_window", row.get("window", "")),
            )
            raw[key].append(float_or_zero(row.get("control_value")))
    summaries: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for key, values in raw.items():
        sorted_values = sorted(values)
        summaries[key] = {
            "count": len(values),
            "mean": mean(values),
            "std": pstdev(values) if len(values) > 1 else 0.0,
            "sorted_values": sorted_values,
        }
    cache_status = "cache_off" if cache_mode == "off" else "rebuilt"
    if cache_mode != "off":
        try:
            resolved_cache.parent.mkdir(parents=True, exist_ok=True)
            with resolved_cache.open("wb") as handle:
                pickle.dump({"metadata": metadata, "summaries": summaries}, handle, protocol=pickle.HIGHEST_PROTOCOL)
            cache_status = f"rebuilt:{resolved_cache.name}"
        except Exception as exc:  # noqa: BLE001
            cache_status = f"rebuild_failed:{type(exc).__name__}"
    return summaries, path.name, len(summaries), cache_status


def control_summary_cache_metadata(path: Path, metrics: set[str]) -> dict[str, object]:
    stat = path.stat()
    return {
        "source_path": str(path.resolve()),
        "source_size": stat.st_size,
        "source_mtime_ns": stat.st_mtime_ns,
        "metrics": sorted(metrics),
        "schema_version": 1,
    }


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
                        jobs.append(
                            {
                                "job_id": f"stage_b2_{group_index:03d}_{seed_index}_{start_count}_{probe}_{condition_id}",
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
                            }
                        )
    return jobs


def mechanism_conditions(args: argparse.Namespace) -> list[dict[str, object]]:
    conditions = [control_condition(BASELINE_CONTROL, BASELINE_CONTROL, "baseline", 0.0, "baseline")]
    for replicate in range(max(0, args.roughness_seed_replicates)):
        conditions.append(control_condition("roughness_seed_resample_generation_control", "roughness_seed_resample_generation_control", "roughness", float(replicate + 1), f"seed{replicate + 1}"))
    for strength in parse_strengths(args.small_edge_resample_strengths):
        conditions.append(control_condition("small_edge_resample_control", "small_edge_resample_control", "roughness", strength, strength_label(strength), proxy_level="topology_level_proxy", interpretation="topology_sensitivity_only"))
    for multiplier in parse_strengths(args.asymmetry_multipliers):
        conditions.append(control_condition("asymmetry_strength_sweep_control", "asymmetry_strength_sweep_control", "asymmetry", multiplier, f"x{multiplier:g}"))
    for strength in parse_strengths(args.asymmetric_edge_flip_strengths):
        conditions.append(control_condition("asymmetric_edge_flip_control", "asymmetric_edge_flip_control", "asymmetry", strength, strength_label(strength), proxy_level="topology_level_proxy", interpretation="topology_sensitivity_only"))
    for strength in parse_strengths(args.constraint_proxy_strengths):
        conditions.append(control_condition("constraint_resampled_generation_proxy", "constraint_resampled_generation_proxy", "constraint", strength, strength_label(strength), proxy_level="generation_level_proxy", interpretation="mechanism_proxy_interpretation_only"))
    return conditions


def control_condition(
    intended: str,
    actual: str,
    family: str,
    strength: float,
    label: str,
    proxy_level: str = "exact_mechanism_control",
    interpretation: str = "mechanism_specific_interpretation_allowed",
) -> dict[str, object]:
    if actual == BASELINE_CONTROL:
        proxy_level = "not_available"
        interpretation = "not_interpretable"
    return {
        "mechanism_condition": "baseline" if actual == BASELINE_CONTROL else "mechanism_control",
        "mechanism_control_name": actual,
        "actual_control_name": actual,
        "intended_control_name": intended,
        "control_family": family,
        "control_variant": label,
        "mechanism_control_strength": strength,
        "mechanism_strength_label": label,
        "proxy_level": proxy_level,
        "intended_mechanism": intended_mechanism(intended),
        "actual_intervention": actual_intervention(actual),
        "preserved_fields_json": preserved_fields(actual),
        "changed_fields_json": changed_fields(actual),
        "unpreserved_fields_json": "[]",
        "preservation_failure_reason": "",
        "allowed_interpretation_level": interpretation,
    }


def intended_mechanism(name: str) -> str:
    return {
        BASELINE_CONTROL: "baseline reference",
        "roughness_seed_resample_generation_control": "generator roughness path",
        "small_edge_resample_control": "realized topology roughening",
        "asymmetry_strength_sweep_control": "generator asymmetry strength",
        "asymmetric_edge_flip_control": "realized asymmetric edge orientation",
        "constraint_resampled_generation_proxy": "broad constraint generation proxy",
    }.get(name, name)


def actual_intervention(name: str) -> str:
    return {
        BASELINE_CONTROL: "no intervention",
        "roughness_seed_resample_generation_control": "regenerate with same parameters and alternate roughness_seed",
        "small_edge_resample_control": "post-hoc out-degree-preserving edge target resampling",
        "asymmetry_strength_sweep_control": "regenerate with asymmetry_strength multiplied by control strength",
        "asymmetric_edge_flip_control": "post-hoc reversal of a fraction of asymmetric realized edges",
        "constraint_resampled_generation_proxy": "regenerate using constraint_shuffled null_kind proxy",
    }.get(name, name)


def preserved_fields(name: str) -> str:
    values = {
        BASELINE_CONTROL: ["all"],
        "roughness_seed_resample_generation_control": ["RelationParams", "constraints", "bias_weights", "candidate_successor_construction"],
        "small_edge_resample_control": ["state_set", "out_degree_sequence"],
        "asymmetry_strength_sweep_control": ["parameter_set_except_asymmetry_strength", "constraint_seed_path"],
        "asymmetric_edge_flip_control": ["state_set", "edge_count"],
        "constraint_resampled_generation_proxy": ["coarse_relation_params"],
    }.get(name, [])
    return json.dumps(values, sort_keys=True)


def changed_fields(name: str) -> str:
    values = {
        BASELINE_CONTROL: [],
        "roughness_seed_resample_generation_control": ["roughness_seed"],
        "small_edge_resample_control": ["realized_edge_targets"],
        "asymmetry_strength_sweep_control": ["asymmetry_strength"],
        "asymmetric_edge_flip_control": ["realized_edge_directions"],
        "constraint_resampled_generation_proxy": ["constraint_assignment_seed_path"],
    }.get(name, [])
    return json.dumps(values, sort_keys=True)


def parse_strengths(raw: str) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in raw.split(",") if item.strip())


def strength_label(value: float) -> str:
    return f"p{value:g}"


def run_batches(
    args: argparse.Namespace,
    jobs: list[dict[str, object]],
    status: dict[str, object],
    started: float,
    writer: StreamingCsvWriter,
    metric_stats: MetricStatsAccumulator,
    component_stats: ComponentStatsAccumulator,
    control_summaries: dict[tuple[str, str, str, str], dict[str, object]],
    selected_components: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    pending = [jobs[index : index + max(1, args.job_batch_size)] for index in range(0, len(jobs), max(1, args.job_batch_size))]
    metric_rows: list[dict[str, object]] = []
    manifests: list[dict[str, object]] = []
    preservation: list[dict[str, object]] = []
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
                futures[executor.submit(run_batch, batch, args.output_profile)] = batch
                status["jobs_submitted"] = int(status["jobs_submitted"]) + len(batch)
            done, _ = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                batch = futures.pop(future)
                try:
                    rows, manifest_rows, preservation_rows, batch_errors, completed = future.result()
                except Exception as exc:  # noqa: BLE001
                    rows, manifest_rows, preservation_rows, batch_errors, completed = [], [], [], [{"job_id": ",".join(str(job.get("job_id", "")) for job in batch), "error": repr(exc)}], 0
                scored = score_components_for_rows(rows, control_summaries, selected_components, args.component_z_threshold)
                metric_stats.add_rows(rows)
                component_stats.add_rows(scored)
                metric_sample = retained_rows(
                    rows,
                    args.metric_output_mode,
                    args.metric_audit_sample_rate,
                    args.metric_audit_sample_cap,
                    metric_stats.audit_sample_rows,
                    "metric",
                )
                component_sample = retained_rows(
                    scored,
                    args.component_output_mode,
                    args.component_audit_sample_rate,
                    args.component_audit_sample_cap,
                    component_stats.audit_sample_rows,
                    "component",
                )
                metric_stats.audit_sample_rows += len(metric_sample)
                component_stats.audit_sample_rows += len(component_sample)
                if args.metric_output_mode == "full":
                    writer.write("stage_b2_metric_rows.csv", metric_sample)
                    metric_rows.extend(metric_sample)
                elif args.metric_output_mode == "audit_sample":
                    writer.write("stage_b2_metric_rows_audit_sample.csv", metric_sample)
                if args.component_output_mode == "full":
                    writer.write("stage_b2_component_scores.csv", component_sample)
                elif args.component_output_mode == "audit_sample":
                    writer.write("stage_b2_component_scores_audit_sample.csv", component_sample)
                manifests.extend(manifest_rows)
                preservation.extend(preservation_rows)
                errors.extend(batch_errors)
                status["jobs_completed"] = int(status["jobs_completed"]) + completed
                if int(status["jobs_completed"]) - last_checkpoint_jobs >= max(1, args.checkpoint_every_jobs):
                    checkpoints.append(checkpoint_row(status, started, metric_stats.total_rows, component_stats.total_rows, manifests, preservation, errors))
                    last_checkpoint_jobs = int(status["jobs_completed"])
                    write_partial_status(args.out, status, started, checkpoints, metric_stats.total_rows, component_stats.total_rows, manifests, preservation, errors)
    finally:
        if futures:
            for future in futures:
                future.cancel()
            status["jobs_cancelled"] = len(futures)
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    status["pending_jobs_remaining"] = sum(len(batch) for batch in pending)
    checkpoints.append(checkpoint_row(status, started, metric_stats.total_rows, component_stats.total_rows, manifests, preservation, errors))
    write_partial_status(args.out, status, started, checkpoints, metric_stats.total_rows, component_stats.total_rows, manifests, preservation, errors)
    return metric_rows, manifests, preservation, errors, checkpoints


def run_batch(batch: list[dict[str, object]], output_profile: str) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], int]:
    metric_rows: list[dict[str, object]] = []
    manifests: list[dict[str, object]] = []
    preservation: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    completed = 0
    for job in batch:
        try:
            rows, manifest, audit = run_stage_b2_job(job, output_profile)
            metric_rows.extend(rows)
            manifests.append(manifest)
            if audit:
                preservation.append(audit)
        except Exception as exc:  # noqa: BLE001
            errors.append({"job_id": job.get("job_id", ""), "error": repr(exc)})
        completed += 1
    return metric_rows, manifests, preservation, errors, completed


def retained_rows(
    rows: list[dict[str, object]],
    mode: str,
    sample_rate: float,
    sample_cap: int,
    retained_so_far: int,
    salt: str,
) -> list[dict[str, object]]:
    if mode == "none":
        return []
    if mode == "full":
        return rows
    remaining = max(0, sample_cap - retained_so_far)
    if remaining <= 0:
        return []
    rate = max(0.0, min(1.0, sample_rate))
    kept = [
        row for row in rows
        if stable_sample_fraction(row, salt) <= rate
    ]
    if len(kept) < min(remaining, len(rows)) and retained_so_far == 0:
        kept.extend(row for row in rows if row not in kept)
    return kept[:remaining]


def stable_sample_fraction(row: dict[str, object], salt: str) -> float:
    text = "|".join(str(row.get(field, "")) for field in ("job_id", "condition_id", "syndrome_id", "syndrome_component_id", "group_id", "seed", "start_index", "window", "probe_key", "flow_mode"))
    value = 0
    for char in f"{salt}|{text}":
        value = (value * 131 + ord(char)) % 1_000_003
    return value / 1_000_003


def run_stage_b2_job(job: dict[str, object], output_profile: str) -> tuple[list[dict[str, object]], dict[str, object], dict[str, object]]:
    params = job["params"]
    seed = int(job["seed"])
    baseline = generate_relation_system(params, seed)  # type: ignore[arg-type]
    control = make_stage_b2_control_system(baseline, job, seed, params)  # type: ignore[arg-type]
    probe, alphabet_size, probe_group = build_probe(control, str(job["probe_key"]), str(job["source_probe_family"]))
    starts = [control.states[(seed + i * 17) % len(control.states)] for i in range(int(job["start_samples"]))]
    row_kind = "baseline" if job.get("actual_control_name") == BASELINE_CONTROL else "mechanism_control"
    rows = rows_for_starts(job, control, probe, alphabet_size, probe_group, starts, row_kind)
    common = common_condition_fields(job, baseline.system_id, control.system_id)
    for row in rows:
        row.update(common)
    manifest = system_manifest_row(job, baseline, control, common)
    audit: dict[str, object] = {}
    if job.get("actual_control_name") != BASELINE_CONTROL:
        audit = dict(substrate_preservation_audit(baseline, control))
        audit.update(common)
        audit["control_too_destructive_flag"] = audit.get("control_too_destructive", 0)
        audit["destructiveness_band"] = destructiveness_band(float_or_zero(audit.get("control_destructiveness_score")))
    compact = [compact_metric_row(row, output_profile) for row in rows]
    return compact, manifest, audit


def make_stage_b2_control_system(baseline: Any, job: dict[str, object], seed: int, params: RelationParams) -> Any:
    actual = str(job.get("actual_control_name", ""))
    strength = float_or_zero(job.get("mechanism_control_strength"))
    if actual == BASELINE_CONTROL:
        return baseline
    if actual == "roughness_seed_resample_generation_control":
        control = generate_relation_system(params, seed, roughness_seed=seed + 31_337 + int(strength) * 10_003)
        metadata = control_metadata(baseline, job, "computed")
        metadata.update(control.metadata)
        metadata["roughness_seed_changed_to"] = seed + 31_337 + int(strength) * 10_003
        return replace(control, system_id=f"{baseline.system_id}_roughness_seed{int(strength)}", metadata=metadata)
    if actual == "small_edge_resample_control":
        control = roughness_resampled_transform_control(baseline, seed + 41_111, strength)
        return replace(control, metadata={**control.metadata, **control_metadata(baseline, job, "computed")})
    if actual == "asymmetry_strength_sweep_control":
        if params.asymmetry_strength == 0.0 and strength != 1.0:
            metadata = control_metadata(baseline, job, "not_available")
            metadata["mechanism_control_unavailable_reason"] = "baseline_asymmetry_zero"
            return replace(baseline, system_id=f"{baseline.system_id}_asymmetry_strength_unavailable", metadata=metadata)
        adjusted = replace(params, asymmetry_strength=params.asymmetry_strength * strength)
        control = generate_relation_system(adjusted, seed)
        metadata = control_metadata(baseline, job, "computed")
        metadata.update(control.metadata)
        metadata["baseline_asymmetry_strength"] = params.asymmetry_strength
        metadata["control_asymmetry_strength"] = adjusted.asymmetry_strength
        return replace(control, system_id=f"{baseline.system_id}_asymmetry_x{strength:g}", metadata=metadata)
    if actual == "asymmetric_edge_flip_control":
        control = asymmetry_flip_sweep_control(baseline, seed + 51_119, strength)
        return replace(control, metadata={**control.metadata, **control_metadata(baseline, job, "computed")})
    if actual == "constraint_resampled_generation_proxy":
        control = constraint_resampled_generation_control(baseline, params, seed + 61_123, strength)
        metadata = control_metadata(baseline, job, "computed")
        metadata.update(control.metadata)
        metadata["proxy_note"] = "generation-level proxy; not a local assignment shuffle"
        return replace(control, metadata=metadata)
    metadata = control_metadata(baseline, job, "not_available")
    metadata["mechanism_control_unavailable_reason"] = "unknown_stage_b2_control"
    return replace(baseline, system_id=f"{baseline.system_id}_{actual}_not_available", metadata=metadata)


def control_metadata(baseline: Any, job: dict[str, object], status: str) -> dict[str, object]:
    return {
        **baseline.metadata,
        "mechanism_control_name": job.get("actual_control_name", ""),
        "mechanism_control_strength": job.get("mechanism_control_strength", ""),
        "mechanism_control_status": status,
        "baseline_system_id": baseline.system_id,
        "intended_control_name": job.get("intended_control_name", ""),
        "actual_control_name": job.get("actual_control_name", ""),
        "proxy_level": job.get("proxy_level", ""),
        "allowed_interpretation_level": job.get("allowed_interpretation_level", ""),
    }


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
        "intended_mechanism",
        "actual_intervention",
        "preserved_fields_json",
        "changed_fields_json",
        "unpreserved_fields_json",
        "preservation_failure_reason",
        "allowed_interpretation_level",
    )
    return {key: job.get(key, "") for key in keys} | {"baseline_system_id": baseline_system_id, "control_system_id": control_system_id}


def system_manifest_row(job: dict[str, object], baseline: Any, control: Any, common: dict[str, object]) -> dict[str, object]:
    return {
        **common,
        "job_id": job.get("job_id", ""),
        "group_id": job.get("group_id", ""),
        "seed": job.get("seed", ""),
        "fresh_seed_index": job.get("fresh_seed_index", ""),
        "start_samples": job.get("start_samples", ""),
        "probe_key": job.get("probe_key", ""),
        "mechanism_control_status": control.metadata.get("mechanism_control_status", "computed"),
        "mechanism_control_unavailable_reason": control.metadata.get("mechanism_control_unavailable_reason", ""),
        "state_count": len(control.states),
        "edge_count": sum(len(targets) for targets in control.edges.values()),
        "baseline_state_count": len(baseline.states),
        "baseline_edge_count": sum(len(targets) for targets in baseline.edges.values()),
    }


def compact_metric_row(row: dict[str, object], output_profile: str) -> dict[str, object]:
    if output_profile == "debug":
        source = dict(row)
    else:
        source = {field: row.get(field, "") for field in METRIC_ROW_FIELDS}
    return {field: source.get(field, "") for field in METRIC_ROW_FIELDS}


def score_components_for_rows(
    metric_rows: list[dict[str, object]],
    control_summaries: dict[tuple[str, str, str, str], dict[str, object]],
    components: list[dict[str, object]],
    threshold: float,
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in metric_rows:
        if row.get("preflight_context") != "design_recurrent_boundary":
            continue
        if row.get("probe_key") in DIAGNOSTIC_PROBES:
            continue
        for comp in components:
            metric = str(comp["metric_name"])
            if row.get(metric, "") == "":
                item = component_score_row(row, comp, threshold, "unavailable_metric")
                out.append(enrich_component_row(item, row))
                continue
            summary = control_summaries.get(control_context_key(row, metric))
            if summary is None:
                item = component_score_row(row, comp, threshold, "unavailable_control")
                out.append(enrich_component_row(item, row))
                continue
            observed = float_or_zero(row.get(metric))
            control_mean = float(summary["mean"])
            control_std = float(summary["std"])
            signed_delta = int(comp["direction"]) * (observed - control_mean)
            signed_z = signed_delta / control_std if control_std > 1e-12 else signed_delta
            item = component_score_row(row, comp, threshold, "scored")
            item.update({
                "observed_value": observed,
                "control_mean": control_mean,
                "control_std": control_std,
                "signed_z": signed_z,
                "control_percentile": percentile_from_sorted(observed, summary["sorted_values"]),
                "component_pass": int(signed_z >= threshold),
                "control_count": summary["count"],
            })
            out.append(enrich_component_row(item, row))
    return out


def enrich_component_row(item: dict[str, object], metric_row: dict[str, object]) -> dict[str, object]:
    for field in (
        "condition_id",
        "intended_control_name",
        "actual_control_name",
        "control_family",
        "control_variant",
        "proxy_level",
        "allowed_interpretation_level",
    ):
        item[field] = metric_row.get(field, "")
    return {field: item.get(field, "") for field in COMPONENT_ROW_FIELDS}


def add_frontier_preservation_metrics(preservation: list[dict[str, object]], metric_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    baseline = {baseline_key(row): row for row in metric_rows if row.get("actual_control_name") == BASELINE_CONTROL}
    for audit in preservation:
        condition_id = audit.get("condition_id", "")
        rows = [row for row in metric_rows if row.get("condition_id") == condition_id]
        frontier_deltas = []
        support_deltas = []
        for row in rows:
            base = baseline.get(baseline_key(row))
            if not base:
                continue
            frontier_deltas.append(abs(float_or_zero(row.get("frontier_size_b")) - float_or_zero(base.get("frontier_size_b"))) / max(1.0, float_or_zero(base.get("frontier_size_b"))))
            support_deltas.append(abs(float_or_zero(row.get("frontier_growth_ratio")) - float_or_zero(base.get("frontier_growth_ratio"))))
        audit["frontier_size_profile_delta"] = mean(frontier_deltas) if frontier_deltas else 0.0
        audit["support_growth_baseline_delta"] = mean(support_deltas) if support_deltas else 0.0
        audit["saturation_timing_delta"] = saturation_timing_delta(rows, baseline)
        audit["control_destructiveness_score"] = max(float_or_zero(audit.get("control_destructiveness_score")), min(1.0, float_or_zero(audit["frontier_size_profile_delta"])))
        audit["control_too_destructive_flag"] = int(float_or_zero(audit.get("control_destructiveness_score")) > 0.50)
        audit["destructiveness_band"] = destructiveness_band(float_or_zero(audit.get("control_destructiveness_score")))
    return preservation


def baseline_key(row: dict[str, object]) -> tuple[object, ...]:
    return (row.get("group_id"), row.get("seed"), row.get("probe_key"), row.get("start_samples"), row.get("start_index"), row.get("flow_mode"), row.get("window"))


def saturation_timing_delta(rows: list[dict[str, object]], baseline: dict[tuple[object, ...], dict[str, object]]) -> float:
    deltas = []
    groups: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[(row.get("group_id"), row.get("seed"), row.get("probe_key"), row.get("start_samples"), row.get("start_index"), row.get("flow_mode"))].append(row)
    for items in groups.values():
        base_items = [baseline.get(baseline_key(row)) for row in items if baseline.get(baseline_key(row))]
        if not base_items:
            continue
        deltas.append(abs(first_stable_window(items) - first_stable_window(base_items)))
    return mean(deltas) if deltas else 0.0


def first_stable_window(rows: list[dict[str, object]]) -> int:
    ordered = sorted(rows, key=lambda row: int(float_or_zero(row.get("H_a"))))
    for index, row in enumerate(ordered):
        if float_or_zero(row.get("frontier_growth_ratio")) <= 1.05:
            return index
    return len(ordered)


def destructiveness_band(value: float) -> str:
    if value <= 0.20:
        return "non_destructive"
    if value <= 0.35:
        return "mildly_destructive"
    if value <= 0.50:
        return "destructive_underdetermined"
    return "control_too_destructive"


def syndrome_rate_rows(component_scores: list[dict[str, object]], selected_syndromes: list[str]) -> list[dict[str, object]]:
    selected = set(selected_syndromes)
    out: list[dict[str, object]] = []
    keys = ("condition_id", "mechanism_condition", "mechanism_control_name", "mechanism_control_strength", "mechanism_strength_label", "actual_control_name", "proxy_level", "allowed_interpretation_level")
    for key, items in group_by(component_scores, keys).items():
        for context in component_contexts(items):
            if selected and context["syndrome_id"] not in selected:
                continue
            out.append({**{field: value for field, value in zip(keys, key)}, "syndrome_id": context["syndrome_id"], "probe_key": context["probe_key"], "flow_mode": context["flow_mode"], "syndrome_rate": context["observed_joint_rate"], "complete_unit_count": context["complete_unit_count"], "component_marginal_rates_json": json.dumps(context["component_marginal_rates"], sort_keys=True)})
    return out


def dependency_score_rows(
    syndrome_rates: list[dict[str, object]],
    preservation: list[dict[str, object]],
    selected_syndromes: list[str],
    identity: list[dict[str, object]],
) -> list[dict[str, object]]:
    baseline_rates = {
        str(syndrome_id): mean(float_or_zero(item.get("syndrome_rate")) for item in items)
        for (syndrome_id,), items in group_by([row for row in syndrome_rates if row.get("actual_control_name") == BASELINE_CONTROL], ("syndrome_id",)).items()
    }
    preservation_by_condition = group_by(preservation, ("condition_id",))
    identity_by_condition = {str(row.get("condition_id")): row for row in identity}
    out: list[dict[str, object]] = []
    for syndrome_id in selected_syndromes:
        baseline = baseline_rates.get(syndrome_id, 0.0)
        rows = [row for row in syndrome_rates if row.get("syndrome_id") == syndrome_id and row.get("actual_control_name") != BASELINE_CONTROL]
        for (condition_id,), items in group_by(rows, ("condition_id",)).items():
            rate = mean(float_or_zero(item.get("syndrome_rate")) for item in items) if items else 0.0
            audits = preservation_by_condition.get((condition_id,), [])
            identity_row = identity_by_condition.get(str(condition_id), {})
            destructive = mean(float_or_zero(row.get("control_destructiveness_score")) for row in audits) if audits else 0.0
            too_destructive = int(any(int(float_or_zero(row.get("control_too_destructive_flag"))) for row in audits))
            drop = baseline - rate
            dependency = drop / baseline if baseline > 1e-12 else 0.0
            actual = str(identity_row.get("actual_control_name", items[0].get("actual_control_name", "") if items else ""))
            proxy = str(identity_row.get("proxy_level", items[0].get("proxy_level", "") if items else ""))
            out.append({
                "syndrome_id": syndrome_id,
                "condition_id": condition_id,
                "actual_control_name": actual,
                "intended_control_name": identity_row.get("intended_control_name", ""),
                "control_family": identity_row.get("control_family", ""),
                "control_variant": identity_row.get("control_variant", ""),
                "proxy_level": proxy,
                "allowed_interpretation_level": allowed_interpretation_after_destructiveness(str(identity_row.get("allowed_interpretation_level", "")), destructive),
                "baseline_syndrome_rate": baseline,
                "mechanism_control_syndrome_rate": rate,
                "syndrome_rate_delta": drop,
                "mechanism_dependency_score": max(0.0, dependency),
                "generic_phase_score": rate / baseline if baseline > 1e-12 else 0.0,
                "control_destructiveness_score": destructive,
                "destructiveness_band": destructiveness_band(destructive),
                "control_too_destructive_flag": too_destructive,
                "decision_class": dependency_decision(actual, proxy, baseline, rate, dependency, destructive),
                "rate_context_count": len(items),
            })
    return out


def allowed_interpretation_after_destructiveness(base: str, destructive: float) -> str:
    if destructive > 0.50:
        return "underdetermined_due_to_destructiveness"
    return base


def dependency_decision(actual: str, proxy: str, baseline: float, rate: float, dependency: float, destructive: float) -> str:
    if baseline <= 1e-12:
        return "baseline_too_sparse_underdetermined"
    if destructive > 0.50:
        return "control_too_destructive_underdetermined"
    if dependency < 0.10:
        return "no_resolved_residual"
    if proxy == "topology_level_proxy" and "edge" in actual:
        return "edge_roughening_sensitive_syndrome" if "resample" in actual else "asymmetric_edge_flip_sensitive_syndrome"
    if actual == "roughness_seed_resample_generation_control":
        return "roughness_term_sensitive_syndrome"
    if actual == "asymmetry_strength_sweep_control":
        return "asymmetry_strength_sensitive_syndrome"
    if "constraint" in actual:
        return "constraint_sensitive_weak_syndrome"
    return "mechanism_calibration_positive_weak" if dependency >= 0.25 else "gauge_overlay_inconclusive"


def decision_summary_rows(dependency: list[dict[str, object]], selected_syndromes: list[str]) -> list[dict[str, object]]:
    out = []
    for syndrome_id in selected_syndromes:
        items = [row for row in dependency if row.get("syndrome_id") == syndrome_id]
        if not items:
            out.append({"syndrome_id": syndrome_id, "decision_class": "baseline_too_sparse_underdetermined"})
            continue
        priority = decision_priority([str(row.get("decision_class")) for row in items])
        out.append({
            "syndrome_id": syndrome_id,
            "decision_class": priority,
            "baseline_syndrome_rate": max(float_or_zero(row.get("baseline_syndrome_rate")) for row in items),
            "max_mechanism_dependency_score": max(float_or_zero(row.get("mechanism_dependency_score")) for row in items),
            "min_generic_phase_score": min(float_or_zero(row.get("generic_phase_score")) for row in items),
            "max_control_destructiveness_score": max(float_or_zero(row.get("control_destructiveness_score")) for row in items),
            "non_destructive_or_mild_control_count": sum(int(float_or_zero(row.get("control_destructiveness_score")) <= 0.35) for row in items),
            "holdout_scoring_count": 0,
        })
    return out


def decision_priority(classes: list[str]) -> str:
    for candidate in (
        "roughness_term_sensitive_syndrome",
        "asymmetry_strength_sensitive_syndrome",
        "edge_roughening_sensitive_syndrome",
        "asymmetric_edge_flip_sensitive_syndrome",
        "constraint_sensitive_weak_syndrome",
        "mechanism_calibration_positive_weak",
        "control_too_destructive_underdetermined",
        "no_resolved_residual",
    ):
        if candidate in classes:
            return candidate
    return classes[0] if classes else "no_resolved_residual"


def entropy_view_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return aggregate_view(rows, ("condition_id", "actual_control_name", "proxy_level", "probe_key", "flow_mode", "horizon_band"), ("transition_matrix_entropy", "row_entropy_mean", "column_entropy_mean"))


def flow_view_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return aggregate_view(rows, ("condition_id", "actual_control_name", "proxy_level", "probe_key", "flow_mode", "horizon_band"), ("frontier_bottleneck_index", "top_k_flow_concentration", "off_diagonal_transform_mass", "edge_into_fb_rate", "states_without_window_target"))


def horizon_view_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return aggregate_view(rows, ("condition_id", "actual_control_name", "proxy_level", "horizon_band"), ("frontier_growth_ratio", "frontier_bottleneck_index", "transition_matrix_entropy", "support_turnover_rate"))


def aggregate_view(rows: list[dict[str, object]], keys: tuple[str, ...], metrics: tuple[str, ...]) -> list[dict[str, object]]:
    enriched = []
    for row in rows:
        item = dict(row)
        item["horizon_band"] = horizon_band(row)
        enriched.append(item)
    out = []
    for key, items in group_by(enriched, keys).items():
        record = {field: value for field, value in zip(keys, key)}
        record["rows"] = len(items)
        for metric in metrics:
            values = [float_or_zero(item.get(metric)) for item in items if item.get(metric, "") != ""]
            record[f"{metric}_mean"] = mean(values) if values else ""
        out.append(record)
    return out


def horizon_band(row: dict[str, object]) -> str:
    ha = int(float_or_zero(row.get("H_a")))
    hb = int(float_or_zero(row.get("H_b")))
    if hb <= 4:
        return "short"
    if hb <= 16:
        return "middle"
    return "downstream"


def entropy_flow_horizon_overlay(entropy: list[dict[str, object]], flow: list[dict[str, object]], horizon: list[dict[str, object]]) -> list[dict[str, object]]:
    baseline_entropy = baseline_means(entropy, "transition_matrix_entropy_mean")
    baseline_flow = baseline_means(flow, "frontier_bottleneck_index_mean")
    baseline_horizon = baseline_means(horizon, "frontier_growth_ratio_mean")
    out = []
    condition_ids = sorted({str(row.get("condition_id")) for row in entropy + flow + horizon if row.get("condition_id") and row.get("actual_control_name") != BASELINE_CONTROL})
    for condition_id in condition_ids:
        entropy_delta = mean_delta(entropy, condition_id, "transition_matrix_entropy_mean", baseline_entropy)
        flow_delta = mean_delta(flow, condition_id, "frontier_bottleneck_index_mean", baseline_flow)
        horizon_delta = mean_delta(horizon, condition_id, "frontier_growth_ratio_mean", baseline_horizon)
        out.append({
            "condition_id": condition_id,
            "entropy_delta_vs_baseline": entropy_delta,
            "flow_bottleneck_delta_vs_baseline": flow_delta,
            "horizon_growth_delta_vs_baseline": horizon_delta,
            "entropy_profile_class": "entropy_concentrating" if entropy_delta < -0.05 else ("entropy_spreading" if entropy_delta > 0.05 else "entropy_near_baseline"),
            "flow_profile_class": "flow_more_bottlenecked" if flow_delta > 0.03 else ("flow_less_bottlenecked" if flow_delta < -0.03 else "flow_near_baseline"),
            "horizon_profile_class": "downstream_reopening_hint" if horizon_delta > 0.05 else ("downstream_narrowing_hint" if horizon_delta < -0.05 else "horizon_near_baseline"),
        })
    return out


def baseline_means(rows: list[dict[str, object]], metric: str) -> dict[tuple[object, ...], float]:
    out = {}
    for row in rows:
        if row.get("actual_control_name") != BASELINE_CONTROL:
            continue
        key = tuple(row.get(field, "") for field in ("probe_key", "flow_mode", "horizon_band") if field in row)
        out[key] = float_or_zero(row.get(metric))
    return out


def mean_delta(rows: list[dict[str, object]], condition_id: str, metric: str, baseline: dict[tuple[object, ...], float]) -> float:
    deltas = []
    for row in rows:
        if row.get("condition_id") != condition_id:
            continue
        key = tuple(row.get(field, "") for field in ("probe_key", "flow_mode", "horizon_band") if field in row)
        if key in baseline:
            deltas.append(float_or_zero(row.get(metric)) - baseline[key])
    return mean(deltas) if deltas else 0.0


def corridor_trap_fakeout_summary(decision: list[dict[str, object]], dependency: list[dict[str, object]], overlay: list[dict[str, object]]) -> list[dict[str, object]]:
    overlay_by_condition = {str(row.get("condition_id")): row for row in overlay}
    out = []
    for row in decision:
        syndrome_id = str(row.get("syndrome_id", ""))
        deps = [item for item in dependency if item.get("syndrome_id") == syndrome_id]
        best = max(deps, key=lambda item: float_or_zero(item.get("mechanism_dependency_score")), default={})
        overlay_row = overlay_by_condition.get(str(best.get("condition_id")), {})
        klass = "underpowered_or_unresolved"
        if row.get("decision_class") == "control_too_destructive_underdetermined":
            klass = "underpowered_or_unresolved"
        elif "edge" in str(row.get("decision_class")):
            klass = "edge_fragile_deformation"
        elif overlay_row.get("horizon_profile_class") == "downstream_reopening_hint":
            klass = "corridor_like_deformation"
        elif overlay_row.get("horizon_profile_class") == "downstream_narrowing_hint":
            klass = "trap_like_deformation"
        elif float_or_zero(best.get("mechanism_dependency_score")) > 0.10:
            klass = "mechanism_sensitive_weak_residue"
        out.append({
            "syndrome_id": syndrome_id,
            "baseline_rate": row.get("baseline_syndrome_rate", ""),
            "best_condition_id": best.get("condition_id", ""),
            "best_non_destructive_control_rate": best.get("mechanism_control_syndrome_rate", ""),
            "roughness_term_sensitivity": sensitivity_for(deps, "roughness_seed_resample_generation_control"),
            "edge_roughening_sensitivity": sensitivity_for(deps, "small_edge_resample_control"),
            "asymmetry_strength_sensitivity": sensitivity_for(deps, "asymmetry_strength_sweep_control"),
            "asymmetric_edge_flip_sensitivity": sensitivity_for(deps, "asymmetric_edge_flip_control"),
            "constraint_gentle_sensitivity": sensitivity_for(deps, "constraint_resampled_generation_proxy"),
            "entropy_profile_class": overlay_row.get("entropy_profile_class", ""),
            "flow_profile_class": overlay_row.get("flow_profile_class", ""),
            "horizon_profile_class": overlay_row.get("horizon_profile_class", ""),
            "corridor_trap_fakeout_class": klass,
            "interpretation_confidence": "low_smoke" if deps else "none",
        })
    return out


def sensitivity_for(rows: list[dict[str, object]], control_name: str) -> float:
    values = [float_or_zero(row.get("mechanism_dependency_score")) for row in rows if row.get("actual_control_name") == control_name and float_or_zero(row.get("control_destructiveness_score")) <= 0.35]
    return max(values, default=0.0)


def control_identity_audit(manifests: list[dict[str, object]], preservation: list[dict[str, object]]) -> list[dict[str, object]]:
    preservation_by_condition = group_by(preservation, ("condition_id",))
    out = []
    seen = set()
    for row in manifests:
        condition_id = row.get("condition_id", "")
        if condition_id in seen:
            continue
        seen.add(condition_id)
        audits = preservation_by_condition.get((condition_id,), [])
        max_destructive = max((float_or_zero(item.get("control_destructiveness_score")) for item in audits), default=0.0)
        item = {field: row.get(field, "") for field in (
            "condition_id",
            "intended_control_name",
            "actual_control_name",
            "control_family",
            "control_variant",
            "proxy_level",
            "intended_mechanism",
            "actual_intervention",
            "preserved_fields_json",
            "changed_fields_json",
            "unpreserved_fields_json",
            "preservation_failure_reason",
            "allowed_interpretation_level",
        )}
        item["max_control_destructiveness_score"] = max_destructive
        item["destructiveness_band"] = destructiveness_band(max_destructive)
        item["allowed_interpretation_level_after_destructiveness"] = allowed_interpretation_after_destructiveness(str(item["allowed_interpretation_level"]), max_destructive)
        item["downgraded_at_runtime"] = int(row.get("intended_control_name") != row.get("actual_control_name"))
        out.append(item)
    return out


def group_by(rows: list[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[object, ...], list[dict[str, object]]]:
    out: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        out[tuple(row.get(key, "") for key in keys)].append(row)
    return out


def checkpoint_row(
    status: dict[str, object],
    started: float,
    metric_row_count: int,
    component_row_count: int,
    manifests: list[dict[str, object]],
    preservation: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "jobs_submitted": status.get("jobs_submitted"),
        "jobs_completed": status.get("jobs_completed"),
        "metric_rows": metric_row_count,
        "component_rows": component_row_count,
        "system_manifest_rows": len(manifests),
        "preservation_rows": len(preservation),
        "errors": len(errors),
        "status": status.get("status"),
    }


def write_partial_status(
    out_dir: Path,
    status: dict[str, object],
    started: float,
    checkpoints: list[dict[str, object]],
    metric_row_count: int,
    component_row_count: int,
    manifests: list[dict[str, object]],
    preservation: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    partial = dict(status)
    partial["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    partial["metric_rows_partial"] = metric_row_count
    partial["component_rows_partial"] = component_row_count
    partial["system_manifest_rows_partial"] = len(manifests)
    partial["preservation_rows_partial"] = len(preservation)
    partial["errors"] = len(errors)
    partial["partial_checkpoint_written_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (out_dir / "status.json").write_text(json.dumps(partial, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(out_dir / "stage_b2_progress_checkpoints.csv", checkpoints)


def write_final_outputs(
    out_dir: Path,
    status: dict[str, object],
    checkpoints: list[dict[str, object]],
    identity: list[dict[str, object]],
    manifests: list[dict[str, object]],
    preservation: list[dict[str, object]],
    syndrome_rates: list[dict[str, object]],
    dependency: list[dict[str, object]],
    decision: list[dict[str, object]],
    entropy: list[dict[str, object]],
    flow: list[dict[str, object]],
    horizon: list[dict[str, object]],
    overlay: list[dict[str, object]],
    corridor: list[dict[str, object]],
    marginal: list[dict[str, object]],
    ablation: list[dict[str, object]],
    vs_controls: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    write_csv(out_dir / "stage_b2_progress_checkpoints.csv", checkpoints)
    write_csv(out_dir / "stage_b2_control_identity_audit.csv", identity)
    write_csv(out_dir / "stage_b2_mechanism_control_system_manifest.csv", manifests)
    write_csv(out_dir / "stage_b2_substrate_preservation.csv", preservation)
    write_csv(out_dir / "stage_b2_syndrome_rates.csv", syndrome_rates)
    write_csv(out_dir / "stage_b2_dependency_scores.csv", dependency)
    write_csv(out_dir / "stage_b2_decision_summary.csv", decision)
    write_csv(out_dir / "stage_b2_entropy_view_summary.csv", entropy)
    write_csv(out_dir / "stage_b2_flow_view_summary.csv", flow)
    write_csv(out_dir / "stage_b2_horizon_view_summary.csv", horizon)
    write_csv(out_dir / "stage_b2_entropy_flow_horizon_overlay.csv", overlay)
    write_csv(out_dir / "stage_b2_corridor_trap_fakeout_summary.csv", corridor)
    write_csv(out_dir / "stage_b2_syndrome_marginal_preserving_controls.csv", marginal)
    write_csv(out_dir / "stage_b2_syndrome_component_ablation.csv", ablation)
    write_csv(out_dir / "stage_b2_syndrome_vs_controls.csv", vs_controls)
    write_csv(out_dir / "errors.csv", errors)
    write_report(out_dir, status, identity, decision, corridor)
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    write_manifest(out_dir, status)


def write_report(out_dir: Path, status: dict[str, object], identity: list[dict[str, object]], decision: list[dict[str, object]], corridor: list[dict[str, object]]) -> None:
    proxy_counts = Counter(str(row.get("proxy_level", "")) for row in identity)
    too_destructive = [
        row for row in identity
        if row.get("allowed_interpretation_level_after_destructiveness") == "underdetermined_due_to_destructiveness"
    ]
    downgraded = [row for row in identity if int(float_or_zero(row.get("downgraded_at_runtime"))) > 0]
    lines = [
        "# RFS-MB0 Stage B-2 Mechanism Calibration and Gauge Overlay Report",
        "",
        "## Claim boundary",
        "",
        "No holdout scoring, n=6 transfer, alphabet expansion, candidate promotion, Omega detection, agent detection, identity detection, or valuer detection.",
        "",
        "## Run shape",
        "",
        f"Status: `{status.get('status')}`. Jobs: `{status.get('jobs_completed')}/{status.get('jobs_requested')}`. Errors: `{status.get('errors')}`.",
        "",
        "## Control identity and proxy discipline",
        "",
        f"Exact mechanism control conditions: `{proxy_counts.get('exact_mechanism_control', 0)}`.",
        f"Near-mechanism proxy conditions: `{proxy_counts.get('near_mechanism_proxy', 0)}`.",
        f"Generation-level proxy conditions: `{proxy_counts.get('generation_level_proxy', 0)}`.",
        f"Topology-level proxy conditions: `{proxy_counts.get('topology_level_proxy', 0)}`.",
        f"Presentation-level control conditions: `{proxy_counts.get('presentation_level_control', 0)}`.",
        f"Not-available/baseline conditions: `{proxy_counts.get('not_available', 0)}`.",
        f"Too-destructive/underdetermined conditions: `{len(too_destructive)}`.",
        f"Runtime-downgraded intended controls: `{len(downgraded)}`.",
        "",
        "## Decision summary",
        "",
        "| syndrome_id | decision_class | baseline_rate | max_dependency | max_destructiveness |",
        "|---|---|---:|---:|---:|",
    ]
    for row in decision:
        lines.append(f"| {row.get('syndrome_id', '')} | {row.get('decision_class', '')} | {float_or_zero(row.get('baseline_syndrome_rate')):.6f} | {float_or_zero(row.get('max_mechanism_dependency_score')):.3f} | {float_or_zero(row.get('max_control_destructiveness_score')):.3f} |")
    lines.extend(["", "## Corridor / Trap / Fakeout", "", "| syndrome_id | class | confidence |", "|---|---|---|"])
    for row in corridor:
        lines.append(f"| {row.get('syndrome_id', '')} | {row.get('corridor_trap_fakeout_class', '')} | {row.get('interpretation_confidence', '')} |")
    lines.extend(["", "## Output manifest", "", "See `output_manifest.json`.", ""])
    (out_dir / "rfs_mb0_stage_b2_mechanism_calibration_and_gauge_overlay_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest(out_dir: Path, status: dict[str, object]) -> None:
    rows = []
    for name in OUTPUTS:
        path = out_dir / name
        exists = path.exists() or name == "output_manifest.json"
        file_status = "present" if exists else "missing"
        if name == "stage_b2_metric_rows.csv" and status.get("metric_output_mode") != "full":
            file_status = f"skipped_by_metric_output_mode:{status.get('metric_output_mode')}"
        if name == "stage_b2_metric_rows_audit_sample.csv" and status.get("metric_output_mode") != "audit_sample":
            file_status = f"skipped_by_metric_output_mode:{status.get('metric_output_mode')}"
        if name == "stage_b2_component_scores.csv" and status.get("component_output_mode") != "full":
            file_status = f"skipped_by_component_output_mode:{status.get('component_output_mode')}"
        if name == "stage_b2_component_scores_audit_sample.csv" and status.get("component_output_mode") != "audit_sample":
            file_status = f"skipped_by_component_output_mode:{status.get('component_output_mode')}"
        rows.append({"file": name, "exists": exists, "status": file_status, "row_count": csv_row_count(path) if path.suffix == ".csv" else ""})
    (out_dir / "output_manifest.json").write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


def csv_row_count(path: Path) -> int:
    if not path.exists() or path.suffix != ".csv":
        return 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        count = sum(1 for _ in handle)
    if count <= 1:
        return 0
    return count - 1


def job_manifest_rows(jobs: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{key: value for key, value in job.items() if key != "params"} for job in jobs]


if __name__ == "__main__":
    main()
