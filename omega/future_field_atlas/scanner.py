from __future__ import annotations

from collections import defaultdict

from omega.rfs_mb0_future_landscape.substrate import State

from .contracts import EdgeAnatomy, RawScan, ScanTask
from .util import stable_hash, state_id


def scan_task(task: ScanTask) -> RawScan:
    condition = task.condition
    system = condition.system
    schedule = tuple(sorted(set(h for h in task.horizon_schedule if 0 <= h <= task.horizon_max)))
    schedule_set = set(schedule)
    frontiers: dict[int, frozenset[State]] = {}
    step_edges: dict[int, tuple[tuple[State, State], ...]] = {}
    node_rows: list[dict[str, object]] = []
    edge_rows: list[dict[str, object]] = []
    incoming_inside_boundary: dict[State, int] = defaultdict(int)
    incoming_outside_boundary: dict[State, int] = defaultdict(int)
    current = frozenset({task.start_state})
    for horizon in range(task.horizon_max + 1):
        frontiers[horizon] = current
        if horizon in schedule_set:
            node_rows.extend(
                node_rows_for_frontier(
                    task,
                    current,
                    horizon,
                    incoming_inside_boundary,
                    incoming_outside_boundary,
                )
            )
        if horizon >= task.horizon_max:
            break
        edges: list[tuple[State, State]] = []
        next_frontier: set[State] = set()
        next_inside_boundary: dict[State, int] = defaultdict(int)
        next_outside_boundary: dict[State, int] = defaultdict(int)
        for source in sorted(current):
            for target in system.edges.get(source, ()):
                anatomy = condition.candidate_anatomy.get((source, target))
                edges.append((source, target))
                next_frontier.add(target)
                if anatomy:
                    next_inside_boundary[target] += int(anatomy.inside_rank_boundary_flag)
                    next_outside_boundary[target] += int(anatomy.outside_rank_boundary_flag)
        step_edges[horizon] = tuple(edges)
        edge_rows.extend(edge_rows_for_step(task, horizon, edges))
        current = frozenset(next_frontier)
        incoming_inside_boundary = next_inside_boundary
        incoming_outside_boundary = next_outside_boundary
    return RawScan(
        scan_id=task.scan_id,
        spec=condition.spec,
        frontier_scan=task.frontier_scan,
        start_index=task.start_index,
        start_state=task.start_state,
        frontiers=frontiers,
        step_edges=step_edges,
        node_rows=node_rows,
        edge_rows=edge_rows,
    )


def node_rows_for_frontier(
    task: ScanTask,
    frontier: frozenset[State],
    horizon: int,
    incoming_inside_boundary: dict[State, int],
    incoming_outside_boundary: dict[State, int],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    component_ids = weak_component_ids(frontier, task.condition.system.edges)
    truncated = len(frontier) > task.max_frontier_nodes_per_horizon
    artifact_status = "complete" if not truncated else "truncated_noninterpretable"
    for rank, state in enumerate(sorted(frontier)[: task.max_frontier_nodes_per_horizon], start=1):
        rows.append({
            **base_scan_fields(task),
            "horizon": horizon,
            "state_id": state_id(state),
            "state_payload_hash": stable_hash(state),
            "frontier_membership_weight": 1.0,
            "frontier_rank": rank,
            "frontier_state_count_full": len(frontier),
            "frontier_nodes_truncated": int(truncated),
            "node_artifact_status": artifact_status,
            "node_artifact_retention_policy": task.frontier_scan.node_artifact_retention_policy,
            "incoming_inside_rank_boundary_flag": int(incoming_inside_boundary.get(state, 0) > 0),
            "incoming_outside_rank_boundary_flag": int(incoming_outside_boundary.get(state, 0) > 0),
            "component_id": component_ids.get(state, -1),
        })
    return rows


def edge_rows_for_step(task: ScanTask, horizon: int, edges: list[tuple[State, State]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    truncated = len(edges) > task.max_frontier_edges_per_step
    artifact_status = "complete" if not truncated else "truncated_noninterpretable"
    for rank, (source, target) in enumerate(edges[: task.max_frontier_edges_per_step], start=1):
        anatomy = task.condition.candidate_anatomy.get((source, target))
        rows.append({
            **base_scan_fields(task),
            "source_horizon": horizon,
            "target_horizon": horizon + 1,
            "source_state_id": state_id(source),
            "target_state_id": state_id(target),
            "edge_rank_within_step_sample": rank,
            "frontier_edge_count_full": len(edges),
            "frontier_edges_truncated": int(truncated),
            "edge_artifact_status": artifact_status,
            "edge_artifact_retention_policy": task.frontier_scan.edge_artifact_retention_policy,
            "edge_weight": 1.0,
            **edge_anatomy_fields(anatomy),
        })
    return rows


def edge_anatomy_fields(anatomy: EdgeAnatomy | None) -> dict[str, object]:
    if anatomy is None:
        return {
            "candidate_rank": "",
            "candidate_energy": "",
            "selected_flag": "",
            "inside_rank_boundary_flag": "",
            "outside_rank_boundary_flag": "",
            "rank_offset_from_boundary": "",
            "perturbation_changed_flag": "",
            "reference_selected_flag": "",
        }
    return {
        "candidate_rank": anatomy.candidate_rank,
        "candidate_energy": anatomy.candidate_energy,
        "selected_flag": anatomy.selected_flag,
        "inside_rank_boundary_flag": anatomy.inside_rank_boundary_flag,
        "outside_rank_boundary_flag": anatomy.outside_rank_boundary_flag,
        "rank_offset_from_boundary": anatomy.rank_offset_from_boundary,
        "perturbation_changed_flag": anatomy.perturbation_changed_flag,
        "reference_selected_flag": anatomy.reference_selected_flag,
    }


def base_scan_fields(task: ScanTask) -> dict[str, object]:
    spec = task.condition.spec
    operator = spec.selection_operator
    frontier_scan = task.frontier_scan
    return {
        "scan_id": task.scan_id,
        "substrate_id": spec.substrate_id,
        "condition_id": spec.condition_id,
        "group_id": spec.group_id,
        "seed": spec.seed,
        "state_space_id": spec.state_space.state_space_id,
        "coordinate_set_id": spec.state_space.coordinate_set_id,
        "symbol_domain_id": spec.state_space.symbol_domain_id,
        "state_id_schema": spec.state_space.state_id_schema,
        "metric_id": spec.state_space.metric_id,
        "adjacency_rule_id": spec.state_space.adjacency_rule_id,
        "law_id": spec.transformation_law.law_id,
        "law_family": spec.transformation_law.law_family,
        "candidate_successor_rule_id": spec.transformation_law.candidate_successor_rule_id,
        "candidate_successor_params_json": spec.transformation_law.candidate_successor_params_json,
        "energy_function_id": spec.transformation_law.energy_function_id,
        "energy_params_json": spec.transformation_law.energy_params_json,
        "admissibility_predicate_id": spec.transformation_law.admissibility_predicate_id,
        "observable_set_id": spec.observable.observable_set_id,
        "observable_family": spec.observable.observable_family,
        "observable_params_json": spec.observable.observable_params_json,
        "frontier_scan_id": frontier_scan.frontier_scan_id,
        "frontier_expansion_rule_id": frontier_scan.frontier_expansion_rule_id,
        "horizon_schedule_id": frontier_scan.horizon_schedule_id,
        "frontier_artifact_status_domain": "complete|lossless_compressed|sampled|truncated_noninterpretable",
        "selection_operator_id": operator.selection_operator_id,
        "selection_operator_family": operator.operator_family,
        "selection_operator_params_json": operator.operator_params_json,
        "base_out_degree": operator.base_out_degree,
        "effective_out_degree": operator.effective_out_degree,
        "retained_rank_set": rank_set_text(operator.retained_rank_set),
        "removed_rank_set": rank_set_text(operator.removed_rank_set),
        "stochastic_selection_flag": operator.stochastic_flag,
        "seed_policy": operator.seed_policy,
        "start_state_id": state_id(task.start_state),
        "start_index": task.start_index,
        "rank_boundary_k": spec.rank_boundary_k,
        "macro_invariant_kind": spec.macro_invariant_kind,
        "macro_invariant_beta": spec.macro_invariant_beta,
    }


def rank_set_text(values: tuple[int, ...]) -> str:
    return ";".join(str(value) for value in values)


def weak_component_ids(frontier: frozenset[State], edges: dict[State, tuple[State, ...]]) -> dict[State, int]:
    frontier_set = set(frontier)
    adjacency: dict[State, set[State]] = {state: set() for state in frontier}
    for source in frontier:
        for target in edges.get(source, ()):
            if target in frontier_set:
                adjacency[source].add(target)
                adjacency[target].add(source)
    component_ids: dict[State, int] = {}
    component = 0
    for state in sorted(frontier):
        if state in component_ids:
            continue
        stack = [state]
        component_ids[state] = component
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor not in component_ids:
                    component_ids[neighbor] = component
                    stack.append(neighbor)
        component += 1
    return component_ids
