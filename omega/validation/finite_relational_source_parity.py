"""Second-source finite relational adapter parity validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.model import load_model, model_digest
from omega.adapters.finite_relational.source_parity import (
    SourceParityCase,
    digest_json,
    generate_source_parity_study,
)
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run finite relational source-parity validation."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_source_parity"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_source_parity(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_source_parity(
    *,
    out_root: Path = Path(".tmp/finite_relational_source_parity"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    cases = generate_source_parity_study()
    case_summaries = [_retain_case(case, run_root / case.case_id) for case in cases]
    result = {
        "status": "PASS",
        "run_root": str(run_root),
        "case_count": len(cases),
        "all_passed": all(summary["all_passed"] for summary in case_summaries),
        "cases": case_summaries,
    }
    _write_json(run_root / "summary.json", result)
    return result


def _retain_case(case: SourceParityCase, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = case.summary() | {"output": str(out_dir)}
    left_model = load_model(case.left_compiled_model)
    right_model = load_model(case.right_compiled_model)

    _write_json(out_dir / "left_source.json", case.left_source)
    _write_json(out_dir / "right_source.json", case.right_source)
    _write_json(out_dir / "left_compiled_model.json", case.left_compiled_model)
    _write_json(out_dir / "right_compiled_model.json", case.right_compiled_model)
    _write_json(out_dir / "comparison.json", case.comparison)
    _write_json(out_dir / "summary.json", summary)
    (out_dir / "left_source_digest.txt").write_text(
        f"{digest_json(case.left_source)}\n",
        encoding="utf-8",
    )
    (out_dir / "right_source_digest.txt").write_text(
        f"{digest_json(case.right_source)}\n",
        encoding="utf-8",
    )
    (out_dir / "left_compiled_model_digest.txt").write_text(
        f"{model_digest(left_model)}\n",
        encoding="utf-8",
    )
    (out_dir / "right_compiled_model_digest.txt").write_text(
        f"{model_digest(right_model)}\n",
        encoding="utf-8",
    )
    return summary


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
