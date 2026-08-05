"""Retained validation runner for generated-controller Robust separation v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega_v2.experiments.generated_controller_robust_separation_v0 import (
    behavior_class_rows,
    controller_rows,
    environment_scope_rows,
    generated_controller_robust_separation_summary,
    generated_run_rows,
    may_fiber_rows,
    robust_fiber_rows,
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
        description=(
            "Run finite generated-controller Robust joint separation v0."
        )
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(
            ".tmp/generated_controller_robust_separation_v0"
        ),
    )
    return parser.parse_args()


def run_generated_controller_robust_separation_v0(
    *,
    out_root: Path = Path(
        ".tmp/generated_controller_robust_separation_v0"
    ),
) -> dict[str, Any]:
    return retain_generated_controller_robust_separation_v0(
        timestamped_output_dir(out_root)
    )


def retain_generated_controller_robust_separation_v0(
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    complete = generated_controller_robust_separation_summary()
    public = {
        key: value for key, value in complete.items() if key != "_objects"
    }
    result = {
        "run_root": str(out_dir),
        "summary_digest": summary_digest(complete),
        **public,
    }

    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "controllers.csv", controller_rows(complete))
    write_csv(
        out_dir / "behavior_classes.csv",
        behavior_class_rows(complete),
    )
    write_csv(
        out_dir / "generated_runs.csv",
        generated_run_rows(complete),
    )
    write_csv(out_dir / "may_fibers.csv", may_fiber_rows(complete))
    write_csv(
        out_dir / "robust_fibers.csv",
        robust_fiber_rows(complete),
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
        "# Omega v2 Generated-Controller Robust Separation v0 Validation",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        f"Summary digest: `{result['summary_digest']}`",
        "",
        "## Controller Class",
        "",
        f"- Enumerated controllers: {strict['controller_count']}",
        f"- Generated behavior classes: {strict['behavior_class_count']}",
        (
            "- Pair-securing sequences: "
            f"{json.dumps(strict['pair_sequences'], sort_keys=True)}"
        ),
        "",
        "## Strict Separation",
        "",
        (
            "- May triple witness count: "
            f"{strict['may_triple_witness_count']}"
        ),
        (
            "- North triple sequences: "
            f"{strict['north_triple_sequences']}"
        ),
        (
            "- South triple sequences: "
            f"{strict['south_triple_sequences']}"
        ),
        (
            "- Full-scope triple sequences: "
            f"{strict['full_triple_sequences']}"
        ),
        "",
        "## Matched Positive",
        "",
        f"- Full-scope triple sequences: {positive['triple_sequences']}",
        (
            "- Strict/positive May support match: "
            f"{result['strict_positive_may_support_match']}"
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
                "The run exhausts one bounded deterministic controller class. "
                "It does not identify that class with agency, valuerhood, "
                "empirical control, or moral compatibility."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    result = run_generated_controller_robust_separation_v0(
        out_root=args.out_root
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
