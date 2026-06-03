"""Input loading and gate checks for the FFA formal adapter package."""

from __future__ import annotations

import json
from pathlib import Path

from .formal_adapter_schema import intish
from .util import read_csv


def load_panel(input_panel: Path) -> dict[str, object]:
    manifest_path = input_panel / "formal_interface_panel_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    return {
        "input_panel": input_panel,
        "manifest": manifest,
        "condition_rows": read_csv(input_panel / "formal_interface_condition_panel.csv"),
        "candidate_rows": read_csv(input_panel / "candidate_designation_manifest.csv"),
        "measure_manifest_rows": read_csv(input_panel / "distinction_measure_manifest.csv"),
        "measure_rows": read_csv(input_panel / "distinction_measure_by_horizon.csv"),
        "retention_rows": read_csv(input_panel / "joint_vs_marginal_distinction_retention.csv"),
        "delta_rows": read_csv(input_panel / "operator_reference_delta_by_horizon.csv"),
        "persistence_rows": read_csv(input_panel / "horizon_signature_persistence.csv"),
        "summary_rows": read_csv(input_panel / "representative_control_signature_summary.csv"),
        "missing_rows": read_csv(input_panel / "formal_interface_missing_cells.csv"),
    }

def input_gate(panel: dict[str, object]) -> dict[str, object]:
    input_panel = panel["input_panel"]
    required = [
        "formal_interface_panel_manifest.json",
        "formal_interface_condition_panel.csv",
        "candidate_designation_manifest.csv",
        "distinction_measure_manifest.csv",
        "distinction_measure_by_horizon.csv",
        "joint_vs_marginal_distinction_retention.csv",
        "operator_reference_delta_by_horizon.csv",
        "horizon_signature_persistence.csv",
        "representative_control_signature_summary.csv",
        "formal_interface_missing_cells.csv",
        "formal_interface_report.md",
    ]
    missing = [name for name in required if not (input_panel / name).exists()]
    manifest = panel["manifest"]
    condition_rows: list[dict[str, object]] = panel["condition_rows"]  # type: ignore[assignment]
    blocked_reasons: list[str] = []
    if missing:
        blocked_reasons.append("missing_artifacts:" + ",".join(missing))
    if intish(manifest.get("cell_count_requested")) != 40:
        blocked_reasons.append("unexpected_requested_cell_count")
    if intish(manifest.get("cell_count_available")) != intish(manifest.get("cell_count_requested")):
        blocked_reasons.append("panel_cells_not_all_available")
    if intish(manifest.get("missing_or_blocked_cell_count")) != 0:
        blocked_reasons.append("manifest_reports_missing_or_blocked_cells")
    if panel["missing_rows"]:  # type: ignore[index]
        blocked_reasons.append("missing_cell_rows_present")
    for row in condition_rows:
        if row.get("cell_status") != "available":
            blocked_reasons.append("condition_cell_not_available")
            break
        if row.get("artifact_completeness_status") != "complete":
            blocked_reasons.append("artifact_not_complete")
            break
        if row.get("reconstruction_audit_status") != "PASS":
            blocked_reasons.append("reconstruction_audit_not_pass")
            break
    return {
        "adapter_status": "blocked_input_incomplete" if blocked_reasons else "input_complete",
        "blocked_reasons": sorted(set(blocked_reasons)),
        "input_panel_digest": manifest.get("panel_digest", ""),
        "requested_cells": manifest.get("cell_count_requested", ""),
        "available_cells": manifest.get("cell_count_available", ""),
        "missing_or_blocked_cells": manifest.get("missing_or_blocked_cell_count", ""),
    }
