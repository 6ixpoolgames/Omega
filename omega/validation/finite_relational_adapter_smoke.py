"""Cross-platform finite relational adapter smoke runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.cli import run_model_file
from omega.adapters.finite_relational.graph_cli import run_graph_file
from omega.adapters.finite_relational.grid_cli import run_grid_file
from omega.validation._common import assert_equal, read_json, resolve_repo_path, run_pytest, timestamped_run_root


IR_FIXTURES: tuple[dict[str, object], ...] = (
    {"id": "sound_pass", "path": "sound_pass.json", "audit_count": 3},
    {"id": "phantom_reachability_fail", "path": "phantom_reachability_fail.json", "audit_count": 1},
    {"id": "hidden_reachability_loss_fail", "path": "hidden_reachability_loss_fail.json", "audit_count": 1},
    {"id": "proxy_nonfactorization_fail", "path": "proxy_nonfactorization_fail.json", "audit_count": 1},
    {
        "id": "simple_form_nonfactorization_fail",
        "path": "simple_form_nonfactorization_fail.json",
        "audit_count": 1,
    },
    {
        "id": "entropy_controlled_nonfactorization_fail",
        "path": "entropy_controlled_nonfactorization_fail.json",
        "audit_count": 1,
    },
    {
        "id": "ordered_trace_nonfactorization_fail",
        "path": "ordered_trace_nonfactorization_fail.json",
        "audit_count": 1,
    },
    {"id": "bounded_recovery_pass", "path": "bounded_recovery_pass.json", "audit_count": 1},
    {
        "id": "bounded_recovery_entropy_fail",
        "path": "bounded_recovery_entropy_fail.json",
        "audit_count": 1,
    },
    {"id": "carrier_transfer_pass", "path": "carrier_transfer_pass.json", "audit_count": 1},
    {
        "id": "carrier_transfer_fail_missing_return",
        "path": "carrier_transfer_fail_missing_return.json",
        "audit_count": 1,
    },
)

DERIVED_GRAPH_FIXTURES: tuple[dict[str, object], ...] = (
    {
        "id": "derived_graph_strict_asymmetry",
        "path": "derived_graph_strict_asymmetry.json",
        "audit_count": 3,
    },
    {
        "id": "derived_graph_recurrent_carrier",
        "path": "derived_graph_recurrent_carrier.json",
        "audit_count": 3,
    },
    {
        "id": "derived_graph_mixed_asymmetry",
        "path": "derived_graph_mixed_asymmetry.json",
        "audit_count": 3,
    },
)

GRID_FIXTURES: tuple[dict[str, object], ...] = (
    {
        "id": "finite_grid_east_asymmetry",
        "path": "finite_grid_east_asymmetry.json",
        "audit_count": 3,
    },
)

ADAPTER_TESTS = [
    "tests/test_finite_relational_adapter.py",
    "tests/test_derived_graph_adapter.py",
    "tests/test_finite_grid_adapter.py",
    "tests/test_finite_relational_adapter_smoke.py",
    "tests/test_finite_relational_adapter_adversarial.py",
    "tests/test_finite_relational_adapter_empirical.py",
    "tests/test_finite_relational_deterministic_layer.py",
    "tests/test_finite_relational_grid_obstacle.py",
    "tests/test_finite_relational_stochastic_recovery.py",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the finite relational adapter smoke.")
    parser.add_argument("--out-root", type=Path, default=Path(".tmp/finite_relational_adapter_smoke"))
    parser.add_argument("--skip-pytest", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_finite_relational_adapter_smoke(
        out_root=args.out_root,
        skip_pytest=args.skip_pytest,
    )
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_finite_relational_adapter_smoke(
    *,
    out_root: Path = Path(".tmp/finite_relational_adapter_smoke"),
    skip_pytest: bool = False,
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    fixture_root = resolve_repo_path(Path("omega/adapters/finite_relational/fixtures"))
    ir_root = run_root / "ir_fixtures"
    derived_root = run_root / "derived_graph_fixtures"
    ir_results = [_run_ir_fixture(spec, fixture_root, ir_root) for spec in IR_FIXTURES]
    derived_results = [
        _run_derived_fixture(spec, fixture_root, derived_root) for spec in DERIVED_GRAPH_FIXTURES
    ]
    grid_root = run_root / "finite_grid_fixtures"
    grid_results = [_run_grid_fixture(spec, fixture_root, grid_root) for spec in GRID_FIXTURES]

    if not skip_pytest:
        run_pytest(ADAPTER_TESTS, run_root=run_root)

    fixture_count = len(ir_results) + len(derived_results) + len(grid_results)
    return {
        "status": "PASS",
        "run_root": str(run_root),
        "fixture_count": fixture_count,
        "ir_fixture_count": len(ir_results),
        "derived_graph_fixture_count": len(derived_results),
        "finite_grid_fixture_count": len(grid_results),
        "focused_pytest": "skipped" if skip_pytest else "passed",
        "ir_fixtures": ir_results,
        "derived_graph_fixtures": derived_results,
        "finite_grid_fixtures": grid_results,
    }


def _run_ir_fixture(
    spec: dict[str, object],
    fixture_root: Path,
    out_root: Path,
) -> dict[str, object]:
    fixture_id = str(spec["id"])
    out_dir = out_root / fixture_id
    summary = run_model_file(fixture_root / str(spec["path"]), out_dir)
    _assert_common_summary(fixture_id, summary, expected_audit_count=int(spec["audit_count"]))
    _require_files(
        out_dir,
        [
            "model_digest.txt",
            "provenance_check.json",
            "audit_results.json",
            "summary.json",
        ],
    )
    provenance = read_json(out_dir / "provenance_check.json")
    assert_equal(f"{fixture_id}.provenance_complete", provenance["complete"], True)
    return {
        "id": fixture_id,
        "model_id": summary["model_id"],
        "audit_count": summary["audit_count"],
        "all_passed": summary["all_passed"],
        "output": str(out_dir),
    }


def _run_derived_fixture(
    spec: dict[str, object],
    fixture_root: Path,
    out_root: Path,
) -> dict[str, object]:
    fixture_id = str(spec["id"])
    out_dir = out_root / fixture_id
    summary = run_graph_file(fixture_root / str(spec["path"]), out_dir)
    _assert_common_summary(fixture_id, summary, expected_audit_count=int(spec["audit_count"]))
    _require_files(
        out_dir,
        [
            "source.json",
            "compiled_model.json",
            "source_digest.txt",
            "compiled_model_digest.txt",
            "provenance_check.json",
            "audit_results.json",
            "summary.json",
        ],
    )
    provenance = read_json(out_dir / "provenance_check.json")
    compiled = read_json(out_dir / "compiled_model.json")
    source = read_json(out_dir / "source.json")
    assert_equal(f"{fixture_id}.provenance_complete", provenance["complete"], True)
    if "derivation_rules" not in compiled.get("provenance", {}):
        raise AssertionError(f"{fixture_id} compiled model is missing derivation_rules")
    reserved = {"predicates", "relations", "functions", "profiles", "audits"}
    leaked = sorted(reserved & set(source))
    if leaked:
        raise AssertionError(f"{fixture_id} source contains reserved IR fields: {leaked}")
    return {
        "id": fixture_id,
        "compiled_model_id": summary["compiled_model_id"],
        "audit_count": summary["audit_count"],
        "all_passed": summary["all_passed"],
        "output": str(out_dir),
    }


def _run_grid_fixture(
    spec: dict[str, object],
    fixture_root: Path,
    out_root: Path,
) -> dict[str, object]:
    fixture_id = str(spec["id"])
    out_dir = out_root / fixture_id
    summary = run_grid_file(fixture_root / str(spec["path"]), out_dir)
    _assert_common_summary(fixture_id, summary, expected_audit_count=int(spec["audit_count"]))
    _require_files(
        out_dir,
        [
            "source.json",
            "compiled_model.json",
            "source_digest.txt",
            "compiled_model_digest.txt",
            "provenance_check.json",
            "audit_results.json",
            "summary.json",
        ],
    )
    provenance = read_json(out_dir / "provenance_check.json")
    compiled = read_json(out_dir / "compiled_model.json")
    source = read_json(out_dir / "source.json")
    assert_equal(f"{fixture_id}.provenance_complete", provenance["complete"], True)
    if compiled.get("provenance", {}).get("compiled_from") != "finite_grid":
        raise AssertionError(f"{fixture_id} compiled model was not marked finite_grid")
    reserved = {"predicates", "relations", "functions", "profiles", "audits"}
    leaked = sorted(reserved & set(source))
    if leaked:
        raise AssertionError(f"{fixture_id} source contains reserved IR fields: {leaked}")
    return {
        "id": fixture_id,
        "compiled_model_id": summary["compiled_model_id"],
        "audit_count": summary["audit_count"],
        "all_passed": summary["all_passed"],
        "output": str(out_dir),
    }


def _assert_common_summary(
    fixture_id: str,
    summary: dict[str, object],
    *,
    expected_audit_count: int,
) -> None:
    assert_equal(f"{fixture_id}.all_passed", summary["all_passed"], True)
    assert_equal(f"{fixture_id}.provenance_complete", summary["provenance_complete"], True)
    assert_equal(f"{fixture_id}.audit_count", summary["audit_count"], expected_audit_count)
    assert_equal(f"{fixture_id}.passed_count", summary["passed_count"], expected_audit_count)


def _require_files(out_dir: Path, names: list[str]) -> None:
    missing = [name for name in names if not (out_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"{out_dir} is missing retained files: {missing}")


if __name__ == "__main__":
    main()
