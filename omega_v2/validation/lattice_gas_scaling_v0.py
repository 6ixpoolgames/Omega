"""Bounded Monte Carlo complete-future breadth, density and re-rooting probe."""

import json
from pathlib import Path
from time import perf_counter

import numpy as np

from omega_v2.finite.lattice_gas import PAIRS, VELOCITIES, encode, successors
from omega_v2.finite.lattice_gas_sampling import from_bitstates, step_batch

HORIZONS = (1, 4, 16, 32, 64, 128)
SAMPLES = 512
CUTS = (16, 64)
OUT = Path("results/local_runs/lattice_gas_scaling_v0")


def statistics(values):
    values = np.asarray(values, dtype=float)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / np.sqrt(values.size)) if values.size > 1 else 0.
    return {"mean": mean, "se": se, "ci95": [mean-1.96*se, mean+1.96*se]}


def uniform_sector(side, number, samples, rng):
    """Uniform fixed-N slot subsets, conditioned on exact zero vector momentum."""
    slots = 6*side*side
    velocities = np.array(VELOCITIES)
    accepted, attempts = [], 0
    while sum(len(a) for a in accepted) < samples:
        scores = rng.random((512, slots))
        selected = np.argpartition(scores, number-1, axis=1)[:, :number]
        momenta = velocities[selected % 6].sum(axis=1)
        chosen = selected[np.all(momenta == 0, axis=1)]
        accepted.append(chosen)
        attempts += 512
    selected = np.concatenate(accepted)[:samples]
    masks = np.zeros((samples, side*side), dtype=np.uint8)
    for row, occupied in enumerate(selected):
        np.bitwise_or.at(masks[row], occupied//6, (1 << (occupied % 6)).astype(np.uint8))
    return masks.reshape(samples, side, side), attempts


def preparations(side, density):
    grid, streams = [], []
    for y in range(side):
        for x in range(side):
            active = (x % 2 == 0 and y % 2 == 0) if density == .5 else (x+y) % 2 == 0
            if active:
                d = (x+y) % 3
                grid.extend([(x, y, d), (x, y, d+3)])
            if density == 1 or x % 2 == 0:
                streams.append((x, y, 0 if y < side//2 else 3))
    aimed = [((x-VELOCITIES[d][0]) % side, (y-VELOCITIES[d][1]) % side, d)
             for x, y, d in grid]
    return {name: from_bitstates([encode(particles, side)], side)[0]
            for name, particles in (("pair_grid", grid), ("aimed_grid", aimed),
                                    ("counterstreams", streams))}


def rollout(states, ticks, rng, save_cuts=()):
    states = states.copy()
    totals = np.zeros((len(states), ticks+1), dtype=np.int64)
    saved = {}
    for t in range(ticks):
        states, count = step_batch(states, rng)
        totals[:, t+1] = totals[:, t] + count
        if t+1 in save_cuts:
            saved[t+1] = states[:16].copy()
    return totals, saved


def reroot(states, rng):
    # 16 outer presents, 64 fresh continuations each, clustered uncertainty.
    totals, _ = rollout(np.repeat(states, 64, axis=0), 32, rng)
    samples = totals[:, -1].reshape(len(states), 64)
    means = samples.mean(axis=1)
    return {"aggregate": statistics(means), "root_estimates": means.tolist(),
            "root_mc_se": (samples.std(axis=1, ddof=1)/8).tolist(),
            "root_count": len(states), "continuations_per_root": 64,
            "range": [float(means.min()), float(means.max())]}


def exact_check():
    root = encode([(0, 0, 0), (0, 0, 3), (1, 1, 0), (1, 1, 3)], 3)
    law, expected = {root: 1.}, 0.
    for _ in range(8):
        next_law = {}
        for state, weight in law.items():
            expected += weight*sum(((state >> (6*i)) & 63) in PAIRS for i in range(9))
            for target, p in successors(state, 3).items():
                next_law[target] = next_law.get(target, 0.) + weight*p
        law = next_law
    totals, _ = rollout(from_bitstates([root]*8192, 3), 8, np.random.default_rng(721))
    estimate = statistics(totals[:, -1])
    assert abs(estimate["mean"]-expected) < max(6*estimate["se"], 1e-10)
    return {"exact_bits": expected, "sample": estimate}


def main():
    started = perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    result = {"seed": 20261007, "samples": SAMPLES, "exact_check": exact_check(), "panels": []}
    rng = np.random.default_rng(result["seed"])
    for side in (6, 12):
        for density in (.5, 1.):
            number = int(side*side*density)
            gas, attempts = uniform_sector(side, number, SAMPLES, rng)
            panel = {"side": side, "density": density, "particles": number,
                     "reference_sampling_attempts": attempts,
                     "stationary_bits_per_tick": statistics(np.isin(gas, PAIRS).sum(axis=(1, 2))),
                     "cases": {}}
            batches = {"thermal": gas}
            batches.update({name: np.repeat(root[None], SAMPLES, axis=0)
                            for name, root in preparations(side, density).items()})
            raw = {}
            for name, batch in batches.items():
                totals, saved = rollout(batch, 128, rng, CUTS)
                raw[name] = totals
                case = {"breadth_bits": {str(h): statistics(totals[:, h]) for h in HORIZONS},
                        "late_bits_per_tick": statistics((totals[:, 128]-totals[:, 64])/64),
                        "reroot": {str(cut): reroot(states, rng) for cut, states in saved.items()}}
                # Cut zero uses the same exact-root projections already sampled.
                case["reroot"]["0"] = {"aggregate": statistics(totals[:, 32]),
                                        "note": "original 512-root/trajectory sample"}
                panel["cases"][name] = case
            ref = panel["cases"]["thermal"]
            for name, case in panel["cases"].items():
                if name == "thermal":
                    continue
                case["excess_bits"] = {}
                for h in HORIZONS:
                    a, b = case["breadth_bits"][str(h)], ref["breadth_bits"][str(h)]
                    se = float(np.hypot(a["se"], b["se"]))
                    mean = a["mean"]-b["mean"]
                    case["excess_bits"][str(h)] = {"mean": mean, "se": se,
                                                     "ci95": [mean-1.96*se, mean+1.96*se]}
            np.savez_compressed(OUT/f"side{side}_density{density}.npz", **raw)
            result["panels"].append(panel)
            print(f"side={side} density={density} complete ({perf_counter()-started:.1f}s)", flush=True)
    result["seconds"] = perf_counter()-started
    (OUT/"summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Saved {OUT/'summary.json'}", flush=True)


if __name__ == "__main__":
    main()
