"""Derived finite facts for the finite relational adapter."""

from __future__ import annotations

from collections import defaultdict, deque
from itertools import product

from omega.adapters.finite_relational.model import DEFAULT_DOMAIN, FiniteRelationalModel, SchemaError


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


def _viability_kernel(edges: set[Pair], safe: set[str]) -> set[str]:
    current = set(safe)
    changed = True
    while changed:
        next_current = {
            state
            for state in current
            if any(source == state and target in current for source, target in edges)
        }
        changed = next_current != current
        current = next_current
    return current


def safe_prefix_count_facts(
    model: FiniteRelationalModel,
    *,
    transition: str,
    safety: str,
    horizon: int,
    start_predicate: str | None = None,
) -> dict[str, object]:
    """Count finite safe transition words up to a declared horizon.

    A prefix of horizon n is a state sequence with n transition edges. Every
    state in the sequence must satisfy the declared safety predicate. If a start
    predicate is supplied, horizon-zero prefixes are restricted to that
    predicate; otherwise all safe states may start a prefix.
    """

    if horizon < 0:
        raise SchemaError(f"viable trajectory horizon must be nonnegative: {horizon}")
    edges = binary_relation(model, transition)
    transition_relation = model.relations[transition]
    if transition_relation.domains[0] != transition_relation.domains[1]:
        raise SchemaError(
            "viable trajectory count requires a transition over one domain: "
            f"{transition_relation.domains}"
        )
    domain = transition_relation.domains[0]
    states = set(model.domain(domain))
    safe = set(model.predicate_members(safety))
    if model.predicates[safety].domain != domain:
        raise SchemaError(
            f"safety predicate domain must match transition domain: "
            f"{model.predicates[safety].domain} != {domain}"
        )
    if start_predicate is None:
        starts = states
    else:
        if model.predicates[start_predicate].domain != domain:
            raise SchemaError(
                f"start predicate domain must match transition domain: "
                f"{model.predicates[start_predicate].domain} != {domain}"
            )
        starts = set(model.predicate_members(start_predicate))

    adjacency: dict[str, list[str]] = defaultdict(list)
    for source, target in sorted(edges):
        adjacency[source].append(target)

    current = {state: 1 for state in sorted(starts & safe)}
    count_profile = [sum(current.values())]
    for _step in range(horizon):
        next_counts: dict[str, int] = defaultdict(int)
        for source, count in current.items():
            for target in adjacency[source]:
                if target in safe:
                    next_counts[target] += count
        current = dict(next_counts)
        count_profile.append(sum(current.values()))

    return {
        "transition": transition,
        "safety": safety,
        "start_predicate": start_predicate,
        "horizon": horizon,
        "count_kind": "safe_prefix",
        "safe_state_count": len(safe),
        "start_state_count": len(starts),
        "safe_start_state_count": len(starts & safe),
        "transition_edge_count": len(edges),
        "count_profile": count_profile,
        "final_count": count_profile[-1],
        "nonempty_at_horizon": count_profile[-1] > 0,
    }


def viable_trajectory_count_facts(
    model: FiniteRelationalModel,
    *,
    transition: str,
    safety: str,
    horizon: int,
    start_predicate: str | None = None,
) -> dict[str, object]:
    """Compatibility alias for safe-prefix counts.

    The historical name is retained for fixtures. New code should use
    `safe_prefix_count_facts` unless it also requires extendability.
    """

    return safe_prefix_count_facts(
        model,
        transition=transition,
        safety=safety,
        horizon=horizon,
        start_predicate=start_predicate,
    )


def extendable_safe_prefix_count_facts(
    model: FiniteRelationalModel,
    *,
    transition: str,
    safety: str,
    horizon: int,
    start_predicate: str | None = None,
) -> dict[str, object]:
    """Count safe prefixes whose endpoint remains indefinitely viable."""

    prefix = safe_prefix_count_facts(
        model,
        transition=transition,
        safety=safety,
        horizon=horizon,
        start_predicate=start_predicate,
    )
    edges = binary_relation(model, transition)
    transition_relation = model.relations[transition]
    domain = transition_relation.domains[0]
    states = set(model.domain(domain))
    safe = set(model.predicate_members(safety))
    starts = (
        states
        if start_predicate is None
        else set(model.predicate_members(start_predicate))
    )
    kernel = _viability_kernel(edges, safe)
    adjacency: dict[str, list[str]] = defaultdict(list)
    for source, target in sorted(edges):
        adjacency[source].append(target)

    current = {state: 1 for state in sorted(starts & safe)}
    extendable_profile = [sum(count for state, count in current.items() if state in kernel)]
    for _step in range(horizon):
        next_counts: dict[str, int] = defaultdict(int)
        for source, count in current.items():
            for target in adjacency[source]:
                if target in safe:
                    next_counts[target] += count
        current = dict(next_counts)
        extendable_profile.append(
            sum(count for state, count in current.items() if state in kernel)
        )

    return {
        **prefix,
        "count_kind": "extendable_safe_prefix",
        "viability_kernel": sorted(kernel),
        "viability_kernel_size": len(kernel),
        "safe_prefix_count_profile": prefix["count_profile"],
        "count_profile": extendable_profile,
        "final_count": extendable_profile[-1],
        "nonempty_at_horizon": extendable_profile[-1] > 0,
    }


def observed_extendable_safe_word_count_facts(
    model: FiniteRelationalModel,
    *,
    transition: str,
    safety: str,
    observation: str,
    horizon: int,
    start_predicate: str | None = None,
) -> dict[str, object]:
    """Count distinct observation words from extendable safe prefixes."""

    if horizon < 0:
        raise SchemaError(
            f"observed extendable safe word horizon must be nonnegative: {horizon}"
        )
    extendable = extendable_safe_prefix_count_facts(
        model,
        transition=transition,
        safety=safety,
        horizon=horizon,
        start_predicate=start_predicate,
    )
    edges = binary_relation(model, transition)
    transition_relation = model.relations[transition]
    domain = transition_relation.domains[0]
    observation_function = model.functions[observation]
    if observation_function.domain != domain:
        raise SchemaError(
            "observed viable word observation domain must match transition domain: "
            f"{observation_function.domain} != {domain}"
        )
    states = set(model.domain(domain))
    missing_states = sorted(states - set(observation_function.mapping))
    if missing_states:
        raise SchemaError(
            f"observation function {observation} is not total on domain "
            f"{domain}: {missing_states}"
        )
    safe = set(model.predicate_members(safety))
    starts = (
        states
        if start_predicate is None
        else set(model.predicate_members(start_predicate))
    )
    kernel = set(extendable["viability_kernel"])
    adjacency: dict[str, list[str]] = defaultdict(list)
    for source, target in sorted(edges):
        adjacency[source].append(target)

    current = {
        (state, (observation_function.mapping[state],))
        for state in sorted(starts & safe)
    }
    words_by_horizon: list[list[list[str]]] = []
    count_profile: list[int] = []
    for step in range(horizon + 1):
        observed_words = sorted({word for state, word in current if state in kernel})
        words_by_horizon.append([list(word) for word in observed_words])
        count_profile.append(len(observed_words))
        if step == horizon:
            break
        next_current = {
            (target, (*word, observation_function.mapping[target]))
            for state, word in current
            for target in adjacency[state]
            if target in safe
        }
        current = next_current

    return {
        "transition": transition,
        "safety": safety,
        "observation": observation,
        "start_predicate": start_predicate,
        "horizon": horizon,
        "count_kind": "observed_extendable_safe_word",
        "viability_kernel": sorted(kernel),
        "viability_kernel_size": len(kernel),
        "safe_prefix_count_profile": extendable["safe_prefix_count_profile"],
        "extendable_safe_prefix_count_profile": extendable["count_profile"],
        "count_profile": count_profile,
        "observed_words_by_horizon": words_by_horizon,
        "final_count": count_profile[-1],
        "nonempty_at_horizon": count_profile[-1] > 0,
    }


def observed_word_lifting_monotonicity_facts(
    model: FiniteRelationalModel,
    *,
    exact_transition: str,
    exact_safety: str,
    exact_observation: str,
    presentation: str,
    abstract_transition: str,
    abstract_safety: str,
    abstract_observation: str,
    horizon: int,
    exact_start_predicate: str | None = None,
    abstract_start_predicate: str | None = None,
) -> dict[str, object]:
    """Check finite observed-word monotonicity under a lifting contract."""

    if horizon < 0:
        raise SchemaError(
            f"observed word lifting monotonicity horizon must be nonnegative: {horizon}"
        )
    context = _dynamic_projection_context(
        model,
        transition=exact_transition,
        presentation=presentation,
        abstract_transition=abstract_transition,
    )
    exact_domain = str(context["state_domain"])
    abstract_domain = str(context["abstract_domain"])
    presentation_map = dict(context["presentation_map"])
    exact_states = set(model.domain(exact_domain))
    abstract_states = set(model.domain(abstract_domain))

    edge_projection = dynamic_edge_projection_exactness_facts(
        model,
        transition=exact_transition,
        presentation=presentation,
        abstract_transition=abstract_transition,
    )
    path_lifting = dynamic_path_lifting_facts(
        model,
        transition=exact_transition,
        presentation=presentation,
        abstract_transition=abstract_transition,
        horizon=horizon,
    )
    exact_words = observed_extendable_safe_word_count_facts(
        model,
        transition=exact_transition,
        safety=exact_safety,
        observation=exact_observation,
        horizon=horizon,
        start_predicate=exact_start_predicate,
    )
    abstract_words = observed_extendable_safe_word_count_facts(
        model,
        transition=abstract_transition,
        safety=abstract_safety,
        observation=abstract_observation,
        horizon=horizon,
        start_predicate=abstract_start_predicate,
    )

    exact_observation_map = _total_function_mapping(
        model,
        exact_observation,
        domain=exact_domain,
    )
    abstract_observation_map = _total_function_mapping(
        model,
        abstract_observation,
        domain=abstract_domain,
    )
    observation_mismatches = [
        {
            "state": state,
            "abstract_state": presentation_map[state],
            "exact_observation": exact_observation_map[state],
            "abstract_observation": abstract_observation_map[presentation_map[state]],
        }
        for state in sorted(exact_states)
        if exact_observation_map[state]
        != abstract_observation_map[presentation_map[state]]
    ]

    exact_safe = set(model.predicate_members(exact_safety))
    abstract_safe = set(model.predicate_members(abstract_safety))
    exact_start = (
        exact_states
        if exact_start_predicate is None
        else set(model.predicate_members(exact_start_predicate))
    )
    abstract_start = (
        abstract_states
        if abstract_start_predicate is None
        else set(model.predicate_members(abstract_start_predicate))
    )
    exact_effective_start = exact_start & exact_safe
    abstract_effective_start = abstract_start & abstract_safe
    projected_exact_starts = {presentation_map[state] for state in exact_effective_start}
    missing_abstract_starts = sorted(abstract_effective_start - projected_exact_starts)

    safety_reflection_failures = [
        {
            "state": state,
            "abstract_state": presentation_map[state],
        }
        for state in sorted(exact_states)
        if presentation_map[state] in abstract_safe and state not in exact_safe
    ]
    exact_kernel = set(exact_words["viability_kernel"])
    abstract_kernel = set(abstract_words["viability_kernel"])
    viability_reflection_failures = [
        {
            "state": state,
            "abstract_state": presentation_map[state],
        }
        for state in sorted(exact_states)
        if presentation_map[state] in abstract_kernel and state not in exact_kernel
    ]

    exact_profile = list(exact_words["count_profile"])
    abstract_profile = list(abstract_words["count_profile"])
    exact_word_sets = [
        {tuple(word) for word in words}
        for words in exact_words["observed_words_by_horizon"]
    ]
    abstract_word_sets = [
        {tuple(word) for word in words}
        for words in abstract_words["observed_words_by_horizon"]
    ]
    phantom_words_by_horizon = [
        sorted(abstract_set - exact_set)
        for exact_set, abstract_set in zip(
            exact_word_sets,
            abstract_word_sets,
            strict=True,
        )
    ]
    exact_only_words_by_horizon = [
        sorted(exact_set - abstract_set)
        for exact_set, abstract_set in zip(
            exact_word_sets,
            abstract_word_sets,
            strict=True,
        )
    ]
    language_subset_by_horizon = [
        not phantom_words for phantom_words in phantom_words_by_horizon
    ]
    language_equal_by_horizon = [
        not phantom_words and not exact_only_words
        for phantom_words, exact_only_words in zip(
            phantom_words_by_horizon,
            exact_only_words_by_horizon,
            strict=True,
        )
    ]
    missing_exact_realizations = [
        {"horizon": horizon_index, "word": list(word)}
        for horizon_index, phantom_words in enumerate(phantom_words_by_horizon)
        for word in phantom_words
    ]
    exact_only_words = [
        {"horizon": horizon_index, "word": list(word)}
        for horizon_index, words in enumerate(exact_only_words_by_horizon)
        for word in words
    ]
    missing_exact_realization_count_profile = [
        len(words) for words in phantom_words_by_horizon
    ]
    exact_only_word_count_profile = [
        len(words) for words in exact_only_words_by_horizon
    ]
    language_subset = all(language_subset_by_horizon)
    language_equal = all(language_equal_by_horizon)
    delta = [
        abstract_count - exact_count
        for exact_count, abstract_count in zip(
            exact_profile,
            abstract_profile,
            strict=True,
        )
    ]
    inflates = any(item > 0 for item in delta)
    hides = any(item < 0 for item in delta)
    contract_holds = (
        bool(edge_projection["edge_projection_exact"])
        and bool(path_lifting["path_lifts"])
        and not observation_mismatches
        and not missing_abstract_starts
        and not safety_reflection_failures
        and not viability_reflection_failures
    )
    return {
        "monotone_under_contract": contract_holds and language_subset,
        "language_monotone_under_contract": contract_holds and language_subset,
        "count_monotone_under_contract": contract_holds and not inflates,
        "contract_holds": contract_holds,
        "language_subset": language_subset,
        "language_equal": language_equal,
        "language_subset_by_horizon": language_subset_by_horizon,
        "language_equal_by_horizon": language_equal_by_horizon,
        "phantom_abstract_words_by_horizon": [
            [list(word) for word in words]
            for words in phantom_words_by_horizon
        ],
        "exact_only_words_by_horizon": [
            [list(word) for word in words]
            for words in exact_only_words_by_horizon
        ],
        "missing_exact_realizations": missing_exact_realizations,
        "missing_exact_realizations_by_horizon": [
            [list(word) for word in words]
            for words in phantom_words_by_horizon
        ],
        "missing_exact_realization_count_profile": (
            missing_exact_realization_count_profile
        ),
        "exact_only_words": exact_only_words,
        "exact_only_word_count_profile": exact_only_word_count_profile,
        "equal_count_but_language_differs": exact_profile == abstract_profile
        and not language_equal,
        "not_inflated": not inflates,
        "inflates": inflates,
        "hides": hides,
        "mixed_distortion": inflates and hides,
        "horizon": horizon,
        "exact_transition": exact_transition,
        "abstract_transition": abstract_transition,
        "presentation": presentation,
        "exact_observation": exact_observation,
        "abstract_observation": abstract_observation,
        "observation_compatible": not observation_mismatches,
        "observation_mismatches": observation_mismatches,
        "start_compatible": not missing_abstract_starts,
        "missing_abstract_starts": missing_abstract_starts,
        "safety_reflects": not safety_reflection_failures,
        "safety_reflection_failures": safety_reflection_failures,
        "viability_reflects": not viability_reflection_failures,
        "viability_reflection_failures": viability_reflection_failures,
        "exact_count_profile": exact_profile,
        "abstract_count_profile": abstract_profile,
        "count_profile_delta": delta,
        "exact_final_count": exact_words["final_count"],
        "abstract_final_count": abstract_words["final_count"],
        "final_count_delta": abstract_words["final_count"] - exact_words["final_count"],
        "exact": exact_words,
        "abstract": abstract_words,
        "edge_projection": edge_projection,
        "path_lifting": path_lifting,
    }


def viable_trajectory_count_comparison_facts(
    model: FiniteRelationalModel,
    *,
    exact_transition: str,
    exact_safety: str,
    presentation: str,
    abstract_transition: str,
    abstract_safety: str,
    horizon: int,
    exact_start_predicate: str | None = None,
    abstract_start_predicate: str | None = None,
) -> dict[str, object]:
    """Compare exact and abstract finite viable-trajectory count profiles.

    This is a finite diagnostic, not a theorem that sound presentations preserve
    state-word counts. It reports whether an abstract dynamics inflates or hides
    counts relative to the declared exact dynamics, and includes the dynamic
    equivariance payload for the same presentation.
    """

    dynamics = dynamic_presentation_equivariance_facts(
        model,
        transition=exact_transition,
        presentation=presentation,
        abstract_transition=abstract_transition,
    )
    exact = viable_trajectory_count_facts(
        model,
        transition=exact_transition,
        safety=exact_safety,
        horizon=horizon,
        start_predicate=exact_start_predicate,
    )
    abstract = viable_trajectory_count_facts(
        model,
        transition=abstract_transition,
        safety=abstract_safety,
        horizon=horizon,
        start_predicate=abstract_start_predicate,
    )
    exact_profile = list(exact["count_profile"])
    abstract_profile = list(abstract["count_profile"])
    delta = [
        abstract_count - exact_count
        for exact_count, abstract_count in zip(
            exact_profile,
            abstract_profile,
            strict=True,
        )
    ]
    inflates = any(item > 0 for item in delta)
    hides = any(item < 0 for item in delta)
    return {
        "distorted": exact_profile != abstract_profile,
        "inflates": inflates,
        "hides": hides,
        "mixed_distortion": inflates and hides,
        "equivariant": dynamics["equivariant"],
        "horizon": horizon,
        "exact_transition": exact_transition,
        "abstract_transition": abstract_transition,
        "presentation": presentation,
        "exact_count_profile": exact_profile,
        "abstract_count_profile": abstract_profile,
        "count_profile_delta": delta,
        "exact_final_count": exact["final_count"],
        "abstract_final_count": abstract["final_count"],
        "final_count_delta": abstract["final_count"] - exact["final_count"],
        "exact": exact,
        "abstract": abstract,
        "dynamics": dynamics,
    }


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


def common_visible_pairs(
    model: FiniteRelationalModel,
    *,
    presentations: tuple[str, ...],
    domain: str = DEFAULT_DOMAIN,
) -> list[Pair]:
    """Pairs kept visible by every declared presentation.

    This is the adapter analogue of the Lean `CommonVisiblePairs` pilot:
    a pair is common-visible when no presentation in the declared family
    merges it.
    """

    mappings = [_total_function_mapping(model, name, domain=domain) for name in presentations]
    states = model.domain(domain)
    visible = []
    for left, right in product(states, states):
        if left == right:
            continue
        if all(mapping[left] != mapping[right] for mapping in mappings):
            visible.append((left, right))
    return sorted(visible)


def predicate_respects_presentation(
    model: FiniteRelationalModel,
    *,
    predicate: str,
    presentation: str,
) -> bool:
    """Whether a predicate is constant on a presentation's fibers."""

    target = model.predicates[predicate]
    mapping = _total_function_mapping(model, presentation, domain=target.domain)
    states = model.domain(target.domain)
    members = target.members
    return all(
        mapping[left] != mapping[right] or ((left in members) == (right in members))
        for left, right in product(states, states)
    )


def common_target_predicates(
    model: FiniteRelationalModel,
    *,
    presentations: tuple[str, ...],
    target_predicates: tuple[str, ...],
) -> list[str]:
    """Predicates preserved by every declared presentation."""

    common = []
    for predicate in target_predicates:
        if all(
            predicate_respects_presentation(
                model,
                predicate=predicate,
                presentation=presentation,
            )
            for presentation in presentations
        ):
            common.append(predicate)
    return sorted(common)


def predicate_is_constant(model: FiniteRelationalModel, name: str) -> bool:
    """Whether a predicate is empty or full on its declared domain."""

    predicate = model.predicates[name]
    states = set(model.domain(predicate.domain))
    return not predicate.members or predicate.members == states


def presentation_fact_closure_facts(
    model: FiniteRelationalModel,
    *,
    presentations: tuple[str, ...],
    target_predicates: tuple[str, ...] = (),
    seed_visible_pairs: tuple[Pair, ...] = (),
    seed_target_predicates: tuple[str, ...] = (),
    expected_common_visible_pairs: tuple[Pair, ...] = (),
    expected_absent_visible_pairs: tuple[Pair, ...] = (),
    expected_common_target_predicates: tuple[str, ...] = (),
    expected_absent_target_predicates: tuple[str, ...] = (),
    expected_surplus_visible_pairs: tuple[Pair, ...] = (),
    expected_absent_surplus_visible_pairs: tuple[Pair, ...] = (),
    expected_surplus_target_predicates: tuple[str, ...] = (),
    expected_absent_surplus_target_predicates: tuple[str, ...] = (),
    expected_nonconstant_surplus_target_predicates: tuple[str, ...] = (),
    expected_absent_nonconstant_surplus_target_predicates: tuple[str, ...] = (),
    domain: str = DEFAULT_DOMAIN,
) -> dict[str, object]:
    """Compute a small finite presentation/fact closure check.

    The audit is intentionally expectation-relative. It reports the common
    visible pairs and common target predicates induced by the declared
    presentation family, then checks any expected inclusions/exclusions.
    """

    if not presentations:
        raise SchemaError("presentation fact closure must declare at least one presentation")

    visible = set(common_visible_pairs(model, presentations=presentations, domain=domain))
    common_targets = set(
        common_target_predicates(
            model,
            presentations=presentations,
            target_predicates=target_predicates,
        )
    )
    seeded_visible = set(seed_visible_pairs)
    seeded_targets = set(seed_target_predicates)
    surplus_visible = visible - seeded_visible
    surplus_targets = common_targets - seeded_targets
    constant_common_targets = {
        predicate for predicate in common_targets if predicate_is_constant(model, predicate)
    }
    nonconstant_common_targets = common_targets - constant_common_targets
    nonconstant_surplus_targets = surplus_targets & nonconstant_common_targets

    expected_common_visible = set(expected_common_visible_pairs)
    expected_absent_visible = set(expected_absent_visible_pairs)
    expected_common_targets = set(expected_common_target_predicates)
    expected_absent_targets = set(expected_absent_target_predicates)
    expected_surplus_visible = set(expected_surplus_visible_pairs)
    expected_absent_surplus_visible = set(expected_absent_surplus_visible_pairs)
    expected_surplus_targets = set(expected_surplus_target_predicates)
    expected_absent_surplus_targets = set(expected_absent_surplus_target_predicates)
    expected_nonconstant_surplus_targets = set(expected_nonconstant_surplus_target_predicates)
    expected_absent_nonconstant_surplus_targets = set(
        expected_absent_nonconstant_surplus_target_predicates
    )

    missing_common_visible = sorted(expected_common_visible - visible)
    present_absent_visible = sorted(expected_absent_visible & visible)
    missing_common_targets = sorted(expected_common_targets - common_targets)
    present_absent_targets = sorted(expected_absent_targets & common_targets)
    missing_surplus_visible = sorted(expected_surplus_visible - surplus_visible)
    present_absent_surplus_visible = sorted(expected_absent_surplus_visible & surplus_visible)
    missing_surplus_targets = sorted(expected_surplus_targets - surplus_targets)
    present_absent_surplus_targets = sorted(expected_absent_surplus_targets & surplus_targets)
    missing_nonconstant_surplus_targets = sorted(
        expected_nonconstant_surplus_targets - nonconstant_surplus_targets
    )
    present_absent_nonconstant_surplus_targets = sorted(
        expected_absent_nonconstant_surplus_targets & nonconstant_surplus_targets
    )
    closure_ok = not (
        missing_common_visible
        or present_absent_visible
        or missing_common_targets
        or present_absent_targets
        or missing_surplus_visible
        or present_absent_surplus_visible
        or missing_surplus_targets
        or present_absent_surplus_targets
        or missing_nonconstant_surplus_targets
        or present_absent_nonconstant_surplus_targets
    )

    return {
        "closure_ok": closure_ok,
        "closure_mode": "declared_family_candidate_fact_surface",
        "surplus_scope": "family_relative",
        "presentations": list(presentations),
        "target_predicates": list(target_predicates),
        "seed_visible_pairs": sorted(seeded_visible),
        "seed_target_predicates": sorted(seeded_targets),
        "common_visible_pair_count": len(visible),
        "common_visible_pairs": sorted(visible),
        "common_target_predicates": sorted(common_targets),
        "constant_common_target_predicates": sorted(constant_common_targets),
        "nonconstant_common_target_predicates": sorted(nonconstant_common_targets),
        "surplus_common_visible_pair_count": len(surplus_visible),
        "surplus_common_visible_pairs": sorted(surplus_visible),
        "surplus_common_target_predicates": sorted(surplus_targets),
        "nonconstant_surplus_target_predicates": sorted(nonconstant_surplus_targets),
        "family_relative_surplus_visible_pair_count": len(surplus_visible),
        "family_relative_surplus_visible_pairs": sorted(surplus_visible),
        "family_relative_surplus_target_predicates": sorted(surplus_targets),
        "family_relative_nonconstant_surplus_target_predicates": sorted(
            nonconstant_surplus_targets
        ),
        "missing_expected_common_visible_pairs": missing_common_visible,
        "present_expected_absent_visible_pairs": present_absent_visible,
        "missing_expected_common_target_predicates": missing_common_targets,
        "present_expected_absent_target_predicates": present_absent_targets,
        "missing_expected_surplus_visible_pairs": missing_surplus_visible,
        "present_expected_absent_surplus_visible_pairs": present_absent_surplus_visible,
        "missing_expected_surplus_target_predicates": missing_surplus_targets,
        "present_expected_absent_surplus_target_predicates": present_absent_surplus_targets,
        "missing_expected_nonconstant_surplus_target_predicates": (
            missing_nonconstant_surplus_targets
        ),
        "present_expected_absent_nonconstant_surplus_target_predicates": (
            present_absent_nonconstant_surplus_targets
        ),
    }


def presentation_fact_derive_closure_facts(
    model: FiniteRelationalModel,
    *,
    seed_target_predicates: tuple[str, ...] = (),
    seed_visible_pairs: tuple[Pair, ...] = (),
    expected_closure_visible_pairs: tuple[Pair, ...] = (),
    expected_absent_closure_visible_pairs: tuple[Pair, ...] = (),
    expected_surplus_visible_pairs: tuple[Pair, ...] = (),
    expected_absent_surplus_visible_pairs: tuple[Pair, ...] = (),
    expected_closure_target_facts: tuple[str, ...] = (),
    expected_absent_closure_target_facts: tuple[str, ...] = (),
    expected_surplus_target_facts: tuple[str, ...] = (),
    expected_absent_surplus_target_facts: tuple[str, ...] = (),
    expected_nonconstant_surplus_target_facts: tuple[str, ...] = (),
    expected_absent_nonconstant_surplus_target_facts: tuple[str, ...] = (),
    expected_known_closure_target_predicates: tuple[str, ...] = (),
    expected_absent_known_closure_target_predicates: tuple[str, ...] = (),
    expected_known_surplus_target_predicates: tuple[str, ...] = (),
    expected_absent_known_surplus_target_predicates: tuple[str, ...] = (),
    domain: str = DEFAULT_DOMAIN,
    max_states: int = 4,
) -> dict[str, object]:
    """Enumerate finite presentations and facts generated from seed constraints.

    Unlike `presentation_fact_closure_facts`, this audit does not take a
    supplied presentation family or candidate target-fact list. It generates:

    * every partition/presentation of the finite carrier up to `max_states`;
    * every Boolean predicate over the carrier;
    * every ordered visible-pair fact.

    It then filters presentations by the seed facts and intersects all facts
    true of every admissible presentation.
    """

    states = tuple(model.domain(domain))
    if len(states) > max_states:
        raise SchemaError(
            "presentation fact derive closure is exponential; "
            f"domain {domain} has {len(states)} states but max_states is {max_states}"
        )
    seeded_visible = set(seed_visible_pairs)
    _validate_pairs_on_states(seeded_visible, set(states), "seed_visible_pairs")
    seed_members_by_predicate: dict[str, frozenset[str]] = {}
    for predicate_name in seed_target_predicates:
        predicate = model.predicates[predicate_name]
        if predicate.domain != domain:
            raise SchemaError(
                f"seed predicate {predicate_name} domain must match {domain}: "
                f"{predicate.domain}"
            )
        seed_members_by_predicate[predicate_name] = predicate.members
    seeded_target_facts = {
        _predicate_fact_key(states, members)
        for members in seed_members_by_predicate.values()
    }

    presentation_universe = list(_all_partition_mappings(states))
    admissible_presentations = [
        mapping
        for mapping in presentation_universe
        if _presentation_satisfies_seed(
            states,
            mapping,
            seed_members_by_predicate.values(),
            seeded_visible,
        )
    ]

    predicate_universe = {
        _predicate_fact_key(states, members): frozenset(members)
        for members in _all_subsets(states)
    }
    closure_target_facts = {
        key
        for key, members in predicate_universe.items()
        if admissible_presentations
        and all(
            _mapping_respects_members(states, mapping, members)
            for mapping in admissible_presentations
        )
    }
    closure_visible = {
        (left, right)
        for left, right in product(states, states)
        if left != right
        and admissible_presentations
        and all(mapping[left] != mapping[right] for mapping in admissible_presentations)
    }

    constant_target_facts = {
        key
        for key, members in predicate_universe.items()
        if not members or set(members) == set(states)
    }
    nonconstant_closure_target_facts = closure_target_facts - constant_target_facts
    surplus_visible = closure_visible - seeded_visible
    surplus_target_facts = closure_target_facts - seeded_target_facts
    nonconstant_surplus_target_facts = (
        surplus_target_facts & nonconstant_closure_target_facts
    )

    known_by_fact = _known_predicates_by_fact(model, states, domain)
    known_closure = sorted(
        {
            predicate
            for fact in closure_target_facts
            for predicate in known_by_fact.get(fact, ())
        }
    )
    known_surplus = sorted(
        {
            predicate
            for fact in surplus_target_facts
            for predicate in known_by_fact.get(fact, ())
        }
    )

    expected_closure_visible = set(expected_closure_visible_pairs)
    expected_absent_closure_visible = set(expected_absent_closure_visible_pairs)
    expected_surplus_visible = set(expected_surplus_visible_pairs)
    expected_absent_surplus_visible = set(expected_absent_surplus_visible_pairs)
    expected_closure_targets = set(expected_closure_target_facts)
    expected_absent_closure_targets = set(expected_absent_closure_target_facts)
    expected_surplus_targets = set(expected_surplus_target_facts)
    expected_absent_surplus_targets = set(expected_absent_surplus_target_facts)
    expected_nonconstant_surplus_targets = set(expected_nonconstant_surplus_target_facts)
    expected_absent_nonconstant_surplus_targets = set(
        expected_absent_nonconstant_surplus_target_facts
    )
    expected_known_closure = set(expected_known_closure_target_predicates)
    expected_absent_known_closure = set(expected_absent_known_closure_target_predicates)
    expected_known_surplus = set(expected_known_surplus_target_predicates)
    expected_absent_known_surplus = set(expected_absent_known_surplus_target_predicates)

    missing_closure_visible = sorted(expected_closure_visible - closure_visible)
    present_absent_closure_visible = sorted(
        expected_absent_closure_visible & closure_visible
    )
    missing_surplus_visible = sorted(expected_surplus_visible - surplus_visible)
    present_absent_surplus_visible = sorted(
        expected_absent_surplus_visible & surplus_visible
    )
    missing_closure_targets = sorted(expected_closure_targets - closure_target_facts)
    present_absent_closure_targets = sorted(
        expected_absent_closure_targets & closure_target_facts
    )
    missing_surplus_targets = sorted(expected_surplus_targets - surplus_target_facts)
    present_absent_surplus_targets = sorted(
        expected_absent_surplus_targets & surplus_target_facts
    )
    missing_nonconstant_surplus_targets = sorted(
        expected_nonconstant_surplus_targets - nonconstant_surplus_target_facts
    )
    present_absent_nonconstant_surplus_targets = sorted(
        expected_absent_nonconstant_surplus_targets & nonconstant_surplus_target_facts
    )
    missing_known_closure = sorted(expected_known_closure - set(known_closure))
    present_absent_known_closure = sorted(
        expected_absent_known_closure & set(known_closure)
    )
    missing_known_surplus = sorted(expected_known_surplus - set(known_surplus))
    present_absent_known_surplus = sorted(
        expected_absent_known_surplus & set(known_surplus)
    )

    derive_ok = bool(admissible_presentations) and not (
        missing_closure_visible
        or present_absent_closure_visible
        or missing_surplus_visible
        or present_absent_surplus_visible
        or missing_closure_targets
        or present_absent_closure_targets
        or missing_surplus_targets
        or present_absent_surplus_targets
        or missing_nonconstant_surplus_targets
        or present_absent_nonconstant_surplus_targets
        or missing_known_closure
        or present_absent_known_closure
        or missing_known_surplus
        or present_absent_known_surplus
    )

    return {
        "derive_ok": derive_ok,
        "closure_mode": "generated_universe_admissible_presentations",
        "domain": domain,
        "state_count": len(states),
        "max_states": max_states,
        "presentation_universe_count": len(presentation_universe),
        "admissible_presentation_count": len(admissible_presentations),
        "admissible_nonempty": bool(admissible_presentations),
        "admissible_presentations": [
            _presentation_signature(states, mapping)
            for mapping in admissible_presentations
        ],
        "target_fact_universe_count": len(predicate_universe),
        "seed_visible_pairs": sorted(seeded_visible),
        "seed_target_predicates": sorted(seed_members_by_predicate),
        "seed_target_facts": sorted(seeded_target_facts),
        "closure_visible_pair_count": len(closure_visible),
        "closure_visible_pairs": sorted(closure_visible),
        "closure_target_facts": sorted(closure_target_facts),
        "constant_closure_target_facts": sorted(closure_target_facts & constant_target_facts),
        "nonconstant_closure_target_facts": sorted(nonconstant_closure_target_facts),
        "surplus_visible_pair_count": len(surplus_visible),
        "surplus_visible_pairs": sorted(surplus_visible),
        "surplus_target_facts": sorted(surplus_target_facts),
        "nonconstant_surplus_target_facts": sorted(nonconstant_surplus_target_facts),
        "known_closure_target_predicates": known_closure,
        "known_surplus_target_predicates": known_surplus,
        "missing_expected_closure_visible_pairs": missing_closure_visible,
        "present_expected_absent_closure_visible_pairs": (
            present_absent_closure_visible
        ),
        "missing_expected_surplus_visible_pairs": missing_surplus_visible,
        "present_expected_absent_surplus_visible_pairs": present_absent_surplus_visible,
        "missing_expected_closure_target_facts": missing_closure_targets,
        "present_expected_absent_closure_target_facts": present_absent_closure_targets,
        "missing_expected_surplus_target_facts": missing_surplus_targets,
        "present_expected_absent_surplus_target_facts": present_absent_surplus_targets,
        "missing_expected_nonconstant_surplus_target_facts": (
            missing_nonconstant_surplus_targets
        ),
        "present_expected_absent_nonconstant_surplus_target_facts": (
            present_absent_nonconstant_surplus_targets
        ),
        "missing_expected_known_closure_target_predicates": missing_known_closure,
        "present_expected_absent_known_closure_target_predicates": (
            present_absent_known_closure
        ),
        "missing_expected_known_surplus_target_predicates": missing_known_surplus,
        "present_expected_absent_known_surplus_target_predicates": (
            present_absent_known_surplus
        ),
    }


def _all_partition_mappings(states: tuple[str, ...]) -> list[dict[str, str]]:
    if not states:
        return [dict()]

    assignments: list[list[int]] = []

    def extend(index: int, blocks: list[int]) -> None:
        if index == len(states):
            assignments.append(list(blocks))
            return
        max_block = max(blocks, default=-1)
        for block in range(max_block + 2):
            blocks.append(block)
            extend(index + 1, blocks)
            blocks.pop()

    extend(0, [])
    return [
        {state: f"block_{block}" for state, block in zip(states, blocks, strict=True)}
        for blocks in assignments
    ]


def _all_subsets(states: tuple[str, ...]) -> list[frozenset[str]]:
    subsets = []
    total = 1 << len(states)
    for mask in range(total):
        subsets.append(
            frozenset(state for index, state in enumerate(states) if mask & (1 << index))
        )
    return subsets


def _predicate_fact_key(states: tuple[str, ...], members: frozenset[str]) -> str:
    if not members:
        return "pred:{}"
    ordered = [state for state in states if state in members]
    return "pred:{" + ",".join(ordered) + "}"


def _mapping_respects_members(
    states: tuple[str, ...],
    mapping: dict[str, str],
    members: frozenset[str],
) -> bool:
    return all(
        mapping[left] != mapping[right] or ((left in members) == (right in members))
        for left, right in product(states, states)
    )


def _presentation_satisfies_seed(
    states: tuple[str, ...],
    mapping: dict[str, str],
    seed_predicates: object,
    seed_visible_pairs: set[Pair],
) -> bool:
    return all(
        _mapping_respects_members(states, mapping, members)
        for members in seed_predicates
    ) and all(mapping[left] != mapping[right] for left, right in seed_visible_pairs)


def _presentation_signature(
    states: tuple[str, ...],
    mapping: dict[str, str],
) -> list[tuple[str, str]]:
    return [(state, mapping[state]) for state in states]


def _known_predicates_by_fact(
    model: FiniteRelationalModel,
    states: tuple[str, ...],
    domain: str,
) -> dict[str, list[str]]:
    known: dict[str, list[str]] = defaultdict(list)
    for name, predicate in model.predicates.items():
        if predicate.domain == domain:
            known[_predicate_fact_key(states, predicate.members)].append(name)
    return {key: sorted(names) for key, names in known.items()}


def _validate_pairs_on_states(pairs: set[Pair], states: set[str], label: str) -> None:
    bad = sorted((left, right) for left, right in pairs if left not in states or right not in states)
    if bad:
        raise SchemaError(f"{label} contains states outside the selected domain: {bad}")


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
        "recovery_mode": "declared_decoder_family",
        "state_count": len(states),
        "observed_labels": observed_labels,
        "ambiguous_observation_labels": ambiguous_labels,
        "decoder_count": len(decoders),
        "successful_decoders": successful_decoders,
        "failed_decoders": failed_decoders,
        "decoder_results": decoder_results,
    }


def target_scramble_sensitivity_facts(
    model: FiniteRelationalModel,
    *,
    observation: str,
    target_predicate: str,
    scrambled_predicate: str,
    decoders: tuple[str, ...],
    true_label: str = "true",
    false_label: str = "false",
) -> dict[str, object]:
    """Check whether scrambling a target changes declared-decoder recovery facts.

    This is an adapter provenance gate, not a semantic target validator. It
    asks whether the supplied target has decoder-relative bite relative to a
    declared observation and decoder family. A target is sensitive here when
    replacing it with the scrambled predicate changes exact recoverability or
    the successful decoder surface.
    """

    target = bounded_recovery_facts(
        model,
        observation=observation,
        target_predicate=target_predicate,
        decoders=decoders,
        true_label=true_label,
        false_label=false_label,
    )
    scrambled = bounded_recovery_facts(
        model,
        observation=observation,
        target_predicate=scrambled_predicate,
        decoders=decoders,
        true_label=true_label,
        false_label=false_label,
    )
    recoverability_changed = bool(target["recoverable"]) != bool(scrambled["recoverable"])
    successful_decoders_changed = target["successful_decoders"] != scrambled["successful_decoders"]
    sensitive = recoverability_changed or successful_decoders_changed
    return {
        "sensitive": sensitive,
        "sensitivity_mode": "decoder_relative",
        "recoverability_changed": recoverability_changed,
        "successful_decoders_changed": successful_decoders_changed,
        "observation": observation,
        "target_predicate": target_predicate,
        "scrambled_predicate": scrambled_predicate,
        "decoders": list(decoders),
        "target_recoverable": target["recoverable"],
        "scrambled_recoverable": scrambled["recoverable"],
        "target_successful_decoders": target["successful_decoders"],
        "scrambled_successful_decoders": scrambled["successful_decoders"],
        "target": target,
        "scrambled": scrambled,
    }


def unrestricted_exact_recovery_facts(
    model: FiniteRelationalModel,
    *,
    observation: str,
    target_predicate: str,
) -> dict[str, object]:
    """Check exact deterministic recoverability by any observation decoder."""

    observation_function = model.functions[observation]
    target = model.predicates[target_predicate]
    if target.domain != observation_function.domain:
        raise SchemaError(
            "unrestricted recovery target predicate and observation function "
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
    ambiguous_labels = []
    label_profiles = []
    for label in observed_labels:
        preimage = [state for state in states if observation_function.mapping[state] == label]
        true_states = sorted(state for state in preimage if state in target_members)
        false_states = sorted(state for state in preimage if state not in target_members)
        target_values = []
        if false_states:
            target_values.append("false")
        if true_states:
            target_values.append("true")
        ambiguous = bool(true_states and false_states)
        if ambiguous:
            ambiguous_labels.append(label)
        label_profiles.append(
            {
                "label": label,
                "states": sorted(preimage),
                "target_values": target_values,
                "true_states": true_states,
                "false_states": false_states,
                "ambiguous": ambiguous,
            }
        )

    return {
        "recoverable": not ambiguous_labels,
        "recovery_mode": "unrestricted_deterministic_decoder",
        "observation": observation,
        "target_predicate": target_predicate,
        "state_count": len(states),
        "target_member_count": len(target_members),
        "observed_labels": observed_labels,
        "ambiguous_observation_labels": ambiguous_labels,
        "label_profiles": label_profiles,
    }


def target_scramble_capacity_sensitivity_facts(
    model: FiniteRelationalModel,
    *,
    observation: str,
    target_predicate: str,
    scrambled_predicate: str,
) -> dict[str, object]:
    """Check whether scrambling changes unrestricted exact recovery capacity."""

    target_domain = model.predicates[target_predicate].domain
    scrambled_domain = model.predicates[scrambled_predicate].domain
    if target_domain != scrambled_domain:
        raise SchemaError(
            "target scramble capacity sensitivity requires predicates over the same domain: "
            f"{target_domain} != {scrambled_domain}"
        )
    target = unrestricted_exact_recovery_facts(
        model,
        observation=observation,
        target_predicate=target_predicate,
    )
    scrambled = unrestricted_exact_recovery_facts(
        model,
        observation=observation,
        target_predicate=scrambled_predicate,
    )
    states = set(model.domain(target_domain))
    target_members = set(model.predicate_members(target_predicate))
    scrambled_members = set(model.predicate_members(scrambled_predicate))
    recoverability_changed = bool(target["recoverable"]) != bool(scrambled["recoverable"])
    return {
        "capacity_sensitive": recoverability_changed,
        "sensitivity_mode": "unrestricted_exact_recovery_capacity",
        "recoverability_changed": recoverability_changed,
        "same_prevalence": len(target_members) == len(scrambled_members),
        "complement_scramble": scrambled_members == states - target_members,
        "observation": observation,
        "target_predicate": target_predicate,
        "scrambled_predicate": scrambled_predicate,
        "target_recoverable": target["recoverable"],
        "scrambled_recoverable": scrambled["recoverable"],
        "target_member_count": len(target_members),
        "scrambled_member_count": len(scrambled_members),
        "target_ambiguous_observation_labels": target["ambiguous_observation_labels"],
        "scrambled_ambiguous_observation_labels": scrambled[
            "ambiguous_observation_labels"
        ],
        "target": target,
        "scrambled": scrambled,
    }


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
