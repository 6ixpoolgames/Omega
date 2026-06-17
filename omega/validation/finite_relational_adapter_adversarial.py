"""Generated/adversarial finite relational adapter validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.adversarial_search import (
    GeneratedAdapterCase,
    digest_json,
    generate_adversarial_cases,
)
from omega.adapters.finite_relational.model import load_model, model_digest
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run generated finite relational adapter hardening cases."
    )
    parser.add_argument("--out-root", type=Path, default=Path(".tmp/finite_relational_adapter_adversarial"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_adapter_adversarial(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_adapter_adversarial(
    *,
    out_root: Path = Path(".tmp/finite_relational_adapter_adversarial"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    cases = generate_adversarial_cases()
    case_summaries = [_retain_case(case, run_root / case.case_id) for case in cases]
    return {
        "status": "PASS",
        "run_root": str(run_root),
        "case_count": len(cases),
        "all_passed": all(summary["all_passed"] for summary in case_summaries),
        "cases": case_summaries,
    }


def _retain_case(case: GeneratedAdapterCase, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = case.summary() | {"output": str(out_dir)}
    audit_results = [result.as_dict() for result in case.audit_results]
    compiled_model = load_model(case.compiled_model)

    _write_json(out_dir / "source.json", case.source)
    _write_json(out_dir / "compiled_model.json", case.compiled_model)
    (out_dir / "source_digest.txt").write_text(f"{digest_json(case.source)}\n", encoding="utf-8")
    (out_dir / "compiled_model_digest.txt").write_text(
        f"{model_digest(compiled_model)}\n",
        encoding="utf-8",
    )
    _write_json(out_dir / "audit_results.json", audit_results)
    _write_json(out_dir / "summary.json", summary)
    return summary


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
