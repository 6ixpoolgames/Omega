"""Retained validation for Bounded Behavioral Logic v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.bounded_behavioral_logic import (
    bounded_behavioral_logic_summary,
    case_rows,
    certificate_rows,
    grammar_rows,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the post-freeze Bounded Behavioral Logic v0 pilot."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_bounded_behavioral_logic_v0"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_bounded_behavioral_logic(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_bounded_behavioral_logic(
    *,
    out_root: Path = Path(".tmp/finite_relational_bounded_behavioral_logic_v0"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_bounded_behavioral_logic(run_root)


def retain_finite_relational_bounded_behavioral_logic(
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = bounded_behavioral_logic_summary()
    result = {
        "status": "PASS" if summary["verdict"] == "retained" else "REVIEW",
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "case_results.csv", case_rows(summary))
    write_csv(out_dir / "certificate_correspondence.csv", certificate_rows(summary))
    write_csv(out_dir / "grammar_adequacy.csv", grammar_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    cases = result["cases"]
    basis = cases["derived_basis_parity"]
    characteristic = cases["characteristic_correspondence"]
    grammar = cases["grammar_adequacy"]
    lines = [
        "# Bounded Behavioral Logic v0 Report",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        "",
        "## Case Results",
        "",
    ]
    lines.extend(f"- {case}: {passes}" for case, passes in result["case_results"].items())
    lines.extend(
        [
            "",
            "## Derived Semantic Universe",
            "",
            f"- Representative states: {basis['representative_count']}",
            f"- Distinct semantic types: {basis['semantic_type_count']}",
            (f"- Duplicate representatives removed: {basis['duplicate_representatives_removed']}"),
            f"- Profile mismatches: {len(basis['mismatches'])}",
            "",
            "## Characteristic Certificates",
            "",
            f"- Ordered type pairs checked: {characteristic['ordered_type_pairs']}",
            f"- Correspondence mismatches: {len(characteristic['mismatches'])}",
            (
                "- Certificates using disjunction: "
                f"{characteristic['disjunctive_certificate_count']}"
            ),
            "",
            "## Grammar Adequacy",
            "",
            (f"- Conjunction-only recovers preorder: {grammar['conjunction_only_sufficient']}"),
            (f"- Conjunction-only mismatch count: {len(grammar['conjunction_only_mismatches'])}"),
            (
                "- Disjunction required on retained fixture: "
                f"{grammar['disjunction_required_on_fixture']}"
            ),
            (
                "- Full positive grammar recovers preorder: "
                f"{grammar['full_grammar_recovers_preorder']}"
            ),
            "",
            "## Evidence Classification",
            "",
            "All cases in this pass are instrument-correctness or finite "
            "correspondence checks. The pass contains no discovery verdict.",
            "",
            "The predecessor adaptive-versus-switching strictness result is "
            "classified separately as its risky retained result.",
            "",
            "## Claim Boundary",
            "",
            "This finite pass does not prove general ATL or modal completeness, "
            "value, valuerhood, agency, standing, identity, moral license, or "
            "Omega validation.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
