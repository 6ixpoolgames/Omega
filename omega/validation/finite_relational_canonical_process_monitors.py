"""Retained validation for Canonical Process Monitors v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.canonical_process_monitors import (
    canonical_process_monitors_summary,
    case_rows,
    lift_rows,
    residue_rows,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the post-freeze Canonical Process Monitors v0 pilot."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_canonical_process_monitors_v0"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_canonical_process_monitors(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_canonical_process_monitors(
    *,
    out_root: Path = Path(".tmp/finite_relational_canonical_process_monitors_v0"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_canonical_process_monitors(run_root)


def retain_finite_relational_canonical_process_monitors(
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = canonical_process_monitors_summary()
    result = {
        "status": "PASS" if summary["verdict"] == "retained" else "REVIEW",
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "case_results.csv", case_rows(summary))
    write_csv(out_dir / "residue_results.csv", residue_rows(summary))
    write_csv(out_dir / "lift_results.csv", lift_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    cases = result["cases"]
    minimization = cases["canonical_minimization"]
    lifting = cases["lifting_and_projection"]
    family = cases["property_family_residue"]
    symmetric = cases["symmetric_copy"]
    lines = [
        "# Canonical Process Monitors v0 Report",
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
            "## Canonical Property Monitor",
            "",
            f"- Compact presentation states: {minimization['compact_state_count']}",
            f"- Redundant presentation states: {minimization['redundant_state_count']}",
            (
                "- Minimal state counts: "
                f"{minimization['compact_minimal_state_count']}/"
                f"{minimization['redundant_minimal_state_count']}"
            ),
            (f"- Canonical payloads equal: {minimization['canonical_payloads_equal']}"),
            "",
            "## Passive Lift",
            "",
            f"- Reachable lifted states: {lifting['reachable_lifted_state_count']}",
            f"- Lifted edges: {lifting['lifted_edge_count']}",
            (f"- Unique step-lift failures: {len(lifting['unique_step_lift_failures'])}"),
            f"- Unique path lifting: {lifting['unique_path_lifting']}",
            (
                "- Projection-conservation failures: "
                f"{len(lifting['projection_conservation_failures'])}"
            ),
            "",
            "The elementary result is the formal contract. Categorically, the "
            "monitor is a finite-set functor on the concrete path category, "
            "the lift is its category of elements, and projection has the "
            "discrete-opfibration unique-lifting property.",
            "",
            "## Property-Relative Residues",
            "",
        ]
    )
    for property_id, property_result in family["properties"].items():
        lines.extend(
            [
                f"### {property_id}",
                "",
                f"- History residue: {property_result['history_residue']}",
                f"- Corridor residue: {property_result['corridor_residue']}",
                (
                    "- Left admissible action classes: "
                    f"{property_result['left_admissible_action_classes']}"
                ),
                (
                    "- Right admissible action classes: "
                    f"{property_result['right_admissible_action_classes']}"
                ),
                "",
            ]
        )
    lines.extend(
        [
            f"- Family classification: {family['classification']}",
            (f"- Family-core history residue: {family['family_core_history_residue']}"),
            (f"- Family-core corridor residue: {family['family_core_corridor_residue']}"),
            "",
            "## Negative Controls",
            "",
            (
                "- Direct emitted-label difference excluded: "
                f"{cases['direct_emission_control']['direct_emission_excluded']}"
            ),
            f"- Symmetric copy observation equal: {symmetric['branch_observations_equal']}",
            f"- Symmetric copy monitor state equal: {symmetric['monitor_states_equal']}",
            f"- Symmetric copy verdict: {symmetric['verdict']}",
            "",
            "## Evidence Classification",
            "",
            "Unique lifting, minimization, projection conservation, direct-label "
            "exclusion, and the symmetric-copy result are instrument controls.",
            "",
            "The per-property residue vector and family classification are the "
            "risky finite result. They remain relative to the declared property "
            "automata.",
            "",
            "## Claim Boundary",
            "",
            "This pilot does not prove identity, selfhood, consciousness, will, "
            "agency, valuerhood, standing, patienthood, intrinsic continuation "
            "relevance, moral license, or Omega validation.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
