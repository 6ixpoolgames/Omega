"""Exact transport limit and crossed mobile probe; generated data stay local."""

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
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from scipy.sparse import save_npz
from scipy.special import rel_entr

from omega_v2.finite.lattice_chemistry import LatticeChemistry, Parameters, State, logistic
from omega_v2.finite.lattice_compartment import CompartmentChemistry, Reservoir
from omega_v2.finite.lattice_equilibrium import sample_chain, split_rhat
from omega_v2.finite.lattice_history_atlas import HistoryAtlas, canonical_state, simulate_history
from omega_v2.finite.lattice_transport_exact import (
    diagnostics,
    exact_generator,
    lift_matrix,
    next_two_chemical_bindings,
    propagate,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2/lattice_refinement_v0"
CUTS = (0, .25, 1, 4, 10)


def write_json(path, value):
    path = Path(path)
    if path.suffix == ".gz":
        with gzip.open(path, "wt", encoding="utf8") as stream:
            json.dump(value, stream, separators=(",", ":"))
    else:
        path.write_text(json.dumps(value, indent=2), encoding="utf8")


def read_state(record):
    return State([tuple(p) for p in record["positions"]], list(record["internal"]),
                 {tuple(p) for p in record["bonds"]}, record["fuel"])


def initial_square(capacity):
    return State([(0, 0), (1, 0), (0, 1), (1, 1)], [1]*4, set(), capacity)


def save_exact(folder, exact):
    save_npz(folder / "generator.npz", exact["q"])
    np.savez_compressed(folder / "equilibrium.npz", probability=exact["pi"])
    write_json(folder / "physical_states_channels.json.gz",
               {"states": [s.record() for s in exact["states"]], "channels": exact["channels"]})


def exact_job(task):
    barrier, path = task
    start = time.perf_counter()
    folder = Path(path) / f"exact_b{barrier}"
    folder.mkdir()
    p = Parameters(side=2, particles=4, capacity=2, bond_strength=2, catalytic_barrier=barrier)
    initial = initial_square(2)
    shared = exact_generator(LatticeChemistry(p), initial)
    shared_dir = folder / "shared"
    shared_dir.mkdir()
    save_exact(shared_dir, shared)
    names = ["unbound", "seeded", "adjacent", "opposite", "equilibrium"]
    laws = np.zeros((len(shared["states"]), len(names)))
    for j, bonds in enumerate((set(), {(0, 1)}, {(0, 1), (0, 2)}, {(0, 1), (2, 3)})):
        s = initial.copy()
        s.bonds = bonds
        laws[shared["index"][canonical_state(s)[0].key()], j] = 1
    laws[:, -1] = shared["pi"]
    targets = {t: propagate(shared["q"], laws, t) for t in (.25, 1, 4)}
    shared_query = next_two_chemical_bindings(shared, 1)@laws
    np.savez_compressed(shared_dir / "laws.npz", initial=laws, query=shared_query,
                        **{f"t{t:g}": law for t, law in targets.items()})
    atlas = HistoryAtlas(shared["model"])
    prefixes = atlas.prefixes(initial, 2)
    write_json(shared_dir / "prefix_atlas.json.gz", {"atlas": atlas.record(), "prefixes": prefixes})
    rows = []
    for speed in (.05, 1, 20, 400):
        local_dir = folder / f"transport_{speed:g}"
        local_dir.mkdir()
        model = CompartmentChemistry(p, Reservoir(transport=speed))
        local = exact_generator(model, model.lift(initial, np.random.default_rng(904)))
        save_exact(local_dir, local)
        lift, project = lift_matrix(shared, local)
        p0 = lift@laws
        diag = diagnostics(local)
        diag["equilibrium_projection_error"] = float(np.max(np.abs(project@local["pi"]-shared["pi"])))
        averaged = project@local["q"].T@lift-shared["q"].T
        diag["averaged_generator_error"] = float(np.max(np.abs(averaged.data), initial=0))
        defect = project@local["q"].T-shared["q"].T@project
        diag["lumpability_defect"] = float(np.max(np.abs(defect.data), initial=0))
        query = next_two_chemical_bindings(local, 1)@p0
        arrays = {"initial": p0, "query": query}
        for t in (.25, 1, 4):
            pt = propagate(local["q"], p0, t)
            arrays[f"t{t:g}"] = pt
            projected = project@pt
            for j, name in enumerate(names):
                entropy = (rel_entr(p0[:, j], local["pi"]).sum()
                           - rel_entr(np.maximum(pt[:, j], 0), local["pi"]).sum())
                rows.append({"barrier": barrier, "transport": speed, "time": t, "preparation": name,
                             "tv_from_shared": float(np.abs(projected[:, j]-targets[t][:, j]).sum()/2),
                             "mass_error": float(abs(pt[:, j].sum()-1)),
                             "total_entropy_production": float(entropy),
                             "two_chemical_bindings_by_1": float(query[j]),
                             "shared_two_bindings_by_1": float(shared_query[j])})
        np.savez_compressed(local_dir / "laws.npz", **arrays)
        if max(diag["balance_error"], diag["equilibrium_projection_error"],
               diag["averaged_generator_error"]) > 1e-10:
            raise AssertionError(diag)
        write_json(local_dir / "checks.json", diag)
    if max(r["mass_error"] for r in rows) > 1e-9:
        raise AssertionError("Mass loss in exact propagation")
    result = {"barrier": barrier, "shared_checks": diagnostics(shared), "rows": rows,
              "shared_prefix_nodes_depth2": len(prefixes), "shared_cached_residuals": len(atlas.states),
              "seconds": time.perf_counter()-start}
    write_json(folder / "summary.json", result)
    return {"panel": "exact", **result}


def mean_se(values):
    values = np.asarray(values, dtype=float)
    return {"mean": float(values.mean()), "se": float(values.std(ddof=1)/np.sqrt(len(values)))}


def mobile_job(task):
    config, path, equilibrium = task
    start = time.perf_counter()
    folder = Path(path) / f"mobile_{config['id']:02d}"
    folder.mkdir()
    p = Parameters(side=4, particles=4, capacity=4, bond_strength=2,
                   catalytic_barrier=config["barrier"], mobility_exponent=config["gamma"])
    if config["transport"] is None:
        model = LatticeChemistry(p)
    else:
        model = CompartmentChemistry(p, Reservoir(transport=config["transport"]))
    atlas = HistoryAtlas(model)
    observations, event_count = [], 0
    for prep_index, name in enumerate(("dispersed_fueled", "seeded_fueled", "equilibrium", "refueled")):
        histories = []
        for replicate, record in enumerate(equilibrium):
            if prep_index < 2:
                state = LatticeChemistry(p).initial(5000+replicate,
                                                    "dispersed" if prep_index == 0 else "seeded")
            else:
                state = read_state(record)
                if prep_index == 3:
                    state.fuel = p.capacity
            if isinstance(model, CompartmentChemistry):
                state = model.lift(state, np.random.default_rng(6000+replicate+100*prep_index))
            seed = 1000000+config["id"]*10000+prep_index*1000+replicate
            trajectory = simulate_history(atlas, state, seed, CUTS)
            histories.append(trajectory)
            event_count += len(trajectory["events"])
        write_json(folder / f"{name}_histories.json.gz", histories)
        for k, t in enumerate(CUTS):
            rows = [h["snapshots"][k] for h in histories]
            fields = ("bonds", "fuel", "largest", "components", "template_opportunities",
                      "max_construction_depth", "live_construction_depth", "events")
            physical = {field: mean_se([r[field] for r in rows]) for field in fields}
            for field in ("move", "hop", "catalytic_forward", "catalytic_reverse",
                          "fuel_forward", "fuel_reverse", "thermal_forward", "thermal_reverse"):
                physical[field] = mean_se([r["counts"].get(field, 0) for r in rows])
            physical["chemical_events"] = mean_se([r["events"]-r["counts"].get("hop", 0) for r in rows])
            # Projected endpoint residual laws remain richer than these summaries;
            # all full residuals and enabled successors are archived separately.
            observations.append({"preparation": name, "cut": t, "physical": physical})
    write_json(folder / "atlas.json.gz", atlas.record())
    result = {"config": config, "parameters": asdict(p), "rows": observations,
              "histories": 4*len(equilibrium), "events": event_count,
              "cached_residuals": len(atlas.states), "seconds": time.perf_counter()-start,
              "dimensionless": {"isolated_exposed_probability": logistic(p.exposed_energy),
                                "one_template_enhancement": float(np.exp(p.catalytic_barrier)),
                                "capacity_per_particle": p.capacity/p.particles,
                                "switching_prefactor_per_hop_prefactor": p.switching/p.diffusion,
                                "thermal_prefactor_per_hop_prefactor": p.thermal_binding/p.diffusion}}
    write_json(folder / "summary.json", result)
    return {"panel": "mobile", **result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--samples-per-chain", type=int, default=12)
    args = parser.parse_args()
    if not 1 <= args.workers <= 10 or args.samples_per_chain < 2:
        parser.error("Use 1..10 workers and at least two samples per chain")
    start = time.perf_counter()
    folder = OUT / datetime.now(UTC).strftime("run_%Y%m%dT%H%M%SZ")
    folder.mkdir(parents=True)
    base = LatticeChemistry(Parameters(side=4, particles=4, capacity=4, bond_strength=2))
    chains = [sample_chain(base, 300+i, samples=args.samples_per_chain, burn_sweeps=4000,
                           spacing=128, compact_start=bool(i % 2)) for i in range(4)]
    eq = [s for c in chains for s in c["states"]]
    rhat = {f: split_rhat([[row[f] for row in c["trace"]] for c in chains])
            for f in ("bonds", "exposed", "largest", "log_weight")}
    write_json(folder / "equilibrium_chains.json.gz", chains)
    configs = [{"id": i, "barrier": b, "gamma": g, "transport": t}
               for i, (b, g, t) in enumerate((b, g, t) for b in (0, 2) for g in (1., .5)
                                             for t in (None, .1, 1., 10.))]
    source_paths = [Path(__file__), *[ROOT / "omega_v2/finite" / name for name in
                   ("lattice_chemistry.py", "lattice_compartment.py", "lattice_history_atlas.py",
                    "lattice_transport_exact.py", "lattice_equilibrium.py")]]
    manifest = {"configuration": configs, "cuts": CUTS, "workers": args.workers,
                "histories_per_preparation": len(eq), "equilibrium_rhat": rhat,
                "source_hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in source_paths}}
    for source in source_paths:
        archived = folder / "source" / source.relative_to(ROOT)
        archived.parent.mkdir(parents=True, exist_ok=True)
        archived.write_bytes(source.read_bytes())
    write_json(folder / "manifest.json", manifest)
    completed = []
    print(f"Output: {folder}", flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pending = [pool.submit(exact_job, (b, str(folder))) for b in (0, 2)]
        pending += [pool.submit(mobile_job, (c, str(folder), eq)) for c in configs]
        for future in as_completed(pending):
            result = future.result()
            completed.append(result)
            print(f"Completed {result['panel']} {len(completed)}/{len(pending)} "
                  f"({result['seconds']:.2f}s)", flush=True)
    result = {"manifest": manifest, "panels": completed, "seconds": time.perf_counter()-start}
    write_json(folder / "summary.json", result)
    print(f"Finished: {result['seconds']:.2f}s", flush=True)


if __name__ == "__main__":
    main()
