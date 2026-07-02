"""Run the finite contextual future-field witness package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.contextual_future_fields.witnesses import contextual_future_field_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run finite contextual future-field witnesses."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(".tmp/contextual_future_fields"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_contextual_future_fields(args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_contextual_future_fields(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = contextual_future_field_summary()
    _write_json(out_dir / "summary.json", summary)
    (out_dir / "report.md").write_text(_render_report(summary), encoding="utf-8")
    return summary


def _render_report(summary: dict[str, Any]) -> str:
    no_global = summary["artifacts"]["no_global_extension"]
    holonomy = summary["artifacts"]["holonomy"]
    kernel = summary["artifacts"]["compatibility_thickness_kernel"]
    deformation = summary["artifacts"]["density_deformation"]
    lines = [
        "# Contextual Future Fields v0",
        "",
        f"Status: {summary['status']}",
        "",
        "## Claim Boundary",
        "",
        summary["claim_boundary"],
        "",
        "## Decision Gate",
        "",
    ]
    for name, passed in summary["decision_gate"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.extend(
        [
            "",
            "## No-Global-Extension Witness",
            "",
            f"- status: {no_global['status']}",
        ]
    )
    for name, passed in no_global["decision_gate"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Holonomy Witnesses", "", f"- status: {holonomy['status']}"])
    for name, passed in holonomy["decision_gate"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    for witness in holonomy["witnesses"]:
        lines.extend(
            [
                "",
                f"### {witness['name']}",
                "",
                f"- proxy returned: {witness['proxy_returned']}",
                f"- holonomy nontrivial: {witness['holonomy_nontrivial']}",
                "- changed continuation coordinates: "
                + ", ".join(witness["changed_continuation_coordinates"]),
                "- initial continuation thickness: "
                + witness["initial_continuation_thickness"],
                "- final continuation thickness: " + witness["final_continuation_thickness"],
            ]
        )
    lines.extend(
        [
            "",
            "## Compatibility-Thickness Kernel",
            "",
            f"- status: {kernel['status']}",
        ]
    )
    for name, passed in kernel["decision_gate"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    overlap = kernel["certified_overlap"]
    non_psd = kernel["non_psd_control"]
    lines.extend(
        [
            f"- certified overlap rank: {overlap['rank']}",
            f"- certified overlap PSD: {overlap['psd']}",
            f"- non-PSD control PSD: {non_psd['psd']}",
            "",
            "## Density-Kernel Deformation",
            "",
            f"- status: {deformation['status']}",
        ]
    )
    for name, passed in deformation["decision_gate"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    for witness in deformation["witnesses"]:
        lines.extend(
            [
                "",
                f"### {witness['name']}",
                "",
                f"- diagonal preserved: {witness['diagonal_preserved']}",
                f"- off-diagonal preserved: {witness['off_diagonal_preserved']}",
                f"- PSD preserved: {witness['psd_preserved']}",
                f"- diagonal changes: {len(witness['diagonal_changes'])}",
                f"- off-diagonal changes: {len(witness['off_diagonal_changes'])}",
            ]
        )
    lines.extend(["", "## Public Read", "", summary["public_read"], ""])
    return "\n".join(lines)


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
