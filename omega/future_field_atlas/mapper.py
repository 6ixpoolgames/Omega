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
        component_count, largest_fraction = component_summary(frontier, condition.system.edges)
        new_states = len([state for state in frontier if first_seen.get(state) == horizon])
        extinct_states = len(previous_frontier - frontier) if horizon > 0 else 0
        returning_states = len([state for state in frontier if first_seen.get(state, horizon) < horizon and state not in previous_frontier])
        core_edges, fringe_edges = edge_class_counts(raw.step_edges.get(max(0, horizon - 1), ()), condition)
        rows.append({
            **profile_base_fields(raw),
            "horizon": horizon,
            "frontier_state_count": len(frontier),
            "frontier_edge_count": len(raw.step_edges.get(horizon, ())),
            "frontier_component_count": component_count,
            "largest_component_fraction": largest_fraction,
            "frontier_entropy": entropy_from_weights([1.0 for _state in frontier]),
            "core_state_count": state_class_count(raw.step_edges.get(max(0, horizon - 1), ()), condition, "core"),
            "fringe_state_count": state_class_count(raw.step_edges.get(max(0, horizon - 1), ()), condition, "fringe"),
            "core_edge_count": core_edges,
            "fringe_edge_count": fringe_edges,
            "core_fringe_ratio": core_edges / max(1, fringe_edges),
            "new_state_count": new_states,
            "extinct_state_count": extinct_states,
            "returning_state_count": returning_states,
        })
        previous_frontier = frontier
    return rows


def membership_rows_for_scan(raw: RawScan, condition: GeneratedCondition) -> list[dict[str, object]]:
    presence: dict[State, list[int]] = defaultdict(list)
    core_counts: dict[State, int] = defaultdict(int)
    fringe_counts: dict[State, int] = defaultdict(int)
    for horizon in range(raw.horizon_max + 1):
        for state in raw.frontiers[horizon]:
            presence[state].append(horizon)
    for edges in raw.step_edges.values():
        for source, target in edges:
            anatomy = condition.candidate_anatomy.get((source, target))
            if not anatomy:
                continue
            core_counts[target] += int(anatomy.core_flag)
            fringe_counts[target] += int(anatomy.fringe_flag)
    rows: list[dict[str, object]] = []
    for state, horizons in sorted(presence.items(), key=lambda item: item[0]):
        rows.append({
            **profile_base_fields(raw),
            "state_id": state_id(state),
            "first_seen_horizon": min(horizons),
            "last_seen_horizon": max(horizons),
            "horizon_presence_sparse_list": ";".join(str(horizon) for horizon in horizons),
            "presence_count": len(horizons),
            "core_presence_count": core_counts.get(state, 0),
            "fringe_presence_count": fringe_counts.get(state, 0),
        })
    return rows


def boundary_rows_for_scan(raw: RawScan, condition: GeneratedCondition) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    candidates_by_source: dict[State, list[tuple[State, object]]] = defaultdict(list)
    for (source, target), anatomy in condition.candidate_anatomy.items():
        candidates_by_source[source].append((target, anatomy))
    for horizon in raw.horizon_schedule:
        if horizon == 0:
            edges: tuple[tuple[State, State], ...] = tuple()
            sources: frozenset[State] = frozenset({raw.start_state})
        else:
            edges = raw.step_edges.get(horizon - 1, tuple())
            sources = raw.frontiers.get(horizon - 1, frozenset())
        selected_core = 0
        selected_fringe = 0
        boundary = 0
        core_energies: list[float] = []
        fringe_energies: list[float] = []
        retained_core = 0
        retained_fringe = 0
        baseline_core_total = 0
        baseline_fringe_total = 0
        selected_keys = set(edges)
        for source in sources:
            for target, anatomy in candidates_by_source.get(source, []):
                if not anatomy.baseline_selected_flag:
                    continue
                if anatomy.candidate_rank <= raw.spec.core_rank_k:
                    baseline_core_total += 1
                    retained_core += int((source, target) in selected_keys)
                else:
                    baseline_fringe_total += 1
                    retained_fringe += int((source, target) in selected_keys)
        for source, target in edges:
            anatomy = condition.candidate_anatomy.get((source, target))
            if not anatomy:
                continue
            selected_core += int(anatomy.core_flag)
            selected_fringe += int(anatomy.fringe_flag)
            boundary += int(anatomy.candidate_rank in {raw.spec.core_rank_k, raw.spec.core_rank_k + 1})
            if anatomy.core_flag:
                core_energies.append(anatomy.candidate_energy)
            if anatomy.fringe_flag:
                fringe_energies.append(anatomy.candidate_energy)
        weakest_core = max(core_energies) if core_energies else ""
        strongest_fringe = min(fringe_energies) if fringe_energies else ""
        gap = (float(strongest_fringe) - float(weakest_core)) if strongest_fringe != "" and weakest_core != "" else ""
        rows.append({
            **profile_base_fields(raw),
            "horizon": horizon,
            "base_m": raw.spec.base_m,
            "effective_m": raw.spec.effective_m,
            "core_edge_count": selected_core,
            "fringe_edge_count": selected_fringe,
            "boundary_edge_count": boundary,
            "weakest_core_energy_mean": weakest_core,
            "strongest_fringe_energy_mean": strongest_fringe,
            "core_fringe_energy_gap_mean": gap,
            "core_retention_fraction_vs_baseline": retained_core / baseline_core_total if baseline_core_total else "",
            "fringe_retention_fraction_vs_baseline": retained_fringe / baseline_fringe_total if baseline_fringe_total else "",
            "selected_core_fraction": selected_core / max(1, selected_core + selected_fringe),
            "selected_fringe_fraction": selected_fringe / max(1, selected_core + selected_fringe),
            "baseline_core_edge_count": baseline_core_total,
            "baseline_fringe_edge_count": baseline_fringe_total,
        })
    return rows


def profile_base_fields(raw: RawScan) -> dict[str, object]:
    spec = raw.spec
    return {
        "scan_id": raw.scan_id,
        "condition_id": spec.condition_id,
        "substrate_id": spec.substrate_id,
        "group_id": spec.group_id,
        "seed": spec.seed,
        "substrate_family": spec.substrate_family,
        "substrate_variant": spec.substrate_variant,
        "boundary_control": spec.boundary_control,
        "condition_role": spec.role,
        "start_index": raw.start_index,
        "start_state_id": state_id(raw.start_state),
        "macro_invariant_kind": spec.macro_invariant_kind,
        "macro_invariant_beta": spec.macro_invariant_beta,
        "core_rank_k": spec.core_rank_k,
    }


def component_summary(frontier: frozenset[State], edges: dict[State, tuple[State, ...]]) -> tuple[int, float]:
    if not frontier:
        return 0, 0.0
    frontier_set = set(frontier)
    adjacency: dict[State, set[State]] = {state: set() for state in frontier}
    for source in frontier:
        for target in edges.get(source, ()):
            if target in frontier_set:
                adjacency[source].add(target)
                adjacency[target].add(source)
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
    core = 0
    fringe = 0
    for source, target in edges:
        anatomy = condition.candidate_anatomy.get((source, target))
        if anatomy:
            core += int(anatomy.core_flag)
            fringe += int(anatomy.fringe_flag)
    return core, fringe


def state_class_count(edges: tuple[tuple[State, State], ...], condition: GeneratedCondition, kind: str) -> int:
    states: set[State] = set()
    for source, target in edges:
        anatomy = condition.candidate_anatomy.get((source, target))
        if not anatomy:
            continue
        if kind == "core" and anatomy.core_flag:
            states.add(target)
        elif kind == "fringe" and anatomy.fringe_flag:
            states.add(target)
    return len(states)
