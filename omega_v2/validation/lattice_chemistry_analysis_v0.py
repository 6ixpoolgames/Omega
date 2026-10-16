"""Small descriptive analysis of the 2D pilot, including physical event replay."""

import gzip
import json
from pathlib import Path

import numpy as np

from omega_v2.finite.lattice_chemistry import Event, LatticeChemistry, Parameters, State

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2/lattice_chemistry_v0"
REPORT = OUT.parent / "lattice_chemistry_report_v0.md"


def mean_se(values):
    a = np.asarray(values, dtype=float)
    return float(a.mean()), float(a.std(ddof=1) / np.sqrt(len(a)))


def main():
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    audit = []
    for row in summary["runs"]:
        data = json.loads(gzip.decompress((OUT / row["trajectory"]).read_bytes()))
        model = LatticeChemistry(Parameters(**data["parameters"]))
        initial = data["initial"]
        state = State([tuple(p) for p in initial["positions"]], initial["internal"].copy(),
                      {tuple(b) for b in initial["bonds"]}, initial["fuel"])
        seen = state.bonds.copy()
        ancestry = {b: {b} for b in state.bonds}
        new_cat, repeated_cat, ancestry_returns, max_ancestry = 0, 0, 0, 0
        first_empty = None
        for time, kind, members, direction, catalyst, rate in data["events"]:
            pair, source = tuple(members), tuple(catalyst)
            if kind in ("thermal", "fuel", "catalytic"):
                if pair in state.bonds:
                    del ancestry[pair]
                else:
                    if source:
                        new_cat += pair not in seen
                        repeated_cat += pair in seen
                        ancestry_returns += pair in ancestry[source]
                        ancestry[pair] = ancestry[source] | {pair}
                        max_ancestry = max(max_ancestry, len(ancestry[pair]))
                    else:
                        ancestry[pair] = {pair}
                    seen.add(pair)
            model.apply(state, Event(kind, pair, rate, tuple(direction), source))
            model.validate(state)
            if state.fuel == 0 and first_empty is None:
                first_empty = time
        assert json.loads(json.dumps(state.record())) == data["final"]
        audit.append({"configuration_id": row["configuration_id"], "replicate": row["replicate"],
                      "new_catalytic_pairs": new_cat, "repeat_catalytic_pairs": repeated_cat,
                      "ancestry_returns": ancestry_returns,
                      "max_distinct_ancestral_pairs": max_ancestry,
                      "distinct_formed_pairs_including_seed": len(seen),
                      "first_empty_fuel_time": first_empty})
    (OUT / "history_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    configs = summary["configurations"]
    lines = ["# Reversible 2D chemistry: exploratory pilot v0", "", "2026-10-04.", "",
             ("The first 2D substrate run is complete: 32 configurations, 12 trajectories each, "
             f"384 trajectories and {sum(r['events'] for r in summary['runs']):,} physical events. "
             f"Simulation took {summary['runtime_seconds']:.2f} seconds with ten workers. "
             "No lushness score was computed. This is a small bracket of physical behavior, "
             "not an exhaustive survey or an equilibrium-gas comparison."), "",
             ("[Model and rationale](lattice_chemistry_protocol_v0.md); "
             "[comparison with established models](model_comparison_map_2026-10-04.md); "
             "[run manifest](lattice_chemistry_v0/manifest.json); "
             "[full summary](lattice_chemistry_v0/summary.json); "
             "[historical audit](lattice_chemistry_v0/history_audit.json). "
             "The data directory also contains all 384 compressed event histories."), "",
             "## What changed from the line model", "",
             ("Particles increased from four to 16/36 and can move in two dimensions. "
             "Loops, bypasses, compact clusters and local crowding can occur. Bonds are "
             "favorable contacts whose energies depend on two conformations; fuel energy "
             "is a separate parameter. Local templates accelerate a reversible chemical "
             "path. The shared finite reservoir and implicit heat bath remain. "
             "This is a coarse hybrid of established ingredients, not a replication of "
             "a particular molecular system. The square template rule is an explicit "
             "mechanistic hypothesis, not a newly observed law of chemistry."), "",
             "## Descriptive results", "",
             ("All figures below refer to t=20 unless a time curve is shown. "
             "Twelve replicates support an initial description, not precise boundaries. "
             "A dispersed initial condition is fuelled and unbonded; it is not equilibrium."), "",
             "### Bond strength and density", "",
             ("N=36, dispersed start. Entries are mean ± one Monte Carlo standard error. "
             "b is the catalytic barrier reduction in kBT units, not composition depth."), "",
             "| Density | Bond strength | b | Bonds | Largest component | Fuel remaining |",
             "|---|---:|---:|---:|---:|---:|"]
    for c in configs:
        p = c["parameters"]
        if p["particles"] != 36 or c["preparation"] != "dispersed":
            continue
        last = c["cuts"][-1]
        entries = [f"{last['mean'][k]:.2f} ± {last['standard_error'][k]:.2f}"
                   for k in ("bonds", "largest", "fuel")]
        lines.append(f"| {c['density']:.3f} | {p['bond_strength']:g} | "
                     f"{p['catalytic_barrier']:g} | " + " | ".join(entries) + " |")
    lines += ["", ("Stronger contacts produce larger retained assemblies in these runs. "
              "They also leave more fuel at the deadline in each listed density/catalysis "
              "comparison. That is consistent with reduced turnover and stronger passive "
              "assembly; bond stock is not simply proportional to fuel spent. "
              "Contact energetics, kinetics and preparation jointly determine the result. "
              "More densely packed systems retain larger components here, but larger is "
              "not itself a continuation or lushness verdict."), "",
              "![Assembly and fuel through time](lattice_chemistry_v0/time_profiles.png)", "",
              "### Catalysis changes history more than the final bond stock", "",
              ("Paired differences b=2 minus b=0, using identical initial configurations "
              "per replicate and independent reaction randomness. SE is computed across "
              "replicate differences. No multiple-comparison significance claim is made."), "",
              ("| N | Density | Strength | Start | Change in bonds ± SE | Change in fuel ± SE | "
              "Catalytic formations | Catalytic reversals |"),
              "|---:|---:|---:|---|---:|---:|---:|---:|"]
    comparisons = []
    for c in configs:
        p = c["parameters"]
        if p["catalytic_barrier"] != 2:
            continue
        base_id = c["id"] - 2
        a = [r for r in summary["runs"] if r["configuration_id"] == c["id"]]
        b = [r for r in summary["runs"] if r["configuration_id"] == base_id]
        differences = {k: mean_se([x["snapshots"][-1][k] - y["snapshots"][-1][k]
                                  for x, y in zip(a, b, strict=True)])
                       for k in ("bonds", "fuel", "largest")}
        comparisons.append({"configuration_id": c["id"], "baseline_id": base_id,
                            "differences_mean_se": differences})
        last = c["cuts"][-1]["mean"]
        db, df = differences["bonds"], differences["fuel"]
        lines.append(f"| {p['particles']} | {c['density']:.3f} | {p['bond_strength']:g} | "
                     f"{c['preparation']} | {db[0]:+.2f} ± {db[1]:.2f} | "
                     f"{df[0]:+.2f} ± {df[1]:.2f} | {last['catalytic_forward']:.2f} | "
                     f"{last['catalytic_reverse']:.2f} |")
    cat_audit = [a for a in audit if configs[a["configuration_id"]]["parameters"]["catalytic_barrier"]]
    cat_runs = [r for r in summary["runs"]
                if configs[r["configuration_id"]]["parameters"]["catalytic_barrier"]]
    new = sum(a["new_catalytic_pairs"] for a in cat_audit)
    repeat = sum(a["repeat_catalytic_pairs"] for a in cat_audit)
    deeper = sum(r["snapshots"][-1]["max_construction_depth"] >= 2 for r in cat_runs)
    spontaneous = [r for r in cat_runs
                   if configs[r["configuration_id"]]["preparation"] == "dispersed"]
    spontaneous_hit = sum(r["first_catalytic_construction"] is not None for r in spontaneous)
    lines += ["", ("The endpoint differences are small or mixed in several conditions, despite "
              "many extra catalytic firings. A forward catalytic event is not automatically "
              "an extra surviving bond: it can replace a later background event, reverse, "
              "or accelerate fuel depletion. Most forward firings need not be promptly "
              "reversed through the same channel; thermal loss is a separate route."), "",
              "### Construction history", "",
              (f"- Catalytic construction occurred in {spontaneous_hit}/{len(spontaneous)} "
              "catalysis-enabled dispersed runs, without a prebuilt seed."),
              (f"- {deeper}/{len(cat_runs)} catalysis-enabled trajectories reached at least "
              "two successive catalytic production steps."),
              (f"- Of {new + repeat:,} catalytic formation events, {new:,} first joined that "
              f"physical particle pair and {repeat:,} re-formed a previously present pair."),
              (f"- {sum(a['ancestry_returns'] for a in cat_audit)} catalytic formation events "
              "returned to a pair already in the catalyst's production ancestry. Raw depth "
              "can therefore count recycling; it is not an open-endedness measure."), "",
              ("The no-catalysis arm is zero on specifically catalytic events by construction. "
              "That is not an independent discovery. The nontrivial observations concern "
              "how often templates arise, their subsequent history, resource use and the "
              "retained structures under the same local rules."), "",
              "## Checks and interpretation limits", "",
              ("Five focused tests passed: exhaustive per-mechanism balance over 768 tiny "
              "states, movement/replay and conservation, rotation/renaming symmetry, "
              "kinetic-only catalysis with inventory concentration scaling, and quiescent "
              "deadline handling. All 158,675 saved events were replayed with valid geometry "
              "and inventory and reproduced the final states. Lint passed."), "",
              ("Full microscopic reversibility does not prevent a transient net chemical "
              "current: the initial fuel-rich distribution is out of equilibrium. "
              "Catalysis leaves equilibrium unchanged but changes relaxation times. "
              "The sampled state free-energy coordinate is not an ensemble free-energy "
              "estimate; no distribution entropy was estimated."), "",
              ("Limitations: short horizons and 12 repeats per condition; a chosen template "
              "geometry; rapid-release catalysis without explicit saturation; square-lattice "
              "anisotropy; reflecting boundaries; rigid components without rotation; "
              "shared fuel without transport; and an implicit bath. Strong attractive "
              "contacts naturally favor aggregation, so a large persistent cluster cannot "
              "be called generativity merely because it contains many bonds."), "",
              "## Next useful probe", "",
              ("Retain this as the inexpensive spatial substrate. Before introducing more "
              "chemical detail, compare residual response to the same native local "
              "perturbations in retained aggregates and dispersed configurations. Ask "
              "whether composition changes later physical access, beyond bond stock, "
              "fuel use or templating turnover. Add rotation or local fuel when a specific "
              "observed bottleneck makes their missing resolution relevant. A thermal "
              "comparison needs an actual equilibrium preparation or a controlled "
              "relaxation reference, not an unbonded picture labeled gas."), ""]
    (OUT / "comparisons.json").write_text(json.dumps(comparisons, indent=2), encoding="utf-8")
    REPORT.write_text("\n".join(line for line in lines if plt is not None
                                or not line.startswith("![")), encoding="utf-8")
    if plt is not None:
        plot_profiles(configs)
    print(json.dumps({"new_catalytic_pairs": new, "repeat_catalytic_pairs": repeat,
                      "depth_at_least_2_runs": deeper,
                      "spontaneous_catalytic_runs": spontaneous_hit,
                      "ancestry_returns": sum(a["ancestry_returns"] for a in cat_audit),
                      "report": str(REPORT)}, indent=2))


def plot_profiles(configs):
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.5), sharex=True, constrained_layout=True)
    for c in configs:
        p = c["parameters"]
        if p["particles"] != 36 or c["preparation"] != "dispersed":
            continue
        col = 0 if p["side"] == 12 else 1
        ts = [r["time"] for r in c["cuts"]]
        color = "#2166ac" if p["bond_strength"] == 1 else "#b35806"
        style = "--" if p["catalytic_barrier"] == 0 else "-"
        label = f"bond {p['bond_strength']:g}, " + ("catalysis" if style == "-" else "baseline")
        for row, key in enumerate(("bonds", "fuel")):
            means = np.array([r["mean"][key] for r in c["cuts"]]) / 36
            se = np.array([r["standard_error"][key] for r in c["cuts"]]) / 36
            axes[row, col].plot(ts, means, style, color=color, marker="o", ms=3, label=label)
            axes[row, col].fill_between(ts, means - se, means + se, color=color, alpha=0.08)
    for j, density in enumerate(("1/4", "4/9")):
        axes[0, j].set_title(f"36 particles; occupancy {density}")
        axes[1, j].set_xlabel("Time (single-particle hopping units)")
    axes[0, 0].set_ylabel("Bonds per particle")
    axes[1, 0].set_ylabel("Fuel fraction remaining")
    for ax in axes.flat:
        ax.grid(alpha=0.2)
        ax.set_ylim(bottom=0)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("2D chemistry pilot — dispersed, fuelled initial conditions\n"
                 "12 trajectories per curve; shading: ±1 standard error", fontsize=12)
    fig.savefig(OUT / "time_profiles.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
