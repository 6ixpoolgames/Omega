"""Small contribution panel under unchanged reversible 2D chemistry."""

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

from omega_v2.finite.lattice_chemistry import LatticeChemistry, Parameters
from omega_v2.finite.lattice_damage import state_from_record
from omega_v2.finite.lattice_equilibrium import sample_chain, split_rhat
from omega_v2.finite.lattice_history_profile import history_profile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2/lattice_corridor_v0"
CUTS = (0, 1, 5, 10, 20)
PREPARATIONS = ("equilibrium", "refueled_equilibrium", "dispersed_fueled")


def write_gzip(path, value):
    data = json.dumps(value, separators=(",", ":")).encode()
    path.write_bytes(gzip.compress(data, mtime=0))
    return hashlib.sha256(data).hexdigest()


def equilibrium_job(task):
    config, chain, settings, directory = task
    started = time.perf_counter()
    model = LatticeChemistry(Parameters(**config["parameters"]))
    seed = 5_000_000 + 1000*config["id"] + chain
    result = sample_chain(model, seed, compact_start=bool(chain % 2), **settings)
    result.update({"regime": config["id"], "chain": chain,
                   "parameters": config["parameters"], "runtime_seconds": time.perf_counter()-started})
    name = f"eq_g{config['id']:02d}_c{chain}.json.gz"
    digest = write_gzip(Path(directory)/name, result)
    views = [model.snapshot(state_from_record(s)) for s in result["states"]]
    return {"regime": config["id"], "chain": chain, "archive": name,
            "sha256": digest, "views": views,
            "relocation_acceptance_given_vacancy": result["relocation_acceptance_given_vacancy"]}


def dynamics_job(task):
    config, barrier, preparation, chain, archive, directory = task
    model = LatticeChemistry(Parameters(**{**config["parameters"], "catalytic_barrier": barrier}))
    equilibrium = json.loads(gzip.decompress((Path(directory)/archive).read_bytes()))
    rows, trajectories = [], []
    for sample, record in enumerate(equilibrium["states"]):
        initial = state_from_record(record)
        if preparation == "refueled_equilibrium":
            initial.fuel = model.p.capacity
        elif preparation == "dispersed_fueled":
            seed = 6_000_000 + config["id"]*10000 + chain*100 + sample
            initial = model.initial(seed)
        sequence = [20261005, config["id"], int(barrier),
                    PREPARATIONS.index(preparation), chain, sample]
        seed = int(np.random.SeedSequence(sequence).generate_state(1)[0])
        trajectory = model.simulate(initial, seed, cuts=CUTS)
        history = history_profile(model, trajectory, CUTS)
        trajectory["history_profile"] = history
        trajectory.update({"preparation": preparation, "chain": chain, "sample": sample})
        trajectories.append(trajectory)
        rows.append({"sample": sample, "events": len(trajectory["events"]),
                     "cuts": [{**a, **b} for a, b in zip(trajectory["snapshots"], history, strict=True)]})
    name = f"g{config['id']:02d}_b{int(barrier)}_{preparation}_c{chain}.json.gz"
    digest = write_gzip(Path(directory)/name, trajectories)
    return {"regime": config["id"], "barrier": barrier, "preparation": preparation,
            "chain": chain, "runs": rows, "archive": name, "sha256": digest}


def aggregate(groups):
    result = []
    for key in sorted({(r["regime"], r["barrier"], r["preparation"]) for r in groups}):
        subset = [r for r in groups if (r["regime"], r["barrier"], r["preparation"]) == key]
        cuts = []
        for j, cut in enumerate(CUTS):
            names = [k for k in subset[0]["runs"][0]["cuts"][j] if k != "time"]
            chain_means = {k: [float(np.mean([v["cuts"][j][k] for v in r["runs"]]))
                              for r in subset] for k in names}
            cuts.append({"time": cut,
                         "mean": {k: float(np.mean(v)) for k, v in chain_means.items()},
                         "chain_se": {k: float(np.std(v, ddof=1)/np.sqrt(len(v)))
                                      for k, v in chain_means.items()},
                         "chain_means": chain_means})
        result.append({"regime": key[0], "barrier": key[1], "preparation": key[2],
                       "replicates": sum(len(r["runs"]) for r in subset), "cuts": cuts})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--samples", type=int, default=24, help="Per equilibrium chain")
    parser.add_argument("--burn", type=int, default=4000)
    parser.add_argument("--spacing", type=int, default=128)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    if not 1 <= args.workers <= 10 or args.samples < 4 or args.burn < 0 or args.spacing < 1:
        parser.error("Invalid workers or equilibrium sample settings")
    args.out.mkdir(parents=True, exist_ok=True)
    if (args.out/"manifest.json").exists():
        raise RuntimeError("Output exists; preserve it and choose a new directory")
    configs = []
    for side in (8, 7, 6):
        for strength in (1.0, 2.0, 3.0):
            configs.append({"id": len(configs), "density": 16/side**2,
                            "parameters": asdict(Parameters(side=side, particles=16, capacity=16,
                                                            bond_strength=strength))})
    settings = {"samples": args.samples, "burn_sweeps": args.burn, "spacing": args.spacing}
    sources = [Path(__file__)] + [ROOT/"omega_v2/finite"/s for s in
                                 ("lattice_chemistry.py", "lattice_equilibrium.py",
                                  "lattice_history_profile.py", "lattice_damage.py")]
    manifest = {"regimes": configs, "barriers": [0, 1, 2], "preparations": PREPARATIONS,
                "cuts": CUTS, "workers": args.workers, "chains": 4, "sampler": settings,
                "equilibrium_status": "Finite MCMC sampling from analytic target; diagnostics required",
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sources}}
    (args.out/"manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    start, eq_rows = time.perf_counter(), []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(equilibrium_job, (c, chain, settings, str(args.out)))
                   for c in configs for chain in range(4)]
        for f in as_completed(futures):
            eq_rows.append(f.result())
            print(f"Equilibrium chains {len(eq_rows)}/36; {time.perf_counter()-start:.1f}s", flush=True)
        eq_rows.sort(key=lambda r: (r["regime"], r["chain"]))
        diagnostics = []
        for c in configs:
            selected = [r for r in eq_rows if r["regime"] == c["id"]]
            diagnostics.append({"regime": c["id"], "split_rhat": {
                k: split_rhat([[v[k] for v in r["views"]] for r in selected])
                for k in ("bonds", "contacts", "exposed", "largest", "energy")}})
        (args.out/"equilibrium.json").write_text(json.dumps(
            {"chains": eq_rows, "diagnostics": diagnostics, "seconds": time.perf_counter()-start},
            indent=2), encoding="utf-8")
        tasks = [(configs[r["regime"]], b, p, r["chain"], r["archive"], str(args.out))
                 for r in eq_rows for b in (0, 1, 2) for p in PREPARATIONS]
        rows = []
        futures = [pool.submit(dynamics_job, task) for task in tasks]
        for f in as_completed(futures):
            rows.append(f.result())
            if len(rows) % 18 == 0 or len(rows) == len(tasks):
                print(f"History batches {len(rows)}/{len(tasks)}; "
                      f"{time.perf_counter()-start:.1f}s", flush=True)
    rows.sort(key=lambda r: (r["regime"], r["barrier"], r["preparation"], r["chain"]))
    summary = {"runtime_seconds": time.perf_counter()-start, "groups": aggregate(rows),
               "batches": rows, "equilibrium_diagnostics": diagnostics,
               "trajectories": sum(len(r["runs"]) for r in rows),
               "events": sum(v["events"] for r in rows for v in r["runs"])}
    (args.out/"summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("runtime_seconds", "trajectories", "events")}), flush=True)


if __name__ == "__main__":
    main()
