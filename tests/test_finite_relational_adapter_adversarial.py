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
    "generated_presentation_fact_closure",
    "generated_reachability_fact_closure",
    "generated_viability_fact_closure",
    "generated_recovery_fact_closure",
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
    assert by_id["generated_presentation_fact_closure"].summary()["findings"].count(
        "closure_ok"
    ) == 2
    assert by_id["generated_reachability_fact_closure"].summary()["findings"] == [
        "closure_ok",
        "closure_ok",
    ]
    assert by_id["generated_viability_fact_closure"].summary()["findings"] == [
        "closure_ok",
        "closure_ok",
    ]
    assert by_id["generated_recovery_fact_closure"].summary()["findings"] == [
        "recoverable",
        "not_recoverable",
        "closure_ok",
        "closure_ok",
    ]


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


def test_generated_presentation_fact_closure_case_has_strict_visibility_drop() -> None:
    case = {
        case.case_id: case for case in generate_adversarial_cases()
    }["generated_presentation_fact_closure"]
    results = {result.audit_id: result.as_dict() for result in case.audit_results}

    exact = results["generated_exact_presentation_keeps_carrier_pair_visible"]
    erasing = results["generated_constant_presentation_erases_carrier_pair_visibility"]

    assert exact["passed"] is True
    assert exact["finding"] == "closure_ok"
    assert exact["observed"]["common_visible_pair_count"] == 2
    assert exact["observed"]["common_visible_pairs"] == [("left", "right"), ("right", "left")]
    assert erasing["passed"] is True
    assert erasing["finding"] == "closure_ok"
    assert erasing["observed"]["common_visible_pair_count"] == 0
    assert erasing["observed"]["present_expected_absent_visible_pairs"] == []


def test_generated_target_fact_closure_cases_have_strict_target_drop() -> None:
    cases = {case.case_id: case for case in generate_adversarial_cases()}
    specs = {
        "generated_reachability_fact_closure": {
            "target": "can_reach_goal",
            "constant": "all_states",
            "exact_audit": "generated_exact_reach_status_preserves_reachability_fact",
            "erasing_audit": "generated_constant_status_erases_reachability_fact",
        },
        "generated_viability_fact_closure": {
            "target": "self_sustaining_safe",
            "constant": "all_states",
            "exact_audit": "generated_exact_viability_status_preserves_viability_fact",
            "erasing_audit": "generated_constant_status_erases_viability_fact",
        },
        "generated_recovery_fact_closure": {
            "target": "bit_target",
            "constant": "all_states",
            "exact_audit": "generated_exact_observation_preserves_recovery_fact",
            "erasing_audit": "generated_constant_observation_erases_recovery_fact",
        },
    }

    for case_id, spec in specs.items():
        results = {result.audit_id: result.as_dict() for result in cases[case_id].audit_results}
        exact = results[str(spec["exact_audit"])]
        erasing = results[str(spec["erasing_audit"])]

        assert exact["passed"] is True
        assert exact["finding"] == "closure_ok"
        assert exact["observed"]["common_target_predicates"] == [
            spec["constant"],
            spec["target"],
        ]
        assert erasing["passed"] is True
        assert erasing["finding"] == "closure_ok"
        assert erasing["observed"]["common_target_predicates"] == [spec["constant"]]
        assert erasing["observed"]["present_expected_absent_target_predicates"] == []


def test_generated_recovery_fact_closure_case_checks_bounded_recovery_gap() -> None:
    case = {
        case.case_id: case for case in generate_adversarial_cases()
    }["generated_recovery_fact_closure"]
    results = {result.audit_id: result.as_dict() for result in case.audit_results}

    exact = results["generated_exact_observation_recovers_bit_target"]
    constant = results["generated_constant_observation_does_not_recover_bit_target"]

    assert exact["passed"] is True
    assert exact["finding"] == "recoverable"
    assert exact["observed"]["successful_decoders"] == ["exact_decoder"]
    assert constant["passed"] is True
    assert constant["finding"] == "not_recoverable"
    assert constant["observed"]["successful_decoders"] == []
    assert constant["observed"]["ambiguous_observation_labels"] == ["merged"]


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
