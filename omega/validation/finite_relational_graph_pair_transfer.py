"""Controlled graph-pair transfer characterization validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.graph_pair_transfer import (
    GraphPairTransferCase,
    digest_json,
    generate_graph_pair_transfer_characterization,
)
from omega.adapters.finite_relational.model import load_model, model_digest
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the controlled graph-pair transfer characterization."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/finite_relational_graph_pair_transfer"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_graph_pair_transfer(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_graph_pair_transfer(
    *,
    out_root: Path = Path(".tmp/finite_relational_graph_pair_transfer"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    studies = generate_graph_pair_transfer_characterization()
    study_summaries = []
    for study in studies:
        study_dir = run_root / study.study_id
        study_dir.mkdir(parents=True, exist_ok=True)
        representative_summaries = [
            _retain_case(case, study_dir / case.case_id)
            for case in study.representative_cases
        ]
        study_summary = study.summary() | {
            "output": str(study_dir),
            "representative_cases": representative_summaries,
        }
        _write_json(study_dir / "study_summary.json", study_summary)
        study_summaries.append(study_summary)

    result = {
        "status": "PASS",
        "run_root": str(run_root),
        "study_count": len(studies),
        "representative_case_count": sum(
            len(study.representative_cases) for study in studies
        ),
        "all_passed": all(study.all_passed for study in studies),
        "studies": study_summaries,
    }
    _write_json(run_root / "summary.json", result)
    return result


def _retain_case(case: GraphPairTransferCase, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = case.summary() | {"output": str(out_dir)}
    compiled_model = load_model(case.compiled_model)

    _write_json(out_dir / "source.json", case.source)
    _write_json(out_dir / "compiled_model.json", case.compiled_model)
    (out_dir / "source_digest.txt").write_text(
        f"{digest_json(case.source)}\n",
        encoding="utf-8",
    )
    (out_dir / "compiled_model_digest.txt").write_text(
        f"{model_digest(compiled_model)}\n",
        encoding="utf-8",
    )
    _write_json(
        out_dir / "audit_results.json",
        [result.as_dict() for result in case.audit_results],
    )
    _write_json(out_dir / "summary.json", summary)
    return summary


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
