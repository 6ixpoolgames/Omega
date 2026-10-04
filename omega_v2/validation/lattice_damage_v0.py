"""Sample native failures from saved cuts and compare unmodified residual laws."""

import os

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"

import argparse
import gzip
import hashlib
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from omega_v2.finite.lattice_chemistry import LatticeChemistry, Parameters
from omega_v2.finite.lattice_damage import (
    native_failure,
    observe,
    probe_coordinates,
    squared_response,
    state_at,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/research_notes/omega_v2/lattice_chemistry_v0"
OUT = ROOT / "docs/research_notes/omega_v2/lattice_damage_v0"
CUTS = (0, 0.5, 2, 5)


def profiles(observations, coordinates):
    result, compact = [], []
    for j, lag in enumerate(CUTS):
        x, y = observations["broken"], observations["skipped"]
        readouts = {}
        for k in x[0][j]["readouts"]:
            a = np.array([o[j]["readouts"][k] for o in x])
            b = np.array([o[j]["readouts"][k] for o in y])
            readouts[k] = {"broken": float(a.mean()), "skipped": float(b.mean()),
                           "difference": float(a.mean() - b.mean()),
                           "conditional_se": float(np.sqrt(a.var(ddof=1)/len(a)
                                                             + b.var(ddof=1)/len(b)))}
        row = {"lag": lag, "readouts": readouts, "response": {}, "joint_recovery": {}}
        full = {"lag": lag, "marginal_laws": {}}
        for family, distances in (("cells", coordinates["cell_distances"]),
                                  ("edges", coordinates["edge_distances"])):
            a = np.array([o[j][family] for o in x])
            b = np.array([o[j][family] for o in y])
            full["marginal_laws"][family] = {
                "broken": a.mean(axis=0).tolist(), "skipped": b.mean(axis=0).tolist(),
                "difference": (a.mean(axis=0) - b.mean(axis=0)).tolist(),
                "conditional_se": np.sqrt(a.var(axis=0, ddof=1)/len(a)
                                          + b.var(axis=0, ddof=1)/len(b)).tolist()}
            for region in ("near", "far"):
                mask = np.array(distances) <= 1
                if region == "far":
                    mask = ~mask
                count = int(mask.sum())
                if count:
                    row["response"][f"{family}_{region}"] = squared_response(a[:, mask], b[:, mask]) / count
                    half = len(b) // 2
                    row["response"][f"sham_{family}_{region}"] = squared_response(
                        b[:half, mask], b[half:, mask]) / count
        for arm in ("broken", "skipped"):
            codes = [o[j]["joint_recovery_state"] for o in observations[arm]]
            row["joint_recovery"][arm] = (np.bincount(codes, minlength=4)/len(codes)).tolist()
        result.append({**row, **full})
        compact.append(row)
    return result, compact


def work(task):
    path, replicates, out = task
    started = time.perf_counter()
    source = json.loads(gzip.decompress(Path(path).read_bytes()))
    config, replicate = source["configuration_id"], source["replicate"]
    model = LatticeChemistry(Parameters(**source["parameters"]))
    before = state_at(model, source, 5)
    sampling_seed = 2_000_000 + config * 100 + replicate
    failure = native_failure(model, before, sampling_seed)
    result = {"configuration_id": config, "source_replicate": replicate,
              "parameters": source["parameters"], "preparation": source["preparation"],
              "source_trajectory": Path(path).name, "source_cut": 5,
              "source_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
              "failure_sampling_seed": sampling_seed, "total_hazard": failure["total_hazard"]}
    if failure["selected"] is None:
        result.update({"eligible": False, "cuts": [], "events": 0})
        return result
    pair = failure["selected"].members
    coordinates = probe_coordinates(model, before, pair)
    result.update({"eligible": True, "pair": pair,
                   **{k: v for k, v in failure.items() if k not in ("selected", "after")},
                   "replicates_per_arm": replicates})
    trajectories, observations = {}, {}
    for arm_id, (arm, initial) in enumerate((("broken", failure["after"]), ("skipped", before))):
        trajectories[arm], observations[arm] = [], []
        for r in range(replicates):
            seed = int(np.random.SeedSequence([20261004, config, replicate, arm_id, r]).generate_state(1)[0])
            trajectory = model.simulate(initial, seed, cuts=CUTS)
            trajectories[arm].append(trajectory)
            observations[arm].append(observe(model, trajectory, pair, coordinates, CUTS))
    full_profiles, compact = profiles(observations, coordinates)
    result["cuts"] = compact
    result["events"] = sum(len(t["events"]) for arm in trajectories.values() for t in arm)
    result["runtime_seconds"] = time.perf_counter() - started
    archive = {"context": result, "coordinates": coordinates, "full_profiles": full_profiles,
               "trajectories": trajectories}
    encoded = json.dumps(archive, separators=(",", ":")).encode()
    name = f"c{config:02d}_s{replicate:02d}.json.gz"
    (Path(out)/name).write_bytes(gzip.compress(encoded, mtime=0))
    result["archive"] = name
    result["archive_uncompressed_sha256"] = hashlib.sha256(encoded).hexdigest()
    return result


def summarize(rows):
    eligible = [r for r in rows if r["eligible"]]
    if not eligible:
        return {"contexts": len(rows), "eligible": 0,
                "mean_thermal_failure_rate": 0.0, "cuts": []}
    weights = np.array([r["total_hazard"] for r in eligible], float)
    weights /= weights.sum()
    out = {"contexts": len(rows), "eligible": len(eligible),
           "mean_thermal_failure_rate": sum(r["total_hazard"] for r in rows)/len(rows),
           "bridge_failure_share": float(weights @ [r["is_bridge"] for r in eligible]),
           "template_failure_share": float(weights @ [r["lost_template_formation_rate"] > 0
                                                       for r in eligible]), "cuts": []}
    for j, lag in enumerate(CUTS):
        item = {"lag": lag, "readouts": {}, "response": {}, "response_context_se": {}}
        for name in eligible[0]["cuts"][j]["readouts"]:
            item["readouts"][name] = {
                arm: float(weights @ [r["cuts"][j]["readouts"][name][arm] for r in eligible])
                for arm in ("broken", "skipped", "difference")}
            # Conditional MC error, given the empirical contexts and sampled failure edges.
            item["readouts"][name]["conditional_se"] = float(np.sqrt(sum(
                w*w*r["cuts"][j]["readouts"][name]["conditional_se"]**2
                for w, r in zip(weights, eligible, strict=True))))
        for name in eligible[0]["cuts"][j]["response"]:
            values = np.array([r["cuts"][j]["response"][name] for r in eligible])
            mean = float(weights @ values)
            item["response"][name] = mean
            denominator = 1 - float(weights @ weights)
            item["response_context_se"][name] = (
                float(np.sqrt(np.sum(weights**2 * (values - mean)**2) / denominator))
                if denominator > 1e-12 else None)
        out["cuts"].append(item)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--replicates", type=int, default=32)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--limit", type=int, default=0, help="Explicitly limited runtime pilot")
    args = parser.parse_args()
    if not 1 <= args.workers <= 10 or args.replicates < 4 or args.limit < 0:
        parser.error("Use 1-10 workers, at least four continuations per arm, nonnegative limit")
    args.out.mkdir(parents=True, exist_ok=True)
    if (args.out/"manifest.json").exists():
        raise RuntimeError("Output exists; use a new directory")
    source_summary = json.loads((SOURCE/"summary.json").read_text(encoding="utf-8"))
    tasks = [(str(SOURCE/r["trajectory"]), args.replicates, str(args.out))
             for r in source_summary["runs"]]
    if args.limit:
        tasks = tasks[:args.limit]
    manifest = {"source": "../lattice_chemistry_v0", "source_cut": 5, "lags": CUTS,
                "replicates_per_arm": args.replicates, "workers": args.workers,
                "source_contexts": len(tasks), "limit": args.limit,
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in (Path(__file__),
                                            ROOT/"omega_v2/finite/lattice_damage.py",
                                            ROOT/"omega_v2/finite/lattice_chemistry.py")}}
    (args.out/"manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    start, rows = time.perf_counter(), []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(work, task) for task in tasks]
        for f in as_completed(futures):
            rows.append(f.result())
            if len(rows) % 32 == 0 or len(rows) == len(tasks):
                print(f"Completed {len(rows)}/{len(tasks)} contexts; "
                      f"{time.perf_counter()-start:.1f}s", flush=True)
    rows.sort(key=lambda r: (r["configuration_id"], r["source_replicate"]))
    groups = {"all": summarize(rows)}
    for name, predicate in (
        ("bridge", lambda r: r["is_bridge"]),
        ("alternate", lambda r: not r["is_bridge"]),
        ("template", lambda r: r["lost_template_formation_rate"] > 0),
        ("non_template", lambda r: r["lost_template_formation_rate"] == 0),
    ):
        group = [r for r in rows if r["eligible"] and predicate(r)]
        if group:
            groups[name] = summarize(group)
    result = {"runtime_seconds": time.perf_counter()-start, "contexts": rows, "groups": groups,
              "configurations": {str(c): summarize([r for r in rows if r["configuration_id"] == c])
                                 for c in sorted({r["configuration_id"] for r in rows})}}
    (args.out/"summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"runtime_seconds": result["runtime_seconds"], "contexts": len(rows),
                      "residual_trajectories": sum(2*args.replicates for r in rows if r["eligible"]),
                      "events": sum(r["events"] for r in rows), "output": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
