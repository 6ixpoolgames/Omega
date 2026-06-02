"""Formal-interface distinction panel for coupled Future Field Atlas runs.

This module postprocesses retained coupled FFA artifacts into declared finite
distinction-measure rows. It intentionally reports measurements and gaps only;
interpretation belongs to downstream theory notes.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .util import read_csv, stable_hash, utc_now, write_csv, write_json


DEFAULT_PAIRS = (
    "pair005",
    "pair012",
    "pair014",
    "pair026",
    "pair000",
    "pair001",
    "pair002",
    "pair045",
)
DEFAULT_OPERATOR_LABELS = (
    "product_selector",
    "zero_penalty_joint_rank_prefix",
    "scalar_mismatch_0.020",
    "shared_capacity_v1",
    "rank_order_boundary",
)
REFERENCE_COMPARISONS = (
    ("rank_order_boundary", "product_selector"),
    ("rank_order_boundary", "zero_penalty_joint_rank_prefix"),
    ("rank_order_boundary", "scalar_mismatch_0.020"),
    ("rank_order_boundary", "shared_capacity_v1"),
    ("scalar_mismatch_0.020", "product_selector"),
    ("shared_capacity_v1", "product_selector"),
)
DELTA_METRICS = (
    "joint_support_residual_fraction",
    "joint_retention_fraction",
    "A_marginal_retention_fraction",
    "B_marginal_retention_fraction",
    "joint_density_vs_marginal_product",
    "coupled_joint_support_count",
    "product_joint_support_count",
)
CLAIM_BOUNDARY = "finite distinction-measure geometry only; no semantic promotion"
REPORT_BLOCKED_SENTENCE = (
    "This is not a proto-valuer, valuer, compatibility, support, capture, erasure, "
    "or Omega result."
)


@dataclass(frozen=True)
class LabeledRun:
    operator_label: str
    path: Path


@dataclass(frozen=True)
class Thresholds:
    marginal_preserving: float = 0.99
    joint_restrictive_density: float = 0.50
    high_residual: float = 0.40

    def as_json(self) -> str:
        return json.dumps(
            {
                "marginal_preserving": {
                    "A_marginal_retention_fraction_gte": self.marginal_preserving,
                    "B_marginal_retention_fraction_gte": self.marginal_preserving,
                },
                "joint_restrictive": {
                    "joint_density_vs_marginal_product_lte": self.joint_restrictive_density,
                },
                "high_residual": {
                    "joint_support_residual_fraction_gte": self.high_residual,
                },
            },
            sort_keys=True,
            separators=(",", ":"),
        )


@dataclass(frozen=True)
class CellKey:
    pair_id: str
    operator_label: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a formal-interface distinction panel from coupled FFA runs."
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--run",
        action="append",
        default=[],
        help="Labeled run in the form operator_label=path.",
    )
    parser.add_argument(
        "--runs",
        nargs="*",
        default=[],
        help="Unlabeled run directories. Operator labels are inferred from run config.",
    )
    parser.add_argument("--pairs", default=",".join(DEFAULT_PAIRS))
    parser.add_argument("--operator-labels", default=",".join(DEFAULT_OPERATOR_LABELS))
    parser.add_argument("--include-existing-retention-summaries", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--gzip-compresslevel", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pairs = parse_csv_arg(args.pairs) or list(DEFAULT_PAIRS)
    operator_labels = parse_csv_arg(args.operator_labels) or list(DEFAULT_OPERATOR_LABELS)
    runs = parse_labeled_runs(args.run) + [
        LabeledRun(infer_operator_label(Path(path)), Path(path)) for path in args.runs
    ]
    result = build_panel(
        out_dir=args.out,
        runs=runs,
        pairs=pairs,
        operator_labels=operator_labels,
        thresholds=Thresholds(),
        write_report=bool(args.write_report),
        gzip_compresslevel=max(1, min(9, int(args.gzip_compresslevel))),
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def build_panel(
    *,
    out_dir: Path,
    runs: list[LabeledRun],
    pairs: list[str],
    operator_labels: list[str],
    thresholds: Thresholds,
    write_report: bool = True,
    gzip_compresslevel: int = 1,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    loaded_runs = [load_run(run) for run in runs]
    cells = build_cells(loaded_runs, pairs=pairs, operator_labels=operator_labels)

    candidate_rows = candidate_designation_manifest(pairs)
    measure_manifest_rows = distinction_measure_manifest(thresholds)
    condition_rows = condition_panel_rows(cells, pairs=pairs, operator_labels=operator_labels)
    missing_rows = missing_cell_rows(cells, pairs=pairs, operator_labels=operator_labels)
    retention_rows = joint_vs_marginal_rows(cells, thresholds=thresholds)
    distinction_rows = distinction_measure_rows(
        cells,
        pairs=pairs,
        operator_labels=operator_labels,
        thresholds=thresholds,
    )
    persistence_rows = horizon_signature_persistence_rows(retention_rows)
    delta_rows = operator_reference_delta_rows(cells, pairs=pairs)
    summary_rows = representative_control_summary_rows(
        cells,
        retention_rows=retention_rows,
        persistence_rows=persistence_rows,
        pairs=pairs,
        operator_labels=operator_labels,
    )

    outputs = {
        "candidate_designation_manifest.csv": candidate_rows,
        "distinction_measure_manifest.csv": measure_manifest_rows,
        "formal_interface_condition_panel.csv": condition_rows,
        "formal_interface_missing_cells.csv": missing_rows,
        "joint_vs_marginal_distinction_retention.csv": retention_rows,
        "distinction_measure_by_horizon.csv": distinction_rows,
        "horizon_signature_persistence.csv": persistence_rows,
        "operator_reference_delta_by_horizon.csv": delta_rows,
        "representative_control_signature_summary.csv": summary_rows,
    }
    for name, rows in outputs.items():
        write_csv(out_dir / name, rows, gzip_compresslevel=gzip_compresslevel)

    manifest = {
        "created_utc": utc_now(),
        "panel_id": "formal_interface_distinction_panel",
        "panel_digest": stable_hash(
            {
                "pairs": pairs,
                "operator_labels": operator_labels,
                "runs": [(run.operator_label, str(run.path)) for run in runs],
                "thresholds": thresholds.as_json(),
            },
            length=24,
        ),
        "source_spec": "docs/specs/current/FUTURE_FIELD_ATLAS_FORMAL_INTERFACE_DISTINCTION_PANEL_SPEC.md",
        "pairs": pairs,
        "operator_labels": operator_labels,
        "thresholds_json": thresholds.as_json(),
        "run_inputs": [
            {"operator_label": run.operator_label, "path": str(run.path)} for run in runs
        ],
        "cell_count_requested": len(pairs) * len(operator_labels),
        "cell_count_available": sum(
            1
            for pair in pairs
            for label in operator_labels
            if cells.get(CellKey(pair, label), {}).get("cell_status") == "available"
        ),
        "missing_or_blocked_cell_count": len(missing_rows),
        "claim_boundary": CLAIM_BOUNDARY,
        "output_files": sorted(outputs) + ["formal_interface_panel_manifest.json"],
    }
    write_json(out_dir / "formal_interface_panel_manifest.json", manifest)
    if write_report:
        report = render_report(
            manifest=manifest,
            condition_rows=condition_rows,
            missing_rows=missing_rows,
            summary_rows=summary_rows,
            delta_rows=delta_rows,
        )
        (out_dir / "formal_interface_report.md").write_text(report, encoding="utf-8")
        manifest["output_files"].append("formal_interface_report.md")
        write_json(out_dir / "formal_interface_panel_manifest.json", manifest)

    return manifest


def load_run(run: LabeledRun) -> dict[str, object]:
    path = run.path
    return {
        "operator_label": run.operator_label,
        "path": path,
        "status": read_json_optional(path / "coupled_future_field_atlas_status.json"),
        "config": read_json_optional(path / "coupled_future_field_atlas_run_config.json"),
        "retention": read_json_optional(path / "_retention_summary" / "retained_run_summary.json"),
        "residual": read_csv(path / "coupled_joint_vs_product_residual_by_horizon.csv.gz"),
        "marginal": read_csv(path / "coupled_marginal_retention_by_horizon.csv.gz"),
        "condition": read_csv(path / "coupled_condition_manifest.csv.gz"),
        "operator": read_csv(path / "coupled_operator_manifest.csv.gz"),
        "audit": read_csv(path / "coupled_reconstruction_audit_summary.csv.gz"),
        "readiness": read_csv(path / "coupled_medium_scale_readiness_summary.csv.gz"),
        "artifact": read_csv(path / "coupled_artifact_completeness_summary.csv.gz"),
    }


def build_cells(
    loaded_runs: list[dict[str, object]],
    *,
    pairs: list[str],
    operator_labels: list[str],
) -> dict[CellKey, dict[str, object]]:
    cells: dict[CellKey, dict[str, object]] = {}
    requested_pairs = set(pairs)
    requested_labels = set(operator_labels)
    for run in loaded_runs:
        label = str(run["operator_label"])
        if label not in requested_labels:
            continue
        gate = run_gate(run)
        metrics = aggregate_metrics(run, requested_pairs)
        condition_by_pair = first_rows_by_pair(run["condition"])  # type: ignore[arg-type]
        operator_row = first_row(run["operator"])  # type: ignore[arg-type]
        for pair_id, horizon_rows in metrics.items():
            key = CellKey(pair_id, label)
            if key in cells and prefer_existing_cell(cells[key], horizon_rows):
                continue
            cells[key] = {
                "pair_id": pair_id,
                "operator_label": label,
                "run_dir": str(run["path"]),
                "run_id": Path(str(run["path"])).name,
                "gate_status": gate["gate_status"],
                "gate_reason": gate["gate_reason"],
                "cell_status": "available" if gate["gate_status"] == "pass" and horizon_rows else "blocked_by_gate",
                "horizon_rows": horizon_rows,
                "condition_row": condition_by_pair.get(pair_id, {}),
                "operator_row": operator_row,
                "source_artifact": "coupled_joint_vs_product_residual_by_horizon.csv.gz+coupled_marginal_retention_by_horizon.csv.gz",
                "artifact_completeness_status": gate["artifact_completeness_status"],
                "reconstruction_audit_status": gate["reconstruction_audit_status"],
                "medium_sweep_interpretation_allowed": gate["medium_sweep_interpretation_allowed"],
            }
    return cells


def aggregate_metrics(
    run: dict[str, object],
    requested_pairs: set[str],
) -> dict[str, list[dict[str, object]]]:
    residual_rows: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    marginal_rows: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in run["residual"]:  # type: ignore[union-attr]
        pair_id = short_pair_id(row)
        if pair_id in requested_pairs:
            residual_rows[(pair_id, int_value(row.get("horizon")))].append(row)
    for row in run["marginal"]:  # type: ignore[union-attr]
        pair_id = short_pair_id(row)
        if pair_id in requested_pairs:
            marginal_rows[(pair_id, int_value(row.get("horizon")))].append(row)

    out: dict[str, list[dict[str, object]]] = defaultdict(list)
    for key in sorted(set(residual_rows) | set(marginal_rows)):
        pair_id, horizon = key
        residual = aggregate_residual_rows(residual_rows.get(key, []))
        marginal = aggregate_marginal_rows(marginal_rows.get(key, []))
        row = {
            "pair_id": pair_id,
            "horizon": horizon,
            "feature_status": worst_feature_status(
                [residual.get("feature_status", ""), marginal.get("feature_status", "")]
            ),
            **residual,
            **marginal,
        }
        row["joint_density_vs_marginal_product"] = joint_density(row)
        out[pair_id].append(row)
    for pair_id in out:
        out[pair_id].sort(key=lambda row: int_value(row.get("horizon")))
    return out


def aggregate_residual_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    if not rows:
        return {}
    return {
        "feature_status": worst_feature_status(row.get("feature_status", "") for row in rows),
        "product_joint_support_count": sum_int(rows, "product_joint_support_count"),
        "coupled_joint_support_count": sum_int(rows, "coupled_joint_support_count"),
        "joint_support_symmetric_difference_count": sum_int(
            rows,
            "joint_support_symmetric_difference_count",
        ),
        "joint_support_residual_fraction": mean_float(rows, "joint_support_residual_fraction"),
    }


def aggregate_marginal_rows(rows: list[dict[str, object]]) -> dict[str, object]:
    if not rows:
        return {}
    return {
        "feature_status": worst_feature_status(row.get("feature_status", "") for row in rows),
        "A_product_marginal_count": sum_int(rows, "A_product_marginal_count"),
        "A_coupled_marginal_count": sum_int(rows, "A_coupled_marginal_count"),
        "A_marginal_retention_fraction": mean_float(rows, "A_marginal_retention_fraction"),
        "B_product_marginal_count": sum_int(rows, "B_product_marginal_count"),
        "B_coupled_marginal_count": sum_int(rows, "B_coupled_marginal_count"),
        "B_marginal_retention_fraction": mean_float(rows, "B_marginal_retention_fraction"),
        "joint_product_state_count": sum_int(rows, "joint_product_state_count"),
        "joint_coupled_state_count": sum_int(rows, "joint_coupled_state_count"),
        "joint_retention_fraction": mean_float(rows, "joint_retention_fraction"),
    }


def run_gate(run: dict[str, object]) -> dict[str, object]:
    status = run["status"] if isinstance(run["status"], dict) else {}
    artifact_statuses = {
        str(row.get("artifact_status", ""))
        for row in run["artifact"]  # type: ignore[union-attr]
        if str(row.get("artifact_status", ""))
    }
    audit_statuses = {
        str(row.get("status", ""))
        for row in run["audit"]  # type: ignore[union-attr]
        if str(row.get("status", ""))
    }
    readiness = first_row(run["readiness"])  # type: ignore[arg-type]
    checks = {
        "status_completed": status.get("status") == "COMPLETED",
        "no_pair_failures": int_value(status.get("coupled_pairs_failed")) == 0,
        "no_internal_caps": int_value(status.get("internal_cap_events")) == 0,
        "complete_artifacts": artifact_statuses <= {"complete"} and bool(artifact_statuses),
        "audits_pass": audit_statuses <= {"PASS"} and bool(audit_statuses),
        "medium_allowed": int_value(readiness.get("medium_sweep_interpretation_allowed")) == 1
        or int_value(status.get("medium_sweep_interpretation_allowed")) == 1,
    }
    gate_pass = all(checks.values())
    failed = [name for name, ok in checks.items() if not ok]
    return {
        "gate_status": "pass" if gate_pass else "blocked_by_gate",
        "gate_reason": "all_required_gates_pass" if gate_pass else ";".join(failed),
        "artifact_completeness_status": ",".join(sorted(artifact_statuses)) or "",
        "reconstruction_audit_status": ",".join(sorted(audit_statuses)) or "",
        "medium_sweep_interpretation_allowed": int(
            int_value(readiness.get("medium_sweep_interpretation_allowed")) == 1
            or int_value(status.get("medium_sweep_interpretation_allowed")) == 1
        ),
    }


def condition_panel_rows(
    cells: dict[CellKey, dict[str, object]],
    *,
    pairs: list[str],
    operator_labels: list[str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for pair_id in pairs:
        for label in operator_labels:
            cell = cells.get(CellKey(pair_id, label))
            if not cell:
                rows.append(base_condition_row(pair_id, label, "missing_not_run", "no_retained_cell"))
                continue
            condition = cell.get("condition_row", {}) if isinstance(cell.get("condition_row"), dict) else {}
            operator = cell.get("operator_row", {}) if isinstance(cell.get("operator_row"), dict) else {}
            final = final_horizon_row(cell.get("horizon_rows", []))  # type: ignore[arg-type]
            row = base_condition_row(
                pair_id,
                label,
                str(cell.get("cell_status", "")),
                str(cell.get("gate_reason", "")),
            )
            row.update(
                {
                    "run_id": cell.get("run_id", ""),
                    "run_dir": cell.get("run_dir", ""),
                    "coupled_operator_id": operator.get("coupled_operator_id", ""),
                    "coupled_operator_family": operator.get("coupled_operator_family", ""),
                    "joint_selection_family": operator.get(
                        "joint_selection_family",
                        condition.get("joint_selection_family", ""),
                    ),
                    "coupling_strength": operator.get("coupling_strength", condition.get("coupling_strength", "")),
                    "joint_effective_out_degree": operator.get(
                        "joint_effective_out_degree",
                        condition.get("joint_effective_out_degree", ""),
                    ),
                    "final_horizon": final.get("horizon", ""),
                    "final_joint_support_residual_fraction": final.get(
                        "joint_support_residual_fraction",
                        "",
                    ),
                    "final_joint_density_vs_marginal_product": final.get(
                        "joint_density_vs_marginal_product",
                        "",
                    ),
                    "artifact_completeness_status": cell.get("artifact_completeness_status", ""),
                    "reconstruction_audit_status": cell.get("reconstruction_audit_status", ""),
                    "source_artifact": cell.get("source_artifact", ""),
                }
            )
            rows.append(row)
    return rows


def base_condition_row(pair_id: str, label: str, status: str, reason: str) -> dict[str, object]:
    return {
        "condition_panel_id": f"{pair_id}__{label}",
        "candidate_designation_id": f"candidate__{pair_id}",
        "pair_id": pair_id,
        "operator_label": label,
        "cell_status": status,
        "gate_reason": reason,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def missing_cell_rows(
    cells: dict[CellKey, dict[str, object]],
    *,
    pairs: list[str],
    operator_labels: list[str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for pair_id in pairs:
        for label in operator_labels:
            cell = cells.get(CellKey(pair_id, label))
            if not cell:
                rows.append(
                    {
                        "pair_id": pair_id,
                        "operator_label": label,
                        "cell_status": "missing_not_run",
                        "missing_reason": "no_retained_run_cell_for_pair_operator",
                        "claim_boundary": CLAIM_BOUNDARY,
                    }
                )
            elif cell.get("cell_status") != "available":
                rows.append(
                    {
                        "pair_id": pair_id,
                        "operator_label": label,
                        "cell_status": cell.get("cell_status", ""),
                        "missing_reason": cell.get("gate_reason", ""),
                        "run_dir": cell.get("run_dir", ""),
                        "claim_boundary": CLAIM_BOUNDARY,
                    }
                )
    return rows


def candidate_designation_manifest(pairs: list[str]) -> list[dict[str, object]]:
    rows = []
    for pair_id in pairs:
        rows.append(
            {
                "candidate_designation_id": f"candidate__{pair_id}",
                "candidate_designation_kind": "pair_frontier_geometry_token",
                "pair_id": pair_id,
                "pair_index": int(pair_id.removeprefix("pair")),
                "representative_class": representative_class(pair_id),
                "selection_reason": selection_reason(pair_id),
                "source_result_note": source_result_note(pair_id),
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def distinction_measure_manifest(thresholds: Thresholds) -> list[dict[str, object]]:
    required_artifacts = json.dumps(
        [
            "coupled_joint_vs_product_residual_by_horizon.csv.gz",
            "coupled_marginal_retention_by_horizon.csv.gz",
        ],
        separators=(",", ":"),
    )
    rows = [
        ("marginal_preserving_joint_restrictive_indicator", "binary_signature_indicator"),
        ("joint_density_vs_surviving_marginals", "joint_vs_marginal_retention"),
        ("high_yield_signature_horizon_persistence", "horizon_persistence"),
        ("residual_delta_vs_product", "operator_delta"),
        ("residual_delta_vs_zero_penalty_joint_rank_prefix", "operator_delta"),
        ("residual_delta_vs_scalar_0.020", "operator_delta"),
        ("residual_delta_vs_shared_capacity_v1", "operator_delta"),
    ]
    return [
        {
            "measure_id": measure_id,
            "measure_family": family,
            "observable_id": "coupled_future_field_joint_vs_marginal_geometry",
            "horizon_regime": "H64_dense",
            "thresholds_json": thresholds.as_json(),
            "normalization_policy": "fractions_normalized_by_declared_retained_support_counts",
            "required_artifacts_json": required_artifacts,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        for measure_id, family in rows
    ]


def distinction_measure_rows(
    cells: dict[CellKey, dict[str, object]],
    *,
    pairs: list[str],
    operator_labels: list[str],
    thresholds: Thresholds,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    delta_lookup = delta_metric_lookup(cells, pairs=pairs)
    for pair_id in pairs:
        for label in operator_labels:
            cell = cells.get(CellKey(pair_id, label))
            if not cell or cell.get("cell_status") != "available":
                rows.extend(unavailable_measure_rows(pair_id, label, cell))
                continue
            for horizon_row in cell["horizon_rows"]:  # type: ignore[index]
                status = signature_class(horizon_row, thresholds)
                indicator = int(status == "marginal_preserving_joint_restrictive")
                base = {
                    "candidate_designation_id": f"candidate__{pair_id}",
                    "pair_id": pair_id,
                    "operator_label": label,
                    "run_id": cell.get("run_id", ""),
                    "horizon": horizon_row.get("horizon", ""),
                    "observable_id": "coupled_future_field_joint_vs_marginal_geometry",
                    "A_marginal_retention": horizon_row.get("A_marginal_retention_fraction", ""),
                    "B_marginal_retention": horizon_row.get("B_marginal_retention_fraction", ""),
                    "joint_support_residual_fraction": horizon_row.get(
                        "joint_support_residual_fraction",
                        "",
                    ),
                    "joint_retention_fraction": horizon_row.get("joint_retention_fraction", ""),
                    "joint_density_vs_marginal_product": horizon_row.get(
                        "joint_density_vs_marginal_product",
                        "",
                    ),
                    "product_joint_support_count": horizon_row.get("product_joint_support_count", ""),
                    "coupled_joint_support_count": horizon_row.get("coupled_joint_support_count", ""),
                    "artifact_completeness_status": cell.get("artifact_completeness_status", ""),
                    "reconstruction_audit_status": cell.get("reconstruction_audit_status", ""),
                    "source_artifact": cell.get("source_artifact", ""),
                }
                rows.append(
                    {
                        **base,
                        "measure_id": "marginal_preserving_joint_restrictive_indicator",
                        "measure_value": indicator,
                        "binary_status": "true" if indicator else "false",
                    }
                )
                rows.append(
                    {
                        **base,
                        "measure_id": "joint_density_vs_surviving_marginals",
                        "measure_value": horizon_row.get("joint_density_vs_marginal_product", ""),
                        "binary_status": "not_binary",
                    }
                )
                rows.append(
                    {
                        **base,
                        "measure_id": "high_yield_signature_horizon_persistence",
                        "measure_value": indicator,
                        "binary_status": "true" if indicator else "false",
                    }
                )
                rows.extend(delta_measure_rows(base, delta_lookup, pair_id, label, horizon_row))
    return rows


def unavailable_measure_rows(
    pair_id: str,
    label: str,
    cell: dict[str, object] | None,
) -> list[dict[str, object]]:
    reason = "missing_not_run" if not cell else str(cell.get("cell_status", "blocked_by_gate"))
    return [
        {
            "candidate_designation_id": f"candidate__{pair_id}",
            "pair_id": pair_id,
            "operator_label": label,
            "run_id": "" if not cell else cell.get("run_id", ""),
            "horizon": "",
            "observable_id": "coupled_future_field_joint_vs_marginal_geometry",
            "measure_id": measure_id,
            "measure_value": "",
            "binary_status": "not_available_from_retained_inputs",
            "artifact_completeness_status": "" if not cell else cell.get("artifact_completeness_status", ""),
            "reconstruction_audit_status": "" if not cell else cell.get("reconstruction_audit_status", ""),
            "source_artifact": "",
            "missing_reason": reason,
        }
        for measure_id in (
            "marginal_preserving_joint_restrictive_indicator",
            "joint_density_vs_surviving_marginals",
            "high_yield_signature_horizon_persistence",
        )
    ]


def delta_measure_rows(
    base: dict[str, object],
    delta_lookup: dict[tuple[str, str, int, str], object],
    pair_id: str,
    label: str,
    horizon_row: dict[str, object],
) -> list[dict[str, object]]:
    del horizon_row
    reference_by_measure = {
        "residual_delta_vs_product": "product_selector",
        "residual_delta_vs_zero_penalty_joint_rank_prefix": "zero_penalty_joint_rank_prefix",
        "residual_delta_vs_scalar_0.020": "scalar_mismatch_0.020",
        "residual_delta_vs_shared_capacity_v1": "shared_capacity_v1",
    }
    rows = []
    horizon = int_value(base.get("horizon"))
    for measure_id, reference in reference_by_measure.items():
        if label == reference:
            value: object = 0.0
            status = "not_binary"
        else:
            value = delta_lookup.get((pair_id, label, horizon, reference), "")
            status = "not_available_from_retained_inputs" if value == "" else "not_binary"
        rows.append({**base, "measure_id": measure_id, "measure_value": value, "binary_status": status})
    return rows


def joint_vs_marginal_rows(
    cells: dict[CellKey, dict[str, object]],
    *,
    thresholds: Thresholds,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key, cell in sorted(cells.items(), key=lambda item: (item[0].pair_id, item[0].operator_label)):
        if cell.get("cell_status") != "available":
            continue
        for horizon_row in cell["horizon_rows"]:  # type: ignore[index]
            status = signature_class(horizon_row, thresholds)
            rows.append(
                {
                    "candidate_designation_id": f"candidate__{key.pair_id}",
                    "pair_id": key.pair_id,
                    "operator_label": key.operator_label,
                    "horizon": horizon_row.get("horizon", ""),
                    "A_marginal_retention": horizon_row.get("A_marginal_retention_fraction", ""),
                    "B_marginal_retention": horizon_row.get("B_marginal_retention_fraction", ""),
                    "joint_density_vs_marginal_product": horizon_row.get(
                        "joint_density_vs_marginal_product",
                        "",
                    ),
                    "joint_support_residual_fraction": horizon_row.get(
                        "joint_support_residual_fraction",
                        "",
                    ),
                    "marginal_preserving_flag": int(
                        marginal_preserving(horizon_row, thresholds)
                    ),
                    "joint_restrictive_flag": int(joint_restrictive(horizon_row, thresholds)),
                    "product_dense_over_surviving_marginals_flag": int(
                        product_dense_over_surviving_marginals(horizon_row, thresholds)
                    ),
                    "signature_class": status,
                }
            )
    return rows


def horizon_signature_persistence_rows(retention_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_cell: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in retention_rows:
        by_cell[(str(row.get("pair_id", "")), str(row.get("operator_label", "")))].append(row)
    rows: list[dict[str, object]] = []
    for (pair_id, label), cell_rows in sorted(by_cell.items()):
        horizons = sorted(int_value(row.get("horizon")) for row in cell_rows)
        if not horizons:
            continue
        windows = [
            ("full_window", min(horizons), max(horizons)),
            ("final_quarter_window", 49, max(horizons)),
        ]
        first_true = first_signature_horizon(cell_rows)
        if first_true != "":
            windows.append(("post_onset_window", int(first_true), max(horizons)))
        for window_id, start, end in windows:
            in_window = [
                row
                for row in cell_rows
                if start <= int_value(row.get("horizon")) <= end
            ]
            true_rows = [
                row
                for row in in_window
                if row.get("signature_class") == "marginal_preserving_joint_restrictive"
            ]
            max_residual_row = max(
                in_window,
                key=lambda row: float_value(row.get("joint_support_residual_fraction")),
                default={},
            )
            rows.append(
                {
                    "candidate_designation_id": f"candidate__{pair_id}",
                    "pair_id": pair_id,
                    "operator_label": label,
                    "window_id": window_id,
                    "window_start": start,
                    "window_end": end,
                    "horizons_available": len(in_window),
                    "horizons_signature_true": len(true_rows),
                    "signature_fraction": safe_fraction(len(true_rows), len(in_window)),
                    "first_horizon_true": first_signature_horizon(in_window),
                    "last_horizon_true": last_signature_horizon(in_window),
                    "max_residual_horizon": max_residual_row.get("horizon", ""),
                    "final_signature_status": final_signature_status(in_window),
                }
            )
    return rows


def operator_reference_delta_rows(
    cells: dict[CellKey, dict[str, object]],
    *,
    pairs: list[str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for left_label, right_label in REFERENCE_COMPARISONS:
        comparison_id = f"{left_label}_vs_{right_label}"
        for pair_id in pairs:
            left_rows = horizon_index(cells.get(CellKey(pair_id, left_label)))
            right_rows = horizon_index(cells.get(CellKey(pair_id, right_label)))
            horizons = sorted(set(left_rows) | set(right_rows))
            if not horizons:
                for metric_name in DELTA_METRICS:
                    rows.append(
                        {
                            "comparison_id": comparison_id,
                            "pair_id": pair_id,
                            "horizon": "",
                            "metric_name": metric_name,
                            "left_operator": left_label,
                            "right_operator": right_label,
                            "left_value": "",
                            "right_value": "",
                            "delta": "",
                            "relative_delta": "",
                            "both_cells_available": 0,
                            "missing_reason": "one_or_both_cells_missing",
                        }
                    )
                continue
            for horizon in horizons:
                left = left_rows.get(horizon)
                right = right_rows.get(horizon)
                both = left is not None and right is not None
                for metric_name in DELTA_METRICS:
                    left_value = "" if left is None else left.get(metric_name, "")
                    right_value = "" if right is None else right.get(metric_name, "")
                    delta = (
                        float_value(left_value) - float_value(right_value)
                        if both and numberish(left_value) and numberish(right_value)
                        else ""
                    )
                    rows.append(
                        {
                            "comparison_id": comparison_id,
                            "pair_id": pair_id,
                            "horizon": horizon,
                            "metric_name": metric_name,
                            "left_operator": left_label,
                            "right_operator": right_label,
                            "left_value": left_value,
                            "right_value": right_value,
                            "delta": delta,
                            "relative_delta": relative_delta(delta, right_value),
                            "both_cells_available": int(both),
                            "missing_reason": "" if both else "one_or_both_cells_missing",
                        }
                    )
    return rows


def representative_control_summary_rows(
    cells: dict[CellKey, dict[str, object]],
    *,
    retention_rows: list[dict[str, object]],
    persistence_rows: list[dict[str, object]],
    pairs: list[str],
    operator_labels: list[str],
) -> list[dict[str, object]]:
    retention_by_cell: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in retention_rows:
        retention_by_cell[(str(row.get("pair_id", "")), str(row.get("operator_label", "")))].append(row)
    persistence_by_cell_window = {
        (str(row.get("pair_id", "")), str(row.get("operator_label", "")), str(row.get("window_id", ""))): row
        for row in persistence_rows
    }
    rows: list[dict[str, object]] = []
    for pair_id in pairs:
        for label in operator_labels:
            final = final_horizon_row(cells.get(CellKey(pair_id, label), {}).get("horizon_rows", []))  # type: ignore[arg-type]
            final_retention = final_horizon_row(retention_by_cell.get((pair_id, label), []))
            full = persistence_by_cell_window.get((pair_id, label, "full_window"), {})
            quarter = persistence_by_cell_window.get((pair_id, label, "final_quarter_window"), {})
            rows.append(
                {
                    "pair_id": pair_id,
                    "representative_class": representative_class(pair_id),
                    "operator_label": label,
                    "final_residual": final.get("joint_support_residual_fraction", ""),
                    "final_joint_retention": final.get("joint_retention_fraction", ""),
                    "final_A_retention": final.get("A_marginal_retention_fraction", ""),
                    "final_B_retention": final.get("B_marginal_retention_fraction", ""),
                    "final_joint_density_vs_marginal_product": final.get(
                        "joint_density_vs_marginal_product",
                        "",
                    ),
                    "final_signature_class": final_retention.get("signature_class", "missing_not_run"),
                    "full_window_signature_fraction": full.get("signature_fraction", ""),
                    "final_quarter_signature_fraction": quarter.get("signature_fraction", ""),
                    "comparison_to_rank_order_boundary": comparison_to_rank_order_boundary(
                        cells,
                        pair_id,
                        label,
                    ),
                    "summary_read": compact_summary_read(final_retention),
                    "claim_boundary": CLAIM_BOUNDARY,
                }
            )
    return rows


def delta_metric_lookup(
    cells: dict[CellKey, dict[str, object]],
    *,
    pairs: list[str],
) -> dict[tuple[str, str, int, str], object]:
    lookup: dict[tuple[str, str, int, str], object] = {}
    for left_label in DEFAULT_OPERATOR_LABELS:
        for reference in DEFAULT_OPERATOR_LABELS:
            if left_label == reference:
                continue
            for pair_id in pairs:
                left_rows = horizon_index(cells.get(CellKey(pair_id, left_label)))
                right_rows = horizon_index(cells.get(CellKey(pair_id, reference)))
                for horizon in sorted(set(left_rows) & set(right_rows)):
                    left = left_rows[horizon]
                    right = right_rows[horizon]
                    if numberish(left.get("joint_support_residual_fraction")) and numberish(
                        right.get("joint_support_residual_fraction")
                    ):
                        lookup[(pair_id, left_label, horizon, reference)] = (
                            float_value(left.get("joint_support_residual_fraction"))
                            - float_value(right.get("joint_support_residual_fraction"))
                        )
    return lookup


def render_report(
    *,
    manifest: dict[str, object],
    condition_rows: list[dict[str, object]],
    missing_rows: list[dict[str, object]],
    summary_rows: list[dict[str, object]],
    delta_rows: list[dict[str, object]],
) -> str:
    available = sum(1 for row in condition_rows if row.get("cell_status") == "available")
    blocked = len(condition_rows) - available
    high_yield_rank = [
        row
        for row in summary_rows
        if row.get("representative_class") == "high_yield_representative"
        and row.get("operator_label") == "rank_order_boundary"
    ]
    control_rank = [
        row
        for row in summary_rows
        if row.get("representative_class") != "high_yield_representative"
        and row.get("operator_label") == "rank_order_boundary"
    ]
    high_yield_statuses = sorted({str(row.get("final_signature_class", "")) for row in high_yield_rank})
    control_statuses = sorted({str(row.get("final_signature_class", "")) for row in control_rank})
    complete_delta_rows = sum(1 for row in delta_rows if int_value(row.get("both_cells_available")) == 1)
    lines = [
        "# Future Field Atlas Formal Interface Distinction Panel",
        "",
        "## Summary",
        "",
        "This pass emits declared finite distinction-measure artifacts from retained coupled FFA compact outputs.",
        REPORT_BLOCKED_SENTENCE,
        "",
        f"- panel digest: `{manifest.get('panel_digest', '')}`",
        f"- requested cells: {manifest.get('cell_count_requested', 0)}",
        f"- available cells: {available}",
        f"- missing or blocked cells: {blocked}",
        f"- complete operator-delta rows: {complete_delta_rows}",
        "",
        "## Candidate Panel",
        "",
        f"- high-yield rank-order-boundary final classes: {', '.join(high_yield_statuses) or 'none'}",
        f"- control rank-order-boundary final classes: {', '.join(control_statuses) or 'none'}",
        "",
        "## Missing Cells And Limits",
        "",
        f"- explicit missing/blocked rows: {len(missing_rows)}",
        "- missing cells remain `missing_not_run`; unavailable values are not filled with zero.",
        "",
        "## Theory-Arm Interface Implications",
        "",
        "The emitted rows are suitable as a first finite distinction-measure interface. They are not identity-decay-null, maintenance-gap, process-bundle, or compatibility-audit artifacts.",
        "",
        "## Claim Boundary",
        "",
        CLAIM_BOUNDARY,
        "",
    ]
    return "\n".join(lines)


def read_json_optional(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_labeled_runs(raw_runs: list[str]) -> list[LabeledRun]:
    runs = []
    for raw in raw_runs:
        if "=" not in raw:
            raise ValueError(f"expected operator_label=path, got {raw!r}")
        label, path = raw.split("=", 1)
        runs.append(LabeledRun(label.strip(), Path(path)))
    return runs


def parse_csv_arg(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def infer_operator_label(path: Path) -> str:
    config = read_json_optional(path / "coupled_future_field_atlas_run_config.json")
    family = str(config.get("joint_selection_family", ""))
    strength = float_value(config.get("coupling_strength"))
    if family == "product":
        return "product_selector"
    if family == "shared_capacity":
        return "shared_capacity_v1"
    if family == "rank_order_boundary":
        return "rank_order_boundary"
    if family == "joint_energy_rank_prefix" and abs(strength) < 1e-12:
        return "zero_penalty_joint_rank_prefix"
    if family == "joint_energy_rank_prefix" and abs(strength - 0.02) < 1e-12:
        return "scalar_mismatch_0.020"
    return family or path.name


def first_rows_by_pair(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    out = {}
    for row in rows:
        out.setdefault(short_pair_id(row), row)
    return out


def first_row(rows: list[dict[str, object]]) -> dict[str, object]:
    return rows[0] if rows else {}


def final_horizon_row(rows: object) -> dict[str, object]:
    if not rows:
        return {}
    return max(rows, key=lambda row: int_value(row.get("horizon")))  # type: ignore[union-attr]


def horizon_index(cell: dict[str, object] | None) -> dict[int, dict[str, object]]:
    if not cell or cell.get("cell_status") != "available":
        return {}
    return {
        int_value(row.get("horizon")): row
        for row in cell.get("horizon_rows", [])  # type: ignore[union-attr]
    }


def prefer_existing_cell(existing: dict[str, object], new_rows: list[dict[str, object]]) -> bool:
    existing_rows = existing.get("horizon_rows", [])
    if existing.get("cell_status") == "available" and existing_rows:
        return max_horizon(existing_rows) >= max_horizon(new_rows)
    return False


def max_horizon(rows: object) -> int:
    if not rows:
        return -1
    return max(int_value(row.get("horizon")) for row in rows)  # type: ignore[union-attr]


def short_pair_id(row: dict[str, object]) -> str:
    return str(row.get("pair_id", "")).split("__")[0]


def representative_class(pair_id: str) -> str:
    if pair_id in {"pair005", "pair012", "pair014", "pair026"}:
        return "high_yield_representative"
    if pair_id == "pair045":
        return "medium_near_high_control"
    return "low_residual_control"


def selection_reason(pair_id: str) -> str:
    if representative_class(pair_id) == "high_yield_representative":
        return "current rank_order_boundary high-yield representative set"
    if pair_id == "pair045":
        return "highest non-high-yield residual in pair024-047 expansion readout"
    return "recurring low-residual control from earlier coupled panels"


def source_result_note(pair_id: str) -> str:
    if pair_id in {"pair026", "pair045"}:
        return "docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_class_expansion_result.md"
    return "docs/research_notes/validation_results/future_field_atlas/future_field_atlas_rank_order_boundary_medium_sweep_result.md"


def marginal_preserving(row: dict[str, object], thresholds: Thresholds) -> bool:
    return (
        numberish(row.get("A_marginal_retention_fraction"))
        and numberish(row.get("B_marginal_retention_fraction"))
        and float_value(row.get("A_marginal_retention_fraction")) >= thresholds.marginal_preserving
        and float_value(row.get("B_marginal_retention_fraction")) >= thresholds.marginal_preserving
    )


def joint_restrictive(row: dict[str, object], thresholds: Thresholds) -> bool:
    return numberish(row.get("joint_density_vs_marginal_product")) and (
        float_value(row.get("joint_density_vs_marginal_product"))
        <= thresholds.joint_restrictive_density
    )


def product_dense_over_surviving_marginals(row: dict[str, object], thresholds: Thresholds) -> bool:
    return numberish(row.get("joint_density_vs_marginal_product")) and not joint_restrictive(
        row,
        thresholds,
    )


def signature_class(row: dict[str, object], thresholds: Thresholds) -> str:
    if row.get("feature_status", "complete") != "complete":
        return "incomplete"
    if not numberish(row.get("joint_density_vs_marginal_product")):
        return "incomplete"
    marginal = marginal_preserving(row, thresholds)
    restrictive = joint_restrictive(row, thresholds)
    if marginal and restrictive:
        return "marginal_preserving_joint_restrictive"
    if marginal and not restrictive:
        return "marginal_preserving_product_dense"
    if not marginal and restrictive:
        return "marginal_loss_joint_restrictive"
    return "marginal_loss_product_dense"


def joint_density(row: dict[str, object]) -> object:
    a_count = int_value(row.get("A_coupled_marginal_count"))
    b_count = int_value(row.get("B_coupled_marginal_count"))
    coupled = int_value(row.get("joint_coupled_state_count") or row.get("coupled_joint_support_count"))
    denominator = a_count * b_count
    if denominator <= 0:
        return ""
    return coupled / denominator


def first_signature_horizon(rows: list[dict[str, object]]) -> object:
    true_horizons = [
        int_value(row.get("horizon"))
        for row in rows
        if row.get("signature_class") == "marginal_preserving_joint_restrictive"
    ]
    return min(true_horizons) if true_horizons else ""


def last_signature_horizon(rows: list[dict[str, object]]) -> object:
    true_horizons = [
        int_value(row.get("horizon"))
        for row in rows
        if row.get("signature_class") == "marginal_preserving_joint_restrictive"
    ]
    return max(true_horizons) if true_horizons else ""


def final_signature_status(rows: list[dict[str, object]]) -> str:
    final = final_horizon_row(rows)
    return str(final.get("signature_class", ""))


def comparison_to_rank_order_boundary(
    cells: dict[CellKey, dict[str, object]],
    pair_id: str,
    label: str,
) -> object:
    if label == "rank_order_boundary":
        return "reference_operator"
    left = final_horizon_row(cells.get(CellKey(pair_id, label), {}).get("horizon_rows", []))  # type: ignore[arg-type]
    right = final_horizon_row(
        cells.get(CellKey(pair_id, "rank_order_boundary"), {}).get("horizon_rows", [])
    )  # type: ignore[arg-type]
    if not left or not right:
        return "not_available_from_retained_inputs"
    if numberish(left.get("joint_support_residual_fraction")) and numberish(
        right.get("joint_support_residual_fraction")
    ):
        return float_value(left.get("joint_support_residual_fraction")) - float_value(
            right.get("joint_support_residual_fraction")
        )
    return "not_available_from_retained_inputs"


def compact_summary_read(row: dict[str, object]) -> str:
    status = str(row.get("signature_class", "missing_not_run"))
    if status == "marginal_preserving_joint_restrictive":
        return "finite_measure_signature_true"
    if status == "missing_not_run":
        return "missing_not_run"
    if status == "incomplete":
        return "incomplete"
    return "finite_measure_signature_false"


def relative_delta(delta: object, right_value: object) -> object:
    if delta == "" or not numberish(right_value):
        return ""
    denominator = abs(float_value(right_value))
    if denominator <= 1e-12:
        return ""
    return float_value(delta) / denominator


def sum_int(rows: list[dict[str, object]], field: str) -> int:
    return sum(int_value(row.get(field)) for row in rows if numberish(row.get(field)))


def mean_float(rows: list[dict[str, object]], field: str) -> object:
    values = [float_value(row.get(field)) for row in rows if numberish(row.get(field))]
    if not values:
        return ""
    return sum(values) / len(values)


def worst_feature_status(values: object) -> str:
    statuses = [str(value) for value in values if str(value)]
    if not statuses:
        return ""
    if "truncated_noninterpretable" in statuses:
        return "truncated_noninterpretable"
    if "sampled" in statuses:
        return "sampled"
    if "lossless_compressed" in statuses:
        return "lossless_compressed"
    if all(status == "complete" for status in statuses):
        return "complete"
    return sorted(statuses)[-1]


def safe_fraction(numerator: int, denominator: int) -> object:
    if denominator <= 0:
        return ""
    return numerator / denominator


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


if __name__ == "__main__":
    main()
