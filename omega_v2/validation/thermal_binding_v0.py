"""Thermal baseline and a small mobile/binding extension of the flow probe."""

import os

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"

import hashlib
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from omega_v2.finite.continuation_readout import ContinuationReadout
from omega_v2.finite.fuel_flow import FuelFlow
from omega_v2.finite.spatial_binding import SpatialBinding

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2/thermal_binding_v0"
CUTS = (0, 1, 5, 20, 100)
LAGS = (1, 5)


def fuel_initial(m, built, stock, independent=False):
    p = np.zeros(len(m.ids))
    for bits in range(8) if independent else (0, 7):
        p[bits + 8 * built + 16 * stock] = 1 / 8 if independent else 0.5
    return p


def analyze(m, preparations, frames, prefix):
    reader = ContinuationReadout(m, frames)
    results = {}
    for label, initial in preparations.items():
        rows = []
        for t in CUTS:
            k, bill = m.evolution(t)
            p = initial @ k
            rows.append(
                {
                    "time": t,
                    "law": p.tolist(),
                    "snapshot": m.snapshot(p),
                    "expected_bill": (initial @ bill).tolist(),
                    "profiles": [reader.profiles(p, lag) for lag in LAGS],
                }
            )
        results[label] = {"initial": initial.tolist(), "cuts": rows}
        print(f"{prefix}: {label} complete", flush=True)
    times = sorted(set(CUTS + LAGS))
    arrays = {
        "Q": m.q,
        "states": m.values,
        "equilibrium": m.pi,
        "rates": m.rates,
        "targets": m.targets,
        "kernel_times": np.array(times),
        "K": np.stack([m.evolution(t)[0] for t in times]),
        "expected_bill": np.stack([m.evolution(t)[1] for t in times]),
    }
    np.savez_compressed(OUT / f"{prefix}_kernels.npz", **arrays)
    return {
        "parameters": m.parameters,
        "states": len(m.ids),
        "frames": frames,
        "channel_names": m.channel_names,
        "preparations": results,
        "detailed_balance_error": float(np.max(abs(m.pi[:, None] * m.q - m.pi[None, :] * m.q.T))),
    }


def cut(model, prep, t):
    return next(r for r in model["preparations"][prep]["cuts"] if r["time"] == t)


def profile(row, lag=1):
    return next(p for p in row["profiles"] if p["lag"] == lag)


def response(row, frame, channel):
    return profile(row)["reaction_response_tv"][frame][channel]


def report(data):
    thermal = data["thermal"]
    lines = [
        "# Thermal baseline and mobile binding — exploratory run v0",
        "",
        "3 October 2026. One existing fuel/coupling law and two mobility settings of a common 800-state particle model. Exact finite matrix dynamics; no fitted score, noise removal or required gas/structure winner.",
        "",
        "## Existing apparatus: equilibrium and matching brackets",
        "",
        "The earlier B=4, assembly=1, damage=0.05 apparatus now runs from its equilibrium law as well as correlated and independently prepared signals. All 32 frames, seven reactions and both response lags (1,5) are retained at cuts 0,1,5,20,100. Incremental prediction is I(X_i;X_rest(future)|X_rest(present)); it is well defined for joint fuel/register jumps, but is not a guarantee of physical control.",
        "",
        "Stationarity concerns the distribution, not an absence of events. Equilibrium retains activity and lagged response. This remains an open system with an implicit constant-temperature bath, not a closed-universe experiment. The fixed apparatus is not relabelled as a gas.",
        "",
        "The equal-free-energy preparation mixes prebuilt states with three and four fuel packets until D(p||π) equals that of the unbuilt four-packet preparation. It is one explicit match, not a unique matching rule. Its extra preparation uncertainty and energy remain in the law. Equal usable fuel instead compares prebuilt and unbuilt states both carrying three packets.",
        "",
        f"Prebuilt four-packet probability in the free-energy match: {thermal['free_energy_match_mixture']:.8f}.",
        "",
        "| Matching condition | Cut | Unbuilt response | Prebuilt response | Prebuilt − unbuilt |",
        "|---|---:|---:|---:|---:|",
    ]
    pairs = [
        ("stored energy", "unbuilt_correlated", "prebuilt_energy_correlated"),
        ("usable fuel", "unbuilt_three_correlated", "prebuilt_energy_correlated"),
        ("free energy", "unbuilt_correlated", "prebuilt_free_energy_correlated"),
    ]
    for name, a, b in pairs:
        for t in (0, 1, 5):
            ra, rb = response(cut(thermal, a, t), 4, 0), response(cut(thermal, b, t), 4, 0)
            lines.append(f"| {name} | {t} | {ra:.6f} | {rb:.6f} | {rb - ra:+.6f} |")
    lines += [
        "",
        "The table uses the native source-flip response at D at lag 1. A crossing changing under a matching rule identifies sensitivity to that physical preparation; it does not divide real mechanisms from mere accounting.",
        "",
        "| Preparation | Cut | Present I(S;D), bits | Response | Incremental prediction, bits | Activity |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label in ("equilibrium", "unbuilt_correlated", "unbuilt_independent"):
        for t in (0, 1, 20):
            row = cut(thermal, label, t)
            lines.append(
                f"| {label} | {t} | {row['snapshot']['source_receiver_bits']:.6f} | {response(row, 4, 0):.6f} | {profile(row)['incremental_prediction_bits'][0]:.6f} | {row['activity']:.6f} |"
            )
    lines += [
        "",
        "Randomizing the initial three signals lowers their correlation resource while preserving their individual fair marginals, geometry and fuel. Its free-energy cost is visible: the independently prepared unbuilt state has 2 ln 2 less D(p||π) than the correlated state. This is a separate physical preparation, not a free quotient of differences.",
        "",
        "## One common mobile substrate",
        "",
        "Three identical particles occupy five sites on a reflecting line. Each carries a binary internal state; empty/0/1 are the local site observations. There are no source, receiver or organism roles in the rules. Adjacent occupied sites exchange unequal internal states at rate 1, whether bonded or unbound. Native internal flips have rate 0.05. These collisions remain available to the dispersed preparation.",
        "",
        "Each adjacent pair may form or lose a bond. With μ=4, E=μ(F+number of bonds), and B=3 fuel/spent packets, the equilibrium weights are binomial(B,F) exp(−E). Thermal formation/breakdown rates are 0.02 exp(∓μ/2). Fuel-assisted formation consumes a packet at rate 0.25 F; reverse disassembly restores one at rate 0.25(B−F). The fuel pool is explicitly well mixed rather than spatially resolved.",
        "",
        "Every unbound particle or bonded connected component can translate one site into available space. A component of n particles has translation rate mobility/n in each allowed direction. Internal states and bonds move with it. This coarse motion rule and reflecting boundaries are declared assumptions, not derived molecular dynamics. Both mobility values, 0.1 and 1, use identical laws for all preparations. No bound-specific exchange-speed bonus is included.",
        "",
        "Four initial preparations are used:",
        "",
        "- Dispersed: occupied sites {0,2,4}, no bonds, three fuel packets.",
        "- Contact, unbound: occupied sites {1,2,3}, no bonds, three fuel packets.",
        "- Assembled: occupied sites {1,2,3}, both internal bonds, one fuel packet.",
        "- Equilibrium: the actual stationary distribution over the same states.",
        "",
        "The first three all have independent fair internal bits, three particles and stored energy 12. Contact versus dispersed also matches free energy exactly. The assembled preparation has ln 3 less D(p||π), due to the fuel-inventory degeneracy; this unmatched resource remains explicit. Geometry and bonds subsequently evolve normally. Initial positions are physical preparations, not labels erased by averaging.",
        "",
        "Each of the 32 site subsets is observed with and without the shared fuel pool, giving 64 declared frames. A frame sees internal bonds whose two endpoints it contains. Boundary-crossing-bond and edge-only readers are not included; this is not the set of all physically possible frames. The full frame identifies every represented state. Present source axes comprise all five site variables, four bond bits and fuel, not a designated beneficiary.",
        "",
        "## Mobile comparison",
        "",
        "Illustration: a native flip at site 2, observed in the joint frame of the other four sites at lag 1. Response is conditional on that flip occurring; its actual rate is retained. Present site information includes occupancy as well as internal state. Full profiles, including all joint frames and reaction types, remain in the evidence.",
        "",
        "| Mobility | Preparation | Cut | Mean bonds | Mean fuel | Response | Flip rate | Incremental prediction at site 2 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, model in data["mobile"].items():
        for t in (0, 1, 20):
            for label in ("dispersed", "contact_unbound", "assembled", "equilibrium"):
                row = cut(model, label, t)
                s, p = row["snapshot"], profile(row)
                lines.append(
                    f"| {name} | {label} | {t} | {s['bonds_mean']:.6f} | {s['fuel_mean']:.6f} | {response(row, 27, 2):.6f} | {p['reaction_rates'][2]:.6f} | {p['incremental_prediction_bits'][2]:.6f} |"
                )
    lines += [
        "",
        "## Scope and evidence",
        "",
        "This is a bounded reactive lattice-gas comparison, not an empirical verdict on molecular gas or open-ended generativity. Assembly creates mobile composites within a fixed primitive law; the full law already predicts their possible formation. Native noise, collisions, reverse reactions and the thermal tail all remain. A high response can transmit destructive consequences as well as constructive ones, so the profile carries no assigned ethical sign.",
        "",
        "All comparisons concern the retained finite-time laws. A common equilibrium does not erase transient differences, and equilibrium can retain conditional dynamics. These runs do not assert that lushness must vanish at equilibrium, that gas must lose, or that a successful response metric alone completes lushness.",
        "",
        f"Runtime: {data['runtime_seconds']:.2f} seconds with one numerical worker. Maximum detailed-balance residual: {data['checks']['detailed_balance_max']:.3g}. Maximum fuel-balance residual: {data['checks']['fuel_balance_max']:.3g}. Maximum mobile bond-balance residual: {data['checks']['bond_balance_max']:.3g}.",
        "",
        "    .venv/Scripts/python.exe -m omega_v2.validation.thermal_binding_v0",
        "",
        "[All profiles, laws and parameters](thermal_binding_v0/profiles.json) · [Thermal kernels](thermal_binding_v0/thermal_kernels.npz) · [Slow-motion kernels](thermal_binding_v0/mobile_0.1_kernels.npz) · [Fast-motion kernels](thermal_binding_v0/mobile_1.0_kernels.npz)",
        "",
        "[Preceding fuel/coupling run](fuel_flow_report_v0.md)",
        "",
    ]
    return "\n".join(lines)


def main():
    start = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    m = FuelFlow(4, assembly=1, damage=0.05)
    unbuilt = fuel_initial(m, 0, 4)
    built3, built4 = fuel_initial(m, 1, 3), fuel_initial(m, 1, 4)
    target = m.snapshot(unbuilt)["nonequilibrium_free_energy_nats"]
    mix = brentq(
        lambda q: (
            m.snapshot((1 - q) * built3 + q * built4)["nonequilibrium_free_energy_nats"] - target
        ),
        0,
        1,
    )
    preps = {
        "equilibrium": m.pi.copy(),
        "unbuilt_correlated": unbuilt,
        "prebuilt_energy_correlated": built3,
        "unbuilt_three_correlated": fuel_initial(m, 0, 3),
        "prebuilt_free_energy_correlated": (1 - mix) * built3 + mix * built4,
        "unbuilt_independent": fuel_initial(m, 0, 4, True),
        "prebuilt_energy_independent": fuel_initial(m, 1, 3, True),
    }
    thermal = analyze(
        m, preps, {mask: [i for i in range(5) if mask & (1 << i)] for mask in range(32)}, "thermal"
    )
    thermal["free_energy_match_mixture"] = mix
    thermal["primitive_names"] = ["S", "R", "D", "G", "F"]
    thermal["bill_columns"] = ["copy_debits", "copy_credits", "assembly_debits", "assembly_credits"]
    fuel_error, bond_error = 0.0, 0.0
    for prep in thermal["preparations"].values():
        initial_fuel = np.array(prep["initial"]) @ m.fuel
        for row in prep["cuts"]:
            row["activity"] = float(np.array(row["law"]) @ m.rates.sum(axis=0))
            b = row["expected_bill"]
            fuel_error = max(
                fuel_error,
                abs(initial_fuel - row["snapshot"]["fuel_mean"] - b[0] + b[1] - b[2] + b[3]),
            )
    mobile = {}
    for mobility in (0.1, 1.0):
        m = SpatialBinding(mobility=mobility)
        prepared = {
            name: m.initial(name)
            for name in ("dispersed", "contact_unbound", "assembled", "equilibrium")
        }
        result = analyze(m, prepared, m.frame_columns(), f"mobile_{mobility}")
        result["primitive_names"], result["bill_columns"] = m.primitive_names, m.reward_names
        mobile[str(mobility)] = result
        for label, p in prepared.items():
            for row in result["preparations"][label]["cuts"]:
                b, s = row["expected_bill"], row["snapshot"]
                fuel_error = max(fuel_error, abs(p @ m.fuel - s["fuel_mean"] - b[0] + b[1]))
                bond_error = max(
                    bond_error, abs(s["bonds_mean"] - p @ m.bond_count - b[0] + b[1] - b[2] + b[3])
                )
    result = {
        "date": "2026-10-03",
        "schema": "thermal-mobile-binding-v0",
        "cuts": CUTS,
        "lags": LAGS,
        "thermal": thermal,
        "mobile": mobile,
        "runtime_seconds": time.perf_counter() - start,
        "source_hashes": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [
                Path(__file__),
                *[
                    ROOT / f"omega_v2/finite/{name}.py"
                    for name in (
                        "spatial_binding",
                        "continuation_readout",
                        "fuel_flow",
                        "local_flow",
                    )
                ],
            ]
        },
        "checks": {
            "detailed_balance_max": max(
                r["detailed_balance_error"] for r in (thermal, *mobile.values())
            ),
            "fuel_balance_max": float(fuel_error),
            "bond_balance_max": float(bond_error),
        },
    }
    (OUT / "profiles.json").write_text(
        json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n", encoding="utf-8"
    )
    (OUT.parent / "thermal_binding_report_v0.md").write_text(report(result), encoding="utf-8")
    print(
        json.dumps(
            {"runtime_seconds": result["runtime_seconds"], "checks": result["checks"]}, indent=2
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
