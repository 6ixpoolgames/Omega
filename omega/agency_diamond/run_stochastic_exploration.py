"""Run Agency Diamond Stochastic Exploration v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.agency_diamond.stochastic_exploration import stochastic_exploration_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Agency Diamond Stochastic Exploration v1."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(".tmp/agency_diamond_stochastic_exploration"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_stochastic_exploration(args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_stochastic_exploration(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = stochastic_exploration_summary()
    _write_json(out_dir / "summary.json", summary)
    (out_dir / "report.md").write_text(_render_report(summary), encoding="utf-8")
    return summary


def _render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Agency Diamond Stochastic Exploration v1",
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
    lines.extend(["", "## Held-Out Search", ""])
    heldout = summary["heldout_search"]
    lines.append(f"- status: {heldout['status']}")
    lines.append(f"- systems: {heldout['case_counts']['systems']}")
    lines.append(f"- metric cases: {heldout['case_counts']['metric_cases']}")
    lines.append(f"- cluster count: {heldout['derived_clusters']['cluster_count']}")
    for name, passed in heldout["decision_gate"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Cross-Substrate Profiles", ""])
    cross = summary["cross_substrate"]
    lines.append(f"- status: {cross['status']}")
    for name, counts in cross["classification_by_substrate"].items():
        lines.append(f"- {name}: {counts}")
    lines.extend(["", "## Calibration / Phase Curves", ""])
    calibration = summary["calibration_phase"]
    lines.append(f"- status: {calibration['status']}")
    for name, threshold in calibration["thresholds"].items():
        lines.append(f"- {name}: {threshold}")
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
