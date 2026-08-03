"""Preregistered fixtures for finite process-interface transport v0."""

from __future__ import annotations

import itertools
import json
from typing import Any, Callable

from omega_v2.finite.component_factorizations import (
    ComponentFactorization,
    FactorBlock,
    FactorizedInterfaceIdentification,
    InterfaceFamilyTransport,
    InterfaceTransportStatus,
    audit_intervention_transport,
    compare_interface_families,
    identify_factorized_interfaces,
)
from omega_v2.finite.process_interfaces import (
    PRIMARY_PROCESS_QUERY,
    BinarySynchronousSystem,
    EvidenceMode,
    InterfaceQuery,
    observational_signature,
)


PROTOCOL_DOC = (
    "docs/research_notes/omega_v2/"
    "process_interface_transport_protocol_v0.md"
)
HORIZON = 4
OUTFLOW_QUERY = InterfaceQuery(
    query_id="persistent_causal_outflow",
    required_true=(
        "persistent_variation",
        "outgoing_influence",
        "continuation_influence",
    ),
)
PERSISTENCE_QUERY = InterfaceQuery(
    query_id="persistent_variation_only",
    required_true=("persistent_variation",),
)


def refinement_system() -> BinarySynchronousSystem:
    """Identified two-bit fixture with one causally inert auxiliary bit."""

    states = tuple(itertools.product((0, 1), repeat=3))
    base_targets = {
        (0, 0): (0, 1),
        (0, 1): (0, 0),
        (1, 0): (1, 0),
        (1, 1): (0, 0),
    }
    return BinarySynchronousSystem(
        system_id="factorization_refinement_system",
        component_ids=("inside", "aux", "outside"),
        transition_rows=tuple(
            (
                state,
                (
                    base_targets[(state[0], state[2])][0],
                    0,
                    base_targets[(state[0], state[2])][1],
                ),
            )
            for state in states
        ),
        initial_states=((0, 0, 0), (1, 0, 0)),
    )


def refinement_factorizations() -> tuple[
    ComponentFactorization,
    ComponentFactorization,
    ComponentFactorization,
]:
    primitive_ids = ("inside", "aux", "outside")
    coarse = ComponentFactorization.from_mapping(
        factorization_id="coarse_core",
        primitive_ids=primitive_ids,
        blocks={
            "core": ("inside", "aux"),
            "environment": ("outside",),
        },
    )
    fine = ComponentFactorization.from_mapping(
        factorization_id="fine_components",
        primitive_ids=primitive_ids,
        blocks={
            "inside_block": ("inside",),
            "aux_block": ("aux",),
            "outside_block": ("outside",),
        },
    )
    relabeled = ComponentFactorization.from_mapping(
        factorization_id="fine_components_relabeled",
        primitive_ids=primitive_ids,
        blocks={
            "alpha": ("inside",),
            "beta": ("aux",),
            "gamma": ("outside",),
        },
    )
    return coarse, fine, relabeled


def _identify(
    system: BinarySynchronousSystem,
    factorization: ComponentFactorization,
    query: InterfaceQuery = PRIMARY_PROCESS_QUERY,
    *,
    evidence_mode: EvidenceMode = EvidenceMode.INTERVENTIONAL,
) -> FactorizedInterfaceIdentification:
    return identify_factorized_interfaces(
        system,
        factorization,
        query,
        evidence_mode=evidence_mode,
        horizon=HORIZON,
    )


def refinement_controls() -> dict[str, Any]:
    system = refinement_system()
    coarse, fine, relabeled = refinement_factorizations()
    coarse_result = _identify(system, coarse)
    fine_result = _identify(system, fine)
    relabeled_result = _identify(system, relabeled)

    relabel_transport = compare_interface_families(
        fine_result,
        relabeled_result,
    )
    refined_transport = compare_interface_families(
        coarse_result,
        fine_result,
    )
    merged_transport = compare_interface_families(
        fine_result,
        coarse_result,
    )

    annotated = system.with_state_atom(
        "agent",
        system_id="factorization_refinement_annotated",
    )
    annotated_fine = _identify(annotated, fine)
    annotation_transport = compare_interface_families(
        fine_result,
        annotated_fine,
    )

    observational_coarse = _identify(
        system,
        coarse,
        evidence_mode=EvidenceMode.OBSERVATIONAL,
    )
    observational_fine = _identify(
        system,
        fine,
        evidence_mode=EvidenceMode.OBSERVATIONAL,
    )
    observational_transport = compare_interface_families(
        observational_coarse,
        observational_fine,
    )

    mismatch_result = _identify(system, fine, OUTFLOW_QUERY)
    query_mismatch = compare_interface_families(
        fine_result,
        mismatch_result,
    )

    return {
        "system": system,
        "factorizations": (coarse, fine, relabeled),
        "coarse_result": coarse_result,
        "fine_result": fine_result,
        "relabeled_result": relabeled_result,
        "relabel_transport": relabel_transport,
        "refined_transport": refined_transport,
        "merged_transport": merged_transport,
        "annotation_transport": annotation_transport,
        "observational_transport": observational_transport,
        "query_mismatch": query_mismatch,
    }


def several_minima_system() -> BinarySynchronousSystem:
    """Symmetric pair with a shared outflow coordinate."""

    return BinarySynchronousSystem.from_update_function(
        system_id="several_refined_minima",
        component_ids=("left", "right", "sink"),
        update=lambda state: (
            state[1],
            state[0],
            state[0] ^ state[1],
        ),
        initial_states=tuple(itertools.product((0, 1), repeat=3)),
    )


def several_minima_controls() -> dict[str, Any]:
    system = several_minima_system()
    primitive_ids = system.component_ids
    coarse = ComponentFactorization.from_mapping(
        factorization_id="coarse_symmetric_pair",
        primitive_ids=primitive_ids,
        blocks={
            "pair": ("left", "right"),
            "sink": ("sink",),
        },
    )
    fine = ComponentFactorization.from_mapping(
        factorization_id="fine_symmetric_pair",
        primitive_ids=primitive_ids,
        blocks={
            "left": ("left",),
            "right": ("right",),
            "sink": ("sink",),
        },
    )
    coarse_result = _identify(system, coarse, OUTFLOW_QUERY)
    fine_result = _identify(system, fine, OUTFLOW_QUERY)
    transport = compare_interface_families(coarse_result, fine_result)
    return {
        "system": system,
        "factorizations": (coarse, fine),
        "coarse_result": coarse_result,
        "fine_result": fine_result,
        "transport": transport,
    }


def crosscut_system() -> BinarySynchronousSystem:
    """Four-bit reversible rotation used only to expose partition crossing."""

    return BinarySynchronousSystem.from_update_function(
        system_id="crosscut_rotation",
        component_ids=("a", "b", "c", "d"),
        update=lambda state: (state[3], state[0], state[1], state[2]),
        initial_states=tuple(itertools.product((0, 1), repeat=4)),
    )


def crosscut_controls() -> dict[str, Any]:
    system = crosscut_system()
    primitive_ids = system.component_ids
    source = ComponentFactorization.from_mapping(
        factorization_id="crosscut_source",
        primitive_ids=primitive_ids,
        blocks={
            "ab": ("a", "b"),
            "cd": ("c", "d"),
        },
    )
    target = ComponentFactorization.from_mapping(
        factorization_id="crosscut_target",
        primitive_ids=primitive_ids,
        blocks={
            "ac": ("a", "c"),
            "bd": ("b", "d"),
        },
    )
    source_result = _identify(system, source, PERSISTENCE_QUERY)
    target_result = _identify(system, target, PERSISTENCE_QUERY)
    forward = audit_intervention_transport(source, target)
    reverse = audit_intervention_transport(target, source)
    transport = compare_interface_families(source_result, target_result)
    source_ab_saturation = target.saturate(("a", "b"))
    return {
        "system": system,
        "factorizations": (source, target),
        "source_result": source_result,
        "target_result": target_result,
        "forward": forward,
        "reverse": reverse,
        "transport": transport,
        "source_ab_saturation": source_ab_saturation,
        "same_observational_signature": (
            observational_signature(system, horizon=HORIZON)
            == observational_signature(system, horizon=HORIZON)
        ),
    }


def _raises_value_error(callback: Callable[[], object]) -> bool:
    try:
        callback()
    except ValueError:
        return True
    return False


def partition_validation_controls() -> dict[str, bool]:
    primitive_ids = ("a", "b")
    return {
        "empty_block_rejected": _raises_value_error(
            lambda: ComponentFactorization(
                factorization_id="invalid_empty",
                primitive_ids=primitive_ids,
                blocks=(
                    FactorBlock("empty", ()),
                    FactorBlock("rest", ("a", "b")),
                ),
            )
        ),
        "overlap_rejected": _raises_value_error(
            lambda: ComponentFactorization.from_mapping(
                factorization_id="invalid_overlap",
                primitive_ids=primitive_ids,
                blocks={
                    "left": ("a",),
                    "right": ("a", "b"),
                },
            )
        ),
        "omission_rejected": _raises_value_error(
            lambda: ComponentFactorization.from_mapping(
                factorization_id="invalid_omission",
                primitive_ids=primitive_ids,
                blocks={"left": ("a",)},
            )
        ),
    }


def _transport_payload(
    transport: InterfaceFamilyTransport,
) -> dict[str, object]:
    return {
        "source_factorization_id": transport.source_factorization_id,
        "target_factorization_id": transport.target_factorization_id,
        "source_query_id": transport.source_query_id,
        "target_query_id": transport.target_query_id,
        "source_evidence_mode": transport.source_evidence_mode.value,
        "target_evidence_mode": transport.target_evidence_mode.value,
        "source_horizon": transport.source_horizon,
        "target_horizon": transport.target_horizon,
        "status": transport.status.value,
        "reason": transport.reason,
        "source_minimal_interfaces": [
            list(interface)
            for interface in transport.source_minimal_interfaces
        ],
        "target_minimal_interfaces": [
            list(interface)
            for interface in transport.target_minimal_interfaces
        ],
        "forward_exact": transport.forward_intervention_audit.exact,
        "reverse_exact": transport.reverse_intervention_audit.exact,
        "forward_failure_count": len(
            transport.forward_intervention_audit.failures
        ),
        "reverse_failure_count": len(
            transport.reverse_intervention_audit.failures
        ),
        "target_saturations": [
            saturation.as_dict()
            for saturation in transport.target_saturations
        ],
    }


def _identification_payload(
    result: FactorizedInterfaceIdentification,
) -> dict[str, object]:
    return {
        "system_id": result.system_id,
        "factorization_id": result.factorization.factorization_id,
        "query_id": result.query.query_id,
        "evidence_mode": result.evidence_mode.value,
        "horizon": result.horizon,
        "status": result.status.value,
        "certified_block_interfaces": [
            list(interface)
            for interface in result.certified_block_interfaces
        ],
        "unresolved_block_interfaces": [
            list(interface)
            for interface in result.unresolved_block_interfaces
        ],
        "rejected_block_interfaces": [
            list(interface)
            for interface in result.rejected_block_interfaces
        ],
        "retained_minimal_block_interfaces": [
            list(interface)
            for interface in result.retained_minimal_block_interfaces
        ],
        "retained_minimal_primitive_interfaces": [
            list(interface)
            for interface in result.retained_minimal_primitive_interfaces
        ],
    }


def run_experiment() -> dict[str, Any]:
    refinement = refinement_controls()
    several = several_minima_controls()
    crosscut = crosscut_controls()
    partition = partition_validation_controls()

    relabel = refinement["relabel_transport"]
    refined = refinement["refined_transport"]
    merged = refinement["merged_transport"]
    annotation = refinement["annotation_transport"]
    observational = refinement["observational_transport"]
    query_mismatch = refinement["query_mismatch"]
    several_transport = several["transport"]
    crosscut_transport = crosscut["transport"]

    case_results = {
        "partition_validation": all(partition.values()),
        "block_relabeling_invariant": (
            relabel.status is InterfaceTransportStatus.INVARIANT
            and relabel.forward_intervention_audit.exact
            and relabel.reverse_intervention_audit.exact
        ),
        "strict_refinement_detected": (
            refined.status is InterfaceTransportStatus.REFINED
            and refined.forward_intervention_audit.exact
        ),
        "reverse_merge_detected": (
            merged.status is InterfaceTransportStatus.MERGED
            and merged.reverse_intervention_audit.exact
        ),
        "several_refined_minima_retained": (
            several_transport.status is InterfaceTransportStatus.REFINED
            and len(
                several["fine_result"].retained_minimal_primitive_interfaces
            )
            == 2
        ),
        "crosscut_obstructed": (
            crosscut_transport.status is InterfaceTransportStatus.OBSTRUCTED
            and not crosscut["forward"].exact
            and not crosscut["reverse"].exact
        ),
        "crosscut_failure_witnessed": (
            bool(crosscut["forward"].failures)
            and bool(crosscut["reverse"].failures)
            and bool(crosscut["source_ab_saturation"].added_members)
        ),
        "query_mismatch_obstructed": (
            query_mismatch.status is InterfaceTransportStatus.OBSTRUCTED
            and query_mismatch.reason == "query_mismatch"
        ),
        "annotation_invariance": (
            annotation.status is InterfaceTransportStatus.INVARIANT
        ),
        "observational_transport_unresolved": (
            observational.status is InterfaceTransportStatus.UNRESOLVED
        ),
        "observation_does_not_override_crosscut": (
            crosscut["same_observational_signature"]
            and crosscut_transport.status
            is InterfaceTransportStatus.OBSTRUCTED
        ),
    }
    kill_conditions = {
        "invalid_partition_accepted": not all(partition.values()),
        "relabeling_changed_family": (
            relabel.status is not InterfaceTransportStatus.INVARIANT
        ),
        "refinement_not_decomposable": (
            not refined.forward_intervention_audit.exact
        ),
        "merge_reported_exact_forward": (
            merged.forward_intervention_audit.exact
        ),
        "refined_representative_selected": (
            len(
                several["fine_result"].retained_minimal_primitive_interfaces
            )
            != 2
        ),
        "crosscut_called_exact": (
            crosscut["forward"].exact or crosscut["reverse"].exact
        ),
        "saturation_silently_accepted": (
            crosscut["source_ab_saturation"].exact
            or crosscut_transport.status
            is not InterfaceTransportStatus.OBSTRUCTED
        ),
        "query_mismatch_called_invariant": (
            query_mismatch.status is InterfaceTransportStatus.INVARIANT
        ),
        "observational_causality_claimed": (
            observational.status is not InterfaceTransportStatus.UNRESOLVED
        ),
    }
    return {
        "status": (
            "retained"
            if all(case_results.values())
            and not any(kill_conditions.values())
            else "failed"
        ),
        "verdict": "finite_process_interface_transport_classified",
        "protocol_doc": PROTOCOL_DOC,
        "horizon": HORIZON,
        "claim_boundary": (
            "Finite factorization-relative interface transport only; not "
            "identity, agency, valuerhood, consciousness, patienthood, "
            "standing, value, responsibility, moral license, or Omega "
            "validation."
        ),
        "case_results": case_results,
        "kill_conditions": kill_conditions,
        "partition_validation": partition,
        "refinement": {
            "coarse_result": _identification_payload(
                refinement["coarse_result"]
            ),
            "fine_result": _identification_payload(
                refinement["fine_result"]
            ),
            "relabel_transport": _transport_payload(relabel),
            "refined_transport": _transport_payload(refined),
            "merged_transport": _transport_payload(merged),
            "annotation_transport": _transport_payload(annotation),
            "observational_transport": _transport_payload(observational),
            "query_mismatch": _transport_payload(query_mismatch),
        },
        "several_minima": {
            "coarse_result": _identification_payload(
                several["coarse_result"]
            ),
            "fine_result": _identification_payload(
                several["fine_result"]
            ),
            "transport": _transport_payload(several_transport),
        },
        "crosscut": {
            "source_result": _identification_payload(
                crosscut["source_result"]
            ),
            "target_result": _identification_payload(
                crosscut["target_result"]
            ),
            "forward_audit": crosscut["forward"].as_dict(),
            "reverse_audit": crosscut["reverse"].as_dict(),
            "transport": _transport_payload(crosscut_transport),
            "source_ab_saturation": (
                crosscut["source_ab_saturation"].as_dict()
            ),
            "same_observational_signature": crosscut[
                "same_observational_signature"
            ],
        },
        "_objects": {
            "factorizations": (
                *refinement["factorizations"],
                *several["factorizations"],
                *crosscut["factorizations"],
            ),
            "identifications": (
                refinement["coarse_result"],
                refinement["fine_result"],
                refinement["relabeled_result"],
                several["coarse_result"],
                several["fine_result"],
                crosscut["source_result"],
                crosscut["target_result"],
            ),
            "transports": (
                relabel,
                refined,
                merged,
                annotation,
                observational,
                query_mismatch,
                several_transport,
                crosscut_transport,
            ),
        },
    }


def factorization_rows(result: dict[str, Any]) -> list[dict[str, object]]:
    seen: set[str] = set()
    rows: list[dict[str, object]] = []
    for factorization in result["_objects"]["factorizations"]:
        if factorization.factorization_id in seen:
            continue
        seen.add(factorization.factorization_id)
        for block in factorization.blocks:
            rows.append(
                {
                    "factorization_id": factorization.factorization_id,
                    "primitive_ids": json.dumps(
                        factorization.primitive_ids
                    ),
                    "block_id": block.block_id,
                    "members": json.dumps(block.members),
                }
            )
    return rows


def block_transport_rows(result: dict[str, Any]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for family_transport in result["_objects"]["transports"]:
        for audit in (
            family_transport.forward_intervention_audit,
            family_transport.reverse_intervention_audit,
        ):
            key = (
                audit.source_factorization_id,
                audit.target_factorization_id,
            )
            if key in seen:
                continue
            seen.add(key)
            for transport in audit.transports:
                rows.append(
                    {
                        "source_factorization_id": (
                            audit.source_factorization_id
                        ),
                        "target_factorization_id": (
                            audit.target_factorization_id
                        ),
                        "audit_exact": audit.exact,
                        "row_kind": "transport",
                        "source_block_id": transport.source_block_id,
                        "source_members": json.dumps(
                            transport.source_members
                        ),
                        "target_block_ids": json.dumps(
                            transport.target_block_ids
                        ),
                        "target_members": json.dumps(
                            transport.target_members
                        ),
                        "missing_source_members": "[]",
                        "added_target_members": "[]",
                    }
                )
            for failure in audit.failures:
                rows.append(
                    {
                        "source_factorization_id": (
                            audit.source_factorization_id
                        ),
                        "target_factorization_id": (
                            audit.target_factorization_id
                        ),
                        "audit_exact": audit.exact,
                        "row_kind": "failure",
                        "source_block_id": failure.source_block_id,
                        "source_members": json.dumps(
                            failure.source_members
                        ),
                        "target_block_ids": json.dumps(
                            failure.overlapping_target_block_ids
                        ),
                        "target_members": json.dumps(
                            failure.overlapping_target_members
                        ),
                        "missing_source_members": json.dumps(
                            failure.missing_source_members
                        ),
                        "added_target_members": json.dumps(
                            failure.added_target_members
                        ),
                    }
                )
    return rows


def factorized_profile_rows(result: dict[str, Any]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for identification in result["_objects"]["identifications"]:
        minimal = set(identification.retained_minimal_block_interfaces)
        certified = set(identification.certified_block_interfaces)
        unresolved = set(identification.unresolved_block_interfaces)
        for profile in identification.profiles:
            if profile.block_interface in certified:
                classification = "certified"
            elif profile.block_interface in unresolved:
                classification = "unresolved"
            else:
                classification = "rejected"
            rows.append(
                {
                    "system_id": identification.system_id,
                    "factorization_id": (
                        identification.factorization.factorization_id
                    ),
                    "query_id": identification.query.query_id,
                    "evidence_mode": identification.evidence_mode.value,
                    "status": identification.status.value,
                    "classification": classification,
                    "minimal": profile.block_interface in minimal,
                    "block_interface": json.dumps(
                        profile.block_interface
                    ),
                    "primitive_interface": json.dumps(
                        profile.primitive_interface
                    ),
                    **{
                        feature: (
                            "UNKNOWN"
                            if profile.profile.feature(feature) is None
                            else profile.profile.feature(feature)
                        )
                        for feature in (
                            "persistent_variation",
                            "internal_influence",
                            "incoming_influence",
                            "outgoing_influence",
                            "latent_state_multiplicity",
                            "record_acquisition",
                            "record_sensitive_outflow",
                            "continuation_influence",
                        )
                    },
                }
            )
    return rows


def family_transport_rows(result: dict[str, Any]) -> list[dict[str, object]]:
    return [
        {
            "source_factorization_id": transport.source_factorization_id,
            "target_factorization_id": transport.target_factorization_id,
            "source_query_id": transport.source_query_id,
            "target_query_id": transport.target_query_id,
            "source_evidence_mode": transport.source_evidence_mode.value,
            "target_evidence_mode": transport.target_evidence_mode.value,
            "source_horizon": transport.source_horizon,
            "target_horizon": transport.target_horizon,
            "status": transport.status.value,
            "reason": transport.reason,
            "source_minimal_interfaces": json.dumps(
                transport.source_minimal_interfaces
            ),
            "target_minimal_interfaces": json.dumps(
                transport.target_minimal_interfaces
            ),
            "forward_exact": transport.forward_intervention_audit.exact,
            "reverse_exact": transport.reverse_intervention_audit.exact,
            "target_saturations": json.dumps(
                [
                    saturation.as_dict()
                    for saturation in transport.target_saturations
                ],
                sort_keys=True,
            ),
        }
        for transport in result["_objects"]["transports"]
    ]


def negative_control_rows(result: dict[str, Any]) -> list[dict[str, object]]:
    rows = [
        {
            "control": control,
            "passed": passed,
        }
        for control, passed in result["case_results"].items()
        if control
        in {
            "partition_validation",
            "crosscut_obstructed",
            "crosscut_failure_witnessed",
            "query_mismatch_obstructed",
            "annotation_invariance",
            "observational_transport_unresolved",
            "observation_does_not_override_crosscut",
        }
    ]
    rows.extend(
        {
            "control": f"kill::{condition}",
            "passed": not fired,
        }
        for condition, fired in result["kill_conditions"].items()
    )
    return rows
