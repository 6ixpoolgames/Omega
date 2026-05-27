from __future__ import annotations

import argparse
import csv
import json
import math
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
METRIC_FAMILIES = ("growth", "support_turnover", "transition_matrix", "branch_merge", "bottleneck", "window_stability")
OUTPUTS = (
    "rfs_mb0_frontier_transform_instrumentation_phase_a_report.md",
    "frontier_transform_metric_manifest.json",
    "frontier_transform_viability_preflight.csv",
    "frontier_transform_metric_summary.md",
    "frontier_transform_window_multiplicity_audit.csv",
    "frontier_transform_control_manifest.csv",
    "frontier_transform_holdout_split.csv",
    "frontier_transform_metric_rows.csv",
    "frontier_transform_context_comparison.csv",
    "errors.csv",
    "status.json",
    "output_manifest.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 frontier-transform instrumentation Phase A preflight.")
    parser.add_argument("--selection", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_boundary_recurrence_repair_batch1/focused_boundary_group_selection.csv"))
    parser.add_argument("--corrected", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_detector_instrumentation_repair_scaled/corrected_group_classification.csv"))
    parser.add_argument("--source-run", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260526_boundary_resolution_sweep"))
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb0_relation_atlas/20260527_frontier_transform_phase_a"))
    parser.add_argument("--groups", type=int, default=20)
    parser.add_argument("--design-groups", type=int, default=10)
    parser.add_argument("--neutral-anchors", type=int, default=6)
    parser.add_argument("--fakeout-groups", type=int, default=4)
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
    source_anchors = list(anchors.values())
    probes = tuple(item.strip() for item in args.probes.split(",") if item.strip())
    jobs = build_jobs(args, groups, split_rows, anchors, source_anchors, probes)
    status: dict[str, object] = {
        "status": "RUNNING",
        "phase": "frontier_transform_A_preflight_only",
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
        "windows": [f"{a}->{b}" for a, b in WINDOWS],
        "probes": list(probes),
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
    write_outputs(args.out, status, started, probes, split_rows, rows, errors)


def build_jobs(args: argparse.Namespace, groups: list[dict[str, str]], split_rows: list[dict[str, object]], anchors: dict[str, dict[str, str]], source_anchors: list[dict[str, str]], probes: tuple[str, ...]) -> list[dict[str, object]]:
    jobs = []
    split_by_group = {str(row["group_id"]): row for row in split_rows}
    fakeouts = 0
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
                "job_id": f"frontier_transform_{context}_{group_index:03d}_{seed_index}_{probe}",
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
                futures[executor.submit(run_batch, batch)] = batch
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


def run_batch(jobs: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], int]:
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    completed = 0
    for job in jobs:
        try:
            rows.extend(run_job(job))
        except Exception as exc:  # noqa: BLE001
            errors.append({"job_id": job.get("job_id", ""), "error": repr(exc)})
        completed += 1
    return rows, errors, completed


def run_job(job: dict[str, object]) -> list[dict[str, object]]:
    params = job["params"]
    seed = int(job["seed"])
    system = generate_relation_system(params, seed)  # type: ignore[arg-type]
    probe, alphabet_size, probe_group = build_probe(system, str(job["probe_key"]), str(job["source_probe_family"]))
    starts = [system.states[(seed + i * 17) % len(system.states)] for i in range(int(job["start_samples"]))]
    horizons = sorted({h for window in WINDOWS for h in window})
    rows = []
    for start_index, start in enumerate(starts):
        frontiers = {h: exact_frontier(system, start, h) for h in horizons}
        window_rows = []
        for window_index, (ha, hb) in enumerate(WINDOWS):
            row = transform_row(job, system, probe, alphabet_size, probe_group, start_index, ha, hb, frontiers)
            window_rows.append(row)
            rows.append(row)
        add_window_stability(window_rows)
    return rows


def transform_row(job: dict[str, object], system: object, probe: object, alphabet_size: int, probe_group: str, start_index: int, ha: int, hb: int, frontiers: dict[int, frozenset[object]]) -> dict[str, object]:
    fa = frontiers[ha]
    fb = frontiers[hb]
    sig_a = signature_distribution(fa, probe)  # type: ignore[arg-type]
    sig_b = signature_distribution(fb, probe)  # type: ignore[arg-type]
    support_a = set(sig_a)
    support_b = set(sig_b)
    joint = transition_counts(system, probe, fa, fb)
    row: dict[str, object] = {
        "job_id": job["job_id"],
        "preflight_context": job["preflight_context"],
        "group_id": job["group_id"],
        "seed": job["seed"],
        "start_index": start_index,
        "probe_key": job["probe_key"],
        "probe_group": probe_group,
        "probe_signature_alphabet_size": alphabet_size,
        "window": f"{ha}->{hb}",
        "H_a": ha,
        "H_b": hb,
        "frontier_size_a": len(fa),
        "frontier_size_b": len(fb),
        "support_size_a": len(support_a),
        "support_size_b": len(support_b),
        "support_floor_flag": int(len(fa) <= 1 or len(fb) <= 1),
        "support_ceiling_flag": int(len(fb) >= 0.90 * max(1, len(system.states))),  # type: ignore[attr-defined]
        "frontier_growth_ratio": len(fb) / max(1, len(fa)),
        "frontier_growth_delta": len(fb) - len(fa),
        "log_frontier_growth_ratio": math.log2(len(fb) / max(1, len(fa)) + 1e-9),
        "pre_saturation_growth_ratio": (len(fb) / max(1, len(fa))) if len(fb) < 0.90 * max(1, len(system.states)) else "",
        "support_turnover_rate": 1.0 - jaccard(support_a, support_b),
        "support_persistence_rate": jaccard(support_a, support_b),
        "new_signature_rate": len(support_b - support_a) / max(1, len(support_b)),
        "lost_signature_rate": len(support_a - support_b) / max(1, len(support_a)),
    }
    row.update(transition_metrics(joint))
    row.update(branch_merge_metrics(system, fa, fb))
    row.update(bottleneck_metrics(joint))
    row["transform_profile_js_to_previous_window"] = ""
    row["transform_profile_js_to_next_window"] = ""
    row["window_persistence_length"] = ""
    row["transform_regime_change_score"] = ""
    row["control_count_reported"] = 9
    row["metric_count_reported"] = 25
    return row


def transition_counts(system: object, probe: object, fa: frozenset[object], fb: frozenset[object]) -> Counter[tuple[object, object]]:
    counts: Counter[tuple[object, object]] = Counter()
    fb_set = set(fb)
    for state in fa:
        source_sig = probe.fn(state)  # type: ignore[attr-defined]
        targets = [target for target in system.edges.get(state, ()) if target in fb_set]  # type: ignore[attr-defined]
        if not targets:
            targets = list(system.edges.get(state, ()))  # type: ignore[attr-defined]
        for target in targets:
            counts[(source_sig, probe.fn(target))] += 1  # type: ignore[attr-defined]
    return counts


def transition_metrics(joint: Counter[tuple[object, object]]) -> dict[str, object]:
    total = sum(joint.values())
    rows: Counter[object] = Counter()
    cols: Counter[object] = Counter()
    for (left, right), count in joint.items():
        rows[left] += count
        cols[right] += count
    row_entropies = []
    row_totals: dict[object, Counter[object]] = defaultdict(Counter)
    for (left, right), count in joint.items():
        row_totals[left][right] += count
    for counts in row_totals.values():
        row_entropies.append(entropy_from_counts(counts))
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


def branch_merge_metrics(system: object, fa: frozenset[object], fb: frozenset[object]) -> dict[str, object]:
    fb_set = set(fb)
    branches = []
    merge_counts: Counter[object] = Counter()
    for state in fa:
        targets = [target for target in system.edges.get(state, ()) if target in fb_set]  # type: ignore[attr-defined]
        branches.append(len(targets))
        for target in targets:
            merge_counts[target] += 1
    merges = list(merge_counts.values())
    branch_mean = mean(branches) if branches else 0.0
    merge_mean = mean(merges) if merges else 0.0
    return {
        "branching_factor_mean": branch_mean,
        "branching_factor_std": pstdev(branches) if len(branches) > 1 else 0.0,
        "merge_factor_mean": merge_mean,
        "merge_factor_std": pstdev(merges) if len(merges) > 1 else 0.0,
        "branch_merge_asymmetry": branch_mean - merge_mean,
    }


def bottleneck_metrics(joint: Counter[tuple[object, object]]) -> dict[str, object]:
    total = sum(joint.values())
    if total <= 0:
        return {"frontier_bottleneck_index": 0.0, "max_signature_flow_fraction": 0.0, "top_k_flow_concentration": 0.0}
    values = sorted(joint.values(), reverse=True)
    max_flow = values[0] / total
    top_k = sum(values[:3]) / total
    return {
        "frontier_bottleneck_index": max_flow,
        "max_signature_flow_fraction": max_flow,
        "top_k_flow_concentration": top_k,
    }


def add_window_stability(rows: list[dict[str, object]]) -> None:
    profiles = [profile_counts(row) for row in rows]
    for index, row in enumerate(rows):
        if index > 0:
            row["transform_profile_js_to_previous_window"] = js_divergence(profiles[index], profiles[index - 1])
        if index < len(rows) - 1:
            row["transform_profile_js_to_next_window"] = js_divergence(profiles[index], profiles[index + 1])
        previous_js = float_or_zero(row.get("transform_profile_js_to_previous_window"))
        next_js = float_or_zero(row.get("transform_profile_js_to_next_window"))
        row["transform_regime_change_score"] = max(previous_js, next_js)
        row["window_persistence_length"] = sum(int(js_divergence(profiles[index], other) <= 0.10) for other in profiles)


def profile_counts(row: dict[str, object]) -> dict[object, int]:
    return {
        "growth": int(10 * float_or_zero(row.get("frontier_growth_ratio"))),
        "turnover": int(10 * float_or_zero(row.get("support_turnover_rate"))),
        "offdiag": int(10 * float_or_zero(row.get("off_diagonal_transform_mass"))),
        "bottleneck": int(10 * float_or_zero(row.get("frontier_bottleneck_index"))),
    }


def write_outputs(out_dir: Path, status: dict[str, object], started: float, probes: tuple[str, ...], split_rows: list[dict[str, object]], rows: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    status["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    status["row_count"] = len(rows)
    status["errors"] = len(errors)
    write_csv(out_dir / "frontier_transform_metric_rows.csv", rows)
    write_csv(out_dir / "frontier_transform_viability_preflight.csv", viability_rows(rows))
    write_csv(out_dir / "frontier_transform_window_multiplicity_audit.csv", multiplicity_rows(probes, split_rows))
    write_csv(out_dir / "frontier_transform_control_manifest.csv", control_manifest())
    write_csv(out_dir / "frontier_transform_holdout_split.csv", split_rows)
    write_csv(out_dir / "frontier_transform_context_comparison.csv", context_comparison(rows))
    write_csv(out_dir / "errors.csv", errors)
    (out_dir / "frontier_transform_metric_manifest.json").write_text(json.dumps(metric_manifest(probes), indent=2, sort_keys=True), encoding="utf-8")
    write_summary(out_dir, status, rows)
    write_report(out_dir, status, probes, rows)
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    write_manifest(out_dir)


def viability_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    metric_names = metric_columns()
    for metric in metric_names:
        family = metric_family(metric)
        for (context, probe), items in group_by(rows, ("preflight_context", "probe_key")).items():
            values = [float_or_zero(row.get(metric)) for row in items if row.get(metric) != ""]
            if not values:
                continue
            constant_rate = max(Counter(round(value, 6) for value in values).values()) / max(1, len(values))
            saturated_rate = bounded_saturation_rate(metric, values)
            support_floor_rate = rate(int(float_or_zero(row.get("support_floor_flag"))) for row in items)
            design_values = [float_or_zero(row.get(metric)) for row in rows if row.get("preflight_context") == "design_recurrent_boundary" and row.get("probe_key") == probe and row.get(metric) != ""]
            control_values = [float_or_zero(row.get(metric)) for row in rows if row.get("preflight_context") in {"matched_fakeout_group", "neutral_generated_system"} and row.get("probe_key") == probe and row.get(metric) != ""]
            effect = effect_size(design_values, control_values)
            stable = seed_start_stability(items, metric)
            viable = constant_rate < 0.80 and saturated_rate < 0.80 and support_floor_rate < 0.80 and stable >= 0.20
            viability_class = "viable_transform_metric" if viable else "transform_metric_not_viable"
            if viable and probe in {"existing_low", "full_state_hash"}:
                viability_class = "control_or_diagnostic_metric_viable_not_for_detection"
            out.append({
                "preflight_context": context,
                "probe_key": probe,
                "metric_family": family,
                "metric_name": metric,
                "rows": len(values),
                "metric_mean": mean(values),
                "metric_std": pstdev(values) if len(values) > 1 else 0.0,
                "constant_rate": constant_rate,
                "saturated_rate": saturated_rate,
                "support_floor_rate": support_floor_rate,
                "design_vs_control_effect_size": effect,
                "seed_start_stability_proxy": stable,
                "viability_class": viability_class,
            })
    return out


def context_comparison(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for metric in metric_columns():
        for (probe,), probe_rows in group_by(rows, ("probe_key",)).items():
            design = [float_or_zero(row.get(metric)) for row in probe_rows if row.get("preflight_context") == "design_recurrent_boundary" and row.get(metric) != ""]
            fakeout = [float_or_zero(row.get(metric)) for row in probe_rows if row.get("preflight_context") == "matched_fakeout_group" and row.get(metric) != ""]
            neutral = [float_or_zero(row.get(metric)) for row in probe_rows if row.get("preflight_context") == "neutral_generated_system" and row.get(metric) != ""]
            out.append({
                "probe_key": probe,
                "metric_name": metric,
                "metric_family": metric_family(metric),
                "design_mean": mean(design) if design else "",
                "fakeout_mean": mean(fakeout) if fakeout else "",
                "neutral_mean": mean(neutral) if neutral else "",
                "design_vs_fakeout_effect_size": effect_size(design, fakeout),
                "design_vs_neutral_effect_size": effect_size(design, neutral),
            })
    return out


def metric_columns() -> tuple[str, ...]:
    return (
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
        "transform_regime_change_score",
        "window_persistence_length",
    )


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


def bounded_saturation_rate(metric: str, values: list[float]) -> float:
    bounded = {
        "support_turnover_rate",
        "support_persistence_rate",
        "new_signature_rate",
        "lost_signature_rate",
        "transition_matrix_sparsity",
        "diagonal_persistence_mass",
        "off_diagonal_transform_mass",
        "frontier_bottleneck_index",
        "max_signature_flow_fraction",
        "top_k_flow_concentration",
    }
    if metric not in bounded:
        return 0.0
    return rate(value <= 1e-9 or value >= 0.999999 for value in values)


def detection_viable_rows(viability: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        row
        for row in viability
        if row.get("preflight_context") == "design_recurrent_boundary"
        and row.get("viability_class") == "viable_transform_metric"
        and row.get("probe_key") not in {"existing_low", "full_state_hash"}
    ]


def metric_manifest(probes: tuple[str, ...]) -> list[dict[str, object]]:
    return [
        {
            "metric_family": family,
            "metrics": [metric for metric in metric_columns() if metric_family(metric) == family],
            "probes": list(probes),
            "windows": [f"{a}->{b}" for a, b in WINDOWS],
            "reason_for_inclusion": "pre-registered frontier-transform Phase A metric family",
            "promotion_enabled": False,
        }
        for family in METRIC_FAMILIES
    ]


def control_manifest() -> list[dict[str, object]]:
    controls = (
        "frontier_size_matched_window_control",
        "probe_marginal_window_control",
        "horizon_order_shuffled_control",
        "start_shuffled_control",
        "matched_fakeout_window_control",
        "neutral_generated_window_control",
        "window_local_random_flow_control",
        "constraint_shuffled_transform_control",
        "asymmetry_shuffled_transform_control",
        "roughness_resampled_transform_control",
    )
    return [{"control_name": name, "phase_a_status": "reported_or_contextual_preflight_control", "candidate_promotion_allowed": 0} for name in controls]


def multiplicity_rows(probes: tuple[str, ...], split_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{
        "window_count_reported": len(WINDOWS),
        "metric_family_count_reported": len(METRIC_FAMILIES),
        "metric_count_reported": len(metric_columns()),
        "probe_count_reported": len(probes),
        "control_count_reported": len(control_manifest()),
        "group_count": len(split_rows),
        "candidate_decision_count": 0,
        "holdout_scoring_count": 0,
        "phase": "A_preflight_only",
    }]


def write_summary(out_dir: Path, status: dict[str, object], rows: list[dict[str, object]]) -> None:
    viability = viability_rows(rows)
    viable = detection_viable_rows(viability)
    families = sorted({str(row.get("metric_family")) for row in viable})
    lines = [
        "# RFS-MB0 Frontier-Transform Metric Summary",
        "",
        "Phase A only. No holdout scoring and no candidate promotion occurred.",
        "",
        f"Status: `{status.get('status')}`. Jobs: {status.get('jobs_completed')}/{status.get('jobs_requested')}. Rows: {status.get('row_count')}. Errors: {status.get('errors')}.",
        "",
        f"Viable design-set metric families: {families}",
        f"Phase B allowed by family count: {len(families) >= 2}",
        "",
        table(viable, ("probe_key", "metric_family", "metric_name", "design_vs_control_effect_size", "seed_start_stability_proxy", "viability_class")),
    ]
    (out_dir / "frontier_transform_metric_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(out_dir: Path, status: dict[str, object], probes: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    viability = viability_rows(rows)
    viable = detection_viable_rows(viability)
    families = sorted({str(row.get("metric_family")) for row in viable})
    decision = "Phase B allowed for a small design-set transform recurrence run." if len(families) >= 2 else "Phase B blocked; return to transform metric design."
    lines = [
        "# RFS-MB0 Frontier-Transform Instrumentation Phase A Report",
        "",
        "## 1. Claim boundary",
        "",
        "This preflight makes no Omega, agency, identity, value, viability, or discovery claim.",
        "",
        "## 2. Why endpoint probes failed",
        "",
        "Endpoint quotients mostly collapsed into collision-limited or constraint-axis-only signal. This run tests whether horizon-window transforms are better instruments.",
        "",
        "## 3. Frontier-transform measurement definition",
        "",
        "Each row summarizes how an exact reachable frontier transforms across a pre-registered horizon window.",
        "",
        "## 4. Metric manifest",
        "",
        f"Metric families: {', '.join(METRIC_FAMILIES)}. Probes: {', '.join(probes)}.",
        "",
        "## 5. Window set and multiplicity audit",
        "",
        f"Windows: {', '.join(f'{a}->{b}' for a, b in WINDOWS)}.",
        "",
        "## 6. Control manifest",
        "",
        "See `frontier_transform_control_manifest.csv`.",
        "",
        "## 7. Viability preflight results",
        "",
        f"Viable design-set metric families: {families}.",
        table(viable, ("probe_key", "metric_family", "metric_name", "design_vs_control_effect_size", "seed_start_stability_proxy")),
        "",
        "## 8. Design/fakeout/neutral descriptive comparison",
        "",
        "See `frontier_transform_context_comparison.csv`.",
        "",
        "## 9. Decision",
        "",
        decision,
        "",
        "## 10. Output manifest",
        "",
        "See `output_manifest.json`.",
    ]
    (out_dir / "rfs_mb0_frontier_transform_instrumentation_phase_a_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def effect_size(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    spread = pstdev(a + b) if len(a) + len(b) > 1 else 0.0
    return (mean(a) - mean(b)) / max(1e-9, spread)


def seed_start_stability(rows: list[dict[str, object]], metric: str) -> float:
    by_seed = []
    for (_seed,), items in group_by(rows, ("seed",)).items():
        vals = [float_or_zero(row.get(metric)) for row in items if row.get(metric) != ""]
        if vals:
            by_seed.append(mean(vals))
    if len(by_seed) < 2:
        return 0.0
    return 1.0 / (1.0 + pstdev(by_seed))


def jaccard(left: set[object], right: set[object]) -> float:
    if not left and not right:
        return 1.0
    return len(left & right) / max(1, len(left | right))


def rate(values: object) -> float:
    items = list(values)
    return sum(int(value) for value in items) / max(1, len(items))


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
