"""Retained validation for Closure v2.1 attribution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.closure_attribution_v21 import (
    ClosureAttributionCase,
    generate_closure_attribution_v21,
)
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Closure v2.1 attribution and held-out checks."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_closure_attribution_v21"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_closure_attribution_v21(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_closure_attribution_v21(
    *,
    out_root: Path = Path(".tmp/finite_relational_closure_attribution_v21"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_closure_attribution_v21(run_root)


def retain_finite_relational_closure_attribution_v21(
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    families = generate_closure_attribution_v21()
    family_summaries = []
    for family in families:
        family_dir = out_dir / family.family_id
        family_dir.mkdir(parents=True, exist_ok=True)
        case_summaries = [case.summary() for case in family.cases]
        representative_summaries = [
            _retain_case(case, family_dir / "representatives" / case.case.case_id)
            for case in family.representative_cases
        ]
        summary = family.summary() | {
            "output": str(family_dir),
            "cases": case_summaries,
            "representative_cases": representative_summaries,
        }
        _write_json(family_dir / "cases.json", case_summaries)
        _write_json(family_dir / "family_summary.json", summary)
        family_summaries.append(summary)

    aggregate = _aggregate_family_summaries(family_summaries)
    result = {
        "status": "PASS",
        "run_root": str(out_dir),
        "family_count": len(families),
        "case_count": sum(len(family.cases) for family in families),
        "residual_case_count": sum(len(family.residual_cases) for family in families),
        "aggregate": aggregate,
        "families": family_summaries,
    }
    _write_json(out_dir / "summary.json", result)
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    bucket_counts = result["aggregate"]["bucket_counts"]
    lines = [
        "# Finite Relational Closure Attribution v2.1",
        "",
        f"Status: {result['status']}",
        "",
        "## Headline",
        "",
        f"- Cases: {result['case_count']}",
        f"- Residual cases: {result['residual_case_count']}",
        f"- Residual facts: {result['aggregate']['residual_fact_count']}",
        (
            "- Bounded process-coherence attributions: "
            f"{bucket_counts.get('bounded_process_coherence_invariance', 0)}"
        ),
        (
            "- Step-implies-path attributions: "
            f"{bucket_counts.get('step_implies_path_lifting', 0)}"
        ),
        "",
        "## Family Breakdown",
        "",
        "| family | cases | residual cases | residual facts |",
        "| --- | ---: | ---: | ---: |",
    ]
    for family in result["families"]:
        lines.append(
            "| {family_id} | {case_count} | {residual_case_count} | "
            "{residual_fact_count} |".format(
                residual_fact_count=family["aggregate"]["residual_fact_count"],
                **family,
            )
        )
    lines.extend(
        [
            "",
            "## Attribution Buckets",
            "",
            "| bucket | count |",
            "| --- | ---: |",
        ]
    )
    for bucket, count in bucket_counts.items():
        lines.append(f"| {bucket} | {count} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            (
                "The fixed classifier attributes all current-v2 and held-out "
                "surplus facts. The current-v2 dynamic-profile facts that were "
                "previously unclassified are attributed to bounded "
                "process-coherence invariance under step lifting."
            ),
            "",
            (
                "This is a calibration result. It supports the interpretation "
                "that Closure v2 found the finite shadow of a known "
                "process-coherence invariance pattern, not yet unexplained new "
                "closure structure."
            ),
            "",
            "## Representatives",
            "",
        ]
    )
    for family in result["families"]:
        lines.append(f"### {family['family_id']}")
        lines.append("")
        lines.append(family["description"])
        lines.append("")
        for case in family["representative_cases"]:
            buckets = ", ".join(
                f"{bucket}={count}"
                for bucket, count in case["attribution_bucket_counts"].items()
            )
            residuals = ", ".join(case["residual_facts"]) or "none"
            lines.append(
                "- `{case_id}`: residuals {residuals}; buckets {buckets}".format(
                    residuals=residuals,
                    buckets=buckets,
                    **case,
                )
            )
        lines.append("")
    lines.extend(
        [
            "## Claim Boundary",
            "",
            (
                "Closure v2.1 is a finite attribution pilot. It does not prove "
                "global invariance, natural admissibility, a modal fixed-point "
                "theorem, agency, identity, value, valuerhood, moral standing, "
                "or Omega validation."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _retain_case(case: ClosureAttributionCase, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = case.summary() | {"output": str(out_dir)}
    _write_json(out_dir / "summary.json", summary)
    _write_json(
        out_dir / "attributions.json",
        [attribution.summary() for attribution in case.attributions],
    )
    return summary


def _aggregate_family_summaries(
    family_summaries: list[dict[str, Any]],
) -> dict[str, object]:
    bucket_counts: dict[str, int] = {}
    support_counts: dict[str, int] = {}
    residual_fact_keys: dict[str, int] = {}
    totals = {
        "surplus_fact_count": 0,
        "residual_fact_count": 0,
        "case_count": 0,
        "residual_case_count": 0,
    }
    for family in family_summaries:
        aggregate = family["aggregate"]
        for key in totals:
            totals[key] += int(aggregate[key])
        for key, count in aggregate["bucket_counts"].items():
            bucket_counts[key] = bucket_counts.get(key, 0) + int(count)
        for key, count in aggregate["support_counts"].items():
            support_counts[key] = support_counts.get(key, 0) + int(count)
        for key, count in aggregate["residual_fact_keys"].items():
            residual_fact_keys[key] = residual_fact_keys.get(key, 0) + int(count)
    return totals | {
        "bucket_counts": dict(sorted(bucket_counts.items())),
        "support_counts": dict(sorted(support_counts.items())),
        "residual_fact_keys": dict(sorted(residual_fact_keys.items())),
        "claim_boundary": (
            "Closure v2.1 attribution only. The classifier is finite and "
            "operational; it is not a formal modal fixed-point theorem."
        ),
    }


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
