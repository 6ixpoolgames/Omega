from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from statistics import mean

from .run_boundary_deformation_guardrail import THRESHOLDS, metric_available, resolution_regime
from .run_deformation_detector_sweep import params_from_parameter_set_id, run_sweep_job, stable_seed
from .run_focused_boundary_recurrence import apply_variant, float_or_zero, group_by, read_csv, write_csv


PROBE_AXES = {
    "constraint_profile_hash": "constraint_axis",
    "constraint_violation_count_plus_local_tuple": "constraint_axis",
    "constraint_gradient_class": "constraint_gradient_axis",
    "degree_profile_rank": "degree_rank_axis",
    "constraint_cross_degree_rank": "cross_constraint_degree_axis",
    "horizon_growth_contrast_v2": "frontier_dynamics_axis",
    "self_recurrence_horizon_v2": "cycle_structure_axis",
    "wiring_role_class_v2": "wiring_role_axis",
    "existing_low": "low_projection_axis",
    "full_state_hash": "identity_axis",
}
PANEL = (
    "constraint_profile_hash",
    "constraint_violation_count_plus_local_tuple",
    "constraint_gradient_class",
    "degree_profile_rank",
    "constraint_cross_degree_rank",
    "horizon_growth_contrast_v2",
    "self_recurrence_horizon_v2",
    "wiring_role_class_v2",
    "existing_low",
    "full_state_hash",
)
OUTPUTS = (
    "rfs_mb0_instrumentation_branch_pivot_report.md",
    "probe_panel_manifest.json",
    "probe_viability_preflight.csv",
    "probe_viability_summary.md",
    "instrumentation_holdout_split.csv",
    "threshold_selection_audit.csv",
    "instrumentation_multiplicity_audit.csv",
    "available_axis_gate_summary.csv",
    "new_quotient_axis_gate_summary.csv",
    "sparse_frontier_probe_viability.csv",
    "sparse_frontier_detection_summary.csv",
    "errors.csv",
    "output_manifest.json",
    "status.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 instrumentation Phase A probe viability preflight.")
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--corrected", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/corrected_group_classification.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_instrumentation_phase_a_preflight"))
    parser.add_argument("--groups", type=int, default=20)
    parser.add_argument("--design-groups", type=int, default=10)
    parser.add_argument("--neutral-anchors", type=int, default=6)
    parser.add_argument("--fakeout-groups", type=int, default=4)
    parser.add_argument("--fresh-seeds-per-group", type=int, default=2)
    parser.add_argument("--start-samples-list", type=str, default="3,8")
    parser.add_argument("--horizons", type=str, default="0,1,2,4,8,12,16,24,32")
    parser.add_argument("--probe-families", type=str, default=",".join(PANEL))
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--job-batch-size", type=int, default=8)
    parser.add_argument("--max-runtime-seconds", type=int, default=1800)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=120)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    selected_groups, split_rows = build_holdout_split(args)
    anchors = {row.get("anchor_id", ""): row for row in read_csv(args.source_run / "atlas_band_selection.csv")}
    source_anchors = list(anchors.values())
    starts = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    horizons = tuple(int(item.strip()) for item in args.horizons.split(",") if item.strip())
    probes = tuple(item.strip() for item in args.probe_families.split(",") if item.strip())
    jobs = build_jobs(args, selected_groups, split_rows, anchors, source_anchors, starts, horizons, probes)
    status: dict[str, object] = {
        "status": "RUNNING",
        "phase": "A_preflight_only",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workers": args.workers,
        "jobs_requested": len(jobs),
        "jobs_submitted": 0,
        "jobs_completed": 0,
        "jobs_cancelled": 0,
        "pending_jobs_remaining": len(jobs),
        "promotion_enabled": False,
        "candidate_detection_enabled": False,
        "holdout_detection_enabled": False,
        "max_runtime_seconds": args.max_runtime_seconds,
        "shutdown_cushion_seconds": args.shutdown_cushion_seconds,
    }
    batches = [jobs[index : index + max(1, args.job_batch_size)] for index in range(0, len(jobs), max(1, args.job_batch_size))]
    status["job_batch_size"] = max(1, args.job_batch_size)
    status["job_batches_requested"] = len(batches)
    rows, errors = run_batches(args, batches, status, started)
    if status["status"] == "RUNNING":
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "all_jobs_completed"
    write_outputs(args, status, started, probes, split_rows, rows, errors)


def build_holdout_split(args: argparse.Namespace) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    selected = {row.get("group_id", ""): row for row in read_csv(args.selection)}
    corrected = read_csv(args.corrected)
    priority = ("independent_axis_recurrent_but_collision_limited", "weak_control_bundle_recurrence")
    groups = []
    for klass in priority:
        for row in corrected:
            group_id = row.get("group_id", "")
            if row.get("corrected_group_class") == klass and group_id in selected:
                merged = dict(selected[group_id])
                merged["prior_corrected_group_class"] = klass
                groups.append(merged)
                if len(groups) >= args.groups:
                    break
        if len(groups) >= args.groups:
            break
    split = []
    for index, group in enumerate(groups):
        split_set = "design_set" if index < args.design_groups else "holdout_set"
        split.append({
            "group_id": group.get("group_id", ""),
            "split_set": split_set,
            "prior_corrected_group_class": group.get("prior_corrected_group_class", ""),
            "source_anchor_id": group.get("source_anchor_id", group.get("source_band_id", "")),
            "variant_dimension": group.get("variant_dimension", ""),
            "variant_value": group.get("variant_value", ""),
            "selection_order": index,
            "candidate_scoring_allowed": int(split_set == "design_set"),
            "holdout_frozen_until_phase_c": int(split_set == "holdout_set"),
        })
    return groups, split


def build_jobs(
    args: argparse.Namespace,
    groups: list[dict[str, str]],
    split_rows: list[dict[str, object]],
    anchors: dict[str, dict[str, str]],
    source_anchors: list[dict[str, str]],
    starts: tuple[int, ...],
    horizons: tuple[int, ...],
    probes: tuple[str, ...],
) -> list[dict[str, object]]:
    jobs = []
    split_by_group = {str(row["group_id"]): row for row in split_rows}
    fakeout_count = 0
    for group_index, group in enumerate(groups):
        split = split_by_group.get(group.get("group_id", ""), {})
        if split.get("split_set") == "holdout_set":
            continue
        context = "design_recurrent_boundary"
        anchor = anchors.get(group.get("source_anchor_id", group.get("source_band_id", "")), {})
        params = params_from_parameter_set_id(anchor.get("parameter_set_id", ""))
        if params is None:
            continue
        variant_params = apply_variant(params, group.get("variant_dimension", ""), group.get("variant_value", ""))
        base_seed = int(anchor.get("seed") or stable_seed(anchor.get("environment_id", group.get("group_id", ""))))
        jobs.extend(make_jobs(context, group.get("group_id", ""), group_index, anchor, variant_params, base_seed, starts, horizons, probes, args.fresh_seeds_per_group))
    for group_index, group in enumerate(groups):
        if fakeout_count >= args.fakeout_groups:
            break
        if group.get("prior_corrected_group_class") != "weak_control_bundle_recurrence":
            continue
        anchor = anchors.get(group.get("source_anchor_id", group.get("source_band_id", "")), {})
        params = params_from_parameter_set_id(anchor.get("parameter_set_id", ""))
        if params is None:
            continue
        variant_params = apply_variant(params, group.get("variant_dimension", ""), group.get("variant_value", ""))
        base_seed = int(anchor.get("seed") or stable_seed(anchor.get("environment_id", group.get("group_id", ""))))
        jobs.extend(make_jobs("matched_fakeout_group", group.get("group_id", ""), group_index, anchor, variant_params, base_seed, starts, horizons, probes, args.fresh_seeds_per_group))
        fakeout_count += 1
    for neutral_index, anchor in enumerate(source_anchors[: args.neutral_anchors]):
        params = params_from_parameter_set_id(anchor.get("parameter_set_id", ""))
        if params is None:
            continue
        base_seed = int(anchor.get("seed") or stable_seed(anchor.get("environment_id", f"neutral_{neutral_index}")))
        jobs.extend(make_jobs("neutral_generated_system", f"neutral_{neutral_index:03d}", neutral_index, anchor, params, base_seed, starts, horizons, probes, args.fresh_seeds_per_group))
    return jobs


def make_jobs(context: str, group_id: str, group_index: int, anchor: dict[str, str], params: object, base_seed: int, starts: tuple[int, ...], horizons: tuple[int, ...], probes: tuple[str, ...], fresh_seeds: int) -> list[dict[str, object]]:
    jobs = []
    for seed_index in range(fresh_seeds):
        seed = base_seed + 50_021 * (seed_index + 1) + group_index
        for probe in probes:
            for start_count in starts:
                jobs.append({
                    "job_id": f"phase_a_{context}_{group_index:03d}_{seed_index}_{probe}_{start_count}",
                    "preflight_context": context,
                    "anchor_id": anchor.get("anchor_id", group_id),
                    "anchor_environment_id": anchor.get("environment_id", ""),
                    "anchor_primary_class": anchor.get("anchor_primary_class", context),
                    "variant_dimension": "baseline" if context == "neutral_generated_system" else "",
                    "variant_value": "baseline" if context == "neutral_generated_system" else "",
                    "params": params,
                    "seed": seed,
                    "probe_key": probe,
                    "source_probe_family": anchor.get("source_probe_family", anchor.get("anchor_probe_family", "")),
                    "start_samples": start_count,
                    "horizons": horizons,
                    "group_id": group_id,
                })
    return jobs


def run_batches(args: argparse.Namespace, batches: list[list[dict[str, object]]], status: dict[str, object], started: float) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    pending = list(batches)
    futures = {}
    executor = ProcessPoolExecutor(max_workers=max(1, args.workers))
    try:
        while pending or futures:
            remaining = args.max_runtime_seconds - (time.perf_counter() - started)
            if remaining <= args.shutdown_cushion_seconds:
                status["status"] = "PARTIAL_TIME_LIMIT_REACHED"
                status["finalization_reason"] = "shutdown_cushion_reached"
                break
            while pending and len(futures) < max(1, args.workers):
                batch = pending.pop(0)
                futures[executor.submit(run_preflight_batch, batch)] = batch
                status["jobs_submitted"] = int(status["jobs_submitted"]) + len(batch)
            done, _ = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                batch_rows, batch_errors, completed = future.result()
                futures.pop(future)
                rows.extend(batch_rows)
                errors.extend(batch_errors)
                status["jobs_completed"] = int(status["jobs_completed"]) + completed
    finally:
        if futures:
            for future in futures:
                future.cancel()
            status["jobs_cancelled"] = len(futures)
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    status["pending_jobs_remaining"] = len(pending)
    return rows, errors


def run_preflight_batch(jobs: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], int]:
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    completed = 0
    for job in jobs:
        try:
            for row in run_sweep_job(job):
                row["preflight_context"] = job.get("preflight_context", "")
                row["group_id"] = job.get("group_id", "")
                row["probe_axis"] = PROBE_AXES.get(str(row.get("probe_key", "")), "unknown_axis")
                row["probe_role"] = probe_role(str(row.get("probe_key", "")))
                annotate_bucket_stats(row)
                row["probe_resolution_regime"] = resolution_regime(row, THRESHOLDS["default"])
                row["preflight_pass_flag"] = int(row["probe_resolution_regime"] == "usable_quotient")
                rows.append(row)
        except Exception as exc:  # noqa: BLE001
            errors.append({"job_id": job.get("job_id", ""), "error": repr(exc)})
        completed += 1
    return rows, errors, completed


def write_outputs(args: argparse.Namespace, status: dict[str, object], started: float, probes: tuple[str, ...], split_rows: list[dict[str, object]], rows: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    manifest = probe_panel_manifest(probes)
    preflight = probe_viability_preflight(rows)
    sparse = sparse_frontier_probe_viability(rows)
    sparse_detection = sparse_frontier_detection_summary(rows)
    threshold_audit = threshold_selection_audit(rows)
    multiplicity = instrumentation_multiplicity_audit(probes, split_rows, rows)
    available_gate = axis_gate_summary(preflight, "available_axis_gate")
    quotient_gate = axis_gate_summary(preflight, "new_quotient_axis_gate")
    status["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    status["row_count"] = len(rows)
    status["errors"] = len(errors)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "probe_panel_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(args.out / "probe_viability_preflight.csv", preflight)
    write_csv(args.out / "instrumentation_holdout_split.csv", split_rows)
    write_csv(args.out / "threshold_selection_audit.csv", threshold_audit)
    write_csv(args.out / "instrumentation_multiplicity_audit.csv", multiplicity)
    write_csv(args.out / "available_axis_gate_summary.csv", available_gate)
    write_csv(args.out / "new_quotient_axis_gate_summary.csv", quotient_gate)
    write_csv(args.out / "sparse_frontier_probe_viability.csv", sparse)
    write_csv(args.out / "sparse_frontier_detection_summary.csv", sparse_detection)
    write_csv(args.out / "errors.csv", errors)
    write_viability_summary(args.out, preflight, sparse, available_gate, quotient_gate)
    write_pivot_report(args.out, status, preflight, sparse, threshold_audit, available_gate, quotient_gate)
    (args.out / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    write_manifest(args.out)


def probe_panel_manifest(probes: tuple[str, ...]) -> list[dict[str, object]]:
    reasons = {
        "constraint_profile_hash": "existing partly-working constraint-axis continuity probe",
        "constraint_violation_count_plus_local_tuple": "existing repaired constraint-axis continuity probe",
        "constraint_gradient_class": "constraint directionality without raw-state identity",
        "degree_profile_rank": "rank-normalized relation geometry",
        "constraint_cross_degree_rank": "crossed constraint and degree-rank instrumentation",
        "horizon_growth_contrast_v2": "dynamic frontier-growth contrast",
        "self_recurrence_horizon_v2": "cycle/return structure",
        "wiring_role_class_v2": "system-relative wiring role",
        "existing_low": "diagnostic low projection control",
        "full_state_hash": "identity leakage control",
    }
    alphabet = {
        "constraint_profile_hash": "16-256",
        "constraint_violation_count_plus_local_tuple": "constraints+local tuple",
        "constraint_gradient_class": "9-18",
        "degree_profile_rank": 16,
        "constraint_cross_degree_rank": "12-24",
        "horizon_growth_contrast_v2": 32,
        "self_recurrence_horizon_v2": 20,
        "wiring_role_class_v2": 64,
        "existing_low": "source probe dependent",
        "full_state_hash": "state-count capped hash",
    }
    risks = {
        "full_state_hash": "identity-like by design; control only",
        "existing_low": "legacy low projection can collide heavily",
    }
    return [
        {
            "probe_key": probe,
            "probe_axis": PROBE_AXES.get(probe, "unknown_axis"),
            "probe_family": probe,
            "intended_alphabet_size": alphabet.get(probe, ""),
            "expected_alphabet_range_for_n": "0.05N_to_0.30N_effective_target; >0.50N_identity_risk",
            "expected_resolution_regime": "usable_quotient" if probe not in {"existing_low", "full_state_hash"} else "diagnostic_or_control",
            "reason_for_inclusion": reasons.get(probe, ""),
            "known_failure_risk": risks.get(probe, "may be too coarse or too high-resolution after empirical preflight"),
        }
        for probe in probes
    ]


def probe_viability_preflight(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (context, probe, axis), items in group_by(rows, ("preflight_context", "probe_key", "probe_axis")).items():
        effective = [float_or_zero(item.get("effective_signature_count")) for item in items]
        state_counts = [float_or_zero(item.get("system_state_count", 243)) or 243 for item in items]
        target_min = mean(0.05 * count for count in state_counts)
        target_max = mean(0.30 * count for count in state_counts)
        effective_mean = mean(effective) if effective else 0.0
        usable_rate = rate(item.get("probe_resolution_regime") == "usable_quotient" for item in items)
        identity_rate = rate(item.get("probe_resolution_regime") == "identity_like_control" for item in items)
        collision_rate = mean(float_or_zero(item.get("probe_collision_rate")) for item in items)
        out.append({
            "preflight_context": context,
            "probe_key": probe,
            "probe_axis": axis,
            "rows": len(items),
            "theoretical_alphabet_size": mean(float_or_zero(item.get("probe_signature_alphabet_size")) for item in items),
            "observed_effective_signature_count": effective_mean,
            "expected_effective_min": target_min,
            "expected_effective_max": target_max,
            "expected_alphabet_verdict": alphabet_verdict(effective_mean, target_min, target_max, mean(0.50 * count for count in state_counts)),
            "usable_quotient_rate": usable_rate,
            "collision_rate": collision_rate,
            "average_bucket_size": mean_present(items, "average_bucket_size"),
            "median_bucket_size": mean_present(items, "median_bucket_size"),
            "singleton_bucket_fraction": mean_present(items, "singleton_bucket_fraction"),
            "entropy_ceiling_fraction": mean(float_or_zero(item.get("signature_entropy_ceiling_fraction")) for item in items),
            "identity_like_score": mean(float_or_zero(item.get("identity_like_score")) for item in items),
            "support_floor_rate": rate(item.get("probe_resolution_regime") == "support_floor_sparse" for item in items),
            "support_ceiling_rate": rate(item.get("probe_resolution_regime") == "support_ceiling_saturated" for item in items),
            "preflight_probe_verdict": preflight_probe_verdict(usable_rate, identity_rate, collision_rate, effective_mean, target_min, target_max),
        })
    return out


def sparse_frontier_probe_viability(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    sparse = [row for row in rows if row.get("probe_resolution_regime") == "support_floor_sparse"]
    out = []
    for (context, probe, axis), items in group_by(sparse, ("preflight_context", "probe_key", "probe_axis")).items():
        out.append({
            "preflight_context": context,
            "probe_key": probe,
            "probe_axis": axis,
            "sparse_rows": len(items),
            "sparse_frontier_rate_within_sparse_set": len(items) / max(1, len(sparse)),
            "mean_effective_signature_count": mean(float_or_zero(item.get("effective_signature_count")) for item in items),
            "mean_collision_rate": mean(float_or_zero(item.get("probe_collision_rate")) for item in items),
            "matched_sparse_controls_required": 1,
            "ordinary_detection_promotion_allowed": 0,
        })
    return out


def sparse_frontier_detection_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (probe,), items in group_by([row for row in rows if row.get("probe_resolution_regime") == "support_floor_sparse"], ("probe_key",)).items():
        out.append({
            "probe_key": probe,
            "sparse_rows": len(items),
            "sparse_regime_detection_status": "not_promotable_in_phase_a",
            "reason": "Phase A only measures sparse-frontier prevalence; matched sparse controls are required before detection claims.",
        })
    return out


def threshold_selection_audit(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for profile, config in THRESHOLDS.items():
        profile_rows = []
        for row in rows:
            item = dict(row)
            item["profile_regime"] = resolution_regime(item, config)
            profile_rows.append(item)
        design = [row for row in profile_rows if row.get("preflight_context") == "design_recurrent_boundary"]
        holdout: list[dict[str, object]] = []
        out.append({
            "threshold_profile": profile,
            "candidate_count_design": "not_scored_in_phase_a",
            "candidate_count_holdout": "not_run_in_phase_a",
            "usable_rate_design": rate(row.get("profile_regime") == "usable_quotient" for row in design),
            "usable_rate_holdout": "not_run_in_phase_a",
            "identity_leakage_design": rate(row.get("profile_regime") == "identity_like_control" for row in design),
            "identity_leakage_holdout": "not_run_in_phase_a",
            "selected_as_primary": int(profile == "default"),
            "selection_reason": "pre_registered_default; no optimization against candidate count",
            "holdout_rows": len(holdout),
        })
    return out


def instrumentation_multiplicity_audit(probes: tuple[str, ...], split_rows: list[dict[str, object]], rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{
        "probe_count": len(probes),
        "axis_count": len({PROBE_AXES.get(probe, "unknown_axis") for probe in probes}),
        "threshold_profile_count": len(THRESHOLDS),
        "recurrence_gate_count": 0,
        "group_count": len(split_rows),
        "candidate_decision_count": 0,
        "matched_control_decision_count": 0,
        "preflight_row_count": len(rows),
        "note": "Phase A preflight only; no discovery/candidate decision made.",
    }]


def axis_gate_summary(preflight: list[dict[str, object]], gate_name: str) -> list[dict[str, object]]:
    passed = [row for row in preflight if row.get("preflight_probe_verdict") == "pass_viability_preflight" and row.get("preflight_context") == "design_recurrent_boundary"]
    axes = {str(row.get("probe_axis")) for row in passed if row.get("probe_axis") not in {"identity_axis", "low_projection_axis"}}
    existing = axes.intersection({"constraint_axis", "cross_constraint_degree_axis"})
    new = axes.intersection({"constraint_gradient_axis", "degree_rank_axis", "frontier_dynamics_axis", "cycle_structure_axis", "wiring_role_axis"})
    if gate_name == "available_axis_gate":
        gate_pass = len(axes) >= 2
        criterion = "at least two non-identity usable axes pass preflight"
    else:
        gate_pass = bool(existing and new) or len(new) >= 2
        criterion = "existing usable axis plus viable new quotient axis, or two viable new quotient axes"
    return [{
        "gate_name": gate_name,
        "gate_pass": int(gate_pass),
        "criterion": criterion,
        "passing_axes": json.dumps(sorted(axes)),
        "passing_axis_count": len(axes),
        "design_preflight_probe_rows_considered": len(passed),
    }]


def annotate_bucket_stats(row: dict[str, object]) -> None:
    missing = []
    for field in ("average_bucket_size", "median_bucket_size", "min_bucket_size", "singleton_bucket_fraction"):
        if not metric_available(row.get(field, "")):
            row[field] = ""
            missing.append(field)
    row["bucket_stats_available"] = int(not missing)
    row["bucket_stats_missing_reason"] = "none" if not missing else "missing:" + ",".join(missing)
    row["support_fraction"] = float_or_zero(row.get("reachable_signature_support_fraction"))
    row["effective_signature_count"] = int(float_or_zero(row.get("effective_signature_count", row.get("reachable_signature_support_size"))))
    row["system_state_count"] = 243
    row["identity_like_score"] = identity_like_score(row)


def identity_like_score(row: dict[str, object]) -> float:
    components = []
    if metric_available(row.get("singleton_bucket_fraction")):
        components.append(float_or_zero(row.get("singleton_bucket_fraction")))
    if metric_available(row.get("average_bucket_size")):
        components.append(max(0.0, min(1.0, (3.0 - float_or_zero(row.get("average_bucket_size"))) / 3.0)))
    if metric_available(row.get("signature_entropy_ceiling_fraction")):
        components.append(float_or_zero(row.get("signature_entropy_ceiling_fraction")))
    return max(components) if components else 0.0


def probe_role(probe_key: str) -> str:
    if probe_key == "full_state_hash":
        return "identity_control"
    if probe_key == "existing_low":
        return "diagnostic"
    return "pre_registered_candidate_instrument"


def alphabet_verdict(effective: float, target_min: float, target_max: float, identity_risk: float) -> str:
    if effective < target_min:
        return "likely_too_coarse"
    if effective > identity_risk:
        return "identity_risk"
    if effective <= target_max:
        return "target_range"
    return "high_resolution_watch"


def preflight_probe_verdict(usable_rate: float, identity_rate: float, collision_rate: float, effective: float, target_min: float, target_max: float) -> str:
    if usable_rate <= 0:
        return "fail_no_usable_quotient_rows"
    if identity_rate > 0.25:
        return "fail_identity_risk"
    if collision_rate >= 0.95 or effective < target_min:
        return "fail_too_coarse"
    if effective > target_max * 1.75:
        return "watch_high_resolution"
    return "pass_viability_preflight"


def mean_present(rows: list[dict[str, object]], field: str) -> float | str:
    values = [float_or_zero(row.get(field)) for row in rows if metric_available(row.get(field, ""))]
    return mean(values) if values else ""


def rate(values: object) -> float:
    items = list(values)
    return sum(int(value) for value in items) / max(1, len(items))


def write_viability_summary(out_dir: Path, preflight: list[dict[str, object]], sparse: list[dict[str, object]], available_gate: list[dict[str, object]], quotient_gate: list[dict[str, object]]) -> None:
    verdict_counts = Counter(str(row.get("preflight_probe_verdict", "")) for row in preflight)
    lines = [
        "# RFS-MB0 Instrumentation Phase A Viability Summary",
        "",
        "Phase A is preflight-only. No candidate promotion, holdout scoring, or discovery claim was made.",
        "",
        f"Verdicts: {dict(sorted(verdict_counts.items()))}",
        f"Available-axis gate: {available_gate[0].get('gate_pass') if available_gate else ''}",
        f"New-quotient-axis gate: {quotient_gate[0].get('gate_pass') if quotient_gate else ''}",
        "",
        "## Probe Summary",
        "",
        table(preflight, ("preflight_context", "probe_key", "probe_axis", "usable_quotient_rate", "collision_rate", "expected_alphabet_verdict", "preflight_probe_verdict")),
        "",
        "## Sparse Frontier",
        "",
        table(sparse, ("preflight_context", "probe_key", "sparse_rows", "mean_collision_rate", "ordinary_detection_promotion_allowed")),
    ]
    (out_dir / "probe_viability_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_pivot_report(out_dir: Path, status: dict[str, object], preflight: list[dict[str, object]], sparse: list[dict[str, object]], threshold: list[dict[str, object]], available_gate: list[dict[str, object]], quotient_gate: list[dict[str, object]]) -> None:
    lines = [
        "# RFS-MB0 Instrumentation Branch Pivot Report",
        "",
        "This run treats MB0 as an instrumentation problem. It asks whether the current probe panel can serve as a reliable instrument before any scaled search or holdout detection.",
        "",
        "## Claim Boundary",
        "",
        "No candidate detection, identity classification, agent classification, or discovery claim is made here.",
        "",
        "## Phase A Result",
        "",
        f"Status: `{status.get('status')}`. Jobs: {status.get('jobs_completed')}/{status.get('jobs_requested')}. Rows: {status.get('row_count')}. Errors: {status.get('errors')}.",
        "",
        "## Axis Gates",
        "",
        table(available_gate + quotient_gate, ("gate_name", "gate_pass", "passing_axis_count", "passing_axes")),
        "",
        "## Threshold Audit",
        "",
        table(threshold, ("threshold_profile", "usable_rate_design", "identity_leakage_design", "selected_as_primary", "selection_reason")),
        "",
        "## Decision",
        "",
        decision(preflight, available_gate, quotient_gate),
        "",
        "## Output Manifest",
        "",
        "See `output_manifest.json`.",
    ]
    (out_dir / "rfs_mb0_instrumentation_branch_pivot_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def decision(preflight: list[dict[str, object]], available_gate: list[dict[str, object]], quotient_gate: list[dict[str, object]]) -> str:
    if available_gate and int(available_gate[0].get("gate_pass", 0)) and quotient_gate and int(quotient_gate[0].get("gate_pass", 0)):
        return "Phase A passes enough instrumentation viability to consider a small frozen-threshold Phase B design-set run."
    passing = [row for row in preflight if row.get("preflight_probe_verdict") == "pass_viability_preflight"]
    if passing:
        return "Some probes passed viability, but axis-gate coverage is insufficient. Tighten or add probes before Phase B."
    return "Phase A does not support candidate detection. Return to probe design before Phase B."


def table(rows: list[dict[str, object]], fields: tuple[str, ...], limit: int = 20) -> str:
    if not rows:
        return "_No rows._"
    lines = ["|" + "|".join(fields) + "|", "|" + "|".join("---" for _ in fields) + "|"]
    for row in rows[:limit]:
        lines.append("|" + "|".join(str(row.get(field, "")) for field in fields) + "|")
    if len(rows) > limit:
        lines.append(f"\n_Showing {limit} of {len(rows)} rows._")
    return "\n".join(lines)


def write_manifest(out_dir: Path) -> None:
    manifest = []
    for name in OUTPUTS:
        path = out_dir / name
        exists = True if name == "output_manifest.json" else path.exists()
        manifest.append({"file": name, "exists": exists, "status": "present" if exists else "missing", "row_count": csv_row_count(path) if path.suffix == ".csv" else ""})
    (out_dir / "output_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def csv_row_count(path: Path) -> int:
    if not path.exists() or path.suffix != ".csv":
        return 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if not rows or rows[0] == ["empty"]:
        return 0
    return max(0, len(rows) - 1)


if __name__ == "__main__":
    main()
