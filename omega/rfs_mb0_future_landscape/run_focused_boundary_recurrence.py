from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import replace
from pathlib import Path
from statistics import pstdev

from .relation_generator import RelationParams
from .run_deformation_detector_sweep import params_from_parameter_set_id, run_sweep_job, stable_seed


PROBE_ROLES = {
    "coordinate_tuple_k3": "evidence",
    "coordinate_tuple_k4": "evidence",
    "constraint_profile_hash": "evidence",
    "constraint_violation_count_plus_local_tuple": "evidence",
    "existing_low": "diagnostic",
    "full_state_hash": "control",
    "full_state_strict": "control",
}
PROBE_AXES = {
    "coordinate_tuple_k3": "coordinate_axis",
    "coordinate_tuple_k4": "coordinate_axis",
    "constraint_profile_hash": "constraint_axis",
    "constraint_violation_count_plus_local_tuple": "constraint_axis",
    "existing_low": "low_projection_axis",
    "relation_role": "relation_role_axis",
    "full_state_hash": "identity_axis",
    "full_state_strict": "identity_axis",
}
REQUIRED_REPAIR_OUTPUTS = (
    "rfs_mb0_detector_instrumentation_repair_report.md",
    "support_regime_summary.csv",
    "probe_limit_decomposition.csv",
    "probe_limit_reason_summary.csv",
    "probe_axis_recurrence_summary.csv",
    "deformation_score_decomposition.csv",
    "focused_group_selection_score_audit.csv",
    "focused_matched_control_bundle.csv",
    "focused_matched_control_rank_effect.csv",
    "focused_margin_sensitivity.csv",
    "corrected_group_classification.csv",
    "corrected_measurement_limits_summary.csv",
    "output_manifest.json",
    "status.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run focused RFS-MB0 boundary recurrence smoke.")
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_focused_boundary_recurrence_smoke"))
    parser.add_argument("--groups", type=int, default=4)
    parser.add_argument("--fresh-seeds-per-group", type=int, default=2)
    parser.add_argument("--start-samples-list", type=str, default="3,8")
    parser.add_argument("--horizons", type=str, default="0,1,2,4,8,12,16,24,32")
    parser.add_argument("--probe-families", type=str, default="coordinate_tuple_k3,coordinate_tuple_k4,constraint_profile_hash,constraint_violation_count_plus_local_tuple,existing_low")
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-runtime-seconds", type=int, default=900)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=120)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    selected = read_csv(args.selection)[: args.groups]
    anchors = {row.get("anchor_id", ""): row for row in read_csv(args.source_run / "atlas_band_selection.csv")}
    starts = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    horizons = tuple(int(item.strip()) for item in args.horizons.split(",") if item.strip())
    probes = tuple(item.strip() for item in args.probe_families.split(",") if item.strip())
    jobs = build_jobs(selected, anchors, starts, horizons, probes, args.fresh_seeds_per_group)
    config: dict[str, object] = {
        "status": "RUNNING",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workers": args.workers,
        "groups_requested": args.groups,
        "groups_selected": len(selected),
        "jobs_requested": len(jobs),
        "jobs_submitted": 0,
        "jobs_completed": 0,
        "jobs_cancelled": 0,
        "pending_jobs_remaining": len(jobs),
        "max_runtime_seconds": args.max_runtime_seconds,
        "shutdown_cushion_seconds": args.shutdown_cushion_seconds,
        "promotion_enabled": False,
    }
    rows, errors = run_jobs(args, jobs, config, started)
    if config["status"] == "RUNNING":
        config["status"] = "COMPLETED"
        config["finalization_reason"] = "all_jobs_completed"
    write_outputs(args.out, config, started, selected, rows, errors)


def build_jobs(
    selected: list[dict[str, str]],
    anchors: dict[str, dict[str, str]],
    starts: tuple[int, ...],
    horizons: tuple[int, ...],
    probes: tuple[str, ...],
    fresh_seeds: int,
) -> list[dict[str, object]]:
    jobs = []
    for group_index, group in enumerate(selected):
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
                            "job_id": f"focused_{group_index:03d}_{seed_index}_{probe}_{start_count}",
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
                        }
                    )
    return jobs


def apply_variant(params: RelationParams, dimension: str, value: str) -> RelationParams:
    if not dimension or dimension == "baseline":
        return params
    if dimension == "out_degree_target":
        return replace(params, **{dimension: int(float(value))})
    return replace(params, **{dimension: float(value)})


def run_jobs(args: argparse.Namespace, jobs: list[dict[str, object]], config: dict[str, object], started: float) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    pending = list(jobs)
    futures = {}
    executor = ProcessPoolExecutor(max_workers=max(1, args.workers))
    try:
        while pending or futures:
            remaining = args.max_runtime_seconds - (time.perf_counter() - started)
            if remaining <= args.shutdown_cushion_seconds:
                config["status"] = "PARTIAL_TIME_LIMIT_REACHED"
                config["finalization_reason"] = "shutdown_cushion_reached"
                break
            while pending and len(futures) < max(1, args.workers):
                job = pending.pop(0)
                futures[executor.submit(run_sweep_job, job)] = job
                config["jobs_submitted"] = int(config["jobs_submitted"]) + 1
            done, _ = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                job = futures.pop(future)
                try:
                    for row in future.result():
                        row["group_id"] = job.get("group_id", "")
                        row["probe_role"] = probe_role(str(row.get("probe_key", "")), str(row.get("probe_family", "")))
                        row["probe_axis"] = probe_axis(str(row.get("probe_key", "")), str(row.get("probe_family", "")))
                        row["is_local_pre_control_candidate_like"] = int(candidate_like(row))
                        row["row_saturation_flag"] = int(saturation_flag(row))
                        annotate_probe_limit(row)
                        rows.append(row)
                except Exception as exc:  # noqa: BLE001
                    errors.append({"job_id": job.get("job_id", ""), "error": repr(exc)})
                config["jobs_completed"] = int(config["jobs_completed"]) + 1
    finally:
        if futures:
            for future in futures:
                future.cancel()
            config["jobs_cancelled"] = len(futures)
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    config["pending_jobs_remaining"] = len(pending)
    return rows, errors


def write_outputs(out_dir: Path, config: dict[str, object], started: float, groups: list[dict[str, str]], rows: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    summary = focused_group_recurrence_summary(rows, groups)
    probe_summary = focused_probe_role_summary(rows)
    saturation = focused_saturation_decomposition(rows)
    terminology = candidate_like_terminology_audit(rows, summary)
    required = required_answer_provenance(summary)
    flags = measurement_limit_flags(summary)
    support_regime = support_regime_summary(rows)
    probe_limits = probe_limit_decomposition(rows)
    probe_limit_reasons = probe_limit_reason_summary(probe_limits)
    axis_summary = probe_axis_recurrence_summary(rows)
    score_decomp = deformation_score_decomposition(rows)
    score_audit = focused_group_selection_score_audit(rows, groups)
    control_bundle = focused_matched_control_bundle(rows)
    control_rank = focused_matched_control_rank_effect(rows, control_bundle)
    margin = focused_margin_sensitivity(control_rank)
    corrected = corrected_group_classification(summary, axis_summary, control_rank)
    corrected_limits = corrected_measurement_limits_summary(corrected)
    write_csv(out_dir / "focused_cross_probe_recurrence.csv", rows)
    write_csv(out_dir / "focused_group_recurrence_summary.csv", summary)
    write_csv(out_dir / "focused_probe_role_summary.csv", probe_summary)
    write_csv(out_dir / "focused_saturation_decomposition.csv", saturation)
    write_csv(out_dir / "focused_candidate_like_terminology_audit.csv", terminology)
    write_csv(out_dir / "focused_required_answer_provenance.csv", required)
    write_csv(out_dir / "focused_measurement_limit_flags.csv", flags)
    write_csv(out_dir / "support_regime_summary.csv", support_regime)
    write_csv(out_dir / "probe_limit_decomposition.csv", probe_limits)
    write_csv(out_dir / "probe_limit_reason_summary.csv", probe_limit_reasons)
    write_csv(out_dir / "probe_axis_recurrence_summary.csv", axis_summary)
    write_csv(out_dir / "deformation_score_decomposition.csv", score_decomp)
    write_csv(out_dir / "focused_group_selection_score_audit.csv", score_audit)
    write_csv(out_dir / "focused_matched_control_bundle.csv", control_bundle)
    write_csv(out_dir / "focused_matched_control_rank_effect.csv", control_rank)
    write_csv(out_dir / "focused_margin_sensitivity.csv", margin)
    write_csv(out_dir / "corrected_group_classification.csv", corrected)
    write_csv(out_dir / "corrected_measurement_limits_summary.csv", corrected_limits)
    write_csv(out_dir / "errors.csv", errors)
    status = {**config, "elapsed_seconds": time.perf_counter() - started, "metric_rows_written": len(rows), "errors": len(errors), "final_outputs_written": True}
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    write_report(out_dir, config, started, groups, rows, summary, flags, errors, corrected)
    write_manifest(out_dir)


def focused_group_recurrence_summary(rows: list[dict[str, object]], groups: list[dict[str, str]]) -> list[dict[str, object]]:
    source = {row.get("group_id", ""): row for row in groups}
    out = []
    for (group_id,), items in group_by(rows, ("group_id",)).items():
        evidence_families = {str(row.get("probe_family", "")) for row in items if row.get("probe_role") == "evidence"}
        evidence_candidates = {str(row.get("probe_family", "")) for row in items if row.get("probe_role") == "evidence" and candidate_like(row)}
        nonsat_evidence_candidates = {str(row.get("probe_family", "")) for row in items if row.get("probe_role") == "evidence" and candidate_like(row) and not saturation_flag(row)}
        candidate_axes = {str(row.get("probe_axis", "")) for row in items if row.get("probe_role") == "evidence" and candidate_like(row)}
        nonsat_candidate_axes = {str(row.get("probe_axis", "")) for row in items if row.get("probe_role") == "evidence" and candidate_like(row) and not saturation_flag(row)}
        starts = group_by(items, ("start_samples",))
        horizons = group_by(items, ("H",))
        saturation_rate = sum(int(saturation_flag(row)) for row in items) / max(1, len(items))
        probe_limited_rate = sum(int("too_coarse" in str(row.get("probe_resolution_class", "")) or "collision" in str(row.get("local_primary_class", ""))) for row in items) / max(1, len(items))
        recurrent = len(evidence_candidates) >= 2
        nonsat_recurrent = len(nonsat_evidence_candidates) >= 2
        independent_axis = {"coordinate_axis", "constraint_axis"}.issubset(candidate_axes)
        independent_axis_nonsat = {"coordinate_axis", "constraint_axis"}.issubset(nonsat_candidate_axes)
        out.append(
            {
                "group_id": group_id,
                "source_band_id": source.get(group_id, {}).get("source_band_id", ""),
                "variant_dimension": source.get(group_id, {}).get("variant_dimension", ""),
                "variant_value": source.get(group_id, {}).get("variant_value", ""),
                "fresh_seed_count": source.get(group_id, {}).get("fresh_seed_count", ""),
                "evidence_probe_count": len(evidence_families),
                "evidence_probe_candidate_count": len(evidence_candidates),
                "evidence_probe_candidate_fraction": len(evidence_candidates) / max(1, len(evidence_families)),
                "evidence_probe_recurrent_flag": int(recurrent),
                "evidence_probe_recurrent_non_saturation_flag": int(nonsat_recurrent),
                "coordinate_axis_hit": int("coordinate_axis" in candidate_axes),
                "constraint_axis_hit": int("constraint_axis" in candidate_axes),
                "independent_axis_recurrent_flag": int(independent_axis),
                "independent_axis_non_saturation_recurrent_flag": int(independent_axis_nonsat),
                "start_recurrence_score": min((candidate_rate(items) for items in starts.values()), default=0.0),
                "horizon_recurrence_score": min((candidate_rate(items) for items in horizons.values()), default=0.0),
                "probe_local_only_flag": int(len(evidence_candidates) <= 1),
                "saturation_contamination_rate": saturation_rate,
                "probe_resolution_contamination_rate": probe_limited_rate,
                "recommended_group_class": group_class(independent_axis, independent_axis_nonsat, saturation_rate, probe_limited_rate),
            }
        )
    return out


def focused_probe_role_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (role,), items in group_by(rows, ("probe_role",)).items():
        out.append({"probe_role": role, "rows": len(items), "candidate_rate": candidate_rate(items), "saturation_rate": sum(int(saturation_flag(row)) for row in items) / max(1, len(items))})
    return out


def focused_saturation_decomposition(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "group_id": row.get("group_id", ""),
            "anchor_id": row.get("anchor_id", ""),
            "variant_dimension": row.get("variant_dimension", ""),
            "variant_value": row.get("variant_value", ""),
            "probe_family": row.get("probe_family", ""),
            "probe_role": row.get("probe_role", ""),
            "probe_axis": row.get("probe_axis", ""),
            "horizon": row.get("H", ""),
            "local_primary_class": row.get("local_primary_class", ""),
            "is_local_pre_control_candidate_like": int(candidate_like(row)),
            "row_saturation_flag": int(saturation_flag(row)),
            "support_floor_flag": row.get("support_floor_flag", ""),
            "support_ceiling_flag": row.get("support_ceiling_flag", ""),
            "support_regime_class": row.get("support_regime_class", support_regime_class(float_or_zero(row.get("reachable_signature_support_fraction")))),
            "probe_resolution_class": row.get("probe_resolution_class", ""),
        }
        for row in rows
    ]


def candidate_like_terminology_audit(rows: list[dict[str, object]], summary: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {"term": "local_pre_control_candidate_like_rows", "value": sum(int(candidate_like(row)) for row in rows)},
        {"term": "matched_control_candidate_like_rows", "value": "not_computed_in_focused_pass"},
        {"term": "band_level_candidate_like_rows", "value": sum(int(row.get("evidence_probe_recurrent_flag", 0)) for row in summary)},
        {"term": "stable_candidate_band_count", "value": 0},
    ]


def support_regime_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (regime,), items in group_by(rows, ("support_regime_class",)).items():
        out.append(
            {
                "support_regime_class": regime or "unknown",
                "rows": len(items),
                "candidate_like_rows": sum(int(candidate_like(row)) for row in items),
                "probe_limited_rows": sum(int(probe_limited(row)) for row in items),
                "matched_control_supported_rows": "computed_in_rank_effect",
            }
        )
    return out


def probe_limit_decomposition(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        reasons = probe_limit_reasons(row)
        out.append(
            {
                "group_id": row.get("group_id", ""),
                "row_id": row.get("job_id", ""),
                "probe_family": row.get("probe_family", ""),
                "probe_role": row.get("probe_role", ""),
                "probe_axis": row.get("probe_axis", ""),
                "local_primary_class": row.get("local_primary_class", ""),
                "collision_limited_flag": int("collision" in str(row.get("local_primary_class", "")) or float_or_zero(row.get("probe_collision_rate")) >= 0.95),
                "identity_like_limited_flag": int("identity_like" in str(row.get("probe_resolution_class", ""))),
                "probe_floor_limited_flag": int(float_or_zero(row.get("support_floor_flag")) > 0),
                "probe_ceiling_limited_flag": int(saturation_flag(row)),
                "probe_local_only_flag": "",
                "probe_limited_flag": int(bool(reasons)),
                "probe_limit_reason": ";".join(reasons) if reasons else "none",
            }
        )
    return out


def probe_limit_reason_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    counts: Counter[str] = Counter()
    for row in rows:
        for reason in str(row.get("probe_limit_reason", "none")).split(";"):
            counts[reason] += 1
    return [{"probe_limit_reason": key, "rows": value} for key, value in sorted(counts.items())]


def probe_axis_recurrence_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (group_id,), items in group_by(rows, ("group_id",)).items():
        candidate_axes = {str(row.get("probe_axis", "")) for row in items if row.get("probe_role") == "evidence" and candidate_like(row)}
        nonsat_axes = {str(row.get("probe_axis", "")) for row in items if row.get("probe_role") == "evidence" and candidate_like(row) and not saturation_flag(row)}
        coordinate = "coordinate_axis" in candidate_axes
        constraint = "constraint_axis" in candidate_axes
        independent = coordinate and constraint
        nonsat_independent = {"coordinate_axis", "constraint_axis"}.issubset(nonsat_axes)
        out.append(
            {
                "group_id": group_id,
                "coordinate_axis_hit": int(coordinate),
                "constraint_axis_hit": int(constraint),
                "any_evidence_probe_recurrent_flag": int(bool(candidate_axes)),
                "same_axis_multi_probe_recurrent_flag": int(any_axis_multi_probe(items)),
                "independent_axis_recurrent_flag": int(independent),
                "independent_axis_non_saturation_recurrent_flag": int(nonsat_independent),
                "independent_axis_clean_recurrent_flag": int(independent and nonsat_independent and not any(probe_limited(row) for row in items)),
                "axis_recurrence_class": axis_recurrence_class(coordinate, constraint, independent),
            }
        )
    return out


def deformation_score_decomposition(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        js = float_or_zero(row.get("JS_to_triviality_nulls")) + float_or_zero(row.get("JS_to_support_nulls"))
        support = float_or_zero(row.get("support_symmetric_difference_fraction"))
        mass = float_or_zero(row.get("mass_concentration_top_k"))
        growth = abs(float_or_zero(row.get("support_growth_slope")))
        combined = 0.40 * js + 0.35 * support + 0.15 * mass + 0.10 * growth
        out.append(
            {
                "group_id": row.get("group_id", ""),
                "row_id": row.get("job_id", ""),
                "js_distribution_score": js,
                "support_set_score": support,
                "mass_concentration_score": mass,
                "support_growth_score": growth,
                "combined_deformation_score": combined,
                "support_growth_score_note": "absolute support_growth_slope proxy",
            }
        )
    return out


def focused_group_selection_score_audit(rows: list[dict[str, object]], groups: list[dict[str, str]]) -> list[dict[str, object]]:
    scores = deformation_score_decomposition(rows)
    by_group = group_by(scores, ("group_id",))
    selected = {row.get("group_id", "") for row in groups}
    out = []
    for group_id, items in by_group.items():
        combined = [float_or_zero(row.get("combined_deformation_score")) for row in items]
        support = [float_or_zero(row.get("support_set_score")) for row in items]
        out.append(
            {
                "group_id": group_id[0],
                "was_selected_originally": int(group_id[0] in selected),
                "mean_combined_deformation_score": sum(combined) / max(1, len(combined)),
                "max_combined_deformation_score": max(combined, default=0.0),
                "mean_support_set_score": sum(support) / max(1, len(support)),
                "support_heavy_group_flag": int((sum(support) / max(1, len(support))) > 0.25),
            }
        )
    return out


def focused_matched_control_bundle(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    by_key = group_by(rows, ("group_id", "probe_axis", "start_samples", "start_index", "H"))
    for key, items in by_key.items():
        candidates = [row for row in items if candidate_like(row)]
        controls = [row for row in items if not candidate_like(row)]
        for candidate in candidates:
            for index, control in enumerate(controls[:5]):
                out.append(
                    {
                        "candidate_row_id": candidate.get("job_id", ""),
                        "control_index": index,
                        "group_id": key[0],
                        "probe_axis": key[1],
                        "start_samples": key[2],
                        "start_index": key[3],
                        "H": key[4],
                        "control_row_id": control.get("job_id", ""),
                        "control_primary_class": control.get("local_primary_class", ""),
                        "candidate_metric": combined_row_score(candidate),
                        "control_metric": combined_row_score(control),
                    }
                )
    return out


def focused_matched_control_rank_effect(rows: list[dict[str, object]], bundle: list[dict[str, object]]) -> list[dict[str, object]]:
    by_candidate = group_by(bundle, ("candidate_row_id",))
    row_by_id = {str(row.get("job_id", "")): row for row in rows}
    out = []
    for (candidate_id,), controls in by_candidate.items():
        candidate = row_by_id.get(str(candidate_id), {})
        control_values = [float_or_zero(row.get("control_metric")) for row in controls]
        candidate_metric = combined_row_score(candidate)
        control_mean = sum(control_values) / max(1, len(control_values))
        control_std = pstdev(control_values)
        out.append(
            {
                "candidate_row_id": candidate_id,
                "group_id": candidate.get("group_id", ""),
                "probe_axis": candidate.get("probe_axis", ""),
                "candidate_metric": candidate_metric,
                "control_mean": control_mean,
                "control_std": control_std,
                "candidate_minus_control_mean": candidate_metric - control_mean,
                "candidate_control_percentile": sum(int(candidate_metric >= value) for value in control_values) / max(1, len(control_values)),
                "control_count": len(control_values),
                "weak_control_bundle_flag": int(len(control_values) < 2),
                "support_jaccard_vs_matched_control": "not_reconstructed_from_aggregate_rows",
                "TV_distance_to_matched_control": abs(float_or_zero(candidate.get("mass_concentration_top_k")) - control_mean),
                "JS_to_matched_control": float_or_zero(candidate.get("JS_to_support_nulls")),
                "combined_score_vs_matched_control": candidate_metric - control_mean,
                "matched_control_class": matched_control_class(candidate_metric, control_mean, len(control_values)),
            }
        )
    return out


def focused_margin_sensitivity(rank_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    margins = (0.00, 0.01, 0.02, 0.05, 0.10)
    out = []
    for row in rank_rows:
        diff = float_or_zero(row.get("candidate_minus_control_mean"))
        for margin in margins:
            out.append(
                {
                    "candidate_row_id": row.get("candidate_row_id", ""),
                    "group_id": row.get("group_id", ""),
                    "margin": margin,
                    "passes_margin": int(diff > margin and not int(row.get("weak_control_bundle_flag", 1))),
                    "margin_class": "matched_control_supported_local_candidate" if diff > margin and not int(row.get("weak_control_bundle_flag", 1)) else row.get("matched_control_class", ""),
                }
            )
    return out


def corrected_group_classification(summary: list[dict[str, object]], axis_summary: list[dict[str, object]], control_rank: list[dict[str, object]]) -> list[dict[str, object]]:
    axis_by_group = {row.get("group_id", ""): row for row in axis_summary}
    controls_by_group = group_by(control_rank, ("group_id",))
    out = []
    for row in summary:
        group_id = row.get("group_id", "")
        axis = axis_by_group.get(group_id, {})
        controls = controls_by_group.get((group_id,), [])
        supported_axes = {str(item.get("probe_axis", "")) for item in controls if item.get("matched_control_class") == "matched_control_supported_local_candidate"}
        weak = any(int(item.get("weak_control_bundle_flag", 0)) for item in controls) or not controls
        collision = float_or_zero(row.get("probe_resolution_contamination_rate")) >= 0.5
        if not int(axis.get("independent_axis_recurrent_flag", 0)):
            klass = "same_axis_only_recurrence"
        elif weak:
            klass = "weak_control_bundle_recurrence"
        elif {"coordinate_axis", "constraint_axis"}.issubset(supported_axes) and not collision:
            klass = "clean_recurrent_boundary_candidate"
        elif collision:
            klass = "independent_axis_recurrent_but_collision_limited"
        else:
            klass = "matched_control_equivalent_recurrence"
        out.append(
            {
                "group_id": group_id,
                "legacy_group_class": row.get("recommended_group_class", ""),
                "corrected_group_class": klass,
                "independent_axis_recurrent_flag": axis.get("independent_axis_recurrent_flag", 0),
                "independent_axis_non_saturation_recurrent_flag": axis.get("independent_axis_non_saturation_recurrent_flag", 0),
                "matched_control_supported_axes": json.dumps(sorted(supported_axes)),
                "weak_control_bundle_flag": int(weak),
            }
        )
    return out


def corrected_measurement_limits_summary(corrected: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter(str(row.get("corrected_group_class", "")) for row in corrected)
    return [{"corrected_group_class": key, "groups": value} for key, value in sorted(counts.items())]


def required_answer_provenance(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    recurrent = [row for row in summary if int(row.get("evidence_probe_recurrent_flag", 0))]
    nonsat = [row for row in summary if int(row.get("evidence_probe_recurrent_non_saturation_flag", 0))]
    return [
        {"required_answer_name": "evidence_probe_recurrent_groups", "value": bool(recurrent), "numerator": len(recurrent), "denominator": len(summary), "source_table": "focused_group_recurrence_summary.csv"},
        {"required_answer_name": "non_saturation_evidence_probe_recurrent_groups", "value": bool(nonsat), "numerator": len(nonsat), "denominator": len(summary), "source_table": "focused_group_recurrence_summary.csv"},
        {"required_answer_name": "n6_transfer_completed", "value": False, "numerator": 0, "denominator": 1, "source_table": "not_run"},
    ]


def measurement_limit_flags(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    clean = [row for row in summary if row.get("recommended_group_class") == "independent_axis_clean_recurrent"]
    return [
        {
            "flag": "measurement_limits_note_required",
            "value": int(not clean),
            "reason": "no clean evidence-probe recurrent boundary candidates; recurrence is probe/saturation limited" if summary else "no focused groups completed",
        }
    ]


def write_report(out_dir: Path, config: dict[str, object], started: float, groups: list[dict[str, str]], rows: list[dict[str, object]], summary: list[dict[str, object]], flags: list[dict[str, object]], errors: list[dict[str, object]], corrected: list[dict[str, object]]) -> None:
    recurrent = sum(int(row.get("evidence_probe_recurrent_flag", 0)) for row in summary)
    nonsat = sum(int(row.get("evidence_probe_recurrent_non_saturation_flag", 0)) for row in summary)
    clean = sum(1 for row in corrected if row.get("corrected_group_class") == "clean_recurrent_boundary_candidate")
    sparse = sum(1 for row in corrected if row.get("corrected_group_class") == "sparse_regime_recurrent_candidate_pending_floor_audit")
    decision = "partial_rescue_tiny_confirmation" if clean or sparse else "measurement_limit_confirmed"
    lines = [
        "# RFS-MB0 Detector Instrumentation Repair Report",
        "",
        "Promotion disabled. This is a focused cross-probe recurrence smoke, not n=6 and not a science-gate run.",
        "",
        f"- Status: {config.get('status', '')}",
        f"- Wall clock used: {time.perf_counter() - started:.1f} seconds",
        f"- Workers requested: {config.get('workers', '')}",
        f"- Groups selected: {len(groups)}",
        f"- Jobs requested: {config.get('jobs_requested', '')}",
        f"- Jobs completed: {config.get('jobs_completed', '')}",
        f"- Metric rows: {len(rows)}",
        f"- Errors: {len(errors)}",
        f"- Evidence-probe recurrent groups: {recurrent}",
        f"- Non-saturation evidence-probe recurrent groups: {nonsat}",
        f"- Clean recurrent boundary candidates: {clean}",
        f"- Sparse pending candidates: {sparse}",
        f"- Decision: {decision}",
        "",
        "## What Changed In Instrumentation",
        "",
        "- Split support ceiling from support floor.",
        "- Split probe limitation reasons into collision, identity-like, floor, ceiling, and probe-local reasons.",
        "- Replaced count-based cross-probe recurrence with independent coordinate-axis plus constraint-axis recurrence.",
        "- Added support-aware deformation score decomposition.",
        "- Added focused matched-control rank/effect tables using same-focused-pass noncandidate rows where available.",
        "",
        "## Claim Boundary",
        "",
        "This run only tests focused evidence-probe recurrence for selected boundary groups. It does not claim Omega, agency, identity, value, viability, or scientific-gate passage.",
    ]
    (out_dir / "boundary_recurrence_repair_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "rfs_mb0_detector_instrumentation_repair_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def group_class(independent_axis: bool, nonsat_independent_axis: bool, saturation_rate: float, probe_limited_rate: float) -> str:
    if independent_axis and nonsat_independent_axis and saturation_rate < 0.5 and probe_limited_rate < 0.5:
        return "independent_axis_clean_recurrent"
    if independent_axis and (saturation_rate >= 0.5 or probe_limited_rate >= 0.5):
        return "independent_axis_recurrent_but_limited"
    if independent_axis:
        return "independent_axis_clean_recurrent"
    return "same_axis_only_recurrence"


def probe_role(probe_key: str, probe_family: str) -> str:
    return PROBE_ROLES.get(probe_key) or PROBE_ROLES.get(probe_family) or "unknown_diagnostic"


def probe_axis(probe_key: str, probe_family: str) -> str:
    return PROBE_AXES.get(probe_key) or PROBE_AXES.get(probe_family) or "unknown_axis"


def annotate_probe_limit(row: dict[str, object]) -> None:
    reasons = probe_limit_reasons(row)
    row["collision_limited_flag"] = int("collision_limited" in reasons)
    row["identity_like_limited_flag"] = int("identity_like_limited" in reasons)
    row["probe_floor_limited_flag"] = int("support_floor_limited" in reasons)
    row["probe_ceiling_limited_flag"] = int("support_ceiling_limited" in reasons)
    row["probe_limited_flag"] = int(bool(reasons))
    row["probe_limit_reason"] = ";".join(reasons) if reasons else "none"


def probe_limit_reasons(row: dict[str, object]) -> list[str]:
    reasons = []
    if "collision" in str(row.get("local_primary_class", "")) or float_or_zero(row.get("probe_collision_rate")) >= 0.95:
        reasons.append("collision_limited")
    if "identity_like" in str(row.get("probe_resolution_class", "")):
        reasons.append("identity_like_limited")
    if float_or_zero(row.get("support_floor_flag")) > 0:
        reasons.append("support_floor_limited")
    if saturation_flag(row):
        reasons.append("support_ceiling_limited")
    return reasons


def probe_limited(row: dict[str, object]) -> bool:
    return bool(probe_limit_reasons(row))


def candidate_like(row: dict[str, object]) -> bool:
    return str(row.get("local_primary_class", "")).endswith("_candidate")


def saturation_flag(row: dict[str, object]) -> bool:
    return float_or_zero(row.get("support_ceiling_flag")) > 0 or float_or_zero(row.get("reachable_signature_support_fraction")) >= 0.90


def support_regime_class(support_fraction: float) -> str:
    if support_fraction <= 0.05:
        return "support_floor_sparse"
    if support_fraction >= 0.90:
        return "support_ceiling_saturated"
    return "middle_support_regime"


def any_axis_multi_probe(rows: list[dict[str, object]]) -> bool:
    by_axis: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if row.get("probe_role") == "evidence" and candidate_like(row):
            by_axis[str(row.get("probe_axis", ""))].add(str(row.get("probe_family", "")))
    return any(len(families) >= 2 for families in by_axis.values())


def axis_recurrence_class(coordinate: bool, constraint: bool, independent: bool) -> str:
    if independent:
        return "independent_axis_recurrent_but_limited"
    if coordinate:
        return "same_axis_only_coordinate"
    if constraint:
        return "same_axis_only_constraint"
    return "no_evidence_recurrence"


def combined_row_score(row: dict[str, object]) -> float:
    js = float_or_zero(row.get("JS_to_triviality_nulls")) + float_or_zero(row.get("JS_to_support_nulls"))
    support = float_or_zero(row.get("support_symmetric_difference_fraction"))
    mass = float_or_zero(row.get("mass_concentration_top_k"))
    growth = abs(float_or_zero(row.get("support_growth_slope")))
    return 0.40 * js + 0.35 * support + 0.15 * mass + 0.10 * growth


def matched_control_class(candidate_metric: float, control_mean: float, control_count: int) -> str:
    if control_count < 2:
        return "weak_control_bundle"
    if candidate_metric > control_mean + 0.02:
        return "matched_control_supported_local_candidate"
    if abs(candidate_metric - control_mean) <= 0.02:
        return "matched_control_equivalent"
    return "matched_control_equivalent"


def candidate_rate(rows: list[dict[str, object]]) -> float:
    return sum(int(candidate_like(row)) for row in rows) / max(1, len(rows))


def group_by(rows: list[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[object, ...], list[dict[str, object]]]:
    out: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        out[tuple(row.get(key, "") for key in keys)].append(row)
    return out


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("empty\n", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_manifest(out_dir: Path) -> None:
    rows = []
    for name in REQUIRED_REPAIR_OUTPUTS:
        path = out_dir / name
        exists = True if name == "output_manifest.json" else path.exists()
        rows.append({"file": name, "exists": exists, "status": "present" if exists else "missing", "row_count": csv_row_count(path) if path.suffix == ".csv" else ""})
    (out_dir / "output_manifest.json").write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


def csv_row_count(path: Path) -> int:
    if not path.exists() or path.suffix != ".csv":
        return 0
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if not rows or rows[0] == ["empty"]:
        return 0
    return max(0, len(rows) - 1)


def float_or_zero(value: object) -> float:
    try:
        if value == "":
            return 0.0
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


if __name__ == "__main__":
    main()
