from __future__ import annotations

import argparse
import csv
import json
import math
import time
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from statistics import mean

from .detectors import entropy_from_counts, js_divergence, smoothed_kl
from .landscape import exact_frontier, signature_distribution
from .relation_generator import RelationParams, generate_relation_system, generated_null_systems
from .run_path_metric_calibration import build_probe, probe_resolution_class


TRIVIALITY_NULLS = ("frontier_size_only", "probe_marginal_only", "frontier_size_plus_probe_marginal")
SUPPORT_NULLS = ("signature_support_matched", "horizon_local_frontier_matched", "window_local_frontier_matched")
MECHANISM_NULLS = ("constraint_shuffled", "asymmetry_shuffled", "roughness_resampled")
DESTRUCTIVE_NULLS = ("degree_preserving_rewire", "out_degree_preserving_random")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 support/distribution deformation taxonomy smoke.")
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260525_relation_generator_phenotype_repair"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260525_support_distribution_taxonomy_smoke"))
    parser.add_argument("--candidate-envs", type=int, default=24)
    parser.add_argument("--start-samples-list", type=str, default="3,8")
    parser.add_argument("--horizons", type=str, default="0,1,2,4,8,12,16")
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-jobs", type=int, default=720)
    parser.add_argument("--checkpoint-every", type=int, default=72)
    parser.add_argument("--max-runtime-seconds", type=int, default=7200)
    parser.add_argument(
        "--probe-families",
        type=str,
        default=(
            "existing_low,coordinate_tuple_k3,coordinate_tuple_k4,"
            "constraint_violation_count,constraint_violation_count_plus_local_tuple,"
            "constraint_profile_hash,relation_role,full_state_hash"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    start_samples = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    horizons = tuple(int(item.strip()) for item in args.horizons.split(",") if item.strip())
    probe_keys = tuple(item.strip() for item in args.probe_families.split(",") if item.strip())
    jobs, selection_rows, matched_rows = build_jobs(args, start_samples, horizons, probe_keys)
    jobs = jobs[: args.max_jobs]
    config = {
        "status": "RUNNING",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "started_perf_counter": started,
        "workers": args.workers,
        "max_runtime_seconds": args.max_runtime_seconds,
        "jobs_requested": len(jobs),
        "candidate_envs": args.candidate_envs,
        "start_samples_list": list(start_samples),
        "horizons": list(horizons),
        "probe_families": list(probe_keys),
        "promotion_enabled": False,
    }
    (args.out / "config.json").write_text(json.dumps(_jsonable(config), indent=2, sort_keys=True), encoding="utf-8")
    results: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    pending = list(jobs)
    executor = ProcessPoolExecutor(max_workers=max(1, args.workers))
    futures = {}
    timed_out = False
    try:
        while pending or futures:
            while pending and len(futures) < max(1, args.workers):
                job = pending.pop(0)
                futures[executor.submit(run_job, job)] = job
            remaining = args.max_runtime_seconds - (time.perf_counter() - started)
            if remaining <= 0:
                config["status"] = "TIME_LIMIT_REACHED"
                timed_out = True
                break
            done, _pending = wait(futures, timeout=max(0.1, min(2.0, remaining)), return_when=FIRST_COMPLETED)
            for future in done:
                job = futures.pop(future)
                try:
                    results.extend(future.result())
                except Exception as exc:  # noqa: BLE001
                    errors.append({"job_id": job.get("job_id", ""), "error": repr(exc)})
            if results and len(results) % max(1, args.checkpoint_every) == 0:
                write_outputs(args.out, config, started, jobs, results, selection_rows, matched_rows, errors)
    finally:
        if timed_out:
            for future in futures:
                future.cancel()
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    if config["status"] == "RUNNING":
        config["status"] = "COMPLETED"
    write_outputs(args.out, config, started, jobs, results, selection_rows, matched_rows, errors)


def build_jobs(
    args: argparse.Namespace,
    start_samples: tuple[int, ...],
    horizons: tuple[int, ...],
    probe_keys: tuple[str, ...],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    phenotype_rows = _read_csv(args.source_run / "candidate_phenotype_summary.csv")
    stage_dir = args.source_run / "start_samples_3"
    metadata = {row["environment_id"]: row for row in _read_csv(stage_dir / "generated_environment_metadata.csv")}
    windows = _read_csv(stage_dir / "relation_atlas_window_summary.csv")
    controls = [
        row for row in windows
        if row.get("aggregate_window_class_v1_2") != "structured_candidate_window"
        and row.get("family") in metadata
    ]
    candidates = [
        row for row in phenotype_rows
        if row.get("roughness_artifact_flag") == "0"
        and row.get("start_coverage_class") in {"environment_level", "basin_local"}
        and row.get("environment_id") in metadata
    ]
    candidates.sort(key=lambda row: (row.get("start_coverage_class") == "environment_level", row.get("phenotype_class")), reverse=True)
    selected = []
    seen_envs = set()
    for row in candidates:
        env = row["environment_id"]
        if env not in seen_envs:
            selected.append(row)
            seen_envs.add(env)
        if len(selected) >= args.candidate_envs:
            break

    jobs: list[dict[str, object]] = []
    selection_rows = []
    matched_rows = []
    for index, candidate in enumerate(selected):
        env = candidate["environment_id"]
        source_probe = candidate["probe_family"]
        matched = match_control(candidate, controls, metadata)
        selection_rows.append(
            {
                "candidate_index": index,
                "candidate_environment_id": env,
                "candidate_id": candidate.get("candidate_id", ""),
                "source_probe_family": source_probe,
                "source_window_name": candidate.get("window_name", ""),
                "matched_control_environment_id": matched.get("family", ""),
                "matched_control_match_quality": matched.get("match_quality", "none"),
            }
        )
        rows_for_candidate = [("candidate", env, source_probe, candidate.get("window_name", ""), candidate.get("candidate_id", f"candidate_{index}"))]
        if matched:
            matched_rows.append(
                {
                    "candidate_environment_id": env,
                    "matched_control_environment_id": matched["family"],
                    "matched_control_probe_family": matched["probe_family"],
                    "matched_control_window": matched["window"],
                    "matched_control_match_quality": matched["match_quality"],
                }
            )
            rows_for_candidate.append(("matched_control", matched["family"], matched["probe_family"], matched["window"], f"control_for_{index}"))
        same_env = [row for row in controls if row["family"] == env and row["probe_family"] == source_probe][:1]
        for control in same_env:
            rows_for_candidate.append(("same_environment_window_control", control["family"], control["probe_family"], control["window"], f"same_env_control_for_{index}"))
        for start_count in start_samples:
            for probe_key in probe_keys:
                for row_kind, row_env, row_probe, row_window, row_id in rows_for_candidate:
                    jobs.append(
                        {
                            "job_id": f"{row_kind}_{index}_{start_count}_{probe_key}",
                            "row_kind": row_kind,
                            "row_id": row_id,
                            "candidate_environment_id": env,
                            "environment_id": row_env,
                            "metadata_json": metadata[row_env]["metadata_json"],
                            "seed": int(metadata[row_env]["seed"]),
                            "source_probe_family": row_probe,
                            "probe_key": probe_key,
                            "source_window_name": row_window,
                            "start_samples": start_count,
                            "horizons": horizons,
                        }
                    )
    return jobs, selection_rows, matched_rows


def match_control(candidate: dict[str, str], controls: list[dict[str, str]], metadata: dict[str, dict[str, str]]) -> dict[str, str]:
    candidate_meta = json.loads(metadata[candidate["environment_id"]]["metadata_json"])
    best = None
    best_score = -1
    for control in controls:
        if control["family"] == candidate["environment_id"]:
            continue
        control_meta = json.loads(metadata[control["family"]]["metadata_json"])
        score = 0
        for key in ("out_degree_target", "constraint_density", "constraint_strength", "asymmetry_strength", "reversibility_fraction", "roughness_strength"):
            score += int(str(candidate_meta.get(key)) == str(control_meta.get(key)))
        if score > best_score:
            best = dict(control)
            best_score = score
    if best is None:
        return {}
    best["match_quality"] = "strong" if best_score >= 4 else "weak"
    return best


def run_job(job: dict[str, object]) -> list[dict[str, object]]:
    params = params_from_metadata(json.loads(str(job["metadata_json"])))
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
        stabilization_h = stabilization_horizon(support_curve, horizons)
        for h in horizons:
            observed = observed_by_h[h]
            support_size = len(observed)
            support_fraction = support_size / max(1, alphabet_size)
            collision = max(0.0, 1.0 - support_size / max(1, len(system.states)))
            support_jaccards = [jaccard(observed, null_by_name[name][h]) for name in sorted(null_by_name)]
            trivial_js = [js_divergence(observed, null_by_name[name][h]) for name in TRIVIALITY_NULLS if name in null_by_name]
            support_js = [js_divergence(observed, null_by_name[name][h]) for name in SUPPORT_NULLS if name in null_by_name]
            mechanism_js = {name: js_divergence(observed, null_by_name[name][h]) for name in MECHANISM_NULLS if name in null_by_name}
            destructive_js = {name: js_divergence(observed, null_by_name[name][h]) for name in DESTRUCTIVE_NULLS if name in null_by_name}
            full_entropy = math.log2(max(1, alphabet_size))
            row = {
                "job_id": job["job_id"],
                "row_kind": job["row_kind"],
                "row_id": job["row_id"],
                "candidate_environment_id": job["candidate_environment_id"],
                "environment_id": job["environment_id"],
                "parameter_set_id": params.parameter_set_id,
                "probe_key": job["probe_key"],
                "source_probe_family": job["source_probe_family"],
                "probe_family": probe.probe_family,
                "probe_group": probe_group,
                "probe_signature_alphabet_size": alphabet_size,
                "start_samples": job["start_samples"],
                "start_index": start_index,
                "H": h,
                "source_window_name": job["source_window_name"],
                "frontier_size": sum(observed.values()),
                "reachable_signature_support_size": support_size,
                "reachable_signature_support_fraction": support_fraction,
                "observed_signature_support_size": support_size,
                "observed_signature_support_fraction": support_fraction,
                "probe_collision_rate": collision,
                "support_ceiling_flag": int(support_fraction >= 0.90),
                "support_floor_flag": int(support_fraction <= 0.05),
                "support_extreme_flag": int(support_fraction >= 0.90 or support_fraction <= 0.05),
                "support_regime_class": support_regime_class(support_fraction),
                "probe_resolution_class": probe_resolution_class(collision, support_fraction, 2 ** entropy_from_counts(observed), len(system.states), probe.probe_family),
                "signature_entropy": entropy_from_counts(observed),
                "signature_entropy_ceiling_fraction": entropy_from_counts(observed) / max(1e-9, full_entropy),
                "support_jaccard_vs_null": mean(support_jaccards) if support_jaccards else "",
                "JS_to_triviality_nulls": mean(trivial_js) if trivial_js else "",
                "JS_to_support_nulls": mean(support_js) if support_js else "",
                "KL_to_triviality_nulls": mean(smoothed_kl(observed, null_by_name[name][h]) for name in TRIVIALITY_NULLS if name in null_by_name),
                "mass_concentration_top_k": mass_concentration(observed, 3),
                "support_concentration_index": mass_concentration(observed, 1),
                "support_growth_curve": json.dumps(support_curve),
                "support_growth_slope": slope(support_curve, horizons),
                "support_growth_curvature": curvature(support_curve),
                "support_stabilization_H": stabilization_h,
                "support_saturation_H": saturation_horizon(support_curve, horizons, alphabet_size),
                "distribution_stabilization_H": stabilization_horizon([round(value, 6) for value in entropy_curve], horizons),
                "pre_saturation_deformation_score": mean([value for hh, value in zip(horizons, trivial_js_by_h(observed_by_h, null_by_name, horizons), strict=True) if hh <= 2] or [0.0]),
                "near_saturation_deformation_score": mean([value for hh, value in zip(horizons, trivial_js_by_h(observed_by_h, null_by_name, horizons), strict=True) if 2 < hh <= 8] or [0.0]),
                "post_saturation_deformation_score": mean([value for hh, value in zip(horizons, trivial_js_by_h(observed_by_h, null_by_name, horizons), strict=True) if hh > 8] or [0.0]),
                "constraint_js": mechanism_js.get("constraint_shuffled", ""),
                "asymmetry_js": mechanism_js.get("asymmetry_shuffled", ""),
                "roughness_js": mechanism_js.get("roughness_resampled", ""),
                "degree_js": destructive_js.get("degree_preserving_rewire", ""),
                "outdegree_random_js": destructive_js.get("out_degree_preserving_random", ""),
                "metadata_json": json.dumps(system.metadata, sort_keys=True),
            }
            row.update(classify_pre_control(row))
            rows.append(row)
    return rows


def diagnostic_nulls(system: object, probe: object, observed_by_h: dict[int, dict[object, int]], horizons: tuple[int, ...]) -> dict[str, dict[int, dict[object, int]]]:
    full_counts = Counter(probe.fn(state) for state in system.states)  # type: ignore[attr-defined]
    signatures = sorted(full_counts, key=str)
    out = {name: {} for name in TRIVIALITY_NULLS + SUPPORT_NULLS}
    for h in horizons:
        observed = observed_by_h[h]
        frontier_size = max(1, sum(observed.values()))
        support = sorted(observed, key=str) or signatures[:1]
        out["frontier_size_only"][h] = uniform_counts(signatures, frontier_size)
        out["probe_marginal_only"][h] = dict(full_counts)
        out["frontier_size_plus_probe_marginal"][h] = scaled_counts(full_counts, frontier_size)
        out["signature_support_matched"][h] = uniform_counts(support, frontier_size)
        out["horizon_local_frontier_matched"][h] = scaled_counts(full_counts, frontier_size)
        out["window_local_frontier_matched"][h] = scaled_counts(full_counts, frontier_size)
    return out


def classify_pre_control(row: dict[str, object]) -> dict[str, object]:
    support_limited = int(row["support_ceiling_flag"])
    support_floor_limited = int(row.get("support_floor_flag", 0) or 0)
    collision_limited = float(row["probe_collision_rate"]) >= 0.95
    identity_like = row["probe_resolution_class"] == "identity_like_control"
    trivial_js = float(row.get("JS_to_triviality_nulls", 0.0) or 0.0)
    support_js = float(row.get("JS_to_support_nulls", 0.0) or 0.0)
    entropy_fraction = float(row.get("signature_entropy_ceiling_fraction", 0.0) or 0.0)
    support_result = "support_deformation" if trivial_js >= 0.05 else "weak"
    distribution_result = "distribution_deformation" if support_js >= 0.05 and entropy_fraction < 0.95 else "weak"
    if support_limited:
        probe_result = "support_ceiling_limited"
    elif collision_limited:
        probe_result = "probe_collision_limited"
    elif identity_like:
        probe_result = "identity_like_control"
    else:
        probe_result = "usable"
    if probe_result in {"probe_collision_limited", "support_ceiling_limited", "identity_like_control"}:
        primary = probe_result
    elif support_result == "support_deformation" and distribution_result == "distribution_deformation":
        primary = "mixed_support_distribution_candidate"
    elif support_result == "support_deformation":
        primary = "support_deformation_candidate"
    elif distribution_result == "distribution_deformation":
        primary = "distribution_deformation_candidate"
    else:
        primary = "underdetermined"
    mechanism_tags = []
    if _float(row.get("constraint_js")) is not None and float(row["constraint_js"]) >= 0.05:
        mechanism_tags.append("constraint_dependent")
    if _float(row.get("asymmetry_js")) is not None and float(row["asymmetry_js"]) >= 0.05:
        mechanism_tags.append("asymmetry_dependent")
    if _float(row.get("roughness_js")) is not None and float(row["roughness_js"]) >= 0.05:
        mechanism_tags.append("roughness_sensitive")
    if _float(row.get("outdegree_random_js")) is not None and float(row["outdegree_random_js"]) >= 0.05:
        mechanism_tags.append("outdegree_ablation_sensitive")
    return {
        "support_result": support_result,
        "distribution_result": distribution_result,
        "probe_result": probe_result,
        "support_floor_result": "support_floor_sparse" if support_floor_limited else "not_floor_limited",
        "matched_control_result": "pending",
        "start_result": "pending",
        "mechanism_result": ";".join(mechanism_tags) if mechanism_tags else "underdetermined",
        "primary_class": primary,
        "fakeout_class": "none" if primary.endswith("_candidate") else primary,
        "base_fakeout_class": "none" if primary.endswith("_candidate") else primary,
        "promotion_enabled": False,
    }


def support_regime_class(support_fraction: float) -> str:
    if support_fraction <= 0.05:
        return "support_floor_sparse"
    if support_fraction >= 0.90:
        return "support_ceiling_saturated"
    return "middle_support_regime"


def write_outputs(
    out_dir: Path,
    config: dict[str, object],
    started: float,
    jobs: list[dict[str, object]],
    rows: list[dict[str, object]],
    selection_rows: list[dict[str, object]],
    matched_rows: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    apply_matched_control_labels(rows)
    candidate_summary = candidate_summary_rows(rows)
    horizon_rows = rows
    window_rows = window_summary_rows(rows)
    probe_rows = probe_diagnostic_rows(rows)
    recurrence_rows = start_recurrence_rows(rows)
    regime_rows = regime_map_rows(candidate_summary)
    fakeout_rows = fakeout_summary_rows(rows)
    mechanism_rows = mechanism_tag_rows(rows)
    _write_csv(out_dir / "support_distribution_candidate_summary.csv", candidate_summary)
    _write_csv(out_dir / "support_distribution_metric_by_horizon.csv", horizon_rows)
    _write_csv(out_dir / "support_distribution_metric_by_window.csv", window_rows)
    _write_csv(out_dir / "support_distribution_matched_controls.csv", matched_rows)
    _write_csv(out_dir / "support_distribution_probe_diagnostics.csv", probe_rows)
    _write_csv(out_dir / "support_distribution_start_recurrence.csv", recurrence_rows)
    _write_csv(out_dir / "support_distribution_regime_map.csv", regime_rows)
    _write_csv(out_dir / "support_distribution_fakeout_summary.csv", fakeout_rows)
    _write_csv(out_dir / "support_distribution_mechanism_tags.csv", mechanism_rows)
    _write_csv(out_dir / "selection.csv", selection_rows)
    _write_csv(out_dir / "errors.csv", errors)
    write_report(out_dir, config, started, rows, candidate_summary, fakeout_rows, regime_rows, errors)
    status = {
        "status": config.get("status", "RUNNING"),
        "wall_clock_seconds": time.perf_counter() - started,
        "jobs_requested": len(jobs),
        "jobs_completed": len({row["job_id"] for row in rows}),
        "metric_rows_completed": len(rows),
        "errors": len(errors),
        "promotion_enabled": False,
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")


def apply_matched_control_labels(rows: list[dict[str, object]]) -> None:
    controls = {}
    for row in rows:
        if row["row_kind"] == "matched_control":
            controls.setdefault((row["candidate_environment_id"], row["probe_key"], row["start_samples"], row["H"], row["start_index"]), row)
    for row in rows:
        if row["row_kind"] != "candidate":
            continue
        row["fakeout_class"] = row.get("base_fakeout_class", row.get("fakeout_class", "none"))
        base_primary = row.get("primary_class", "underdetermined")
        control = controls.get((row["candidate_environment_id"], row["probe_key"], row["start_samples"], row["H"], row["start_index"]))
        if not control:
            row["matched_control_result"] = "no_control"
            row["primary_class"] = "underdetermined"
            row["fakeout_class"] = append_tag(str(row["fakeout_class"]), "descriptive_only_no_matched_control")
            continue
        row["primary_class"] = base_primary
        row["matched_control_environment_id"] = control["environment_id"]
        row["support_jaccard_vs_matched_control"] = jaccard_counts(row, control)
        row["TV_distance_to_matched_control"] = abs(float(row["mass_concentration_top_k"]) - float(control["mass_concentration_top_k"]))
        row["mass_shift_vs_control"] = float(row["signature_entropy"]) - float(control["signature_entropy"])
        row["candidate_deformation_score"] = deformation_score(row)
        row["matched_control_deformation_score"] = deformation_score(control)
        if row["candidate_deformation_score"] > row["matched_control_deformation_score"] + 0.02:
            row["matched_control_result"] = "candidate_exceeds_control"
        elif row["matched_control_deformation_score"] > row["candidate_deformation_score"] + 0.02:
            row["matched_control_result"] = "control_exceeds_candidate"
            row["primary_class"] = "matched_control_equivalent"
            row["fakeout_class"] = append_tag(str(row["fakeout_class"]), "matched_control_equivalent")
        else:
            row["matched_control_result"] = "control_equivalent"
            row["primary_class"] = "matched_control_equivalent"
            row["fakeout_class"] = append_tag(str(row["fakeout_class"]), "matched_control_equivalent")


def candidate_summary_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        if row["row_kind"] == "candidate":
            key = (row["candidate_environment_id"], row["probe_key"], row["start_samples"])
            grouped.setdefault(key, []).append(row)
    out = []
    for (env, probe_key, start_samples), items in sorted(grouped.items(), key=lambda item: str(item[0])):
        class_counts = _counts(row["primary_class"] for row in items)
        support_rate = mean(int(row["support_result"] == "support_deformation") for row in items)
        distribution_rate = mean(int(row["distribution_result"] == "distribution_deformation") for row in items)
        pass_rate = mean(int(row["matched_control_result"] == "candidate_exceeds_control") for row in items)
        primary = max(class_counts.items(), key=lambda item: item[1])[0]
        out.append(
            {
                "candidate_environment_id": env,
                "parameter_set_id": items[0]["parameter_set_id"],
                "probe_key": probe_key,
                "probe_family": items[0]["probe_family"],
                "start_samples": start_samples,
                "primary_class": primary,
                "support_deformation_rate": support_rate,
                "distribution_deformation_rate": distribution_rate,
                "candidate_exceeds_control_rate": pass_rate,
                "probe_family_recurrence_key": f"{env}|{probe_key}",
                "mean_probe_collision_rate": _mean(row["probe_collision_rate"] for row in items),
                "mean_support_fraction": _mean(row["reachable_signature_support_fraction"] for row in items),
                "mean_signature_entropy_ceiling_fraction": _mean(row["signature_entropy_ceiling_fraction"] for row in items),
                "mean_deformation_score": _mean(deformation_score(row) for row in items),
                "class_counts_json": json.dumps(class_counts, sort_keys=True),
                "mechanism_result": summarize_tags(row["mechanism_result"] for row in items),
            }
        )
    return out


def window_summary_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    windows = {"early_window": lambda h: h <= 4, "pre_saturation_window": lambda h: 4 <= h <= 12, "long_window": lambda h: h >= 8}
    for name, predicate in windows.items():
        for key, items in _group(rows, ("row_kind", "candidate_environment_id", "environment_id", "probe_key", "start_samples")).items():
            selected = [row for row in items if predicate(int(row["H"]))]
            if not selected:
                continue
            out.append(
                {
                    "window": name,
                    "row_kind": key[0],
                    "candidate_environment_id": key[1],
                    "environment_id": key[2],
                    "probe_key": key[3],
                    "start_samples": key[4],
                    "mean_support_fraction": _mean(row["reachable_signature_support_fraction"] for row in selected),
                    "mean_JS_to_triviality_nulls": _mean(row["JS_to_triviality_nulls"] for row in selected),
                    "mean_JS_to_support_nulls": _mean(row["JS_to_support_nulls"] for row in selected),
                    "dominant_primary_class": max(_counts(row["primary_class"] for row in selected).items(), key=lambda item: item[1])[0],
                }
            )
    return out


def probe_diagnostic_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for key, items in _group(rows, ("probe_family", "probe_group")).items():
        out.append(
            {
                "probe_family": key[0],
                "probe_group": key[1],
                "n_rows": len(items),
                "mean_probe_collision_rate": _mean(row["probe_collision_rate"] for row in items),
                "mean_support_fraction": _mean(row["reachable_signature_support_fraction"] for row in items),
                "support_ceiling_rate": _mean(row["support_ceiling_flag"] for row in items),
                "probe_resolution_class_counts": json.dumps(_counts(row["probe_resolution_class"] for row in items), sort_keys=True),
            }
        )
    return out


def start_recurrence_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for key, items in _group([row for row in rows if row["row_kind"] == "candidate"], ("candidate_environment_id", "probe_key")).items():
        starts = sorted({int(row["start_samples"]) for row in items})
        classes = _counts(row["primary_class"] for row in items)
        candidate_rates = {
            start: mean(int(row["primary_class"].endswith("_candidate")) for row in items if int(row["start_samples"]) == start)
            for start in starts
        }
        if len(starts) >= 2 and min(candidate_rates.values()) >= 0.50:
            start_result = "environment_level"
        elif len(starts) >= 2 and max(candidate_rates.values()) >= 0.50:
            start_result = "basin_local"
        else:
            start_result = "start_local"
        out.append(
            {
                "candidate_environment_id": key[0],
                "probe_key": key[1],
                "start_samples_observed": json.dumps(starts),
                "support_phenotype_recurrence_across_starts": min(candidate_rates.values()) if candidate_rates else 0.0,
                "distribution_phenotype_recurrence_across_starts": mean(int(row["distribution_result"] == "distribution_deformation") for row in items),
                "start_result": start_result,
                "primary_class_counts": json.dumps(classes, sort_keys=True),
            }
        )
    return out


def regime_map_rows(candidate_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for region, items in _group(candidate_rows, ("parameter_set_id",)).items():
        out.append(
            {
                "parameter_region_id": region[0],
                "n_candidate_rows": len(items),
                "support_deformation_rate": _mean(row["support_deformation_rate"] for row in items),
                "distribution_deformation_rate": _mean(row["distribution_deformation_rate"] for row in items),
                "mixed_deformation_rate": mean(int(row["primary_class"] == "mixed_support_distribution_candidate") for row in items),
                "matched_control_equivalent_rate": mean(int(row["primary_class"] == "matched_control_equivalent") for row in items),
                "probe_limited_rate": mean(int(str(row["primary_class"]).endswith("_limited") or str(row["primary_class"]) == "identity_like_control") for row in items),
                "constraint_dependent_rate": mean(int("constraint_dependent" in str(row["mechanism_result"])) for row in items),
                "roughness_sensitive_rate": mean(int("roughness_sensitive" in str(row["mechanism_result"])) for row in items),
            }
        )
    return out


def fakeout_summary_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter()
    for row in rows:
        if row.get("row_kind") != "candidate":
            continue
        for item in str(row.get("fakeout_class", "none")).split(";"):
            if item and item != "none":
                counts[item] += 1
    return [{"fakeout_class": key, "n_rows": value} for key, value in sorted(counts.items())]


def mechanism_tag_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter()
    for row in rows:
        for item in str(row.get("mechanism_result", "underdetermined")).split(";"):
            if item:
                counts[item] += 1
    return [{"mechanism_tag": key, "n_rows": value} for key, value in sorted(counts.items())]


def write_report(
    out_dir: Path,
    config: dict[str, object],
    started: float,
    rows: list[dict[str, object]],
    candidate_rows: list[dict[str, object]],
    fakeout_rows: list[dict[str, object]],
    regime_rows: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    class_counts = _counts(row["primary_class"] for row in candidate_rows)
    probe_counts = _counts(row["probe_family"] for row in candidate_rows if str(row["primary_class"]).endswith("_candidate"))
    next_focus = "continue support/distribution taxonomy" if any(str(key).endswith("_candidate") for key in class_counts) else "pause or tighten measurement limits"
    lines = [
        "# RFS-MB0 Support/Distribution Deformation Taxonomy Report",
        "",
        "Promotion disabled: this is a deformation taxonomy run, not a path-process or Omega validation run.",
        "",
        f"- Wall clock used: {time.perf_counter() - started:.1f} seconds",
        f"- Workers requested: {config['workers']}",
        f"- Jobs requested: {config['jobs_requested']}",
        f"- Metric rows completed: {len(rows)}",
        f"- Errors: {len(errors)}",
        f"- Recommended next focus: {next_focus}",
        "",
        "## Candidate Classes",
        "",
        "| class | n |",
        "|---|---:|",
    ]
    for key, value in sorted(class_counts.items()):
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Candidate Probe Recurrence", "", "| probe_family | candidate_rows |", "|---|---:|"])
    for key, value in sorted(probe_counts.items()):
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Fakeouts", "", "| fakeout | n |", "|---|---:|"])
    for row in fakeout_rows:
        lines.append(f"| {row['fakeout_class']} | {row['n_rows']} |")
    lines.extend(["", "## Regime Map Rows", "", f"- Regime rows: {len(regime_rows)}", "", "## Claim Boundary", "", "This run classifies support/distribution deformation phenotypes under controls. It does not claim agency, identity, valuerhood, path-process detection, Omega detection, or scientific-gate passage."])
    (out_dir / "support_distribution_taxonomy_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def uniform_counts(signatures: list[object], total: int) -> dict[object, int]:
    if not signatures or total <= 0:
        return {}
    counts = {signature: total // len(signatures) for signature in signatures}
    for index in range(total - sum(counts.values())):
        counts[signatures[index % len(signatures)]] += 1
    return {key: value for key, value in counts.items() if value > 0}


def scaled_counts(counts: Counter[object], total: int) -> dict[object, int]:
    source_total = sum(counts.values())
    if source_total <= 0 or total <= 0:
        return {}
    signatures = sorted(counts, key=str)
    scaled = {signature: max(0, round(total * counts[signature] / source_total)) for signature in signatures}
    drift = total - sum(scaled.values())
    index = 0
    while drift != 0 and signatures:
        signature = signatures[index % len(signatures)]
        if drift > 0:
            scaled[signature] += 1
            drift -= 1
        elif scaled[signature] > 0:
            scaled[signature] -= 1
            drift += 1
        index += 1
    return {key: value for key, value in scaled.items() if value > 0}


def jaccard(left: dict[object, int], right: dict[object, int]) -> float:
    left_support = set(left)
    right_support = set(right)
    if not left_support and not right_support:
        return 1.0
    return len(left_support & right_support) / max(1, len(left_support | right_support))


def jaccard_counts(row: dict[str, object], control: dict[str, object]) -> float:
    left = float(row["reachable_signature_support_size"])
    right = float(control["reachable_signature_support_size"])
    return min(left, right) / max(1.0, max(left, right))


def mass_concentration(counts: dict[object, int], k: int) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    return sum(sorted(counts.values(), reverse=True)[:k]) / total


def append_tag(existing: str, tag: str) -> str:
    parts = [item for item in existing.split(";") if item and item != "none"]
    if tag not in parts:
        parts.append(tag)
    return ";".join(parts) if parts else "none"


def deformation_score(row: dict[str, object]) -> float:
    return float(row.get("JS_to_triviality_nulls", 0.0) or 0.0) + float(row.get("JS_to_support_nulls", 0.0) or 0.0)


def trivial_js_by_h(observed_by_h: dict[int, dict[object, int]], null_by_name: dict[str, dict[int, dict[object, int]]], horizons: tuple[int, ...]) -> list[float]:
    return [
        mean(js_divergence(observed_by_h[h], null_by_name[name][h]) for name in TRIVIALITY_NULLS if name in null_by_name)
        for h in horizons
    ]


def slope(values: list[float | int], horizons: tuple[int, ...]) -> float:
    if len(values) < 2:
        return 0.0
    return (float(values[-1]) - float(values[0])) / max(1, horizons[-1] - horizons[0])


def curvature(values: list[float | int]) -> float:
    if len(values) < 3:
        return 0.0
    second = [float(values[i + 1]) - 2 * float(values[i]) + float(values[i - 1]) for i in range(1, len(values) - 1)]
    return mean(second)


def stabilization_horizon(values: list[float | int], horizons: tuple[int, ...]) -> int | str:
    if not values:
        return ""
    final = values[-1]
    for h, value in zip(horizons, values, strict=True):
        if value == final:
            return h
    return horizons[-1]


def saturation_horizon(values: list[int], horizons: tuple[int, ...], alphabet_size: int) -> int | str:
    for h, value in zip(horizons, values, strict=True):
        if value / max(1, alphabet_size) >= 0.95:
            return h
    return ""


def params_from_metadata(metadata: dict[str, object]) -> RelationParams:
    return RelationParams(
        parameter_set_id=str(metadata["parameter_set_id"]),
        coordinate_count=int(metadata["coordinate_count"]),
        alphabet_size=int(metadata["alphabet_size"]),
        neighborhood_radius=int(metadata["neighborhood_radius"]),
        update_footprint=int(metadata["update_footprint"]),
        out_degree_target=int(metadata["out_degree_target"]),
        constraint_density=float(metadata["constraint_density"]),
        constraint_strength=float(metadata["constraint_strength"]),
        asymmetry_strength=float(metadata["asymmetry_strength"]),
        reversibility_fraction=float(metadata["reversibility_fraction"]),
        rewire_probability=float(metadata["rewire_probability"]),
        roughness_strength=float(metadata.get("roughness_strength", 0.01)),
        constraint_arity=int(metadata.get("constraint_arity", 2)),
        constraint_change_weight=float(metadata.get("constraint_change_weight", 0.35)),
    )


def _group(rows: list[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[object, ...], list[dict[str, object]]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row.get(key, "") for key in keys), []).append(row)
    return grouped


def _counts(values: object) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:  # type: ignore[union-attr]
        out[str(value)] = out.get(str(value), 0) + 1
    return out


def _mean(values: object) -> float:
    numbers = [float(value) for value in values]  # type: ignore[union-attr]
    return mean(numbers) if numbers else 0.0


def _float(value: object) -> float | None:
    try:
        if value == "":
            return None
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def summarize_tags(values: object) -> str:
    counts = Counter()
    for value in values:  # type: ignore[union-attr]
        for tag in str(value).split(";"):
            if tag:
                counts[tag] += 1
    if not counts:
        return "underdetermined"
    return ";".join(key for key, _count in counts.most_common())


def _jsonable(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
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
