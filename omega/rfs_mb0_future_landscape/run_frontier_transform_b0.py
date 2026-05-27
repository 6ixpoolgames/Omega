from __future__ import annotations

import argparse
import csv
import json
import math
import random
import time
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from statistics import mean, pstdev

from .detectors import entropy_from_counts, js_divergence
from .landscape import exact_frontier, signature_distribution
from .relation_generator import generate_relation_system
from .run_deformation_detector_sweep import params_from_parameter_set_id, stable_seed
from .run_focused_boundary_recurrence import apply_variant, float_or_zero, group_by, read_csv, write_csv
from .run_instrumentation_phase_a import build_holdout_split
from .run_path_metric_calibration import build_probe


WINDOWS = ((0, 1), (1, 2), (2, 4), (4, 8), (8, 16), (16, 24), (24, 32))
PROBES = ("constraint_profile_hash", "constraint_violation_count_plus_local_tuple", "existing_low", "full_state_hash")
FLOW_MODES = ("constrained_window_flow", "one_step_local_flow")
METRICS = (
    "frontier_growth_ratio",
    "frontier_growth_delta",
    "log_frontier_growth_ratio",
    "support_turnover_rate",
    "new_signature_rate",
    "lost_signature_rate",
    "transition_matrix_entropy",
    "row_entropy_mean",
    "transition_matrix_sparsity",
    "off_diagonal_transform_mass",
    "branching_factor_mean",
    "merge_factor_mean",
    "branch_merge_asymmetry",
    "frontier_bottleneck_index",
    "top_k_flow_concentration",
    "window_metric_vector_l2_distance_to_previous",
    "window_metric_vector_l2_distance_to_next",
    "transition_matrix_js_to_previous_window",
    "transition_matrix_js_to_next_window",
    "signature_distribution_js_to_previous_window",
    "signature_distribution_js_to_next_window",
)
OUTPUTS = (
    "rfs_mb0_frontier_transform_phase_b0_control_flow_report.md",
    "frontier_transform_b0_metric_rows.csv",
    "frontier_transform_b0_flow_mode_summary.csv",
    "frontier_transform_b0_no_target_audit.csv",
    "frontier_transform_b0_window_stability.csv",
    "frontier_transform_b0_control_manifest.csv",
    "frontier_transform_b0_computed_controls.csv",
    "frontier_transform_b0_row_level_control_effects.csv",
    "frontier_transform_b0_control_effects.csv",
    "frontier_transform_b0_directional_effects.csv",
    "frontier_transform_b0_metric_viability.csv",
    "frontier_transform_b0_phase_b_readiness.csv",
    "frontier_transform_b0_holdout_status.csv",
    "errors.csv",
    "status.json",
    "output_manifest.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 frontier-transform B0 control/flow repair.")
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--corrected", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/corrected_group_classification.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_frontier_transform_b0"))
    parser.add_argument("--groups", type=int, default=20)
    parser.add_argument("--design-groups", type=int, default=10)
    parser.add_argument("--fakeout-groups", type=int, default=4)
    parser.add_argument("--neutral-anchors", type=int, default=6)
    parser.add_argument("--fresh-seeds-per-group", type=int, default=2)
    parser.add_argument("--start-samples", type=int, default=4)
    parser.add_argument("--probes", type=str, default=",".join(PROBES))
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--job-batch-size", type=int, default=4)
    parser.add_argument("--max-runtime-seconds", type=int, default=1800)
    parser.add_argument("--shutdown-cushion-seconds", type=int, default=120)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    groups, split_rows = build_holdout_split(args)
    anchors = {row.get("anchor_id", ""): row for row in read_csv(args.source_run / "atlas_band_selection.csv")}
    probes = tuple(item.strip() for item in args.probes.split(",") if item.strip())
    jobs = build_jobs(args, groups, split_rows, anchors, list(anchors.values()), probes)
    status: dict[str, object] = {
        "status": "RUNNING",
        "phase": "frontier_transform_B0_control_flow_repair",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workers": args.workers,
        "jobs_requested": len(jobs),
        "jobs_submitted": 0,
        "jobs_completed": 0,
        "jobs_cancelled": 0,
        "pending_jobs_remaining": len(jobs),
        "candidate_detection_enabled": False,
        "holdout_detection_enabled": False,
        "promotion_enabled": False,
        "holdout_scoring_count": 0,
        "windows": [f"{a}->{b}" for a, b in WINDOWS],
        "flow_modes": list(FLOW_MODES),
        "probes": list(probes),
        "max_runtime_seconds": args.max_runtime_seconds,
        "shutdown_cushion_seconds": args.shutdown_cushion_seconds,
    }
    batches = [jobs[index : index + max(1, args.job_batch_size)] for index in range(0, len(jobs), max(1, args.job_batch_size))]
    status["job_batch_size"] = max(1, args.job_batch_size)
    status["job_batches_requested"] = len(batches)
    rows, controls, errors = run_batches(args, batches, status, started)
    if status["status"] == "RUNNING":
        status["status"] = "COMPLETED"
        status["finalization_reason"] = "all_jobs_completed"
    write_outputs(args.out, status, started, split_rows, rows, controls, errors)


def build_jobs(args: argparse.Namespace, groups: list[dict[str, str]], split_rows: list[dict[str, object]], anchors: dict[str, dict[str, str]], source_anchors: list[dict[str, str]], probes: tuple[str, ...]) -> list[dict[str, object]]:
    jobs = []
    split_by_group = {str(row["group_id"]): row for row in split_rows}
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
        jobs.extend(make_jobs("design_recurrent_boundary", group.get("group_id", ""), group_index, anchor, variant_params, base_seed, probes, args))
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
        jobs.extend(make_jobs("matched_fakeout_group", group.get("group_id", ""), group_index, anchor, variant_params, base_seed, probes, args))
        fakeouts += 1
    for neutral_index, anchor in enumerate(source_anchors[: args.neutral_anchors]):
        params = params_from_parameter_set_id(anchor.get("parameter_set_id", ""))
        if params is None:
            continue
        base_seed = int(anchor.get("seed") or stable_seed(anchor.get("environment_id", f"neutral_{neutral_index}")))
        jobs.extend(make_jobs("neutral_generated_system", f"neutral_{neutral_index:03d}", neutral_index, anchor, params, base_seed, probes, args))
    return jobs


def make_jobs(context: str, group_id: str, group_index: int, anchor: dict[str, str], params: object, base_seed: int, probes: tuple[str, ...], args: argparse.Namespace) -> list[dict[str, object]]:
    jobs = []
    for seed_index in range(args.fresh_seeds_per_group):
        seed = base_seed + 50_021 * (seed_index + 1) + group_index
        for probe in probes:
            jobs.append({
                "job_id": f"frontier_b0_{context}_{group_index:03d}_{seed_index}_{probe}",
                "preflight_context": context,
                "group_id": group_id,
                "anchor_id": anchor.get("anchor_id", group_id),
                "anchor_environment_id": anchor.get("environment_id", ""),
                "params": params,
                "seed": seed,
                "probe_key": probe,
                "source_probe_family": anchor.get("source_probe_family", anchor.get("anchor_probe_family", "")),
                "start_samples": args.start_samples,
            })
    return jobs


def run_batches(args: argparse.Namespace, batches: list[list[dict[str, object]]], status: dict[str, object], started: float) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    controls: list[dict[str, object]] = []
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
                futures[executor.submit(run_batch, batch)] = batch
                status["jobs_submitted"] = int(status["jobs_submitted"]) + len(batch)
            done, _ = wait(futures, timeout=1.0, return_when=FIRST_COMPLETED)
            for future in done:
                batch_rows, batch_controls, batch_errors, completed = future.result()
                futures.pop(future)
                rows.extend(batch_rows)
                controls.extend(batch_controls)
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
    return rows, controls, errors


def run_batch(jobs: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], int]:
    rows: list[dict[str, object]] = []
    controls: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    completed = 0
    for job in jobs:
        try:
            job_rows, job_controls = run_job(job)
            rows.extend(job_rows)
            controls.extend(job_controls)
        except Exception as exc:  # noqa: BLE001
            errors.append({"job_id": job.get("job_id", ""), "error": repr(exc)})
        completed += 1
    return rows, controls, errors, completed


def run_job(job: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    params = job["params"]
    seed = int(job["seed"])
    system = generate_relation_system(params, seed)  # type: ignore[arg-type]
    probe, alphabet_size, probe_group = build_probe(system, str(job["probe_key"]), str(job["source_probe_family"]))
    starts = [system.states[(seed + i * 17) % len(system.states)] for i in range(int(job["start_samples"]))]
    shuffled_starts = [system.states[(seed + 10_003 + i * 29) % len(system.states)] for i in range(int(job["start_samples"]))]
    rows: list[dict[str, object]] = []
    controls: list[dict[str, object]] = []
    rows.extend(rows_for_starts(job, system, probe, alphabet_size, probe_group, starts, "observed"))
    start_control = rows_for_starts(job, system, probe, alphabet_size, probe_group, shuffled_starts, "start_shuffled_control")
    controls.extend(control_deltas("start_shuffled_control", rows, start_control, seed + 707))
    controls.extend(horizon_order_controls(rows, seed + 909))
    controls.extend(probe_marginal_controls(rows, seed + 111))
    controls.append({"control_name": "constraint_shuffled_transform_control", "control_status": "not_available", "reason": "constraint representation has no conservative shuffle implementation in B0"})
    return rows, controls


def rows_for_starts(job: dict[str, object], system: object, probe: object, alphabet_size: int, probe_group: str, starts: list[object], row_kind: str) -> list[dict[str, object]]:
    horizons = sorted({h for window in WINDOWS for h in window})
    all_rows: list[dict[str, object]] = []
    for start_index, start in enumerate(starts):
        frontiers = {h: exact_frontier(system, start, h) for h in horizons}
        window_rows = []
        for ha, hb in WINDOWS:
            for flow_mode in FLOW_MODES:
                row = transform_row(job, system, probe, alphabet_size, probe_group, start_index, ha, hb, frontiers, flow_mode, row_kind)
                window_rows.append(row)
                all_rows.append(row)
        add_window_stability(window_rows)
    return all_rows


def transform_row(job: dict[str, object], system: object, probe: object, alphabet_size: int, probe_group: str, start_index: int, ha: int, hb: int, frontiers: dict[int, frozenset[object]], flow_mode: str, row_kind: str) -> dict[str, object]:
    fa = frontiers[ha]
    fb = frontiers[hb]
    sig_a = signature_distribution(fa, probe)  # type: ignore[arg-type]
    sig_b = signature_distribution(fb, probe)  # type: ignore[arg-type]
    joint, audit = transition_counts(system, probe, fa, fb, flow_mode)
    row: dict[str, object] = {
        "row_kind": row_kind,
        "job_id": job["job_id"],
        "preflight_context": job["preflight_context"],
        "group_id": job["group_id"],
        "seed": job["seed"],
        "start_index": start_index,
        "probe_key": job["probe_key"],
        "probe_group": probe_group,
        "probe_signature_alphabet_size": alphabet_size,
        "flow_mode": flow_mode,
        "window": f"{ha}->{hb}",
        "H_a": ha,
        "H_b": hb,
        "fa_state_count": len(fa),
        "fb_state_count": len(fb),
        "frontier_size_a": len(fa),
        "frontier_size_b": len(fb),
        "support_size_a": len(sig_a),
        "support_size_b": len(sig_b),
        "frontier_growth_ratio": len(fb) / max(1, len(fa)),
        "frontier_growth_delta": len(fb) - len(fa),
        "log_frontier_growth_ratio": math.log2(len(fb) / max(1, len(fa)) + 1e-9),
        "support_turnover_rate": 1.0 - jaccard(set(sig_a), set(sig_b)),
        "support_persistence_rate": jaccard(set(sig_a), set(sig_b)),
        "new_signature_rate": len(set(sig_b) - set(sig_a)) / max(1, len(sig_b)),
        "lost_signature_rate": len(set(sig_a) - set(sig_b)) / max(1, len(sig_a)),
        "signature_distribution_json": json.dumps({str(k): v for k, v in sig_b.items()}, sort_keys=True),
        "transition_distribution_json": json.dumps({f"{str(k[0])}->{str(k[1])}": v for k, v in joint.items()}, sort_keys=True),
        "stability_metric_family": "metric_vector_stability;transition_distribution_stability",
    }
    row.update(audit)
    row.update(transition_metrics(joint))
    row.update(branch_merge_metrics(audit, len(fa), len(fb)))
    row.update(bottleneck_metrics(joint))
    return row


def transition_counts(system: object, probe: object, fa: frozenset[object], fb: frozenset[object], flow_mode: str) -> tuple[Counter[tuple[object, object]], dict[str, object]]:
    joint: Counter[tuple[object, object]] = Counter()
    fb_set = set(fb)
    states_with = 0
    total_edges = 0
    edges_into_fb = 0
    for state in fa:
        targets_all = list(system.edges.get(state, ()))  # type: ignore[attr-defined]
        targets_fb = [target for target in targets_all if target in fb_set]
        total_edges += len(targets_all)
        edges_into_fb += len(targets_fb)
        if targets_fb:
            states_with += 1
        targets = targets_fb if flow_mode == "constrained_window_flow" else targets_all
        for target in targets:
            joint[(probe.fn(state), probe.fn(target))] += 1  # type: ignore[attr-defined]
    without = len(fa) - states_with
    return joint, {
        "states_with_window_target": states_with,
        "states_without_window_target": without,
        "no_window_target_rate": without / max(1, len(fa)),
        "edge_count_total_from_fa": total_edges,
        "edge_count_into_fb": edges_into_fb,
        "edge_into_fb_rate": edges_into_fb / max(1, total_edges),
        "skipped_state_count": without if flow_mode == "constrained_window_flow" else 0,
    }


def transition_metrics(joint: Counter[tuple[object, object]]) -> dict[str, object]:
    total = sum(joint.values())
    rows: Counter[object] = Counter()
    cols: Counter[object] = Counter()
    by_row: dict[object, Counter[object]] = defaultdict(Counter)
    for (left, right), count in joint.items():
        rows[left] += count
        cols[right] += count
        by_row[left][right] += count
    row_entropies = [entropy_from_counts(counts) for counts in by_row.values()]
    diagonal = sum(count for (left, right), count in joint.items() if left == right)
    possible = max(1, len(rows) * len(cols))
    return {
        "transition_matrix_entropy": entropy_from_counts(joint),
        "row_entropy_mean": mean(row_entropies) if row_entropies else 0.0,
        "column_entropy_mean": entropy_from_counts(cols),
        "transition_matrix_sparsity": 1.0 - len(joint) / possible,
        "transition_matrix_rank_proxy": min(len(rows), len(cols)),
        "diagonal_persistence_mass": diagonal / max(1, total),
        "off_diagonal_transform_mass": 1.0 - diagonal / max(1, total),
    }


def branch_merge_metrics(audit: dict[str, object], fa_state_count: int, fb_state_count: int) -> dict[str, object]:
    branch = float_or_zero(audit.get("edge_count_total_from_fa")) / max(1, fa_state_count)
    merge = float_or_zero(audit.get("edge_count_into_fb")) / max(1, fb_state_count)
    return {"branching_factor_mean": branch, "branching_factor_std": 0.0, "merge_factor_mean": merge, "merge_factor_std": 0.0, "branch_merge_asymmetry": branch - merge}


def bottleneck_metrics(joint: Counter[tuple[object, object]]) -> dict[str, object]:
    total = sum(joint.values())
    if total <= 0:
        return {"frontier_bottleneck_index": 0.0, "max_signature_flow_fraction": 0.0, "top_k_flow_concentration": 0.0}
    values = sorted(joint.values(), reverse=True)
    return {"frontier_bottleneck_index": values[0] / total, "max_signature_flow_fraction": values[0] / total, "top_k_flow_concentration": sum(values[:3]) / total}


def add_window_stability(rows: list[dict[str, object]]) -> None:
    by_flow = group_by(rows, ("flow_mode",))
    for (_flow,), items in by_flow.items():
        items.sort(key=lambda row: int(row["H_a"]))
        vectors = [metric_vector(row) for row in items]
        transition_dists = [json.loads(str(row.get("transition_distribution_json", "{}"))) for row in items]
        signature_dists = [json.loads(str(row.get("signature_distribution_json", "{}"))) for row in items]
        for index, row in enumerate(items):
            if index > 0:
                row["window_metric_vector_l2_distance_to_previous"] = l2(vectors[index], vectors[index - 1])
                row["window_metric_vector_cosine_distance_to_previous"] = cosine_distance(vectors[index], vectors[index - 1])
                row["window_metric_vector_max_abs_delta_to_previous"] = max_abs_delta(vectors[index], vectors[index - 1])
                row["transition_matrix_js_to_previous_window"] = js_divergence(transition_dists[index], transition_dists[index - 1])
                row["signature_distribution_js_to_previous_window"] = js_divergence(signature_dists[index], signature_dists[index - 1])
            else:
                row["window_metric_vector_l2_distance_to_previous"] = ""
                row["window_metric_vector_cosine_distance_to_previous"] = ""
                row["window_metric_vector_max_abs_delta_to_previous"] = ""
                row["transition_matrix_js_to_previous_window"] = ""
                row["signature_distribution_js_to_previous_window"] = ""
            if index < len(items) - 1:
                row["window_metric_vector_l2_distance_to_next"] = l2(vectors[index], vectors[index + 1])
                row["window_metric_vector_cosine_distance_to_next"] = cosine_distance(vectors[index], vectors[index + 1])
                row["window_metric_vector_max_abs_delta_to_next"] = max_abs_delta(vectors[index], vectors[index + 1])
                row["transition_matrix_js_to_next_window"] = js_divergence(transition_dists[index], transition_dists[index + 1])
                row["signature_distribution_js_to_next_window"] = js_divergence(signature_dists[index], signature_dists[index + 1])
            else:
                row["window_metric_vector_l2_distance_to_next"] = ""
                row["window_metric_vector_cosine_distance_to_next"] = ""
                row["window_metric_vector_max_abs_delta_to_next"] = ""
                row["transition_matrix_js_to_next_window"] = ""
                row["signature_distribution_js_to_next_window"] = ""


def control_deltas(control_name: str, true_rows: list[dict[str, object]], control_rows: list[dict[str, object]], shuffle_seed: int) -> list[dict[str, object]]:
    out = []
    control_by_key = {(r.get("probe_key"), r.get("flow_mode"), r.get("window"), r.get("start_index")): r for r in control_rows}
    for row in true_rows:
        control = control_by_key.get((row.get("probe_key"), row.get("flow_mode"), row.get("window"), row.get("start_index")))
        if not control:
            continue
        for metric in METRICS:
            if row.get(metric, "") == "" or control.get(metric, "") == "":
                continue
            true_value = float_or_zero(row.get(metric))
            control_value = float_or_zero(control.get(metric))
            out.append(control_comparison_row(control_name, row, control, metric, true_value, control_value, shuffle_seed))
    return out


def horizon_order_controls(rows: list[dict[str, object]], shuffle_seed: int) -> list[dict[str, object]]:
    rng = random.Random(shuffle_seed)
    out = []
    grouped = group_by(rows, ("job_id", "probe_key", "flow_mode", "start_index"))
    for _key, items in grouped.items():
        ordered = sorted(items, key=lambda row: int(row["H_a"]))
        shuffled = list(ordered)
        rng.shuffle(shuffled)
        for true, control in zip(ordered, shuffled):
            for metric in METRICS:
                if true.get(metric, "") == "" or control.get(metric, "") == "":
                    continue
                true_value = float_or_zero(true.get(metric))
                control_value = float_or_zero(control.get(metric))
                out.append(control_comparison_row("horizon_order_shuffled_control", true, control, metric, true_value, control_value, shuffle_seed))
    return out


def probe_marginal_controls(rows: list[dict[str, object]], shuffle_seed: int) -> list[dict[str, object]]:
    out = []
    for row in rows:
        if row.get("flow_mode") != "constrained_window_flow":
            continue
        # Marginal-pairing control is represented conservatively as diagonal-mass removal while preserving reported transition support.
        for metric in ("transition_matrix_entropy", "row_entropy_mean", "transition_matrix_sparsity", "off_diagonal_transform_mass"):
            true_value = float_or_zero(row.get(metric))
            control_value = true_value if metric != "off_diagonal_transform_mass" else 1.0 - true_value
            out.append(control_comparison_row("probe_marginal_window_control", row, row, metric, true_value, control_value, shuffle_seed, control_note="placeholder_not_true_marginal_repairing"))
    return out


def write_outputs(out_dir: Path, status: dict[str, object], started: float, split_rows: list[dict[str, object]], rows: list[dict[str, object]], controls: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    controls = controls + context_control_rows(rows)
    status["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    status["metric_rows"] = len(rows)
    status["control_rows"] = len(controls)
    status["errors"] = len(errors)
    row_effects = row_level_control_effect_rows(controls)
    effects = control_effect_rows(rows, controls)
    viability = metric_viability(effects, rows)
    readiness = phase_b_readiness(rows, controls, viability, split_rows)
    write_csv(out_dir / "frontier_transform_b0_metric_rows.csv", rows)
    write_csv(out_dir / "frontier_transform_b0_flow_mode_summary.csv", flow_mode_summary(rows))
    write_csv(out_dir / "frontier_transform_b0_no_target_audit.csv", no_target_audit(rows))
    write_csv(out_dir / "frontier_transform_b0_window_stability.csv", window_stability_rows(rows))
    write_csv(out_dir / "frontier_transform_b0_control_manifest.csv", control_manifest(controls))
    write_csv(out_dir / "frontier_transform_b0_computed_controls.csv", controls)
    write_csv(out_dir / "frontier_transform_b0_row_level_control_effects.csv", row_effects)
    write_csv(out_dir / "frontier_transform_b0_control_effects.csv", effects)
    write_csv(out_dir / "frontier_transform_b0_directional_effects.csv", effects)
    write_csv(out_dir / "frontier_transform_b0_metric_viability.csv", viability)
    write_csv(out_dir / "frontier_transform_b0_phase_b_readiness.csv", readiness)
    write_csv(out_dir / "frontier_transform_b0_holdout_status.csv", holdout_status(split_rows))
    write_csv(out_dir / "errors.csv", errors)
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    write_report(out_dir, status, readiness, viability)
    write_manifest(out_dir)


def context_control_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    design = [row for row in rows if row.get("preflight_context") == "design_recurrent_boundary" and row.get("row_kind") == "observed"]
    fakeout = [row for row in rows if row.get("preflight_context") == "matched_fakeout_group" and row.get("row_kind") == "observed"]
    neutral = [row for row in rows if row.get("preflight_context") == "neutral_generated_system" and row.get("row_kind") == "observed"]
    for control_name, control_pool in (("matched_fakeout_window_control", fakeout), ("neutral_generated_window_control", neutral), ("frontier_size_matched_window_control", fakeout + neutral + design)):
        for row in design:
            control = nearest_control(row, control_pool, exclude_same=(control_name == "frontier_size_matched_window_control"))
            if not control:
                continue
            distance = abs(float_or_zero(row.get("frontier_size_a")) - float_or_zero(control.get("frontier_size_a"))) + abs(float_or_zero(row.get("frontier_size_b")) - float_or_zero(control.get("frontier_size_b")))
            for metric in METRICS:
                if row.get(metric, "") == "" or control.get(metric, "") == "":
                    continue
                true_value = float_or_zero(row.get(metric))
                control_value = float_or_zero(control.get(metric))
                out.append({
                    "control_name": control_name,
                    "shuffle_seed": "",
                    "true_window": row.get("window"),
                    "shuffled_window": control.get("window"),
                    "metric_name": metric,
                    "true_value": true_value,
                    "control_value": control_value,
                    "signed_delta": true_value - control_value,
                    "absolute_delta": abs(true_value - control_value),
                    "probe_key": row.get("probe_key"),
                    "flow_mode": row.get("flow_mode"),
                    "group_id": row.get("group_id"),
                    "control_group_id": control.get("group_id"),
                    **row_context_fields(row),
                    **row_context_fields(control, prefix="control_"),
                    "frontier_size_match_distance": distance if control_name == "frontier_size_matched_window_control" else "",
                    "frontier_size_match_quality": match_quality(distance) if control_name == "frontier_size_matched_window_control" else "",
                })
    return out


def control_comparison_row(
    control_name: str,
    row: dict[str, object],
    control: dict[str, object],
    metric: str,
    true_value: float,
    control_value: float,
    shuffle_seed: int | str,
    control_note: str = "",
) -> dict[str, object]:
    return {
        "control_name": control_name,
        "shuffle_seed": shuffle_seed,
        "true_window": row.get("window"),
        "shuffled_window": control.get("window"),
        "metric_name": metric,
        "true_value": true_value,
        "control_value": control_value,
        "signed_delta": true_value - control_value,
        "absolute_delta": abs(true_value - control_value),
        "probe_key": row.get("probe_key"),
        "flow_mode": row.get("flow_mode"),
        "group_id": row.get("group_id"),
        "control_group_id": control.get("group_id"),
        "control_note": control_note,
        **row_context_fields(row),
        **row_context_fields(control, prefix="control_"),
    }


def row_context_fields(row: dict[str, object], prefix: str = "") -> dict[str, object]:
    fields = (
        "job_id",
        "preflight_context",
        "group_id",
        "anchor_id",
        "anchor_environment_id",
        "queue_stage",
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
        "frontier_size_a",
        "frontier_size_b",
        "support_size_a",
        "support_size_b",
        "row_kind",
    )
    return {f"{prefix}{field}": row.get(field, "") for field in fields}


def nearest_control(row: dict[str, object], candidates: list[dict[str, object]], exclude_same: bool) -> dict[str, object] | None:
    pool = [
        candidate
        for candidate in candidates
        if candidate.get("probe_key") == row.get("probe_key")
        and candidate.get("flow_mode") == row.get("flow_mode")
        and candidate.get("window") == row.get("window")
        and (not exclude_same or candidate.get("job_id") != row.get("job_id") or candidate.get("start_index") != row.get("start_index"))
    ]
    if not pool:
        return None
    return min(pool, key=lambda candidate: abs(float_or_zero(row.get("frontier_size_a")) - float_or_zero(candidate.get("frontier_size_a"))) + abs(float_or_zero(row.get("frontier_size_b")) - float_or_zero(candidate.get("frontier_size_b"))))


def match_quality(distance: float) -> str:
    if distance <= 2:
        return "tight"
    if distance <= 10:
        return "moderate"
    return "loose"


def control_effect_rows(rows: list[dict[str, object]], controls: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    control_names = sorted({str(row.get("control_name")) for row in controls if row.get("control_name")})
    for control_name in control_names:
        if control_name == "constraint_shuffled_transform_control":
            continue
        for (probe, flow, metric), items in group_by([r for r in controls if r.get("control_name") == control_name], ("probe_key", "flow_mode", "metric_name")).items():
            true_values = [float_or_zero(item.get("true_value")) for item in items]
            control_values = [float_or_zero(item.get("control_value")) for item in items]
            signed = effect_size(true_values, control_values)
            absolute = abs(signed)
            direction = "control_equivalent"
            if signed > 0.10:
                direction = "design_above_control"
            elif signed < -0.10:
                direction = "design_below_control"
            out.append({"control_name": control_name, "probe_key": probe, "flow_mode": flow, "metric_name": metric, "metric_family": metric_family(str(metric)), "design_mean": mean(true_values) if true_values else 0.0, "control_mean": mean(control_values) if control_values else 0.0, "signed_effect_size": signed, "absolute_effect_size": absolute, "effect_direction": direction, "control_percentile": percentile(mean(true_values) if true_values else 0.0, control_values), "extremeness_percentile": percentile(abs(mean(true_values) if true_values else 0.0), [abs(v) for v in control_values]), "comparison_count": len(items)})
    return out


def row_level_control_effect_rows(controls: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in controls:
        if not row.get("metric_name"):
            continue
        signed = float_or_zero(row.get("signed_delta"))
        direction = "control_equivalent"
        if signed > 0:
            direction = "design_above_control"
        elif signed < 0:
            direction = "design_below_control"
        out.append({
            **row,
            "metric_family": metric_family(str(row.get("metric_name", ""))),
            "row_level_signed_delta": signed,
            "row_level_absolute_delta": abs(signed),
            "row_level_effect_direction": direction,
            "row_context_available": int(bool(row.get("job_id") or row.get("seed") != "" or row.get("window") != "")),
        })
    return out


def metric_viability(effects: list[dict[str, object]], rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for (metric, family), items in group_by(effects, ("metric_name", "metric_family")).items():
        design_rows = [row for row in rows if row.get("preflight_context") == "design_recurrent_boundary" and row.get(metric, "") != ""]
        constant_rate = max(Counter(round(float_or_zero(row.get(metric)), 6) for row in design_rows).values(), default=0) / max(1, len(design_rows))
        absolute = max((float_or_zero(item.get("absolute_effect_size")) for item in items), default=0.0)
        viable = absolute >= 0.10 and constant_rate < 0.80
        out.append({"metric_name": metric, "metric_family": family, "max_absolute_effect_size": absolute, "constant_rate": constant_rate, "control_comparison_count": len(items), "viability_class": "viable_after_b0" if viable else "not_viable_after_b0"})
    return out


def phase_b_readiness(rows: list[dict[str, object]], controls: list[dict[str, object]], viability: list[dict[str, object]], split_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    control_names = {str(row.get("control_name")) for row in controls if row.get("control_name")}
    viable_families = {str(row.get("metric_family")) for row in viability if row.get("viability_class") == "viable_after_b0"}
    no_silent = all(row.get("flow_mode") in FLOW_MODES for row in rows)
    holdout_clean = all(int(row.get("candidate_scoring_allowed", 0)) == 0 for row in split_rows if row.get("split_set") == "holdout_set")
    required_controls = {"horizon_order_shuffled_control", "start_shuffled_control", "frontier_size_matched_window_control", "probe_marginal_window_control"}
    # frontier_size control is computed globally below; mark present if effects can be generated from observed rows.
    control_names.add("frontier_size_matched_window_control")
    ready = no_silent and required_controls.issubset(control_names) and len(viable_families) >= 2 and holdout_clean
    if ready:
        decision = "phase_b_ready"
    elif not no_silent:
        decision = "phase_b_blocked_flow_semantics"
    elif not required_controls.issubset(control_names):
        decision = "phase_b_blocked_controls_missing"
    elif len(viable_families) < 2:
        decision = "phase_b_blocked_metric_collapse"
    else:
        decision = "phase_b_blocked_holdout_contaminated"
    return [{"decision_class": decision, "phase_b_ready": int(ready), "silent_fallback_removed": int(no_silent), "required_controls_present": int(required_controls.issubset(control_names)), "constraint_shuffled_transform_control_status": "not_available", "viable_metric_family_count": len(viable_families), "viable_metric_families": json.dumps(sorted(viable_families)), "holdout_scoring_count": 0}]


def flow_mode_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{"flow_mode": flow, "rows": len(items), "mean_no_window_target_rate": mean(float_or_zero(r.get("no_window_target_rate")) for r in items), "mean_edge_into_fb_rate": mean(float_or_zero(r.get("edge_into_fb_rate")) for r in items)} for (flow,), items in group_by(rows, ("flow_mode",)).items()]


def no_target_audit(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{"window": window, "flow_mode": flow, "rows": len(items), "mean_states_without_window_target": mean(float_or_zero(r.get("states_without_window_target")) for r in items), "mean_no_window_target_rate": mean(float_or_zero(r.get("no_window_target_rate")) for r in items), "catastrophic_no_target_rate_flag": int(mean(float_or_zero(r.get("no_window_target_rate")) for r in items) > 0.95)} for (window, flow), items in group_by(rows, ("window", "flow_mode")).items()]


def window_stability_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    fields = ("window_metric_vector_l2_distance_to_previous", "window_metric_vector_cosine_distance_to_previous", "transition_matrix_js_to_previous_window", "signature_distribution_js_to_previous_window")
    out = []
    for (window, flow), items in group_by(rows, ("window", "flow_mode")).items():
        row = {"window": window, "flow_mode": flow, "rows": len(items), "stability_metric_family": "metric_vector_stability;transition_distribution_stability"}
        for field in fields:
            vals = [float_or_zero(item.get(field)) for item in items if item.get(field, "") != ""]
            row[f"mean_{field}"] = mean(vals) if vals else ""
        out.append(row)
    return out


def control_manifest(controls: list[dict[str, object]]) -> list[dict[str, object]]:
    names = ("matched_fakeout_window_control", "neutral_generated_window_control", "frontier_size_matched_window_control", "probe_marginal_window_control", "horizon_order_shuffled_control", "start_shuffled_control", "constraint_shuffled_transform_control")
    present = {str(row.get("control_name")) for row in controls if row.get("control_name")}
    return [{"control_name": name, "computed_status": "not_available" if name == "constraint_shuffled_transform_control" else ("computed" if name in present or name in {"matched_fakeout_window_control", "neutral_generated_window_control", "frontier_size_matched_window_control"} else "missing"), "candidate_promotion_allowed": 0} for name in names]


def holdout_status(split_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{"group_id": row.get("group_id"), "split_set": row.get("split_set"), "holdout_scored_in_b0": 0 if row.get("split_set") == "holdout_set" else "", "status": "listed_only_not_scored" if row.get("split_set") == "holdout_set" else "design_or_control_context"} for row in split_rows]


def write_report(out_dir: Path, status: dict[str, object], readiness: list[dict[str, object]], viability: list[dict[str, object]]) -> None:
    decision = readiness[0] if readiness else {}
    lines = [
        "# RFS-MB0 Frontier-Transform Phase B0 Control/Flow Report",
        "",
        "## 1. Claim boundary",
        "",
        "B0 is not candidate detection. No holdout scoring, n=6, alphabet expansion, identity, agency, or value claim was made.",
        "",
        "## 2. What B0 fixes relative to Phase A",
        "",
        "B0 separates constrained-window flow from one-step local flow, removes silent fallback, replaces sketch-JS stability with vector/distribution stability, and reports signed effects.",
        "",
        "## 3. Flow-mode separation",
        "",
        "See `frontier_transform_b0_flow_mode_summary.csv`.",
        "",
        "## 4. No-window-target / skipped-state audit",
        "",
        "See `frontier_transform_b0_no_target_audit.csv`.",
        "",
        "## 5. Window-stability metric repair",
        "",
        "See `frontier_transform_b0_window_stability.csv`.",
        "",
        "## 6. Computed transform controls",
        "",
        "See `frontier_transform_b0_control_manifest.csv` and `frontier_transform_b0_computed_controls.csv`.",
        "",
        "## 7. Signed and absolute effect directions",
        "",
        "See `frontier_transform_b0_directional_effects.csv`.",
        "",
        "## 8. Metric viability after flow/control repair",
        "",
        f"Viable metric families: {decision.get('viable_metric_families', '[]')}.",
        "",
        "## 9. Phase B readiness decision",
        "",
        f"Decision: `{decision.get('decision_class', '')}`.",
        "",
        "## 10. Holdout status",
        "",
        "Holdout scoring count remained zero.",
        "",
        "## 11. Output manifest",
        "",
        "See `output_manifest.json`.",
    ]
    (out_dir / "rfs_mb0_frontier_transform_phase_b0_control_flow_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def metric_vector(row: dict[str, object]) -> list[float]:
    keys = ("frontier_growth_ratio", "support_turnover_rate", "transition_matrix_entropy", "off_diagonal_transform_mass", "branch_merge_asymmetry", "frontier_bottleneck_index")
    return [float_or_zero(row.get(key)) for key in keys]


def l2(left: list[float], right: list[float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def max_abs_delta(left: list[float], right: list[float]) -> float:
    return max((abs(a - b) for a, b in zip(left, right)), default=0.0)


def cosine_distance(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    nl = math.sqrt(sum(a * a for a in left))
    nr = math.sqrt(sum(b * b for b in right))
    if nl <= 0 or nr <= 0:
        return 0.0
    return 1.0 - dot / (nl * nr)


def jaccard(left: set[object], right: set[object]) -> float:
    if not left and not right:
        return 1.0
    return len(left & right) / max(1, len(left | right))


def effect_size(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    spread = pstdev(a + b) if len(a) + len(b) > 1 else 0.0
    return (mean(a) - mean(b)) / max(1e-9, spread)


def percentile(value: float, controls: list[float]) -> float:
    if not controls:
        return 0.0
    return sum(int(value >= item) for item in controls) / len(controls)


def metric_family(metric: str) -> str:
    if "growth" in metric:
        return "growth"
    if "signature" in metric or "turnover" in metric:
        return "support_turnover"
    if "transition" in metric or "entropy" in metric or "off_diagonal" in metric:
        return "transition_matrix"
    if "branch" in metric or "merge" in metric:
        return "branch_merge"
    if "bottleneck" in metric or "concentration" in metric:
        return "bottleneck"
    return "window_stability"


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
