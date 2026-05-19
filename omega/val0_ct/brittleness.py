from __future__ import annotations

import random
from dataclasses import dataclass
from statistics import mean, pvariance

from .algebra import AlgebraState, TaskAlgebra, apply_path
from .policies import evaluate_decision
from .reachability import candidate_paths, r0


@dataclass(frozen=True)
class CandidateBrittleness:
    path: tuple[int, ...]
    first_task: int
    base_r0: int
    mean_depth: float
    structuredness: float
    stress_retention: float
    perturbation_sensitivity: float
    brittleness: float


def reachable_depth_mean(
    algebra: TaskAlgebra,
    state: AlgebraState,
    horizon: int,
    max_paths: int,
) -> float:
    paths = candidate_paths(algebra, state, horizon, max_paths=max_paths)
    if not paths:
        return 0.0
    depths: dict[int, int] = {}
    for path in paths:
        for depth, task_id in enumerate(path, start=1):
            depths[task_id] = min(depths.get(task_id, depth), depth)
    return mean(depths.values()) if depths else 0.0


def score_candidate_brittleness(
    algebra: TaskAlgebra,
    state: AlgebraState,
    path: tuple[int, ...],
    H: int,
    stress_samples: int,
    seed: int,
    max_paths: int,
    horizon_delta: int = 4,
) -> CandidateBrittleness:
    rng = random.Random(seed)
    path_state = apply_path(algebra, state, path)
    base = r0(algebra, path_state, H, max_paths=max_paths)
    base_r0 = base.count
    mean_depth = reachable_depth_mean(algebra, path_state, H, max_paths=max_paths)
    initial_density = len(algebra.initial_state.enabled) / max(1, algebra.num_tasks)
    density_penalty = max(0.0, 1.0 - (initial_density / 0.35))
    structuredness = (float(base_r0) / max(1, algebra.num_tasks)) * mean_depth * density_penalty
    retentions: list[float] = []

    reachable = list(base.reachable_tasks)
    enabled = list(path_state.enabled - path_state.completed - path_state.obstructed)
    for _ in range(stress_samples):
        if enabled:
            dropped = rng.choice(enabled)
            stressed = AlgebraState(
                enabled=frozenset(task for task in path_state.enabled if task != dropped),
                obstructed=path_state.obstructed,
                completed=path_state.completed,
                time=path_state.time,
            )
            retentions.append(r0(algebra, stressed, H, max_paths=max_paths).count / max(1, base_r0))
        if reachable:
            obstructed = rng.choice(reachable)
            stressed = AlgebraState(
                enabled=path_state.enabled,
                obstructed=frozenset(set(path_state.obstructed) | {obstructed}),
                completed=path_state.completed,
                time=path_state.time,
            )
            retentions.append(r0(algebra, stressed, H, max_paths=max_paths).count / max(1, base_r0))

    extended_r0 = r0(algebra, path_state, H + horizon_delta, max_paths=max_paths).count
    # This treats a large increase under horizon extension as evidence that the
    # original H-window was shallow relative to nearby continuation structure.
    retentions.append(base_r0 / max(1, extended_r0))

    stress_retention = max(0.0, min(1.0, mean(retentions))) if retentions else 1.0
    sensitivity = 1.0 - stress_retention
    brittleness = structuredness * sensitivity
    return CandidateBrittleness(
        path=path,
        first_task=path[0] if path else -1,
        base_r0=base_r0,
        mean_depth=mean_depth,
        structuredness=structuredness,
        stress_retention=stress_retention,
        perturbation_sensitivity=sensitivity,
        brittleness=brittleness,
    )


def brittleness_sidecar(
    algebra: TaskAlgebra,
    state: AlgebraState,
    h: int,
    H: int,
    candidate_sample_size: int,
    stress_samples: int,
    seed: int,
    max_paths: int,
) -> dict[str, object]:
    rng = random.Random(seed)
    paths = list(candidate_paths(algebra, state, h, max_paths=max_paths, rng=random.Random(seed)))
    if len(paths) > candidate_sample_size:
        paths = rng.sample(paths, candidate_sample_size)
    if not paths:
        return {
            "brittleness_candidate_sample_size": 0,
            "brittleness_stress_sample_size": stress_samples,
            "brittleness_stress_types": "enabled_drop,obstruction_add,horizon_extension",
            "candidate_structuredness_mean": 0.0,
            "candidate_structuredness_max": 0.0,
            "candidate_stress_retention_mean": 0.0,
            "candidate_perturbation_sensitivity_mean": 0.0,
            "candidate_brittleness_mean": 0.0,
            "candidate_brittleness_max": 0.0,
            "candidate_brittleness_variance": 0.0,
            "R0lookahead_chosen_brittleness": 0.0,
            "R1_chosen_brittleness": 0.0,
            "chosen_brittleness_gap": 0.0,
        }
    scores = [
        score_candidate_brittleness(
            algebra,
            state,
            path,
            H=H,
            stress_samples=stress_samples,
            seed=seed * 1009 + idx,
            max_paths=max_paths,
        )
        for idx, path in enumerate(paths)
    ]
    by_first: dict[int, list[CandidateBrittleness]] = {}
    for score in scores:
        by_first.setdefault(score.first_task, []).append(score)

    def mean_brittleness(task_id: int) -> float:
        values = by_first.get(task_id, [])
        return mean(score.brittleness for score in values) if values else 0.0

    decision = evaluate_decision(
        algebra,
        state,
        h=h,
        H=H,
        seed=seed,
        sample_size=candidate_sample_size,
        max_paths=max_paths,
    )
    decision.pop("_paths", None)
    r0_task = int(decision["R0_lookahead_chosen_task"])
    r1_task = int(decision["R1_chosen_task"])
    brittleness_values = [score.brittleness for score in scores]
    structuredness_values = [score.structuredness for score in scores]
    retention_values = [score.stress_retention for score in scores]
    sensitivity_values = [score.perturbation_sensitivity for score in scores]
    r0_brittleness = mean_brittleness(r0_task)
    r1_brittleness = mean_brittleness(r1_task)
    return {
        "brittleness_candidate_sample_size": len(scores),
        "brittleness_stress_sample_size": stress_samples,
        "brittleness_stress_types": "enabled_drop,obstruction_add,horizon_extension",
        "candidate_structuredness_mean": mean(structuredness_values),
        "candidate_structuredness_max": max(structuredness_values),
        "candidate_stress_retention_mean": mean(retention_values),
        "candidate_perturbation_sensitivity_mean": mean(sensitivity_values),
        "candidate_brittleness_mean": mean(brittleness_values),
        "candidate_brittleness_max": max(brittleness_values),
        "candidate_brittleness_variance": pvariance(brittleness_values) if len(brittleness_values) > 1 else 0.0,
        "R0lookahead_chosen_brittleness": r0_brittleness,
        "R1_chosen_brittleness": r1_brittleness,
        "chosen_brittleness_gap": r0_brittleness - r1_brittleness,
    }
