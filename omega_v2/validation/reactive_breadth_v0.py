"""Exact sampled-path breadth on a closed, locally autocatalytic RDME patch."""

import json
from math import comb
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.linalg import expm
from scipy.sparse.csgraph import connected_components

from omega_v2.finite.closed_schlogl import build_model

OUT = Path("results/local_runs/reactive_breadth_v0")
ROOTS = {"ready": (0, 2, 1, 1, 0, 0), "separated": (1, 2, 0, 0, 0, 1)}


def integrate(q, observables, time):
    """Exact expected integrated event counts, no numerical time quadrature."""
    size = len(q)
    block = np.zeros((size+len(observables), size+len(observables)))
    block[:size, :size] = q
    block[:size, size:] = np.column_stack(observables)
    evolution = expm(time*block)
    return evolution[:size, :size], evolution[:size, size:]


def run():
    start = perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for d in (.1, 1., 10.):
        for k in (0., .1, 1., 10.):
            model = build_model(k, d)
            states, index, q, pi = (model[s] for s in ("states", "index", "q", "pi"))
            size = len(states)
            placement = np.zeros(size)
            for a in range(2):
                for x in range(3):
                    for b in range(2):
                        placement[index[(a, x, b, 1-a, 2-x, 1-b)]] = comb(2, x)/16
            assert np.isclose(placement.sum(), 1)
            sources = {name: np.eye(size)[index[root]] for name, root in ROOTS.items()}
            sources.update(thermal=pi, placement=placement)
            balance = np.max(np.abs(pi[:, None]*q-pi[None, :]*q.T))
            components, _ = connected_components(q > 0, directed=True, connection="strong")
            assert k == 0 or components == 1
            assert balance < 1e-10
            record = {"d": d, "k": k, "states": size, "components": components,
                      "balance_error": float(balance), "row_error": float(np.abs(q.sum(1)).max()),
                      "root_pi": {name: float(pi[index[root]]) for name, root in ROOTS.items()},
                      "physical": {}, "profiles": {}}
            observable_names = ("activity", "forward", "reverse")
            kernels = {}
            for time in (1, 4, 16):
                p, counts = integrate(q, [model["observables"][s] for s in observable_names], time)
                kernels[time] = p
                record["physical"][str(time)] = {
                    name: {**{r: float(rho@counts[:, j]) for j, r in enumerate(observable_names)},
                           "x_count": float(rho@p@model["observables"]["x_count"])}
                    for name, rho in sources.items()}
            for dt in (.05, .2, 1.):
                p = expm(dt*q)
                assert np.min(p) > -1e-12
                assert np.max(np.abs(p.sum(1)-1)) < 1e-10
                p = np.maximum(p, 0)
                logp = np.zeros_like(p)
                np.log2(p, out=logp, where=p > 0)
                h = -(p*logp).sum(1)
                ell = np.zeros(size)
                horizons = {round(time/dt): time for time in (1, 4, 16)}
                profiles = {}
                for step in range(1, max(horizons)+1):
                    ell = h+p@ell
                    if step in horizons:
                        time = horizons[step]
                        profiles[str(time)] = {name: float(rho@ell) for name, rho in sources.items()}
                        if time == 4:
                            profiles["fresh_at4_next4"] = {
                                name: float(rho@kernels[4]@ell) for name, rho in sources.items()}
                record["profiles"][str(dt)] = profiles
            results.append(record)
            print(f"d={d} k={k} done ({perf_counter()-start:.1f}s)", flush=True)
    result = {"seconds": perf_counter()-start, "records": results}
    (OUT/"summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    run()
