from __future__ import annotations

import argparse
import csv
import json
import math
import re
import time
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import replace
from pathlib import Path
from statistics import mean, pstdev

from .detectors import entropy_from_counts, js_divergence, smoothed_kl
from .landscape import exact_frontier, signature_distribution
from .relation_generator import RelationParams, generate_relation_system, generated_null_systems
from .run_path_metric_calibration import build_probe, probe_resolution_class
from .run_support_distribution_taxonomy import (
    TRIVIALITY_NULLS,
    SUPPORT_NULLS,
    append_tag,
    classify_pre_control,
    deformation_score,
    diagnostic_nulls,
    mass_concentration,
    params_from_metadata,
    slope,
    stabilization_horizon,
    saturation_horizon,
)


MARGIN_GRID = (0.00, 0.01, 0.02, 0.05, 0.10)
RANK_METRICS = (
    "support_deformation_score",
    "distribution_deformation_score",
    "mixed_deformation_score",
    "JS_to_triviality_nulls",
    "JS_to_support_nulls",
    "support_symmetric_difference_fraction",
    "support_growth_slope",
    "support_stabilization_H_numeric",
)
SWEEP_DIMENSIONS = (
    "constraint_density",
    "constraint_strength",
    "constraint_change_weight",
    "asymmetry_strength",
    "out_degree_target",
    "reversibility_fraction",
)
SWEEP_VALUES = {
    "constraint_density": (0.10, 0.25, 0.40),
    "constraint_strength": (0.5, 1.0, 2.0),
    "constraint_change_weight": (0.0, 0.35, 0.75),
    "asymmetry_strength": (0.0, 0.25, 0.5),
    "out_degree_target": (2, 3, 4),
    "reversibility_fraction": (0.0, 0.25, 0.5),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upgrade RFS-MB0 deformation detector and run local parameter sweeps.")
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260525_support_distribution_taxonomy_smoke"))
    parser.add_argument("--boundary-anchor-run", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260525_deformation_detector_sweep_validation"))
    parser.add_argument("--anchors", type=int, default=12)
    parser.add_argument("--fresh-seeds-per-variant", type=int, default=2)
    parser.add_argument("--start-samples-list", type=str, default="3,8")
    parser.add_argument("--horizons", type=str, default="0,1,2,4,8,12,16,24")
    parser.add_argument("--probe-families", type=str, default="coordinate_tuple_k3,coordinate_tuple_k4,constraint_profile_hash,constraint_violation_count_plus_local_tuple,existing_low,full_state_hash")
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-sweep-jobs", type=int, default=288)
    parser.add_argument("--checkpoint-every", type=int, default=36)
    parser.add_argument("--max-runtime-seconds", type=int, default=3600)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    metric_rows = _read_csv(args.source_run / "support_distribution_metric_by_horizon.csv")
    candidate_summary = _read_csv(args.source_run / "support_distribution_candidate_summary.csv")
    if not metric_rows or not candidate_summary:
        raise ValueError(f"source run is missing taxonomy outputs: {args.source_run}")
    anchors = select_boundary_anchors(args.boundary_anchor_run, args.anchors) if args.boundary_anchor_run else select_anchors(candidate_summary, metric_rows, args.anchors)
    matched_bundle = matched_control_bundle(metric_rows)
    rank_effect = rank_effect_summary(metric_rows, matched_bundle)
    margins = margin_sensitivity(rank_effect)
    separation = support_vs_distribution_rows(rank_effect)
    sweep_jobs = build_sweep_jobs(args, anchors)
    sweep_jobs = sweep_jobs[: args.max_sweep_jobs]
    config = {
        "status": "RUNNING",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "started_perf_counter": started,
        "workers": args.workers,
        "source_run": str(args.source_run),
        "anchors_requested": args.anchors,
        "anchors_selected": len(anchors),
        "sweep_jobs_requested": len(sweep_jobs),
        "fresh_seeds_per_variant": args.fresh_seeds_per_variant,
        "promotion_enabled": False,
    }
    _write_outputs(args.out, config, started, anchors, matched_bundle, rank_effect, margins, separation, [], [], [])
    sweep_rows, errors = run_sweep_jobs(args, sweep_jobs, config, started, anchors, matched_bundle, rank_effect, margins, separation)
    if config["status"] == "RUNNING":
        config["status"] = "COMPLETED"
    _write_outputs(args.out, config, started, anchors, matched_bundle, rank_effect, margins, separation, sweep_rows, errors, sweep_jobs)


def select_anchors(candidate_summary: list[dict[str, str]], metric_rows: list[dict[str, str]], target: int) -> list[dict[str, object]]:
    metric_by_key = {}
    for row in metric_rows:
        if row.get("row_kind") != "candidate":
            continue
        key = (row.get("candidate_environment_id"), row.get("probe_key"), row.get("start_samples"))
        metric_by_key.setdefault(key, row)
    if target <= 6:
        buckets = (
            ("mixed_support_distribution_candidate", 1),
            ("support_deformation_candidate", 1),
            ("matched_control_equivalent", 1),
            ("support_ceiling_limited", 1),
            ("probe_collision_limited", 1),
            ("underdetermined", 1),
        )
    else:
        buckets = (
            ("mixed_support_distribution_candidate", 3),
            ("support_deformation_candidate", 2),
            ("matched_control_equivalent", 3),
            ("support_ceiling_limited", 2),
            ("probe_collision_limited", 2),
            ("underdetermined", 2),
        )
    anchors = []
    used = set()
    for klass, count in buckets:
        rows = [row for row in candidate_summary if row.get("primary_class") == klass]
        rows.sort(key=lambda row: float(row.get("mean_deformation_score", 0.0) or 0.0), reverse=klass.endswith("_candidate"))
        for row in rows[:count]:
            key = (row.get("candidate_environment_id"), row.get("probe_key"), row.get("start_samples"))
            if key in used or key not in metric_by_key:
                continue
            metric = metric_by_key[key]
            anchors.append(
                {
                    "anchor_id": f"anchor_{len(anchors):03d}",
                    "environment_id": row["candidate_environment_id"],
                    "parameter_set_id": row["parameter_set_id"],
                    "anchor_primary_class": row["primary_class"],
                    "anchor_probe_family": row["probe_family"],
                    "probe_key": row["probe_key"],
                    "anchor_start_samples": row["start_samples"],
                    "anchor_horizon_window": "all_horizons",
                    "selection_reason": klass,
                    "anchor_deformation_scores": json.dumps(
                        {
                            "support_deformation_rate": row.get("support_deformation_rate", ""),
                            "distribution_deformation_rate": row.get("distribution_deformation_rate", ""),
                            "candidate_exceeds_control_rate": row.get("candidate_exceeds_control_rate", ""),
                            "mean_deformation_score": row.get("mean_deformation_score", ""),
                        },
                        sort_keys=True,
                    ),
                    "anchor_fakeout_tags": row.get("class_counts_json", ""),
                    "metadata_json": metric.get("metadata_json", ""),
                    "seed": metric.get("seed", ""),
                    "source_probe_family": metric.get("source_probe_family", row.get("probe_family", "")),
                }
            )
            used.add(key)
            if len(anchors) >= target:
                return anchors
    for row in candidate_summary:
        key = (row.get("candidate_environment_id"), row.get("probe_key"), row.get("start_samples"))
        if key in used or key not in metric_by_key:
            continue
        metric = metric_by_key[key]
        anchors.append(
            {
                "anchor_id": f"anchor_{len(anchors):03d}",
                "environment_id": row["candidate_environment_id"],
                "parameter_set_id": row["parameter_set_id"],
                "anchor_primary_class": row["primary_class"],
                "anchor_probe_family": row["probe_family"],
                "probe_key": row["probe_key"],
                "anchor_start_samples": row["start_samples"],
                "anchor_horizon_window": "fallback",
                "selection_reason": "proportional_fill",
                "anchor_deformation_scores": json.dumps({"mean_deformation_score": row.get("mean_deformation_score", "")}, sort_keys=True),
                "anchor_fakeout_tags": row.get("class_counts_json", ""),
                "metadata_json": metric.get("metadata_json", ""),
                "seed": metric.get("seed", ""),
                "source_probe_family": metric.get("source_probe_family", row.get("probe_family", "")),
            }
        )
        used.add(key)
        if len(anchors) >= target:
            break
    return anchors


def select_boundary_anchors(source_run: Path | None, target: int) -> list[dict[str, object]]:
    if source_run is None:
        return []
    band_rows = _read_csv(source_run / "atlas_band_classification_audit.csv")
    anchor_rows = _read_csv(source_run / "atlas_band_selection.csv")
    if not band_rows or not anchor_rows:
        return []
    band_by_id = {row.get("anchor_id", row.get("band_id", "")): row for row in band_rows}
    priority = {
        "saturation_boundary_band": 0,
        "probe_resolution_boundary_band": 1,
        "near_miss_transition_band": 2,
        "stable_fakeout_band": 3,
    }
    def score(row: dict[str, str]) -> tuple[int, int, int, float]:
        band = band_by_id.get(row.get("anchor_id", ""), {})
        klass = str(band.get("band_class", ""))
        blockers = str(band.get("stable_candidate_blockers", ""))
        return (
            priority.get(klass, 10),
            -int(float(band.get("saturation_boundary_count", 0.0) or 0.0) > 0),
            -int(float(band.get("probe_resolution_boundary_count", 0.0) or 0.0) > 0),
            -float(band.get("candidate_rate", 0.0) or 0.0),
        )
    selected = sorted(anchor_rows, key=score)[:target]
    anchors: list[dict[str, object]] = []
    for index, row in enumerate(selected):
        band = band_by_id.get(row.get("anchor_id", ""), {})
        params = params_from_parameter_set_id(row.get("parameter_set_id", ""))
        metadata = metadata_from_params(params) if params else {}
        anchors.append(
            {
                "anchor_id": f"anchor_{index:03d}",
                "source_anchor_id": row.get("anchor_id", ""),
                "environment_id": row.get("environment_id", ""),
                "parameter_set_id": row.get("parameter_set_id", ""),
                "anchor_primary_class": row.get("anchor_primary_class", ""),
                "anchor_probe_family": row.get("anchor_probe_family", ""),
                "probe_key": row.get("probe_key", ""),
                "anchor_start_samples": row.get("anchor_start_samples", ""),
                "anchor_horizon_window": "boundary_focused",
                "selection_reason": f"boundary_focus:{band.get('band_class', '')}",
                "boundary_band_class": band.get("band_class", ""),
                "boundary_band_reason": band.get("band_class_reason", ""),
                "candidate_rate": band.get("candidate_rate", ""),
                "saturation_boundary_count": band.get("saturation_boundary_count", ""),
                "probe_resolution_boundary_count": band.get("probe_resolution_boundary_count", ""),
                "candidate_to_fakeout_count": band.get("candidate_to_fakeout_count", ""),
                "fakeout_to_candidate_count": band.get("fakeout_to_candidate_count", ""),
                "stable_candidate_blockers": band.get("stable_candidate_blockers", ""),
                "anchor_deformation_scores": row.get("anchor_deformation_scores", ""),
                "anchor_fakeout_tags": row.get("anchor_fakeout_tags", ""),
                "metadata_json": json.dumps(metadata, sort_keys=True) if metadata else "",
                "seed": row.get("seed", ""),
                "source_probe_family": row.get("source_probe_family", row.get("anchor_probe_family", "")),
            }
        )
    return anchors


def matched_control_bundle(metric_rows: list[dict[str, str]], target: int = 5) -> list[dict[str, object]]:
    controls_by_key: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = {}
    for row in metric_rows:
        if row.get("row_kind") == "candidate":
            continue
        key = (row.get("candidate_environment_id", ""), row.get("probe_key", ""), row.get("start_samples", ""), row.get("H", ""), row.get("start_index", ""))
        controls_by_key.setdefault(key, []).append(row)
    out = []
    for row in metric_rows:
        if row.get("row_kind") != "candidate":
            continue
        key = (row.get("candidate_environment_id", ""), row.get("probe_key", ""), row.get("start_samples", ""), row.get("H", ""), row.get("start_index", ""))
        controls = sorted(controls_by_key.get(key, []), key=lambda item: (item.get("row_kind") != "matched_control", item.get("environment_id", "")))[:target]
        for index, control in enumerate(controls):
            out.append(
                {
                    "candidate_row_id": row_id(row),
                    "control_index": index,
                    "control_environment_id": control.get("environment_id", ""),
                    "control_row_kind": control.get("row_kind", ""),
                    "candidate_environment_id": row.get("candidate_environment_id", ""),
                    "probe_key": row.get("probe_key", ""),
                    "probe_family": row.get("probe_family", ""),
                    "start_samples": row.get("start_samples", ""),
                    "H": row.get("H", ""),
                    "start_index": row.get("start_index", ""),
                    "match_quality": "local_bundle",
                    "control_deformation_score": deformation_score_csv(control),
                }
            )
    return out


def rank_effect_summary(metric_rows: list[dict[str, str]], bundle: list[dict[str, object]]) -> list[dict[str, object]]:
    rows_by_id = {row_id(row): row for row in metric_rows}
    controls_by_candidate: dict[str, list[dict[str, str]]] = {}
    for item in bundle:
        candidate_id = str(item["candidate_row_id"])
        control_id = control_row_lookup_key(item)
        control = rows_by_id.get(control_id)
        if control:
            controls_by_candidate.setdefault(candidate_id, []).append(control)
    out = []
    for candidate_id, candidate in rows_by_id.items():
        if candidate.get("row_kind") != "candidate":
            continue
        controls = controls_by_candidate.get(candidate_id, [])
        derived_candidate = derived_scores(candidate)
        derived_controls = [derived_scores(control) for control in controls]
        for metric in RANK_METRICS:
            candidate_metric = derived_candidate.get(metric, 0.0)
            control_values = [scores.get(metric, 0.0) for scores in derived_controls]
            control_mean = mean(control_values) if control_values else 0.0
            control_std = pstdev(control_values) if len(control_values) > 1 else 0.0
            rank = sum(candidate_metric >= value for value in control_values)
            percentile = rank / max(1, len(control_values))
            out.append(
                {
                    "candidate_row_id": candidate_id,
                    "environment_id": candidate.get("environment_id", ""),
                    "candidate_environment_id": candidate.get("candidate_environment_id", ""),
                    "probe_key": candidate.get("probe_key", ""),
                    "probe_family": candidate.get("probe_family", ""),
                    "start_samples": candidate.get("start_samples", ""),
                    "H": candidate.get("H", ""),
                    "start_index": candidate.get("start_index", ""),
                    "metric": metric,
                    "candidate_metric": candidate_metric,
                    "control_mean": control_mean,
                    "control_std": control_std,
                    "candidate_minus_control_mean": candidate_metric - control_mean,
                    "candidate_control_rank": rank,
                    "candidate_control_percentile": percentile,
                    "control_count": len(control_values),
                }
            )
    return out


def margin_sensitivity(rank_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rank_rows:
        grouped.setdefault(str(row["candidate_row_id"]), []).append(row)
    out = []
    for candidate_id, rows in grouped.items():
        mixed = next((row for row in rows if row["metric"] == "mixed_deformation_score"), rows[0])
        margin_classes = {}
        for margin in MARGIN_GRID:
            margin_classes[f"class_at_margin_{str(margin).replace('.', '_')}"] = classify_margin(rows, margin)
        classes = list(margin_classes.values())
        if all(value == "candidate" for value in classes):
            stability = "strong_margin_candidate"
        elif classes[0] == "candidate" and classes[2] == "candidate":
            stability = "moderate_margin_candidate"
        elif classes[0] == "candidate":
            stability = "fragile_margin_candidate"
        elif all(value == "control_equivalent" for value in classes):
            stability = "control_equivalent_all_margins"
        else:
            stability = "margin_sensitive_fakeout"
        out.append(
            {
                "candidate_row_id": candidate_id,
                "candidate_environment_id": mixed.get("candidate_environment_id", ""),
                "probe_key": mixed.get("probe_key", ""),
                "probe_family": mixed.get("probe_family", ""),
                "start_samples": mixed.get("start_samples", ""),
                "H": mixed.get("H", ""),
                **margin_classes,
                "margin_stability_class": stability,
            }
        )
    return out


def support_vs_distribution_rows(rank_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, dict[str, object]]] = {}
    for row in rank_rows:
        grouped.setdefault(str(row["candidate_row_id"]), {})[str(row["metric"])] = row
    out = []
    for candidate_id, by_metric in grouped.items():
        support = by_metric.get("support_deformation_score", {})
        distribution = by_metric.get("distribution_deformation_score", {})
        mixed = by_metric.get("mixed_deformation_score", {})
        support_score = float(support.get("candidate_metric", 0.0) or 0.0)
        distribution_score = float(distribution.get("candidate_metric", 0.0) or 0.0)
        support_only = max(0.0, support_score - distribution_score)
        distribution_given_support = max(0.0, distribution_score - support_score * 0.5)
        out.append(
            {
                "candidate_row_id": candidate_id,
                "candidate_environment_id": mixed.get("candidate_environment_id", support.get("candidate_environment_id", "")),
                "probe_key": mixed.get("probe_key", support.get("probe_key", "")),
                "support_only_score": support_only,
                "distribution_given_support_score": distribution_given_support,
                "mixed_score": float(mixed.get("candidate_metric", 0.0) or 0.0),
                "support_explains_distribution_flag": int(distribution_score <= support_score * 0.5),
                "distribution_beyond_support_flag": int(distribution_given_support >= 0.05),
            }
        )
    return out


def build_sweep_jobs(args: argparse.Namespace, anchors: list[dict[str, object]]) -> list[dict[str, object]]:
    start_samples = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    horizons = tuple(int(item.strip()) for item in args.horizons.split(",") if item.strip())
    probe_keys = tuple(item.strip() for item in args.probe_families.split(",") if item.strip())
    jobs_by_anchor: list[list[dict[str, object]]] = []
    for anchor in anchors:
        anchor_jobs = []
        if not anchor.get("metadata_json"):
            params = params_from_parameter_set_id(str(anchor.get("parameter_set_id", "")))
        else:
            params = params_from_metadata(json.loads(str(anchor["metadata_json"])))
        if params is None:
            continue
        variants = local_variants(params)
        for variant_index, (dimension, value, variant_params) in enumerate(variants):
            for seed_index in range(args.fresh_seeds_per_variant):
                seed = int(anchor.get("seed") or stable_seed(str(anchor["environment_id"]))) + 10_007 * (seed_index + 1) + variant_index
                for probe_key in probe_keys:
                    for start_count in start_samples:
                        anchor_jobs.append(
                            {
                                "job_id": f"{anchor['anchor_id']}_{variant_index}_{seed_index}_{probe_key}_{start_count}",
                                "anchor_id": anchor["anchor_id"],
                                "anchor_environment_id": anchor["environment_id"],
                                "anchor_primary_class": anchor["anchor_primary_class"],
                                "variant_dimension": dimension,
                                "variant_value": value,
                                "params": variant_params,
                                "seed": seed,
                                "probe_key": probe_key,
                                "source_probe_family": anchor.get("source_probe_family", anchor.get("anchor_probe_family", "")),
                                "start_samples": start_count,
                                "horizons": horizons,
                            }
                        )
        jobs_by_anchor.append(anchor_jobs)
    interleaved = []
    max_len = max((len(anchor_jobs) for anchor_jobs in jobs_by_anchor), default=0)
    for index in range(max_len):
        for anchor_jobs in jobs_by_anchor:
            if index < len(anchor_jobs):
                interleaved.append(anchor_jobs[index])
    return interleaved


def run_sweep_jobs(
    args: argparse.Namespace,
    jobs: list[dict[str, object]],
    config: dict[str, object],
    started: float,
    anchors: list[dict[str, object]],
    matched_bundle: list[dict[str, object]],
    rank_effect: list[dict[str, object]],
    margins: list[dict[str, object]],
    separation: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    pending = list(jobs)
    executor = ProcessPoolExecutor(max_workers=max(1, args.workers))
    futures = {}
    timed_out = False
    try:
        while pending or futures:
            while pending and len(futures) < max(1, args.workers):
                job = pending.pop(0)
                futures[executor.submit(run_sweep_job, job)] = job
            remaining = args.max_runtime_seconds - (time.perf_counter() - started)
            if remaining <= 0:
                config["status"] = "TIME_LIMIT_REACHED"
                timed_out = True
                break
            done, _pending = wait(futures, timeout=max(0.1, min(2.0, remaining)), return_when=FIRST_COMPLETED)
            for future in done:
                job = futures.pop(future)
                try:
                    rows.extend(future.result())
                except Exception as exc:  # noqa: BLE001
                    errors.append({"job_id": job.get("job_id", ""), "error": repr(exc)})
            if rows and len(rows) % max(1, args.checkpoint_every) == 0:
                _write_outputs(args.out, config, started, anchors, matched_bundle, rank_effect, margins, separation, rows, errors, jobs)
    finally:
        if timed_out:
            for future in futures:
                future.cancel()
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    return rows, errors


def run_sweep_job(job: dict[str, object]) -> list[dict[str, object]]:
    params = job["params"]
    if not isinstance(params, RelationParams):
        raise TypeError("params must be RelationParams")
    seed = int(job["seed"])
    system = generate_relation_system(params, seed)
    null_systems = generated_null_systems(params, seed)
    probe, alphabet_size, probe_group = build_probe(system, str(job["probe_key"]), str(job["source_probe_family"]))
    starts = [system.states[(seed + i * 17) % len(system.states)] for i in range(int(job["start_samples"]))]
    horizons = tuple(int(value) for value in job["horizons"])  # type: ignore[union-attr]
    rows = []
    for start_index, start in enumerate(starts):
        observed_by_h = {h: signature_distribution(exact_frontier(system, start, h), probe) for h in horizons}
        null_by_name = {
            null_name: {h: signature_distribution(exact_frontier(null_system, start, h), probe) for h in horizons}
            for null_name, null_system in null_systems.items()
        }
        null_by_name.update(diagnostic_nulls(system, probe, observed_by_h, horizons))
        support_curve = [len(observed_by_h[h]) for h in horizons]
        entropy_curve = [entropy_from_counts(observed_by_h[h]) for h in horizons]
        trivial_by_h = [
            mean(js_divergence(observed_by_h[h], null_by_name[name][h]) for name in TRIVIALITY_NULLS if name in null_by_name)
            for h in horizons
        ]
        support_by_h = [
            mean(js_divergence(observed_by_h[h], null_by_name[name][h]) for name in SUPPORT_NULLS if name in null_by_name)
            for h in horizons
        ]
        for h in horizons:
            observed = observed_by_h[h]
            support_size = len(observed)
            support_fraction = support_size / max(1, alphabet_size)
            collision = max(0.0, 1.0 - support_size / max(1, len(system.states)))
            entropy = entropy_from_counts(observed)
            full_entropy = math.log2(max(1, alphabet_size))
            row = {
                "job_id": job["job_id"],
                "anchor_id": job["anchor_id"],
                "anchor_environment_id": job["anchor_environment_id"],
                "anchor_primary_class": job["anchor_primary_class"],
                "variant_dimension": job["variant_dimension"],
                "variant_value": job["variant_value"],
                "seed": seed,
                "environment_id": system.system_id,
                "parameter_set_id": params.parameter_set_id,
                "probe_key": job["probe_key"],
                "probe_family": probe.probe_family,
                "probe_group": probe_group,
                "start_samples": job["start_samples"],
                "start_index": start_index,
                "H": h,
                "frontier_size": sum(observed.values()),
                "probe_signature_alphabet_size": alphabet_size,
                "reachable_signature_support_size": support_size,
                "reachable_signature_support_fraction": support_fraction,
                "observed_signature_support_size": support_size,
                "observed_signature_support_fraction": support_fraction,
                "probe_collision_rate": collision,
                "support_ceiling_flag": int(support_fraction >= 0.90),
                "support_floor_flag": int(support_fraction <= 0.05),
                "support_extreme_flag": int(support_fraction >= 0.90 or support_fraction <= 0.05),
                "support_regime_class": support_regime_class(support_fraction),
                "probe_resolution_class": probe_resolution_class(collision, support_fraction, 2 ** entropy, len(system.states), probe.probe_family),
                "signature_entropy": entropy,
                "signature_entropy_ceiling_fraction": entropy / max(1e-9, full_entropy),
                "JS_to_triviality_nulls": mean(js_divergence(observed, null_by_name[name][h]) for name in TRIVIALITY_NULLS if name in null_by_name),
                "JS_to_support_nulls": mean(js_divergence(observed, null_by_name[name][h]) for name in SUPPORT_NULLS if name in null_by_name),
                "KL_to_triviality_nulls": mean(smoothed_kl(observed, null_by_name[name][h]) for name in TRIVIALITY_NULLS if name in null_by_name),
                "support_symmetric_difference_fraction": 1.0 - mean(jaccard_keys(observed, null_by_name[name][h]) for name in SUPPORT_NULLS if name in null_by_name),
                "mass_concentration_top_k": mass_concentration(observed, 3),
                "support_concentration_index": mass_concentration(observed, 1),
                "support_growth_slope": slope(support_curve, horizons),
                "support_stabilization_H": stabilization_horizon(support_curve, horizons),
                "support_stabilization_H_numeric": numeric_h(stabilization_horizon(support_curve, horizons)),
                "support_saturation_H": saturation_horizon(support_curve, horizons, alphabet_size),
                "distribution_stabilization_H": stabilization_horizon([round(value, 6) for value in entropy_curve], horizons),
                "support_deformation_score": trivial_by_h[horizons.index(h)],
                "distribution_deformation_score": support_by_h[horizons.index(h)],
                "mixed_deformation_score": trivial_by_h[horizons.index(h)] + support_by_h[horizons.index(h)],
            }
            row.update(classify_pre_control(row))
            row["local_primary_class"] = row["primary_class"]
            rows.append(row)
    return rows


def local_variants(params: RelationParams) -> list[tuple[str, object, RelationParams]]:
    variants: list[tuple[str, object, RelationParams]] = [("baseline", "baseline", params)]
    for dimension in SWEEP_DIMENSIONS:
        values = boundary_sweep_values(params, dimension)
        current = getattr(params, dimension)
        candidates = sorted(set(values), key=lambda value: (abs(float(value) - float(current)), float(value)))
        for value in candidates[:5]:
            if value == current and dimension != "baseline":
                continue
            kwargs = {dimension: int(value) if dimension == "out_degree_target" else float(value)}
            variants.append((dimension, kwargs[dimension], replace(params, **kwargs)))
    return variants


def boundary_sweep_values(params: RelationParams, dimension: str) -> tuple[float | int, ...]:
    current = getattr(params, dimension)
    if dimension == "out_degree_target":
        values = {int(current), max(1, int(current) - 1), min(5, int(current) + 1)}
        values.update(int(value) for value in SWEEP_VALUES[dimension])
        return tuple(sorted(values))
    if dimension in {"constraint_density", "reversibility_fraction", "asymmetry_strength"}:
        delta = 0.075 if dimension == "constraint_density" else 0.125
        values = {float(current), max(0.0, float(current) - delta), min(0.75, float(current) + delta)}
        values.update(float(value) for value in SWEEP_VALUES[dimension])
        return tuple(sorted(round(value, 4) for value in values))
    if dimension == "constraint_strength":
        values = {float(current), max(0.1, float(current) * 0.5), (float(current) + 0.5) / 2.0, min(3.0, float(current) * 1.5)}
        values.update(float(value) for value in SWEEP_VALUES[dimension])
        return tuple(sorted(round(value, 4) for value in values))
    if dimension == "constraint_change_weight":
        values = {float(current), max(0.0, float(current) - 0.175), min(1.0, float(current) + 0.175)}
        values.update(float(value) for value in SWEEP_VALUES[dimension])
        return tuple(sorted(round(value, 4) for value in values))
    return tuple(SWEEP_VALUES[dimension])


def _write_outputs(
    out_dir: Path,
    config: dict[str, object],
    started: float,
    anchors: list[dict[str, object]],
    matched_bundle: list[dict[str, object]],
    rank_effect: list[dict[str, object]],
    margins: list[dict[str, object]],
    separation: list[dict[str, object]],
    sweep_rows: list[dict[str, object]],
    errors: list[dict[str, object]],
    sweep_jobs: list[dict[str, object]],
) -> None:
    transition_graph = phenotype_transition_graph(anchors, sweep_rows)
    transition_summary = transition_class_summary_rows(transition_graph)
    sensitivity = local_parameter_sensitivity(sweep_rows)
    fakeouts = fakeout_transition_summary(anchors, sweep_rows)
    stability = candidate_stability_summary(anchors, sweep_rows, margins)
    near_misses = near_miss_summary(anchors, sweep_rows)
    boundaries = regime_boundary_summary(sweep_rows)
    sampling_plan = atlas_sampling_plan_rows(config, anchors, sweep_jobs)
    band_summary = atlas_band_summary_rows(transition_graph, stability, fakeouts, boundaries)
    fresh_seed_confirmation = fresh_seed_band_confirmation_rows(sweep_rows)
    fresh_seed_audit = fresh_seed_recurrence_audit_rows(sweep_rows)
    n6_transfer = n6_transfer_summary_rows(sweep_rows)
    band_audit = atlas_band_classification_audit_rows(anchors, band_summary, stability, transition_graph, margins)
    stable_blockers = stable_candidate_blocker_summary_rows(band_audit)
    saturation_audit = saturation_boundary_audit_rows(sweep_rows)
    probe_audit = probe_resolution_boundary_audit_rows(sweep_rows)
    probe_outcomes = probe_family_outcome_summary_rows(sweep_rows)
    margin_by_band = margin_stability_by_band_rows(margins, anchors)
    candidate_blockers = candidate_blocker_summary_rows(sweep_rows, margins)
    required_answers = required_answer_provenance_rows(transition_summary, band_summary, fresh_seed_audit, n6_transfer)
    _write_csv(out_dir / "local_sweep_anchor_selection.csv", strip_internal(anchors))
    _write_csv(out_dir / "matched_control_bundle.csv", matched_bundle)
    _write_csv(out_dir / "deformation_rank_effect_summary.csv", rank_effect)
    _write_csv(out_dir / "deformation_margin_sensitivity.csv", margins)
    _write_csv(out_dir / "support_vs_distribution_separation.csv", separation)
    _write_csv(out_dir / "local_parameter_sweep_results.csv", sweep_rows)
    _write_csv(out_dir / "phenotype_transition_graph.csv", transition_graph)
    _write_csv(out_dir / "transition_class_summary.csv", transition_summary)
    _write_csv(out_dir / "local_parameter_sensitivity.csv", sensitivity)
    _write_csv(out_dir / "fakeout_transition_summary.csv", fakeouts)
    _write_csv(out_dir / "candidate_stability_summary.csv", stability)
    _write_csv(out_dir / "near_miss_summary.csv", near_misses)
    _write_csv(out_dir / "regime_boundary_summary.csv", boundaries)
    _write_csv(out_dir / "atlas_band_selection.csv", strip_internal(anchors))
    _write_csv(out_dir / "atlas_sampling_plan.csv", sampling_plan)
    _write_csv(out_dir / "atlas_rank_effect_summary.csv", rank_effect)
    _write_csv(out_dir / "atlas_margin_sensitivity.csv", margins)
    _write_csv(out_dir / "atlas_support_vs_distribution_separation.csv", separation)
    _write_csv(out_dir / "atlas_matched_control_bundle.csv", matched_bundle)
    _write_csv(out_dir / "atlas_regime_map.csv", boundaries)
    _write_csv(out_dir / "atlas_band_summary.csv", band_summary)
    _write_csv(out_dir / "atlas_fakeout_transition_summary.csv", fakeouts)
    _write_csv(out_dir / "atlas_candidate_stability_summary.csv", stability)
    _write_csv(out_dir / "fresh_seed_band_confirmation.csv", fresh_seed_confirmation)
    _write_csv(out_dir / "n6_transfer_summary.csv", n6_transfer)
    _write_csv(out_dir / "required_answer_provenance.csv", required_answers)
    _write_csv(out_dir / "atlas_band_classification_audit.csv", band_audit)
    _write_csv(out_dir / "stable_candidate_blocker_summary.csv", stable_blockers)
    _write_csv(out_dir / "saturation_boundary_audit.csv", saturation_audit)
    _write_csv(out_dir / "probe_resolution_boundary_audit.csv", probe_audit)
    _write_csv(out_dir / "probe_family_outcome_summary.csv", probe_outcomes)
    _write_csv(out_dir / "margin_stability_by_band.csv", margin_by_band)
    _write_csv(out_dir / "candidate_blocker_summary.csv", candidate_blockers)
    _write_csv(out_dir / "fresh_seed_recurrence_audit.csv", fresh_seed_audit)
    _write_csv(out_dir / "errors.csv", errors)
    write_report(out_dir, config, started, anchors, rank_effect, margins, sweep_rows, transition_graph, stability, fakeouts, errors)
    write_medium_atlas_report(out_dir, config, started, anchors, rank_effect, margins, sweep_rows, transition_graph, stability, fakeouts, boundaries, fresh_seed_confirmation, n6_transfer, errors, required_answers, band_audit, stable_blockers, transition_summary, saturation_audit, probe_audit, fresh_seed_audit, candidate_blockers)
    write_boundary_resolution_report(out_dir, config, started, anchors, sweep_rows, band_audit, saturation_audit, probe_audit, transition_summary, fresh_seed_audit, errors)
    status = {
        "status": config.get("status", "RUNNING"),
        "wall_clock_seconds": time.perf_counter() - started,
        "anchors_selected": len(anchors),
        "sweep_jobs_requested": len(sweep_jobs),
        "sweep_jobs_completed": len({row["job_id"] for row in sweep_rows}),
        "sweep_rows_completed": len(sweep_rows),
        "rank_effect_rows": len(rank_effect),
        "errors": len(errors),
        "promotion_enabled": False,
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    write_output_manifest(out_dir)


def atlas_sampling_plan_rows(config: dict[str, object], anchors: list[dict[str, object]], sweep_jobs: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for key, jobs in group_by(sweep_jobs, ("anchor_id", "variant_dimension")).items():
        anchor = next((row for row in anchors if row["anchor_id"] == key[0]), {})
        rows.append(
            {
                "anchor_id": key[0],
                "anchor_primary_class": anchor.get("anchor_primary_class", ""),
                "variant_dimension": key[1],
                "planned_jobs": len(jobs),
                "fresh_seeds_per_variant": config.get("fresh_seeds_per_variant", ""),
                "workers": config.get("workers", ""),
                "promotion_enabled": False,
            }
        )
    return rows


def atlas_band_summary_rows(
    transition_graph: list[dict[str, object]],
    stability: list[dict[str, object]],
    fakeouts: list[dict[str, object]],
    boundaries: list[dict[str, object]],
) -> list[dict[str, object]]:
    transition_counts = _counts(row["transition_class"] for row in transition_graph)
    fakeout_rate_by_anchor = {row["anchor_id"]: row.get("fakeout_to_candidate_rate", 0.0) for row in fakeouts}
    stability_by_anchor = {row["anchor_id"]: row for row in stability}
    rows = []
    for anchor_id, stability_row in sorted(stability_by_anchor.items()):
        rows.append(
            {
                "band_id": anchor_id,
                "baseline_class": stability_row.get("baseline_class", ""),
                "candidate_retention_rate": stability_row.get("candidate_retention_rate", ""),
                "fakeout_to_candidate_rate": fakeout_rate_by_anchor.get(anchor_id, ""),
                "start_recurrence_rate": stability_row.get("start_recurrence_rate", ""),
                "probe_recurrence_rate": stability_row.get("probe_recurrence_rate", ""),
                "transition_class": stability_row.get("transition_class", ""),
                "atlas_level_class": atlas_level_class(stability_row, fakeout_rate_by_anchor.get(anchor_id, 0.0)),
                "global_transition_counts": json.dumps(transition_counts, sort_keys=True),
                "sensitive_parameter_count": len(boundaries),
            }
        )
    return rows


def atlas_level_class(stability_row: dict[str, object], fakeout_to_candidate_rate: object) -> str:
    retention = float(stability_row.get("candidate_retention_rate", 0.0) or 0.0)
    fakeout_rate = float(fakeout_to_candidate_rate or 0.0)
    baseline = str(stability_row.get("baseline_class", ""))
    if retention >= 0.50:
        return "stable_candidate_band"
    if fakeout_rate > 0.0:
        return "near_miss_transition_band"
    if "ceiling" in baseline:
        return "saturation_boundary_band"
    if "collision" in baseline:
        return "probe_resolution_boundary_band"
    if baseline == "matched_control_equivalent":
        return "matched_control_boundary_band"
    return "stable_fakeout_band"


def fresh_seed_band_confirmation_rows(sweep_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for key, items in group_by(sweep_rows, ("anchor_id", "variant_dimension", "variant_value")).items():
        seed_rates = {
            str(seed): mean(int(str(row["local_primary_class"]).endswith("_candidate")) for row in subset)
            for (seed,), subset in group_by(items, ("seed",)).items()
        }
        rows.append(
            {
                "anchor_id": key[0],
                "variant_dimension": key[1],
                "variant_value": key[2],
                "fresh_seed_count": len(seed_rates),
                "fresh_seed_candidate_rate_mean": mean(seed_rates.values()) if seed_rates else 0.0,
                "fresh_seed_candidate_rate_min": min(seed_rates.values()) if seed_rates else 0.0,
                "fresh_seed_recurrence_class": "seed_recurrent" if seed_rates and min(seed_rates.values()) > 0.0 else "seed_fragile_or_absent",
                "seed_rates_json": json.dumps(seed_rates, sort_keys=True),
            }
        )
    return rows


def n6_transfer_summary_rows(sweep_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    n6_rows = [row for row in sweep_rows if "n6_" in str(row.get("parameter_set_id", "")) or "n6" in str(row.get("environment_id", ""))]
    if not n6_rows:
        return [
            {
                "transfer_status": "skipped_budget",
                "reason": "n=6 transfer was intentionally skipped for this small repair run; it should not be interpreted as completed",
                "eligible_band_count": 0,
                "selected_band_count": 0,
                "jobs_requested": 0,
                "jobs_completed": 0,
                "errors": 0,
                "n5_source_band_ids": "",
                "n6_result_rows": 0,
                "n6_recurrent_count": 0,
                "n6_control_equivalent_count": 0,
                "n6_probe_limited_count": 0,
                "n6_saturation_limited_count": 0,
            }
        ]
    return [
        {
            "transfer_status": "run_completed",
            "reason": "n=6 transfer rows detected in sweep output",
            "eligible_band_count": len({row.get("anchor_id", "") for row in n6_rows}),
            "selected_band_count": len({row.get("anchor_id", "") for row in n6_rows}),
            "jobs_requested": len({row.get("job_id", "") for row in n6_rows}),
            "jobs_completed": len({row.get("job_id", "") for row in n6_rows}),
            "errors": 0,
            "n5_source_band_ids": json.dumps(sorted({str(row.get("anchor_id", "")) for row in n6_rows})),
            "n6_result_rows": len(n6_rows),
            "n6_recurrent_count": sum(int(str(row["local_primary_class"]).endswith("_candidate")) for row in n6_rows),
            "n6_control_equivalent_count": sum(int(str(row["local_primary_class"]) == "matched_control_equivalent") for row in n6_rows),
            "n6_probe_limited_count": sum(int("collision" in str(row["local_primary_class"])) for row in n6_rows),
            "n6_saturation_limited_count": sum(int("ceiling" in str(row["local_primary_class"])) for row in n6_rows),
        }
    ]


def phenotype_transition_graph(anchors: list[dict[str, object]], sweep_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    anchor_by_id = {str(row["anchor_id"]): row for row in anchors}
    out = []
    for key, rows in group_by(sweep_rows, ("anchor_id", "variant_dimension", "variant_value")).items():
        classes = _counts(row["local_primary_class"] for row in rows)
        anchor_class = str(anchor_by_id.get(str(key[0]), {}).get("anchor_primary_class", ""))
        dominant = max(classes.items(), key=lambda item: item[1])[0] if classes else "underdetermined"
        example = rows[0] if rows else {}
        transition = transition_class(anchor_class, dominant, rows)
        out.append(
            {
                "anchor_id": key[0],
                "band_id": key[0],
                "source_row_id": f"{key[0]}|anchor",
                "target_row_id": str(example.get("job_id", "")),
                "source_class": anchor_class,
                "target_class": dominant,
                "baseline_class": anchor_class,
                "variant_dimension": key[1],
                "variant_value": key[2],
                "sweep_parameter": key[1],
                "sweep_value": key[2],
                "fresh_seed": example.get("seed", ""),
                "probe_family": example.get("probe_family", ""),
                "start_samples": example.get("start_samples", ""),
                "horizon": example.get("H", ""),
                "margin_level": "aggregate",
                "classification_before": anchor_class,
                "classification_after": dominant,
                "dominant_variant_class": dominant,
                "variant_class_counts": json.dumps(classes, sort_keys=True),
                "transition_class": transition,
                "transition_reason": transition_reason(anchor_class, dominant, rows),
            }
        )
    return out


def transition_reason(anchor_class: str, dominant: str, rows: list[dict[str, object]]) -> str:
    if dominant.endswith("_candidate") and not anchor_class.endswith("_candidate"):
        return "fakeout anchor produced candidate-like dominant variant class"
    if anchor_class.endswith("_candidate") and not dominant.endswith("_candidate"):
        return "candidate anchor became fakeout/limited under local variant"
    if "ceiling" in dominant or mean(int(float(row.get("reachable_signature_support_fraction", 0.0) or 0.0) >= 0.90) for row in rows) > 0.5:
        return "support/probe saturation dominated variant rows"
    if "collision" in dominant:
        return "probe collision dominated variant rows"
    if dominant.endswith("_candidate"):
        return "candidate-like dominant variant class"
    return "no candidate-like transition under aggregate dominance"


def transition_class_summary_rows(transition_graph: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for klass, items in group_by(transition_graph, ("transition_class",)).items():
        rows.append(
            {
                "transition_class": klass[0],
                "n_edges": len(items),
                "example_row_ids": json.dumps([row.get("target_row_id", "") for row in items[:5]]),
            }
        )
    return rows


def fresh_seed_recurrence_audit_rows(sweep_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for key, items in group_by(sweep_rows, ("anchor_id", "variant_dimension", "variant_value")).items():
        by_seed = group_by(items, ("seed",))
        seed_classes = {}
        for (seed,), seed_rows in by_seed.items():
            classes = _counts(row["local_primary_class"] for row in seed_rows)
            dominant = max(classes.items(), key=lambda item: item[1])[0] if classes else "underdetermined"
            seed_classes[str(seed)] = dominant
        candidate_count = sum(int(value.endswith("_candidate")) for value in seed_classes.values())
        control_count = sum(int(value == "matched_control_equivalent") for value in seed_classes.values())
        probe_limited = sum(int("collision" in value) for value in seed_classes.values())
        saturation_limited = sum(int("ceiling" in value) for value in seed_classes.values())
        fakeout_count = len(seed_classes) - candidate_count
        score = candidate_count / max(1, len(seed_classes))
        if len(seed_classes) < 2:
            klass = "insufficient_fresh_seeds"
        elif candidate_count == len(seed_classes):
            klass = "seed_recurrent_candidate_like"
        elif fakeout_count == len(seed_classes):
            klass = "seed_recurrent_fakeout_like"
        elif candidate_count > 0:
            klass = "seed_mixed_or_boundary"
        else:
            klass = "seed_fragile_or_absent"
        rows.append(
            {
                "band_id": key[0],
                "anchor_id": key[0],
                "parameter_variant_id": f"{key[1]}={key[2]}",
                "fresh_seed_count": len(seed_classes),
                "fresh_seed_candidate_count": candidate_count,
                "fresh_seed_fakeout_count": fakeout_count,
                "fresh_seed_control_equivalent_count": control_count,
                "fresh_seed_probe_limited_count": probe_limited,
                "fresh_seed_saturation_limited_count": saturation_limited,
                "fresh_seed_recurrence_score": score,
                "fresh_seed_recurrence_class": klass,
                "recurrence_threshold": 1.0,
                "example_seed_ids": json.dumps(list(seed_classes)[:5]),
            }
        )
    return rows


def saturation_boundary_audit_rows(sweep_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in sweep_rows:
        support_fraction = float(row.get("reachable_signature_support_fraction", 0.0) or 0.0)
        support_ceiling = int(row.get("support_ceiling_flag", 0) or 0)
        saturation_flag = int(support_ceiling or support_fraction >= 0.90)
        if not saturation_flag:
            continue
        pre_score = float(row.get("mixed_deformation_score", 0.0) or 0.0) if float(row.get("H", 0) or 0) <= 4 else 0.0
        near_score = float(row.get("mixed_deformation_score", 0.0) or 0.0) if 4 < float(row.get("H", 0) or 0) <= 16 else 0.0
        post_score = float(row.get("mixed_deformation_score", 0.0) or 0.0) if float(row.get("H", 0) or 0) > 16 else 0.0
        rows.append(
            {
                "row_id": row.get("job_id", ""),
                "band_id": row.get("anchor_id", ""),
                "anchor_id": row.get("anchor_id", ""),
                "probe_family": row.get("probe_family", ""),
                "horizon": row.get("H", ""),
                "start_samples": row.get("start_samples", ""),
                "support_fraction": support_fraction,
                "support_ceiling_flag": support_ceiling,
                "support_floor_flag": row.get("support_floor_flag", ""),
                "support_extreme_flag": row.get("support_extreme_flag", ""),
                "support_regime_class": row.get("support_regime_class", ""),
                "state_space_saturation_flag": int(support_fraction >= 0.95),
                "probe_alphabet_saturation_flag": support_ceiling,
                "frontier_growth_slope": row.get("support_growth_slope", ""),
                "frontier_growth_curvature": "",
                "saturation_H": row.get("support_saturation_H", ""),
                "pre_saturation_candidate_score": pre_score,
                "near_saturation_candidate_score": near_score,
                "post_saturation_candidate_score": post_score,
                "classification_if_pre_saturation_only": "candidate_like" if pre_score >= 0.10 else "not_candidate_like",
                "classification_if_saturation_excluded": "excluded_saturation_row",
            }
        )
    return rows


def probe_resolution_boundary_audit_rows(sweep_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    by_band = group_by(sweep_rows, ("anchor_id",))
    for row in sweep_rows:
        collision_limited = "collision" in str(row.get("local_primary_class", ""))
        identity_like_limited = "identity_like" in str(row.get("probe_resolution_class", ""))
        probe_limited = collision_limited or identity_like_limited
        if not probe_limited:
            continue
        same_band_classes = sorted({str(item.get("local_primary_class", "")) for item in by_band.get((row.get("anchor_id", ""),), []) if item.get("probe_family") != row.get("probe_family")})
        rows.append(
            {
                "row_id": row.get("job_id", ""),
                "band_id": row.get("anchor_id", ""),
                "probe_family": row.get("probe_family", ""),
                "probe_resolution_class": row.get("probe_resolution_class", ""),
                "probe_collision_rate": row.get("probe_collision_rate", ""),
                "observed_signature_support_fraction": row.get("observed_signature_support_fraction", row.get("reachable_signature_support_fraction", "")),
                "support_ceiling_flag": row.get("support_ceiling_flag", ""),
                "support_floor_flag": row.get("support_floor_flag", ""),
                "collision_limited_flag": int(collision_limited),
                "identity_like_limited_flag": int(identity_like_limited),
                "candidate_score": row.get("mixed_deformation_score", ""),
                "matched_control_score": "",
                "candidate_minus_control": "",
                "class_under_probe": row.get("local_primary_class", ""),
                "same_band_classes_other_probes": json.dumps(same_band_classes[:12]),
                "cross_probe_recurrence_flag": int(any(value.endswith("_candidate") for value in same_band_classes)),
                "probe_local_only_flag": int(not any(value.endswith("_candidate") for value in same_band_classes)),
            }
        )
    return rows


def probe_family_outcome_summary_rows(sweep_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for key, items in group_by(sweep_rows, ("probe_family",)).items():
        rows.append(
            {
                "probe_family": key[0],
                "n_rows": len(items),
                "probe_family_candidate_rate": mean(int(str(row["local_primary_class"]).endswith("_candidate")) for row in items),
                "probe_family_fakeout_rate": mean(int(not str(row["local_primary_class"]).endswith("_candidate")) for row in items),
                "probe_family_probe_limited_rate": mean(int("collision" in str(row["local_primary_class"]) or "identity_like" in str(row.get("probe_resolution_class", ""))) for row in items),
                "probe_family_matched_control_equivalent_rate": mean(int(str(row["local_primary_class"]) == "matched_control_equivalent") for row in items),
            }
        )
    return rows


def atlas_band_classification_audit_rows(
    anchors: list[dict[str, object]],
    band_summary: list[dict[str, object]],
    stability: list[dict[str, object]],
    transition_graph: list[dict[str, object]],
    margins: list[dict[str, object]],
) -> list[dict[str, object]]:
    anchors_by_id = {str(row["anchor_id"]): row for row in anchors}
    stability_by_id = {str(row["anchor_id"]): row for row in stability}
    transitions_by_id = group_by(transition_graph, ("anchor_id",))
    margin_by_band = group_by(margins, ("candidate_environment_id", "probe_key"))
    rows = []
    for band in band_summary:
        band_id = str(band["band_id"])
        anchor = anchors_by_id.get(band_id, {})
        stable = stability_by_id.get(band_id, {})
        transitions = transitions_by_id.get((band_id,), [])
        transition_counts = _counts(row["transition_class"] for row in transitions)
        candidate_rate = float(stable.get("candidate_retention_rate", 0.0) or 0.0)
        fakeout_rate = 1.0 - candidate_rate
        fresh_seed_recurrent = int(float(stable.get("fresh_seed_recurrence_rate", 0.0) or 0.0) > 0.0)
        probe_recurrence = float(stable.get("probe_recurrence_rate", 0.0) or 0.0)
        start_recurrence = float(stable.get("start_recurrence_rate", 0.0) or 0.0)
        margin_rows = margin_by_band.get((anchor.get("environment_id", ""), anchor.get("probe_key", "")), [])
        margin_summary = json.dumps(_counts(row.get("margin_stability_class", "") for row in margin_rows), sort_keys=True)
        blockers = stable_candidate_blockers(candidate_rate, fresh_seed_recurrent, probe_recurrence, start_recurrence, transition_counts, margin_summary)
        eligible = int(not blockers)
        rows.append(
            {
                "band_id": band_id,
                "anchor_id": band_id,
                "anchor_class": anchor.get("anchor_primary_class", ""),
                "band_class": band.get("atlas_level_class", ""),
                "band_class_reason": band_class_reason(str(band.get("atlas_level_class", "")), candidate_rate, transition_counts),
                "candidate_rate": candidate_rate,
                "fakeout_rate": fakeout_rate,
                "candidate_rate_threshold": 0.50,
                "fresh_seed_recurrent_count": fresh_seed_recurrent,
                "fresh_seed_recurrent_threshold": 1,
                "probe_recurrence_score": probe_recurrence,
                "probe_recurrence_threshold": 0.10,
                "start_recurrence_score": start_recurrence,
                "start_recurrence_threshold": 0.10,
                "margin_stability_summary": margin_summary,
                "matched_control_equivalent_rate": transition_counts.get("matched_control_boundary", 0) / max(1, len(transitions)),
                "saturation_boundary_count": transition_counts.get("saturation_boundary", 0),
                "probe_resolution_boundary_count": transition_counts.get("probe_resolution_boundary", 0),
                "candidate_to_fakeout_count": transition_counts.get("candidate_to_fakeout_transition", 0),
                "fakeout_to_candidate_count": transition_counts.get("fakeout_to_candidate_transition", 0),
                "eligible_for_stable_candidate_band": eligible,
                "stable_candidate_blockers": ";".join(blockers) if blockers else "none",
            }
        )
    return rows


def band_class_reason(band_class: str, candidate_rate: float, transition_counts: dict[str, int]) -> str:
    if band_class == "stable_candidate_band":
        return "candidate retention crossed stable threshold and blockers were below ceilings"
    if band_class == "near_miss_transition_band":
        return "candidate-like variants occurred but stable candidate criteria were not met"
    if band_class == "saturation_boundary_band":
        return "support/probe saturation boundary dominated anchor neighborhood"
    if band_class == "probe_resolution_boundary_band":
        return "probe-resolution/collision boundary dominated anchor neighborhood"
    return f"candidate_rate={candidate_rate:.3f}; transition_counts={json.dumps(transition_counts, sort_keys=True)}"


def stable_candidate_blockers(
    candidate_rate: float,
    fresh_seed_recurrent: int,
    probe_recurrence: float,
    start_recurrence: float,
    transition_counts: dict[str, int],
    margin_summary: str,
) -> list[str]:
    blockers = []
    if candidate_rate < 0.50:
        blockers.append("candidate_rate_below_threshold")
    if fresh_seed_recurrent < 1:
        blockers.append("fresh_seed_recurrence_below_threshold")
    if probe_recurrence < 0.10:
        blockers.append("probe_recurrence_below_threshold")
    if start_recurrence < 0.10:
        blockers.append("start_recurrence_below_threshold")
    if transition_counts.get("saturation_boundary", 0) > 0:
        blockers.append("saturation_boundary_present")
    if transition_counts.get("probe_resolution_boundary", 0) > 0:
        blockers.append("probe_resolution_boundary_present")
    if "fragile_margin_candidate" in margin_summary and "strong_margin_candidate" not in margin_summary:
        blockers.append("fragile_margin_only")
    return blockers


def stable_candidate_blocker_summary_rows(band_audit: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter()
    for row in band_audit:
        for blocker in str(row.get("stable_candidate_blockers", "none")).split(";"):
            if blocker and blocker != "none":
                counts[blocker] += 1
    if not counts:
        return [{"blocker": "none", "n_bands": 0}]
    return [{"blocker": key, "n_bands": value} for key, value in sorted(counts.items())]


def local_parameter_sensitivity(sweep_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for key, rows in group_by(sweep_rows, ("anchor_id", "variant_dimension")).items():
        candidate_rate = mean(int(str(row["local_primary_class"]).endswith("_candidate")) for row in rows)
        fakeout_rate = mean(int("limited" in str(row["local_primary_class"]) or str(row["local_primary_class"]) == "matched_control_equivalent") for row in rows)
        out.append(
            {
                "anchor_id": key[0],
                "parameter": key[1],
                "n_rows": len(rows),
                "candidate_rate": candidate_rate,
                "fakeout_rate": fakeout_rate,
                "mean_mixed_deformation_score": _mean(row["mixed_deformation_score"] for row in rows),
                "mean_probe_collision_rate": _mean(row["probe_collision_rate"] for row in rows),
            }
        )
    return out


def fakeout_transition_summary(anchors: list[dict[str, object]], sweep_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    anchor_by_id = {str(row["anchor_id"]): row for row in anchors}
    out = []
    for anchor_id, rows in group_by(sweep_rows, ("anchor_id",)).items():
        anchor = anchor_by_id.get(str(anchor_id[0]), {})
        anchor_class = str(anchor.get("anchor_primary_class", ""))
        if anchor_class.endswith("_candidate"):
            continue
        candidate_rate = mean(int(str(row["local_primary_class"]).endswith("_candidate")) for row in rows)
        out.append(
            {
                "anchor_id": anchor_id[0],
                "baseline_fakeout_class": anchor_class,
                "fakeout_to_candidate_rate": candidate_rate,
                "dominant_variant_class": max(_counts(row["local_primary_class"] for row in rows).items(), key=lambda item: item[1])[0],
                "transition_summary": "near_miss_transition" if candidate_rate > 0 else "stable_artifact",
            }
        )
    return out


def candidate_stability_summary(anchors: list[dict[str, object]], sweep_rows: list[dict[str, object]], margins: list[dict[str, object]]) -> list[dict[str, object]]:
    margin_by_anchor_probe = {}
    for row in margins:
        margin_by_anchor_probe.setdefault((row.get("candidate_environment_id"), row.get("probe_key")), row.get("margin_stability_class", ""))
    out = []
    for anchor in anchors:
        rows = [row for row in sweep_rows if row.get("anchor_id") == anchor["anchor_id"]]
        if not rows:
            continue
        candidate_rate = mean(int(str(row["local_primary_class"]).endswith("_candidate")) for row in rows)
        start_rates = {
            str(start): mean(int(str(row["local_primary_class"]).endswith("_candidate")) for row in subset)
            for (start,), subset in group_by(rows, ("start_samples",)).items()
        }
        probe_rates = {
            str(probe): mean(int(str(row["local_primary_class"]).endswith("_candidate")) for row in subset)
            for (probe,), subset in group_by(rows, ("probe_family",)).items()
        }
        out.append(
            {
                "anchor_id": anchor["anchor_id"],
                "baseline_class": anchor["anchor_primary_class"],
                "candidate_retention_rate": candidate_rate,
                "candidate_retention_rate_by_parameter": json.dumps(
                    {
                        str(key[0]): mean(int(str(row["local_primary_class"]).endswith("_candidate")) for row in subset)
                        for key, subset in group_by(rows, ("variant_dimension",)).items()
                    },
                    sort_keys=True,
                ),
                "fresh_seed_recurrence_rate": mean(int(str(row["local_primary_class"]).endswith("_candidate")) for row in rows),
                "start_recurrence_rate": min(start_rates.values()) if start_rates else 0.0,
                "probe_recurrence_rate": min(probe_rates.values()) if probe_rates else 0.0,
                "margin_stability_class": margin_by_anchor_probe.get((anchor["environment_id"], anchor["probe_key"]), "not_directly_mapped"),
                "transition_class": "candidate_stable_region" if candidate_rate >= 0.5 else ("candidate_knife_edge" if str(anchor["anchor_primary_class"]).endswith("_candidate") else "fakeout_anchor"),
            }
        )
    return out


def margin_stability_by_band_rows(margins: list[dict[str, object]], anchors: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for anchor in anchors:
        selected = [row for row in margins if row.get("candidate_environment_id") == anchor.get("environment_id") and row.get("probe_key") == anchor.get("probe_key")]
        counts = _counts(row.get("margin_stability_class", "") for row in selected)
        rows.append(
            {
                "band_id": anchor.get("anchor_id", ""),
                "anchor_id": anchor.get("anchor_id", ""),
                "n_margin_rows": len(selected),
                "margin_stability_counts": json.dumps(counts, sort_keys=True),
                "fragile_margin_only_flag": int(bool(counts.get("fragile_margin_candidate")) and not bool(counts.get("strong_margin_candidate"))),
                "dominant_margin_stability_class": max(counts.items(), key=lambda item: item[1])[0] if counts else "missing",
            }
        )
    return rows


def candidate_blocker_summary_rows(sweep_rows: list[dict[str, object]], margins: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter()
    for row in sweep_rows:
        klass = str(row.get("local_primary_class", ""))
        if klass.endswith("_candidate"):
            continue
        if klass == "matched_control_equivalent":
            counts["matched_control_equivalent"] += 1
        if "collision" in klass or "identity_like" in str(row.get("probe_resolution_class", "")):
            counts["probe_limited"] += 1
        if "ceiling" in klass or int(row.get("support_ceiling_flag", 0) or 0):
            counts["support_ceiling_limited"] += 1
        if float(row.get("reachable_signature_support_fraction", 0.0) or 0.0) >= 0.90:
            counts["saturation_limited"] += 1
    margin_counts = _counts(row.get("margin_stability_class", "") for row in margins)
    if margin_counts.get("fragile_margin_candidate", 0):
        counts["fragile_margin_only"] += int(margin_counts["fragile_margin_candidate"])
    if not counts:
        return [{"blocker": "none", "n_rows": 0}]
    return [{"blocker": key, "n_rows": value} for key, value in sorted(counts.items())]


def near_miss_summary(anchors: list[dict[str, object]], sweep_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for anchor in anchors:
        rows = [row for row in sweep_rows if row.get("anchor_id") == anchor["anchor_id"]]
        if not rows:
            continue
        near = [row for row in rows if str(row["local_primary_class"]).endswith("_candidate")]
        if near:
            out.append(
                {
                    "anchor_id": anchor["anchor_id"],
                    "baseline_class": anchor["anchor_primary_class"],
                    "near_miss_count": len(near),
                    "best_variant_dimension": max(group_by(near, ("variant_dimension",)).items(), key=lambda item: len(item[1]))[0][0],
                    "best_candidate_rate": len(near) / len(rows),
                }
            )
    return out


def regime_boundary_summary(sweep_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for key, rows in group_by(sweep_rows, ("variant_dimension",)).items():
        class_counts = _counts(row["local_primary_class"] for row in rows)
        out.append(
            {
                "parameter": key[0],
                "n_rows": len(rows),
                "candidate_rate": mean(int(str(row["local_primary_class"]).endswith("_candidate")) for row in rows),
                "fakeout_rate": mean(int(not str(row["local_primary_class"]).endswith("_candidate")) for row in rows),
                "most_sensitive_parameter": key[0],
                "candidate_promoting_parameter_changes": json.dumps(_counts(row["variant_value"] for row in rows if str(row["local_primary_class"]).endswith("_candidate")), sort_keys=True),
                "fakeout_promoting_parameter_changes": json.dumps(_counts(row["variant_value"] for row in rows if not str(row["local_primary_class"]).endswith("_candidate")), sort_keys=True),
                "class_counts": json.dumps(class_counts, sort_keys=True),
            }
        )
    return out


def required_answer_provenance_rows(
    transition_summary: list[dict[str, object]],
    band_summary: list[dict[str, object]],
    fresh_seed_audit: list[dict[str, object]],
    n6_transfer: list[dict[str, object]],
) -> list[dict[str, object]]:
    transition_counts = {str(row["transition_class"]): int(row["n_edges"]) for row in transition_summary}
    band_fakeout_count = sum(int(float(row.get("fakeout_to_candidate_rate", 0.0) or 0.0) > 0.0) for row in band_summary)
    fresh_seed_recurrent = sum(int(row.get("fresh_seed_recurrence_class") in {"seed_recurrent_candidate_like", "seed_mixed_or_boundary"}) for row in fresh_seed_audit)
    stable_candidate_count = sum(int(row.get("atlas_level_class") == "stable_candidate_band") for row in band_summary)
    transfer = n6_transfer[0] if n6_transfer else {}
    graph_count = transition_counts.get("fakeout_to_candidate_transition", 0)
    return [
        {
            "required_answer_name": "candidate_stable_local_neighborhoods_generalized",
            "value": bool(stable_candidate_count > 0),
            "source_table": "atlas_band_summary.csv",
            "source_column": "atlas_level_class",
            "source_filter": "atlas_level_class == stable_candidate_band",
            "numerator": stable_candidate_count,
            "denominator": len(band_summary),
            "threshold": "> 0",
            "example_row_ids": json.dumps([row.get("band_id", "") for row in band_summary if row.get("atlas_level_class") == "stable_candidate_band"][:5]),
        },
        {
            "required_answer_name": "fakeout_to_candidate_transition_graph_count",
            "value": graph_count > 0,
            "source_table": "transition_class_summary.csv",
            "source_column": "transition_class",
            "source_filter": "transition_class == fakeout_to_candidate_transition",
            "numerator": graph_count,
            "denominator": sum(transition_counts.values()),
            "threshold": "> 0",
            "example_row_ids": "see phenotype_transition_graph.csv",
        },
        {
            "required_answer_name": "fakeout_to_candidate_band_level_count",
            "value": band_fakeout_count > 0,
            "source_table": "atlas_band_summary.csv",
            "source_column": "fakeout_to_candidate_rate",
            "source_filter": "fakeout_to_candidate_rate > 0",
            "numerator": band_fakeout_count,
            "denominator": len(band_summary),
            "threshold": "> 0",
            "example_row_ids": json.dumps([row.get("band_id", "") for row in band_summary if float(row.get("fakeout_to_candidate_rate", 0.0) or 0.0) > 0.0][:5]),
        },
        {
            "required_answer_name": "fakeout_to_candidate_fresh_seed_recurrent_count",
            "value": fresh_seed_recurrent > 0,
            "source_table": "fresh_seed_recurrence_audit.csv",
            "source_column": "fresh_seed_recurrence_class",
            "source_filter": "class in seed_recurrent_candidate_like, seed_mixed_or_boundary",
            "numerator": fresh_seed_recurrent,
            "denominator": len(fresh_seed_audit),
            "threshold": "> 0",
            "example_row_ids": json.dumps([row.get("parameter_variant_id", "") for row in fresh_seed_audit if row.get("fresh_seed_recurrence_class") in {"seed_recurrent_candidate_like", "seed_mixed_or_boundary"}][:5]),
        },
        {
            "required_answer_name": "fakeout_to_candidate_any_recurred",
            "value": graph_count > 0 or band_fakeout_count > 0 or fresh_seed_recurrent > 0,
            "source_table": "transition_class_summary.csv;atlas_band_summary.csv;fresh_seed_recurrence_audit.csv",
            "source_column": "multiple",
            "source_filter": "any fakeout-to-candidate recurrence criterion positive",
            "numerator": graph_count + band_fakeout_count + fresh_seed_recurrent,
            "denominator": sum(transition_counts.values()) + len(band_summary) + len(fresh_seed_audit),
            "threshold": "> 0",
            "example_row_ids": "see component rows above",
        },
        {
            "required_answer_name": "n6_transfer_completed",
            "value": transfer.get("transfer_status") == "run_completed",
            "source_table": "n6_transfer_summary.csv",
            "source_column": "transfer_status",
            "source_filter": "transfer_status == run_completed",
            "numerator": int(transfer.get("transfer_status") == "run_completed"),
            "denominator": 1,
            "threshold": "run_completed",
            "example_row_ids": transfer.get("n5_source_band_ids", ""),
        },
    ]


REQUIRED_REPAIR_OUTPUTS = (
    "medium_breadth_support_distribution_atlas_report.md",
    "required_answer_provenance.csv",
    "n6_transfer_summary.csv",
    "atlas_band_classification_audit.csv",
    "stable_candidate_blocker_summary.csv",
    "phenotype_transition_graph.csv",
    "transition_class_summary.csv",
    "saturation_boundary_audit.csv",
    "probe_resolution_boundary_audit.csv",
    "probe_family_outcome_summary.csv",
    "atlas_rank_effect_summary.csv",
    "atlas_margin_sensitivity.csv",
    "margin_stability_by_band.csv",
    "candidate_blocker_summary.csv",
    "fresh_seed_recurrence_audit.csv",
    "output_manifest.json",
    "status.json",
)


def write_output_manifest(out_dir: Path) -> None:
    rows = []
    for name in REQUIRED_REPAIR_OUTPUTS:
        path = out_dir / name
        exists = path.exists()
        row_count = ""
        status = "present" if exists else "missing"
        if exists and path.suffix == ".csv":
            row_count = csv_row_count(path)
            status = "present_empty" if row_count == 0 else "present"
        rows.append({"file": name, "exists": exists, "row_count": row_count, "status": status})
    (out_dir / "output_manifest.json").write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


def csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        rows = list(reader)
    if not rows:
        return 0
    if rows[0] == ["empty"]:
        return 0
    return max(0, len(rows) - 1)


def write_report(
    out_dir: Path,
    config: dict[str, object],
    started: float,
    anchors: list[dict[str, object]],
    rank_effect: list[dict[str, object]],
    margins: list[dict[str, object]],
    sweep_rows: list[dict[str, object]],
    transition_graph: list[dict[str, object]],
    stability: list[dict[str, object]],
    fakeouts: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    stable_candidates = [row for row in stability if float(row.get("candidate_retention_rate", 0.0) or 0.0) >= 0.5]
    stable_transition_regions = [row for row in transition_graph if row.get("transition_class") == "candidate_stable_region"]
    fakeout_transitions = [row for row in fakeouts if float(row.get("fakeout_to_candidate_rate", 0.0) or 0.0) > 0.0]
    margin_counts = _counts(row["margin_stability_class"] for row in margins)
    transition_counts = _counts(row["transition_class"] for row in transition_graph)
    if (stable_candidates or stable_transition_regions) and fakeout_transitions:
        decision = "proceed_to_medium_breadth_atlas"
    elif fakeout_transitions or stable_candidates or stable_transition_regions:
        decision = "continue_local_sweeps"
    else:
        decision = "measurement_limits_note_or_pause"
    lines = [
        "# RFS-MB0 Deformation Detector Upgrade Report",
        "",
        "Promotion disabled: this is detector calibration and local transition geometry, not Omega validation.",
        "",
        f"- Wall clock used: {time.perf_counter() - started:.1f} seconds",
        f"- Workers requested: {config['workers']}",
        f"- Anchors selected: {len(anchors)}",
        f"- Rank/effect rows: {len(rank_effect)}",
        f"- Sweep rows completed: {len(sweep_rows)}",
        f"- Errors: {len(errors)}",
        f"- Recommended next step: {decision}",
        "",
        "## Margin Stability",
        "",
        "| stability | n |",
        "|---|---:|",
    ]
    for key, value in sorted(margin_counts.items()):
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Transition Classes", "", "| transition | n |", "|---|---:|"])
    for key, value in sorted(transition_counts.items()):
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Required Answers",
            "",
            f"- Candidate residues remain under upgraded scoring: {bool(stable_candidates or stable_transition_regions)}",
            f"- Fakeout-to-candidate transitions observed: {len(fakeout_transitions) > 0}",
            "- Path metrics remain parked and do not drive classification.",
            "",
            "## Claim Boundary",
            "",
            "This run may identify local support/distribution transition geometry. It does not claim agency, identity, valuerhood, path-process detection, Omega detection, or scientific-gate passage.",
        ]
    )
    (out_dir / "deformation_detector_upgrade_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_medium_atlas_report(
    out_dir: Path,
    config: dict[str, object],
    started: float,
    anchors: list[dict[str, object]],
    rank_effect: list[dict[str, object]],
    margins: list[dict[str, object]],
    sweep_rows: list[dict[str, object]],
    transition_graph: list[dict[str, object]],
    stability: list[dict[str, object]],
    fakeouts: list[dict[str, object]],
    boundaries: list[dict[str, object]],
    fresh_seed_confirmation: list[dict[str, object]],
    n6_transfer: list[dict[str, object]],
    errors: list[dict[str, object]],
    required_answers: list[dict[str, object]],
    band_audit: list[dict[str, object]],
    stable_blockers: list[dict[str, object]],
    transition_summary: list[dict[str, object]],
    saturation_audit: list[dict[str, object]],
    probe_audit: list[dict[str, object]],
    fresh_seed_audit: list[dict[str, object]],
    candidate_blockers: list[dict[str, object]],
) -> None:
    transition_counts = _counts(row["transition_class"] for row in transition_graph)
    margin_counts = _counts(row["margin_stability_class"] for row in margins)
    band_classes = _counts(atlas_level_class(row, next((fakeout.get("fakeout_to_candidate_rate", 0.0) for fakeout in fakeouts if fakeout.get("anchor_id") == row.get("anchor_id")), 0.0)) for row in stability)
    seed_recurrent = sum(1 for row in fresh_seed_confirmation if row.get("fresh_seed_recurrence_class") == "seed_recurrent")
    n6_status = next((row.get("transfer_status", "not_run") for row in n6_transfer), "not_run")
    if band_classes.get("stable_candidate_band", 0) or band_classes.get("near_miss_transition_band", 0):
        decision = "broader_atlas_or_second_local_sweep"
    elif transition_counts.get("fakeout_to_candidate_transition", 0):
        decision = "second_local_sweep"
    else:
        decision = "measurement_limits_note_or_pause"
    lines = [
        "# RFS-MB0 Medium-Breadth Support/Distribution Atlas Report",
        "",
        "Promotion disabled: this is a guided support/distribution atlas repair smoke, not Omega validation.",
        "",
        "## 1. Run Shape And Integrity",
        "",
        f"- Wall clock used: {time.perf_counter() - started:.1f} seconds",
        f"- Workers requested: {config['workers']}",
        f"- Anchors selected: {len(anchors)}",
        f"- Sweep rows completed: {len(sweep_rows)}",
        f"- Rank/effect rows: {len(rank_effect)}",
        f"- Errors: {len(errors)}",
        f"- Recommended next step: {decision}",
        "",
        "## 2. Promotion/Claim Boundary",
        "",
        "No row is promoted to Omega, agency, identity, valuerhood, viability, path-process detection, or scientific-gate passage.",
        "",
        "## 3. Required-Answer Provenance",
        "",
        "| answer | value | source | numerator | denominator |",
        "|---|---|---|---:|---:|",
    ]
    for row in required_answers:
        lines.append(f"| {row['required_answer_name']} | {row['value']} | {row['source_table']} | {row['numerator']} | {row['denominator']} |")
    graph_count = next((row for row in required_answers if row["required_answer_name"] == "fakeout_to_candidate_transition_graph_count"), {})
    band_count = next((row for row in required_answers if row["required_answer_name"] == "fakeout_to_candidate_band_level_count"), {})
    if int(graph_count.get("numerator", 0) or 0) == 0 and int(band_count.get("numerator", 0) or 0) > 0:
        lines.extend(["", "No explicit fakeout_to_candidate transition graph edges were emitted, but band-level fakeout-to-candidate recurrence was observed under the band-level criterion."])
    elif int(graph_count.get("numerator", 0) or 0) == 0:
        lines.extend(["", "No explicit fakeout_to_candidate transition graph edges were emitted."])
    n6_status = next((row.get("transfer_status", "not_run") for row in n6_transfer), "not_run")
    if n6_status != "run_completed":
        lines.extend(["", "n=6 transfer was not run and should not be interpreted as completed."])
    lines.extend(
        [
            "",
            "## 4. Band Class Summary",
        "",
        "| class | n |",
        "|---|---:|",
        ]
    )
    for key, value in sorted(band_classes.items()):
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## 5. Stable-Candidate Blocker Summary", "", "| blocker | n |", "|---|---:|"])
    for row in stable_blockers:
        lines.append(f"| {row.get('blocker', '')} | {row.get('n_bands', row.get('n_rows', ''))} |")
    lines.extend(["", "## 6. Transition Graph Summary", "", "| transition | n |", "|---|---:|"])
    for row in transition_summary:
        lines.append(f"| {row.get('transition_class', '')} | {row.get('n_edges', '')} |")
    lines.extend(
        [
            "",
            "## 7. Saturation Boundary Audit",
            "",
            f"- Saturation audit rows: {len(saturation_audit)}",
            "",
            "## 8. Probe-Resolution Boundary Audit",
            "",
            f"- Probe-resolution audit rows: {len(probe_audit)}",
            "",
            "## 9. Fresh-Seed Recurrence Audit",
            "",
            f"- Fresh-seed recurrence audit rows: {len(fresh_seed_audit)}",
            "",
            "## 10. Margin/Rank-Effect Summary",
            "",
            "| stability | n |",
            "|---|---:|",
        ]
    )
    for key, value in sorted(margin_counts.items()):
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## 11. n=6 Transfer Status",
            "",
            f"- n=6 transfer status: {n6_status}",
            f"- n=6 transfer reason: {n6_transfer[0].get('reason', '') if n6_transfer else ''}",
            "",
            "## 12. Recommended Next Step",
            "",
            f"- {decision}",
            "",
            "## 13. Machine-Readable Output Manifest",
            "",
            "- See `output_manifest.json`.",
            "",
            "## Candidate Blockers",
            "",
            "| blocker | n |",
            "|---|---:|",
        ]
    )
    for row in candidate_blockers:
        lines.append(f"| {row.get('blocker', '')} | {row.get('n_rows', '')} |")
    lines.extend(
        [
            "",
            "## Sensitive Parameters",
            "",
            "| parameter | candidate_rate | fakeout_rate |",
            "|---|---:|---:|",
        ]
    )
    for row in boundaries:
        lines.append(f"| {row.get('parameter', '')} | {row.get('candidate_rate', '')} | {row.get('fakeout_rate', '')} |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This run maps support/distribution deformation bands under specified controls. It does not claim agency, identity, valuerhood, path-process detection, Omega detection, or scientific-gate passage.",
        ]
    )
    (out_dir / "medium_breadth_support_distribution_atlas_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary_resolution_report(
    out_dir: Path,
    config: dict[str, object],
    started: float,
    anchors: list[dict[str, object]],
    sweep_rows: list[dict[str, object]],
    band_audit: list[dict[str, object]],
    saturation_audit: list[dict[str, object]],
    probe_audit: list[dict[str, object]],
    transition_summary: list[dict[str, object]],
    fresh_seed_audit: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    candidate_rows = [row for row in sweep_rows if str(row.get("local_primary_class", "")).endswith("_candidate")]
    nonsat_candidates = [
        row for row in candidate_rows
        if not int(float(row.get("support_ceiling_flag", 0.0) or 0.0))
        and float(row.get("reachable_signature_support_fraction", 0.0) or 0.0) < 0.90
    ]
    probe_recurrent_bands = [
        row for row in band_audit
        if float(row.get("probe_recurrence_score", 0.0) or 0.0) >= float(row.get("probe_recurrence_threshold", 0.10) or 0.10)
    ]
    fresh_seed_recurrent = [
        row for row in fresh_seed_audit
        if row.get("fresh_seed_recurrence_class") in {"seed_recurrent_candidate_like", "seed_mixed_or_boundary"}
    ]
    transition_counts = {str(row.get("transition_class", "")): int(row.get("n_edges", row.get("count", 0)) or 0) for row in transition_summary}
    stable_bands = [row for row in band_audit if int(float(row.get("eligible_for_stable_candidate_band", 0.0) or 0.0))]
    if stable_bands:
        decision = "continue_mb0_boundary_followup_before_n6"
    elif candidate_rows and not nonsat_candidates:
        decision = "write_measurement_limits_note_if_replicated"
    elif fresh_seed_recurrent or probe_recurrent_bands:
        decision = "continue_mb0_with_tighter_boundary_repair"
    else:
        decision = "measurement_limits_likely"
    lines = [
        "# RFS-MB0 Boundary Resolution Report",
        "",
        "Promotion disabled. This report focuses on saturation, probe-resolution, candidate-to-fakeout, near-miss, and fakeout-to-candidate boundary behavior.",
        "",
        f"- Status: {config.get('status', '')}",
        f"- Wall clock used: {time.perf_counter() - started:.1f} seconds",
        f"- Workers requested: {config.get('workers', '')}",
        f"- Anchors selected: {len(anchors)}",
        f"- Sweep rows completed: {len(sweep_rows)}",
        f"- Candidate-like rows: {len(candidate_rows)}",
        f"- Non-saturation candidate-like rows: {len(nonsat_candidates)}",
        f"- Probe-recurrent bands: {len(probe_recurrent_bands)}",
        f"- Fresh-seed recurrent variant groups: {len(fresh_seed_recurrent)}",
        f"- Stable candidate bands: {len(stable_bands)}",
        f"- Saturation audit rows: {len(saturation_audit)}",
        f"- Probe-resolution audit rows: {len(probe_audit)}",
        f"- Errors: {len(errors)}",
        f"- Decision: {decision}",
        "",
        "## Boundary Transition Counts",
        "",
        "| transition | n |",
        "|---|---:|",
    ]
    for key, value in sorted(transition_counts.items()):
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Anchor Boundary Classes", "", "| anchor | source class | boundary class | candidate rate | blockers |", "|---|---|---|---:|---|"])
    for row in band_audit:
        lines.append(
            f"| {row.get('anchor_id', '')} | {row.get('anchor_class', '')} | {row.get('band_class', '')} | {row.get('candidate_rate', '')} | {row.get('stable_candidate_blockers', '')} |"
        )
    lines.extend(
        [
            "",
            "## Decision Rule",
            "",
            "Continue MB0 only if near-miss bands become less saturated, probe recurrence improves, candidate-like behavior survives fresh seeds, or fakeout-to-candidate behavior becomes fresh-seed recurrent.",
            "",
            "Write a measurement-limits note if candidate-like behavior remains saturation/probe-boundary dominated, probe recurrence stays weak, fresh-seed recurrence remains absent, and stable candidate bands remain zero.",
            "",
            "Only consider n=6 if at least one n=5 band is cross-probe recurrent, not saturation/probe limited, and fresh-seed stable.",
            "",
            "## Claim Boundary",
            "",
            "This is a boundary-resolution audit for a toy neutral relation substrate. It does not claim Omega, agency, value, identity, viability, path-process detection, or scientific-gate passage.",
        ]
    )
    (out_dir / "boundary_resolution_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def derived_scores(row: dict[str, str]) -> dict[str, float]:
    support = float(row.get("JS_to_triviality_nulls", 0.0) or 0.0)
    distribution = float(row.get("JS_to_support_nulls", 0.0) or 0.0)
    mixed = support + distribution
    return {
        "support_deformation_score": support,
        "distribution_deformation_score": distribution,
        "mixed_deformation_score": mixed,
        "JS_to_triviality_nulls": support,
        "JS_to_support_nulls": distribution,
        "TV_distance_to_matched_control": float(row.get("TV_distance_to_matched_control", 0.0) or 0.0),
        "mass_shift_vs_control": abs(float(row.get("mass_shift_vs_control", 0.0) or 0.0)),
        "support_symmetric_difference_fraction": float(row.get("support_symmetric_difference_fraction", 1.0 - float(row.get("support_jaccard_vs_matched_control", 0.0) or 0.0)) or 0.0),
        "support_growth_slope": float(row.get("support_growth_slope", 0.0) or 0.0),
        "support_stabilization_H_numeric": numeric_h(row.get("support_stabilization_H", "")),
    }


def classify_margin(rows: list[dict[str, object]], margin: float) -> str:
    mixed = next((row for row in rows if row["metric"] == "mixed_deformation_score"), None)
    support = next((row for row in rows if row["metric"] == "support_deformation_score"), None)
    if not mixed:
        return "underdetermined"
    delta = float(mixed["candidate_minus_control_mean"])
    control_count = int(mixed["control_count"])
    if control_count < 1:
        return "underdetermined"
    if delta >= margin and float(mixed["candidate_control_percentile"]) >= 0.75:
        return "candidate"
    if support and float(support["candidate_minus_control_mean"]) >= margin:
        return "support_only_candidate"
    return "control_equivalent"


def transition_class(anchor_class: str, dominant: str, rows: list[dict[str, object]]) -> str:
    if dominant.endswith("_candidate") and anchor_class.endswith("_candidate"):
        return "candidate_stable_region"
    if dominant.endswith("_candidate") and not anchor_class.endswith("_candidate"):
        return "fakeout_to_candidate_transition"
    if anchor_class.endswith("_candidate") and not dominant.endswith("_candidate"):
        return "candidate_to_fakeout_transition"
    if "ceiling" in dominant:
        return "saturation_boundary"
    if "collision" in dominant:
        return "probe_resolution_boundary"
    if mean(int(float(row.get("reachable_signature_support_fraction", 0.0) or 0.0) >= 0.90) for row in rows) > 0.5:
        return "saturation_boundary"
    return "fakeout_stable_artifact"


def local_parameter_value(value: object) -> object:
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def deformation_score_csv(row: dict[str, str]) -> float:
    js_distribution_score = float(row.get("JS_to_triviality_nulls", 0.0) or 0.0) + float(row.get("JS_to_support_nulls", 0.0) or 0.0)
    support_set_score = float(row.get("support_symmetric_difference_fraction", 0.0) or 0.0)
    mass_concentration_score = float(row.get("mass_concentration_top_k", 0.0) or 0.0)
    support_growth_score = abs(float(row.get("support_growth_slope", 0.0) or 0.0))
    return 0.40 * js_distribution_score + 0.35 * support_set_score + 0.15 * mass_concentration_score + 0.10 * support_growth_score


def support_regime_class(support_fraction: float) -> str:
    if support_fraction <= 0.05:
        return "support_floor_sparse"
    if support_fraction >= 0.90:
        return "support_ceiling_saturated"
    return "middle_support_regime"


def row_id(row: dict[str, str]) -> str:
    return "|".join(str(row.get(key, "")) for key in ("row_kind", "candidate_environment_id", "environment_id", "probe_key", "start_samples", "H", "start_index"))


def control_row_lookup_key(bundle_row: dict[str, object]) -> str:
    return "|".join(
        str(bundle_row.get(key, ""))
        for key in ("control_row_kind", "candidate_environment_id", "control_environment_id", "probe_key", "start_samples", "H", "start_index")
    )


def numeric_h(value: object) -> float:
    try:
        if value == "":
            return 0.0
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


def jaccard_keys(left: dict[object, int], right: dict[object, int]) -> float:
    left_keys = set(left)
    right_keys = set(right)
    if not left_keys and not right_keys:
        return 1.0
    return len(left_keys & right_keys) / max(1, len(left_keys | right_keys))


def stable_seed(text: str) -> int:
    total = 0
    for index, char in enumerate(text):
        total = (total * 131 + (index + 17) * ord(char)) % 10_000_000
    return total


def params_from_parameter_set_id(parameter_set_id: str) -> RelationParams | None:
    match = re.match(
        r"relgen_n(?P<n>\d+)_a(?P<a>\d+)_r(?P<r>\d+)_m(?P<m>\d+)_"
        r"k(?P<k>\d+)_cd(?P<cd>[0-9.]+)_cs(?P<cs>[0-9.]+)_"
        r"as(?P<asym>[0-9.]+)_rev(?P<rev>[0-9.]+)_rw(?P<rw>[0-9.]+)",
        parameter_set_id,
    )
    if not match:
        return None
    return RelationParams(
        parameter_set_id=parameter_set_id,
        coordinate_count=int(match.group("n")),
        alphabet_size=int(match.group("a")),
        neighborhood_radius=int(match.group("r")),
        update_footprint=int(match.group("m")),
        out_degree_target=int(match.group("k")),
        constraint_density=float(match.group("cd")),
        constraint_strength=float(match.group("cs")),
        asymmetry_strength=float(match.group("asym")),
        reversibility_fraction=float(match.group("rev")),
        rewire_probability=float(match.group("rw")),
        roughness_strength=0.01,
        constraint_arity=2,
        constraint_change_weight=0.35,
    )


def metadata_from_params(params: RelationParams) -> dict[str, object]:
    return {
        "parameter_set_id": params.parameter_set_id,
        "coordinate_count": params.coordinate_count,
        "alphabet_size": params.alphabet_size,
        "neighborhood_radius": params.neighborhood_radius,
        "update_footprint": params.update_footprint,
        "out_degree_target": params.out_degree_target,
        "constraint_density": params.constraint_density,
        "constraint_strength": params.constraint_strength,
        "asymmetry_strength": params.asymmetry_strength,
        "reversibility_fraction": params.reversibility_fraction,
        "rewire_probability": params.rewire_probability,
        "roughness_strength": params.roughness_strength,
        "constraint_arity": params.constraint_arity,
        "constraint_change_weight": params.constraint_change_weight,
    }


def group_by(rows: list[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[object, ...], list[dict[str, object]]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row.get(key, "") for key in keys), []).append(row)
    return grouped


def strip_internal(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{key: value for key, value in row.items() if key not in {"metadata_json"}} for row in rows]


def _counts(values: object) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:  # type: ignore[union-attr]
        out[str(value)] = out.get(str(value), 0) + 1
    return out


def _mean(values: object) -> float:
    numbers = [float(value) for value in values]  # type: ignore[union-attr]
    return mean(numbers) if numbers else 0.0


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("empty\n", encoding="utf-8")
        return
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
