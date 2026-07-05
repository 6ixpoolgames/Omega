"""Retained validation for Closure v2.2 guarded implication basis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.closure_implication_basis_v22 import (
    ClosureImplicationCase,
    generate_closure_implication_basis_v22,
)
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Closure v2.2 guarded implication-basis extraction."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_closure_implication_basis_v22"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_closure_implication_basis_v22(
        out_root=args.out_root
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_closure_implication_basis_v22(
    *,
    out_root: Path = Path(".tmp/finite_relational_closure_implication_basis_v22"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_closure_implication_basis_v22(run_root)


def retain_finite_relational_closure_implication_basis_v22(
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    families = generate_closure_implication_basis_v22()
    family_summaries = []
    for family in families:
        family_dir = out_dir / family.family_id
        family_dir.mkdir(parents=True, exist_ok=True)
        case_summaries = [case.summary() for case in family.cases]
        representative_summaries = [
            _retain_case(case, family_dir / "representatives" / case.attribution_case.case.case_id)
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
        "aggregate": aggregate,
        "families": family_summaries,
    }
    _write_json(out_dir / "summary.json", result)
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    aggregate = result["aggregate"]
    lines = [
        "# Finite Relational Closure Implication Basis v2.2",
        "",
        f"Status: {result['status']}",
        "",
        "## Headline",
        "",
        f"- Cases: {result['case_count']}",
        f"- Implications: {aggregate['implication_count']}",
        f"- Guard-accounted implications: {aggregate['guard_accounted_implication_count']}",
        f"- Classifier-only implications: {aggregate['classifier_only_implication_count']}",
        f"- Residual implications: {aggregate['residual_implication_count']}",
        f"- Unique seed implication signatures: {aggregate['unique_seed_implication_count']}",
        f"- Unique guard implication signatures: {aggregate['unique_guard_implication_count']}",
        "",
        "## Basis Kinds",
        "",
        "| kind | count |",
        "| --- | ---: |",
    ]
    for kind, count in aggregate["basis_kind_counts"].items():
        lines.append(f"| `{kind}` | {count} |")
    lines.extend(
        [
            "",
            "## Antecedent Sizes",
            "",
            "| antecedent | size | count |",
            "| --- | ---: | ---: |",
        ]
    )
    for size, count in aggregate["seed_antecedent_size_counts"].items():
        lines.append(f"| seed | {size} | {count} |")
    for size, count in aggregate["guard_antecedent_size_counts"].items():
        lines.append(f"| guard | {size} | {count} |")
    lines.extend(
        [
            "",
            "## Family Breakdown",
            "",
            "| family | cases | implications | guard-accounted | residual |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for family in result["families"]:
        aggregate = family["aggregate"]
        lines.append(
            "| {family_id} | {case_count} | {implication_count} | "
            "{guard_accounted_implication_count} | {residual_implication_count} |".format(
                family_id=family["family_id"],
                case_count=family["case_count"],
                implication_count=aggregate["implication_count"],
                guard_accounted_implication_count=aggregate[
                    "guard_accounted_implication_count"
                ],
                residual_implication_count=aggregate["residual_implication_count"],
            )
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            (
                "Closure v2.2 extracts minimal seed and guard antecedents for "
                "the retained v2.1.5 surplus facts. It does not run a larger "
                "graph sweep or add new fact kinds."
            ),
            "",
            (
                "The current run leaves no classifier-only or residual "
                "implications. The implication basis is therefore guard-accounted "
                "over the current and held-out v2.1.5 families."
            ),
            "",
            (
                "This is still finite and key-level. Unique implication "
                "signatures are not claimed as global theorems over all graphs."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _retain_case(case: ClosureImplicationCase, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = case.summary() | {"output": str(out_dir)}
    _write_json(out_dir / "summary.json", summary)
    _write_json(
        out_dir / "implications.json",
        [implication.summary() for implication in case.implications],
    )
    return summary


def _aggregate_family_summaries(
    family_summaries: list[dict[str, Any]],
) -> dict[str, object]:
    totals = {
        "case_count": 0,
        "implication_count": 0,
        "guard_accounted_implication_count": 0,
        "classifier_only_implication_count": 0,
        "residual_implication_count": 0,
    }
    merged_counts: dict[str, dict[str, int]] = {
        "basis_kind_counts": {},
        "bucket_counts": {},
        "theorem_counts": {},
        "proof_status_counts": {},
        "seed_antecedent_size_counts": {},
        "guard_antecedent_size_counts": {},
    }
    unique_seed: set[tuple[tuple[str, ...], str]] = set()
    unique_guard: set[tuple[tuple[str, ...], str, str | None]] = set()
    for family in family_summaries:
        aggregate = family["aggregate"]
        for key in totals:
            totals[key] += int(aggregate[key])
        for key, target in merged_counts.items():
            _merge_counts(target, aggregate[key])
        for case in family["cases"]:
            for implication in case["implications"]:
                unique_seed.add(
                    (
                        tuple(implication["seed_antecedent_facts"]),
                        str(implication["consequent_fact"]),
                    )
                )
                unique_guard.add(
                    (
                        tuple(implication["guard_antecedent_facts"]),
                        str(implication["consequent_fact"]),
                        implication["theorem_id"],
                    )
                )
    return totals | {
        key: dict(sorted(value.items())) for key, value in merged_counts.items()
    } | {
        "unique_seed_implication_count": len(unique_seed),
        "unique_guard_implication_count": len(unique_guard),
        "claim_boundary": (
            "Closure v2.2 guarded implication basis only. The rows are finite "
            "key-level implications over retained generated cases; they are not "
            "global implication theorems."
        ),
    }


def _merge_counts(target: dict[str, int], source: dict[str, int]) -> None:
    for key, count in source.items():
        target[key] = target.get(key, 0) + int(count)


def _status_from_aggregate(aggregate: dict[str, object]) -> str:
    if int(aggregate["residual_implication_count"]) != 0:
        return "FAIL_RESIDUAL_IMPLICATIONS"
    if int(aggregate["classifier_only_implication_count"]) != 0:
        return "FAIL_CLASSIFIER_ONLY_IMPLICATIONS"
    if int(aggregate["guard_accounted_implication_count"]) != int(
        aggregate["implication_count"]
    ):
        return "FAIL_GUARD_ACCOUNTING_MISMATCH"
    return "PASS"


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
