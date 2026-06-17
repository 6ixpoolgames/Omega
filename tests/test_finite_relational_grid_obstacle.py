from pathlib import Path

from omega.adapters.finite_relational import (
    compile_grid_obstacle_source,
    generate_grid_obstacle_study,
    load_model,
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
        "grid_obstacle_hidden_loss": ["hidden_loss"],
        "grid_obstacle_no_hidden_loss_control": ["not_hidden_loss"],
    }


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


def test_grid_obstacle_validation_retains_outputs(tmp_path: Path) -> None:
    result = run_finite_relational_grid_obstacle(out_root=tmp_path)

    assert result["status"] == "PASS"
    assert result["study_count"] == 1
    assert result["representative_case_count"] == 2
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
