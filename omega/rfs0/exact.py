from __future__ import annotations

from collections import deque
from functools import lru_cache

from .substrate import RFSSystem, State, perturb

PERTURBATIONS = ("capacity_loss", "integrity_damage", "option_loss", "repair_loss")


def reverse_edges(system: RFSSystem) -> dict[State, tuple[State, ...]]:
    rev: dict[State, list[State]] = {state: [] for state in system.states}
    for source, targets in system.edges.items():
        for target in targets:
            rev[target].append(source)
    return {state: tuple(items) for state, items in rev.items()}


def reachable(system: RFSSystem, start: State, horizon: int) -> frozenset[State]:
    seen = {start}
    frontier = {start}
    for _ in range(horizon):
        next_frontier: set[State] = set()
        for state in frontier:
            next_frontier.update(system.edges[state])
        next_frontier -= seen
        if not next_frontier:
            break
        seen.update(next_frontier)
        frontier = next_frontier
    return frozenset(seen)


def viability_kernel(system: RFSSystem, admissible: set[State], horizon: int) -> set[State]:
    viable = set(admissible)
    for _ in range(horizon):
        viable = {state for state in viable if any(target in viable for target in system.edges[state])}
        if not viable:
            break
    return viable


def capture_basin(system: RFSSystem, target: set[State], horizon: int) -> set[State]:
    rev = reverse_edges(system)
    captured = set(target)
    frontier = set(target)
    for _ in range(horizon):
        next_frontier = {source for state in frontier for source in rev[state] if source not in captured}
        if not next_frontier:
            break
        captured.update(next_frontier)
        frontier = next_frontier
    return captured


def shortest_capture_distances(system: RFSSystem, target: set[State], horizon: int) -> dict[State, int]:
    rev = reverse_edges(system)
    dist = {state: 0 for state in target}
    queue = deque(target)
    while queue:
        state = queue.popleft()
        if dist[state] >= horizon:
            continue
        for source in rev[state]:
            if source not in dist:
                dist[source] = dist[state] + 1
                queue.append(source)
    return dist


def filter_sets(system: RFSSystem) -> dict[str, set[State]]:
    k0 = {state for state in system.states if system.edges[state]}

    @lru_cache(maxsize=None)
    def reach_count(state: State) -> int:
        return len(reachable(system, state, 4))

    min_reach = int(system.constraint_params.get("min_reach_h4", 5))
    k1 = {state for state in k0 if reach_count(state) >= min_reach}
    capture_k1 = capture_basin(system, k1, 4)
    if system.control_type == "no_perturbation_control":
        k2 = set(k1)
    else:
        k2 = {state for state in k1 if _perturb_recovery_rate(state, capture_k1) >= 0.5}
    k3 = {state for state in k2 if state[2] >= int(system.constraint_params.get("min_repair_strict", 1))}
    k4 = {
        state
        for state in k3
        if state[4] == 0
        and state[0] >= int(system.constraint_params.get("min_capacity_strict", 1))
        and state[1] >= int(system.constraint_params.get("min_integrity_strict", 2))
        and state[3] >= int(system.constraint_params.get("min_option_strict", 1))
    }
    if system.control_type == "shuffled_admissibility_control":
        k4 = _deterministic_shuffle_like_size(system, k4)
    return {"K0": k0, "K1": k1, "K2": k2, "K3": k3, "K4": k4, "K_strict": set(k4)}


def contraction_metrics(system: RFSSystem, strict_kernel: set[State], horizons: tuple[int, ...]) -> dict[str, float | int]:
    output: dict[str, float | int] = {}
    strict_edges = [(s, t) for s, targets in system.edges.items() if s in strict_kernel for t in targets if t in strict_kernel]
    output["strict_preserving_transition_count"] = len(strict_edges)
    for horizon in horizons:
        strict_reach_cache: dict[State, int] = {}

        def strict_reach_size(state: State) -> int:
            if state not in strict_reach_cache:
                strict_reach_cache[state] = len(reachable(system, state, horizon) & strict_kernel)
            return strict_reach_cache[state]

        ratios = [strict_reach_size(target) / max(1, strict_reach_size(source)) for source, target in strict_edges]
        output[f"mean_contraction_ratio_H{horizon}"] = sum(ratios) / len(ratios) if ratios else 0.0
        output[f"contraction_event_rate_H{horizon}"] = sum(1 for ratio in ratios if ratio < 0.75) / len(ratios) if ratios else 0.0
        output[f"expansion_event_rate_H{horizon}"] = sum(1 for ratio in ratios if ratio > 1.10) / len(ratios) if ratios else 0.0
    return output


def recovery_metrics(system: RFSSystem, source_sets: dict[str, set[State]], capture: set[State], hr4_distances: dict[State, int]) -> dict[str, float | int]:
    output: dict[str, float | int] = {}
    strict_source = source_sets["K_strict"]
    loose_source = source_sets["K0"]
    for kind in PERTURBATIONS:
        output[f"recovery_rate_K_strict_{kind}"] = _source_recovery_rate(strict_source, capture, kind)
        output[f"recovery_rate_K0_{kind}"] = _source_recovery_rate(loose_source, capture, kind)
        distances = [hr4_distances[perturb(state, kind)] for state in strict_source if perturb(state, kind) in hr4_distances]
        output[f"mean_recovery_horizon_K_strict_{kind}"] = sum(distances) / len(distances) if distances else 0.0
        output[f"failed_recovery_count_K_strict_{kind}"] = len(strict_source) - len(distances)
    return output


def _source_recovery_rate(source: set[State], capture: set[State], kind: str) -> float:
    if not source:
        return 0.0
    return sum(1 for state in source if perturb(state, kind) in capture) / len(source)


def _perturb_recovery_rate(state: State, capture: set[State]) -> float:
    return sum(1 for kind in PERTURBATIONS if perturb(state, kind) in capture) / len(PERTURBATIONS)


def _deterministic_shuffle_like_size(system: RFSSystem, original: set[State]) -> set[State]:
    target_size = len(original)
    ordered = sorted(system.states, key=lambda state: ((state[0] * 31 + state[1] * 17 + state[2] * 13 + state[3] * 7 + state[4] * 5 + state[5] * 3 + system.seed) % 997, state))
    return set(ordered[:target_size])
