"""Finite safe-prefix and observed-word language facts."""

from __future__ import annotations

from collections import defaultdict

from omega.adapters.finite_relational.facts_common import (
    Pair,
    binary_relation,
    _total_function_mapping,
)
from omega.adapters.finite_relational.facts_dynamics import (
    dynamic_edge_projection_exactness_facts,
    dynamic_path_lifting_facts,
    dynamic_presentation_equivariance_facts,
    _dynamic_projection_context,
)
from omega.adapters.finite_relational.model import FiniteRelationalModel, SchemaError

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
