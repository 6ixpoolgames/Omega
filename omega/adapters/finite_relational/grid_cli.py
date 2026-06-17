"""CLI for compiling and auditing finite grid adapter sources."""

from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path

from omega.adapters.finite_relational.audits import run_declared_audits
from omega.adapters.finite_relational.finite_grid import compile_finite_grid_path, load_finite_grid_path
from omega.adapters.finite_relational.model import load_model, model_digest, validate_provenance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile and audit a finite grid adapter source.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_grid_file(args.source, args.out)
    print(json.dumps(summary, indent=2, sort_keys=True))


def run_grid_file(source_path: Path, out_dir: Path) -> dict[str, object]:
    source = load_finite_grid_path(source_path)
    compiled = compile_finite_grid_path(source_path)
    model = load_model(compiled)
    provenance = validate_provenance(model)
    audit_results = [result.as_dict() for result in run_declared_audits(model)]
    digest = model_digest(model)
    source_digest = _digest_json(source)
    summary = {
        "source_model_id": str(source.get("model_id", "finite_grid")),
        "compiled_model_id": model.model_id,
        "source_path": str(source_path),
        "source_digest": source_digest,
        "compiled_model_digest": digest,
        "provenance_complete": provenance["complete"],
        "audit_count": len(audit_results),
        "passed_count": sum(1 for result in audit_results if result["passed"]),
        "all_passed": all(result["passed"] for result in audit_results),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(out_dir / "source.json", source)
    _write_json(out_dir / "compiled_model.json", compiled)
    (out_dir / "source_digest.txt").write_text(f"{source_digest}\n", encoding="utf-8")
    (out_dir / "compiled_model_digest.txt").write_text(f"{digest}\n", encoding="utf-8")
    _write_json(out_dir / "provenance_check.json", provenance)
    _write_json(out_dir / "audit_results.json", audit_results)
    _write_json(out_dir / "summary.json", summary)
    return summary


def _digest_json(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
