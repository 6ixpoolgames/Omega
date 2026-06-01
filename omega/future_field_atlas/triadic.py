from __future__ import annotations

from dataclasses import dataclass

from omega.rfs_mb0_future_landscape.substrate import State

from .contracts import GeneratedCondition
from .util import state_id


TriadicState = tuple[State, State, State]


@dataclass(frozen=True)
class TriadicProbeTask:
    triple_id: str
    field_a: GeneratedCondition
    field_b: GeneratedCondition
    field_c: GeneratedCondition
    start_a: State
    start_b: State
    start_c: State
    horizon_schedule: tuple[int, ...]
    horizon_max: int
    joint_effective_out_degree: int
    coupling_strength: float
    max_internal_joint_frontier_states: int


@dataclass
class TriadicProbeResult:
    triple_id: str
    profile_rows: list[dict[str, object]]
    residual_rows: list[dict[str, object]]
    internal_cap_rows: list[dict[str, object]]


@dataclass(frozen=True)
class TriadicEdge:
    source: TriadicState
    target: TriadicState
    a_rank_offset_from_boundary: int
    b_rank_offset_from_boundary: int
    c_rank_offset_from_boundary: int
    joint_transition_energy: float


def scan_triadic_probe(task: TriadicProbeTask) -> TriadicProbeResult:
    schedule = tuple(sorted(set(h for h in task.horizon_schedule if 0 <= h <= task.horizon_max)))
    schedule_set = set(schedule)
    product_current = frozenset({(task.start_a, task.start_b, task.start_c)})
    triadic_current = product_current
    product_cap_poisoned = 0
    triadic_cap_poisoned = 0
    profile_rows: list[dict[str, object]] = []
    residual_rows: list[dict[str, object]] = []
    internal_cap_rows: list[dict[str, object]] = []
    for horizon in range(task.horizon_max + 1):
        if horizon in schedule_set:
            feature_status = artifact_status_for(product_cap_poisoned or triadic_cap_poisoned)
            profile_rows.append(profile_row(task, "product_baseline", horizon, product_current, product_cap_poisoned))
            profile_rows.append(profile_row(task, "triadic", horizon, triadic_current, triadic_cap_poisoned))
            residual_rows.append(residual_row(task, horizon, product_current, triadic_current, feature_status))
        if horizon >= task.horizon_max:
            break
        product_edges = expand_triadic_edges(task, product_current, mode="product_baseline")
        triadic_edges = expand_triadic_edges(task, triadic_current, mode="triadic")
        product_next, product_capped = cap_frontier(
            {edge.target for edge in product_edges},
            task.max_internal_joint_frontier_states,
        )
        triadic_next, triadic_capped = cap_frontier(
            {edge.target for edge in triadic_edges},
            task.max_internal_joint_frontier_states,
        )
        if product_capped:
            internal_cap_rows.append(
                internal_cap_row(task, "product_baseline", horizon + 1, len({edge.target for edge in product_edges}), len(product_next))
            )
        if triadic_capped:
            internal_cap_rows.append(
                internal_cap_row(task, "triadic", horizon + 1, len({edge.target for edge in triadic_edges}), len(triadic_next))
            )
        product_cap_poisoned = int(product_cap_poisoned or product_capped)
        triadic_cap_poisoned = int(triadic_cap_poisoned or triadic_capped)
        product_current = frozenset(product_next)
        triadic_current = frozenset(triadic_next)
    return TriadicProbeResult(
        triple_id=task.triple_id,
        profile_rows=profile_rows,
        residual_rows=residual_rows,
        internal_cap_rows=internal_cap_rows,
    )


def expand_triadic_edges(task: TriadicProbeTask, frontier: frozenset[TriadicState], mode: str) -> list[TriadicEdge]:
    edges: list[TriadicEdge] = []
    for source in sorted(frontier, key=triadic_state_id):
        a_source, b_source, c_source = source
        candidates: list[TriadicEdge] = []
        for a_target in task.field_a.system.edges.get(a_source, ()):
            a_anatomy = task.field_a.candidate_anatomy[(a_source, a_target)]
            for b_target in task.field_b.system.edges.get(b_source, ()):
                b_anatomy = task.field_b.candidate_anatomy[(b_source, b_target)]
                for c_target in task.field_c.system.edges.get(c_source, ()):
                    c_anatomy = task.field_c.candidate_anatomy[(c_source, c_target)]
                    pairwise_penalty = (
                        abs(a_anatomy.rank_offset_from_boundary - b_anatomy.rank_offset_from_boundary)
                        + abs(a_anatomy.rank_offset_from_boundary - c_anatomy.rank_offset_from_boundary)
                        + abs(b_anatomy.rank_offset_from_boundary - c_anatomy.rank_offset_from_boundary)
                    )
                    candidates.append(
                        TriadicEdge(
                            source=source,
                            target=(a_target, b_target, c_target),
                            a_rank_offset_from_boundary=int(a_anatomy.rank_offset_from_boundary),
                            b_rank_offset_from_boundary=int(b_anatomy.rank_offset_from_boundary),
                            c_rank_offset_from_boundary=int(c_anatomy.rank_offset_from_boundary),
                            joint_transition_energy=float(
                                a_anatomy.candidate_energy
                                + b_anatomy.candidate_energy
                                + c_anatomy.candidate_energy
                                + task.coupling_strength * pairwise_penalty
                            ),
                        )
                    )
        candidates.sort(
            key=lambda edge: (
                edge.joint_transition_energy,
                edge.a_rank_offset_from_boundary,
                edge.b_rank_offset_from_boundary,
                edge.c_rank_offset_from_boundary,
                triadic_state_id(edge.target),
            )
        )
        if mode == "product_baseline":
            edges.extend(candidates)
        elif mode == "triadic":
            edges.extend(candidates[: max(1, task.joint_effective_out_degree)])
        else:
            raise ValueError(f"unsupported triadic mode: {mode}")
    return edges


def profile_row(
    task: TriadicProbeTask,
    mode: str,
    horizon: int,
    frontier: frozenset[TriadicState],
    internal_capped: int,
) -> dict[str, object]:
    a_states, b_states, c_states = marginals(frontier)
    product_count = len(a_states) * len(b_states) * len(c_states)
    return {
        **base_fields(task),
        "joint_scan_mode": mode,
        "horizon": horizon,
        "feature_status": artifact_status_for(internal_capped),
        "joint_frontier_state_count": len(frontier),
        "A_marginal_state_count": len(a_states),
        "B_marginal_state_count": len(b_states),
        "C_marginal_state_count": len(c_states),
        "marginal_product_state_count": product_count,
        "joint_density_vs_marginal_product": len(frontier) / max(1, product_count),
        "internal_frontier_capped": int(internal_capped),
    }


def residual_row(
    task: TriadicProbeTask,
    horizon: int,
    product_frontier: frozenset[TriadicState],
    triadic_frontier: frozenset[TriadicState],
    feature_status: str,
) -> dict[str, object]:
    intersection = product_frontier & triadic_frontier
    union = product_frontier | triadic_frontier
    product_a, product_b, product_c = marginals(product_frontier)
    triadic_a, triadic_b, triadic_c = marginals(triadic_frontier)
    return {
        **base_fields(task),
        "horizon": horizon,
        "feature_status": feature_status,
        "product_joint_support_count": len(product_frontier),
        "triadic_joint_support_count": len(triadic_frontier),
        "joint_support_intersection_count": len(intersection),
        "joint_support_union_count": len(union),
        "joint_support_residual_fraction": len(union - intersection) / max(1, len(union)),
        "A_marginal_retention_fraction": len(product_a & triadic_a) / max(1, len(product_a)),
        "B_marginal_retention_fraction": len(product_b & triadic_b) / max(1, len(product_b)),
        "C_marginal_retention_fraction": len(product_c & triadic_c) / max(1, len(product_c)),
    }


def internal_cap_row(
    task: TriadicProbeTask,
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


def base_fields(task: TriadicProbeTask) -> dict[str, object]:
    return {
        "triple_id": task.triple_id,
        "A_condition_id": task.field_a.spec.condition_id,
        "B_condition_id": task.field_b.spec.condition_id,
        "C_condition_id": task.field_c.spec.condition_id,
        "A_selection_operator_id": task.field_a.spec.selection_operator.selection_operator_id,
        "B_selection_operator_id": task.field_b.spec.selection_operator.selection_operator_id,
        "C_selection_operator_id": task.field_c.spec.selection_operator.selection_operator_id,
        "A_start_state_id": state_id(task.start_a),
        "B_start_state_id": state_id(task.start_b),
        "C_start_state_id": state_id(task.start_c),
        "triadic_operator_family": "pairwise_rank_boundary_mismatch_penalized_joint_selector",
        "triadic_joint_effective_out_degree": task.joint_effective_out_degree,
        "triadic_coupling_strength": task.coupling_strength,
    }


def marginals(frontier: frozenset[TriadicState]) -> tuple[set[State], set[State], set[State]]:
    return {state[0] for state in frontier}, {state[1] for state in frontier}, {state[2] for state in frontier}


def cap_frontier(frontier: set[TriadicState], cap: int) -> tuple[set[TriadicState], int]:
    if cap <= 0 or len(frontier) <= cap:
        return frontier, 0
    retained = set(sorted(frontier, key=triadic_state_id)[:cap])
    return retained, 1


def artifact_status_for(internal_capped: int) -> str:
    if internal_capped:
        return "truncated_noninterpretable"
    return "complete"


def triadic_state_id(joint_state: TriadicState) -> str:
    return f"A{state_id(joint_state[0])}|B{state_id(joint_state[1])}|C{state_id(joint_state[2])}"
