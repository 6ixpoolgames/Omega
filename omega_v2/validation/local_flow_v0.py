"""Small dynamic continuation probe; independent reconstruction, not Opus replication."""

import os

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from omega_v2.finite.local_flow import Flip, LocalFlow

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2/local_flow_v0"
LAGS = (0, 0.01, 0.1, 1, 10, 100)
DRIVES = (0, 2, 4, 8)


def apparatus(kind, drive):
    # Same native noise and local update family in every six-register case.
    channels = [Flip(i, 0.02 if i == 0 else 0.1) for i in range(6)]

    def link(source, target, invert=False, gate=None):
        channels.append(Flip(target, 1, drive, (source,), 1 if invert else 2, gate))

    if kind == "sensor":
        link(0, 1)
    elif kind == "relay":
        for i in range(5):
            link(i, i + 1)
    elif kind == "fan":
        for i in range(1, 6):
            link(0, i)
    elif kind == "gated_relay":
        for i in range(4):
            link(i, i + 1, gate=5 if i == 2 else None)
    elif kind == "two_clocks":
        for i in (0, 2):
            link(i + 1, i, invert=True)
            link(i, i + 1)
    elif kind == "ring4":
        link(3, 0, invert=True)
        for i in range(3):
            link(i, i + 1)
    elif kind == "parity":
        channels.append(Flip(2, 1, drive, (0, 1), 6))
    elif kind not in ("disconnected", "passive_pair"):
        raise ValueError(kind)
    energy = None
    if kind == "passive_pair":
        states = np.arange(64)
        energy = 2 * ((states & 1) ^ ((states >> 1) & 1))
    return LocalFlow(6, channels, energy)


def analyze(model):
    flow = model.signed_flow()
    return {
        "stationary": model.pi.tolist(),
        "thermodynamics": model.thermodynamics(),
        "signed_flow_bits_per_time": flow,
        "signed_flow_sum": float(sum(flow)),
        "flow_complement_error": max(abs(flow[i] + flow[63 ^ i]) for i in range(64)),
        "stationarity_error": float(max(abs(model.pi @ model.q))),
        "profiles": [model.profiles(t) for t in LAGS],
        "channels": [asdict(c) for c in model.channels],
        "energy": model.energy.tolist(),
    }


def lag(row, t):
    return next(p for p in row["profiles"] if p["lag"] == t)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    kernels = {}
    for kind in (
        "disconnected",
        "sensor",
        "relay",
        "fan",
        "gated_relay",
        "two_clocks",
        "ring4",
        "parity",
        "passive_pair",
    ):
        for drive in (0,) if kind == "passive_pair" else DRIVES:
            name = f"{kind}_d{drive}"
            model = apparatus(kind, drive)
            results[name] = analyze(model)
            kernels[f"{name}_Q"] = model.q
            kernels[f"{name}_channel_rates"] = model.rates
            kernels[f"{name}_K"] = np.stack([model.kernel(t) for t in LAGS])
    model = apparatus("gated_relay", 4)
    cuts = {}
    for value in (0, 1):
        p = model.pi * (model.bits[:, 5] == value)
        p /= p.sum()
        cuts[str(value)] = {
            "initial_law": p.tolist(),
            "profiles": [model.profiles(t, p) for t in LAGS],
        }
    result = {
        "version": "local_flow_v0",
        "n": 6,
        "lags": LAGS,
        "choice": "Retain the joint transition kernel, signed cut flows, held information, incremental prediction and event-conditioned flip response separately. No lushness score.",
        "all_frames": "Mask 0..63; low bit is site 0; array axes [frame_mask][initial_site]",
        "source_hashes": {
            str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__), ROOT / "omega_v2/finite/local_flow.py")
        },
        "cases": results,
        "gated_relay_d4_initial_gate": cuts,
    }
    (OUT / "profiles.json").write_text(
        json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    np.savez_compressed(OUT / "kernels.npz", **kernels)
    report(results, cuts)
    print(
        json.dumps(
            {
                "cases": len(results),
                "lags": LAGS,
                "max_stationarity_error": max(r["stationarity_error"] for r in results.values()),
                "max_flow_complement_error": max(
                    r["flow_complement_error"] for r in results.values()
                ),
            }
        )
    )


def report(data, cuts):
    lines = [
        "# Local flow and continuation response v0",
        "",
        "3 October 2026 · exploratory classical adapter",
        "",
        "## What changed",
        "",
        (
            "This independently implemented six-register model builds on Opus's flow-probe form, not its "
            "unavailable code. It retains K(t)=exp(tQ), the complete joint transition law, and compares "
            "separate projections of it. No scalar lushness score or preferred architecture is imposed. "
            "Thirty-three small parameter cases and six actual lags are evaluated by finite matrices."
        ),
        "",
        "## One local rate family",
        "",
        (
            "Each reservoir mechanism flips one register. With target predicate f of other registers, "
            "the rate is k exp((-Delta E + mu d)/2), where d=+1 towards f and -1 away. "
            "An optional gate multiplies both forward and reverse rates by another register's value. "
            "Predicates never depend on the flipped register, so the forward/reverse ratio is "
            "exp(-Delta E+mu d). Energy and chemical work are in thermal units."
        ),
        "",
        (
            "Every site has an undriven noise mechanism, rate 0.02 at site 0 and 0.1 elsewhere before "
            "the energy factor. Directed mechanisms have prefactor 1 and drives 0,2,4,8. "
            "All channel truth tables, gates and rates are in the evidence. Geometry is the declared "
            "coupling network; clock, sensor and relay are descriptions of that wiring, not scoring labels. "
            "Changing wiring changes the physical model. No equal construction or equal burn claim is made."
        ),
        "",
        (
            "Zero drive gives detailed balance with exp(-E). The separate passive-pair control has "
            "E=2 when sites 0 and 1 disagree. Other energy tables are zero. Reservoir channels stay "
            "distinct when computing entropy production, so opposite driven mechanisms are not hidden "
            "by summing their rates first. The bath's microscopic records are not represented: this "
            "is an open-system adapter with maintained reservoirs, not the complete quantum field or "
            "a finite-fuel generativity experiment. Local updates do not establish a relativistic light cone."
        ),
        "",
        "## Three distinct questions",
        "",
        "- Held information: I(X_i(0); X_F(t)), using the actual joint initial law and K(t).",
        "- Extra prediction: I(X_i(0); X_rest(t) | X_rest(0)). A perfect existing copy can make this zero.",
        (
            "- Flip response: sum_x w_i(x) TV(K(t)(x)|F, K(t)(x xor 2^i)|F). "
            "Here w_i is the normalized actual flux of the native undriven flip mechanism "
            "under the initial law; its event rate is also retained. The paired reference skips "
            "that flip. This is a counterfactual response contrast, not an additional sampled branch, "
            "an accessible decoder, or a positive/negative value assignment."
        ),
        "",
        (
            "These are computed for every site and every subset, including the whole and empty frame. "
            "No minimum-frame winner or average over frame sizes is used to replace the arrays. "
            "The generator retains joint compatibility: all future marginals come from one joint law. "
            "It does not make separate interventions or optimal responses jointly realizable."
        ),
        "",
        "## Copy fidelity versus extra prediction",
        "",
        "Sensor, site 0 to site 1, lag 1. CTL conditions on all other sites' present.",
        "",
        "| Drive | Held bits | Extra prediction bits | Flip response TV | Entropy production |",
        "|---|---:|---:|---:|---:|",
    ]
    for d in DRIVES:
        row = data[f"sensor_d{d}"]
        p = lag(row, 1)
        lines.append(
            f"| {d} | {p['held_bits'][2][0]:.6f} | {p['incremental_bits'][0]:.6f} | "
            f"{p['flip_response_tv'][2][0]:.6f} | {row['thermodynamics']['entropy_production_nats_per_time']:.6f} |"
        )
    lines += [
        "",
        "## Dependence on the physical cut",
        "",
        (
            "Same gated-relay generator and drive 4. Only the initial cut is conditioned "
            "on gate register 5 being off or on; it subsequently evolves normally and is not clamped. "
            "The gated link is 2 to 3 in the chain 0 to 1 to 2 to 3 to 4. "
            "The table shows source-0 flip response at site 4."
        ),
        "",
        "| Lag | Initially off | Initially on |",
        "|---|---:|---:|",
    ]
    for a, b in zip(cuts["0"]["profiles"], cuts["1"]["profiles"], strict=True):
        lines.append(
            f"| {a['lag']} | {a['flip_response_tv'][16][0]:.6f} | {b['flip_response_tv'][16][0]:.6f} |"
        )
    lines += ["", "## Equilibrium and signed flow", ""]
    passive = data["passive_pair_d0"]
    p = lag(passive, 1)
    lines.append(
        f"Passive pair: entropy production {passive['thermodynamics']['entropy_production_nats_per_time']:.3g}; "
        f"activity {passive['thermodynamics']['activity_per_time']:.6f}; "
        f"site-0 to site-1 held information {p['held_bits'][2][0]:.6f} bits; "
        f"flip response {p['flip_response_tv'][2][0]:.6f}."
    )
    lines += [
        "",
        (
            "Signed flow is explicitly the contribution of updates within F to dI(F:F-complement)/dt, "
            "in bits per unit time. Complementary terms cancel at stationarity. We do not sum magnitudes "
            "and call that the same quantity. Nonzero individual flows and their signs stay in the file."
        ),
        "",
        "## Scope of the result",
        "",
        (
            "The three readouts can disagree without the physical model becoming inconsistent. "
            "The complete lagged law retains the relations their summaries omit. Its restart identity "
            "K(s+t)=K(s)K(t) is checked, as are detailed balance, complementary signed flow and "
            "the exact perfect-copy conditional-information case. The response magnitude can be high "
            "for destructive propagation too; it has no ethical sign. Construction, fuel depletion, "
            "explicit bath records and a lushness extent remain further work."
        ),
        "",
        (
            "The relay has only five links. Only those sites and listed lags are evaluated; "
            "no fitted longer propagation range or universal gas comparison is claimed. "
            "The all-frame arrays, rather than the selected tables above, are the experimental output."
        ),
        "",
        "## Reproduction and evidence",
        "",
        "    .venv/Scripts/python.exe -m omega_v2.validation.local_flow_v0",
        "",
        "[Profiles and model declarations](local_flow_v0/profiles.json) · [Generators and kernels](local_flow_v0/kernels.npz)",
        "",
        (
            "Stochastic-thermodynamic reference: [Horowitz and Esposito](https://arxiv.org/abs/1402.3276). "
            "The earlier [flow-note assessment](opus_flow_note_2026-10-03.md) explains the motivation."
        ),
        "",
    ]
    (OUT.parent / "local_flow_report_v0.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
