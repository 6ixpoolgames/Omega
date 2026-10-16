"""Exploratory 2D chemistry pilot; no lushness ranking or equilibrium-gas claim."""

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

from omega_v2.finite.lattice_chemistry import LatticeChemistry, Parameters, balance_residual

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "docs/research_notes/omega_v2/lattice_chemistry_v0"


def job(task):
    config, replicate, out = task
    started = time.perf_counter()
    parameters = Parameters(**config["parameters"])
    model = LatticeChemistry(parameters)
    # Same initial state across barrier/energy choices at fixed geometry/preparation/replicate.
    initial_seed = 100_000 + 1000 * config["geometry_id"] + replicate
    dynamics_seed = 900_000 + 1000 * config["id"] + replicate
    initial = model.initial(initial_seed, config["preparation"])
    balance = balance_residual(model, initial) if replicate == 0 else None
    result = model.simulate(initial, dynamics_seed)
    result.update({"configuration_id": config["id"], "preparation": config["preparation"],
                   "replicate": replicate, "initial_seed": initial_seed})
    path = Path(out) / f"c{config['id']:02d}_r{replicate:02d}.json.gz"
    encoded = json.dumps(result, separators=(",", ":")).encode()
    path.write_bytes(gzip.compress(encoded, mtime=0))
    return {"configuration_id": config["id"], "replicate": replicate,
            "snapshots": result["snapshots"], "events": len(result["events"]),
            "first_catalytic_construction": result["first_catalytic_construction"],
            "balance_residual": balance, "runtime_seconds": time.perf_counter() - started,
            "trajectory": path.name, "uncompressed_sha256": hashlib.sha256(encoded).hexdigest()}


def configurations():
    configs = []
    for geometry_id, (n, side) in enumerate(((16, 8), (36, 12), (16, 6), (36, 9))):
        for strength in (1.0, 3.0):
            for barrier in (0.0, 2.0):
                for preparation in ("dispersed", "seeded"):
                    p = Parameters(side=side, particles=n, capacity=n, bond_strength=strength,
                                   catalytic_barrier=barrier)
                    configs.append({"id": len(configs), "geometry_id": geometry_id,
                                    "preparation": preparation, "density": n / side**2,
                                    "parameters": asdict(p)})
    return configs


def aggregate(configs, rows):
    result = []
    for config in configs:
        group = [r for r in rows if r["configuration_id"] == config["id"]]
        entry = {**config, "replicates": len(group), "cuts": [],
                 "catalytic_construction_runs": sum(r["first_catalytic_construction"] is not None
                                                    for r in group),
                 "events_total": sum(r["events"] for r in group)}
        for cut in range(len(group[0]["snapshots"])):
            values = [r["snapshots"][cut] for r in group]
            entry["cuts"].append({
                "time": values[0]["time"],
                "mean": {k: float(np.mean([s[k] for s in values])) for k in values[0] if k != "time"},
                "standard_error": {k: float(np.std([s[k] for s in values], ddof=1) / np.sqrt(len(group)))
                                   if len(group) > 1 else None
                                   for k in values[0] if k != "time"},
            })
        result.append(entry)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--replicates", type=int, default=12)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    if not 1 <= args.workers <= 10 or args.replicates < 1:
        parser.error("Use 1-10 workers and positive replicates")
    args.out.mkdir(parents=True, exist_ok=True)
    if (args.out / "manifest.json").exists():
        raise RuntimeError("Output already exists; choose a new directory")
    configs = configurations()
    manifest = {"configurations": configs, "replicates": args.replicates,
                "workers": args.workers, "cuts": [0, 1, 5, 10, 20],
                "interpretation": "exploratory substrate pilot; no lushness score",
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in (Path(__file__),
                                            ROOT / "omega_v2/finite/lattice_chemistry.py")}}
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    tasks = [(c, r, str(args.out)) for c in configs for r in range(args.replicates)]
    started, rows = time.perf_counter(), []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(job, task) for task in tasks]
        for f in as_completed(futures):
            rows.append(f.result())
            if len(rows) % 32 == 0 or len(rows) == len(tasks):
                print(f"Completed {len(rows)}/{len(tasks)} trajectories; "
                      f"{time.perf_counter()-started:.1f}s", flush=True)
    rows.sort(key=lambda r: (r["configuration_id"], r["replicate"]))
    result = {"runtime_seconds": time.perf_counter() - started,
              "configurations": aggregate(configs, rows), "runs": rows}
    (args.out / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"runtime_seconds": result["runtime_seconds"], "runs": len(rows),
                      "events": sum(r["events"] for r in rows),
                      "max_balance_residual": max(r["balance_residual"] or 0 for r in rows),
                      "output": str(args.out)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
