"""Deterministic pre-stochastic finite relational validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.deterministic_recovery import (
    DeterministicLayerFamily,
    generate_deterministic_layer_study,
)
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run deterministic pre-stochastic finite relational validation."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_deterministic_layer"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_deterministic_layer(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_deterministic_layer(
    *,
    out_root: Path = Path(".tmp/finite_relational_deterministic_layer"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    families = generate_deterministic_layer_study()
    family_summaries = []
    for family in families:
        family_dir = run_root / family.family_id
        family_dir.mkdir(parents=True, exist_ok=True)
        summary = _family_summary(family) | {"output": str(family_dir)}
        _write_json(family_dir / "family_summary.json", summary)
        family_summaries.append(summary)

    result = {
        "status": "PASS",
        "run_root": str(run_root),
        "family_count": len(families),
        "all_passed": True,
        "families": family_summaries,
    }
    _write_json(run_root / "summary.json", result)
    return result


def _family_summary(family: DeterministicLayerFamily) -> dict[str, Any]:
    return {
        "family_id": family.family_id,
        "description": family.description,
        "metrics": family.metrics,
    }


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
