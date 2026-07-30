"""Retained validation for the finite lushness/diversity pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.lushness_diversity import (
    case_rows,
    lushness_diversity_summary,
    profile_rows,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the post-freeze finite lushness/diversity pilot."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_lushness_diversity_v0"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_lushness_diversity(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_lushness_diversity(
    *,
    out_root: Path = Path(".tmp/finite_relational_lushness_diversity_v0"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_lushness_diversity(run_root)


def retain_finite_relational_lushness_diversity(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = lushness_diversity_summary()
    result = {
        "status": "PASS" if summary["verdict"] == "retained" else "REVIEW",
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "case_results.csv", case_rows(summary))
    write_csv(out_dir / "profiles.csv", profile_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    cases = result["cases"]
    controls = result["negative_controls"]
    lines = [
        "# Lushness Diversity Pilot v0 Report",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        "",
        "## Case Results",
        "",
    ]
    lines.extend(
        f"- {case}: {passes}"
        for case, passes in result["case_results"].items()
    )
    lines.extend(
        [
            "",
            "## Structural Coverage",
            "",
            (
                "- Duplicate adds no profile: "
                f"{cases['duplicate']['duplicate_adds_no_profile']}"
            ),
            (
                "- Non-fungible extension strictly refines: "
                f"{cases['nonfungible']['extension_strictly_refines']}"
            ),
            (
                "- Same count, different profile verdict: "
                f"{cases['cardinality']['same_count_different_profile_verdict']}"
            ),
            "",
            "## Higher-Order Compatibility",
            "",
            f"- One-skeletons equal: {cases['pairwise']['one_skeletons_equal']}",
            (
                "- Singleton/pair profiles equal: "
                f"{cases['pairwise']['singleton_pair_profiles_equal']}"
            ),
            f"- Filled structure is flag: {cases['pairwise']['filled_is_flag']}",
            f"- Hollow structure is flag: {cases['pairwise']['hollow_is_flag']}",
            (
                "- Hollow triple realizable: "
                f"{cases['pairwise']['hollow_triple_realizable']}"
            ),
            "",
            "## Effective Freedom Boundary",
            "",
            (
                "- Agreement case orders agree: "
                f"{cases['effective_freedom']['agreement']['orders_agree']}"
            ),
            (
                "- Coverage-only case diverges: "
                f"{cases['effective_freedom']['coverage_only']['orders_diverge']}"
            ),
            (
                "- Preference-only case diverges: "
                f"{cases['effective_freedom']['preference_only']['orders_diverge']}"
            ),
            f"- Boundary: {cases['effective_freedom']['quantifier_boundary']}",
            "",
            "## Excisive Paperclipper",
            "",
            (
                "- Paperclip preference favors excision: "
                f"{cases['paperclipper']['paperclipper_prefers_excision']}"
            ),
            (
                "- Cooperative profile strictly refines excisive profile: "
                f"{cases['paperclipper']['cooperation_strictly_lusher']}"
            ),
            "",
            "## Negative Controls",
            "",
            (
                "- Relabeling preserves profile: "
                f"{controls['relabeling_preserves_profile']}"
            ),
            (
                "- Scalar shadow flips while primary order remains incomparable: "
                f"{controls['scalar_shadow']['scalar_order_flips']}"
            ),
            (
                "- Marginal profile is submodular: "
                f"{controls['submodularity']['marginal_profile_submodular']}"
            ),
            (
                "- Joint-augmented profile is submodular: "
                f"{controls['submodularity']['joint_augmented_profile_submodular']}"
            ),
            (
                "- Unrealizable profile rejected: "
                f"{controls['unrealizable_profile_rejected']}"
            ),
            f"- Negative controls pass: {controls['negative_controls_pass']}",
            "",
            "## Interpretation",
            "",
            f"Primary instrument: {result['primary_instrument']}.",
            f"Separate instrument: {result['separate_instrument']}.",
            f"Open debt: {result['attribute_selection_debt']}.",
            "",
            "## Claim Boundary",
            "",
            "This finite successor pilot does not prove value, standing, autonomy, "
            "patienthood, population ethics, moral aggregation, universal lushness, "
            "paperclipper defeat, or Omega validation.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
