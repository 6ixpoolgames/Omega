"""Retained validation for CompensationClaim / NOLP v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.compensation_claim import (
    compensation_claim_summary,
    compensation_verdict_rows,
)
from omega.future_field_atlas.util import write_csv, write_json
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CompensationClaim / NOLP v0 finite audit.")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_compensation_claim_v0"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_compensation_claim(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_compensation_claim(
    *,
    out_root: Path = Path(".tmp/finite_relational_compensation_claim_v0"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return retain_finite_relational_compensation_claim(run_root)


def retain_finite_relational_compensation_claim(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = compensation_claim_summary()
    result = {
        "status": "PASS" if summary["verdict"] == "retained" else "REVIEW",
        "run_root": str(out_dir),
        **summary,
    }
    write_json(out_dir / "summary.json", result)
    write_csv(out_dir / "compensation_verdicts.csv", compensation_verdict_rows(summary))
    (out_dir / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(result: dict[str, Any]) -> str:
    certified = result["certified_same_frame_cover"]["verdict"]
    uncertified = result["uncertified_cover"]["verdict"]
    incomplete = result["incomplete_cover"]["verdict"]
    phantom = result["phantom_compensation"]
    lines = [
        "# CompensationClaim / NOLP v0 Report",
        "",
        f"Status: {result['status']}",
        f"Verdict: {result['verdict']}",
        f"Protocol: `{result['protocol_doc']}`",
        "",
        "## Cases",
        "",
        f"- Certified same-frame cover defeats NOLP refusal: {not certified['nolp_refuses_contraction']}",
        f"- Uncertified cover is refused: {uncertified['nolp_refuses_contraction']}",
        f"- Incomplete cover is refused: {incomplete['nolp_refuses_contraction']}",
        f"- Phantom compensation diverges: {phantom['phantom_compensation_diverges']}",
        f"- Kill conditions pass: {result['kill_conditions_pass']}",
        "",
        "## Stability Labels",
        "",
        f"- Certified cover: {certified['stability_label']}",
        f"- Uncertified cover: {uncertified['stability_label']}",
        f"- Incomplete cover: {incomplete['stability_label']}",
        "",
        "## NOLP v0 Reading",
        "",
        result["nolp_v0_read"],
        "",
        "## Claim Boundary",
        "",
        "This is a same-frame finite compensation harness. It does not prove value, "
        "standing, aggregation, population ethics, patienthood, cross-valuer "
        "compensation, the correct compensation order, or Omega validation.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
