from pathlib import Path

import pytest

from omega.adapters.finite_relational import (
    SchemaError,
    compile_graph_pair_transfer_source,
    generate_graph_pair_transfer_characterization,
    reserved_ir_fields,
)
from omega.validation.finite_relational_graph_pair_transfer import (
    run_finite_relational_graph_pair_transfer,
)


def test_graph_pair_transfer_characterization_sweeps_target_graphs() -> None:
    studies = generate_graph_pair_transfer_characterization()
    by_id = {study.study_id: study for study in studies}

    assert set(by_id) == {
        "graph_pair_two_node_transfer_sweep",
        "graph_pair_three_node_extension_transfer_sweep",
    }
    assert all(study.all_passed for study in studies)
    assert by_id["graph_pair_two_node_transfer_sweep"].metrics[
        "transferred_fraction"
    ] == "1/4"
    assert by_id["graph_pair_two_node_transfer_sweep"].metrics[
        "forward_but_not_transferred_target_graph_count"
    ] == 1
    assert by_id["graph_pair_three_node_extension_transfer_sweep"].metrics[
        "transferred_fraction"
    ] == "18/64"
    assert by_id["graph_pair_three_node_extension_transfer_sweep"].metrics[
        "forward_but_not_transferred_target_graph_count"
    ] == 22


def test_graph_pair_transfer_representatives_use_generic_transfer_audit() -> None:
    studies = generate_graph_pair_transfer_characterization()
    for study in studies:
        findings = [
            tuple(result.finding for result in case.audit_results)
            for case in study.representative_cases
        ]
        assert ("transferred",) in findings
        assert ("not_transferred",) in findings


def test_graph_pair_transfer_compiler_retains_derivation_provenance() -> None:
    [study] = [
        study
        for study in generate_graph_pair_transfer_characterization()
        if study.study_id == "graph_pair_three_node_extension_transfer_sweep"
    ]
    [case] = [
        case
        for case in study.representative_cases
        if [result.finding for result in case.audit_results] == ["transferred"]
    ]
    compiled = compile_graph_pair_transfer_source(case.source)
    provenance = compiled["provenance"]

    assert provenance["compiled_from"] == "derived_graph_pair"
    assert provenance["source_graph_compiled_digest"]
    assert provenance["target_graph_compiled_digest"]
    assert "audit=carrier_transfer" in provenance["derivation_rules"]
    assert compiled["audits"][0]["kind"] == "carrier_transfer"


def test_graph_pair_transfer_source_rejects_reserved_ir_fields() -> None:
    [study] = [
        study
        for study in generate_graph_pair_transfer_characterization()
        if study.study_id == "graph_pair_two_node_transfer_sweep"
    ]
    source = dict(study.representative_cases[0].source)
    source["audits"] = [{"id": "private", "kind": "carrier_transfer"}]

    assert reserved_ir_fields(source) == ("audits",)
    with pytest.raises(SchemaError, match="must not declare finite relational IR fields"):
        compile_graph_pair_transfer_source(source)


def test_graph_pair_transfer_validation_retains_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_graph_pair_transfer(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["study_count"] == 2
    assert result["representative_case_count"] == 4
    assert result["all_passed"] is True
    assert (Path(str(result["run_root"])) / "summary.json").exists()
    for study in result["studies"]:
        study_dir = Path(str(study["output"]))
        assert (study_dir / "study_summary.json").exists()
        for case in study["representative_cases"]:
            out_dir = Path(str(case["output"]))
            assert (out_dir / "source.json").exists()
            assert (out_dir / "compiled_model.json").exists()
            assert (out_dir / "source_digest.txt").exists()
            assert (out_dir / "compiled_model_digest.txt").exists()
            assert (out_dir / "audit_results.json").exists()
            assert (out_dir / "summary.json").exists()
