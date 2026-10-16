"""Small finite-fuel follow-up: assembly, depletion and native breakdowns."""

import os

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"

import hashlib
import json
import time
from pathlib import Path

import numpy as np

from omega_v2.finite.fuel_flow import FuelFlow

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2/fuel_flow_v0"
CUTS = (0, 0.5, 1, 2, 5, 10, 20, 50, 100)
LAGS = (1, 5)
RECOVERY = (0, 1, 5, 20, 50)


def observe(model, p):
    return {"snapshot": model.snapshot(p), "profiles": [model.profiles(p, lag) for lag in LAGS]}


def response(row, lag=1):
    profile = next(p for p in row["profiles"] if p["lag"] == lag)
    return profile["reaction_response_tv"][4][0]


def run_preparation(model, built):
    initial = model.initial(built)
    rows = []
    for t in CUTS:
        kernel, charges = model.evolution(t)
        p = initial @ kernel
        row = {"time": t, "law": p.tolist(), **observe(model, p)}
        row["cumulative_fuel_reactions"] = (initial @ charges).tolist()
        row["first_exhaustion_probability"] = float(initial @ model.exhaustion_probability(t))
        bill = row["cumulative_fuel_reactions"]
        row["fuel_accounting_error"] = float(
            abs(initial @ model.fuel - p @ model.fuel - bill[0] + bill[1] - bill[2] + bill[3])
        )
        rows.append(row)
    cut = model.breakdown_cut(initial @ model.evolution(5)[0])
    aftermath = []
    for elapsed in RECOVERY:
        kernel = model.evolution(elapsed)[0]
        aftermath.append(
            {
                "elapsed": elapsed,
                "after_event": observe(model, cut["after"] @ kernel),
                "skip_event_reference": observe(model, cut["before"] @ kernel),
            }
        )
    return {
        "built": built,
        "initial": initial.tolist(),
        "cuts": rows,
        "breakdown_at_time": 5,
        "breakdown_event_rate": cut["rate"],
        "breakdown_before_law": cut["before"].tolist(),
        "breakdown_after_law": cut["after"].tolist(),
        "aftermath": aftermath,
    }


def make_report(result):
    cases = result["models"]
    lines = [
        "# Finite fuel and repairable coupling — exploratory run v0",
        "",
        "Run date: 2026-10-03. Twelve exact finite classical generators; two preparations each.",
        "No fitted lushness score or prescribed winning mechanism. All 32 frames and seven native reaction channels are retained.",
        "",
        "## Physical model and bill",
        "",
        "State is (S,R,D,G,F): three signal registers, the assembly state of the R→D link, and fuel count 0…B. The material scaffold is present in both preparations. There are 16(B+1) states. The source-to-relay coupling is always present; the relay-to-destination coupling requires G=1. Every signal bit has native thermal noise, and the link can both disassemble and assemble thermally.",
        "",
        "The temperature unit is one. Stored energy is E=μ(F+G), μ=4. With B−F spent packets, the equilibrium law is proportional to binomial(B,F) exp(−E). The inventory degeneracy is explicit. Channel rates are:",
        "",
        "- Thermal S/R/D flips: 0.1 / 0.02 / 0.02 in either direction.",
        "- Thermal link assembly: d exp(−μ/2); breakdown: d exp(+μ/2).",
        "- A copying correction consumes one fuel packet at rate c F exp(+μ/2), c=0.25. Its reverse breaks the match and restores fuel at rate c(B−F) exp(−μ/2). The R→D pair is enabled only with G=1.",
        "- Assembly transfers one packet's stored energy into the link: (G=0,F)→(G=1,F−1) at rate a F. Its reverse is a(B−F). All reverse reactions remain in the actual generator.",
        "",
        "Sweep: B∈{1,4,8}, a∈{0.25,1}, d∈{0.005,0.05}. Parameters specify kinetic laws, not scoring coefficients. Each law is run from an unbuilt preparation (G=0,F=B) and a prebuilt preparation (G=1,F=B−1); both start with a fair S and R=D=S. Initial signal content and stored energy are matched. Initial thermodynamic free energy is NOT matched: the prebuilt fuel macrostate has B-fold inventory degeneracy, making its relative entropy to equilibrium smaller by ln B. Both free-energy values are retained; the comparison is not a general equal-resource dominance claim.",
        "",
        "This is a finite fuel inventory coupled to an implicit heat bath. Zero fuel is not absorbing: reverse reactions can restore fuel, and the link can assemble through thermal fluctuations. The first-hit-to-zero calculation uses a separate absorbing construction only to report that event; it never truncates actual continuation.",
        "",
        "## Readouts",
        "",
        "For every cut and lag, held information I(X_i(cut); X_frame(cut+lag)) uses the actual law. The response to each reaction is the average total-variation distance between future frame laws with that reaction taken and skipped, weighted by its actual reaction flux at the cut. Its rate is reported separately. This is a counterfactual contrast, not a newly inserted random event, policy, or ethical sign. When a channel has no events its response array uses zero with event_present=false, not an inferred zero effect.",
        "",
        "Snapshots also retain link occupancy, fuel stock, current source/destination mutual information, stored energy and D(p||π). The last is a thermodynamic diagnostic, not a lushness measure. Fuel-consuming and fuel-restoring reaction counts are integrated separately. Because copying and assembly change multiple coordinates jointly, the previous single-coordinate signed information-flow formula is not applied here.",
        "",
        "## Matched stored energy, changing residual access",
        "",
        "Illustrative common law: B=4, a=1, d=0.05. Response below is a native source flip's effect on D at lag 1; information is present-time I(S;D). All sweep entries are in the evidence.",
        "",
        "| Cut | Preparation | Mean fuel | Link on | I(S;D), bits | Source→D response | First fuel-zero hit | Now at zero |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    selected = cases["B4_a1_d0.05"]
    for t in (0, 1, 10, 50, 100):
        for name, prep in selected["preparations"].items():
            row = next(r for r in prep["cuts"] if r["time"] == t)
            s = row["snapshot"]
            lines.append(
                f"| {t} | {name} | {s['fuel_mean']:.6f} | {s['link_on_probability']:.6f} | {s['source_receiver_bits']:.6f} | {response(row):.6f} | {row['first_exhaustion_probability']:.6f} | {s['fuel_zero_probability']:.6f} |"
            )
    lines += [
        "",
        "## Native damage and subsequent repair",
        "",
        "At time 5, condition on a native thermal G=1→0 event. The initial law is weighted by that event's flux, and its rate is retained. Evolve the post-event law using the unchanged generator. The comparison law skips that one event from the same pre-event distribution. It is a conditional effect comparison, not an external free reset. Link occupancy after damage records repeated assembly and breakdown; it is neither first repair nor permanent recovery.",
        "",
        "For the same B=4, a=1, d=0.05 law, from the unbuilt preparation:",
        "",
        "| Elapsed after event | Link on, damaged | Link on, skip event | Source→D response, damaged | Source→D response, skip event |",
        "|---:|---:|---:|---:|---:|",
    ]
    damaged = selected["preparations"]["unbuilt"]
    for r in damaged["aftermath"]:
        a, b = r["after_event"], r["skip_event_reference"]
        lines.append(
            f"| {r['elapsed']} | {a['snapshot']['link_on_probability']:.6f} | {b['snapshot']['link_on_probability']:.6f} | {response(a):.6f} | {response(b):.6f} |"
        )
    lines += [
        "",
        f"The conditioned event has instantaneous rate {damaged['breakdown_event_rate']:.6f} at time 5. This rate is not the probability of a breakdown during a unit interval.",
        "",
        "## What changes the interpretation",
        "",
        "The prebuilt preparation has the larger lag-1 response at cut 0, but the initially unbuilt preparation has the larger response at cut 1 in the illustrated law. The cuts retain fuel, link state and correlations together. Neither the opening link state nor initial content alone fixes later access. The free-energy mismatch above prevents interpreting this crossing as a universal construction advantage.",
        "",
        "Faster assembly is also faster reversible disassembly in this model. Increasing that kinetic prefactor improves early response but can lower later response. For B=4, d=0.05 and the same unbuilt preparation:",
        "",
        "| Assembly prefactor | Cut | Source→D response | Mean fuel | Assembly fuel debits | Assembly fuel credits |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for rate in (0.25, 1):
        prep = cases[f"B4_a{rate}_d0.05"]["preparations"]["unbuilt"]
        for row in prep["cuts"]:
            if row["time"] in (1, 10):
                bill = row["cumulative_fuel_reactions"]
                lines.append(
                    f"| {rate} | {row['time']} | {response(row):.6f} | {row['snapshot']['fuel_mean']:.6f} | {bill[2]:.6f} | {bill[3]:.6f} |"
                )
    lines += [
        "",
        "Repeated assembly events are not repeated creation of distinct access. The faster case records nearly ten fuel-consuming assemblies by time 10, but most are paired with fuel-restoring disassembly. Gross activity, net fuel use and residual access must remain distinguishable. This is a concrete reason to keep the physical bill and residual law beside any flow summary.",
        "",
        "First fuel exhaustion also differs from present exhaustion: at cut 10 in the illustrated unbuilt law the probabilities are 0.708748 and 0.423857. Restored fuel is part of the dynamics, not an accounting reset. After a conditioned breakdown, the link-on probability rises from zero to 0.293074 at elapsed 1, then declines. Reopening a channel does not establish durable recovery or restore its earlier response.",
        "",
        "At the late cuts, present I(S;D) approaches zero while the lagged response remains positive. A native perturbation can still propagate through transient coupling without leaving a persistent present-time record. This separation limits both information-only and response-only summaries; it supplies no positive or negative ethical sign.",
        "",
        "## Evidence and numerical scope",
        "",
        f"Runtime: {result['runtime_seconds']:.2f} seconds, one numerical worker. Maximum per-channel detailed-balance residual: {result['checks']['detailed_balance_max']:.3g}. Maximum expected-fuel accounting residual: {result['checks']['fuel_accounting_max']:.3g}. Maximum upward D(p||π) difference between successive cuts: {result['checks']['free_energy_increase_max']:.3g} (zero means none).",
        "",
        "The analytic equilibrium has independent fair signal bits, link-on probability 1/(1+exp(μ)), and mean fuel B/(1+exp(μ)). The preparations under any fixed generator approach this same distribution. Their transient laws and retained finite-time differences remain distinct; a shared equilibrium is not equivalence of completed continuations or a universal thermal floor.",
        "",
        "This extension models maintenance of an already specified coupling repertoire. It does not demonstrate open-ended generativity, invent new transition types, represent bath microrecords, solve quantum continuation, or select a scalar lushness extent. All native noise and reverse reactions remain present. Finite-time physical access can now be inspected alongside the fuel it uses and the repair pathways it leaves.",
        "",
        "Reproduce:",
        "",
        "    .venv/Scripts/python.exe -m omega_v2.validation.fuel_flow_v0",
        "",
        "[All profiles and declarations](fuel_flow_v0/profiles.json) · [Generators, reaction maps and kernels](fuel_flow_v0/kernels.npz) · [Preceding maintained-reservoir run](local_flow_report_v0.md)",
        "",
    ]
    return "\n".join(lines)


def main():
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    models, arrays = {}, {}
    balance_error = 0.0
    for capacity in (1, 4, 8):
        for assembly in (0.25, 1):
            for damage in (0.005, 0.05):
                m = FuelFlow(capacity, assembly=assembly, damage=damage)
                name = f"B{capacity}_a{assembly}_d{damage}"
                preparations = {
                    label: run_preparation(m, built)
                    for label, built in (("unbuilt", False), ("prebuilt", True))
                }
                models[name] = {
                    "parameters": m.parameters,
                    "equilibrium": m.pi.tolist(),
                    "equilibrium_snapshot": m.snapshot(m.pi),
                    "preparations": preparations,
                }
                for c in range(7):
                    reverse = m.targets[c]
                    balance_error = max(
                        balance_error,
                        float(max(abs(m.pi * m.rates[c] - m.pi[reverse] * m.rates[c, reverse]))),
                    )
                arrays[f"{name}_Q"] = m.q
                arrays[f"{name}_states"] = m.values
                arrays[f"{name}_rates"] = m.rates
                arrays[f"{name}_targets"] = m.targets
                times = sorted(set(CUTS + LAGS + RECOVERY))
                arrays[f"{name}_times"] = np.array(times)
                arrays[f"{name}_K"] = np.stack([m.evolution(t)[0] for t in times])
                arrays[f"{name}_expected_charges"] = np.stack([m.evolution(t)[1] for t in times])
                arrays[f"{name}_first_exhaustion"] = np.stack(
                    [m.exhaustion_probability(t) for t in CUTS]
                )
    runs = [p for m in models.values() for p in m["preparations"].values()]
    checks = {
        "detailed_balance_max": balance_error,
        "fuel_accounting_max": max(r["fuel_accounting_error"] for p in runs for r in p["cuts"]),
        "free_energy_increase_max": max(
            0.0,
            max(
                float(
                    max(
                        np.diff(
                            [r["snapshot"]["nonequilibrium_free_energy_nats"] for r in p["cuts"]]
                        )
                    )
                )
                for p in runs
            ),
        ),
    }
    result = {
        "schema": "finite-fuel-local-flow-v0",
        "date": "2026-10-03",
        "frames": "integer bit masks over (S,R,D,G,F), including empty and whole",
        "channel_names": FuelFlow.channel_names,
        "charge_columns": [
            "copy_fuel_debits",
            "copy_fuel_credits",
            "assembly_fuel_debits",
            "assembly_fuel_credits",
        ],
        "cut_times": CUTS,
        "response_lags": LAGS,
        "recovery_times": RECOVERY,
        "source_hashes": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (
                Path(__file__),
                ROOT / "omega_v2/finite/fuel_flow.py",
                ROOT / "omega_v2/finite/local_flow.py",
            )
        },
        "models": models,
        "checks": checks,
        "runtime_seconds": time.perf_counter() - started,
    }
    np.savez_compressed(OUT / "kernels.npz", **arrays)
    (OUT / "profiles.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    (OUT.parent / "fuel_flow_report_v0.md").write_text(make_report(result), encoding="utf-8")
    print(
        json.dumps(
            {
                "models": len(models),
                "preparations": len(runs),
                "checks": checks,
                "runtime_seconds": result["runtime_seconds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
