"""Graph-pair source characterization for carrier-transfer audits."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
from typing import Any

from omega.adapters.finite_relational.audits import AuditResult, run_declared_audits
from omega.adapters.finite_relational.derived_graph import compile_derived_graph
from omega.adapters.finite_relational.facts import Pair, reachable_pairs
from omega.adapters.finite_relational.model import SchemaError, load_model, model_digest
from omega.adapters.finite_relational.source_contract import assert_no_reserved_ir_fields


@dataclass(frozen=True)
class GraphPairTransferCase:
    """A graph-pair source, compiled IR model, and carrier-transfer audit result."""

    case_id: str
    source: dict[str, Any]
    compiled_model: dict[str, Any]
    audit_results: tuple[AuditResult, ...]

    @property
    def all_passed(self) -> bool:
        return all(result.passed for result in self.audit_results)

    def summary(self) -> dict[str, object]:
        model = load_model(self.compiled_model)
        return {
            "case_id": self.case_id,
            "source_digest": digest_json(self.source),
            "compiled_model_id": model.model_id,
            "compiled_model_digest": model_digest(model),
            "audit_count": len(self.audit_results),
            "passed_count": sum(1 for result in self.audit_results if result.passed),
            "all_passed": self.all_passed,
            "findings": [result.finding for result in self.audit_results],
        }


@dataclass(frozen=True)
class GraphPairTransferStudy:
    """A finite target-graph sweep for graph-pair carrier transfer."""

    study_id: str
    description: str
    search_space: dict[str, object]
    metrics: dict[str, object]
    representative_cases: tuple[GraphPairTransferCase, ...]

    @property
    def all_passed(self) -> bool:
        return all(case.all_passed for case in self.representative_cases)

    def summary(self) -> dict[str, object]:
        return {
            "study_id": self.study_id,
            "description": self.description,
            "search_space": self.search_space,
            "metrics": self.metrics,
            "representative_case_count": len(self.representative_cases),
            "all_passed": self.all_passed,
            "representative_cases": [case.summary() for case in self.representative_cases],
        }


def generate_graph_pair_transfer_characterization() -> tuple[GraphPairTransferStudy, ...]:
    """Generate small graph-pair transfer sweeps over target dynamics."""

    return (
        _generated_graph_pair_transfer_study(
            study_id="graph_pair_two_node_transfer_sweep",
            target_nodes=("t_left", "t_right"),
            target_left="t_left",
            target_right="t_right",
        ),
        _generated_graph_pair_transfer_study(
            study_id="graph_pair_three_node_extension_transfer_sweep",
            target_nodes=("t_left", "t_mid", "t_right"),
            target_left="t_left",
            target_right="t_right",
        ),
    )


def compile_graph_pair_transfer_source(raw: dict[str, Any]) -> dict[str, Any]:
    """Compile a graph-pair transfer source into finite relational IR."""

    assert_no_reserved_ir_fields(raw, source_kind="graph pair transfer")
    source_graph = _dict(raw.get("source_graph"), "source_graph")
    target_graph = _dict(raw.get("target_graph"), "target_graph")
    source_compiled = compile_derived_graph(source_graph)
    target_compiled = compile_derived_graph(target_graph)
    source_model = load_model(source_compiled)
    target_model = load_model(target_compiled)
    source_states = list(source_model.domain("state"))
    target_states = list(target_model.domain("state"))
    if set(source_states) & set(target_states):
        raise SchemaError("source and target graph states must be disjoint")

    source_left = str(raw.get("source_left", "s_left"))
    source_right = str(raw.get("source_right", "s_right"))
    target_left = str(raw.get("target_left", "t_left"))
    target_right = str(raw.get("target_right", "t_right"))
    _require_member(source_left, source_states, "source_left")
    _require_member(source_right, source_states, "source_right")
    _require_member(target_left, target_states, "target_left")
    _require_member(target_right, target_states, "target_right")

    correspondence = _graph_pair_correspondence(
        raw.get("correspondence", ()),
        source_states=source_states,
        target_states=target_states,
    )
    model_id = str(raw.get("model_id", "compiled_graph_pair_transfer"))
    provenance = _dict(raw.get("provenance", {}), "provenance") | {
        "compiled_from": "derived_graph_pair",
        "source_graph_compiled_digest": model_digest(source_model),
        "target_graph_compiled_digest": model_digest(target_model),
        "source_graph_model_id": source_model.model_id,
        "target_graph_model_id": target_model.model_id,
        "source_digest": digest_json(raw),
        "derivation_rules": [
            "source_next=source_graph.next",
            "target_next=target_graph.next",
            "source_separated=source_graph.merge_separated",
            "target_separated=target_graph.merge_separated",
            "source_carrier=all_source_graph_nodes",
            "target_carrier=all_target_graph_nodes",
            "correspondence=declared_graph_pair_correspondence",
            "audit=carrier_transfer",
        ],
    }
    return {
        "model_id": model_id,
        "schema_version": "0.1.0",
        "carrier": source_states + target_states,
        "predicates": {
            "source_safe": sorted(source_model.predicate_members("safe")),
            "source_carrier": source_states,
            "target_safe": sorted(target_model.predicate_members("safe")),
            "target_carrier": target_states,
        },
        "relations": {
            "source_next": _relation_rows(source_model.relation_tuples("next")),
            "target_next": _relation_rows(target_model.relation_tuples("next")),
            "source_separated": _relation_rows(
                source_model.relation_tuples("merge_separated")
            ),
            "target_separated": _relation_rows(
                target_model.relation_tuples("merge_separated")
            ),
            "corresponds": _relation_rows(correspondence),
        },
        "audits": [
            {
                "id": f"{model_id}_carrier_transfer_contract",
                "kind": "carrier_transfer",
                "source_transition": "source_next",
                "source_safety": "source_safe",
                "source_carrier": "source_carrier",
                "source_left": source_left,
                "source_right": source_right,
                "source_separation": "source_separated",
                "target_transition": "target_next",
                "target_safety": "target_safe",
                "target_carrier": "target_carrier",
                "target_left": target_left,
                "target_right": target_right,
                "target_separation": "target_separated",
                "correspondence": "corresponds",
                "expect": str(raw.get("expect", "transferred")),
            }
        ],
        "provenance": provenance,
    }


def digest_json(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _generated_graph_pair_transfer_study(
    *,
    study_id: str,
    target_nodes: tuple[str, ...],
    target_left: str,
    target_right: str,
) -> GraphPairTransferStudy:
    possible_edges = tuple(
        (source, target)
        for source in target_nodes
        for target in target_nodes
        if source != target
    )
    edge_subsets = tuple(
        subset
        for size in range(len(possible_edges) + 1)
        for subset in combinations(possible_edges, size)
    )
    transferred_sets = []
    not_transferred_sets = []
    target_state_set = set(target_nodes)
    for target_edges in edge_subsets:
        reach = reachable_pairs(target_state_set, set(target_edges))
        strongly_connected = all(
            (source, target) in reach
            for source in target_nodes
            for target in target_nodes
        )
        if strongly_connected:
            transferred_sets.append(target_edges)
        else:
            not_transferred_sets.append(target_edges)
    if not transferred_sets:
        raise AssertionError(f"{study_id} generated no transfer-positive target graphs")
    if not not_transferred_sets:
        raise AssertionError(f"{study_id} generated no transfer-negative target graphs")
    forward_but_not_transferred_sets = [
        target_edges
        for target_edges in not_transferred_sets
        if (target_left, target_right)
        in reachable_pairs(target_state_set, set(target_edges))
    ]
    negative_control = (
        forward_but_not_transferred_sets[0]
        if forward_but_not_transferred_sets
        else not_transferred_sets[0]
    )

    positive_source = _graph_pair_transfer_source(
        source_id=f"{study_id}_positive",
        target_nodes=target_nodes,
        target_edges=transferred_sets[0],
        target_left=target_left,
        target_right=target_right,
        expect="transferred",
        claim_boundary=(
            "Generated graph-pair transfer characterization positive: target "
            "carrier remains recurrent under the declared correspondence."
        ),
    )
    negative_source = _graph_pair_transfer_source(
        source_id=f"{study_id}_negative",
        target_nodes=target_nodes,
        target_edges=negative_control,
        target_left=target_left,
        target_right=target_right,
        expect="not_transferred",
        claim_boundary=(
            "Generated graph-pair transfer characterization negative: endpoint "
            "correspondence is present, but target recurrence is not certified."
        ),
    )

    return GraphPairTransferStudy(
        study_id=study_id,
        description=(
            "Enumerates target graph edge subsets while keeping the source graph "
            "and endpoint correspondence fixed, then audits carrier transfer over "
            "the compiled graph-pair source."
        ),
        search_space={
            "source_nodes": ["s_left", "s_right"],
            "target_nodes": list(target_nodes),
            "target_edge_candidate_count": len(possible_edges),
            "target_edge_subset_count": len(edge_subsets),
            "target_left": target_left,
            "target_right": target_right,
        },
        metrics={
            "transferred_target_graph_count": len(transferred_sets),
            "not_transferred_target_graph_count": len(not_transferred_sets),
            "transferred_fraction": f"{len(transferred_sets)}/{len(edge_subsets)}",
            "forward_but_not_transferred_target_graph_count": len(
                forward_but_not_transferred_sets
            ),
            "representative_transferred_edges": [list(edge) for edge in transferred_sets[0]],
            "representative_not_transferred_edges": [
                list(edge) for edge in negative_control
            ],
        },
        representative_cases=(
            _validated_case(f"{study_id}_transferred", positive_source),
            _validated_case(f"{study_id}_not_transferred", negative_source),
        ),
    )


def _graph_pair_transfer_source(
    *,
    source_id: str,
    target_nodes: tuple[str, ...],
    target_edges: tuple[Pair, ...],
    target_left: str,
    target_right: str,
    expect: str,
    claim_boundary: str,
) -> dict[str, Any]:
    target_observations = {
        node: (
            "left"
            if node == target_left
            else "right"
            if node == target_right
            else "intermediate"
        )
        for node in target_nodes
    }
    return {
        "model_id": source_id,
        "source_left": "s_left",
        "source_right": "s_right",
        "target_left": target_left,
        "target_right": target_right,
        "expect": expect,
        "source_graph": {
            "model_id": f"{source_id}_source",
            "nodes": ["s_left", "s_right"],
            "edges": [["s_left", "s_right"], ["s_right", "s_left"]],
            "observations": {
                "role": {
                    "s_left": "left",
                    "s_right": "right",
                }
            },
            "safety": "all",
            "provenance": _provenance(
                "Generated graph-pair transfer source side."
            ),
        },
        "target_graph": {
            "model_id": f"{source_id}_target",
            "nodes": list(target_nodes),
            "edges": [list(edge) for edge in target_edges],
            "observations": {"role": target_observations},
            "safety": "all",
            "provenance": _provenance(
                "Generated graph-pair transfer target side."
            ),
        },
        "correspondence": [["s_left", target_left], ["s_right", target_right]],
        "provenance": _provenance(claim_boundary),
    }


def _validated_case(case_id: str, source: dict[str, Any]) -> GraphPairTransferCase:
    compiled = compile_graph_pair_transfer_source(source)
    model = load_model(compiled)
    audit_results = tuple(run_declared_audits(model))
    if not audit_results:
        raise AssertionError(f"{case_id} generated no audits")
    if not all(result.passed for result in audit_results):
        failures = [result.as_dict() for result in audit_results if not result.passed]
        raise AssertionError(f"{case_id} generated failing audits: {failures}")
    return GraphPairTransferCase(
        case_id=case_id,
        source=source,
        compiled_model=compiled,
        audit_results=audit_results,
    )


def _graph_pair_correspondence(
    pairs: object,
    *,
    source_states: list[str],
    target_states: list[str],
) -> tuple[Pair, ...]:
    source_set = set(source_states)
    target_set = set(target_states)
    rows = []
    if not isinstance(pairs, list):
        raise SchemaError("graph pair correspondence must be a list")
    for raw_pair in pairs:
        if not isinstance(raw_pair, list) or len(raw_pair) != 2:
            raise SchemaError("graph pair correspondence rows must be length-2 lists")
        source, target = str(raw_pair[0]), str(raw_pair[1])
        if source not in source_set:
            raise SchemaError(f"unknown source correspondence state: {source}")
        if target not in target_set:
            raise SchemaError(f"unknown target correspondence state: {target}")
        rows.append((source, target))
    return tuple(sorted(rows))


def _relation_rows(edges: set[Pair] | tuple[Pair, ...]) -> list[list[str]]:
    return [[source, target] for source, target in sorted(edges)]


def _require_member(value: str, values: list[str], label: str) -> None:
    if value not in values:
        raise SchemaError(f"{label} is not in declared graph states: {value}")


def _dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SchemaError(f"{label} must be an object")
    return value


def _provenance(claim_boundary: str) -> dict[str, object]:
    return {
        "declared_before_run": True,
        "source": "omega.adapters.finite_relational.graph_pair_transfer",
        "claim_boundary": claim_boundary,
        "fixture_intent": "controlled graph-pair transfer characterization",
    }
