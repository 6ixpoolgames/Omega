from __future__ import annotations

import random
from statistics import mean

from omega.val0_g.metrics import geometry_metrics

from .coupled_grammar import JointState, JointWorld, apply_joint_action, joint_signature, valid_joint_actions


def joint_metrics(
    joint: JointWorld,
    max_states_per_depth: int,
    rollout_samples: int,
    seed: int,
) -> dict[str, float | int | str]:
    rng = random.Random(seed)
    single_A = geometry_metrics(joint.world_A, max_states_per_depth, rollout_samples, 0, seed + 11, "full")
    single_B = geometry_metrics(joint.world_B, max_states_per_depth, rollout_samples, 0, seed + 12, "full")
    states_by_depth = reachable_joint_states_by_depth(joint, (4, 8, 16), max_states_per_depth, rng)
    joint_masses = {depth: len(states_by_depth.get(depth, ())) for depth in (4, 8, 16)}
    field_survival = _field_survival_from_joint(states_by_depth)
    terminal = joint_terminal_probabilities(joint, rollout_samples, (16,), random.Random(seed + 20_000))
    a_single = float(single_A["descendant_mass_d16"])
    b_single = float(single_B["descendant_mass_d16"])
    a_coupled = float(field_survival["A_coupled_survival_d16"])
    b_coupled = float(field_survival["B_coupled_survival_d16"])
    joint_survival = float(joint_masses[16])
    a_filter_raw = a_coupled / max(1.0, a_single)
    b_filter_raw = b_coupled / max(1.0, b_single)
    joint_filter_raw = joint_survival / max(1.0, min(a_single, b_single))
    a_filter = min(1.0, a_filter_raw)
    b_filter = min(1.0, b_filter_raw)
    joint_filter = min(1.0, joint_filter_raw)
    compatibility = min(1.0, joint_filter / max(0.001, min(a_filter, b_filter)))
    row: dict[str, float | int | str] = {
        "A_single_survival_d16": a_single,
        "B_single_survival_d16": b_single,
        "joint_survival_d16": joint_survival,
        **field_survival,
        "A_single_P_terminal_d16": single_A["P_terminal_d16"],
        "B_single_P_terminal_d16": single_B["P_terminal_d16"],
        "joint_P_terminal_d16": terminal["joint_P_terminal_d16"],
        "A_coupled_P_terminal_d16": terminal["A_coupled_P_terminal_d16"],
        "B_coupled_P_terminal_d16": terminal["B_coupled_P_terminal_d16"],
        "A_single_cap_hit_d16": single_A["cap_hit_d16"],
        "B_single_cap_hit_d16": single_B["cap_hit_d16"],
        "joint_cap_hit_d16": int(joint_survival >= max_states_per_depth),
        "A_coupled_cap_hit_d16": int(a_coupled >= max_states_per_depth),
        "B_coupled_cap_hit_d16": int(b_coupled >= max_states_per_depth),
        "A_filter_ratio": a_filter,
        "B_filter_ratio": b_filter,
        "joint_filter_ratio": joint_filter,
        "A_filter_ratio_raw": a_filter_raw,
        "B_filter_ratio_raw": b_filter_raw,
        "joint_filter_ratio_raw": joint_filter_raw,
        "compatibility_ratio": compatibility,
        "local_global_divergence_A": a_filter - joint_filter,
        "local_global_divergence_B": b_filter - joint_filter,
        "exclusion_ratio_A": a_filter - b_filter,
        "exclusion_ratio_B": b_filter - a_filter,
    }
    row["neutral_bin"] = classify_compatibility(row)
    row["interpretive_label_optional"] = interpretive_label(row["neutral_bin"])
    return row


def reachable_joint_states_by_depth(
    joint: JointWorld,
    depths: tuple[int, ...],
    max_states_per_depth: int,
    rng: random.Random,
) -> dict[int, tuple[JointState, ...]]:
    max_depth = max(depths)
    states_by_depth: dict[int, list[JointState]] = {0: [joint.initial_state]}
    for depth in range(1, max_depth + 1):
        previous = list(states_by_depth.get(depth - 1, []))
        rng.shuffle(previous)
        next_states: list[JointState] = []
        signatures: set[tuple[object, ...]] = set()
        for state in previous:
            actions = list(valid_joint_actions(joint, state))
            rng.shuffle(actions)
            for action in actions:
                try:
                    next_state = apply_joint_action(joint, state, action)
                except ValueError:
                    continue
                signature = joint_signature(next_state)
                if signature in signatures:
                    continue
                signatures.add(signature)
                next_states.append(next_state)
                if len(next_states) >= max_states_per_depth:
                    break
            if len(next_states) >= max_states_per_depth:
                break
        states_by_depth[depth] = next_states
    return {depth: tuple(states_by_depth.get(depth, [])) for depth in depths}


def joint_terminal_probabilities(
    joint: JointWorld,
    rollout_samples: int,
    depths: tuple[int, ...],
    rng: random.Random,
) -> dict[str, float]:
    joint_terminal = {depth: 0 for depth in depths}
    a_terminal = {depth: 0 for depth in depths}
    b_terminal = {depth: 0 for depth in depths}
    for _ in range(rollout_samples):
        state = joint.initial_state
        seen_joint_terminal = False
        seen_a_terminal = False
        seen_b_terminal = False
        for depth in range(1, max(depths) + 1):
            actions = valid_joint_actions(joint, state)
            if not actions:
                if not seen_joint_terminal:
                    for target_depth in depths:
                        if depth <= target_depth:
                            joint_terminal[target_depth] += 1
                    seen_joint_terminal = True
                break
            state = apply_joint_action(joint, state, rng.choice(actions))
            if not valid_joint_actions(joint, state) and not seen_joint_terminal:
                for target_depth in depths:
                    if depth <= target_depth:
                        joint_terminal[target_depth] += 1
                seen_joint_terminal = True
            if not seen_a_terminal and not state.state_A.enabled - state.state_A.disabled - state.state_A.completed:
                for target_depth in depths:
                    if depth <= target_depth:
                        a_terminal[target_depth] += 1
                seen_a_terminal = True
            if not seen_b_terminal and not state.state_B.enabled - state.state_B.disabled - state.state_B.completed:
                for target_depth in depths:
                    if depth <= target_depth:
                        b_terminal[target_depth] += 1
                seen_b_terminal = True
    depth = max(depths)
    return {
        f"joint_P_terminal_d{depth}": joint_terminal[depth] / max(1, rollout_samples),
        f"A_coupled_P_terminal_d{depth}": a_terminal[depth] / max(1, rollout_samples),
        f"B_coupled_P_terminal_d{depth}": b_terminal[depth] / max(1, rollout_samples),
    }


def classify_compatibility(row: dict[str, float | int | str]) -> str:
    a_filter = float(row["A_filter_ratio"])
    b_filter = float(row["B_filter_ratio"])
    joint_filter = float(row["joint_filter_ratio"])
    joint_terminal = float(row["joint_P_terminal_d16"])
    cap = max(float(row["joint_cap_hit_d16"]), float(row["A_coupled_cap_hit_d16"]), float(row["B_coupled_cap_hit_d16"]))
    if cap and joint_filter >= 0.95:
        return "mixed_or_censored_bin"
    if min(a_filter, b_filter, joint_filter) >= 0.65 and joint_terminal < 0.25:
        return "joint_viable_bin"
    if a_filter >= 0.55 and b_filter < 0.35 and joint_filter < 0.45:
        return "A_dominant_collapse_bin"
    if b_filter >= 0.55 and a_filter < 0.35 and joint_filter < 0.45:
        return "B_dominant_collapse_bin"
    if a_filter < 0.35 and b_filter < 0.35 and joint_filter < 0.35:
        return "mutual_collapse_bin"
    if abs(a_filter - 1.0) < 0.20 and abs(b_filter - 1.0) < 0.20 and joint_filter > 0.70:
        return "uncoupled_parallel_bin"
    return "mixed_or_censored_bin"


def interpretive_label(neutral_bin: object) -> str:
    return {
        "joint_viable_bin": "joint_viable_like",
        "A_dominant_collapse_bin": "pseudo_omega_like_A",
        "B_dominant_collapse_bin": "pseudo_omega_like_B",
        "mutual_collapse_bin": "mutual_collapse_like",
        "uncoupled_parallel_bin": "uncoupled_parallel_like",
        "mixed_or_censored_bin": "mixed_or_censored",
    }.get(str(neutral_bin), "mixed_or_censored")


def _field_survival_from_joint(states_by_depth: dict[int, tuple[JointState, ...]]) -> dict[str, int]:
    states = states_by_depth.get(16, ())
    a_signatures = {(state.state_A.enabled, state.state_A.disabled, state.state_A.completed, state.state_A.irreversible, state.state_A.capacity) for state in states}
    b_signatures = {(state.state_B.enabled, state.state_B.disabled, state.state_B.completed, state.state_B.irreversible, state.state_B.capacity) for state in states}
    return {
        "A_coupled_survival_d16": len(a_signatures),
        "B_coupled_survival_d16": len(b_signatures),
    }


def mean_row(labels: dict[str, object], rows: list[dict[str, object]]) -> dict[str, object]:
    numeric_keys = [
        "A_filter_ratio",
        "B_filter_ratio",
        "joint_filter_ratio",
        "compatibility_ratio",
        "local_global_divergence_A",
        "local_global_divergence_B",
        "joint_cap_hit_d16",
        "A_single_cap_hit_d16",
        "B_single_cap_hit_d16",
        "joint_P_terminal_d16",
    ]
    output = {**labels, "n": len(rows)}
    for key in numeric_keys:
        output[f"mean_{key}"] = mean(float(row[key]) for row in rows) if rows else 0.0
    return output
