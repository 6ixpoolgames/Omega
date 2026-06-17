import json
from pathlib import Path

from omega.adapters.finite_relational import compile_derived_graph_path, load_model, run_declared_audits
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
