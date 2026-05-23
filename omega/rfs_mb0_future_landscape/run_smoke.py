from __future__ import annotations

import argparse
import csv
import json
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime
from pathlib import Path
from statistics import median, mean

from .controls import null_bundle_distribution_by_h, null_transition_metrics
from .landscape import edge_deformations, future_profile
from .probes import generate_probes
from .substrate import FAMILIES, generate_system

NULL_OR_CONTROL_FAMILIES = {
    "random_relation_control",
    "degree_preserving_control",
    "coordinate_permutation_control",
    "phase_cycle_control",
    "fixed_point_control",
    "permissive_probe_control",
    "strict_probe_control",
}

HORIZON_GRIDS = {
    "default": (0, 1, 2, 4, 8, 12, 16),
    "dense_early": tuple(range(17)),
    "long_5x": (0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 16, 24, 32, 48, 64, 80),
    "long_10x": (0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 16, 24, 32, 48, 64, 80, 96, 128, 160),
    "long_100x": (0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 16, 24, 32, 48, 64, 80, 96, 128, 160, 224, 320, 512, 768, 1024),
}


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
    parser.add_argument("--horizon-grid", choices=sorted(HORIZON_GRIDS), default="default")
    parser.add_argument("--horizons", type=str, default="")
    return parser.parse_args()


def _run_one(job: dict[str, object]) -> dict[str, object]:
    started = time.perf_counter()
    system = generate_system(int(job["seed"]), str(job["family"]))
    probes = generate_probes(system, int(job["sigma"]))
    horizons = tuple(int(value) for value in job["horizons"])
    start_count = int(job["start_samples"])
    starts = [system.states[(system.seed + i * 17) % len(system.states)] for i in range(start_count)]
    profiles = []
    profile_rows = []
    transition_rows = []
    distributions = []
    deformations = []
    for probe in probes:
        for start in starts:
            null_bundle_by_h = null_bundle_distribution_by_h(system, probe, start, horizons)
            null_transitions = null_transition_metrics(system, probe, start, horizons)
            profile, rows, dist_rows = future_profile(
                system,
                start,
                probe,
                null_bundle_by_h.get("degree", {}),
                null_bundle_by_h,
                null_transitions,
                horizons,
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
        "horizons_json": json.dumps(horizons),
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
    horizons = _resolve_horizons(args)
    jobs = []
    for family in families:
        for seed_index in range(args.seeds_per_family):
            jobs.append(
                {
                    "seed": _seed_for(family, seed_index),
                    "family": family,
                    "sigma": args.sigma,
                    "start_samples": args.start_samples,
                    "horizons": horizons,
                }
            )
    return jobs


def _resolve_horizons(args: argparse.Namespace) -> tuple[int, ...]:
    if args.horizons.strip():
        values = tuple(sorted({int(item.strip()) for item in args.horizons.split(",") if item.strip()}))
    else:
        values = HORIZON_GRIDS[args.horizon_grid]
    if not values or values[0] != 0:
        raise ValueError("horizon grid must include 0")
    return values


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


def _median(values: list[object]) -> float:
    return median(float(value) for value in values) if values else 0.0


def _lower_quartile(values: list[object]) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return 0.0
    return ordered[len(ordered) // 4]


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


def _aggregate_probe_family_classes(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["family"]), str(row["probe_family"])), []).append(row)
    out = []
    for (family, probe_family), items in sorted(grouped.items()):
        summary = _aggregate_metrics(items)
        summary["family"] = family
        summary["probe_family"] = probe_family
        summary["aggregate_probe_family_class_v1_1"] = _aggregate_probe_family_class(family, summary)
        out.append(summary)
    return out


def _aggregate_family_classes(rows: list[dict[str, object]], probe_family_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    passing_probe_counts: dict[str, int] = {}
    for row in probe_family_rows:
        if row["aggregate_probe_family_class_v1_1"] == "structured_propagation":
            passing_probe_counts[str(row["family"])] = passing_probe_counts.get(str(row["family"]), 0) + 1
    for row in rows:
        grouped.setdefault(str(row["family"]), []).append(row)
    out = []
    for family, items in sorted(grouped.items()):
        summary = _aggregate_metrics(items)
        summary["family"] = family
        summary["passing_probe_family_count"] = passing_probe_counts.get(family, 0)
        summary["aggregate_family_class_v1_1"] = _aggregate_family_class(family, summary)
        out.append(summary)
    return out


def _aggregate_metrics(items: list[dict[str, object]]) -> dict[str, object]:
    local_candidate_flags = [int(item["local_profile_class_v1_1"] == "local_structured_candidate") for item in items]
    null_mimic_flags = [int(item["control_relative_profile_class_v1"] == "null_mimic") for item in items]
    mi_deltas = [item["MI_delta_vs_null"] for item in items]
    motif_deltas = [item["signature_transition_motif_reuse_delta_vs_null"] for item in items]
    return {
        "n_profiles": len(items),
        "local_candidate_fraction": _mean(local_candidate_flags),
        "saturation_dominated_fraction": _mean([item["saturation_dominated"] for item in items]),
        "null_mimic_fraction": _mean(null_mimic_flags),
        "mean_transition_MI": _mean([item["signature_transition_MI_mean"] for item in items]),
        "mean_MI_delta_vs_null": _mean(mi_deltas),
        "median_MI_delta_vs_null": _median(mi_deltas),
        "lower_quartile_MI_delta_vs_null": _lower_quartile(mi_deltas),
        "mean_motif_delta_vs_null": _mean(motif_deltas),
        "median_motif_delta_vs_null": _median(motif_deltas),
        "lower_quartile_motif_delta_vs_null": _lower_quartile(motif_deltas),
        "mean_JS_bundle": _mean([item["JS_to_null_bundle_mean"] for item in items]),
        "mean_KL_bundle": _mean([item["KL_to_null_bundle_mean"] for item in items]),
        "mean_reach_saturation_fraction": _mean([item["reach_saturation_fraction"] for item in items]),
        "mean_exact_saturation_fraction": _mean([item["exact_saturation_fraction"] for item in items]),
        "mean_signature_transition_motif_reuse": _mean([item["signature_transition_motif_reuse_mean"] for item in items]),
        "mean_signature_transition_conditional_entropy": _mean([item["signature_transition_conditional_entropy_mean"] for item in items]),
    }


def _aggregate_probe_family_class(family: str, row: dict[str, object]) -> str:
    if family in NULL_OR_CONTROL_FAMILIES:
        return "control_local_candidates" if float(row["local_candidate_fraction"]) > 0 else "control_no_pass"
    if float(row["saturation_dominated_fraction"]) >= 0.50 or float(row["mean_reach_saturation_fraction"]) >= 0.95:
        return "saturation_dominated"
    if (
        float(row["local_candidate_fraction"]) >= 0.50
        and float(row["mean_MI_delta_vs_null"]) > 0.05
        and float(row["median_MI_delta_vs_null"]) > 0.0
        and float(row["mean_motif_delta_vs_null"]) > 0.02
    ):
        return "structured_propagation"
    if float(row["local_candidate_fraction"]) > 0:
        return "local_only"
    return "underdetermined"


def _aggregate_family_class(family: str, row: dict[str, object]) -> str:
    if family in NULL_OR_CONTROL_FAMILIES:
        return "control_local_candidates" if float(row["local_candidate_fraction"]) > 0 else "control_no_pass"
    if float(row["saturation_dominated_fraction"]) >= 0.50 or float(row["mean_reach_saturation_fraction"]) >= 0.95:
        return "saturation_dominated"
    if (
        float(row["local_candidate_fraction"]) >= 0.50
        and float(row["mean_MI_delta_vs_null"]) > 0.05
        and float(row["median_MI_delta_vs_null"]) > 0.0
        and float(row["mean_motif_delta_vs_null"]) > 0.02
        and int(row.get("passing_probe_family_count", 0)) >= 2
    ):
        return "structured_propagation"
    if int(row.get("passing_probe_family_count", 0)) == 1:
        return "underdetermined_probe_concentrated"
    if float(row["local_candidate_fraction"]) > 0:
        return "local_only"
    return "underdetermined"


def _degree_control_false_positives(probe_family_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in probe_family_rows:
        if row["family"] != "degree_preserving_control":
            continue
        out.append(
            {
                "family": row["family"],
                "probe_family": row["probe_family"],
                "local_false_positive_count": round(float(row["local_candidate_fraction"]) * int(row["n_profiles"])),
                "local_false_positive_fraction": row["local_candidate_fraction"],
                "aggregate_pass": int(row["aggregate_probe_family_class_v1_1"] == "structured_propagation"),
            }
        )
    return out


def _matched_null_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    null_names = sorted(set(
        key[len("null_JS_") :]
        for row in rows
        for key in row
        if key.startswith("null_JS_")
    ))
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        for null_name in null_names:
            grouped.setdefault((str(row["family"]), null_name), []).append(row)
    out = []
    for (family, null_name), items in sorted(grouped.items()):
        out.append(
            {
                "family": family,
                "null_name": null_name,
                "mean_JS": _mean([item.get(f"null_JS_{null_name}", 0.0) for item in items]),
                "mean_KL": _mean([item.get(f"null_KL_{null_name}", 0.0) for item in items]),
                "mean_MI_delta": _mean([item["MI_delta_vs_null"] for item in items]),
                "mean_motif_delta": _mean([item["signature_transition_motif_reuse_delta_vs_null"] for item in items]),
            }
        )
    return out


def _horizon_local_nulls(profile_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "system_id": row["system_id"],
            "family": row["family"],
            "probe_name": row["probe_name"],
            "probe_family": row["probe_family"],
            "H": row["H"],
            "JS_to_null_H": row["JS_to_null"],
            "KL_to_null_H": row["smoothed_KL_to_null"],
            "reach_saturation_fraction_H": row["reach_saturation_fraction_H"],
            "exact_saturation_fraction_H": row["exact_saturation_fraction_H"],
        }
        for row in profile_rows
    ]


def _horizon_window_summary(profile_rows: list[dict[str, object]], transition_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    transition_by_key = {
        (row["system_id"], row["probe_name"], int(row["H"])): row
        for row in transition_rows
    }
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for row in profile_rows:
        h = int(row["H"])
        windows = _windows_for_horizon(row, h)
        transition = transition_by_key.get((row["system_id"], row["probe_name"], h), {})
        merged = {**row, **transition}
        for window in windows:
            grouped.setdefault((str(row["family"]), str(row["probe_family"]), window), []).append(merged)
    out = []
    for (family, probe_family, window), items in sorted(grouped.items()):
        summary = {
            "family": family,
            "probe_family": probe_family,
            "window": window,
            "n": len(items),
            "mean_transition_MI_H": _mean([item.get("signature_transition_MI_by_h", 0.0) for item in items]),
            "median_transition_MI_H": _median([item.get("signature_transition_MI_by_h", 0.0) for item in items]),
            "mean_transition_conditional_entropy_H": _mean([item.get("signature_transition_conditional_entropy_by_h", 0.0) for item in items]),
            "mean_transition_motif_reuse_H": _mean([item.get("signature_transition_motif_reuse_by_h", 0.0) for item in items]),
            "mean_JS_to_null_H": _mean([item.get("JS_to_null", 0.0) for item in items]),
            "mean_KL_to_null_H": _mean([item.get("smoothed_KL_to_null", 0.0) for item in items]),
            "saturation_fraction": _mean([float(item.get("reach_saturation_fraction_H", 0.0)) >= 0.95 for item in items]),
            "cycle_fraction": _mean([item.get("control_relative_profile_class_v1") == "cycle_like" for item in items]),
        }
        summary["aggregate_window_class_v1_2"] = _window_class(summary)
        out.append(summary)
    return out


def _windows_for_horizon(row: dict[str, object], h: int) -> list[str]:
    reach_sat = float(row.get("reach_saturation_fraction_H", 0.0))
    windows = []
    if h <= 4:
        windows.append("early_window")
    if reach_sat < 0.95:
        windows.append("pre_saturation_window")
    if 0.75 <= reach_sat < 0.95:
        windows.append("near_saturation_window")
    if reach_sat >= 0.95:
        windows.append("post_saturation_window")
    return windows or ["undetermined_window"]


def _window_class(row: dict[str, object]) -> str:
    if float(row["saturation_fraction"]) >= 0.50:
        return "saturation_dominated_window"
    if float(row["cycle_fraction"]) >= 0.50:
        return "cycle_dominated_window"
    if float(row["mean_transition_MI_H"]) > 0.25 and float(row["mean_JS_to_null_H"]) > 0.10:
        return "structured_candidate_window"
    if float(row["mean_JS_to_null_H"]) <= 0.05:
        return "null_mimic_window"
    return "underdetermined_window"


def _saturation_onset_by_family(profile_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in profile_rows:
        grouped.setdefault(str(row["family"]), []).append(row)
    out = []
    for family, items in sorted(grouped.items()):
        horizons = sorted({int(item["H"]) for item in items})
        mean_by_h = {
            h: _mean([item["reach_saturation_fraction_H"] for item in items if int(item["H"]) == h])
            for h in horizons
        }
        saturation = next((h for h in horizons if mean_by_h[h] >= 0.95), None)
        max_non_sat = max((h for h in horizons if mean_by_h[h] < 0.95), default=0)
        out.append(
            {
                "family": family,
                "saturation_onset_H": saturation if saturation is not None else "",
                "frontier_repeat_onset_H": "",
                "max_non_saturated_H": max_non_sat,
                "fast_saturation_flag": int(saturation is not None and saturation <= 16),
                "mean_final_reach_saturation_fraction": mean_by_h[horizons[-1]],
            }
        )
    return out


def _viscosity_diagnostics(profile_rows: list[dict[str, object]], transition_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    profile_by_key = {
        (row["system_id"], row["probe_name"], int(row["H"])): row
        for row in profile_rows
    }
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in transition_rows:
        profile = profile_by_key.get((row["system_id"], row["probe_name"], int(row["H"])), {})
        merged = {**profile, **row}
        grouped.setdefault((str(row["family"]), str(row["probe_family"])), []).append(merged)
    out = []
    for (family, probe_family), items in sorted(grouped.items()):
        positive_mi = [item for item in items if float(item.get("signature_transition_MI_by_h", 0.0)) > 0.05]
        positive_js = [item for item in items if float(item.get("JS_to_null", 0.0)) > 0.05]
        peak_mi = max(items, key=lambda item: float(item.get("signature_transition_MI_by_h", 0.0))) if items else {}
        pre_sat_items = [item for item in items if float(item.get("reach_saturation_fraction_H", 0.0)) < 0.95]
        peak_pre_sat = max((float(item.get("signature_transition_MI_by_h", 0.0)) for item in pre_sat_items), default=0.0)
        first_mi_h = min((int(item["H"]) for item in positive_mi), default="")
        out.append(
            {
                "family": family,
                "probe_family": probe_family,
                "first_nonzero_transition_MI_H": first_mi_h,
                "first_positive_MI_delta_H": first_mi_h,
                "first_positive_motif_delta_H": "",
                "first_JS_separation_H": min((int(item["H"]) for item in positive_js), default=""),
                "peak_MI_delta_H": peak_mi.get("H", ""),
                "peak_motif_delta_H": "",
                "peak_JS_H": max((int(item["H"]) for item in positive_js), default=""),
                "peak_signal_before_saturation": peak_pre_sat,
                "viscous_candidate_flag": int(isinstance(first_mi_h, int) and first_mi_h > 16 and peak_pre_sat > 0.05),
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
    aggregate_probe_family_classes = _aggregate_probe_family_classes(profiles)
    aggregate_family_classes = _aggregate_family_classes(profiles, aggregate_probe_family_classes)
    degree_false_positives = _degree_control_false_positives(aggregate_probe_family_classes)
    matched_null_summary = _matched_null_summary(profiles)
    horizon_local_nulls = _horizon_local_nulls(profile_rows)
    horizon_window_summary = _horizon_window_summary(profile_rows, transition_rows)
    saturation_onset = _saturation_onset_by_family(profile_rows)
    viscosity_diagnostics = _viscosity_diagnostics(profile_rows, transition_rows)
    _write_csv(out_dir / "results.csv", systems)
    _write_csv(out_dir / "future_profiles.csv", profile_rows)
    _write_csv(out_dir / "horizon_local_profiles.csv", profile_rows)
    _write_csv(out_dir / "horizon_local_nulls.csv", horizon_local_nulls)
    _write_csv(out_dir / "transition_information.csv", transition_rows)
    _write_csv(out_dir / "signature_distributions.csv", distributions)
    _write_csv(out_dir / "control_comparison.csv", family_summary)
    _write_csv(out_dir / "profile_classes.csv", class_summary)
    _write_csv(out_dir / "control_relative_profile_classes.csv", v1_class_summary)
    _write_csv(out_dir / "divergence_summary.csv", divergence_summary)
    _write_csv(out_dir / "null_bundle_summary.csv", null_bundle_summary)
    _write_csv(out_dir / "matched_null_summary.csv", matched_null_summary)
    _write_csv(out_dir / "probe_summary.csv", probe_summary)
    _write_csv(out_dir / "saturation_summary.csv", saturation_summary)
    _write_csv(out_dir / "aggregate_family_classes.csv", aggregate_family_classes)
    _write_csv(out_dir / "aggregate_probe_family_classes.csv", aggregate_probe_family_classes)
    _write_csv(out_dir / "degree_control_false_positives.csv", degree_false_positives)
    _write_csv(out_dir / "horizon_window_summary.csv", horizon_window_summary)
    _write_csv(out_dir / "aggregate_window_classes.csv", horizon_window_summary)
    _write_csv(out_dir / "saturation_onset_by_family.csv", saturation_onset)
    _write_csv(out_dir / "viscosity_diagnostics.csv", viscosity_diagnostics)
    _write_csv(out_dir / "deformation_summary.csv", deformation_summary)
    _write_csv(out_dir / "errors.csv", errors)
    status = {
        "status": config.get("status", "RUNNING"),
        "systems_completed": len(systems),
        "profiles_completed": len(profiles),
        "errors": len(errors),
        "degree_control_local_false_positive_count": sum(int(row["local_false_positive_count"]) for row in degree_false_positives),
        "degree_control_probe_family_aggregate_passes": sum(int(row["aggregate_pass"]) for row in degree_false_positives),
        "aggregate_structured_family_count": sum(1 for row in aggregate_family_classes if row["aggregate_family_class_v1_1"] == "structured_propagation"),
        "elapsed_seconds": time.perf_counter() - float(config["started_perf_counter"]),
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "long_horizon_status.json").write_text(json.dumps({**status, "horizons": config.get("resolved_horizons", [])}, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(out_dir, config, systems, profiles, class_summary, v1_class_summary, family_summary, divergence_summary, v1_divergence_summary, deformation_summary, probe_summary, null_bundle_summary, saturation_summary, aggregate_family_classes, aggregate_probe_family_classes, degree_false_positives, matched_null_summary, horizon_window_summary, saturation_onset, viscosity_diagnostics, errors)


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
    aggregate_family_classes: list[dict[str, object]],
    aggregate_probe_family_classes: list[dict[str, object]],
    degree_false_positives: list[dict[str, object]],
    matched_null_summary: list[dict[str, object]],
    horizon_window_summary: list[dict[str, object]],
    saturation_onset: list[dict[str, object]],
    viscosity_diagnostics: list[dict[str, object]],
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
        "## Horizon Grid",
        "",
        "```text",
        ",".join(str(item) for item in config.get("resolved_horizons", [])),
        "```",
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
    lines.extend(["", "## v1.1 Aggregate Family Classes", "", "| family | aggregate class | n | local candidates | saturation | MI delta | median MI delta | motif delta | median motif delta | passing probe families |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"])
    for row in aggregate_family_classes:
        lines.append(
            "| {family} | {klass} | {n} | {local:.3f} | {sat:.3f} | {mi:.3f} | {medmi:.3f} | {motif:.3f} | {medmotif:.3f} | {passing} |".format(
                family=row["family"],
                klass=row["aggregate_family_class_v1_1"],
                n=row["n_profiles"],
                local=float(row["local_candidate_fraction"]),
                sat=float(row["saturation_dominated_fraction"]),
                mi=float(row["mean_MI_delta_vs_null"]),
                medmi=float(row["median_MI_delta_vs_null"]),
                motif=float(row["mean_motif_delta_vs_null"]),
                medmotif=float(row["median_motif_delta_vs_null"]),
                passing=row["passing_probe_family_count"],
            )
        )
    lines.extend(["", "## v1.1 Probe-Family Classes", "", "| family | probe family | aggregate class | n | local candidates | MI delta | motif delta |", "|---|---|---|---:|---:|---:|---:|"])
    for row in aggregate_probe_family_classes:
        lines.append(
            "| {family} | {probe} | {klass} | {n} | {local:.3f} | {mi:.3f} | {motif:.3f} |".format(
                family=row["family"],
                probe=row["probe_family"],
                klass=row["aggregate_probe_family_class_v1_1"],
                n=row["n_profiles"],
                local=float(row["local_candidate_fraction"]),
                mi=float(row["mean_MI_delta_vs_null"]),
                motif=float(row["mean_motif_delta_vs_null"]),
            )
        )
    lines.extend(["", "## Saturation Onset", "", "| family | saturation onset H | max non-saturated H | fast saturation | final reach saturation |", "|---|---:|---:|---:|---:|"])
    for row in saturation_onset:
        lines.append(
            "| {family} | {onset} | {max_h} | {fast} | {final:.3f} |".format(
                family=row["family"],
                onset=row["saturation_onset_H"],
                max_h=row["max_non_saturated_H"],
                fast=row["fast_saturation_flag"],
                final=float(row["mean_final_reach_saturation_fraction"]),
            )
        )
    lines.extend(["", "## Window-Level Classes", "", "| family | probe family | window | class | n | MI H | median MI H | motif reuse H | JS H | saturation | cycle |", "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|"])
    for row in horizon_window_summary[:120]:
        lines.append(
            "| {family} | {probe} | {window} | {klass} | {n} | {mi:.3f} | {medmi:.3f} | {motif:.3f} | {js:.3f} | {sat:.3f} | {cycle:.3f} |".format(
                family=row["family"],
                probe=row["probe_family"],
                window=row["window"],
                klass=row["aggregate_window_class_v1_2"],
                n=row["n"],
                mi=float(row["mean_transition_MI_H"]),
                medmi=float(row["median_transition_MI_H"]),
                motif=float(row["mean_transition_motif_reuse_H"]),
                js=float(row["mean_JS_to_null_H"]),
                sat=float(row["saturation_fraction"]),
                cycle=float(row["cycle_fraction"]),
            )
        )
    lines.extend(["", "## Viscosity Diagnostics", "", "| family | probe family | first MI H | first JS H | peak MI H | peak pre-saturation signal | viscous |", "|---|---|---:|---:|---:|---:|---:|"])
    for row in viscosity_diagnostics:
        lines.append(
            "| {family} | {probe} | {first_mi} | {first_js} | {peak_mi} | {peak:.3f} | {viscous} |".format(
                family=row["family"],
                probe=row["probe_family"],
                first_mi=row["first_nonzero_transition_MI_H"],
                first_js=row["first_JS_separation_H"],
                peak_mi=row["peak_MI_delta_H"],
                peak=float(row["peak_signal_before_saturation"]),
                viscous=row["viscous_candidate_flag"],
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
    lines.extend(["", "## Degree-Control False Positive Audit", "", "| family | probe family | local false positives | local false positive fraction | aggregate pass |", "|---|---|---:|---:|---:|"])
    for row in degree_false_positives:
        lines.append(
            "| {family} | {probe} | {count} | {fraction:.3f} | {passed} |".format(
                family=row["family"],
                probe=row["probe_family"],
                count=row["local_false_positive_count"],
                fraction=float(row["local_false_positive_fraction"]),
                passed=row["aggregate_pass"],
            )
        )
    lines.extend(["", "## Matched Null Summary", "", "| family | null | JS | KL | MI delta | motif delta |", "|---|---|---:|---:|---:|---:|"])
    for row in matched_null_summary:
        lines.append(
            "| {family} | {null} | {js:.3f} | {kl:.3f} | {mi:.3f} | {motif:.3f} |".format(
                family=row["family"],
                null=row["null_name"],
                js=float(row["mean_JS"]),
                kl=float(row["mean_KL"]),
                mi=float(row["mean_MI_delta"]),
                motif=float(row["mean_motif_delta"]),
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
    aggregate_passes = [row for row in aggregate_family_classes if row["aggregate_family_class_v1_1"] == "structured_propagation"]
    degree_passes = [row for row in degree_false_positives if int(row["aggregate_pass"])]
    viscous_count = sum(int(row["viscous_candidate_flag"]) for row in viscosity_diagnostics)
    fast_saturation_count = sum(int(row["fast_saturation_flag"]) for row in saturation_onset)
    gate_status = "passed" if aggregate_passes and not degree_passes else "not passed"
    lines.extend([
        "",
        "## Gate Status",
        "",
        f"- Scientific gate: {gate_status}",
        f"- Aggregate structured families: {len(aggregate_passes)}",
        f"- Degree-control aggregate probe-family passes: {len(degree_passes)}",
        "",
        "## Long-Horizon Gate Read",
        "",
        f"- Are we ending too early? {'possible' if viscous_count else 'not indicated by this run'}",
        f"- Are signals only transient/pre-saturation? {'inspect window classes; saturated families are withheld' if horizon_window_summary else 'not measured'}",
        f"- Are families saturation-dominated? {fast_saturation_count} families saturate within the measured grid",
        f"- Are controls still clean at long horizons? {'yes at aggregate level' if not degree_passes else 'no'}",
        "",
        "## Claim Boundary",
        "",
        "This smoke reports mechanically generated future-landscape probes, transition-level information measures, matched null bundles, local candidates, and aggregate classes only. It does not assign semantic roles or preferred outcomes.",
        "",
        "## Next Recommendation",
        "",
        "- Treat local_structured_candidate as diagnostic only.",
        "- Do not scale until aggregate family classes separate from degree/frontier/saturation-matched controls.",
    ])
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
    config["resolved_horizons"] = list(_resolve_horizons(args))
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
