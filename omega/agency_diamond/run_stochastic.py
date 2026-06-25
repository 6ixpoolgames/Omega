"""Run Agency Diamond Stochastic Pilot v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.agency_diamond.stochastic_examples import stochastic_pilot_summary


CLAIM_BOUNDARY = (
    "Exploratory finite stochastic agency-diamond pilot only. This uses "
    "exact-rational synthetic controlled systems to test probabilistic "
    "live-vs-open-loop feedback, reflexive maintenance, joint effect, blind "
    "generated profiles, and strong-lumpability coherence controls. It does "
    "not detect agency, identity, value, valuerhood, or Omega, and it does not "
    "validate any empirical transition model."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Agency Diamond Stochastic Pilot v1.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(".tmp/agency_diamond_stochastic"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_stochastic(args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_stochastic(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = stochastic_pilot_summary()
    summary["claim_boundary"] = CLAIM_BOUNDARY
    _write_json(out_dir / "summary.json", summary)
    (out_dir / "report.md").write_text(_render_report(summary), encoding="utf-8")
    return summary


def _render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Agency Diamond Stochastic Pilot v1",
        "",
        f"Status: {summary['status']}",
        "",
        "## Claim Boundary",
        "",
        summary["claim_boundary"],
        "",
        "## Generator",
        "",
        f"- blind seed count: {summary['generator']['blind_seed_count']}",
        f"- horizons: {', '.join(str(horizon) for horizon in summary['generator']['horizons'])}",
        f"- surface: {summary['generator']['surface']}",
        "",
        "## Decision Gate",
        "",
    ]
    for name, passed in summary["decision_gate"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Blind Classification Counts", ""])
    for name, count in summary["blind_classification_counts"].items():
        lines.append(f"- {name}: {count}")
    lines.extend(["", "## Derived Clusters", ""])
    lines.append(f"- cluster count: {summary['derived_clusters']['cluster_count']}")
    for cluster in summary["derived_clusters"]["clusters"][:8]:
        lines.append(
            f"- {cluster['signature']}: {cluster['count']} "
            f"(representative: {cluster['representative']})"
        )
    lines.extend(["", "## Counterexample Search", ""])
    for witness in summary["counterexample_search"]:
        status = "PASS" if witness["passed"] else "FAIL"
        lines.append(f"- {witness['name']}: {status}")
    lines.extend(["", "## Stochastic Coherence", ""])
    lines.append(f"- report count: {summary['coherence']['report_count']}")
    lines.append(
        f"- strongly lumpable: {summary['coherence']['strongly_lumpable_count']}"
    )
    lines.append(f"- non-lumpable: {summary['coherence']['non_lumpable_count']}")
    lines.extend(["", "## Negative Result Retention", ""])
    for name, retained in summary["negative_result_retention"]["retention_status"].items():
        lines.append(f"- {name}: {'retained' if retained else 'missing'}")
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
