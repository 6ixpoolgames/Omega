"""Retained validation for finite relational closure discovery."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.closure_discovery import (
    ClosureDiscoveryCase,
    generate_closure_discovery,
)
from omega.adapters.finite_relational.model import load_model, model_digest
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run generated finite relational closure-discovery studies."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_closure_discovery"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_closure_discovery(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_closure_discovery(
    *,
    out_root: Path = Path(".tmp/finite_relational_closure_discovery"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_closure_discovery(run_root)


def retain_finite_relational_closure_discovery(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    families = generate_closure_discovery()
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

    result = {
        "status": "PASS",
        "run_root": str(out_dir),
        "family_count": len(families),
        "case_count": sum(len(family.cases) for family in families),
        "nonconstant_surplus_case_count": sum(
            len(family.nonconstant_surplus_cases) for family in families
        ),
        "collapse_case_count": sum(len(family.collapse_cases) for family in families),
        "all_families_have_positive_and_collapse_controls": all(
            family.nonconstant_surplus_cases and family.collapse_cases
            for family in families
        ),
        "families": family_summaries,
    }
    _write_json(out_dir / "summary.json", result)
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# Finite Relational Closure Discovery v0",
        "",
        f"Status: {result['status']}",
        "",
        "## Headline",
        "",
        (
            f"- Cases: {result['case_count']}"
        ),
        (
            "- Nonconstant-surplus cases: "
            f"{result['nonconstant_surplus_case_count']}"
        ),
        f"- Collapse cases: {result['collapse_case_count']}",
        (
            "- Every family has positive and collapse controls: "
            f"{result['all_families_have_positive_and_collapse_controls']}"
        ),
        "",
        "## Family Breakdown",
        "",
        "| family | cases | nonconstant surplus | collapse | inconsistent seed |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for family in result["families"]:
        lines.append(
            "| {family_id} | {case_count} | {nonconstant_surplus_case_count} | "
            "{collapse_case_count} | {inconsistent_seed_case_count} |".format(
                **family
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            (
                "This is generated finite closure discovery over small adapter "
                "substrates. It does not predeclare expected surplus facts. It "
                "does not prove global invariance, agency, value, Omega, or "
                "empirical model validity."
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
            facts = ", ".join(case["nonconstant_surplus_target_facts"]) or "none"
            lines.append(
                "- `{case_id}`: {classification}; admissible presentations "
                "{admissible_presentation_count}; surplus target facts {facts}".format(
                    facts=facts,
                    **case,
                )
            )
        lines.append("")
    return "\n".join(lines)


def _retain_case(case: ClosureDiscoveryCase, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    loaded = load_model(case.model)
    summary = case.summary() | {"output": str(out_dir)}
    _write_json(out_dir / "model.json", case.model)
    (out_dir / "model_digest.txt").write_text(
        f"{model_digest(loaded)}\n",
        encoding="utf-8",
    )
    _write_json(out_dir / "observed_closure.json", case.observed)
    _write_json(out_dir / "summary.json", summary)
    return summary


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
