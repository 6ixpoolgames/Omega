from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime
from pathlib import Path
from statistics import mean

from .coupled_grammar import cross_edge_counts, generate_joint_world
from .metrics import joint_metrics, mean_row


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VAL1-MF two-field compatibility smoke.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--pairs", type=int, default=150)
    parser.add_argument("--num-tasks", type=int, default=64)
    parser.add_argument("--max-states-per-depth", type=int, default=1024)
    parser.add_argument("--rollout-samples", type=int, default=128)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-runtime-seconds", type=int, default=1800)
    return parser.parse_args()


def _run_one(job: dict[str, object]) -> dict[str, object]:
    started = time.perf_counter()
    joint = generate_joint_world(int(job["seed_pair"]), int(job["num_tasks"]))
    metrics = joint_metrics(
        joint,
        max_states_per_depth=int(job["max_states_per_depth"]),
        rollout_samples=int(job["rollout_samples"]),
        seed=int(job["seed_pair"]) + 50_003,
    )
    return {
        "seed_pair": joint.seed_pair,
        "seed_A": joint.world_A.seed,
        "seed_B": joint.world_B.seed,
        "coupling_parameter_json": json.dumps(joint.params, sort_keys=True),
        "num_tasks_A": joint.world_A.num_tasks,
        "num_tasks_B": joint.world_B.num_tasks,
        "signature_mode": "full",
        "job_elapsed_seconds": time.perf_counter() - started,
        **cross_edge_counts(joint),
        **metrics,
    }


def _jobs(args: argparse.Namespace) -> list[dict[str, object]]:
    return [
        {
            "seed_pair": seed_pair,
            "num_tasks": args.num_tasks,
            "max_states_per_depth": args.max_states_per_depth,
            "rollout_samples": args.rollout_samples,
        }
        for seed_pair in range(args.pairs)
    ]


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


def _group_summary(rows: list[dict[str, object]], key: str, out_key: str | None = None) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    return [mean_row({out_key or key: value}, items) for value, items in sorted(grouped.items())]


def _coupling_regime_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for key in ("coupling_density", "cross_effect_balance", "shared_capacity_pressure", "cross_commit_probability", "symmetry"):
        grouped: dict[str, list[dict[str, object]]] = {}
        for row in rows:
            value = json.loads(str(row["coupling_parameter_json"])).get(key, "NA")
            grouped.setdefault(str(value), []).append(row)
        for value, items in sorted(grouped.items()):
            output.append(mean_row({"parameter": key, "value": value}, items))
    return output


def _cap_hit_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["neutral_bin"]), []).append(row)
    output: list[dict[str, object]] = []
    for bin_name, items in sorted(grouped.items()):
        output.append(
            {
                "neutral_bin": bin_name,
                "n": len(items),
                "A_single_cap_hit_d16": mean(float(row["A_single_cap_hit_d16"]) for row in items),
                "B_single_cap_hit_d16": mean(float(row["B_single_cap_hit_d16"]) for row in items),
                "joint_cap_hit_d16": mean(float(row["joint_cap_hit_d16"]) for row in items),
                "A_coupled_cap_hit_d16": mean(float(row["A_coupled_cap_hit_d16"]) for row in items),
                "B_coupled_cap_hit_d16": mean(float(row["B_coupled_cap_hit_d16"]) for row in items),
            }
        )
    return output


def _write_outputs(out_dir: Path, config: dict[str, object], rows: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    aggregate = [mean_row({"scope": "all"}, rows)] if rows else []
    compatibility_bins = _group_summary(rows, "neutral_bin")
    coupling_summary = _coupling_regime_summary(rows)
    cap_hit_summary = _cap_hit_summary(rows)
    filter_summary = _group_summary(rows, "interpretive_label_optional", "interpretive_label")
    _write_csv(out_dir / "aggregate.csv", aggregate)
    _write_csv(out_dir / "compatibility_bins.csv", compatibility_bins)
    _write_csv(out_dir / "coupling_regime_summary.csv", coupling_summary)
    _write_csv(out_dir / "cap_hit_summary.csv", cap_hit_summary)
    _write_csv(out_dir / "filter_ratio_summary.csv", filter_summary)
    status = {
        "status": config.get("status", "RUNNING"),
        "rows_completed": len(rows),
        "errors": len(errors),
        "elapsed_seconds": time.perf_counter() - float(config["started_perf_counter"]),
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(out_dir, config, aggregate, compatibility_bins, cap_hit_summary, rows, errors)


def _write_summary(
    out_dir: Path,
    config: dict[str, object],
    aggregate: list[dict[str, object]],
    compatibility_bins: list[dict[str, object]],
    cap_hit_summary: list[dict[str, object]],
    rows: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    lines = [
        "# VAL1-MF Two-Field Compatibility Smoke",
        "",
        "Minimal multifield smoke. Neutral bins are primary; interpretive labels are provisional.",
        "",
        "## Config",
        "",
        "```json",
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        "```",
        "",
        "## Aggregate",
        "",
        "| scope | n | A filter | B filter | joint filter | compatibility | A div | B div | joint cap | joint terminal |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in aggregate:
        lines.append(_format_summary_row(row, "scope"))
    lines.extend(
        [
            "",
            "## Compatibility Bins",
            "",
            "| neutral bin | n | A filter | B filter | joint filter | compatibility | A div | B div | joint cap | joint terminal |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in compatibility_bins:
        lines.append(_format_summary_row(row, "neutral_bin"))
    lines.extend(
        [
            "",
            "## Cap Hits By Bin",
            "",
            "| neutral bin | n | A single cap | B single cap | joint cap | A coupled cap | B coupled cap |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in cap_hit_summary:
        lines.append(
            "| {bin} | {n} | {asingle:.3f} | {bsingle:.3f} | {joint:.3f} | {ac:.3f} | {bc:.3f} |".format(
                bin=row["neutral_bin"],
                n=row["n"],
                asingle=float(row["A_single_cap_hit_d16"]),
                bsingle=float(row["B_single_cap_hit_d16"]),
                joint=float(row["joint_cap_hit_d16"]),
                ac=float(row["A_coupled_cap_hit_d16"]),
                bc=float(row["B_coupled_cap_hit_d16"]),
            )
        )
    bins = sorted({str(row["neutral_bin"]) for row in rows})
    lines.extend(["", "## Smoke Read", "", f"- Bins observed: {', '.join(bins) if bins else 'none'}.", f"- Rows completed: {len(rows)}.", f"- Errors: {len(errors)}."])
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _format_summary_row(row: dict[str, object], label_key: str) -> str:
    return "| {label} | {n} | {a:.3f} | {b:.3f} | {j:.3f} | {c:.3f} | {ad:.3f} | {bd:.3f} | {cap:.3f} | {term:.3f} |".format(
        label=row[label_key],
        n=row["n"],
        a=float(row["mean_A_filter_ratio"]),
        b=float(row["mean_B_filter_ratio"]),
        j=float(row["mean_joint_filter_ratio"]),
        c=float(row["mean_compatibility_ratio"]),
        ad=float(row["mean_local_global_divergence_A"]),
        bd=float(row["mean_local_global_divergence_B"]),
        cap=float(row["mean_joint_cap_hit_d16"]),
        term=float(row["mean_joint_P_terminal_d16"]),
    )


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "val1_mf" / f"{run_id}_two_field_compatibility_smoke"
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
    pending = _jobs(args)
    futures = {}
    timed_out = False
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        while pending and len(futures) < args.workers:
            job = pending.pop(0)
            futures[executor.submit(_run_one, job)] = job
        while futures:
            if time.perf_counter() - float(config["started_perf_counter"]) >= args.max_runtime_seconds:
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
