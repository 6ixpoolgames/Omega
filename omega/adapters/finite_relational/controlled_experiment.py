"""Controlled finite-substrate studies for the finite relational adapter."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations, product
from typing import Any

from omega.adapters.finite_relational.adversarial_search import digest_json
from omega.adapters.finite_relational.audits import AuditResult, run_declared_audits
from omega.adapters.finite_relational.facts import (
    Pair,
    carrier_certificate_facts,
    reachable_pairs,
)
from omega.adapters.finite_relational.model import load_model, model_digest


@dataclass(frozen=True)
class ControlledExperimentCase:
    """One retained representative model from a controlled family."""

    case_id: str
    model: dict[str, Any]
    audit_results: tuple[AuditResult, ...]

    @property
    def all_passed(self) -> bool:
        return all(result.passed for result in self.audit_results)

    def summary(self) -> dict[str, object]:
        loaded = load_model(self.model)
        return {
            "case_id": self.case_id,
            "model_id": loaded.model_id,
            "model_digest": model_digest(loaded),
            "audit_count": len(self.audit_results),
            "passed_count": sum(1 for result in self.audit_results if result.passed),
            "all_passed": self.all_passed,
            "findings": [result.finding for result in self.audit_results],
        }


@dataclass(frozen=True)
class ControlledExperimentFamily:
    """A tiny enumerated family plus representative audit cases."""

    family_id: str
    description: str
    search_space: dict[str, object]
    metrics: dict[str, object]
    representative_cases: tuple[ControlledExperimentCase, ...]

    @property
    def all_passed(self) -> bool:
        return all(case.all_passed for case in self.representative_cases)

    def summary(self) -> dict[str, object]:
        return {
            "family_id": self.family_id,
            "description": self.description,
            "search_space": self.search_space,
            "metrics": self.metrics,
            "representative_case_count": len(self.representative_cases),
            "all_passed": self.all_passed,
            "representative_cases": [case.summary() for case in self.representative_cases],
        }


def generate_controlled_experiment() -> tuple[ControlledExperimentFamily, ...]:
    """Generate the first fixed finite-substrate empirical pilot.

    The families are exhaustive only over the small search spaces declared in
    each summary. They are not evidence about real systems.
    """

    return (
        _bounded_recovery_histogram_family(),
        _ordered_trace_bag_family(),
        _hidden_reachability_loss_family(),
        _carrier_endpoint_survival_family(),
    )


def _bounded_recovery_histogram_family() -> ControlledExperimentFamily:
    states = ("s0", "s1", "s2", "s3")
    observation = {
        "s0": "red",
        "s1": "red",
        "s2": "blue",
        "s3": "blue",
    }
    target_subsets = _all_subsets(states)
    recoverable_subsets = [
        subset for subset in target_subsets if _target_recoverable_from_observation(states, observation, subset)
    ]
    ambiguous_subsets = [subset for subset in target_subsets if subset not in recoverable_subsets]
    histogram = _histogram_signature(observation.values())

    return ControlledExperimentFamily(
        family_id="bounded_recovery_same_histogram",
        description=(
            "Enumerates all binary target predicates over four states under a fixed "
            "2/2 observation histogram and checks when a bounded Boolean decoder "
            "can recover the target."
        ),
        search_space={
            "state_count": len(states),
            "observation_labels": ["blue", "red"],
            "observation_histogram": histogram,
            "target_predicate_count": len(target_subsets),
        },
        metrics={
            "recoverable_target_count": len(recoverable_subsets),
            "not_recoverable_target_count": len(ambiguous_subsets),
            "recoverable_fraction": f"{len(recoverable_subsets)}/{len(target_subsets)}",
            "same_histogram_controls_recoverability": False,
        },
        representative_cases=(
            _validated_case(
                "bounded_recovery_histogram_pass",
                _bounded_recovery_model(
                    model_id="controlled_bounded_recovery_histogram_pass",
                    target_members=("s2", "s3"),
                    expectation="recoverable",
                    claim_boundary=(
                        "Controlled finite study representative: under the 2/2 "
                        "observation histogram, this target is recoverable by a "
                        "declared bounded decoder."
                    ),
                ),
            ),
            _validated_case(
                "bounded_recovery_histogram_fail",
                _bounded_recovery_model(
                    model_id="controlled_bounded_recovery_histogram_fail",
                    target_members=("s0", "s2"),
                    expectation="no_recovery",
                    claim_boundary=(
                        "Controlled finite study representative: under the same "
                        "2/2 observation histogram, this target is not recoverable "
                        "by any declared Boolean decoder."
                    ),
                ),
            ),
        ),
    )


def _ordered_trace_bag_family() -> ControlledExperimentFamily:
    traces = tuple("".join(bits) for bits in product(("A", "B"), repeat=4))
    bag_by_trace = {trace: _histogram_signature(trace) for trace in traces}
    alternating = {trace for trace in traces if _is_alternating(trace)}
    witness_pairs = [
        (left, right)
        for left, right in combinations(traces, 2)
        if bag_by_trace[left] == bag_by_trace[right]
        and ((left in alternating) != (right in alternating))
    ]
    same_bag_pairs = [
        (left, right)
        for left, right in combinations(traces, 2)
        if bag_by_trace[left] == bag_by_trace[right]
    ]

    return ControlledExperimentFamily(
        family_id="ordered_trace_same_bag",
        description=(
            "Enumerates binary traces of length four and checks whether unordered "
            "bag summaries determine an order-sensitive alternating-trace target."
        ),
        search_space={
            "alphabet": ["A", "B"],
            "trace_length": 4,
            "trace_count": len(traces),
            "same_bag_pair_count": len(same_bag_pairs),
        },
        metrics={
            "alternating_trace_count": len(alternating),
            "same_bag_target_change_pair_count": len(witness_pairs),
            "same_bag_target_change_fraction": f"{len(witness_pairs)}/{len(same_bag_pairs)}",
        },
        representative_cases=(
            _validated_case(
                "ordered_trace_same_bag_witness",
                {
                    "model_id": "controlled_ordered_trace_same_bag_witness",
                    "schema_version": "0.1.0",
                    "carrier": ["ABAB", "AABB"],
                    "predicates": {"alternating": ["ABAB"]},
                    "functions": {
                        "bag_summary": {
                            "domain": "state",
                            "mapping": {"ABAB": "A:2;B:2", "AABB": "A:2;B:2"},
                        }
                    },
                    "audits": [
                        {
                            "id": "same_bag_different_alternating_target",
                            "kind": "nonfactorization",
                            "summary": "bag_summary",
                            "target_predicate": "alternating",
                            "expect": "witness",
                        }
                    ],
                    "provenance": _provenance(
                        "Controlled finite study representative: unordered trace bag "
                        "summary does not determine an order-sensitive target."
                    ),
                },
            ),
        ),
    )


def _hidden_reachability_loss_family() -> ControlledExperimentFamily:
    states = ("a", "b", "c")
    source = "a"
    target = "c"
    edge_subsets = tuple(_edge_subsets(states, loops=False))
    hidden_loss_count = 0
    before_path_count = 0
    for before_edges in edge_subsets:
        before_path = (source, target) in reachable_pairs(set(states), set(before_edges))
        if before_path:
            before_path_count += 1
        for after_edges in edge_subsets:
            after_path = (source, target) in reachable_pairs(set(states), set(after_edges))
            if before_path and not after_path:
                hidden_loss_count += 1

    total_pairs = len(edge_subsets) * len(edge_subsets)
    return ControlledExperimentFamily(
        family_id="hidden_reachability_loss_under_stale_abstraction",
        description=(
            "Enumerates before/after transition relations on a three-state graph. "
            "The abstract transition is held fixed at the before relation, so it "
            "can hide exact reachability loss after perturbation."
        ),
        search_space={
            "state_count": len(states),
            "edge_subset_count": len(edge_subsets),
            "before_after_pair_count": total_pairs,
            "source": source,
            "target": target,
        },
        metrics={
            "before_path_count": before_path_count,
            "hidden_loss_pair_count": hidden_loss_count,
            "hidden_loss_fraction": f"{hidden_loss_count}/{total_pairs}",
        },
        representative_cases=(
            _validated_case(
                "hidden_reachability_loss_representative",
                {
                    "model_id": "controlled_hidden_reachability_loss_representative",
                    "schema_version": "0.1.0",
                    "carrier": list(states),
                    "relations": {
                        "before_next": [["a", "b"], ["b", "c"]],
                        "after_next": [["a", "b"]],
                        "abstract_next": [["a", "b"], ["b", "c"]],
                    },
                    "audits": [
                        {
                            "id": "stale_abstraction_hides_reachability_loss",
                            "kind": "hidden_reachability_loss",
                            "before_transition": "before_next",
                            "after_transition": "after_next",
                            "abstract_transition": "abstract_next",
                            "source": source,
                            "target": target,
                            "expect": "hidden_loss",
                        }
                    ],
                    "provenance": _provenance(
                        "Controlled finite study representative: stale abstraction "
                        "still reports a path after exact dynamics lose it."
                    ),
                },
            ),
        ),
    )


def _carrier_endpoint_survival_family() -> ControlledExperimentFamily:
    states = ("left", "right")
    edge_subsets = tuple(_edge_subsets(states, loops=True))
    forward_reach_count = 0
    certified_count = 0
    forward_but_uncertified_count = 0
    for edges in edge_subsets:
        model = _carrier_model(
            model_id="controlled_carrier_family_scratch",
            edges=edges,
            expectation="certified",
            claim_boundary="scratch model for controlled carrier-family enumeration",
        )
        facts = carrier_certificate_facts(
            load_model(model),
            transition="next",
            safety="safe",
            carrier="carrier_lr",
            left="left",
            right="right",
            separation="merge_separated",
        )
        forward_reach = ("left", "right") in reachable_pairs(set(states), set(edges))
        if forward_reach:
            forward_reach_count += 1
        if bool(facts["certified"]):
            certified_count += 1
        if forward_reach and not bool(facts["certified"]):
            forward_but_uncertified_count += 1

    return ControlledExperimentFamily(
        family_id="endpoint_forward_reach_not_carrier_certificate",
        description=(
            "Enumerates two-state transition relations, keeping endpoints safe "
            "and separated, and checks when endpoint forward reachability still "
            "fails recurrent carrier certification."
        ),
        search_space={
            "state_count": len(states),
            "edge_subset_count": len(edge_subsets),
            "loops_allowed": True,
        },
        metrics={
            "forward_reach_count": forward_reach_count,
            "certified_count": certified_count,
            "forward_reach_but_uncertified_count": forward_but_uncertified_count,
            "forward_reach_but_uncertified_fraction": (
                f"{forward_but_uncertified_count}/{len(edge_subsets)}"
            ),
        },
        representative_cases=(
            _validated_case(
                "endpoint_forward_reach_uncertified_representative",
                _carrier_model(
                    model_id="controlled_endpoint_forward_reach_uncertified_representative",
                    edges=(("left", "right"),),
                    expectation="uncertified",
                    claim_boundary=(
                        "Controlled finite study representative: endpoints are safe "
                        "and left reaches right, but missing return structure prevents "
                        "carrier certification."
                    ),
                ),
            ),
        ),
    )


def _bounded_recovery_model(
    *,
    model_id: str,
    target_members: tuple[str, ...],
    expectation: str,
    claim_boundary: str,
) -> dict[str, Any]:
    return {
        "model_id": model_id,
        "schema_version": "0.1.0",
        "domains": {
            "state": ["s0", "s1", "s2", "s3"],
            "observation": ["red", "blue"],
            "truth": ["false", "true"],
        },
        "predicates": {"target_true": list(target_members)},
        "functions": {
            "color_observation": {
                "domain": "state",
                "codomain": "observation",
                "mapping": {"s0": "red", "s1": "red", "s2": "blue", "s3": "blue"},
            },
            "decoder_false_false": _decoder("false", "false"),
            "decoder_false_true": _decoder("false", "true"),
            "decoder_true_false": _decoder("true", "false"),
            "decoder_true_true": _decoder("true", "true"),
        },
        "audits": [
            {
                "id": "bounded_decoder_family_recovers_target",
                "kind": "bounded_recovery",
                "observation": "color_observation",
                "target_predicate": "target_true",
                "decoders": [
                    "decoder_false_false",
                    "decoder_false_true",
                    "decoder_true_false",
                    "decoder_true_true",
                ],
                "expect": expectation,
            }
        ],
        "provenance": _provenance(claim_boundary),
    }


def _carrier_model(
    *,
    model_id: str,
    edges: tuple[Pair, ...],
    expectation: str,
    claim_boundary: str,
) -> dict[str, Any]:
    return {
        "model_id": model_id,
        "schema_version": "0.1.0",
        "carrier": ["left", "right"],
        "predicates": {
            "safe": ["left", "right"],
            "carrier_lr": ["left", "right"],
        },
        "relations": {
            "next": [list(edge) for edge in sorted(edges)],
            "merge_separated": [["left", "right"], ["right", "left"]],
        },
        "audits": [
            {
                "id": "carrier_lr_certificate",
                "kind": "carrier_certificate",
                "transition": "next",
                "safety": "safe",
                "carrier": "carrier_lr",
                "separation": "merge_separated",
                "left": "left",
                "right": "right",
                "expect": expectation,
            }
        ],
        "provenance": _provenance(claim_boundary),
    }


def _validated_case(case_id: str, model: dict[str, Any]) -> ControlledExperimentCase:
    loaded = load_model(model)
    audit_results = tuple(run_declared_audits(loaded))
    if not audit_results:
        raise AssertionError(f"{case_id} generated no audits")
    if not all(result.passed for result in audit_results):
        failures = [result.as_dict() for result in audit_results if not result.passed]
        raise AssertionError(f"{case_id} generated failing audits: {failures}")
    return ControlledExperimentCase(case_id=case_id, model=model, audit_results=audit_results)


def _target_recoverable_from_observation(
    states: tuple[str, ...],
    observation: dict[str, str],
    target: frozenset[str],
) -> bool:
    labels = set(observation.values())
    return all(
        len({state in target for state in states if observation[state] == label}) <= 1
        for label in labels
    )


def _decoder(red_value: str, blue_value: str) -> dict[str, object]:
    return {
        "domain": "observation",
        "codomain": "truth",
        "mapping": {
            "red": red_value,
            "blue": blue_value,
        },
    }


def _all_subsets(values: tuple[str, ...]) -> tuple[frozenset[str], ...]:
    subsets = []
    for size in range(len(values) + 1):
        for subset in combinations(values, size):
            subsets.append(frozenset(subset))
    return tuple(subsets)


def _edge_subsets(nodes: tuple[str, ...], *, loops: bool) -> tuple[tuple[Pair, ...], ...]:
    possible_edges = sorted(
        (source, target)
        for source in nodes
        for target in nodes
        if loops or source != target
    )
    edge_subsets = []
    for size in range(len(possible_edges) + 1):
        for subset in combinations(possible_edges, size):
            edge_subsets.append(tuple(subset))
    return tuple(edge_subsets)


def _histogram_signature(values: Any) -> str:
    counts = Counter(values)
    return ";".join(f"{key}:{counts[key]}" for key in sorted(counts))


def _is_alternating(trace: str) -> bool:
    return all(left != right for left, right in zip(trace, trace[1:], strict=False))


def _provenance(claim_boundary: str) -> dict[str, object]:
    return {
        "declared_before_run": True,
        "source": "omega.adapters.finite_relational.controlled_experiment",
        "claim_boundary": claim_boundary,
        "fixture_intent": "controlled finite adapter empirical pilot",
    }


def controlled_experiment_summary() -> dict[str, object]:
    families = generate_controlled_experiment()
    representative_case_count = sum(len(family.representative_cases) for family in families)
    return {
        "status": "PASS",
        "family_count": len(families),
        "representative_case_count": representative_case_count,
        "all_passed": all(family.all_passed for family in families),
        "families": [family.summary() for family in families],
        "experiment_digest": digest_json([family.summary() for family in families]),
    }
