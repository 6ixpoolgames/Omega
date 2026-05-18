from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import signal
import time
from datetime import datetime
from pathlib import Path

from .generators import generate_algebra
from .policies import POLICIES
from .simulation import run_condition
from .summarize import write_aggregate_csv, write_summary


FAMILIES = ("low_resolution_dense", "structured_asymmetric", "lock_in_seeded")
STOP_REQUESTED = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the VAL0-CT smoke batch.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--num-tasks", type=int, default=64)
    parser.add_argument("--num-constructors", type=int, default=2)
    parser.add_argument("--sample-size", type=int, default=256)
    parser.add_argument("--max-paths", type=int, default=512)
    parser.add_argument("--families", type=str, nargs="+", default=list(FAMILIES))
    parser.add_argument(
        "--seed-counts",
        type=str,
        default=None,
        help="Comma-separated family=count overrides, e.g. brittle_peak=150,lock_in_seeded=50",
    )
    parser.add_argument("--store-steps", action="store_true")
    parser.add_argument("--max-runtime-seconds", type=float, default=None)
    parser.add_argument("--shutdown-reserve-seconds", type=float, default=300.0)
    parser.add_argument("--checkpoint-every", type=int, default=100)
    parser.add_argument("--max-pending-multiplier", type=int, default=2)
    parser.add_argument("--max-jobs", type=int, default=None)
    parser.add_argument("--job-order", choices=["interleaved", "grouped"], default="interleaved")
    parser.add_argument("--h", type=int, nargs="+", default=[1, 2, 4])
    parser.add_argument("--H", type=int, nargs="+", default=[4, 8])
    parser.add_argument("--T", type=int, nargs="+", default=[16, 32])
    return parser.parse_args()


def _job(args: tuple[str, int, int, int, int, str, dict[str, object]]) -> dict[str, object]:
    family, seed, h, H, T, policy, config = args
    algebra = generate_algebra(
        family,
        seed=seed,
        num_tasks=config["num_tasks"],
        num_constructors=config["num_constructors"],
    )
    return run_condition(
        algebra,
        h=h,
        H=H,
        T=T,
        policy=policy,
        sample_size=config["sample_size"],
        seed=seed + h * 10_000 + H * 1_000 + T * 100,
        max_paths=config["max_paths"],
        store_steps=bool(config["store_steps"]),
    )


def _parse_seed_counts(raw: str | None, families: list[str], default: int) -> dict[str, int]:
    counts = {family: default for family in families}
    if not raw:
        return counts
    for item in raw.split(","):
        if not item.strip():
            continue
        family, value = item.split("=", 1)
        counts[family.strip()] = int(value)
    return counts


def _build_jobs(
    families: list[str],
    seed_counts: dict[str, int],
    h_values: list[int],
    H_values: list[int],
    T_values: list[int],
    config: dict[str, object],
    order: str,
) -> list[tuple[str, int, int, int, int, str, dict[str, object]]]:
    if order == "grouped":
        return [
            (family, seed, h, H, T, policy, config)
            for family in families
            for seed in range(seed_counts[family])
            for h in h_values
            for H in H_values
            for T in T_values
            for policy in POLICIES
        ]
    max_seeds = max(seed_counts.values()) if seed_counts else 0
    return [
        (family, seed, h, H, T, policy, config)
        for seed in range(max_seeds)
        for h in h_values
        for H in H_values
        for T in T_values
        for policy in POLICIES
        for family in families
        if seed < seed_counts[family]
    ]


def _request_stop(signum: int, _frame: object) -> None:
    global STOP_REQUESTED
    STOP_REQUESTED = True
    print(json.dumps({"event": "stop_requested", "signal": signum}), flush=True)


def _write_json(path: Path, data: dict[str, object]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp_path.replace(path)


def _write_status(
    out_dir: Path,
    config: dict[str, object],
    status: str,
    start: float,
    total_jobs: int,
    submitted: int,
    completed: int,
    failed: int,
    cancelled: int,
) -> None:
    elapsed = time.perf_counter() - start
    payload = {
        "status": status,
        "elapsed_seconds": elapsed,
        "total_jobs": total_jobs,
        "submitted_jobs": submitted,
        "completed_jobs": completed,
        "failed_jobs": failed,
        "cancelled_jobs": cancelled,
        "remaining_unsubmitted_jobs": max(0, total_jobs - submitted),
        "completion_fraction": completed / max(1, total_jobs),
        "config": config,
    }
    _write_json(out_dir / "status.json", payload)


def _write_partial_outputs(
    out_dir: Path,
    config: dict[str, object],
    rows: list[dict[str, object]],
    status: str,
) -> None:
    config["status"] = status
    _write_json(out_dir / "config.json", config)
    if rows:
        aggregate = write_aggregate_csv(out_dir / "aggregate.csv", rows)
        write_summary(out_dir / "summary.md", config, aggregate)
    else:
        (out_dir / "summary.md").write_text(
            "# VAL0-CT Run Summary\n\nNo completed rows were available for aggregation.\n",
            encoding="utf-8",
        )


def main() -> int:
    signal.signal(signal.SIGINT, _request_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _request_stop)
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "val0_ct" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    families = list(args.families)
    seed_counts = _parse_seed_counts(args.seed_counts, families, args.seeds)
    config = {
        "run_id": run_id,
        "families": families,
        "seed_counts": seed_counts,
        "policies": list(POLICIES),
        "seeds": args.seeds,
        "workers": args.workers,
        "num_tasks": args.num_tasks,
        "num_constructors": args.num_constructors,
        "sample_size": args.sample_size,
        "max_paths": args.max_paths,
        "store_steps": args.store_steps,
        "max_runtime_seconds": args.max_runtime_seconds,
        "shutdown_reserve_seconds": args.shutdown_reserve_seconds,
        "checkpoint_every": args.checkpoint_every,
        "max_pending_multiplier": args.max_pending_multiplier,
        "max_jobs": args.max_jobs,
        "job_order": args.job_order,
        "h": args.h,
        "H": args.H,
        "T": args.T,
        "cpu_count": os.cpu_count(),
    }
    _write_json(out_dir / "config.json", config)
    jobs = _build_jobs(families, seed_counts, args.h, args.H, args.T, config, args.job_order)
    if args.max_jobs is not None:
        jobs = jobs[: args.max_jobs]
        config["job_scope_note"] = f"truncated to first {args.max_jobs} jobs by --max-jobs"
        _write_json(out_dir / "config.json", config)
    start = time.perf_counter()
    stop_submission_at = None
    hard_stop_at = None
    if args.max_runtime_seconds is not None:
        hard_stop_at = start + args.max_runtime_seconds
        stop_submission_at = hard_stop_at - max(0.0, args.shutdown_reserve_seconds)
    status = "running"
    failed = 0
    cancelled = 0
    submitted = 0
    rows: list[dict[str, object]] = []
    results_path = out_dir / "results.jsonl"
    errors_path = out_dir / "errors.jsonl"
    max_pending = max(1, args.workers * max(1, args.max_pending_multiplier))
    job_iter = iter(jobs)
    pending: dict[concurrent.futures.Future[dict[str, object]], tuple[str, int, int, int, int, str, dict[str, object]]] = {}
    with results_path.open("w", encoding="utf-8") as handle:
        with errors_path.open("w", encoding="utf-8") as error_handle:
            executor = concurrent.futures.ProcessPoolExecutor(max_workers=args.workers)
            try:
                while pending or submitted < len(jobs):
                    now = time.perf_counter()
                    can_submit = not STOP_REQUESTED
                    if stop_submission_at is not None and now >= stop_submission_at:
                        can_submit = False
                        status = "partial_time_budget_stop"
                    while can_submit and len(pending) < max_pending and submitted < len(jobs):
                        try:
                            job = next(job_iter)
                        except StopIteration:
                            break
                        future = executor.submit(_job, job)
                        pending[future] = job
                        submitted += 1
                    if not pending:
                        break
                    timeout = 5.0
                    if hard_stop_at is not None:
                        timeout = max(0.1, min(timeout, hard_stop_at - time.perf_counter()))
                    done, _ = concurrent.futures.wait(
                        pending,
                        timeout=timeout,
                        return_when=concurrent.futures.FIRST_COMPLETED,
                    )
                    if not done:
                        if hard_stop_at is not None and time.perf_counter() >= hard_stop_at:
                            status = "partial_hard_stop"
                            break
                        if STOP_REQUESTED:
                            status = "partial_signal_stop"
                            break
                        continue
                    for future in done:
                        job = pending.pop(future)
                        try:
                            row = future.result()
                        except Exception as exc:  # noqa: BLE001 - record job-scoped failure and continue batch.
                            failed += 1
                            error_handle.write(
                                json.dumps(
                                    {
                                        "job": {
                                            "family": job[0],
                                            "seed": job[1],
                                            "h": job[2],
                                            "H": job[3],
                                            "T": job[4],
                                            "policy": job[5],
                                        },
                                        "error": repr(exc),
                                    },
                                    sort_keys=True,
                                )
                                + "\n"
                            )
                            error_handle.flush()
                            continue
                        rows.append(row)
                        handle.write(json.dumps(row, sort_keys=True) + "\n")
                        handle.flush()
                    if len(rows) and len(rows) % max(1, args.checkpoint_every) == 0:
                        _write_status(
                            out_dir,
                            config,
                            status,
                            start,
                            len(jobs),
                            submitted,
                            len(rows),
                            failed,
                            cancelled,
                        )
                        _write_partial_outputs(out_dir, config, rows, status)
                    if hard_stop_at is not None and time.perf_counter() >= hard_stop_at:
                        status = "partial_hard_stop"
                        break
                    if STOP_REQUESTED:
                        status = "partial_signal_stop"
                        break
                if pending or submitted < len(jobs):
                    status = status if status.startswith("partial") else "partial_stopped"
                    for future in pending:
                        if future.cancel():
                            cancelled += 1
                    cancelled += max(0, len(jobs) - submitted)
                elif failed:
                    status = "completed_with_errors"
                else:
                    status = "completed"
            finally:
                executor.shutdown(wait=False, cancel_futures=True)
    elapsed = time.perf_counter() - start
    config["elapsed_seconds"] = elapsed
    _write_partial_outputs(out_dir, config, rows, status)
    _write_status(out_dir, config, status, start, len(jobs), submitted, len(rows), failed, cancelled)
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "rows": len(rows),
                "elapsed_seconds": elapsed,
                "status": status,
                "submitted_jobs": submitted,
                "total_jobs": len(jobs),
                "failed_jobs": failed,
                "cancelled_jobs": cancelled,
            },
            indent=2,
        )
    )
    return 0 if status in {"completed", "completed_with_errors"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
