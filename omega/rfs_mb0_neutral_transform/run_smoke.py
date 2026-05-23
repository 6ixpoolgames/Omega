from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime
from pathlib import Path
from statistics import mean

from .exact import HORIZONS, filtration_rows
from .extractors import extract_candidates
from .substrate import FAMILIES, generate_system


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 neutral transform reset smoke.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seeds-per-family", type=int, default=5)
    parser.add_argument("--families", type=str, default=",".join(FAMILIES))
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-runtime-seconds", type=int, default=900)
    parser.add_argument("--checkpoint-every", type=int, default=4)
    return parser.parse_args()


def _run_one(job: dict[str, object]) -> dict[str, object]:
    started = time.perf_counter()
    system = generate_system(int(job["seed"]), str(job["family"]))
    mu, nu = extract_candidates(system)
    base = {
        "system_id": system.system_id,
        "seed": system.seed,
        "family": system.family,
        "n_states": len(system.states),
        "n_edges": sum(len(targets) for targets in system.edges.values()),
        "initial_state_json": json.dumps(system.initial_state),
        "transform_names_json": json.dumps(system.transform_names),
        "extractor_mode": system.extractor_mode,
        "metadata_json": json.dumps(system.metadata, sort_keys=True),
    }
    rows = []
    for row in filtration_rows(system, mu, nu):
        rows.append({**base, **row, "job_elapsed_seconds": time.perf_counter() - started})
    return {"system": base, "rows": rows}


def _jobs(args: argparse.Namespace) -> list[dict[str, object]]:
    families = [item.strip() for item in args.families.split(",") if item.strip()]
    jobs = []
    for family in families:
        for seed_index in range(args.seeds_per_family):
            jobs.append({"seed": _seed_for(family, seed_index), "family": family})
    return jobs


def _seed_for(family: str, seed_index: int) -> int:
    text = f"neutral-mb0:{family}"
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


def _group(rows: list[dict[str, object]], keys: tuple[str, ...]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, ...], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(tuple(str(row[key]) for key in keys), []).append(row)
    out = []
    for labels, items in sorted(grouped.items(), key=lambda item: _group_sort_key(keys, item[0])):
        summary = {key: label for key, label in zip(keys, labels)}
        summary["n"] = len(items)
        for metric in (
            "mu_count",
            "nu_count",
            "joint_count",
            "exact_mu_count",
            "exact_nu_count",
            "exact_joint_count",
            "joint_over_min",
            "exact_joint_over_min",
            "first_mu_H",
            "first_nu_H",
            "first_joint_H",
            "first_nonphase_joint_H",
            "joint_delay",
            "exact_joint_delay",
            "joint_flatline_flag",
            "joint_saturates_early_flag",
            "last_joint_change_H",
            "mean_changed_coordinate_count",
            "mean_changed_nonphase_coordinate_count",
            "mean_changed_mu_block_count",
            "mean_changed_nu_block_count",
            "mean_changed_outside_block_count",
            "phase_only_change_fraction",
            "nonphase_change_fraction",
            "block_relation_changed_fraction",
            "local_mu_persists_joint_contracts_rate",
            "local_nu_persists_joint_contracts_rate",
            "min_joint_delta",
        ):
            summary[f"mean_{metric}"] = _mean([item[metric] for item in items])
        out.append(summary)
    return out


def _group_sort_key(keys: tuple[str, ...], labels: tuple[str, ...]) -> tuple[object, ...]:
    output: list[object] = []
    for key, label in zip(keys, labels):
        output.append(int(label) if key == "H" else label)
    return tuple(output)


def _write_outputs(
    out_dir: Path,
    config: dict[str, object],
    rows: list[dict[str, object]],
    systems: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    hmax = max(HORIZONS)
    hmax_rows = [row for row in rows if int(row["H"]) == hmax]
    _write_csv(out_dir / "results.csv", rows)
    _write_csv(out_dir / "family_horizon_summary.csv", _group(rows, ("family", "H")))
    _write_csv(out_dir / "geometry_summary.csv", _group(hmax_rows, ("family",)))
    _write_csv(out_dir / "result_bins.csv", _group(hmax_rows, ("family", "result_bin")))
    status = {
        "status": config.get("status", "RUNNING"),
        "systems_completed": len(systems),
        "rows_completed": len(rows),
        "errors": len(errors),
        "elapsed_seconds": time.perf_counter() - float(config["started_perf_counter"]),
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "summary.json").write_text(
        json.dumps(
            {
                "status": status,
                "family_horizon_summary": _group(rows, ("family", "H")),
                "geometry_summary": _group(hmax_rows, ("family",)),
                "result_bins": _group(hmax_rows, ("family", "result_bin")),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    _write_summary(out_dir, config, rows, hmax_rows, errors)


def _write_summary(
    out_dir: Path,
    config: dict[str, object],
    rows: list[dict[str, object]],
    hmax_rows: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    geometry = _group(hmax_rows, ("family",))
    bins = _group(hmax_rows, ("family", "result_bin"))
    filtration = _group(rows, ("family", "H"))
    lines = [
        "# RFS-MB0 Neutral Transform Reset Smoke",
        "",
        "Neutral finite transformation substrate. This is a reset smoke for derived signature filtrations.",
        "",
        "## Config",
        "",
        "```json",
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        "```",
        "",
        "## H16 Geometry",
        "",
        "| family | n | mu | nu | joint | joint/min | exact joint | exact joint/min | first joint | first nonphase joint | joint delay | flatline | saturates early |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in geometry:
        lines.append(
            "| {family} | {n} | {mu:.1f} | {nu:.1f} | {joint:.1f} | {ratio:.3f} | {exact_joint:.1f} | {exact_ratio:.3f} | {first_joint:.1f} | {first_nonphase:.1f} | {delay:.1f} | {flat:.3f} | {sat:.3f} |".format(
                family=row["family"],
                n=row["n"],
                mu=float(row["mean_mu_count"]),
                nu=float(row["mean_nu_count"]),
                joint=float(row["mean_joint_count"]),
                ratio=float(row["mean_joint_over_min"]),
                exact_joint=float(row["mean_exact_joint_count"]),
                exact_ratio=float(row["mean_exact_joint_over_min"]),
                first_joint=float(row["mean_first_joint_H"]),
                first_nonphase=float(row["mean_first_nonphase_joint_H"]),
                delay=float(row["mean_joint_delay"]),
                flat=float(row["mean_joint_flatline_flag"]),
                sat=float(row["mean_joint_saturates_early_flag"]),
            )
        )
    lines.extend(
        [
            "",
            "## H16 Result Bins",
            "",
            "| family | result bin | n | joint/min | local mu | local nu | phase-only | nonphase | relation changed |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in bins:
        lines.append(
            "| {family} | {result_bin} | {n} | {ratio:.3f} | {local_mu:.3f} | {local_nu:.3f} | {phase:.3f} | {nonphase:.3f} | {relation:.3f} |".format(
                family=row["family"],
                result_bin=row["result_bin"],
                n=row["n"],
                ratio=float(row["mean_joint_over_min"]),
                local_mu=float(row["mean_local_mu_persists_joint_contracts_rate"]),
                local_nu=float(row["mean_local_nu_persists_joint_contracts_rate"]),
                phase=float(row["mean_phase_only_change_fraction"]),
                nonphase=float(row["mean_nonphase_change_fraction"]),
                relation=float(row["mean_block_relation_changed_fraction"]),
            )
        )
    lines.extend(
        [
            "",
            "## Horizon Filtration",
            "",
            "| family | H | mu | nu | joint | exact joint | joint/min | exact joint/min | nonphase endpoint | relation changed |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in filtration:
        lines.append(
            "| {family} | {h} | {mu:.1f} | {nu:.1f} | {joint:.1f} | {exact_joint:.1f} | {ratio:.3f} | {exact_ratio:.3f} | {nonphase:.3f} | {relation:.3f} |".format(
                family=row["family"],
                h=row["H"],
                mu=float(row["mean_mu_count"]),
                nu=float(row["mean_nu_count"]),
                joint=float(row["mean_joint_count"]),
                exact_joint=float(row["mean_exact_joint_count"]),
                ratio=float(row["mean_joint_over_min"]),
                exact_ratio=float(row["mean_exact_joint_over_min"]),
                nonphase=float(row["mean_nonphase_change_fraction"]),
                relation=float(row["mean_block_relation_changed_fraction"]),
            )
        )
    lines.extend(
        [
            "",
            "## Smoke Read",
            "",
            f"- Rows completed: {len(rows)}.",
            f"- Errors: {len(errors)}.",
            "- Claim boundary: neutral transform substrate and derived signature filtrations only.",
            "- Graceful-stop behavior: partial rows, summaries, status, and this Markdown report are rewritten after completed systems.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "rfs_mb0_neutral_transform" / f"{run_id}_neutral_transform_reset_smoke"
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
    rows: list[dict[str, object]] = []
    systems: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    pending = _jobs(args)
    systems_path = out_dir / "systems.jsonl"
    errors_path = out_dir / "errors.jsonl"
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
                _write_outputs(out_dir, config, rows, systems, errors)
                continue
            for future in done:
                job = futures.pop(future)
                try:
                    payload = future.result()
                    systems.append(payload["system"])
                    rows.extend(payload["rows"])
                    with systems_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(payload["system"], sort_keys=True) + "\n")
                except Exception as exc:  # noqa: BLE001
                    error = {"job": job, "error": repr(exc)}
                    errors.append(error)
                    with errors_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(error, sort_keys=True) + "\n")
                while pending and len(futures) < args.workers:
                    next_job = pending.pop(0)
                    futures[executor.submit(_run_one, next_job)] = next_job
            if len(systems) % max(1, args.checkpoint_every) == 0:
                _write_outputs(out_dir, config, rows, systems, errors)
    finally:
        if not timed_out:
            executor.shutdown(wait=True, cancel_futures=False)
    config["status"] = "TIMED_OUT" if timed_out else "COMPLETED"
    _write_outputs(out_dir, config, rows, systems, errors)
    (out_dir / "config.json").write_text(
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "systems": len(systems),
                "rows": len(rows),
                "errors": len(errors),
                "status": config["status"],
            },
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
