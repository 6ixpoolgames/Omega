"""Analysis of the sampled probe; alternative decoder hardware is explicit."""

import os

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path

import numpy as np

from omega_v2.validation.structural_probe_10min_v0 import (
    DTERMS,
    POW,
    SRC,
    partition,
)


def analyze(path):
    data = np.load(path)
    codes, depths, ccx = data["codes"], data["depths"], data["ccx"]
    terms = sorted({255, *SRC, *(255 ^ s for s in SRC), *(m for m, _ in DTERMS)})
    costs = {0: 0, **{t: 1 for t in terms}}
    for a, b in combinations(terms, 2):
        costs.setdefault(a ^ b, 2)
    dec = np.array(sorted(costs), dtype=np.uint16)
    bills = np.array([costs[int(k)] for k in dec])
    response = np.sum(((dec[None, :, None] >> codes[:, None, :]) & 1) * POW[None, None, :], axis=2)
    groups = {}
    comparisons = changed = changed_set = 0
    witness = None
    for i, row in enumerate(codes):
        key = (partition(row), int(depths[i]), int(ccx[i]))
        old = groups.setdefault(key, i)
        if old == i:
            continue
        comparisons += 1
        maps = []
        for index in (old, i):
            mapping = {}
            for q, c in zip(response[index], bills):
                mapping[int(q)] = min(mapping.get(int(q), 99), int(c))
            maps.append(mapping)
        different = maps[0] != maps[1]
        changed += different
        changed_set += maps[0].keys() != maps[1].keys()
        if different and witness is None and len(set(row.tolist())) >= 4:
            q = next(
                k
                for k in sorted(maps[0].keys() | maps[1].keys())
                if maps[0].get(k, 99) != maps[1].get(k, 99)
            )
            witness = {
                "seed": path.stem,
                "indices": [old, i],
                "states": data["states"][[old, i]].tolist(),
                "programs": data["programs"][[old, i]].tolist(),
                "depth": int(depths[i]),
                "ccx": int(ccx[i]),
                "partition": list(key[0]),
                "query": q,
                "costs": [m.get(q, 99) for m in maps],
                "H_at_p_0_2": data["entropy"][4, [old, i], 6].tolist(),
                "Syn_at_p_0_2": data["synergy"][4, [old, i], 6].tolist(),
            }
    nonconstant = (data["states"] != 0) & (data["states"] != 255)
    repairable = (data["repair_cost"] < 99) & nonconstant
    result = {
        "seed": path.stem,
        "matched_comparisons": comparisons,
        "symmetric_cost_profile_different": int(changed),
        "symmetric_response_set_different": int(changed_set),
        "symmetric_panel_size": len(dec),
        "nonconstant_lost_records": int(nonconstant.sum()),
        "repairable_nonconstant_records": int(repairable.sum()),
        "witness": witness,
    }
    return result


if __name__ == "__main__":
    folder = Path(sys.argv[1])
    with ProcessPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(analyze, sorted(folder.glob("seed_*.npz"))))
    output = {
        "scope": "Same sampled maps; alternate hardware supplies native X and complemented CNOT at unit cost. Not a free transformation of the original apparatus.",
        "results": results,
    }
    for key in (
        "matched_comparisons",
        "symmetric_cost_profile_different",
        "symmetric_response_set_different",
        "nonconstant_lost_records",
        "repairable_nonconstant_records",
    ):
        output[key] = sum(r[key] for r in results)
    (folder / "analysis.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in output.items() if k != "results"}))
    print(json.dumps(results[0]["witness"]))
