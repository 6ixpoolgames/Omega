"""Preregistered fixtures for finite process-interface identifiability v0."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from typing import Any, Mapping

from omega_v2.finite.controllers import FiniteStateController
from omega_v2.finite.model import ControlledMarkovSystem
from omega_v2.finite.process_interfaces import (
    FEATURE_FIELDS,
    PRIMARY_PROCESS_QUERY,
    BinaryState,
    BinarySynchronousSystem,
    EvidenceMode,
    IdentificationStatus,
    InterfaceIdentification,
    InterfaceQuery,
    ProcessInterfaceProfile,
    audit_deterministic_closed_loop_map,
    audit_memory_update_injectivity,
    coordinate_influence_witnesses,
    identify_process_interfaces,
    interventionally_equivalent,
    observationally_equivalent,
    profile_process_interface,
)


PROTOCOL_DOC = (
    "docs/research_notes/omega_v2/"
    "process_interface_identifiability_protocol_v0.md"
)
HORIZON = 4
CENSUS_FEATURES = (
    "persistent_variation",
    "internal_influence",
    "incoming_influence",
    "outgoing_influence",
    "latent_state_multiplicity",
    "record_sensitive_outflow",
    "continuation_influence",
)
CAUSAL_CONTINUATION_QUERY = InterfaceQuery(
    query_id="causal_continuation_interface",
    required_true=(
        "persistent_variation",
        "incoming_influence",
        "outgoing_influence",
        "continuation_influence",
    ),
)


def _profile_map(
    result: InterfaceIdentification,
) -> dict[tuple[str, ...], ProcessInterfaceProfile]:
    return {profile.interface: profile for profile in result.profiles}


def _identification_payload(
    result: InterfaceIdentification,
) -> dict[str, object]:
    return {
        "status": result.status.value,
        "certified_interfaces": [
            list(interface) for interface in result.certified_interfaces
        ],
        "unresolved_interfaces": [
            list(interface) for interface in result.unresolved_interfaces
        ],
        "rejected_interfaces": [
            list(interface) for interface in result.rejected_interfaces
        ],
        "retained_minimal_interfaces": [
            list(interface) for interface in result.retained_minimal_interfaces
        ],
    }


def _structural_identification_signature(
    result: InterfaceIdentification,
) -> tuple[object, ...]:
    return (
        result.status.value,
        tuple(
            (
                profile.interface,
                profile.outside,
                profile.structural_signature(),
            )
            for profile in result.profiles
        ),
        result.certified_interfaces,
        result.unresolved_interfaces,
        result.rejected_interfaces,
        result.retained_minimal_interfaces,
    )


def _rename_interface(
    interface: tuple[str, ...],
    renaming: Mapping[str, str],
) -> tuple[str, ...]:
    return tuple(renaming[item] for item in interface)


def _renaming_covariant(
    original: InterfaceIdentification,
    renamed: InterfaceIdentification,
    renaming: Mapping[str, str],
) -> bool:
    original_profiles = {
        _rename_interface(profile.interface, renaming): profile.structural_signature()
        for profile in original.profiles
    }
    renamed_profiles = {
        profile.interface: profile.structural_signature()
        for profile in renamed.profiles
    }
    return (
        original.status == renamed.status
        and original_profiles == renamed_profiles
        and tuple(
            _rename_interface(interface, renaming)
            for interface in original.retained_minimal_interfaces
        )
        == renamed.retained_minimal_interfaces
    )


def identified_interface_system() -> BinarySynchronousSystem:
    """Two-bit fixture with exactly one minimal primary-query interface."""

    states = tuple(itertools.product((0, 1), repeat=2))
    targets = (
        (0, 1),
        (0, 0),
        (1, 0),
        (0, 0),
    )
    return BinarySynchronousSystem(
        system_id="identified_interface_rule_18",
        component_ids=("inside", "outside"),
        transition_rows=tuple(zip(states, targets, strict=True)),
        initial_states=((0, 0), (1, 0)),
    )


def set_identified_interface_system() -> BinarySynchronousSystem:
    """Symmetric swap with two incomparable minimal primary-query interfaces."""

    return BinarySynchronousSystem.from_update_function(
        system_id="set_identified_symmetric_swap",
        component_ids=("left", "right"),
        update=lambda state: (state[1], state[0]),
        initial_states=tuple(itertools.product((0, 1), repeat=2)),
    )


def identification_controls() -> dict[str, Any]:
    identified_system = identified_interface_system()
    observational = identify_process_interfaces(
        identified_system,
        evidence_mode=EvidenceMode.OBSERVATIONAL,
        horizon=HORIZON,
    )
    identified = identify_process_interfaces(
        identified_system,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )
    secondary = identify_process_interfaces(
        identified_system,
        CAUSAL_CONTINUATION_QUERY,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )

    set_system = set_identified_interface_system()
    set_identified = identify_process_interfaces(
        set_system,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )

    annotated = identified_system.with_state_atom(
        "agent",
        system_id="identified_interface_with_agent_atom",
    )
    annotated_result = identify_process_interfaces(
        annotated,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )
    annotation_edges_invariant = (
        coordinate_influence_witnesses(identified_system)
        == coordinate_influence_witnesses(annotated)
    )
    renaming = {"inside": "alpha", "outside": "beta"}
    renamed = identified_system.rename_components(
        renaming,
        system_id="identified_interface_renamed",
    )
    renamed_result = identify_process_interfaces(
        renamed,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )

    return {
        "identified_system": identified_system,
        "observational": observational,
        "identified": identified,
        "secondary": secondary,
        "set_system": set_system,
        "set_identified": set_identified,
        "annotated": annotated,
        "annotated_result": annotated_result,
        "renamed": renamed,
        "renamed_result": renamed_result,
        "observational_result": _identification_payload(observational),
        "identified_result": _identification_payload(identified),
        "secondary_result": _identification_payload(secondary),
        "set_identified_result": _identification_payload(set_identified),
        "annotation_invariant": (
            _structural_identification_signature(identified)
            == _structural_identification_signature(annotated_result)
            and annotation_edges_invariant
        ),
        "annotation_edges_invariant": annotation_edges_invariant,
        "renaming_covariant": _renaming_covariant(
            identified,
            renamed_result,
            renaming,
        ),
        "feature_dependent": (
            identified.retained_minimal_interfaces
            != secondary.retained_minimal_interfaces
        ),
        "profile_count": len(identified.profiles),
        "expected_profile_count": (
            2 ** len(identified_system.component_ids) - 2
        ),
    }


def common_driver_system() -> BinarySynchronousSystem:
    return BinarySynchronousSystem.from_update_function(
        system_id="common_driver_shadow",
        component_ids=("driver", "left", "right"),
        update=lambda state: (1 - state[0], state[0], state[0]),
        initial_states=((0, 0, 0), (1, 1, 1)),
    )


def common_driver_control() -> dict[str, Any]:
    system = common_driver_system()
    edges = coordinate_influence_witnesses(system)
    edge_pairs = {
        (witness.source_component, witness.target_component)
        for witness in edges
    }
    post_update_states = set().union(*system.states_by_depth(HORIZON)[1:])
    descendant_pairs = {(state[1], state[2]) for state in post_update_states}
    return {
        "system": system,
        "edges": edges,
        "edge_pairs": sorted(edge_pairs),
        "descendant_pairs": sorted(descendant_pairs),
        "descendants_correlated": (
            bool(descendant_pairs)
            and all(left == right for left, right in descendant_pairs)
            and len({left for left, _right in descendant_pairs}) == 2
        ),
        "driver_edges_present": {
            ("driver", "left"),
            ("driver", "right"),
        }
        <= edge_pairs,
        "descendant_edge_absent": (
            ("left", "right") not in edge_pairs
            and ("right", "left") not in edge_pairs
        ),
    }


def copied_record_system() -> BinarySynchronousSystem:
    return BinarySynchronousSystem.from_update_function(
        system_id="copied_record_shadow",
        component_ids=("source", "copy", "output"),
        update=lambda state: (1 - state[0], state[0], state[0]),
        initial_states=((0, 0, 0), (1, 1, 1)),
    )


def copied_record_control() -> dict[str, Any]:
    system = copied_record_system()
    profile = profile_process_interface(
        system,
        ("copy",),
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )
    result = identify_process_interfaces(
        system,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )
    reached_after_update = set().union(*system.states_by_depth(HORIZON)[1:])
    copy_tracks_output = all(state[1] == state[2] for state in reached_after_update)
    copy_tracks_source_update = all(
        target[1] == source[0]
        for source, target in system.transition_rows
    )
    edge_pairs = {
        (witness.source_component, witness.target_component)
        for witness in coordinate_influence_witnesses(system)
    }
    return {
        "system": system,
        "profile": profile,
        "identification": result,
        "copy_tracks_output": copy_tracks_output,
        "copy_tracks_source_update": copy_tracks_source_update,
        "copy_to_output_edge_absent": ("copy", "output") not in edge_pairs,
        "copy_outgoing_influence": profile.outgoing_influence,
        "copy_primary_certified": ("copy",) in result.certified_interfaces,
    }


def observational_nonidentifiability_systems() -> tuple[
    BinarySynchronousSystem,
    BinarySynchronousSystem,
]:
    def shared_observed(state: BinaryState) -> BinaryState:
        inside, outside = state
        if outside == 0:
            return (1 - inside, 0)
        return (1 - inside, 1)

    def intervention_distinct(state: BinaryState) -> BinaryState:
        inside, outside = state
        if outside == 0:
            return (1 - inside, 0)
        return (1 - inside, inside)

    common = {
        "component_ids": ("inside", "outside"),
        "initial_states": ((0, 0), (1, 0)),
    }
    return (
        BinarySynchronousSystem.from_update_function(
            system_id="observational_model_left",
            update=shared_observed,
            **common,
        ),
        BinarySynchronousSystem.from_update_function(
            system_id="observational_model_right",
            update=intervention_distinct,
            **common,
        ),
    )


def observational_nonidentifiability_control() -> dict[str, Any]:
    left, right = observational_nonidentifiability_systems()
    left_observational = identify_process_interfaces(
        left,
        evidence_mode=EvidenceMode.OBSERVATIONAL,
        horizon=HORIZON,
    )
    right_observational = identify_process_interfaces(
        right,
        evidence_mode=EvidenceMode.OBSERVATIONAL,
        horizon=HORIZON,
    )
    left_interventional = identify_process_interfaces(
        left,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )
    right_interventional = identify_process_interfaces(
        right,
        evidence_mode=EvidenceMode.INTERVENTIONAL,
        horizon=HORIZON,
    )
    left_inside = _profile_map(left_interventional)[("inside",)]
    right_inside = _profile_map(right_interventional)[("inside",)]
    return {
        "left": left,
        "right": right,
        "left_observational": left_observational,
        "right_observational": right_observational,
        "left_interventional": left_interventional,
        "right_interventional": right_interventional,
        "observationally_equivalent": observationally_equivalent(
            left,
            right,
            horizon=HORIZON,
        ),
        "interventionally_equivalent": interventionally_equivalent(left, right),
        "observational_profiles_equal": (
            tuple(
                profile.structural_signature()
                for profile in left_observational.profiles
            )
            == tuple(
                profile.structural_signature()
                for profile in right_observational.profiles
            )
        ),
        "observational_status_left": left_observational.status.value,
        "observational_status_right": right_observational.status.value,
        "inside_interventional_profile_left": left_inside.as_dict(),
        "inside_interventional_profile_right": right_inside.as_dict(),
        "inside_interventional_profiles_differ": (
            left_inside.structural_signature()
            != right_inside.structural_signature()
        ),
    }


def _system_from_rule_code(code: int) -> BinarySynchronousSystem:
    if not 0 <= code < 256:
        raise ValueError("two-component rule code must lie in [0, 256)")
    states = tuple(itertools.product((0, 1), repeat=2))
    targets = tuple(
        (
            (code >> (2 * index)) & 1,
            (code >> (2 * index + 1)) & 1,
        )
        for index in range(4)
    )
    return BinarySynchronousSystem(
        system_id=f"binary_rule_{code:03d}",
        component_ids=("inside", "outside"),
        transition_rows=tuple(zip(states, targets, strict=True)),
        initial_states=((0, 0), (1, 0)),
    )


def exact_independence_census() -> dict[str, Any]:
    rows = []
    profiles: dict[int, ProcessInterfaceProfile] = {}
    for code in range(256):
        system = _system_from_rule_code(code)
        profile = profile_process_interface(
            system,
            ("inside",),
            evidence_mode=EvidenceMode.INTERVENTIONAL,
            horizon=HORIZON,
        )
        profiles[code] = profile
        rows.append(
            {
                "rule_code": code,
                "transition_targets": "|".join(
                    "".join(str(bit) for bit in target)
                    for _source, target in system.transition_rows
                ),
                **{
                    feature: bool(profile.feature(feature))
                    for feature in FEATURE_FIELDS
                },
            }
        )

    isolating_witnesses = {}
    for feature in CENSUS_FEATURES:
        other_features = tuple(
            candidate
            for candidate in CENSUS_FEATURES
            if candidate != feature
        )
        retained: tuple[int, int] | None = None
        for left_code, right_code in itertools.combinations(range(256), 2):
            left = profiles[left_code]
            right = profiles[right_code]
            if left.feature(feature) == right.feature(feature):
                continue
            if all(
                left.feature(other) == right.feature(other)
                for other in other_features
            ):
                retained = (left_code, right_code)
                break
        isolating_witnesses[feature] = retained

    feature_results = {
        feature: {
            "true_count": sum(bool(row[feature]) for row in rows),
            "false_count": sum(not bool(row[feature]) for row in rows),
            "verdict": (
                "ISOLATED"
                if isolating_witnesses[feature] is not None
                else "NOT_ISOLATED_IN_CENSUS"
            ),
            "witness_codes": (
                list(isolating_witnesses[feature])
                if isolating_witnesses[feature] is not None
                else []
            ),
        }
        for feature in CENSUS_FEATURES
    }
    joint_signatures = {
        tuple(bool(row[feature]) for feature in CENSUS_FEATURES)
        for row in rows
    }
    canonical = json.dumps(
        rows,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "rows": rows,
        "profiles": profiles,
        "feature_results": feature_results,
        "isolating_witnesses": isolating_witnesses,
        "enumerated_rule_count": len(rows),
        "expected_rule_count": 256,
        "joint_signature_count": len(joint_signatures),
        "record_acquisition_composite_holds": all(
            row["record_acquisition"]
            == (
                row["incoming_influence"]
                and row["latent_state_multiplicity"]
            )
            for row in rows
        ),
        "manifest_digest": hashlib.sha256(canonical).hexdigest(),
    }


def _memory_world() -> ControlledMarkovSystem[int, str]:
    return ControlledMarkovSystem(
        system_id="fixed_observation_world",
        states=(0, 1),
        actions=("hold",),
        transitions=(
            (0, "hold", 0, Fraction(1)),
            (1, "hold", 1, Fraction(1)),
        ),
    )


def _memory_controller(*, reversible: bool) -> FiniteStateController:
    memory_states = (0, 1)
    observations = (0, 1)
    return FiniteStateController(
        controller_id=(
            "xor_record_update" if reversible else "copy_record_update"
        ),
        memory_states=memory_states,
        initial_memory=0,
        observation_rows=((0, 0), (1, 1)),
        update_rows=tuple(
            (
                memory,
                observation,
                (
                    memory ^ observation
                    if reversible
                    else observation
                ),
            )
            for memory in memory_states
            for observation in observations
        ),
        policy_rows=tuple(
            (memory, observation, "hold")
            for memory in memory_states
            for observation in observations
        ),
    )


def memory_injectivity_control() -> dict[str, Any]:
    world = _memory_world()
    copy = _memory_controller(reversible=False)
    xor = _memory_controller(reversible=True)
    copy_update = audit_memory_update_injectivity(copy)
    xor_update = audit_memory_update_injectivity(xor)
    copy_closed = audit_deterministic_closed_loop_map(world, copy)
    xor_closed = audit_deterministic_closed_loop_map(world, xor)
    return {
        "world": world,
        "copy_controller": copy,
        "xor_controller": xor,
        "copy_update": copy_update,
        "xor_update": xor_update,
        "copy_closed_loop": copy_closed,
        "xor_closed_loop": xor_closed,
        "world_dynamics_shared": True,
    }


def process_interface_identifiability_summary() -> dict[str, Any]:
    identification = identification_controls()
    common_driver = common_driver_control()
    copied_record = copied_record_control()
    nonidentifiability = observational_nonidentifiability_control()
    census = exact_independence_census()
    memory = memory_injectivity_control()

    case_results = {
        "complete_interface_enumeration": (
            identification["profile_count"]
            == identification["expected_profile_count"]
        ),
        "observational_causal_features_unknown": all(
            profile.feature(feature) is None
            for profile in identification["observational"].profiles
            for feature in (
                "internal_influence",
                "incoming_influence",
                "outgoing_influence",
                "record_acquisition",
                "record_sensitive_outflow",
                "continuation_influence",
            )
        ),
        "identified_positive": (
            identification["identified"].status
            is IdentificationStatus.IDENTIFIED
            and identification["identified"].retained_minimal_interfaces
            == (("inside",),)
        ),
        "set_identified_positive": (
            identification["set_identified"].status
            is IdentificationStatus.SET_IDENTIFIED
            and identification["set_identified"].retained_minimal_interfaces
            == (("left",), ("right",))
        ),
        "observational_query_unresolved": (
            identification["observational"].status
            is IdentificationStatus.UNRESOLVED
        ),
        "annotation_invariance": identification["annotation_invariant"],
        "component_renaming_covariance": identification["renaming_covariant"],
        "feature_dependence_reported": identification["feature_dependent"],
        "common_driver_control": (
            common_driver["descendants_correlated"]
            and common_driver["driver_edges_present"]
            and common_driver["descendant_edge_absent"]
        ),
        "copied_record_control": (
            copied_record["copy_tracks_source_update"]
            and copied_record["copy_tracks_output"]
            and copied_record["copy_to_output_edge_absent"]
            and copied_record["copy_outgoing_influence"] is False
            and not copied_record["copy_primary_certified"]
        ),
        "observational_nonidentifiability": (
            nonidentifiability["observationally_equivalent"]
            and not nonidentifiability["interventionally_equivalent"]
            and nonidentifiability["observational_profiles_equal"]
            and nonidentifiability["observational_status_left"]
            == IdentificationStatus.UNRESOLVED.value
            and nonidentifiability["observational_status_right"]
            == IdentificationStatus.UNRESOLVED.value
            and nonidentifiability["inside_interventional_profiles_differ"]
        ),
        "exhaustive_census": (
            census["enumerated_rule_count"] == census["expected_rule_count"]
        ),
        "record_acquisition_composite": census[
            "record_acquisition_composite_holds"
        ],
        "memory_injectivity_control": (
            not memory["copy_update"].conditionally_injective
            and not memory["copy_closed_loop"].injective
            and memory["copy_closed_loop"].image_size == 2
            and memory["xor_update"].conditionally_injective
            and memory["xor_closed_loop"].injective
            and memory["xor_closed_loop"].image_size == 4
            and memory["world_dynamics_shared"]
        ),
    }
    kill_conditions = {
        "injected_atom_changed_structure": not case_results[
            "annotation_invariance"
        ],
        "component_renaming_changed_structure": not case_results[
            "component_renaming_covariance"
        ],
        "observational_causality_fabricated": not case_results[
            "observational_causal_features_unknown"
        ],
        "common_driver_phantom_edge": not case_results[
            "common_driver_control"
        ],
        "copied_record_phantom_effect": not case_results[
            "copied_record_control"
        ],
        "observational_pair_declared_identified": not case_results[
            "observational_nonidentifiability"
        ],
        "set_identified_representative_selected": not case_results[
            "set_identified_positive"
        ],
        "census_incomplete": not case_results["exhaustive_census"],
        "memory_controls_changed_world": not memory["world_dynamics_shared"],
        "memory_injectivity_control_failed": not case_results[
            "memory_injectivity_control"
        ],
    }
    retained = all(case_results.values()) and not any(kill_conditions.values())
    return {
        "status": "retained" if retained else "failed",
        "verdict": (
            "finite_process_interfaces_set_identified"
            if retained
            else "process_interface_contract_failed"
        ),
        "protocol_doc": PROTOCOL_DOC,
        "horizon": HORIZON,
        "primary_query": {
            "query_id": PRIMARY_PROCESS_QUERY.query_id,
            "required_true": list(PRIMARY_PROCESS_QUERY.required_true),
        },
        "identification": {
            key: value
            for key, value in identification.items()
            if key
            not in {
                "identified_system",
                "observational",
                "identified",
                "secondary",
                "set_system",
                "set_identified",
                "annotated",
                "annotated_result",
                "renamed",
                "renamed_result",
            }
        },
        "common_driver": {
            key: value
            for key, value in common_driver.items()
            if key not in {"system", "edges"}
        },
        "copied_record": {
            "copy_tracks_source_update": copied_record[
                "copy_tracks_source_update"
            ],
            "copy_tracks_output": copied_record["copy_tracks_output"],
            "copy_to_output_edge_absent": copied_record[
                "copy_to_output_edge_absent"
            ],
            "copy_outgoing_influence": copied_record[
                "copy_outgoing_influence"
            ],
            "copy_primary_certified": copied_record[
                "copy_primary_certified"
            ],
            "copy_profile": copied_record["profile"].as_dict(),
            "identification_status": copied_record[
                "identification"
            ].status.value,
        },
        "observational_nonidentifiability": {
            key: value
            for key, value in nonidentifiability.items()
            if key
            not in {
                "left",
                "right",
                "left_observational",
                "right_observational",
                "left_interventional",
                "right_interventional",
            }
        },
        "independence_census": {
            "enumerated_rule_count": census["enumerated_rule_count"],
            "expected_rule_count": census["expected_rule_count"],
            "joint_signature_count": census["joint_signature_count"],
            "record_acquisition_composite_holds": census[
                "record_acquisition_composite_holds"
            ],
            "manifest_digest": census["manifest_digest"],
            "feature_results": census["feature_results"],
        },
        "memory_injectivity": {
            "copy_update": memory["copy_update"].as_dict(),
            "xor_update": memory["xor_update"].as_dict(),
            "copy_closed_loop": memory["copy_closed_loop"].as_dict(),
            "xor_closed_loop": memory["xor_closed_loop"].as_dict(),
            "world_dynamics_shared": memory["world_dynamics_shared"],
        },
        "case_results": case_results,
        "kill_conditions": kill_conditions,
        "claim_boundary": (
            "Finite feature-relative process-interface identification only; "
            "not agency, identity, valuerhood, consciousness, patienthood, "
            "standing, value, responsibility, moral license, or Omega "
            "validation."
        ),
        "_objects": {
            "identification": identification,
            "common_driver": common_driver,
            "copied_record": copied_record,
            "nonidentifiability": nonidentifiability,
            "census": census,
            "memory": memory,
        },
    }


def interface_profile_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    identification = summary["_objects"]["identification"]
    cases = {
        "identified_observational": identification["observational"],
        "identified_interventional": identification["identified"],
        "identified_secondary_query": identification["secondary"],
        "set_identified_interventional": identification["set_identified"],
        "annotated_interventional": identification["annotated_result"],
        "renamed_interventional": identification["renamed_result"],
        "copied_record_interventional": summary["_objects"][
            "copied_record"
        ]["identification"],
    }
    return [
        {
            "case": case,
            "query_id": result.query.query_id,
            "evidence_mode": result.evidence_mode.value,
            "interface": "|".join(profile.interface),
            **{
                feature: (
                    "UNKNOWN"
                    if profile.feature(feature) is None
                    else profile.feature(feature)
                )
                for feature in FEATURE_FIELDS
            },
        }
        for case, result in cases.items()
        for profile in result.profiles
    ]


def identification_result_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    identification = summary["_objects"]["identification"]
    nonidentifiability = summary["_objects"]["nonidentifiability"]
    cases = {
        "identified_observational": identification["observational"],
        "identified_interventional": identification["identified"],
        "identified_secondary_query": identification["secondary"],
        "set_identified_interventional": identification["set_identified"],
        "observational_left": nonidentifiability["left_observational"],
        "observational_right": nonidentifiability["right_observational"],
        "interventional_left": nonidentifiability["left_interventional"],
        "interventional_right": nonidentifiability["right_interventional"],
    }
    return [
        {
            "case": case,
            "query_id": result.query.query_id,
            "evidence_mode": result.evidence_mode.value,
            "status": result.status.value,
            "certified_interfaces": ";".join(
                "|".join(interface)
                for interface in result.certified_interfaces
            ),
            "unresolved_interfaces": ";".join(
                "|".join(interface)
                for interface in result.unresolved_interfaces
            ),
            "retained_minimal_interfaces": ";".join(
                "|".join(interface)
                for interface in result.retained_minimal_interfaces
            ),
        }
        for case, result in cases.items()
    ]


def influence_edge_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    objects = summary["_objects"]
    systems = {
        "identified": objects["identification"]["identified_system"],
        "set_identified": objects["identification"]["set_system"],
        "common_driver": objects["common_driver"]["system"],
        "copied_record": objects["copied_record"]["system"],
        "observational_left": objects["nonidentifiability"]["left"],
        "observational_right": objects["nonidentifiability"]["right"],
    }
    return [
        {
            "case": case,
            **witness.as_dict(),
        }
        for case, system in systems.items()
        for witness in coordinate_influence_witnesses(system)
    ]


def independence_census_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    return list(summary["_objects"]["census"]["rows"])


def independence_witness_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    census = summary["_objects"]["census"]
    rows = []
    census_row_by_code = {
        row["rule_code"]: row for row in census["rows"]
    }
    for feature, result in census["feature_results"].items():
        codes = result["witness_codes"]
        rows.append(
            {
                "feature": feature,
                "verdict": result["verdict"],
                "true_count": result["true_count"],
                "false_count": result["false_count"],
                "left_rule_code": codes[0] if codes else "",
                "right_rule_code": codes[1] if codes else "",
                "left_transition_targets": (
                    census_row_by_code[codes[0]]["transition_targets"]
                    if codes
                    else ""
                ),
                "right_transition_targets": (
                    census_row_by_code[codes[1]]["transition_targets"]
                    if codes
                    else ""
                ),
            }
        )
    return rows


def negative_control_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    return [
        {
            "control": "annotation_invariance",
            "passed": summary["case_results"]["annotation_invariance"],
        },
        {
            "control": "component_renaming_covariance",
            "passed": summary["case_results"][
                "component_renaming_covariance"
            ],
        },
        {
            "control": "common_driver",
            "passed": summary["case_results"]["common_driver_control"],
        },
        {
            "control": "copied_record",
            "passed": summary["case_results"]["copied_record_control"],
        },
        {
            "control": "observational_nonidentifiability",
            "passed": summary["case_results"][
                "observational_nonidentifiability"
            ],
        },
    ]


def memory_injectivity_rows(
    summary: Mapping[str, Any],
) -> list[dict[str, object]]:
    memory = summary["_objects"]["memory"]
    return [
        {
            "controller": label,
            "conditionally_injective": update.conditionally_injective,
            "update_collision_count": len(update.collisions),
            "closed_loop_injective": closed.injective,
            "closed_loop_state_count": closed.state_count,
            "closed_loop_image_size": closed.image_size,
            "closed_loop_collision_count": len(closed.collisions),
        }
        for label, update, closed in (
            (
                "copy",
                memory["copy_update"],
                memory["copy_closed_loop"],
            ),
            (
                "xor",
                memory["xor_update"],
                memory["xor_closed_loop"],
            ),
        )
    ]
