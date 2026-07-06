"""Retained validation for the relational-composability v0 coupling instrument."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.relational_composability import (
    compatibility_profile_rows,
    relational_composability_summary,
    relational_control_rows,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the relational-composability v0 finite audit.")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_composability_v0"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_composability(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_composability(
    *,
    out_root: Path = Path(".tmp/finite_relational_composability_v0"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_composability(run_root)


def retain_finite_relational_composability(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = relational_composability_summary()
    result = {
        "status": "PASS" if summary["verdict"] == "separated" else "REVIEW",
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "control_comparison.csv", relational_control_rows(summary))
    write_csv(out_dir / "compatibility_profiles.csv", compatibility_profile_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    pair = result["candidate_pair"]
    robustness = result["graph_structure_robustness"]
    controls = result["negative_controls"]
    left_profile = pair["left_compatibility_profile"]
    right_profile = pair["right_compatibility_profile"]
    robustness_left = robustness["left_compatibility_profile"]
    robustness_right = robustness["right_compatibility_profile"]
    lines = [
        "# Relational Composability v0 Report",
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
        f"- Compatibility separates: {pair['compatibility_separates']}",
        "",
        "## Compatibility Profiles",
        "",
        f"- Left compatible pair count: {left_profile['compatible_pair_count']}",
        f"- Right compatible pair count: {right_profile['compatible_pair_count']}",
        f"- Left max component size: {left_profile['max_compatible_component_size']}",
        f"- Right max component size: {right_profile['max_compatible_component_size']}",
        "",
        "## Graph-Structure Robustness",
        "",
        f"- Left: `{robustness['left']}`",
        f"- Right: `{robustness['right']}`",
        f"- Full vector census equal: {robustness['full_vector_census_equal']}",
        f"- Pure span equivalent: {robustness['span_equivalent']}",
        f"- Compatible pair count equal: {robustness['same_compatible_pair_count']}",
        f"- Degree sequence equal: {robustness['same_degree_sequence']}",
        f"- Left component sizes: {robustness_left['component_sizes']}",
        f"- Right component sizes: {robustness_right['component_sizes']}",
        f"- Component structure separates: {robustness['component_structure_separates']}",
        "",
        "## Negative Controls",
        "",
        (
            "- Full vectors plus identical coupling determine this profile: "
            f"{controls['identical_coupling']['full_vectors_and_coupling_determine_profile']}"
        ),
        f"- Negative controls pass: {controls['negative_controls_pass']}",
        "",
        "## Claim Boundary",
        "",
        "This is a finite coupling instrument report. It does not prove value, "
        "standing, agency, plurality theory, population ethics, aggregation, "
        "population optimum, or Omega validation.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
