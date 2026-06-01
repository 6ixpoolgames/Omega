from __future__ import annotations

from collections import defaultdict

from omega.rfs_mb0_future_landscape.substrate import State

from .contracts import GeneratedCondition, MappedScan, RawScan
from .util import entropy_from_weights, state_id


def map_scan(raw: RawScan, condition: GeneratedCondition) -> MappedScan:
    profile_rows = profile_rows_for_scan(raw, condition)
    membership_rows = membership_rows_for_scan(raw, condition)
    boundary_rows = boundary_rows_for_scan(raw, condition)
    return MappedScan(
        raw=raw,
        profile_rows=profile_rows,
        membership_rows=membership_rows,
        boundary_rows=boundary_rows,
    )


def profile_rows_for_scan(raw: RawScan, condition: GeneratedCondition) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    first_seen: dict[State, int] = {}
    previous_frontier: frozenset[State] = frozenset()
    for horizon in range(raw.horizon_max + 1):
        frontier = raw.frontiers[horizon]
        for state in frontier:
            first_seen.setdefault(state, horizon)
        if horizon not in raw.horizon_schedule:
            previous_frontier = frontier
            continue
        step_edges = raw.step_edges.get(horizon, tuple())
        component_count, largest_fraction = component_summary(frontier, step_edges)
        new_states = len([state for state in frontier if first_seen.get(state) == horizon])
        extinct_states = len(previous_frontier - frontier) if horizon > 0 else 0
        returning_states = len([state for state in frontier if first_seen.get(state, horizon) < horizon and state not in previous_frontier])
        inside_boundary_edges, outside_boundary_edges = edge_class_counts(
            raw.step_edges.get(max(0, horizon - 1), ()),
            condition,
        )
        node_truncated = len(frontier) > raw.max_frontier_nodes_per_horizon
        edge_truncated = len(step_edges) > raw.max_frontier_edges_per_step
        rows.append({
            **profile_base_fields(raw),
            "horizon": horizon,
            "feature_status": "complete" if not node_truncated and not edge_truncated else "truncated_noninterpretable",
            "node_artifact_status": "complete" if not node_truncated else "truncated_noninterpretable",
            "edge_artifact_status": "complete" if not edge_truncated else "truncated_noninterpretable",
            "frontier_state_count": len(frontier),
            "frontier_edge_count": len(step_edges),
            "frontier_component_count": component_count,
            "largest_component_fraction": largest_fraction,
            "frontier_entropy": entropy_from_weights([1.0 for _state in frontier]),
            "inside_rank_boundary_state_count": state_class_count(
                raw.step_edges.get(max(0, horizon - 1), ()),
                condition,
                "inside",
            ),
            "outside_rank_boundary_state_count": state_class_count(
                raw.step_edges.get(max(0, horizon - 1), ()),
                condition,
                "outside",
            ),
            "inside_rank_boundary_edge_count": inside_boundary_edges,
            "outside_rank_boundary_edge_count": outside_boundary_edges,
            "inside_outside_rank_boundary_ratio": inside_boundary_edges / max(1, outside_boundary_edges),
            "new_state_count": new_states,
            "extinct_state_count": extinct_states,
            "returning_state_count": returning_states,
        })
        previous_frontier = frontier
    return rows


def membership_rows_for_scan(raw: RawScan, condition: GeneratedCondition) -> list[dict[str, object]]:
    presence: dict[State, list[int]] = defaultdict(list)
    inside_boundary_counts: dict[State, int] = defaultdict(int)
    outside_boundary_counts: dict[State, int] = defaultdict(int)
    for horizon in range(raw.horizon_max + 1):
        for state in raw.frontiers[horizon]:
            presence[state].append(horizon)
    for edges in raw.step_edges.values():
        for source, target in edges:
            anatomy = condition.candidate_anatomy.get((source, target))
            if not anatomy:
                continue
            inside_boundary_counts[target] += int(anatomy.inside_rank_boundary_flag)
            outside_boundary_counts[target] += int(anatomy.outside_rank_boundary_flag)
    rows: list[dict[str, object]] = []
    for state, horizons in sorted(presence.items(), key=lambda item: item[0]):
        rows.append({
            **profile_base_fields(raw),
            "state_id": state_id(state),
            "first_seen_horizon": min(horizons),
            "last_seen_horizon": max(horizons),
            "horizon_presence_sparse_list": ";".join(str(horizon) for horizon in horizons),
            "presence_count": len(horizons),
            "inside_rank_boundary_presence_count": inside_boundary_counts.get(state, 0),
            "outside_rank_boundary_presence_count": outside_boundary_counts.get(state, 0),
        })
    return rows


def boundary_rows_for_scan(raw: RawScan, condition: GeneratedCondition) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for horizon in raw.horizon_schedule:
        if horizon == 0:
            edges: tuple[tuple[State, State], ...] = tuple()
        else:
            edges = raw.step_edges.get(horizon - 1, tuple())
        selected_inside_boundary = 0
        selected_outside_boundary = 0
        boundary = 0
        inside_boundary_energies: list[float] = []
        outside_boundary_energies: list[float] = []
        for source, target in edges:
            anatomy = condition.candidate_anatomy.get((source, target))
            if not anatomy:
                continue
            selected_inside_boundary += int(anatomy.inside_rank_boundary_flag)
            selected_outside_boundary += int(anatomy.outside_rank_boundary_flag)
            boundary += int(anatomy.candidate_rank in {raw.spec.rank_boundary_k, raw.spec.rank_boundary_k + 1})
            if anatomy.inside_rank_boundary_flag:
                inside_boundary_energies.append(anatomy.candidate_energy)
            if anatomy.outside_rank_boundary_flag:
                outside_boundary_energies.append(anatomy.candidate_energy)
        weakest_inside = max(inside_boundary_energies) if inside_boundary_energies else ""
        strongest_outside = min(outside_boundary_energies) if outside_boundary_energies else ""
        gap = (float(strongest_outside) - float(weakest_inside)) if strongest_outside != "" and weakest_inside != "" else ""
        rows.append({
            **profile_base_fields(raw),
            "horizon": horizon,
            "inside_rank_boundary_edge_count": selected_inside_boundary,
            "outside_rank_boundary_edge_count": selected_outside_boundary,
            "rank_boundary_edge_count": boundary,
            "weakest_inside_rank_boundary_energy": weakest_inside,
            "strongest_outside_rank_boundary_energy": strongest_outside,
            "rank_boundary_energy_gap": gap,
            "selected_inside_rank_boundary_fraction": selected_inside_boundary / max(
                1,
                selected_inside_boundary + selected_outside_boundary,
            ),
            "selected_outside_rank_boundary_fraction": selected_outside_boundary / max(
                1,
                selected_inside_boundary + selected_outside_boundary,
            ),
        })
    return rows


def profile_base_fields(raw: RawScan) -> dict[str, object]:
    spec = raw.spec
    operator = spec.selection_operator
    frontier_scan = raw.frontier_scan
    return {
        "scan_id": raw.scan_id,
        "condition_id": spec.condition_id,
        "substrate_id": spec.substrate_id,
        "group_id": spec.group_id,
        "seed": spec.seed,
        "state_space_id": spec.state_space.state_space_id,
        "coordinate_set_id": spec.state_space.coordinate_set_id,
        "symbol_domain_id": spec.state_space.symbol_domain_id,
        "state_id_schema": spec.state_space.state_id_schema,
        "metric_id": spec.state_space.metric_id,
        "adjacency_rule_id": spec.state_space.adjacency_rule_id,
        "state_space_params_json": spec.state_space.state_space_params_json,
        "law_id": spec.transformation_law.law_id,
        "law_family": spec.transformation_law.law_family,
        "candidate_successor_rule_id": spec.transformation_law.candidate_successor_rule_id,
        "candidate_successor_params_json": spec.transformation_law.candidate_successor_params_json,
        "energy_function_id": spec.transformation_law.energy_function_id,
        "energy_params_json": spec.transformation_law.energy_params_json,
        "admissibility_predicate_id": spec.transformation_law.admissibility_predicate_id,
        "invariant_observable_id": spec.transformation_law.invariant_observable_id,
        "invariant_params_json": spec.transformation_law.invariant_params_json,
        "asymmetry_term_id": spec.transformation_law.asymmetry_term_id,
        "roughness_term_id": spec.transformation_law.roughness_term_id,
        "transformation_law_seed_policy": spec.transformation_law.seed_policy,
        "observable_set_id": spec.observable.observable_set_id,
        "observable_family": spec.observable.observable_family,
        "observable_params_json": spec.observable.observable_params_json,
        "frontier_scan_id": frontier_scan.frontier_scan_id,
        "frontier_expansion_rule_id": frontier_scan.frontier_expansion_rule_id,
        "horizon_schedule_id": frontier_scan.horizon_schedule_id,
        "frontier_scan_params_json": frontier_scan.frontier_scan_params_json,
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
        "start_index": raw.start_index,
        "start_state_id": state_id(raw.start_state),
        "macro_invariant_kind": spec.macro_invariant_kind,
        "macro_invariant_beta": spec.macro_invariant_beta,
        "rank_boundary_k": spec.rank_boundary_k,
    }


def rank_set_text(values: tuple[int, ...]) -> str:
    return ";".join(str(value) for value in values)


def component_summary(frontier: frozenset[State], step_edges: tuple[tuple[State, State], ...]) -> tuple[int, float]:
    if not frontier:
        return 0, 0.0
    adjacency: dict[State, set[State]] = {state: set() for state in frontier}
    sources_by_target: dict[State, list[State]] = defaultdict(list)
    for source, target in step_edges:
        if source in adjacency:
            sources_by_target[target].append(source)
    for sources in sources_by_target.values():
        for left in sources:
            for right in sources:
                if left != right:
                    adjacency[left].add(right)
    seen: set[State] = set()
    sizes: list[int] = []
    for state in frontier:
        if state in seen:
            continue
        stack = [state]
        seen.add(state)
        size = 0
        while stack:
            current = stack.pop()
            size += 1
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        sizes.append(size)
    return len(sizes), max(sizes) / max(1, len(frontier))


def edge_class_counts(edges: tuple[tuple[State, State], ...], condition: GeneratedCondition) -> tuple[int, int]:
    inside_boundary = 0
    outside_boundary = 0
    for source, target in edges:
        anatomy = condition.candidate_anatomy.get((source, target))
        if anatomy:
            inside_boundary += int(anatomy.inside_rank_boundary_flag)
            outside_boundary += int(anatomy.outside_rank_boundary_flag)
    return inside_boundary, outside_boundary


def state_class_count(edges: tuple[tuple[State, State], ...], condition: GeneratedCondition, kind: str) -> int:
    states: set[State] = set()
    for source, target in edges:
        anatomy = condition.candidate_anatomy.get((source, target))
        if not anatomy:
            continue
        if kind == "inside" and anatomy.inside_rank_boundary_flag:
            states.add(target)
        elif kind == "outside" and anatomy.outside_rank_boundary_flag:
            states.add(target)
    return len(states)
