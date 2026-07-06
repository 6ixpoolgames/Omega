"""Retained validation for the joint-tier reduction audit v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.joint_tier_reduction_audit import (
    joint_tier_reduction_audit_summary,
    planted_null_rows,
    reduction_attempt_rows,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the joint-tier reduction audit v0.")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_joint_tier_reduction_audit_v0"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_joint_tier_reduction_audit(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_joint_tier_reduction_audit(
    *,
    out_root: Path = Path(".tmp/finite_relational_joint_tier_reduction_audit_v0"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_joint_tier_reduction_audit(run_root)


def retain_finite_relational_joint_tier_reduction_audit(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = joint_tier_reduction_audit_summary()
    result = {
        "status": "PASS" if summary["verdict"] == "calibrated" else "REVIEW",
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "planted_nulls.csv", planted_null_rows(summary))
    write_csv(out_dir / "reduction_attempts.csv", reduction_attempt_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# Joint-Tier Reduction Audit v0 Report",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        "",
        "## Planted Nulls",
        "",
    ]
    for row in result["planted_nulls"]:
        lines.extend(
            [
                f"### {row['instrument']}: {row['planted_coordinate']}",
                "",
                f"- Verdict: {row['verdict']}",
                f"- Reduction basis: `{row['reduction_basis']}`",
                f"- Passes: {row['passes']}",
                f"- Note: {row['evidence']['note']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Reduction Attempts",
            "",
        ]
    )
    for row in result["reduction_attempts"]:
        lines.extend(
            [
                f"### {row['target']}",
                "",
                f"- Hypothesis: {row['hypothesis']}",
                f"- Verdict: {row['verdict']}",
                f"- Passes: {row['passes']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "This is a finite audit of instrument reduction pressure. It does not "
            "prove value, standing, agency, population ethics, plurality theory, "
            "aggregation, patienthood, or Omega validation.",
            "",
            "## Public Compression",
            "",
            "The joint-tier reduction audit calibrates planted-null controls before "
            "NOLP: known reducible coordinates reduce, relational composability "
            "survives cheap graph-scalar reductions, colonization keeps an explicit "
            "lens-invariance debt, and joint-recovery compatibility is treated as "
            "a recovery-grounded bridge rather than an independent axis.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
