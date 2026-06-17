"""Derived finite facts for the finite relational adapter."""

from __future__ import annotations

from collections import defaultdict, deque
from itertools import product

from omega.adapters.finite_relational.model import FiniteRelationalModel, SchemaError


Pair = tuple[str, str]


def binary_relation(model: FiniteRelationalModel, name: str) -> set[Pair]:
    relation = model.relations[name]
    if relation.arity != 2:
        raise SchemaError(f"relation {name} must be binary")
    return {(left, right) for left, right in relation.tuples}


def ternary_relation(model: FiniteRelationalModel, name: str) -> set[tuple[str, str, str]]:
    relation = model.relations[name]
    if relation.arity != 3:
        raise SchemaError(f"relation {name} must be ternary")
    return {(a, b, c) for a, b, c in relation.tuples}


def reachable_pairs(states: set[str], edges: set[Pair]) -> set[Pair]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for source, target in edges:
        adjacency[source].add(target)

    reachable: set[Pair] = set()
    for source in states:
        seen = {source}
        queue = deque([source])
        while queue:
            current = queue.popleft()
            reachable.add((source, current))
            for target in adjacency[current]:
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
    return reachable


def internal_edges(edges: set[Pair], carrier: set[str]) -> set[Pair]:
    return {(source, target) for source, target in edges if source in carrier and target in carrier}


def function_merges(model: FiniteRelationalModel, name: str) -> set[Pair]:
    function = model.functions[name]
    states = model.domain(function.domain)
    missing = sorted(set(states) - set(function.mapping))
    if missing:
        raise SchemaError(f"function {name} is not total on domain {function.domain}: {missing}")
    return {
        (left, right)
        for left, right in product(states, states)
        if left != right and function.mapping[left] == function.mapping[right]
    }


def presentation_violations(
    model: FiniteRelationalModel,
    *,
    presentation: str,
    forbidden: str,
) -> list[Pair]:
    merges = function_merges(model, presentation)
    forbidden_pairs = binary_relation(model, forbidden)
    return sorted(merges & forbidden_pairs)


def nonfactorization_witnesses_for_predicate(
    model: FiniteRelationalModel,
    *,
    summary: str,
    target_predicate: str,
) -> list[Pair]:
    function = model.functions[summary]
    states = model.domain(function.domain)
    missing = sorted(set(states) - set(function.mapping))
    if missing:
        raise SchemaError(f"summary function {summary} is not total on {function.domain}: {missing}")
    target = model.predicate_members(target_predicate)
    witnesses = []
    for left, right in product(states, states):
        if left >= right:
            continue
        same_summary = function.mapping[left] == function.mapping[right]
        target_differs = (left in target) != (right in target)
        if same_summary and target_differs:
            witnesses.append((left, right))
    return witnesses


def bounded_recovery_facts(
    model: FiniteRelationalModel,
    *,
    observation: str,
    target_predicate: str,
    decoders: tuple[str, ...],
    true_label: str = "true",
    false_label: str = "false",
) -> dict[str, object]:
    """Check exact recovery by a declared bounded decoder family.

    The audit is intentionally family-relative: failure means no declared
    decoder recovers the target from the observation, not that no possible
    decoder exists in a richer class.
    """

    if not decoders:
        raise SchemaError("bounded recovery must declare at least one decoder")

    observation_function = model.functions[observation]
    target = model.predicates[target_predicate]
    if target.domain != observation_function.domain:
        raise SchemaError(
            "bounded recovery target predicate and observation function "
            f"must share a domain: {target.domain} != {observation_function.domain}"
        )

    states = model.domain(observation_function.domain)
    missing_states = sorted(set(states) - set(observation_function.mapping))
    if missing_states:
        raise SchemaError(
            f"observation function {observation} is not total on "
            f"{observation_function.domain}: {missing_states}"
        )

    target_members = target.members
    observed_labels = sorted({observation_function.mapping[state] for state in states})
    decoder_results: list[dict[str, object]] = []
    successful_decoders: list[str] = []
    failed_decoders: list[str] = []

    for decoder_name in decoders:
        decoder = model.functions[decoder_name]
        missing_labels = sorted(set(observed_labels) - set(decoder.mapping))
        if missing_labels:
            raise SchemaError(
                f"decoder {decoder_name} is not total on observed labels "
                f"from {observation}: {missing_labels}"
            )
        mismatches = []
        for state in states:
            observed = observation_function.mapping[state]
            predicted = decoder.mapping[observed]
            expected = true_label if state in target_members else false_label
            if predicted != expected:
                mismatches.append(
                    {
                        "state": state,
                        "observation": observed,
                        "predicted": predicted,
                        "expected": expected,
                    }
                )
        succeeds = not mismatches
        if succeeds:
            successful_decoders.append(decoder_name)
        else:
            failed_decoders.append(decoder_name)
        decoder_results.append(
            {
                "decoder": decoder_name,
                "succeeds": succeeds,
                "mismatch_count": len(mismatches),
                "mismatches": mismatches,
            }
        )

    ambiguous_labels = []
    for label in observed_labels:
        preimage = [state for state in states if observation_function.mapping[state] == label]
        target_values = {state in target_members for state in preimage}
        if len(target_values) > 1:
            ambiguous_labels.append(label)

    return {
        "recoverable": bool(successful_decoders),
        "state_count": len(states),
        "observed_labels": observed_labels,
        "ambiguous_observation_labels": ambiguous_labels,
        "decoder_count": len(decoders),
        "successful_decoders": successful_decoders,
        "failed_decoders": failed_decoders,
        "decoder_results": decoder_results,
    }


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
