from __future__ import annotations

import argparse
import csv
import json
import math
import time
from datetime import datetime
from pathlib import Path
from statistics import mean

from .brittleness import brittleness_sidecar
from .generators import generate_algebra
from .simulation import run_condition


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VAL0-CT brittleness sidecar smoke.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--families", nargs="+", default=["brittle_peak", "structured_asymmetric_v2", "low_resolution_dense"])
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--num-tasks", type=int, default=64)
    parser.add_argument("--num-constructors", type=int, default=2)
    parser.add_argument("--h", type=int, nargs="+", default=[1, 2])
    parser.add_argument("--H", type=int, default=16)
    parser.add_argument("--T", type=int, default=32)
    parser.add_argument("--sample-size", type=int, default=256)
    parser.add_argument("--max-paths", type=int, default=512)
    parser.add_argument("--brittleness-candidate-sample", type=int, default=32)
    parser.add_argument("--brittleness-stress-samples", type=int, default=4)
    return parser.parse_args()


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
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "val0_ct" / f"{run_id}_brittleness_smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    config = vars(args)
    config["run_id"] = run_id
    config["out"] = str(out_dir)
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")

    start = time.perf_counter()
    rows: list[dict[str, object]] = []
    for family in args.families:
        for seed in range(args.seeds):
            algebra = generate_algebra(family, seed, args.num_tasks, args.num_constructors)
            for h in args.h:
                r1 = run_condition(algebra, h, args.H, args.T, "R1", args.sample_size, seed, args.max_paths)
                r0 = run_condition(algebra, h, args.H, args.T, "R0_lookahead", args.sample_size, seed, args.max_paths)
                sidecar = brittleness_sidecar(
                    algebra,
                    algebra.initial_state,
                    h=h,
                    H=args.H,
                    candidate_sample_size=args.brittleness_candidate_sample,
                    stress_samples=args.brittleness_stress_samples,
                    seed=seed + h * 10_000,
                    max_paths=args.max_paths,
                )
                rows.append(
                    {
                        "family": family,
                        "seed": seed,
                        "near_horizon": h,
                        "continuation_horizon": args.H,
                        "T": args.T,
                        "R1_global_lhr": r1["global_lhr"],
                        "R0lookahead_global_lhr": r0["global_lhr"],
                        "R1_advantage": float(r1["global_lhr"]) - float(r0["global_lhr"]),
                        **sidecar,
                    }
                )
    elapsed = time.perf_counter() - start
    config["elapsed_seconds"] = elapsed
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")
    with (out_dir / "results.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    _write_csv(out_dir / "results.csv", rows)

    by_family: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_family.setdefault(str(row["family"]), []).append(row)
    aggregate: list[dict[str, object]] = []
    for family, items in sorted(by_family.items()):
        aggregate.append(
            {
                "family": family,
                "n": len(items),
                "mean_R1_advantage": mean(float(item["R1_advantage"]) for item in items),
                "mean_candidate_brittleness": mean(float(item["candidate_brittleness_mean"]) for item in items),
                "mean_chosen_brittleness_gap": mean(float(item["chosen_brittleness_gap"]) for item in items),
                "mean_R0lookahead_chosen_brittleness": mean(float(item["R0lookahead_chosen_brittleness"]) for item in items),
                "mean_R1_chosen_brittleness": mean(float(item["R1_chosen_brittleness"]) for item in items),
                "corr_brittleness_R1_advantage": _corr(
                    [float(item["candidate_brittleness_mean"]) for item in items],
                    [float(item["R1_advantage"]) for item in items],
                ),
            }
        )
    _write_csv(out_dir / "aggregate.csv", aggregate)

    lines = [
        "# VAL0-CT Brittleness Sidecar Smoke",
        "",
        "Brittleness is diagnostic only. This run does not change R1, R0-lookahead, policies, or success criteria.",
        "",
        "## Config",
        "",
        "```json",
        json.dumps(config, indent=2, sort_keys=True),
        "```",
        "",
        "## Aggregate",
        "",
        "| family | n | mean R1 advantage | mean brittleness | chosen brittleness gap | corr(brittleness,R1_advantage) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in aggregate:
        lines.append(
            "| {family} | {n} | {adv:.3f} | {brit:.3f} | {gap:.3f} | {corr:.3f} |".format(
                family=row["family"],
                n=row["n"],
                adv=float(row["mean_R1_advantage"]),
                brit=float(row["mean_candidate_brittleness"]),
                gap=float(row["mean_chosen_brittleness_gap"]),
                corr=float(row["corr_brittleness_R1_advantage"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- Positive `chosen_brittleness_gap` means R0-lookahead selected a more brittle branch than R1.",
            "- High brittleness in low-resolution dense controls would be suspicious.",
            "- Correlation is exploratory in this smoke because sample sizes are small.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out_dir": str(out_dir), "rows": len(rows), "elapsed_seconds": elapsed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
