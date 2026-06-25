"""Run Agency Diamond Stochastic Hardening v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.agency_diamond.stochastic_hardening import stochastic_hardening_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Agency Diamond Stochastic Hardening v1.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(".tmp/agency_diamond_stochastic_hardening"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_stochastic_hardening(args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_stochastic_hardening(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = stochastic_hardening_summary()
    _write_json(out_dir / "summary.json", summary)
    (out_dir / "report.md").write_text(_render_report(summary), encoding="utf-8")
    return summary


def _render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Agency Diamond Stochastic Hardening v1",
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
    lines.extend(["", "## False-Positive Search", ""])
    for witness in summary["false_positive_search"]["witnesses"]:
        lines.append(f"- {witness['name']}: {'PASS' if witness['passed'] else 'FAIL'}")
    lines.extend(["", "## Ablation Probes", ""])
    for name, passed in summary["ablation_probes"]["probe_status"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Robust Ambiguity", ""])
    for name, passed in summary["robust_ambiguity"]["hypothesis_status"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
