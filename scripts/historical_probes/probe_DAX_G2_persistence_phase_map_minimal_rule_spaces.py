#!/usr/bin/env python
"""Probe DAX-G2: persistence phase map across minimal rule spaces.

Samples two minimal expansions beyond ECA:

- q=3, radius=1
- q=2, radius=2

The probe asks whether robust persistence survives while relation-dependence,
asymmetry-dependence, or interaction/composition improve over G1 anchors.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import probe_DAX_G0_minimal_DAR_rule_space_persistence as g0


Q3_ICS = [
    "random_uniform",
    "sparse_active_010",
    "sparse_active_025",
    "single_active_1",
    "single_active_2",
    "two_cell_active",
    "short_random_active_block",
    "periodic_background_perturbation",
]
Q2_ICS = [
    "bernoulli_050",
    "bernoulli_025",
    "single_seed",
    "two_cell_seed",
    "short_random_block",
    "periodic_perturbation",
]
STAGE1_KEEP_CLASSES = [
    "localized_persistence",
    "transported_identity",
    "emitter_or_generator",
    "mixed",
]
ANCHOR_RULES = [169, 225, 73, 109, 145, 131, 62, 118, 230, 188, 54, 61, 163, 177, 0, 4, 8, 12, 32, 36, 44, 51, 57, 60, 64, 68, 72, 76, 77, 90, 170, 204, 240]


@dataclass(frozen=True)
class RuleSpec:
    space: str
    rule_id: str
    stratum: str
    q: int
    radius: int
    table: tuple[int, ...]
    eca_rule: int | None = None


@dataclass(frozen=True)
class Config:
    out_dir: Path
    workers: int
    stage1_n_seeds: int
    stage1_T: int
    stage1_ring: int
    stage2_n_seeds: int
    stage2_horizons: tuple[int, ...]
    stage2_rings: tuple[int, ...]
    sample_main: int
    sample_control: int
    stage2_cap: int
    diagram_count: int


def parse_csv_ints(value: str) -> tuple[int, ...]:
    return tuple(int(x.strip()) for x in value.split(",") if x.strip())


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=Path("probe_DAX_G2_persistence_phase_map_minimal_rule_spaces_results"))
    p.add_argument("--workers", type=int, default=int(os.environ.get("OMEGA_WORKERS", "18")))
    p.add_argument("--stage1-n-seeds", type=int, default=64)
    p.add_argument("--stage1-T", type=int, default=256)
    p.add_argument("--stage1-ring", type=int, default=256)
    p.add_argument("--stage2-n-seeds", type=int, default=128)
    p.add_argument("--stage2-horizons", type=parse_csv_ints, default=(512, 1024))
    p.add_argument("--stage2-rings", type=parse_csv_ints, default=(256, 512))
    p.add_argument("--sample-main", type=int, default=300)
    p.add_argument("--sample-control", type=int, default=150)
    p.add_argument("--stage2-cap", type=int, default=160)
    p.add_argument("--diagram-count", type=int, default=20)
    return p.parse_args()


def table_digest(table: tuple[int, ...]) -> str:
    raw = bytes(table)
    return hashlib.sha1(raw).hexdigest()[:12]


def decode_idx(idx: int, q: int, n: int) -> tuple[int, ...]:
    vals = []
    for _ in range(n):
        vals.append(idx % q)
        idx //= q
    return tuple(reversed(vals))


def encode_tuple(vals: tuple[int, ...], q: int) -> int:
    idx = 0
    for v in vals:
        idx = idx * q + int(v)
    return idx


def reflected_index(idx: int, q: int, radius: int) -> int:
    vals = decode_idx(idx, q, 2 * radius + 1)
    return encode_tuple(tuple(reversed(vals)), q)


def dependency_flags(table: np.ndarray, q: int, radius: int) -> list[bool]:
    n = 2 * radius + 1
    flags = []
    for pos in range(n):
        dep = False
        for idx in range(q**n):
            vals = list(decode_idx(idx, q, n))
            base = table[idx]
            for alt in range(q):
                if alt == vals[pos]:
                    continue
                vals2 = vals.copy()
                vals2[pos] = alt
                if table[encode_tuple(tuple(vals2), q)] != base:
                    dep = True
                    break
            if dep:
                break
        flags.append(dep)
    return flags


def primitive_for_spec(spec: RuleSpec) -> dict[str, object]:
    table = np.array(spec.table, dtype=np.uint8)
    flags = dependency_flags(table, spec.q, spec.radius)
    center = spec.radius
    relation_positions = [i for i in range(len(flags)) if i != center]
    relation_degree = int(sum(flags[i] for i in relation_positions))
    reflected = np.array([table[reflected_index(i, spec.q, spec.radius)] for i in range(len(table))], dtype=np.uint8)
    lr_asym = float(np.mean(table != reflected))
    counts = np.bincount(table, minlength=spec.q)
    p = counts / max(counts.sum(), 1)
    output_entropy = float(-np.sum(p[p > 0] * np.log2(p[p > 0])))
    compression = float(1.0 - output_entropy / max(math.log2(spec.q), 1e-12))
    left_dep = any(flags[:center])
    right_dep = any(flags[center + 1 :])
    directional = float(abs(int(left_dep) - int(right_dep)))
    return {
        "space": spec.space,
        "rule_id": spec.rule_id,
        "stratum": spec.stratum,
        "q": spec.q,
        "radius": spec.radius,
        "table_digest": table_digest(spec.table),
        "depends_center": bool(flags[center]),
        "relation_degree": relation_degree,
        "relation_complete": relation_degree > 0,
        "self_only": bool(flags[center] and relation_degree == 0),
        "left_right_asymmetry": lr_asym,
        "output_entropy": output_entropy,
        "temporal_irreversibility_proxy": compression,
        "directional_consequence": directional,
        "DAR_complete_structural": bool(relation_degree > 0 and compression > 0.02),
        "DAR_asymmetric_structural": bool(relation_degree > 0 and compression > 0.02 and (lr_asym > 0.02 or directional > 0)),
    }


def random_table(rng: np.random.Generator, q: int, radius: int) -> np.ndarray:
    return rng.integers(0, q, size=q ** (2 * radius + 1), dtype=np.uint8)


def make_symmetric(table: np.ndarray, q: int, radius: int, rng: np.random.Generator) -> np.ndarray:
    out = table.copy()
    for idx in range(len(out)):
        ridx = reflected_index(idx, q, radius)
        if ridx < idx:
            out[idx] = out[ridx]
        elif ridx == idx:
            out[idx] = table[idx]
        else:
            val = int(table[idx] if rng.random() < 0.5 else table[ridx])
            out[idx] = val
            out[ridx] = val
    return out


def generate_table(q: int, radius: int, stratum: str, rng: np.random.Generator) -> np.ndarray:
    n = 2 * radius + 1
    size = q**n
    zero_idx = 0
    for attempt in range(200):
        if stratum == "S1_random_unbiased":
            table = random_table(rng, q, radius)
        elif stratum == "S2_quiescent_preserving":
            table = random_table(rng, q, radius)
            table[zero_idx] = 0
        elif stratum == "S3_sparse_active_preserving":
            table = np.zeros(size, dtype=np.uint8)
            for idx in range(size):
                vals = decode_idx(idx, q, n)
                active = sum(v != 0 for v in vals)
                if active == 0:
                    table[idx] = 0
                elif active == 1:
                    p_active = 0.68
                    table[idx] = int(rng.integers(1, q)) if rng.random() < p_active else 0
                elif active <= max(2, radius + 1):
                    p_active = 0.48
                    table[idx] = int(rng.integers(1, q)) if rng.random() < p_active else 0
                else:
                    p_active = 0.30
                    table[idx] = int(rng.integers(1, q)) if rng.random() < p_active else 0
        elif stratum == "S4_neighbor_dependent":
            table = random_table(rng, q, radius)
        elif stratum == "S5_asymmetric_neighbor_dependent":
            table = random_table(rng, q, radius)
            table[zero_idx] = 0
        elif stratum == "S6_relation_rich_nonchaotic_bias":
            table = np.zeros(size, dtype=np.uint8)
            for idx in range(size):
                vals = decode_idx(idx, q, n)
                center = vals[radius]
                active = sum(v != 0 for v in vals)
                if active == 0:
                    table[idx] = 0
                elif rng.random() < 0.50:
                    table[idx] = center
                elif rng.random() < 0.78:
                    table[idx] = int((sum(vals) + vals[0] + 2 * vals[-1]) % q)
                else:
                    table[idx] = int(rng.integers(0, q))
        elif stratum == "S7_symmetric_control":
            table = make_symmetric(random_table(rng, q, radius), q, radius, rng)
            table[zero_idx] = 0
        elif stratum == "S8_self_only_control":
            table = np.zeros(size, dtype=np.uint8)
            for idx in range(size):
                center = decode_idx(idx, q, n)[radius]
                table[idx] = center if rng.random() < 0.88 else int(rng.integers(0, q))
        else:
            raise ValueError(stratum)
        prim = primitive_for_spec(RuleSpec("tmp", "tmp", stratum, q, radius, tuple(int(x) for x in table)))
        if stratum == "S4_neighbor_dependent" and not prim["relation_complete"]:
            continue
        if stratum == "S5_asymmetric_neighbor_dependent" and not (prim["relation_complete"] and prim["left_right_asymmetry"] > 0.05):
            continue
        if stratum == "S6_relation_rich_nonchaotic_bias" and not (prim["relation_complete"] and 0.2 <= prim["output_entropy"] <= math.log2(q) * 0.98):
            continue
        return table
    return table


def build_rule_manifest(cfg: Config) -> list[RuleSpec]:
    specs: list[RuleSpec] = []
    strata_main = [
        "S1_random_unbiased",
        "S2_quiescent_preserving",
        "S3_sparse_active_preserving",
        "S4_neighbor_dependent",
        "S5_asymmetric_neighbor_dependent",
        "S6_relation_rich_nonchaotic_bias",
    ]
    strata_control = ["S7_symmetric_control", "S8_self_only_control"]
    for space, q, radius, prefix in [("q3_radius1", 3, 1, "q3r1"), ("q2_radius2", 2, 2, "q2r2")]:
        for stratum in strata_main + strata_control:
            count = cfg.sample_control if stratum in strata_control else cfg.sample_main
            for i in range(count):
                seed = 910_000 + len(specs) * 37 + q * 1000 + radius * 101
                rng = np.random.default_rng(seed)
                table = generate_table(q, radius, stratum, rng)
                specs.append(RuleSpec(space, f"{prefix}_{stratum[:2].lower()}_{i:04d}", stratum, q, radius, tuple(int(x) for x in table)))
    for rule in ANCHOR_RULES:
        table = tuple(int(x) for x in g0.rule_table(rule))
        specs.append(RuleSpec("ECA_anchor", f"ECA_{rule}", "ECA_anchor", 2, 1, table, rule))
    return specs


def initial_states(spec: RuleSpec, ic: str, n_seeds: int, ring: int, rng: np.random.Generator) -> np.ndarray:
    x = np.zeros((n_seeds, ring), dtype=np.uint8)
    if spec.space == "q3_radius1":
        if ic == "random_uniform":
            return rng.integers(0, 3, size=(n_seeds, ring), dtype=np.uint8)
        if ic == "sparse_active_010":
            mask = rng.random((n_seeds, ring)) < 0.10
            x[mask] = rng.integers(1, 3, size=int(mask.sum()), dtype=np.uint8)
            return x
        if ic == "sparse_active_025":
            mask = rng.random((n_seeds, ring)) < 0.25
            x[mask] = rng.integers(1, 3, size=int(mask.sum()), dtype=np.uint8)
            return x
        if ic == "single_active_1":
            x[:, ring // 2] = 1
            return x
        if ic == "single_active_2":
            x[:, ring // 2] = 2
            return x
        if ic == "two_cell_active":
            x[:, ring // 2] = 1
            x[:, ring // 2 + 1] = 2
            return x
        if ic == "short_random_active_block":
            for s in range(n_seeds):
                width = int(rng.integers(8, 25))
                start = ring // 2 - width // 2
                block_mask = rng.random(width) < 0.65
                vals = rng.integers(1, 3, size=width, dtype=np.uint8)
                x[s, start : start + width] = vals * block_mask
            return x
        if ic == "periodic_background_perturbation":
            x[:, ::3] = 1
            x[:, 1::3] = 0
            x[:, 2::3] = 2
            for s in range(n_seeds):
                center = ring // 2 + int(rng.integers(-8, 9))
                x[s, center - 2 : center + 3] = rng.integers(0, 3, size=5, dtype=np.uint8)
            return x
    if spec.space == "ECA_anchor":
        cfg = g0.Config(Path("."), ring, 1, n_seeds, 0, 1)
        return g0.initial_states(ic, cfg, rng)
    if spec.space == "q2_radius2":
        cfg = g0.Config(Path("."), ring, 1, n_seeds, 0, 1)
        return g0.initial_states(ic, cfg, rng)
    raise ValueError(f"{spec.space}:{ic}")


def ca_step(x: np.ndarray, spec: RuleSpec, table: np.ndarray) -> np.ndarray:
    q = spec.q
    if spec.radius == 1:
        idx = np.roll(x, 1, axis=1).astype(np.int16) * (q * q) + x.astype(np.int16) * q + np.roll(x, -1, axis=1).astype(np.int16)
    elif spec.radius == 2:
        idx = (
            np.roll(x, 2, axis=1).astype(np.int16) * 16
            + np.roll(x, 1, axis=1).astype(np.int16) * 8
            + x.astype(np.int16) * 4
            + np.roll(x, -1, axis=1).astype(np.int16) * 2
            + np.roll(x, -2, axis=1).astype(np.int16)
        )
    else:
        raise ValueError(spec.radius)
    return table[idx]


def simulate(spec: RuleSpec, ic: str, T: int, ring: int, n_seeds: int, salt: int = 0) -> np.ndarray:
    rng_seed = int(hashlib.sha1(f"{spec.rule_id}:{ic}:{T}:{ring}:{n_seeds}:{salt}".encode()).hexdigest()[:12], 16) % (2**32)
    rng = np.random.default_rng(rng_seed)
    table = np.array(spec.table, dtype=np.uint8)
    x = initial_states(spec, ic, n_seeds, ring, rng)
    hist = np.empty((T + 1, n_seeds, ring), dtype=np.uint8)
    hist[0] = x
    for t in range(T):
        x = ca_step(x, spec, table)
        hist[t + 1] = x
    return hist


def entropy_from_counts(counts: np.ndarray) -> float:
    p = counts[counts > 0] / max(counts.sum(), 1)
    return float(-np.sum(p * np.log2(p))) if p.size else 0.0


def component_lengths_active(row: np.ndarray) -> list[int]:
    active = row != 0
    return g0.component_lengths(active.astype(np.uint8))


def shifted_overlap_state(a: np.ndarray, b: np.ndarray, max_shift: int = 8) -> tuple[float, int]:
    best = -1.0
    best_shift = 0
    for s in range(-max_shift, max_shift + 1):
        score = float(np.mean(a == np.roll(b, s)))
        if score > best:
            best = score
            best_shift = s
    return best, best_shift


def estimate_period_state(series: np.ndarray) -> int:
    tail = series[-64:]
    for p in range(1, 33):
        if len(tail) > p and np.mean(tail[p:] == tail[:-p]) > 0.995:
            return p
    return 0


def metrics_for_history(hist: np.ndarray, q: int) -> dict[str, float]:
    T, n, L = hist.shape[0] - 1, hist.shape[1], hist.shape[2]
    active_mask = hist != 0
    active = active_mask.mean(axis=2)
    active_mean = float(np.mean(active))
    active_final = float(np.mean(active[-1]))
    final = hist[-1]
    extinction = float(np.mean(np.all(final == 0, axis=1)))
    fixed = float(np.mean(np.all(hist[-1] == hist[-2], axis=1)))
    symbol_counts = np.bincount(hist.reshape(-1), minlength=q)
    symbol_entropy_mean = entropy_from_counts(symbol_counts) / max(math.log2(q), 1e-12)
    period_flags = []
    comp_lifetimes = []
    comp_sizes = []
    recurrence_scores = []
    shifts = []
    turnover = []
    fragmentation = []
    damage = []
    compress = []
    contrasts = []
    for s in range(n):
        h = hist[:, s]
        period_flags.append(estimate_period_state(h) > 0)
        prev_center = None
        lifetime = 0
        max_life = 0
        for t in range(0, T + 1, 4):
            lengths = component_lengths_active(h[t])
            good = [x for x in lengths if 1 <= x <= L // 4]
            comp_sizes.extend(good)
            fragmentation.append(len(good) / max(int(np.sum(h[t] != 0)), 1))
            if good:
                coords = np.where(h[t] != 0)[0]
                center = int(np.round(np.mean(coords)))
                if prev_center is None or abs(center - prev_center) <= 12:
                    lifetime += 4
                else:
                    max_life = max(max_life, lifetime)
                    lifetime = 4
                prev_center = center
            else:
                max_life = max(max_life, lifetime)
                lifetime = 0
                prev_center = None
        comp_lifetimes.append(max(max_life, lifetime))
        a = h[max(0, T // 2)]
        b = h[-1]
        rec, sh = shifted_overlap_state(a, b)
        recurrence_scores.append(rec)
        shifts.append(sh / max(T // 2, 1))
        turnover.append(float(np.mean(a != b)))
        active_final_row = b != 0
        if np.any(active_final_row) and np.any(~active_final_row):
            contrasts.append(1.0)
        else:
            contrasts.append(0.0)
        damage.append(float(np.mean(b != np.roll(b, 1))))
        transitions = float(np.mean(b != np.roll(b, 1)))
        compress.append(1.0 - transitions)
    sizes = np.array(comp_sizes if comp_sizes else [0])
    lifetimes = np.array(comp_lifetimes)
    recurrence = float(np.mean(recurrence_scores))
    material_turnover = float(np.mean(turnover))
    frozen = float(0.65 * fixed + 0.35 * np.mean(np.array(turnover) < 0.02))
    chaos = float(symbol_entropy_mean * np.mean(damage))
    persistent_count = float(np.mean(lifetimes >= 32))
    localized_life_max = float(np.max(lifetimes))
    return {
        "active_fraction_mean": active_mean,
        "active_fraction_final": active_final,
        "symbol_entropy_mean": symbol_entropy_mean,
        "extinction_rate": extinction,
        "all_zero_attractor_rate": extinction,
        "all_one_attractor_rate": float(np.mean(np.all(final == q - 1, axis=1))),
        "global_fixed_point_rate": fixed,
        "global_periodic_rate": float(np.mean(period_flags)),
        "localized_component_lifetime_mean": float(np.mean(lifetimes)),
        "localized_component_lifetime_max": localized_life_max,
        "component_size_median": float(np.median(sizes)),
        "component_size_entropy": g0.entropy_from_values(sizes),
        "persistent_component_count": persistent_count,
        "recurrence_up_to_shift": recurrence,
        "motif_survival_depth": localized_life_max / max(T, 1),
        "motif_material_turnover": material_turnover,
        "translation_velocity_estimate": float(np.mean(shifts)),
        "period_estimate": float(np.median([estimate_period_state(hist[:, s]) for s in range(n)])),
        "pattern_background_contrast": float(np.mean(contrasts)),
        "local_entropy_inside_pattern": active_mean,
        "local_entropy_outside_pattern": 1.0 - active_mean,
        "signal_to_background_ratio": float(np.mean(contrasts) / max(np.std(active[-64:]) + 1e-9, 1e-9)),
        "exact_static_fraction": fixed,
        "global_period_fraction": float(np.mean(period_flags)),
        "low_turnover_persistence_fraction": float(np.mean(np.array(turnover) < 0.02)),
        "frozen_order_index": frozen,
        "activity_entropy": symbol_entropy_mean,
        "damage_spreading_rate": float(np.mean(damage)),
        "compressibility_proxy": float(np.mean(compress)),
        "component_fragmentation_rate": float(np.mean(fragmentation)),
        "chaos_index": chaos,
    }


def classify_persistence(row: dict[str, float]) -> str:
    if row["extinction_rate"] > 0.65 or row["all_zero_attractor_rate"] + row["all_one_attractor_rate"] > 0.70:
        return "collapse"
    if row["frozen_order_index"] > 0.65 and row["motif_material_turnover"] < 0.08:
        return "frozen_order"
    if row["global_periodic_rate"] > 0.65 and row["persistent_component_count"] < 0.35:
        return "global_periodic"
    if row["chaos_index"] > 0.60 and row["recurrence_up_to_shift"] < 0.80:
        return "chaotic"
    transported = (
        row["persistent_component_count"] > 0.20
        and row["localized_component_lifetime_max"] >= 48
        and row["recurrence_up_to_shift"] > 0.70
        and row["motif_material_turnover"] > 0.08
        and row["frozen_order_index"] < 0.70
    )
    if transported and abs(row["translation_velocity_estimate"]) > 0.01:
        return "transported_identity"
    if transported:
        return "localized_persistence"
    if row["persistent_component_count"] > 0.25 and row["component_fragmentation_rate"] > 0.10:
        return "emitter_or_generator"
    return "mixed"


def motif_type(row: dict[str, float]) -> str:
    if row["frozen_order_index"] > 0.70 and row["motif_material_turnover"] < 0.05:
        return "static_object"
    if row["global_periodic_rate"] > 0.70:
        return "global_periodic_artifact"
    if row["chaos_index"] > 0.60 and row["pattern_background_contrast"] < 0.20:
        return "chaotic_fragment"
    if row["component_fragmentation_rate"] > 0.20 and row["persistent_component_count"] > 0.20:
        return "emitter"
    if abs(row["translation_velocity_estimate"]) > 0.01 and row["motif_material_turnover"] > 0.08:
        return "travelling_identity"
    if row["recurrence_up_to_shift"] > 0.72 and row["motif_material_turnover"] > 0.08:
        return "localized_oscillator"
    if row["pattern_background_contrast"] > 0.25 and row["localized_component_lifetime_max"] > 128:
        return "domain_wall"
    return "unknown"


def evaluate_stage1_rule(spec: RuleSpec, cfg: Config) -> dict[str, object]:
    ics = Q3_ICS if spec.space == "q3_radius1" else Q2_ICS
    metric_rows = []
    for ic in ics:
        hist = simulate(spec, ic, cfg.stage1_T, cfg.stage1_ring, cfg.stage1_n_seeds)
        metric_rows.append(metrics_for_history(hist, spec.q))
    out: dict[str, object] = {
        "space": spec.space,
        "rule_id": spec.rule_id,
        "stratum": spec.stratum,
        "q": spec.q,
        "radius": spec.radius,
        "table_digest": table_digest(spec.table),
        "table_json": json.dumps(list(spec.table), separators=(",", ":")),
    }
    for k in metric_rows[0].keys():
        out[k] = float(np.mean([m[k] for m in metric_rows]))
    out["classification"] = classify_persistence(out)  # type: ignore[arg-type]
    prim = primitive_for_spec(spec)
    out.update({k: v for k, v in prim.items() if k not in out})
    out["stage1_score"] = float(
        out["recurrence_up_to_shift"]
        * out["motif_material_turnover"]
        * (1.0 - min(float(out["frozen_order_index"]), 1.0))
        * (1.0 - min(float(out["chaos_index"]), 1.0))
    )
    out["relation_asymmetry_priority"] = float(out["stage1_score"]) * (1.0 + float(out["relation_degree"]) + float(out["left_right_asymmetry"]))
    return out


def evaluate_stage1_worker(args: tuple[RuleSpec, Config]) -> dict[str, object]:
    return evaluate_stage1_rule(*args)


def select_stage2_candidates(stage1: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    picks = []
    for space in ["q3_radius1", "q2_radius2"]:
        sdf = stage1[stage1["space"] == space].copy()
        for cls in STAGE1_KEEP_CLASSES:
            cdf = sdf[sdf["classification"] == cls].sort_values("stage1_score", ascending=False).head(25)
            picks.append(cdf)
        picks.append(sdf.sort_values("relation_asymmetry_priority", ascending=False).head(25))
    picks.append(stage1[stage1["space"] == "ECA_anchor"].copy())
    out = pd.concat(picks, ignore_index=True).drop_duplicates(["space", "rule_id"])
    per_expanded = max(1, cfg.stage2_cap // 3)
    eca_cap = max(1, cfg.stage2_cap - 2 * per_expanded)
    selected = []
    for space, cap in [("q3_radius1", per_expanded), ("q2_radius2", per_expanded), ("ECA_anchor", eca_cap)]:
        selected.append(out[out["space"] == space].sort_values("stage1_score", ascending=False).head(cap))
    return pd.concat(selected, ignore_index=True)


def spec_from_row(row: pd.Series) -> RuleSpec:
    table = tuple(int(x) for x in json.loads(row["table_json"]))
    return RuleSpec(str(row["space"]), str(row["rule_id"]), str(row["stratum"]), int(row["q"]), int(row["radius"]), table, None)


def evaluate_stage2_cell(args: tuple[RuleSpec, str, int, int, int]) -> dict[str, object]:
    spec, ic, T, ring, n_seeds = args
    hist = simulate(spec, ic, T, ring, n_seeds, salt=2)
    m = metrics_for_history(hist, spec.q)
    mt = motif_type(m)
    confirmed = (
        mt in {"localized_oscillator", "travelling_identity", "emitter", "domain_wall"}
        and m["recurrence_up_to_shift"] > 0.70
        and m["motif_material_turnover"] > 0.08
        and m["frozen_order_index"] < 0.70
        and m["chaos_index"] < 0.65
    )
    return {
        "space": spec.space,
        "rule_id": spec.rule_id,
        "stratum": spec.stratum,
        "q": spec.q,
        "radius": spec.radius,
        "ic_family": ic,
        "T": T,
        "ring_size": ring,
        "motif_type": mt,
        "confirmed": confirmed,
        **m,
    }


def project_table(spec: RuleSpec, kind: str) -> RuleSpec:
    q, radius = spec.q, spec.radius
    n = 2 * radius + 1
    table = np.array(spec.table, dtype=np.uint8)
    new = np.zeros_like(table)
    for idx in range(len(table)):
        vals = list(decode_idx(idx, q, n))
        src_vals = vals.copy()
        if kind == "center_only_projection":
            src_vals = [vals[radius]] * n
            new[idx] = table[encode_tuple(tuple(src_vals), q)]
        elif kind == "left_neighbor_removed":
            for p in range(radius):
                src_vals[p] = vals[radius]
            new[idx] = table[encode_tuple(tuple(src_vals), q)]
        elif kind == "right_neighbor_removed":
            for p in range(radius + 1, n):
                src_vals[p] = vals[radius]
            new[idx] = table[encode_tuple(tuple(src_vals), q)]
        elif kind == "inner_neighbors_only" and radius == 2:
            src_vals[0] = vals[radius]
            src_vals[-1] = vals[radius]
            new[idx] = table[encode_tuple(tuple(src_vals), q)]
        elif kind == "outer_neighbors_removed" and radius == 2:
            src_vals[0] = vals[radius]
            src_vals[-1] = vals[radius]
            new[idx] = table[encode_tuple(tuple(src_vals), q)]
        elif kind == "left_right_symmetrized_rule":
            ridx = reflected_index(idx, q, radius)
            counts = np.bincount([int(table[idx]), int(table[ridx])], minlength=q)
            new[idx] = int(np.argmax(counts))
        elif kind == "active_symbol_permutation_control" and q == 3:
            src = int(table[idx])
            new[idx] = {0: 0, 1: 2, 2: 1}[src]
        elif kind == "background_symbol_swap_control" and q == 3:
            src = int(table[idx])
            new[idx] = {0: 1, 1: 0, 2: 2}[src]
        else:
            new[idx] = table[idx]
    return RuleSpec(spec.space, f"{spec.rule_id}_{kind}", kind, q, radius, tuple(int(x) for x in new))


def motif_survival_score(spec: RuleSpec) -> float:
    ic = "short_random_active_block" if spec.space == "q3_radius1" else "short_random_block"
    hist = simulate(spec, ic, 256, 256, 32, salt=7)
    m = metrics_for_history(hist, spec.q)
    return float(m["recurrence_up_to_shift"] * m["motif_material_turnover"] * (1.0 - min(m["frozen_order_index"], 1.0)))


def primitive_load_bearing(spec: RuleSpec) -> dict[str, object]:
    original = motif_survival_score(spec)
    kinds = ["center_only_projection", "left_neighbor_removed", "right_neighbor_removed", "left_right_symmetrized_rule"]
    if spec.space == "q3_radius1":
        kinds += ["active_symbol_permutation_control", "background_symbol_swap_control"]
    elif spec.space == "q2_radius2":
        kinds += ["inner_neighbors_only", "outer_neighbors_removed"]
    scores = {k: motif_survival_score(project_table(spec, k)) for k in kinds}
    relation_drop = original - max(scores.get("center_only_projection", 0.0), scores.get("left_neighbor_removed", 0.0), scores.get("right_neighbor_removed", 0.0))
    asym_drop = original - scores.get("left_right_symmetrized_rule", original)
    return {
        "space": spec.space,
        "rule_id": spec.rule_id,
        "stratum": spec.stratum,
        "original_survival_score": original,
        **{f"{k}_score": v for k, v in scores.items()},
        "relation_dependence_delta": relation_drop,
        "asymmetry_dependence_delta": asym_drop,
        "relation_dependence_positive": relation_drop > 0.02,
        "asymmetry_dependence_positive": asym_drop > 0.02,
    }


def perturbation_response(spec: RuleSpec) -> dict[str, object]:
    ic = "short_random_active_block" if spec.space == "q3_radius1" else "short_random_block"
    hist = simulate(spec, ic, 128, 256, 48, salt=11)
    table = np.array(spec.table, dtype=np.uint8)
    rng = np.random.default_rng(int(hashlib.sha1(spec.rule_id.encode()).hexdigest()[:8], 16))
    mid = hist[48].copy()
    base_codes = []
    pert_codes = []
    labels = []
    for s in range(mid.shape[0]):
        xb = mid[s : s + 1].copy()
        xp = xb.copy()
        active = np.where(xp[0] != 0)[0]
        pos = int(rng.choice(active)) if len(active) else xp.shape[1] // 2
        xp[0, pos] = int((xp[0, pos] + 1) % spec.q)
        for _ in range(80):
            xb = ca_step(xb, spec, table)
            xp = ca_step(xp, spec, table)
        base_codes.append(hashlib.sha1(xb.tobytes()).hexdigest()[:16])
        pert_codes.append(hashlib.sha1(xp.tobytes()).hexdigest()[:16])
        active_frac = float(np.mean(xp != 0))
        if active_frac < 0.001:
            labels.append("collapse")
        elif active_frac > 0.92:
            labels.append("explosion")
        elif base_codes[-1] == pert_codes[-1]:
            labels.append("same")
        else:
            labels.append("related")
    return {
        "space": spec.space,
        "rule_id": spec.rule_id,
        "post_perturbation_survival_rate": float(np.mean([x != "collapse" for x in labels])),
        "return_to_same_motif_rate": float(np.mean([x == "same" for x in labels])),
        "transition_to_related_motif_rate": float(np.mean([x == "related" for x in labels])),
        "collapse_rate": float(np.mean([x == "collapse" for x in labels])),
        "explosion_rate": float(np.mean([x == "explosion" for x in labels])),
        "future_distinct_descendant_count": float(len(set(pert_codes))),
        "future_distinct_ratio": float(len(set(pert_codes)) / max(len(pert_codes), 1)),
        "descendant_entropy": entropy_from_counts(np.array(list(pd.Series(pert_codes).value_counts()))),
        "descendant_class_diversity": float(len(set(labels))),
    }


def interaction_composition(specs: list[RuleSpec]) -> pd.DataFrame:
    rows = []
    for spec in specs:
        if spec.space == "ECA_anchor":
            continue
        table = np.array(spec.table, dtype=np.uint8)
        distances = [16, 32, 64]
        phases = [0, 1, 2]
        outcomes = []
        for distance in distances:
            for phase in phases:
                n = 16
                ring = 256
                x = np.zeros((n, ring), dtype=np.uint8)
                for s in range(n):
                    c1 = ring // 2 - distance // 2
                    c2 = ring // 2 + distance // 2
                    val1 = 1
                    val2 = 2 if spec.q == 3 and phase % 2 else 1
                    x[s, c1 - 1 : c1 + 2] = val1
                    x[s, c2 - 1 : c2 + 2] = val2
                initial_components = np.mean([len(component_lengths_active(row)) for row in x])
                for _ in range(192):
                    x = ca_step(x, spec, table)
                final_components = np.mean([len(component_lengths_active(row)) for row in x])
                active = float(np.mean(x != 0))
                if active < 0.001:
                    outcome = "collapse"
                elif active > 0.92:
                    outcome = "chaotic_explosion"
                elif final_components > initial_components + 1:
                    outcome = "emission"
                elif final_components < max(1, initial_components - 1):
                    outcome = "merge_or_annihilation"
                elif abs(final_components - initial_components) <= 0.5:
                    outcome = "pass_through_or_no_interaction"
                else:
                    outcome = "new_motif"
                outcomes.append(outcome)
        composition_positive = [x for x in outcomes if x in {"emission", "new_motif", "merge_or_annihilation"}]
        rows.append(
            {
                "space": spec.space,
                "rule_id": spec.rule_id,
                "composition_positive_count": len(composition_positive),
                "stable_product_rate": float(np.mean([x == "new_motif" for x in outcomes])),
                "phase_sensitive_outcome_rate": float(len(set(outcomes)) > 1),
                "future_distinct_interaction_products": float(len(set(outcomes))),
                "interaction_outcome_diversity": entropy_from_counts(np.array(list(pd.Series(outcomes).value_counts()))),
                "dominant_interaction_outcome": pd.Series(outcomes).mode().iloc[0],
            }
        )
    return pd.DataFrame(rows)


def make_spacetime_diagrams(out: Path, specs: list[RuleSpec], count: int) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    d = out / "spacetime_examples"
    d.mkdir(exist_ok=True)
    for spec in specs[:count]:
        ic = "short_random_active_block" if spec.space == "q3_radius1" else "short_random_block"
        if spec.space == "ECA_anchor":
            ic = "short_random_block"
        hist = simulate(spec, ic, 256, 256, 1, salt=99)[:, 0, :]
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.imshow(hist, aspect="auto", interpolation="nearest", cmap="viridis", vmin=0, vmax=max(spec.q - 1, 1))
        ax.set_title(spec.rule_id)
        ax.set_xlabel("site")
        ax.set_ylabel("t")
        fig.tight_layout()
        label = spec.rule_id.replace("/", "_")
        fig.savefig(d / f"{label}_motif_seed_0.png", dpi=140)
        plt.close(fig)


def make_plots(out: Path, stage1: pd.DataFrame, stage2: pd.DataFrame, prim: pd.DataFrame, comp: pd.DataFrame, compare: pd.DataFrame) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    enrich = stage1.groupby(["space", "stratum", "classification"]).size().reset_index(name="count")
    pivot = enrich.pivot_table(index=["space", "stratum"], columns="classification", values="count", fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 5))
    pivot.plot(kind="bar", stacked=True, ax=ax)
    ax.set_ylabel("rule count")
    fig.tight_layout()
    fig.savefig(out / "stratum_enrichment_by_space.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    compare.plot(x="space", y=["confirmed_robust_motif_rate"], kind="bar", ax=ax)
    ax.set_ylabel("rate")
    fig.tight_layout()
    fig.savefig(out / "expanded_vs_ECA_persistence.png", dpi=160)
    plt.close(fig)

    for col, name in [
        ("relation_dependence_delta", "relation_dependence_by_space.png"),
        ("asymmetry_dependence_delta", "asymmetry_dependence_by_space.png"),
    ]:
        fig, ax = plt.subplots(figsize=(7, 4))
        prim.groupby("space")[col].mean().plot(kind="bar", ax=ax)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_ylabel(col)
        fig.tight_layout()
        fig.savefig(out / name, dpi=160)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4))
    if len(comp):
        comp.groupby("space")["composition_positive_count"].sum().plot(kind="bar", ax=ax)
    ax.set_ylabel("composition positives")
    fig.tight_layout()
    fig.savefig(out / "composition_positive_by_space.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(stage1["chaos_index"], stage1["stage1_score"], s=8, alpha=0.5)
    ax.set_xlabel("chaos_index")
    ax.set_ylabel("stage1_score")
    fig.tight_layout()
    fig.savefig(out / "persistence_vs_chaos_scatter.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(stage2["localized_component_lifetime_max"], stage2["motif_material_turnover"], s=12, alpha=0.6)
    ax.set_xlabel("motif lifetime max")
    ax.set_ylabel("material turnover")
    fig.tight_layout()
    fig.savefig(out / "motif_lifetime_vs_turnover_expanded.png", dpi=160)
    plt.close(fig)

    metrics = ["confirmed_fraction", "recurrence_up_to_shift", "motif_material_turnover", "frozen_order_index", "chaos_index"]
    heat = stage2.groupby(["space", "rule_id"])[metrics].mean(numeric_only=True).head(60)
    fig, ax = plt.subplots(figsize=(9, 8))
    ax.imshow(heat.to_numpy(), aspect="auto", interpolation="nearest")
    ax.set_yticks(range(len(heat.index)))
    ax.set_yticklabels([f"{a}:{b}" for a, b in heat.index], fontsize=6)
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(metrics, rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(out / "candidate_control_heatmap.png", dpi=160)
    plt.close(fig)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = sorted({k for row in rows for k in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def json_sanitize(value: object) -> object:
    if isinstance(value, dict):
        return {str(k): json_sanitize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_sanitize(v) for v in value]
    if isinstance(value, tuple):
        return [json_sanitize(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        if value == 0.0:
            return 0.0
        return value
    if pd.isna(value):
        return None
    return value


def main() -> None:
    args = parse_args()
    cfg = Config(
        args.out_dir,
        args.workers,
        args.stage1_n_seeds,
        args.stage1_T,
        args.stage1_ring,
        args.stage2_n_seeds,
        tuple(args.stage2_horizons),
        tuple(args.stage2_rings),
        args.sample_main,
        args.sample_control,
        args.stage2_cap,
        args.diagram_count,
    )
    t0 = time.time()
    if cfg.out_dir.exists():
        shutil.rmtree(cfg.out_dir)
    cfg.out_dir.mkdir(parents=True)

    specs = build_rule_manifest(cfg)
    manifest_rows = [primitive_for_spec(s) | {"table_json": json.dumps(list(s.table), separators=(",", ":"))} for s in specs]
    pd.DataFrame(manifest_rows).to_csv(cfg.out_dir / "sampled_rule_manifest.csv", index=False)

    stage1_rows = []
    with ProcessPoolExecutor(max_workers=cfg.workers) as ex:
        futures = [ex.submit(evaluate_stage1_worker, (s, cfg)) for s in specs]
        for i, fut in enumerate(as_completed(futures), 1):
            stage1_rows.append(fut.result())
            if i % max(1, len(futures) // 20) == 0:
                print(f"stage1 {i}/{len(futures)}", flush=True)
    stage1 = pd.DataFrame(stage1_rows)
    stage1.to_csv(cfg.out_dir / "rule_space_scan_metrics.csv", index=False)
    stage1[["space", "rule_id", "stratum", "classification", "stage1_score", "relation_asymmetry_priority"]].to_csv(
        cfg.out_dir / "stage1_persistence_classification.csv", index=False
    )
    stratum_enrichment = (
        stage1.groupby(["space", "stratum", "classification"]).size().reset_index(name="count")
    )
    totals = stage1.groupby(["space", "stratum"]).size().reset_index(name="stratum_total")
    stratum_enrichment = stratum_enrichment.merge(totals, on=["space", "stratum"])
    stratum_enrichment["rate"] = stratum_enrichment["count"] / stratum_enrichment["stratum_total"]
    stratum_enrichment.to_csv(cfg.out_dir / "stage1_stratum_enrichment.csv", index=False)

    stage2_candidates = select_stage2_candidates(stage1, cfg)
    stage2_candidates.to_csv(cfg.out_dir / "stage2_candidate_rules.csv", index=False)
    stage2_specs = [spec_from_row(row) for _, row in stage2_candidates.iterrows()]

    tasks = []
    for spec in stage2_specs:
        ics = Q3_ICS if spec.space == "q3_radius1" else Q2_ICS
        for T in cfg.stage2_horizons:
            for ring in cfg.stage2_rings:
                for ic in ics:
                    tasks.append((spec, ic, T, ring, cfg.stage2_n_seeds))
    stage2_rows = []
    with ProcessPoolExecutor(max_workers=cfg.workers) as ex:
        futures = [ex.submit(evaluate_stage2_cell, task) for task in tasks]
        for i, fut in enumerate(as_completed(futures), 1):
            stage2_rows.append(fut.result())
            if i % max(1, len(futures) // 20) == 0:
                print(f"stage2 {i}/{len(futures)}", flush=True)
    stage2 = pd.DataFrame(stage2_rows)
    conf = stage2.groupby(["space", "rule_id"])["confirmed"].mean().reset_index(name="confirmed_fraction")
    stage2 = stage2.merge(conf, on=["space", "rule_id"], how="left")
    stage2.to_csv(cfg.out_dir / "stage2_motif_anatomy.csv", index=False)
    robustness = stage2.groupby(["space", "rule_id", "T", "ring_size"]).agg(
        confirmed_rate=("confirmed", "mean"),
        recurrence_up_to_shift=("recurrence_up_to_shift", "mean"),
        motif_material_turnover=("motif_material_turnover", "mean"),
        frozen_order_index=("frozen_order_index", "mean"),
        chaos_index=("chaos_index", "mean"),
    ).reset_index()
    robustness.to_csv(cfg.out_dir / "stage2_robustness.csv", index=False)

    confirmed_ids = conf[conf["confirmed_fraction"] >= 0.35][["space", "rule_id"]]
    confirmed_specs = [s for s in stage2_specs if ((confirmed_ids["space"] == s.space) & (confirmed_ids["rule_id"] == s.rule_id)).any()]
    sidecar_specs = confirmed_specs[:80] if confirmed_specs else stage2_specs[:40]
    primitive_rows = []
    perturb_rows = []
    with ProcessPoolExecutor(max_workers=cfg.workers) as ex:
        prim_futs = [ex.submit(primitive_load_bearing, s) for s in sidecar_specs]
        pert_futs = [ex.submit(perturbation_response, s) for s in sidecar_specs]
        for fut in as_completed(prim_futs):
            primitive_rows.append(fut.result())
        for fut in as_completed(pert_futs):
            perturb_rows.append(fut.result())
    primitive_df = pd.DataFrame(primitive_rows)
    perturb_df = pd.DataFrame(perturb_rows)
    primitive_df.to_csv(cfg.out_dir / "stage2_primitive_load_bearing.csv", index=False)
    perturb_df.to_csv(cfg.out_dir / "future_distinct_descendants.csv", index=False)

    comp_df = interaction_composition(confirmed_specs[:40])
    comp_df.to_csv(cfg.out_dir / "stage2_interaction_composition.csv", index=False)

    motif_summary = stage2.groupby(["space", "rule_id"]).agg(
        confirmed_fraction=("confirmed", "mean"),
        localized_component_lifetime_max=("localized_component_lifetime_max", "mean"),
        recurrence_up_to_shift=("recurrence_up_to_shift", "mean"),
        motif_material_turnover=("motif_material_turnover", "mean"),
        background_contrast=("pattern_background_contrast", "mean"),
        frozen_order_index=("frozen_order_index", "mean"),
        chaos_index=("chaos_index", "mean"),
    ).reset_index()
    motif_summary = motif_summary.merge(stage2_candidates[["space", "rule_id", "stratum", "classification", "stage1_score"]], on=["space", "rule_id"], how="left")
    motif_summary = motif_summary.merge(primitive_df[["space", "rule_id", "relation_dependence_delta", "asymmetry_dependence_delta", "relation_dependence_positive", "asymmetry_dependence_positive"]] if len(primitive_df) else pd.DataFrame(columns=["space", "rule_id"]), on=["space", "rule_id"], how="left")
    motif_summary = motif_summary.merge(perturb_df[["space", "rule_id", "post_perturbation_survival_rate", "future_distinct_descendant_count"]] if len(perturb_df) else pd.DataFrame(columns=["space", "rule_id"]), on=["space", "rule_id"], how="left")
    motif_summary = motif_summary.merge(comp_df[["space", "rule_id", "composition_positive_count", "stable_product_rate", "interaction_outcome_diversity", "dominant_interaction_outcome"]] if len(comp_df) else pd.DataFrame(columns=["space", "rule_id"]), on=["space", "rule_id"], how="left")
    motif_summary.to_csv(cfg.out_dir / "expanded_vs_ECA_comparison.csv", index=False)

    control_summary = stage1[stage1["stratum"].isin(["S7_symmetric_control", "S8_self_only_control", "ECA_anchor"])].groupby(["space", "stratum", "classification"]).size().reset_index(name="count")
    control_summary.to_csv(cfg.out_dir / "control_summary.csv", index=False)
    pd.DataFrame([{"warning": ""}]).to_csv(cfg.out_dir / "estimator_report.csv", index=False)

    space_rows = []
    for space in ["ECA_anchor", "q3_radius1", "q2_radius2"]:
        sdf = motif_summary[motif_summary["space"] == space]
        prim_sdf = primitive_df[primitive_df["space"] == space] if len(primitive_df) else pd.DataFrame()
        comp_sdf = comp_df[comp_df["space"] == space] if len(comp_df) else pd.DataFrame()
        sampled = int((stage1["space"] == space).sum())
        confirmed_count = int((sdf["confirmed_fraction"] >= 0.35).sum())
        relation_count = int(prim_sdf.get("relation_dependence_positive", pd.Series(dtype=bool)).sum()) if len(prim_sdf) else 0
        asym_count = int(prim_sdf.get("asymmetry_dependence_positive", pd.Series(dtype=bool)).sum()) if len(prim_sdf) else 0
        comp_count = int((comp_sdf.get("composition_positive_count", pd.Series(dtype=float)) > 0).sum()) if len(comp_sdf) else 0
        space_rows.append(
            {
                "space": space,
                "sampled_rules": sampled,
                "confirmed_motifs": confirmed_count,
                "confirmed_robust_motif_rate": confirmed_count / max(sampled, 1),
                "relation_positive_count": relation_count,
                "asymmetry_positive_count": asym_count,
                "composition_positive_count": comp_count,
            }
        )
    compare = pd.DataFrame(space_rows)
    compare.to_csv(cfg.out_dir / "space_summary.csv", index=False)

    make_spacetime_diagrams(cfg.out_dir, sorted(confirmed_specs, key=lambda s: s.rule_id) or stage2_specs, cfg.diagram_count)
    make_plots(cfg.out_dir, stage1, motif_summary, primitive_df, comp_df, compare)

    eca = compare[compare["space"] == "ECA_anchor"]
    expanded = compare[compare["space"].isin(["q3_radius1", "q2_radius2"])]
    eca_confirmed = int(eca["confirmed_motifs"].max()) if len(eca) else 0
    expanded_best_confirmed = int(expanded["confirmed_motifs"].max()) if len(expanded) else 0
    relation_improved = bool(expanded["relation_positive_count"].max() > (int(eca["relation_positive_count"].max()) if len(eca) else 0)) if len(expanded) else False
    asym_improved = bool(expanded["asymmetry_positive_count"].max() > (int(eca["asymmetry_positive_count"].max()) if len(eca) else 0)) if len(expanded) else False
    comp_recovered = bool(expanded["composition_positive_count"].max() > 0) if len(expanded) else False
    control_leaks = stage1[
        (stage1["stratum"].isin(["S7_symmetric_control", "S8_self_only_control"]))
        & (stage1["classification"].isin(["localized_persistence", "transported_identity", "emitter_or_generator"]))
    ]
    controls_rejected = bool(control_leaks.empty)
    control_leak_count_by_space = control_leaks.groupby("space").size().to_dict() if len(control_leaks) else {}

    best = motif_summary.sort_values(["confirmed_fraction", "relation_dependence_delta", "asymmetry_dependence_delta", "stage1_score"], ascending=False).head(1)
    if len(best):
        b = best.iloc[0].to_dict()
    else:
        b = {}
    top_candidates = motif_summary.sort_values(["confirmed_fraction", "stage1_score"], ascending=False).head(20).to_dict(orient="records")
    recommendation = "No expanded-space improvement over ECA; stay with G1 motifs and do not expand blindly."
    next_probe = "DAX_G1_followup_or_metric_revision"
    if comp_recovered or relation_improved or asym_improved:
        recommendation = "Expanded-space smoke shows at least one missing invariant improving; run a larger targeted G2 main pass on the winning space."
        next_probe = "DAX_G2_main_targeted_phase_map"
    if controls_rejected is False:
        recommendation = "Controls leaked in the expanded-space scan; fix metrics before interpreting positives."
        next_probe = "DAX_G2_metric_guardrail_revision"

    summary = {
        "probe": "DAX_G2_persistence_phase_map_minimal_rule_spaces",
        "status": "COMPLETE",
        "runtime_seconds": round(time.time() - t0, 3),
        "config": {
            "sample_main": cfg.sample_main,
            "sample_control": cfg.sample_control,
            "stage1_n_seeds": cfg.stage1_n_seeds,
            "stage1_T": cfg.stage1_T,
            "stage1_ring": cfg.stage1_ring,
            "stage2_n_seeds": cfg.stage2_n_seeds,
            "stage2_horizons": list(cfg.stage2_horizons),
            "stage2_rings": list(cfg.stage2_rings),
            "stage2_cap": cfg.stage2_cap,
            "workers": cfg.workers,
        },
        "spaces": {
            row["space"]: {
                "sampled_rules": int(row["sampled_rules"]),
                "confirmed_motifs": int(row["confirmed_motifs"]),
                "relation_positive_count": int(row["relation_positive_count"]),
                "asymmetry_positive_count": int(row["asymmetry_positive_count"]),
                "composition_positive_count": int(row["composition_positive_count"]),
            }
            for row in space_rows
        },
        "primary_result": {
            "expanded_space_improves_over_ECA": expanded_best_confirmed > eca_confirmed or relation_improved or asym_improved or comp_recovered,
            "robust_persistence_confirmed": expanded_best_confirmed > 0,
            "relation_load_bearing_improved": relation_improved,
            "asymmetry_load_bearing_improved": asym_improved,
            "composition_recovered": comp_recovered,
            "controls_rejected": controls_rejected,
            "control_leak_count_by_space": {k: int(v) for k, v in control_leak_count_by_space.items()},
        },
        "top_candidates": top_candidates,
        "best_candidate_profile": {
            "space": b.get("space"),
            "rule_id": b.get("rule_id"),
            "stratum": b.get("stratum"),
            "motif_type": None,
            "recurrence_up_to_shift": b.get("recurrence_up_to_shift"),
            "material_turnover_rate": b.get("motif_material_turnover"),
            "background_contrast": b.get("background_contrast"),
            "post_perturbation_survival_rate": b.get("post_perturbation_survival_rate"),
            "relation_dependence_delta": b.get("relation_dependence_delta"),
            "asymmetry_dependence_delta": b.get("asymmetry_dependence_delta"),
            "composition_outcome": b.get("dominant_interaction_outcome"),
            "future_distinct_descendant_count": b.get("future_distinct_descendant_count"),
            "frozen_order_index": b.get("frozen_order_index"),
            "chaos_index": b.get("chaos_index"),
        },
        "recommendation": recommendation,
        "next_probe": next_probe,
        "estimator_warnings": [],
    }
    clean_summary = json_sanitize(summary)
    (cfg.out_dir / "summary.json").write_text(json.dumps(clean_summary, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(clean_summary, indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
