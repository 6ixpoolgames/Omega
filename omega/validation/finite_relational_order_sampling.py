"""Retained validation for the order-sampling harness v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.order_sampling import (
    order_sampling_rows,
    order_sampling_summary,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the order-sampling harness v0.")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_order_sampling_v0"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_order_sampling(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_order_sampling(
    *,
    out_root: Path = Path(".tmp/finite_relational_order_sampling_v0"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_order_sampling(run_root)


def retain_finite_relational_order_sampling(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = order_sampling_summary()
    result = {
        "status": "PASS" if summary["verdict"] == "calibrated" else "REVIEW",
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "order_sampling_rows.csv", order_sampling_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    loss = result["loss_dependency_witness"]
    fragile = result["loss_fragility_witness"]
    pathological = result["pathological_order_witness"]
    expansion = result["expansion_invariant_witness"]
    lines = [
        "# Order Sampling Harness v0 Report",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        "",
        "## Calibration Witnesses",
        "",
        f"- Loss comparison classification: {loss['classification']}",
        f"- Fragility classification: {fragile['classification']}",
        f"- Pathological-order classification: {pathological['classification']}",
        f"- Expansion comparison classification: {expansion['classification']}",
        f"- Kill conditions pass: {result['kill_conditions_pass']}",
        "",
        "## Loss Dependency",
        "",
    ]
    for row in loss["rows"]:
        lines.append(f"- {row['order_id']}: {row['verdict']}")
    lines.extend(
        [
            "",
            "## Fragility",
            "",
        ]
    )
    for row in fragile["rows"]:
        lines.append(f"- {row['order_id']}: {row['verdict']}")
    lines.extend(
        [
            "",
            "## Pathological Order",
            "",
        ]
    )
    for row in pathological["rows"]:
        lines.append(
            f"- {row['order_id']}: verdict={row['verdict']}, "
            f"soundness_violation={row['soundness_violation']}"
        )
    lines.extend(
        [
            "",
            "## Expansion Invariance",
            "",
        ]
    )
    for row in expansion["rows"]:
        lines.append(f"- {row['order_id']}: {row['verdict']}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "This is a finite declared-order sensitivity harness. It does not "
            "derive the correct fact order, value, standing, aggregation, "
            "arbitration, patienthood, or Omega validation.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
