from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from statistics import mean, pstdev

from .run_deformation_detector_sweep import run_sweep_job
from .run_focused_boundary_recurrence import (
    apply_variant,
    candidate_like,
    combined_row_score,
    float_or_zero,
    group_by,
    read_csv,
    write_csv,
)
from .run_deformation_detector_sweep import params_from_parameter_set_id, stable_seed


PROBE_AXES = {
    "coordinate_tuple_k3": "coordinate_axis",
    "coordinate_tuple_k4": "coordinate_axis",
    "constraint_profile_hash": "constraint_axis",
    "constraint_violation_count_plus_local_tuple": "constraint_axis",
    "constraint_neighborhood_histogram": "constraint_neighborhood_axis",
    "relation_neighborhood_degree_asymmetry_histogram": "relation_geometry_axis",
    "frontier_response_bucket": "frontier_response_axis",
    "motif_count_bucket": "relation_motif_axis",
    "multi_scale_support_region_bucket": "support_growth_axis",
    "existing_low": "low_projection_axis",
    "full_state_hash": "identity_axis",
    "full_state_strict": "identity_axis",
}
NEW_QUOTIENT_AXES = {
    "constraint_neighborhood_axis",
    "relation_geometry_axis",
    "frontier_response_axis",
    "relation_motif_axis",
    "support_growth_axis",
}
EXISTING_REPAIRED_AXES = {"coordinate_axis", "constraint_axis"}
OUTPUTS = (
    "boundary_deformation_guardrail_report.md",
    "probe_resolution_threshold_config.json",
    "probe_resolution_threshold_sweep.csv",
    "probe_resolution_guardrail_rows.csv",
    "probe_resolution_regime_summary.csv",
    "quotient_probe_metric_rows.csv",
    "quotient_probe_family_summary.csv",
    "identity_leakage_audit.csv",
    "path_dependence_profile.csv",
    "matched_recurrence_controls.csv",
    "matched_recurrence_excess.csv",
    "fractional_recurrence_summary.csv",
    "independent_probe_axis_summary.csv",
    "corrected_boundary_detection_summary.csv",
    "errors.csv",
    "output_manifest.json",
    "status.json",
)
THRESHOLDS = {
    "strict": {
        "identity_like": {"singleton_bucket_fraction": 0.35, "average_bucket_size": 1.50, "entropy_ceiling_fraction": 0.90},
        "high_resolution_watch": {"singleton_bucket_fraction": 0.20, "average_bucket_size": 3.00, "entropy_ceiling_fraction": 0.75},
        "too_coarse_collision": {"collision_rate": 0.85, "effective_signature_count_min_fraction": 0.05},
    },
    "default": {
        "identity_like": {"singleton_bucket_fraction": 0.50, "average_bucket_size": 1.50, "entropy_ceiling_fraction": 0.90},
        "high_resolution_watch": {"singleton_bucket_fraction": 0.25, "average_bucket_size": 3.00, "entropy_ceiling_fraction": 0.75},
        "too_coarse_collision": {"collision_rate": 0.90, "effective_signature_count_min_fraction": 0.05},
    },
    "lenient": {
        "identity_like": {"singleton_bucket_fraction": 0.65, "average_bucket_size": 1.50, "entropy_ceiling_fraction": 0.90},
        "high_resolution_watch": {"singleton_bucket_fraction": 0.35, "average_bucket_size": 3.00, "entropy_ceiling_fraction": 0.75},
        "too_coarse_collision": {"collision_rate": 0.95, "effective_signature_count_min_fraction": 0.05},
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 boundary deformation guardrail and quotient probe audit.")
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--corrected", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/corrected_group_classification.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_deformation_guardrail_smoke"))
    parser.add_argument("--groups", type=int, default=4)
    parser.add_argument("--include-weak-controls", action="store_true")
    parser.add_argument("--fresh-seeds-per-group", type=int, default=2)
    parser.add_argument("--start-samples-list", type=str, default="3,8")
    parser.add_argument("--horizons", type=str, default="0,1,2,4,8,12,16,24,32")
    parser.add_argument(
        "--probe-families",
        type=str,
        default=(
            "coordinate_tuple_k3,coordinate_tuple_k4,constraint_profile_hash,"
            "constraint_violation_count_plus_local_tuple,constraint_neighborhood_histogram,"
            "relation_neighborhood_degree_asymmetry_histogram,frontier_response_bucket,"
            "motif_count_bucket,multi_scale_support_region_bucket,existing_low,full_state_hash"
        ),
    )
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--job-batch-size", type=int, default=8)
    parser.add_argument("--max-runtime-seconds", type=int, default=1800)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=120)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    groups = select_groups(args)
    anchors = {row.get("anchor_id", ""): row for row in read_csv(args.source_run / "atlas_band_selection.csv")}
    starts = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    horizons = tuple(int(item.strip()) for item in args.horizons.split(",") if item.strip())
    probes = tuple(item.strip() for item in args.probe_families.split(",") if item.strip())
    jobs = build_jobs(groups, anchors, starts, horizons, probes, args.fresh_seeds_per_group)
    status: dict[str, object] = {
        "status": "RUNNING",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workers": args.workers,
        "groups_selected": len(groups),
        "jobs_requested": len(jobs),
        "jobs_submitted": 0,
        "jobs_completed": 0,
        "jobs_cancelled": 0,
        "pending_jobs_remaining": len(jobs),
        "max_runtime_seconds": args.max_runtime_seconds,
        "shutdown_cushion_seconds": args.shutdown_cushion_seconds,
        "promotion_enabled": False,
        "n6_transfer": False,
    }
    job_batches = [jobs[index : index + max(1, args.job_batch_size)] for index in range(0, len(jobs), max(1, args.job_batch_size))]
    status["job_batch_size"] = max(1, args.job_batch_size)
    status["job_batches_requested"] = len(job_batches)
    rows, errors = run_job_batches(args, job_batches, status, started)
    if status["status"] == "RUNNING":
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "all_jobs_completed"
    write_outputs(args.out, status, started, groups, rows, errors)


def select_groups(args: argparse.Namespace) -> list[dict[str, str]]:
    selected = {row.get("group_id", ""): row for row in read_csv(args.selection)}
    corrected = read_csv(args.corrected)
    priority = ["independent_axis_recurrent_but_collision_limited"]
    if args.include_weak_controls:
        priority.append("weak_control_bundle_recurrence")
    rows = []
    for klass in priority:
        for row in corrected:
            group_id = row.get("group_id", "")
            if row.get("corrected_group_class") == klass and group_id in selected:
                merged = dict(selected[group_id])
                merged["prior_corrected_group_class"] = klass
                rows.append(merged)
                if len(rows) >= args.groups:
                    return rows
    return rows[: args.groups]


def build_jobs(groups: list[dict[str, str]], anchors: dict[str, dict[str, str]], starts: tuple[int, ...], horizons: tuple[int, ...], probes: tuple[str, ...], fresh_seeds: int) -> list[dict[str, object]]:
    jobs = []
    for group_index, group in enumerate(groups):
        anchor = anchors.get(group.get("source_anchor_id", group.get("source_band_id", "")), {})
        params = params_from_parameter_set_id(anchor.get("parameter_set_id", ""))
        if params is None:
            continue
        variant_params = apply_variant(params, group.get("variant_dimension", ""), group.get("variant_value", ""))
        base_seed = int(anchor.get("seed") or stable_seed(anchor.get("environment_id", group.get("group_id", ""))))
        for seed_index in range(fresh_seeds):
            seed = base_seed + 50_021 * (seed_index + 1) + group_index
            for probe in probes:
                for start_count in starts:
                    jobs.append(
                        {
                            "job_id": f"guardrail_{group_index:03d}_{seed_index}_{probe}_{start_count}",
                            "anchor_id": group.get("source_band_id", ""),
                            "anchor_environment_id": anchor.get("environment_id", ""),
                            "anchor_primary_class": anchor.get("anchor_primary_class", ""),
                            "variant_dimension": group.get("variant_dimension", ""),
                            "variant_value": group.get("variant_value", ""),
                            "params": variant_params,
                            "seed": seed,
                            "probe_key": probe,
                            "source_probe_family": anchor.get("source_probe_family", anchor.get("anchor_probe_family", "")),
                            "start_samples": start_count,
                            "horizons": horizons,
                            "group_id": group.get("group_id", ""),
                            "prior_corrected_group_class": group.get("prior_corrected_group_class", ""),
                        }
                    )
    return jobs


def run_job_batches(args: argparse.Namespace, job_batches: list[list[dict[str, object]]], status: dict[str, object], started: float) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    pending = list(job_batches)
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
                futures[executor.submit(run_sweep_job_batch, batch)] = batch
                status["jobs_submitted"] = int(status["jobs_submitted"]) + len(batch)
            done, _ = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                batch = futures.pop(future)
                batch_rows, batch_errors, completed = future.result()
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


def run_sweep_job_batch(jobs: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], int]:
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    completed = 0
    for job in jobs:
        try:
            for row in run_sweep_job(job):
                row["group_id"] = job.get("group_id", "")
                row["prior_corrected_group_class"] = job.get("prior_corrected_group_class", "")
                row["probe_axis"] = PROBE_AXES.get(str(row.get("probe_key", "")), "unknown_axis")
                row["probe_role"] = probe_role(str(row.get("probe_key", "")))
                row["detection_candidate_flag"] = int(candidate_like(row))
                row.update(default_guardrail_fields(row))
                rows.append(row)
        except Exception as exc:  # noqa: BLE001
            errors.append({"job_id": job.get("job_id", ""), "error": repr(exc)})
        completed += 1
    return rows, errors, completed


def write_outputs(out_dir: Path, status: dict[str, object], started: float, groups: list[dict[str, str]], rows: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    threshold_rows = threshold_sweep_rows(rows)
    guardrail_rows = [row for row in threshold_rows if row.get("threshold_profile") == "default"]
    metric_rows = quotient_metric_rows(rows, guardrail_rows)
    regime_summary = probe_resolution_regime_summary(threshold_rows)
    family_summary = quotient_probe_family_summary(metric_rows)
    identity = identity_leakage_audit(metric_rows)
    path = path_dependence_profile(metric_rows)
    controls = matched_recurrence_controls(metric_rows)
    excess = matched_recurrence_excess(path, controls)
    fractional = fractional_recurrence_summary(metric_rows, excess)
    axes = independent_probe_axis_summary(metric_rows)
    corrected = corrected_boundary_detection_summary(fractional, axes, identity, excess)
    status["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    status["metric_rows"] = len(metric_rows)
    status["errors"] = len(errors)
    write_csv(out_dir / "probe_resolution_threshold_sweep.csv", threshold_rows)
    write_csv(out_dir / "probe_resolution_guardrail_rows.csv", guardrail_rows)
    write_csv(out_dir / "probe_resolution_regime_summary.csv", regime_summary)
    write_csv(out_dir / "quotient_probe_metric_rows.csv", metric_rows)
    write_csv(out_dir / "quotient_probe_family_summary.csv", family_summary)
    write_csv(out_dir / "identity_leakage_audit.csv", identity)
    write_csv(out_dir / "path_dependence_profile.csv", path)
    write_csv(out_dir / "matched_recurrence_controls.csv", controls)
    write_csv(out_dir / "matched_recurrence_excess.csv", excess)
    write_csv(out_dir / "fractional_recurrence_summary.csv", fractional)
    write_csv(out_dir / "independent_probe_axis_summary.csv", axes)
    write_csv(out_dir / "corrected_boundary_detection_summary.csv", corrected)
    write_csv(out_dir / "errors.csv", errors)
    (out_dir / "probe_resolution_threshold_config.json").write_text(json.dumps(THRESHOLDS, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    write_manifest(out_dir)
    write_report(out_dir, status, groups, regime_summary, family_summary, identity, fractional, axes, corrected)


def threshold_sweep_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    by_key: dict[tuple[object, ...], dict[str, str]] = {}
    for row in rows:
        regimes = {profile: resolution_regime(row, config) for profile, config in THRESHOLDS.items()}
        stability = threshold_stability(regimes)
        by_key[(row.get("group_id"), row.get("probe_key"), row.get("seed"), row.get("start_samples"), row.get("start_index"), row.get("H"))] = regimes
        for profile, regime in regimes.items():
            out_row = dict(row)
            out_row["threshold_profile"] = profile
            out_row["probe_resolution_regime"] = regime
            out_row["threshold_stability_class"] = stability
            out_row[f"probe_regime_under_{profile}"] = regime
            out.append(out_row)
    for out_row in out:
        regimes = by_key[(out_row.get("group_id"), out_row.get("probe_key"), out_row.get("seed"), out_row.get("start_samples"), out_row.get("start_index"), out_row.get("H"))]
        for profile, regime in regimes.items():
            out_row[f"probe_regime_under_{profile}"] = regime
    return out


def quotient_metric_rows(rows: list[dict[str, object]], guardrail_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    regime_by_key = {
        (row.get("group_id"), row.get("probe_key"), row.get("seed"), row.get("start_samples"), row.get("start_index"), row.get("H")): row
        for row in guardrail_rows
    }
    out = []
    for row in rows:
        key = (row.get("group_id"), row.get("probe_key"), row.get("seed"), row.get("start_samples"), row.get("start_index"), row.get("H"))
        guard = regime_by_key.get(key, {})
        metric = dict(row)
        metric["probe_resolution_regime"] = guard.get("probe_resolution_regime", "")
        metric["threshold_stability_class"] = guard.get("threshold_stability_class", "")
        metric["classification_status"] = "classification_not_attempted"
        metric["detection_status"] = detection_status(metric)
        metric["row_score"] = combined_row_score(metric)
        out.append(metric)
    return out


def default_guardrail_fields(row: dict[str, object]) -> dict[str, object]:
    row["effective_signature_count"] = int(float_or_zero(row.get("effective_signature_count", row.get("reachable_signature_support_size"))))
    row["average_bucket_size"] = float_or_zero(row.get("average_bucket_size")) or (float_or_zero(row.get("frontier_size")) / max(1.0, float_or_zero(row.get("effective_signature_count"))))
    row["median_bucket_size"] = float_or_zero(row.get("median_bucket_size"))
    row["min_bucket_size"] = float_or_zero(row.get("min_bucket_size"))
    row["singleton_bucket_fraction"] = float_or_zero(row.get("singleton_bucket_fraction"))
    row["support_fraction"] = float_or_zero(row.get("reachable_signature_support_fraction"))
    row["identity_like_score"] = identity_like_score(row)
    return {}


def resolution_regime(row: dict[str, object], threshold: dict[str, dict[str, float]]) -> str:
    support = float_or_zero(row.get("support_fraction", row.get("reachable_signature_support_fraction")))
    if support <= 0.05:
        return "support_floor_sparse"
    if support >= 0.90:
        return "support_ceiling_saturated"
    effective_fraction = float_or_zero(row.get("effective_signature_count")) / max(1.0, float_or_zero(row.get("probe_signature_alphabet_size")))
    if float_or_zero(row.get("probe_collision_rate")) >= threshold["too_coarse_collision"]["collision_rate"] or effective_fraction < threshold["too_coarse_collision"]["effective_signature_count_min_fraction"]:
        return "too_coarse_collision"
    identity = threshold["identity_like"]
    if (
        float_or_zero(row.get("singleton_bucket_fraction")) >= identity["singleton_bucket_fraction"]
        or float_or_zero(row.get("average_bucket_size")) <= identity["average_bucket_size"]
        or float_or_zero(row.get("signature_entropy_ceiling_fraction")) >= identity["entropy_ceiling_fraction"]
        or row.get("probe_axis") == "identity_axis"
    ):
        return "identity_like_control"
    watch = threshold["high_resolution_watch"]
    if (
        float_or_zero(row.get("singleton_bucket_fraction")) >= watch["singleton_bucket_fraction"]
        or float_or_zero(row.get("average_bucket_size")) <= watch["average_bucket_size"]
        or float_or_zero(row.get("signature_entropy_ceiling_fraction")) >= watch["entropy_ceiling_fraction"]
    ):
        return "high_resolution_watch"
    return "usable_quotient"


def threshold_stability(regimes: dict[str, str]) -> str:
    values = set(regimes.values())
    if values == {"usable_quotient"}:
        return "stable_usable_quotient"
    if regimes.get("strict") == "high_resolution_watch" and regimes.get("default") == "usable_quotient":
        return "strict_watch_default_usable"
    if regimes.get("lenient") == "usable_quotient" and regimes.get("default") != "usable_quotient":
        return "lenient_only_usable"
    if values == {"too_coarse_collision"}:
        return "stable_collision_limited"
    if values == {"identity_like_control"}:
        return "stable_identity_like"
    return "threshold_fragile"


def probe_resolution_regime_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (profile, regime), items in group_by(rows, ("threshold_profile", "probe_resolution_regime")).items():
        out.append({"threshold_profile": profile, "probe_resolution_regime": regime, "rows": len(items), "candidate_rate": rate(candidate_like(item) for item in items)})
    return out


def quotient_probe_family_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (probe, axis), items in group_by(rows, ("probe_key", "probe_axis")).items():
        usable = [item for item in items if item.get("probe_resolution_regime") == "usable_quotient"]
        out.append({
            "probe_key": probe,
            "probe_axis": axis,
            "rows": len(items),
            "usable_quotient_rate": len(usable) / max(1, len(items)),
            "candidate_rate": rate(candidate_like(item) for item in usable),
            "mean_identity_like_score": mean(float_or_zero(item.get("identity_like_score")) for item in items),
            "mean_collision_rate": mean(float_or_zero(item.get("probe_collision_rate")) for item in items),
        })
    return out


def identity_leakage_audit(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (group_id,), items in group_by(rows, ("group_id",)).items():
        candidate_rows = [item for item in items if candidate_like(item)]
        usable_candidates = [item for item in candidate_rows if item.get("probe_resolution_regime") == "usable_quotient"]
        high_or_identity = [item for item in candidate_rows if item.get("probe_resolution_regime") in {"high_resolution_watch", "identity_like_control"} or item.get("probe_axis") == "identity_axis"]
        out.append({
            "group_id": group_id,
            "identity_leakage_score": len(high_or_identity) / max(1, len(candidate_rows)),
            "identity_like_probe_dependency": int(bool(candidate_rows) and not usable_candidates),
            "usable_quotient_probe_dependency": int(bool(usable_candidates)),
            "classification_if_identity_like_probes_excluded": group_detection_class(usable_candidates),
            "classification_if_high_resolution_watch_excluded": group_detection_class(usable_candidates),
            "classification_using_only_usable_quotient_probes": group_detection_class(usable_candidates),
        })
    return out


def path_dependence_profile(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (group_id,), items in group_by(rows, ("group_id",)).items():
        usable_candidates = [item for item in items if item.get("probe_resolution_regime") == "usable_quotient" and candidate_like(item)]
        starts = {str(item.get("start_index")) for item in items}
        seeds = {str(item.get("seed")) for item in items}
        horizons = {str(item.get("H")) for item in items}
        axes = {str(item.get("probe_axis")) for item in usable_candidates}
        out.append({
            "group_id": group_id,
            "start_recurrence_rate": coverage_rate(usable_candidates, "start_index", starts),
            "seed_recurrence_rate": coverage_rate(usable_candidates, "seed", seeds),
            "parameter_variant_recurrence_rate": 1.0 if usable_candidates else 0.0,
            "horizon_window_recurrence_rate": coverage_rate(usable_candidates, "H", horizons),
            "probe_axis_recurrence_rate": len(axes) / max(1, len({str(item.get("probe_axis")) for item in items if item.get("probe_role") == "quotient_evidence"})),
            "matched_recurrence_excess": "",
            "recurrence_percentile_vs_controls": "",
            "path_dependence_class": path_dependence_class(usable_candidates, starts, seeds, horizons, axes),
        })
    return out


def matched_recurrence_controls(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (group_id,), items in group_by(rows, ("group_id",)).items():
        observed = recurrence_rate(items, candidate=True, usable=True)
        controls = []
        controls.append(("identity_like_controls", recurrence_rate([item for item in items if item.get("probe_axis") == "identity_axis"], candidate=True, usable=False)))
        controls.append(("probe_marginal_controls", recurrence_rate([item for item in items if item.get("probe_resolution_regime") != "usable_quotient"], candidate=True, usable=False)))
        controls.append(("frontier_size_matched_controls", recurrence_rate([item for item in items if float_or_zero(item.get("frontier_size")) <= mean(float_or_zero(x.get("frontier_size")) for x in items)], candidate=True, usable=False)))
        control_values = [value for _name, value in controls]
        out.append({
            "group_id": group_id,
            "observed_recurrence_rate": observed,
            "matched_control_recurrence_mean": mean(control_values) if control_values else 0.0,
            "matched_control_recurrence_std": pstdev(control_values) if len(control_values) > 1 else 0.0,
            "matched_recurrence_excess": observed - (mean(control_values) if control_values else 0.0),
            "recurrence_percentile_vs_controls": percentile(observed, control_values),
            "control_count": len(control_values),
            "weak_recurrence_control_flag": int(len(control_values) < 3),
            "control_bundle_json": json.dumps(dict(controls), sort_keys=True),
        })
    return out


def matched_recurrence_excess(path_rows: list[dict[str, object]], control_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    controls = {row.get("group_id"): row for row in control_rows}
    out = []
    for row in path_rows:
        control = controls.get(row.get("group_id"), {})
        out_row = dict(row)
        out_row["matched_recurrence_excess"] = control.get("matched_recurrence_excess", 0.0)
        out_row["recurrence_percentile_vs_controls"] = control.get("recurrence_percentile_vs_controls", 0.0)
        out.append(out_row)
    return out


def fractional_recurrence_summary(rows: list[dict[str, object]], excess_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    excess = {row.get("group_id"): row for row in excess_rows}
    out = []
    for (group_id,), items in group_by(rows, ("group_id",)).items():
        usable_candidate = [item for item in items if item.get("probe_resolution_regime") == "usable_quotient" and candidate_like(item)]
        ex = excess.get(group_id, {})
        out.append({
            "group_id": group_id,
            "usable_quotient_candidate_rate": len(usable_candidate) / max(1, len(items)),
            "seed_recurrence_rate": coverage_rate(usable_candidate, "seed", {str(item.get("seed")) for item in items}),
            "start_recurrence_rate": coverage_rate(usable_candidate, "start_index", {str(item.get("start_index")) for item in items}),
            "horizon_window_recurrence_rate": coverage_rate(usable_candidate, "H", {str(item.get("H")) for item in items}),
            "matched_recurrence_excess": ex.get("matched_recurrence_excess", 0.0),
            "recurrence_percentile_vs_controls": ex.get("recurrence_percentile_vs_controls", 0.0),
        })
    return out


def independent_probe_axis_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (group_id,), items in group_by(rows, ("group_id",)).items():
        usable_candidate = [item for item in items if item.get("probe_resolution_regime") == "usable_quotient" and candidate_like(item)]
        axes = {str(item.get("probe_axis")) for item in usable_candidate}
        out.append({
            "group_id": group_id,
            "usable_candidate_axes": json.dumps(sorted(axes)),
            "usable_candidate_axis_count": len(axes),
            "has_existing_repaired_axis": int(bool(axes.intersection(EXISTING_REPAIRED_AXES))),
            "has_new_quotient_axis": int(bool(axes.intersection(NEW_QUOTIENT_AXES))),
            "has_two_new_quotient_axes": int(len(axes.intersection(NEW_QUOTIENT_AXES)) >= 2),
            "independent_probe_axis_gate_pass": int((bool(axes.intersection(EXISTING_REPAIRED_AXES)) and bool(axes.intersection(NEW_QUOTIENT_AXES))) or len(axes.intersection(NEW_QUOTIENT_AXES)) >= 2),
        })
    return out


def corrected_boundary_detection_summary(fractional: list[dict[str, object]], axes: list[dict[str, object]], identity: list[dict[str, object]], excess: list[dict[str, object]]) -> list[dict[str, object]]:
    axis_by_group = {row.get("group_id"): row for row in axes}
    identity_by_group = {row.get("group_id"): row for row in identity}
    excess_by_group = {row.get("group_id"): row for row in excess}
    out = []
    for row in fractional:
        group_id = row.get("group_id", "")
        axis = axis_by_group.get(group_id, {})
        leak = identity_by_group.get(group_id, {})
        ex = excess_by_group.get(group_id, {})
        klass = classify_group(row, axis, leak, ex)
        out.append({
            "group_id": group_id,
            "corrected_boundary_detection_class": klass,
            "detection_status": detection_status_from_group_class(klass),
            "classification_status": "classification_not_attempted",
            "usable_quotient_candidate_rate": row.get("usable_quotient_candidate_rate", 0.0),
            "matched_recurrence_excess": row.get("matched_recurrence_excess", 0.0),
            "independent_probe_axis_gate_pass": axis.get("independent_probe_axis_gate_pass", 0),
            "identity_leakage_score": leak.get("identity_leakage_score", 0.0),
        })
    return out


def classify_group(row: dict[str, object], axis: dict[str, object], leak: dict[str, object], excess: dict[str, object]) -> str:
    if int(float_or_zero(leak.get("identity_like_probe_dependency"))) > 0:
        return "identity_leakage_dependent"
    if float_or_zero(row.get("usable_quotient_candidate_rate")) <= 0:
        return "collision_limited_under_all_quotient_probes"
    if int(float_or_zero(axis.get("independent_probe_axis_gate_pass"))) <= 0:
        return "underdetermined_after_guardrail_audit"
    if float_or_zero(excess.get("matched_recurrence_excess")) <= 0.02:
        return "quotient_resolved_but_matched_control_equivalent"
    if float_or_zero(row.get("seed_recurrence_rate")) >= 0.60 and float_or_zero(row.get("horizon_window_recurrence_rate")) >= 0.40:
        return "fractional_recurrent_above_controls"
    return "path_dependent_recurrent_above_controls"


def probe_role(probe_key: str) -> str:
    if probe_key in {"existing_low"}:
        return "diagnostic"
    if probe_key in {"full_state_hash", "full_state_strict"}:
        return "control"
    return "quotient_evidence"


def identity_like_score(row: dict[str, object]) -> float:
    singleton = float_or_zero(row.get("singleton_bucket_fraction"))
    avg = float_or_zero(row.get("average_bucket_size"))
    entropy = float_or_zero(row.get("signature_entropy_ceiling_fraction"))
    avg_component = max(0.0, min(1.0, (3.0 - avg) / 3.0))
    return max(singleton, avg_component, entropy)


def detection_status(row: dict[str, object]) -> str:
    if row.get("probe_resolution_regime") == "usable_quotient" and candidate_like(row):
        return "quotient_resolved_pending_controls"
    if row.get("probe_resolution_regime") == "too_coarse_collision":
        return "measurement_limited_collision"
    return "not_detected"


def detection_status_from_group_class(klass: str) -> str:
    if klass in {"fractional_recurrent_above_controls", "path_dependent_recurrent_above_controls", "quotient_resolved_recurrent_boundary_deformation"}:
        return "recurrent_boundary_deformation_detected"
    if "collision_limited" in klass or "measurement_limited" in klass:
        return "measurement_limited_collision"
    if "quotient_resolved" in klass:
        return "quotient_resolved_pending_controls"
    return "not_detected"


def recurrence_rate(items: list[dict[str, object]], candidate: bool, usable: bool) -> float:
    filtered = items
    if usable:
        filtered = [item for item in filtered if item.get("probe_resolution_regime") == "usable_quotient"]
    if candidate:
        filtered = [item for item in filtered if candidate_like(item)]
    return len(filtered) / max(1, len(items))


def group_detection_class(items: list[dict[str, object]]) -> str:
    return "quotient_resolved_pending_controls" if items else "not_detected"


def coverage_rate(items: list[dict[str, object]], key: str, universe: set[str]) -> float:
    return len({str(item.get(key)) for item in items}) / max(1, len(universe))


def path_dependence_class(items: list[dict[str, object]], starts: set[str], seeds: set[str], horizons: set[str], axes: set[str]) -> str:
    if not items:
        return "single_start_lucky"
    if len(axes) >= 2 and coverage_rate(items, "seed", seeds) >= 0.60 and coverage_rate(items, "H", horizons) >= 0.40:
        return "multi_axis_recurrent"
    if coverage_rate(items, "seed", seeds) >= 0.60:
        return "seed_recurrent"
    if coverage_rate(items, "start_index", starts) >= 0.50:
        return "basin_local"
    return "single_start_lucky"


def percentile(observed: float, controls: list[float]) -> float:
    if not controls:
        return 0.0
    return sum(int(observed >= value) for value in controls) / len(controls)


def rate(values: object) -> float:
    items = list(values)
    return sum(int(value) for value in items) / max(1, len(items))


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


def write_report(out_dir: Path, status: dict[str, object], groups: list[dict[str, str]], regime: list[dict[str, object]], family: list[dict[str, object]], identity: list[dict[str, object]], fractional: list[dict[str, object]], axes: list[dict[str, object]], corrected: list[dict[str, object]]) -> None:
    class_counts = Counter(str(row.get("corrected_boundary_detection_class", "")) for row in corrected)
    regime_counts = Counter(str(row.get("probe_resolution_regime", "")) for row in regime for _ in range(int(row.get("rows", 0))))
    lines = [
        "# RFS-MB0 Boundary Deformation Guardrail Audit",
        "",
        "## 1. Claim boundary",
        "",
        "This audit tests recurrent boundary deformation detection only. It does not classify identity-like or agent-like structures.",
        "",
        "## 2. Why this is detection improvement, not identity/agent classification",
        "",
        "The probe families are quotient-style measurements with explicit identity-leakage and threshold-stability guardrails. Identity-axis probes are controls.",
        "",
        "## 3. Threshold configuration and sweep results",
        "",
        f"Threshold profiles emitted: {', '.join(THRESHOLDS)}.",
        f"Rows by default/swept regime: {dict(sorted(regime_counts.items()))}.",
        "",
        "## 4. Probe-resolution regime summary",
        "",
        table_preview(regime, ("threshold_profile", "probe_resolution_regime", "rows", "candidate_rate")),
        "",
        "## 5. Quotient probe family performance",
        "",
        table_preview(family, ("probe_key", "probe_axis", "usable_quotient_rate", "candidate_rate", "mean_collision_rate")),
        "",
        "## 6. Identity leakage audit",
        "",
        table_preview(identity, ("group_id", "identity_leakage_score", "identity_like_probe_dependency", "usable_quotient_probe_dependency")),
        "",
        "## 7. Fractional recurrence and path-dependence profile",
        "",
        table_preview(fractional, ("group_id", "usable_quotient_candidate_rate", "seed_recurrence_rate", "horizon_window_recurrence_rate", "matched_recurrence_excess")),
        "",
        "## 8. Matched recurrence controls: luck versus recurrence",
        "",
        "Matched recurrence controls are reported in `matched_recurrence_controls.csv` and `matched_recurrence_excess.csv`.",
        "",
        "## 9. Matched-control separation",
        "",
        "Groups are not promoted unless usable quotient recurrence exceeds matched control recurrence and passes independent-axis gates.",
        "",
        "## 10. Group reclassification",
        "",
        f"Class counts: {dict(sorted(class_counts.items()))}.",
        table_preview(corrected, ("group_id", "corrected_boundary_detection_class", "detection_status", "identity_leakage_score")),
        "",
        "## 11. Decision",
        "",
        decision_text(class_counts),
        "",
        "## 12. Output manifest",
        "",
        f"Status: `{status.get('status')}`. Groups: {len(groups)}. Metric rows: {status.get('metric_rows')}. Errors: {status.get('errors')}.",
    ]
    (out_dir / "boundary_deformation_guardrail_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def table_preview(rows: list[dict[str, object]], fields: tuple[str, ...], limit: int = 12) -> str:
    if not rows:
        return "_No rows._"
    lines = ["|" + "|".join(fields) + "|", "|" + "|".join("---" for _ in fields) + "|"]
    for row in rows[:limit]:
        lines.append("|" + "|".join(str(row.get(field, "")) for field in fields) + "|")
    if len(rows) > limit:
        lines.append(f"\n_Showing {limit} of {len(rows)} rows._")
    return "\n".join(lines)


def decision_text(class_counts: Counter[str]) -> str:
    if class_counts.get("fractional_recurrent_above_controls", 0) or class_counts.get("quotient_resolved_recurrent_boundary_deformation", 0):
        return "Continue with a small confirmation pass; at least one group passed usable-quotient and control gates."
    if class_counts.get("collision_limited_under_all_quotient_probes", 0):
        return "Confirm or continue probing measurement limits; non-identity quotient probes remain collision-limited for at least part of the set."
    return "Do not scale yet; current result is underdetermined after guardrail audit."


if __name__ == "__main__":
    main()
