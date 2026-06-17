"""Controlled finite relational adapter empirical pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.controlled_experiment import (
    ControlledExperimentCase,
    generate_controlled_experiment,
)
from omega.adapters.finite_relational.model import load_model, model_digest
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the controlled finite relational adapter empirical pilot."
    )
    parser.add_argument("--out-root", type=Path, default=Path(".tmp/finite_relational_adapter_empirical"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_adapter_empirical(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_adapter_empirical(
    *,
    out_root: Path = Path(".tmp/finite_relational_adapter_empirical"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    families = generate_controlled_experiment()
    family_summaries = []
    for family in families:
        family_dir = run_root / family.family_id
        family_dir.mkdir(parents=True, exist_ok=True)
        representative_summaries = [
            _retain_case(case, family_dir / case.case_id)
            for case in family.representative_cases
        ]
        summary = family.summary() | {
            "output": str(family_dir),
            "representative_cases": representative_summaries,
        }
        _write_json(family_dir / "family_summary.json", summary)
        family_summaries.append(summary)

    result = {
        "status": "PASS",
        "run_root": str(run_root),
        "family_count": len(families),
        "representative_case_count": sum(
            len(family.representative_cases) for family in families
        ),
        "all_passed": all(summary["all_passed"] for summary in family_summaries),
        "families": family_summaries,
    }
    _write_json(run_root / "summary.json", result)
    return result


def _retain_case(case: ControlledExperimentCase, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = case.summary() | {"output": str(out_dir)}
    loaded = load_model(case.model)
    _write_json(out_dir / "model.json", case.model)
    (out_dir / "model_digest.txt").write_text(f"{model_digest(loaded)}\n", encoding="utf-8")
    _write_json(out_dir / "audit_results.json", [result.as_dict() for result in case.audit_results])
    _write_json(out_dir / "summary.json", summary)
    return summary


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
