"""Postprocess coupled Future Field Atlas mechanism-resolution runs."""

from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from .util import read_csv, stable_hash, write_csv, write_json


COMPACT_TABLES = (
    "coupled_joint_vs_product_residual_by_horizon.csv.gz",
    "coupled_marginal_retention_by_horizon.csv.gz",
    "coupled_marginal_projection_delta_by_horizon.csv.gz",
    "coupled_joint_frontier_profile_by_horizon.csv.gz",
)

IDENTITY_FIELDS = {
    "coupled_operator_id",
    "coupled_operator_family",
    "coupling_strength",
}


@dataclass(frozen=True)
class LabeledRun:
    label: str
    path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize coupled mechanism-resolution runs.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--run",
        action="append",
        default=[],
        help="Labeled run in the form label=path.",
    )
    parser.add_argument("--zero-label", default="0.000")
    parser.add_argument("--product-label", default="product")
    parser.add_argument("--pair-forensic", default="pair005")
    parser.add_argument(
        "--crossing",
        action="append",
        default=[],
        help="Optional selected-edge comparison in the form label:left_label:right_label.",
    )
    parser.add_argument(
        "--crossing-pairs",
        default="pair005",
        help="Comma-separated short pair ids to include in raw selected-edge crossing audits.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = parse_labeled_runs(args.run)
    summaries = build_mechanism_summaries(
        runs=runs,
        out_dir=args.out,
        zero_label=args.zero_label,
        product_label=args.product_label,
        pair_forensic=args.pair_forensic,
        crossing_specs=args.crossing,
        crossing_pairs=tuple(item.strip() for item in args.crossing_pairs.split(",") if item.strip()),
    )
    print(json.dumps(summaries, indent=2, sort_keys=True, default=str))


def build_mechanism_summaries(
    *,
    runs: list[LabeledRun],
    out_dir: Path,
    zero_label: str,
    product_label: str,
    pair_forensic: str,
    crossing_specs: list[str],
    crossing_pairs: tuple[str, ...],
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    run_map = {run.label: run for run in runs}
    loaded = {run.label: load_run(run) for run in runs}
    run_gate_rows = run_gate_summary(loaded)
    ladder_rows = coupling_ladder_summary(loaded)
    pair_rows = pair_level_residual_summary(loaded)
    horizon_rows = horizon_of_divergence_summary(loaded, zero_label=zero_label, product_label=product_label)
    near_zero_rows = near_zero_threshold_summary(loaded, zero_label=zero_label)
    product_rows = product_selector_sanity_summary(loaded, zero_label=zero_label, product_label=product_label)
    pair_forensic_rows = [
        row for row in pair_rows
        if str(row.get("pair_id")) == pair_forensic or str(row.get("pair_id")).endswith(pair_forensic)
    ]
    crossing_rows = joint_candidate_crossing_summary(run_map, crossing_specs, crossing_pairs)

    outputs = {
        "run_gate_summary.csv": run_gate_rows,
        "coupling_ladder_summary.csv": ladder_rows,
        "near_zero_threshold_summary.csv": near_zero_rows,
        "pair_level_residual_summary.csv": pair_rows,
        "pair005_forensic_summary.csv": pair_forensic_rows,
        "product_selector_sanity_summary.csv": product_rows,
        "horizon_of_divergence_summary.csv": horizon_rows,
        "joint_candidate_crossing_summary.csv": crossing_rows,
    }
    for name, rows in outputs.items():
        write_csv(out_dir / name, rows)
    summary = {
        "out_dir": str(out_dir),
        "run_count": len(runs),
        "labels": [run.label for run in runs],
        "zero_label": zero_label,
        "product_label": product_label,
        "pair_forensic": pair_forensic,
        "output_files": sorted(outputs),
    }
    write_json(out_dir / "mechanism_summary_manifest.json", summary)
    return summary


def load_run(run: LabeledRun) -> dict[str, object]:
    return {
        "label": run.label,
        "path": run.path,
        "status": read_json(run.path / "coupled_future_field_atlas_status.json"),
        "config": read_json(run.path / "coupled_future_field_atlas_run_config.json"),
        "retention": read_json(run.path / "_retention_summary" / "retained_run_summary.json"),
        "residual": read_csv(run.path / "coupled_joint_vs_product_residual_by_horizon.csv.gz"),
        "marginal": read_csv(run.path / "coupled_marginal_retention_by_horizon.csv.gz"),
        "projection": read_csv(run.path / "coupled_marginal_projection_delta_by_horizon.csv.gz"),
        "profile": read_csv(run.path / "coupled_joint_frontier_profile_by_horizon.csv.gz"),
    }


def run_gate_summary(loaded: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for label, data in loaded.items():
        status = data["status"]  # type: ignore[assignment]
        config = data["config"]  # type: ignore[assignment]
        retention = data["retention"]  # type: ignore[assignment]
        rows.append({
            "label": label,
            "run_dir": str(data["path"]),
            "status": status.get("status", ""),
            "joint_selection_family": config.get("joint_selection_family", ""),
            "coupling_strength": config.get("coupling_strength", ""),
            "horizon_max": config.get("horizon_max", ""),
            "pair_indexes_resolved": json.dumps(config.get("pair_indexes_resolved", [])),
            "coupled_pairs_completed": int_value(status.get("coupled_pairs_completed")),
            "coupled_pairs_failed": int_value(status.get("coupled_pairs_failed")),
            "internal_cap_events": int_value(status.get("internal_cap_events")),
            "artifact_completeness_statuses": status.get("artifact_completeness_statuses", ""),
            "reconstruction_audit_clean_pass": int_value(status.get("reconstruction_audit_clean_pass")),
            "medium_sweep_interpretation_allowed": int_value(status.get("medium_sweep_interpretation_allowed")),
            "raw_spools_deleted": int_value(retention.get("raw_spools_deleted")),
            "joint_edge_rows": int_value(status.get("joint_edge_rows")),
            "joint_node_rows": int_value(status.get("joint_node_rows")),
        })
    return rows


def coupling_ladder_summary(loaded: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for label, data in loaded.items():
        residual = complete_rows(data["residual"])  # type: ignore[arg-type]
        marginal = complete_rows(data["marginal"])  # type: ignore[arg-type]
        profile = complete_rows(data["profile"])  # type: ignore[arg-type]
        coupled_profiles = [row for row in profile if row.get("joint_scan_mode") == "coupled"]
        product_profiles = [row for row in profile if row.get("joint_scan_mode") == "product_baseline"]
        rows.append({
            "label": label,
            "joint_selection_family": data["config"].get("joint_selection_family", ""),  # type: ignore[index]
            "coupling_strength": data["config"].get("coupling_strength", ""),  # type: ignore[index]
            "residual_mean": mean_metric(residual, "joint_support_residual_fraction"),
            "residual_min": min_metric(residual, "joint_support_residual_fraction"),
            "residual_max": max_metric(residual, "joint_support_residual_fraction"),
            "joint_retention_mean": mean_metric(marginal, "joint_retention_fraction"),
            "joint_retention_min": min_metric(marginal, "joint_retention_fraction"),
            "A_retention_mean": mean_metric(marginal, "A_marginal_retention_fraction"),
            "B_retention_mean": mean_metric(marginal, "B_marginal_retention_fraction"),
            "coupled_frontier_state_mean": mean_metric(coupled_profiles, "joint_frontier_state_count"),
            "product_frontier_state_mean": mean_metric(product_profiles, "joint_frontier_state_count"),
            "joint_edge_rows": int_value(data["status"].get("joint_edge_rows")),  # type: ignore[index]
            "joint_node_rows": int_value(data["status"].get("joint_node_rows")),  # type: ignore[index]
        })
    return rows


def pair_level_residual_summary(loaded: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for label, data in loaded.items():
        residual_by_pair: dict[str, list[dict[str, object]]] = defaultdict(list)
        marginal_by_pair: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in complete_rows(data["residual"]):  # type: ignore[arg-type]
            residual_by_pair[short_pair_id(row)].append(row)
        for row in complete_rows(data["marginal"]):  # type: ignore[arg-type]
            marginal_by_pair[short_pair_id(row)].append(row)
        for pair_id in sorted(residual_by_pair):
            residual_rows = residual_by_pair[pair_id]
            marginal_rows = marginal_by_pair[pair_id]
            final_residual = final_horizon_row(residual_rows)
            final_marginal = final_horizon_row(marginal_rows)
            rows.append({
                "label": label,
                "joint_selection_family": data["config"].get("joint_selection_family", ""),  # type: ignore[index]
                "coupling_strength": data["config"].get("coupling_strength", ""),  # type: ignore[index]
                "pair_id": pair_id,
                "residual_mean": mean_metric(residual_rows, "joint_support_residual_fraction"),
                "residual_max": max_metric(residual_rows, "joint_support_residual_fraction"),
                "residual_final_horizon": float_value(final_residual.get("joint_support_residual_fraction")),
                "joint_retention_mean": mean_metric(marginal_rows, "joint_retention_fraction"),
                "joint_retention_final_horizon": float_value(final_marginal.get("joint_retention_fraction")),
                "A_retention_mean": mean_metric(marginal_rows, "A_marginal_retention_fraction"),
                "B_retention_mean": mean_metric(marginal_rows, "B_marginal_retention_fraction"),
            })
    return rows


def near_zero_threshold_summary(loaded: dict[str, dict[str, object]], *, zero_label: str) -> list[dict[str, object]]:
    if zero_label not in loaded:
        return [{"status": "zero_label_missing", "zero_label": zero_label}]
    zero = loaded[zero_label]
    rows: list[dict[str, object]] = []
    positive_labels = [
        label for label, data in loaded.items()
        if label != zero_label
        and is_numeric_label(label)
        and data["config"].get("joint_selection_family") == "joint_energy_rank_prefix"  # type: ignore[index]
    ]
    positive_labels = sorted(positive_labels, key=label_sort_key)
    first_diff = ""
    first_identical = ""
    reference_positive = positive_labels[0] if positive_labels else ""
    for label in positive_labels:
        identical_to_zero = compact_tables_identical(zero, loaded[label])
        identical_to_first_positive = (
            compact_tables_identical(loaded[reference_positive], loaded[label])
            if reference_positive else False
        )
        if not identical_to_zero and not first_diff:
            first_diff = label
        if identical_to_zero and not first_identical:
            first_identical = label
        rows.append({
            "label": label,
            "zero_label": zero_label,
            "identical_to_zero": int(identical_to_zero),
            "reference_positive_label": reference_positive,
            "identical_to_first_positive": int(identical_to_first_positive),
            "topology_digest": compact_digest(loaded[label]),
        })
    rows.append({
        "label": "decision",
        "zero_label": zero_label,
        "first_positive_differs_from_zero": first_diff,
        "first_positive_identical_to_zero": first_identical,
        "all_positive_identical_to_first_positive": int(
            bool(reference_positive)
            and all(compact_tables_identical(loaded[reference_positive], loaded[label]) for label in positive_labels)
        ),
        "zero_topology_digest": compact_digest(zero),
    })
    return rows


def product_selector_sanity_summary(
    loaded: dict[str, dict[str, object]],
    *,
    zero_label: str,
    product_label: str,
) -> list[dict[str, object]]:
    if product_label not in loaded:
        return [{"status": "product_label_missing", "product_label": product_label}]
    rows: list[dict[str, object]] = []
    product = loaded[product_label]
    rows.append({
        "comparison": f"{product_label}_vs_{zero_label}",
        "left_label": product_label,
        "right_label": zero_label,
        "compact_tables_identical": int(zero_label in loaded and compact_tables_identical(product, loaded[zero_label])),
        "product_residual_mean": mean_metric(complete_rows(product["residual"]), "joint_support_residual_fraction"),  # type: ignore[arg-type]
        "product_residual_max": max_metric(complete_rows(product["residual"]), "joint_support_residual_fraction"),  # type: ignore[arg-type]
        "product_joint_retention_mean": mean_metric(complete_rows(product["marginal"]), "joint_retention_fraction"),  # type: ignore[arg-type]
        "product_A_retention_mean": mean_metric(complete_rows(product["marginal"]), "A_marginal_retention_fraction"),  # type: ignore[arg-type]
        "product_B_retention_mean": mean_metric(complete_rows(product["marginal"]), "B_marginal_retention_fraction"),  # type: ignore[arg-type]
    })
    return rows


def horizon_of_divergence_summary(
    loaded: dict[str, dict[str, object]],
    *,
    zero_label: str,
    product_label: str,
) -> list[dict[str, object]]:
    comparisons: list[tuple[str, str, str]] = []
    if zero_label in loaded:
        for label in sorted(loaded, key=label_sort_key):
            if (
                label != zero_label
                and is_numeric_label(label)
                and loaded[label]["config"].get("joint_selection_family") == "joint_energy_rank_prefix"  # type: ignore[index]
            ):
                comparisons.append((f"{label}_vs_{zero_label}", zero_label, label))
    if product_label in loaded and zero_label in loaded:
        comparisons.append((f"{product_label}_vs_{zero_label}", product_label, zero_label))
    rows: list[dict[str, object]] = []
    for comparison, left_label, right_label in comparisons:
        left = loaded[left_label]
        right = loaded[right_label]
        left_index = residual_index(left)
        right_index = residual_index(right)
        for pair_id in sorted(set(left_index) | set(right_index)):
            first = ""
            max_delta = 0.0
            max_delta_horizon = ""
            for horizon in sorted(set(left_index.get(pair_id, {})) | set(right_index.get(pair_id, {}))):
                delta = abs(
                    float_value(left_index.get(pair_id, {}).get(horizon, {}).get("joint_support_residual_fraction"))
                    - float_value(right_index.get(pair_id, {}).get(horizon, {}).get("joint_support_residual_fraction"))
                )
                if delta > 1e-12 and first == "":
                    first = str(horizon)
                if delta > max_delta:
                    max_delta = delta
                    max_delta_horizon = str(horizon)
            rows.append({
                "comparison": comparison,
                "left_label": left_label,
                "right_label": right_label,
                "pair_id": pair_id,
                "first_horizon_where_residual_differs": first,
                "max_residual_delta": max_delta,
                "max_residual_delta_horizon": max_delta_horizon,
            })
    return rows


def joint_candidate_crossing_summary(
    run_map: dict[str, LabeledRun],
    crossing_specs: list[str],
    crossing_pairs: tuple[str, ...],
) -> list[dict[str, object]]:
    if not crossing_specs:
        return [{
            "status": "not_requested",
            "candidate_crossing_semantics": "selected_edge_set_comparison_only",
        }]
    rows: list[dict[str, object]] = []
    for spec in crossing_specs:
        label, left_label, right_label = parse_crossing_spec(spec)
        if left_label not in run_map or right_label not in run_map:
            rows.append({"comparison": label, "status": "run_label_missing"})
            continue
        left_edges = selected_edge_sets(run_map[left_label].path, crossing_pairs)
        right_edges = selected_edge_sets(run_map[right_label].path, crossing_pairs)
        for pair_id in sorted(set(left_edges) | set(right_edges)):
            left_set = left_edges.get(pair_id, {}).get("edges", set())
            right_set = right_edges.get(pair_id, {}).get("edges", set())
            left_offsets = left_edges.get(pair_id, {}).get("offsets", Counter())
            right_offsets = right_edges.get(pair_id, {}).get("offsets", Counter())
            rows.append({
                "comparison": label,
                "left_label": left_label,
                "right_label": right_label,
                "pair_id": pair_id,
                "status": "ok",
                "candidate_crossing_semantics": "selected_edge_set_comparison_only",
                "selected_at_left_not_right_count": len(left_set - right_set),
                "selected_at_right_not_left_count": len(right_set - left_set),
                "selected_intersection_count": len(left_set & right_set),
                "selected_union_count": len(left_set | right_set),
                "rank_boundary_offset_distribution_left": json.dumps(dict(left_offsets), sort_keys=True),
                "rank_boundary_offset_distribution_right": json.dumps(dict(right_offsets), sort_keys=True),
                "joint_transition_energy_tie_or_near_tie_count": "",
                "rank_order_crossing_count": "",
                "limitation": "nonselected candidate ranks are not emitted by the runner",
            })
    return rows


def selected_edge_sets(run_dir: Path, crossing_pairs: tuple[str, ...]) -> dict[str, dict[str, object]]:
    manifest = read_csv(run_dir / "coupled_pair_spool_manifest.csv.gz")
    output: dict[str, dict[str, object]] = {}
    for row in manifest:
        pair_id = short_pair_id(row)
        if crossing_pairs and pair_id not in crossing_pairs:
            continue
        edge_file = run_dir / str(row.get("edge_file", ""))
        if not edge_file.exists():
            output[pair_id] = {"edges": set(), "offsets": Counter(), "status": "edge_file_missing"}
            continue
        edges: set[str] = set()
        offsets: Counter[str] = Counter()
        with gzip.open(edge_file, "rt", newline="", encoding="utf-8") as handle:
            import csv

            reader = csv.DictReader(handle)
            for edge in reader:
                if edge.get("joint_scan_mode") != "coupled" or edge.get("edge_artifact_status") != "complete":
                    continue
                token = "|".join([
                    pair_id,
                    edge.get("source_horizon", ""),
                    edge.get("target_horizon", ""),
                    edge.get("source_joint_state_id", ""),
                    edge.get("target_joint_state_id", ""),
                ])
                edges.add(stable_hash(token, length=24))
                offsets[f"{edge.get('A_rank_offset_from_boundary', '')}:{edge.get('B_rank_offset_from_boundary', '')}"] += 1
        output[pair_id] = {"edges": edges, "offsets": offsets, "status": "ok"}
    return output


def residual_index(data: dict[str, object]) -> dict[str, dict[int, dict[str, object]]]:
    index: dict[str, dict[int, dict[str, object]]] = defaultdict(dict)
    for row in complete_rows(data["residual"]):  # type: ignore[arg-type]
        index[short_pair_id(row)][int_value(row.get("horizon"))] = row
    return index


def compact_tables_identical(left: dict[str, object], right: dict[str, object]) -> bool:
    return all(normalized_rows(left[name]) == normalized_rows(right[name]) for name in ("residual", "marginal", "projection", "profile"))


def compact_digest(data: dict[str, object]) -> str:
    payload = {
        name: normalized_rows(data[name])
        for name in ("residual", "marginal", "projection", "profile")
    }
    return stable_hash(payload, length=24)


def normalized_rows(rows: object) -> list[dict[str, object]]:
    normalized = []
    for row in rows:  # type: ignore[union-attr]
        normalized.append({
            key: value
            for key, value in row.items()
            if key not in IDENTITY_FIELDS and not str(key).startswith("coupled_operator")
        })
    return sorted(
        normalized,
        key=lambda row: tuple((key, str(row.get(key, ""))) for key in sorted(row)),
    )


def parse_labeled_runs(raw_runs: list[str]) -> list[LabeledRun]:
    runs: list[LabeledRun] = []
    for raw in raw_runs:
        if "=" not in raw:
            raise ValueError(f"expected label=path run spec, got {raw!r}")
        label, path = raw.split("=", 1)
        runs.append(LabeledRun(label=label, path=Path(path)))
    return runs


def parse_crossing_spec(raw: str) -> tuple[str, str, str]:
    parts = raw.split(":")
    if len(parts) != 3:
        raise ValueError(f"expected label:left:right crossing spec, got {raw!r}")
    return parts[0], parts[1], parts[2]


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def complete_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [row for row in rows if row.get("feature_status", "complete") == "complete"]


def final_horizon_row(rows: list[dict[str, object]]) -> dict[str, object]:
    if not rows:
        return {}
    return max(rows, key=lambda row: int_value(row.get("horizon")))


def short_pair_id(row: dict[str, object]) -> str:
    return str(row.get("pair_id", "")).split("__")[0]


def mean_metric(rows: list[dict[str, object]], field: str) -> float:
    values = [float_value(row.get(field)) for row in rows if numberish(row.get(field))]
    return mean(values) if values else 0.0


def min_metric(rows: list[dict[str, object]], field: str) -> float:
    values = [float_value(row.get(field)) for row in rows if numberish(row.get(field))]
    return min(values) if values else 0.0


def max_metric(rows: list[dict[str, object]], field: str) -> float:
    values = [float_value(row.get(field)) for row in rows if numberish(row.get(field))]
    return max(values) if values else 0.0


def int_value(value: object) -> int:
    if value in {"", None}:
        return 0
    return int(float(str(value)))


def float_value(value: object) -> float:
    if value in {"", None}:
        return 0.0
    return float(str(value))


def numberish(value: object) -> bool:
    if value in {"", None}:
        return False
    try:
        float(str(value))
    except ValueError:
        return False
    return True


def label_sort_key(label: str) -> tuple[int, float | str]:
    try:
        return (0, float(label))
    except ValueError:
        return (1, label)


def is_numeric_label(label: str) -> bool:
    try:
        float(label)
    except ValueError:
        return False
    return True


if __name__ == "__main__":
    main()
