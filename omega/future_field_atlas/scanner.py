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
    incoming_core: dict[State, int] = defaultdict(int)
    incoming_fringe: dict[State, int] = defaultdict(int)
    current = frozenset({task.start_state})
    for horizon in range(task.horizon_max + 1):
        frontiers[horizon] = current
        if horizon in schedule_set:
            node_rows.extend(node_rows_for_frontier(task, current, horizon, incoming_core, incoming_fringe))
        if horizon >= task.horizon_max:
            break
        edges: list[tuple[State, State]] = []
        next_frontier: set[State] = set()
        next_core: dict[State, int] = defaultdict(int)
        next_fringe: dict[State, int] = defaultdict(int)
        for source in sorted(current):
            for target in system.edges.get(source, ()):
                anatomy = condition.candidate_anatomy.get((source, target))
                edges.append((source, target))
                next_frontier.add(target)
                if anatomy:
                    next_core[target] += int(anatomy.core_flag)
                    next_fringe[target] += int(anatomy.fringe_flag)
        step_edges[horizon] = tuple(edges)
        edge_rows.extend(edge_rows_for_step(task, horizon, edges))
        current = frozenset(next_frontier)
        incoming_core = next_core
        incoming_fringe = next_fringe
    return RawScan(
        scan_id=task.scan_id,
        spec=condition.spec,
        start_index=task.start_index,
        start_state=task.start_state,
        horizon_schedule=schedule,
        horizon_max=task.horizon_max,
        max_frontier_nodes_per_horizon=task.max_frontier_nodes_per_horizon,
        max_frontier_edges_per_step=task.max_frontier_edges_per_step,
        frontiers=frontiers,
        step_edges=step_edges,
        node_rows=node_rows,
        edge_rows=edge_rows,
    )


def node_rows_for_frontier(
    task: ScanTask,
    frontier: frozenset[State],
    horizon: int,
    incoming_core: dict[State, int],
    incoming_fringe: dict[State, int],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    component_ids = weak_component_ids(frontier, task.condition.system.edges)
    truncated = len(frontier) > task.max_frontier_nodes_per_horizon
    artifact_status = "complete" if not truncated else "truncated_sorted_prefix_noninterpretable"
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
            "core_membership_flag": int(incoming_core.get(state, 0) > 0),
            "fringe_membership_flag": int(incoming_fringe.get(state, 0) > 0),
            "component_id": component_ids.get(state, -1),
        })
    return rows


def edge_rows_for_step(task: ScanTask, horizon: int, edges: list[tuple[State, State]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    truncated = len(edges) > task.max_frontier_edges_per_step
    artifact_status = "complete" if not truncated else "truncated_sorted_prefix_noninterpretable"
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
            "core_flag": "",
            "fringe_flag": "",
            "rank_offset_from_core_boundary": "",
            "perturbation_changed_flag": "",
            "baseline_selected_flag": "",
        }
    return {
        "candidate_rank": anatomy.candidate_rank,
        "candidate_energy": anatomy.candidate_energy,
        "selected_flag": anatomy.selected_flag,
        "core_flag": anatomy.core_flag,
        "fringe_flag": anatomy.fringe_flag,
        "rank_offset_from_core_boundary": anatomy.rank_offset_from_core_boundary,
        "perturbation_changed_flag": anatomy.perturbation_changed_flag,
        "baseline_selected_flag": anatomy.baseline_selected_flag,
    }


def base_scan_fields(task: ScanTask) -> dict[str, object]:
    spec = task.condition.spec
    operator = spec.selection_operator
    return {
        "scan_id": task.scan_id,
        "substrate_id": spec.substrate_id,
        "condition_id": spec.condition_id,
        "group_id": spec.group_id,
        "seed": spec.seed,
        "state_space_id": spec.state_space.state_space_id,
        "law_id": spec.transformation_law.law_id,
        "law_family": spec.transformation_law.law_family,
        "observable_set_id": spec.observable.observable_set_id,
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
        "core_rank_k": spec.core_rank_k,
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
