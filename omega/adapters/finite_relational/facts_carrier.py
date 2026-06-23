"""Carrier certificate and transfer facts."""

from __future__ import annotations

from omega.adapters.finite_relational.facts_common import (
    binary_relation,
    internal_edges,
    reachable_pairs,
)
from omega.adapters.finite_relational.model import FiniteRelationalModel

def carrier_certificate_facts(
    model: FiniteRelationalModel,
    *,
    transition: str,
    safety: str,
    carrier: str,
    left: str,
    right: str,
    separation: str,
) -> dict[str, object]:
    edges = binary_relation(model, transition)
    safe_states = set(model.predicate_members(safety))
    carrier_states = set(model.predicate_members(carrier))
    separated = binary_relation(model, separation)
    internal = internal_edges(edges, carrier_states)
    internal_reach = reachable_pairs(carrier_states, internal) if carrier_states else set()

    no_exits = all(target in carrier_states for source, target in edges if source in carrier_states)
    all_safe = carrier_states <= safe_states
    endpoints_in_carrier = left in carrier_states and right in carrier_states
    endpoints_separated = (left, right) in separated or (right, left) in separated
    mutually_reachable = endpoints_in_carrier and (left, right) in internal_reach and (right, left) in internal_reach
    internally_connected = all(
        (source, target) in internal_reach
        for source in carrier_states
        for target in carrier_states
    )

    certified = (
        bool(carrier_states)
        and endpoints_in_carrier
        and endpoints_separated
        and all_safe
        and no_exits
        and internally_connected
        and mutually_reachable
    )

    return {
        "certified": certified,
        "carrier_size": len(carrier_states),
        "endpoints_in_carrier": endpoints_in_carrier,
        "endpoints_separated": endpoints_separated,
        "all_safe": all_safe,
        "no_exits": no_exits,
        "internally_connected": internally_connected,
        "mutually_reachable": mutually_reachable,
    }


def carrier_transfer_facts(
    model: FiniteRelationalModel,
    *,
    source_transition: str,
    source_safety: str,
    source_carrier: str,
    source_left: str,
    source_right: str,
    source_separation: str,
    target_transition: str,
    target_safety: str,
    target_carrier: str,
    target_left: str,
    target_right: str,
    target_separation: str,
    correspondence: str,
) -> dict[str, object]:
    source_facts = carrier_certificate_facts(
        model,
        transition=source_transition,
        safety=source_safety,
        carrier=source_carrier,
        left=source_left,
        right=source_right,
        separation=source_separation,
    )
    target_facts = carrier_certificate_facts(
        model,
        transition=target_transition,
        safety=target_safety,
        carrier=target_carrier,
        left=target_left,
        right=target_right,
        separation=target_separation,
    )
    correspondence_pairs = binary_relation(model, correspondence)
    source_members = set(model.predicate_members(source_carrier))
    target_members = set(model.predicate_members(target_carrier))

    endpoint_correspondence = (
        (source_left, target_left) in correspondence_pairs
        and (source_right, target_right) in correspondence_pairs
    )
    correspondence_total_on_source_carrier = all(
        any((source, target) in correspondence_pairs for target in target_members)
        for source in source_members
    )
    correspondence_stays_in_target_carrier = all(
        target in target_members
        for source, target in correspondence_pairs
        if source in source_members
    )
    transferred = (
        bool(source_facts["certified"])
        and bool(target_facts["certified"])
        and endpoint_correspondence
        and correspondence_total_on_source_carrier
        and correspondence_stays_in_target_carrier
    )

    return {
        "transferred": transferred,
        "source_certified": source_facts["certified"],
        "target_certified": target_facts["certified"],
        "endpoint_correspondence": endpoint_correspondence,
        "correspondence_total_on_source_carrier": correspondence_total_on_source_carrier,
        "correspondence_stays_in_target_carrier": correspondence_stays_in_target_carrier,
        "source": source_facts,
        "target": target_facts,
    }
