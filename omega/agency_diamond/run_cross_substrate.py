"""Run Agency Diamond Cross-Substrate v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.agency_diamond.cross_substrate import cross_substrate_summary


CLAIM_BOUNDARY = (
    "Exploratory finite cross-substrate challenge only. This does not detect "
    "agency, identity, value, valuerhood, or Omega; it checks whether the "
    "operational-causal-diamond profile preserves its hierarchy, adversarial "
    "counterexamples, and basic transport controls across several small "
    "generated source grammars with held-out seeds."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Agency Diamond Cross-Substrate v1.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(".tmp/agency_diamond_cross_substrate"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_cross_substrate(args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_cross_substrate(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = cross_substrate_summary()
    summary["claim_boundary"] = CLAIM_BOUNDARY
    _write_json(out_dir / "summary.json", summary)
    (out_dir / "report.md").write_text(_render_report(summary), encoding="utf-8")
    return summary


def _render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Agency Diamond Cross-Substrate v1",
        "",
        f"Status: {summary['status']}",
        "",
        "## Claim Boundary",
        "",
        summary["claim_boundary"],
        "",
        "## Generator",
        "",
        f"- substrates: {', '.join(summary['generator']['substrates'])}",
        f"- train seeds: {', '.join(str(seed) for seed in summary['generator']['train_seeds'])}",
        f"- holdout seeds: {', '.join(str(seed) for seed in summary['generator']['holdout_seeds'])}",
        f"- horizons: {', '.join(str(horizon) for horizon in summary['generator']['horizons'])}",
        "",
        "## Decision Gate",
        "",
    ]
    for name, passed in summary["decision_gate"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Holdout Classification Counts", ""])
    for name, count in summary["holdout_classification_counts"].items():
        lines.append(f"- {name}: {count}")
    lines.extend(["", "## Holdout Classification By Substrate", ""])
    for substrate, counts in summary["holdout_classification_by_substrate"].items():
        rendered = ", ".join(f"{name}: {count}" for name, count in counts.items())
        lines.append(f"- {substrate}: {rendered}")
    lines.extend(["", "## Adversarial Probes", ""])
    for name, passed in summary["adversarial"]["probe_status"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Counterexample Search", ""])
    for witness in summary["counterexample_search"]:
        status = "PASS" if witness["passed"] else "FAIL"
        lines.append(f"- {witness['name']}: {status}")
    lines.extend(["", "## Transport", ""])
    for name, passed in summary["transport"]["checks"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
