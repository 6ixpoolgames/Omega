"""Small exact continuation probe with reversible recursive catalysis."""

import os

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"

import hashlib
import json
import time
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import expm_multiply

from omega_v2.finite.catalytic_binding import CatalyticBinding
from omega_v2.finite.native_response import NativeResponse

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2/catalytic_binding_v0"
CUTS = (0, 1, 5, 20)
LAGS = (1, 5)
PREPARATIONS = ("dispersed", "contact_unbound", "seeded", "assembled", "equilibrium")


def run(barrier):
    started = time.perf_counter()
    model = CatalyticBinding(barrier=barrier)
    reader = NativeResponse(model)
    for lag in LAGS:
        reader.contrasts(lag)
        print(f"barrier {barrier}: response lag {lag} complete", flush=True)
    n = len(model.ids)
    monitor = model.two_stage_generator()
    completed = np.concatenate((np.zeros(2 * n), np.ones(n)))
    sequence = {t: expm_multiply(monitor * t, completed)[:n] for t in CUTS}
    checks = {"fuel_balance": 0.0, "bond_balance": 0.0, "probability_mass": 0.0}

    def row(initial, t):
        law = model.advance(initial, t)
        bills = initial @ model.charges(t)
        checks["fuel_balance"] = max(
            checks["fuel_balance"],
            abs(initial @ model.fuel - law @ model.fuel - bills[0] + bills[1]),
        )
        checks["bond_balance"] = max(
            checks["bond_balance"],
            abs(
                law @ model.bond_count
                - initial @ model.bond_count
                - bills[0]
                + bills[1]
                - bills[2]
                + bills[3]
            ),
        )
        checks["probability_mass"] = max(checks["probability_mass"], abs(law.sum() - 1))
        return {
            "time": t,
            "law": law.tolist(),
            "snapshot": model.snapshot(law),
            "expected_bill": bills.tolist(),
            "profiles": [reader.profiles(law, lag) for lag in LAGS],
        }

    preparations = {}
    for name in PREPARATIONS:
        initial = model.initial(name)
        rows = []
        for t in CUTS:
            entry = row(initial, t)
            entry["first_tetramer_probability"] = float(initial @ model.hitting("tetramer", t))
            entry["two_stage_sequence_probability"] = float(initial @ sequence[t])
            rows.append(entry)
        preparations[name] = {"initial": initial.tolist(), "cuts": rows}
    cut_law = model.advance(model.initial("seeded"), 5)
    damage = model.breakdown(cut_law)
    recovery = {
        "preparation": "seeded",
        "cut": 5,
        "edge": 0,
        "native_breakdown_rate": damage["rate"],
        "before": damage["before"].tolist(),
        "after": damage["after"].tolist(),
        "cuts": [],
    }
    for elapsed in CUTS:
        after, skipped = row(damage["after"], elapsed), row(damage["before"], elapsed)
        recovery["cuts"].append(
            {
                "elapsed": elapsed,
                "taken": after,
                "skipped_reference": skipped,
                "first_edge_restoration_probability": float(
                    damage["after"] @ model.hitting("edge0", elapsed)
                ),
                "whole_law_tv": float(0.5 * np.abs(np.array(after["law"]) - skipped["law"]).sum()),
            }
        )
    checks["detailed_balance"] = float(
        np.max(abs(model.pi[:, None] * model.q - model.pi[None, :] * model.q.T))
    )
    checks["kernel_rows"] = max(
        float(np.max(abs(model.evolution(t)[0].sum(axis=1) - 1))) for t in LAGS
    )
    checks["kernel_minimum"] = min(float(model.evolution(t)[0].min()) for t in LAGS)
    if max(v for k, v in checks.items() if k != "kernel_minimum") > 1e-8:
        raise ValueError(checks)
    sparse = csr_matrix(model.q)
    np.savez_compressed(
        OUT / f"barrier_{barrier}_kernels.npz",
        states=model.states,
        values=model.values,
        equilibrium=model.pi,
        rates=model.rates,
        targets=model.targets,
        reward_rates=model.rewards,
        Q_data=sparse.data,
        Q_indices=sparse.indices,
        Q_indptr=sparse.indptr,
        Q_shape=np.array(sparse.shape),
        kernel_lags=np.array(LAGS),
        K=np.stack([model.evolution(t)[0] for t in LAGS]),
    )
    print(f"barrier {barrier}: laws, recovery and bills complete", flush=True)
    return {
        "parameters": model.parameters,
        "states": n,
        "frames": model.frame_columns(),
        "primitive_names": model.primitive_names,
        "channels": model.channel_names,
        "bill_columns": model.reward_names,
        "preparations": preparations,
        "recovery": recovery,
        "checks": checks,
        "runtime_seconds": time.perf_counter() - started,
    }


def main():
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    models = {str(b): run(b) for b in (0, 1, 2)}
    source_files = [
        Path(__file__),
        *[
            ROOT / f"omega_v2/finite/{s}.py"
            for s in (
                "spatial_binding",
                "catalytic_binding",
                "native_response",
                "continuation_readout",
            )
        ],
    ]
    data = {
        "schema": "catalytic-binding-v0",
        "date": "2026-10-04",
        "cuts": CUTS,
        "lags": LAGS,
        "models": models,
        "runtime_seconds": time.perf_counter() - started,
        "source_hashes": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in source_files
        },
    }
    (OUT / "profiles.json").write_text(
        json.dumps(data, separators=(",", ":"), allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "runtime_seconds": data["runtime_seconds"],
                "checks": {b: m["checks"] for b, m in models.items()},
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
