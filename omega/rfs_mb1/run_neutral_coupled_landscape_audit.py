from __future__ import annotations

import argparse
import csv
import json
import math
import random
import time
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import replace
from pathlib import Path

from omega.rfs_mb0_future_landscape.detectors import entropy_from_counts, js_divergence
from omega.rfs_mb0_future_landscape.landscape import exact_frontier, reachable, signature_distribution
from omega.rfs_mb0_future_landscape.probes import Probe, generate_probes
from omega.rfs_mb0_future_landscape.relation_generator import (
    RelationParams,
    generate_relation_system,
    sample_parameter_sets,
)
from omega.rfs_mb0_future_landscape.substrate import LandscapeSystem, State


COUPLING_MAPS = ("frontier_signature", "constraint_profile", "asymmetry_profile")
MODES = (
    "uncoupled",
    "full_coupling_A_to_B",
    "full_coupling_B_to_A",
    "bidirectional_full_coupling",
    "source_shuffled_coupling",
    "magnitude_matched_random_coupling",
    "target_shuffled_coupling",
    "direction_reversed_coupling",
    "A_B_swapped_control",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB1 neutral coupled-landscape exploratory audit.")
    parser.add_argument("--out", type=Path, default=Path("results/rfs_mb1_coupled_landscape/20260526_exploratory_smoke"))
    parser.add_argument("--paired-landscapes", type=int, default=36)
    parser.add_argument("--fresh-seeds", type=int, default=1)
    parser.add_argument("--horizons", type=str, default="4,8,16,24,32")
    parser.add_argument("--start-samples", type=int, default=3)
    parser.add_argument("--probe-limit", type=int, default=5)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-jobs", type=int, default=1200)
    parser.add_argument("--checkpoint-every", type=int, default=120)
    parser.add_argument("--max-runtime-seconds", type=int, default=1800)
    parser.add_argument("--seed", type=int, default=260526)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    horizons = tuple(int(item.strip()) for item in args.horizons.split(",") if item.strip())
    jobs, sampling_rows = build_jobs(args, horizons)
    jobs = jobs[: args.max_jobs]
    config: dict[str, object] = {
        "status": "RUNNING",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workers": args.workers,
        "paired_landscapes_requested": args.paired_landscapes,
        "fresh_seeds": args.fresh_seeds,
        "horizons": list(horizons),
        "start_samples": args.start_samples,
        "probe_limit": args.probe_limit,
        "max_jobs": args.max_jobs,
        "max_runtime_seconds": args.max_runtime_seconds,
        "jobs_requested": len(jobs),
        "promotion_enabled": False,
        "claim_boundary": "exploratory neutral coupling audit only; no agency/Omega/identity/value claims",
    }
    write_status(args.out, config, started, 0, 0)
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    pending = list(jobs)
    futures = {}
    timed_out = False
    executor = ProcessPoolExecutor(max_workers=max(1, args.workers))
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
            done, _ = wait(futures, timeout=max(0.1, min(2.0, remaining)), return_when=FIRST_COMPLETED)
            for future in done:
                job = futures.pop(future)
                try:
                    rows.extend(future.result())
                except Exception as exc:  # noqa: BLE001
                    errors.append({"job_id": job.get("job_id", ""), "error": repr(exc)})
            if rows and len(rows) % max(1, args.checkpoint_every) == 0:
                write_outputs(args.out, config, started, sampling_rows, rows, errors)
    finally:
        if timed_out:
            for future in futures:
                future.cancel()
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
    if config["status"] == "RUNNING":
        config["status"] = "COMPLETED"
    config["jobs_completed"] = len({row["job_id"] for row in rows})
    config["errors"] = len(errors)
    write_outputs(args.out, config, started, sampling_rows, rows, errors)


def build_jobs(args: argparse.Namespace, horizons: tuple[int, ...]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    params = sample_parameter_sets(max(args.paired_landscapes * 2 + 12, 72), args.seed)
    jobs: list[dict[str, object]] = []
    sampling_rows: list[dict[str, object]] = []
    for pair_index in range(args.paired_landscapes):
        a_params = params[(2 * pair_index) % len(params)]
        b_params = params[(2 * pair_index + 1) % len(params)]
        for fresh_index in range(args.fresh_seeds):
            seed_a = args.seed + 1009 * pair_index + 17 * fresh_index
            seed_b = args.seed + 1009 * pair_index + 503 + 17 * fresh_index
            sampling_rows.append(
                {
                    "pair_id": f"pair_{pair_index:04d}_fresh_{fresh_index}",
                    "fresh_index": fresh_index,
                    "A_parameter_set_id": a_params.parameter_set_id,
                    "B_parameter_set_id": b_params.parameter_set_id,
                    "A_seed": seed_a,
                    "B_seed": seed_b,
                }
            )
            for coupling_map in COUPLING_MAPS:
                for start_index in range(args.start_samples):
                    for probe_index in range(args.probe_limit):
                        jobs.append(
                            {
                                "job_id": f"pair{pair_index:04d}_fresh{fresh_index}_{coupling_map}_s{start_index}_p{probe_index}",
                                "pair_id": f"pair_{pair_index:04d}_fresh_{fresh_index}",
                                "pair_index": pair_index,
                                "fresh_index": fresh_index,
                                "A_params": params_to_dict(a_params),
                                "B_params": params_to_dict(b_params),
                                "A_seed": seed_a,
                                "B_seed": seed_b,
                                "coupling_map": coupling_map,
                                "start_index": start_index,
                                "probe_index": probe_index,
                                "horizons": horizons,
                            }
                        )
    return jobs, sampling_rows


def run_job(job: dict[str, object]) -> list[dict[str, object]]:
    horizons = tuple(int(item) for item in job["horizons"])  # type: ignore[union-attr]
    system_a = generate_relation_system(params_from_dict(job["A_params"]), int(job["A_seed"]))  # type: ignore[arg-type]
    system_b = generate_relation_system(params_from_dict(job["B_params"]), int(job["B_seed"]))  # type: ignore[arg-type]
    probe_a = select_probe(system_a, int(job["probe_index"]))
    probe_b = select_probe(system_b, int(job["probe_index"]))
    start_a = system_a.states[(int(job["A_seed"]) + 31 * int(job["start_index"])) % len(system_a.states)]
    start_b = system_b.states[(int(job["B_seed"]) + 31 * int(job["start_index"])) % len(system_b.states)]
    coupling_map = str(job["coupling_map"])
    rows = []

    uncoupled_b = metric_bundle(system_b, start_b, probe_b, horizons)
    uncoupled_a = metric_bundle(system_a, start_a, probe_a, horizons)
    coupled_b = apply_coupling(system_b, system_a, start_a, probe_a, coupling_map, "full", horizons, int(job["B_seed"]) + 7001)
    coupled_a = apply_coupling(system_a, system_b, start_b, probe_b, coupling_map, "full", horizons, int(job["A_seed"]) + 7003)
    bidir_a = apply_coupling(coupled_a, system_b, start_b, probe_b, coupling_map, "full", horizons, int(job["A_seed"]) + 7011)
    bidir_b = apply_coupling(coupled_b, system_a, start_a, probe_a, coupling_map, "full", horizons, int(job["B_seed"]) + 7013)

    mode_systems = {
        "uncoupled": ("B", system_b, uncoupled_b, uncoupled_b),
        "full_coupling_A_to_B": ("B", coupled_b, metric_bundle(coupled_b, start_b, probe_b, horizons), uncoupled_b),
        "full_coupling_B_to_A": ("A", coupled_a, metric_bundle(coupled_a, start_a, probe_a, horizons), uncoupled_a),
        "bidirectional_full_coupling": ("B", bidir_b, metric_bundle(bidir_b, start_b, probe_b, horizons), uncoupled_b),
        "source_shuffled_coupling": ("B", apply_coupling(system_b, system_a, start_a, probe_a, coupling_map, "source_shuffled", horizons, int(job["B_seed"]) + 7021), None, uncoupled_b),
        "magnitude_matched_random_coupling": ("B", apply_coupling(system_b, system_a, start_a, probe_a, coupling_map, "random", horizons, int(job["B_seed"]) + 7023), None, uncoupled_b),
        "target_shuffled_coupling": ("B", apply_coupling(system_b, system_a, start_a, probe_a, coupling_map, "target_shuffled", horizons, int(job["B_seed"]) + 7027), None, uncoupled_b),
        "direction_reversed_coupling": ("B", apply_coupling(system_b, system_a, start_a, probe_a, coupling_map, "direction_reversed", horizons, int(job["B_seed"]) + 7029), None, uncoupled_b),
        "A_B_swapped_control": ("A", coupled_a, metric_bundle(coupled_a, start_a, probe_a, horizons), uncoupled_a),
    }
    for mode, (target, system, metrics, baseline) in mode_systems.items():
        if metrics is None:
            probe = probe_b if target == "B" else probe_a
            start = start_b if target == "B" else start_a
            metrics = metric_bundle(system, start, probe, horizons)
        rows.append(
            {
                "job_id": job["job_id"],
                "pair_id": job["pair_id"],
                "coupling_map": coupling_map,
                "coupling_mode": mode,
                "target_landscape": target,
                "start_index": job["start_index"],
                "probe_name": probe_b.name if target == "B" else probe_a.name,
                "probe_family": probe_b.probe_family if target == "B" else probe_a.probe_family,
                **metrics,
                **delta_metrics(metrics, baseline),
            }
        )
    return annotate_specificity(rows)


def apply_coupling(
    target: LandscapeSystem,
    source: LandscapeSystem,
    source_start: State,
    source_probe: Probe,
    coupling_map: str,
    mode: str,
    horizons: tuple[int, ...],
    seed: int,
) -> LandscapeSystem:
    rng = random.Random(seed)
    signal = coupling_signal(source, source_start, source_probe, coupling_map, mode, horizons, seed)
    states = list(target.states)
    new_edges: dict[State, tuple[State, ...]] = {}
    for index, state in enumerate(target.states):
        targets = list(target.edges[state])
        if not targets:
            new_edges[state] = tuple()
            continue
        replace_index = signal_hash(signal, f"{state}:{index}:slot") % len(targets)
        if mode == "direction_reversed":
            source_pool = incoming_neighbors(target, state) or states
        elif mode == "target_shuffled":
            source_pool = states
        else:
            source_pool = local_candidate_pool(target, state)
        candidate_index = signal_hash(signal, f"{state}:{index}:candidate") % len(source_pool)
        if mode == "random":
            candidate_index = rng.randrange(len(source_pool))
        targets[replace_index] = source_pool[candidate_index]
        if len(targets) > 1 and signal_hash(signal, f"{state}:second") % 5 == 0:
            second = (replace_index + 1) % len(targets)
            targets[second] = source_pool[(candidate_index + 1) % len(source_pool)]
        new_edges[state] = tuple(sorted(set(targets)))
    return replace(
        target,
        system_id=f"{target.system_id}_{coupling_map}_{mode}_coupled",
        family=f"{target.family}_{coupling_map}_{mode}_coupled",
        edges=new_edges,
        metadata={**target.metadata, "coupling_map": coupling_map, "coupling_mode": mode, "coupling_source_id": source.system_id},
    )


def coupling_signal(
    source: LandscapeSystem,
    source_start: State,
    source_probe: Probe,
    coupling_map: str,
    mode: str,
    horizons: tuple[int, ...],
    seed: int,
) -> str:
    frontier = exact_frontier(source, source_start, min(max(horizons), 16))
    if mode == "source_shuffled":
        shuffled = list(frontier)
        random.Random(seed + 41).shuffle(shuffled)
        frontier = frozenset(shuffled[: max(1, len(shuffled) // 2)])
    if coupling_map == "frontier_signature":
        counts = signature_distribution(frontier, source_probe)
        return json.dumps(sorted((str(key), value) for key, value in counts.items()))
    if coupling_map == "constraint_profile":
        return str(source.metadata.get("constraint_hash", "")) + ":" + str(source.metadata.get("constraint_density", ""))
    if coupling_map == "asymmetry_profile":
        out_degrees = [len(source.edges[state]) for state in source.states]
        in_counts = Counter(target for targets in source.edges.values() for target in targets)
        payload = {
            "out": histogram(out_degrees),
            "in": histogram(list(in_counts.values())),
            "asymmetry": source.metadata.get("asymmetry_strength", 0.0),
        }
        return json.dumps(payload, sort_keys=True)
    return source.system_id


def metric_bundle(system: LandscapeSystem, start: State, probe: Probe, horizons: tuple[int, ...]) -> dict[str, object]:
    distributions = {h: signature_distribution(exact_frontier(system, start, h), probe) for h in horizons}
    reach_counts = {h: len(reachable(system, start, h)) for h in horizons}
    support_sizes = {h: len(distributions[h]) for h in horizons}
    entropies = {h: entropy_from_counts(distributions[h]) for h in horizons}
    max_h = max(horizons)
    return {
        "reachable_signature_support_size": support_sizes[max_h],
        "reachable_signature_support_fraction": support_sizes[max_h] / max(1, len(system.states)),
        "distribution_entropy": entropies[max_h],
        "support_growth_curve": json.dumps([support_sizes[h] for h in horizons]),
        "reach_growth_curve": json.dumps([reach_counts[h] for h in horizons]),
        "entropy_curve": json.dumps([round(entropies[h], 6) for h in horizons]),
        "cap_or_censoring_flag": int(reach_counts[max_h] / max(1, len(system.states)) >= 0.95),
        "_distributions": distributions,
    }


def delta_metrics(metrics: dict[str, object], baseline: dict[str, object]) -> dict[str, object]:
    horizons = sorted(metrics["_distributions"])  # type: ignore[index]
    js_values = [
        js_divergence(metrics["_distributions"][h], baseline["_distributions"][h])  # type: ignore[index]
        for h in horizons
    ]
    support_jaccards = [
        jaccard(metrics["_distributions"][h], baseline["_distributions"][h])  # type: ignore[index]
        for h in horizons
    ]
    support_symdiffs = [
        1.0 - support_jaccards[index]
        for index, _h in enumerate(horizons)
    ]
    entropy_delta = float(metrics["distribution_entropy"]) - float(baseline["distribution_entropy"])
    support_delta = float(metrics["reachable_signature_support_size"]) - float(baseline["reachable_signature_support_size"])
    return {
        "support_symmetric_difference_fraction": support_symdiffs[-1],
        "support_jaccard_vs_uncoupled": support_jaccards[-1],
        "distribution_JS_vs_uncoupled": js_values[-1],
        "TV_distance_vs_uncoupled": tv_distance(metrics["_distributions"][horizons[-1]], baseline["_distributions"][horizons[-1]]),  # type: ignore[index]
        "mass_shift_vs_uncoupled": support_delta,
        "support_growth_curve_delta": support_delta,
        "distribution_entropy_delta": entropy_delta,
        "coupled_deformation_delta": js_values[-1] + support_symdiffs[-1] + abs(entropy_delta),
        "horizon_lag_class": lag_class(js_values, horizons),
        "JS_curve_vs_uncoupled": json.dumps([round(value, 6) for value in js_values]),
    }


def annotate_specificity(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_mode = {str(row["coupling_mode"]): row for row in rows}
    full = by_mode.get("full_coupling_A_to_B")
    if not full:
        return cleanup_rows(rows)
    random_control = by_mode.get("magnitude_matched_random_coupling", full)
    source_control = by_mode.get("source_shuffled_coupling", full)
    target_control = by_mode.get("target_shuffled_coupling", full)
    reversed_control = by_mode.get("direction_reversed_coupling", full)
    swapped = by_mode.get("A_B_swapped_control", full)
    for row in rows:
        score = float(row["coupled_deformation_delta"])
        row["specific_coupling_excess"] = score - float(random_control["coupled_deformation_delta"])
        row["source_structure_excess"] = score - float(source_control["coupled_deformation_delta"])
        row["target_specificity_excess"] = score - float(target_control["coupled_deformation_delta"])
        row["directionality_delta"] = float(full["coupled_deformation_delta"]) - float(reversed_control["coupled_deformation_delta"])
        row["swap_delta"] = float(full["coupled_deformation_delta"]) - float(swapped["coupled_deformation_delta"])
        row["phenotype_class"] = phenotype_class(row)
        row["fakeout_class"] = fakeout_class(row)
    return cleanup_rows(rows)


def phenotype_class(row: dict[str, object]) -> str:
    if int(row["cap_or_censoring_flag"]):
        return "cap_or_censoring_limited"
    score = float(row["coupled_deformation_delta"])
    if score < 0.05:
        return "no_detectable_coupling"
    if float(row["specific_coupling_excess"]) <= 0.01:
        return "magnitude_only_deformation"
    if float(row["source_structure_excess"]) > 0.03 and float(row["target_specificity_excess"]) > 0.03:
        return "mixed_support_distribution_coupling"
    if float(row["source_structure_excess"]) > 0.03:
        return "source_structure_specific_deformation"
    if float(row["target_specificity_excess"]) > 0.03:
        return "target_specific_deformation"
    if abs(float(row["directionality_delta"])) > 0.05:
        return "directional_coupling"
    return "underdetermined_coupling"


def fakeout_class(row: dict[str, object]) -> str:
    if int(row["cap_or_censoring_flag"]):
        return "saturation_fakeout"
    if float(row["coupled_deformation_delta"]) < 0.05:
        return "none"
    if float(row["specific_coupling_excess"]) <= 0.01 and float(row["coupled_deformation_delta"]) >= 0.05:
        return "magnitude_only_fakeout"
    if float(row["source_structure_excess"]) <= 0.01:
        return "source_shuffle_equivalent"
    if float(row["target_specificity_excess"]) <= 0.01:
        return "target_shuffle_equivalent"
    if float(row["reachable_signature_support_fraction"]) <= 0.02:
        return "probe_collision_fakeout"
    return "none"


def write_outputs(
    out_dir: Path,
    config: dict[str, object],
    started: float,
    sampling_rows: list[dict[str, object]],
    rows: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    summary = coupling_summary_rows(rows)
    specificity = specificity_rows(rows)
    lag = lag_profile_rows(rows)
    fakeouts = fakeout_rows(rows)
    phenotypes = phenotype_rows(rows)
    recurrence = recurrence_rows(rows)
    write_csv(out_dir / "coupled_landscape_sampling_plan.csv", sampling_rows)
    write_csv(out_dir / "coupling_mode_metric_rows.csv", rows)
    write_csv(out_dir / "coupling_map_summary.csv", summary)
    write_csv(out_dir / "coupling_specificity_summary.csv", specificity)
    write_csv(out_dir / "coupling_horizon_lag_profile.csv", lag)
    write_csv(out_dir / "coupling_matched_controls.csv", matched_control_rows(rows))
    write_csv(out_dir / "coupling_fakeout_summary.csv", fakeouts)
    write_csv(out_dir / "coupling_phenotype_summary.csv", phenotypes)
    write_csv(out_dir / "coupling_start_probe_recurrence.csv", recurrence)
    write_csv(out_dir / "errors.csv", errors)
    write_case_studies(out_dir, rows)
    write_report(out_dir, config, started, rows, summary, specificity, lag, fakeouts, phenotypes, recurrence, errors)
    write_status(out_dir, config, started, len(rows), len(errors))


def write_report(
    out_dir: Path,
    config: dict[str, object],
    started: float,
    rows: list[dict[str, object]],
    summary: list[dict[str, object]],
    specificity: list[dict[str, object]],
    lag: list[dict[str, object]],
    fakeouts: list[dict[str, object]],
    phenotypes: list[dict[str, object]],
    recurrence: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    full_rows = [row for row in rows if row.get("coupling_mode") == "full_coupling_A_to_B"]
    specific = [row for row in full_rows if float(row.get("specific_coupling_excess", 0.0)) > 0.03 and row.get("fakeout_class") == "none"]
    recommendation = "keep_as_exploratory_sandbox"
    if len(specific) >= max(3, len(full_rows) // 20):
        recommendation = "run_broader_neutral_coupled_landscape_atlas"
    if not specific and full_rows:
        recommendation = "defer_or_repair_coupling_maps"
    lines = [
        "# RFS-MB1 Neutral Coupled Landscape Audit Report",
        "",
        "Promotion disabled. This is an exploratory coupled-landscape smoke, not an Omega, agency, value, identity, or scientific-gate claim.",
        "",
        f"- Status: {config.get('status', '')}",
        f"- Wall clock used: {time.perf_counter() - started:.1f} seconds",
        f"- Workers requested: {config.get('workers', '')}",
        f"- Metric rows completed: {len(rows)}",
        f"- Full A->B rows: {len(full_rows)}",
        f"- Specific non-fakeout full rows: {len(specific)}",
        f"- Errors: {len(errors)}",
        f"- Recommendation: {recommendation}",
        "",
        "## Coupling Map Summary",
        "",
        "| coupling_map | mode | n | mean deformation | mean specific excess | mean source excess | mean target excess | fakeout rate |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            "| {coupling_map} | {coupling_mode} | {n_rows} | {mean_coupled_deformation_delta:.4f} | {mean_specific_coupling_excess:.4f} | {mean_source_structure_excess:.4f} | {mean_target_specificity_excess:.4f} | {fakeout_rate:.3f} |".format(**row)
        )
    lines.extend(["", "## Phenotypes", "", "| phenotype | n |", "|---|---:|"])
    for row in phenotypes:
        lines.append(f"| {row['phenotype_class']} | {row['n_rows']} |")
    lines.extend(["", "## Fakeouts", "", "| fakeout | n |", "|---|---:|"])
    for row in fakeouts:
        lines.append(f"| {row['fakeout_class']} | {row['n_rows']} |")
    lines.extend(
        [
            "",
            "## Required Questions",
            "",
            f"- Beyond uncoupled controls: mean full A->B deformation is {mean([float(row.get('coupled_deformation_delta', 0.0)) for row in full_rows]):.4f}.",
            f"- Magnitude-only explanation: {sum(1 for row in full_rows if row.get('fakeout_class') == 'magnitude_only_fakeout')} full rows are magnitude-only fakeouts.",
            f"- Source structure: {sum(1 for row in full_rows if float(row.get('source_structure_excess', 0.0)) > 0.03)} full rows clear a source-shuffle margin.",
            f"- Target specificity: {sum(1 for row in full_rows if float(row.get('target_specificity_excess', 0.0)) > 0.03)} full rows clear a target-shuffle margin.",
            f"- Directionality: {sum(1 for row in full_rows if abs(float(row.get('directionality_delta', 0.0))) > 0.05)} full rows show directional imbalance.",
            f"- Lag: {len(lag)} coupling-map/mode lag summaries written to `coupling_horizon_lag_profile.csv`.",
            f"- Recurrence: {len(recurrence)} start/probe recurrence summaries written to `coupling_start_probe_recurrence.csv`.",
            "",
            "## Claim Boundary",
            "",
            "This smoke tests whether neutral coupling maps can deform reachable future support/distribution beyond matched controls. It does not assess agency, consciousness, identity, valuerhood, or Omega.",
        ]
    )
    (out_dir / "neutral_coupled_landscape_audit_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def coupling_summary_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for key, items in group(rows, ("coupling_map", "coupling_mode")).items():
        out.append(
            {
                "coupling_map": key[0],
                "coupling_mode": key[1],
                "n_rows": len(items),
                "mean_coupled_deformation_delta": mean_float(items, "coupled_deformation_delta"),
                "mean_specific_coupling_excess": mean_float(items, "specific_coupling_excess"),
                "mean_source_structure_excess": mean_float(items, "source_structure_excess"),
                "mean_target_specificity_excess": mean_float(items, "target_specificity_excess"),
                "fakeout_rate": sum(1 for row in items if row.get("fakeout_class") != "none") / max(1, len(items)),
            }
        )
    return sorted(out, key=lambda row: (str(row["coupling_map"]), str(row["coupling_mode"])))


def specificity_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "coupling_map": key[0],
            "n_rows": len(items),
            "positive_specific_excess_rate": sum(1 for row in items if float(row.get("specific_coupling_excess", 0.0)) > 0.03) / max(1, len(items)),
            "positive_source_excess_rate": sum(1 for row in items if float(row.get("source_structure_excess", 0.0)) > 0.03) / max(1, len(items)),
            "positive_target_excess_rate": sum(1 for row in items if float(row.get("target_specificity_excess", 0.0)) > 0.03) / max(1, len(items)),
            "mean_directionality_abs": mean([abs(float(row.get("directionality_delta", 0.0))) for row in items]),
        }
        for key, items in group([row for row in rows if row.get("coupling_mode") == "full_coupling_A_to_B"], ("coupling_map",)).items()
    ]


def lag_profile_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "coupling_map": key[0],
            "coupling_mode": key[1],
            "lag_class": key[2],
            "n_rows": len(items),
        }
        for key, items in group(rows, ("coupling_map", "coupling_mode", "horizon_lag_class")).items()
    ]


def fakeout_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter(str(row.get("fakeout_class", "none")) for row in rows)
    return [{"fakeout_class": key, "n_rows": value} for key, value in sorted(counts.items())]


def phenotype_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter(str(row.get("phenotype_class", "underdetermined")) for row in rows)
    return [{"phenotype_class": key, "n_rows": value} for key, value in sorted(counts.items())]


def recurrence_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for key, items in group([row for row in rows if row.get("coupling_mode") == "full_coupling_A_to_B"], ("coupling_map", "probe_family")).items():
        pair_ids = {row["pair_id"] for row in items}
        candidate_pairs = {row["pair_id"] for row in items if row.get("fakeout_class") == "none" and float(row.get("specific_coupling_excess", 0.0)) > 0.03}
        out.append(
            {
                "coupling_map": key[0],
                "probe_family": key[1],
                "pair_count": len(pair_ids),
                "specific_pair_count": len(candidate_pairs),
                "specific_pair_rate": len(candidate_pairs) / max(1, len(pair_ids)),
            }
        )
    return out


def matched_control_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    wanted = {"magnitude_matched_random_coupling", "source_shuffled_coupling", "target_shuffled_coupling", "direction_reversed_coupling", "A_B_swapped_control"}
    return [
        {
            "pair_id": row["pair_id"],
            "job_id": row["job_id"],
            "coupling_map": row["coupling_map"],
            "control_mode": row["coupling_mode"],
            "coupled_deformation_delta": row["coupled_deformation_delta"],
            "phenotype_class": row["phenotype_class"],
            "fakeout_class": row["fakeout_class"],
        }
        for row in rows
        if row.get("coupling_mode") in wanted
    ]


def write_case_studies(out_dir: Path, rows: list[dict[str, object]]) -> None:
    selected = sorted(
        [row for row in rows if row.get("coupling_mode") == "full_coupling_A_to_B"],
        key=lambda row: float(row.get("specific_coupling_excess", 0.0)),
        reverse=True,
    )[:12]
    lines = ["# Coupling Case Studies", "", "Top full A->B rows by specific coupling excess.", ""]
    for row in selected:
        lines.extend(
            [
                f"## {row['pair_id']} / {row['coupling_map']} / {row['probe_name']}",
                "",
                f"- phenotype: {row['phenotype_class']}",
                f"- fakeout: {row['fakeout_class']}",
                f"- deformation: {float(row['coupled_deformation_delta']):.4f}",
                f"- specific excess: {float(row['specific_coupling_excess']):.4f}",
                f"- source excess: {float(row['source_structure_excess']):.4f}",
                f"- target excess: {float(row['target_specificity_excess']):.4f}",
                f"- lag class: {row['horizon_lag_class']}",
                "",
            ]
        )
    (out_dir / "coupling_case_studies.md").write_text("\n".join(lines), encoding="utf-8")


def write_status(out_dir: Path, config: dict[str, object], started: float, rows: int, errors: int) -> None:
    status = {
        **config,
        "elapsed_seconds": time.perf_counter() - started,
        "metric_rows_written": rows,
        "errors": errors,
    }
    (out_dir / "status.json").write_text(json.dumps(jsonable(status), indent=2, sort_keys=True), encoding="utf-8")


def cleanup_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    cleaned = []
    for row in rows:
        cleaned.append({key: value for key, value in row.items() if not key.startswith("_")})
    return cleaned


def local_candidate_pool(system: LandscapeSystem, state: State) -> list[State]:
    pool = set(system.edges[state])
    for target in system.edges[state]:
        pool.update(system.edges.get(target, ()))
    if not pool:
        pool = set(system.states)
    return sorted(pool)


def incoming_neighbors(system: LandscapeSystem, state: State) -> list[State]:
    return sorted(source for source, targets in system.edges.items() if state in targets)


def select_probe(system: LandscapeSystem, index: int) -> Probe:
    probes = [
        probe for probe in generate_probes(system, sigma=3)
        if probe.probe_family
        in {
            "single_coordinate_projection",
            "pairwise_ordered_projection",
            "pairwise_modular_difference",
            "pairwise_equality_indicator",
            "triple_residue",
        }
    ]
    return probes[index % len(probes)]


def jaccard(left: dict[object, int], right: dict[object, int]) -> float:
    lset = set(left)
    rset = set(right)
    if not lset and not rset:
        return 1.0
    return len(lset & rset) / max(1, len(lset | rset))


def tv_distance(left: dict[object, int], right: dict[object, int]) -> float:
    keys = set(left) | set(right)
    ltotal = sum(left.values())
    rtotal = sum(right.values())
    if ltotal <= 0 or rtotal <= 0:
        return 0.0
    return 0.5 * sum(abs(left.get(key, 0) / ltotal - right.get(key, 0) / rtotal) for key in keys)


def lag_class(js_values: list[float], horizons: list[int] | tuple[int, ...]) -> str:
    if max(js_values, default=0.0) < 0.03:
        return "no_detectable_coupling"
    first = next((index for index, value in enumerate(js_values) if value >= 0.03), None)
    if first is None:
        return "no_detectable_coupling"
    if first <= 1:
        return "immediate_spillover"
    if horizons[first] <= 16:
        return "short_lag_coupling"
    return "delayed_coupling"


def histogram(values: list[int]) -> dict[int, int]:
    return dict(Counter(values))


def signal_hash(signal: str, salt: str) -> int:
    total = 0
    for index, char in enumerate(f"{signal}:{salt}"):
        total = (total * 131 + (index + 23) * ord(char)) % 2_147_483_647
    return total


def params_to_dict(params: RelationParams) -> dict[str, object]:
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


def params_from_dict(data: object) -> RelationParams:
    item = dict(data)  # type: ignore[arg-type]
    return RelationParams(
        parameter_set_id=str(item["parameter_set_id"]),
        coordinate_count=int(item["coordinate_count"]),
        alphabet_size=int(item["alphabet_size"]),
        neighborhood_radius=int(item["neighborhood_radius"]),
        update_footprint=int(item["update_footprint"]),
        out_degree_target=int(item["out_degree_target"]),
        constraint_density=float(item["constraint_density"]),
        constraint_strength=float(item["constraint_strength"]),
        asymmetry_strength=float(item["asymmetry_strength"]),
        reversibility_fraction=float(item["reversibility_fraction"]),
        rewire_probability=float(item["rewire_probability"]),
        roughness_strength=float(item.get("roughness_strength", 0.01)),
        constraint_arity=int(item.get("constraint_arity", 2)),
        constraint_change_weight=float(item.get("constraint_change_weight", 0.35)),
    )


def group(rows: list[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[object, ...], list[dict[str, object]]]:
    out: dict[tuple[object, ...], list[dict[str, object]]] = {}
    for row in rows:
        out.setdefault(tuple(row.get(key, "") for key in keys), []).append(row)
    return out


def mean_float(rows: list[dict[str, object]], key: str) -> float:
    return mean([float(row.get(key, 0.0) or 0.0) for row in rows])


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
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


def jsonable(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value


if __name__ == "__main__":
    main()
