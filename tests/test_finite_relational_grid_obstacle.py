from pathlib import Path

import pytest

from omega.adapters.finite_relational import (
    SchemaError,
    compile_grid_obstacle_source,
    generate_grid_obstacle_characterization,
    generate_grid_obstacle_study,
    load_model,
    reserved_ir_fields,
)
from omega.validation.finite_relational_grid_obstacle import (
    run_finite_relational_grid_obstacle,
)


def test_grid_obstacle_study_counts_hidden_loss_cases() -> None:
    study = generate_grid_obstacle_study()

    assert study.study_id == "grid_obstacle_insertion_hidden_loss"
    assert study.all_passed is True
    assert study.search_space["width"] == 3
    assert study.search_space["height"] == 3
    assert study.search_space["movement_rule"] == "orthogonal"
    assert study.metrics["before_path"] is True
    assert study.metrics["hidden_loss_set_count"] > 0
    assert study.metrics["no_loss_set_count"] > 0
    assert study.metrics["hidden_loss_fraction"] == "9/64"


def test_grid_obstacle_representatives_use_hidden_loss_audit() -> None:
    study = generate_grid_obstacle_study()
    findings = {
        case.case_id: [result.finding for result in case.audit_results]
        for case in study.representative_cases
    }

    assert findings == {
        "grid_obstacle_hidden_loss": ["hidden_loss", "closure_ok", "closure_ok"],
        "grid_obstacle_no_hidden_loss_control": [
            "not_hidden_loss",
            "closure_ok",
            "closure_ok",
        ],
    }


def test_grid_obstacle_characterization_sweeps_multiple_source_grids() -> None:
    studies = generate_grid_obstacle_characterization()
    by_id = {study.study_id: study for study in studies}

    assert set(by_id) == {
        "grid_obstacle_insertion_hidden_loss",
        "grid_obstacle_east_south_diagonal_hidden_loss",
        "grid_obstacle_orthogonal_rectangle_hidden_loss",
    }
    assert all(study.all_passed for study in studies)
    assert by_id["grid_obstacle_east_south_diagonal_hidden_loss"].metrics[
        "hidden_loss_fraction"
    ] == "2/29"
    assert by_id["grid_obstacle_orthogonal_rectangle_hidden_loss"].metrics[
        "hidden_loss_fraction"
    ] == "6/22"
    for study in studies:
        assert len(study.representative_cases) == 2
        findings = [
            tuple(result.finding for result in case.audit_results)
            for case in study.representative_cases
        ]
        assert ("hidden_loss", "closure_ok", "closure_ok") in findings
        assert ("not_hidden_loss", "closure_ok", "closure_ok") in findings


def test_grid_obstacle_representatives_expose_empirical_adjacent_closure() -> None:
    cases = {
        case.case_id: case
        for case in generate_grid_obstacle_study().representative_cases
    }
    hidden = cases["grid_obstacle_hidden_loss"]
    results = {result.audit_id: result.as_dict() for result in hidden.audit_results}

    reflected = results["reflected_grid_status_preserves_after_source_reachability"]
    stale_reflected = results[
        "stale_reflected_grid_status_drops_after_source_reachability"
    ]

    assert reflected["passed"] is True
    assert reflected["observed"]["common_target_predicates"] == [
        "after_reachable_from_source",
        "all_states",
    ]
    assert stale_reflected["passed"] is True
    assert stale_reflected["observed"]["common_target_predicates"] == ["all_states"]
    assert stale_reflected["observed"]["present_expected_absent_target_predicates"] == []


def test_grid_obstacle_compiler_retains_source_and_compiled_provenance() -> None:
    [case] = [
        case
        for case in generate_grid_obstacle_study().representative_cases
        if case.case_id == "grid_obstacle_hidden_loss"
    ]
    compiled = compile_grid_obstacle_source(case.source)
    model = load_model(compiled)

    assert compiled["provenance"]["compiled_from"] == "grid_obstacle_insertion"
    assert compiled["provenance"]["source_digest"]
    assert model.relation_tuples("before_next")
    assert model.relation_tuples("after_next")
    assert model.relation_tuples("abstract_next") == model.relation_tuples("before_next")
    assert "after_reachable_from_source" in compiled["predicates"]
    assert "reflected_source_reach_status" in compiled["functions"]
    assert (
        "optional_audits=presentation_fact_closure(stale,reflected)"
        in compiled["provenance"]["derivation_rules"]
    )


def test_grid_obstacle_source_rejects_reserved_ir_fields() -> None:
    source = {
        "model_id": "bad_grid_obstacle_private_audit",
        "width": 2,
        "height": 1,
        "movement_rule": "orthogonal",
        "source": "0,0",
        "target": "1,0",
        "before_blocked": [],
        "after_blocked": [],
        "audits": [{"id": "private", "kind": "hidden_reachability_loss"}],
        "provenance": {
            "declared_before_run": True,
            "source": "inline test",
            "claim_boundary": "reserved-field rejection test",
        },
    }

    assert reserved_ir_fields(source) == ("audits",)
    with pytest.raises(SchemaError, match="must not declare finite relational IR fields"):
        compile_grid_obstacle_source(source)


def test_grid_obstacle_validation_retains_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_grid_obstacle(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["study_count"] == 3
    assert result["representative_case_count"] == 6
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
