from pathlib import Path

from omega.adapters.finite_relational import (
    RESERVED_IR_FIELDS,
    generate_adversarial_cases,
    load_model,
)
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
    "generated_presentation_fact_derive_closure",
    "generated_presentation_fact_derive_closure_constant_control",
    "generated_reachability_fact_closure",
    "generated_viability_fact_closure",
    "generated_recovery_fact_closure",
    "generated_target_scramble_sensitivity",
    "generated_decorative_target_scramble_control",
    "generated_target_scramble_capacity_sensitivity",
    "generated_target_scramble_capacity_label_swap_control",
    "generated_dynamic_equivariance",
    "generated_dynamic_non_equivariance",
    "generated_edge_exact_path_lifting_failure",
    "generated_viable_trajectory_count_cycle",
    "generated_viable_trajectory_count_branching",
    "generated_dead_end_safe_prefix",
    "generated_observed_word_count_collapses_branching",
    "generated_observed_word_count_labeled_cycle",
    "generated_observed_word_lifting_monotonicity",
    "generated_observed_word_lifting_inflation",
    "generated_viable_count_inflation",
    "generated_viable_count_hiding",
    "generated_stale_reflected_fact_closure",
    "generated_multi_presentation_fact_closure",
    "generated_crosscutting_presentation_closure",
    "generated_graph_pair_transfer",
    "generated_graph_pair_transfer_missing_return",
    "generated_transport_fact_closure",
    "generated_failed_transport_fact_closure",
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
    assert by_id["generated_presentation_fact_derive_closure"].summary()["findings"] == [
        "derive_ok"
    ]
    assert by_id[
        "generated_presentation_fact_derive_closure_constant_control"
    ].summary()["findings"] == ["derive_ok"]
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
    assert by_id["generated_target_scramble_sensitivity"].summary()["findings"] == [
        "sensitive"
    ]
    assert by_id["generated_decorative_target_scramble_control"].summary()["findings"] == [
        "not_sensitive"
    ]
    assert by_id[
        "generated_target_scramble_capacity_sensitivity"
    ].summary()["findings"] == ["capacity_sensitive"]
    assert by_id[
        "generated_target_scramble_capacity_label_swap_control"
    ].summary()["findings"] == ["not_capacity_sensitive"]
    assert by_id["generated_dynamic_equivariance"].summary()["findings"] == ["equivariant"]
    assert by_id["generated_dynamic_non_equivariance"].summary()["findings"] == [
        "not_equivariant"
    ]
    assert by_id["generated_edge_exact_path_lifting_failure"].summary()["findings"] == [
        "edge_exact",
        "not_step_lifts",
        "not_path_lifts",
    ]
    assert by_id["generated_viable_trajectory_count_cycle"].summary()["findings"] == [
        "count_ok"
    ]
    assert by_id["generated_viable_trajectory_count_branching"].summary()["findings"] == [
        "count_ok"
    ]
    assert by_id["generated_dead_end_safe_prefix"].summary()["findings"] == [
        "count_ok",
        "count_ok",
    ]
    assert by_id[
        "generated_observed_word_count_collapses_branching"
    ].summary()["findings"] == ["count_ok"]
    assert by_id["generated_observed_word_count_labeled_cycle"].summary()["findings"] == [
        "count_ok"
    ]
    assert by_id[
        "generated_observed_word_lifting_monotonicity"
    ].summary()["findings"] == ["monotone"]
    assert by_id["generated_observed_word_lifting_inflation"].summary()["findings"] == [
        "not_monotone"
    ]
    assert by_id["generated_viable_count_inflation"].summary()["findings"] == [
        "distorted"
    ]
    assert by_id["generated_viable_count_hiding"].summary()["findings"] == [
        "distorted"
    ]
    assert by_id["generated_stale_reflected_fact_closure"].summary()["findings"] == [
        "closure_ok",
        "closure_ok",
        "closure_ok",
    ]
    assert by_id["generated_multi_presentation_fact_closure"].summary()["findings"] == [
        "closure_ok",
        "closure_ok",
        "closure_ok",
    ]
    assert by_id["generated_crosscutting_presentation_closure"].summary()["findings"] == [
        "closure_ok",
        "closure_ok",
        "closure_ok",
        "closure_ok",
    ]
    assert by_id["generated_graph_pair_transfer"].summary()["findings"] == [
        "transferred"
    ]
    assert by_id["generated_graph_pair_transfer_missing_return"].summary()["findings"] == [
        "not_transferred"
    ]
    assert by_id["generated_transport_fact_closure"].summary()["findings"] == [
        "transferred",
        "closure_ok",
        "closure_ok",
    ]
    assert by_id["generated_failed_transport_fact_closure"].summary()["findings"] == [
        "not_transferred",
        "closure_ok",
        "closure_ok",
    ]


def test_generated_source_compilers_do_not_smuggle_reserved_ir_fields() -> None:
    generated = {
        case.case_id: case
        for case in generate_adversarial_cases()
        if case.source_format in {"derived_graph", "finite_grid", "derived_graph_pair"}
    }

    assert generated
    for case in generated.values():
        assert not (RESERVED_IR_FIELDS & set(case.source))
        if case.source_format == "derived_graph_pair":
            assert not (RESERVED_IR_FIELDS & set(case.source["source_graph"]))
            assert not (RESERVED_IR_FIELDS & set(case.source["target_graph"]))


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


def test_generated_presentation_fact_derive_closure_cases_do_not_need_candidate_facts() -> None:
    cases = {case.case_id: case for case in generate_adversarial_cases()}
    derive = cases["generated_presentation_fact_derive_closure"].audit_results[0].as_dict()
    constant = cases[
        "generated_presentation_fact_derive_closure_constant_control"
    ].audit_results[0].as_dict()

    assert derive["passed"] is True
    assert derive["finding"] == "derive_ok"
    assert derive["observed"]["closure_mode"] == (
        "generated_universe_admissible_presentations"
    )
    assert derive["observed"]["presentation_universe_count"] == 2
    assert derive["observed"]["admissible_presentation_count"] == 1
    assert derive["observed"]["target_fact_universe_count"] == 4
    assert derive["observed"]["seed_target_facts"] == ["pred:{left}"]
    assert derive["observed"]["surplus_visible_pairs"] == [
        ("left", "right"),
        ("right", "left"),
    ]
    assert derive["observed"]["nonconstant_surplus_target_facts"] == ["pred:{right}"]
    assert derive["observed"]["known_surplus_target_predicates"] == [
        "all_states",
        "empty_target",
        "right_target",
    ]

    assert constant["passed"] is True
    assert constant["finding"] == "derive_ok"
    assert constant["observed"]["presentation_universe_count"] == 2
    assert constant["observed"]["admissible_presentation_count"] == 2
    assert constant["observed"]["closure_visible_pairs"] == []
    assert constant["observed"]["nonconstant_surplus_target_facts"] == []


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
        assert exact["observed"]["seed_target_predicates"] == [spec["constant"]]
        assert exact["observed"]["surplus_common_target_predicates"] == [spec["target"]]
        assert exact["observed"]["nonconstant_surplus_target_predicates"] == [spec["target"]]
        assert erasing["passed"] is True
        assert erasing["finding"] == "closure_ok"
        assert erasing["observed"]["common_target_predicates"] == [spec["constant"]]
        assert erasing["observed"]["surplus_common_target_predicates"] == []
        assert erasing["observed"]["nonconstant_surplus_target_predicates"] == []
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


def test_generated_target_scramble_sensitivity_cases_gate_decorative_targets() -> None:
    cases = {case.case_id: case for case in generate_adversarial_cases()}
    sensitive = cases["generated_target_scramble_sensitivity"].audit_results[0].as_dict()
    decorative = cases["generated_decorative_target_scramble_control"].audit_results[
        0
    ].as_dict()

    assert sensitive["passed"] is True
    assert sensitive["finding"] == "sensitive"
    assert sensitive["observed"]["recoverability_changed"] is True
    assert sensitive["observed"]["successful_decoders_changed"] is True
    assert sensitive["observed"]["target_recoverable"] is True
    assert sensitive["observed"]["scrambled_recoverable"] is False

    assert decorative["passed"] is True
    assert decorative["finding"] == "not_sensitive"
    assert decorative["observed"]["recoverability_changed"] is False
    assert decorative["observed"]["successful_decoders_changed"] is False
    assert decorative["observed"]["target_recoverable"] is False
    assert decorative["observed"]["scrambled_recoverable"] is False


def test_generated_target_scramble_capacity_cases_ignore_label_swap() -> None:
    cases = {case.case_id: case for case in generate_adversarial_cases()}
    sensitive = cases[
        "generated_target_scramble_capacity_sensitivity"
    ].audit_results[0].as_dict()
    label_swap = cases[
        "generated_target_scramble_capacity_label_swap_control"
    ].audit_results[0].as_dict()

    assert sensitive["passed"] is True
    assert sensitive["finding"] == "capacity_sensitive"
    assert sensitive["observed"]["sensitivity_mode"] == (
        "unrestricted_exact_recovery_capacity"
    )
    assert sensitive["observed"]["same_prevalence"] is True
    assert sensitive["observed"]["complement_scramble"] is False
    assert sensitive["observed"]["target_recoverable"] is True
    assert sensitive["observed"]["scrambled_recoverable"] is False
    assert sensitive["observed"]["scrambled_ambiguous_observation_labels"] == [
        "left_block",
        "right_block",
    ]

    assert label_swap["passed"] is True
    assert label_swap["finding"] == "not_capacity_sensitive"
    assert label_swap["observed"]["same_prevalence"] is True
    assert label_swap["observed"]["complement_scramble"] is True
    assert label_swap["observed"]["target_recoverable"] is True
    assert label_swap["observed"]["scrambled_recoverable"] is True
    assert label_swap["observed"]["recoverability_changed"] is False


def test_generated_dynamic_equivariance_cases_check_projected_edges() -> None:
    cases = {case.case_id: case for case in generate_adversarial_cases()}
    equivariant = cases["generated_dynamic_equivariance"].audit_results[0].as_dict()
    broken = cases["generated_dynamic_non_equivariance"].audit_results[0].as_dict()

    assert equivariant["passed"] is True
    assert equivariant["finding"] == "equivariant"
    assert equivariant["observed"]["preserves_steps"] is True
    assert equivariant["observed"]["reflects_steps"] is True
    assert equivariant["observed"]["projected_exact_edges"] == [("L", "R"), ("R", "L")]

    assert broken["passed"] is True
    assert broken["finding"] == "not_equivariant"
    assert broken["observed"]["preserves_steps"] is False
    assert broken["observed"]["reflects_steps"] is False
    assert broken["observed"]["missing_projected_edges"] == [("R", "L")]
    assert broken["observed"]["phantom_abstract_edges"] == [("L", "L")]


def test_generated_edge_exact_case_can_fail_step_and_path_lifting() -> None:
    case = {
        case.case_id: case for case in generate_adversarial_cases()
    }["generated_edge_exact_path_lifting_failure"]
    results = {result.audit_id: result.as_dict() for result in case.audit_results}

    edge = results["generated_global_edge_image_is_exact"]
    step = results["generated_step_lifting_fails_inside_merged_fiber"]
    path = results["generated_path_lifting_detects_spliced_abstract_history"]

    assert edge["passed"] is True
    assert edge["finding"] == "edge_exact"
    assert edge["observed"]["edge_projection_exact"] is True
    assert edge["observed"]["projected_exact_edges"] == [("A", "M"), ("M", "D")]

    assert step["passed"] is True
    assert step["finding"] == "not_step_lifts"
    assert step["observed"]["failures"] == [
        {"state": "b", "source_label": "M", "abstract_target": "D"}
    ]

    assert path["passed"] is True
    assert path["finding"] == "not_path_lifts"
    assert {
        "exact_start": "a",
        "abstract_path": ["A", "M", "D"],
        "path_length": 2,
    } in path["observed"]["failures"]


def test_generated_viable_trajectory_count_cases_expose_growth_profiles() -> None:
    cases = {case.case_id: case for case in generate_adversarial_cases()}
    cycle = cases["generated_viable_trajectory_count_cycle"].audit_results[0].as_dict()
    branching = cases["generated_viable_trajectory_count_branching"].audit_results[
        0
    ].as_dict()

    assert cycle["passed"] is True
    assert cycle["finding"] == "count_ok"
    assert cycle["observed"]["count_profile"] == [2, 2, 2, 2]
    assert cycle["observed"]["final_count"] == 2

    assert branching["passed"] is True
    assert branching["finding"] == "count_ok"
    assert branching["observed"]["count_profile"] == [2, 4, 8, 16]
    assert branching["observed"]["final_count"] == 16


def test_generated_dead_end_safe_prefix_case_separates_extendable_counts() -> None:
    case = {
        case.case_id: case for case in generate_adversarial_cases()
    }["generated_dead_end_safe_prefix"]
    results = {result.audit_id: result.as_dict() for result in case.audit_results}

    safe_prefix = results["generated_dead_end_branching_safe_prefixes"]
    extendable = results["generated_dead_end_branching_not_extendable"]

    assert safe_prefix["passed"] is True
    assert safe_prefix["observed"]["count_kind"] == "safe_prefix"
    assert safe_prefix["observed"]["count_profile"] == [1, 2, 0]

    assert extendable["passed"] is True
    assert extendable["observed"]["count_kind"] == "extendable_safe_prefix"
    assert extendable["observed"]["safe_prefix_count_profile"] == [1, 2, 0]
    assert extendable["observed"]["count_profile"] == [0, 0, 0]
    assert extendable["observed"]["viability_kernel"] == []


def test_generated_observed_word_count_cases_use_observation_language() -> None:
    cases = {case.case_id: case for case in generate_adversarial_cases()}
    collapsed = cases[
        "generated_observed_word_count_collapses_branching"
    ].audit_results[0].as_dict()
    labeled = cases["generated_observed_word_count_labeled_cycle"].audit_results[0].as_dict()

    assert collapsed["passed"] is True
    assert collapsed["finding"] == "count_ok"
    assert collapsed["observed"]["count_kind"] == "observed_extendable_safe_word"
    assert collapsed["observed"]["safe_prefix_count_profile"] == [2, 4, 8]
    assert collapsed["observed"]["extendable_safe_prefix_count_profile"] == [2, 4, 8]
    assert collapsed["observed"]["count_profile"] == [1, 1, 1]
    assert collapsed["observed"]["observed_words_by_horizon"] == [
        [["same"]],
        [["same", "same"]],
        [["same", "same", "same"]],
    ]

    assert labeled["passed"] is True
    assert labeled["finding"] == "count_ok"
    assert labeled["observed"]["safe_prefix_count_profile"] == [2, 2, 2]
    assert labeled["observed"]["extendable_safe_prefix_count_profile"] == [2, 2, 2]
    assert labeled["observed"]["count_profile"] == [2, 2, 2]
    assert labeled["observed"]["observed_words_by_horizon"] == [
        [["L"], ["R"]],
        [["L", "R"], ["R", "L"]],
        [["L", "R", "L"], ["R", "L", "R"]],
    ]


def test_generated_observed_word_lifting_cases_check_monotonicity_contract() -> None:
    cases = {case.case_id: case for case in generate_adversarial_cases()}
    monotone = cases[
        "generated_observed_word_lifting_monotonicity"
    ].audit_results[0].as_dict()
    inflated = cases[
        "generated_observed_word_lifting_inflation"
    ].audit_results[0].as_dict()

    assert monotone["passed"] is True
    assert monotone["finding"] == "monotone"
    assert monotone["observed"]["contract_holds"] is True
    assert monotone["observed"]["not_inflated"] is True
    assert monotone["observed"]["inflates"] is False
    assert monotone["observed"]["exact_count_profile"] == [2, 2, 2]
    assert monotone["observed"]["abstract_count_profile"] == [2, 2, 2]
    assert monotone["observed"]["count_profile_delta"] == [0, 0, 0]

    assert inflated["passed"] is True
    assert inflated["finding"] == "not_monotone"
    assert inflated["observed"]["edge_projection"]["edge_projection_exact"] is True
    assert inflated["observed"]["path_lifting"]["path_lifts"] is False
    assert inflated["observed"]["observation_compatible"] is True
    assert inflated["observed"]["contract_holds"] is False
    assert inflated["observed"]["inflates"] is True
    assert inflated["observed"]["exact_count_profile"] == [1, 1, 1]
    assert inflated["observed"]["abstract_count_profile"] == [1, 1, 2]
    assert inflated["observed"]["count_profile_delta"] == [0, 0, 1]


def test_generated_viable_count_comparison_cases_detect_inflation_and_hiding() -> None:
    cases = {case.case_id: case for case in generate_adversarial_cases()}
    inflation = cases["generated_viable_count_inflation"].audit_results[0].as_dict()
    hiding = cases["generated_viable_count_hiding"].audit_results[0].as_dict()

    assert inflation["passed"] is True
    assert inflation["finding"] == "distorted"
    assert inflation["observed"]["equivariant"] is False
    assert inflation["observed"]["inflates"] is True
    assert inflation["observed"]["hides"] is False
    assert inflation["observed"]["exact_count_profile"] == [2, 2, 2]
    assert inflation["observed"]["abstract_count_profile"] == [2, 4, 8]
    assert inflation["observed"]["count_profile_delta"] == [0, 2, 6]

    assert hiding["passed"] is True
    assert hiding["finding"] == "distorted"
    assert hiding["observed"]["equivariant"] is False
    assert hiding["observed"]["inflates"] is False
    assert hiding["observed"]["hides"] is True
    assert hiding["observed"]["exact_count_profile"] == [2, 4, 8]
    assert hiding["observed"]["abstract_count_profile"] == [2, 2, 2]
    assert hiding["observed"]["count_profile_delta"] == [0, -2, -6]


def test_generated_stale_reflected_fact_closure_case_has_time_indexed_intersection() -> None:
    case = {
        case.case_id: case for case in generate_adversarial_cases()
    }["generated_stale_reflected_fact_closure"]
    results = {result.audit_id: result.as_dict() for result in case.audit_results}

    stale = results["generated_stale_status_preserves_before_reach_fact"]
    reflected = results["generated_reflected_status_preserves_after_reach_fact"]
    intersection = results["generated_stale_reflected_intersection_drops_time_specific_facts"]

    assert stale["passed"] is True
    assert stale["observed"]["common_target_predicates"] == [
        "all_states",
        "before_can_reach_goal",
    ]
    assert stale["observed"]["present_expected_absent_target_predicates"] == []
    assert reflected["passed"] is True
    assert reflected["observed"]["common_target_predicates"] == [
        "after_can_reach_goal",
        "all_states",
    ]
    assert reflected["observed"]["present_expected_absent_target_predicates"] == []
    assert intersection["passed"] is True
    assert intersection["observed"]["common_target_predicates"] == ["all_states"]
    assert intersection["observed"]["present_expected_absent_target_predicates"] == []


def test_generated_multi_presentation_fact_closure_case_intersects_family_facts() -> None:
    case = {
        case.case_id: case for case in generate_adversarial_cases()
    }["generated_multi_presentation_fact_closure"]
    results = {result.audit_id: result.as_dict() for result in case.audit_results}

    row = results["generated_identity_row_family_keeps_row_fact"]
    col = results["generated_identity_col_family_keeps_col_fact"]
    family = results["generated_row_col_family_keeps_only_shared_constants"]

    assert row["passed"] is True
    assert row["observed"]["common_target_predicates"] == ["all_states", "row_top"]
    assert row["observed"]["common_visible_pair_count"] == 8
    assert col["passed"] is True
    assert col["observed"]["common_target_predicates"] == ["all_states", "col_left"]
    assert family["passed"] is True
    assert family["observed"]["common_target_predicates"] == ["all_states"]
    assert family["observed"]["common_visible_pair_count"] == 4
    assert family["observed"]["present_expected_absent_target_predicates"] == []
    assert family["observed"]["missing_expected_common_visible_pairs"] == []


def test_generated_crosscutting_presentation_closure_case_collapses_specific_facts() -> None:
    case = {
        case.case_id: case for case in generate_adversarial_cases()
    }["generated_crosscutting_presentation_closure"]
    results = {result.audit_id: result.as_dict() for result in case.audit_results}

    row = results["generated_row_projection_keeps_row_fact"]
    col = results["generated_col_projection_keeps_col_fact"]
    parity = results["generated_parity_projection_keeps_parity_fact"]
    family = results["generated_row_col_parity_family_erases_all_specific_facts"]

    assert row["passed"] is True
    assert row["observed"]["common_target_predicates"] == ["all_states", "row_zero"]
    assert row["observed"]["common_visible_pair_count"] == 8
    assert col["passed"] is True
    assert col["observed"]["common_target_predicates"] == ["all_states", "col_zero"]
    assert col["observed"]["common_visible_pair_count"] == 8
    assert parity["passed"] is True
    assert parity["observed"]["common_target_predicates"] == [
        "all_states",
        "even_parity",
    ]
    assert parity["observed"]["common_visible_pair_count"] == 8
    assert family["passed"] is True
    assert family["observed"]["common_target_predicates"] == ["all_states"]
    assert family["observed"]["common_visible_pair_count"] == 0
    assert family["observed"]["present_expected_absent_target_predicates"] == []
    assert family["observed"]["present_expected_absent_visible_pairs"] == []


def test_generated_graph_pair_transfer_cases_use_compiled_graph_surfaces() -> None:
    cases = {case.case_id: case for case in generate_adversarial_cases()}
    transferred = cases["generated_graph_pair_transfer"]
    missing_return = cases["generated_graph_pair_transfer_missing_return"]

    assert transferred.source_format == "derived_graph_pair"
    assert missing_return.source_format == "derived_graph_pair"
    for case in (transferred, missing_return):
        assert "source_graph" in case.source
        assert "target_graph" in case.source
        assert "correspondence" in case.source
        assert "relations" not in case.source
        assert "predicates" not in case.source
        assert case.compiled_model["provenance"]["compiled_from"] == "derived_graph_pair"
        assert "source_graph_compiled_digest" in case.compiled_model["provenance"]
        assert "target_graph_compiled_digest" in case.compiled_model["provenance"]
        assert "audit=carrier_transfer" in case.compiled_model["provenance"][
            "derivation_rules"
        ]

    positive = transferred.audit_results[0].as_dict()
    negative = missing_return.audit_results[0].as_dict()

    assert positive["passed"] is True
    assert positive["finding"] == "transferred"
    assert positive["observed"]["source_certified"] is True
    assert positive["observed"]["target_certified"] is True
    assert positive["observed"]["endpoint_correspondence"] is True
    assert negative["passed"] is True
    assert negative["finding"] == "not_transferred"
    assert negative["observed"]["source_certified"] is True
    assert negative["observed"]["target_certified"] is False
    assert negative["observed"]["endpoint_correspondence"] is True
    assert negative["observed"]["target"]["mutually_reachable"] is False


def test_generated_transport_fact_closure_case_tracks_transferred_role() -> None:
    case = {
        case.case_id: case for case in generate_adversarial_cases()
    }["generated_transport_fact_closure"]
    results = {result.audit_id: result.as_dict() for result in case.audit_results}

    transfer = results["generated_cycle_carrier_transfer_contract"]
    lifted = results["generated_lifted_transfer_views_preserve_transported_role"]
    erasing = results["generated_erasing_transport_view_drops_transported_role"]

    assert transfer["passed"] is True
    assert transfer["finding"] == "transferred"
    assert transfer["observed"]["source_certified"] is True
    assert transfer["observed"]["target_certified"] is True
    assert transfer["observed"]["endpoint_correspondence"] is True
    assert lifted["passed"] is True
    assert lifted["observed"]["common_target_predicates"] == [
        "all_states",
        "transported_left_endpoint",
    ]
    assert lifted["observed"]["common_visible_pair_count"] == 8
    assert lifted["observed"]["missing_expected_common_visible_pairs"] == []
    assert erasing["passed"] is True
    assert erasing["observed"]["common_target_predicates"] == ["all_states"]
    assert erasing["observed"]["common_visible_pair_count"] == 0
    assert erasing["observed"]["present_expected_absent_target_predicates"] == []
    assert erasing["observed"]["present_expected_absent_visible_pairs"] == []


def test_generated_failed_transport_fact_closure_case_blocks_identity_smuggling() -> None:
    case = {
        case.case_id: case for case in generate_adversarial_cases()
    }["generated_failed_transport_fact_closure"]
    results = {result.audit_id: result.as_dict() for result in case.audit_results}

    transfer = results["generated_broken_carrier_transfer_contract"]
    lifted = results["generated_role_views_preserve_label_fact_despite_failed_transfer"]
    erasing = results["generated_erasing_view_drops_label_fact_after_failed_transfer"]

    assert transfer["passed"] is True
    assert transfer["finding"] == "not_transferred"
    assert transfer["observed"]["source_certified"] is True
    assert transfer["observed"]["target_certified"] is False
    assert transfer["observed"]["endpoint_correspondence"] is True
    assert transfer["observed"]["target"]["mutually_reachable"] is False
    assert lifted["passed"] is True
    assert lifted["observed"]["common_target_predicates"] == [
        "all_states",
        "transported_left_endpoint",
    ]
    assert lifted["observed"]["common_visible_pair_count"] == 8
    assert erasing["passed"] is True
    assert erasing["observed"]["common_target_predicates"] == ["all_states"]
    assert erasing["observed"]["present_expected_absent_target_predicates"] == []


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
