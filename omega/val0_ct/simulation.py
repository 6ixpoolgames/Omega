from __future__ import annotations

from dataclasses import asdict
from statistics import mean

from .algebra import TaskAlgebra, algebra_diagnostics, apply_task, family_counts
from .policies import choose_task
from .reachability import r0, r1


def simulate_policy(
    algebra: TaskAlgebra,
    policy: str,
    h: int,
    H: int,
    T: int,
    sample_size: int,
    seed: int,
    max_paths: int,
    store_steps: bool = False,
) -> dict[str, object]:
    state = algebra.initial_state
    initial_r0_result = r0(algebra, state, H, max_paths=max_paths)
    r0_initial = initial_r0_result.count
    lock_initial = family_counts(algebra, state.enabled).get("lock_in", 0)
    steps: list[dict[str, object]] = []
    same_choice_values: list[float] = []
    score_gap_values: list[float] = []
    candidate_variance_values: list[float] = []
    candidate_r1_fraction_values: list[float] = []
    obstruction_values: list[float] = []
    for t in range(T):
        task_id, info = choose_task(
            algebra,
            state,
            policy,
            h=h,
            H=H,
            seed=seed * 1009 + t,
            sample_size=sample_size,
            max_paths=max_paths,
        )
        if task_id is None:
            if store_steps:
                steps.append({"t": t, "chosen_task": None, **info})
            break
        same_choice_values.append(float(info.get("R1_R0lookahead_same_choice", 0.0)))
        score_gap_values.append(float(info.get("R1_R0lookahead_score_gap", 0.0)))
        candidate_variance_values.append(float(info.get("candidate_future_R0_variance", 0.0)))
        candidate_r1_fraction_values.append(float(info.get("candidate_R1_fraction", 0.0)))
        if policy == "R1":
            obstruction_values.append(float(info.get("R1_chosen_obstruction_count", 0.0)))
        elif policy == "R0_lookahead":
            obstruction_values.append(float(info.get("R0_lookahead_chosen_obstruction_count", 0.0)))
        state = apply_task(algebra, state, task_id)
        if store_steps:
            steps.append({"t": t, "chosen_task": task_id, "chosen_family": algebra.task(task_id).family, **info})
    final_r0_result = r0(algebra, state, H, max_paths=max_paths)
    r0_final = final_r0_result.count
    lock_final = family_counts(algebra, state.enabled | state.completed).get("lock_in", 0)
    initial_reachable_families = family_counts(algebra, initial_r0_result.reachable_tasks)
    final_reachable_families = family_counts(algebra, final_r0_result.reachable_tasks)
    p_initial = initial_reachable_families.get("lock_in", 0)
    p_final = final_reachable_families.get("lock_in", 0)
    global_lhr = r0_final / max(1, r0_initial)
    local_lhr = lock_final / max(1, lock_initial) if lock_initial else 0.0
    result = {
        "policy": policy,
        "r0_initial": r0_initial,
        "r0_final": r0_final,
        "global_R0_initial": r0_initial,
        "global_R0_final": r0_final,
        "local_R0_initial": p_initial,
        "local_R0_final": p_final,
        "P_family_reachability_initial": p_initial,
        "P_family_reachability_final": p_final,
        "P_family_reachability_delta": p_final - p_initial,
        "global_lhr": global_lhr,
        "local_lhr": local_lhr,
        "local_global_divergence": local_lhr - global_lhr,
        "pseudo_omega_flag": local_lhr > 1.0 and global_lhr < 0.8,
        "R1_R0lookahead_same_choice_rate": mean(same_choice_values) if same_choice_values else 0.0,
        "R1_R0lookahead_score_gap": mean(score_gap_values) if score_gap_values else 0.0,
        "candidate_future_R0_variance_mean": mean(candidate_variance_values) if candidate_variance_values else 0.0,
        "candidate_R1_fraction_mean": mean(candidate_r1_fraction_values) if candidate_r1_fraction_values else 0.0,
        "chosen_path_obstruction_mean": mean(obstruction_values) if obstruction_values else 0.0,
        "completed_count": len(state.completed),
        "obstructed_count": len(state.obstructed),
        "final_enabled_count": len(state.enabled),
    }
    if store_steps:
        result["steps"] = steps
    return result


def run_condition(
    algebra: TaskAlgebra,
    h: int,
    H: int,
    T: int,
    policy: str,
    sample_size: int,
    seed: int,
    max_paths: int,
    store_steps: bool = False,
) -> dict[str, object]:
    initial_r0 = r0(algebra, algebra.initial_state, H, max_paths=max_paths)
    initial_r1 = r1(algebra, algebra.initial_state, h, H, sample_size, seed=seed, max_paths=max_paths)
    sim = simulate_policy(algebra, policy, h, H, T, sample_size, seed, max_paths=max_paths, store_steps=store_steps)
    diagnostics = algebra_diagnostics(algebra)
    row = {
        "family": algebra.family,
        "seed": algebra.seed,
        "h": h,
        "H": H,
        "T": T,
        "policy": policy,
        **diagnostics,
        "initial_r0_count": initial_r0.count,
        "initial_r0_truncated": initial_r0.truncated,
        "initial_r1": {k: v for k, v in asdict(initial_r1).items() if k != "future_r0_values"},
        **{k: v for k, v in sim.items() if k != "steps"},
    }
    if "steps" in sim:
        row["steps"] = sim["steps"]
    return row
