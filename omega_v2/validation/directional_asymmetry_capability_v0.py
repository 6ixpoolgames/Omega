"""Retained validation runner for directional asymmetry and capability v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega_v2.experiments.directional_asymmetry_capability_v0 import (
    case_result_rows,
    directional_asymmetry_capability_summary,
    passive_asymmetry_rows,
    record_selector_rows,
    reversible_action_rows,
)
from omega_v2.validation.artifacts import (
    timestamped_output_dir,
    write_csv,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run directional asymmetry and operational capability v0."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/directional_asymmetry_capability_v0"),
    )
    parser.add_argument("--horizon", type=int, default=3)
    return parser.parse_args()


def run_directional_asymmetry_capability_v0(
    *,
    out_root: Path = Path(".tmp/directional_asymmetry_capability_v0"),
    horizon: int = 3,
) -> dict[str, Any]:
    return retain_directional_asymmetry_capability_v0(
        timestamped_output_dir(out_root),
        horizon=horizon,
    )


def retain_directional_asymmetry_capability_v0(
    out_dir: Path,
    *,
    horizon: int = 3,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = directional_asymmetry_capability_summary(horizon=horizon)
    result = {"run_root": str(out_dir), **summary}
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "case_results.csv", case_result_rows(summary))
    write_csv(
        out_dir / "passive_asymmetry.csv",
        passive_asymmetry_rows(summary),
    )
    write_csv(
        out_dir / "reversible_action_census.csv",
        reversible_action_rows(summary),
    )
    write_csv(
        out_dir / "record_selector_comparison.csv",
        record_selector_rows(summary),
    )
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    passive = result["passive_asymmetry"]
    census = result["reversible_action_census"]
    matched = result["matched_record_selector"]
    balanced = matched["balanced"]
    biased = matched["biased"]
    lines = [
        "# Directional Asymmetry and Operational Capability v0 Validation",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        f"Finite path horizon: {result['horizon']}",
        "",
        "## Hypothesis Verdicts",
        "",
    ]
    lines.extend(
        f"- {hypothesis}: {verdict}"
        for hypothesis, verdict in result["hypothesis_verdicts"].items()
    )
    lines.extend(
        [
            "",
            "## Case Results",
            "",
        ]
    )
    lines.extend(
        f"- {case}: {passed}" for case, passed in result["case_results"].items()
    )
    lines.extend(
        [
            "",
            "## Passive Biased Cycle",
            "",
            (
                "- Path-reversal total variation: "
                f"{passive['directionality']['comparison']['total_variation']}"
            ),
            (
                "- Reciprocal support: "
                f"{passive['directionality']['comparison']['support_equal']}"
            ),
            (
                "- Causal action influence: "
                f"{passive['features']['causal_action_influence']}"
            ),
            (
                "- Record-sensitive selection: "
                f"{passive['features']['record_sensitive_selection']}"
            ),
            (
                "- Closed-loop persistence: "
                f"{passive['features']['closed_loop_persistence']}"
            ),
            "",
            "## Reversal-Paired Action Census",
            "",
            f"- Permutations: {census['permutation_count']}",
            f"- Policies: {census['policy_count']}",
            f"- Manifest digest: `{census['manifest_digest']}`",
            (
                "- All primitive actions bijective: "
                f"{census['all_primitive_actions_bijective']}"
            ),
            (
                "- All reversal contracts hold: "
                f"{census['all_reversal_contracts_hold']}"
            ),
            (
                "- All constant forward/reverse distances zero: "
                f"{census['all_reverse_pair_distances_zero']}"
            ),
            (
                "- Noninjective mixed-policy witnesses: "
                f"{census['qualifying_witness_count']}"
            ),
            (
                "- First witness: "
                f"{json.dumps(census['first_qualifying_witness'], sort_keys=True)}"
            ),
            "",
            "## Matched Record-Sensitive Pair",
            "",
            (
                "- Balanced / biased directional total variation: "
                f"{balanced['directionality']['comparison']['total_variation']} / "
                f"{biased['directionality']['comparison']['total_variation']}"
            ),
            (
                "- Balanced selector / baseline branch fidelity: "
                f"{balanced['selector_branch_fidelity']} / "
                f"{balanced['baseline_branch_fidelity']}"
            ),
            (
                "- Biased selector / baseline branch fidelity: "
                f"{biased['selector_branch_fidelity']} / "
                f"{biased['baseline_branch_fidelity']}"
            ),
            (
                "- Policy-deformation total variation, balanced / biased: "
                f"{balanced['policy_deformation_total_variation']} / "
                f"{biased['policy_deformation_total_variation']}"
            ),
            (
                "- Selector closed-loop reversal TV, balanced / biased: "
                f"{balanced['selector_closed_loop_directionality']['total_variation']} / "
                f"{biased['selector_closed_loop_directionality']['total_variation']}"
            ),
            (
                "- Selector closed-loop reciprocal support, balanced / biased: "
                f"{balanced['selector_closed_loop_directionality']['support_equal']} / "
                f"{biased['selector_closed_loop_directionality']['support_equal']}"
            ),
            (
                "- Operational signature unchanged: "
                f"{matched['operational_signature_unchanged']}"
            ),
            (
                "- Branch fidelity unchanged: "
                f"{matched['branch_fidelity_unchanged']}"
            ),
            (
                "- Policy deformation unchanged: "
                f"{matched['policy_deformation_unchanged']}"
            ),
            "",
            "Matched controls:",
            "",
        ]
    )
    lines.extend(
        f"- {control}: {holds}"
        for control, holds in matched["matched_surface"].items()
    )
    lines.extend(
        [
            "",
            "## Dependency Surface",
            "",
        ]
    )
    for dependency_class, dependencies in result["dependencies"].items():
        lines.append(f"- {dependency_class}: {', '.join(dependencies)}")
    lines.extend(
        [
            "",
            "## Kill Conditions",
            "",
        ]
    )
    lines.extend(
        f"- {condition}: {fired}"
        for condition, fired in result["kill_conditions"].items()
    )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            result["claim_boundary"],
            "",
            (
                "The independent-product control does not test a directional "
                "resource coupled to controller operation."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    result = run_directional_asymmetry_capability_v0(
        out_root=args.out_root,
        horizon=args.horizon,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
