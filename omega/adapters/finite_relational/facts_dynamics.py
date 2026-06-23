"""Dynamic presentation and process-lifting facts."""

from __future__ import annotations

from collections import defaultdict

from omega.adapters.finite_relational.facts_common import (
    binary_relation,
    _total_function_mapping,
)
from omega.adapters.finite_relational.model import FiniteRelationalModel, SchemaError

def dynamic_edge_projection_exactness_facts(
    model: FiniteRelationalModel,
    *,
    transition: str,
    presentation: str,
    abstract_transition: str,
) -> dict[str, object]:
    """Check whether abstract edges equal the global projected edge image.

    This is weaker than path/process equivariance. It says every exact edge
    projects to an abstract edge, and every abstract edge is induced by some
    exact edge somewhere. It does not require coherent representative-wise
    lifting along paths.
    """

    exact_edges = binary_relation(model, transition)
    abstract_edges = binary_relation(model, abstract_transition)
    transition_relation = model.relations[transition]
    abstract_relation = model.relations[abstract_transition]
    if transition_relation.domains[0] != transition_relation.domains[1]:
        raise SchemaError(
            "dynamic presentation equivariance requires a transition over one domain: "
            f"{transition_relation.domains}"
        )
    if abstract_relation.domains[0] != abstract_relation.domains[1]:
        raise SchemaError(
            "dynamic presentation equivariance requires an abstract transition over one domain: "
            f"{abstract_relation.domains}"
        )
    function = model.functions[presentation]
    if function.codomain is not None and abstract_relation.domains[0] != function.codomain:
        raise SchemaError(
            "dynamic presentation equivariance abstract transition domain must "
            f"match presentation codomain: {abstract_relation.domains[0]} != {function.codomain}"
        )
    presentation_map = _total_function_mapping(
        model,
        presentation,
        domain=transition_relation.domains[0],
    )
    projected_exact_edges = {
        (presentation_map[source], presentation_map[target])
        for source, target in exact_edges
    }
    missing_projected_edges = sorted(projected_exact_edges - abstract_edges)
    phantom_abstract_edges = sorted(abstract_edges - projected_exact_edges)
    return {
        "edge_projection_exact": not missing_projected_edges and not phantom_abstract_edges,
        "equivariant": not missing_projected_edges and not phantom_abstract_edges,
        "preserves_steps": not missing_projected_edges,
        "reflects_steps": not phantom_abstract_edges,
        "transition": transition,
        "presentation": presentation,
        "abstract_transition": abstract_transition,
        "exact_edge_count": len(exact_edges),
        "projected_exact_edge_count": len(projected_exact_edges),
        "abstract_edge_count": len(abstract_edges),
        "projected_exact_edges": sorted(projected_exact_edges),
        "abstract_edges": sorted(abstract_edges),
        "missing_projected_edges": missing_projected_edges,
        "phantom_abstract_edges": phantom_abstract_edges,
    }


def dynamic_presentation_equivariance_facts(
    model: FiniteRelationalModel,
    *,
    transition: str,
    presentation: str,
    abstract_transition: str,
) -> dict[str, object]:
    """Compatibility alias for edge-projection exactness.

    The historical audit name overstated the semantics. Use
    `dynamic_edge_projection_exactness_facts` for new code and pair it with
    step/path lifting when process coherence matters.
    """

    return dynamic_edge_projection_exactness_facts(
        model,
        transition=transition,
        presentation=presentation,
        abstract_transition=abstract_transition,
    )


def dynamic_step_lifting_facts(
    model: FiniteRelationalModel,
    *,
    transition: str,
    presentation: str,
    abstract_transition: str,
) -> dict[str, object]:
    """Check representative-wise one-step lifting for abstract dynamics."""

    context = _dynamic_projection_context(
        model,
        transition=transition,
        presentation=presentation,
        abstract_transition=abstract_transition,
    )
    states = model.domain(context["state_domain"])
    exact_edges = context["exact_edges"]
    abstract_edges = context["abstract_edges"]
    presentation_map = context["presentation_map"]
    adjacency: dict[str, list[str]] = defaultdict(list)
    for source, target in sorted(exact_edges):
        adjacency[source].append(target)

    failures = []
    for state in states:
        source_label = presentation_map[state]
        for abstract_source, abstract_target in sorted(abstract_edges):
            if abstract_source != source_label:
                continue
            if not any(presentation_map[target] == abstract_target for target in adjacency[state]):
                failures.append(
                    {
                        "state": state,
                        "source_label": source_label,
                        "abstract_target": abstract_target,
                    }
                )

    return {
        "step_lifts": not failures,
        "transition": transition,
        "presentation": presentation,
        "abstract_transition": abstract_transition,
        "failure_count": len(failures),
        "failures": failures,
    }


def dynamic_path_lifting_facts(
    model: FiniteRelationalModel,
    *,
    transition: str,
    presentation: str,
    abstract_transition: str,
    horizon: int,
) -> dict[str, object]:
    """Check coherent finite path lifting through a declared horizon."""

    if horizon < 0:
        raise SchemaError(f"dynamic path lifting horizon must be nonnegative: {horizon}")
    context = _dynamic_projection_context(
        model,
        transition=transition,
        presentation=presentation,
        abstract_transition=abstract_transition,
    )
    states = model.domain(context["state_domain"])
    exact_edges = context["exact_edges"]
    abstract_edges = context["abstract_edges"]
    presentation_map = context["presentation_map"]
    labels = sorted(model.domain(context["abstract_domain"]))

    exact_adjacency: dict[str, list[str]] = defaultdict(list)
    for source, target in sorted(exact_edges):
        exact_adjacency[source].append(target)
    abstract_adjacency: dict[str, list[str]] = defaultdict(list)
    for source, target in sorted(abstract_edges):
        abstract_adjacency[source].append(target)

    failures = []
    checked_path_count = 0
    for exact_start in states:
        start_label = presentation_map[exact_start]
        for abstract_path in _abstract_paths_from(start_label, abstract_adjacency, horizon):
            checked_path_count += 1
            if not _abstract_path_lifts_from(
                exact_start,
                abstract_path,
                exact_adjacency,
                presentation_map,
            ):
                failures.append(
                    {
                        "exact_start": exact_start,
                        "abstract_path": list(abstract_path),
                        "path_length": len(abstract_path) - 1,
                    }
                )

    return {
        "path_lifts": not failures,
        "transition": transition,
        "presentation": presentation,
        "abstract_transition": abstract_transition,
        "horizon": horizon,
        "abstract_label_count": len(labels),
        "checked_path_count": checked_path_count,
        "failure_count": len(failures),
        "failures": failures,
    }


def _dynamic_projection_context(
    model: FiniteRelationalModel,
    *,
    transition: str,
    presentation: str,
    abstract_transition: str,
) -> dict[str, object]:
    exact_edges = binary_relation(model, transition)
    abstract_edges = binary_relation(model, abstract_transition)
    transition_relation = model.relations[transition]
    abstract_relation = model.relations[abstract_transition]
    if transition_relation.domains[0] != transition_relation.domains[1]:
        raise SchemaError(
            "dynamic projection requires a transition over one domain: "
            f"{transition_relation.domains}"
        )
    if abstract_relation.domains[0] != abstract_relation.domains[1]:
        raise SchemaError(
            "dynamic projection requires an abstract transition over one domain: "
            f"{abstract_relation.domains}"
        )
    function = model.functions[presentation]
    if function.codomain is not None and abstract_relation.domains[0] != function.codomain:
        raise SchemaError(
            "dynamic projection abstract transition domain must match "
            f"presentation codomain: {abstract_relation.domains[0]} != {function.codomain}"
        )
    return {
        "exact_edges": exact_edges,
        "abstract_edges": abstract_edges,
        "presentation_map": _total_function_mapping(
            model,
            presentation,
            domain=transition_relation.domains[0],
        ),
        "state_domain": transition_relation.domains[0],
        "abstract_domain": abstract_relation.domains[0],
    }


def _abstract_paths_from(
    start: str,
    adjacency: dict[str, list[str]],
    horizon: int,
) -> list[tuple[str, ...]]:
    paths = [(start,)]
    frontier = [(start,)]
    for _step in range(horizon):
        next_frontier = []
        for path in frontier:
            for target in adjacency[path[-1]]:
                extended = (*path, target)
                paths.append(extended)
                next_frontier.append(extended)
        frontier = next_frontier
    return paths


def _abstract_path_lifts_from(
    exact_start: str,
    abstract_path: tuple[str, ...],
    exact_adjacency: dict[str, list[str]],
    presentation_map: dict[str, str],
) -> bool:
    current = {exact_start}
    for abstract_label in abstract_path[1:]:
        next_states = {
            target
            for state in current
            for target in exact_adjacency[state]
            if presentation_map[target] == abstract_label
        }
        if not next_states:
            return False
        current = next_states
    return True
