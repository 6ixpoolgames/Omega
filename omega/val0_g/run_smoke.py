from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime
from pathlib import Path
from statistics import mean

from .grammar import generate_world
from .metrics import geometry_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VAL0-G neutral grammar geometry smoke.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--neutral-seeds", type=int, default=50)
    parser.add_argument("--guardrail-seeds", type=int, default=12)
    parser.add_argument("--num-tasks", type=int, default=64)
    parser.add_argument("--max-states-per-depth", type=int, default=512)
    parser.add_argument("--rollout-samples", type=int, default=128)
    parser.add_argument("--cut-samples", type=int, default=4)
    parser.add_argument("--signature-modes", nargs="+", default=["coarse", "full"])
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-runtime-seconds", type=int, default=1800)
    return parser.parse_args()


def _jobs(args: argparse.Namespace) -> list[dict[str, object]]:
    jobs: list[dict[str, object]] = []
    for seed in range(args.neutral_seeds):
        for signature_mode in args.signature_modes:
            jobs.append({"family": "neutral_grammar_v1", "seed": seed, "signature_mode": signature_mode})
    for family in ("low_resolution_dense", "brittle_peak"):
        for seed in range(args.guardrail_seeds):
            for signature_mode in args.signature_modes:
                jobs.append({"family": family, "seed": seed, "signature_mode": signature_mode})
    for job in jobs:
        job.update(
            {
                "num_tasks": args.num_tasks,
                "max_states_per_depth": args.max_states_per_depth,
                "rollout_samples": args.rollout_samples,
                "cut_samples": args.cut_samples,
            }
        )
    return jobs


def _run_one(job: dict[str, object]) -> dict[str, object]:
    started = time.perf_counter()
    world = generate_world(str(job["family"]), int(job["seed"]), int(job["num_tasks"]))
    metrics = geometry_metrics(
        world,
        max_states_per_depth=int(job["max_states_per_depth"]),
        rollout_samples=int(job["rollout_samples"]),
        cut_samples=int(job["cut_samples"]),
        seed=int(job["seed"]) + 100_003,
        signature_mode=str(job["signature_mode"]),
    )
    enable_edges = sum(len(task.enables) for task in world.tasks)
    obstruct_edges = sum(len(task.obstructs) for task in world.tasks)
    restore_edges = sum(len(task.restores) for task in world.tasks)
    decay_edges = sum(len(task.decays) for task in world.tasks)
    commit_edges = sum(len(task.commits) for task in world.tasks)
    return {
        "family": world.family,
        "seed": world.seed,
        "signature_mode": job["signature_mode"],
        "num_tasks": world.num_tasks,
        "parameter_regime_json": json.dumps(world.params, sort_keys=True),
        "initial_enabled_count": len(world.initial_state.enabled),
        "initial_capacity": world.initial_state.capacity,
        "enable_edges": enable_edges,
        "obstruct_edges": obstruct_edges,
        "restore_edges": restore_edges,
        "decay_edges": decay_edges,
        "commit_edges": commit_edges,
        "job_elapsed_seconds": time.perf_counter() - started,
        **metrics,
    }


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _summarize(rows: list[dict[str, object]], key: str) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    return [_summary_row({key: value}, items) for value, items in sorted(grouped.items())]


def _summary_row(labels: dict[str, object], items: list[dict[str, object]]) -> dict[str, object]:
    return {
        **labels,
        "n": len(items),
        "mean_survival_auc": mean(float(row["survival_auc"]) for row in items),
        "mean_survival_slope": mean(float(row["survival_slope"]) for row in items),
        "mean_descendant_mass_d16": mean(float(row["descendant_mass_d16"]) for row in items),
        "mean_descendant_mass_d32": mean(float(row["descendant_mass_d32"]) for row in items),
        "mean_P_terminal_d16": mean(float(row["P_terminal_d16"]) for row in items),
        "mean_P_terminal_d32": mean(float(row["P_terminal_d32"]) for row in items),
        "mean_cut_sensitivity_k1": mean(float(row["cut_sensitivity_k1"]) for row in items),
        "mean_initial_cut_sensitivity_k1": mean(float(row["initial_cut_sensitivity_k1"]) for row in items),
        "mean_downstream_cut_sensitivity_k1": mean(float(row["downstream_cut_sensitivity_k1"]) for row in items),
        "mean_branching_B8": mean(float(row["branching_B8"]) for row in items),
        "mean_cap_hit_d16": mean(float(row["cap_hit_d16"]) for row in items),
        "mean_cap_hit_d32": mean(float(row["cap_hit_d32"]) for row in items),
    }


def _parameter_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    neutral = [row for row in rows if row["family"] == "neutral_grammar_v1" and row["signature_mode"] == "full"]
    output: list[dict[str, object]] = []
    for param in (
        "density_regime",
        "obstruction_regime",
        "restore_regime",
        "commit_regime",
        "decay_regime",
        "substitute_regime",
        "capacity_regime",
    ):
        grouped: dict[str, list[dict[str, object]]] = {}
        for row in neutral:
            value = json.loads(str(row["parameter_regime_json"])).get(param, "NA")
            grouped.setdefault(str(value), []).append(row)
        for value, items in sorted(grouped.items()):
            output.append(_summary_row({"parameter": param, "value": value}, items))
    return output


def _cap_hit_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["family"]), str(row["posthoc_bin_neutral"])), []).append(row)
    output: list[dict[str, object]] = []
    for (family, neutral_bin), items in sorted(grouped.items()):
        output.append(
            {
                "family": family,
                "posthoc_bin_neutral": neutral_bin,
                "n": len(items),
                "cap_hit_rate_d1": mean(float(row["cap_hit_d1"]) for row in items),
                "cap_hit_rate_d2": mean(float(row["cap_hit_d2"]) for row in items),
                "cap_hit_rate_d4": mean(float(row["cap_hit_d4"]) for row in items),
                "cap_hit_rate_d8": mean(float(row["cap_hit_d8"]) for row in items),
                "cap_hit_rate_d16": mean(float(row["cap_hit_d16"]) for row in items),
                "cap_hit_rate_d32": mean(float(row["cap_hit_d32"]) for row in items),
            }
        )
    return output


def _cut_sensitivity_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["family"]), str(row["posthoc_bin_neutral"])), []).append(row)
    output: list[dict[str, object]] = []
    for (family, neutral_bin), items in sorted(grouped.items()):
        output.append(
            {
                "family": family,
                "posthoc_bin_neutral": neutral_bin,
                "n": len(items),
                "mean_initial_cut_sensitivity_k1": mean(float(row["initial_cut_sensitivity_k1"]) for row in items),
                "mean_downstream_cut_sensitivity_k1": mean(float(row["downstream_cut_sensitivity_k1"]) for row in items),
                "mean_cut_delta_downstream_minus_initial": mean(
                    float(row["downstream_cut_sensitivity_k1"]) - float(row["initial_cut_sensitivity_k1"])
                    for row in items
                ),
            }
        )
    return output


def _signature_comparison(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    pairs: dict[tuple[str, int], dict[str, dict[str, object]]] = {}
    for row in rows:
        pairs.setdefault((str(row["family"]), int(row["seed"])), {})[str(row["signature_mode"])] = row
    comparisons: list[dict[str, object]] = []
    for (family, seed), modes in sorted(pairs.items()):
        coarse = modes.get("coarse")
        full = modes.get("full")
        if not coarse or not full:
            continue
        full_mass = max(1.0, float(full["descendant_mass_d16"]))
        full_auc = max(1.0, abs(float(full["survival_auc"])))
        full_cut = max(1.0, abs(float(full["downstream_cut_sensitivity_k1"])))
        comparisons.append(
            {
                "family": family,
                "seed": seed,
                "same_posthoc_class": int(coarse["posthoc_class"] == full["posthoc_class"]),
                "same_neutral_bin": int(coarse["posthoc_bin_neutral"] == full["posthoc_bin_neutral"]),
                "coarse_posthoc_class": coarse["posthoc_class"],
                "full_posthoc_class": full["posthoc_class"],
                "coarse_neutral_bin": coarse["posthoc_bin_neutral"],
                "full_neutral_bin": full["posthoc_bin_neutral"],
                "relative_descendant_mass_d16_difference": (float(coarse["descendant_mass_d16"]) - float(full["descendant_mass_d16"])) / full_mass,
                "relative_survival_auc_difference": (float(coarse["survival_auc"]) - float(full["survival_auc"])) / full_auc,
                "relative_downstream_cut_difference": (float(coarse["downstream_cut_sensitivity_k1"]) - float(full["downstream_cut_sensitivity_k1"])) / full_cut,
            }
        )
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in comparisons:
        grouped.setdefault(str(row["family"]), []).append(row)
    summary_rows: list[dict[str, object]] = []
    for family, items in sorted(grouped.items()):
        summary_rows.append(
            {
                "family": family,
                "seed": "ALL",
                "same_posthoc_class": mean(float(row["same_posthoc_class"]) for row in items),
                "same_neutral_bin": mean(float(row["same_neutral_bin"]) for row in items),
                "coarse_posthoc_class": "SUMMARY",
                "full_posthoc_class": "SUMMARY",
                "coarse_neutral_bin": "SUMMARY",
                "full_neutral_bin": "SUMMARY",
                "relative_descendant_mass_d16_difference": mean(float(row["relative_descendant_mass_d16_difference"]) for row in items),
                "relative_survival_auc_difference": mean(float(row["relative_survival_auc_difference"]) for row in items),
                "relative_downstream_cut_difference": mean(float(row["relative_downstream_cut_difference"]) for row in items),
            }
        )
    return summary_rows + comparisons


def _write_outputs(out_dir: Path, config: dict[str, object], rows: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    aggregate = _summarize(rows, "family")
    class_bins = _summarize(rows, "posthoc_class")
    neutral_bins = _summarize(rows, "posthoc_bin_neutral")
    param_summary = _parameter_summary(rows)
    cap_hit_summary = _cap_hit_summary(rows)
    cut_summary = _cut_sensitivity_summary(rows)
    signature_comparison = _signature_comparison(rows)
    _write_csv(out_dir / "aggregate.csv", aggregate)
    _write_csv(out_dir / "geometry_class_bins.csv", class_bins)
    _write_csv(out_dir / "neutral_bin_summary.csv", neutral_bins)
    _write_csv(out_dir / "parameter_regime_summary.csv", param_summary)
    _write_csv(out_dir / "cap_hit_summary.csv", cap_hit_summary)
    _write_csv(out_dir / "cut_sensitivity_summary.csv", cut_summary)
    _write_csv(out_dir / "signature_comparison.csv", signature_comparison)
    status = {
        "status": config.get("status", "RUNNING"),
        "rows_completed": len(rows),
        "errors": len(errors),
        "elapsed_seconds": time.perf_counter() - float(config["started_perf_counter"]),
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(out_dir, config, aggregate, class_bins, neutral_bins, signature_comparison, rows, errors)


def _write_summary(
    out_dir: Path,
    config: dict[str, object],
    aggregate: list[dict[str, object]],
    class_bins: list[dict[str, object]],
    neutral_bins: list[dict[str, object]],
    signature_comparison: list[dict[str, object]],
    rows: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    lines = [
        "# VAL0-G Neutral Grammar Geometry Smoke",
        "",
        "Geometry-first smoke. This run does not test full Omega and does not tune R1.",
        "",
        "## Config",
        "",
        "```json",
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Aggregate",
        "",
        "| family | n | survival AUC | mass d16 | mass d32 | P terminal d16 | P terminal d32 | initial cut | downstream cut | cap d16 | cap d32 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in aggregate:
        lines.append(
            "| {family} | {n} | {auc:.3f} | {mass16:.3f} | {mass32:.3f} | {term16:.3f} | {term32:.3f} | {icut:.3f} | {dcut:.3f} | {cap16:.3f} | {cap32:.3f} |".format(
                family=row["family"],
                n=row["n"],
                auc=float(row["mean_survival_auc"]),
                mass16=float(row["mean_descendant_mass_d16"]),
                mass32=float(row["mean_descendant_mass_d32"]),
                term16=float(row["mean_P_terminal_d16"]),
                term32=float(row["mean_P_terminal_d32"]),
                icut=float(row["mean_initial_cut_sensitivity_k1"]),
                dcut=float(row["mean_downstream_cut_sensitivity_k1"]),
                cap16=float(row["mean_cap_hit_d16"]),
                cap32=float(row["mean_cap_hit_d32"]),
            )
        )
    lines.extend(["", "## Neutral Bins", "", "| neutral bin | n | survival AUC | mass d16 | P terminal d16 | downstream cut | cap d16 |", "|---|---:|---:|---:|---:|---:|---:|"])
    for row in neutral_bins:
        lines.append(
            "| {bin} | {n} | {auc:.3f} | {mass:.3f} | {term:.3f} | {cut:.3f} | {cap:.3f} |".format(
                bin=row["posthoc_bin_neutral"],
                n=row["n"],
                auc=float(row["mean_survival_auc"]),
                mass=float(row["mean_descendant_mass_d16"]),
                term=float(row["mean_P_terminal_d16"]),
                cut=float(row["mean_downstream_cut_sensitivity_k1"]),
                cap=float(row["mean_cap_hit_d16"]),
            )
        )
    lines.extend(["", "## Post-Hoc Geometry Classes", "", "| class | n | survival AUC | mass d16 | P terminal d16 | cut k1 |", "|---|---:|---:|---:|---:|---:|"])
    for row in class_bins:
        lines.append(
            "| {cls} | {n} | {auc:.3f} | {mass:.3f} | {term:.3f} | {cut:.3f} |".format(
                cls=row["posthoc_class"],
                n=row["n"],
                auc=float(row["mean_survival_auc"]),
                mass=float(row["mean_descendant_mass_d16"]),
                term=float(row["mean_P_terminal_d16"]),
                cut=float(row["mean_cut_sensitivity_k1"]),
            )
        )
    neutral_classes = sorted({str(row["posthoc_class"]) for row in rows if row["family"] == "neutral_grammar_v1"})
    signature_summary = [row for row in signature_comparison if row["seed"] == "ALL"]
    lines.extend(
        [
            "",
            "## Signature Agreement",
            "",
            "| family | same class | same neutral bin | rel mass d16 diff | rel survival AUC diff | rel downstream cut diff |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in signature_summary:
        lines.append(
            "| {family} | {cls:.3f} | {bin:.3f} | {mass:.3f} | {auc:.3f} | {cut:.3f} |".format(
                family=row["family"],
                cls=float(row["same_posthoc_class"]),
                bin=float(row["same_neutral_bin"]),
                mass=float(row["relative_descendant_mass_d16_difference"]),
                auc=float(row["relative_survival_auc_difference"]),
                cut=float(row["relative_downstream_cut_difference"]),
            )
        )
    lines.extend(
        [
            "",
            "## Smoke Read",
            "",
            f"- Neutral classes observed: {', '.join(neutral_classes) if neutral_classes else 'none yet'}.",
            f"- Rows completed: {len(rows)}.",
            f"- Errors: {len(errors)}.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "val0_g" / f"{run_id}_neutral_grammar_smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    config = vars(args)
    config["run_id"] = run_id
    config["out"] = str(out_dir)
    config["started_perf_counter"] = time.perf_counter()
    config["status"] = "RUNNING"
    (out_dir / "config.json").write_text(json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True), encoding="utf-8")
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    result_path = out_dir / "results.jsonl"
    error_path = out_dir / "errors.jsonl"
    jobs = _jobs(args)
    pending = list(jobs)
    futures = {}
    timed_out = False
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        while pending and len(futures) < args.workers:
            job = pending.pop(0)
            futures[executor.submit(_run_one, job)] = job
        while futures:
            elapsed = time.perf_counter() - float(config["started_perf_counter"])
            if elapsed >= args.max_runtime_seconds:
                timed_out = True
                pending = []
            done, _ = wait(futures, timeout=5.0, return_when=FIRST_COMPLETED)
            if not done:
                continue
            for future in done:
                job = futures.pop(future)
                try:
                    row = future.result()
                    rows.append(row)
                    with result_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(row, sort_keys=True) + "\n")
                except Exception as exc:  # noqa: BLE001
                    error = {"job": job, "error": repr(exc)}
                    errors.append(error)
                    with error_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(error, sort_keys=True) + "\n")
                while not timed_out and pending and len(futures) < args.workers:
                    next_job = pending.pop(0)
                    futures[executor.submit(_run_one, next_job)] = next_job
            _write_outputs(out_dir, config, rows, errors)
    config["status"] = "TIMED_OUT" if timed_out else "COMPLETED"
    _write_csv(out_dir / "results.csv", rows)
    _write_outputs(out_dir, config, rows, errors)
    (out_dir / "config.json").write_text(json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"out_dir": str(out_dir), "rows": len(rows), "errors": len(errors), "status": config["status"]}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
