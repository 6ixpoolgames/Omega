"""Retained validation runner for controlled Markov abstraction v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega_v2.experiments.controlled_markov_abstraction_v0 import (
    continuation_rows,
    controlled_markov_abstraction_summary,
    directionality_rows,
    lumpability_rows,
    path_transport_rows,
)
from omega_v2.validation.artifacts import (
    timestamped_output_dir,
    write_csv,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run finite controlled Markov abstraction v0 validation."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/controlled_markov_abstraction_v0"),
    )
    parser.add_argument("--horizon", type=int, default=3)
    return parser.parse_args()


def run_controlled_markov_abstraction_v0(
    *,
    out_root: Path = Path(".tmp/controlled_markov_abstraction_v0"),
    horizon: int = 3,
) -> dict[str, Any]:
    return retain_controlled_markov_abstraction_v0(
        timestamped_output_dir(out_root),
        horizon=horizon,
    )


def retain_controlled_markov_abstraction_v0(
    out_dir: Path,
    *,
    horizon: int = 3,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = controlled_markov_abstraction_summary(horizon=horizon)
    result = {"run_root": str(out_dir), **summary}
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "lumpability.csv", lumpability_rows(summary))
    write_csv(out_dir / "path_transport.csv", path_transport_rows(summary))
    write_csv(out_dir / "directionality_loss.csv", directionality_rows(summary))
    write_csv(out_dir / "continuation_events.csv", continuation_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    exact = result["exact_nontrivial"]
    rejected = result["non_lumpable"]
    loss = result["directionality_loss"]
    sufficient = result["sufficient_hidden_coordinate"]
    lines = [
        "# Finite Controlled Markov Abstraction v0 Validation",
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
        f"- {case}: {passed}" for case, passed in result["case_results"].items()
    )
    lines.extend(
        [
            "",
            "## Exact Nontrivial Quotient",
            "",
            (
                "- Action-aware strong lumpability: "
                f"{exact['lumpability']['strongly_lumpable']}"
            ),
            f"- Support bisimulation: {exact['support']['bisimilar']}",
            f"- Full path-law pushforward: {exact['path_transport']['commutes']}",
            (
                "- Bounded target-hit transport: "
                f"{exact['continuation']['agrees']}"
            ),
            (
                "- Path-event mass, pushed concrete / quotient: "
                f"{exact['path_event_probability_concrete_pushforward']} / "
                f"{exact['path_event_probability_quotient']}"
            ),
            "",
            "## Rejected Aggregation",
            "",
            (
                "- Action-aware strong lumpability: "
                f"{rejected['lumpability']['strongly_lumpable']}"
            ),
            f"- Exact witness count: {rejected['lumpability']['witness_count']}",
            (
                "- Maximum representative TV discrepancy: "
                f"{rejected['lumpability']['maximum_total_variation_discrepancy']}"
            ),
            f"- Quotient construction refused: {rejected['quotient_refused']}",
            "",
            "## Weighted Directionality Loss",
            "",
            f"- Support bisimulation: {loss['support']['bisimilar']}",
            f"- Strong lumpability: {loss['lumpability']['strongly_lumpable']}",
            f"- Full path-law pushforward: {loss['path_transport']['commutes']}",
            (
                "- Concrete / aggregate total variation: "
                f"{loss['concrete_comparison']['total_variation']} / "
                f"{loss['abstract_comparison']['total_variation']}"
            ),
            (
                "- Likelihood-ratio sufficiency: "
                f"{loss['likelihood_ratio_sufficiency']['sufficient']}"
            ),
            f"- Data processing holds: {loss['data_processing_holds']}",
            "",
            "## Sufficient Hidden-Coordinate Quotient",
            "",
            (
                "- Strong lumpability / full path-law pushforward: "
                f"{sufficient['lumpability']['strongly_lumpable']} / "
                f"{sufficient['path_transport']['commutes']}"
            ),
            (
                "- Concrete / aggregate total variation: "
                f"{sufficient['concrete_comparison']['total_variation']} / "
                f"{sufficient['abstract_comparison']['total_variation']}"
            ),
            (
                "- Likelihood-ratio sufficiency: "
                f"{sufficient['likelihood_ratio_sufficiency']['sufficient']}"
            ),
            f"- Data processing holds: {sufficient['data_processing_holds']}",
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
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    result = run_controlled_markov_abstraction_v0(
        out_root=args.out_root,
        horizon=args.horizon,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
