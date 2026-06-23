import json
from pathlib import Path

import pytest

from omega.adapters.finite_relational import (
    SchemaError,
    compile_derived_graph,
    compile_derived_graph_path,
    compiled_derivation_contract,
    load_model,
    load_model_path,
    reserved_ir_fields,
    run_declared_audits,
)
from omega.adapters.finite_relational.graph_cli import run_graph_file


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "omega" / "adapters" / "finite_relational" / "fixtures"


def test_derived_graph_earns_alpha_asymmetry_without_source_labeling() -> None:
    source_path = FIXTURES / "derived_graph_strict_asymmetry.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))

    compiled = compile_derived_graph_path(source_path)
    model = load_model(compiled)
    results = {result.audit_id: result.as_dict() for result in run_declared_audits(model)}

    assert "relations" not in source
    assert "profiles" not in source
    assert "audits" not in source
    assert model.relation_tuples("primitive_asym") == frozenset({("color", "source", "sink")})
    assert model.relation_tuples("primitive_sep") == frozenset(
        {
            ("color", "source", "sink"),
            ("color", "sink", "source"),
        }
    )
    assert results["derived_alpha_laws"]["passed"] is True
    assert results["derived_alpha_laws"]["observed"]["primitive_witness_exists"] is True
    assert results["presentation_identity"]["finding"] == "sound"
    assert results["presentation_identity"]["passed"] is True
    assert results["presentation_constant"]["finding"] == "not_sound"
    assert results["presentation_constant"]["passed"] is True
    assert results["presentation_constant"]["observed"]["violation_count"] == 2


def test_derived_graph_earns_recurrent_carrier_certificate() -> None:
    source_path = FIXTURES / "derived_graph_recurrent_carrier.json"
    source_text = source_path.read_text(encoding="utf-8")

    compiled = compile_derived_graph_path(source_path)
    model = load_model(compiled)
    results = {result.audit_id: result.as_dict() for result in run_declared_audits(model)}

    assert "carrier_0" not in source_text
    assert model.relation_tuples("primitive_asym") == frozenset()
    assert model.predicate_members("carrier_0") == frozenset({"left", "right"})
    assert results["carrier_0_certificate"]["passed"] is True
    assert results["carrier_0_certificate"]["observed"]["certified"] is True
    assert results["carrier_0_certificate"]["observed"]["mutually_reachable"] is True


def test_derived_graph_matches_hand_specified_carrier_semantics() -> None:
    compiled = compile_derived_graph_path(FIXTURES / "derived_graph_recurrent_carrier.json")
    derived = load_model(compiled)
    hand_specified = load_model_path(FIXTURES / "sound_pass.json")

    derived_results = {result.finding for result in run_declared_audits(derived)}
    hand_results = {result.finding for result in run_declared_audits(hand_specified)}

    assert derived.relation_tuples("merge_separated") == hand_specified.relation_tuples(
        "merge_separated"
    )
    assert derived.function_mapping("identity") == hand_specified.function_mapping("present_identity")
    assert "sound" in derived_results
    assert "sound" in hand_results
    assert "certified" in derived_results
    assert "certified" in hand_results


def test_mixed_asymmetry_fixture_derives_only_strict_separated_edges() -> None:
    compiled = compile_derived_graph_path(FIXTURES / "derived_graph_mixed_asymmetry.json")
    model = load_model(compiled)

    assert model.relation_tuples("primitive_asym") == frozenset({("color", "c", "d")})
    assert ("color", "a", "b") in model.relation_tuples("primitive_sep")
    assert ("color", "b", "a") in model.relation_tuples("primitive_sep")
    assert ("color", "d", "e") not in model.relation_tuples("primitive_sep")


def test_derived_graph_rejects_reserved_ir_fields() -> None:
    source = {
        "model_id": "bad_private_audit_source",
        "nodes": ["x", "y"],
        "edges": [["x", "y"]],
        "observations": {"color": {"x": "red", "y": "blue"}},
        "presentations": {},
        "audits": [{"id": "private", "kind": "alpha_laws"}],
        "provenance": {
            "declared_before_run": True,
            "source": "inline test",
            "claim_boundary": "reserved-field rejection test",
        },
    }

    assert reserved_ir_fields(source) == ("audits",)
    with pytest.raises(SchemaError, match="must not declare finite relational IR fields"):
        compile_derived_graph(source)


def test_derived_graph_compiled_provenance_records_derivation_contract() -> None:
    compiled = compile_derived_graph_path(FIXTURES / "derived_graph_strict_asymmetry.json")

    contract = compiled_derivation_contract(
        compiled,
        compiled_from="derived_graph",
        required_derivation_rules=(
            "Rel=edge",
            "Sep=observation_differs",
            "Asym=strict_directed_edge_and_observation_differs",
        ),
    )

    assert contract["complete"] is True
    assert contract["missing_derivation_rules"] == []


def test_derived_graph_rejects_raw_functions_field() -> None:
    with pytest.raises(SchemaError, match="functions"):
        compile_derived_graph(
            {
                "model_id": "bad_private_function_source",
                "nodes": ["x"],
                "edges": [],
                "observations": {"color": {"x": "red"}},
                "presentations": {},
                "functions": {"private": {"x": "merged"}},
                "provenance": {
                    "declared_before_run": True,
                    "source": "inline test",
                    "claim_boundary": "reserved-field rejection test",
                },
            }
        )


def test_derived_graph_cli_retains_source_compiled_model_and_audits(tmp_path: Path) -> None:
    out_dir = tmp_path / "derived_graph_smoke"
    summary = run_graph_file(FIXTURES / "derived_graph_strict_asymmetry.json", out_dir)

    assert summary["all_passed"] is True
    assert summary["audit_count"] == 3
    assert (out_dir / "source.json").exists()
    assert (out_dir / "compiled_model.json").exists()
    assert (out_dir / "source_digest.txt").exists()
    assert (out_dir / "compiled_model_digest.txt").exists()
    assert (out_dir / "provenance_check.json").exists()
    assert (out_dir / "audit_results.json").exists()
    assert (out_dir / "summary.json").exists()
