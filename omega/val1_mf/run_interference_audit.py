from __future__ import annotations

import argparse
import csv
import json
import math
import random
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from statistics import mean

from omega.val0_g.grammar import apply_task, valid_tasks

from .coupled_grammar import CrossEffects, JointState, JointWorld, apply_joint_action, cross_edge_counts, generate_joint_world, valid_joint_actions
from .metrics import reachable_joint_states_by_depth

MODES = (
    "A_alone",
    "B_alone",
    "uncoupled_parallel",
    "full_coupling",
    "cross_enable_only",
    "cross_obstruct_only",
    "cross_restore_only",
    "cross_commit_only",
    "shared_capacity_only",
)

JOINT_MODES = tuple(mode for mode in MODES if mode not in {"A_alone", "B_alone"})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VAL1-MF sampled interference audit.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--pairs", type=int, default=100)
    parser.add_argument("--num-tasks", type=int, default=64)
    parser.add_argument("--rollout-samples", type=int, default=256)
    parser.add_argument("--horizon", type=int, default=16)
    parser.add_argument("--max-states-per-depth", type=int, default=1024)
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--max-runtime-seconds", type=int, default=1800)
    return parser.parse_args()


def _run_one(job: dict[str, object]) -> dict[str, object]:
    started = time.perf_counter()
    seed_pair = int(job["seed_pair"])
    joint = generate_joint_world(seed_pair, int(job["num_tasks"]))
    horizon = int(job["horizon"])
    rollout_samples = int(job["rollout_samples"])
    max_states = int(job["max_states_per_depth"])
    mode_results = {
        mode: _mode_rollout_metrics(joint, mode, horizon, rollout_samples, random.Random(seed_pair * 10_003 + index))
        for index, mode in enumerate(MODES)
    }
    diagnostic = _diagnostic_enumeration(joint, max_states, random.Random(seed_pair + 91_777))
    deltas = _interference_deltas(mode_results)
    neutral_bin = _classify_interference(deltas, mode_results, diagnostic, rollout_samples)
    row: dict[str, object] = {
        "seed_pair": joint.seed_pair,
        "seed_A": joint.world_A.seed,
        "seed_B": joint.world_B.seed,
        "coupling_parameter_json": json.dumps(joint.params, sort_keys=True),
        "num_tasks_A": joint.world_A.num_tasks,
        "num_tasks_B": joint.world_B.num_tasks,
        "rollout_samples": rollout_samples,
        "horizon": horizon,
        "max_states_per_depth": max_states,
        "mode_results_json": json.dumps(mode_results, sort_keys=True),
        "job_elapsed_seconds": time.perf_counter() - started,
        **cross_edge_counts(joint),
        **_flatten_mode_results(mode_results, horizon),
        **deltas,
        **diagnostic,
        "neutral_bin": neutral_bin,
        "interpretive_label_optional": _interpretive_label(neutral_bin),
    }
    row["cap_hit_any"] = int(max(float(row.get("cap_hit_joint_uncoupled_d16", 0)), float(row.get("cap_hit_joint_full_d16", 0))) > 0)
    row["low_confidence_flag"] = int(_low_confidence(row, rollout_samples))
    return row


def _mode_rollout_metrics(joint: JointWorld, mode: str, horizon: int, samples: int, rng: random.Random) -> dict[str, float | int]:
    if mode == "A_alone":
        return _single_rollout_metrics(joint, "A", horizon, samples, rng)
    if mode == "B_alone":
        return _single_rollout_metrics(joint, "B", horizon, samples, rng)
    masked = _masked_joint(joint, mode)
    counts = {
        "A_alive": 0,
        "B_alive": 0,
        "joint_alive": 0,
        "A_terminal": 0,
        "B_terminal": 0,
        "joint_terminal": 0,
        "A_valid_actions": 0,
        "B_valid_actions": 0,
        "joint_valid_actions": 0,
    }
    for _ in range(samples):
        state = masked.initial_state
        joint_terminal = False
        for _step in range(horizon):
            actions = valid_joint_actions(masked, state)
            if not actions:
                joint_terminal = True
                break
            state = apply_joint_action(masked, state, rng.choice(actions))
        a_valid = len(valid_tasks(masked.world_A, state.state_A))
        b_valid = len(valid_tasks(masked.world_B, state.state_B))
        joint_valid = len(valid_joint_actions(masked, state))
        a_alive = a_valid > 0
        b_alive = b_valid > 0
        counts["A_alive"] += int(a_alive)
        counts["B_alive"] += int(b_alive)
        counts["joint_alive"] += int(a_alive and b_alive and joint_valid > 0 and not joint_terminal)
        counts["A_terminal"] += int(not a_alive)
        counts["B_terminal"] += int(not b_alive)
        counts["joint_terminal"] += int(joint_terminal or joint_valid == 0)
        counts["A_valid_actions"] += a_valid
        counts["B_valid_actions"] += b_valid
        counts["joint_valid_actions"] += joint_valid
    return _probability_result(counts, samples)


def _single_rollout_metrics(joint: JointWorld, side: str, horizon: int, samples: int, rng: random.Random) -> dict[str, float | int]:
    world = joint.world_A if side == "A" else joint.world_B
    own_alive_key = "A_alive" if side == "A" else "B_alive"
    other_alive_key = "B_alive" if side == "A" else "A_alive"
    own_terminal_key = "A_terminal" if side == "A" else "B_terminal"
    other_terminal_key = "B_terminal" if side == "A" else "A_terminal"
    own_valid_key = "A_valid_actions" if side == "A" else "B_valid_actions"
    other_valid_key = "B_valid_actions" if side == "A" else "A_valid_actions"
    counts = {
        "A_alive": 0,
        "B_alive": 0,
        "joint_alive": 0,
        "A_terminal": 0,
        "B_terminal": 0,
        "joint_terminal": 0,
        "A_valid_actions": 0,
        "B_valid_actions": 0,
        "joint_valid_actions": 0,
    }
    for _ in range(samples):
        state = world.initial_state
        terminal = False
        for _step in range(horizon):
            actions = valid_tasks(world, state)
            if not actions:
                terminal = True
                break
            state = apply_task(world, state, rng.choice(actions))
        own_valid = len(valid_tasks(world, state))
        own_alive = own_valid > 0 and not terminal
        counts[own_alive_key] += int(own_alive)
        counts[other_alive_key] += 0
        counts["joint_alive"] += 0
        counts[own_terminal_key] += int(not own_alive)
        counts[other_terminal_key] += 1
        counts["joint_terminal"] += 1
        counts[own_valid_key] += own_valid
        counts[other_valid_key] += 0
        counts["joint_valid_actions"] += 0
    return _probability_result(counts, samples)


def _probability_result(counts: dict[str, int], samples: int) -> dict[str, float | int]:
    result: dict[str, float | int] = {"sample_count": samples}
    for key in ("A_alive", "B_alive", "joint_alive", "A_terminal", "B_terminal", "joint_terminal"):
        p = counts[key] / max(1, samples)
        result[key] = p
        result[f"{key}_se"] = math.sqrt(p * (1.0 - p) / max(1, samples))
    for key in ("A_valid_actions", "B_valid_actions", "joint_valid_actions"):
        result[f"mean_{key}"] = counts[key] / max(1, samples)
    return result


def _masked_joint(joint: JointWorld, mode: str) -> JointWorld:
    if mode == "full_coupling":
        return joint
    keep_shared = mode in {"full_coupling", "shared_capacity_only"}
    return JointWorld(
        seed_pair=joint.seed_pair,
        world_A=joint.world_A,
        world_B=joint.world_B,
        cross_A_to_B={task_id: _mask_effect(effect, mode) for task_id, effect in joint.cross_A_to_B.items()},
        cross_B_to_A={task_id: _mask_effect(effect, mode) for task_id, effect in joint.cross_B_to_A.items()},
        params={**joint.params, "coupling_mode": mode},
        initial_state=replace(joint.initial_state, shared_capacity=joint.initial_state.shared_capacity if keep_shared else joint.world_A.num_tasks + joint.world_B.num_tasks),
    )


def _mask_effect(effect: CrossEffects, mode: str) -> CrossEffects:
    if mode == "uncoupled_parallel":
        return CrossEffects()
    if mode == "cross_enable_only":
        return CrossEffects(enables=effect.enables)
    if mode == "cross_obstruct_only":
        return CrossEffects(obstructs=effect.obstructs)
    if mode == "cross_restore_only":
        return CrossEffects(restores=effect.restores)
    if mode == "cross_commit_only":
        return CrossEffects(commits=effect.commits)
    if mode == "shared_capacity_only":
        return CrossEffects(shared_capacity_delta=effect.shared_capacity_delta)
    raise ValueError(f"unknown coupling mode: {mode}")


def _diagnostic_enumeration(joint: JointWorld, max_states: int, rng: random.Random) -> dict[str, int]:
    output: dict[str, int] = {}
    for label, mode in (("uncoupled", "uncoupled_parallel"), ("full", "full_coupling")):
        states = reachable_joint_states_by_depth(_masked_joint(joint, mode), (16,), max_states, rng).get(16, ())
        mass = len(states)
        output[f"enumerated_mass_joint_{label}_d16"] = mass
        output[f"cap_hit_joint_{label}_d16"] = int(mass >= max_states)
    return output


def _flatten_mode_results(mode_results: dict[str, dict[str, float | int]], horizon: int) -> dict[str, float | int]:
    aliases = {
        "uncoupled_parallel": "uncoupled",
        "full_coupling": "full",
        "cross_enable_only": "enable_only",
        "cross_obstruct_only": "obstruct_only",
        "cross_restore_only": "restore_only",
        "cross_commit_only": "commit_only",
        "shared_capacity_only": "shared_capacity_only",
        "A_alone": "A_alone",
        "B_alone": "B_alone",
    }
    flat: dict[str, float | int] = {}
    for mode, result in mode_results.items():
        alias = aliases[mode]
        for key, value in result.items():
            if key == "sample_count":
                flat[f"{alias}_sample_count"] = value
            elif key.startswith("mean_"):
                flat[f"{alias}_{key}_d{horizon}"] = value
            else:
                flat[f"{key}_{alias}_d{horizon}"] = value
    return flat


def _interference_deltas(mode_results: dict[str, dict[str, float | int]]) -> dict[str, float]:
    uncoupled = mode_results["uncoupled_parallel"]
    full = mode_results["full_coupling"]
    deltas: dict[str, float] = {
        "constructive_interference_d16": float(full["joint_alive"]) - float(uncoupled["joint_alive"]),
        "destructive_interference_d16": float(uncoupled["joint_alive"]) - float(full["joint_alive"]),
        "A_harm_d16": float(uncoupled["A_alive"]) - float(full["A_alive"]),
        "B_harm_d16": float(uncoupled["B_alive"]) - float(full["B_alive"]),
        "A_help_d16": float(full["A_alive"]) - float(uncoupled["A_alive"]),
        "B_help_d16": float(full["B_alive"]) - float(uncoupled["B_alive"]),
    }
    deltas["A_pseudo_omega_candidate_score"] = (
        max(0.0, float(full["A_alive"]) - float(full["B_alive"]))
        + max(0.0, float(uncoupled["B_alive"]) - float(full["B_alive"]))
        + max(0.0, float(uncoupled["joint_alive"]) - float(full["joint_alive"]))
    )
    deltas["B_pseudo_omega_candidate_score"] = (
        max(0.0, float(full["B_alive"]) - float(full["A_alive"]))
        + max(0.0, float(uncoupled["A_alive"]) - float(full["A_alive"]))
        + max(0.0, float(uncoupled["joint_alive"]) - float(full["joint_alive"]))
    )
    deltas["mutual_support_delta"] = min(float(full["A_alive"]), float(full["B_alive"]), float(full["joint_alive"])) - min(
        float(uncoupled["A_alive"]),
        float(uncoupled["B_alive"]),
        float(uncoupled["joint_alive"]),
    )
    for mode in ("cross_enable_only", "cross_obstruct_only", "cross_restore_only", "cross_commit_only", "shared_capacity_only"):
        alias = mode.replace("cross_", "").replace("_only", "")
        current = mode_results[mode]
        deltas[f"{alias}_joint_delta_d16"] = float(current["joint_alive"]) - float(uncoupled["joint_alive"])
        deltas[f"{alias}_A_delta_d16"] = float(current["A_alive"]) - float(uncoupled["A_alive"])
        deltas[f"{alias}_B_delta_d16"] = float(current["B_alive"]) - float(uncoupled["B_alive"])
    return deltas


def _classify_interference(
    deltas: dict[str, float],
    mode_results: dict[str, dict[str, float | int]],
    diagnostic: dict[str, int],
    samples: int,
) -> str:
    threshold = max(0.05, 2.0 / max(1, math.sqrt(samples)))
    full = mode_results["full_coupling"]
    uncoupled = mode_results["uncoupled_parallel"]
    _ = diagnostic
    if max(float(full["joint_alive_se"]), float(uncoupled["joint_alive_se"])) > 0.08:
        return "censored_or_low_confidence_bin"
    if deltas["A_pseudo_omega_candidate_score"] > 2 * threshold and float(full["A_alive"]) >= 0.50 and deltas["B_harm_d16"] > threshold:
        return "A_local_dominance_bin"
    if deltas["B_pseudo_omega_candidate_score"] > 2 * threshold and float(full["B_alive"]) >= 0.50 and deltas["A_harm_d16"] > threshold:
        return "B_local_dominance_bin"
    if deltas["A_harm_d16"] > threshold and deltas["B_harm_d16"] > threshold:
        return "mutual_collapse_delta_bin"
    if deltas["constructive_interference_d16"] > threshold or deltas["mutual_support_delta"] > threshold:
        return "constructive_delta_bin"
    if deltas["destructive_interference_d16"] > threshold or max(deltas["A_harm_d16"], deltas["B_harm_d16"]) > threshold:
        return "destructive_delta_bin"
    return "no_detectable_interference_bin"


def _interpretive_label(neutral_bin: str) -> str:
    return {
        "constructive_delta_bin": "constructive_interference_like",
        "destructive_delta_bin": "destructive_interference_like",
        "A_local_dominance_bin": "pseudo_omega_like_A_provisional",
        "B_local_dominance_bin": "pseudo_omega_like_B_provisional",
        "mutual_collapse_delta_bin": "mutual_collapse_like",
        "no_detectable_interference_bin": "no_detectable_interference",
        "censored_or_low_confidence_bin": "censored_or_low_confidence",
    }[neutral_bin]


def _low_confidence(row: dict[str, object], samples: int) -> bool:
    _ = samples
    return max(float(row["joint_alive_se_full_d16"]), float(row["joint_alive_se_uncoupled_d16"])) > 0.08


def _jobs(args: argparse.Namespace) -> list[dict[str, object]]:
    return [
        {
            "seed_pair": seed_pair,
            "num_tasks": args.num_tasks,
            "rollout_samples": args.rollout_samples,
            "horizon": args.horizon,
            "max_states_per_depth": args.max_states_per_depth,
        }
        for seed_pair in range(args.pairs)
    ]


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _mean(values: list[object]) -> float:
    return mean(float(value) for value in values) if values else 0.0


def _mean_row(labels: dict[str, object], rows: list[dict[str, object]]) -> dict[str, object]:
    keys = [
        "constructive_interference_d16",
        "destructive_interference_d16",
        "A_harm_d16",
        "B_harm_d16",
        "A_help_d16",
        "B_help_d16",
        "A_pseudo_omega_candidate_score",
        "B_pseudo_omega_candidate_score",
        "mutual_support_delta",
        "A_alive_uncoupled_d16",
        "B_alive_uncoupled_d16",
        "joint_alive_uncoupled_d16",
        "A_alive_full_d16",
        "B_alive_full_d16",
        "joint_alive_full_d16",
        "joint_terminal_full_d16",
        "cap_hit_any",
        "low_confidence_flag",
    ]
    output = {**labels, "n": len(rows)}
    for key in keys:
        output[f"mean_{key}"] = _mean([row[key] for row in rows]) if rows and key in rows[0] else 0.0
    return output


def _group_summary(rows: list[dict[str, object]], key: str, out_key: str | None = None) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    return [_mean_row({out_key or key: value}, items) for value, items in sorted(grouped.items())]


def _mode_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for mode, alias in (
        ("uncoupled_parallel", "uncoupled"),
        ("full_coupling", "full"),
        ("cross_enable_only", "enable_only"),
        ("cross_obstruct_only", "obstruct_only"),
        ("cross_restore_only", "restore_only"),
        ("cross_commit_only", "commit_only"),
        ("shared_capacity_only", "shared_capacity_only"),
    ):
        output.append(
            {
                "mode": mode,
                "n": len(rows),
                "mean_A_alive_d16": _mean([row[f"A_alive_{alias}_d16"] for row in rows]),
                "mean_B_alive_d16": _mean([row[f"B_alive_{alias}_d16"] for row in rows]),
                "mean_joint_alive_d16": _mean([row[f"joint_alive_{alias}_d16"] for row in rows]),
                "mean_joint_terminal_d16": _mean([row[f"joint_terminal_{alias}_d16"] for row in rows]),
                "mean_joint_valid_actions_d16": _mean([row[f"{alias}_mean_joint_valid_actions_d16"] for row in rows]),
            }
        )
    return output


def _ablation_effects(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for key in ("enable", "obstruct", "restore", "commit", "shared_capacity"):
        output.append(
            {
                "ablation": key,
                "n": len(rows),
                "mean_joint_delta_d16": _mean([row[f"{key}_joint_delta_d16"] for row in rows]),
                "mean_A_delta_d16": _mean([row[f"{key}_A_delta_d16"] for row in rows]),
                "mean_B_delta_d16": _mean([row[f"{key}_B_delta_d16"] for row in rows]),
            }
        )
    return output


def _operator_footprint_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for key in (
        "cross_enable_edges_A_to_B",
        "cross_enable_edges_B_to_A",
        "cross_obstruct_edges_A_to_B",
        "cross_obstruct_edges_B_to_A",
        "cross_restore_edges_A_to_B",
        "cross_restore_edges_B_to_A",
        "cross_commit_edges_A_to_B",
        "cross_commit_edges_B_to_A",
    ):
        low = [row for row in rows if float(row[key]) <= _mean([item[key] for item in rows])]
        high = [row for row in rows if float(row[key]) > _mean([item[key] for item in rows])]
        output.append(
            {
                "operator_count": key,
                "n_low_or_equal": len(low),
                "n_high": len(high),
                "mean_constructive_low_or_equal": _mean([row["constructive_interference_d16"] for row in low]),
                "mean_constructive_high": _mean([row["constructive_interference_d16"] for row in high]),
                "mean_destructive_low_or_equal": _mean([row["destructive_interference_d16"] for row in low]),
                "mean_destructive_high": _mean([row["destructive_interference_d16"] for row in high]),
            }
        )
    return output


def _coupling_regime_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for key in ("coupling_density", "cross_effect_balance", "shared_capacity_pressure", "cross_commit_probability", "symmetry"):
        grouped: dict[str, list[dict[str, object]]] = {}
        for row in rows:
            value = json.loads(str(row["coupling_parameter_json"])).get(key, "NA")
            grouped.setdefault(str(value), []).append(row)
        for value, items in sorted(grouped.items()):
            output.append(_mean_row({"parameter": key, "value": value}, items))
    return output


def _write_outputs(out_dir: Path, config: dict[str, object], rows: list[dict[str, object]], errors: list[dict[str, object]]) -> None:
    aggregate = [_mean_row({"scope": "all"}, rows)] if rows else []
    mode_summary = _mode_summary(rows) if rows else []
    interference_bins = _group_summary(rows, "neutral_bin") if rows else []
    ablation_effects = _ablation_effects(rows) if rows else []
    operator_summary = _operator_footprint_summary(rows) if rows else []
    coupling_summary = _coupling_regime_summary(rows) if rows else []
    _write_csv(out_dir / "aggregate.csv", aggregate)
    _write_csv(out_dir / "mode_summary.csv", mode_summary)
    _write_csv(out_dir / "interference_bins.csv", interference_bins)
    _write_csv(out_dir / "ablation_effects.csv", ablation_effects)
    _write_csv(out_dir / "operator_footprint_summary.csv", operator_summary)
    _write_csv(out_dir / "coupling_regime_summary.csv", coupling_summary)
    status = {
        "status": config.get("status", "RUNNING"),
        "rows_completed": len(rows),
        "errors": len(errors),
        "elapsed_seconds": time.perf_counter() - float(config["started_perf_counter"]),
    }
    (out_dir / "status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(out_dir, config, aggregate, mode_summary, interference_bins, ablation_effects, rows, errors)


def _write_summary(
    out_dir: Path,
    config: dict[str, object],
    aggregate: list[dict[str, object]],
    mode_summary: list[dict[str, object]],
    interference_bins: list[dict[str, object]],
    ablation_effects: list[dict[str, object]],
    rows: list[dict[str, object]],
    errors: list[dict[str, object]],
) -> None:
    lines = [
        "# VAL1-MF Interference Audit",
        "",
        "Counterfactual sampled audit. Neutral bins are primary; interpretive labels are provisional.",
        "",
        "## Config",
        "",
        "```json",
        json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True),
        "```",
        "",
        "## Aggregate",
        "",
        "| scope | n | constructive | destructive | A harm | B harm | mutual support | cap any | low confidence |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in aggregate:
        lines.append(
            "| {scope} | {n} | {con:.3f} | {des:.3f} | {ah:.3f} | {bh:.3f} | {ms:.3f} | {cap:.3f} | {lc:.3f} |".format(
                scope=row["scope"],
                n=row["n"],
                con=float(row["mean_constructive_interference_d16"]),
                des=float(row["mean_destructive_interference_d16"]),
                ah=float(row["mean_A_harm_d16"]),
                bh=float(row["mean_B_harm_d16"]),
                ms=float(row["mean_mutual_support_delta"]),
                cap=float(row["mean_cap_hit_any"]),
                lc=float(row["mean_low_confidence_flag"]),
            )
        )
    lines.extend(["", "## Mode Summary", "", "| mode | n | A alive | B alive | joint alive | joint terminal | joint valid actions |", "|---|---:|---:|---:|---:|---:|---:|"])
    for row in mode_summary:
        lines.append(
            "| {mode} | {n} | {a:.3f} | {b:.3f} | {j:.3f} | {t:.3f} | {v:.3f} |".format(
                mode=row["mode"],
                n=row["n"],
                a=float(row["mean_A_alive_d16"]),
                b=float(row["mean_B_alive_d16"]),
                j=float(row["mean_joint_alive_d16"]),
                t=float(row["mean_joint_terminal_d16"]),
                v=float(row["mean_joint_valid_actions_d16"]),
            )
        )
    lines.extend(["", "## Interference Bins", "", "| neutral bin | n | constructive | destructive | A harm | B harm | mutual support | low confidence |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
    for row in interference_bins:
        lines.append(
            "| {bin} | {n} | {con:.3f} | {des:.3f} | {ah:.3f} | {bh:.3f} | {ms:.3f} | {lc:.3f} |".format(
                bin=row["neutral_bin"],
                n=row["n"],
                con=float(row["mean_constructive_interference_d16"]),
                des=float(row["mean_destructive_interference_d16"]),
                ah=float(row["mean_A_harm_d16"]),
                bh=float(row["mean_B_harm_d16"]),
                ms=float(row["mean_mutual_support_delta"]),
                lc=float(row["mean_low_confidence_flag"]),
            )
        )
    lines.extend(["", "## Ablation Effects", "", "| ablation | n | joint delta | A delta | B delta |", "|---|---:|---:|---:|---:|"])
    for row in ablation_effects:
        lines.append(
            "| {ablation} | {n} | {j:.3f} | {a:.3f} | {b:.3f} |".format(
                ablation=row["ablation"],
                n=row["n"],
                j=float(row["mean_joint_delta_d16"]),
                a=float(row["mean_A_delta_d16"]),
                b=float(row["mean_B_delta_d16"]),
            )
        )
    bins = sorted({str(row["neutral_bin"]) for row in rows})
    lines.extend(
        [
            "",
            "## Smoke Read",
            "",
            f"- Bins observed: {', '.join(bins) if bins else 'none'}.",
            f"- Rows completed: {len(rows)}.",
            f"- Errors: {len(errors)}.",
            "- Raw joint enumeration is diagnostic only; sampled deltas are the primary readout.",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "val1_mf" / f"{run_id}_interference_audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    config = vars(args)
    config["run_id"] = run_id
    config["out"] = str(out_dir)
    config["started_perf_counter"] = time.perf_counter()
    config["status"] = "RUNNING"
    (out_dir / "config.json").write_text(json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True), encoding="utf-8")
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    result_path = out_dir / "results.jsonl"
    error_path = out_dir / "errors.jsonl"
    pending = _jobs(args)
    futures = {}
    timed_out = False
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        while pending and len(futures) < args.workers:
            job = pending.pop(0)
            futures[executor.submit(_run_one, job)] = job
        while futures:
            if time.perf_counter() - float(config["started_perf_counter"]) >= args.max_runtime_seconds:
                timed_out = True
                pending = []
            done, _ = wait(futures, timeout=5.0, return_when=FIRST_COMPLETED)
            if not done:
                continue
            for future in done:
                job = futures.pop(future)
                try:
                    row = future.result()
                    rows.append(row)
                    with result_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(row, sort_keys=True) + "\n")
                except Exception as exc:  # noqa: BLE001
                    error = {"job": job, "error": repr(exc)}
                    errors.append(error)
                    with error_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(error, sort_keys=True) + "\n")
                while not timed_out and pending and len(futures) < args.workers:
                    next_job = pending.pop(0)
                    futures[executor.submit(_run_one, next_job)] = next_job
            _write_outputs(out_dir, config, rows, errors)
    config["status"] = "TIMED_OUT" if timed_out else "COMPLETED"
    _write_csv(out_dir / "results.csv", rows)
    _write_outputs(out_dir, config, rows, errors)
    (out_dir / "config.json").write_text(json.dumps({k: v for k, v in config.items() if k != "started_perf_counter"}, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"out_dir": str(out_dir), "rows": len(rows), "errors": len(errors), "status": config["status"]}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
