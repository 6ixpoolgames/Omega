"""Retained validation for the ensemble-span v0 joint-tier instrument."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.ensemble_span import (
    ensemble_span_summary,
    marginal_control_rows,
    span_profile_rows,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ensemble-span v0 finite audit.")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_ensemble_span_v0"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_ensemble_span(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_ensemble_span(
    *,
    out_root: Path = Path(".tmp/finite_relational_ensemble_span_v0"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_ensemble_span(run_root)


def retain_finite_relational_ensemble_span(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = ensemble_span_summary()
    result = {
        "status": "PASS" if summary["verdict"] == "separated" else "REVIEW",
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "marginal_control_comparison.csv", marginal_control_rows(summary))
    write_csv(out_dir / "span_profiles.csv", span_profile_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    pair = result["candidate_pair"]
    robustness = result["larger_rank_robustness"]
    diminishing = result["diminishing_returns"]
    controls = result["negative_controls"]
    lines = [
        "# Ensemble Span v0 Report",
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
        f"- Left rank: {pair['left_span_profile']['rank']}",
        f"- Right rank: {pair['right_span_profile']['rank']}",
        f"- Left includes right: {pair['left_span_includes_right']}",
        f"- Right includes left: {pair['right_span_includes_left']}",
        f"- Full vector census equal: {pair['full_vector_census_equal']}",
        "",
        "## Larger Rank Robustness",
        "",
        f"- Left: `{robustness['left']}`",
        f"- Right: `{robustness['right']}`",
        f"- Marginal scalar controls equal: {robustness['marginal_scalar_controls_equal']}",
        f"- Left rank: {robustness['left_span_profile']['rank']}",
        f"- Right rank: {robustness['right_span_profile']['rank']}",
        f"- Left includes right: {robustness['left_span_includes_right']}",
        f"- Right includes left: {robustness['right_span_includes_left']}",
        "",
        "## Diminishing Returns",
        "",
        f"- Base rank: {diminishing['base_rank']}",
        f"- Correlated rank gain: {diminishing['correlated_rank_gain']}",
        f"- Orthogonal rank gain: {diminishing['orthogonal_rank_gain']}",
        "",
        "## Negative Controls",
        "",
        (
            "- Identical-vector control reduces to singleton orientation: "
            f"{controls['identical_vectors']['rank_reduces_to_singleton_orientation']}"
        ),
        (
            "- Full-vector census determines pure span: "
            f"{controls['full_vector_census']['full_vector_census_determines_pure_span']}"
        ),
        f"- Negative controls pass: {controls['negative_controls_pass']}",
        "",
        "## Claim Boundary",
        "",
        "This is a finite joint-tier instrument report. It does not prove value, "
        "standing, agency, population ethics, aggregation, relational surplus, "
        "population optimum, or Omega validation.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
