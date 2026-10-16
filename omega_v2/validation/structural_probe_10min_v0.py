"""Exploratory sampled classical circuits; exact eight-input analysis.

No exhaustive circuit search and no lushness score. Run as a module.
"""

from __future__ import annotations

import os

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"

import argparse
import hashlib
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import combinations, product
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

X = np.array(list(product((0, 1), repeat=3)), dtype=np.uint8)
POW = (1 << np.arange(8)).astype(np.uint16)
SRC = tuple(int(np.dot(X[:, i], POW)) for i in range(3))
GATES = []
for _t in range(3):
    _cs = [i for i in range(6) if i != _t + 3]
    GATES.extend((_t, ((c, 1),)) for c in _cs)
    GATES.extend(
        (_t, tuple(zip(pair, pol)))
        for pair in combinations(_cs, 2)
        for pol in product((0, 1), repeat=2)
    )


def advance(state, gate):
    target, controls = gate
    vals = SRC + tuple(state)
    active = 255
    for c, v in controls:
        active &= vals[c] if v else vals[c] ^ 255
    out = list(state)
    out[target] ^= active
    return tuple(out)


def partition(row):
    labels = {}
    return tuple(labels.setdefault(int(v), len(labels)) for v in row)


PRODUCT_PARTITIONS = {
    partition([sum(int(x[i]) << i for i in range(3) if m & (1 << i)) for x in X]) for m in range(8)
}


def classify(row):
    key = partition(row)
    if key in PRODUCT_PARTITIONS:
        return 0
    for value in set(row.tolist()):
        cell = X[row == value]
        size = np.prod([len(np.unique(cell[:, i])) for i in range(3)])
        if size != len(cell):
            return 2
    return 1


def decoder_panel():
    terms = [(SRC[i], ((i, 1),)) for i in range(3)]
    for pair in combinations(range(3), 2):
        for pol in product((0, 1), repeat=2):
            mask = 255
            for i, v in zip(pair, pol):
                mask &= SRC[i] if v else SRC[i] ^ 255
            terms.append((mask, tuple(zip(pair, pol))))
    found = {0: (0, [])}
    for i, (mask, controls) in enumerate(terms):
        found.setdefault(mask, (1, [i]))
    for i, j in combinations(range(len(terms)), 2):
        found.setdefault(terms[i][0] ^ terms[j][0], (2, [i, j]))
    keys = sorted(found)
    return (
        np.array(keys, dtype=np.uint16),
        np.array([found[k][0] for k in keys], dtype=np.uint8),
        terms,
        {str(k): found[k] for k in keys},
    )


DEC, DCOST, DTERMS, DWIT = decoder_panel()


def responses(codes):
    values = (DEC[None, :, None] >> codes[:, None, :]) & 1
    return np.sum(values * POW[None, None, :], axis=2, dtype=np.uint16)


def entropies(codes, weights, bins=8):
    probs = np.zeros((len(codes), bins), dtype=np.float64)
    rows = np.arange(len(codes))
    for x, w in enumerate(weights):
        probs[rows, codes[:, x]] += w
    return -np.sum(probs * np.log2(np.where(probs > 0, probs, 1)), axis=1)


def info(codes, weights):
    hf = entropies(codes, weights)
    individual = []
    for i in range(3):
        px = float(np.dot(weights, X[:, i]))
        hx = -sum(v * np.log2(v) for v in (px, 1 - px) if v > 0)
        joint = entropies(codes + 8 * X[None, :, i], weights, 16)
        individual.append(hf + hx - joint)
    syn = hf - np.sum(individual, axis=0)
    return hf, syn


def source_laws():
    cases = []
    for p, q in product((0.5, 0.2, 0.05), repeat=2):
        bias = np.array([p, q, q])
        w = np.prod(np.where(X, bias, 1 - bias), axis=1)
        cases.append((f"ind_{p}_{q}", w))
    for rho in (0.5, 0.9):
        p = 0.2
        w = (1 - rho) * np.prod(np.where(X, p, 1 - p), axis=1)
        w[0] += rho * (1 - p)
        w[-1] += rho * p
        cases.append((f"corr_0.2_{rho}", w))
    return cases


def rank_corr(a, b):
    if len(a) < 3 or np.ptp(a) < 1e-10 or np.ptp(b) < 1e-10:
        return None
    return float(spearmanr(a, b).statistic)


def checks():
    fair = np.full(8, 1 / 8)
    xor = (X[:, 0] ^ X[:, 1])[None, :]
    conjunction = (X[:, 0] & X[:, 1])[None, :]
    assert np.isclose(info(xor, fair)[1][0], 1)
    assert np.isclose(info(conjunction, fair)[1][0], 0.188721875540867)
    biased = source_laws()[4][1]
    h0 = (1 - X[:, 0]) & (1 - X[:, 1])
    h1 = X[:, 0] ^ (h0 & X[:, 2])
    h, s = info((2 * h0 + h1)[None, :], biased)
    assert np.isclose(h[0], 1.7615045515251642) and abs(s[0]) < 1e-12
    assert len(GATES) == 135
    assert classify(2 * h0 + h1) == 1
    assert classify(4 * X[:, 0] + 2 * X[:, 1] + X[:, 2]) == 0
    for mask, (cost, word) in zip(DEC, [DWIT[str(k)] for k in DEC]):
        actual = 0
        for i in word:
            actual ^= DTERMS[i][0]
        assert int(mask) == actual and len(word) == cost
    for _, w in source_laws():
        assert np.isclose(w.sum(), 1) and np.all(w > 0)
    copy_state = np.array([[SRC[0]] * 3], dtype=np.uint16)
    c = sum(((copy_state[:, i, None] >> np.arange(8)) & 1) << (2 - i) for i in range(3))
    for j in range(3):
        resp = responses(c & (7 ^ (1 << (2 - j))))
        assert np.min(np.where(resp[0] == SRC[0], DCOST, 99)) == 1
    return {
        "known_information": "passed",
        "hierarchy": "passed",
        "decoder_witnesses": "passed",
        "probability_mass": "passed",
        "copy_recovery": "passed",
    }


def worker(args):
    seed, per_length, outdir = args
    start = time.perf_counter()
    rng = np.random.default_rng(seed)
    states, programs, depths, n_ccx, record_controls = [], [], [], [], []
    seen = set()
    attempted = 0
    for depth in range(1, 6):
        for _ in range(per_length):
            word = rng.integers(0, len(GATES), depth).tolist()
            state = (0, 0, 0)
            for gi in word:
                state = advance(state, GATES[gi])
            attempted += 1
            ccx = sum(len(GATES[g][1]) == 2 for g in word)
            key = (state, depth, ccx)
            if key in seen:
                continue
            seen.add(key)
            states.append(state)
            programs.append(word + [-1] * (5 - depth))
            depths.append(depth)
            n_ccx.append(ccx)
            record_controls.append(sum(any(c >= 3 for c, _ in GATES[g][1]) for g in word))
    states = np.array(states, dtype=np.uint16)
    programs = np.array(programs, dtype=np.int16)
    depths = np.array(depths, dtype=np.uint8)
    n_ccx = np.array(n_ccx, dtype=np.uint8)
    codes = sum(((states[:, i, None] >> np.arange(8)) & 1) << (2 - i) for i in range(3))
    codes = codes.astype(np.uint8)
    classes = np.array([classify(row) for row in codes], dtype=np.uint8)
    response = responses(codes)
    coverage = np.stack(
        [np.array([len(np.unique(row)) for row in response[:, DCOST <= b]]) for b in (0, 1, 2)],
        axis=1,
    )
    source_cost = np.stack(
        [np.min(np.where(response == s, DCOST, 99), axis=1) for s in SRC], axis=1
    )
    repair_cost, repair_ceiling = [], []
    for j in range(3):
        damaged = codes & (7 ^ (1 << (2 - j)))
        rr = responses(damaged)
        repair_cost.append(np.min(np.where(rr == states[:, j, None], DCOST, 99), axis=1))
        possible = []
        for row, target in zip(damaged, states[:, j]):
            possible.append(
                all(
                    len({(int(target) >> x) & 1 for x in range(8) if row[x] == cell}) == 1
                    for cell in set(row.tolist())
                )
            )
        repair_ceiling.append(possible)
    repair_cost = np.stack(repair_cost, axis=1)
    repair_ceiling = np.stack(repair_ceiling, axis=1)
    assert np.all((repair_cost < 99) <= repair_ceiling)
    laws = source_laws()
    all_h, all_syn, all_loss = [], [], []
    case_summary = []
    for name, weights in laws:
        hs, ss = zip(*(info(codes & mask, weights) for mask in range(1, 8)))
        hs, ss = np.stack(hs, axis=1), np.stack(ss, axis=1)
        loss = np.stack([hs[:, 6] - hs[:, (7 ^ (1 << (2 - j))) - 1] for j in range(3)], axis=1)
        assert np.min(loss) > -1e-10
        if name.startswith("ind"):
            assert np.min(ss) > -1e-10
        all_h.append(hs)
        all_syn.append(ss)
        all_loss.append(loss)
        krows = []
        for k in (1, 2, 3):
            cols = [m - 1 for m in range(1, 8) if m.bit_count() == k]
            krows.append(
                {
                    "k": k,
                    "rho_H_syn": rank_corr(hs[:, cols].ravel(), ss[:, cols].ravel()),
                    "max_H": float(hs[:, cols].max()),
                    "negative_syn_fraction": float(np.mean(ss[:, cols] < -1e-9)),
                }
            )
        case_summary.append(
            {
                "case": name,
                "by_frame_size": krows,
                "rho_H_cheap_response_count": rank_corr(hs[:, 6], coverage[:, 2]),
                "rho_syn_worst_information_loss": rank_corr(ss[:, 6], loss.max(axis=1)),
                "mean_worst_information_loss": float(np.mean(loss.max(axis=1))),
            }
        )
    # Same input partition and same CNOT/Toffoli bill: every current full-record
    # information diagnostic agrees for every source law; future access may not.
    groups = {}
    witnesses = []
    compared = different = repair_different = 0
    for i, row in enumerate(codes):
        key = (partition(row), int(depths[i]), int(n_ccx[i]))
        old = groups.setdefault(key, i)
        if old == i:
            continue
        compared += 1
        a = {int(q): int(c) for q, c in zip(response[old], DCOST)}
        b = {int(q): int(c) for q, c in zip(response[i], DCOST)}
        # zip iteration can overwrite a cheaper realization; rebuild with min.
        for idx, mapping in ((old, a), (i, b)):
            for q, c in zip(response[idx], DCOST):
                mapping[int(q)] = min(mapping[int(q)], int(c))
        access_diff = a != b
        repair_diff = not np.array_equal(repair_cost[old], repair_cost[i])
        different += int(access_diff)
        repair_different += int(repair_diff)
        if access_diff and len(witnesses) < 8:
            changed = [q for q in sorted(a.keys() | b.keys()) if a.get(q, 99) != b.get(q, 99)]
            witnesses.append(
                {
                    "a": old,
                    "b": i,
                    "partition": list(key[0]),
                    "depth": key[1],
                    "CCX": key[2],
                    "a_program": programs[old].tolist(),
                    "b_program": programs[i].tolist(),
                    "a_state": states[old].tolist(),
                    "b_state": states[i].tolist(),
                    "changed_query_examples": [
                        {"truth_mask": q, "a_cost": a.get(q, 99), "b_cost": b.get(q, 99)}
                        for q in changed[:8]
                    ],
                    "repair_a": repair_cost[old].tolist(),
                    "repair_b": repair_cost[i].tolist(),
                }
            )
    output = Path(outdir)
    np.savez_compressed(
        output / f"seed_{seed}.npz",
        states=states,
        programs=programs,
        depths=depths,
        ccx=n_ccx,
        record_controls=np.array(record_controls),
        classes=classes,
        codes=codes,
        response=response,
        coverage=coverage,
        source_cost=source_cost,
        repair_cost=repair_cost,
        repair_ceiling=repair_ceiling,
        entropy=np.stack(all_h),
        synergy=np.stack(all_syn),
        losses=np.stack(all_loss),
    )
    result = {
        "seed": seed,
        "programs_sampled": attempted,
        "retained_map_bill_pairs": len(states),
        "classes": {
            n: int(np.sum(classes == k)) for k, n in enumerate(("product", "hierarchy", "fusion"))
        },
        "matched_partition_bill_comparisons": compared,
        "different_access": different,
        "different_repair": repair_different,
        "repair_fraction_by_lost_register": (repair_cost < 99).mean(axis=0).tolist(),
        "cases": case_summary,
        "witnesses": witnesses,
        "seconds": time.perf_counter() - start,
    }
    (output / f"seed_{seed}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--per-length", type=int, default=2000)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    check_results = checks()
    manifest = {
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workers": args.workers,
        "seeds": list(range(202610030, 202610040)),
        "per_length": args.per_length,
        "depths": [1, 2, 3, 4, 5],
        "scope": "Sampled open-loop classical reversible encodings, exact input-law analysis; not a lushness score.",
        "sampling": "Uniform independent primitive draws at each depth. Deduplicate map/depth/CCX per seed for analysis. This is a sampling measure, not a physical probability over programs.",
        "initial_state": "Three independent or explicitly correlated source bits; three blank records. Sources retained and unavailable to downstream decoder.",
        "cost": "One serial tick per primitive; CX and CCX counts also retained separately. No energy claim. Decoder uses one additional blank Y.",
        "damage": "One D register swapped into an inaccessible retained bath register; known location. Three CX-equivalent damage steps, same for all. Repair decoder writes Y; copying Y back to reset D adds one CX. Full-source global information is retained.",
        "decoder_scope": "At most two CX/CCX-to-Y gates controlled only by D. Flat record-preserving response panel, no adaptive controllers. Cost 99 means not witnessed in this panel.",
        "queries": "All 256 Boolean truth tables are coordinates; no uniform value or task distribution is assigned.",
        "gate_count": len(GATES),
        "gates": GATES,
        "decoder_terms": DTERMS,
        "decoder_witnesses": DWIT,
        "source_laws": [{"name": n, "weights": w.tolist()} for n, w in source_laws()],
        "checks": check_results,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    started = time.perf_counter()
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = [
            pool.submit(worker, (seed, args.per_length, str(out))) for seed in manifest["seeds"]
        ]
        for job in as_completed(jobs):
            r = job.result()
            results.append(r)
            print(
                json.dumps(
                    {
                        "seed": r["seed"],
                        "retained": r["retained_map_bill_pairs"],
                        "different_access": r["different_access"],
                        "seconds": round(r["seconds"], 2),
                    }
                ),
                flush=True,
            )
    summary = {
        "wall_seconds": time.perf_counter() - started,
        "programs_sampled": sum(r["programs_sampled"] for r in results),
        "retained_map_bill_pairs": sum(r["retained_map_bill_pairs"] for r in results),
        "matched_comparisons": sum(r["matched_partition_bill_comparisons"] for r in results),
        "different_access": sum(r["different_access"] for r in results),
        "different_repair": sum(r["different_repair"] for r in results),
        "results": sorted(results, key=lambda r: r["seed"]),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}), flush=True)


if __name__ == "__main__":
    main()
