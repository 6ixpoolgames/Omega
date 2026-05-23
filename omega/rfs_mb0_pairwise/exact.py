from __future__ import annotations

from .substrate import MB0System, State, a_continuous, b_continuous, shuffled_a_continuous, shuffled_b_continuous


def reachable(
    system: MB0System,
    start: State,
    horizon: int,
    predicate=None,
) -> frozenset[State]:
    if predicate is not None and not predicate(start):
        return frozenset()
    seen = {start}
    frontier = {start}
    for _ in range(horizon):
        next_frontier: set[State] = set()
        for state in frontier:
            for target in system.edges[state]:
                if predicate is None or predicate(target):
                    next_frontier.add(target)
        next_frontier -= seen
        if not next_frontier:
            break
        seen.update(next_frontier)
        frontier = next_frontier
    return frozenset(seen)


def identity_predicates(system: MB0System):
    if system.control_type == "identity_shuffle_control":
        return (
            lambda state: shuffled_a_continuous(state, system.seed),
            lambda state: shuffled_b_continuous(state, system.seed),
        )
    if system.control_type == "permissive_control":
        return (lambda _state: True, lambda _state: True)
    return a_continuous, b_continuous


def pairwise_metrics(system: MB0System, horizon: int) -> dict[str, int | float | str]:
    pred_a, pred_b = identity_predicates(system)
    pred_ab = lambda state: pred_a(state) and pred_b(state)
    reach = reachable(system, system.initial_state, horizon)
    f_a = reachable(system, system.initial_state, horizon, pred_a)
    f_b = reachable(system, system.initial_state, horizon, pred_b)
    f_ab = reachable(system, system.initial_state, horizon, pred_ab)
    a_count = len(f_a)
    b_count = len(f_b)
    ab_count = len(f_ab)
    min_singleton = min(a_count, b_count)
    return {
        "H": horizon,
        "reach_count": len(reach),
        "A_count": a_count,
        "B_count": b_count,
        "AB_count": ab_count,
        "A_viable": int(a_count > 0),
        "B_viable": int(b_count > 0),
        "AB_viable": int(ab_count > 0),
        "AB_over_A": ab_count / max(1, a_count),
        "AB_over_B": ab_count / max(1, b_count),
        "joint_gap": min_singleton - ab_count,
        "joint_gap_ratio": ab_count / max(1, min_singleton),
        "class_bin": classify(a_count, b_count, ab_count),
    }


def transition_deltas(system: MB0System, horizon: int) -> dict[str, int | float]:
    initial = system.initial_state
    pred_a, pred_b = identity_predicates(system)
    pred_ab = lambda state: pred_a(state) and pred_b(state)
    base_a = len(reachable(system, initial, horizon, pred_a))
    base_b = len(reachable(system, initial, horizon, pred_b))
    base_ab = len(reachable(system, initial, horizon, pred_ab))
    targets = system.edges[initial]
    if not targets:
        return {
            "mean_A_delta": 0.0,
            "mean_B_delta": 0.0,
            "mean_AB_delta": 0.0,
            "local_A_joint_contracting_rate": 0.0,
            "local_B_joint_contracting_rate": 0.0,
        }
    deltas = []
    for target in targets:
        a_delta = len(reachable(system, target, horizon, pred_a)) - base_a
        b_delta = len(reachable(system, target, horizon, pred_b)) - base_b
        ab_delta = len(reachable(system, target, horizon, pred_ab)) - base_ab
        deltas.append((a_delta, b_delta, ab_delta))
    a_contracting = [(a, ab) for a, _b, ab in deltas if ab < 0]
    b_contracting = [(b, ab) for _a, b, ab in deltas if ab < 0]
    return {
        "mean_A_delta": sum(item[0] for item in deltas) / len(deltas),
        "mean_B_delta": sum(item[1] for item in deltas) / len(deltas),
        "mean_AB_delta": sum(item[2] for item in deltas) / len(deltas),
        "local_A_joint_contracting_rate": sum(1 for a, _b, ab in deltas if a >= 0 and ab < 0) / len(deltas),
        "local_B_joint_contracting_rate": sum(1 for _a, b, ab in deltas if b >= 0 and ab < 0) / len(deltas),
        "max_A_delta_when_AB_contracts": max((a for a, _ab in a_contracting), default=0),
        "max_B_delta_when_AB_contracts": max((b for b, _ab in b_contracting), default=0),
        "min_AB_delta": min((ab for _a, _b, ab in deltas), default=0),
    }


def classify(a_count: int, b_count: int, ab_count: int) -> str:
    a_viable = a_count > 0
    b_viable = b_count > 0
    ab_viable = ab_count > 0
    if not a_viable and not b_viable:
        return "neither_viable"
    if a_viable and not b_viable:
        return "A_only_viable"
    if b_viable and not a_viable:
        return "B_only_viable"
    if a_viable and b_viable and not ab_viable:
        return "pairwise_incompatible"
    joint_ratio = ab_count / max(1, min(a_count, b_count))
    if joint_ratio < 0.25:
        return "pairwise_incompatible_like"
    if joint_ratio < 0.75:
        return "pairwise_degraded"
    return "pairwise_compatible"
