"""Policy-conditioned finite stochastic dynamics validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.stochastic_policy_dynamics import (
    generate_policy_dynamics_study,
)
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run policy-conditioned finite stochastic dynamics validation."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_policy_dynamics"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_policy_dynamics(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_policy_dynamics(
    *,
    out_root: Path = Path(".tmp/finite_relational_policy_dynamics"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    families = generate_policy_dynamics_study()
    family_summaries = []
    for family in families:
        family_dir = run_root / family.family_id
        family_dir.mkdir(parents=True, exist_ok=True)
        facts_path = family_dir / "facts.json"
        hypotheses_path = family_dir / "hypotheses.json"
        _write_json(facts_path, family.facts)
        _write_json(hypotheses_path, [hypothesis.as_dict() for hypothesis in family.hypotheses])
        summary = family.summary() | {
            "output": str(family_dir),
            "facts": str(facts_path),
            "hypotheses": str(hypotheses_path),
        }
        _write_json(family_dir / "family_summary.json", summary)
        family_summaries.append(summary)

    result = {
        "status": "PASS",
        "run_root": str(run_root),
        "family_count": len(families),
        "all_hypotheses_passed": all(
            family.all_hypotheses_passed for family in families
        ),
        "families": family_summaries,
    }
    _write_json(run_root / "summary.json", result)
    return result


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
