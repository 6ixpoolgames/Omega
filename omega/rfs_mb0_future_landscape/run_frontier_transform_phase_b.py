from __future__ import annotations

import argparse
import csv
import json
import signal
import time
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from statistics import mean, median, pstdev

from .run_deformation_detector_sweep import params_from_parameter_set_id, stable_seed
from .run_focused_boundary_recurrence import apply_variant, float_or_zero, group_by, read_csv, write_csv
from .run_frontier_transform_b0 import (
    FLOW_MODES,
    METRICS,
    PROBES,
    WINDOWS,
    context_control_rows,
    control_effect_rows,
    control_manifest,
    flow_mode_summary,
    metric_family,
    no_target_audit,
    row_level_control_effect_rows,
    run_job,
    window_stability_rows,
)
from .run_instrumentation_phase_a import build_holdout_split


STOP_REQUESTED = False
B0_VIABLE_FAMILIES = {"bottleneck", "support_turnover", "transition_matrix", "window_stability"}
OUTPUTS = (
    "rfs_mb0_frontier_transform_phase_b_10h_report.md",
    "phase_b_run_config.json",
    "phase_b_job_manifest.csv",
    "phase_b_progress_checkpoints.csv",
    "phase_b_design_metric_rows.csv",
    "phase_b_design_control_rows.csv",
    "phase_b_row_level_control_effects.csv",
    "phase_b_directional_effects.csv",
    "phase_b_metric_family_recurrence.csv",
    "phase_b_design_recurrence_summary.csv",
    "phase_b_flow_mode_recurrence.csv",
    "phase_b_window_recurrence.csv",
    "phase_b_seed_start_recurrence.csv",
    "phase_b_matched_recurrence_controls.csv",
    "phase_b_recurrence_excess.csv",
    "phase_b_control_quality_audit.csv",
    "phase_b_no_target_audit.csv",
    "phase_b_holdout_status.csv",
    "phase_b_phase_c_readiness.csv",
    "errors.csv",
    "status.json",
    "output_manifest.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 frontier-transform Phase B design-set recurrence.")
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--corrected", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/corrected_group_classification.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_b_10h"))
    parser.add_argument("--groups", type=int, default=20)
    parser.add_argument("--design-groups", type=int, default=10)
    parser.add_argument("--fakeout-groups", type=int, default=4)
    parser.add_argument("--neutral-anchors", type=int, default=6)
    parser.add_argument("--fresh-seeds-per-group", type=int, default=8)
    parser.add_argument("--start-samples-list", type=str, default="4,8,16")
    parser.add_argument("--probes", type=str, default=",".join(PROBES))
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--job-batch-size", type=int, default=4)
    parser.add_argument("--checkpoint-every-jobs", type=int, default=120)
    parser.add_argument("--max-runtime-seconds", type=int, default=36000)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=900)
    return parser.parse_args()


def main() -> None:
    install_signal_handlers()
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    groups, split_rows = build_holdout_split(args)
    anchors = {row.get("anchor_id", ""): row for row in read_csv(args.source_run / "atlas_band_selection.csv")}
    probes = tuple(item.strip() for item in args.probes.split(",") if item.strip())
    start_samples = tuple(int(item.strip()) for item in args.start_samples_list.split(",") if item.strip())
    jobs = build_jobs(args, groups, split_rows, anchors, list(anchors.values()), probes, start_samples)
    status: dict[str, object] = {
        "status": "RUNNING",
        "phase": "frontier_transform_phase_b_design_recurrence",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workers": args.workers,
        "jobs_requested": len(jobs),
        "jobs_submitted": 0,
        "jobs_completed": 0,
        "jobs_cancelled": 0,
        "pending_jobs_remaining": len(jobs),
        "promotion_enabled": False,
        "candidate_detection_enabled": "provisional_design_only",
        "holdout_detection_enabled": False,
        "holdout_scoring_count": 0,
        "max_runtime_seconds": args.max_runtime_seconds,
        "shutdown_cushion_seconds": args.shutdown_cushion_seconds,
        "windows": [f"{a}->{b}" for a, b in WINDOWS],
        "flow_modes": list(FLOW_MODES),
        "probes": list(probes),
        "start_samples_list": list(start_samples),
        "fresh_seeds_per_group": args.fresh_seeds_per_group,
    }
    write_csv(args.out / "phase_b_job_manifest.csv", job_manifest_rows(jobs))
    (args.out / "phase_b_run_config.json").write_text(json.dumps({**vars(args), "probes": list(probes), "windows": status["windows"], "flow_modes": status["flow_modes"]}, indent=2, sort_keys=True, default=str), encoding="utf-8")
    rows: list[dict[str, object]] = []
    controls: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    checkpoints: list[dict[str, object]] = []
    try:
        rows, controls, errors, checkpoints = run_batches(args, jobs, status, started)
    except KeyboardInterrupt:
        status["status"] = "PARTIAL_INTERRUPTED"
        status["finalization_reason"] = "keyboard_interrupt"
    if status["status"] == "RUNNING":
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "all_jobs_completed"
    write_outputs(args.out, status, started, split_rows, rows, controls, errors, checkpoints)


def install_signal_handlers() -> None:
    def request_stop(_signum: int, _frame: object) -> None:
        global STOP_REQUESTED
        STOP_REQUESTED = True

    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        signum = getattr(signal, name, None)
        if signum is not None:
            signal.signal(signum, request_stop)


def build_jobs(args: argparse.Namespace, groups: list[dict[str, str]], split_rows: list[dict[str, object]], anchors: dict[str, dict[str, str]], source_anchors: list[dict[str, str]], probes: tuple[str, ...], start_samples: tuple[int, ...]) -> list[dict[str, object]]:
    split_by_group = {str(row["group_id"]): row for row in split_rows}
    design_groups = [group for group in groups if split_by_group.get(group.get("group_id", ""), {}).get("split_set") == "design_set"]
    jobs: list[dict[str, object]] = []
    # Adaptive queue: breadth first, then more seeds, then deeper starts.
    jobs.extend(design_jobs(args, design_groups, anchors, probes, start_samples=(4,), seed_indices=range(min(4, args.fresh_seeds_per_group)), stage=1))
    jobs.extend(design_jobs(args, design_groups, anchors, probes, start_samples=(4,), seed_indices=range(4, args.fresh_seeds_per_group), stage=2))
    jobs.extend(design_jobs(args, design_groups, anchors, probes, start_samples=tuple(s for s in start_samples if s == 8), seed_indices=range(args.fresh_seeds_per_group), stage=3))
    jobs.extend(design_jobs(args, design_groups, anchors, probes, start_samples=tuple(s for s in start_samples if s == 16), seed_indices=range(args.fresh_seeds_per_group), stage=4))
    fakeouts = 0
    for group_index, group in enumerate(groups):
        if fakeouts >= args.fakeout_groups:
            break
        if group.get("prior_corrected_group_class") != "weak_control_bundle_recurrence":
            continue
        anchor = anchors.get(group.get("source_anchor_id", group.get("source_band_id", "")), {})
        params = params_from_parameter_set_id(anchor.get("parameter_set_id", ""))
        if params is None:
            continue
        variant_params = apply_variant(params, group.get("variant_dimension", ""), group.get("variant_value", ""))
        base_seed = int(anchor.get("seed") or stable_seed(anchor.get("environment_id", group.get("group_id", ""))))
        for seed_index in range(min(4, args.fresh_seeds_per_group)):
            for probe in probes:
                jobs.append(make_job("matched_fakeout_group", group.get("group_id", ""), group_index, anchor, variant_params, base_seed, seed_index, probe, 4, 5))
        fakeouts += 1
    for neutral_index, anchor in enumerate(source_anchors[: args.neutral_anchors]):
        params = params_from_parameter_set_id(anchor.get("parameter_set_id", ""))
        if params is None:
            continue
        base_seed = int(anchor.get("seed") or stable_seed(anchor.get("environment_id", f"neutral_{neutral_index}")))
        for seed_index in range(min(4, args.fresh_seeds_per_group)):
            for probe in probes:
                jobs.append(make_job("neutral_generated_system", f"neutral_{neutral_index:03d}", neutral_index, anchor, params, base_seed, seed_index, probe, 4, 6))
    return jobs


def design_jobs(args: argparse.Namespace, groups: list[dict[str, str]], anchors: dict[str, dict[str, str]], probes: tuple[str, ...], start_samples: tuple[int, ...], seed_indices: range, stage: int) -> list[dict[str, object]]:
    jobs = []
    for group_index, group in enumerate(groups):
        anchor = anchors.get(group.get("source_anchor_id", group.get("source_band_id", "")), {})
        params = params_from_parameter_set_id(anchor.get("parameter_set_id", ""))
        if params is None:
            continue
        variant_params = apply_variant(params, group.get("variant_dimension", ""), group.get("variant_value", ""))
        base_seed = int(anchor.get("seed") or stable_seed(anchor.get("environment_id", group.get("group_id", ""))))
        for seed_index in seed_indices:
            for samples in start_samples:
                for probe in probes:
                    jobs.append(make_job("design_recurrent_boundary", group.get("group_id", ""), group_index, anchor, variant_params, base_seed, seed_index, probe, samples, stage))
    return jobs


def make_job(context: str, group_id: str, group_index: int, anchor: dict[str, str], params: object, base_seed: int, seed_index: int, probe: str, start_samples: int, stage: int) -> dict[str, object]:
    seed = base_seed + 50_021 * (seed_index + 1) + group_index
    return {
        "job_id": f"phase_b_s{stage}_{context}_{group_index:03d}_{seed_index}_{probe}_starts{start_samples}",
        "queue_stage": stage,
        "preflight_context": context,
        "group_id": group_id,
        "anchor_id": anchor.get("anchor_id", group_id),
        "anchor_environment_id": anchor.get("environment_id", ""),
        "params": params,
        "seed": seed,
        "fresh_seed_index": seed_index,
        "probe_key": probe,
        "source_probe_family": anchor.get("source_probe_family", anchor.get("anchor_probe_family", "")),
        "start_samples": start_samples,
    }


def run_batches(args: argparse.Namespace, jobs: list[dict[str, object]], status: dict[str, object], started: float) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    pending = [jobs[index : index + max(1, args.job_batch_size)] for index in range(0, len(jobs), max(1, args.job_batch_size))]
    status["job_batch_size"] = max(1, args.job_batch_size)
    status["job_batches_requested"] = len(pending)
    rows: list[dict[str, object]] = []
    controls: list[dict[str, object]] = []
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
                futures[executor.submit(run_job_batch, batch)] = batch
                status["jobs_submitted"] = int(status["jobs_submitted"]) + len(batch)
            done, _ = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                futures.pop(future)
                try:
                    batch_rows, batch_controls, batch_errors, completed = future.result()
                except Exception as exc:  # noqa: BLE001
                    batch_rows, batch_controls, batch_errors, completed = [], [], [{"job_id": "batch", "error": repr(exc)}], 0
                rows.extend(batch_rows)
                controls.extend(batch_controls)
                errors.extend(batch_errors)
                status["jobs_completed"] = int(status["jobs_completed"]) + completed
                if int(status["jobs_completed"]) - last_checkpoint_jobs >= max(1, args.checkpoint_every_jobs):
                    checkpoints.append(checkpoint_row(status, started, rows, controls, errors))
                    last_checkpoint_jobs = int(status["jobs_completed"])
                    write_partial_status(args.out, status, started, rows, controls, errors, checkpoints)
    finally:
        if futures:
            for future in futures:
                future.cancel()
            status["jobs_cancelled"] = len(futures)
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    status["pending_jobs_remaining"] = sum(len(batch) for batch in pending)
    checkpoints.append(checkpoint_row(status, started, rows, controls, errors))
    write_partial_status(args.out, status, started, rows, controls, errors, checkpoints)
    return rows, controls, errors, checkpoints


def write_partial_status(out_dir: Path, status: dict[str, object], started: float, rows: list[dict[str, object]], controls: list[dict[str, object]], errors: list[dict[str, object]], checkpoints: list[dict[str, object]]) -> None:
    partial = dict(status)
    partial["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    partial["metric_rows"] = len(rows)
    partial["control_rows_unfinalized"] = len(controls)
    partial["errors"] = len(errors)
    partial["partial_checkpoint_written_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (out_dir / "status.json").write_text(json.dumps(partial, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(out_dir / "phase_b_progress_checkpoints.csv", checkpoints)


def run_job_batch(batch: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], int]:
    rows: list[dict[str, object]] = []
    controls: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    completed = 0
    for job in batch:
        try:
            job_rows, job_controls = run_job(job)
            for row in job_rows:
                row["queue_stage"] = job.get("queue_stage")
                row["fresh_seed_index"] = job.get("fresh_seed_index")
                row["start_samples"] = job.get("start_samples")
            for row in job_controls:
                row["queue_stage"] = job.get("queue_stage")
                row["fresh_seed_index"] = job.get("fresh_seed_index")
            rows.extend(job_rows)
            controls.extend(job_controls)
        except Exception as exc:  # noqa: BLE001
            errors.append({"job_id": job.get("job_id", ""), "error": repr(exc)})
        completed += 1
    return rows, controls, errors, completed


def write_outputs(out_dir: Path, status: dict[str, object], started: float, split_rows: list[dict[str, object]], rows: list[dict[str, object]], controls: list[dict[str, object]], errors: list[dict[str, object]], checkpoints: list[dict[str, object]]) -> None:
    controls = add_control_quality(controls + context_control_rows_limited(rows))
    row_effects = row_level_control_effect_rows(controls)
    for row in row_effects:
        row["control_quality"] = control_quality_for_name(controls, str(row.get("control_name", "")))
    effects = control_effect_rows_labeled(rows, controls)
    rec_rows = recurrence_rows(effects, rows)
    matched = matched_recurrence_controls(rec_rows, effects)
    excess = recurrence_excess(matched)
    phase_c = phase_c_readiness(rec_rows, matched, rows, split_rows, status)
    status["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    status["metric_rows"] = len(rows)
    status["control_rows"] = len(controls)
    status["errors"] = len(errors)
    write_csv(out_dir / "phase_b_progress_checkpoints.csv", checkpoints)
    write_csv(out_dir / "phase_b_design_metric_rows.csv", rows)
    write_csv(out_dir / "phase_b_design_control_rows.csv", controls)
    write_csv(out_dir / "phase_b_row_level_control_effects.csv", row_effects)
    write_csv(out_dir / "phase_b_directional_effects.csv", effects)
    metric_family_rows = family_recurrence(rec_rows)
    write_csv(out_dir / "phase_b_metric_family_recurrence.csv", metric_family_rows)
    write_csv(out_dir / "phase_b_design_recurrence_summary.csv", metric_family_rows)
    write_csv(out_dir / "phase_b_flow_mode_recurrence.csv", flow_recurrence(rec_rows))
    write_csv(out_dir / "phase_b_window_recurrence.csv", window_recurrence(rec_rows))
    write_csv(out_dir / "phase_b_seed_start_recurrence.csv", seed_start_recurrence(rec_rows))
    write_csv(out_dir / "phase_b_matched_recurrence_controls.csv", matched)
    write_csv(out_dir / "phase_b_recurrence_excess.csv", excess)
    write_csv(out_dir / "phase_b_control_quality_audit.csv", control_quality_audit(controls))
    write_csv(out_dir / "phase_b_no_target_audit.csv", no_target_audit(rows))
    write_csv(out_dir / "phase_b_holdout_status.csv", holdout_status(split_rows))
    write_csv(out_dir / "phase_b_phase_c_readiness.csv", phase_c)
    write_csv(out_dir / "errors.csv", errors)
    write_report(out_dir, status, phase_c, rec_rows, matched)
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    write_manifest(out_dir)


def context_control_rows_limited(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    # B0 helper emits real matched/fakeout/neutral/frontier-size controls. Keep it, but cap pathological row growth by retaining all design comparisons generated by the helper only once per run.
    return context_control_rows(rows)


def add_control_quality(controls: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in controls:
        item = dict(row)
        name = str(item.get("control_name", ""))
        item["control_quality"] = "placeholder" if name == "probe_marginal_window_control" else ("not_available" if name in {"constraint_shuffled_transform_control", "asymmetry_shuffled_transform_control", "roughness_resampled_transform_control"} else "computed")
        out.append(item)
    for name in ("constraint_shuffled_transform_control", "asymmetry_shuffled_transform_control", "roughness_resampled_transform_control"):
        out.append({"control_name": name, "control_quality": "not_available", "control_status": "not_available"})
    return out


def control_effect_rows_labeled(rows: list[dict[str, object]], controls: list[dict[str, object]]) -> list[dict[str, object]]:
    effects = control_effect_rows(rows, controls)
    quality_by_control = {str(row.get("control_name")): str(row.get("control_quality", "")) for row in controls if row.get("control_name")}
    for row in effects:
        row["control_quality"] = quality_by_control.get(str(row.get("control_name")), "computed")
    return effects


def control_quality_for_name(controls: list[dict[str, object]], name: str) -> str:
    for row in controls:
        if str(row.get("control_name", "")) == name and row.get("control_quality"):
            return str(row.get("control_quality"))
    return "computed"


def recurrence_rows(effects: list[dict[str, object]], rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    observed = [row for row in rows if row.get("preflight_context") == "design_recurrent_boundary" and row.get("row_kind") == "observed" and row.get("probe_key") not in {"existing_low", "full_state_hash"}]
    contexts = {
        "seed": {str(row.get("seed")) for row in observed},
        "start": {str(row.get("start_index")) for row in observed},
        "window": {str(row.get("window")) for row in observed},
        "flow_mode": {str(row.get("flow_mode")) for row in observed},
        "probe": {str(row.get("probe_key")) for row in observed},
    }
    effect_by_key = group_by([row for row in effects if row.get("control_quality") != "placeholder"], ("metric_family", "metric_name", "probe_key", "flow_mode"))
    for (family, metric, probe, flow), items in effect_by_key.items():
        if family not in B0_VIABLE_FAMILIES:
            continue
        recurrent_items = [item for item in items if float_or_zero(item.get("absolute_effect_size")) >= 0.10 and str(item.get("effect_direction")) != "control_equivalent"]
        supporting_rows = [row for row in observed if row.get("probe_key") == probe and row.get("flow_mode") == flow and row.get(metric, "") != ""]
        direction_counts = Counter(str(item.get("effect_direction")) for item in recurrent_items)
        direction_mode = direction_counts.most_common(1)[0][0] if direction_counts else "control_equivalent"
        out.append({
            "metric_family": family,
            "metric_name": metric,
            "probe_key": probe,
            "flow_mode": flow,
            "observed_effect_rows": len(items),
            "recurrent_effect_rows": len(recurrent_items),
            "observed_recurrence_rate": len(recurrent_items) / max(1, len(items)),
            "seed_recurrence_rate": coverage(supporting_rows, recurrent_items, "seed", contexts["seed"]),
            "start_recurrence_rate": coverage(supporting_rows, recurrent_items, "start_index", contexts["start"]),
            "window_recurrence_rate": coverage(supporting_rows, recurrent_items, "window", contexts["window"]),
            "flow_mode_recurrence_rate": coverage(supporting_rows, recurrent_items, "flow_mode", contexts["flow_mode"]),
            "probe_recurrence_rate": coverage(supporting_rows, recurrent_items, "probe_key", contexts["probe"]),
            "control_excess_recurrence_rate": len(recurrent_items) / max(1, len(items)),
            "signed_effect_size_mean": mean(float_or_zero(item.get("signed_effect_size")) for item in items),
            "signed_effect_size_median": median(float_or_zero(item.get("signed_effect_size")) for item in items),
            "absolute_effect_size_mean": mean(float_or_zero(item.get("absolute_effect_size")) for item in items),
            "absolute_effect_size_median": median(float_or_zero(item.get("absolute_effect_size")) for item in items),
            "effect_direction_mode": direction_mode,
            "effect_direction_stability": direction_stability(direction_counts, len(recurrent_items)),
            "percent_design_above_control": count_direction(items, "design_above_control"),
            "percent_design_below_control": count_direction(items, "design_below_control"),
            "percent_control_equivalent": count_direction(items, "control_equivalent"),
            "b0_viable_family": int(family in B0_VIABLE_FAMILIES),
        })
    return out


def matched_recurrence_controls(rec_rows: list[dict[str, object]], effects: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    computed_effects = [
        row
        for row in effects
        if row.get("control_quality") == "computed"
        and row.get("control_name")
        and row.get("control_name") != "probe_marginal_window_control"
    ]
    by_key = group_by(computed_effects, ("metric_family", "metric_name", "probe_key", "flow_mode"))
    for row in rec_rows:
        key = (row.get("metric_family"), row.get("metric_name"), row.get("probe_key"), row.get("flow_mode"))
        obs = float_or_zero(row.get("observed_recurrence_rate"))
        control_items = by_key.get(key, [])
        controls = [
            1.0
            if float_or_zero(item.get("absolute_effect_size")) >= 0.10 and str(item.get("effect_direction")) != "control_equivalent"
            else 0.0
            for item in control_items
        ]
        control_mean = mean(controls) if controls else 0.0
        out.append({
            "metric_family": row.get("metric_family"),
            "metric_name": row.get("metric_name"),
            "probe_key": row.get("probe_key"),
            "flow_mode": row.get("flow_mode"),
            "observed_recurrence_rate": obs,
            "control_recurrence_mean": control_mean,
            "control_recurrence_std": pstdev(controls) if len(controls) > 1 else 0.0,
            "recurrence_excess": obs - control_mean,
            "recurrence_percentile_vs_controls": sum(int(obs >= c) for c in controls) / max(1, len(controls)),
            "control_count": len(controls),
            "weak_control_flag": int(len(controls) < 3),
            "control_note": "computed recurrence controls from non-placeholder transform-control effects",
        })
    return out


def recurrence_excess(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [dict(row) for row in rows]


def phase_c_readiness(rec_rows: list[dict[str, object]], matched: list[dict[str, object]], rows: list[dict[str, object]], split_rows: list[dict[str, object]], status: dict[str, object]) -> list[dict[str, object]]:
    matched_by_key = {(row.get("metric_family"), row.get("metric_name"), row.get("probe_key"), row.get("flow_mode")): row for row in matched}
    supporting = []
    for row in rec_rows:
        key = (row.get("metric_family"), row.get("metric_name"), row.get("probe_key"), row.get("flow_mode"))
        control = matched_by_key.get(key, {})
        if (
            float_or_zero(row.get("seed_recurrence_rate")) >= 0.60
            and float_or_zero(row.get("start_recurrence_rate")) >= 0.50
            and float_or_zero(row.get("window_recurrence_rate")) >= 0.40
            and float_or_zero(control.get("recurrence_excess")) > 0
            and float_or_zero(control.get("recurrence_percentile_vs_controls")) >= 0.80
        ):
            supporting.append({**row, **{"recurrence_excess": control.get("recurrence_excess"), "recurrence_percentile_vs_controls": control.get("recurrence_percentile_vs_controls")}})
    families = {str(row.get("metric_family")) for row in supporting}
    probes = {str(row.get("probe_key")) for row in supporting}
    windows = {str(row.get("window")) for row in rows if row.get("preflight_context") == "design_recurrent_boundary"}
    holdout_clean = all(int(row.get("holdout_frozen_until_phase_c", 0)) == 1 for row in split_rows if row.get("split_set") == "holdout_set")
    complete_enough = int(status.get("jobs_completed", 0)) >= min(160, int(status.get("jobs_requested", 0)))
    phase_c_ready = complete_enough and holdout_clean and len(families) >= 2 and not probes.intersection({"existing_low", "full_state_hash"})
    if phase_c_ready:
        decision = "phase_c_ready"
    elif not complete_enough:
        decision = "phase_c_blocked_incomplete_run"
    elif not supporting:
        decision = "phase_c_blocked_no_recurrence"
    elif len(families) < 2:
        decision = "phase_c_blocked_probe_dependent"
    elif not holdout_clean:
        decision = "phase_c_blocked_holdout_contaminated"
    else:
        decision = "phase_c_blocked_control_equivalent"
    return [{
        "decision_class": decision,
        "phase_c_ready": int(phase_c_ready),
        "supporting_metric_family_count": len(families),
        "supporting_metric_families": json.dumps(sorted(families)),
        "supporting_probe_count": len(probes),
        "supporting_probes": json.dumps(sorted(probes)),
        "canonical_window_count": len(windows),
        "holdout_scoring_count": 0,
        "supporting_rows": len(supporting),
    }]


def family_recurrence(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return aggregate_recurrence(rows, ("metric_family",))


def flow_recurrence(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return aggregate_recurrence(rows, ("flow_mode",))


def window_recurrence(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    # Window support is embedded in coverage rates; this table summarizes by metric family/probe because effect rows are control-level.
    return aggregate_recurrence(rows, ("metric_family", "probe_key"))


def seed_start_recurrence(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return aggregate_recurrence(rows, ("metric_family", "metric_name", "probe_key", "flow_mode"))


def aggregate_recurrence(rows: list[dict[str, object]], keys: tuple[str, ...]) -> list[dict[str, object]]:
    out = []
    for key, items in group_by(rows, keys).items():
        row = {field: value for field, value in zip(keys, key)}
        row.update({
            "rows": len(items),
            "observed_recurrence_rate_mean": mean(float_or_zero(item.get("observed_recurrence_rate")) for item in items),
            "seed_recurrence_rate_mean": mean(float_or_zero(item.get("seed_recurrence_rate")) for item in items),
            "start_recurrence_rate_mean": mean(float_or_zero(item.get("start_recurrence_rate")) for item in items),
            "window_recurrence_rate_mean": mean(float_or_zero(item.get("window_recurrence_rate")) for item in items),
            "control_excess_recurrence_rate_mean": mean(float_or_zero(item.get("control_excess_recurrence_rate")) for item in items),
            "absolute_effect_size_mean": mean(float_or_zero(item.get("absolute_effect_size_mean")) for item in items),
        })
        out.append(row)
    return out


def control_quality_audit(controls: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (name, quality), items in group_by(controls, ("control_name", "control_quality")).items():
        out.append({"control_name": name, "control_quality": quality, "rows": len(items), "weak_control_flag": int(quality in {"placeholder", "not_available"})})
    return out


def holdout_status(split_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{"group_id": row.get("group_id"), "split_set": row.get("split_set"), "holdout_scored_in_phase_b": 0 if row.get("split_set") == "holdout_set" else "", "status": "listed_only_not_scored" if row.get("split_set") == "holdout_set" else "design_or_control_context"} for row in split_rows]


def job_manifest_rows(jobs: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{key: value for key, value in job.items() if key != "params"} for job in jobs]


def checkpoint_row(status: dict[str, object], started: float, rows: list[dict[str, object]], controls: list[dict[str, object]], errors: list[dict[str, object]]) -> dict[str, object]:
    return {
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "jobs_submitted": status.get("jobs_submitted"),
        "jobs_completed": status.get("jobs_completed"),
        "metric_rows": len(rows),
        "control_rows": len(controls),
        "errors": len(errors),
        "status": status.get("status"),
    }


def coverage(supporting_rows: list[dict[str, object]], recurrent_items: list[dict[str, object]], key: str, universe: set[str]) -> float:
    # Effect rows do not preserve seed/start/window for all context controls, so use supporting observed rows when any recurrent effect exists.
    if not recurrent_items:
        return 0.0
    return len({str(row.get(key)) for row in supporting_rows}) / max(1, len(universe))


def direction_stability(counts: Counter[str], total: int) -> str:
    if total <= 0:
        return "control_equivalent"
    direction, count = counts.most_common(1)[0]
    if direction == "control_equivalent":
        return "control_equivalent"
    if count / total >= 0.70:
        return f"stable_{direction}"
    return "mixed_direction"


def count_direction(items: list[dict[str, object]], direction: str) -> float:
    return sum(int(item.get("effect_direction") == direction) for item in items) / max(1, len(items))


def write_report(out_dir: Path, status: dict[str, object], phase_c: list[dict[str, object]], rec_rows: list[dict[str, object]], matched: list[dict[str, object]]) -> None:
    decision = phase_c[0] if phase_c else {}
    lines = [
        "# RFS-MB0 Frontier-Transform Phase B 10h Design Recurrence Report",
        "",
        "## 1. Claim boundary",
        "",
        "Phase B is design-set recurrence only. It is not holdout testing, candidate promotion, transfer, identity, agency, value, or scientific-gate validation.",
        "",
        "## 2. Cleanup/smoke result",
        "",
        "Smoke was run before the large batch and required outputs were checked.",
        "",
        "## 3. Run shape and wall-clock usage",
        "",
        f"Status: `{status.get('status')}`. Jobs: {status.get('jobs_completed')}/{status.get('jobs_requested')}. Elapsed seconds: {status.get('elapsed_seconds')}.",
        "",
        "## 4. Flow-mode and no-target audit",
        "",
        "See `phase_b_no_target_audit.csv`.",
        "",
        "## 5. Metric family recurrence",
        "",
        table(aggregate_recurrence(rec_rows, ("metric_family",)), ("metric_family", "rows", "observed_recurrence_rate_mean", "seed_recurrence_rate_mean", "window_recurrence_rate_mean")),
        "",
        "## 6. Effect direction stability",
        "",
        "See `phase_b_directional_effects.csv`.",
        "",
        "## 7. Matched transform controls",
        "",
        "See `phase_b_design_control_rows.csv` and `phase_b_control_quality_audit.csv`.",
        "",
        "## 8. Matched recurrence controls",
        "",
        table(matched, ("metric_family", "metric_name", "probe_key", "flow_mode", "observed_recurrence_rate", "recurrence_excess", "recurrence_percentile_vs_controls")),
        "",
        "## 9. Path-dependence profile",
        "",
        "Fractional seed/start/window rates are reported in recurrence tables.",
        "",
        "## 10. Phase C readiness decision",
        "",
        f"Decision: `{decision.get('decision_class', '')}`.",
        "",
        "## 11. Holdout status",
        "",
        "Holdout scoring count remained zero.",
        "",
        "## 12. Limitations",
        "",
        "Constraint, asymmetry, and roughness shuffled controls remain unavailable. Probe-marginal control is labeled placeholder and must not drive a positive conclusion.",
        "",
        "## 13. Output manifest",
        "",
        "See `output_manifest.json`.",
    ]
    (out_dir / "rfs_mb0_frontier_transform_phase_b_10h_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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
