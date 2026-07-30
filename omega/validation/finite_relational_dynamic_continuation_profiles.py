"""Retained validation for Dynamic Continuation Profiles v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.dynamic_continuation_profiles import (
    case_rows,
    deformation_rows,
    dynamic_continuation_profiles_summary,
    signature_rows,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the post-freeze Dynamic Continuation Profiles v0 pilot."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_dynamic_continuation_profiles_v0"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_dynamic_continuation_profiles(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_dynamic_continuation_profiles(
    *,
    out_root: Path = Path(".tmp/finite_relational_dynamic_continuation_profiles_v0"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_dynamic_continuation_profiles(run_root)


def retain_finite_relational_dynamic_continuation_profiles(
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = dynamic_continuation_profiles_summary()
    result = {
        "status": "PASS" if summary["verdict"] == "retained" else "REVIEW",
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "case_results.csv", case_rows(summary))
    write_csv(out_dir / "signatures.csv", signature_rows(summary))
    write_csv(out_dir / "deformations.csv", deformation_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    cases = result["cases"]
    controls = result["negative_controls"]
    duplicate = cases["duplicate_outcome"]
    novel = cases["novel_branch"]
    delayed = cases["delayed_divergence"]
    quantifier = cases["action_outcome_quantifier"]
    adaptive = cases["switching_adaptive"]
    bridge = cases["lushness_bridge"]
    lines = [
        "# Dynamic Continuation Profiles v0 Report",
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
            "## Duplicate Resistance",
            "",
            f"- Raw edge count changes: {duplicate['raw_edge_count_changes']}",
            f"- Root behavior types equal: {duplicate['root_types_equal']}",
            f"- Derived profiles equal: {duplicate['profiles_equal']}",
            (
                "- Effect-equivalent duplicate action is idempotent: "
                f"{cases['duplicate_action']['root_types_equal']}"
            ),
            "",
            "## Novelty And Horizon",
            "",
            (f"- Novel branch strictly refines base: {novel['extension_strictly_refines']}"),
            (f"- Strict new represented capabilities: {len(novel['strict_new_capabilities'])}"),
            (f"- First delayed-divergence separation depth: {delayed['first_separation_depth']}"),
            "",
            "## Controller And Environment Quantifiers",
            "",
            (f"- Flattened successor unions equal: {quantifier['flattened_successors_equal']}"),
            f"- Nested behavior types equal: {quantifier['nested_types_equal']}",
            (f"- Choice strictly refines risk: {quantifier['choice_strictly_refines_risk']}"),
            "",
            "## Dynamic Deformation",
            "",
        ]
    )
    lines.extend(
        f"- {expected}: {observed}"
        for expected, observed in cases["deformation"]["verdicts"].items()
    )
    lines.extend(
        [
            "",
            "## Presentation Control",
            "",
            (
                "- State relabeling preserves behavior type/profile: "
                f"{cases['presentation']['state_relabeling_preserves_type']}/"
                f"{cases['presentation']['state_relabeling_preserves_profile']}"
            ),
            (
                "- Action relabeling preserves behavior type/profile: "
                f"{cases['presentation']['action_relabeling_preserves_type']}/"
                f"{cases['presentation']['action_relabeling_preserves_profile']}"
            ),
            (
                "- Atom-respect failures in unsound merge: "
                f"{cases['presentation']['atom_respect_failure_count']}"
            ),
            (
                "- Unsound abstraction rejected: "
                f"{cases['presentation']['unsound_abstraction_rejected']}"
            ),
            "",
            "## Switching And Adaptive Dynamics",
            "",
            f"- Status: {adaptive['status']}",
            f"- First strict adaptive horizon: {adaptive['first_strict_horizon']}",
            (
                "- Sound-update truth-preservation failures: "
                f"{adaptive['sound_update_truth_preservation_failures']}"
            ),
            (f"- Information-state atoms excluded: {adaptive['information_state_atoms_excluded']}"),
            "",
            "## Lushness Instrument Bridge",
            "",
            (
                "- Duplicate family profile remains equal: "
                f"{bridge['duplicate_family_profile_equal']}"
            ),
            (f"- Novel family profile is strict: {bridge['novel_family_profile_strict']}"),
            (
                "- Attributes are dynamic fingerprints: "
                f"{bridge['attributes_are_dynamic_fingerprints']}"
            ),
            "",
            "## Negative Controls",
            "",
        ]
    )
    lines.extend(f"- {control}: {passes}" for control, passes in controls.items())
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"Primary instrument: {result['primary_instrument']}.",
            f"Bridge: {result['bridge']}.",
            f"Remaining debt: {result['remaining_debt']}.",
            "",
            "## Claim Boundary",
            "",
            "This finite pilot does not prove value, valuerhood, standing, "
            "agency, autonomy, patienthood, universal lushness, thermodynamic "
            "law, moral licensing, paperclipper defeat, or Omega validation.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
