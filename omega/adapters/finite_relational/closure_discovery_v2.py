"""Closure-discovery v2 over richer finite fact languages.

The v0 closure-discovery sweep generated Boolean predicate and visible-pair
facts. This module keeps the same finite-presentation discipline but broadens
the fact universe to include dynamic profile facts and structural process
coherence facts. It is a pilot, not a theorem layer.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations, product

from omega.adapters.finite_relational.facts_common import Pair, reachable_pairs


@dataclass(frozen=True)
class ClosureV2Fact:
    """A generated fact interpreted as a predicate over presentations."""

    key: str
    kind: str
    dynamic: bool
    profile: tuple[tuple[str, str], ...] = ()

    @property
    def is_profile(self) -> bool:
        return bool(self.profile)

    @property
    def nonconstant_profile(self) -> bool:
        return len({value for _state, value in self.profile}) > 1

    def profile_map(self) -> dict[str, str]:
        return dict(self.profile)


@dataclass(frozen=True)
class ClosureV2Case:
    """One generated graph case plus its closure-v2 result."""

    case_id: str
    states: tuple[str, ...]
    edges: tuple[Pair, ...]
    seed_fact_keys: tuple[str, ...]
    facts: tuple[ClosureV2Fact, ...]
    observed: dict[str, object]

    @property
    def has_dynamic_surplus(self) -> bool:
        return bool(self.observed["dynamic_surplus_facts"])

    @property
    def has_unclassified_dynamic_profile_surplus(self) -> bool:
        return bool(self.observed["unclassified_dynamic_profile_surplus_facts"])

    @property
    def classification(self) -> str:
        if not self.observed["admissible_nonempty"]:
            return "inconsistent_seed"
        if self.has_unclassified_dynamic_profile_surplus:
            return "unclassified_dynamic_profile_surplus"
        if self.has_dynamic_surplus:
            return "dynamic_surplus"
        return "collapse"

    def summary(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "state_count": len(self.states),
            "edge_count": len(self.edges),
            "seed_fact_keys": list(self.seed_fact_keys),
            "classification": self.classification,
            "presentation_universe_count": self.observed[
                "presentation_universe_count"
            ],
            "admissible_presentation_count": self.observed[
                "admissible_presentation_count"
            ],
            "closure_fact_count": self.observed["closure_fact_count"],
            "surplus_fact_count": self.observed["surplus_fact_count"],
            "dynamic_surplus_facts": self.observed["dynamic_surplus_facts"],
            "seed_determined_dynamic_profile_surplus_facts": self.observed[
                "seed_determined_dynamic_profile_surplus_facts"
            ],
            "unclassified_dynamic_profile_surplus_facts": self.observed[
                "unclassified_dynamic_profile_surplus_facts"
            ],
            "seed_forced_structural_surplus_facts": self.observed[
                "seed_forced_structural_surplus_facts"
            ],
            "globally_valid_surplus_facts": self.observed[
                "globally_valid_surplus_facts"
            ],
        }


@dataclass(frozen=True)
class ClosureV2Family:
    """A deterministic generated family for closure-discovery v2."""

    family_id: str
    description: str
    search_space: dict[str, object]
    cases: tuple[ClosureV2Case, ...]

    @property
    def dynamic_surplus_cases(self) -> tuple[ClosureV2Case, ...]:
        return tuple(case for case in self.cases if case.has_dynamic_surplus)

    @property
    def unclassified_dynamic_profile_cases(self) -> tuple[ClosureV2Case, ...]:
        return tuple(
            case
            for case in self.cases
            if case.has_unclassified_dynamic_profile_surplus
        )

    @property
    def collapse_cases(self) -> tuple[ClosureV2Case, ...]:
        return tuple(case for case in self.cases if case.classification == "collapse")

    @property
    def representative_cases(self) -> tuple[ClosureV2Case, ...]:
        representatives: list[ClosureV2Case] = []
        if self.unclassified_dynamic_profile_cases:
            representatives.append(self.unclassified_dynamic_profile_cases[0])
        if self.dynamic_surplus_cases:
            candidate = self.dynamic_surplus_cases[0]
            if candidate not in representatives:
                representatives.append(candidate)
        if self.collapse_cases:
            representatives.append(self.collapse_cases[0])
        return tuple(representatives)

    def summary(self) -> dict[str, object]:
        aggregate = _aggregate_case_observations(self.cases)
        return {
            "family_id": self.family_id,
            "description": self.description,
            "search_space": self.search_space,
            "case_count": len(self.cases),
            "dynamic_surplus_case_count": len(self.dynamic_surplus_cases),
            "unclassified_dynamic_profile_case_count": len(
                self.unclassified_dynamic_profile_cases
            ),
            "collapse_case_count": len(self.collapse_cases),
            "representative_case_count": len(self.representative_cases),
            "representative_cases": [
                case.summary() for case in self.representative_cases
            ],
            "aggregate": aggregate,
        }


def generate_closure_discovery_v2() -> tuple[ClosureV2Family, ...]:
    """Run generated closure-discovery v2 families."""

    return (
        _step_lifting_seed_family(),
        _observed_word_seed_family(),
        _constant_control_family(),
    )


def closure_discovery_v2_summary() -> dict[str, object]:
    families = generate_closure_discovery_v2()
    all_cases = tuple(case for family in families for case in family.cases)
    return {
        "family_count": len(families),
        "case_count": len(all_cases),
        "dynamic_surplus_case_count": sum(
            len(family.dynamic_surplus_cases) for family in families
        ),
        "unclassified_dynamic_profile_case_count": sum(
            len(family.unclassified_dynamic_profile_cases) for family in families
        ),
        "collapse_case_count": sum(len(family.collapse_cases) for family in families),
        "aggregate": _aggregate_case_observations(all_cases),
        "families": [family.summary() for family in families],
    }


def _step_lifting_seed_family() -> ClosureV2Family:
    states = ("a", "b", "c")
    cases = tuple(
        _closure_v2_case(
            case_id=f"step_lifting_seed_{index:02d}",
            states=states,
            edges=edges,
            seed_fact_keys=("struct:step_lifting",),
        )
        for index, edges in enumerate(_edge_subsets(states, loops=False))
    )
    return ClosureV2Family(
        family_id="step_lifting_seed_graph_sweep",
        description=(
            "Enumerates loop-free directed graphs on three states, admits "
            "presentations satisfying representative-wise step lifting, and "
            "asks which richer dynamic facts are forced."
        ),
        search_space={
            "state_count": len(states),
            "edge_subset_count": len(cases),
            "loops": False,
            "seed": "struct:step_lifting",
            "expected_surplus_predeclared": False,
        },
        cases=cases,
    )


def _observed_word_seed_family() -> ClosureV2Family:
    states = ("a", "b", "c")
    cases = tuple(
        _closure_v2_case(
            case_id=f"observed_word_seed_{index:02d}",
            states=states,
            edges=edges,
            seed_fact_keys=("profile:observed_words:goal_status:h=1",),
        )
        for index, edges in enumerate(_edge_subsets(states, loops=False))
    )
    return ClosureV2Family(
        family_id="observed_word_seed_graph_sweep",
        description=(
            "Enumerates loop-free directed graphs on three states, admits "
            "presentations respecting the horizon-1 observed extendable word "
            "profile, and computes closure over reachability, viability, "
            "path-count, and observed-language profiles."
        ),
        search_space={
            "state_count": len(states),
            "edge_subset_count": len(cases),
            "loops": False,
            "seed": "profile:observed_words:goal_status:h=1",
            "expected_surplus_predeclared": False,
        },
        cases=cases,
    )


def _constant_control_family() -> ClosureV2Family:
    states = ("a", "b", "c")
    selected_edges = (
        tuple(),
        (("a", "b"),),
        (("a", "b"), ("b", "c")),
        (("a", "b"), ("b", "a"), ("c", "a")),
    )
    cases = tuple(
        _closure_v2_case(
            case_id=f"constant_control_{index:02d}",
            states=states,
            edges=edges,
            seed_fact_keys=("profile:constant_all",),
        )
        for index, edges in enumerate(selected_edges)
    )
    return ClosureV2Family(
        family_id="constant_seed_control",
        description=(
            "Control family using only the constant profile as seed. It checks "
            "that richer fact generation does not by itself license dynamic "
            "closure without admissibility pressure."
        ),
        search_space={
            "state_count": len(states),
            "case_count": len(cases),
            "seed": "profile:constant_all",
            "expected_surplus_predeclared": False,
        },
        cases=cases,
    )


def _closure_v2_case(
    *,
    case_id: str,
    states: tuple[str, ...],
    edges: tuple[Pair, ...],
    seed_fact_keys: tuple[str, ...],
) -> ClosureV2Case:
    facts = _generated_fact_universe(states, edges)
    observed = _derive_closure_v2(states, edges, facts, seed_fact_keys)
    return ClosureV2Case(
        case_id=case_id,
        states=states,
        edges=edges,
        seed_fact_keys=seed_fact_keys,
        facts=facts,
        observed=observed,
    )


def _derive_closure_v2(
    states: tuple[str, ...],
    edges: tuple[Pair, ...],
    facts: tuple[ClosureV2Fact, ...],
    seed_fact_keys: tuple[str, ...],
) -> dict[str, object]:
    fact_by_key = {fact.key: fact for fact in facts}
    missing_seed = sorted(set(seed_fact_keys) - set(fact_by_key))
    if missing_seed:
        raise ValueError(f"closure v2 seed facts missing from universe: {missing_seed}")

    presentations = list(_all_partition_mappings(states))
    admissible = [
        mapping
        for mapping in presentations
        if all(
            _fact_holds(states, edges, mapping, fact_by_key[key])
            for key in seed_fact_keys
        )
    ]
    closure = {
        fact.key
        for fact in facts
        if admissible
        and all(_fact_holds(states, edges, mapping, fact) for mapping in admissible)
    }
    globally_valid = {
        fact.key
        for fact in facts
        if all(_fact_holds(states, edges, mapping, fact) for mapping in presentations)
    }
    seed = set(seed_fact_keys)
    surplus = closure - seed
    dynamic_surplus = {
        key for key in surplus if fact_by_key[key].dynamic and key not in globally_valid
    }
    seed_profile_keys = [
        key for key in seed_fact_keys if fact_by_key[key].is_profile
    ]
    seed_determined_dynamic_profiles = {
        key
        for key in dynamic_surplus
        if fact_by_key[key].is_profile
        and _profile_is_seed_determined(
            states,
            fact_by_key[key],
            [fact_by_key[seed_key] for seed_key in seed_profile_keys],
        )
    }
    unclassified_dynamic_profiles = {
        key
        for key in dynamic_surplus
        if fact_by_key[key].is_profile
        and key not in seed_determined_dynamic_profiles
    }
    seed_forced_structural = {
        key
        for key in dynamic_surplus
        if fact_by_key[key].kind == "structural" and key not in globally_valid
    }
    return {
        "closure_mode": "generated_richer_fact_language_v2",
        "state_count": len(states),
        "edge_count": len(edges),
        "presentation_universe_count": len(presentations),
        "admissible_presentation_count": len(admissible),
        "admissible_nonempty": bool(admissible),
        "admissible_presentations": [
            _presentation_signature(states, mapping) for mapping in admissible
        ],
        "fact_universe_count": len(facts),
        "fact_universe": [_fact_summary(fact) for fact in facts],
        "seed_fact_keys": sorted(seed),
        "closure_fact_count": len(closure),
        "closure_facts": sorted(closure),
        "surplus_fact_count": len(surplus),
        "surplus_facts": sorted(surplus),
        "dynamic_surplus_facts": sorted(dynamic_surplus),
        "seed_determined_dynamic_profile_surplus_facts": sorted(
            seed_determined_dynamic_profiles
        ),
        "unclassified_dynamic_profile_surplus_facts": sorted(
            unclassified_dynamic_profiles
        ),
        "seed_forced_structural_surplus_facts": sorted(seed_forced_structural),
        "globally_valid_surplus_facts": sorted(globally_valid & surplus),
        "claim_boundary": (
            "Closure v2 is a generated finite pilot over richer fact objects. "
            "It is not a canonical implication basis and does not establish "
            "natural admissibility, global invariance, agency, value, or Omega."
        ),
    }


def _generated_fact_universe(
    states: tuple[str, ...],
    edges: tuple[Pair, ...],
) -> tuple[ClosureV2Fact, ...]:
    safe = frozenset(states)
    goal = states[-1]
    observation = {state: ("goal" if state == goal else "other") for state in states}
    facts = [
        _profile_fact(
            "profile:constant_all",
            "predicate",
            {state: "1" for state in states},
            dynamic=False,
        ),
        _profile_fact(
            "profile:reach:goal",
            "reachability_profile",
            {
                state: str(int((state, goal) in reachable_pairs(set(states), set(edges))))
                for state in states
            },
            dynamic=True,
        ),
        _profile_fact(
            "profile:viability:safe_all",
            "viability_profile",
            {
                state: str(int(state in _viability_kernel(set(edges), safe)))
                for state in states
            },
            dynamic=True,
        ),
        _profile_fact(
            "profile:safe_prefix_count:h=1",
            "safe_prefix_count_profile",
            _safe_prefix_count_profile(states, edges, safe, horizon=1),
            dynamic=True,
        ),
        _profile_fact(
            "profile:safe_prefix_count:h=2",
            "safe_prefix_count_profile",
            _safe_prefix_count_profile(states, edges, safe, horizon=2),
            dynamic=True,
        ),
        _profile_fact(
            "profile:extendable_safe_prefix_count:h=1",
            "extendable_safe_prefix_count_profile",
            _safe_prefix_count_profile(
                states,
                edges,
                safe,
                horizon=1,
                require_extendable_endpoint=True,
            ),
            dynamic=True,
        ),
        _profile_fact(
            "profile:observed_words:goal_status:h=1",
            "observed_word_profile",
            _observed_extendable_words_profile(
                states,
                edges,
                safe,
                observation,
                horizon=1,
            ),
            dynamic=True,
        ),
        _profile_fact(
            "profile:observed_words:goal_status:h=2",
            "observed_word_profile",
            _observed_extendable_words_profile(
                states,
                edges,
                safe,
                observation,
                horizon=2,
            ),
            dynamic=True,
        ),
        ClosureV2Fact("struct:step_lifting", "structural", True),
        ClosureV2Fact("struct:path_lifting:h=1", "structural", True),
        ClosureV2Fact("struct:path_lifting:h=2", "structural", True),
        ClosureV2Fact("struct:path_lifting:h=3", "structural", True),
    ]
    for left, right in product(states, states):
        if left != right:
            facts.append(ClosureV2Fact(f"visible:{left}->{right}", "visible_pair", False))
    return tuple(facts)


def _profile_fact(
    key: str,
    kind: str,
    values: dict[str, object],
    *,
    dynamic: bool,
) -> ClosureV2Fact:
    return ClosureV2Fact(
        key=key,
        kind=kind,
        dynamic=dynamic,
        profile=tuple(sorted((state, str(value)) for state, value in values.items())),
    )


def _fact_holds(
    states: tuple[str, ...],
    edges: tuple[Pair, ...],
    mapping: dict[str, str],
    fact: ClosureV2Fact,
) -> bool:
    if fact.is_profile:
        return _mapping_respects_profile(states, mapping, fact.profile_map())
    if fact.kind == "visible_pair":
        left, right = fact.key.removeprefix("visible:").split("->", maxsplit=1)
        return mapping[left] != mapping[right]
    if fact.key == "struct:step_lifting":
        return _step_lifts(states, edges, mapping)
    if fact.key.startswith("struct:path_lifting:h="):
        horizon = int(fact.key.rsplit("=", maxsplit=1)[1])
        return _path_lifts(states, edges, mapping, horizon=horizon)
    raise ValueError(f"unsupported closure v2 fact: {fact.key}")


def _fact_summary(fact: ClosureV2Fact) -> dict[str, object]:
    values = dict(fact.profile)
    return {
        "key": fact.key,
        "kind": fact.kind,
        "dynamic": fact.dynamic,
        "nonconstant_profile": fact.nonconstant_profile,
        "profile": values,
    }


def _mapping_respects_profile(
    states: tuple[str, ...],
    mapping: dict[str, str],
    profile: dict[str, str],
) -> bool:
    return all(
        mapping[left] != mapping[right] or profile[left] == profile[right]
        for left, right in product(states, states)
    )


def _profile_is_seed_determined(
    states: tuple[str, ...],
    fact: ClosureV2Fact,
    seed_facts: list[ClosureV2Fact],
) -> bool:
    if not seed_facts:
        return False
    profile = fact.profile_map()
    seed_profiles = [seed.profile_map() for seed in seed_facts]
    seen: dict[tuple[str, ...], str] = {}
    for state in states:
        key = tuple(seed_profile[state] for seed_profile in seed_profiles)
        value = profile[state]
        if key in seen and seen[key] != value:
            return False
        seen[key] = value
    return True


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


def _safe_prefix_count_profile(
    states: tuple[str, ...],
    edges: tuple[Pair, ...],
    safe: frozenset[str],
    *,
    horizon: int,
    require_extendable_endpoint: bool = False,
) -> dict[str, int]:
    kernel = _viability_kernel(set(edges), safe)
    adjacency: dict[str, set[str]] = defaultdict(set)
    for source, target in edges:
        adjacency[source].add(target)
    profile: dict[str, int] = {}
    for start in states:
        if start not in safe:
            profile[start] = 0
            continue
        current = {start: 1}
        for _step in range(horizon):
            next_counts: dict[str, int] = defaultdict(int)
            for state, count in current.items():
                for target in adjacency[state]:
                    if target in safe:
                        next_counts[target] += count
            current = dict(next_counts)
        if require_extendable_endpoint:
            profile[start] = sum(
                count for state, count in current.items() if state in kernel
            )
        else:
            profile[start] = sum(current.values())
    return profile


def _observed_extendable_words_profile(
    states: tuple[str, ...],
    edges: tuple[Pair, ...],
    safe: frozenset[str],
    observation: dict[str, str],
    *,
    horizon: int,
) -> dict[str, str]:
    kernel = _viability_kernel(set(edges), safe)
    adjacency: dict[str, set[str]] = defaultdict(set)
    for source, target in edges:
        adjacency[source].add(target)
    profile: dict[str, str] = {}
    for start in states:
        if start not in safe:
            profile[start] = ""
            continue
        current = {(start, (observation[start],))}
        for _step in range(horizon):
            current = {
                (target, (*word, observation[target]))
                for state, word in current
                for target in adjacency[state]
                if target in safe
            }
        words = sorted(word for state, word in current if state in kernel)
        profile[start] = "|".join(",".join(word) for word in words)
    return profile


def _viability_kernel(edges: set[Pair], safe: frozenset[str]) -> set[str]:
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


def _edge_subsets(
    states: tuple[str, ...],
    *,
    loops: bool,
) -> tuple[tuple[Pair, ...], ...]:
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


def _presentation_signature(
    states: tuple[str, ...],
    mapping: dict[str, str],
) -> list[tuple[str, str]]:
    return [(state, mapping[state]) for state in states]


def _aggregate_case_observations(
    cases: tuple[ClosureV2Case, ...],
) -> dict[str, object]:
    classification_counts: dict[str, int] = {}
    for case in cases:
        classification_counts[case.classification] = (
            classification_counts.get(case.classification, 0) + 1
        )
    return {
        "case_count": len(cases),
        "classification_counts": classification_counts,
        "dynamic_surplus_fact_count": sum(
            len(case.observed["dynamic_surplus_facts"]) for case in cases
        ),
        "seed_determined_dynamic_profile_surplus_fact_count": sum(
            len(case.observed["seed_determined_dynamic_profile_surplus_facts"])
            for case in cases
        ),
        "unclassified_dynamic_profile_surplus_fact_count": sum(
            len(case.observed["unclassified_dynamic_profile_surplus_facts"])
            for case in cases
        ),
        "seed_forced_structural_surplus_fact_count": sum(
            len(case.observed["seed_forced_structural_surplus_facts"])
            for case in cases
        ),
        "globally_valid_surplus_fact_count": sum(
            len(case.observed["globally_valid_surplus_facts"]) for case in cases
        ),
    }
