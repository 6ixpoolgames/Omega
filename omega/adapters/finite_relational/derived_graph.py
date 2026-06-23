"""Compile small declared graph sources into finite relational adapter models."""

from __future__ import annotations

import json
from collections import defaultdict, deque
from itertools import product
from pathlib import Path
from typing import Any

from omega.adapters.finite_relational.model import SchemaError, load_model
from omega.adapters.finite_relational.source_contract import assert_no_reserved_ir_fields


def load_derived_graph_path(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compile_derived_graph_path(path: Path) -> dict[str, Any]:
    return compile_derived_graph(load_derived_graph_path(path))


def compile_derived_graph(raw: dict[str, Any]) -> dict[str, Any]:
    """Compile a graph source into the lower-level finite relational IR.

    The source declares graph observations and presentations. It does not
    declare `Rel`, `Sep`, `Asym`, carrier predicates, profiles, or audits.
    Those surfaces are derived mechanically from the declared graph fields.
    """

    assert_no_reserved_ir_fields(raw, source_kind="derived graph")
    model_id = str(raw.get("model_id", "derived_graph"))
    nodes = _unique_string_list(raw.get("nodes"), "nodes")
    node_set = set(nodes)
    edges = _edge_list(raw.get("edges", []), node_set, "edges")
    observations = _observations(raw.get("observations", {}), node_set)
    presentations = _presentations(raw.get("presentations", {}), node_set)
    provenance = _dict(raw.get("provenance", {}), "provenance")

    safe_members = _safety(raw.get("safety", "all"), node_set)
    distinction_names = list(observations)
    primitive_sep = _derive_sep(nodes, observations)
    primitive_asym = _derive_strict_edge_asym(edges, observations)
    merge_separated = sorted({(x, y) for _d, x, y in primitive_sep})

    predicates: dict[str, Any] = {"safe": safe_members}
    profiles: dict[str, dict[str, str]] = {
        "alpha_derived": {
            "kind": "alpha",
            "rel": "primitive_rel",
            "sep": "primitive_sep",
            "asym": "primitive_asym",
        }
    }
    audits = _generated_alpha_audits()

    functions = {
        name: {"domain": "state", "mapping": mapping}
        for name, mapping in presentations.items()
    }
    audits.extend(_generated_presentation_audits(raw, presentations))

    carrier_profiles, carrier_predicates, carrier_audits = _generated_carriers(
        nodes=nodes,
        edges=edges,
        separated_pairs=set(merge_separated),
    )
    predicates.update(carrier_predicates)
    profiles.update(carrier_profiles)
    audits.extend(carrier_audits)

    compiled = {
        "model_id": f"compiled_{model_id}",
        "schema_version": "0.1.0",
        "domains": {
            "state": nodes,
            "distinction": distinction_names,
        },
        "predicates": predicates,
        "relations": {
            "next": {
                "domains": ["state", "state"],
                "tuples": [list(edge) for edge in edges],
            },
            "primitive_rel": {
                "domains": ["state", "state"],
                "tuples": [list(edge) for edge in edges],
            },
            "primitive_sep": {
                "domains": ["distinction", "state", "state"],
                "tuples": [list(item) for item in primitive_sep],
            },
            "primitive_asym": {
                "domains": ["distinction", "state", "state"],
                "tuples": [list(item) for item in primitive_asym],
            },
            "merge_separated": {
                "domains": ["state", "state"],
                "tuples": [list(pair) for pair in merge_separated],
            },
        },
        "functions": functions,
        "profiles": profiles,
        "audits": audits,
        "provenance": provenance
        | {
            "compiled_from": "derived_graph",
            "source_model_id": model_id,
            "derivation_rules": [
                "Rel=edge",
                "Sep=observation_differs",
                "Asym=strict_directed_edge_and_observation_differs",
                "merge_separated=exists_observation_difference",
                "carrier=mutual_reach_component_with_separated_pair",
            ],
        },
    }
    load_model(compiled)
    return compiled


def _generated_alpha_audits() -> list[dict[str, Any]]:
    return [
        {
            "id": "derived_alpha_laws",
            "kind": "alpha_laws",
            "profile": "alpha_derived",
            "expect": "alpha_laws_hold",
        }
    ]


def _generated_presentation_audits(
    raw: dict[str, Any],
    presentations: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    expectations = _dict(raw.get("presentation_expectations", {}), "presentation_expectations")
    audits = []
    for name in sorted(presentations):
        audit: dict[str, Any] = {
            "id": f"presentation_{name}",
            "kind": "sound_presentation",
            "presentation": name,
            "forbidden": "merge_separated",
        }
        if name in expectations:
            audit["expect"] = str(expectations[name])
        audits.append(audit)
    return audits


def _generated_carriers(
    *,
    nodes: list[str],
    edges: list[tuple[str, str]],
    separated_pairs: set[tuple[str, str]],
) -> tuple[dict[str, dict[str, str]], dict[str, list[str]], list[dict[str, Any]]]:
    profiles: dict[str, dict[str, str]] = {}
    predicates: dict[str, list[str]] = {}
    audits: list[dict[str, Any]] = []
    for index, component in enumerate(_mutual_reach_components(nodes, edges)):
        pair = _first_separated_pair(component, separated_pairs)
        if pair is None:
            continue
        name = f"carrier_{index}"
        predicates[name] = component
        profiles[name] = {
            "kind": "carrier",
            "transition": "next",
            "safety": "safe",
            "carrier": name,
            "separation": "merge_separated",
        }
        left, right = pair
        audits.append(
            {
                "id": f"{name}_certificate",
                "kind": "carrier_certificate",
                "profile": name,
                "left": left,
                "right": right,
                "expect": "certified",
            }
        )
    return profiles, predicates, audits


def _derive_sep(
    nodes: list[str],
    observations: dict[str, dict[str, str]],
) -> list[tuple[str, str, str]]:
    sep = []
    for distinction, mapping in observations.items():
        for left, right in product(nodes, nodes):
            if left != right and mapping[left] != mapping[right]:
                sep.append((distinction, left, right))
    return sorted(sep)


def _derive_strict_edge_asym(
    edges: list[tuple[str, str]],
    observations: dict[str, dict[str, str]],
) -> list[tuple[str, str, str]]:
    edge_set = set(edges)
    asym = []
    for left, right in edges:
        if (right, left) in edge_set:
            continue
        for distinction, mapping in observations.items():
            if mapping[left] != mapping[right]:
                asym.append((distinction, left, right))
    return sorted(asym)


def _mutual_reach_components(nodes: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
    reach = _reachable_pairs(nodes, edges)
    remaining = set(nodes)
    components = []
    for node in nodes:
        if node not in remaining:
            continue
        component = [other for other in nodes if (node, other) in reach and (other, node) in reach]
        for member in component:
            remaining.discard(member)
        components.append(component)
    return components


def _reachable_pairs(nodes: list[str], edges: list[tuple[str, str]]) -> set[tuple[str, str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for source, target in edges:
        adjacency[source].add(target)
    reachable = set()
    for source in nodes:
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


def _first_separated_pair(
    component: list[str],
    separated_pairs: set[tuple[str, str]],
) -> tuple[str, str] | None:
    for left, right in product(component, component):
        if left != right and (left, right) in separated_pairs:
            return left, right
    return None


def _safety(value: Any, nodes: set[str]) -> list[str]:
    if value == "all":
        return sorted(nodes)
    members = _unique_string_list(value, "safety")
    bad = sorted(set(members) - nodes)
    if bad:
        raise SchemaError(f"safety references nodes outside graph: {bad}")
    return members


def _observations(value: Any, nodes: set[str]) -> dict[str, dict[str, str]]:
    observations_raw = _dict(value, "observations")
    observations = {}
    for name, mapping_raw in observations_raw.items():
        mapping = _string_mapping(mapping_raw, f"observation {name}")
        _require_total_on_nodes(mapping, nodes, f"observation {name}")
        observations[str(name)] = mapping
    if not observations:
        raise SchemaError("derived graph must declare at least one observation")
    return observations


def _presentations(value: Any, nodes: set[str]) -> dict[str, dict[str, str]]:
    presentations_raw = _dict(value, "presentations")
    presentations = {}
    for name, mapping_raw in presentations_raw.items():
        mapping = _string_mapping(mapping_raw, f"presentation {name}")
        _require_total_on_nodes(mapping, nodes, f"presentation {name}")
        presentations[str(name)] = mapping
    return presentations


def _edge_list(value: Any, nodes: set[str], label: str) -> list[tuple[str, str]]:
    if not isinstance(value, list):
        raise SchemaError(f"{label} must be a list")
    edges = []
    for item in value:
        if not isinstance(item, list) or len(item) != 2:
            raise SchemaError(f"{label} entries must be two-item lists")
        edge = (str(item[0]), str(item[1]))
        bad = sorted(set(edge) - nodes)
        if bad:
            raise SchemaError(f"{label} references nodes outside graph: {bad}")
        edges.append(edge)
    if len(set(edges)) != len(edges):
        raise SchemaError(f"{label} must not contain duplicate edges")
    return sorted(edges)


def _require_total_on_nodes(mapping: dict[str, str], nodes: set[str], label: str) -> None:
    missing = sorted(nodes - set(mapping))
    extra = sorted(set(mapping) - nodes)
    if missing:
        raise SchemaError(f"{label} is missing nodes: {missing}")
    if extra:
        raise SchemaError(f"{label} has nodes outside graph: {extra}")


def _string_mapping(value: Any, label: str) -> dict[str, str]:
    raw_mapping = _dict(value, label)
    return {str(key): str(target) for key, target in raw_mapping.items()}


def _dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchemaError(f"{label} must be an object")
    return value


def _unique_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise SchemaError(f"{label} must be a list")
    items = [str(item) for item in value]
    if len(set(items)) != len(items):
        raise SchemaError(f"{label} must not contain duplicates")
    return items
