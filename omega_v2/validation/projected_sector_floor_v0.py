"""Retained validation runner for the Omega v2 projected-sector floor."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega_v2.experiments.projected_sector_floor_v0 import (
    commuting_diamond_rows,
    fixture_rows,
    history_comparison_rows,
    projected_component_rows,
    projected_sector_floor_summary,
    projection_profile_rows,
    sector_profile_rows,
    summary_digest,
)
from omega_v2.validation.artifacts import (
    timestamped_output_dir,
    write_csv,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the finite exact projected-sector floor v0."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/projected_sector_floor_v0"),
    )
    return parser.parse_args()


def run_projected_sector_floor_v0(
    *,
    out_root: Path = Path(".tmp/projected_sector_floor_v0"),
) -> dict[str, Any]:
    return retain_projected_sector_floor_v0(
        timestamped_output_dir(out_root)
    )


def retain_projected_sector_floor_v0(
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    complete = projected_sector_floor_summary()
    public = {
        key: value for key, value in complete.items() if key != "_objects"
    }
    result = {
        "run_root": str(out_dir),
        "summary_digest": summary_digest(complete),
        **public,
    }

    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "fixtures.csv", fixture_rows(complete))
    write_csv(
        out_dir / "sector_profiles.csv",
        sector_profile_rows(complete),
    )
    write_csv(
        out_dir / "projection_profiles.csv",
        projection_profile_rows(complete),
    )
    write_csv(
        out_dir / "projected_components.csv",
        projected_component_rows(complete),
    )
    write_csv(
        out_dir / "history_comparisons.csv",
        history_comparison_rows(complete),
    )
    write_csv(
        out_dir / "commuting_diamonds.csv",
        commuting_diamond_rows(complete),
    )
    (out_dir / "report.md").write_text(
        render_report(result),
        encoding="utf-8",
    )
    return result


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# Omega v2 Projected-Sector Floor v0 Validation",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        f"Protocol commit: `{result['protocol_commit']}`",
        f"Summary digest: `{result['summary_digest']}`",
        "",
        "## Exact Scope",
        "",
        f"- Preregistered fixtures: {result['fixture_count']}",
        (
            "- Bounded extendability horizon: "
            f"{result['extendability_horizon']}"
        ),
        (
            "- Formal fragment: "
            "`formal/lean/OmegaV2/Finite/ProjectedOrder.lean`"
        ),
        "",
        "## Retained Separations",
        "",
        (
            "- A terminating, branching disintegration law can remain "
            "locally and globally confluent."
        ),
        (
            "- A terminating branch can fail both local and global "
            "confluence."
        ),
        (
            "- A recurrent nonbranching sector differs from both "
            "terminating controls."
        ),
        (
            "- Two exact-distinct histories can be related by an "
            "independent commuting diamond and share one projected history."
        ),
        (
            "- A projection can be null, one-sided, or bidirectional; "
            "bidirectionality does not select a preferred polarity."
        ),
        "",
        "## Case Results",
        "",
    ]
    lines.extend(
        f"- {case}: {passed}"
        for case, passed in result["case_results"].items()
    )
    lines.extend(["", "## Kill Conditions", ""])
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
            "## Public Compression",
            "",
            result["public_compression"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    result = run_projected_sector_floor_v0(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
