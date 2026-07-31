"""Retained validation for Generated Continuation Dynamics v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.generated_continuation_dynamics import (
    case_rows,
    deformation_distribution_rows,
    deformation_system_rows,
    generated_continuation_dynamics_summary,
    generator_manifest_rows,
    nonflag_search_rows,
    sensitivity_rows,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Generated Continuation Dynamics v0.")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_generated_continuation_dynamics_v0"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_generated_continuation_dynamics(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_generated_continuation_dynamics(
    *,
    out_root: Path = Path(".tmp/finite_relational_generated_continuation_dynamics_v0"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_generated_continuation_dynamics(run_root)


def retain_generated_continuation_dynamics(
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = generated_continuation_dynamics_summary()
    result = {
        "status": "PASS" if summary["verdict"] == "retained" else "REVIEW",
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "case_results.csv", case_rows(summary))
    write_csv(
        out_dir / "generator_manifest.csv",
        generator_manifest_rows(summary),
    )
    write_csv(out_dir / "nonflag_search.csv", nonflag_search_rows())
    write_json(
        out_dir / "nonflag_witness.json",
        {
            "hollow": summary["compatibility"]["hollow"],
            "filled": summary["compatibility"]["filled"],
            "matched_control_panel": summary["compatibility"]["matched_control_panel"],
        },
    )
    write_csv(
        out_dir / "deformation_distribution.csv",
        deformation_distribution_rows(),
    )
    write_csv(
        out_dir / "deformation_system_summary.csv",
        deformation_system_rows(),
    )
    write_csv(
        out_dir / "sensitivity_results.csv",
        sensitivity_rows(summary),
    )
    (out_dir / "report.md").write_text(
        render_report(result),
        encoding="utf-8",
    )
    return result


def render_report(result: dict[str, Any]) -> str:
    compatibility = result["compatibility"]
    deformation = result["deformation"]
    hollow = compatibility["hollow"]
    filled = compatibility["filled"]
    lines = [
        "# Generated Continuation Dynamics v0 Report",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        "",
        "## Case Results",
        "",
    ]
    lines.extend(f"- {case}: {passes}" for case, passes in result["case_results"].items())
    lines.extend(
        [
            "",
            "## Generated Joint Compatibility",
            "",
            (f"- Exhaustive assignments: {compatibility['assignment_count']}"),
            (f"- Hollow assignments: {compatibility['hollow_assignment_count']}"),
            (f"- Filled assignments: {compatibility['filled_assignment_count']}"),
            (f"- Matched filled controls: {compatibility['matched_filled_count']}"),
            (f"- Downward-closure failures: {len(compatibility['downward_closure_failures'])}"),
            (
                "- Kernel/intersection correspondence failures: "
                f"{len(compatibility['intersection_correspondence_failures'])}"
            ),
            "",
            "### Retained hollow witness",
            "",
            f"- Allowed actions: `{json.dumps(hollow['allowed_actions'], sort_keys=True)}`",
            f"- Maximal faces: `{hollow['maximal_faces']}`",
            f"- One-skeleton: `{hollow['one_skeleton']}`",
            f"- Flag: {hollow['is_flag']}",
            "",
            "### Matched filled control",
            "",
            f"- Allowed actions: `{json.dumps(filled['allowed_actions'], sort_keys=True)}`",
            f"- Maximal faces: `{filled['maximal_faces']}`",
            f"- One-skeleton: `{filled['one_skeleton']}`",
            f"- Flag: {filled['is_flag']}",
            "",
            (
                "- Independent-action triple viable: "
                f"{compatibility['independent_action_triple_realizable']}"
            ),
            (f"- Relabeling preserved: {compatibility['relabeling_preserved']}"),
            (f"- Deadlock singleton viable: {compatibility['deadlock_singleton_realizable']}"),
            (f"- Derived-face bridge exact: {compatibility['bridge_faces_equal']}"),
            "",
            "The maximal faces above are outputs of shared-action greatest "
            "fixed-point computations. They were not supplied to the search.",
            "",
            "## Generated Deformation Distributions",
            "",
            (f"- Complete systems: {deformation['manifest']['class_counts']['complete']}"),
            (f"- Reversible systems: {deformation['manifest']['class_counts']['reversible']}"),
            (f"- Absorbing systems: {deformation['manifest']['class_counts']['absorbing']}"),
            "",
            "| Class | h | Expansion | Contraction | Mixed | Equivalent |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in deformation["distribution_rows"]:
        lines.append(
            "| "
            f"{row['generator_class']} | {row['horizon']} | "
            f"{row['structural_expansion_share']:.6f} | "
            f"{row['structural_contraction_share']:.6f} | "
            f"{row['structural_mixed_share']:.6f} | "
            f"{row['structural_equivalent_share']:.6f} |"
        )
    duplicate = deformation["duplicate_action_control"]
    reverse_edge = deformation["reverse_edge_control"]
    lines.extend(
        [
            "",
            "Primary rows count each unique `(source,target)` edge once per "
            "system. Per-system means and action-edge diagnostics are retained "
            "in the CSV output.",
            "",
            "## Sensitivity",
            "",
            (
                "- Deformation relabeling preserved: "
                f"{deformation['relabeling_control']['preserved']}"
            ),
            (
                "- Duplicate action preserved structural verdicts: "
                f"{duplicate['structural_verdicts_preserved']}"
            ),
            (
                "- Duplicate action changed diagnostic action weights: "
                f"{duplicate['action_weight_changed']}"
            ),
            (f"- Synthetic reverse edge excluded: {reverse_edge['synthetic_reverse_excluded']}"),
            (f"- Retained classifier verdicts: {deformation['retained_classifier_verdicts']}"),
            "",
            "## Evidence Classification",
            "",
            "Generator counts, closure, relabeling, deadlock, duplicate-action, "
            "and reverse-edge cases are correctness controls.",
            "",
            "The hollow/filled pair is a constructive strictness witness: "
            "pairwise continuation compatibility does not imply joint "
            "continuation compatibility.",
            "",
            "The deformation frequencies are risky generated results relative "
            "to each declared class and horizon. No pooled frequency is a "
            "universal probability.",
            "",
            "## Claim Boundary",
            "",
            "Graph direction is not a thermodynamic orientation. The absorbing "
            "class is not an entropy model, and the reversible class is only a "
            "finite structural null. This pass does not prove value, agency, "
            "lushness, or Omega.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
