from __future__ import annotations

import argparse
import csv
import json
import math
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime
from pathlib import Path
from statistics import mean

from .generators import generate_algebra
from .geometry import geometry_sidecar
from .simulation import run_condition


GUARDRAIL_FAMILIES = ("brittle_peak", "structured_asymmetric_v2", "low_resolution_dense")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VAL0-CT 12h unlabeled geometry battery.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--sanity-seeds", type=int, default=8)
    parser.add_argument("--unlabeled-seeds", type=int, default=1500)
    parser.add_argument("--guardrail-seeds", type=int, default=100)
    parser.add_argument("--num-tasks", type=int, default=64)
    parser.add_argument("--num-constructors", type=int, default=2)
    parser.add_argument("--h", type=int, nargs="+", default=[1, 2])
    parser.add_argument("--H", type=int, default=16)
    parser.add_argument("--T", type=int, default=32)
    parser.add_argument("--sample-size", type=int, default=256)
    parser.add_argument("--max-paths", type=int, default=512)
    parser.add_argument("--geometry-samples", type=int, default=32)
    parser.add_argument("--reentry-samples", type=int, default=0)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-runtime-seconds", type=int, default=43_200)
    parser.add_argument("--checkpoint-rows", type=int, default=50)
    return parser.parse_args()


def _run_one(job: dict[str, object]) -> dict[str, object]:
    family = str(job["family"])
    seed = int(job["seed"])
    h = int(job["h"])
    H = int(job["H"])
    T = int(job["T"])
    sample_size = int(job["sample_size"])
    max_paths = int(job["max_paths"])
    algebra = generate_algebra(
        family,
        seed,
        num_tasks=int(job["num_tasks"]),
        num_constructors=int(job["num_constructors"]),
    )
    started = time.perf_counter()
    r1 = run_condition(algebra, h, H, T, "R1", sample_size, seed, max_paths)
    r0 = run_condition(algebra, h, H, T, "R0_lookahead", sample_size, seed, max_paths)
    sidecar = geometry_sidecar(
        algebra,
        algebra.initial_state,
        h=h,
        H=H,
        seed=seed,
        sample_size=sample_size,
        max_paths=max_paths,
        geometry_samples=int(job["geometry_samples"]),
        reentry_samples=int(job["reentry_samples"]),
    )
    r1_advantage = float(r1["global_lhr"]) - float(r0["global_lhr"])
    return {
        "phase": job["phase"],
        "family": family,
        "seed": seed,
        "near_horizon": h,
        "continuation_horizon": H,
        "T": T,
        "R1_global_lhr": r1["global_lhr"],
        "R0lookahead_global_lhr": r0["global_lhr"],
        "R1_advantage": r1_advantage,
        "R1_win": int(r1_advantage > 0.0),
        "same_choice_rate_R1_run": r1["R1_R0lookahead_same_choice_rate"],
        "candidate_future_R0_variance_mean_R1_run": r1["candidate_future_R0_variance_mean"],
        "job_elapsed_seconds": time.perf_counter() - started,
        **sidecar,
    }


def _jobs_for_phase(args: argparse.Namespace, phase: str) -> list[dict[str, object]]:
    if phase == "sanity":
        family_seed_counts = {
            "unlabeled_structural": args.sanity_seeds,
            "brittle_peak": args.sanity_seeds,
            "low_resolution_dense": args.sanity_seeds,
        }
    elif phase == "unlabeled_main":
        family_seed_counts = {"unlabeled_structural": args.unlabeled_seeds}
    elif phase == "guardrails":
        family_seed_counts = {family: args.guardrail_seeds for family in GUARDRAIL_FAMILIES}
    else:
        raise ValueError(f"unknown phase: {phase}")

    jobs: list[dict[str, object]] = []
    for seed in range(max(family_seed_counts.values(), default=0)):
        for h in args.h:
            for family, count in family_seed_counts.items():
                if seed >= count:
                    continue
                jobs.append(
                    {
                        "phase": phase,
                        "family": family,
                        "seed": seed,
                        "h": h,
                        "H": args.H,
                        "T": args.T,
                        "sample_size": args.sample_size,
                        "max_paths": args.max_paths,
                        "num_tasks": args.num_tasks,
                        "num_constructors": args.num_constructors,
                        "geometry_samples": args.geometry_samples,
                        "reentry_samples": args.reentry_samples,
                    }
                )
    return jobs


def _corr(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(ys) < 2:
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0.0 or den_y == 0.0:
        return 0.0
    return num / (den_x * den_y)


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


def _aggregate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, int], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["phase"]), str(row["family"]), int(row["near_horizon"])), []).append(row)
    aggregate: list[dict[str, object]] = []
    for (phase, family, h), items in sorted(grouped.items()):
        aggregate.append(_summary_row(items, {"phase": phase, "family": family, "near_horizon": h}))
    return aggregate


def _summary_row(items: list[dict[str, object]], labels: dict[str, object]) -> dict[str, object]:
    return {
        **labels,
        "n": len(items),
        "mean_R1_advantage": mean(float(item["R1_advantage"]) for item in items),
        "R1_win_rate": mean(float(item["R1_win"]) for item in items),
        "mean_R1_global_lhr": mean(float(item["R1_global_lhr"]) for item in items),
        "mean_R0lookahead_global_lhr": mean(float(item["R0lookahead_global_lhr"]) for item in items),
        "mean_same_choice": mean(float(item["R1_R0lookahead_same_choice"]) for item in items),
        "mean_candidate_future_R0_variance": mean(float(item["candidate_future_R0_variance"]) for item in items),
        "mean_corridor_d8_gap": mean(float(item["geometry_gap_corridor_width_d8"]) for item in items),
        "mean_corridor_d16_gap": mean(float(item["geometry_gap_corridor_width_d16"]) for item in items),
        "mean_depth_profile_d16_gap": mean(float(item["geometry_gap_depth_profile_d16"]) for item in items),
        "mean_reentry_gap": mean(float(item["geometry_gap_reentry_score"]) for item in items),
    }


def _posthoc_rows(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    unlabeled = [row for row in rows if row["family"] == "unlabeled_structural"]
    bin_rows: list[dict[str, object]] = []
    interaction_rows: list[dict[str, object]] = []
    scopes: list[tuple[str, list[dict[str, object]]]] = [("combined", unlabeled)]
    for h in sorted({int(row["near_horizon"]) for row in unlabeled}):
        scopes.append((f"h={h}", [row for row in unlabeled if int(row["near_horizon"]) == h]))

    for scope, items in scopes:
        for variable in (
            "geometry_gap_corridor_width_d8",
            "candidate_future_R0_variance",
            "geometry_gap_depth_profile_d16",
        ):
            for label, bin_items in _quintile_bins(items, variable):
                if bin_items:
                    bin_rows.append(_summary_row(bin_items, {"scope": scope, "bin_variable": variable, "bin_label": label}))
        for label, bin_items in _same_choice_bins(items):
            if bin_items:
                bin_rows.append(_summary_row(bin_items, {"scope": scope, "bin_variable": "same_choice", "bin_label": label}))

        corridor_bins = _assign_quintiles(items, "geometry_gap_corridor_width_d8")
        variance_bins = _assign_quintiles(items, "candidate_future_R0_variance")
        cells: dict[tuple[int, int], list[dict[str, object]]] = {}
        for item in items:
            key = (corridor_bins.get(id(item), 0), variance_bins.get(id(item), 0))
            if key[0] and key[1]:
                cells.setdefault(key, []).append(item)
        for (corridor_q, variance_q), cell_items in sorted(cells.items()):
            interaction_rows.append(
                _summary_row(
                    cell_items,
                    {
                        "scope": scope,
                        "corridor_d8_quintile": corridor_q,
                        "candidate_variance_quintile": variance_q,
                    },
                )
            )
    return bin_rows, interaction_rows


def _quintile_bins(rows: list[dict[str, object]], variable: str) -> list[tuple[str, list[dict[str, object]]]]:
    assignments = _assign_quintiles(rows, variable)
    bins: list[tuple[str, list[dict[str, object]]]] = []
    for quintile in range(1, 6):
        bins.append((f"q{quintile}", [row for row in rows if assignments.get(id(row)) == quintile]))
    return bins


def _assign_quintiles(rows: list[dict[str, object]], variable: str) -> dict[int, int]:
    sorted_rows = sorted(rows, key=lambda row: (float(row[variable]), int(row["seed"]), int(row["near_horizon"])))
    n = len(sorted_rows)
    if n == 0:
        return {}
    return {id(row): min(5, int(index * 5 / n) + 1) for index, row in enumerate(sorted_rows)}


def _same_choice_bins(rows: list[dict[str, object]]) -> list[tuple[str, list[dict[str, object]]]]:
    same = [row for row in rows if float(row["R1_R0lookahead_same_choice"]) >= 0.5]
    different = [row for row in rows if float(row["R1_R0lookahead_same_choice"]) < 0.5]
    return [("same_choice", same), ("different_choice", different)]


def _write_checkpoint(
    out_dir: Path,
    config: dict[str, object],
    rows: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    aggregate = _aggregate(rows)
    bin_rows, interaction_rows = _posthoc_rows(rows)
    _write_csv(out_dir / "aggregate.csv", aggregate)
    _write_csv(out_dir / "unlabeled_geometry_bins.csv", bin_rows)
    _write_csv(out_dir / "unlabeled_corridor_variance_interaction.csv", interaction_rows)
    elapsed = time.perf_counter() - float(config["started_perf_counter"])
    status = {
        "status": config.get("status", "RUNNING"),
        "phase": config.get("phase", "unknown"),
        "rows_completed": len(rows),
        "errors": len(errors),
        "elapsed_seconds": elapsed,
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(out_dir, config, aggregate, bin_rows, interaction_rows, rows, errors)


def _write_summary(
    out_dir: Path,
    config: dict[str, object],
    aggregate: list[dict[str, object]],
    bin_rows: list[dict[str, object]],
    interaction_rows: list[dict[str, object]],
    rows: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    lines = [
        "# VAL0-CT 12h Unlabeled Geometry Battery",
        "",
        "Diagnostic-only battery. Policies are frozen; geometry is measured after R1 and R0-lookahead choices.",
        "",
        "## Config",
        "",
        "```json",
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        "```",
        "",
        "## Aggregate",
        "",
        "| phase | family | h | n | mean R1 advantage | R1 win rate | R1 LHR | R0-lookahead LHR | same choice | corridor d8 gap | variance | depth d16 gap |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in aggregate:
        lines.append(
            "| {phase} | {family} | {h} | {n} | {adv:.3f} | {win:.3f} | {r1:.3f} | {r0:.3f} | {same:.3f} | {c8:.3f} | {var:.3f} | {d16:.3f} |".format(
                phase=row["phase"],
                family=row["family"],
                h=row["near_horizon"],
                n=row["n"],
                adv=float(row["mean_R1_advantage"]),
                win=float(row["R1_win_rate"]),
                r1=float(row["mean_R1_global_lhr"]),
                r0=float(row["mean_R0lookahead_global_lhr"]),
                same=float(row["mean_same_choice"]),
                c8=float(row["mean_corridor_d8_gap"]),
                var=float(row["mean_candidate_future_R0_variance"]),
                d16=float(row["mean_depth_profile_d16_gap"]),
            )
        )

    top_lines = _top_unlabeled_lines(bin_rows, interaction_rows)
    lines.extend(
        [
            "",
            "## Unlabeled Highlights",
            "",
            *top_lines,
            "",
            "## Completion",
            "",
            f"- Rows completed: {len(rows)}",
            f"- Errors: {len(errors)}",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _top_unlabeled_lines(bin_rows: list[dict[str, object]], interaction_rows: list[dict[str, object]]) -> list[str]:
    lines: list[str] = []
    for variable in ("geometry_gap_corridor_width_d8", "candidate_future_R0_variance", "geometry_gap_depth_profile_d16"):
        combined = [row for row in bin_rows if row["scope"] == "combined" and row["bin_variable"] == variable]
        if combined:
            bottom = next((row for row in combined if row["bin_label"] == "q1"), None)
            top = next((row for row in combined if row["bin_label"] == "q5"), None)
            if bottom and top:
                lines.append(
                    "- `{var}` q1 vs q5: mean R1 advantage {lo:.3f} -> {hi:.3f}; win rate {lo_win:.3f} -> {hi_win:.3f}.".format(
                        var=variable,
                        lo=float(bottom["mean_R1_advantage"]),
                        hi=float(top["mean_R1_advantage"]),
                        lo_win=float(bottom["R1_win_rate"]),
                        hi_win=float(top["R1_win_rate"]),
                    )
                )
    if interaction_rows:
        best = max(interaction_rows, key=lambda row: (float(row["mean_R1_advantage"]), float(row["R1_win_rate"])))
        lines.append(
            "- Best corridor x variance cell: scope {scope}, corridor q{cq}, variance q{vq}, n={n}, mean R1 advantage {adv:.3f}, win rate {win:.3f}.".format(
                scope=best["scope"],
                cq=best["corridor_d8_quintile"],
                vq=best["candidate_variance_quintile"],
                n=best["n"],
                adv=float(best["mean_R1_advantage"]),
                win=float(best["R1_win_rate"]),
            )
        )
    if not lines:
        lines.append("- Waiting for enough unlabeled rows to compute bins.")
    return lines


def _run_phase(
    phase: str,
    jobs: list[dict[str, object]],
    args: argparse.Namespace,
    out_dir: Path,
    config: dict[str, object],
    rows: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> bool:
    config["phase"] = phase
    pending_jobs = list(jobs)
    futures = {}
    completed_since_checkpoint = 0
    result_path = out_dir / "results.jsonl"
    error_path = out_dir / "errors.jsonl"
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        while pending_jobs and len(futures) < args.workers:
            job = pending_jobs.pop(0)
            futures[executor.submit(_run_one, job)] = job
        timed_out = False
        while futures:
            elapsed = time.perf_counter() - float(config["started_perf_counter"])
            if elapsed >= args.max_runtime_seconds:
                timed_out = True
                pending_jobs = []
            wait_timeout = 5.0 if timed_out else min(5.0, args.max_runtime_seconds - elapsed)
            done, _ = wait(futures, timeout=wait_timeout, return_when=FIRST_COMPLETED)
            if not done:
                continue
            for future in done:
                job = futures.pop(future)
                try:
                    row = future.result()
                    rows.append(row)
                    completed_since_checkpoint += 1
                    with result_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(row, sort_keys=True) + "\n")
                except Exception as exc:  # noqa: BLE001
                    error = {"job": job, "error": repr(exc)}
                    errors.append(error)
                    completed_since_checkpoint += 1
                    with error_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(error, sort_keys=True) + "\n")
                while not timed_out and pending_jobs and len(futures) < args.workers:
                    next_job = pending_jobs.pop(0)
                    futures[executor.submit(_run_one, next_job)] = next_job
            if completed_since_checkpoint >= args.checkpoint_rows:
                _write_checkpoint(out_dir, config, rows, errors)
                completed_since_checkpoint = 0
    _write_checkpoint(out_dir, config, rows, errors)
    return not timed_out


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "val0_ct" / f"{run_id}_unlabeled_geometry_battery"
    out_dir.mkdir(parents=True, exist_ok=True)
    config = vars(args)
    config["run_id"] = run_id
    config["out"] = str(out_dir)
    config["started_perf_counter"] = time.perf_counter()
    config["status"] = "RUNNING"
    config["phase"] = "initializing"
    (out_dir / "config.json").write_text(
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    completed = True
    for phase in ("sanity", "unlabeled_main", "guardrails"):
        if not _run_phase(phase, _jobs_for_phase(args, phase), args, out_dir, config, rows, errors):
            completed = False
            break
    config["status"] = "COMPLETED" if completed else "TIMED_OUT"
    _write_checkpoint(out_dir, config, rows, errors)
    _write_csv(out_dir / "results.csv", rows)
    (out_dir / "config.json").write_text(
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps({"out_dir": str(out_dir), "rows": len(rows), "errors": len(errors), "status": config["status"]}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
