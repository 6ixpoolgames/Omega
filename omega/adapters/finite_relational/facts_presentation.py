"""Presentation, nonfactorization, and closure facts."""

from __future__ import annotations

from collections import defaultdict
from itertools import product

from omega.adapters.finite_relational.facts_common import (
    Pair,
    _total_function_mapping,
)
from omega.adapters.finite_relational.model import DEFAULT_DOMAIN, FiniteRelationalModel, SchemaError

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
