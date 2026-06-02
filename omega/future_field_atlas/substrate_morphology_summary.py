"""Build a compact morphology atlas from retained Future Field Atlas outputs."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Iterable

from .util import canonical_json, read_csv, stable_hash, utc_now, write_csv, write_json


NUMERIC_METRICS = (
    "joint_support_residual_fraction",
    "joint_retention_fraction",
    "A_marginal_retention_fraction",
    "B_marginal_retention_fraction",
    "coupled_joint_support_count",
    "product_joint_support_count",
    "joint_density_vs_marginal_product",
)

CLAIM_BOUNDARY = (
    "substrate morphology summary only: no Omega, agency, identity, valuerhood, "
    "value, compatibility, support, capture, erasure, or interaction claim"
)


@dataclass(frozen=True)
class RunRef:
    run_id: str
    path: Path


@dataclass
class CoupledRun:
    ref: RunRef
    status: dict[str, object]
    config: dict[str, object]
    operator: dict[str, object]
    retention: dict[str, object]
    residual_rows: list[dict[str, object]]
    marginal_rows: list[dict[str, object]]
    profile_rows: list[dict[str, object]]
    spool_rows: list[dict[str, object]]
    audit_rows: list[dict[str, object]]
    completeness_rows: list[dict[str, object]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize Future Field Atlas substrate morphology.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--runs",
        nargs="*",
        default=[],
        help="Run directories, optionally label=path. Directories may be coupled runs or summary bundles.",
    )
    parser.add_argument(
        "--run",
        action="append",
        default=[],
        help="Additional run directory, optionally label=path. This mirrors older summary utilities.",
    )
    parser.add_argument(
        "--run-manifest",
        type=Path,
        default=None,
        help="Optional JSON or newline manifest of run directories.",
    )
    parser.add_argument(
        "--include-existing-retention-summaries",
        action="store_true",
        help="Prefer retained compact artifacts when root artifacts are missing.",
    )
    parser.add_argument("--write-report", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_refs = parse_run_refs(args.runs + args.run, args.run_manifest)
    result = build_substrate_morphology_summary(
        out_dir=args.out,
        run_refs=run_refs,
        include_existing_retention_summaries=bool(args.include_existing_retention_summaries),
        write_report=bool(args.write_report),
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def build_substrate_morphology_summary(
    *,
    out_dir: Path,
    run_refs: list[RunRef],
    include_existing_retention_summaries: bool = False,
    write_report: bool = False,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    coupled_runs = [
        load_coupled_run(run_ref, include_existing_retention_summaries=include_existing_retention_summaries)
        for run_ref in run_refs
        if is_coupled_run_dir(run_ref.path, include_existing_retention_summaries=include_existing_retention_summaries)
    ]
    summary_dirs = [
        run_ref for run_ref in run_refs
        if not is_coupled_run_dir(run_ref.path, include_existing_retention_summaries=include_existing_retention_summaries)
    ]

    field_rows = field_morphology_rows(coupled_runs)
    pair_rows = pair_morphology_rows(coupled_runs)
    operator_rows = operator_sensitivity_rows(coupled_runs)
    onset_rows = horizon_onset_rows(coupled_runs)
    observable_rows = observable_geometry_rows(coupled_runs)
    exemplar_rows = pair_class_exemplar_rows(pair_rows, onset_rows)
    target_rows = morphology_next_target_rows(pair_rows, observable_rows)
    crossing_rows = joint_candidate_crossing_rows(summary_dirs)
    growth_rows = frontier_growth_regime_rows(coupled_runs)
    composition_rows = composition_residual_rows()
    rank_rows = rank_boundary_offset_rows(summary_dirs)

    outputs = {
        "field_morphology_summary.csv": field_rows,
        "pair_morphology_summary.csv": pair_rows,
        "operator_sensitivity_summary.csv": operator_rows,
        "horizon_onset_summary.csv": onset_rows,
        "observable_geometry_summary.csv": observable_rows,
        "pair_class_exemplar_summary.csv": exemplar_rows,
        "morphology_next_targets.csv": target_rows,
        "rank_boundary_offset_morphology.csv": rank_rows,
        "joint_candidate_crossing_morphology.csv": crossing_rows,
        "composition_residual_morphology.csv": composition_rows,
        "frontier_growth_regime_summary.csv": growth_rows,
    }
    for filename, rows in outputs.items():
        write_csv(out_dir / filename, rows)

    manifest = {
        "created_utc": utc_now(),
        "instrument": "future_field_atlas_substrate_morphology_summary",
        "instrument_role": "postprocess_retained_future_field_atlas_outputs",
        "source_run_count": len(coupled_runs),
        "source_summary_dir_count": len(summary_dirs),
        "source_runs": [
            {
                "run_id": run.ref.run_id,
                "path": str(run.ref.path),
                "status": run.status.get("status", ""),
                "horizon_max": run.config.get("horizon_max", ""),
                "joint_selection_family": run.config.get("joint_selection_family", ""),
                "coupling_strength": run.config.get("coupling_strength", ""),
            }
            for run in coupled_runs
        ],
        "source_summary_dirs": [{"run_id": ref.run_id, "path": str(ref.path)} for ref in summary_dirs],
        "output_files": sorted(outputs),
        "claim_boundary": CLAIM_BOUNDARY,
        "manifest_digest": stable_hash(
            {
                "runs": [(run.ref.run_id, run.config.get("horizon_max"), run.config.get("coupling_strength")) for run in coupled_runs],
                "outputs": sorted(outputs),
            },
            length=24,
        ),
    }
    write_json(out_dir / "substrate_morphology_manifest.json", manifest)
    if write_report:
        write_morphology_report(
            out_dir / "substrate_morphology_report.md",
            coupled_runs=coupled_runs,
            summary_dirs=summary_dirs,
            field_rows=field_rows,
            pair_rows=pair_rows,
            operator_rows=operator_rows,
            onset_rows=onset_rows,
            observable_rows=observable_rows,
            exemplar_rows=exemplar_rows,
            target_rows=target_rows,
        )
    return manifest


def is_coupled_run_dir(path: Path, *, include_existing_retention_summaries: bool) -> bool:
    return bool(resolve_artifact_path(path, "coupled_future_field_atlas_status.json", include_existing_retention_summaries))


def load_coupled_run(run_ref: RunRef, *, include_existing_retention_summaries: bool) -> CoupledRun:
    path = run_ref.path
    return CoupledRun(
        ref=run_ref,
        status=read_json_artifact(path, "coupled_future_field_atlas_status.json", include_existing_retention_summaries),
        config=read_json_artifact(path, "coupled_future_field_atlas_run_config.json", include_existing_retention_summaries),
        operator=first_row(read_csv_artifact(path, "coupled_operator_manifest.csv.gz", include_existing_retention_summaries)),
        retention=read_json_optional(path / "_retention_summary" / "retained_run_summary.json"),
        residual_rows=read_csv_artifact(path, "coupled_joint_vs_product_residual_by_horizon.csv.gz", include_existing_retention_summaries),
        marginal_rows=read_csv_artifact(path, "coupled_marginal_retention_by_horizon.csv.gz", include_existing_retention_summaries),
        profile_rows=read_csv_artifact(path, "coupled_joint_frontier_profile_by_horizon.csv.gz", include_existing_retention_summaries),
        spool_rows=read_csv_artifact(path, "coupled_pair_spool_manifest.csv.gz", include_existing_retention_summaries),
        audit_rows=read_csv_artifact(path, "coupled_reconstruction_audit_summary.csv.gz", include_existing_retention_summaries),
        completeness_rows=read_csv_artifact(path, "coupled_artifact_completeness_summary.csv.gz", include_existing_retention_summaries),
    )


def field_morphology_rows(runs: list[CoupledRun]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for run in runs:
        profile_index = group_rows(run.profile_rows, ("pair_id", "start_index", "joint_scan_mode"))
        for (_pair_id, start_index, scan_mode), profile_rows in sorted(profile_index.items()):
            if scan_mode != "product_baseline":
                continue
            for side in ("A", "B"):
                side_rows = complete_rows(profile_rows)
                if not side_rows:
                    continue
                first = horizon_row(side_rows, 0)
                final = final_horizon_row(side_rows)
                counts = [float_value(row.get(f"{side}_marginal_state_count")) for row in side_rows]
                template = final or first or side_rows[0]
                h0 = float_value((first or {}).get(f"{side}_marginal_state_count"))
                h_final = float_value((final or {}).get(f"{side}_marginal_state_count"))
                h_max = max(counts) if counts else 0.0
                rows.append(
                    {
                        "run_id": run.ref.run_id,
                        "field_side": side,
                        "condition_id": template.get(f"{side}_condition_id", ""),
                        "start_index": start_index,
                        "state_space_id": template.get(f"{side}_substrate_id", ""),
                        "law_id": template.get(f"{side}_law_id", ""),
                        "selection_operator_id": template.get(f"{side}_selection_operator_id", ""),
                        "observable_set_id": run.config.get("macro_invariant_kind", ""),
                        "horizon_max": run.config.get("horizon_max", ""),
                        "artifact_completeness_status": run.status.get("artifact_completeness_statuses", ""),
                        "reconstruction_audit_status": audit_status(run.audit_rows),
                        "frontier_count_h0": h0,
                        "frontier_count_h_final": h_final,
                        "frontier_count_max": h_max,
                        "frontier_growth_ratio_final_vs_h0": safe_fraction(h_final, h0),
                        "frontier_growth_ratio_max_vs_h0": safe_fraction(h_max, h0),
                        "frontier_entropy_final": "",
                        "frontier_entropy_max": "",
                        "component_count_final": "",
                        "component_count_max": "",
                        "largest_component_fraction_final": "",
                        "rank_boundary_inside_fraction_mean": "",
                        "rank_boundary_outside_fraction_mean": "",
                        "transport_composition_residual_mean": "",
                        "transport_composition_residual_max": "",
                    }
                )
    return rows


def pair_morphology_rows(runs: list[CoupledRun]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for run in runs:
        spool_by_pair = {short_pair_id(row): row for row in run.spool_rows}
        residual_by_pair = group_complete_rows(run.residual_rows, ("pair_id",))
        marginal_by_pair = group_complete_rows(run.marginal_rows, ("pair_id",))
        coupled_profile_by_pair = group_complete_rows(
            [row for row in run.profile_rows if row.get("joint_scan_mode") == "coupled"],
            ("pair_id",),
        )
        for (raw_pair_id,), residual_rows in sorted(residual_by_pair.items(), key=lambda item: short_pair_id_value(item[0][0])):
            pair_id = short_pair_id_value(raw_pair_id)
            marginal_rows = marginal_by_pair.get((raw_pair_id,), [])
            profile_rows = coupled_profile_by_pair.get((raw_pair_id,), [])
            residual_final = final_horizon_row(residual_rows)
            marginal_final = final_horizon_row(marginal_rows)
            profile_final = final_horizon_row(profile_rows)
            spool = spool_by_pair.get(pair_id, {})
            edge_rows = int_value(spool.get("edge_rows"))
            node_rows = int_value(spool.get("node_rows"))
            row = {
                "run_id": run.ref.run_id,
                "pair_id": pair_id,
                "pair_index": pair_index(pair_id),
                "operator_family": operator_family(run),
                "coupled_operator_id": run.operator.get("coupled_operator_id", ""),
                "joint_selection_family": run.config.get("joint_selection_family", ""),
                "coupling_strength": run.config.get("coupling_strength", ""),
                "horizon_max": run.config.get("horizon_max", ""),
                "artifact_completeness_status": run.status.get("artifact_completeness_statuses", ""),
                "reconstruction_audit_status": audit_status(run.audit_rows),
                "product_joint_support_final": int_value(residual_final.get("product_joint_support_count")),
                "coupled_joint_support_final": int_value(residual_final.get("coupled_joint_support_count")),
                "joint_support_residual_final": float_value(residual_final.get("joint_support_residual_fraction")),
                "joint_support_residual_mean": mean_metric(residual_rows, "joint_support_residual_fraction"),
                "joint_support_residual_max": max_metric(residual_rows, "joint_support_residual_fraction"),
                "joint_retention_final": float_value(marginal_final.get("joint_retention_fraction")),
                "joint_retention_mean": mean_metric(marginal_rows, "joint_retention_fraction"),
                "joint_retention_min": min_metric(marginal_rows, "joint_retention_fraction"),
                "A_marginal_retention_final": float_value(marginal_final.get("A_marginal_retention_fraction")),
                "B_marginal_retention_final": float_value(marginal_final.get("B_marginal_retention_fraction")),
                "A_marginal_retention_mean": mean_metric(marginal_rows, "A_marginal_retention_fraction"),
                "B_marginal_retention_mean": mean_metric(marginal_rows, "B_marginal_retention_fraction"),
                "joint_density_vs_marginal_product_final": float_value(profile_final.get("joint_density_vs_marginal_product")),
                "joint_density_vs_marginal_product_mean": mean_metric(profile_rows, "joint_density_vs_marginal_product"),
                "frontier_node_rows": node_rows,
                "frontier_edge_rows": edge_rows,
                "output_size_mb_if_available": output_size_mb(run, pair_id),
            }
            row["joint_residual_class"] = residual_class(float_value(row["joint_support_residual_final"]))
            row["marginal_retention_class"] = marginal_retention_class(
                float_value(row["A_marginal_retention_final"]),
                float_value(row["B_marginal_retention_final"]),
            )
            row["joint_density_class"] = density_class(float_value(row["joint_density_vs_marginal_product_final"]))
            rows.append(row)
    apply_size_classes(rows)
    return rows


def operator_sensitivity_rows(runs: list[CoupledRun]) -> list[dict[str, object]]:
    metric_index: dict[tuple[str, str, int, str], float] = {}
    digest_index = {run.ref.run_id: compact_digest(run) for run in runs}
    meta = {run.ref.run_id: run for run in runs}
    for run in runs:
        for key, values in run_metric_values(run).items():
            pair_id, horizon, metric = key
            metric_index[(run.ref.run_id, pair_id, horizon, metric)] = values

    comparisons = comparison_pairs(runs)
    rows: list[dict[str, object]] = []
    for baseline_id, comparison_id in comparisons:
        baseline_run = meta[baseline_id]
        comparison_run = meta[comparison_id]
        keys = [
            key for key in metric_index
            if key[0] == baseline_id
            and (comparison_id, key[1], key[2], key[3]) in metric_index
        ]
        for _run_id, pair_id, horizon, metric_name in sorted(keys, key=lambda item: (item[1], item[2], item[3])):
            baseline_value = metric_index[(baseline_id, pair_id, horizon, metric_name)]
            comparison_value = metric_index[(comparison_id, pair_id, horizon, metric_name)]
            delta = comparison_value - baseline_value
            rows.append(
                {
                    "comparison_id": f"{comparison_id}_vs_{baseline_id}",
                    "pair_id": pair_id,
                    "baseline_operator": operator_label(baseline_run),
                    "comparison_operator": operator_label(comparison_run),
                    "baseline_coupling_strength": baseline_run.config.get("coupling_strength", ""),
                    "comparison_coupling_strength": comparison_run.config.get("coupling_strength", ""),
                    "horizon": horizon,
                    "metric_name": metric_name,
                    "baseline_value": baseline_value,
                    "comparison_value": comparison_value,
                    "delta": delta,
                    "relative_delta": safe_fraction(delta, abs(baseline_value)) if baseline_value else "",
                    "same_compact_digest_flag_if_available": int(digest_index[baseline_id] == digest_index[comparison_id]),
                }
            )
    return rows


def horizon_onset_rows(runs: list[CoupledRun]) -> list[dict[str, object]]:
    meta = {run.ref.run_id: run for run in runs}
    metric_index: dict[tuple[str, str, int, str], float] = {}
    for run in runs:
        for key, value in run_metric_values(run).items():
            pair_id, horizon, metric = key
            metric_index[(run.ref.run_id, pair_id, horizon, metric)] = value
    rows: list[dict[str, object]] = []
    for baseline_id, comparison_id in comparison_pairs(runs):
        comparison_run = meta[comparison_id]
        horizon_max = int_value(comparison_run.config.get("horizon_max"))
        for metric_name in NUMERIC_METRICS:
            pair_ids = sorted({
                key[1] for key in metric_index
                if key[0] == baseline_id
                and key[3] == metric_name
            })
            for pair_id in pair_ids:
                horizons = sorted({
                    key[2] for key in metric_index
                    if key[0] == baseline_id
                    and key[1] == pair_id
                    and key[3] == metric_name
                    and (comparison_id, pair_id, key[2], metric_name) in metric_index
                })
                if not horizons:
                    continue
                deltas = [
                    (
                        horizon,
                        abs(
                            metric_index[(comparison_id, pair_id, horizon, metric_name)]
                            - metric_index[(baseline_id, pair_id, horizon, metric_name)]
                        ),
                        metric_index[(comparison_id, pair_id, horizon, metric_name)],
                    )
                    for horizon in horizons
                ]
                threshold = 1e-12
                crossing = next((horizon for horizon, delta, _value in deltas if delta > threshold), "")
                max_horizon, max_delta, max_value = max(deltas, key=lambda item: item[1])
                final_horizon, _final_delta, final_value = max(deltas, key=lambda item: item[0])
                rows.append(
                    {
                        "run_id": comparison_id,
                        "pair_id": pair_id,
                        "operator_family": operator_family(comparison_run),
                        "coupling_strength": comparison_run.config.get("coupling_strength", ""),
                        "comparison_reference": baseline_id,
                        "metric_name": metric_name,
                        "threshold": threshold,
                        "first_horizon_crossing_threshold": crossing,
                        "max_delta_horizon": max_horizon,
                        "final_horizon_value": final_value if final_horizon == horizon_max else final_value,
                        "max_horizon_value": max_value,
                        "onset_class": onset_class(int_value(crossing), horizon_max, max_delta),
                    }
                )
    return rows


def observable_geometry_rows(runs: list[CoupledRun]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [
        {
            "observable_id": "observable_coverage",
            "observable_family": "coverage_status",
            "run_id": "atlas",
            "condition_or_pair_id": "all",
            "horizon_max": "",
            "geometry_metric": "observable_coverage",
            "value_mean": "",
            "value_max": "",
            "value_final": "",
            "artifact_completeness_status": "",
            "notes": "single_observable_only: symbol_histogram_distance is the only law observable present in retained coupled runs",
        }
    ]
    for run in runs:
        observable_id = str(run.config.get("macro_invariant_kind", "")) or "unknown"
        for pair_key, residual_rows in group_complete_rows(run.residual_rows, ("pair_id",)).items():
            pair_id = short_pair_id_value(pair_key[0])
            marginal_rows = group_complete_rows(run.marginal_rows, ("pair_id",)).get(pair_key, [])
            profile_rows = group_complete_rows(
                [row for row in run.profile_rows if row.get("joint_scan_mode") == "coupled"],
                ("pair_id",),
            ).get(pair_key, [])
            for metric, source_rows, field in (
                ("joint_support_residual_fraction", residual_rows, "joint_support_residual_fraction"),
                ("joint_retention_fraction", marginal_rows, "joint_retention_fraction"),
                ("A_marginal_retention_fraction", marginal_rows, "A_marginal_retention_fraction"),
                ("B_marginal_retention_fraction", marginal_rows, "B_marginal_retention_fraction"),
                ("joint_density_vs_marginal_product", profile_rows, "joint_density_vs_marginal_product"),
            ):
                rows.append(
                    {
                        "observable_id": observable_id,
                        "observable_family": "macro_invariant_law_observable",
                        "run_id": run.ref.run_id,
                        "condition_or_pair_id": pair_id,
                        "horizon_max": run.config.get("horizon_max", ""),
                        "geometry_metric": metric,
                        "value_mean": mean_metric(source_rows, field),
                        "value_max": max_metric(source_rows, field),
                        "value_final": float_value(final_horizon_row(source_rows).get(field)),
                        "artifact_completeness_status": run.status.get("artifact_completeness_statuses", ""),
                        "notes": "observable_coverage: single_observable_only",
                    }
                )
    return rows


def pair_class_exemplar_rows(pair_rows: list[dict[str, object]], onset_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if not pair_rows:
        return rows

    def add(reason: str, row: dict[str, object], followup: str) -> None:
        rows.append(
            {
                "pair_id": row.get("pair_id", ""),
                "class_reason": reason,
                "run_id": row.get("run_id", ""),
                "operator_family": row.get("operator_family", ""),
                "coupling_strength": row.get("coupling_strength", ""),
                "horizon": row.get("horizon_max", ""),
                "joint_residual": row.get("joint_support_residual_final", ""),
                "joint_retention": row.get("joint_retention_final", ""),
                "A_marginal_retention": row.get("A_marginal_retention_final", ""),
                "B_marginal_retention": row.get("B_marginal_retention_final", ""),
                "edge_rows": row.get("frontier_edge_rows", ""),
                "node_rows": row.get("frontier_node_rows", ""),
                "recommended_followup": followup,
            }
        )

    add("heaviest_pair", max(pair_rows, key=lambda row: float_value(row.get("frontier_edge_rows"))), "include_as_scale_stress_exemplar")
    add("highest_joint_residual", max(pair_rows, key=lambda row: float_value(row.get("joint_support_residual_final"))), "shared_capacity_or_rank_order_native_probe")
    add("lowest_joint_retention", min(pair_rows, key=lambda row: float_value(row.get("joint_retention_final"))), "shared_capacity_or_rank_order_native_probe")
    preserving_restrictive = [
        row for row in pair_rows
        if row.get("marginal_retention_class") == "marginal_preserving"
        and row.get("joint_density_class") == "joint_restrictive"
    ]
    if preserving_restrictive:
        add("marginal_preserving_joint_restrictive", max(preserving_restrictive, key=lambda row: float_value(row.get("joint_support_residual_final"))), "small_shared_capacity_h64_smoke")
    stable_low = [row for row in pair_rows if row.get("joint_residual_class") == "low_residual"]
    if stable_low:
        add("stable_low_residual", min(stable_low, key=lambda row: float_value(row.get("joint_support_residual_final"))), "negative_control_pair_for_next_operator")
    pair005_rows = [row for row in pair_rows if row.get("pair_id") == "pair005"]
    if pair005_rows:
        add("pair005_like", max(pair005_rows, key=lambda row: float_value(row.get("joint_support_residual_final"))), "retain_as_forensic_exemplar_not_branch_basis_alone")
    late_pairs = {
        row.get("pair_id"): row
        for row in onset_rows
        if row.get("onset_class") in {"late_onset", "terminal_only"}
        and row.get("metric_name") == "joint_support_residual_fraction"
    }
    if late_pairs:
        pair_id = sorted(late_pairs)[0]
        candidates = [row for row in pair_rows if row.get("pair_id") == pair_id]
        if candidates:
            add("late_onset_divergence", candidates[0], "horizon_depth_check")
    return dedupe_rows(rows)


def morphology_next_target_rows(pair_rows: list[dict[str, object]], observable_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    high_preserving = [
        row for row in pair_rows
        if row.get("marginal_retention_class") == "marginal_preserving"
        and float_value(row.get("joint_support_residual_final")) >= 0.4
    ]
    high_pair_ids = sorted({str(row.get("pair_id")) for row in high_preserving})[:8]
    low_control_ids = sorted({
        str(row.get("pair_id")) for row in pair_rows
        if row.get("joint_residual_class") == "low_residual"
        and row.get("marginal_retention_class") == "marginal_preserving"
    })[:3]
    medium_control_ids = sorted({
        str(row.get("pair_id")) for row in pair_rows
        if row.get("joint_residual_class") == "medium_residual"
    })[:3]
    exemplar_set = ordered_unique(high_pair_ids + low_control_ids + medium_control_ids)
    exemplar_pairs = ";".join(exemplar_set) if exemplar_set else "select_high_residual_marginal_preserving_pairs_with_low_and_medium_controls"
    pair005_seen = any(row.get("pair_id") == "pair005" for row in pair_rows)
    rows: list[dict[str, object]] = []
    shared_rows = [row for row in pair_rows if row.get("joint_selection_family") == "shared_capacity"]
    rank_order_rows = [row for row in pair_rows if row.get("joint_selection_family") == "rank_order_boundary"]
    rank_order_high_preserving = [
        row for row in rank_order_rows
        if row.get("marginal_retention_class") == "marginal_preserving"
        and row.get("joint_density_class") == "joint_restrictive"
    ]
    rank_order_low_controls = [
        row for row in rank_order_rows
        if row.get("marginal_retention_class") == "marginal_preserving"
        and row.get("joint_residual_class") == "low_residual"
    ]
    if rank_order_high_preserving and rank_order_low_controls:
        rows.append({
            "target_id": "rank_order_boundary_medium_pair_sweep",
            "target_type": "rank_order_native_scale_candidate",
            "reason": "rank_order_boundary produced marginal-preserving joint restriction on a high-residual exemplar while low/medium controls stayed marginal-preserving and low-residual",
            "recommended_operator": "rank_order_boundary",
            "recommended_horizon": "H64_then_targeted_H128",
            "recommended_pairs": exemplar_pairs,
            "required_controls": "product_selector;zero_penalty_joint_selector;scalar_mismatch_0.020;shared_capacity_v1_reference",
            "expected_disambiguation": "tests whether ordinal rank-boundary alignment defines a broader pair morphology class beyond pair005",
            "claim_boundary": CLAIM_BOUNDARY,
        })
    if shared_rows:
        rows.append({
            "target_id": "shared_capacity_v2_marginal_coverage_repair",
            "target_type": "shared_capacity_repair_candidate",
            "reason": "shared_capacity v1 was operational but pruned marginals; only revisit if finite shared capacity remains theory-critical",
            "recommended_operator": "marginal_coverage_preserving_shared_capacity_v2",
            "recommended_horizon": "H32_or_H64",
            "recommended_pairs": exemplar_pairs,
            "required_controls": "shared_capacity_v1;product_selector;rank_order_boundary",
            "expected_disambiguation": "tests whether capacity can restrict joint combinations without erasing component marginal support",
            "claim_boundary": CLAIM_BOUNDARY,
        })
    else:
        rows.append({
            "target_id": "shared_capacity_marginal_preserving_high_residual",
            "target_type": "shared_capacity_candidate",
            "reason": "retained morphology contains preserved-marginal high-residual exemplars; include low and medium controls so pair005 does not anchor the branch alone",
            "recommended_operator": "shared_capacity_coupling",
            "recommended_horizon": "H64",
            "recommended_pairs": exemplar_pairs,
            "required_controls": "product_selector;zero_penalty_joint_selector;matched_pair_set",
            "expected_disambiguation": "tests whether finite shared continuation capacity explains joint restriction better than scalar mismatch strength",
            "claim_boundary": CLAIM_BOUNDARY,
        })
    if not rank_order_rows:
        rows.append({
            "target_id": "rank_order_native_operator",
            "target_type": "rank_order_native_candidate",
            "reason": "near-zero scalar ladder changes quickly and saturates; rank order may be the native control surface",
            "recommended_operator": "rank_boundary_ordering_operator",
            "recommended_horizon": "H64",
            "recommended_pairs": ";".join(exemplar_set[:4]) if exemplar_set else "pair005_plus_two_low_residual_controls",
            "required_controls": "product_selector;scalar_mismatch_0.020;low_residual_pair_controls",
            "expected_disambiguation": "separates scalar penalty magnitude from ordinal candidate ordering",
            "claim_boundary": CLAIM_BOUNDARY,
        })
    rows.append({
        "target_id": "observable_extension",
        "target_type": "observable_extension",
        "reason": "current retained coupled morphology is single-observable only",
        "recommended_operator": "none_postprocessing_or_small_rescan",
        "recommended_horizon": "H32_or_H64",
        "recommended_pairs": "representative_low_medium_high_residual_pairs",
        "required_controls": "paired_baselines;artifact_completeness;reconstruction_audits",
        "expected_disambiguation": "checks whether morphology is tied to symbol_histogram_distance only",
        "claim_boundary": CLAIM_BOUNDARY,
    })
    if pair005_seen:
        rows.append(
            {
                "target_id": "pair005_threshold_bracket",
                "target_type": "pair_forensics",
                "reason": "pair005 is a repeat high-residual exemplar and should not anchor a branch without neighbors",
                "recommended_operator": "current_joint_rank_prefix_scalar_bracket",
                "recommended_horizon": "H64",
                "recommended_pairs": "pair005;nearest_high_residual_neighbors;low_residual_control",
                "required_controls": "0.002_to_0.005_bracket;product_selector;zero_penalty_joint_selector",
                "expected_disambiguation": "tests whether pair005 is unique or part of a morphology class",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def joint_candidate_crossing_rows(summary_dirs: list[RunRef]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for ref in summary_dirs:
        for row in read_csv(ref.path / "joint_candidate_crossing_summary.csv"):
            copied = dict(row)
            copied["source_summary_id"] = ref.run_id
            rows.append(copied)
    return rows or [{"status": "not_available_from_retained_inputs", "notes": "selected-candidate crossing requires a mechanism summary or raw selected-edge comparison"}]


def rank_boundary_offset_rows(summary_dirs: list[RunRef]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in joint_candidate_crossing_rows(summary_dirs):
        if "rank_boundary_offset_distribution_left" in row or "rank_boundary_offset_distribution_right" in row:
            rows.append(
                {
                    "source_summary_id": row.get("source_summary_id", ""),
                    "comparison": row.get("comparison", ""),
                    "pair_id": row.get("pair_id", ""),
                    "left_label": row.get("left_label", ""),
                    "right_label": row.get("right_label", ""),
                    "rank_boundary_offset_distribution_left": row.get("rank_boundary_offset_distribution_left", ""),
                    "rank_boundary_offset_distribution_right": row.get("rank_boundary_offset_distribution_right", ""),
                    "notes": row.get("limitation", "selected topology only"),
                }
            )
    return rows or [{"status": "not_available_from_retained_inputs"}]


def composition_residual_rows() -> list[dict[str, object]]:
    return [
        {
            "status": "not_available_from_retained_inputs",
            "notes": "transport composition residuals are not emitted by current coupled compact runs; joint-vs-product support residuals are summarized separately",
        }
    ]


def frontier_growth_regime_rows(runs: list[CoupledRun]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for run in runs:
        for key, profile_rows in group_complete_rows(run.profile_rows, ("pair_id", "joint_scan_mode")).items():
            pair_id = short_pair_id_value(key[0])
            mode = key[1]
            first = horizon_row(profile_rows, 0)
            final = final_horizon_row(profile_rows)
            counts = [float_value(row.get("joint_frontier_state_count")) for row in profile_rows]
            h0 = float_value((first or {}).get("joint_frontier_state_count"))
            h_final = float_value((final or {}).get("joint_frontier_state_count"))
            h_max = max(counts) if counts else 0.0
            rows.append(
                {
                    "run_id": run.ref.run_id,
                    "pair_id": pair_id,
                    "joint_scan_mode": mode,
                    "horizon_max": run.config.get("horizon_max", ""),
                    "frontier_count_h0": h0,
                    "frontier_count_h_final": h_final,
                    "frontier_count_max": h_max,
                    "frontier_growth_ratio_final_vs_h0": safe_fraction(h_final, h0),
                    "frontier_growth_ratio_max_vs_h0": safe_fraction(h_max, h0),
                    "growth_regime": growth_regime(safe_fraction(h_final, h0), safe_fraction(h_max, h0)),
                    "artifact_completeness_status": run.status.get("artifact_completeness_statuses", ""),
                }
            )
    return rows


def run_metric_values(run: CoupledRun) -> dict[tuple[str, int, str], float]:
    values: dict[tuple[str, int, str], float] = {}
    for row in complete_rows(run.residual_rows):
        pair_id = short_pair_id_value(row.get("pair_id"))
        horizon = int_value(row.get("horizon"))
        for metric in ("joint_support_residual_fraction", "coupled_joint_support_count", "product_joint_support_count"):
            values[(pair_id, horizon, metric)] = float_value(row.get(metric))
    for row in complete_rows(run.marginal_rows):
        pair_id = short_pair_id_value(row.get("pair_id"))
        horizon = int_value(row.get("horizon"))
        for metric in ("joint_retention_fraction", "A_marginal_retention_fraction", "B_marginal_retention_fraction"):
            values[(pair_id, horizon, metric)] = float_value(row.get(metric))
    for row in complete_rows([row for row in run.profile_rows if row.get("joint_scan_mode") == "coupled"]):
        pair_id = short_pair_id_value(row.get("pair_id"))
        horizon = int_value(row.get("horizon"))
        values[(pair_id, horizon, "joint_density_vs_marginal_product")] = float_value(row.get("joint_density_vs_marginal_product"))
    return values


def comparison_pairs(runs: list[CoupledRun]) -> list[tuple[str, str]]:
    by_horizon: dict[int, list[CoupledRun]] = defaultdict(list)
    for run in runs:
        by_horizon[int_value(run.config.get("horizon_max"))].append(run)
    comparisons: list[tuple[str, str]] = []
    for grouped in by_horizon.values():
        product = next((run for run in grouped if run.config.get("joint_selection_family") == "product"), None)
        zero = next(
            (
                run for run in grouped
                if run.config.get("joint_selection_family") == "joint_energy_rank_prefix"
                and abs(float_value(run.config.get("coupling_strength"))) <= 1e-12
            ),
            None,
        )
        positives = sorted(
            [
                run for run in grouped
                if run.config.get("joint_selection_family") == "joint_energy_rank_prefix"
                and float_value(run.config.get("coupling_strength")) > 0
            ],
            key=lambda run: float_value(run.config.get("coupling_strength")),
        )
        non_product_operators = sorted(
            [
                run for run in grouped
                if run.config.get("joint_selection_family") != "product"
            ],
            key=lambda run: (
                str(run.config.get("joint_selection_family", "")),
                float_value(run.config.get("coupling_strength")),
                run.ref.run_id,
            ),
        )
        if product and zero:
            comparisons.append((product.ref.run_id, zero.ref.run_id))
        if product:
            comparisons.extend(
                (product.ref.run_id, run.ref.run_id)
                for run in non_product_operators
                if run.ref.run_id != (zero.ref.run_id if zero else "")
            )
        if zero:
            comparisons.extend(
                (zero.ref.run_id, run.ref.run_id)
                for run in non_product_operators
                if run.ref.run_id != zero.ref.run_id
            )
    return dedupe_pairs(comparisons)


def compact_digest(run: CoupledRun) -> str:
    payload = {
        "residual": normalized_rows(run.residual_rows),
        "marginal": normalized_rows(run.marginal_rows),
        "profile": normalized_rows(run.profile_rows),
    }
    return stable_hash(payload, length=24)


def normalized_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    ignored = {"coupled_operator_id", "coupled_operator_family", "coupling_strength"}
    normalized = []
    for row in rows:
        normalized.append({
            key: value
            for key, value in row.items()
            if key not in ignored and not str(key).startswith("coupled_operator")
        })
    return sorted(normalized, key=lambda row: canonical_json(row))


def write_morphology_report(
    path: Path,
    *,
    coupled_runs: list[CoupledRun],
    summary_dirs: list[RunRef],
    field_rows: list[dict[str, object]],
    pair_rows: list[dict[str, object]],
    operator_rows: list[dict[str, object]],
    onset_rows: list[dict[str, object]],
    observable_rows: list[dict[str, object]],
    exemplar_rows: list[dict[str, object]],
    target_rows: list[dict[str, object]],
) -> None:
    clean_runs = [
        run for run in coupled_runs
        if run.status.get("status") == "COMPLETED"
        and int_value(run.status.get("coupled_pairs_failed")) == 0
        and int_value(run.status.get("internal_cap_events")) == 0
        and str(run.status.get("artifact_completeness_statuses", "")) == "complete"
        and int_value(run.status.get("reconstruction_audit_clean_pass")) == 1
    ]
    high_rows = [row for row in pair_rows if row.get("joint_residual_class") == "high_residual"]
    preserving_high = [
        row for row in high_rows
        if row.get("marginal_retention_class") == "marginal_preserving"
    ]
    pair005_rows = [row for row in pair_rows if row.get("pair_id") == "pair005"]
    product_comparisons = [
        row for row in operator_rows
        if str(row.get("baseline_operator", "")).startswith("product")
    ]
    first_target = target_rows[0] if target_rows else {}
    lines = [
        "# Future Field Atlas Substrate Morphology Atlas Result",
        "",
        "Status: completed as a retained-output postprocess",
        "",
        "## Summary",
        "",
        (
            f"The morphology atlas ingested {len(coupled_runs)} coupled Future Field Atlas run "
            f"directories and {len(summary_dirs)} compact summary directories. "
            f"{len(clean_runs)} coupled runs passed the clean infrastructure gates used here."
        ),
        "",
        "Allowed claim:",
        "",
        "```text",
        "The current finite Future Field Atlas substrate has a usable morphology map over retained coupled outputs.",
        "It separates product-selector behavior, zero-penalty joint rank-prefix behavior, positive scalar penalties, pair-level residual structure, horizon onset, and observable coverage.",
        "```",
        "",
        "Blocked claims:",
        "",
        "```text",
        "Omega validation",
        "agency / identity / valuerhood / value",
        "compatibility detection",
        "support / capture / erasure",
        "interaction detection",
        "```",
        "",
        "## Inputs And Retained Runs",
        "",
        "Primary inputs were existing compact coupled outputs; no new broad scan was run.",
        "",
        "```text",
        *[run.ref.run_id for run in coupled_runs],
        "```",
        "",
        "## Gate And Completeness Status",
        "",
        f"Clean runs: {len(clean_runs)} / {len(coupled_runs)}",
        "",
        "All retained coupled runs used in the morphology tables are kept descriptive. Rows with missing compact data are left blank rather than reconstructed from deleted raw spools.",
        "",
        "## Field Morphology",
        "",
        f"Field-equivalent rows emitted: {len(field_rows)}.",
        "",
        "Field rows are inferred from component marginal counts inside the coupled product-baseline profiles. Entropy, component topology, and transport-composition fields remain blank where those summaries were not retained.",
        "",
        "## Pair Morphology",
        "",
        f"Pair morphology rows emitted: {len(pair_rows)}.",
        f"High-residual descriptive rows: {len(high_rows)}.",
        f"High-residual rows with preserved component marginals: {len(preserving_high)}.",
        "",
        "Pair005 remains a high-yield forensic exemplar, but the atlas treats it as an exemplar to compare against neighbors, not as a branch basis by itself.",
        "",
        "## Operator Sensitivity",
        "",
        f"Operator sensitivity rows emitted: {len(operator_rows)}.",
        f"Product-vs-joint comparison rows emitted: {len(product_comparisons)}.",
        "",
        "The product selector remains the true product-equivalence reference. Zero-penalty joint rank-prefix selection is a separate operator and should not be treated as product-neutral.",
        "",
        "## Horizon Onset",
        "",
        f"Horizon onset rows emitted: {len(onset_rows)}.",
        "",
        "Onset rows record first metric divergence from the selected comparison reference. They are descriptive timing markers, not semantic labels.",
        "",
        "## Observable Coverage",
        "",
        "Observable coverage is currently single-observable only for retained coupled runs: `symbol_histogram_distance` is the law observable available in these compact outputs.",
        "",
        "## Pair Exemplars",
        "",
        "Recommended exemplar table rows:",
        "",
    ]
    for row in exemplar_rows[:12]:
        lines.append(
            f"- {row.get('class_reason')}: {row.get('pair_id')} "
            f"({row.get('run_id')}, residual {row.get('joint_residual')}, "
            f"retention {row.get('joint_retention')})"
        )
    lines.extend(
        [
            "",
            "## Recommended Next Targets",
            "",
        ]
    )
    for row in target_rows:
        lines.append(
            f"- `{row.get('target_id')}`: {row.get('recommended_operator')} at {row.get('recommended_horizon')} "
            f"on `{row.get('recommended_pairs')}`."
        )
    lines.extend(
        [
            "",
            "Most useful next target:",
            "",
            "```text",
            str(first_target.get("target_id", "")),
            "```",
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_run_refs(raw_runs: list[str], manifest: Path | None) -> list[RunRef]:
    values = list(raw_runs)
    if manifest is not None and manifest.exists():
        if manifest.suffix.lower() == ".json":
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                values.extend(str(item) for item in payload)
            elif isinstance(payload, dict):
                values.extend(str(item) for item in payload.get("runs", []))
        else:
            values.extend(line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip())
    refs: list[RunRef] = []
    for raw in values:
        if not raw:
            continue
        if "=" in raw:
            run_id, path_text = raw.split("=", 1)
            path = Path(path_text)
        else:
            path = Path(raw)
            run_id = path.name
        refs.append(RunRef(run_id=safe_run_id(run_id), path=path))
    return refs


def resolve_artifact_path(run_dir: Path, filename: str, include_existing_retention_summaries: bool) -> Path | None:
    direct = run_dir / filename
    if direct.exists():
        return direct
    if include_existing_retention_summaries:
        retained = run_dir / "_retention_summary" / "compact_artifacts" / filename
        if retained.exists():
            return retained
    return None


def read_json_artifact(run_dir: Path, filename: str, include_existing_retention_summaries: bool) -> dict[str, object]:
    path = resolve_artifact_path(run_dir, filename, include_existing_retention_summaries)
    return read_json_optional(path) if path is not None else {}


def read_csv_artifact(run_dir: Path, filename: str, include_existing_retention_summaries: bool) -> list[dict[str, object]]:
    path = resolve_artifact_path(run_dir, filename, include_existing_retention_summaries)
    return read_csv(path) if path is not None else []


def read_json_optional(path: Path | None) -> dict[str, object]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def complete_rows(rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    return [row for row in rows if row.get("feature_status", "complete") == "complete"]


def group_complete_rows(rows: Iterable[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[str, ...], list[dict[str, object]]]:
    return group_rows(complete_rows(rows), keys)


def group_rows(rows: Iterable[dict[str, object]], keys: tuple[str, ...]) -> dict[tuple[str, ...], list[dict[str, object]]]:
    grouped: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(str(row.get(key, "")) for key in keys)].append(row)
    return grouped


def first_row(rows: list[dict[str, object]]) -> dict[str, object]:
    return rows[0] if rows else {}


def horizon_row(rows: list[dict[str, object]], horizon: int) -> dict[str, object]:
    for row in rows:
        if int_value(row.get("horizon")) == horizon:
            return row
    return {}


def final_horizon_row(rows: list[dict[str, object]]) -> dict[str, object]:
    if not rows:
        return {}
    return max(rows, key=lambda row: int_value(row.get("horizon")))


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


def safe_fraction(numerator: float, denominator: float) -> float | str:
    if denominator == 0:
        return ""
    return numerator / denominator


def safe_run_id(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return token.strip("_") or "run"


def short_pair_id(row: dict[str, object]) -> str:
    return short_pair_id_value(row.get("pair_id", ""))


def short_pair_id_value(value: object) -> str:
    return str(value).split("__", 1)[0]


def pair_index(pair_id_value: object) -> int:
    match = re.search(r"pair(\d+)", str(pair_id_value))
    return int(match.group(1)) if match else -1


def audit_status(rows: list[dict[str, object]]) -> str:
    statuses = sorted({str(row.get("status", "")) for row in rows if row.get("status", "")})
    return ";".join(statuses)


def operator_family(run: CoupledRun) -> str:
    return str(run.operator.get("coupled_operator_family", run.config.get("joint_selection_family", "")))


def operator_label(run: CoupledRun) -> str:
    family = str(run.config.get("joint_selection_family", ""))
    strength = run.config.get("coupling_strength", "")
    return f"{family}@{strength}"


def output_size_mb(run: CoupledRun, pair_id: str) -> float | str:
    pair_skew = read_csv(run.ref.path / "_retention_summary" / "retained_pair_skew.csv.gz")
    for row in pair_skew:
        if short_pair_id(row) == pair_id:
            size_gib = float_value(row.get("spool_size_gib"))
            return round(size_gib * 1024, 6)
    total = float_value(run.retention.get("total_output_size_gib"))
    realized = int_value(run.status.get("pair_count_realized"))
    if total and realized:
        return round(total * 1024 / realized, 6)
    return ""


def residual_class(value: float) -> str:
    if value < 0.1:
        return "low_residual"
    if value < 0.4:
        return "medium_residual"
    return "high_residual"


def marginal_retention_class(a_value: float, b_value: float) -> str:
    a_loss = a_value < 0.98
    b_loss = b_value < 0.98
    if a_loss and b_loss:
        return "marginal_loss_both"
    if a_loss:
        return "marginal_loss_A"
    if b_loss:
        return "marginal_loss_B"
    return "marginal_preserving"


def density_class(value: float) -> str:
    if value >= 0.9:
        return "product_dense"
    if value < 0.5:
        return "joint_restrictive"
    return "product_sparse"


def apply_size_classes(rows: list[dict[str, object]]) -> None:
    values = sorted(float_value(row.get("frontier_edge_rows")) for row in rows)
    if not values:
        return
    lower = values[len(values) // 3]
    upper = values[(2 * len(values)) // 3]
    for row in rows:
        value = float_value(row.get("frontier_edge_rows"))
        if value <= lower:
            row["pair_size_class"] = "light"
        elif value <= upper:
            row["pair_size_class"] = "medium"
        else:
            row["pair_size_class"] = "heavy"


def onset_class(first_horizon: int, horizon_max: int, max_delta: float) -> str:
    if max_delta <= 1e-12 or first_horizon <= 0:
        return "no_detected_onset"
    if first_horizon == horizon_max:
        return "terminal_only"
    ratio = first_horizon / max(1, horizon_max)
    if ratio <= 0.25:
        return "early_onset"
    if ratio <= 0.75:
        return "mid_onset"
    return "late_onset"


def growth_regime(final_ratio: float | str, max_ratio: float | str) -> str:
    if not isinstance(final_ratio, float) or not isinstance(max_ratio, float):
        return "unavailable"
    if max_ratio <= 1.0:
        return "flat"
    if final_ratio < max_ratio * 0.5:
        return "transient_peak"
    if final_ratio >= max_ratio * 0.95:
        return "monotone_or_plateau_growth"
    return "growth_then_partial_contraction"


def dedupe_pairs(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    output: list[tuple[str, str]] = []
    for pair in pairs:
        if pair not in seen:
            output.append(pair)
            seen.add(pair)
    return output


def dedupe_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[str] = set()
    output: list[dict[str, object]] = []
    for row in rows:
        key = canonical_json(row)
        if key not in seen:
            output.append(row)
            seen.add(key)
    return output


def ordered_unique(values: Iterable[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            output.append(value)
            seen.add(value)
    return output


if __name__ == "__main__":
    main()
