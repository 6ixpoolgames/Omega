"""Run the bounded agency-diamond spectral pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.agency_diamond.spectral import spectral_pilot_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run agency-diamond spectral pilot.")
    parser.add_argument("--out", type=Path, default=Path(".tmp/agency_diamond_spectral"))
    parser.add_argument("--horizon", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_spectral(args.out, horizon=args.horizon)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_spectral(out_dir: Path, *, horizon: int = 3) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = spectral_pilot_summary(horizon=horizon)
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (out_dir / "report.md").write_text(render_report(summary), encoding="utf-8")
    return summary


def render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Agency Diamond Spectral Pilot v0",
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
            "## Strictness Witness",
            "",
            f"- status: {summary['strictness']['status']}",
            "- positive case joint effect: "
            + summary["strictness"]["positive_case"]["joint_effect_delta"],
            "- negative case joint effect: "
            + summary["strictness"]["negative_case"]["joint_effect_delta"],
            "- shared own live-maintenance score: "
            + summary["strictness"]["positive_case"]["live_maintenance_score"],
            "",
            "## Profiles",
            "",
            "| system | family | spectral radius | complex modes | max | phase angles |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for profile in summary["profiles"]:
        angles = ", ".join(str(angle) for angle in profile["nonzero_phase_angles"])
        lines.append(
            "| {system_id} | {family} | {spectral_radius} | {complex_mode_count} | "
            "{max_abs_imaginary} | {angles} |".format(
                angles=angles or "none",
                **profile,
            )
        )
    lines.extend(["", "## Public Read", "", summary["public_read"], ""])
    return "\n".join(lines)


if __name__ == "__main__":
    main()
