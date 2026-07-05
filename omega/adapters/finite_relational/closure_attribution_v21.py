"""Closure v2.1 attribution and held-out checks.

This module does not add new fact kinds. It classifies Closure v2 surplus using
fixed explanatory rules, then applies the same classifier to held-out generated
families.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import product
from random import Random

from omega.adapters.finite_relational.closure_discovery_v2 import (
    ClosureV2Case,
    ClosureV2Fact,
    closure_v2_case_from_edges,
    generate_closure_discovery_v2,
)
from omega.adapters.finite_relational.facts_common import Pair


PROCESS_COHERENCE_FACTS = (
    "struct:step_lifting",
    "struct:path_lifting:h=1",
    "struct:path_lifting:h=2",
    "struct:path_lifting:h=3",
)


@dataclass(frozen=True)
class ClosureAttribution:
    """Attribution result for one surplus fact in one closure-v2 case."""

    fact_key: str
    bucket: str
    support_fact: str | None = None

    def summary(self) -> dict[str, object]:
        return {
            "fact_key": self.fact_key,
            "bucket": self.bucket,
            "support_fact": self.support_fact,
        }


@dataclass(frozen=True)
class ClosureAttributionCase:
    """One closure-v2 case with v2.1 surplus attribution."""

    case: ClosureV2Case
    attributions: tuple[ClosureAttribution, ...]

    @property
    def residual(self) -> tuple[ClosureAttribution, ...]:
        return tuple(
            attribution
            for attribution in self.attributions
            if attribution.bucket == "residual"
        )

    @property
    def has_residual(self) -> bool:
        return bool(self.residual)

    def bucket_counts(self) -> dict[str, int]:
        return dict(Counter(attribution.bucket for attribution in self.attributions))

    def summary(self) -> dict[str, object]:
        return {
            **self.case.summary(),
            "attribution_bucket_counts": self.bucket_counts(),
            "residual_count": len(self.residual),
            "residual_facts": [attribution.fact_key for attribution in self.residual],
            "attributions": [
                attribution.summary() for attribution in self.attributions
            ],
        }


@dataclass(frozen=True)
class ClosureAttributionFamily:
    """Attributed closure-v2 family."""

    family_id: str
    description: str
    search_space: dict[str, object]
    cases: tuple[ClosureAttributionCase, ...]

    @property
    def residual_cases(self) -> tuple[ClosureAttributionCase, ...]:
        return tuple(case for case in self.cases if case.has_residual)

    @property
    def representative_cases(self) -> tuple[ClosureAttributionCase, ...]:
        representatives: list[ClosureAttributionCase] = []
        if self.residual_cases:
            representatives.append(self.residual_cases[0])
        process_cases = [
            case
            for case in self.cases
            if "bounded_process_coherence_invariance" in case.bucket_counts()
        ]
        if process_cases and process_cases[0] not in representatives:
            representatives.append(process_cases[0])
        collapse_cases = [
            case for case in self.cases if case.case.classification == "collapse"
        ]
        if collapse_cases and collapse_cases[0] not in representatives:
            representatives.append(collapse_cases[0])
        return tuple(representatives)

    def summary(self) -> dict[str, object]:
        aggregate = _aggregate_attribution_cases(self.cases)
        return {
            "family_id": self.family_id,
            "description": self.description,
            "search_space": self.search_space,
            "case_count": len(self.cases),
            "residual_case_count": len(self.residual_cases),
            "representative_case_count": len(self.representative_cases),
            "representative_cases": [
                case.summary() for case in self.representative_cases
            ],
            "aggregate": aggregate,
        }


def generate_closure_attribution_v21() -> tuple[ClosureAttributionFamily, ...]:
    """Run attribution over current v2 and held-out generated families."""

    return (
        _current_v2_attribution_family(),
        _heldout_step_lifting_family(),
        _heldout_observed_word_family(),
        _heldout_constant_control_family(),
    )


def closure_attribution_v21_summary() -> dict[str, object]:
    families = generate_closure_attribution_v21()
    all_cases = tuple(case for family in families for case in family.cases)
    aggregate = _aggregate_attribution_cases(all_cases)
    return {
        "family_count": len(families),
        "case_count": len(all_cases),
        "residual_case_count": sum(len(family.residual_cases) for family in families),
        "aggregate": aggregate,
        "families": [family.summary() for family in families],
    }


def attribute_closure_v2_case(case: ClosureV2Case) -> ClosureAttributionCase:
    """Classify every surplus fact in a closure-v2 case."""

    fact_by_key = {fact.key: fact for fact in case.facts}
    closure = set(case.observed["closure_facts"])
    surplus = set(case.observed["surplus_facts"])
    globally_valid = set(case.observed["globally_valid_surplus_facts"])
    seed_determined = set(
        case.observed["seed_determined_dynamic_profile_surplus_facts"]
    )
    seed_forced_structural = set(case.observed["seed_forced_structural_surplus_facts"])
    attributions = [
        _attribute_surplus_fact(
            case,
            fact_by_key,
            closure,
            globally_valid,
            seed_determined,
            seed_forced_structural,
            fact_key,
        )
        for fact_key in sorted(surplus)
    ]
    return ClosureAttributionCase(case=case, attributions=tuple(attributions))


def _attribute_surplus_fact(
    case: ClosureV2Case,
    fact_by_key: dict[str, ClosureV2Fact],
    closure: set[str],
    globally_valid: set[str],
    seed_determined: set[str],
    seed_forced_structural: set[str],
    fact_key: str,
) -> ClosureAttribution:
    if fact_key in globally_valid:
        return ClosureAttribution(fact_key, "globally_valid")
    if fact_key in seed_determined:
        return ClosureAttribution(fact_key, "seed_determined_profile")
    if _step_implies_path_lifting(fact_key, closure):
        return ClosureAttribution(
            fact_key,
            "step_implies_path_lifting",
            support_fact="struct:step_lifting",
        )
    if fact_key in seed_forced_structural:
        support = _first_present_process_support(closure)
        return ClosureAttribution(
            fact_key,
            "seed_forced_structural",
            support_fact=support,
        )
    fact = fact_by_key[fact_key]
    if fact.kind == "visible_pair":
        support = _visible_pair_support(
            fact_key,
            case.seed_fact_keys,
            closure,
            fact_by_key,
        )
        if support is not None:
            bucket = (
                "seed_profile_separation"
                if support in set(case.seed_fact_keys)
                else "profile_fiber_separation"
            )
            return ClosureAttribution(fact_key, bucket, support_fact=support)
        process_support = _bounded_process_coherence_support(case, fact)
        if process_support is not None:
            return ClosureAttribution(
                fact_key,
                "process_coherence_separation",
                support_fact=process_support,
            )
    if fact.is_profile and fact.dynamic:
        support = _bounded_process_coherence_support(case, fact)
        if support is not None:
            return ClosureAttribution(
                fact_key,
                "bounded_process_coherence_invariance",
                support_fact=support,
            )
    return ClosureAttribution(fact_key, "residual")


def _visible_pair_support(
    fact_key: str,
    seed_fact_keys: tuple[str, ...],
    closure: set[str],
    fact_by_key: dict[str, ClosureV2Fact],
) -> str | None:
    left, right = fact_key.removeprefix("visible:").split("->", maxsplit=1)
    ordered_candidates = [
        *seed_fact_keys,
        *(key for key in sorted(closure) if key not in set(seed_fact_keys)),
    ]
    for candidate_key in ordered_candidates:
        candidate = fact_by_key.get(candidate_key)
        if candidate is None or not candidate.is_profile:
            continue
        profile = candidate.profile_map()
        if profile[left] != profile[right]:
            return candidate_key
    return None


def _step_implies_path_lifting(fact_key: str, closure: set[str]) -> bool:
    return (
        fact_key.startswith("struct:path_lifting:h=")
        and "struct:step_lifting" in closure
    )


def _first_present_process_support(closure: set[str]) -> str | None:
    return next((fact for fact in PROCESS_COHERENCE_FACTS if fact in closure), None)


def _bounded_process_coherence_support(
    case: ClosureV2Case,
    fact: ClosureV2Fact,
) -> str | None:
    """Find a fixed process-coherence fact that entails a profile fact."""

    for support_key in PROCESS_COHERENCE_FACTS:
        support = next(
            (candidate for candidate in case.facts if candidate.key == support_key),
            None,
        )
        if support is None:
            continue
        if _support_entails_fact(case, support, fact):
            return support_key
    return None


def _support_entails_fact(
    case: ClosureV2Case,
    support: ClosureV2Fact,
    fact: ClosureV2Fact,
) -> bool:
    presentations = _all_partition_mappings(case.states)
    admissible = [
        mapping
        for mapping in presentations
        if _fact_holds(case.states, case.edges, mapping, support)
    ]
    return bool(admissible) and all(
        _fact_holds(case.states, case.edges, mapping, fact)
        for mapping in admissible
    )


def _current_v2_attribution_family() -> ClosureAttributionFamily:
    v2_families = generate_closure_discovery_v2()
    cases = tuple(
        attribute_closure_v2_case(case)
        for family in v2_families
        for case in family.cases
    )
    return ClosureAttributionFamily(
        family_id="current_v2_attribution",
        description=(
            "Attributes the retained Closure v2 n=3 graph sweep without changing "
            "the v2 fact universe or case definitions."
        ),
        search_space={
            "source": "generate_closure_discovery_v2",
            "case_count": len(cases),
            "classifier_fixed_before_heldout": True,
        },
        cases=cases,
    )


def _heldout_step_lifting_family() -> ClosureAttributionFamily:
    states = ("a", "b", "c", "d")
    sampled_edges = _sample_edge_subsets(states, sample_size=32, seed=20260705)
    cases = tuple(
        attribute_closure_v2_case(
            closure_v2_case_from_edges(
                case_id=f"heldout_n4_step_{index:02d}",
                states=states,
                edges=edges,
                seed_fact_keys=("struct:step_lifting",),
            )
        )
        for index, edges in enumerate(sampled_edges)
    )
    return ClosureAttributionFamily(
        family_id="heldout_n4_step_lifting_sample",
        description=(
            "Held-out sampled loop-free four-state graphs with step lifting as "
            "the only seed."
        ),
        search_space={
            "state_count": len(states),
            "sample_size": len(cases),
            "sampling_seed": 20260705,
            "edge_universe": "loop-free directed edges",
            "seed": "struct:step_lifting",
        },
        cases=cases,
    )


def _heldout_observed_word_family() -> ClosureAttributionFamily:
    states = ("a", "b", "c", "d")
    sampled_edges = _sample_edge_subsets(states, sample_size=32, seed=20260706)
    cases = tuple(
        attribute_closure_v2_case(
            closure_v2_case_from_edges(
                case_id=f"heldout_n4_observed_word_{index:02d}",
                states=states,
                edges=edges,
                seed_fact_keys=("profile:observed_words:goal_status:h=1",),
            )
        )
        for index, edges in enumerate(sampled_edges)
    )
    return ClosureAttributionFamily(
        family_id="heldout_n4_observed_word_sample",
        description=(
            "Held-out sampled loop-free four-state graphs with the horizon-1 "
            "observed extendable word profile as seed."
        ),
        search_space={
            "state_count": len(states),
            "sample_size": len(cases),
            "sampling_seed": 20260706,
            "edge_universe": "loop-free directed edges",
            "seed": "profile:observed_words:goal_status:h=1",
        },
        cases=cases,
    )


def _heldout_constant_control_family() -> ClosureAttributionFamily:
    states = ("a", "b", "c", "d")
    sampled_edges = _sample_edge_subsets(states, sample_size=8, seed=20260707)
    cases = tuple(
        attribute_closure_v2_case(
            closure_v2_case_from_edges(
                case_id=f"heldout_n4_constant_{index:02d}",
                states=states,
                edges=edges,
                seed_fact_keys=("profile:constant_all",),
            )
        )
        for index, edges in enumerate(sampled_edges)
    )
    return ClosureAttributionFamily(
        family_id="heldout_n4_constant_control",
        description=(
            "Held-out sampled loop-free four-state graphs with only the constant "
            "profile as seed."
        ),
        search_space={
            "state_count": len(states),
            "sample_size": len(cases),
            "sampling_seed": 20260707,
            "edge_universe": "loop-free directed edges",
            "seed": "profile:constant_all",
        },
        cases=cases,
    )


def _sample_edge_subsets(
    states: tuple[str, ...],
    *,
    sample_size: int,
    seed: int,
) -> tuple[tuple[Pair, ...], ...]:
    possible_edges = tuple(
        (source, target)
        for source, target in product(states, states)
        if source != target
    )
    total = 1 << len(possible_edges)
    rng = Random(seed)
    masks = sorted(rng.sample(range(total), sample_size))
    return tuple(
        tuple(
            edge
            for index, edge in enumerate(possible_edges)
            if mask & (1 << index)
        )
        for mask in masks
    )


def _fact_holds(
    states: tuple[str, ...],
    edges: tuple[Pair, ...],
    mapping: dict[str, str],
    fact: ClosureV2Fact,
) -> bool:
    if fact.is_profile:
        profile = dict(fact.profile)
        return all(
            mapping[left] != mapping[right] or profile[left] == profile[right]
            for left, right in product(states, states)
        )
    if fact.kind == "visible_pair":
        left, right = fact.key.removeprefix("visible:").split("->", maxsplit=1)
        return mapping[left] != mapping[right]
    if fact.key == "struct:step_lifting":
        return _step_lifts(states, edges, mapping)
    if fact.key.startswith("struct:path_lifting:h="):
        horizon = int(fact.key.rsplit("=", maxsplit=1)[1])
        return _path_lifts(states, edges, mapping, horizon=horizon)
    raise ValueError(f"unsupported closure attribution fact: {fact.key}")


def _step_lifts(
    states: tuple[str, ...],
    edges: tuple[Pair, ...],
    mapping: dict[str, str],
) -> bool:
    abstract_edges = _induced_abstract_edges(edges, mapping)
    adjacency: dict[str, set[str]] = defaultdict(set)
    for source, target in edges:
        adjacency[source].add(target)
    for state in states:
        source_label = mapping[state]
        for abstract_source, abstract_target in abstract_edges:
            if abstract_source != source_label:
                continue
            if not any(mapping[target] == abstract_target for target in adjacency[state]):
                return False
    return True


def _path_lifts(
    states: tuple[str, ...],
    edges: tuple[Pair, ...],
    mapping: dict[str, str],
    *,
    horizon: int,
) -> bool:
    abstract_edges = _induced_abstract_edges(edges, mapping)
    exact_adjacency: dict[str, set[str]] = defaultdict(set)
    abstract_adjacency: dict[str, set[str]] = defaultdict(set)
    for source, target in edges:
        exact_adjacency[source].add(target)
    for source, target in abstract_edges:
        abstract_adjacency[source].add(target)
    for start in states:
        for abstract_path in _abstract_paths_from(
            mapping[start],
            abstract_adjacency,
            horizon,
        ):
            if not _abstract_path_lifts_from(
                start,
                abstract_path,
                exact_adjacency,
                mapping,
            ):
                return False
    return True


def _induced_abstract_edges(
    edges: tuple[Pair, ...],
    mapping: dict[str, str],
) -> set[Pair]:
    return {(mapping[source], mapping[target]) for source, target in edges}


def _abstract_paths_from(
    start: str,
    adjacency: dict[str, set[str]],
    horizon: int,
) -> list[tuple[str, ...]]:
    paths = [(start,)]
    frontier = [(start,)]
    for _step in range(horizon):
        next_frontier = []
        for path in frontier:
            for target in sorted(adjacency[path[-1]]):
                next_path = (*path, target)
                next_frontier.append(next_path)
                paths.append(next_path)
        frontier = next_frontier
    return paths


def _abstract_path_lifts_from(
    start: str,
    abstract_path: tuple[str, ...],
    exact_adjacency: dict[str, set[str]],
    mapping: dict[str, str],
) -> bool:
    frontier = {start}
    if mapping[start] != abstract_path[0]:
        return False
    for abstract_target in abstract_path[1:]:
        frontier = {
            target
            for state in frontier
            for target in exact_adjacency[state]
            if mapping[target] == abstract_target
        }
        if not frontier:
            return False
    return True


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


def _aggregate_attribution_cases(
    cases: tuple[ClosureAttributionCase, ...],
) -> dict[str, object]:
    bucket_counts: Counter[str] = Counter()
    support_counts: Counter[str] = Counter()
    residual_facts: Counter[str] = Counter()
    for case in cases:
        for attribution in case.attributions:
            bucket_counts[attribution.bucket] += 1
            if attribution.support_fact is not None:
                support_counts[attribution.support_fact] += 1
            if attribution.bucket == "residual":
                residual_facts[attribution.fact_key] += 1
    return {
        "surplus_fact_count": sum(bucket_counts.values()),
        "bucket_counts": dict(sorted(bucket_counts.items())),
        "support_counts": dict(sorted(support_counts.items())),
        "residual_fact_count": sum(residual_facts.values()),
        "residual_fact_keys": dict(sorted(residual_facts.items())),
        "case_count": len(cases),
        "residual_case_count": sum(1 for case in cases if case.has_residual),
    }
