"""Retained validation runner for process-interface transport v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega_v2.experiments.process_interface_transport_v0 import (
    block_transport_rows,
    factorization_rows,
    factorized_profile_rows,
    family_transport_rows,
    negative_control_rows,
    run_experiment,
)
from omega_v2.validation.artifacts import (
    timestamped_output_dir,
    write_csv,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run finite process-interface transport v0."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/process_interface_transport_v0"),
    )
    return parser.parse_args()


def run_process_interface_transport_v0(
    *,
    out_root: Path = Path(".tmp/process_interface_transport_v0"),
) -> dict[str, Any]:
    return retain_process_interface_transport_v0(
        timestamped_output_dir(out_root)
    )


def retain_process_interface_transport_v0(
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    complete = run_experiment()
    public = {
        key: value
        for key, value in complete.items()
        if key != "_objects"
    }
    result = {"run_root": str(out_dir), **public}

    write_json(out_dir / "summary.json", result)
    write_csv(
        out_dir / "factorizations.csv",
        factorization_rows(complete),
    )
    write_csv(
        out_dir / "block_transport.csv",
        block_transport_rows(complete),
    )
    write_csv(
        out_dir / "interface_profiles.csv",
        factorized_profile_rows(complete),
    )
    write_csv(
        out_dir / "family_transport.csv",
        family_transport_rows(complete),
    )
    write_csv(
        out_dir / "negative_controls.csv",
        negative_control_rows(complete),
    )
    (out_dir / "report.md").write_text(
        render_report(result),
        encoding="utf-8",
    )
    return result


def render_report(result: dict[str, Any]) -> str:
    refinement = result["refinement"]
    several = result["several_minima"]
    crosscut = result["crosscut"]
    lines = [
        "# Omega v2 Process Interface Transport v0 Validation",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        f"Horizon: {result['horizon']}",
        "",
        "## Exact Transport Controls",
        "",
        (
            "- Relabeling: "
            f"{refinement['relabel_transport']['status']}"
        ),
        (
            "- Coarse to fine: "
            f"{refinement['refined_transport']['status']}"
        ),
        (
            "- Coarse minima: "
            f"{refinement['refined_transport']['source_minimal_interfaces']}"
        ),
        (
            "- Fine minima: "
            f"{refinement['refined_transport']['target_minimal_interfaces']}"
        ),
        (
            "- Fine to coarse: "
            f"{refinement['merged_transport']['status']}"
        ),
        (
            "- Annotation control: "
            f"{refinement['annotation_transport']['status']}"
        ),
        (
            "- Observation-only comparison: "
            f"{refinement['observational_transport']['status']}"
        ),
        (
            "- Query mismatch: "
            f"{refinement['query_mismatch']['status']}"
        ),
        "",
        "## Several Refined Minima",
        "",
        f"- Verdict: {several['transport']['status']}",
        (
            "- Coarse minima: "
            f"{several['transport']['source_minimal_interfaces']}"
        ),
        (
            "- Fine minima: "
            f"{several['transport']['target_minimal_interfaces']}"
        ),
        "",
        "## Cross-cut Obstruction",
        "",
        f"- Same observational signature: {crosscut['same_observational_signature']}",
        f"- Forward exact: {crosscut['forward_audit']['exact']}",
        f"- Reverse exact: {crosscut['reverse_audit']['exact']}",
        f"- Family verdict: {crosscut['transport']['status']}",
        (
            "- Saturation adds: "
            f"{crosscut['source_ab_saturation']['added_members']}"
        ),
        "",
        "## Case Results",
        "",
    ]
    lines.extend(
        f"- {case}: {passed}"
        for case, passed in result["case_results"].items()
    )
    lines.extend(["", "## Kill Conditions", ""])
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
                "The checker compares finite partition-relative interface "
                "families. It does not infer a canonical process boundary."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    result = run_process_interface_transport_v0(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
