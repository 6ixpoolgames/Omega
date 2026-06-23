"""Second-source parity checks for finite relational adapter compilers."""

from __future__ import annotations

from dataclasses import dataclass
import json
from hashlib import sha256
from typing import Any

from omega.adapters.finite_relational.audits import run_declared_audits
from omega.adapters.finite_relational.derived_graph import compile_derived_graph
from omega.adapters.finite_relational.finite_grid import compile_finite_grid
from omega.adapters.finite_relational.model import FiniteRelationalModel, load_model, model_digest


@dataclass(frozen=True)
class SourceParityCase:
    """Two source presentations compiled to comparable finite relational facts."""

    case_id: str
    description: str
    left_source_kind: str
    right_source_kind: str
    left_source: dict[str, Any]
    right_source: dict[str, Any]
    left_compiled_model: dict[str, Any]
    right_compiled_model: dict[str, Any]
    state_map: dict[str, str]
    comparison: dict[str, object]

    @property
    def all_passed(self) -> bool:
        return bool(self.comparison["all_passed"])

    def summary(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "description": self.description,
            "left_source_kind": self.left_source_kind,
            "right_source_kind": self.right_source_kind,
            "left_source_digest": digest_json(self.left_source),
            "right_source_digest": digest_json(self.right_source),
            "left_compiled_model_digest": model_digest(load_model(self.left_compiled_model)),
            "right_compiled_model_digest": model_digest(load_model(self.right_compiled_model)),
            "all_passed": self.all_passed,
            "comparison": self.comparison,
        }


def generate_source_parity_study() -> tuple[SourceParityCase, ...]:
    """Generate retained second-source parity checks over the same IR surface."""

    return (
        _strict_asymmetry_graph_grid_case(),
        _recurrent_carrier_graph_grid_case(),
        _observation_closure_graph_grid_case(),
    )


def source_parity_summary() -> dict[str, object]:
    cases = generate_source_parity_study()
    return {
        "status": "PASS",
        "case_count": len(cases),
        "all_passed": all(case.all_passed for case in cases),
        "cases": [case.summary() for case in cases],
    }


def digest_json(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _strict_asymmetry_graph_grid_case() -> SourceParityCase:
    graph_source = {
        "model_id": "parity_graph_strict_asymmetry",
        "nodes": ["source", "sink"],
        "edges": [["source", "sink"]],
        "observations": {
            "color": {
                "source": "red",
                "sink": "blue",
            }
        },
        "presentations": {
            "identity": {
                "source": "source",
                "sink": "sink",
            },
            "constant": {
                "source": "merged",
                "sink": "merged",
            },
        },
        "presentation_expectations": {
            "identity": "sound",
            "constant": "unsound",
        },
        "safety": "all",
        "provenance": {
            "declared_before_run": True,
            "source": "omega.adapters.finite_relational.source_parity",
            "claim_boundary": (
                "Second-source parity source: graph strict-asymmetry side. "
                "This is a compiler parity check, not empirical validation."
            ),
        },
    }
    grid_source = {
        "model_id": "parity_grid_strict_asymmetry",
        "width": 2,
        "height": 1,
        "movement_rule": "east",
        "observations": {
            "color": {
                "0,0": "red",
                "1,0": "blue",
            }
        },
        "presentations": {
            "identity": {
                "0,0": "0,0",
                "1,0": "1,0",
            },
            "constant": {
                "0,0": "merged",
                "1,0": "merged",
            },
        },
        "presentation_expectations": {
            "identity": "sound",
            "constant": "unsound",
        },
        "safety": "all",
        "provenance": {
            "declared_before_run": True,
            "source": "omega.adapters.finite_relational.source_parity",
            "claim_boundary": (
                "Second-source parity source: grid strict-asymmetry side. "
                "This is a compiler parity check, not empirical validation."
            ),
        },
    }
    return _build_graph_grid_case(
        case_id="graph_grid_strict_asymmetry_parity",
        description=(
            "A declared graph source and a finite grid source produce the same "
            "strict-edge asymmetry, separation, presentation-soundness findings, "
            "and transition facts after state renaming."
        ),
        graph_source=graph_source,
        grid_source=grid_source,
        state_map={"source": "0,0", "sink": "1,0"},
        predicate_names=("safe",),
        function_names=("identity", "constant"),
    )


def _recurrent_carrier_graph_grid_case() -> SourceParityCase:
    graph_source = {
        "model_id": "parity_graph_recurrent_carrier",
        "nodes": ["left", "right"],
        "edges": [["left", "right"], ["right", "left"]],
        "observations": {
            "color": {
                "left": "red",
                "right": "blue",
            }
        },
        "presentations": {
            "identity": {
                "left": "left",
                "right": "right",
            }
        },
        "presentation_expectations": {
            "identity": "sound",
        },
        "safety": "all",
        "provenance": {
            "declared_before_run": True,
            "source": "omega.adapters.finite_relational.source_parity",
            "claim_boundary": (
                "Second-source parity source: graph recurrent-carrier side. "
                "This is a compiler parity check, not empirical validation."
            ),
        },
    }
    grid_source = {
        "model_id": "parity_grid_recurrent_carrier",
        "width": 2,
        "height": 1,
        "movement_rule": "orthogonal",
        "observations": {
            "color": {
                "0,0": "red",
                "1,0": "blue",
            }
        },
        "presentations": {
            "identity": {
                "0,0": "0,0",
                "1,0": "1,0",
            }
        },
        "presentation_expectations": {
            "identity": "sound",
        },
        "safety": "all",
        "provenance": {
            "declared_before_run": True,
            "source": "omega.adapters.finite_relational.source_parity",
            "claim_boundary": (
                "Second-source parity source: grid recurrent-carrier side. "
                "This is a compiler parity check, not empirical validation."
            ),
        },
    }
    return _build_graph_grid_case(
        case_id="graph_grid_recurrent_carrier_parity",
        description=(
            "A declared graph source and a finite grid source produce the same "
            "mutual-reach carrier certificate, merge separation, and presentation "
            "facts after state renaming."
        ),
        graph_source=graph_source,
        grid_source=grid_source,
        state_map={"left": "0,0", "right": "1,0"},
        predicate_names=("safe", "carrier_0"),
        function_names=("identity",),
    )


def _observation_closure_graph_grid_case() -> SourceParityCase:
    graph_source = {
        "model_id": "parity_graph_observation_closure",
        "nodes": ["source", "sink"],
        "edges": [["source", "sink"]],
        "observations": {
            "color": {
                "source": "red",
                "sink": "blue",
            }
        },
        "presentations": {
            "identity": {
                "source": "source",
                "sink": "sink",
            },
            "constant": {
                "source": "merged",
                "sink": "merged",
            },
        },
        "presentation_expectations": {
            "identity": "sound",
            "constant": "unsound",
        },
        "safety": "all",
        "provenance": {
            "declared_before_run": True,
            "source": "omega.adapters.finite_relational.source_parity",
            "claim_boundary": (
                "Second-source parity source: graph observation-closure side. "
                "This is a compiler and closure parity check, not empirical validation."
            ),
        },
    }
    grid_source = {
        "model_id": "parity_grid_observation_closure",
        "width": 2,
        "height": 1,
        "movement_rule": "east",
        "observations": {
            "color": {
                "0,0": "red",
                "1,0": "blue",
            }
        },
        "presentations": {
            "identity": {
                "0,0": "0,0",
                "1,0": "1,0",
            },
            "constant": {
                "0,0": "merged",
                "1,0": "merged",
            },
        },
        "presentation_expectations": {
            "identity": "sound",
            "constant": "unsound",
        },
        "safety": "all",
        "provenance": {
            "declared_before_run": True,
            "source": "omega.adapters.finite_relational.source_parity",
            "claim_boundary": (
                "Second-source parity source: grid observation-closure side. "
                "This is a compiler and closure parity check, not empirical validation."
            ),
        },
    }
    state_map = {"source": "0,0", "sink": "1,0"}
    graph_compiled = _with_observation_closure_surface(
        compile_derived_graph(graph_source),
        target_members=_observed_members(graph_source, observation="color", label="blue"),
    )
    grid_compiled = _with_observation_closure_surface(
        compile_finite_grid(grid_source),
        target_members=_observed_members(grid_source, observation="color", label="blue"),
    )
    graph_model = load_model(graph_compiled)
    grid_model = load_model(grid_compiled)
    comparison = _compare_models(
        left=graph_model,
        right=grid_model,
        state_map=state_map,
        relation_names=(
            "next",
            "primitive_rel",
            "primitive_sep",
            "primitive_asym",
            "merge_separated",
        ),
        predicate_names=("safe", "blue_observed"),
        function_names=("identity", "constant"),
        closure_audit_ids=(
            "identity_observation_target_closure",
            "identity_constant_observation_target_closure",
        ),
    )
    if not comparison["all_passed"]:
        raise AssertionError(
            "source parity case failed: graph_grid_observation_closure_parity: "
            f"{comparison}"
        )
    return SourceParityCase(
        case_id="graph_grid_observation_closure_parity",
        description=(
            "A declared graph source and a finite grid source derive the same "
            "observation target and the same presentation/fact closure results "
            "after state renaming."
        ),
        left_source_kind="derived_graph",
        right_source_kind="finite_grid",
        left_source=graph_source,
        right_source=grid_source,
        left_compiled_model=graph_compiled,
        right_compiled_model=grid_compiled,
        state_map=state_map,
        comparison=comparison,
    )


def _build_graph_grid_case(
    *,
    case_id: str,
    description: str,
    graph_source: dict[str, Any],
    grid_source: dict[str, Any],
    state_map: dict[str, str],
    predicate_names: tuple[str, ...],
    function_names: tuple[str, ...],
) -> SourceParityCase:
    graph_compiled = compile_derived_graph(graph_source)
    grid_compiled = compile_finite_grid(grid_source)
    graph_model = load_model(graph_compiled)
    grid_model = load_model(grid_compiled)
    comparison = _compare_models(
        left=graph_model,
        right=grid_model,
        state_map=state_map,
        relation_names=(
            "next",
            "primitive_rel",
            "primitive_sep",
            "primitive_asym",
            "merge_separated",
        ),
        predicate_names=predicate_names,
        function_names=function_names,
    )
    if not comparison["all_passed"]:
        raise AssertionError(f"source parity case failed: {case_id}: {comparison}")
    return SourceParityCase(
        case_id=case_id,
        description=description,
        left_source_kind="derived_graph",
        right_source_kind="finite_grid",
        left_source=graph_source,
        right_source=grid_source,
        left_compiled_model=graph_compiled,
        right_compiled_model=grid_compiled,
        state_map=state_map,
        comparison=comparison,
    )


def _compare_models(
    *,
    left: FiniteRelationalModel,
    right: FiniteRelationalModel,
    state_map: dict[str, str],
    relation_names: tuple[str, ...],
    predicate_names: tuple[str, ...],
    function_names: tuple[str, ...],
    closure_audit_ids: tuple[str, ...] = (),
) -> dict[str, object]:
    left_states = tuple(_rename_items(left.domain("state"), state_map))
    right_states = right.domain("state")
    relation_matches = {
        name: _rename_relation(left.relation_tuples(name), state_map)
        == right.relation_tuples(name)
        for name in relation_names
    }
    predicate_matches = {
        name: _rename_items(left.predicate_members(name), state_map)
        == tuple(sorted(right.predicate_members(name)))
        for name in predicate_names
    }
    function_matches = {
        name: _rename_mapping(left.function_mapping(name), state_map)
        == right.function_mapping(name)
        for name in function_names
    }
    left_audit_findings = _audit_findings(left)
    right_audit_findings = _audit_findings(right)
    left_audit_results = tuple(run_declared_audits(left))
    right_audit_results = tuple(run_declared_audits(right))
    left_audits_passed = all(result.passed for result in left_audit_results)
    right_audits_passed = all(result.passed for result in right_audit_results)
    closure_observed_matches = _closure_observed_matches(
        left_results=left_audit_results,
        right_results=right_audit_results,
        state_map=state_map,
        audit_ids=closure_audit_ids,
    )
    all_passed = (
        left_states == right_states
        and all(relation_matches.values())
        and all(predicate_matches.values())
        and all(function_matches.values())
        and left_audit_findings == right_audit_findings
        and left_audits_passed
        and right_audits_passed
        and all(closure_observed_matches.values())
    )
    return {
        "all_passed": all_passed,
        "state_map": state_map,
        "left_states_after_rename": list(left_states),
        "right_states": list(right_states),
        "state_domain_match": left_states == right_states,
        "relation_matches": relation_matches,
        "predicate_matches": predicate_matches,
        "function_matches": function_matches,
        "left_audit_findings": left_audit_findings,
        "right_audit_findings": right_audit_findings,
        "audit_findings_match": left_audit_findings == right_audit_findings,
        "left_audits_passed": left_audits_passed,
        "right_audits_passed": right_audits_passed,
        "closure_observed_matches": closure_observed_matches,
    }


def _with_observation_closure_surface(
    compiled: dict[str, Any],
    *,
    target_members: tuple[str, ...],
) -> dict[str, Any]:
    enriched = dict(compiled)
    enriched["predicates"] = dict(compiled.get("predicates", {})) | {
        "blue_observed": list(target_members),
    }
    enriched["audits"] = list(compiled.get("audits", [])) + [
        {
            "id": "identity_observation_target_closure",
            "kind": "presentation_fact_closure",
            "presentations": ["identity"],
            "target_predicates": ["blue_observed", "safe"],
            "expected_common_target_predicates": ["blue_observed", "safe"],
            "expect": "closure_ok",
        },
        {
            "id": "identity_constant_observation_target_closure",
            "kind": "presentation_fact_closure",
            "presentations": ["identity", "constant"],
            "target_predicates": ["blue_observed", "safe"],
            "expected_common_target_predicates": ["safe"],
            "expected_absent_target_predicates": ["blue_observed"],
            "expect": "closure_ok",
        },
    ]
    provenance = dict(compiled.get("provenance", {}))
    derivation_rules = list(provenance.get("derivation_rules", []))
    derivation_rules.extend(
        [
            "blue_observed=observation_label(color,blue)",
            "closure_audits=presentation_fact_closure(identity,constant)",
        ]
    )
    enriched["provenance"] = provenance | {"derivation_rules": derivation_rules}
    load_model(enriched)
    return enriched


def _observed_members(
    source: dict[str, Any],
    *,
    observation: str,
    label: str,
) -> tuple[str, ...]:
    mapping = source["observations"][observation]
    return tuple(sorted(state for state, value in mapping.items() if value == label))


def _closure_observed_matches(
    *,
    left_results: tuple[Any, ...],
    right_results: tuple[Any, ...],
    state_map: dict[str, str],
    audit_ids: tuple[str, ...],
) -> dict[str, bool]:
    left_by_id = {result.audit_id: result for result in left_results}
    right_by_id = {result.audit_id: result for result in right_results}
    return {
        audit_id: _rename_closure_observed(left_by_id[audit_id].observed, state_map)
        == _rename_closure_observed(right_by_id[audit_id].observed, {})
        for audit_id in audit_ids
    }


def _rename_closure_observed(
    observed: dict[str, Any],
    state_map: dict[str, str],
) -> dict[str, Any]:
    renamed = dict(observed)
    for key in (
        "common_visible_pairs",
        "missing_expected_common_visible_pairs",
        "present_expected_absent_visible_pairs",
    ):
        if key in renamed:
            renamed[key] = sorted(
                [
                    [state_map.get(left, left), state_map.get(right, right)]
                    for left, right in renamed[key]
                ]
            )
    return renamed


def _rename_relation(
    tuples: frozenset[tuple[str, ...]],
    state_map: dict[str, str],
) -> frozenset[tuple[str, ...]]:
    return frozenset(tuple(state_map.get(item, item) for item in row) for row in tuples)


def _rename_items(
    items: tuple[str, ...] | frozenset[str],
    state_map: dict[str, str],
) -> tuple[str, ...]:
    return tuple(sorted(state_map.get(item, item) for item in items))


def _rename_mapping(
    mapping: dict[str, str],
    state_map: dict[str, str],
) -> dict[str, str]:
    return {
        state_map.get(source, source): state_map.get(target, target)
        for source, target in mapping.items()
    }


def _audit_findings(model: FiniteRelationalModel) -> dict[str, str]:
    return {
        result.audit_id: result.finding
        for result in run_declared_audits(model)
    }
