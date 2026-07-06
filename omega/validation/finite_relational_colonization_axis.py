"""Retained validation for the colonization-axis v0 discovery sprint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.colonization_axis import (
    colonization_axis_summary,
    control_panel_rows,
    profile_rows,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the colonization-axis v0 discovery audit.")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_colonization_axis_v0"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_colonization_axis(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_colonization_axis(
    *,
    out_root: Path = Path(".tmp/finite_relational_colonization_axis_v0"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_colonization_axis(run_root)


def retain_finite_relational_colonization_axis(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = colonization_axis_summary()
    result = {
        "status": "PASS" if summary["verdict"] == "separated" else "REVIEW",
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "control_panel_comparison.csv", control_panel_rows(summary))
    write_csv(out_dir / "colonization_profiles.csv", profile_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    pair = result["candidate_pair"]
    gauntlet = result["demotion_gauntlet"]
    lines = [
        "# Colonization Axis v0 Discovery Report",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        "",
        "## Candidate Pair",
        "",
        f"- Left: `{pair['left']}`",
        f"- Right: `{pair['right']}`",
        f"- State bound satisfied: {pair['state_bound_satisfied']}",
        f"- Control panel equal: {pair['control_panel_equal']}",
        f"- Left refines right: {pair['left_refines_right']['refines']}",
        f"- Right refines left: {pair['right_refines_left']['refines']}",
        "",
        "## Profiles",
        "",
        f"- Left chain signatures: {pair['left_profile']['chain_cell_count_signatures']}",
        f"- Right chain signatures: {pair['right_profile']['chain_cell_count_signatures']}",
        "",
        "## Demotion Gauntlet",
        "",
        (
            "- Lens/presentation audit: "
            f"{gauntlet['lens_presentation_audit']['registered_chains_certified']}"
        ),
        (
            "- Converse witness attempt: "
            f"{gauntlet['converse_witness_attempt']['same_colonization_profile']} profile match, "
            f"{gauntlet['converse_witness_attempt']['joint_behavior_differs']} joint difference"
        ),
        (
            "- Scalar-shadow check: "
            f"{gauntlet['scalar_shadow_check']['scalar_equal']} scalar equality, "
            f"{gauntlet['scalar_shadow_check']['order_separates']} order separation"
        ),
        f"- Gauntlet passes: {gauntlet['gauntlet_passes']}",
        "",
        "## Claim Boundary",
        "",
        "This is a retained finite witness report. It does not prove lushness, value, "
        "agency, identity, moral standing, a global lens-invariance theorem, or Omega validation.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
