"""Exploratory boundary scan, no changes to chemistry or breadth definition."""

import json
from itertools import pairwise
from pathlib import Path

import numpy as np
from scipy.linalg import expm

from omega_v2.finite.closed_schlogl import build_model
from omega_v2.validation.reactive_breadth_v0 import ROOTS


def contrast(d, k, dt):
    model = build_model(k, d)
    q, index = model["q"], model["index"]
    p = expm(dt*q)
    logp = np.zeros_like(p)
    np.log2(p, out=logp, where=p > 0)
    h = -(p*logp).sum(1)
    ell = np.zeros(len(q))
    for _ in range(round(4/dt)):
        ell = h+p@ell
    fresh = expm(4*q)@ell
    return float(fresh[index[ROOTS["ready"]]]-fresh[index[ROOTS["separated"]]])


def main():
    output = Path("results/local_runs/reactive_boundary_v0")
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for dt in (.0125, .025, .05, .1, .2, 1.):
        for d in np.geomspace(.1, 100., 31):
            active, ablated = contrast(float(d), 1., dt), contrast(float(d), 0., dt)
            records.append({"dt": dt, "d": float(d), "active": active,
                            "ablated": ablated, "increment": active-ablated})
    (output/"summary.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    for dt in sorted({r["dt"] for r in records}):
        group = [r for r in records if r["dt"] == dt]
        brackets = [(a["d"], b["d"]) for a, b in pairwise(group)
                    if a["increment"]*b["increment"] < 0]
        print(dt, "sign brackets", brackets, "at d=10", group[20]["increment"],
              "range", min(r["increment"] for r in group),
              max(r["increment"] for r in group))


if __name__ == "__main__":
    main()
