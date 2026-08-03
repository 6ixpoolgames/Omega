"""Retained validation runner for robust joint separation v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega_v2.experiments.robust_joint_separation_v0 import (
    environment_scope_rows,
    may_fiber_rows,
    policy_environment_run_rows,
    robust_fiber_rows,
    robust_joint_separation_summary,
    structural_control_rows,
    summary_digest,
)
from omega_v2.validation.artifacts import (
    timestamped_output_dir,
    write_csv,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run strict finite Robust joint separation v0."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/robust_joint_separation_v0"),
    )
    return parser.parse_args()


def run_robust_joint_separation_v0(
    *,
    out_root: Path = Path(".tmp/robust_joint_separation_v0"),
) -> dict[str, Any]:
    return retain_robust_joint_separation_v0(
        timestamped_output_dir(out_root)
    )


def retain_robust_joint_separation_v0(
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    complete = robust_joint_separation_summary()
    public = {
        key: value
        for key, value in complete.items()
        if key != "_objects"
    }
    result = {
        "run_root": str(out_dir),
        "summary_digest": summary_digest(complete),
        **public,
    }

    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "may_fibers.csv", may_fiber_rows(complete))
    write_csv(
        out_dir / "robust_fibers.csv",
        robust_fiber_rows(complete),
    )
    write_csv(
        out_dir / "policy_environment_runs.csv",
        policy_environment_run_rows(complete),
    )
    write_csv(
        out_dir / "environment_scope.csv",
        environment_scope_rows(complete),
    )
    write_csv(
        out_dir / "structural_controls.csv",
        structural_control_rows(complete),
    )
    (out_dir / "report.md").write_text(
        render_report(result),
        encoding="utf-8",
    )
    return result


def render_report(result: dict[str, Any]) -> str:
    strict = result["strict"]
    positive = result["positive"]
    lines = [
        "# Omega v2 Robust Joint Separation v0 Validation",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        f"Summary digest: `{result['summary_digest']}`",
        "",
        "## Strict Separation",
        "",
        (
            "- May triple witnesses: "
            f"{strict['may_triple_witness_ids']}"
        ),
        f"- Pair policies: {json.dumps(strict['pair_policy_ids'], sort_keys=True)}",
        f"- Full triple Robust: {strict['full_triple_robust']}",
        f"- Full triple policies: {strict['full_triple_policy_ids']}",
        f"- North triple Robust: {strict['north_triple_robust']}",
        f"- North triple policies: {strict['north_triple_policy_ids']}",
        (
            "- Robust maximal-face count: "
            f"{strict['robust_maximal_face_count']}"
        ),
        "",
        "## Matched Positive",
        "",
        f"- Triple Robust: {positive['triple_robust']}",
        f"- Triple policies: {positive['triple_policy_ids']}",
        (
            "- May payload matches strict fixture: "
            f"{positive['may_payload_matches_strict']}"
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
                "The fixture isolates lookup-table Robust securability from "
                "joint May realization. It does not establish dynamic, "
                "empirical, or moral robustness."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    result = run_robust_joint_separation_v0(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
