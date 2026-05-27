from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import replace
from pathlib import Path

from .relation_generator import RelationParams
from .run_deformation_detector_sweep import params_from_parameter_set_id, run_sweep_job, stable_seed


PROBE_ROLES = {
    "coordinate_tuple_k3": "evidence",
    "coordinate_tuple_k4": "evidence",
    "constraint_profile_hash": "evidence",
    "constraint_violation_count_plus_local_tuple": "evidence",
    "existing_low": "diagnostic",
    "full_state_hash": "control",
}


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
                        row["is_local_pre_control_candidate_like"] = int(candidate_like(row))
                        row["row_saturation_flag"] = int(saturation_flag(row))
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
    write_csv(out_dir / "focused_cross_probe_recurrence.csv", rows)
    write_csv(out_dir / "focused_group_recurrence_summary.csv", summary)
    write_csv(out_dir / "focused_probe_role_summary.csv", probe_summary)
    write_csv(out_dir / "focused_saturation_decomposition.csv", saturation)
    write_csv(out_dir / "focused_candidate_like_terminology_audit.csv", terminology)
    write_csv(out_dir / "focused_required_answer_provenance.csv", required)
    write_csv(out_dir / "focused_measurement_limit_flags.csv", flags)
    write_csv(out_dir / "errors.csv", errors)
    write_report(out_dir, config, started, groups, rows, summary, flags, errors)
    status = {**config, "elapsed_seconds": time.perf_counter() - started, "metric_rows_written": len(rows), "errors": len(errors), "final_outputs_written": True}
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")


def focused_group_recurrence_summary(rows: list[dict[str, object]], groups: list[dict[str, str]]) -> list[dict[str, object]]:
    source = {row.get("group_id", ""): row for row in groups}
    out = []
    for (group_id,), items in group_by(rows, ("group_id",)).items():
        evidence_families = {str(row.get("probe_family", "")) for row in items if row.get("probe_role") == "evidence"}
        evidence_candidates = {str(row.get("probe_family", "")) for row in items if row.get("probe_role") == "evidence" and candidate_like(row)}
        nonsat_evidence_candidates = {str(row.get("probe_family", "")) for row in items if row.get("probe_role") == "evidence" and candidate_like(row) and not saturation_flag(row)}
        starts = group_by(items, ("start_samples",))
        horizons = group_by(items, ("H",))
        saturation_rate = sum(int(saturation_flag(row)) for row in items) / max(1, len(items))
        probe_limited_rate = sum(int("too_coarse" in str(row.get("probe_resolution_class", "")) or "collision" in str(row.get("local_primary_class", ""))) for row in items) / max(1, len(items))
        recurrent = len(evidence_candidates) >= 2
        nonsat_recurrent = len(nonsat_evidence_candidates) >= 2
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
                "start_recurrence_score": min((candidate_rate(items) for items in starts.values()), default=0.0),
                "horizon_recurrence_score": min((candidate_rate(items) for items in horizons.values()), default=0.0),
                "probe_local_only_flag": int(len(evidence_candidates) <= 1),
                "saturation_contamination_rate": saturation_rate,
                "probe_resolution_contamination_rate": probe_limited_rate,
                "recommended_group_class": group_class(recurrent, nonsat_recurrent, saturation_rate, probe_limited_rate),
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
            "horizon": row.get("H", ""),
            "local_primary_class": row.get("local_primary_class", ""),
            "is_local_pre_control_candidate_like": int(candidate_like(row)),
            "row_saturation_flag": int(saturation_flag(row)),
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


def required_answer_provenance(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    recurrent = [row for row in summary if int(row.get("evidence_probe_recurrent_flag", 0))]
    nonsat = [row for row in summary if int(row.get("evidence_probe_recurrent_non_saturation_flag", 0))]
    return [
        {"required_answer_name": "evidence_probe_recurrent_groups", "value": bool(recurrent), "numerator": len(recurrent), "denominator": len(summary), "source_table": "focused_group_recurrence_summary.csv"},
        {"required_answer_name": "non_saturation_evidence_probe_recurrent_groups", "value": bool(nonsat), "numerator": len(nonsat), "denominator": len(summary), "source_table": "focused_group_recurrence_summary.csv"},
        {"required_answer_name": "n6_transfer_completed", "value": False, "numerator": 0, "denominator": 1, "source_table": "not_run"},
    ]


def measurement_limit_flags(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    clean = [row for row in summary if row.get("recommended_group_class") == "evidence_probe_recurrent_boundary_candidate"]
    return [
        {
            "flag": "measurement_limits_note_required",
            "value": int(not clean),
            "reason": "no clean evidence-probe recurrent boundary candidates; recurrence is probe/saturation limited" if summary else "no focused groups completed",
        }
    ]


def write_report(out_dir: Path, config: dict[str, object], started: float, groups: list[dict[str, str]], rows: list[dict[str, object]], summary: list[dict[str, object]], flags: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    recurrent = sum(int(row.get("evidence_probe_recurrent_flag", 0)) for row in summary)
    nonsat = sum(int(row.get("evidence_probe_recurrent_non_saturation_flag", 0)) for row in summary)
    clean = sum(1 for row in summary if row.get("recommended_group_class") == "evidence_probe_recurrent_boundary_candidate")
    decision = "continue_mb0_small_confirmation" if clean else "write_measurement_limits_note"
    lines = [
        "# Focused Boundary Recurrence Smoke Report",
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
        f"- Decision: {decision}",
        "",
        "## Claim Boundary",
        "",
        "This run only tests focused evidence-probe recurrence for selected boundary groups. It does not claim Omega, agency, identity, value, viability, or scientific-gate passage.",
    ]
    (out_dir / "boundary_recurrence_repair_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def group_class(recurrent: bool, nonsat_recurrent: bool, saturation_rate: float, probe_limited_rate: float) -> str:
    if recurrent and nonsat_recurrent and saturation_rate < 0.5 and probe_limited_rate < 0.5:
        return "evidence_probe_recurrent_boundary_candidate"
    if recurrent and saturation_rate >= 0.5:
        return "evidence_probe_recurrent_but_saturation_contaminated"
    if recurrent and probe_limited_rate >= 0.5:
        return "evidence_probe_recurrent_but_probe_limited"
    if recurrent:
        return "evidence_probe_recurrent_boundary_candidate"
    return "fresh_seed_recurrent_but_not_cross_probe"


def probe_role(probe_key: str, probe_family: str) -> str:
    return PROBE_ROLES.get(probe_key) or PROBE_ROLES.get(probe_family) or "unknown_diagnostic"


def candidate_like(row: dict[str, object]) -> bool:
    return str(row.get("local_primary_class", "")).endswith("_candidate")


def saturation_flag(row: dict[str, object]) -> bool:
    return float_or_zero(row.get("support_ceiling_flag")) > 0 or float_or_zero(row.get("reachable_signature_support_fraction")) >= 0.90 or "ceiling" in str(row.get("local_primary_class", ""))


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


def float_or_zero(value: object) -> float:
    try:
        if value == "":
            return 0.0
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


if __name__ == "__main__":
    main()
