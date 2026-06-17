from pathlib import Path

import pytest

from omega.adapters.finite_relational import (
    compile_derived_graph_path,
    load_model,
    run_declared_audits,
)
from omega.adapters.finite_relational.finite_grid import compile_finite_grid, compile_finite_grid_path
from omega.adapters.finite_relational.grid_cli import run_grid_file
from omega.adapters.finite_relational.model import SchemaError


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "omega" / "adapters" / "finite_relational" / "fixtures"


def test_finite_grid_compiles_through_relational_ir_and_generic_audits() -> None:
    compiled = compile_finite_grid_path(FIXTURES / "finite_grid_east_asymmetry.json")
    model = load_model(compiled)
    results = {result.audit_id: result.as_dict() for result in run_declared_audits(model)}

    assert compiled["provenance"]["compiled_from"] == "finite_grid"
    assert compiled["provenance"]["intermediate_compiler"] == "derived_graph"
    assert model.domain("state") == ("0,0", "1,0")
    assert model.relation_tuples("next") == frozenset({("0,0", "1,0")})
    assert model.relation_tuples("primitive_asym") == frozenset({("color", "0,0", "1,0")})
    assert results["derived_alpha_laws"]["passed"] is True
    assert results["presentation_identity"]["finding"] == "sound"
    assert results["presentation_constant"]["finding"] == "not_sound"
    assert results["presentation_constant"]["passed"] is True


def test_finite_grid_and_derived_graph_compile_equivalent_ir_facts() -> None:
    graph = load_model(compile_derived_graph_path(FIXTURES / "derived_graph_strict_asymmetry.json"))
    grid = load_model(compile_finite_grid_path(FIXTURES / "finite_grid_east_asymmetry.json"))
    state_map = {"source": "0,0", "sink": "1,0"}

    assert _rename_relation(graph.relation_tuples("next"), state_map) == grid.relation_tuples("next")
    assert _rename_relation(graph.relation_tuples("primitive_rel"), state_map) == grid.relation_tuples(
        "primitive_rel"
    )
    assert _rename_relation(graph.relation_tuples("primitive_sep"), state_map) == grid.relation_tuples(
        "primitive_sep"
    )
    assert _rename_relation(graph.relation_tuples("primitive_asym"), state_map) == grid.relation_tuples(
        "primitive_asym"
    )
    assert _rename_relation(graph.relation_tuples("merge_separated"), state_map) == grid.relation_tuples(
        "merge_separated"
    )

    graph_results = {result.audit_id: result.finding for result in run_declared_audits(graph)}
    grid_results = {result.audit_id: result.finding for result in run_declared_audits(grid)}
    assert graph_results == grid_results


def test_finite_grid_cli_retains_source_compiled_model_and_audits(tmp_path: Path) -> None:
    out_dir = tmp_path / "finite_grid_smoke"
    summary = run_grid_file(FIXTURES / "finite_grid_east_asymmetry.json", out_dir)

    assert summary["all_passed"] is True
    assert summary["audit_count"] == 3
    assert (out_dir / "source.json").exists()
    assert (out_dir / "compiled_model.json").exists()
    assert (out_dir / "source_digest.txt").exists()
    assert (out_dir / "compiled_model_digest.txt").exists()
    assert (out_dir / "provenance_check.json").exists()
    assert (out_dir / "audit_results.json").exists()
    assert (out_dir / "summary.json").exists()


def test_finite_grid_rejects_reserved_ir_fields() -> None:
    with pytest.raises(SchemaError, match="must not declare finite relational IR fields"):
        compile_finite_grid(
            {
                "model_id": "bad_grid_private_relations",
                "width": 1,
                "height": 1,
                "movement_rule": "orthogonal",
                "observations": {"color": {"0,0": "red"}},
                "presentations": {},
                "relations": {"private": []},
                "provenance": {
                    "declared_before_run": True,
                    "source": "inline test",
                    "claim_boundary": "reserved-field rejection test",
                },
            }
        )


def _rename_relation(
    tuples: frozenset[tuple[str, ...]],
    mapping: dict[str, str],
) -> frozenset[tuple[str, ...]]:
    return frozenset(tuple(mapping.get(item, item) for item in row) for row in tuples)
