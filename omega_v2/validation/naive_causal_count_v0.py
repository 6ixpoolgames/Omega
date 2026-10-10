"""Replay prior histories and sample a dilute bracket for naive causal counts."""

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
from math import log2
from pathlib import Path

import numpy as np

from omega_v2.finite.lattice_causal_count import causal_count
from omega_v2.finite.lattice_chemistry import LatticeChemistry, Parameters
from omega_v2.finite.lattice_damage import state_from_record
from omega_v2.finite.lattice_equilibrium import split_rhat
from omega_v2.validation.lattice_corridor_v0 import (
    CUTS,
    PREPARATIONS,
    ROOT,
    equilibrium_job,
    write_gzip,
)

SOURCE = ROOT / "docs/research_notes/omega_v2/lattice_corridor_v0"
OUT = ROOT / "docs/research_notes/omega_v2/naive_causal_count_v0"
GRAPHS = ("full", "without_fuel_register")


def count_batch(trajectories):
    runs, records = [], []
    for trajectory in trajectories:
        model = LatticeChemistry(Parameters(**trajectory["parameters"]))
        count = causal_count(model, trajectory, CUTS)
        runs.append({"sample": trajectory["sample"], "events": len(trajectory["events"]),
                     "graphs": {g: count[g] for g in GRAPHS},
                     "physical": trajectory["snapshots"]})
        records.append({"sample": trajectory["sample"], **count})
    return runs, records


def replay_job(task):
    batch, source, out = task
    data = gzip.decompress((Path(source) / batch["archive"]).read_bytes())
    if hashlib.sha256(data).hexdigest() != batch["sha256"]:
        raise AssertionError("Source archive differs from its manifest")
    runs, records = count_batch(json.loads(data))
    digest = write_gzip(Path(out) / batch["archive"], records)
    return {k: batch[k] for k in ("regime", "barrier", "preparation", "chain")} | {
        "panel": "corridor", "archive": batch["archive"], "sha256": digest,
        "source_sha256": batch["sha256"], "runs": runs}


def dilute_job(task):
    config, barrier, preparation, chain, archive, directory = task
    model = LatticeChemistry(Parameters(**{**config["parameters"], "catalytic_barrier": barrier}))
    equilibrium = json.loads(gzip.decompress((Path(directory) / archive).read_bytes()))
    trajectories = []
    for sample, record in enumerate(equilibrium["states"]):
        initial = state_from_record(record)
        if preparation == "refueled_equilibrium":
            initial.fuel = model.p.capacity
        elif preparation == "dispersed_fueled":
            initial = model.initial(8_000_000 + 10000 * config["id"] + 100 * chain + sample)
        seed = int(np.random.SeedSequence([20261005, 91, config["id"], int(barrier),
                   PREPARATIONS.index(preparation), chain, sample]).generate_state(1)[0])
        trajectory = model.simulate(initial, seed, cuts=CUTS)
        trajectory.update({"preparation": preparation, "chain": chain, "sample": sample})
        trajectories.append(trajectory)
    name = f"g{config['id']:02d}_b{barrier}_{preparation}_c{chain}.json.gz"
    trajectory_digest = write_gzip(Path(directory) / name, trajectories)
    runs, records = count_batch(trajectories)
    graph_name = "graph_" + name
    digest = write_gzip(Path(directory) / graph_name, records)
    return {"panel": "dilute", "regime": config["id"], "barrier": barrier,
            "preparation": preparation, "chain": chain, "runs": runs,
            "archive": graph_name, "sha256": digest,
            "trajectory_archive": name, "trajectory_sha256": trajectory_digest}


def aggregate(batches):
    output = []
    keys = ("panel", "regime", "barrier", "preparation")
    for key in sorted({tuple(b[k] for k in keys) for b in batches}):
        subset = sorted([b for b in batches if tuple(b[k] for k in keys) == key],
                        key=lambda b: b["chain"])
        item = dict(zip(keys, key, strict=True))
        item["replicates"] = sum(len(b["runs"]) for b in subset)
        item["graphs"] = {}
        for graph in (*GRAPHS, "physical"):
            cuts = []
            for j, cut in enumerate(CUTS):
                def view(run, j=j, graph=graph):
                    return run["physical"][j] if graph == "physical" else run["graphs"][graph][j]
                names = [k for k in view(subset[0]["runs"][0]) if k not in ("time", "routes_exact")]
                means = {k: [float(np.mean([view(v)[k] for v in b["runs"]]))
                             for b in subset] for k in names}
                row = {"time": cut, "mean": {k: float(np.mean(v)) for k, v in means.items()},
                       "chain_se": {k: float(np.std(v, ddof=1) / np.sqrt(len(v)))
                                    for k, v in means.items()}, "chain_means": means}
                if graph != "physical":
                    route_sum = sum(int(view(v)["routes_exact"]) for b in subset for v in b["runs"])
                    row["log2_mean_routes"] = log2(route_sum) - log2(item["replicates"]) if route_sum else None
                cuts.append(row)
            item["graphs"][graph] = cuts
        output.append(item)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    if not 1 <= args.workers <= 10:
        parser.error("Use one to ten worker processes")
    args.out.mkdir(parents=True, exist_ok=True)
    if (args.out / "manifest.json").exists():
        raise RuntimeError("Output exists; choose another directory")
    for folder in ("corridor", "dilute"):
        (args.out / folder).mkdir(exist_ok=True)
    old = json.loads((SOURCE / "summary.json").read_text())
    configs = [{"id": i, "density": 16 / 144,
                "parameters": asdict(Parameters(side=12, bond_strength=float(i)))} for i in range(3)]
    settings = {"samples": 16, "burn_sweeps": 4000, "spacing": 128}
    sources = [Path(__file__), ROOT / "docs/research_notes/omega_v2/naive_causal_count_protocol_v0.md"]
    sources += [ROOT / "omega_v2/finite" / n for n in (
        "lattice_causal_count.py", "lattice_chemistry.py", "lattice_damage.py", "lattice_equilibrium.py")]
    sources += [ROOT / "omega_v2/validation/lattice_corridor_v0.py"]
    manifest = {"cuts": CUTS, "workers": args.workers, "dilute_regimes": configs,
                "barriers": [0, 1, 2], "preparations": PREPARATIONS, "sampler": settings,
                "source_corridor": str(SOURCE.relative_to(ROOT)),
                "source_summary_sha256": hashlib.sha256((SOURCE / "summary.json").read_bytes()).hexdigest(),
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sources}}
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    start, batches, eq_rows = time.perf_counter(), [], []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(replay_job, (b, str(SOURCE), str(args.out / "corridor")))
                   for b in old["batches"]]
        for f in as_completed(futures):
            batches.append(f.result())
            if len(batches) % 36 == 0:
                print(f"Replayed {len(batches)}/{len(futures)} batches; {time.perf_counter()-start:.1f}s", flush=True)
        futures = [pool.submit(equilibrium_job, (c, chain, settings, str(args.out / "dilute")))
                   for c in configs for chain in range(4)]
        for f in as_completed(futures):
            eq_rows.append(f.result())
            print(f"Dilute source chains {len(eq_rows)}/12; {time.perf_counter()-start:.1f}s", flush=True)
        eq_rows.sort(key=lambda r: (r["regime"], r["chain"]))
        diagnostics = []
        for config in configs:
            selected = [r for r in eq_rows if r["regime"] == config["id"]]
            diagnostics.append({"regime": config["id"], "split_rhat": {
                k: split_rhat([[v[k] for v in r["views"]] for r in selected])
                for k in ("bonds", "contacts", "exposed", "largest", "energy")}})
        (args.out / "equilibrium.json").write_text(json.dumps({"chains": eq_rows,
            "diagnostics": diagnostics}, indent=2), encoding="utf-8")
        tasks = [(configs[r["regime"]], b, p, r["chain"], r["archive"], str(args.out / "dilute"))
                 for r in eq_rows for b in (0, 1, 2) for p in PREPARATIONS]
        futures = [pool.submit(dilute_job, t) for t in tasks]
        for i, f in enumerate(as_completed(futures), 1):
            batches.append(f.result())
            if i % 12 == 0:
                print(f"New dilute batches {i}/{len(tasks)}; {time.perf_counter()-start:.1f}s", flush=True)
    batches.sort(key=lambda b: (b["panel"], b["regime"], b["barrier"], b["preparation"], b["chain"]))
    summary = {"runtime_seconds": time.perf_counter()-start, "groups": aggregate(batches),
               "trajectories": sum(len(b["runs"]) for b in batches),
               "events": sum(v["events"] for b in batches for v in b["runs"]),
               "equilibrium_diagnostics": diagnostics}
    write_gzip(args.out / "batches.json.gz", batches)
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("runtime_seconds", "trajectories", "events")}), flush=True)


if __name__ == "__main__":
    main()
