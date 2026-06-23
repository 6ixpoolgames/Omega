"""Shared finite relational fact helpers."""

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


def _total_function_mapping(
    model: FiniteRelationalModel,
    name: str,
    *,
    domain: str,
) -> dict[str, str]:
    function = model.functions[name]
    if function.domain != domain:
        raise SchemaError(
            f"function {name} is over domain {function.domain}, expected {domain}"
        )
    states = model.domain(domain)
    missing = sorted(set(states) - set(function.mapping))
    if missing:
        raise SchemaError(f"function {name} is not total on domain {domain}: {missing}")
    return function.mapping
