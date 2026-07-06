"""Retained validation for the joint-recovery compatibility v0 bridge."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.joint_recovery_compatibility import (
    joint_recovery_compatibility_summary,
    joint_recovery_control_rows,
    joint_recovery_profile_rows,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the joint-recovery compatibility v0 finite audit.")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_joint_recovery_compatibility_v0"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_joint_recovery_compatibility(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_joint_recovery_compatibility(
    *,
    out_root: Path = Path(".tmp/finite_relational_joint_recovery_compatibility_v0"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_joint_recovery_compatibility(run_root)


def retain_finite_relational_joint_recovery_compatibility(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = joint_recovery_compatibility_summary()
    result = {
        "status": "PASS" if summary["verdict"] == "separated" else "REVIEW",
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "control_comparison.csv", joint_recovery_control_rows(summary))
    write_csv(out_dir / "joint_recovery_profiles.csv", joint_recovery_profile_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    pair = result["candidate_pair"]
    controls = result["negative_controls"]
    left_recovery = pair["left_recovery_profile"]
    right_recovery = pair["right_recovery_profile"]
    lines = [
        "# Joint Recovery Compatibility v0 Report",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        "",
        "## Candidate Pair",
        "",
        f"- Left: `{pair['left']}`",
        f"- Right: `{pair['right']}`",
        f"- Marginal scalar controls equal: {pair['marginal_scalar_controls_equal']}",
        f"- Full vector census equal: {pair['full_vector_census_equal']}",
        f"- Pure span equivalent: {pair['span_equivalent']}",
        f"- Span rank separates: {pair['span_rank_separates']}",
        f"- Individual recovery profiles equal: {pair['individual_recovery_profiles_equal']}",
        f"- Joint recovery separates: {pair['joint_recovery_separates']}",
        "",
        "## Recovery Profiles",
        "",
        f"- Left joint recovered facts: {left_recovery['joint_recovered_fact_ids']}",
        f"- Right joint recovered facts: {right_recovery['joint_recovered_fact_ids']}",
        f"- Left joint recovery succeeds: {left_recovery['joint_recovery_succeeds']}",
        f"- Right joint recovery succeeds: {right_recovery['joint_recovery_succeeds']}",
        f"- Right missing facts: {right_recovery['joint_missing_fact_ids']}",
        "",
        "## Negative Controls",
        "",
        (
            "- Same individual and same joint recovery determine this profile: "
            f"{controls['identical_joint_recovery']['same_individual_and_joint_recovery_determine_profile']}"
        ),
        (
            "- Individual-profile difference is not credited as joint-only: "
            f"{controls['individual_difference']['not_credited_as_joint_only']}"
        ),
        f"- Negative controls pass: {controls['negative_controls_pass']}",
        "",
        "## Claim Boundary",
        "",
        "This is a finite recovery-grounded compatibility report. It does not prove "
        "value, standing, agency, plurality theory, moral aggregation, patienthood, "
        "population optimum, or Omega validation.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
