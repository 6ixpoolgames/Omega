"""Run agency-diamond hardening pilots."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from omega.agency_diamond.baselines import (
    find_baseline_collisions,
    required_collision_status,
    strictness_status,
    strictness_witnesses,
)
from omega.agency_diamond.examples import midscale_cases
from omega.agency_diamond.generated import evaluate_generated_variants
from omega.agency_diamond.metrics import evaluate_case
from omega.agency_diamond.transport import transport_pilot


CLAIM_BOUNDARY = (
    "Exploratory synthetic finite agency-layer hardening only. This does not "
    "detect agency, identity, value, valuerhood, or Omega; it tests whether the "
    "operational-causal-diamond pilot rejects simple baselines, survives "
    "generated relabel/decoy variants, and obeys basic state-presentation "
    "transport controls."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run agency diamond hardening pilots.")
    parser.add_argument("--out", type=Path, default=Path(".tmp/agency_diamond_hardening"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_hardening(args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_hardening(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = [evaluate_case(case) for case in midscale_cases()]
    collisions = find_baseline_collisions(metrics)
    strictness = strictness_witnesses(metrics)
    generated = evaluate_generated_variants()
    transport = transport_pilot()

    collision_status = required_collision_status(collisions)
    strict_status = strictness_status(strictness)
    decision_gate = {
        "required_baseline_collisions_found": all(collision_status.values()),
        "strictness_witnesses_passed": all(strict_status.values()),
        "generated_profiles_preserved": bool(generated["all_profiles_preserved"]),
        "transport_controls_passed": bool(transport["all_transport_checks_passed"]),
    }
    summary = {
        "status": "PASS" if all(decision_gate.values()) else "FAIL",
        "claim_boundary": CLAIM_BOUNDARY,
        "base_case_count": len(metrics),
        "base_classification_counts": dict(
            sorted(Counter(metric.classification for metric in metrics).items())
        ),
        "baseline_collision_count": len(collisions),
        "required_baseline_collision_status": collision_status,
        "baseline_collision_witnesses": [witness.as_dict() for witness in collisions],
        "strictness_status": strict_status,
        "strictness_witnesses": [witness.as_dict() for witness in strictness],
        "generated": generated,
        "transport": transport,
        "decision_gate": decision_gate,
    }
    _write_json(out_dir / "summary.json", summary)
    (out_dir / "report.md").write_text(_render_report(summary), encoding="utf-8")
    return summary


def _render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Agency Diamond Hardening v1",
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
            "## Required Baseline Collisions",
            "",
        ]
    )
    for name, passed in summary["required_baseline_collision_status"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Strictness Witnesses",
            "",
        ]
    )
    for witness in summary["strictness_witnesses"]:
        status = "PASS" if witness["passed"] else "FAIL"
        lines.append(f"- {witness['name']}: {status} ({witness['left_case']} vs {witness['right_case']})")
    lines.extend(
        [
            "",
            "## Generated Variants",
            "",
            f"- variants: {summary['generated']['variant_count']}",
            f"- cases: {summary['generated']['case_count']}",
            f"- all profiles preserved: {summary['generated']['all_profiles_preserved']}",
            "",
            "## Transport Controls",
            "",
        ]
    )
    for name, passed in summary["transport"]["checks"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
