"""Compare the finite adopted frame-volume readout under common catalytic laws."""

import os

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"

import hashlib
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from omega_v2.finite.catalytic_binding import CatalyticBinding
from omega_v2.finite.history_volume import HistoryVolume

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2/active_thermal_volume_v0"
PREVIOUS = ROOT / "docs/research_notes/omega_v2/catalytic_binding_v0"


def preparations(m):
    fair = m.initial("seeded")
    aligned = m.states[:, 0] == m.states[:, 1]
    active, inactive = 2 * fair * aligned, 2 * fair * ~aligned
    gaps = {}
    for gap in (1, 2, 3):
        p = np.zeros(len(m.ids))
        sites = [i for i in range(5) if i != gap]
        for bits in range(16):
            cells = [-1] * 5
            for j, site in enumerate(sites):
                cells[site] = (bits >> j) & 1
            p[m.index[(*cells, 0, 3)]] = 1 / 16
        gaps[gap] = p

    def mixed(q):
        return q * gaps[2] + (1 - q) * (gaps[1] + gaps[3]) / 2

    target = m.snapshot(active)["free_energy_nats"]
    central = brentq(lambda q: m.snapshot(mixed(q))["free_energy_nats"] - target, 1 / 3, 1)
    ready = np.zeros(len(m.ids), dtype=bool)
    for edge, neighbor in m.catalytic_pairs:
        ready |= (
            (m.fuel > 0)
            & ((m.states[:, 5] & (1 << edge)) == 0)
            & (m.states[:, edge] >= 0)
            & (m.states[:, edge + 1] >= 0)
            & ((m.states[:, 5] & (1 << neighbor)) != 0)
            & (m.states[:, neighbor] == m.states[:, neighbor + 1])
        )
    at5 = m.advance(fair, 5)
    mass = float(at5 @ ready)
    ps = {
        "thermal": m.pi.copy(),
        "aligned_seed": active,
        "misaligned_seed": inactive,
        "seeded_fair": fair,
        "dispersed": m.initial("dispersed"),
        "dispersed_free_energy_matched": mixed(central),
        "contact_unbound": m.initial("contact_unbound"),
        "assembled": m.initial("assembled"),
        "natural_cut5": at5,
        "natural_cut5_ready": at5 * ready / mass,
    }
    for name in ("misaligned_seed", "dispersed_free_energy_matched"):
        snapshot = m.snapshot(ps[name])
        if (
            abs(snapshot["free_energy_nats"] - target) > 1e-10
            or abs(snapshot["stored_energy"] - 12) > 1e-10
        ):
            raise ValueError("Preparation matching failed")
    return (
        ps,
        ready,
        {
            "central_gap_probability": central,
            "outer_gap_probability_each": (1 - central) / 2,
            "aligned_given_fair_seed_probability": 0.5,
            "natural_cut5_readiness_probability": mass,
        },
    )


def run(barrier, reader):
    start = time.perf_counter()
    m = CatalyticBinding(barrier=barrier)
    ps, ready, matching = preparations(m)
    previous = PREVIOUS / f"barrier_{barrier}_kernels.npz"
    with np.load(previous) as old:
        if not np.array_equal(old["states"], m.states) or not np.array_equal(old["rates"], m.rates):
            raise ValueError("Cached physical kernels do not match the current model")
        steps = {int(t): k for t, k in zip(old["kernel_lags"], old["K"], strict=True)}
    prepared = {
        name: {
            "initial": p.tolist(),
            "snapshot": m.snapshot(p),
            "readiness_probability": float(p @ ready),
            "windows": [],
        }
        for name, p in ps.items()
    }
    checks = {"kernel_rows": 0.0, "pair_chain_entropy": 0.0, "three_cut_refinement": 0.0}
    for lag, step in steps.items():
        endpoint = step @ step
        checks["kernel_rows"] = max(
            checks["kernel_rows"], float(np.max(abs(endpoint.sum(axis=1) - 1)))
        )
        for name, p in ps.items():
            paired = reader.pair_profile(p, endpoint)
            triple = reader.three_cut_profile(p, step, (barrier, lag))
            p_final = p @ endpoint
            # Every two-cut projection is a marginal of the matching three-cut view.
            for r in triple["frames"]:
                checks["three_cut_refinement"] = max(
                    checks["three_cut_refinement"],
                    max(0.0, float(paired["history_bits"][r["mask"]] - r["history_bits"])),
                )
            from scipy.special import xlogy

            chain = (
                -np.sum(xlogy(p, p)) - np.sum(p[:, None] * xlogy(endpoint, endpoint))
            ) / np.log(2)
            checks["pair_chain_entropy"] = max(
                checks["pair_chain_entropy"], abs(float(chain) - paired["whole_history_bits"])
            )
            arrays = {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in paired.items()}
            prepared[name]["windows"].append(
                {
                    "times": [0, 2 * lag],
                    **arrays,
                    "coverage_envelope": reader.envelope(paired),
                    "three_cut_times": [0, lag, 2 * lag],
                    "three_cut": triple,
                    "final_law": p_final.tolist(),
                    "final_snapshot": m.snapshot(p_final),
                    "expected_resource_profile": (p @ m.charges(2 * lag)).tolist(),
                }
            )
            print(f"b={barrier}, H={2 * lag}: {name} complete", flush=True)
    if max(checks.values()) > 1e-8:
        raise ValueError(checks)
    return {
        "parameters": m.parameters,
        "matching": matching,
        "resource_columns": m.reward_names,
        "preparations": prepared,
        "checks": checks,
        "kernel_source": str(previous.relative_to(ROOT)),
        "kernel_sha256": hashlib.sha256(previous.read_bytes()).hexdigest(),
        "runtime_seconds": time.perf_counter() - start,
    }


def main():
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    m = CatalyticBinding()
    reader = HistoryVolume(m.values, (0,) * 5 + (1,) * 4 + (2,))
    catalog = {
        "coordinate_names": m.primitive_names,
        "coverage_coordinates": ["site_variables", "bond_variables", "fuel_variable"],
        "frames": [
            {
                "mask": mask,
                "columns": [i for i in range(reader.d) if mask & (1 << i)],
                "coverage": reader.costs[mask].tolist(),
            }
            for mask in range(reader.full + 1)
        ],
        "content_classes": reader.content_catalog(),
    }
    models = {str(b): run(b, reader) for b in (0, 1, 2)}
    paths = [
        Path(__file__),
        ROOT / "omega_v2/finite/history_volume.py",
        ROOT / "omega_v2/finite/catalytic_binding.py",
        ROOT / "omega_v2/finite/spatial_binding.py",
    ]
    data = {
        "date": "2026-10-04",
        "schema": "active-thermal-history-volume-v0",
        "models": models,
        "runtime_seconds": time.perf_counter() - started,
        "source_hashes": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths
        },
    }
    (OUT / "results.json").write_text(
        json.dumps(data, separators=(",", ":"), allow_nan=False) + "\n", encoding="utf-8"
    )
    (OUT / "frame_catalog.json").write_text(
        json.dumps(catalog, separators=(",", ":")) + "\n", encoding="utf-8"
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
