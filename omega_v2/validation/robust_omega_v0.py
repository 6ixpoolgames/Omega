"""Retained validation runner for finite May and Robust Omega v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega_v2.experiments.robust_omega_v0 import (
    candidate_class_rows,
    case_result_rows,
    environment_sensitivity_rows,
    may_fiber_rows,
    policy_environment_run_rows,
    robust_fiber_rows,
    robust_omega_summary,
)
from omega_v2.validation.artifacts import (
    timestamped_output_dir,
    write_csv,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run finite witness-retaining May and Robust Omega v0."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/robust_omega_v0"),
    )
    return parser.parse_args()


def run_robust_omega_v0(
    *,
    out_root: Path = Path(".tmp/robust_omega_v0"),
) -> dict[str, Any]:
    return retain_robust_omega_v0(timestamped_output_dir(out_root))


def retain_robust_omega_v0(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    complete_summary = robust_omega_summary()
    public_summary = {
        key: value
        for key, value in complete_summary.items()
        if key != "_objects"
    }
    result = {"run_root": str(out_dir), **public_summary}

    write_json(out_dir / "summary.json", result)
    write_csv(
        out_dir / "case_results.csv",
        case_result_rows(complete_summary),
    )
    write_csv(
        out_dir / "candidate_classes.csv",
        candidate_class_rows(complete_summary),
    )
    write_csv(
        out_dir / "may_fibers.csv",
        may_fiber_rows(complete_summary),
    )
    write_csv(
        out_dir / "robust_fibers.csv",
        robust_fiber_rows(complete_summary),
    )
    write_csv(
        out_dir / "policy_environment_runs.csv",
        policy_environment_run_rows(complete_summary),
    )
    write_csv(
        out_dir / "environment_sensitivity.csv",
        environment_sensitivity_rows(complete_summary),
    )
    (out_dir / "report.md").write_text(
        render_report(result),
        encoding="utf-8",
    )
    return result


def render_report(result: dict[str, Any]) -> str:
    may = result["may_migration"]
    sensitivity = result["environment_sensitivity"]
    hollow = result["robust_hollow_triangle"]
    positive = result["robust_positive_control"]
    lines = [
        "# Omega v2 May and Robust Realization v0 Validation",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        "",
        "## Quantifier Contract",
        "",
        f"- Policy quantifier: {result['semantics']['policy_quantifier']}",
        (
            "- Environment quantifier: "
            f"{result['semantics']['environment_quantifier']}"
        ),
        f"- Run semantics: {result['semantics']['run_semantics']}",
        (
            "- Nonempty environment scope required: "
            f"{result['semantics']['environment_scope_nonempty']}"
        ),
        "",
        "## Case Results",
        "",
    ]
    lines.extend(
        f"- {case}: {passed}"
        for case, passed in result["case_results"].items()
    )
    lines.extend(
        [
            "",
            "## May Migration",
            "",
            f"- Pair fibers: {json.dumps(may['pair_fibers'], sort_keys=True)}",
            f"- Triple witnesses: {may['triple_witness_ids']}",
            f"- Maximal faces: {may['maximal_face_count']}",
            f"- Greatest face exists: {may['greatest_face_exists']}",
            f"- Structural digest: `{may['structural_digest']}`",
            f"- Legacy parity: {may['legacy_parity']}",
            f"- Duplicate invariant: {may['duplicate_invariant']}",
            "",
            "## May but Not Robust",
            "",
            f"- May-compatible: {sensitivity['may_compatible']}",
            f"- Robust over calm scope: {sensitivity['robust_calm']}",
            f"- Robust over full scope: {sensitivity['robust_full']}",
            (
                "- Environment antitone failures: "
                f"{len(sensitivity['environment_antitone_failures'])}"
            ),
            (
                "- Candidate classes stable across scopes: "
                f"{sensitivity['candidate_classes_stable']}"
            ),
            "",
            "## Robust Hollow Triangle",
            "",
            f"- Pairwise Robust: {hollow['all_pairs_robust']}",
            f"- Triple Robust: {hollow['triple_robust']}",
            (
                "- Pair securing policies: "
                f"{json.dumps(hollow['pair_policy_ids'], sort_keys=True)}"
            ),
            f"- Triple securing policies: {hollow['triple_policy_ids']}",
            (
                "- Robust maximal faces: "
                f"{hollow['robust_maximal_face_count']}"
            ),
            (
                "- Candidate antitone failures: "
                f"{len(hollow['candidate_antitone_failures'])}"
            ),
            (
                "- Restriction failures: "
                f"{len(hollow['restriction_failures'])}"
            ),
            (
                "- Robust-implies-May failures: "
                f"{len(hollow['robust_implies_may_failures'])}"
            ),
            f"- Duplicate invariant: {hollow['duplicate_invariant']}",
            "",
            "## Robust Positive Control",
            "",
            f"- Triple Robust: {positive['triple_robust']}",
            f"- Securing policies: {positive['triple_policy_ids']}",
            (
                "- Environment-indexed witnesses: "
                f"{json.dumps(positive['triple_environment_runs'], sort_keys=True)}"
            ),
            "",
            "## Kill Conditions",
            "",
        ]
    )
    lines.extend(
        f"- {condition}: {fired}"
        for condition, fired in result["kill_conditions"].items()
    )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            result["claim_boundary"],
            "",
            (
                "The retained fixtures are exact finite constructions. They do "
                "not validate the supplied candidate, policy, or environment "
                "classes as empirical or moral objects."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    result = run_robust_omega_v0(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
