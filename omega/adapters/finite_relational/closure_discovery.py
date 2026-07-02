"""Generated closure-discovery studies for finite relational adapters.

This module is deliberately not another expectation-pinned fixture suite. It
generates small finite substrates, computes presentation/fact derive closure,
and records whether nonconstant surplus facts appear without predeclaring which
surplus facts should appear.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from typing import Any

from omega.adapters.finite_relational.facts import (
    Pair,
    presentation_fact_derive_closure_facts,
    reachable_pairs,
)
from omega.adapters.finite_relational.model import load_model, model_digest


@dataclass(frozen=True)
class ClosureDiscoveryCase:
    """One generated substrate plus its computed derive-closure payload."""

    case_id: str
    model: dict[str, Any]
    seed_target_predicates: tuple[str, ...]
    seed_visible_pairs: tuple[Pair, ...]
    observed: dict[str, object]

    @property
    def has_nonconstant_surplus(self) -> bool:
        return bool(self.observed["nonconstant_surplus_target_facts"])

    @property
    def classification(self) -> str:
        if not self.observed["admissible_nonempty"]:
            return "inconsistent_seed"
        if self.has_nonconstant_surplus:
            return "nonconstant_surplus"
        return "collapse"

    def summary(self) -> dict[str, object]:
        loaded = load_model(self.model)
        surplus_redundancy = _case_surplus_redundancy(self)
        return {
            "case_id": self.case_id,
            "model_id": loaded.model_id,
            "model_digest": model_digest(loaded),
            "seed_target_predicates": list(self.seed_target_predicates),
            "seed_visible_pairs": [list(pair) for pair in self.seed_visible_pairs],
            "classification": self.classification,
            "has_nonconstant_surplus": self.has_nonconstant_surplus,
            "presentation_universe_count": self.observed[
                "presentation_universe_count"
            ],
            "admissible_presentation_count": self.observed[
                "admissible_presentation_count"
            ],
            "closure_visible_pair_count": self.observed[
                "closure_visible_pair_count"
            ],
            "surplus_visible_pair_count": self.observed[
                "surplus_visible_pair_count"
            ],
            "nonconstant_surplus_target_facts": self.observed[
                "nonconstant_surplus_target_facts"
            ],
            "surplus_redundancy": surplus_redundancy,
        }


@dataclass(frozen=True)
class ClosureDiscoveryFamily:
    """A deterministic closure-discovery family over a small search space."""

    family_id: str
    description: str
    search_space: dict[str, object]
    cases: tuple[ClosureDiscoveryCase, ...]

    @property
    def nonconstant_surplus_cases(self) -> tuple[ClosureDiscoveryCase, ...]:
        return tuple(case for case in self.cases if case.has_nonconstant_surplus)

    @property
    def collapse_cases(self) -> tuple[ClosureDiscoveryCase, ...]:
        return tuple(case for case in self.cases if case.classification == "collapse")

    @property
    def representative_cases(self) -> tuple[ClosureDiscoveryCase, ...]:
        representatives: list[ClosureDiscoveryCase] = []
        if self.nonconstant_surplus_cases:
            representatives.append(self.nonconstant_surplus_cases[0])
        if self.collapse_cases:
            representatives.append(self.collapse_cases[0])
        return tuple(representatives)

    def summary(self) -> dict[str, object]:
        redundancy = _family_surplus_redundancy(self.cases)
        return {
            "family_id": self.family_id,
            "description": self.description,
            "search_space": self.search_space,
            "case_count": len(self.cases),
            "nonconstant_surplus_case_count": len(self.nonconstant_surplus_cases),
            "collapse_case_count": len(self.collapse_cases),
            "inconsistent_seed_case_count": sum(
                1 for case in self.cases if case.classification == "inconsistent_seed"
            ),
            "representative_case_count": len(self.representative_cases),
            "representative_cases": [
                case.summary() for case in self.representative_cases
            ],
            "surplus_redundancy": redundancy,
        }


def generate_closure_discovery() -> tuple[ClosureDiscoveryFamily, ...]:
    """Run deterministic closure-discovery over three small finite families."""

    return (
        _predicate_seed_family(),
        _reachability_seed_family(),
        _viability_seed_family(),
    )


def closure_discovery_summary() -> dict[str, object]:
    families = generate_closure_discovery()
    all_cases = tuple(case for family in families for case in family.cases)
    return {
        "family_count": len(families),
        "case_count": sum(len(family.cases) for family in families),
        "nonconstant_surplus_case_count": sum(
            len(family.nonconstant_surplus_cases) for family in families
        ),
        "collapse_case_count": sum(len(family.collapse_cases) for family in families),
        "surplus_redundancy": _family_surplus_redundancy(all_cases),
        "families": [family.summary() for family in families],
    }


def _predicate_seed_family() -> ClosureDiscoveryFamily:
    states = ("s0", "s1", "s2")
    cases = tuple(
        _closure_case(
            case_id=f"predicate_seed_{_subset_id(subset)}",
            model=_predicate_seed_model(
                model_id=f"closure_discovery_predicate_seed_{_subset_id(subset)}",
                states=states,
                predicate_name="seed",
                members=subset,
                claim_boundary=(
                    "Closure discovery predicate-seed sweep. The generator records "
                    "whatever generated-universe closure forces; it does not "
                    "predeclare an expected surplus fact."
                ),
            ),
            seed_target_predicates=("seed",),
        )
        for subset in _all_subsets(states)
    )
    return ClosureDiscoveryFamily(
        family_id="predicate_seed_partition_sweep",
        description=(
            "Enumerates all Boolean seed predicates over three states and asks "
            "which generated target facts and visible pairs survive every "
            "admissible presentation."
        ),
        search_space={
            "state_count": len(states),
            "seed_predicate_count": len(cases),
            "presentation_universe": "all finite partitions of the state carrier",
            "expected_surplus_predeclared": False,
        },
        cases=cases,
    )


def _reachability_seed_family() -> ClosureDiscoveryFamily:
    states = ("a", "b", "c")
    goal = "c"
    cases = []
    for index, edges in enumerate(_edge_subsets(states, loops=False)):
        reach = {
            source
            for source, target in reachable_pairs(set(states), set(edges))
            if target == goal
        }
        cases.append(
            _closure_case(
                case_id=f"reachability_seed_{index:02d}",
                model=_transition_seed_model(
                    model_id=f"closure_discovery_reachability_seed_{index:02d}",
                    states=states,
                    edges=edges,
                    predicate_name="can_reach_goal",
                    predicate_members=tuple(sorted(reach)),
                    claim_boundary=(
                        "Closure discovery reachability-seed sweep. The seed "
                        "predicate is generated from reachability-to-goal before "
                        "derive closure is computed."
                    ),
                ),
                seed_target_predicates=("can_reach_goal",),
            )
        )
    return ClosureDiscoveryFamily(
        family_id="reachability_seed_graph_sweep",
        description=(
            "Enumerates loop-free directed graphs on three states, derives the "
            "can-reach-goal predicate, and computes generated-universe closure "
            "without expected surplus annotations."
        ),
        search_space={
            "state_count": len(states),
            "goal": goal,
            "edge_subset_count": len(cases),
            "loops": False,
            "expected_surplus_predeclared": False,
        },
        cases=tuple(cases),
    )


def _viability_seed_family() -> ClosureDiscoveryFamily:
    states = ("a", "b", "c")
    safe = set(states)
    cases = []
    for index, edges in enumerate(_edge_subsets(states, loops=False)):
        kernel = _finite_viability_kernel(states, edges, safe)
        cases.append(
            _closure_case(
                case_id=f"viability_seed_{index:02d}",
                model=_transition_seed_model(
                    model_id=f"closure_discovery_viability_seed_{index:02d}",
                    states=states,
                    edges=edges,
                    predicate_name="viability_kernel",
                    predicate_members=tuple(sorted(kernel)),
                    claim_boundary=(
                        "Closure discovery viability-seed sweep. The seed "
                        "predicate is generated as the finite viability kernel "
                        "before derive closure is computed."
                    ),
                ),
                seed_target_predicates=("viability_kernel",),
            )
        )
    return ClosureDiscoveryFamily(
        family_id="viability_seed_graph_sweep",
        description=(
            "Enumerates loop-free directed graphs on three states, derives the "
            "finite viability kernel under all-safe states, and computes "
            "generated-universe closure without expected surplus annotations."
        ),
        search_space={
            "state_count": len(states),
            "edge_subset_count": len(cases),
            "safe": "all states",
            "loops": False,
            "expected_surplus_predeclared": False,
        },
        cases=tuple(cases),
    )


def _closure_case(
    *,
    case_id: str,
    model: dict[str, Any],
    seed_target_predicates: tuple[str, ...] = (),
    seed_visible_pairs: tuple[Pair, ...] = (),
) -> ClosureDiscoveryCase:
    loaded = load_model(model)
    observed = presentation_fact_derive_closure_facts(
        loaded,
        seed_target_predicates=seed_target_predicates,
        seed_visible_pairs=seed_visible_pairs,
    )
    return ClosureDiscoveryCase(
        case_id=case_id,
        model=model,
        seed_target_predicates=seed_target_predicates,
        seed_visible_pairs=seed_visible_pairs,
        observed=observed,
    )


def _predicate_seed_model(
    *,
    model_id: str,
    states: tuple[str, ...],
    predicate_name: str,
    members: frozenset[str],
    claim_boundary: str,
) -> dict[str, Any]:
    return {
        "model_id": model_id,
        "schema_version": "0.1.0",
        "carrier": list(states),
        "predicates": {
            predicate_name: sorted(members),
        },
        "provenance": _provenance(claim_boundary),
    }


def _transition_seed_model(
    *,
    model_id: str,
    states: tuple[str, ...],
    edges: tuple[Pair, ...],
    predicate_name: str,
    predicate_members: tuple[str, ...],
    claim_boundary: str,
) -> dict[str, Any]:
    return {
        "model_id": model_id,
        "schema_version": "0.1.0",
        "carrier": list(states),
        "predicates": {
            predicate_name: list(predicate_members),
        },
        "relations": {
            "next": {
                "domains": ["state", "state"],
                "tuples": [list(edge) for edge in edges],
            },
        },
        "provenance": _provenance(claim_boundary),
    }


def _finite_viability_kernel(
    states: tuple[str, ...],
    edges: tuple[Pair, ...],
    safe: set[str],
) -> set[str]:
    current = set(states) & safe
    edge_set = set(edges)
    changed = True
    while changed:
        changed = False
        next_current = {
            state
            for state in current
            if any((state, target) in edge_set for target in current)
        }
        if next_current != current:
            current = next_current
            changed = True
    return current


def _edge_subsets(states: tuple[str, ...], *, loops: bool) -> tuple[tuple[Pair, ...], ...]:
    possible_edges = tuple(
        (source, target)
        for source, target in product(states, states)
        if loops or source != target
    )
    return tuple(
        tuple(combination)
        for size in range(len(possible_edges) + 1)
        for combination in combinations(possible_edges, size)
    )


def _all_subsets(states: tuple[str, ...]) -> tuple[frozenset[str], ...]:
    total = 1 << len(states)
    return tuple(
        frozenset(state for index, state in enumerate(states) if mask & (1 << index))
        for mask in range(total)
    )


def _subset_id(subset: frozenset[str]) -> str:
    if not subset:
        return "empty"
    return "_".join(sorted(subset))


def _provenance(claim_boundary: str) -> dict[str, object]:
    return {
        "declared_before_run": True,
        "source": "generated finite relational closure discovery",
        "claim_boundary": claim_boundary,
    }


def _case_surplus_redundancy(case: ClosureDiscoveryCase) -> dict[str, object]:
    """Classify first-pass redundancy in generated closure surplus.

    This is not a canonical implication basis. It only separates the current
    easy cases: complement facts forced by a seed predicate and visible-pair
    facts forced by seed-fiber separation. Anything else remains explicitly
    unclassified.
    """

    states = tuple(load_model(case.model).domain())
    seed_facts = set(case.observed["seed_target_facts"])
    seed_members = {
        fact: _predicate_fact_members(fact)
        for fact in seed_facts
    }
    seed_complements = {
        _predicate_fact_key_for_states(states, frozenset(set(states) - set(members)))
        for members in seed_members.values()
    }
    nonconstant_surplus = set(case.observed["nonconstant_surplus_target_facts"])
    complement_surplus = sorted(nonconstant_surplus & seed_complements)
    unclassified_target_surplus = sorted(nonconstant_surplus - seed_complements)

    surplus_visible = [
        (str(left), str(right))
        for left, right in case.observed["surplus_visible_pairs"]
    ]
    seed_separated_visible = [
        pair
        for pair in surplus_visible
        if _pair_crosses_any_seed_members(pair, seed_members.values())
    ]
    unclassified_visible = [
        pair for pair in surplus_visible if pair not in seed_separated_visible
    ]

    if nonconstant_surplus and not unclassified_target_surplus:
        target_classification = "seed_complement_only"
    elif nonconstant_surplus:
        target_classification = "has_unclassified_target_surplus"
    else:
        target_classification = "no_nonconstant_target_surplus"

    return {
        "target_classification": target_classification,
        "nonconstant_surplus_target_count": len(nonconstant_surplus),
        "seed_complement_target_count": len(complement_surplus),
        "seed_complement_target_facts": complement_surplus,
        "unclassified_nonconstant_target_count": len(unclassified_target_surplus),
        "unclassified_nonconstant_target_facts": unclassified_target_surplus,
        "surplus_visible_pair_count": len(surplus_visible),
        "seed_separation_visible_pair_count": len(seed_separated_visible),
        "unclassified_visible_pair_count": len(unclassified_visible),
        "unclassified_visible_pairs": unclassified_visible,
    }


def _family_surplus_redundancy(
    cases: tuple[ClosureDiscoveryCase, ...],
) -> dict[str, object]:
    rows = [_case_surplus_redundancy(case) for case in cases]
    target_classification_counts: dict[str, int] = {}
    for row in rows:
        key = str(row["target_classification"])
        target_classification_counts[key] = target_classification_counts.get(key, 0) + 1
    return {
        "case_count": len(cases),
        "target_classification_counts": target_classification_counts,
        "nonconstant_surplus_target_count": sum(
            int(row["nonconstant_surplus_target_count"]) for row in rows
        ),
        "seed_complement_target_count": sum(
            int(row["seed_complement_target_count"]) for row in rows
        ),
        "unclassified_nonconstant_target_count": sum(
            int(row["unclassified_nonconstant_target_count"]) for row in rows
        ),
        "surplus_visible_pair_count": sum(
            int(row["surplus_visible_pair_count"]) for row in rows
        ),
        "seed_separation_visible_pair_count": sum(
            int(row["seed_separation_visible_pair_count"]) for row in rows
        ),
        "unclassified_visible_pair_count": sum(
            int(row["unclassified_visible_pair_count"]) for row in rows
        ),
        "claim_boundary": (
            "First-pass redundancy classification only. Seed complements and "
            "seed-separated visible pairs are easy closure consequences, not "
            "canonical implication-basis structure. Unclassified buckets are "
            "the only current candidates for richer dynamic surplus."
        ),
    }


def _predicate_fact_members(fact: str) -> frozenset[str]:
    if fact == "pred:{}":
        return frozenset()
    prefix = "pred:{"
    if not fact.startswith(prefix) or not fact.endswith("}"):
        raise ValueError(f"unsupported predicate fact key: {fact}")
    inner = fact[len(prefix):-1]
    if not inner:
        return frozenset()
    return frozenset(inner.split(","))


def _predicate_fact_key_for_states(
    states: tuple[str, ...],
    members: frozenset[str],
) -> str:
    if not members:
        return "pred:{}"
    ordered = [state for state in states if state in members]
    return "pred:{" + ",".join(ordered) + "}"


def _pair_crosses_any_seed_members(
    pair: Pair,
    seed_member_sets: object,
) -> bool:
    left, right = pair
    return any(
        (left in members) != (right in members)
        for members in seed_member_sets
    )
