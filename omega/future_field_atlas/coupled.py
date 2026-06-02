from __future__ import annotations

import math
from dataclasses import dataclass

from omega.rfs_mb0_future_landscape.substrate import State

from .contracts import GeneratedCondition
from .util import canonical_json, stable_hash, state_id


JointState = tuple[State, State]


@dataclass(frozen=True)
class CoupledOperatorSpec:
    coupled_operator_id: str
    coupled_operator_family: str
    product_baseline_definition: str
    joint_candidate_set_definition: str
    joint_energy_function_id: str
    joint_energy_params_json: str
    coupling_term_id: str
    coupling_strength: float
    joint_selection_family: str
    joint_effective_out_degree: int
    stochastic_flag: int
    seed_policy: str


@dataclass(frozen=True)
class CoupledProbeTask:
    pair_id: str
    field_a: GeneratedCondition
    field_b: GeneratedCondition
    start_index: int
    start_a: State
    start_b: State
    horizon_schedule: tuple[int, ...]
    horizon_max: int
    joint_selection_family: str
    joint_effective_out_degree: int
    coupling_strength: float
    coupled_operator: CoupledOperatorSpec
    max_joint_frontier_nodes_per_horizon: int
    max_joint_edges_per_step: int
    max_internal_joint_frontier_states: int


@dataclass
class CoupledProbeResult:
    pair_id: str
    node_rows: list[dict[str, object]]
    edge_rows: list[dict[str, object]]
    profile_rows: list[dict[str, object]]
    marginal_rows: list[dict[str, object]]
    residual_rows: list[dict[str, object]]
    marginal_projection_rows: list[dict[str, object]]
    internal_cap_rows: list[dict[str, object]]


@dataclass(frozen=True)
class JointEdge:
    source: JointState
    target: JointState
    a_energy: float
    b_energy: float
    a_candidate_rank: int
    b_candidate_rank: int
    a_rank_offset_from_boundary: int
    b_rank_offset_from_boundary: int
    coupling_penalty: float
    joint_transition_energy: float


def scan_coupled_probe(task: CoupledProbeTask) -> CoupledProbeResult:
    schedule = tuple(sorted(set(h for h in task.horizon_schedule if 0 <= h <= task.horizon_max)))
    schedule_set = set(schedule)
    product_frontiers: dict[int, frozenset[JointState]] = {}
    coupled_frontiers: dict[int, frozenset[JointState]] = {}
    product_edges_by_step: dict[int, tuple[JointEdge, ...]] = {}
    coupled_edges_by_step: dict[int, tuple[JointEdge, ...]] = {}
    node_rows: list[dict[str, object]] = []
    edge_rows: list[dict[str, object]] = []
    profile_rows: list[dict[str, object]] = []
    marginal_rows: list[dict[str, object]] = []
    residual_rows: list[dict[str, object]] = []
    marginal_projection_rows: list[dict[str, object]] = []
    internal_cap_rows: list[dict[str, object]] = []
    product_current = frozenset({(task.start_a, task.start_b)})
    coupled_current = frozenset({(task.start_a, task.start_b)})
    product_cap_poisoned = 0
    coupled_cap_poisoned = 0
    for horizon in range(task.horizon_max + 1):
        product_frontiers[horizon] = product_current
        coupled_frontiers[horizon] = coupled_current
        if horizon in schedule_set:
            comparison_status = comparison_feature_status(
                task,
                product_current,
                coupled_current,
                product_cap_poisoned,
                coupled_cap_poisoned,
            )
            node_rows.extend(node_rows_for_frontier(task, "product_baseline", horizon, product_current, product_cap_poisoned))
            node_rows.extend(node_rows_for_frontier(task, "coupled", horizon, coupled_current, coupled_cap_poisoned))
            profile_rows.append(profile_row(task, "product_baseline", horizon, product_current, product_edges_by_step.get(horizon, tuple()), product_cap_poisoned))
            profile_rows.append(profile_row(task, "coupled", horizon, coupled_current, coupled_edges_by_step.get(horizon, tuple()), coupled_cap_poisoned))
            marginal_rows.append(marginal_retention_row(task, horizon, product_current, coupled_current, comparison_status))
            residual_rows.append(joint_vs_product_residual_row(task, horizon, product_current, coupled_current, comparison_status))
            marginal_projection_rows.extend(make_marginal_projection_rows(task, horizon, product_current, coupled_current, comparison_status))
        if horizon >= task.horizon_max:
            break
        product_edges = expand_joint_edges(task, product_current, "product_baseline")
        coupled_edges = expand_joint_edges(task, coupled_current, "coupled")
        product_edges_by_step[horizon] = tuple(product_edges)
        coupled_edges_by_step[horizon] = tuple(coupled_edges)
        edge_rows.extend(edge_rows_for_step(task, "product_baseline", horizon, product_edges, product_cap_poisoned))
        edge_rows.extend(edge_rows_for_step(task, "coupled", horizon, coupled_edges, coupled_cap_poisoned))
        product_next, product_capped = cap_frontier(
            {edge.target for edge in product_edges},
            task.max_internal_joint_frontier_states,
        )
        coupled_next, coupled_capped = cap_frontier(
            {edge.target for edge in coupled_edges},
            task.max_internal_joint_frontier_states,
        )
        if product_capped:
            internal_cap_rows.append(internal_cap_row(task, "product_baseline", horizon + 1, len({edge.target for edge in product_edges}), len(product_next)))
        if coupled_capped:
            internal_cap_rows.append(internal_cap_row(task, "coupled", horizon + 1, len({edge.target for edge in coupled_edges}), len(coupled_next)))
        product_cap_poisoned = int(product_cap_poisoned or product_capped)
        coupled_cap_poisoned = int(coupled_cap_poisoned or coupled_capped)
        product_current = frozenset(product_next)
        coupled_current = frozenset(coupled_next)
    return CoupledProbeResult(
        pair_id=task.pair_id,
        node_rows=node_rows,
        edge_rows=edge_rows,
        profile_rows=profile_rows,
        marginal_rows=marginal_rows,
        residual_rows=residual_rows,
        marginal_projection_rows=marginal_projection_rows,
        internal_cap_rows=internal_cap_rows,
    )


def expand_joint_edges(task: CoupledProbeTask, frontier: frozenset[JointState], mode: str) -> list[JointEdge]:
    edges: list[JointEdge] = []
    for source in sorted(frontier, key=joint_state_id):
        a_source, b_source = source
        candidates: list[JointEdge] = []
        for a_target in task.field_a.system.edges.get(a_source, ()):
            a_anatomy = task.field_a.candidate_anatomy[(a_source, a_target)]
            for b_target in task.field_b.system.edges.get(b_source, ()):
                b_anatomy = task.field_b.candidate_anatomy[(b_source, b_target)]
                penalty = coupling_penalty(task, a_anatomy.rank_offset_from_boundary, b_anatomy.rank_offset_from_boundary)
                candidates.append(
                    JointEdge(
                        source=source,
                        target=(a_target, b_target),
                        a_energy=float(a_anatomy.candidate_energy),
                        b_energy=float(b_anatomy.candidate_energy),
                        a_candidate_rank=int(a_anatomy.candidate_rank),
                        b_candidate_rank=int(b_anatomy.candidate_rank),
                        a_rank_offset_from_boundary=int(a_anatomy.rank_offset_from_boundary),
                        b_rank_offset_from_boundary=int(b_anatomy.rank_offset_from_boundary),
                        coupling_penalty=float(penalty),
                        joint_transition_energy=float(a_anatomy.candidate_energy + b_anatomy.candidate_energy + penalty),
                    )
                )
        candidates.sort(
            key=lambda edge: (
                edge.joint_transition_energy,
                edge.a_candidate_rank,
                edge.b_candidate_rank,
                joint_state_id(edge.target),
            )
        )
        if mode == "product_baseline" or task.joint_selection_family == "product":
            edges.extend(candidates)
        elif task.joint_selection_family == "joint_energy_rank_prefix":
            edges.extend(candidates[: max(1, task.joint_effective_out_degree)])
        elif task.joint_selection_family == "shared_capacity":
            edges.extend(select_shared_capacity_edges(candidates, max(1, task.joint_effective_out_degree)))
        else:
            raise ValueError(f"unsupported joint selection family: {task.joint_selection_family}")
    return edges


def coupling_penalty(task: CoupledProbeTask, a_offset: int, b_offset: int) -> float:
    if task.joint_selection_family == "shared_capacity":
        return 0.0
    return float(task.coupling_strength) * abs(int(a_offset) - int(b_offset))


def select_shared_capacity_edges(candidates: list[JointEdge], joint_capacity: int) -> list[JointEdge]:
    if len(candidates) <= joint_capacity:
        return list(candidates)
    a_targets = {edge.target[0] for edge in candidates}
    b_targets = {edge.target[1] for edge in candidates}
    a_capacity = max(1, math.ceil(joint_capacity / max(1, len(a_targets))))
    b_capacity = max(1, math.ceil(joint_capacity / max(1, len(b_targets))))
    selected: list[JointEdge] = []
    a_load: dict[State, int] = {}
    b_load: dict[State, int] = {}
    for edge in candidates:
        a_target, b_target = edge.target
        if a_load.get(a_target, 0) >= a_capacity:
            continue
        if b_load.get(b_target, 0) >= b_capacity:
            continue
        selected.append(edge)
        a_load[a_target] = a_load.get(a_target, 0) + 1
        b_load[b_target] = b_load.get(b_target, 0) + 1
        if len(selected) >= joint_capacity:
            return selected
    selected_ids = {edge_identity(edge) for edge in selected}
    for edge in candidates:
        if edge_identity(edge) in selected_ids:
            continue
        selected.append(edge)
        if len(selected) >= joint_capacity:
            break
    return selected


def edge_identity(edge: JointEdge) -> tuple[str, str]:
    return joint_state_id(edge.source), joint_state_id(edge.target)


def node_rows_for_frontier(
    task: CoupledProbeTask,
    mode: str,
    horizon: int,
    frontier: frozenset[JointState],
    internal_capped: int,
) -> list[dict[str, object]]:
    row_limit = max(0, task.max_joint_frontier_nodes_per_horizon)
    row_truncated = row_limit > 0 and len(frontier) > row_limit
    artifact_status = artifact_status_for(row_truncated, internal_capped)
    rows: list[dict[str, object]] = []
    for rank, joint_state in enumerate(sorted(frontier, key=joint_state_id)[:row_limit], start=1):
        a_state, b_state = joint_state
        rows.append({
            **base_fields(task),
            "joint_scan_mode": mode,
            "horizon": horizon,
            "joint_state_id": joint_state_id(joint_state),
            "joint_state_payload_hash": stable_hash(joint_state),
            "A_state_id": state_id(a_state),
            "B_state_id": state_id(b_state),
            "frontier_membership_weight": 1.0,
            "joint_frontier_rank": rank,
            "joint_frontier_state_count_full": len(frontier),
            "joint_frontier_nodes_truncated": int(row_truncated),
            "internal_frontier_capped": int(internal_capped),
            "cap_poisoned_flag": int(internal_capped),
            "node_artifact_status": artifact_status,
        })
    return rows


def edge_rows_for_step(
    task: CoupledProbeTask,
    mode: str,
    horizon: int,
    edges: list[JointEdge],
    cap_poisoned: int,
) -> list[dict[str, object]]:
    row_limit = max(0, task.max_joint_edges_per_step)
    row_truncated = row_limit > 0 and len(edges) > row_limit
    artifact_status = artifact_status_for(row_truncated, cap_poisoned)
    rows: list[dict[str, object]] = []
    for rank, edge in enumerate(edges[:row_limit], start=1):
        a_source, b_source = edge.source
        a_target, b_target = edge.target
        rows.append({
            **base_fields(task),
            "joint_scan_mode": mode,
            "source_horizon": horizon,
            "target_horizon": horizon + 1,
            "source_joint_state_id": joint_state_id(edge.source),
            "target_joint_state_id": joint_state_id(edge.target),
            "A_source_state_id": state_id(a_source),
            "A_target_state_id": state_id(a_target),
            "B_source_state_id": state_id(b_source),
            "B_target_state_id": state_id(b_target),
            "joint_edge_rank_within_step_sample": rank,
            "joint_frontier_edge_count_full": len(edges),
            "joint_frontier_edges_truncated": int(row_truncated),
            "cap_poisoned_flag": int(cap_poisoned),
            "edge_artifact_status": artifact_status,
            "edge_weight": 1.0,
            "A_candidate_rank": edge.a_candidate_rank,
            "B_candidate_rank": edge.b_candidate_rank,
            "A_candidate_energy": edge.a_energy,
            "B_candidate_energy": edge.b_energy,
            "A_rank_offset_from_boundary": edge.a_rank_offset_from_boundary,
            "B_rank_offset_from_boundary": edge.b_rank_offset_from_boundary,
            "coupling_penalty": edge.coupling_penalty,
            "joint_transition_energy": edge.joint_transition_energy,
            "joint_selection_family": task.joint_selection_family,
            "joint_effective_out_degree": task.joint_effective_out_degree,
            "coupled_operator_id": task.coupled_operator.coupled_operator_id,
            "coupling_strength": task.coupling_strength,
        })
    return rows


def profile_row(
    task: CoupledProbeTask,
    mode: str,
    horizon: int,
    frontier: frozenset[JointState],
    step_edges: tuple[JointEdge, ...],
    internal_capped: int,
) -> dict[str, object]:
    a_marginal, b_marginal = marginals(frontier)
    node_truncated = len(frontier) > task.max_joint_frontier_nodes_per_horizon
    edge_truncated = len(step_edges) > task.max_joint_edges_per_step
    status = artifact_status_for(node_truncated or edge_truncated, internal_capped)
    return {
        **base_fields(task),
        "joint_scan_mode": mode,
        "horizon": horizon,
        "feature_status": status,
        "node_artifact_status": artifact_status_for(node_truncated, internal_capped),
        "edge_artifact_status": artifact_status_for(edge_truncated, 0),
        "joint_frontier_state_count": len(frontier),
        "joint_frontier_edge_count": len(step_edges),
        "A_marginal_state_count": len(a_marginal),
        "B_marginal_state_count": len(b_marginal),
        "marginal_product_state_count": len(a_marginal) * len(b_marginal),
        "joint_density_vs_marginal_product": len(frontier) / max(1, len(a_marginal) * len(b_marginal)),
        "internal_frontier_capped": int(internal_capped),
        "cap_poisoned_flag": int(internal_capped),
    }


def marginal_retention_row(
    task: CoupledProbeTask,
    horizon: int,
    product_frontier: frozenset[JointState],
    coupled_frontier: frozenset[JointState],
    feature_status: str,
) -> dict[str, object]:
    product_a, product_b = marginals(product_frontier)
    coupled_a, coupled_b = marginals(coupled_frontier)
    return {
        **base_fields(task),
        "horizon": horizon,
        "feature_status": feature_status,
        "coupled_operator_id": task.coupled_operator.coupled_operator_id,
        "A_product_marginal_count": len(product_a),
        "A_coupled_marginal_count": len(coupled_a),
        "A_marginal_intersection_count": len(product_a & coupled_a),
        "A_marginal_retention_fraction": len(product_a & coupled_a) / max(1, len(product_a)),
        "B_product_marginal_count": len(product_b),
        "B_coupled_marginal_count": len(coupled_b),
        "B_marginal_intersection_count": len(product_b & coupled_b),
        "B_marginal_retention_fraction": len(product_b & coupled_b) / max(1, len(product_b)),
        "joint_product_state_count": len(product_frontier),
        "joint_coupled_state_count": len(coupled_frontier),
        "joint_intersection_count": len(product_frontier & coupled_frontier),
        "joint_retention_fraction": len(product_frontier & coupled_frontier) / max(1, len(product_frontier)),
    }


def joint_vs_product_residual_row(
    task: CoupledProbeTask,
    horizon: int,
    product_frontier: frozenset[JointState],
    coupled_frontier: frozenset[JointState],
    feature_status: str,
) -> dict[str, object]:
    intersection = product_frontier & coupled_frontier
    union = product_frontier | coupled_frontier
    return {
        **base_fields(task),
        "horizon": horizon,
        "feature_status": feature_status,
        "coupled_operator_id": task.coupled_operator.coupled_operator_id,
        "product_joint_support_count": len(product_frontier),
        "coupled_joint_support_count": len(coupled_frontier),
        "joint_support_intersection_count": len(intersection),
        "joint_support_union_count": len(union),
        "joint_support_symmetric_difference_count": len(union - intersection),
        "joint_support_residual_fraction": len(union - intersection) / max(1, len(union)),
        "coupled_missing_from_product_count": len(coupled_frontier - product_frontier),
        "product_missing_from_coupled_count": len(product_frontier - coupled_frontier),
    }


def make_marginal_projection_rows(
    task: CoupledProbeTask,
    horizon: int,
    product_frontier: frozenset[JointState],
    coupled_frontier: frozenset[JointState],
    feature_status: str,
) -> list[dict[str, object]]:
    product_a, product_b = marginals(product_frontier)
    coupled_a, coupled_b = marginals(coupled_frontier)
    return [
        marginal_projection_row(task, horizon, "A", "B", product_a, coupled_a, feature_status),
        marginal_projection_row(task, horizon, "B", "A", product_b, coupled_b, feature_status),
    ]


def marginal_projection_row(
    task: CoupledProbeTask,
    horizon: int,
    projected_field: str,
    paired_field: str,
    product_marginal: set[State],
    coupled_marginal: set[State],
    feature_status: str,
) -> dict[str, object]:
    intersection = product_marginal & coupled_marginal
    union = product_marginal | coupled_marginal
    return {
        **base_fields(task),
        "horizon": horizon,
        "feature_status": feature_status,
        "projection_semantics": "product_vs_coupled_marginal_set_delta",
        "causal_interpretation": "none",
        "coupled_operator_id": task.coupled_operator.coupled_operator_id,
        "projected_field": projected_field,
        "paired_field": paired_field,
        "product_marginal_count": len(product_marginal),
        "coupled_marginal_count": len(coupled_marginal),
        "marginal_intersection_count": len(intersection),
        "marginal_union_count": len(union),
        "marginal_retention_fraction": len(intersection) / max(1, len(product_marginal)),
        "marginal_symmetric_difference_fraction": len(union - intersection) / max(1, len(union)),
        "product_missing_from_coupled_count": len(product_marginal - coupled_marginal),
        "coupled_missing_from_product_count": len(coupled_marginal - product_marginal),
    }


def internal_cap_row(
    task: CoupledProbeTask,
    mode: str,
    horizon: int,
    uncapped_count: int,
    retained_count: int,
) -> dict[str, object]:
    return {
        **base_fields(task),
        "joint_scan_mode": mode,
        "horizon": horizon,
        "uncapped_frontier_count": uncapped_count,
        "retained_frontier_count": retained_count,
        "cap_policy": f"deterministic_sorted_prefix_{task.max_internal_joint_frontier_states}",
        "artifact_status": "truncated_noninterpretable",
    }


def base_fields(task: CoupledProbeTask) -> dict[str, object]:
    return {
        "pair_id": task.pair_id,
        "condition_pairing_policy": "index_matched",
        "start_pairing_policy": "zip_selected_starts",
        "A_condition_id": task.field_a.spec.condition_id,
        "B_condition_id": task.field_b.spec.condition_id,
        "A_substrate_id": task.field_a.spec.substrate_id,
        "B_substrate_id": task.field_b.spec.substrate_id,
        "A_selection_operator_id": task.field_a.spec.selection_operator.selection_operator_id,
        "B_selection_operator_id": task.field_b.spec.selection_operator.selection_operator_id,
        "A_law_id": task.field_a.spec.transformation_law.law_id,
        "B_law_id": task.field_b.spec.transformation_law.law_id,
        "coupled_operator_id": task.coupled_operator.coupled_operator_id,
        "coupled_operator_family": task.coupled_operator.coupled_operator_family,
        "start_index": task.start_index,
        "A_start_state_id": state_id(task.start_a),
        "B_start_state_id": state_id(task.start_b),
    }


def marginals(frontier: frozenset[JointState]) -> tuple[set[State], set[State]]:
    return {state[0] for state in frontier}, {state[1] for state in frontier}


def cap_frontier(frontier: set[JointState], cap: int) -> tuple[set[JointState], int]:
    if cap <= 0 or len(frontier) <= cap:
        return frontier, 0
    retained = set(sorted(frontier, key=joint_state_id)[:cap])
    return retained, 1


def artifact_status_for(truncated: bool, internal_capped: int) -> str:
    if internal_capped or truncated:
        return "truncated_noninterpretable"
    return "complete"


def comparison_feature_status(
    task: CoupledProbeTask,
    product_frontier: frozenset[JointState],
    coupled_frontier: frozenset[JointState],
    product_internal_capped: int,
    coupled_internal_capped: int,
) -> str:
    truncated = (
        len(product_frontier) > task.max_joint_frontier_nodes_per_horizon
        or len(coupled_frontier) > task.max_joint_frontier_nodes_per_horizon
    )
    return artifact_status_for(truncated, int(product_internal_capped or coupled_internal_capped))


def build_coupled_operator_spec(
    *,
    joint_selection_family: str,
    joint_effective_out_degree: int,
    coupling_strength: float,
) -> CoupledOperatorSpec:
    coupled_operator_family = coupled_operator_family_for(joint_selection_family)
    joint_energy_function_id = joint_energy_function_for(joint_selection_family)
    coupling_term_id = coupling_term_for(joint_selection_family)
    params_json = canonical_json({
        "coupling_strength": coupling_strength,
        "coupling_term_id": coupling_term_id,
        "joint_candidate_set_definition": "cartesian_product_of_component_selected_successors",
        "joint_effective_out_degree": joint_effective_out_degree,
        "joint_energy_function_id": joint_energy_function_id,
        "joint_selection_family": joint_selection_family,
        "product_baseline_definition": "cartesian_product_of_component_selected_successors",
        "shared_capacity_policy": shared_capacity_policy_for(joint_selection_family),
    })
    return CoupledOperatorSpec(
        coupled_operator_id=(
            f"coupled_operator__{joint_selection_family}"
            f"__k{int(joint_effective_out_degree)}"
            f"__{stable_hash(params_json, length=12)}"
        ),
        coupled_operator_family=coupled_operator_family,
        product_baseline_definition="cartesian_product_of_component_selected_successors",
        joint_candidate_set_definition="cartesian_product_of_component_selected_successors",
        joint_energy_function_id=joint_energy_function_id,
        joint_energy_params_json=params_json,
        coupling_term_id=coupling_term_id,
        coupling_strength=float(coupling_strength),
        joint_selection_family=joint_selection_family,
        joint_effective_out_degree=int(joint_effective_out_degree),
        stochastic_flag=0,
        seed_policy="deterministic_joint_energy_rank_order",
    )


def coupled_operator_family_for(joint_selection_family: str) -> str:
    if joint_selection_family == "shared_capacity":
        return "shared_capacity_joint_selector"
    return "rank_boundary_mismatch_penalized_joint_selector"


def joint_energy_function_for(joint_selection_family: str) -> str:
    if joint_selection_family == "shared_capacity":
        return "component_energy_sum_with_balanced_marginal_capacity_filter"
    return "component_energy_sum_plus_rank_boundary_offset_mismatch_penalty"


def coupling_term_for(joint_selection_family: str) -> str:
    if joint_selection_family == "shared_capacity":
        return "balanced_marginal_successor_capacity"
    return "rank_boundary_offset_absolute_difference_penalty"


def shared_capacity_policy_for(joint_selection_family: str) -> str:
    if joint_selection_family != "shared_capacity":
        return "not_applicable"
    return "per_source_balanced_marginal_usage_cap_ceil(joint_effective_out_degree / marginal_successor_count)"


def coupled_operator_canonical_json(spec: CoupledOperatorSpec) -> str:
    from dataclasses import asdict

    return canonical_json(asdict(spec))


def coupled_operator_digest(spec: CoupledOperatorSpec) -> str:
    return stable_hash(coupled_operator_canonical_json(spec), length=20)


def joint_state_id(joint_state: JointState) -> str:
    return f"A{state_id(joint_state[0])}|B{state_id(joint_state[1])}"
