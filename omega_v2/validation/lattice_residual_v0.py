"""Exact small-square residual atlas using the unchanged lattice chemistry."""

import os

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"

import argparse
import gzip
import hashlib
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy.sparse import save_npz
from scipy.sparse.csgraph import connected_components

from omega_v2.finite.lattice_chemistry import Parameters
from omega_v2.finite.lattice_residual import (
    counted_generator,
    exact_square,
    jump_distribution,
    preparations,
    propagate_with_events,
    support_profiles,
    two_forward_bindings,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2/lattice_residual_v0"
CUTS, LAGS, DEPTH = (0, 1, 5, 20), (.25, 1, 4), 8


def job(task):
    config, out = task
    start = time.perf_counter()
    folder = Path(out) / f"g{config['id']:02d}"
    folder.mkdir()
    square = exact_square(Parameters(**config["parameters"]))
    q, states = square["q"], square["states"]
    n = len(states)
    support = support_profiles(square["unique"], square["multiplicity"], DEPTH)
    initial = preparations(square)
    names = list(initial)
    laws = np.stack(list(initial.values()), axis=1)
    views = [square["model"].snapshot(s) for s in states]
    fields = ("bonds", "fuel", "exposed", "components", "largest", "energy",
              "free_energy_of_state", "template_opportunities")
    observable = {k: np.array([v[k] for v in views]) for k in fields}
    enabled = np.diff(square["multiplicity"].indptr)
    channel_count = np.asarray(square["multiplicity"].sum(axis=1)).ravel()
    law_blocks, cut_rows = [], []
    for cut in CUTS:
        p, events = propagate_with_events(q, laws, cut)
        law_blocks.append(p)
        for j, name in enumerate(names):
            cut_rows.append({"cut": cut, "preparation": name, "mean_events_before_cut": float(events[j]),
                             "physical": {k: float(v @ p[:, j]) for k, v in observable.items()},
                             "enabled_successors": float(enabled @ p[:, j]),
                             "enabled_channels": float(channel_count @ p[:, j]),
                             "event_rate": float(square["escape"] @ p[:, j]),
                             "support": {k: (v @ p[:, j]).tolist() for k, v in support.items()}})
    columns = np.hstack(law_blocks)
    generator = counted_generator(q, DEPTH)
    residual_rows, mass_errors, negative_errors = [], [], []
    for lag in LAGS:
        layers, tail = jump_distribution(generator, columns, lag, DEPTH)
        endpoint, mean_events = propagate_with_events(q, columns, lag)
        jump_mass = layers.sum(axis=1)
        two_bindings = two_forward_bindings(square, lag) @ columns
        np.savez_compressed(folder / f"residual_lag{lag:g}.npz", layers=layers, overflow=tail,
                            endpoint=endpoint, mean_events=mean_events)
        mass_errors.append(float(np.max(np.abs(jump_mass.sum(axis=0) + tail - 1))))
        negative_errors.append(float(min(layers.min(), tail.min(), endpoint.min())))
        for j, row in enumerate(cut_rows):
            # Exact prefix-cylinder mass at depth d is P(N>=d), no rescaling.
            at_least = 1 - np.concatenate(([0.], np.cumsum(jump_mass[:-1, j])))
            residual_rows.append({"cut": row["cut"], "preparation": row["preparation"], "lag": lag,
                                  "jump_probabilities_0_to_depth": jump_mass[:, j].tolist(),
                                  "overflow_probability": float(tail[j]),
                                  "prefix_mass_0_to_depth": at_least.tolist(),
                                  "weighted_prefix_count_through_depth": float(at_least.sum()),
                                  "weighted_prefix_count_all_depths": float(1 + mean_events[j]),
                                  "mean_future_events": float(mean_events[j]),
                                  "two_next_jumps_fuel_bind": float(two_bindings[j]),
                                  "endpoint_physical": {k: float(v @ endpoint[:, j])
                                                        for k, v in observable.items()}})
    pi = square["equilibrium"]
    flux = q.multiply(pi[:, None])
    balance = flux - flux.T
    diagnostics = {"row_sum_error": float(np.max(np.abs(np.asarray(q.sum(axis=1))))),
                   "detailed_balance_error": float(np.max(np.abs(balance.data), initial=0)),
                   "stationary_error": float(np.max(np.abs(q.T @ pi))),
                   "probability_mass_error": max(mass_errors), "minimum_probability": min(negative_errors),
                   "communicating_classes": int(connected_components(q, directed=True, connection="strong")[0])}
    if diagnostics["probability_mass_error"] > 1e-10 or diagnostics["minimum_probability"] < -1e-12:
        raise AssertionError(diagnostics)
    save_npz(folder / "generator.npz", q)
    np.savez_compressed(folder / "laws_support.npz", initial=laws, cut_laws=columns, **support)
    raw = {"parameters": config["parameters"], "states": [s.record() for s in states],
           "channels": square["channels"], "preparations": names,
           "column_order": [{"cut": r["cut"], "preparation": r["preparation"]} for r in cut_rows]}
    (folder / "states_channels.json.gz").write_bytes(gzip.compress(json.dumps(raw).encode(), mtime=0))
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()}
    return {**config, "states": n, "state_edges": square["unique"].nnz,
            "channels": sum(len(c) for c in square["channels"]), "cuts": cut_rows,
            "residuals": residual_rows, "diagnostics": diagnostics, "files_sha256": hashes,
            "runtime_seconds": time.perf_counter() - start}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    if not 1 <= args.workers <= 10:
        parser.error("Use one to ten processes")
    args.out.mkdir(parents=True, exist_ok=True)
    if (args.out / "manifest.json").exists():
        raise RuntimeError("Existing results are protected; choose a fresh --out")
    configs = []
    for capacity in (1, 4):
        for strength in (0., 2.):
            for barrier in (0., 2.):
                configs.append({"id": len(configs), "parameters": asdict(Parameters(
                    side=2, particles=4, capacity=capacity, bond_strength=strength,
                    catalytic_barrier=barrier))})
    files = [Path(__file__), ROOT / "omega_v2/finite/lattice_residual.py",
             ROOT / "omega_v2/finite/lattice_chemistry.py",
             ROOT / "docs/research_notes/omega_v2/lattice_residual_protocol_v0.md"]
    manifest = {"regimes": configs, "cuts": CUTS, "lags": LAGS, "depth": DEPTH,
                "workers": args.workers, "source_sha256": {str(p.relative_to(ROOT)):
                hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    started, results = time.perf_counter(), []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(job, (c, str(args.out))) for c in configs]
        for f in as_completed(futures):
            result = f.result()
            results.append(result)
            print(f"Regime {result['id']} done: {result['states']} states; "
                  f"{time.perf_counter()-started:.1f}s elapsed", flush=True)
    results.sort(key=lambda r: r["id"])
    output = {"regimes": results, "runtime_seconds": time.perf_counter() - started}
    (args.out / "summary.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({"runtime_seconds": output["runtime_seconds"], "regimes": len(results)}), flush=True)


if __name__ == "__main__":
    main()
