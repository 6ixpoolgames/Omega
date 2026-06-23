from pathlib import Path

import pytest

from omega.adapters.finite_relational import (
    SchemaError,
    load_model,
    load_model_path,
    model_digest,
    run_declared_audits,
    validate_provenance,
)
from omega.adapters.finite_relational.cli import run_model_file


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "omega" / "adapters" / "finite_relational" / "fixtures"


def test_sound_fixture_exposes_alpha_surface_and_carrier_certificate() -> None:
    model = load_model_path(FIXTURES / "sound_pass.json")

    provenance = validate_provenance(model)
    results = [result.as_dict() for result in run_declared_audits(model)]

    assert provenance["complete"] is True
    assert len(model_digest(model)) == 64
    assert all(result["passed"] for result in results)
    assert [result["finding"] for result in results] == [
        "alpha_laws_hold",
        "sound",
        "certified",
    ]

    carrier = next(result for result in results if result["kind"] == "carrier_certificate")
    assert carrier["observed"]["certified"] is True
    assert carrier["observed"]["mutually_reachable"] is True


def test_phantom_reachability_fixture_detects_fabricated_path() -> None:
    model = load_model_path(FIXTURES / "phantom_reachability_fail.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "phantom"
    assert result["observed"]["exact_path"] is False
    assert result["observed"]["abstract_path"] is True


def test_hidden_reachability_loss_fixture_detects_abstractly_hidden_loss() -> None:
    model = load_model_path(FIXTURES / "hidden_reachability_loss_fail.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "hidden_loss"
    assert result["observed"]["before_path"] is True
    assert result["observed"]["after_path"] is False
    assert result["observed"]["abstract_path"] is True


def test_proxy_fixture_detects_nonfactorization_witness() -> None:
    model = load_model_path(FIXTURES / "proxy_nonfactorization_fail.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "witness"
    assert {frozenset(pair) for pair in result["observed"]["witnesses"]} == {
        frozenset({"safe_run", "loss_run"})
    }


def test_simple_form_fixture_detects_function_target_nonfactorization() -> None:
    model = load_model_path(FIXTURES / "simple_form_nonfactorization_fail.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "witness"
    assert {frozenset(pair) for pair in result["observed"]["witnesses"]} == {
        frozenset({"weak_constraint", "strong_constraint"})
    }


def test_entropy_control_fixture_detects_bounded_recoverability_nonfactorization() -> None:
    model = load_model_path(FIXTURES / "entropy_controlled_nonfactorization_fail.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "witness"
    assert {frozenset(pair) for pair in result["observed"]["witnesses"]} == {
        frozenset({"bounded_recoverable_layout", "entropy_matched_scramble"})
    }


def test_ordered_trace_fixture_detects_bag_summary_nonfactorization() -> None:
    model = load_model_path(FIXTURES / "ordered_trace_nonfactorization_fail.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "witness"
    assert {frozenset(pair) for pair in result["observed"]["witnesses"]} == {
        frozenset({"alternating_trace", "blocked_trace"})
    }


def test_bounded_recovery_fixture_accepts_successful_declared_decoder() -> None:
    model = load_model_path(FIXTURES / "bounded_recovery_pass.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "recoverable"
    assert result["observed"]["successful_decoders"] == ["color_decoder"]
    assert result["observed"]["ambiguous_observation_labels"] == []


def test_bounded_recovery_fixture_rejects_entropy_matched_ambiguous_observation() -> None:
    model = load_model_path(FIXTURES / "bounded_recovery_entropy_fail.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "not_recoverable"
    assert result["observed"]["successful_decoders"] == []
    assert result["observed"]["ambiguous_observation_labels"] == ["blue", "red"]
    assert result["observed"]["decoder_count"] == 4


def test_target_scramble_sensitivity_compares_declared_recovery_surface() -> None:
    model = load_model(
        {
            "model_id": "inline_target_scramble_sensitivity",
            "domains": {
                "state": ["left", "right"],
                "observation": ["red", "blue"],
                "truth": ["false", "true"],
            },
            "predicates": {
                "left_target": ["left"],
                "right_scramble": ["right"],
            },
            "functions": {
                "color_observation": {
                    "domain": "state",
                    "codomain": "observation",
                    "mapping": {"left": "red", "right": "blue"},
                },
                "left_decoder": {
                    "domain": "observation",
                    "codomain": "truth",
                    "mapping": {"red": "true", "blue": "false"},
                },
            },
            "audits": [
                {
                    "id": "declared_target_changes_under_scramble",
                    "kind": "target_scramble_sensitivity",
                    "observation": "color_observation",
                    "target_predicate": "left_target",
                    "scrambled_predicate": "right_scramble",
                    "decoders": ["left_decoder"],
                    "expect": "sensitive",
                }
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "target scramble sensitivity unit test",
            },
        }
    )
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "sensitive"
    assert result["observed"]["sensitivity_mode"] == "decoder_relative"
    assert result["observed"]["recoverability_changed"] is True
    assert result["observed"]["target_recoverable"] is True
    assert result["observed"]["scrambled_recoverable"] is False
    assert result["observed"]["target_successful_decoders"] == ["left_decoder"]
    assert result["observed"]["scrambled_successful_decoders"] == []


def test_target_scramble_sensitivity_can_fail_when_observation_is_decorative() -> None:
    model = load_model(
        {
            "model_id": "inline_target_scramble_decorative_control",
            "domains": {
                "state": ["left", "right"],
                "observation": ["merged"],
                "truth": ["false", "true"],
            },
            "predicates": {
                "left_target": ["left"],
                "right_scramble": ["right"],
            },
            "functions": {
                "constant_observation": {
                    "domain": "state",
                    "codomain": "observation",
                    "mapping": {"left": "merged", "right": "merged"},
                },
                "always_false_decoder": {
                    "domain": "observation",
                    "codomain": "truth",
                    "mapping": {"merged": "false"},
                },
            },
            "audits": [
                {
                    "id": "declared_target_unchanged_under_scramble",
                    "kind": "target_scramble_sensitivity",
                    "observation": "constant_observation",
                    "target_predicate": "left_target",
                    "scrambled_predicate": "right_scramble",
                    "decoders": ["always_false_decoder"],
                    "expect": "not_sensitive",
                }
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "target scramble decorative-control unit test",
            },
        }
    )
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "not_sensitive"
    assert result["observed"]["sensitivity_mode"] == "decoder_relative"
    assert result["observed"]["recoverability_changed"] is False
    assert result["observed"]["successful_decoders_changed"] is False
    assert result["observed"]["target_recoverable"] is False
    assert result["observed"]["scrambled_recoverable"] is False


def test_target_scramble_capacity_ignores_boolean_label_swap() -> None:
    model = load_model(
        {
            "model_id": "inline_target_scramble_capacity_label_swap_control",
            "domains": {
                "state": ["left", "right"],
                "observation": ["red", "blue"],
            },
            "predicates": {
                "left_target": ["left"],
                "right_scramble": ["right"],
            },
            "functions": {
                "color_observation": {
                    "domain": "state",
                    "codomain": "observation",
                    "mapping": {"left": "red", "right": "blue"},
                },
            },
            "audits": [
                {
                    "id": "boolean_label_swap_does_not_change_capacity",
                    "kind": "target_scramble_capacity_sensitivity",
                    "observation": "color_observation",
                    "target_predicate": "left_target",
                    "scrambled_predicate": "right_scramble",
                    "expect": "not_capacity_sensitive",
                }
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "target scramble capacity label-swap control",
            },
        }
    )
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "not_capacity_sensitive"
    assert result["observed"]["sensitivity_mode"] == "unrestricted_exact_recovery_capacity"
    assert result["observed"]["complement_scramble"] is True
    assert result["observed"]["target_recoverable"] is True
    assert result["observed"]["scrambled_recoverable"] is True
    assert result["observed"]["recoverability_changed"] is False


def test_target_scramble_capacity_detects_same_prevalence_non_relabel_scramble() -> None:
    model = load_model(
        {
            "model_id": "inline_target_scramble_capacity_same_prevalence",
            "domains": {
                "state": ["a", "b", "c", "d"],
                "observation": ["left_block", "right_block"],
            },
            "predicates": {
                "block_target": ["a", "b"],
                "crosscut_scramble": ["a", "c"],
            },
            "functions": {
                "block_observation": {
                    "domain": "state",
                    "codomain": "observation",
                    "mapping": {
                        "a": "left_block",
                        "b": "left_block",
                        "c": "right_block",
                        "d": "right_block",
                    },
                },
            },
            "audits": [
                {
                    "id": "same_prevalence_scramble_changes_capacity",
                    "kind": "target_scramble_capacity_sensitivity",
                    "observation": "block_observation",
                    "target_predicate": "block_target",
                    "scrambled_predicate": "crosscut_scramble",
                    "expect": "capacity_sensitive",
                }
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "target scramble capacity same-prevalence test",
            },
        }
    )
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "capacity_sensitive"
    assert result["observed"]["same_prevalence"] is True
    assert result["observed"]["complement_scramble"] is False
    assert result["observed"]["target_recoverable"] is True
    assert result["observed"]["scrambled_recoverable"] is False
    assert result["observed"]["scrambled_ambiguous_observation_labels"] == [
        "left_block",
        "right_block",
    ]


def test_dynamic_presentation_equivariance_accepts_projected_transition() -> None:
    model = load_model(
        {
            "model_id": "inline_dynamic_equivariance_pass",
            "domains": {
                "state": ["left", "right"],
                "role": ["L", "R"],
            },
            "relations": {
                "next": {
                    "domains": ["state", "state"],
                    "tuples": [["left", "right"], ["right", "left"]],
                },
                "role_next": {
                    "domains": ["role", "role"],
                    "tuples": [["L", "R"], ["R", "L"]],
                },
            },
            "functions": {
                "role_presentation": {
                    "domain": "state",
                    "codomain": "role",
                    "mapping": {"left": "L", "right": "R"},
                },
            },
            "audits": [
                {
                    "id": "projected_role_dynamics_commutes",
                    "kind": "dynamic_presentation_equivariance",
                    "transition": "next",
                    "presentation": "role_presentation",
                    "abstract_transition": "role_next",
                    "expect": "equivariant",
                }
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "dynamic equivariance unit test",
            },
        }
    )
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "equivariant"
    assert result["observed"]["preserves_steps"] is True
    assert result["observed"]["reflects_steps"] is True
    assert result["observed"]["projected_exact_edges"] == [("L", "R"), ("R", "L")]
    assert result["observed"]["missing_projected_edges"] == []
    assert result["observed"]["phantom_abstract_edges"] == []


def test_dynamic_presentation_equivariance_rejects_missing_and_phantom_edges() -> None:
    model = load_model(
        {
            "model_id": "inline_dynamic_equivariance_fail",
            "domains": {
                "state": ["left", "right"],
                "role": ["L", "R"],
            },
            "relations": {
                "next": {
                    "domains": ["state", "state"],
                    "tuples": [["left", "right"], ["right", "left"]],
                },
                "bad_role_next": {
                    "domains": ["role", "role"],
                    "tuples": [["L", "R"], ["L", "L"]],
                },
            },
            "functions": {
                "role_presentation": {
                    "domain": "state",
                    "codomain": "role",
                    "mapping": {"left": "L", "right": "R"},
                },
            },
            "audits": [
                {
                    "id": "bad_role_dynamics_does_not_commute",
                    "kind": "dynamic_presentation_equivariance",
                    "transition": "next",
                    "presentation": "role_presentation",
                    "abstract_transition": "bad_role_next",
                    "expect": "not_equivariant",
                }
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "dynamic non-equivariance unit test",
            },
        }
    )
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "not_equivariant"
    assert result["observed"]["preserves_steps"] is False
    assert result["observed"]["reflects_steps"] is False
    assert result["observed"]["missing_projected_edges"] == [("R", "L")]
    assert result["observed"]["phantom_abstract_edges"] == [("L", "L")]


def test_edge_projection_exactness_does_not_imply_path_lifting() -> None:
    model = load_model(
        {
            "model_id": "inline_edge_exact_but_path_splices_representatives",
            "domains": {
                "state": ["a", "b", "c", "d"],
                "label": ["A", "M", "D"],
            },
            "relations": {
                "next": {
                    "domains": ["state", "state"],
                    "tuples": [["a", "b"], ["c", "d"]],
                },
                "abstract_next": {
                    "domains": ["label", "label"],
                    "tuples": [["A", "M"], ["M", "D"]],
                },
            },
            "functions": {
                "presentation": {
                    "domain": "state",
                    "codomain": "label",
                    "mapping": {"a": "A", "b": "M", "c": "M", "d": "D"},
                },
            },
            "audits": [
                {
                    "id": "global_edge_image_is_exact",
                    "kind": "dynamic_edge_projection_exactness",
                    "transition": "next",
                    "presentation": "presentation",
                    "abstract_transition": "abstract_next",
                    "expect": "edge_exact",
                },
                {
                    "id": "merged_representative_step_does_not_lift",
                    "kind": "dynamic_step_lifting",
                    "transition": "next",
                    "presentation": "presentation",
                    "abstract_transition": "abstract_next",
                    "expect": "not_step_lifts",
                },
                {
                    "id": "abstract_path_splices_incompatible_representatives",
                    "kind": "dynamic_path_lifting",
                    "transition": "next",
                    "presentation": "presentation",
                    "abstract_transition": "abstract_next",
                    "horizon": 2,
                    "expect": "not_path_lifts",
                },
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "edge exactness versus path lifting unit test",
            },
        }
    )
    results = {result.audit_id: result.as_dict() for result in run_declared_audits(model)}

    edge = results["global_edge_image_is_exact"]
    step = results["merged_representative_step_does_not_lift"]
    path = results["abstract_path_splices_incompatible_representatives"]

    assert edge["passed"] is True
    assert edge["finding"] == "edge_exact"
    assert edge["observed"]["projected_exact_edges"] == [("A", "M"), ("M", "D")]
    assert edge["observed"]["phantom_abstract_edges"] == []

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


def test_viable_trajectory_count_counts_safe_cycle_words() -> None:
    model = load_model(
        {
            "model_id": "inline_viable_trajectory_count_cycle",
            "domains": {"state": ["left", "right"]},
            "predicates": {"safe": ["left", "right"]},
            "relations": {
                "next": {
                    "domains": ["state", "state"],
                    "tuples": [["left", "right"], ["right", "left"]],
                }
            },
            "audits": [
                {
                    "id": "two_state_cycle_has_flat_safe_word_profile",
                    "kind": "viable_trajectory_count",
                    "transition": "next",
                    "safety": "safe",
                    "horizon": 3,
                    "expected_count_profile": [2, 2, 2, 2],
                    "expected_final_count": 2,
                    "expect": "count_ok",
                }
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "viable trajectory count unit test",
            },
        }
    )
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "count_ok"
    assert result["observed"]["count_profile"] == [2, 2, 2, 2]
    assert result["observed"]["final_count"] == 2
    assert result["observed"]["nonempty_at_horizon"] is True


def test_viable_trajectory_count_rejects_wrong_branching_profile() -> None:
    model = load_model(
        {
            "model_id": "inline_viable_trajectory_count_branching_control",
            "domains": {"state": ["left", "right"]},
            "predicates": {"safe": ["left", "right"]},
            "relations": {
                "next": {
                    "domains": ["state", "state"],
                    "tuples": [
                        ["left", "left"],
                        ["left", "right"],
                        ["right", "left"],
                        ["right", "right"],
                    ],
                }
            },
            "audits": [
                {
                    "id": "complete_two_state_graph_is_not_flat",
                    "kind": "viable_trajectory_count",
                    "transition": "next",
                    "safety": "safe",
                    "horizon": 2,
                    "expected_count_profile": [2, 2, 2],
                    "expected_final_count": 2,
                    "expect": "not_count_ok",
                }
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "viable trajectory count negative unit test",
            },
        }
    )
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "not_count_ok"
    assert result["observed"]["count_profile"] == [2, 4, 8]
    assert result["observed"]["final_count"] == 8
    assert result["observed"]["profile_matches"] is False
    assert result["observed"]["final_count_matches"] is False


def test_safe_prefix_count_can_overstate_extendable_continuation() -> None:
    model = load_model(
        {
            "model_id": "inline_dead_end_branching_prefix_count",
            "domains": {"state": ["start", "dead_a", "dead_b"]},
            "predicates": {
                "safe": ["start", "dead_a", "dead_b"],
                "start_only": ["start"],
            },
            "relations": {
                "next": {
                    "domains": ["state", "state"],
                    "tuples": [["start", "dead_a"], ["start", "dead_b"]],
                }
            },
            "audits": [
                {
                    "id": "dead_end_branching_has_safe_prefixes",
                    "kind": "safe_prefix_count",
                    "transition": "next",
                    "safety": "safe",
                    "start_predicate": "start_only",
                    "horizon": 2,
                    "expected_count_profile": [1, 2, 0],
                    "expected_final_count": 0,
                    "expect": "count_ok",
                },
                {
                    "id": "dead_end_branching_has_no_extendable_prefixes",
                    "kind": "extendable_safe_prefix_count",
                    "transition": "next",
                    "safety": "safe",
                    "start_predicate": "start_only",
                    "horizon": 2,
                    "expected_count_profile": [0, 0, 0],
                    "expected_final_count": 0,
                    "expect": "count_ok",
                },
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "safe prefix versus extendable prefix unit test",
            },
        }
    )
    results = {result.audit_id: result.as_dict() for result in run_declared_audits(model)}

    safe_prefix = results["dead_end_branching_has_safe_prefixes"]
    extendable = results["dead_end_branching_has_no_extendable_prefixes"]

    assert safe_prefix["passed"] is True
    assert safe_prefix["observed"]["count_kind"] == "safe_prefix"
    assert safe_prefix["observed"]["count_profile"] == [1, 2, 0]

    assert extendable["passed"] is True
    assert extendable["observed"]["count_kind"] == "extendable_safe_prefix"
    assert extendable["observed"]["safe_prefix_count_profile"] == [1, 2, 0]
    assert extendable["observed"]["count_profile"] == [0, 0, 0]
    assert extendable["observed"]["viability_kernel"] == []


def test_observed_extendable_word_count_collapses_unobserved_branching() -> None:
    model = load_model(
        {
            "model_id": "inline_observed_word_count_collapses_branching",
            "domains": {
                "state": ["left", "right"],
                "observation": ["same"],
            },
            "predicates": {
                "safe": {"domain": "state", "members": ["left", "right"]},
            },
            "relations": {
                "next": {
                    "domains": ["state", "state"],
                    "tuples": [
                        ["left", "left"],
                        ["left", "right"],
                        ["right", "left"],
                        ["right", "right"],
                    ],
                },
            },
            "functions": {
                "constant_observation": {
                    "domain": "state",
                    "codomain": "observation",
                    "mapping": {
                        "left": "same",
                        "right": "same",
                    },
                },
            },
            "audits": [
                {
                    "id": "branching_collapses_to_one_observed_word",
                    "kind": "observed_extendable_safe_word_count",
                    "transition": "next",
                    "safety": "safe",
                    "observation": "constant_observation",
                    "horizon": 2,
                    "expected_count_profile": [1, 1, 1],
                    "expect": "count_ok",
                }
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "observed word count branch-collapse unit test",
            },
        }
    )
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "count_ok"
    assert result["observed"]["count_kind"] == "observed_extendable_safe_word"
    assert result["observed"]["safe_prefix_count_profile"] == [2, 4, 8]
    assert result["observed"]["extendable_safe_prefix_count_profile"] == [2, 4, 8]
    assert result["observed"]["count_profile"] == [1, 1, 1]
    assert result["observed"]["observed_words_by_horizon"] == [
        [["same"]],
        [["same", "same"]],
        [["same", "same", "same"]],
    ]


def test_observed_extendable_word_count_keeps_labeled_cycle_words() -> None:
    model = load_model(
        {
            "model_id": "inline_observed_word_count_labeled_cycle",
            "domains": {
                "state": ["left", "right"],
                "observation": ["L", "R"],
            },
            "predicates": {
                "safe": {"domain": "state", "members": ["left", "right"]},
            },
            "relations": {
                "next": {
                    "domains": ["state", "state"],
                    "tuples": [["left", "right"], ["right", "left"]],
                },
            },
            "functions": {
                "role_observation": {
                    "domain": "state",
                    "codomain": "observation",
                    "mapping": {
                        "left": "L",
                        "right": "R",
                    },
                },
            },
            "audits": [
                {
                    "id": "labeled_cycle_keeps_two_observed_words",
                    "kind": "observed_extendable_safe_word_count",
                    "transition": "next",
                    "safety": "safe",
                    "observation": "role_observation",
                    "horizon": 2,
                    "expected_count_profile": [2, 2, 2],
                    "expect": "count_ok",
                }
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "observed word count labeled-cycle unit test",
            },
        }
    )
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["observed"]["safe_prefix_count_profile"] == [2, 2, 2]
    assert result["observed"]["extendable_safe_prefix_count_profile"] == [2, 2, 2]
    assert result["observed"]["count_profile"] == [2, 2, 2]
    assert result["observed"]["observed_words_by_horizon"] == [
        [["L"], ["R"]],
        [["L", "R"], ["R", "L"]],
        [["L", "R", "L"], ["R", "L", "R"]],
    ]


def test_viable_trajectory_count_comparison_detects_phantom_count_inflation() -> None:
    model = load_model(
        {
            "model_id": "inline_viable_count_inflation",
            "domains": {
                "state": ["left", "right"],
                "label": ["left", "right"],
            },
            "predicates": {
                "exact_safe": {"domain": "state", "members": ["left", "right"]},
                "abstract_safe": {"domain": "label", "members": ["left", "right"]},
            },
            "relations": {
                "exact_next": {
                    "domains": ["state", "state"],
                    "tuples": [["left", "right"], ["right", "left"]],
                },
                "abstract_next": {
                    "domains": ["label", "label"],
                    "tuples": [
                        ["left", "left"],
                        ["left", "right"],
                        ["right", "left"],
                        ["right", "right"],
                    ],
                },
            },
            "functions": {
                "identity_presentation": {
                    "domain": "state",
                    "codomain": "label",
                    "mapping": {"left": "left", "right": "right"},
                }
            },
            "audits": [
                {
                    "id": "phantom_abstract_edges_inflate_viable_counts",
                    "kind": "viable_trajectory_count_comparison",
                    "exact_transition": "exact_next",
                    "exact_safety": "exact_safe",
                    "presentation": "identity_presentation",
                    "abstract_transition": "abstract_next",
                    "abstract_safety": "abstract_safe",
                    "horizon": 2,
                    "expect": "distorted",
                }
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "viable trajectory count inflation unit test",
            },
        }
    )
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "distorted"
    assert result["observed"]["equivariant"] is False
    assert result["observed"]["inflates"] is True
    assert result["observed"]["hides"] is False
    assert result["observed"]["exact_count_profile"] == [2, 2, 2]
    assert result["observed"]["abstract_count_profile"] == [2, 4, 8]
    assert result["observed"]["count_profile_delta"] == [0, 2, 6]
    assert result["observed"]["dynamics"]["phantom_abstract_edges"] == [
        ("left", "left"),
        ("right", "right"),
    ]


def test_viable_trajectory_count_comparison_detects_missing_edge_hiding() -> None:
    model = load_model(
        {
            "model_id": "inline_viable_count_hiding",
            "domains": {
                "state": ["left", "right"],
                "label": ["left", "right"],
            },
            "predicates": {
                "exact_safe": {"domain": "state", "members": ["left", "right"]},
                "abstract_safe": {"domain": "label", "members": ["left", "right"]},
            },
            "relations": {
                "exact_next": {
                    "domains": ["state", "state"],
                    "tuples": [
                        ["left", "left"],
                        ["left", "right"],
                        ["right", "left"],
                        ["right", "right"],
                    ],
                },
                "abstract_next": {
                    "domains": ["label", "label"],
                    "tuples": [["left", "right"], ["right", "left"]],
                },
            },
            "functions": {
                "identity_presentation": {
                    "domain": "state",
                    "codomain": "label",
                    "mapping": {"left": "left", "right": "right"},
                }
            },
            "audits": [
                {
                    "id": "missing_abstract_edges_hide_viable_counts",
                    "kind": "viable_trajectory_count_comparison",
                    "exact_transition": "exact_next",
                    "exact_safety": "exact_safe",
                    "presentation": "identity_presentation",
                    "abstract_transition": "abstract_next",
                    "abstract_safety": "abstract_safe",
                    "horizon": 2,
                    "expect": "distorted",
                }
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "viable trajectory count hiding unit test",
            },
        }
    )
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "distorted"
    assert result["observed"]["equivariant"] is False
    assert result["observed"]["inflates"] is False
    assert result["observed"]["hides"] is True
    assert result["observed"]["exact_count_profile"] == [2, 4, 8]
    assert result["observed"]["abstract_count_profile"] == [2, 2, 2]
    assert result["observed"]["count_profile_delta"] == [0, -2, -6]
    assert result["observed"]["dynamics"]["missing_projected_edges"] == [
        ("left", "left"),
        ("right", "right"),
    ]


def test_presentation_fact_closure_audit_checks_visible_pairs_and_targets() -> None:
    model = load_model(
        {
            "model_id": "inline_presentation_fact_closure",
            "carrier": ["left", "right"],
            "predicates": {
                "left_target": ["left"],
                "right_target": ["right"],
                "constant_target": ["left", "right"],
                "empty_target": [],
            },
            "functions": {
                "identity": {
                    "left": "left",
                    "right": "right",
                },
                "constant": {
                    "left": "merged",
                    "right": "merged",
                },
            },
            "audits": [
                {
                    "id": "exact_only_common_facts",
                    "kind": "presentation_fact_closure",
                    "presentations": ["identity"],
                    "target_predicates": ["left_target", "constant_target"],
                    "seed_target_predicates": ["constant_target"],
                    "expected_common_visible_pairs": [["left", "right"], ["right", "left"]],
                    "expected_common_target_predicates": ["left_target", "constant_target"],
                    "expected_surplus_target_predicates": ["left_target"],
                    "expected_nonconstant_surplus_target_predicates": ["left_target"],
                    "expect": "closure_ok",
                },
                {
                    "id": "constant_erases_left_target",
                    "kind": "presentation_fact_closure",
                    "presentations": ["identity", "constant"],
                    "target_predicates": ["left_target", "constant_target"],
                    "seed_target_predicates": ["constant_target"],
                    "expected_absent_visible_pairs": [["left", "right"], ["right", "left"]],
                    "expected_absent_target_predicates": ["left_target"],
                    "expected_common_target_predicates": ["constant_target"],
                    "expected_absent_surplus_target_predicates": ["left_target"],
                    "expected_absent_nonconstant_surplus_target_predicates": ["left_target"],
                    "expect": "closure_ok",
                },
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "presentation fact closure unit test",
            },
        }
    )
    exact, erasing = [result.as_dict() for result in run_declared_audits(model)]

    assert exact["passed"] is True
    assert exact["finding"] == "closure_ok"
    assert exact["observed"]["common_visible_pair_count"] == 2
    assert exact["observed"]["common_target_predicates"] == [
        "constant_target",
        "left_target",
    ]
    assert exact["observed"]["seed_target_predicates"] == ["constant_target"]
    assert exact["observed"]["surplus_common_target_predicates"] == ["left_target"]
    assert exact["observed"]["nonconstant_surplus_target_predicates"] == ["left_target"]
    assert exact["observed"]["surplus_scope"] == "family_relative"
    assert exact["observed"]["family_relative_surplus_target_predicates"] == [
        "left_target"
    ]
    assert erasing["passed"] is True
    assert erasing["finding"] == "closure_ok"
    assert erasing["observed"]["common_visible_pair_count"] == 0
    assert erasing["observed"]["common_target_predicates"] == ["constant_target"]
    assert erasing["observed"]["surplus_common_target_predicates"] == []
    assert erasing["observed"]["nonconstant_surplus_target_predicates"] == []


def test_presentation_fact_derive_closure_generates_from_seed_constraints() -> None:
    model = load_model(
        {
            "model_id": "inline_presentation_fact_derive_closure",
            "carrier": ["left", "right"],
            "predicates": {
                "left_target": ["left"],
                "right_target": ["right"],
                "constant_target": ["left", "right"],
                "empty_target": [],
            },
            "audits": [
                {
                    "id": "derive_from_left_seed",
                    "kind": "presentation_fact_derive_closure",
                    "seed_target_predicates": ["left_target"],
                    "expected_closure_visible_pairs": [["left", "right"], ["right", "left"]],
                    "expected_surplus_visible_pairs": [["left", "right"], ["right", "left"]],
                    "expected_closure_target_facts": [
                        "pred:{}",
                        "pred:{left}",
                        "pred:{right}",
                        "pred:{left,right}",
                    ],
                    "expected_nonconstant_surplus_target_facts": ["pred:{right}"],
                    "expected_known_closure_target_predicates": [
                        "constant_target",
                        "empty_target",
                        "left_target",
                        "right_target",
                    ],
                    "expected_known_surplus_target_predicates": [
                        "constant_target",
                        "empty_target",
                        "right_target",
                    ],
                    "expect": "derive_ok",
                },
                {
                    "id": "constant_seed_derives_no_nonconstant_fact",
                    "kind": "presentation_fact_derive_closure",
                    "seed_target_predicates": ["constant_target"],
                    "expected_absent_closure_visible_pairs": [
                        ["left", "right"],
                        ["right", "left"],
                    ],
                    "expected_absent_closure_target_facts": [
                        "pred:{left}",
                        "pred:{right}",
                    ],
                    "expected_absent_nonconstant_surplus_target_facts": [
                        "pred:{left}",
                        "pred:{right}",
                    ],
                    "expect": "derive_ok",
                },
            ],
            "provenance": {
                "declared_before_run": True,
                "source": "inline test",
                "claim_boundary": "presentation derive closure unit test",
            },
        }
    )
    left_seed, constant_seed = [result.as_dict() for result in run_declared_audits(model)]

    assert left_seed["passed"] is True
    assert left_seed["finding"] == "derive_ok"
    assert left_seed["observed"]["closure_mode"] == (
        "generated_universe_admissible_presentations"
    )
    assert left_seed["observed"]["presentation_universe_count"] == 2
    assert left_seed["observed"]["admissible_presentation_count"] == 1
    assert left_seed["observed"]["seed_target_facts"] == ["pred:{left}"]
    assert left_seed["observed"]["closure_visible_pairs"] == [
        ("left", "right"),
        ("right", "left"),
    ]
    assert left_seed["observed"]["nonconstant_surplus_target_facts"] == ["pred:{right}"]

    assert constant_seed["passed"] is True
    assert constant_seed["finding"] == "derive_ok"
    assert constant_seed["observed"]["presentation_universe_count"] == 2
    assert constant_seed["observed"]["admissible_presentation_count"] == 2
    assert constant_seed["observed"]["closure_visible_pairs"] == []
    assert constant_seed["observed"]["nonconstant_surplus_target_facts"] == []


def test_carrier_transfer_fixture_accepts_declared_transfer_contract() -> None:
    model = load_model_path(FIXTURES / "carrier_transfer_pass.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "transferred"
    assert result["observed"]["source_certified"] is True
    assert result["observed"]["target_certified"] is True
    assert result["observed"]["endpoint_correspondence"] is True
    assert result["observed"]["correspondence_total_on_source_carrier"] is True


def test_carrier_transfer_negative_fixture_rejects_missing_target_return() -> None:
    model = load_model_path(FIXTURES / "carrier_transfer_fail_missing_return.json")
    [result] = [result.as_dict() for result in run_declared_audits(model)]

    assert result["passed"] is True
    assert result["finding"] == "not_transferred"
    assert result["observed"]["source_certified"] is True
    assert result["observed"]["target_certified"] is False
    assert result["observed"]["endpoint_correspondence"] is True
    assert result["observed"]["target"]["mutually_reachable"] is False


def test_cli_retains_digest_provenance_audits_and_summary(tmp_path: Path) -> None:
    out_dir = tmp_path / "adapter_smoke"
    summary = run_model_file(FIXTURES / "sound_pass.json", out_dir)

    assert summary["all_passed"] is True
    assert summary["audit_count"] == 3
    assert (out_dir / "model_digest.txt").exists()
    assert (out_dir / "provenance_check.json").exists()
    assert (out_dir / "audit_results.json").exists()
    assert (out_dir / "summary.json").exists()


def test_provenance_requires_declaration_before_run() -> None:
    model = load_model(
        {
            "model_id": "missing_provenance_fixture",
            "carrier": ["x"],
            "provenance": {
                "declared_before_run": False,
                "source": "inline test",
                "claim_boundary": "negative provenance test",
            },
        }
    )

    assert validate_provenance(model)["complete"] is False


def test_schema_rejects_relation_elements_outside_declared_domain() -> None:
    with pytest.raises(SchemaError, match="not in domain"):
        load_model(
            {
                "carrier": ["x"],
                "relations": {
                    "bad_edge": [["x", "y"]],
                },
                "provenance": {
                    "declared_before_run": True,
                    "source": "inline test",
                    "claim_boundary": "negative schema test",
                },
            }
        )
