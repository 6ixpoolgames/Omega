"""Retained validation for Alpha-Omega Foundation v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.alpha_omega_foundation import (
    alpha_omega_foundation_summary,
    directionality_rows,
    omega_fiber_rows,
    presentation_rows,
    process_rows,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the post-freeze Alpha-Omega Foundation v0 validation."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_alpha_omega_foundation_v0"),
    )
    parser.add_argument("--horizon", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_alpha_omega_foundation(
        out_root=args.out_root,
        horizon=args.horizon,
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_alpha_omega_foundation(
    *,
    out_root: Path = Path(".tmp/finite_relational_alpha_omega_foundation_v0"),
    horizon: int = 3,
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_alpha_omega_foundation(
        run_root,
        horizon=horizon,
    )


def retain_finite_relational_alpha_omega_foundation(
    out_dir: Path,
    *,
    horizon: int = 3,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = alpha_omega_foundation_summary(horizon=horizon)
    result = {
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(
        out_dir / "case_results.csv",
        [
            {"case": case, "passes": passes}
            for case, passes in summary["case_results"].items()
        ],
    )
    write_csv(out_dir / "directionality.csv", directionality_rows(summary))
    write_csv(out_dir / "presentations.csv", presentation_rows(summary))
    write_csv(out_dir / "process_profiles.csv", process_rows(summary))
    write_csv(out_dir / "omega_fibers.csv", omega_fiber_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    directionality = result["directionality"]
    support = result["support_blindness"]
    presentations = result["presentations"]
    processes = result["processes"]
    omega = result["omega"]
    lines = [
        "# Alpha-Omega Foundation v0 Validation Report",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        f"Finite path horizon: {result['horizon']}",
        "",
        "## Case Results",
        "",
    ]
    lines.extend(
        f"- {case}: {passes}" for case, passes in result["case_results"].items()
    )
    lines.extend(
        [
            "",
            "## Oriented Path Laws",
            "",
            (
                "- Null reversible total variation / KL: "
                f"{directionality['null']['total_variation']} / "
                f"{directionality['null']['kl_forward_to_reversed']}"
            ),
            (
                "- Biased reciprocal-support total variation / KL: "
                f"{directionality['biased_reciprocal']['total_variation']} / "
                f"{directionality['biased_reciprocal']['kl_forward_to_reversed']}"
            ),
            (
                "- Residual law probability / endpoint respected: "
                f"{directionality['residual_continuation']['total_probability']} / "
                f"{directionality['residual_continuation']['all_paths_start_at_prefix_end']}"
            ),
            (
                "- Probabilistic return at horizon 2: "
                f"{directionality['probabilistic_nonreturn']['return_probability_at_horizon_2']}"
            ),
            (
                "- Policy collapse forecloses live support: "
                f"{directionality['policy_contraction']['collapse_forecloses_live_support']}"
            ),
            "",
            "## Support Blindness",
            "",
            f"- Action-labelled support equal: {support['support_equivalent']}",
            (
                "- Exhaustive support observables equal: "
                f"{support['all_support_observables_equal']}"
            ),
            f"- Weighted path directionality separates: {support['directionality_separates']}",
            "",
            "## Presentation Contracts",
            "",
            (
                "- Exact relabeling is an isomorphism: "
                f"{presentations['exact_relabeling']['isomorphism']}"
            ),
            (
                "- Duplicate quotient is functionally bisimilar: "
                f"{presentations['bisimilar_duplicate']['functional_bisimulation']}"
            ),
            (
                "- Forward/back/atom negative controls fire: "
                f"{presentations['forward_failure']['forward_failure_count']}/"
                f"{presentations['back_failure']['back_failure_count']}/"
                f"{presentations['atom_failure']['atom_failure_count']}"
            ),
            (
                "- Support bisimulation hides weighted grain: "
                f"{presentations['weighted_grain_hidden']['weighted_directionality_changes']}"
            ),
            "",
            "## Candidate Process Profiles",
            "",
            (
                "- Passive causal deformer: "
                f"{processes['passive']['causal_deformer']}"
            ),
            (
                "- Memoryless controller causal/endogenous: "
                f"{processes['effectful_memoryless']['causal_deformer']}/"
                f"{processes['effectful_memoryless']['endogenous_record_selector']}"
            ),
            (
                "- Record selector causal/endogenous/persistent: "
                f"{processes['record_sensitive']['causal_deformer']}/"
                f"{processes['record_sensitive']['endogenous_record_selector']}/"
                f"{processes['record_sensitive']['persistent_closed_loop']}"
            ),
            (
                "- Injected label changes features: "
                f"{processes['injected_label_changes_features']}"
            ),
            "",
            "## Decorated May-Omega",
            "",
            f"- Source witness: {omega['assignment_id']}",
            f"- Singleton fibers all nonempty: {omega['all_singletons_nonempty']}",
            f"- Pair fibers all nonempty: {omega['all_pairs_nonempty']}",
            f"- Triple fiber empty: {omega['triple_empty']}",
            f"- Maximal face count: {omega['maximal_face_count']}",
            f"- Greatest face exists: {omega['greatest_face_exists']}",
            (
                "- Downward-closure/restriction failures: "
                f"{len(omega['downward_closure_failures'])}/"
                f"{len(omega['restriction_failures'])}"
            ),
            (
                "- Duplicate quotient preserves structural payload: "
                f"{omega['duplicate_structural_payload_equal']}"
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
            (
                "This retained finite foundation derives path-law, support, "
                "presentation, process-profile, and realization-fiber objects. "
                "It does not establish value, standing, personhood, "
                "consciousness, moral agency, thermodynamic universality, a "
                "preferred physical orientation, normative allegiance, "
                "lushness as an imperative, or Omega as a realized moral object."
            ),
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
