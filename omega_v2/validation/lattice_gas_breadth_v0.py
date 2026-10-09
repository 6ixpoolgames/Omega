"""Exact rooted FHP-I breadth versus invariant uniform gas references."""

import json
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.sparse.csgraph import connected_components
from scipy.special import logsumexp

from omega_v2.finite.lattice_gas import VELOCITIES, conserved, decode, encode, exact_sector


def preparations(side):
    pair_sites = [(0, 0), (1, 1)]
    collide = [(x, y, d) for x, y in pair_sites for d in (0, 3)]
    aimed = [((x-VELOCITIES[d][0]) % side, (y-VELOCITIES[d][1]) % side, d)
             for (x, y), ds in zip(pair_sites, ((0, 3), (1, 4)), strict=True) for d in ds]
    return {
        "two_colliding_pairs": encode(collide, side),
        "aimed_pairs": encode(aimed, side),
        "separated_counterstreams": encode([(0, 0, 0), (0, 1, 0), (0, 2, 3), (1, 2, 3)], side),
        "packed_four": encode([(0, 0, d) for d in (0, 1, 3, 4)], side),
    }


def probe(side):
    start = perf_counter()
    states, index, p, checks = exact_sector(side)
    print(f"side={side}: sector {len(states)} states, {p.nnz} branches", flush=True)
    ncomp, labels = connected_components(p, directed=True, connection="strong")
    # All states of a finite doubly-stochastic law belong to closed components.
    rows = np.repeat(np.arange(len(states)), np.diff(p.indptr))
    checks["cross_component_edges"] = int(np.count_nonzero(labels[rows] != labels[p.indices]))
    assert checks["cross_component_edges"] == 0
    sizes = np.bincount(labels)
    log_p = p.copy()
    log_p.data = np.log(p.data)
    h = -np.asarray(p.multiply(log_p).sum(axis=1)).ravel()
    roots = preparations(side)
    assert all(conserved(s, side) == (4, 0, 0) for s in roots.values())
    lookup = {name: index[s] for name, s in roots.items()}
    ell = np.zeros(len(states))
    counts = [1]*len(states)
    neighbors = [p.indices[p.indptr[i]:p.indptr[i+1]].tolist() for i in range(len(states))]
    root_rows, summaries = [], []
    max_stationary_error = 0.
    for n in range(65):
        if n in (0, 1, 2, 4, 8, 16, 32, 64):
            gas_mean = float(ell.mean())
            comp_means = np.bincount(labels, weights=ell)/sizes
            summaries.append({"horizon": n, "mean_log_breadth": gas_mean,
                "log_mean_breadth": float(logsumexp(ell)-np.log(len(states))),
                "log_breadth_quantiles": np.quantile(ell, [0, .1, .5, .9, 1]).tolist(),
                "fraction_above_mean_log_breadth": float(np.mean(ell > gas_mean+1e-12)),
                "maximum_root_configuration_posthoc": decode(states[int(ell.argmax())], side)})
            for name, i in lookup.items():
                root_rows.append({"name": name, "horizon": n, "log_breadth": float(ell[i]),
                    "breadth": float(np.exp(ell[i])), "support_count": str(counts[i]),
                    "delta_vs_sector_mean_log": float(ell[i]-gas_mean),
                    "delta_vs_sector_log_mean_breadth":
                        float(ell[i]-summaries[-1]["log_mean_breadth"]),
                    "component_states": int(sizes[labels[i]]),
                    "delta_vs_component_mean_log": float(ell[i]-comp_means[labels[i]]),
                    "delta_vs_component_log_mean_breadth": float(ell[i]
                        -logsumexp(ell[labels == labels[i]])+np.log(sizes[labels[i]])),
                    "sector_percentile_midrank": float((np.count_nonzero(ell < ell[i]-1e-12)
                        +.5*np.count_nonzero(np.abs(ell-ell[i]) <= 1e-12))/len(states))})
            max_stationary_error = max(max_stationary_error, abs(gas_mean-n*float(h.mean())))
        if n == 64:
            break
        ell = h+p @ ell
        counts = [sum(counts[j] for j in row) for row in neighbors]
    checks["equilibrium_entropy_identity_error"] = max_stationary_error
    checks["local_coin_entropy_error"] = float(np.max(np.abs(h/np.log(2)-np.rint(h/np.log(2)))))
    assert max_stationary_error < 1e-10
    assert checks["row_error"] < 1e-12 and checks["column_error"] < 1e-12
    return {"side": side, "sites": side*side, "particles": 4,
            "momentum": [0, 0], "states": len(states), "branches": p.nnz,
            "components": int(ncomp), "largest_component": int(sizes.max()),
            "mean_equilibrium_collision_bits_per_tick": float(h.mean()/np.log(2)),
            "root_configurations": {name: decode(s, side) for name, s in roots.items()},
            "checks": checks, "sector_profiles": summaries, "root_profiles": root_rows,
            "seconds": perf_counter()-start}


def run():
    out = Path("docs/research_notes/omega_v2/lattice_gas_breadth_v0")
    out.mkdir(parents=True, exist_ok=True)
    for side in (3, 4):
        result = probe(side)
        (out/f"side{side}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps({k: result[k] for k in ("side", "states", "components", "checks", "seconds")}),
              flush=True)


if __name__ == "__main__":
    run()
