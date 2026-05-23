from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime
from pathlib import Path
from statistics import mean

from .controls import null_bundle_distribution_by_h, null_transition_metrics
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
    transition_rows = []
    distributions = []
    deformations = []
    for probe in probes:
        for start in starts:
            null_bundle_by_h = null_bundle_distribution_by_h(system, probe, start)
            null_transitions = null_transition_metrics(system, probe, start)
            profile, rows, dist_rows = future_profile(
                system,
                start,
                probe,
                null_bundle_by_h.get("degree", {}),
                null_bundle_by_h,
                null_transitions,
            )
            profiles.append(profile)
            for row in rows:
                if row.get("row_kind") == "transition_information":
                    transition_rows.append(row)
                else:
                    profile_rows.append(row)
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
        "probe_names_json": json.dumps([probe.name for probe in probes]),
        "probe_family_counts_json": json.dumps(_probe_family_counts(probes), sort_keys=True),
        "sigma": int(job["sigma"]),
        "start_count": len(starts),
        "metadata_json": json.dumps(system.metadata, sort_keys=True),
        "job_elapsed_seconds": time.perf_counter() - started,
    }
    return {
        "system": system_row,
        "profiles": profiles,
        "profile_rows": profile_rows,
        "transition_rows": transition_rows,
        "distributions": distributions,
        "deformations": deformations,
    }


def _probe_family_counts(probes: tuple[object, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for probe in probes:
        family = str(getattr(probe, "probe_family"))
        counts[family] = counts.get(family, 0) + 1
    return counts


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
            "adjacent_distribution_similarity",
            "conditional_entropy_proxy",
            "compression_proxy",
            "signature_reuse_fraction",
            "signature_transition_MI_mean",
            "signature_transition_conditional_entropy_mean",
            "signature_transition_entropy_rate_proxy",
            "signature_transition_grammar_size_mean",
            "signature_transition_motif_reuse_mean",
            "MI_delta_vs_null",
            "signature_transition_motif_reuse_delta_vs_null",
            "control_relative_pass_count",
            "JS_to_null_bundle_mean",
            "KL_to_null_bundle_mean",
            "reach_saturation_fraction",
            "exact_saturation_fraction",
            "saturation_dominated",
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


def _probe_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["probe_family"]), str(row["probe_mode"])), []).append(row)
    out = []
    for (probe_family, probe_mode), items in sorted(grouped.items()):
        out.append(
            {
                "probe_family": probe_family,
                "probe_mode": probe_mode,
                "n": len(items),
                "mean_probe_arity": _mean([item["probe_arity"] for item in items]),
                "mean_signature_transition_MI": _mean([item["signature_transition_MI_mean"] for item in items]),
                "mean_signature_transition_motif_reuse": _mean([item["signature_transition_motif_reuse_mean"] for item in items]),
            }
        )
    return out


def _null_bundle_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["family"]), []).append(row)
    out = []
    for family, items in sorted(grouped.items()):
        out.append(
            {
                "family": family,
                "n": len(items),
                "mean_null_JS_degree": _mean([item["null_JS_degree"] for item in items]),
                "mean_null_JS_random": _mean([item["null_JS_random"] for item in items]),
                "mean_null_JS_probe_marginal": _mean([item["null_JS_probe_marginal"] for item in items]),
                "mean_MI_delta_vs_null": _mean([item["MI_delta_vs_null"] for item in items]),
                "mean_motif_delta_vs_null": _mean([item["signature_transition_motif_reuse_delta_vs_null"] for item in items]),
                "mean_control_relative_pass_count": _mean([item["control_relative_pass_count"] for item in items]),
            }
        )
    return out


def _saturation_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["family"]), []).append(row)
    out = []
    for family, items in sorted(grouped.items()):
        out.append(
            {
                "family": family,
                "n": len(items),
                "mean_reach_saturation_fraction": _mean([item["reach_saturation_fraction"] for item in items]),
                "mean_exact_saturation_fraction": _mean([item["exact_saturation_fraction"] for item in items]),
                "mean_saturation_horizon": _mean([item["saturation_horizon"] for item in items]),
                "saturation_dominated_fraction": _mean([item["saturation_dominated"] for item in items]),
            }
        )
    return out


def _write_outputs(
    out_dir: Path,
    config: dict[str, object],
    systems: list[dict[str, object]],
    profiles: list[dict[str, object]],
    profile_rows: list[dict[str, object]],
    transition_rows: list[dict[str, object]],
    distributions: list[dict[str, object]],
    deformations: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    class_summary = _group(profiles, ("family", "profile_class"))
    v1_class_summary = _group(profiles, ("family", "control_relative_profile_class_v1"))
    family_summary = _group(profiles, ("family",))
    divergence_summary = _group(profiles, ("profile_class",))
    v1_divergence_summary = _group(profiles, ("control_relative_profile_class_v1",))
    deformation_summary = _deformation_summary(deformations)
    probe_summary = _probe_summary(profiles)
    null_bundle_summary = _null_bundle_summary(profiles)
    saturation_summary = _saturation_summary(profiles)
    _write_csv(out_dir / "results.csv", systems)
    _write_csv(out_dir / "future_profiles.csv", profile_rows)
    _write_csv(out_dir / "transition_information.csv", transition_rows)
    _write_csv(out_dir / "signature_distributions.csv", distributions)
    _write_csv(out_dir / "control_comparison.csv", family_summary)
    _write_csv(out_dir / "profile_classes.csv", class_summary)
    _write_csv(out_dir / "control_relative_profile_classes.csv", v1_class_summary)
    _write_csv(out_dir / "divergence_summary.csv", divergence_summary)
    _write_csv(out_dir / "null_bundle_summary.csv", null_bundle_summary)
    _write_csv(out_dir / "probe_summary.csv", probe_summary)
    _write_csv(out_dir / "saturation_summary.csv", saturation_summary)
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
    _write_summary(out_dir, config, systems, profiles, class_summary, v1_class_summary, family_summary, divergence_summary, v1_divergence_summary, deformation_summary, probe_summary, null_bundle_summary, saturation_summary, errors)


def _write_summary(
    out_dir: Path,
    config: dict[str, object],
    systems: list[dict[str, object]],
    profiles: list[dict[str, object]],
    class_summary: list[dict[str, object]],
    v1_class_summary: list[dict[str, object]],
    family_summary: list[dict[str, object]],
    divergence_summary: list[dict[str, object]],
    v1_divergence_summary: list[dict[str, object]],
    deformation_summary: list[dict[str, object]],
    probe_summary: list[dict[str, object]],
    null_bundle_summary: list[dict[str, object]],
    saturation_summary: list[dict[str, object]],
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
        "## v0 Heuristic Class Counts",
        "",
        "| family | class | n | entropy | predictive | recurrence | compression | JS null | KL null |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in class_summary:
        lines.append(_profile_line(row, "family", "profile_class"))
    lines.extend(["", "## v1 Control-Relative Class Counts", "", "| family | v1 class | n | transition MI | MI delta | motif delta | pass count | JS bundle | saturation |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"])
    for row in v1_class_summary:
        lines.append(
            "| {family} | {klass} | {n} | {mi:.3f} | {mid:.3f} | {motif:.3f} | {passes:.2f} | {js:.3f} | {sat:.3f} |".format(
                family=row["family"],
                klass=row["control_relative_profile_class_v1"],
                n=row["n"],
                mi=float(row["mean_signature_transition_MI_mean"]),
                mid=float(row["mean_MI_delta_vs_null"]),
                motif=float(row["mean_signature_transition_motif_reuse_delta_vs_null"]),
                passes=float(row["mean_control_relative_pass_count"]),
                js=float(row["mean_JS_to_null_bundle_mean"]),
                sat=float(row["mean_saturation_dominated"]),
            )
        )
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
    lines.extend(["", "## Null Bundle Comparison", "", "| family | n | JS degree | JS random | JS probe marginal | MI delta | motif delta | pass count |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
    for row in null_bundle_summary:
        lines.append(
            "| {family} | {n} | {degree:.3f} | {random:.3f} | {marginal:.3f} | {mi:.3f} | {motif:.3f} | {passes:.2f} |".format(
                family=row["family"],
                n=row["n"],
                degree=float(row["mean_null_JS_degree"]),
                random=float(row["mean_null_JS_random"]),
                marginal=float(row["mean_null_JS_probe_marginal"]),
                mi=float(row["mean_MI_delta_vs_null"]),
                motif=float(row["mean_motif_delta_vs_null"]),
                passes=float(row["mean_control_relative_pass_count"]),
            )
        )
    lines.extend(["", "## Probe Enumeration Summary", "", "| probe family | mode | n | arity | transition MI | motif reuse |", "|---|---|---:|---:|---:|---:|"])
    for row in probe_summary:
        lines.append(
            "| {family} | {mode} | {n} | {arity:.1f} | {mi:.3f} | {motif:.3f} |".format(
                family=row["probe_family"],
                mode=row["probe_mode"],
                n=row["n"],
                arity=float(row["mean_probe_arity"]),
                mi=float(row["mean_signature_transition_MI"]),
                motif=float(row["mean_signature_transition_motif_reuse"]),
            )
        )
    lines.extend(["", "## Saturation Warning", "", "| family | n | reach saturation | exact saturation | saturation horizon | dominated fraction |", "|---|---:|---:|---:|---:|---:|"])
    for row in saturation_summary:
        lines.append(
            "| {family} | {n} | {reach:.3f} | {exact:.3f} | {h:.2f} | {dom:.3f} |".format(
                family=row["family"],
                n=row["n"],
                reach=float(row["mean_reach_saturation_fraction"]),
                exact=float(row["mean_exact_saturation_fraction"]),
                h=float(row["mean_saturation_horizon"]),
                dom=float(row["saturation_dominated_fraction"]),
            )
        )
    lines.extend(["", "## Transition-Level Information Summary", "", "| v1 class | n | transition MI | conditional entropy | entropy-rate proxy | grammar size | motif reuse |", "|---|---:|---:|---:|---:|---:|---:|"])
    for row in v1_divergence_summary:
        lines.append(
            "| {klass} | {n} | {mi:.3f} | {cond:.3f} | {rate:.3f} | {grammar:.1f} | {motif:.3f} |".format(
                klass=row["control_relative_profile_class_v1"],
                n=row["n"],
                mi=float(row["mean_signature_transition_MI_mean"]),
                cond=float(row["mean_signature_transition_conditional_entropy_mean"]),
                rate=float(row["mean_signature_transition_entropy_rate_proxy"]),
                grammar=float(row["mean_signature_transition_grammar_size_mean"]),
                motif=float(row["mean_signature_transition_motif_reuse_mean"]),
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
    lines.extend(["", "## Claim Boundary", "", "This smoke reports mechanically generated future-landscape probes, transition-level information measures, matched null bundles, and control-relative classes only. It does not assign semantic roles or preferred outcomes.", "", "## Next Recommendation", "", "- Treat v1 structured_propagation as provisional only when it separates from matched nulls by the predeclared pass-count rule.", "- If v1 returns null_mimic or saturation_dominated, revise substrate/probes before increasing compute."])
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
    transition_rows: list[dict[str, object]] = []
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
                _write_outputs(out_dir, config, systems, profiles, profile_rows, transition_rows, distributions, deformations, errors)
                continue
            for future in done:
                job = futures.pop(future)
                try:
                    payload = future.result()
                    systems.append(payload["system"])
                    profiles.extend(payload["profiles"])
                    profile_rows.extend(payload["profile_rows"])
                    transition_rows.extend(payload["transition_rows"])
                    distributions.extend(payload["distributions"])
                    deformations.extend(payload["deformations"])
                except Exception as exc:  # noqa: BLE001
                    errors.append({"job": job, "error": repr(exc)})
                while pending and len(futures) < args.workers:
                    next_job = pending.pop(0)
                    futures[executor.submit(_run_one, next_job)] = next_job
            if len(systems) % max(1, args.checkpoint_every) == 0:
                _write_outputs(out_dir, config, systems, profiles, profile_rows, transition_rows, distributions, deformations, errors)
    finally:
        if not timed_out:
            executor.shutdown(wait=True, cancel_futures=False)
    config["status"] = "TIMED_OUT" if timed_out else "COMPLETED"
    _write_outputs(out_dir, config, systems, profiles, profile_rows, transition_rows, distributions, deformations, errors)
    (out_dir / "config.json").write_text(json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"out_dir": str(out_dir), "systems": len(systems), "profiles": len(profiles), "errors": len(errors), "status": config["status"]}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
