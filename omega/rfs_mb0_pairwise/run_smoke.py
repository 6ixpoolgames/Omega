from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime
from pathlib import Path
from statistics import mean

from .exact import pairwise_metrics, transition_deltas
from .substrate import CONTROLS, REGIMES, generate_system

HORIZONS = (0, 1, 2, 4, 8, 12, 16)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 pairwise compatibility smoke.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seeds-per-regime", type=int, default=5)
    parser.add_argument("--regimes", type=str, default=",".join(REGIMES))
    parser.add_argument("--controls", type=str, default="structured,random_edge_control,degree_preserving_control,identity_shuffle_control,no_interaction_control,dead_control,permissive_control")
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-runtime-seconds", type=int, default=900)
    parser.add_argument("--checkpoint-every", type=int, default=4)
    return parser.parse_args()


def _run_one(job: dict[str, object]) -> dict[str, object]:
    started = time.perf_counter()
    system = generate_system(int(job["seed"]), str(job["regime"]), str(job["control_type"]))
    base: dict[str, object] = {
        "system_id": system.system_id,
        "seed": system.seed,
        "regime": system.regime,
        "control_type": system.control_type,
        "is_control": int(system.is_control),
        "n_states": len(system.states),
        "n_edges": sum(len(targets) for targets in system.edges.values()),
        "initial_state_json": json.dumps(system.initial_state),
        "generator_params_json": json.dumps(system.generator_params, sort_keys=True),
    }
    rows = []
    for horizon in HORIZONS:
        row = dict(base)
        row.update(pairwise_metrics(system, horizon))
        row.update(transition_deltas(system, horizon))
        row["readout"] = _readout(row)
        row["job_elapsed_seconds"] = time.perf_counter() - started
        rows.append(row)
    geometry = _geometry_fields(rows)
    for row in rows:
        row.update(geometry)
    return {"system": base, "rows": rows}


def _readout(row: dict[str, object]) -> str:
    class_bin = str(row["class_bin"])
    if int(row["AB_count"]) > 0 and int(row["exact_AB_count"]) == 0:
        return "no_exact_joint_persistence"
    if int(row["flatline_flag"]):
        return "flatline_joint_persistence"
    if class_bin in {"pairwise_incompatible", "pairwise_incompatible_like"}:
        return "singleton_overcall"
    if float(row["local_A_joint_contracting_rate"]) > 0 or (
        float(row["max_A_delta_when_AB_contracts"]) >= 0 and float(row["min_AB_delta"]) < 0
    ):
        return "local_A_joint_contracting"
    if float(row["local_B_joint_contracting_rate"]) > 0 or (
        float(row["max_B_delta_when_AB_contracts"]) >= 0 and float(row["min_AB_delta"]) < 0
    ):
        return "local_B_joint_contracting"
    if class_bin == "pairwise_compatible" and float(row["joint_gap_ratio"]) > 0.5:
        return "mutual_support_like"
    return class_bin


def _geometry_fields(rows: list[dict[str, object]]) -> dict[str, int | float]:
    by_h = sorted(rows, key=lambda row: int(row["H"]))

    def first_h(metric: str) -> int:
        for row in by_h:
            if int(row[metric]) > 0:
                return int(row["H"])
        return -1

    max_h_row = by_h[-1]
    max_singleton_nontrivial = max(
        first_h("nontrivial_A_count"),
        first_h("nontrivial_B_count"),
    )
    first_nontrivial_ab = first_h("nontrivial_AB_count")
    exact_max_singleton_nontrivial = max(
        first_h("exact_nontrivial_A_count"),
        first_h("exact_nontrivial_B_count"),
    )
    first_exact_nontrivial_ab = first_h("exact_nontrivial_AB_count")
    ab_counts = [(int(row["H"]), int(row["AB_count"])) for row in by_h]
    exact_nontrivial_ab_counts = [
        (int(row["H"]), int(row["exact_nontrivial_AB_count"])) for row in by_h
    ]
    last_ab_change_h = _last_change_h(ab_counts)
    return {
        "first_A_H": first_h("A_count"),
        "first_B_H": first_h("B_count"),
        "first_AB_H": first_h("AB_count"),
        "first_exact_A_H": first_h("exact_A_count"),
        "first_exact_B_H": first_h("exact_B_count"),
        "first_exact_AB_H": first_h("exact_AB_count"),
        "first_nontrivial_A_H": first_h("nontrivial_A_count"),
        "first_nontrivial_B_H": first_h("nontrivial_B_count"),
        "first_nontrivial_AB_H": first_nontrivial_ab,
        "first_exact_nontrivial_A_H": first_h("exact_nontrivial_A_count"),
        "first_exact_nontrivial_B_H": first_h("exact_nontrivial_B_count"),
        "first_exact_nontrivial_AB_H": first_exact_nontrivial_ab,
        "joint_delay": _delay(first_nontrivial_ab, max_singleton_nontrivial),
        "exact_joint_delay": _delay(
            first_exact_nontrivial_ab, exact_max_singleton_nontrivial
        ),
        "AB_flatline_all_H": int(
            int(max_h_row["AB_count"]) > 0
            and all(int(row["exact_nontrivial_AB_count"]) == 0 for row in by_h)
        ),
        "AB_saturates_early": int(int(max_h_row["AB_count"]) > 0 and last_ab_change_h <= 2),
        "exact_nontrivial_AB_never": int(
            all(count == 0 for _h, count in exact_nontrivial_ab_counts)
        ),
        "stasis_like_geometry": int(
            int(max_h_row["AB_count"]) > 0 and int(max_h_row["nontrivial_AB_count"]) == 0
        ),
        "last_AB_change_H": last_ab_change_h,
        "exact_H_growth_AB": int(max_h_row["exact_AB_count"]) - int(by_h[0]["exact_AB_count"]),
        "exact_H_growth_nontrivial_AB": int(max_h_row["exact_nontrivial_AB_count"])
        - int(by_h[0]["exact_nontrivial_AB_count"]),
    }


def _last_change_h(series: list[tuple[int, int]]) -> int:
    last_h = series[0][0]
    last_value = series[0][1]
    for horizon, value in series[1:]:
        if value != last_value:
            last_h = horizon
            last_value = value
    return last_h


def _delay(first_joint: int, first_singleton: int) -> int:
    if first_joint < 0 or first_singleton < 0:
        return -1
    return first_joint - first_singleton


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
    text = f"mb0:{control_type}:{regime}"
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
            "reach_count",
            "A_count",
            "B_count",
            "AB_count",
            "exact_A_count",
            "exact_B_count",
            "exact_AB_count",
            "nontrivial_A_count",
            "nontrivial_B_count",
            "nontrivial_AB_count",
            "exact_nontrivial_A_count",
            "exact_nontrivial_B_count",
            "exact_nontrivial_AB_count",
            "AB_over_A",
            "AB_over_B",
            "joint_gap",
            "joint_gap_ratio",
            "exact_joint_gap_ratio",
            "nontrivial_joint_fraction",
            "exact_nontrivial_joint_fraction",
            "flatline_flag",
            "mean_A_delta",
            "mean_B_delta",
            "mean_AB_delta",
            "local_A_joint_contracting_rate",
            "local_B_joint_contracting_rate",
            "max_A_delta_when_AB_contracts",
            "max_B_delta_when_AB_contracts",
            "min_AB_delta",
            "first_A_H",
            "first_B_H",
            "first_AB_H",
            "first_exact_A_H",
            "first_exact_B_H",
            "first_exact_AB_H",
            "first_nontrivial_A_H",
            "first_nontrivial_B_H",
            "first_nontrivial_AB_H",
            "first_exact_nontrivial_A_H",
            "first_exact_nontrivial_B_H",
            "first_exact_nontrivial_AB_H",
            "joint_delay",
            "exact_joint_delay",
            "AB_flatline_all_H",
            "AB_saturates_early",
            "exact_nontrivial_AB_never",
            "stasis_like_geometry",
            "last_AB_change_H",
            "exact_H_growth_AB",
            "exact_H_growth_nontrivial_AB",
        ):
            summary[f"mean_{metric}"] = _mean([item[metric] for item in items])
        out.append(summary)
    return out


def _group_sort_key(keys: tuple[str, ...], labels: tuple[str, ...]) -> tuple[object, ...]:
    sortable: list[object] = []
    for key, label in zip(keys, labels):
        sortable.append(int(label) if key == "H" else label)
    return tuple(sortable)


def _write_outputs(
    out_dir: Path,
    config: dict[str, object],
    rows: list[dict[str, object]],
    systems: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    hmax_rows = [row for row in rows if int(row["H"]) == max(HORIZONS)]
    _write_csv(out_dir / "results.csv", rows)
    _write_csv(out_dir / "regime_summary.csv", _group(rows, ("control_type", "regime", "H")))
    _write_csv(out_dir / "readout_summary.csv", _group(rows, ("control_type", "readout", "H")))
    _write_csv(out_dir / "geometry_summary.csv", _group(hmax_rows, ("control_type", "regime")))
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
                "readout_summary": _group(rows, ("control_type", "readout", "H")),
                "regime_summary": _group(rows, ("control_type", "regime", "H")),
                "geometry_summary": _group(hmax_rows, ("control_type", "regime")),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    _write_summary(out_dir, config, rows, errors)


def _write_summary(out_dir: Path, config: dict[str, object], rows: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    h16 = [row for row in rows if int(row["H"]) == 16]
    regime_summary = _group(h16, ("control_type", "regime", "H"))
    readout_summary = _group(h16, ("control_type", "readout", "H"))
    geometry_summary = _group(h16, ("control_type", "regime"))
    filtration_summary = _group(rows, ("control_type", "regime", "H"))
    lines = [
        "# RFS-MB0 Pairwise Compatibility Smoke",
        "",
        "Controlled toy-regime smoke for singleton versus joint identity-preserving reachable futures. This is not an Omega validation run.",
        "",
        "## Config",
        "",
        "```json",
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        "```",
        "",
        "## H16 By Regime",
        "",
        "| control | regime | n | A | B | AB | AB/min | exact AB | exact AB/min | nontriv AB | flatline | A joint-contract | B joint-contract |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in regime_summary:
        lines.append(
            "| {control_type} | {regime} | {n} | {a:.1f} | {b:.1f} | {ab:.1f} | {ratio:.3f} | {exact_ab:.1f} | {exact_ratio:.3f} | {nontriv:.1f} | {flatline:.3f} | {la:.3f} | {lb:.3f} |".format(
                control_type=row["control_type"],
                regime=row["regime"],
                n=row["n"],
                a=float(row["mean_A_count"]),
                b=float(row["mean_B_count"]),
                ab=float(row["mean_AB_count"]),
                ratio=float(row["mean_joint_gap_ratio"]),
                exact_ab=float(row["mean_exact_AB_count"]),
                exact_ratio=float(row["mean_exact_joint_gap_ratio"]),
                nontriv=float(row["mean_nontrivial_AB_count"]),
                flatline=float(row["mean_flatline_flag"]),
                la=float(row["mean_local_A_joint_contracting_rate"]),
                lb=float(row["mean_local_B_joint_contracting_rate"]),
            )
        )
    lines.extend(
        [
            "",
            "## H16 Readouts",
            "",
            "| control | readout | n | A | B | AB | AB/min | exact AB | nontriv AB | flatline |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in readout_summary:
        lines.append(
            "| {control_type} | {readout} | {n} | {a:.1f} | {b:.1f} | {ab:.1f} | {ratio:.3f} | {exact_ab:.1f} | {nontriv:.1f} | {flatline:.3f} |".format(
                control_type=row["control_type"],
                readout=row["readout"],
                n=row["n"],
                a=float(row["mean_A_count"]),
                b=float(row["mean_B_count"]),
                ab=float(row["mean_AB_count"]),
                ratio=float(row["mean_joint_gap_ratio"]),
                exact_ab=float(row["mean_exact_AB_count"]),
                nontriv=float(row["mean_nontrivial_AB_count"]),
                flatline=float(row["mean_flatline_flag"]),
            )
        )
    lines.extend(
        [
            "",
            "## First Propagation Geometry",
            "",
            "| control | regime | first nontriv AB | first exact nontriv AB | joint delay | exact joint delay | AB saturates early | exact nontriv AB never | stasis-like |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in geometry_summary:
        lines.append(
            "| {control_type} | {regime} | {first_ab:.1f} | {first_exact_ab:.1f} | {delay:.1f} | {exact_delay:.1f} | {saturates:.3f} | {never:.3f} | {stasis:.3f} |".format(
                control_type=row["control_type"],
                regime=row["regime"],
                first_ab=float(row["mean_first_nontrivial_AB_H"]),
                first_exact_ab=float(row["mean_first_exact_nontrivial_AB_H"]),
                delay=float(row["mean_joint_delay"]),
                exact_delay=float(row["mean_exact_joint_delay"]),
                saturates=float(row["mean_AB_saturates_early"]),
                never=float(row["mean_exact_nontrivial_AB_never"]),
                stasis=float(row["mean_stasis_like_geometry"]),
            )
        )
    lines.extend(
        [
            "",
            "## Horizon Filtration By Regime",
            "",
            "| control | regime | H | A | B | AB | exact AB | exact nontriv AB | AB/min | exact AB/min |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in filtration_summary:
        lines.append(
            "| {control_type} | {regime} | {h} | {a:.1f} | {b:.1f} | {ab:.1f} | {exact_ab:.1f} | {exact_nontriv_ab:.1f} | {ratio:.3f} | {exact_ratio:.3f} |".format(
                control_type=row["control_type"],
                regime=row["regime"],
                h=row["H"],
                a=float(row["mean_A_count"]),
                b=float(row["mean_B_count"]),
                ab=float(row["mean_AB_count"]),
                exact_ab=float(row["mean_exact_AB_count"]),
                exact_nontriv_ab=float(row["mean_exact_nontrivial_AB_count"]),
                ratio=float(row["mean_joint_gap_ratio"]),
                exact_ratio=float(row["mean_exact_joint_gap_ratio"]),
            )
        )
    lines.extend(
        [
            "",
            "## Smoke Read",
            "",
            f"- Rows completed: {len(rows)}.",
            f"- Errors: {len(errors)}.",
            "- Public claim boundary: pairwise futures machinery only; controlled toy regimes; no Omega-positive interpretation.",
            "- Graceful-stop behavior: partial rows, summaries, status, and this Markdown report are rewritten after completed systems.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "rfs_mb0_pairwise" / f"{run_id}_pairwise_compatibility_smoke"
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
                    system = payload["system"]
                    result_rows = payload["rows"]
                    systems.append(system)
                    rows.extend(result_rows)
                    with systems_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(system, sort_keys=True) + "\n")
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
    print(json.dumps({"out_dir": str(out_dir), "systems": len(systems), "rows": len(rows), "errors": len(errors), "status": config["status"]}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
