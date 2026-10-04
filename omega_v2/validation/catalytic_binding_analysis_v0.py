"""Readable tables from the saved catalytic continuation run; no simulation."""

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2"


def cut(model, name, time):
    return next(r for r in model["preparations"][name]["cuts"] if r["time"] == time)


def profile(row, lag=1):
    return next(p for p in row["profiles"] if p["lag"] == lag)


def main():
    data = json.loads((OUT / "catalytic_binding_v0/profiles.json").read_text(encoding="utf-8"))
    models = data["models"]
    lines = [
        "# Catalytic continuation, propagation and recovery — exploratory run v0",
        "",
        "4 October 2026. Three exact 1,792-state classical laws. Four physical preparations and equilibrium under each law; cuts 0,1,5,20; response lags 1,5; 74 declared frames and 43 reaction channels. No outcome was required to win.",
        "",
        "## Finding",
        "",
        "Composition now changes subsequent construction: an aligned bonded pair supplies an additional reversible pathway for a neighboring bond reaction, and the resulting bond can assist another. This mechanism is specified in the physics. Its existence is an implementation witness, not a discovered law of generativity. The run asks what that mechanism actually does to subsequent assembly, spatial response and recovery with noise, mobility, costs and reversals retained.",
        "",
        "Stronger assistance greatly raises the probability of having formed a four-particle chain at least once, but changes its later occupancy much less. Most added construction is reversed. A native internal flip can now affect future bond geometry; selected distant responses grow while other responses shrink. More frequent first restoration after breakage does not imply better later retention. These are distinct deformations of one residual process, not a scalar ranking.",
        "",
        "## Common physical model",
        "",
        "Four identical particles occupy five reflecting-line sites. A site is empty, 0 or 1; the internal bit moves with its particle. No organism, constructor or beneficiary labels enter the rates. Native internal flips have rate 0.05; adjacent unequal bits exchange at rate 1 whether bonded or unbound. A bonded component of size n translates at rate 1/n when space permits. The dense 'dispersed' preparation below is two separated pairs, not a dilute molecular gas.",
        "",
        "The earlier reversible bond/fuel law is retained: B=3 fuel/spent packets, E=4(F+number of bonds), thermal formation/breakdown rates 0.02 exp(∓2), fuel-assisted formation 0.25F, and reverse disassembly 0.25(3−F). Equilibrium is π(x) proportional to binomial(3,F) exp(−E). Bonds are energetically costly in this model; this assumption is not universal chemistry. The shared fuel pool is well mixed and the heat bath implicit.",
        "",
        "A present bond whose two endpoint bits agree supplies an additional pathway for the adjacent bond reaction. Its rate is (exp(b)−1) times the original fuel-assisted rate. One catalyst therefore makes the total rate exp(b) times the background; two catalysts contribute parallel pathways. The catalyst and its internal bits are unchanged in that reaction. BOTH formation and reversal are accelerated by the same factor, preserving detailed balance, energies and π. Native flips can open or close this catalytic condition.",
        "",
        "The barrier reductions b=0,1,2 are physical kinetic parameters in thermal units, not lushness multipliers. Each law is shared by all preparations. Changing b compares different kinetics, not a cost-free intervention available to an agent. No primitive transition is invented during a run: composition changes which existing mechanisms are available at the current state.",
        "",
        "| Preparation | Occupied sites | Initial bonds | Fuel | D(p||π), nats |",
        "|---|---|---|---:|---:|",
    ]
    configs = {
        "dispersed": ("0,1,3,4", "none"),
        "contact_unbound": ("0,1,2,3", "none"),
        "seeded": ("0,1,2,3", "0–1"),
        "assembled": ("0,1,2,3", "0–1,1–2,2–3"),
    }
    for name, (sites, bonds) in configs.items():
        s = cut(models["1"], name, 0)["snapshot"]
        lines.append(
            f"| {name} | {sites} | {bonds} | {s['fuel_mean']:.0f} | {s['free_energy_nats']:.6f} |"
        )
    lines += [
        "",
        "All four have independent fair internal bits and stored energy 12. Contact-unbound, dispersed and fully assembled match free energy too. The seeded preparation has ln 3 less free energy, from fuel-stock degeneracy; no seed-versus-unbound advantage is treated as a fully matched comparison. The fuel-free assembled preparation can disassemble and regain fuel. Zero fuel is not a terminal state.",
        "",
        "## Construction, persistence and bills",
        "",
        "Seeded preparation at cut 5. First occurrence is computed with an absorbing diagnostic copy; the actual residual law continues through breakdown and reversal. Gross assembly counts are debits, reverse counts are credits; their difference is net fuel depletion. Catalytic counts in the evidence are subsets of these bills and must not be added a second time.",
        "",
        "| b | P(chain occurred by 5) | P(chain present at 5) | Mean bonds at 5 | Fuel assembly debits | Reverse credits |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for b, m in models.items():
        r = cut(m, "seeded", 5)
        s, bill = r["snapshot"], r["expected_bill"]
        lines.append(
            f"| {b} | {r['first_tetramer_probability']:.6f} | {s['tetramer_probability']:.6f} | {s['bonds_mean']:.6f} | {bill[0]:.6f} | {bill[1]:.6f} |"
        )
    lines += [
        "",
        "The matched, fully assembled preparation also loses its initial chain faster with stronger catalysis:",
        "",
        "| b | P(chain present at cut 1) | Mean bonds at cut 1 | Mean bonds at cut 5 |",
        "|---:|---:|---:|---:|",
    ]
    for b, m in models.items():
        a, z = cut(m, "assembled", 1)["snapshot"], cut(m, "assembled", 5)["snapshot"]
        lines.append(
            f"| {b} | {a['tetramer_probability']:.6f} | {a['bonds_mean']:.6f} | {z['bonds_mean']:.6f} |"
        )
    lines += [
        "",
        "A path monitor records one local cascade: the 0–1 bond assists formation of 1–2, then that still-present 1–2 bond assists formation of 2–3. Losing or moving the intermediate bond resets the unfinished monitor. This observes one spatially anchored sequence, not every possible construction lineage or an identity tracked after movement. Once observed, the monitor retains that historical fact while the physical process keeps evolving.",
        "",
        "| b | Seeded: P(sequence by 5) | Seeded: P(sequence by 20) | Initially unbound: P(sequence by 20) |",
        "|---:|---:|---:|---:|",
    ]
    for b, m in models.items():
        rows = (cut(m, "seeded", 5), cut(m, "seeded", 20), cut(m, "contact_unbound", 20))
        vals = [r["two_stage_sequence_probability"] for r in rows]
        lines.append(f"| {b} | {vals[0]:.6f} | {vals[1]:.6f} | {vals[2]:.6f} |")
    lines += [
        "",
        "Zero at b=0 follows from the absence of the monitored catalytic pathways. The monitor's physical marginal was checked against the unmonitored dynamics. These probabilities establish finite, reversible reuse in this specified model; they are not evidence for unbounded generativity.",
        "",
        "## Consequence across physical frames",
        "",
        "For native reaction c at cut law p, contexts x are weighted by p(x)r_c(x)/Σp(x)r_c(x). Response at lag τ is the average total-variation distance between the future frame laws starting from x and from the reaction's target. The reaction rate Σp(x)r_c(x) is reported separately. Absent reactions have an explicit false event_present flag; their zero array entries are not measured zero effects.",
        "",
        "This is a state-resolved counterfactual diagnostic, not a free intervention, an attainable decoder, or a signed benefit. The full event law remains alongside it. No average or vote over frames defines a winner. Frames comprise the previous 64 site-subset/fuel views plus each bond alone/with fuel and the joint bond field alone/with fuel. They do not exhaust every possible physical observer or cost of reading.",
        "",
        "The table follows a native bit flip at site 0 from the seeded preparation at cut 0. Each target is a physical site's full empty/0/1 state. Response can therefore include altered occupancy, not merely delivery of a readable bit. All five source sites, all other reactions and joint frames remain in the raw profiles.",
        "",
        "Site separation indexes the spatial profile, not a strict causal distance: the shared well-mixed fuel stock also couples spatially separated reactions. This probe cannot isolate transmission along neighboring bonds from transmission through that common resource. Spatially resolving fuel would be a further physical extension, not a correction factor to this readout.",
        "",
        "| b | Lag | Site 0 | Site 1 | Site 2 | Site 3 | Site 4 | Joint bond field |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for b, m in models.items():
        for lag in (1, 5):
            v = profile(cut(m, "seeded", 0), lag)["reaction_response_tv"]
            vals = [v[1 << j][0] for j in range(5)] + [v[72][0]]
            lines.append(f"| {b} | {lag} | " + " | ".join(f"{v:.6f}" for v in vals) + " |")
    lines += [
        "",
        "At b=0, the geometric process does not depend on internal bits; the bit-to-bond response vanishes up to numerical error. Turning assistance on creates that physical dependence. Its nonzero response confirms the specified coupling rather than independently discovering it. The magnitude, delay and competing propagation changes are the probe's output. There are only five sites; no asymptotic decay length is inferred.",
        "",
        "At b=2, cut 0 and lag 1, seeded versus dispersed gives greater site-4 response (0.014484 versus 0.008928), but lower joint response at the other four sites (0.358317 versus 0.400038). Farther propagation on one coordinate does not establish larger total access. In the exactly resource-matched assembled/contact-unbound comparison, the all-frame profiles also cross.",
        "",
        "## Native breakage and restoration",
        "",
        "Start from the seeded law at cut 5 and condition on an actual thermal breakdown of the bond at physical edge 0. Its event rate and flux-conditioned pre/post laws are retained. Evolve both the post-break law and a skipped-event reference under the same autonomous dynamics. This is not a clamped controller. The breakdown releases bond energy to the implicit bath. Rates are hazards, not finite-interval probabilities.",
        "",
        "Conditioning produces a different damage ensemble at each b. Comparisons below concern each law's own native failures, not the isolated effect of b on one identical post-damage distribution. Restoring an edge means the local bond is present again, possibly between different particles; it does not prove recovery of the complete earlier access structure.",
        "",
        "| b | Time since break | P(first local restoration) | P(local bond present now) | TV(taken, skipped full residual laws) |",
        "|---:|---:|---:|---:|---:|",
    ]
    for b, m in models.items():
        for r in m["recovery"]["cuts"][1:]:
            lines.append(
                f"| {b} | {r['elapsed']} | {r['first_edge_restoration_probability']:.6f} | {r['taken']['snapshot']['bond_probabilities'][0]:.6f} | {r['whole_law_tv']:.6f} |"
            )
    lines += [
        "",
        "Stronger assistance raises first-return probability here, but late bond occupancy is slightly lower. A return is not permanence: every formed bond retains a positive thermal breakdown hazard. Full residual laws and all reaction/frame responses after breakage remain available rather than being replaced with a binary 'recovered' score.",
        "",
        "## Scope, checks and evidence",
        "",
        "The common equilibrium distribution is unchanged by assistance. Equilibrium still has native events and lagged response, including a small bit-to-bond response when catalysis is on. Zero net equilibrium currents do not imply zero consequence. This is a bath-coupled finite classical substrate, not a closed universe, quantum branching calculation, gas defeat, lushness extent or ethical verdict.",
        "",
        "The next unresolved issue is how to compare these joint residual deformations without allowing gross turnover, a privileged destination or a selected recovery target to stand in for the entire field. This run improves the substrate on which the adopted aggregation can be investigated; it does not finish or replace that aggregation.",
        "",
        f"Numerical run: {data['runtime_seconds']:.2f} seconds with one numerical worker. Three new focused tests cover channel reversibility, catalyst preservation, physical marginal preservation of the path monitor, fuel/bond accounting, reflection/bit inversion and preparation matching. Together with the existing spatial/fuel/local-flow checks, 12 tests passed. Lint passed. These are implementation checks, not independent empirical evidence.",
        "",
        "Maximum run residuals:",
        "",
    ]
    for key in (
        "fuel_balance",
        "bond_balance",
        "probability_mass",
        "detailed_balance",
        "kernel_rows",
    ):
        lines.append(f"- {key}: {max(m['checks'][key] for m in models.values()):.3g}.")
    lines += [
        "",
        "Reproduce:",
        "",
        "    .venv/Scripts/python.exe -m omega_v2.validation.catalytic_binding_v0",
        "    .venv/Scripts/python.exe -m omega_v2.validation.catalytic_binding_analysis_v0",
        "",
        "[Profiles, actual laws, bills, monitor results and source hashes](catalytic_binding_v0/profiles.json) · [Comparison counts](catalytic_binding_v0/comparison_summary.json)",
        "",
        "[No-assistance kernels](catalytic_binding_v0/barrier_0_kernels.npz) · [b=1 kernels](catalytic_binding_v0/barrier_1_kernels.npz) · [b=2 kernels](catalytic_binding_v0/barrier_2_kernels.npz)",
        "",
        "NPZ files retain states, channel rates/targets, reward rates, sparse Q, equilibrium and exact numerical transition kernels at both lags. No simulated sample trajectories or fitted parameters are substituted for these laws.",
        "",
        "[Previous thermal/mobile comparison](thermal_binding_report_v0.md)",
        "",
    ]
    comparisons = []
    for b, m in models.items():
        for t in data["cuts"]:
            a, z = profile(cut(m, "contact_unbound", t)), profile(cut(m, "assembled", t))
            common = np.array(a["event_present"]) & np.array(z["event_present"])
            delta = (np.array(z["reaction_response_tv"]) - a["reaction_response_tv"])[:, common]
            comparisons.append(
                {
                    "barrier": b,
                    "cut": t,
                    "lag": 1,
                    "comparison": "assembled minus contact_unbound",
                    "common_events": int(common.sum()),
                    "greater": int((delta > 1e-10).sum()),
                    "lower": int((delta < -1e-10).sum()),
                    "tied": int((abs(delta) <= 1e-10).sum()),
                    "tolerance": 1e-10,
                }
            )
    (OUT / "catalytic_binding_v0/comparison_summary.json").write_text(
        json.dumps(
            {
                "note": "Counts only demonstrate crossings; they are not physical weights or votes.",
                "rows": comparisons,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (OUT / "catalytic_binding_report_v0.md").write_text("\n".join(lines), encoding="utf-8")
    print("Wrote catalytic continuation report and comparison summary.")


if __name__ == "__main__":
    main()
