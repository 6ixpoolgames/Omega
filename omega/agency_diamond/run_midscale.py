"""Run the finite operational-causal-diamond midscale pilot."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from omega.agency_diamond.examples import canonical_battery, midscale_cases
from omega.agency_diamond.metrics import DiamondMetrics, evaluate_case


CLAIM_BOUNDARY = (
    "Synthetic finite agency-layer pilot only. This does not detect agency, "
    "identity, value, valuerhood, or Omega; it only checks whether declared "
    "finite null-battery systems separate persistence, control, feedback "
    "advantage, reflexive maintenance, and joint-continuation effect."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run agency diamond midscale pilot.")
    parser.add_argument("--out", type=Path, default=Path(".tmp/agency_diamond_midscale"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_midscale(args.out)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_midscale(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    systems = canonical_battery()
    cases = midscale_cases()
    metrics = [evaluate_case(case) for case in cases]
    rows = [metric.as_dict() for metric in metrics]

    _write_json(out_dir / "metrics.json", rows)
    _write_csv(out_dir / "metrics.csv", rows)

    summary = summarize(metrics)
    summary.update(
        {
            "status": "PASS" if summary["all_prespecified_separations_passed"] else "FAIL",
            "claim_boundary": CLAIM_BOUNDARY,
            "system_count": len(systems),
            "case_count": len(cases),
            "outputs": {
                "metrics_json": str(out_dir / "metrics.json"),
                "metrics_csv": str(out_dir / "metrics.csv"),
                "summary_json": str(out_dir / "summary.json"),
                "report_md": str(out_dir / "report.md"),
            },
        }
    )
    _write_json(out_dir / "summary.json", summary)
    (out_dir / "report.md").write_text(render_report(summary, rows), encoding="utf-8")
    return summary


def summarize(metrics: list[DiamondMetrics]) -> dict[str, Any]:
    by_system: dict[str, list[DiamondMetrics]] = defaultdict(list)
    for metric in metrics:
        by_system[metric.system_id].append(metric)

    class_counts = Counter(metric.classification for metric in metrics)
    checks = {
        "passive_has_no_control": all(
            metric.control_reach_count == 0
            for metric in by_system["passive_attractor"]
        ),
        "driven_cycle_has_recurrence_without_control": all(
            metric.control_reach_count == 0
            for metric in by_system["driven_cycle"]
        ) and any(
            metric.recurrence_detected
            for metric in by_system["driven_cycle"]
        ),
        "open_loop_has_control_without_feedback_advantage": any(
            metric.control_reach_count > 0 and metric.feedback_advantage == 0
            for metric in by_system["open_loop_controller"]
        ),
        "feedback_cases_gain_over_replay": all(
            _max_feedback(by_system[system_id]) > 0
            for system_id in ("thermostat", "adaptive_controller", "cooperative_controller")
        ),
        "thermostat_has_no_reflexive_challenge": all(
            metric.reflexive_advantage is None
            for metric in by_system["thermostat"]
        ),
        "self_restoring_has_reflexive_advantage": any(
            metric.reflexive_advantage is not None and metric.reflexive_advantage > 0
            for metric in by_system["self_restoring_controller"]
        ),
        "dominant_controller_has_negative_joint_effect": any(
            metric.joint_effect_delta is not None and metric.joint_effect_delta < 0
            for metric in by_system["dominant_horizon_controller"]
        ),
        "cooperative_controller_has_positive_joint_effect": any(
            metric.joint_effect_delta is not None and metric.joint_effect_delta > 0
            for metric in by_system["cooperative_controller"]
        ),
    }

    return {
        "classification_counts": dict(sorted(class_counts.items())),
        "prespecified_checks": checks,
        "all_prespecified_separations_passed": all(checks.values()),
        "system_summaries": {
            system_id: _system_summary(system_metrics)
            for system_id, system_metrics in sorted(by_system.items())
        },
    }


def render_report(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Agency Diamond Midscale Pilot",
        "",
        f"Status: {summary['status']}",
        "",
        "## Claim Boundary",
        "",
        summary["claim_boundary"],
        "",
        "## Scale",
        "",
        f"- Systems: {summary['system_count']}",
        f"- Cases: {summary['case_count']}",
        "",
        "## Prespecified Checks",
        "",
    ]
    for name, passed in summary["prespecified_checks"].items():
        lines.append(f"- {name}: {'PASS' if passed else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Classification Counts",
            "",
        ]
    )
    for name, count in summary["classification_counts"].items():
        lines.append(f"- {name}: {count}")
    lines.extend(
        [
            "",
            "## Case Rows",
            "",
            "| case | family | horizon | class | feedback advantage | reflexive advantage | joint effect |",
            "|---|---:|---:|---|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            "| {case_id} | {family} | {horizon} | {classification} | "
            "{feedback_advantage} | {reflexive_advantage} | {joint_effect_delta} |".format(
                **row
            )
        )
    lines.append("")
    return "\n".join(lines)


def _system_summary(metrics: list[DiamondMetrics]) -> dict[str, Any]:
    return {
        "case_count": len(metrics),
        "horizons": [metric.horizon for metric in metrics],
        "classifications": sorted(set(metric.classification for metric in metrics)),
        "max_feedback_advantage": _frac(max(metric.feedback_advantage for metric in metrics)),
        "max_reflexive_advantage": _maybe_frac(
            max(
                (
                    metric.reflexive_advantage
                    for metric in metrics
                    if metric.reflexive_advantage is not None
                ),
                default=None,
            )
        ),
        "min_joint_effect_delta": _maybe_frac(
            min(
                (
                    metric.joint_effect_delta
                    for metric in metrics
                    if metric.joint_effect_delta is not None
                ),
                default=None,
            )
        ),
        "max_joint_effect_delta": _maybe_frac(
            max(
                (
                    metric.joint_effect_delta
                    for metric in metrics
                    if metric.joint_effect_delta is not None
                ),
                default=None,
            )
        ),
    }


def _max_feedback(metrics: list[DiamondMetrics]):
    return max(metric.feedback_advantage for metric in metrics)


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _frac(value) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _maybe_frac(value) -> str | None:
    return None if value is None else _frac(value)


if __name__ == "__main__":
    main()
