"""Deterministic generated cases for finite relational adapter hardening."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations, product
import json
from typing import Any

from omega.adapters.finite_relational.audits import AuditResult, run_declared_audits
from omega.adapters.finite_relational.derived_graph import compile_derived_graph
from omega.adapters.finite_relational.facts import Pair, reachable_pairs
from omega.adapters.finite_relational.finite_grid import compile_finite_grid
from omega.adapters.finite_relational.graph_pair_transfer import (
    compile_graph_pair_transfer_source,
)
from omega.adapters.finite_relational.model import load_model, model_digest


@dataclass(frozen=True)
class GeneratedAdapterCase:
    """A generated adapter case plus the compiled model and audit results."""

    case_id: str
    source_format: str
    source: dict[str, Any]
    compiled_model: dict[str, Any]
    audit_results: tuple[AuditResult, ...]

    @property
    def all_passed(self) -> bool:
        return all(result.passed for result in self.audit_results)

    def summary(self) -> dict[str, object]:
        model = load_model(self.compiled_model)
        return {
            "case_id": self.case_id,
            "source_format": self.source_format,
            "compiled_model_id": model.model_id,
            "audit_count": len(self.audit_results),
            "passed_count": sum(1 for result in self.audit_results if result.passed),
            "all_passed": self.all_passed,
            "source_digest": digest_json(self.source),
            "compiled_model_digest": model_digest(model),
            "findings": [result.finding for result in self.audit_results],
        }


def generate_adversarial_cases() -> tuple[GeneratedAdapterCase, ...]:
    """Generate a small deterministic suite of adapter hardening cases."""

    return (
        _generated_phantom_reachability_case(),
        _generated_hidden_reachability_loss_case(),
        _generated_proxy_nonfactorization_case(),
        _generated_derived_graph_asymmetry_case(),
        _generated_derived_graph_carrier_case(),
        _generated_presentation_fact_closure_case(),
        _generated_presentation_fact_derive_closure_case(),
        _generated_presentation_fact_derive_closure_constant_control_case(),
        _generated_reachability_fact_closure_case(),
        _generated_viability_fact_closure_case(),
        _generated_recovery_fact_closure_case(),
        _generated_target_scramble_sensitivity_case(),
        _generated_decorative_target_scramble_control_case(),
        _generated_target_scramble_capacity_sensitivity_case(),
        _generated_target_scramble_capacity_label_swap_control_case(),
        _generated_dynamic_equivariance_case(),
        _generated_dynamic_non_equivariance_case(),
        _generated_edge_exact_path_lifting_failure_case(),
        _generated_viable_trajectory_count_cycle_case(),
        _generated_viable_trajectory_count_branching_case(),
        _generated_dead_end_safe_prefix_case(),
        _generated_observed_word_count_collapses_branching_case(),
        _generated_observed_word_count_labeled_cycle_case(),
        _generated_viable_count_inflation_case(),
        _generated_viable_count_hiding_case(),
        _generated_stale_reflected_fact_closure_case(),
        _generated_multi_presentation_fact_closure_case(),
        _generated_crosscutting_presentation_closure_case(),
        _generated_graph_pair_transfer_case(),
        _generated_graph_pair_transfer_missing_return_case(),
        _generated_transport_fact_closure_case(),
        _generated_failed_transport_fact_closure_case(),
        _generated_finite_grid_asymmetry_case(),
    )


def digest_json(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _generated_phantom_reachability_case() -> GeneratedAdapterCase:
    states = ("a", "b", "c")
    source = "a"
    target = "c"
    for abstract_edges in _edge_subsets(states):
        if (source, target) in abstract_edges:
            continue
        if (source, target) not in reachable_pairs(set(states), set(abstract_edges)):
            continue
        for exact_edges in _edge_subsets(states):
            if (source, target) in reachable_pairs(set(states), set(exact_edges)):
                continue
            model = _transition_audit_model(
                model_id="generated_phantom_reachability",
                states=states,
                relations={
                    "exact_next": exact_edges,
                    "abstract_next": abstract_edges,
                },
                audit={
                    "id": "generated_abstract_path_without_exact_path",
                    "kind": "phantom_reachability",
                    "exact_transition": "exact_next",
                    "abstract_transition": "abstract_next",
                    "source": source,
                    "target": target,
                    "expect": "phantom",
                },
                claim_boundary=(
                    "Generated finite relational case: abstract reachability reports a path "
                    "not present in the exact transition relation."
                ),
            )
            return _validated_ir_case("generated_phantom_reachability", model)
    raise AssertionError("failed to generate phantom reachability case")


def _generated_hidden_reachability_loss_case() -> GeneratedAdapterCase:
    states = ("a", "b", "c")
    source = "a"
    target = "c"
    for before_edges in _edge_subsets(states):
        if (source, target) in before_edges:
            continue
        if (source, target) not in reachable_pairs(set(states), set(before_edges)):
            continue
        for after_edges in _edge_subsets(states):
            if (source, target) in reachable_pairs(set(states), set(after_edges)):
                continue
            model = _transition_audit_model(
                model_id="generated_hidden_reachability_loss",
                states=states,
                relations={
                    "before_next": before_edges,
                    "after_next": after_edges,
                    "abstract_next": before_edges,
                },
                audit={
                    "id": "generated_abstract_still_reports_lost_path",
                    "kind": "hidden_reachability_loss",
                    "before_transition": "before_next",
                    "after_transition": "after_next",
                    "abstract_transition": "abstract_next",
                    "source": source,
                    "target": target,
                    "expect": "hidden_loss",
                },
                claim_boundary=(
                    "Generated finite relational case: changed exact dynamics lose a path "
                    "that the stale abstract transition still reports."
                ),
            )
            return _validated_ir_case("generated_hidden_reachability_loss", model)
    raise AssertionError("failed to generate hidden reachability loss case")


def _generated_proxy_nonfactorization_case() -> GeneratedAdapterCase:
    states = ("left", "right")
    labels = ("same", "left", "right")
    for left_label, right_label in product(labels, labels):
        summary = {"left": left_label, "right": right_label}
        for target_members in (["left"], ["right"]):
            same_summary = summary["left"] == summary["right"]
            target_differs = ("left" in target_members) != ("right" in target_members)
            if not same_summary or not target_differs:
                continue
            model = {
                "model_id": "generated_proxy_nonfactorization",
                "schema_version": "0.1.0",
                "carrier": list(states),
                "predicates": {"target": target_members},
                "functions": {"summary": summary},
                "audits": [
                    {
                        "id": "generated_same_summary_different_target",
                        "kind": "nonfactorization",
                        "summary": "summary",
                        "target_predicate": "target",
                        "expect": "witness",
                    }
                ],
                "provenance": _generated_provenance(
                    "Generated finite relational case: same summary label, different target value."
                ),
            }
            return _validated_ir_case("generated_proxy_nonfactorization", model)
    raise AssertionError("failed to generate proxy nonfactorization case")


def _generated_derived_graph_asymmetry_case() -> GeneratedAdapterCase:
    nodes = ("source", "sink")
    observation_values = ("red", "blue")
    for edges in _edge_subsets(nodes):
        for source_color, sink_color in product(observation_values, observation_values):
            if source_color == sink_color:
                continue
            graph_source = {
                "model_id": "generated_derived_graph_asymmetry",
                "nodes": list(nodes),
                "edges": [list(edge) for edge in edges],
                "observations": {
                    "color": {
                        "source": source_color,
                        "sink": sink_color,
                    }
                },
                "presentations": {
                    "identity": {
                        "source": "source",
                        "sink": "sink",
                    },
                    "constant": {
                        "source": "merged",
                        "sink": "merged",
                    },
                },
                "presentation_expectations": {
                    "identity": "sound",
                    "constant": "unsound",
                },
                "safety": "all",
                "provenance": _generated_provenance(
                    "Generated derived graph case: strict one-way edge plus observation "
                    "difference earns Alpha-like asymmetry."
                ),
            }
            compiled = compile_derived_graph(graph_source)
            model = load_model(compiled)
            if model.relation_tuples("primitive_asym"):
                return _validated_compiled_case(
                    "generated_derived_graph_asymmetry",
                    "derived_graph",
                    graph_source,
                    compiled,
                )
    raise AssertionError("failed to generate derived graph asymmetry case")


def _generated_derived_graph_carrier_case() -> GeneratedAdapterCase:
    nodes = ("left", "right")
    observation_values = ("red", "blue")
    for edges in _edge_subsets(nodes):
        for left_color, right_color in product(observation_values, observation_values):
            if left_color == right_color:
                continue
            graph_source = {
                "model_id": "generated_derived_graph_carrier",
                "nodes": list(nodes),
                "edges": [list(edge) for edge in edges],
                "observations": {
                    "color": {
                        "left": left_color,
                        "right": right_color,
                    }
                },
                "presentations": {
                    "identity": {
                        "left": "left",
                        "right": "right",
                    }
                },
                "presentation_expectations": {"identity": "sound"},
                "safety": "all",
                "provenance": _generated_provenance(
                    "Generated derived graph case: mutually reachable separated endpoints "
                    "earn a carrier certificate."
                ),
            }
            compiled = compile_derived_graph(graph_source)
            model = load_model(compiled)
            if any(name.startswith("carrier_") for name in model.predicates):
                return _validated_compiled_case(
                    "generated_derived_graph_carrier",
                    "derived_graph",
                    graph_source,
                    compiled,
                )
    raise AssertionError("failed to generate derived graph carrier case")


def _generated_presentation_fact_closure_case() -> GeneratedAdapterCase:
    graph_source = {
        "model_id": "generated_presentation_fact_closure",
        "nodes": ["left", "right"],
        "edges": [["left", "right"], ["right", "left"]],
        "observations": {
            "color": {
                "left": "red",
                "right": "blue",
            }
        },
        "presentations": {
            "identity": {
                "left": "left",
                "right": "right",
            },
            "constant": {
                "left": "merged",
                "right": "merged",
            },
        },
        "presentation_expectations": {
            "identity": "sound",
            "constant": "unsound",
        },
        "safety": "all",
        "provenance": _generated_provenance(
            "Generated derived graph case: carrier endpoint visibility survives "
            "the exact presentation and disappears when the constant presentation "
            "is admitted."
        ),
    }
    compiled = compile_derived_graph(graph_source)
    carrier_audits = [
        audit for audit in compiled["audits"] if audit.get("kind") == "carrier_certificate"
    ]
    if not carrier_audits:
        raise AssertionError("presentation fact closure case generated no carrier audit")
    left = str(carrier_audits[0]["left"])
    right = str(carrier_audits[0]["right"])
    compiled["audits"].extend(
        [
            {
                "id": "generated_exact_presentation_keeps_carrier_pair_visible",
                "kind": "presentation_fact_closure",
                "presentations": ["identity"],
                "expected_common_visible_pairs": [[left, right], [right, left]],
                "expect": "closure_ok",
            },
            {
                "id": "generated_constant_presentation_erases_carrier_pair_visibility",
                "kind": "presentation_fact_closure",
                "presentations": ["identity", "constant"],
                "expected_absent_visible_pairs": [[left, right], [right, left]],
                "expect": "closure_ok",
            },
        ]
    )
    return _validated_compiled_case(
        "generated_presentation_fact_closure",
        "derived_graph",
        graph_source,
        compiled,
    )


def _generated_presentation_fact_derive_closure_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_presentation_fact_derive_closure",
        "schema_version": "0.1.0",
        "carrier": ["left", "right"],
        "predicates": {
            "left_target": ["left"],
            "right_target": ["right"],
            "all_states": ["left", "right"],
            "empty_target": [],
        },
        "audits": [
            {
                "id": "generated_left_seed_forces_complement_and_visibility",
                "kind": "presentation_fact_derive_closure",
                "seed_target_predicates": ["left_target"],
                "expected_closure_visible_pairs": [["left", "right"], ["right", "left"]],
                "expected_surplus_visible_pairs": [["left", "right"], ["right", "left"]],
                "expected_nonconstant_surplus_target_facts": ["pred:{right}"],
                "expected_known_surplus_target_predicates": [
                    "all_states",
                    "empty_target",
                    "right_target",
                ],
                "expect": "derive_ok",
            }
        ],
        "provenance": _generated_provenance(
            "Generated finite derive-mode closure case: a nonconstant seed "
            "predicate filters the generated presentation universe and forces "
            "additional visible-pair and complement facts."
        ),
    }
    return _validated_ir_case("generated_presentation_fact_derive_closure", model)


def _generated_presentation_fact_derive_closure_constant_control_case() -> (
    GeneratedAdapterCase
):
    model = {
        "model_id": "generated_presentation_fact_derive_closure_constant_control",
        "schema_version": "0.1.0",
        "carrier": ["left", "right"],
        "predicates": {
            "left_target": ["left"],
            "right_target": ["right"],
            "all_states": ["left", "right"],
            "empty_target": [],
        },
        "audits": [
            {
                "id": "generated_constant_seed_forces_no_nonconstant_fact",
                "kind": "presentation_fact_derive_closure",
                "seed_target_predicates": ["all_states"],
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
            }
        ],
        "provenance": _generated_provenance(
            "Generated finite derive-mode closure control: a constant seed "
            "admits every generated presentation, so only constant predicate "
            "facts survive."
        ),
    }
    return _validated_ir_case(
        "generated_presentation_fact_derive_closure_constant_control",
        model,
    )


def _generated_reachability_fact_closure_case() -> GeneratedAdapterCase:
    states = ("start", "goal", "dead")
    edges = (("start", "goal"),)
    target = "goal"
    reachable = {
        source
        for source in states
        if (source, target) in reachable_pairs(set(states), set(edges))
    }
    model = {
        "model_id": "generated_reachability_fact_closure",
        "schema_version": "0.1.0",
        "carrier": list(states),
        "relations": {"next": [list(edge) for edge in edges]},
        "predicates": {
            "can_reach_goal": sorted(reachable),
            "all_states": list(states),
        },
        "functions": {
            "reach_status": {
                state: ("can_reach_goal" if state in reachable else "cannot_reach_goal")
                for state in states
            },
            "constant_status": {state: "merged" for state in states},
        },
        "audits": _target_closure_audits(
            exact_presentation="reach_status",
            erasing_presentation="constant_status",
            target_predicate="can_reach_goal",
            constant_predicate="all_states",
            exact_audit_id="generated_exact_reach_status_preserves_reachability_fact",
            erasing_audit_id="generated_constant_status_erases_reachability_fact",
        ),
        "provenance": _generated_provenance(
            "Generated finite relational case: reachability-to-goal status is "
            "derived from the transition relation, then erased by a constant "
            "presentation."
        ),
    }
    return _validated_ir_case("generated_reachability_fact_closure", model)


def _generated_viability_fact_closure_case() -> GeneratedAdapterCase:
    states = ("loop", "dead")
    edges = (("loop", "loop"),)
    safe = set(states)
    viable = {state for state in states if state in safe and (state, state) in set(edges)}
    model = {
        "model_id": "generated_viability_fact_closure",
        "schema_version": "0.1.0",
        "carrier": list(states),
        "relations": {"next": [list(edge) for edge in edges]},
        "predicates": {
            "safe": sorted(safe),
            "self_sustaining_safe": sorted(viable),
            "all_states": list(states),
        },
        "functions": {
            "viability_status": {
                state: ("self_sustaining_safe" if state in viable else "not_self_sustaining")
                for state in states
            },
            "constant_status": {state: "merged" for state in states},
        },
        "audits": _target_closure_audits(
            exact_presentation="viability_status",
            erasing_presentation="constant_status",
            target_predicate="self_sustaining_safe",
            constant_predicate="all_states",
            exact_audit_id="generated_exact_viability_status_preserves_viability_fact",
            erasing_audit_id="generated_constant_status_erases_viability_fact",
        ),
        "provenance": _generated_provenance(
            "Generated finite relational case: a tiny self-sustaining safe "
            "status is derived from transition and safety structure, then "
            "erased by a constant presentation."
        ),
    }
    return _validated_ir_case("generated_viability_fact_closure", model)


def _generated_recovery_fact_closure_case() -> GeneratedAdapterCase:
    states = ("left", "right")
    model = {
        "model_id": "generated_recovery_fact_closure",
        "schema_version": "0.1.0",
        "domains": {
            "state": list(states),
            "observation": ["left_obs", "right_obs", "merged"],
            "truth": ["true", "false"],
        },
        "predicates": {
            "bit_target": {
                "domain": "state",
                "members": ["left"],
            },
            "all_states": {
                "domain": "state",
                "members": list(states),
            },
        },
        "functions": {
            "exact_observation": {
                "domain": "state",
                "codomain": "observation",
                "mapping": {
                    "left": "left_obs",
                    "right": "right_obs",
                },
            },
            "constant_observation": {
                "domain": "state",
                "codomain": "observation",
                "mapping": {
                    "left": "merged",
                    "right": "merged",
                },
            },
            "exact_decoder": {
                "domain": "observation",
                "codomain": "truth",
                "mapping": {
                    "left_obs": "true",
                    "right_obs": "false",
                    "merged": "true",
                },
            },
            "always_true": {
                "domain": "observation",
                "codomain": "truth",
                "mapping": {
                    "left_obs": "true",
                    "right_obs": "true",
                    "merged": "true",
                },
            },
            "always_false": {
                "domain": "observation",
                "codomain": "truth",
                "mapping": {
                    "left_obs": "false",
                    "right_obs": "false",
                    "merged": "false",
                },
            },
        },
        "audits": [
            {
                "id": "generated_exact_observation_recovers_bit_target",
                "kind": "bounded_recovery",
                "observation": "exact_observation",
                "target_predicate": "bit_target",
                "decoders": ["exact_decoder", "always_true", "always_false"],
                "expect": "recoverable",
            },
            {
                "id": "generated_constant_observation_does_not_recover_bit_target",
                "kind": "bounded_recovery",
                "observation": "constant_observation",
                "target_predicate": "bit_target",
                "decoders": ["exact_decoder", "always_true", "always_false"],
                "expect": "not_recoverable",
            },
            *_target_closure_audits(
                exact_presentation="exact_observation",
                erasing_presentation="constant_observation",
                target_predicate="bit_target",
                constant_predicate="all_states",
                exact_audit_id="generated_exact_observation_preserves_recovery_fact",
                erasing_audit_id="generated_constant_observation_erases_recovery_fact",
            ),
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: exact observation supports a "
            "declared bounded decoder for the bit target, while a constant "
            "observation cannot recover it and removes it from common target "
            "facts."
        ),
    }
    return _validated_ir_case("generated_recovery_fact_closure", model)


def _generated_target_scramble_sensitivity_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_target_scramble_sensitivity",
        "schema_version": "0.1.0",
        "carrier": ["left", "right"],
        "domains": {
            "state": ["left", "right"],
            "observation": ["red", "blue"],
            "truth": ["false", "true"],
        },
        "predicates": {
            "left_target": {"domain": "state", "members": ["left"]},
            "right_scramble": {"domain": "state", "members": ["right"]},
        },
        "functions": {
            "color_observation": {
                "domain": "state",
                "codomain": "observation",
                "mapping": {
                    "left": "red",
                    "right": "blue",
                },
            },
            "left_decoder": {
                "domain": "observation",
                "codomain": "truth",
                "mapping": {
                    "red": "true",
                    "blue": "false",
                },
            },
        },
        "audits": [
            {
                "id": "generated_declared_target_changes_under_scramble",
                "kind": "target_scramble_sensitivity",
                "observation": "color_observation",
                "target_predicate": "left_target",
                "scrambled_predicate": "right_scramble",
                "decoders": ["left_decoder"],
                "expect": "sensitive",
            }
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: the declared target has "
            "operational recovery bite because replacing it with a scrambled "
            "target changes exact recoverability under the declared observation "
            "and decoder family."
        ),
    }
    return _validated_ir_case("generated_target_scramble_sensitivity", model)


def _generated_decorative_target_scramble_control_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_decorative_target_scramble_control",
        "schema_version": "0.1.0",
        "carrier": ["left", "right"],
        "domains": {
            "state": ["left", "right"],
            "observation": ["merged"],
            "truth": ["false", "true"],
        },
        "predicates": {
            "left_target": {"domain": "state", "members": ["left"]},
            "right_scramble": {"domain": "state", "members": ["right"]},
        },
        "functions": {
            "constant_observation": {
                "domain": "state",
                "codomain": "observation",
                "mapping": {
                    "left": "merged",
                    "right": "merged",
                },
            },
            "always_false_decoder": {
                "domain": "observation",
                "codomain": "truth",
                "mapping": {
                    "merged": "false",
                },
            },
        },
        "audits": [
            {
                "id": "generated_decorative_target_unchanged_under_scramble",
                "kind": "target_scramble_sensitivity",
                "observation": "constant_observation",
                "target_predicate": "left_target",
                "scrambled_predicate": "right_scramble",
                "decoders": ["always_false_decoder"],
                "expect": "not_sensitive",
            }
        ],
        "provenance": _generated_provenance(
            "Generated finite relational control: the declared target and its "
            "scrambled counterpart are both unrecoverable under a constant "
            "observation, so the adapter should not treat the target as "
            "operationally sensitive."
        ),
    }
    return _validated_ir_case("generated_decorative_target_scramble_control", model)


def _generated_target_scramble_capacity_sensitivity_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_target_scramble_capacity_sensitivity",
        "schema_version": "0.1.0",
        "domains": {
            "state": ["a", "b", "c", "d"],
            "observation": ["left_block", "right_block"],
        },
        "predicates": {
            "block_target": {
                "domain": "state",
                "members": ["a", "b"],
            },
            "crosscut_scramble": {
                "domain": "state",
                "members": ["a", "c"],
            },
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
                "id": "generated_same_prevalence_scramble_changes_capacity",
                "kind": "target_scramble_capacity_sensitivity",
                "observation": "block_observation",
                "target_predicate": "block_target",
                "scrambled_predicate": "crosscut_scramble",
                "expect": "capacity_sensitive",
            }
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: the original target is exactly "
            "recoverable from a fixed block observation, while a same-prevalence "
            "crosscut scramble is not recoverable by any deterministic decoder."
        ),
    }
    return _validated_ir_case("generated_target_scramble_capacity_sensitivity", model)


def _generated_target_scramble_capacity_label_swap_control_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_target_scramble_capacity_label_swap_control",
        "schema_version": "0.1.0",
        "domains": {
            "state": ["left", "right"],
            "observation": ["red", "blue"],
        },
        "predicates": {
            "left_target": {
                "domain": "state",
                "members": ["left"],
            },
            "right_scramble": {
                "domain": "state",
                "members": ["right"],
            },
        },
        "functions": {
            "color_observation": {
                "domain": "state",
                "codomain": "observation",
                "mapping": {
                    "left": "red",
                    "right": "blue",
                },
            },
        },
        "audits": [
            {
                "id": "generated_boolean_label_swap_does_not_change_capacity",
                "kind": "target_scramble_capacity_sensitivity",
                "observation": "color_observation",
                "target_predicate": "left_target",
                "scrambled_predicate": "right_scramble",
                "expect": "not_capacity_sensitive",
            }
        ],
        "provenance": _generated_provenance(
            "Generated finite relational control: the scrambled target is the "
            "Boolean complement of the original target, and an unrestricted "
            "deterministic decoder class recovers both from the same exact "
            "observation."
        ),
    }
    return _validated_ir_case(
        "generated_target_scramble_capacity_label_swap_control",
        model,
    )


def _generated_dynamic_equivariance_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_dynamic_equivariance",
        "schema_version": "0.1.0",
        "carrier": ["left", "right"],
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
                "mapping": {
                    "left": "L",
                    "right": "R",
                },
            },
        },
        "audits": [
            {
                "id": "generated_projected_role_dynamics_commutes",
                "kind": "dynamic_presentation_equivariance",
                "transition": "next",
                "presentation": "role_presentation",
                "abstract_transition": "role_next",
                "expect": "equivariant",
            }
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: projected role dynamics includes "
            "exactly the transition edges induced by the state-level dynamics "
            "and presentation."
        ),
    }
    return _validated_ir_case("generated_dynamic_equivariance", model)


def _generated_dynamic_non_equivariance_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_dynamic_non_equivariance",
        "schema_version": "0.1.0",
        "carrier": ["left", "right"],
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
                "mapping": {
                    "left": "L",
                    "right": "R",
                },
            },
        },
        "audits": [
            {
                "id": "generated_bad_role_dynamics_does_not_commute",
                "kind": "dynamic_presentation_equivariance",
                "transition": "next",
                "presentation": "role_presentation",
                "abstract_transition": "bad_role_next",
                "expect": "not_equivariant",
            }
        ],
        "provenance": _generated_provenance(
            "Generated finite relational control: abstract role dynamics both "
            "misses a projected state transition and adds a phantom role edge."
        ),
    }
    return _validated_ir_case("generated_dynamic_non_equivariance", model)


def _generated_edge_exact_path_lifting_failure_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_edge_exact_path_lifting_failure",
        "schema_version": "0.1.0",
        "carrier": ["a", "b", "c", "d"],
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
                "id": "generated_global_edge_image_is_exact",
                "kind": "dynamic_edge_projection_exactness",
                "transition": "next",
                "presentation": "presentation",
                "abstract_transition": "abstract_next",
                "expect": "edge_exact",
            },
            {
                "id": "generated_step_lifting_fails_inside_merged_fiber",
                "kind": "dynamic_step_lifting",
                "transition": "next",
                "presentation": "presentation",
                "abstract_transition": "abstract_next",
                "expect": "not_step_lifts",
            },
            {
                "id": "generated_path_lifting_detects_spliced_abstract_history",
                "kind": "dynamic_path_lifting",
                "transition": "next",
                "presentation": "presentation",
                "abstract_transition": "abstract_next",
                "horizon": 2,
                "expect": "not_path_lifts",
            },
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: global edge projection is exact, "
            "but a merged intermediate label lets abstract paths splice "
            "incompatible exact representatives."
        ),
    }
    return _validated_ir_case("generated_edge_exact_path_lifting_failure", model)


def _generated_viable_trajectory_count_cycle_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_viable_trajectory_count_cycle",
        "schema_version": "0.1.0",
        "carrier": ["left", "right"],
        "predicates": {
            "safe": ["left", "right"],
        },
        "relations": {
            "next": [["left", "right"], ["right", "left"]],
        },
        "audits": [
            {
                "id": "generated_cycle_safe_word_profile",
                "kind": "viable_trajectory_count",
                "transition": "next",
                "safety": "safe",
                "horizon": 3,
                "expected_count_profile": [2, 2, 2, 2],
                "expected_final_count": 2,
                "expect": "count_ok",
            }
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: a two-state recurrent cycle has "
            "a flat finite viable-trajectory count profile over the declared "
            "safe support."
        ),
    }
    return _validated_ir_case("generated_viable_trajectory_count_cycle", model)


def _generated_viable_trajectory_count_branching_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_viable_trajectory_count_branching",
        "schema_version": "0.1.0",
        "carrier": ["left", "right"],
        "predicates": {
            "safe": ["left", "right"],
        },
        "relations": {
            "next": [
                ["left", "left"],
                ["left", "right"],
                ["right", "left"],
                ["right", "right"],
            ],
        },
        "audits": [
            {
                "id": "generated_branching_safe_word_profile",
                "kind": "viable_trajectory_count",
                "transition": "next",
                "safety": "safe",
                "horizon": 3,
                "expected_count_profile": [2, 4, 8, 16],
                "expected_final_count": 16,
                "expect": "count_ok",
            }
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: a fully branching two-state "
            "safe dynamics has a larger finite viable-trajectory count profile "
            "than the recurrent two-state cycle."
        ),
    }
    return _validated_ir_case("generated_viable_trajectory_count_branching", model)


def _generated_dead_end_safe_prefix_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_dead_end_safe_prefix",
        "schema_version": "0.1.0",
        "carrier": ["start", "dead_a", "dead_b"],
        "predicates": {
            "safe": ["start", "dead_a", "dead_b"],
            "start_only": ["start"],
        },
        "relations": {
            "next": [["start", "dead_a"], ["start", "dead_b"]],
        },
        "audits": [
            {
                "id": "generated_dead_end_branching_safe_prefixes",
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
                "id": "generated_dead_end_branching_not_extendable",
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
        "provenance": _generated_provenance(
            "Generated finite relational case: branching creates safe prefixes, "
            "but every branch ends in a safe dead end outside the viability "
            "kernel."
        ),
    }
    return _validated_ir_case("generated_dead_end_safe_prefix", model)


def _generated_observed_word_count_collapses_branching_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_observed_word_count_collapses_branching",
        "schema_version": "0.1.0",
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
                "id": "generated_branching_collapses_to_one_observed_word",
                "kind": "observed_extendable_safe_word_count",
                "transition": "next",
                "safety": "safe",
                "observation": "constant_observation",
                "horizon": 2,
                "expected_count_profile": [1, 1, 1],
                "expected_final_count": 1,
                "expect": "count_ok",
            }
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: raw state-path branching remains "
            "extendable, but a constant observation collapses all extendable "
            "safe prefixes to one observed word at each horizon."
        ),
    }
    return _validated_ir_case("generated_observed_word_count_collapses_branching", model)


def _generated_observed_word_count_labeled_cycle_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_observed_word_count_labeled_cycle",
        "schema_version": "0.1.0",
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
                "id": "generated_labeled_cycle_keeps_two_observed_words",
                "kind": "observed_extendable_safe_word_count",
                "transition": "next",
                "safety": "safe",
                "observation": "role_observation",
                "horizon": 2,
                "expected_count_profile": [2, 2, 2],
                "expected_final_count": 2,
                "expect": "count_ok",
            }
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: a labeled recurrent cycle keeps "
            "two distinct observed extendable words at each finite horizon."
        ),
    }
    return _validated_ir_case("generated_observed_word_count_labeled_cycle", model)


def _generated_viable_count_inflation_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_viable_count_inflation",
        "schema_version": "0.1.0",
        "carrier": ["left", "right"],
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
            },
        },
        "audits": [
            {
                "id": "generated_phantom_edges_inflate_viable_counts",
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
        "provenance": _generated_provenance(
            "Generated finite relational case: non-equivariant abstract dynamics "
            "adds phantom self-edges and inflates finite viable trajectory counts."
        ),
    }
    return _validated_ir_case("generated_viable_count_inflation", model)


def _generated_viable_count_hiding_case() -> GeneratedAdapterCase:
    model = {
        "model_id": "generated_viable_count_hiding",
        "schema_version": "0.1.0",
        "carrier": ["left", "right"],
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
            },
        },
        "audits": [
            {
                "id": "generated_missing_edges_hide_viable_counts",
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
        "provenance": _generated_provenance(
            "Generated finite relational case: non-equivariant abstract dynamics "
            "omits projected self-edges and hides finite viable trajectory counts."
        ),
    }
    return _validated_ir_case("generated_viable_count_hiding", model)


def _generated_stale_reflected_fact_closure_case() -> GeneratedAdapterCase:
    states = ("start", "mid", "goal", "dead")
    before_edges = (("start", "mid"), ("mid", "goal"))
    after_edges = (("start", "mid"),)
    target = "goal"
    before_reachable = {
        source
        for source in states
        if (source, target) in reachable_pairs(set(states), set(before_edges))
    }
    after_reachable = {
        source
        for source in states
        if (source, target) in reachable_pairs(set(states), set(after_edges))
    }
    model = {
        "model_id": "generated_stale_reflected_fact_closure",
        "schema_version": "0.1.0",
        "carrier": list(states),
        "relations": {
            "before_next": [list(edge) for edge in before_edges],
            "after_next": [list(edge) for edge in after_edges],
        },
        "predicates": {
            "before_can_reach_goal": sorted(before_reachable),
            "after_can_reach_goal": sorted(after_reachable),
            "all_states": list(states),
        },
        "functions": {
            "stale_reach_status": {
                state: ("can_reach_goal" if state in before_reachable else "cannot_reach_goal")
                for state in states
            },
            "reflected_reach_status": {
                state: ("can_reach_goal" if state in after_reachable else "cannot_reach_goal")
                for state in states
            },
        },
        "audits": [
            {
                "id": "generated_stale_status_preserves_before_reach_fact",
                "kind": "presentation_fact_closure",
                "presentations": ["stale_reach_status"],
                "target_predicates": [
                    "before_can_reach_goal",
                    "after_can_reach_goal",
                    "all_states",
                ],
                "expected_common_target_predicates": [
                    "before_can_reach_goal",
                    "all_states",
                ],
                "expected_absent_target_predicates": ["after_can_reach_goal"],
                "expect": "closure_ok",
            },
            {
                "id": "generated_reflected_status_preserves_after_reach_fact",
                "kind": "presentation_fact_closure",
                "presentations": ["reflected_reach_status"],
                "target_predicates": [
                    "before_can_reach_goal",
                    "after_can_reach_goal",
                    "all_states",
                ],
                "expected_common_target_predicates": [
                    "after_can_reach_goal",
                    "all_states",
                ],
                "expected_absent_target_predicates": ["before_can_reach_goal"],
                "expect": "closure_ok",
            },
            {
                "id": "generated_stale_reflected_intersection_drops_time_specific_facts",
                "kind": "presentation_fact_closure",
                "presentations": ["stale_reach_status", "reflected_reach_status"],
                "target_predicates": [
                    "before_can_reach_goal",
                    "after_can_reach_goal",
                    "all_states",
                ],
                "expected_common_target_predicates": ["all_states"],
                "expected_absent_target_predicates": [
                    "before_can_reach_goal",
                    "after_can_reach_goal",
                ],
                "expect": "closure_ok",
            },
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: stale and reflected reachability "
            "presentations each preserve their matching time-indexed fact, but "
            "their common closure drops both time-specific reachability facts."
        ),
    }
    return _validated_ir_case("generated_stale_reflected_fact_closure", model)


def _generated_multi_presentation_fact_closure_case() -> GeneratedAdapterCase:
    states = ("top_left", "top_right", "bottom_left", "bottom_right")
    row_top = {"top_left", "top_right"}
    col_left = {"top_left", "bottom_left"}
    model = {
        "model_id": "generated_multi_presentation_fact_closure",
        "schema_version": "0.1.0",
        "carrier": list(states),
        "predicates": {
            "row_top": sorted(row_top),
            "col_left": sorted(col_left),
            "all_states": list(states),
        },
        "functions": {
            "identity": {state: state for state in states},
            "row_projection": {
                state: ("top" if state in row_top else "bottom") for state in states
            },
            "col_projection": {
                state: ("left" if state in col_left else "right") for state in states
            },
        },
        "audits": [
            {
                "id": "generated_identity_row_family_keeps_row_fact",
                "kind": "presentation_fact_closure",
                "presentations": ["identity", "row_projection"],
                "target_predicates": ["row_top", "col_left", "all_states"],
                "expected_common_target_predicates": ["row_top", "all_states"],
                "expected_absent_target_predicates": ["col_left"],
                "expected_common_visible_pairs": [
                    ["top_left", "bottom_left"],
                    ["top_left", "bottom_right"],
                    ["top_right", "bottom_left"],
                    ["top_right", "bottom_right"],
                    ["bottom_left", "top_left"],
                    ["bottom_left", "top_right"],
                    ["bottom_right", "top_left"],
                    ["bottom_right", "top_right"],
                ],
                "expect": "closure_ok",
            },
            {
                "id": "generated_identity_col_family_keeps_col_fact",
                "kind": "presentation_fact_closure",
                "presentations": ["identity", "col_projection"],
                "target_predicates": ["row_top", "col_left", "all_states"],
                "expected_common_target_predicates": ["col_left", "all_states"],
                "expected_absent_target_predicates": ["row_top"],
                "expect": "closure_ok",
            },
            {
                "id": "generated_row_col_family_keeps_only_shared_constants",
                "kind": "presentation_fact_closure",
                "presentations": ["identity", "row_projection", "col_projection"],
                "target_predicates": ["row_top", "col_left", "all_states"],
                "expected_common_target_predicates": ["all_states"],
                "expected_absent_target_predicates": ["row_top", "col_left"],
                "expected_common_visible_pairs": [
                    ["top_left", "bottom_right"],
                    ["top_right", "bottom_left"],
                    ["bottom_left", "top_right"],
                    ["bottom_right", "top_left"],
                ],
                "expect": "closure_ok",
            },
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: row and column presentations "
            "preserve different exact target facts, while the declared family "
            "closure keeps only facts invariant across every presentation."
        ),
    }
    return _validated_ir_case("generated_multi_presentation_fact_closure", model)


def _generated_crosscutting_presentation_closure_case() -> GeneratedAdapterCase:
    states = ("00", "01", "10", "11")
    row_zero = {"00", "01"}
    col_zero = {"00", "10"}
    even_parity = {"00", "11"}
    all_ordered_pairs = [
        [left, right]
        for left in states
        for right in states
        if left != right
    ]
    model = {
        "model_id": "generated_crosscutting_presentation_closure",
        "schema_version": "0.1.0",
        "carrier": list(states),
        "predicates": {
            "row_zero": sorted(row_zero),
            "col_zero": sorted(col_zero),
            "even_parity": sorted(even_parity),
            "all_states": list(states),
        },
        "functions": {
            "identity": {state: state for state in states},
            "row_projection": {
                state: ("row0" if state in row_zero else "row1")
                for state in states
            },
            "col_projection": {
                state: ("col0" if state in col_zero else "col1")
                for state in states
            },
            "parity_projection": {
                state: ("even" if state in even_parity else "odd")
                for state in states
            },
        },
        "audits": [
            {
                "id": "generated_row_projection_keeps_row_fact",
                "kind": "presentation_fact_closure",
                "presentations": ["identity", "row_projection"],
                "target_predicates": [
                    "row_zero",
                    "col_zero",
                    "even_parity",
                    "all_states",
                ],
                "expected_common_target_predicates": ["row_zero", "all_states"],
                "expected_absent_target_predicates": ["col_zero", "even_parity"],
                "expect": "closure_ok",
            },
            {
                "id": "generated_col_projection_keeps_col_fact",
                "kind": "presentation_fact_closure",
                "presentations": ["identity", "col_projection"],
                "target_predicates": [
                    "row_zero",
                    "col_zero",
                    "even_parity",
                    "all_states",
                ],
                "expected_common_target_predicates": ["col_zero", "all_states"],
                "expected_absent_target_predicates": ["row_zero", "even_parity"],
                "expect": "closure_ok",
            },
            {
                "id": "generated_parity_projection_keeps_parity_fact",
                "kind": "presentation_fact_closure",
                "presentations": ["identity", "parity_projection"],
                "target_predicates": [
                    "row_zero",
                    "col_zero",
                    "even_parity",
                    "all_states",
                ],
                "expected_common_target_predicates": ["even_parity", "all_states"],
                "expected_absent_target_predicates": ["row_zero", "col_zero"],
                "expect": "closure_ok",
            },
            {
                "id": "generated_row_col_parity_family_erases_all_specific_facts",
                "kind": "presentation_fact_closure",
                "presentations": [
                    "identity",
                    "row_projection",
                    "col_projection",
                    "parity_projection",
                ],
                "target_predicates": [
                    "row_zero",
                    "col_zero",
                    "even_parity",
                    "all_states",
                ],
                "expected_common_target_predicates": ["all_states"],
                "expected_absent_target_predicates": [
                    "row_zero",
                    "col_zero",
                    "even_parity",
                ],
                "expected_absent_visible_pairs": all_ordered_pairs,
                "expect": "closure_ok",
            },
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: row, column, and parity "
            "presentations each preserve a different target fact, while their "
            "declared family closure preserves only the constant target and no "
            "ordered visible state pairs."
        ),
    }
    return _validated_ir_case("generated_crosscutting_presentation_closure", model)


def _generated_graph_pair_transfer_case() -> GeneratedAdapterCase:
    source = _graph_pair_transfer_source(
        source_id="generated_graph_pair_transfer",
        target_edges=(("t_left", "t_right"), ("t_right", "t_left")),
        expect="transferred",
        claim_boundary=(
            "Generated graph-pair transfer source: source and target graph "
            "cycles are compiled separately, then audited through a declared "
            "endpoint correspondence."
        ),
    )
    compiled = compile_graph_pair_transfer_source(source)
    return _validated_compiled_case(
        "generated_graph_pair_transfer",
        "derived_graph_pair",
        source,
        compiled,
    )


def _generated_graph_pair_transfer_missing_return_case() -> GeneratedAdapterCase:
    source = _graph_pair_transfer_source(
        source_id="generated_graph_pair_transfer_missing_return",
        target_edges=(("t_left", "t_right"),),
        expect="not_transferred",
        claim_boundary=(
            "Generated graph-pair transfer source: endpoint correspondence is "
            "present, but the target graph loses the return edge required for "
            "carrier transfer."
        ),
    )
    compiled = compile_graph_pair_transfer_source(source)
    return _validated_compiled_case(
        "generated_graph_pair_transfer_missing_return",
        "derived_graph_pair",
        source,
        compiled,
    )


def _graph_pair_transfer_source(
    *,
    source_id: str,
    target_edges: tuple[Pair, ...],
    expect: str,
    claim_boundary: str,
) -> dict[str, Any]:
    return {
        "model_id": source_id,
        "expect": expect,
        "source_left": "s_left",
        "source_right": "s_right",
        "target_left": "t_left",
        "target_right": "t_right",
        "source_graph": {
            "model_id": f"{source_id}_source",
            "nodes": ["s_left", "s_right"],
            "edges": [["s_left", "s_right"], ["s_right", "s_left"]],
            "observations": {
                "role": {
                    "s_left": "left",
                    "s_right": "right",
                }
            },
            "safety": "all",
            "provenance": _generated_provenance(
                "Generated graph-pair transfer source side."
            ),
        },
        "target_graph": {
            "model_id": f"{source_id}_target",
            "nodes": ["t_left", "t_right"],
            "edges": [list(edge) for edge in target_edges],
            "observations": {
                "role": {
                    "t_left": "left",
                    "t_right": "right",
                }
            },
            "safety": "all",
            "provenance": _generated_provenance(
                "Generated graph-pair transfer target side."
            ),
        },
        "correspondence": [["s_left", "t_left"], ["s_right", "t_right"]],
        "provenance": _generated_provenance(claim_boundary),
    }


def _generated_transport_fact_closure_case() -> GeneratedAdapterCase:
    states = ("s_left", "s_right", "t_left", "t_right")
    model = {
        "model_id": "generated_transport_fact_closure",
        "schema_version": "0.1.0",
        "carrier": list(states),
        "predicates": {
            "source_safe": ["s_left", "s_right"],
            "source_carrier": ["s_left", "s_right"],
            "target_safe": ["t_left", "t_right"],
            "target_carrier": ["t_left", "t_right"],
            "transported_left_endpoint": ["s_left", "t_left"],
            "all_states": list(states),
        },
        "relations": {
            "source_next": [["s_left", "s_right"], ["s_right", "s_left"]],
            "target_next": [["t_left", "t_right"], ["t_right", "t_left"]],
            "source_separated": [["s_left", "s_right"], ["s_right", "s_left"]],
            "target_separated": [["t_left", "t_right"], ["t_right", "t_left"]],
            "corresponds": [["s_left", "t_left"], ["s_right", "t_right"]],
        },
        "functions": {
            "source_lifted_role": {
                "s_left": "left",
                "s_right": "right",
                "t_left": "left",
                "t_right": "right",
            },
            "target_lifted_role": {
                "s_left": "left",
                "s_right": "right",
                "t_left": "left",
                "t_right": "right",
            },
            "constant_transport_view": {state: "merged" for state in states},
        },
        "audits": [
            {
                "id": "generated_cycle_carrier_transfer_contract",
                "kind": "carrier_transfer",
                "source_transition": "source_next",
                "source_safety": "source_safe",
                "source_carrier": "source_carrier",
                "source_left": "s_left",
                "source_right": "s_right",
                "source_separation": "source_separated",
                "target_transition": "target_next",
                "target_safety": "target_safe",
                "target_carrier": "target_carrier",
                "target_left": "t_left",
                "target_right": "t_right",
                "target_separation": "target_separated",
                "correspondence": "corresponds",
                "expect": "transferred",
            },
            {
                "id": "generated_lifted_transfer_views_preserve_transported_role",
                "kind": "presentation_fact_closure",
                "presentations": ["source_lifted_role", "target_lifted_role"],
                "target_predicates": ["transported_left_endpoint", "all_states"],
                "expected_common_target_predicates": [
                    "transported_left_endpoint",
                    "all_states",
                ],
                "expected_common_visible_pairs": [
                    ["s_left", "s_right"],
                    ["s_left", "t_right"],
                    ["s_right", "s_left"],
                    ["s_right", "t_left"],
                    ["t_left", "s_right"],
                    ["t_left", "t_right"],
                    ["t_right", "s_left"],
                    ["t_right", "t_left"],
                ],
                "expect": "closure_ok",
            },
            {
                "id": "generated_erasing_transport_view_drops_transported_role",
                "kind": "presentation_fact_closure",
                "presentations": [
                    "source_lifted_role",
                    "target_lifted_role",
                    "constant_transport_view",
                ],
                "target_predicates": ["transported_left_endpoint", "all_states"],
                "expected_common_target_predicates": ["all_states"],
                "expected_absent_target_predicates": ["transported_left_endpoint"],
                "expected_absent_visible_pairs": [
                    ["s_left", "s_right"],
                    ["t_left", "t_right"],
                ],
                "expect": "closure_ok",
            },
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: a declared carrier-transfer "
            "contract supports lifted source/target endpoint-role presentations, "
            "and an admitted erasing presentation removes the transported role "
            "from common facts."
        ),
    }
    return _validated_ir_case("generated_transport_fact_closure", model)


def _generated_failed_transport_fact_closure_case() -> GeneratedAdapterCase:
    states = ("s_left", "s_right", "t_left", "t_right")
    model = {
        "model_id": "generated_failed_transport_fact_closure",
        "schema_version": "0.1.0",
        "carrier": list(states),
        "predicates": {
            "source_safe": ["s_left", "s_right"],
            "source_carrier": ["s_left", "s_right"],
            "target_safe": ["t_left", "t_right"],
            "target_carrier": ["t_left", "t_right"],
            "transported_left_endpoint": ["s_left", "t_left"],
            "all_states": list(states),
        },
        "relations": {
            "source_next": [["s_left", "s_right"], ["s_right", "s_left"]],
            "target_next": [["t_left", "t_right"]],
            "source_separated": [["s_left", "s_right"], ["s_right", "s_left"]],
            "target_separated": [["t_left", "t_right"], ["t_right", "t_left"]],
            "corresponds": [["s_left", "t_left"], ["s_right", "t_right"]],
        },
        "functions": {
            "source_lifted_role": {
                "s_left": "left",
                "s_right": "right",
                "t_left": "left",
                "t_right": "right",
            },
            "target_lifted_role": {
                "s_left": "left",
                "s_right": "right",
                "t_left": "left",
                "t_right": "right",
            },
            "constant_transport_view": {state: "merged" for state in states},
        },
        "audits": [
            {
                "id": "generated_broken_carrier_transfer_contract",
                "kind": "carrier_transfer",
                "source_transition": "source_next",
                "source_safety": "source_safe",
                "source_carrier": "source_carrier",
                "source_left": "s_left",
                "source_right": "s_right",
                "source_separation": "source_separated",
                "target_transition": "target_next",
                "target_safety": "target_safe",
                "target_carrier": "target_carrier",
                "target_left": "t_left",
                "target_right": "t_right",
                "target_separation": "target_separated",
                "correspondence": "corresponds",
                "expect": "not_transferred",
            },
            {
                "id": "generated_role_views_preserve_label_fact_despite_failed_transfer",
                "kind": "presentation_fact_closure",
                "presentations": ["source_lifted_role", "target_lifted_role"],
                "target_predicates": ["transported_left_endpoint", "all_states"],
                "expected_common_target_predicates": [
                    "transported_left_endpoint",
                    "all_states",
                ],
                "expected_common_visible_pairs": [
                    ["s_left", "s_right"],
                    ["s_left", "t_right"],
                    ["s_right", "s_left"],
                    ["s_right", "t_left"],
                    ["t_left", "s_right"],
                    ["t_left", "t_right"],
                    ["t_right", "s_left"],
                    ["t_right", "t_left"],
                ],
                "expect": "closure_ok",
            },
            {
                "id": "generated_erasing_view_drops_label_fact_after_failed_transfer",
                "kind": "presentation_fact_closure",
                "presentations": [
                    "source_lifted_role",
                    "target_lifted_role",
                    "constant_transport_view",
                ],
                "target_predicates": ["transported_left_endpoint", "all_states"],
                "expected_common_target_predicates": ["all_states"],
                "expected_absent_target_predicates": ["transported_left_endpoint"],
                "expect": "closure_ok",
            },
        ],
        "provenance": _generated_provenance(
            "Generated finite relational case: lifted endpoint-role presentations "
            "can preserve a transport-looking label fact even when the carrier "
            "transfer contract fails because target return structure is missing."
        ),
    }
    return _validated_ir_case("generated_failed_transport_fact_closure", model)


def _target_closure_audits(
    *,
    exact_presentation: str,
    erasing_presentation: str,
    target_predicate: str,
    constant_predicate: str,
    exact_audit_id: str,
    erasing_audit_id: str,
) -> list[dict[str, Any]]:
    return [
        {
            "id": exact_audit_id,
            "kind": "presentation_fact_closure",
            "presentations": [exact_presentation],
            "target_predicates": [target_predicate, constant_predicate],
            "seed_target_predicates": [constant_predicate],
            "expected_common_target_predicates": [target_predicate, constant_predicate],
            "expected_surplus_target_predicates": [target_predicate],
            "expected_nonconstant_surplus_target_predicates": [target_predicate],
            "expect": "closure_ok",
        },
        {
            "id": erasing_audit_id,
            "kind": "presentation_fact_closure",
            "presentations": [exact_presentation, erasing_presentation],
            "target_predicates": [target_predicate, constant_predicate],
            "seed_target_predicates": [constant_predicate],
            "expected_absent_target_predicates": [target_predicate],
            "expected_common_target_predicates": [constant_predicate],
            "expected_absent_surplus_target_predicates": [target_predicate],
            "expected_absent_nonconstant_surplus_target_predicates": [target_predicate],
            "expect": "closure_ok",
        },
    ]


def _generated_finite_grid_asymmetry_case() -> GeneratedAdapterCase:
    for width, height, movement_rule in ((2, 1, "east"), (1, 2, "orthogonal"), (2, 2, "east")):
        cells = [f"{x},{y}" for y in range(height) for x in range(width)]
        if len(cells) < 2:
            continue
        first, second = cells[:2]
        grid_source = {
            "model_id": "generated_finite_grid_asymmetry",
            "width": width,
            "height": height,
            "movement_rule": movement_rule,
            "observations": {
                "color": {cell: ("red" if cell == first else "blue") for cell in cells}
            },
            "presentations": {
                "identity": {cell: cell for cell in cells},
                "constant": {cell: "merged" for cell in cells},
            },
            "presentation_expectations": {
                "identity": "sound",
                "constant": "unsound",
            },
            "safety": "all",
            "provenance": _generated_provenance(
                "Generated finite grid case: movement and observation difference compile "
                "through derived graph into Alpha-like asymmetry."
            ),
        }
        compiled = compile_finite_grid(grid_source)
        model = load_model(compiled)
        if model.relation_tuples("primitive_asym"):
            return _validated_compiled_case(
                "generated_finite_grid_asymmetry",
                "finite_grid",
                grid_source,
                compiled,
            )
    raise AssertionError("failed to generate finite grid asymmetry case")


def _validated_ir_case(case_id: str, model: dict[str, Any]) -> GeneratedAdapterCase:
    return _validated_compiled_case(case_id, "finite_relational_ir", model, model)


def _validated_compiled_case(
    case_id: str,
    source_format: str,
    source: dict[str, Any],
    compiled: dict[str, Any],
) -> GeneratedAdapterCase:
    model = load_model(compiled)
    audit_results = tuple(run_declared_audits(model))
    if not audit_results:
        raise AssertionError(f"{case_id} generated no audits")
    if not all(result.passed for result in audit_results):
        failures = [result.as_dict() for result in audit_results if not result.passed]
        raise AssertionError(f"{case_id} generated failing audits: {failures}")
    return GeneratedAdapterCase(
        case_id=case_id,
        source_format=source_format,
        source=source,
        compiled_model=compiled,
        audit_results=audit_results,
    )


def _transition_audit_model(
    *,
    model_id: str,
    states: Iterable[str],
    relations: dict[str, Iterable[Pair]],
    audit: dict[str, Any],
    claim_boundary: str,
) -> dict[str, Any]:
    return {
        "model_id": model_id,
        "schema_version": "0.1.0",
        "carrier": list(states),
        "relations": {
            name: [list(edge) for edge in sorted(edge_set)]
            for name, edge_set in relations.items()
        },
        "audits": [audit],
        "provenance": _generated_provenance(claim_boundary),
    }


def _generated_provenance(claim_boundary: str) -> dict[str, object]:
    return {
        "declared_before_run": True,
        "source": "omega.adapters.finite_relational.adversarial_search",
        "claim_boundary": claim_boundary,
        "fixture_intent": "generated finite adapter hardening case",
    }


def _edge_subsets(nodes: Iterable[str]) -> Iterable[tuple[Pair, ...]]:
    possible_edges = sorted((source, target) for source in nodes for target in nodes if source != target)
    for size in range(len(possible_edges) + 1):
        for edge_subset in combinations(possible_edges, size):
            yield tuple(edge_subset)
