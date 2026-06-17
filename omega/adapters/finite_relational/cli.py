"""CLI for the finite relational adapter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from omega.adapters.finite_relational.audits import run_declared_audits
from omega.adapters.finite_relational.model import load_model_path, model_digest, validate_provenance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run finite relational adapter audits.")
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_model_file(args.model, args.out)
    print(json.dumps(summary, indent=2, sort_keys=True))


def run_model_file(model_path: Path, out_dir: Path) -> dict[str, object]:
    model = load_model_path(model_path)
    provenance = validate_provenance(model)
    audit_results = [result.as_dict() for result in run_declared_audits(model)]
    digest = model_digest(model)
    summary = {
        "model_id": model.model_id,
        "model_path": str(model_path),
        "model_digest": digest,
        "provenance_complete": provenance["complete"],
        "audit_count": len(audit_results),
        "passed_count": sum(1 for result in audit_results if result["passed"]),
        "all_passed": all(result["passed"] for result in audit_results),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "model_digest.txt").write_text(f"{digest}\n", encoding="utf-8")
    _write_json(out_dir / "provenance_check.json", provenance)
    _write_json(out_dir / "audit_results.json", audit_results)
    _write_json(out_dir / "summary.json", summary)
    return summary


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
