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
    assert result["observed"]["recoverability_changed"] is False
    assert result["observed"]["successful_decoders_changed"] is False
    assert result["observed"]["target_recoverable"] is False
    assert result["observed"]["scrambled_recoverable"] is False


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
                "constant_target": ["left", "right"],
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
    assert erasing["passed"] is True
    assert erasing["finding"] == "closure_ok"
    assert erasing["observed"]["common_visible_pair_count"] == 0
    assert erasing["observed"]["common_target_predicates"] == ["constant_target"]
    assert erasing["observed"]["surplus_common_target_predicates"] == []
    assert erasing["observed"]["nonconstant_surplus_target_predicates"] == []


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
