"""Retained validation for Closure v2.1.5 guard-theorem attribution."""

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
        description="Run Closure v2.1.5 guard-theorem attribution."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_closure_guard_v215"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_closure_guard_v215(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_closure_guard_v215(
    *,
    out_root: Path = Path(".tmp/finite_relational_closure_guard_v215"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_closure_guard_v215(run_root)


def retain_finite_relational_closure_guard_v215(out_dir: Path) -> dict[str, Any]:
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
        "status": _status_from_aggregate(aggregate),
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
    aggregate = result["aggregate"]
    theorem_counts = aggregate["theorem_counts"]
    lines = [
        "# Finite Relational Closure Guard Attribution v2.1.5",
        "",
        f"Status: {result['status']}",
        "",
        "## Headline",
        "",
        f"- Cases: {result['case_count']}",
        f"- Surplus facts: {aggregate['surplus_fact_count']}",
        f"- Theorem-backed facts: {aggregate['theorem_backed_fact_count']}",
        f"- Classifier-only facts: {aggregate['classifier_only_fact_count']}",
        f"- Residual cases: {result['residual_case_count']}",
        f"- Residual facts: {aggregate['residual_fact_count']}",
        (
            "- Process-coherence profile guard facts: "
            f"{theorem_counts.get('closure.guard.process_coherence_entails_bounded_profile_invariance', 0)}"
        ),
        (
            "- Step-to-path guard facts: "
            f"{theorem_counts.get('closure.guard.step_lifting_implies_bounded_path_lifting', 0)}"
        ),
        "",
        "## Guard Theorems",
        "",
        "| theorem | count |",
        "| --- | ---: |",
    ]
    for theorem_id, count in theorem_counts.items():
        lines.append(f"| `{theorem_id}` | {count} |")
    lines.extend(
        [
            "",
            "## Family Breakdown",
            "",
            "| family | cases | theorem-backed | classifier-only | residual facts |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for family in result["families"]:
        aggregate = family["aggregate"]
        lines.append(
            "| {family_id} | {case_count} | {theorem_backed_fact_count} | "
            "{classifier_only_fact_count} | {residual_fact_count} |".format(
                family_id=family["family_id"],
                case_count=family["case_count"],
                theorem_backed_fact_count=aggregate["theorem_backed_fact_count"],
                classifier_only_fact_count=aggregate["classifier_only_fact_count"],
                residual_fact_count=aggregate["residual_fact_count"],
            )
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            (
                "Closure v2.1.5 adds proof attribution to the v2.1 classifier. "
                "Each surplus fact is now attached to a named finite guard "
                "theorem and the hypothesis facts used by that theorem."
            ),
            "",
            (
                "The process-coherence bucket is no longer merely a label: the "
                "runner verifies, for each case, that every generated "
                "presentation satisfying the support fact also satisfies the "
                "attributed bounded profile or visibility fact."
            ),
            "",
            (
                "This remains a finite guard pass over the generated Closure v2 "
                "fact language. It is not a global modal fixed-point theorem or "
                "a natural-admissibility theorem."
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
    theorem_counts: dict[str, int] = {}
    proof_status_counts: dict[str, int] = {}
    residual_fact_keys: dict[str, int] = {}
    totals = {
        "surplus_fact_count": 0,
        "theorem_backed_fact_count": 0,
        "classifier_only_fact_count": 0,
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
        for key, count in aggregate["theorem_counts"].items():
            theorem_counts[key] = theorem_counts.get(key, 0) + int(count)
        for key, count in aggregate["proof_status_counts"].items():
            proof_status_counts[key] = proof_status_counts.get(key, 0) + int(count)
        for key, count in aggregate["residual_fact_keys"].items():
            residual_fact_keys[key] = residual_fact_keys.get(key, 0) + int(count)
    return totals | {
        "bucket_counts": dict(sorted(bucket_counts.items())),
        "support_counts": dict(sorted(support_counts.items())),
        "theorem_counts": dict(sorted(theorem_counts.items())),
        "proof_status_counts": dict(sorted(proof_status_counts.items())),
        "residual_fact_keys": dict(sorted(residual_fact_keys.items())),
        "claim_boundary": (
            "Closure v2.1.5 guard attribution only. The guard checks are finite "
            "proof obligations over generated presentations; they are not a "
            "global modal fixed-point theorem."
        ),
    }


def _status_from_aggregate(aggregate: dict[str, object]) -> str:
    if int(aggregate["residual_fact_count"]) != 0:
        return "FAIL_RESIDUAL_FACTS"
    if int(aggregate["classifier_only_fact_count"]) != 0:
        return "FAIL_CLASSIFIER_ONLY_FACTS"
    if int(aggregate["theorem_backed_fact_count"]) != int(
        aggregate["surplus_fact_count"]
    ):
        return "FAIL_THEOREM_BACKING_MISMATCH"
    return "PASS"


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
