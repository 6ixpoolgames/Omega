from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime
from pathlib import Path
from statistics import mean

from .controls import null_distribution_by_h
from .landscape import edge_deformations, future_profile
from .probes import generate_probes
from .substrate import FAMILIES, generate_system


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFS-MB0 future landscape smoke.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--seeds-per-family", type=int, default=3)
    parser.add_argument("--families", type=str, default=",".join(FAMILIES))
    parser.add_argument("--sigma", type=int, default=2)
    parser.add_argument("--start-samples", type=int, default=4)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-runtime-seconds", type=int, default=900)
    parser.add_argument("--checkpoint-every", type=int, default=4)
    return parser.parse_args()


def _run_one(job: dict[str, object]) -> dict[str, object]:
    started = time.perf_counter()
    system = generate_system(int(job["seed"]), str(job["family"]))
    probes = generate_probes(system, int(job["sigma"]))
    start_count = int(job["start_samples"])
    starts = [system.states[(system.seed + i * 17) % len(system.states)] for i in range(start_count)]
    profiles = []
    profile_rows = []
    distributions = []
    deformations = []
    for probe in probes:
        null_by_h = null_distribution_by_h(system, probe)
        for start in starts:
            profile, rows, dist_rows = future_profile(system, start, probe, null_by_h)
            profiles.append(profile)
            profile_rows.extend(rows)
            distributions.extend(dist_rows)
        deformations.extend(edge_deformations(system, probe))
    system_row = {
        "system_id": system.system_id,
        "seed": system.seed,
        "family": system.family,
        "n_states": len(system.states),
        "n_edges": sum(len(targets) for targets in system.edges.values()),
        "transform_names_json": json.dumps(system.transform_names),
        "probe_count": len(probes),
        "start_count": len(starts),
        "metadata_json": json.dumps(system.metadata, sort_keys=True),
        "job_elapsed_seconds": time.perf_counter() - started,
    }
    return {
        "system": system_row,
        "profiles": profiles,
        "profile_rows": profile_rows,
        "distributions": distributions,
        "deformations": deformations,
    }


def _jobs(args: argparse.Namespace) -> list[dict[str, object]]:
    families = [item.strip() for item in args.families.split(",") if item.strip()]
    jobs = []
    for family in families:
        for seed_index in range(args.seeds_per_family):
            jobs.append(
                {
                    "seed": _seed_for(family, seed_index),
                    "family": family,
                    "sigma": args.sigma,
                    "start_samples": args.start_samples,
                }
            )
    return jobs


def _seed_for(family: str, seed_index: int) -> int:
    text = f"future-landscape:{family}"
    stable = sum((index + 1) * ord(char) for index, char in enumerate(text))
    return stable * 100 + seed_index


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _mean(values: list[object]) -> float:
    return mean(float(value) for value in values) if values else 0.0


def _group(rows: list[dict[str, object]], keys: tuple[str, ...]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, ...], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(tuple(str(row[key]) for key in keys), []).append(row)
    out = []
    for labels, items in sorted(grouped.items()):
        summary = {key: label for key, label in zip(keys, labels)}
        summary["n"] = len(items)
        for metric in (
            "reach_H16",
            "exact_H16",
            "growth_mean",
            "entropy_mean",
            "signature_support_mean",
            "recurrence_rate",
            "motif_reuse",
            "transition_motif_count_mean",
            "predictive_information",
            "conditional_entropy_proxy",
            "compression_proxy",
            "saturation_horizon",
            "cycle_indicator",
            "collapse_indicator",
            "JS_to_null_mean",
            "smoothed_KL_to_null_mean",
        ):
            summary[f"mean_{metric}"] = _mean([item[metric] for item in items])
        out.append(summary)
    return out


def _deformation_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["family"]), str(row["probe_name"])), []).append(row)
    out = []
    for (family, probe_name), items in sorted(grouped.items()):
        summary = {"family": family, "probe_name": probe_name, "n": len(items)}
        for metric in (
            "future_entropy_delta",
            "reach_growth_delta",
            "predictive_information_delta",
            "recurrence_delta",
            "compression_delta",
            "collapse_indicator_delta",
            "cycle_indicator_delta",
            "JS_to_null_delta",
        ):
            summary[f"mean_{metric}"] = _mean([item[metric] for item in items])
        out.append(summary)
    return out


def _write_outputs(
    out_dir: Path,
    config: dict[str, object],
    systems: list[dict[str, object]],
    profiles: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
    distributions: list[dict[str, object]],
    deformations: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    class_summary = _group(profiles, ("family", "profile_class"))
    family_summary = _group(profiles, ("family",))
    divergence_summary = _group(profiles, ("profile_class",))
    deformation_summary = _deformation_summary(deformations)
    _write_csv(out_dir / "results.csv", systems)
    _write_csv(out_dir / "future_profiles.csv", profile_rows)
    _write_csv(out_dir / "signature_distributions.csv", distributions)
    _write_csv(out_dir / "control_comparison.csv", family_summary)
    _write_csv(out_dir / "profile_classes.csv", class_summary)
    _write_csv(out_dir / "divergence_summary.csv", divergence_summary)
    _write_csv(out_dir / "deformation_summary.csv", deformation_summary)
    _write_csv(out_dir / "errors.csv", errors)
    status = {
        "status": config.get("status", "RUNNING"),
        "systems_completed": len(systems),
        "profiles_completed": len(profiles),
        "errors": len(errors),
        "elapsed_seconds": time.perf_counter() - float(config["started_perf_counter"]),
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(out_dir, config, systems, profiles, class_summary, family_summary, divergence_summary, deformation_summary, errors)


def _write_summary(
    out_dir: Path,
    config: dict[str, object],
    systems: list[dict[str, object]],
    profiles: list[dict[str, object]],
    class_summary: list[dict[str, object]],
    family_summary: list[dict[str, object]],
    divergence_summary: list[dict[str, object]],
    deformation_summary: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    lines = [
        "# RFS-MB0 Future Landscape Smoke",
        "",
        "Neutral future-profile probe derived from finite distinction states and neutral relations.",
        "",
        "## Config",
        "",
        "```json",
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        "```",
        "",
        "## Run Shape",
        "",
        f"- Systems completed: {len(systems)}",
        f"- Future profiles completed: {len(profiles)}",
        f"- Errors: {len(errors)}",
        "",
        "## Future-Profile Class Counts",
        "",
        "| family | class | n | entropy | predictive | recurrence | compression | JS null | KL null |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in class_summary:
        lines.append(_profile_line(row, "family", "profile_class"))
    lines.extend(["", "## Control Comparison", "", "| family | n | reach H16 | exact H16 | entropy | predictive | recurrence | compression | collapse | cycle | JS null |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"])
    for row in family_summary:
        lines.append(
            "| {family} | {n} | {reach:.1f} | {exact:.1f} | {entropy:.3f} | {pred:.3f} | {rec:.3f} | {comp:.3f} | {collapse:.3f} | {cycle:.3f} | {js:.3f} |".format(
                family=row["family"],
                n=row["n"],
                reach=float(row["mean_reach_H16"]),
                exact=float(row["mean_exact_H16"]),
                entropy=float(row["mean_entropy_mean"]),
                pred=float(row["mean_predictive_information"]),
                rec=float(row["mean_recurrence_rate"]),
                comp=float(row["mean_compression_proxy"]),
                collapse=float(row["mean_collapse_indicator"]),
                cycle=float(row["mean_cycle_indicator"]),
                js=float(row["mean_JS_to_null_mean"]),
            )
        )
    lines.extend(["", "## Divergence By Class", "", "| class | n | JS null | KL null | entropy | predictive |", "|---|---:|---:|---:|---:|---:|"])
    for row in divergence_summary:
        lines.append(
            "| {klass} | {n} | {js:.3f} | {kl:.3f} | {entropy:.3f} | {pred:.3f} |".format(
                klass=row["profile_class"],
                n=row["n"],
                js=float(row["mean_JS_to_null_mean"]),
                kl=float(row["mean_smoothed_KL_to_null_mean"]),
                entropy=float(row["mean_entropy_mean"]),
                pred=float(row["mean_predictive_information"]),
            )
        )
    lines.extend(["", "## Deformation Summary", "", "| family | probe | n | entropy delta | growth delta | predictive delta | recurrence delta | compression delta | JS delta |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"])
    for row in deformation_summary[:80]:
        lines.append(
            "| {family} | {probe} | {n} | {ent:.3f} | {growth:.3f} | {pred:.3f} | {rec:.3f} | {comp:.3f} | {js:.3f} |".format(
                family=row["family"],
                probe=row["probe_name"],
                n=row["n"],
                ent=float(row["mean_future_entropy_delta"]),
                growth=float(row["mean_reach_growth_delta"]),
                pred=float(row["mean_predictive_information_delta"]),
                rec=float(row["mean_recurrence_delta"]),
                comp=float(row["mean_compression_delta"]),
                js=float(row["mean_JS_to_null_delta"]),
            )
        )
    lines.extend(["", "## Claim Boundary", "", "This smoke reports future-landscape profiles, neutral class labels, and null divergences only. It does not assign semantic roles or preferred outcomes.", "", "## Next Recommendation", "", "- Treat this as an instrumentation smoke unless structured_propagation separates from controls across multiple measures.", "- If classes collapse into controls, revise probes/detectors before increasing compute."])
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _profile_line(row: dict[str, object], family_key: str, class_key: str) -> str:
    return "| {family} | {klass} | {n} | {entropy:.3f} | {pred:.3f} | {rec:.3f} | {comp:.3f} | {js:.3f} | {kl:.3f} |".format(
        family=row[family_key],
        klass=row[class_key],
        n=row["n"],
        entropy=float(row["mean_entropy_mean"]),
        pred=float(row["mean_predictive_information"]),
        rec=float(row["mean_recurrence_rate"]),
        comp=float(row["mean_compression_proxy"]),
        js=float(row["mean_JS_to_null_mean"]),
        kl=float(row["mean_smoothed_KL_to_null_mean"]),
    )


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "rfs_mb0_future_landscape" / f"{run_id}_future_landscape_smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    config = vars(args)
    config["run_id"] = run_id
    config["out"] = str(out_dir)
    config["started_perf_counter"] = time.perf_counter()
    config["status"] = "RUNNING"
    (out_dir / "config.json").write_text(json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True), encoding="utf-8")
    systems: list[dict[str, object]] = []
    profiles: list[dict[str, object]] = []
    profile_rows: list[dict[str, object]] = []
    distributions: list[dict[str, object]] = []
    deformations: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    pending = _jobs(args)
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
                _write_outputs(out_dir, config, systems, profiles, profile_rows, distributions, deformations, errors)
                continue
            for future in done:
                job = futures.pop(future)
                try:
                    payload = future.result()
                    systems.append(payload["system"])
                    profiles.extend(payload["profiles"])
                    profile_rows.extend(payload["profile_rows"])
                    distributions.extend(payload["distributions"])
                    deformations.extend(payload["deformations"])
                except Exception as exc:  # noqa: BLE001
                    errors.append({"job": job, "error": repr(exc)})
                while pending and len(futures) < args.workers:
                    next_job = pending.pop(0)
                    futures[executor.submit(_run_one, next_job)] = next_job
            if len(systems) % max(1, args.checkpoint_every) == 0:
                _write_outputs(out_dir, config, systems, profiles, profile_rows, distributions, deformations, errors)
    finally:
        if not timed_out:
            executor.shutdown(wait=True, cancel_futures=False)
    config["status"] = "TIMED_OUT" if timed_out else "COMPLETED"
    _write_outputs(out_dir, config, systems, profiles, profile_rows, distributions, deformations, errors)
    (out_dir / "config.json").write_text(json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"out_dir": str(out_dir), "systems": len(systems), "profiles": len(profiles), "errors": len(errors), "status": config["status"]}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
