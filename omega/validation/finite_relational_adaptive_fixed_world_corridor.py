"""Retained validation for adaptive fixed-world corridor B2.1 witnesses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.adaptive_fixed_world_corridor import (
    generate_adaptive_fixed_world_corridor_study,
)
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run finite relational adaptive fixed-world corridor witnesses."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_adaptive_fixed_world_corridor"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_adaptive_fixed_world_corridor(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_adaptive_fixed_world_corridor(
    *,
    out_root: Path = Path(".tmp/finite_relational_adaptive_fixed_world_corridor"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_adaptive_fixed_world_corridor(run_root)


def retain_finite_relational_adaptive_fixed_world_corridor(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    study = generate_adaptive_fixed_world_corridor_study()
    summary = study.summary()
    result = {
        "status": _status_from_summary(summary),
        "run_root": str(out_dir),
        **summary,
    }
    _write_json(out_dir / "summary.json", result)
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# Finite Relational Adaptive Fixed-World Corridor B2.1",
        "",
        f"Status: {result['status']}",
        "",
        "## Headline",
        "",
        f"- Cases: {result['case_count']}",
        f"- Learnable ambiguity cases: {result['learnable_case_count']}",
        f"- Unlearnable ambiguity cases: {result['unlearnable_case_count']}",
        f"- Fake-update failure cases: {result['fake_update_case_count']}",
        (
            "- Sound-update truth-preservation failures: "
            f"{result['truth_preservation_failure_count']}"
        ),
        "",
        "## Case Breakdown",
        "",
        "| case | switching start | adaptive start | frozen start | load-bearing actions | read |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for diag in result["diagnostics"]:
        read = _case_read(diag)
        lines.append(
            "| {case_id} | {switching} | {adaptive} | {frozen} | `{actions}` | {read} |".format(
                case_id=diag["case_id"],
                switching=diag["start_in_switching_kernel"],
                adaptive=diag["start_in_adaptive_kernel"],
                frozen=diag["start_in_frozen_kernel"],
                actions=", ".join(diag["epistemically_load_bearing_actions"]) or "none",
                read=read,
            )
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            (
                "The learnable witness separates switching ambiguity from "
                "fixed-world adaptive ambiguity: a safe probe is outside the "
                "ordinary switching corridor but inside the lifted information-state "
                "corridor."
            ),
            "",
            (
                "The unlearnable witness shows that singleton-model viability "
                "does not imply full adaptive viability when no safe shared "
                "identification action exists."
            ),
            "",
            (
                "The fake-update witness retains the learning-layer phantom: "
                "dropping the true model can create a fake corridor state whose "
                "selected action fails in the excluded world."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _case_read(diag: dict[str, Any]) -> str:
    if diag["learnable_gap"]:
        return "safe learning expands beyond switching"
    if diag["unlearnable_gap"]:
        return "unsafe/unavailable learning cannot expand"
    if diag["fake_update_failure"]:
        return "fabricated identification creates phantom corridor"
    return "diagnostic did not hit retained target"


def _status_from_summary(summary: dict[str, object]) -> str:
    return (
        "PASS"
        if summary["case_count"] == 3
        and summary["learnable_case_count"] == 1
        and summary["unlearnable_case_count"] == 1
        and summary["fake_update_case_count"] == 1
        and summary["truth_preservation_failure_count"] == 0
        else "FAIL"
    )


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
