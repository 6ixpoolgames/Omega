from __future__ import annotations

import argparse
import json
import signal
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from statistics import mean

from .mechanism_controls import (
    MECHANISM_CONTROL_NAMES,
    make_mechanism_control_system,
    substrate_preservation_audit,
)
from .relation_generator import generate_relation_system
from .run_deformation_detector_sweep import params_from_parameter_set_id, stable_seed
from .run_focused_boundary_recurrence import apply_variant, float_or_zero, read_csv, write_csv
from .run_frontier_transform_b0 import METRICS, WINDOWS, rows_for_starts
from .run_frontier_transform_syndrome_audit import (
    component_contexts,
    control_quality_by_name,
    read_control_rows,
    syndrome_component_scores,
)
from .run_instrumentation_phase_a import build_holdout_split
from .run_path_metric_calibration import build_probe


OUTPUTS = (
    "mechanism_control_progress_checkpoints.csv",
    "mechanism_control_system_manifest.csv",
    "mechanism_control_substrate_preservation.csv",
    "mechanism_control_syndrome_rates.csv",
    "mechanism_control_dependency_scores.csv",
    "mechanism_control_decision_summary.csv",
    "frontier_transform_syndrome_mechanism_audit_report.md",
    "mechanism_control_metric_rows.csv",
    "mechanism_control_component_scores.csv",
    "errors.csv",
    "status.json",
    "output_manifest.json",
)
ROUGHNESS_CONTROL = "roughness_resampled_transform_control"
ASYMMETRY_CONTROL = "asymmetry_flip_sweep_control"
CONSTRAINT_CONTROL = "constraint_resampled_generation_control"
BASELINE_CONTROL = "baseline_unperturbed"
DIAGNOSTIC_PROBES = {"existing_low", "full_state_hash"}
STOP_REQUESTED = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Stage B mechanism-control syndrome dependency smoke.")
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--corrected", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/corrected_group_classification.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--phase-b-dir", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_frontier_transform_phase_b_regenerated_full_controls"))
    parser.add_argument("--stage-a-dir", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_a_addendum_laptop_full_control"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260528_frontier_transform_stage_b_mechanism_smoke_30m"))
    parser.add_argument("--groups", type=int, default=1)
    parser.add_argument("--design-groups", type=int, default=1)
    parser.add_argument("--fresh-seeds-per-group", type=int, default=2)
    parser.add_argument("--start-samples-list", type=str, default="4,8")
    parser.add_argument("--probes", type=str, default="constraint_profile_hash,constraint_violation_count_plus_local_tuple,existing_low,full_state_hash")
    parser.add_argument("--roughness-strengths", type=str, default="0.01,0.02,0.05,0.10,0.20")
    parser.add_argument("--asymmetry-strengths", type=str, default="0.01,0.02,0.05,0.10,0.20")
    parser.add_argument("--constraint-strengths", type=str, default="0.01,0.05,0.20")
    parser.add_argument("--workers", type=int, default=7)
    parser.add_argument("--job-batch-size", type=int, default=2)
    parser.add_argument("--max-runtime-seconds", type=int, default=1800)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=120)
    parser.add_argument("--component-z-threshold", type=float, default=0.5)
    return parser.parse_args()


def main() -> None:
    install_signal_handlers()
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    selected_syndromes = selected_syndrome_ids(args.stage_a_dir)
    groups, split_rows = build_holdout_split(args)
    anchors = {row.get("anchor_id", ""): row for row in read_csv(args.source_run / "atlas_band_selection.csv")}
    probes = tuple(item.strip() for item in args.probes.split(",") if item.strip())
    start_samples = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    jobs = build_jobs(args, groups, split_rows, anchors, probes, start_samples)
    status: dict[str, object] = {
        "status": "RUNNING",
        "phase": "frontier_transform_stage_b_mechanism_control_smoke",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase_b_dir": str(args.phase_b_dir),
        "stage_a_dir": str(args.stage_a_dir),
        "out_dir": str(args.out),
        "selected_syndrome_ids": selected_syndromes,
        "workers": args.workers,
        "job_batch_size": args.job_batch_size,
        "jobs_requested": len(jobs),
        "jobs_submitted": 0,
        "jobs_completed": 0,
        "jobs_cancelled": 0,
        "pending_jobs_remaining": len(jobs),
        "max_runtime_seconds": args.max_runtime_seconds,
        "shutdown_cushion_seconds": args.shutdown_cushion_seconds,
        "new_systems_generated": 0,
        "mechanism_control_systems_generated": 0,
        "holdout_scoring_count": 0,
        "n6_run_count": 0,
        "alphabet_expansion_count": 0,
        "promotion_enabled": False,
        "candidate_detection_enabled": False,
        "holdout_detection_enabled": False,
    }
    metric_rows, manifest, preservation, errors, checkpoints = run_batches(args, jobs, status, started)
    preservation = add_frontier_preservation_metrics(preservation, metric_rows)
    component_scores = score_components(args, metric_rows)
    syndrome_rates = syndrome_rate_rows(component_scores, selected_syndromes)
    dependency_scores = dependency_score_rows(syndrome_rates, preservation, selected_syndromes)
    decision_summary = decision_summary_rows(dependency_scores, selected_syndromes)
    if status["status"] == "RUNNING":
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "all_jobs_completed"
    status["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    status["metric_rows"] = len(metric_rows)
    status["component_score_rows"] = len(component_scores)
    status["syndrome_rate_rows"] = len(syndrome_rates)
    status["dependency_score_rows"] = len(dependency_scores)
    status["decision_rows"] = len(decision_summary)
    status["errors"] = len(errors)
    status["mechanism_control_systems_generated"] = sum(1 for row in manifest if row.get("mechanism_control_name") != BASELINE_CONTROL)
    write_outputs(args.out, status, metric_rows, manifest, preservation, component_scores, syndrome_rates, dependency_scores, decision_summary, errors, checkpoints)


def install_signal_handlers() -> None:
    def request_stop(_signum: int, _frame: object) -> None:
        global STOP_REQUESTED
        STOP_REQUESTED = True

    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        signum = getattr(signal, name, None)
        if signum is not None:
            signal.signal(signum, request_stop)


def selected_syndrome_ids(stage_a_dir: Path) -> list[str]:
    rows = read_csv(stage_a_dir / "phase_b_syndrome_readiness.csv")
    if not rows:
        return []
    raw = rows[0].get("selected_syndrome_ids", "[]")
    try:
        values = json.loads(raw)
    except json.JSONDecodeError:
        values = []
    return [str(value) for value in values]


def build_jobs(
    args: argparse.Namespace,
    groups: list[dict[str, str]],
    split_rows: list[dict[str, object]],
    anchors: dict[str, dict[str, str]],
    probes: tuple[str, ...],
    start_samples: tuple[int, ...],
) -> list[dict[str, object]]:
    split_by_group = {str(row["group_id"]): row for row in split_rows}
    jobs: list[dict[str, object]] = []
    conditions = mechanism_conditions(args)
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
                        condition_id = f"{condition['mechanism_control_name']}:{condition['mechanism_strength_label']}"
                        jobs.append(
                            {
                                "job_id": f"stage_b_{group_index:03d}_{seed_index}_{start_count}_{probe}_{condition_id}",
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
    conditions: list[dict[str, object]] = [
        {
            "mechanism_condition": "baseline",
            "mechanism_control_name": BASELINE_CONTROL,
            "mechanism_control_strength": 0.0,
            "mechanism_strength_label": "baseline",
        }
    ]
    for control_name, raw_strengths, labels in (
        (ROUGHNESS_CONTROL, args.roughness_strengths, None),
        (ASYMMETRY_CONTROL, args.asymmetry_strengths, None),
        (CONSTRAINT_CONTROL, args.constraint_strengths, ("weak", "medium", "strong")),
    ):
        strengths = parse_strengths(raw_strengths)
        for index, strength in enumerate(strengths):
            label = labels[index] if labels and index < len(labels) else f"p{strength:.2f}"
            conditions.append(
                {
                    "mechanism_condition": "mechanism_control",
                    "mechanism_control_name": control_name,
                    "mechanism_control_strength": strength,
                    "mechanism_strength_label": label,
                }
            )
    return conditions


def parse_strengths(raw: str) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in raw.split(",") if item.strip())


def run_batches(
    args: argparse.Namespace,
    jobs: list[dict[str, object]],
    status: dict[str, object],
    started: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    batches = [jobs[index : index + max(1, args.job_batch_size)] for index in range(0, len(jobs), max(1, args.job_batch_size))]
    pending = list(batches)
    futures = {}
    metric_rows: list[dict[str, object]] = []
    manifest: list[dict[str, object]] = []
    preservation: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    checkpoints: list[dict[str, object]] = []
    last_checkpoint_jobs = 0
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
                futures[executor.submit(run_batch, batch)] = batch
                status["jobs_submitted"] = int(status["jobs_submitted"]) + len(batch)
            done, _ = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                batch = futures.pop(future)
                try:
                    rows, systems, audits, batch_errors, completed = future.result()
                    metric_rows.extend(rows)
                    manifest.extend(systems)
                    preservation.extend(audits)
                    errors.extend(batch_errors)
                    status["jobs_completed"] = int(status["jobs_completed"]) + completed
                    if int(status["jobs_completed"]) - last_checkpoint_jobs >= 60:
                        checkpoints.append(checkpoint_row(status, started, metric_rows, manifest, preservation, errors))
                        last_checkpoint_jobs = int(status["jobs_completed"])
                        write_partial_status(args.out, status, started, metric_rows, manifest, preservation, errors, checkpoints)
                except Exception as exc:  # noqa: BLE001
                    errors.append({"job_id": ",".join(str(job.get("job_id", "")) for job in batch), "error": repr(exc)})
    finally:
        if futures:
            for future in futures:
                future.cancel()
            status["jobs_cancelled"] = len(futures)
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    status["pending_jobs_remaining"] = sum(len(batch) for batch in pending)
    checkpoints.append(checkpoint_row(status, started, metric_rows, manifest, preservation, errors))
    write_partial_status(args.out, status, started, metric_rows, manifest, preservation, errors, checkpoints)
    return metric_rows, manifest, preservation, errors, checkpoints


def checkpoint_row(
    status: dict[str, object],
    started: float,
    metric_rows: list[dict[str, object]],
    manifest: list[dict[str, object]],
    preservation: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "jobs_submitted": status.get("jobs_submitted"),
        "jobs_completed": status.get("jobs_completed"),
        "metric_rows": len(metric_rows),
        "system_manifest_rows": len(manifest),
        "preservation_rows": len(preservation),
        "errors": len(errors),
        "status": status.get("status"),
    }


def write_partial_status(
    out_dir: Path,
    status: dict[str, object],
    started: float,
    metric_rows: list[dict[str, object]],
    manifest: list[dict[str, object]],
    preservation: list[dict[str, object]],
    errors: list[dict[str, object]],
    checkpoints: list[dict[str, object]],
) -> None:
    partial = dict(status)
    partial["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    partial["metric_rows_partial"] = len(metric_rows)
    partial["system_manifest_rows_partial"] = len(manifest)
    partial["preservation_rows_partial"] = len(preservation)
    partial["errors"] = len(errors)
    partial["partial_checkpoint_written_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (out_dir / "status.json").write_text(json.dumps(partial, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(out_dir / "mechanism_control_progress_checkpoints.csv", checkpoints)


def run_batch(jobs: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], int]:
    metric_rows: list[dict[str, object]] = []
    manifest: list[dict[str, object]] = []
    preservation: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    completed = 0
    for job in jobs:
        try:
            rows, system_row, audit = run_stage_b_job(job)
            metric_rows.extend(rows)
            manifest.append(system_row)
            if audit:
                preservation.append(audit)
        except Exception as exc:  # noqa: BLE001
            errors.append({"job_id": job.get("job_id", ""), "error": repr(exc)})
        completed += 1
    return metric_rows, manifest, preservation, errors, completed


def run_stage_b_job(job: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, object], dict[str, object]]:
    params = job["params"]
    seed = int(job["seed"])
    baseline = generate_relation_system(params, seed)  # type: ignore[arg-type]
    control_name = str(job["mechanism_control_name"])
    strength = float(job["mechanism_control_strength"])
    if control_name == BASELINE_CONTROL:
        system = baseline
        audit: dict[str, object] = {}
    else:
        system = make_mechanism_control_system(baseline, control_name, seed + 31_337, strength, params)  # type: ignore[arg-type]
        audit = dict(substrate_preservation_audit(baseline, system))
        audit.update(common_condition_fields(job, baseline.system_id, system.system_id))
        audit["control_too_destructive_flag"] = audit.get("control_too_destructive", 0)
    probe, alphabet_size, probe_group = build_probe(system, str(job["probe_key"]), str(job["source_probe_family"]))
    starts = [system.states[(seed + i * 17) % len(system.states)] for i in range(int(job["start_samples"]))]
    rows = rows_for_starts(job, system, probe, alphabet_size, probe_group, starts, "mechanism_control" if control_name != BASELINE_CONTROL else "baseline")
    for row in rows:
        row.update(common_condition_fields(job, baseline.system_id, system.system_id))
        row["fresh_seed_index"] = job.get("fresh_seed_index", "")
    system_row = {
        **common_condition_fields(job, baseline.system_id, system.system_id),
        "job_id": job.get("job_id", ""),
        "group_id": job.get("group_id", ""),
        "seed": seed,
        "fresh_seed_index": job.get("fresh_seed_index", ""),
        "start_samples": job.get("start_samples", ""),
        "probe_key": job.get("probe_key", ""),
        "mechanism_control_status": system.metadata.get("mechanism_control_status", "baseline"),
        "mechanism_control_unavailable_reason": system.metadata.get("mechanism_control_unavailable_reason", ""),
        "state_count": len(system.states),
        "edge_count": sum(len(targets) for targets in system.edges.values()),
        "constraint_control_type": system.metadata.get("constraint_control_type", ""),
        "constraint_metadata_available": system.metadata.get("constraint_metadata_available", ""),
    }
    return rows, system_row, audit


def common_condition_fields(job: dict[str, object], baseline_system_id: str, control_system_id: str) -> dict[str, object]:
    return {
        "condition_id": job.get("condition_id", ""),
        "mechanism_condition": job.get("mechanism_condition", ""),
        "mechanism_control_name": job.get("mechanism_control_name", ""),
        "mechanism_control_strength": job.get("mechanism_control_strength", ""),
        "mechanism_strength_label": job.get("mechanism_strength_label", ""),
        "baseline_system_id": baseline_system_id,
        "control_system_id": control_system_id,
    }


def score_components(args: argparse.Namespace, metric_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    control_source_name, control_rows = read_control_rows(args.phase_b_dir)
    quality_rows = read_csv(args.phase_b_dir / "phase_b_control_quality_audit.csv")
    control_quality = control_quality_by_name(control_rows, quality_rows)
    scored = syndrome_component_scores(metric_rows, control_rows, control_quality, args.component_z_threshold)
    for row in scored:
        row["stage_b_control_source"] = control_source_name
    return scored


def syndrome_rate_rows(component_scores: list[dict[str, object]], selected_syndromes: list[str]) -> list[dict[str, object]]:
    selected = set(selected_syndromes)
    out = []
    keys = ("condition_id", "mechanism_condition", "mechanism_control_name", "mechanism_control_strength", "mechanism_strength_label")
    for key, items in group_by_objects(component_scores, keys).items():
        for context in component_contexts(items):
            if selected and context["syndrome_id"] not in selected:
                continue
            component_rates = context["component_marginal_rates"]
            out.append(
                {
                    **{field: value for field, value in zip(keys, key)},
                    "syndrome_id": context["syndrome_id"],
                    "probe_key": context["probe_key"],
                    "flow_mode": context["flow_mode"],
                    "syndrome_rate": context["observed_joint_rate"],
                    "complete_unit_count": context["complete_unit_count"],
                    "component_marginal_rates_json": json.dumps(component_rates, sort_keys=True),
                }
            )
    return out


def dependency_score_rows(
    syndrome_rates: list[dict[str, object]],
    preservation: list[dict[str, object]],
    selected_syndromes: list[str],
) -> list[dict[str, object]]:
    out = []
    baseline_rates = {
        str(syndrome_id): mean(float_or_zero(item.get("syndrome_rate")) for item in items)
        for (syndrome_id,), items in group_by_objects(
            [row for row in syndrome_rates if row.get("mechanism_control_name") == BASELINE_CONTROL],
            ("syndrome_id",),
        ).items()
    }
    preservation_by_condition = group_by_objects(preservation, ("condition_id",))
    selected = selected_syndromes or sorted(baseline_rates)
    for syndrome_id in selected:
        baseline = baseline_rates.get(syndrome_id, 0.0)
        controls = [row for row in syndrome_rates if row.get("syndrome_id") == syndrome_id and row.get("mechanism_control_name") != BASELINE_CONTROL]
        for (control_name, strength, label), items in group_by_objects(controls, ("mechanism_control_name", "mechanism_control_strength", "mechanism_strength_label")).items():
            rate = mean(float_or_zero(item.get("syndrome_rate")) for item in items) if items else 0.0
            drop = baseline - rate
            dependency = drop / baseline if baseline > 1e-12 else 0.0
            audits = preservation_by_condition.get((f"{control_name}:{label}",), [])
            destructive = mean(float_or_zero(row.get("control_destructiveness_score")) for row in audits) if audits else 0.0
            too_destructive = int(any(int(float_or_zero(row.get("control_too_destructive_flag"))) for row in audits))
            out.append(
                {
                    "syndrome_id": syndrome_id,
                    "mechanism_control_name": control_name,
                    "mechanism_control_strength": strength,
                    "mechanism_strength_label": label,
                    "baseline_syndrome_rate": baseline,
                    "mechanism_control_syndrome_rate": rate,
                    "syndrome_rate_delta": drop,
                    "mechanism_dependency_score": max(0.0, dependency),
                    "generic_phase_score": rate / baseline if baseline > 1e-12 else 0.0,
                    "roughness_robustness_score": rate / baseline if control_name == ROUGHNESS_CONTROL and baseline > 1e-12 else "",
                    "roughness_brittleness_score": max(0.0, dependency) if control_name == ROUGHNESS_CONTROL else "",
                    "control_destructiveness_score": destructive,
                    "control_too_destructive_flag": too_destructive,
                    "decision_class": dependency_decision(control_name, baseline, rate, dependency, too_destructive, label),
                    "rate_context_count": len(items),
                }
            )
    return out


def decision_summary_rows(dependency_scores: list[dict[str, object]], selected_syndromes: list[str]) -> list[dict[str, object]]:
    out = []
    selected = selected_syndromes or sorted({str(row.get("syndrome_id")) for row in dependency_scores})
    for syndrome_id in selected:
        items = [row for row in dependency_scores if row.get("syndrome_id") == syndrome_id]
        if not items:
            out.append({"syndrome_id": syndrome_id, "decision_class": "no_measurable_syndrome", "stage_b_interpretation": "no scored mechanism contexts"})
            continue
        baseline = max(float_or_zero(row.get("baseline_syndrome_rate")) for row in items)
        if baseline <= 1e-12:
            decision = "no_measurable_syndrome"
        elif any(row.get("decision_class") == "control_too_destructive_underdetermined" for row in items):
            decision = "control_too_destructive_underdetermined"
        elif any(row.get("decision_class") == "roughness_brittle_syndrome" for row in items):
            decision = "roughness_brittle_syndrome"
        elif any(row.get("decision_class") == "mechanism_dependent_syndrome" for row in items):
            decision = "mechanism_dependent_syndrome"
        elif all(float_or_zero(row.get("generic_phase_score")) >= 0.75 for row in items):
            decision = "mechanism_independent_generic_phase_syndrome"
        else:
            decision = "control_equivalent_syndrome"
        out.append(
            {
                "syndrome_id": syndrome_id,
                "decision_class": decision,
                "baseline_syndrome_rate": baseline,
                "max_mechanism_dependency_score": max(float_or_zero(row.get("mechanism_dependency_score")) for row in items),
                "min_generic_phase_score": min(float_or_zero(row.get("generic_phase_score")) for row in items),
                "max_control_destructiveness_score": max(float_or_zero(row.get("control_destructiveness_score")) for row in items),
                "stage_b_interpretation": interpretation_for_decision(decision),
                "holdout_scoring_count": 0,
            }
        )
    return out


def dependency_decision(control_name: object, baseline: float, rate: float, dependency: float, too_destructive: int, label: object) -> str:
    if baseline <= 1e-12:
        return "no_measurable_syndrome"
    if too_destructive:
        return "control_too_destructive_underdetermined"
    if control_name == ROUGHNESS_CONTROL and str(label) == "p0.01" and rate <= 0.25 * baseline:
        return "roughness_brittle_syndrome"
    if control_name in {ASYMMETRY_CONTROL, CONSTRAINT_CONTROL} and dependency >= 0.50:
        return "mechanism_dependent_syndrome"
    if rate >= 0.75 * baseline:
        return "mechanism_independent_generic_phase_syndrome"
    return "control_equivalent_syndrome"


def interpretation_for_decision(decision: str) -> str:
    return {
        "mechanism_dependent_syndrome": "syndrome degrades under constraint/asymmetry mechanism controls; dependency profile, not falsification",
        "mechanism_independent_generic_phase_syndrome": "syndrome persists under mechanism controls; likely generic phase behavior",
        "roughness_brittle_syndrome": "tiny roughness perturbation strongly degrades the syndrome",
        "control_equivalent_syndrome": "mechanism-control effect is mixed or weak at this smoke scale",
        "control_too_destructive_underdetermined": "one or more mechanism controls altered substrate too strongly for negative interpretation",
        "no_measurable_syndrome": "baseline syndrome rate was zero in this Stage B smoke",
    }.get(decision, "")


def add_frontier_preservation_metrics(preservation: list[dict[str, object]], metric_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    baseline = {
        baseline_key(row): row
        for row in metric_rows
        if row.get("mechanism_control_name") == BASELINE_CONTROL
    }
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
        audit["control_destructiveness_score"] = max(float_or_zero(audit.get("control_destructiveness_score")), min(1.0, audit["frontier_size_profile_delta"]))
        audit["control_too_destructive_flag"] = int(float_or_zero(audit.get("control_destructiveness_score")) > 0.50)
    return preservation


def baseline_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        row.get("group_id"),
        row.get("seed"),
        row.get("probe_key"),
        row.get("start_samples"),
        row.get("start_index"),
        row.get("flow_mode"),
        row.get("window"),
    )


def saturation_timing_delta(rows: list[dict[str, object]], baseline: dict[tuple[object, ...], dict[str, object]]) -> float:
    deltas = []
    keys = ("group_id", "seed", "probe_key", "start_samples", "start_index", "flow_mode")
    for key, items in group_by_objects(rows, keys).items():
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


def group_by_objects(rows: list[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[object, ...], list[dict[str, object]]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        key = tuple(row.get(field, "") for field in keys)
        grouped.setdefault(key, []).append(row)
    return grouped


def write_outputs(
    out_dir: Path,
    status: dict[str, object],
    metric_rows: list[dict[str, object]],
    manifest: list[dict[str, object]],
    preservation: list[dict[str, object]],
    component_scores: list[dict[str, object]],
    syndrome_rates: list[dict[str, object]],
    dependency_scores: list[dict[str, object]],
    decision_summary: list[dict[str, object]],
    errors: list[dict[str, object]],
    checkpoints: list[dict[str, object]],
) -> None:
    write_csv(out_dir / "mechanism_control_progress_checkpoints.csv", checkpoints)
    write_csv(out_dir / "mechanism_control_system_manifest.csv", manifest)
    write_csv(out_dir / "mechanism_control_substrate_preservation.csv", preservation)
    write_csv(out_dir / "mechanism_control_syndrome_rates.csv", syndrome_rates)
    write_csv(out_dir / "mechanism_control_dependency_scores.csv", dependency_scores)
    write_csv(out_dir / "mechanism_control_decision_summary.csv", decision_summary)
    write_csv(out_dir / "mechanism_control_metric_rows.csv", metric_rows)
    write_csv(out_dir / "mechanism_control_component_scores.csv", component_scores)
    write_csv(out_dir / "errors.csv", errors)
    write_report(out_dir, status, decision_summary, preservation)
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    write_manifest(out_dir)


def write_report(out_dir: Path, status: dict[str, object], decision_summary: list[dict[str, object]], preservation: list[dict[str, object]]) -> None:
    lines = [
        "# Frontier-Transform Syndrome Mechanism Audit: Stage B Smoke",
        "",
        "## Claim Boundary",
        "",
        "Mechanism-control dependency smoke only. No holdout scoring, no n=6, no alphabet expansion, no candidate promotion.",
        "",
        "## Run Shape",
        "",
        f"Jobs completed: `{status.get('jobs_completed', 0)}/{status.get('jobs_requested', 0)}`",
        f"Metric rows: `{status.get('metric_rows', 0)}`",
        f"Errors: `{status.get('errors', 0)}`",
        "",
        "## Decision Summary",
        "",
        "| syndrome_id | decision_class | baseline_rate | max_dependency | max_destructiveness |",
        "|---|---|---:|---:|---:|",
    ]
    for row in decision_summary:
        lines.append(
            f"| {row.get('syndrome_id', '')} | {row.get('decision_class', '')} | {float_or_zero(row.get('baseline_syndrome_rate')):.6f} | {float_or_zero(row.get('max_mechanism_dependency_score')):.3f} | {float_or_zero(row.get('max_control_destructiveness_score')):.3f} |"
        )
    too_destructive = sum(int(float_or_zero(row.get("control_too_destructive_flag"))) for row in preservation)
    lines.extend([
        "",
        "## Substrate Preservation",
        "",
        f"Control systems flagged too destructive: `{too_destructive}`",
        "",
        "Mechanism controls are interpreted as dependency profiles, not survival gates.",
        "",
        "## Output Manifest",
        "",
        "See `output_manifest.json`.",
        "",
    ])
    (out_dir / "frontier_transform_syndrome_mechanism_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest(out_dir: Path) -> None:
    rows = []
    for name in OUTPUTS:
        path = out_dir / name
        exists = path.exists() or name == "output_manifest.json"
        rows.append({"file": name, "exists": exists, "status": "present" if exists else "missing"})
    (out_dir / "output_manifest.json").write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
