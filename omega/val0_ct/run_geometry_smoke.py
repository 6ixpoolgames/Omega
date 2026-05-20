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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VAL0-CT reachable-neighborhood geometry smoke.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--families",
        nargs="+",
        default=["brittle_peak", "structured_asymmetric_v2", "low_resolution_dense", "unlabeled_structural"],
    )
    parser.add_argument("--seeds", type=int, default=6)
    parser.add_argument("--num-tasks", type=int, default=64)
    parser.add_argument("--num-constructors", type=int, default=2)
    parser.add_argument("--h", type=int, nargs="+", default=[1, 2])
    parser.add_argument("--H", type=int, default=16)
    parser.add_argument("--T", type=int, default=32)
    parser.add_argument("--sample-size", type=int, default=256)
    parser.add_argument("--max-paths", type=int, default=512)
    parser.add_argument("--geometry-samples", type=int, default=32)
    parser.add_argument("--reentry-samples", type=int, default=3)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-runtime-seconds", type=int, default=900)
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
    return {
        "family": family,
        "seed": seed,
        "near_horizon": h,
        "continuation_horizon": H,
        "T": T,
        "R1_global_lhr": r1["global_lhr"],
        "R0lookahead_global_lhr": r0["global_lhr"],
        "R1_advantage": float(r1["global_lhr"]) - float(r0["global_lhr"]),
        "same_choice_rate_R1_run": r1["R1_R0lookahead_same_choice_rate"],
        "candidate_future_R0_variance_mean_R1_run": r1["candidate_future_R0_variance_mean"],
        "job_elapsed_seconds": time.perf_counter() - started,
        **sidecar,
    }


def _corr(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(ys) < 2:
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
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
    grouped: dict[tuple[str, int], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["family"]), int(row["near_horizon"])), []).append(row)
    aggregate: list[dict[str, object]] = []
    for (family, h), items in sorted(grouped.items()):
        aggregate.append(
            {
                "family": family,
                "near_horizon": h,
                "n": len(items),
                "mean_R1_advantage": mean(float(item["R1_advantage"]) for item in items),
                "mean_same_choice": mean(float(item["R1_R0lookahead_same_choice"]) for item in items),
                "mean_candidate_future_R0_variance": mean(float(item["candidate_future_R0_variance"]) for item in items),
                "mean_geometry_gap_terminal_depth": mean(float(item["geometry_gap_terminal_depth"]) for item in items),
                "mean_geometry_gap_depth_profile_d16": mean(float(item["geometry_gap_depth_profile_d16"]) for item in items),
                "mean_geometry_gap_corridor_width_d8": mean(float(item["geometry_gap_corridor_width_d8"]) for item in items),
                "mean_geometry_gap_corridor_width_d16": mean(float(item["geometry_gap_corridor_width_d16"]) for item in items),
                "mean_geometry_gap_reentry_score": mean(float(item["geometry_gap_reentry_score"]) for item in items),
                "corr_terminal_depth_gap_R1_advantage": _corr(
                    [float(item["geometry_gap_terminal_depth"]) for item in items],
                    [float(item["R1_advantage"]) for item in items],
                ),
                "corr_reentry_gap_R1_advantage": _corr(
                    [float(item["geometry_gap_reentry_score"]) for item in items],
                    [float(item["R1_advantage"]) for item in items],
                ),
            }
        )
    return aggregate


def _write_status(out_dir: Path, config: dict[str, object], rows: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    aggregate = _aggregate(rows)
    _write_csv(out_dir / "aggregate.csv", aggregate)
    status = {
        "rows_completed": len(rows),
        "errors": len(errors),
        "elapsed_seconds": time.perf_counter() - float(config["started_perf_counter"]),
        "status": config.get("status", "RUNNING"),
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(out_dir, config, aggregate, rows, errors)


def _write_summary(
    out_dir: Path,
    config: dict[str, object],
    aggregate: list[dict[str, object]],
    rows: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    lines = [
        "# VAL0-CT Reachable-Neighborhood Geometry Smoke",
        "",
        "Diagnostic-only sidecar. Policies are frozen; geometry is measured after R1 and R0-lookahead choices.",
        "",
        "## Config",
        "",
        "```json",
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        "```",
        "",
        "## Aggregate",
        "",
        "| family | h | n | mean R1 advantage | same choice | terminal gap | d16 gap | corridor d8 gap | corridor d16 gap | re-entry gap | corr(term,R1adv) | corr(reentry,R1adv) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in aggregate:
        lines.append(
            "| {family} | {h} | {n} | {adv:.3f} | {same:.3f} | {term:.3f} | {d16:.3f} | {c8:.3f} | {c16:.3f} | {re:.3f} | {ct:.3f} | {cr:.3f} |".format(
                family=row["family"],
                h=row["near_horizon"],
                n=row["n"],
                adv=float(row["mean_R1_advantage"]),
                same=float(row["mean_same_choice"]),
                term=float(row["mean_geometry_gap_terminal_depth"]),
                d16=float(row["mean_geometry_gap_depth_profile_d16"]),
                c8=float(row["mean_geometry_gap_corridor_width_d8"]),
                c16=float(row["mean_geometry_gap_corridor_width_d16"]),
                re=float(row["mean_geometry_gap_reentry_score"]),
                ct=float(row["corr_terminal_depth_gap_R1_advantage"]),
                cr=float(row["corr_reentry_gap_R1_advantage"]),
            )
        )
    lines.extend(
        [
            "",
            "## Smoke Interpretation",
            "",
            "- Minimal success: non-degenerate geometry, anchor R1 advantage preserved, dense control not spuriously separated.",
            "- Stronger success: positive anchor families show positive geometry gaps for R1-selected states.",
            "- Best smoke signal: unlabeled structural rows show geometry gaps that move with R1 advantage.",
            "- Correlations are exploratory at this sample size.",
            "",
            "## Completion",
            "",
            f"- Rows completed: {len(rows)}",
            f"- Errors: {len(errors)}",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _jobs(args: argparse.Namespace) -> list[dict[str, object]]:
    jobs: list[dict[str, object]] = []
    for family in args.families:
        for seed in range(args.seeds):
            for h in args.h:
                jobs.append(
                    {
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


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "val0_ct" / f"{run_id}_geometry_smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    config = vars(args)
    config["run_id"] = run_id
    config["out"] = str(out_dir)
    config["started_perf_counter"] = time.perf_counter()
    config["status"] = "RUNNING"
    (out_dir / "config.json").write_text(
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    jobs = _jobs(args)
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    result_path = out_dir / "results.jsonl"
    error_path = out_dir / "errors.jsonl"
    pending_jobs = list(jobs)
    futures = {}
    timed_out = False
    executor = ProcessPoolExecutor(max_workers=args.workers)
    try:
        while pending_jobs and len(futures) < args.workers:
            job = pending_jobs.pop(0)
            futures[executor.submit(_run_one, job)] = job
        while futures:
            elapsed = time.perf_counter() - config["started_perf_counter"]
            if elapsed >= args.max_runtime_seconds:
                timed_out = True
                break
            done, _ = wait(futures, timeout=min(5.0, args.max_runtime_seconds - elapsed), return_when=FIRST_COMPLETED)
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
                while pending_jobs and len(futures) < args.workers:
                    next_job = pending_jobs.pop(0)
                    futures[executor.submit(_run_one, next_job)] = next_job
            _write_status(out_dir, config, rows, errors)
    finally:
        config["status"] = "TIMED_OUT" if timed_out else "COMPLETED"
        executor.shutdown(wait=False, cancel_futures=True)
        _write_status(out_dir, config, rows, errors)
        (out_dir / "config.json").write_text(
            json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        _write_csv(out_dir / "results.csv", rows)
    print(json.dumps({"out_dir": str(out_dir), "rows": len(rows), "errors": len(errors), "status": config["status"]}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
