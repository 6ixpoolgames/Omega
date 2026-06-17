from pathlib import Path

from omega.adapters.finite_relational import generate_adversarial_cases, load_model
from omega.validation.finite_relational_adapter_adversarial import (
    run_finite_relational_adapter_adversarial,
)


REQUIRED_CASE_IDS = {
    "generated_phantom_reachability",
    "generated_hidden_reachability_loss",
    "generated_proxy_nonfactorization",
    "generated_derived_graph_asymmetry",
    "generated_derived_graph_carrier",
    "generated_finite_grid_asymmetry",
}


def test_generated_adversarial_cases_cover_adapter_failure_modes() -> None:
    cases = generate_adversarial_cases()
    by_id = {case.case_id: case for case in cases}

    assert set(by_id) == REQUIRED_CASE_IDS
    assert all(case.all_passed for case in cases)
    assert by_id["generated_phantom_reachability"].summary()["findings"] == ["phantom"]
    assert by_id["generated_hidden_reachability_loss"].summary()["findings"] == ["hidden_loss"]
    assert by_id["generated_proxy_nonfactorization"].summary()["findings"] == ["witness"]
    assert "certified" in by_id["generated_derived_graph_carrier"].summary()["findings"]


def test_generated_source_compilers_do_not_smuggle_reserved_ir_fields() -> None:
    reserved = {"predicates", "relations", "functions", "profiles", "audits"}
    generated = {
        case.case_id: case
        for case in generate_adversarial_cases()
        if case.source_format in {"derived_graph", "finite_grid"}
    }

    assert generated
    for case in generated.values():
        assert not (reserved & set(case.source))


def test_generated_finite_grid_case_compiles_to_alpha_like_asymmetry() -> None:
    case = {
        case.case_id: case for case in generate_adversarial_cases()
    }["generated_finite_grid_asymmetry"]
    model = load_model(case.compiled_model)

    assert model.relation_tuples("primitive_asym")
    assert case.compiled_model["provenance"]["compiled_from"] == "finite_grid"
    assert case.compiled_model["provenance"]["intermediate_compiler"] == "derived_graph"


def test_generated_adversarial_validation_retains_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_adapter_adversarial(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["case_count"] == len(REQUIRED_CASE_IDS)
    assert result["all_passed"] is True
    for case in result["cases"]:
        out_dir = Path(str(case["output"]))
        assert out_dir.exists()
        assert (out_dir / "source.json").exists()
        assert (out_dir / "compiled_model.json").exists()
        assert (out_dir / "source_digest.txt").exists()
        assert (out_dir / "compiled_model_digest.txt").exists()
        assert (out_dir / "audit_results.json").exists()
        assert (out_dir / "summary.json").exists()
