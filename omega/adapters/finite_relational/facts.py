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
