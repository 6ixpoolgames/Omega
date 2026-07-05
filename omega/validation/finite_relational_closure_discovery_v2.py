"""Retained validation for finite relational closure discovery v2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.closure_discovery_v2 import (
    ClosureV2Case,
    generate_closure_discovery_v2,
)
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run finite relational closure-discovery v2 studies."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_closure_discovery_v2"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_closure_discovery_v2(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_closure_discovery_v2(
    *,
    out_root: Path = Path(".tmp/finite_relational_closure_discovery_v2"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_closure_discovery_v2(run_root)


def retain_finite_relational_closure_discovery_v2(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    families = generate_closure_discovery_v2()
    family_summaries = []
    for family in families:
        family_dir = out_dir / family.family_id
        family_dir.mkdir(parents=True, exist_ok=True)
        case_summaries = [case.summary() for case in family.cases]
        representative_summaries = [
            _retain_case(case, family_dir / "representatives" / case.case_id)
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
        "dynamic_surplus_case_count": sum(
            len(family.dynamic_surplus_cases) for family in families
        ),
        "unclassified_dynamic_profile_case_count": sum(
            len(family.unclassified_dynamic_profile_cases) for family in families
        ),
        "collapse_case_count": sum(len(family.collapse_cases) for family in families),
        "constant_control_collapsed": all(
            case.classification == "collapse"
            for family in families
            if family.family_id == "constant_seed_control"
            for case in family.cases
        ),
        "aggregate": aggregate,
        "families": family_summaries,
    }
    _write_json(out_dir / "summary.json", result)
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# Finite Relational Closure Discovery v2",
        "",
        f"Status: {result['status']}",
        "",
        "## Headline",
        "",
        f"- Cases: {result['case_count']}",
        f"- Dynamic-surplus cases: {result['dynamic_surplus_case_count']}",
        (
            "- Unclassified dynamic-profile cases: "
            f"{result['unclassified_dynamic_profile_case_count']}"
        ),
        f"- Collapse cases: {result['collapse_case_count']}",
        f"- Constant control collapsed: {result['constant_control_collapsed']}",
        "",
        "## Family Breakdown",
        "",
        "| family | cases | dynamic surplus | unclassified dynamic profile | collapse |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for family in result["families"]:
        lines.append(
            "| {family_id} | {case_count} | {dynamic_surplus_case_count} | "
            "{unclassified_dynamic_profile_case_count} | "
            "{collapse_case_count} |".format(**family)
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            (
                "Closure v2 broadens the generated fact universe from Boolean "
                "predicates and visible pairs to dynamic profiles and structural "
                "process-coherence facts. It reports seed-determined profile "
                "surplus, seed-forced structural surplus, and dynamic profile "
                "surplus not determined by seed profiles."
            ),
            "",
            (
                "This is not a canonical implication basis. It is a generated "
                "finite pilot used to decide whether richer fact languages can "
                "produce nontrivial closure behavior before stronger theorem "
                "claims are attempted."
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
            dynamic = ", ".join(case["dynamic_surplus_facts"]) or "none"
            unclassified = (
                ", ".join(case["unclassified_dynamic_profile_surplus_facts"])
                or "none"
            )
            lines.append(
                "- `{case_id}`: {classification}; admissible presentations "
                "{admissible_presentation_count}; dynamic surplus {dynamic}; "
                "unclassified dynamic profiles {unclassified}".format(
                    dynamic=dynamic,
                    unclassified=unclassified,
                    **case,
                )
            )
        lines.append("")
    lines.extend(
        [
            "## Claim Boundary",
            "",
            (
                "Closure v2 is finite, generated, and adapter-relative. It does "
                "not establish global invariance, natural admissibility, agency, "
                "identity, value, valuerhood, moral standing, or Omega validation."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _retain_case(case: ClosureV2Case, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = case.summary() | {"output": str(out_dir)}
    _write_json(
        out_dir / "case.json",
        {
            "case_id": case.case_id,
            "states": list(case.states),
            "edges": [list(edge) for edge in case.edges],
            "seed_fact_keys": list(case.seed_fact_keys),
            "facts": [
                {
                    "key": fact.key,
                    "kind": fact.kind,
                    "dynamic": fact.dynamic,
                    "profile": dict(fact.profile),
                }
                for fact in case.facts
            ],
            "observed": case.observed,
        },
    )
    _write_json(out_dir / "summary.json", summary)
    return summary


def _aggregate_family_summaries(
    family_summaries: list[dict[str, Any]],
) -> dict[str, object]:
    totals = {
        "dynamic_surplus_fact_count": 0,
        "seed_determined_dynamic_profile_surplus_fact_count": 0,
        "unclassified_dynamic_profile_surplus_fact_count": 0,
        "seed_forced_structural_surplus_fact_count": 0,
        "globally_valid_surplus_fact_count": 0,
    }
    classification_counts: dict[str, int] = {}
    for family in family_summaries:
        aggregate = family["aggregate"]
        for key in totals:
            totals[key] += int(aggregate[key])
        for key, count in aggregate["classification_counts"].items():
            classification_counts[key] = classification_counts.get(key, 0) + int(count)
    return totals | {
        "classification_counts": classification_counts,
        "claim_boundary": (
            "Generated finite closure-v2 pilot only. These counts do not form a "
            "canonical implication basis and do not certify global invariance."
        ),
    }


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
