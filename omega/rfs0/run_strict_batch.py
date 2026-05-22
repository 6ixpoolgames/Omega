from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime
from pathlib import Path
from statistics import mean

from .exact import capture_basin, contraction_metrics, filter_sets, recovery_metrics, shortest_capture_distances, viability_kernel
from .substrate import CONTROLS, REGIMES, generate_system

HORIZONS = (4, 8, 16)
RECOVERY_HORIZONS = (2, 4, 8)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS0 strict reachable-futures batch.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seeds-per-regime", type=int, default=25)
    parser.add_argument("--regimes", type=str, default=",".join(REGIMES))
    parser.add_argument("--controls", type=str, default="structured,dense_permissive_control,dead_control,random_edge_control,shuffled_admissibility_control,no_perturbation_control")
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-runtime-seconds", type=int, default=1800)
    parser.add_argument("--checkpoint-every", type=int, default=1)
    return parser.parse_args()


def _run_one(job: dict[str, object]) -> dict[str, object]:
    started = time.perf_counter()
    system = generate_system(int(job["seed"]), str(job["regime"]), str(job["control_type"]))
    filters = filter_sets(system)
    viab = {name: {h: viability_kernel(system, states, h) for h in HORIZONS} for name, states in filters.items()}
    captures = {hr: capture_basin(system, filters["K_strict"], hr) for hr in RECOVERY_HORIZONS}
    distances_hr4 = shortest_capture_distances(system, filters["K_strict"], 4)
    row: dict[str, object] = {
        "system_id": system.system_id,
        "seed": system.seed,
        "regime": system.regime,
        "control_type": system.control_type,
        "is_control": int(system.is_control),
        "num_states": len(system.states),
        "num_transitions": sum(len(targets) for targets in system.edges.values()),
        "constraint_params_json": json.dumps(system.constraint_params, sort_keys=True),
        "transform_params_json": json.dumps(system.transform_params, sort_keys=True),
        "transform_names_json": json.dumps([transform.name for transform in system.transforms]),
        "job_elapsed_seconds": time.perf_counter() - started,
    }
    for name in ("K0", "K1", "K2", "K3", "K4", "K_strict"):
        row[f"{name}_size"] = len(filters[name])
        for horizon in HORIZONS:
            row[f"viab_{name}_H{horizon}"] = len(viab[name][horizon])
    for horizon in HORIZONS:
        row[f"strict_kernel_fraction_H{horizon}"] = row[f"viab_K_strict_H{horizon}"] / max(1, row["num_states"])
        row[f"strict_given_loose_fraction_H{horizon}"] = row[f"viab_K_strict_H{horizon}"] / max(1, row[f"viab_K0_H{horizon}"])
    for hr, states in captures.items():
        row[f"capture_K_strict_Hr{hr}"] = len(states)
        row[f"strict_capture_fraction_Hr{hr}"] = len(states) / max(1, row["num_states"])
    row.update(recovery_metrics(system, filters, captures[4], distances_hr4))
    row.update(contraction_metrics(system, viab["K_strict"][16], HORIZONS))
    row["filter_collapse_stage"] = _collapse_stage(row)
    row["strict_object_class"] = _strict_object_class(row)
    row["batch_read"] = _batch_read(row)
    return row


def _collapse_stage(row: dict[str, object]) -> str:
    for key in ("K0_size", "K1_size", "K2_size", "K3_size", "K4_size", "K_strict_size", "viab_K_strict_H16"):
        if int(row[key]) == 0:
            return key
    return "none"


def _strict_object_class(row: dict[str, object]) -> str:
    frac = float(row["strict_kernel_fraction_H16"])
    if int(row["viab_K_strict_H16"]) == 0:
        return "strict_zero"
    if frac < 0.005:
        return "strict_sparse_nonzero"
    if frac < 0.10:
        return "strict_moderate"
    return "strict_large_or_trivial"


def _batch_read(row: dict[str, object]) -> str:
    if row["strict_object_class"] == "strict_zero":
        return "overfiltered_or_dead"
    if row["strict_object_class"] == "strict_large_or_trivial":
        return "possibly_too_permissive"
    if float(row["contraction_event_rate_H16"]) > 0 and float(row["expansion_event_rate_H16"]) > 0:
        return "resolving_contraction_and_expansion"
    return "strict_object_without_contraction_resolution"


def _jobs(args: argparse.Namespace) -> list[dict[str, object]]:
    regimes = [item.strip() for item in args.regimes.split(",") if item.strip()]
    controls = [item.strip() for item in args.controls.split(",") if item.strip()]
    jobs = []
    for control_type in controls:
        for regime in regimes:
            for seed_index in range(args.seeds_per_regime):
                jobs.append({"seed": _seed_for(control_type, regime, seed_index), "regime": regime, "control_type": control_type})
    return jobs


def _seed_for(control_type: str, regime: str, seed_index: int) -> int:
    text = f"{control_type}:{regime}"
    stable = sum((index + 1) * ord(char) for index, char in enumerate(text))
    return stable * 100 + seed_index


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


def _mean(values: list[object]) -> float:
    return mean(float(value) for value in values) if values else 0.0


def _mean_row(labels: dict[str, object], rows: list[dict[str, object]]) -> dict[str, object]:
    keys = [
        "K0_size",
        "K_strict_size",
        "viab_K0_H16",
        "viab_K_strict_H16",
        "strict_kernel_fraction_H16",
        "strict_given_loose_fraction_H16",
        "capture_K_strict_Hr4",
        "strict_capture_fraction_Hr4",
        "recovery_rate_K_strict_capacity_loss",
        "recovery_rate_K_strict_integrity_damage",
        "recovery_rate_K_strict_option_loss",
        "recovery_rate_K_strict_repair_loss",
        "mean_contraction_ratio_H16",
        "contraction_event_rate_H16",
        "expansion_event_rate_H16",
        "strict_preserving_transition_count",
    ]
    output = {**labels, "n": len(rows)}
    for key in keys:
        output[f"mean_{key}"] = _mean([row[key] for row in rows]) if rows and key in rows[0] else 0.0
    return output


def _group_summary(rows: list[dict[str, object]], key: str) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    return [_mean_row({key: value}, items) for value, items in sorted(grouped.items())]


def _write_outputs(out_dir: Path, config: dict[str, object], rows: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    aggregate = [_mean_row({"scope": "all"}, rows)] if rows else []
    kernel_summary = _group_summary(rows, "strict_object_class") if rows else []
    capture_summary = _group_summary(rows, "regime") if rows else []
    contraction_summary = _group_summary(rows, "batch_read") if rows else []
    control_summary = _group_summary(rows, "control_type") if rows else []
    regime_summary = _group_summary([row for row in rows if not int(row["is_control"])], "regime") if rows else []
    _write_csv(out_dir / "aggregate.csv", aggregate)
    _write_csv(out_dir / "results.csv", rows)
    _write_csv(out_dir / "kernel_summary.csv", kernel_summary)
    _write_csv(out_dir / "capture_summary.csv", capture_summary)
    _write_csv(out_dir / "contraction_summary.csv", contraction_summary)
    _write_csv(out_dir / "control_summary.csv", control_summary)
    _write_csv(out_dir / "regime_summary.csv", regime_summary)
    status = {
        "status": config.get("status", "RUNNING"),
        "rows_completed": len(rows),
        "errors": len(errors),
        "elapsed_seconds": time.perf_counter() - float(config["started_perf_counter"]),
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(out_dir, config, aggregate, kernel_summary, control_summary, regime_summary, errors)


def _write_summary(
    out_dir: Path,
    config: dict[str, object],
    aggregate: list[dict[str, object]],
    kernel_summary: list[dict[str, object]],
    control_summary: list[dict[str, object]],
    regime_summary: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    lines = [
        "# RFS0 Strict Reachable Futures Batch",
        "",
        "Exact finite substrate batch. Omega-positive labels are not used.",
        "",
        "## Config",
        "",
        "```json",
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        "```",
        "",
        "## Aggregate",
        "",
        "| scope | n | K strict | Viab strict H16 | strict fraction | capture Hr4 | recovery cap | recovery integrity | contraction | expansion |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in aggregate:
        lines.append(_summary_line(row, "scope"))
    lines.extend(["", "## Kernel Classes", "", "| class | n | K strict | Viab strict H16 | strict fraction | capture Hr4 | contraction | expansion |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
    for row in kernel_summary:
        lines.append(_compact_line(row, "strict_object_class"))
    lines.extend(["", "## Controls", "", "| control | n | K strict | Viab strict H16 | strict fraction | capture Hr4 | contraction | expansion |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
    for row in control_summary:
        lines.append(_compact_line(row, "control_type"))
    lines.extend(["", "## Structured Regimes", "", "| regime | n | K strict | Viab strict H16 | strict fraction | capture Hr4 | contraction | expansion |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
    for row in regime_summary:
        lines.append(_compact_line(row, "regime"))
    lines.extend(
        [
            "",
            "## Smoke Read",
            "",
            f"- Rows completed: {aggregate[0]['n'] if aggregate else 0}.",
            f"- Errors: {len(errors)}.",
            "- Graceful-stop behavior: partial rows, CSV summaries, status, and this summary are rewritten after completed jobs.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _summary_line(row: dict[str, object], label_key: str) -> str:
    return "| {label} | {n} | {ks:.1f} | {vs:.1f} | {sf:.4f} | {cap:.1f} | {rc:.3f} | {ri:.3f} | {con:.3f} | {exp:.3f} |".format(
        label=row[label_key],
        n=row["n"],
        ks=float(row["mean_K_strict_size"]),
        vs=float(row["mean_viab_K_strict_H16"]),
        sf=float(row["mean_strict_kernel_fraction_H16"]),
        cap=float(row["mean_capture_K_strict_Hr4"]),
        rc=float(row["mean_recovery_rate_K_strict_capacity_loss"]),
        ri=float(row["mean_recovery_rate_K_strict_integrity_damage"]),
        con=float(row["mean_contraction_event_rate_H16"]),
        exp=float(row["mean_expansion_event_rate_H16"]),
    )


def _compact_line(row: dict[str, object], label_key: str) -> str:
    return "| {label} | {n} | {ks:.1f} | {vs:.1f} | {sf:.4f} | {cap:.1f} | {con:.3f} | {exp:.3f} |".format(
        label=row[label_key],
        n=row["n"],
        ks=float(row["mean_K_strict_size"]),
        vs=float(row["mean_viab_K_strict_H16"]),
        sf=float(row["mean_strict_kernel_fraction_H16"]),
        cap=float(row["mean_capture_K_strict_Hr4"]),
        con=float(row["mean_contraction_event_rate_H16"]),
        exp=float(row["mean_expansion_event_rate_H16"]),
    )


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "rfs0" / f"{run_id}_strict_reachable_futures_batch"
    out_dir.mkdir(parents=True, exist_ok=True)
    config = vars(args)
    config["run_id"] = run_id
    config["out"] = str(out_dir)
    config["started_perf_counter"] = time.perf_counter()
    config["status"] = "RUNNING"
    (out_dir / "config.json").write_text(json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True), encoding="utf-8")
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    pending = _jobs(args)
    result_path = out_dir / "systems.jsonl"
    error_path = out_dir / "errors.jsonl"
    futures = {}
    timed_out = False
    executor = ProcessPoolExecutor(max_workers=args.workers)
    try:
        while pending and len(futures) < args.workers:
            job = pending.pop(0)
            futures[executor.submit(_run_one, job)] = job
        while futures:
            if time.perf_counter() - float(config["started_perf_counter"]) >= args.max_runtime_seconds:
                timed_out = True
                pending = []
                for future in futures:
                    future.cancel()
                futures.clear()
                executor.shutdown(wait=False, cancel_futures=True)
                break
            done, _ = wait(futures, timeout=2.0, return_when=FIRST_COMPLETED)
            if not done:
                _write_outputs(out_dir, config, rows, errors)
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
            if len(rows) % max(1, args.checkpoint_every) == 0:
                _write_outputs(out_dir, config, rows, errors)
    finally:
        if not timed_out:
            executor.shutdown(wait=True, cancel_futures=False)
    config["status"] = "TIMED_OUT" if timed_out else "COMPLETED"
    _write_outputs(out_dir, config, rows, errors)
    (out_dir / "config.json").write_text(json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"out_dir": str(out_dir), "rows": len(rows), "errors": len(errors), "status": config["status"]}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
