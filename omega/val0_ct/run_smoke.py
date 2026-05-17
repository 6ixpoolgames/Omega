from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import time
from datetime import datetime
from pathlib import Path

from .generators import generate_algebra
from .policies import POLICIES
from .simulation import run_condition
from .summarize import write_aggregate_csv, write_jsonl, write_summary


FAMILIES = ("low_resolution_dense", "structured_asymmetric", "lock_in_seeded")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the VAL0-CT smoke batch.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--num-tasks", type=int, default=64)
    parser.add_argument("--num-constructors", type=int, default=2)
    parser.add_argument("--sample-size", type=int, default=256)
    parser.add_argument("--max-paths", type=int, default=512)
    parser.add_argument("--h", type=int, nargs="+", default=[1, 2, 4])
    parser.add_argument("--H", type=int, nargs="+", default=[4, 8])
    parser.add_argument("--T", type=int, nargs="+", default=[16, 32])
    return parser.parse_args()


def _job(args: tuple[str, int, int, int, int, str, dict[str, int]]) -> dict[str, object]:
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
    )


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "val0_ct" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "run_id": run_id,
        "families": list(FAMILIES),
        "policies": list(POLICIES),
        "seeds": args.seeds,
        "workers": args.workers,
        "num_tasks": args.num_tasks,
        "num_constructors": args.num_constructors,
        "sample_size": args.sample_size,
        "max_paths": args.max_paths,
        "h": args.h,
        "H": args.H,
        "T": args.T,
        "cpu_count": os.cpu_count(),
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")
    jobs = [
        (family, seed, h, H, T, policy, config)
        for family in FAMILIES
        for seed in range(args.seeds)
        for h in args.h
        for H in args.H
        for T in args.T
        for policy in POLICIES
    ]
    start = time.perf_counter()
    rows: list[dict[str, object]] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
        for row in executor.map(_job, jobs, chunksize=4):
            rows.append(row)
    elapsed = time.perf_counter() - start
    config["elapsed_seconds"] = elapsed
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")
    write_jsonl(out_dir / "results.jsonl", rows)
    aggregate = write_aggregate_csv(out_dir / "aggregate.csv", rows)
    write_summary(out_dir / "summary.md", config, aggregate)
    print(json.dumps({"out_dir": str(out_dir), "rows": len(rows), "elapsed_seconds": elapsed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
