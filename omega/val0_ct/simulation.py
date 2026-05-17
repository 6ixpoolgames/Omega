from __future__ import annotations

from dataclasses import asdict

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
) -> dict[str, object]:
    state = algebra.initial_state
    r0_initial = r0(algebra, state, H, max_paths=max_paths).count
    lock_initial = family_counts(algebra, state.enabled).get("lock_in", 0)
    steps: list[dict[str, object]] = []
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
            steps.append({"t": t, "chosen_task": None, **info})
            break
        state = apply_task(algebra, state, task_id)
        steps.append({"t": t, "chosen_task": task_id, "chosen_family": algebra.task(task_id).family, **info})
    r0_final = r0(algebra, state, H, max_paths=max_paths).count
    lock_final = family_counts(algebra, state.enabled | state.completed).get("lock_in", 0)
    global_lhr = r0_final / max(1, r0_initial)
    local_lhr = lock_final / max(1, lock_initial) if lock_initial else 0.0
    return {
        "policy": policy,
        "r0_initial": r0_initial,
        "r0_final": r0_final,
        "global_lhr": global_lhr,
        "local_lhr": local_lhr,
        "local_global_divergence": local_lhr - global_lhr,
        "pseudo_omega_flag": local_lhr > 1.0 and global_lhr < 0.8,
        "completed_count": len(state.completed),
        "obstructed_count": len(state.obstructed),
        "final_enabled_count": len(state.enabled),
        "steps": steps,
    }


def run_condition(
    algebra: TaskAlgebra,
    h: int,
    H: int,
    T: int,
    policy: str,
    sample_size: int,
    seed: int,
    max_paths: int,
) -> dict[str, object]:
    initial_r0 = r0(algebra, algebra.initial_state, H, max_paths=max_paths)
    initial_r1 = r1(algebra, algebra.initial_state, h, H, sample_size, seed=seed, max_paths=max_paths)
    sim = simulate_policy(algebra, policy, h, H, T, sample_size, seed, max_paths=max_paths)
    diagnostics = algebra_diagnostics(algebra)
    return {
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
        "steps": sim["steps"],
    }
