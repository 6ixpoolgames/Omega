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


def dynamic_presentation_equivariance_facts(
    model: FiniteRelationalModel,
    *,
    transition: str,
    presentation: str,
    abstract_transition: str,
) -> dict[str, object]:
    """Check whether a presentation commutes with transition structure.

    The audit is exact and finite. Preservation says every exact transition
    edge projects to an abstract transition edge. Reflection says every
    declared abstract edge is realized by at least one exact transition edge
    between states in the corresponding presentation fibers.
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


def viable_trajectory_count_facts(
    model: FiniteRelationalModel,
    *,
    transition: str,
    safety: str,
    horizon: int,
    start_predicate: str | None = None,
) -> dict[str, object]:
    """Count finite safe transition words up to a declared horizon.

    A word of horizon n is a state sequence with n transition edges. Every
    state in the sequence must satisfy the declared safety predicate. If a
    start predicate is supplied, horizon-zero words are restricted to that
    predicate; otherwise all safe states may start a word.
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
        "safe_state_count": len(safe),
        "start_state_count": len(starts),
        "safe_start_state_count": len(starts & safe),
        "transition_edge_count": len(edges),
        "count_profile": count_profile,
        "final_count": count_profile[-1],
        "nonempty_at_horizon": count_profile[-1] > 0,
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
    """Check whether scrambling a target changes declared recovery facts.

    This is an adapter provenance gate, not a semantic target validator. It
    asks whether the supplied target has operational bite relative to a
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
