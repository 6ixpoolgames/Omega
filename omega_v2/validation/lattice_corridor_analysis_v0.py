"""Report the exploratory corridor and companion dependency panel."""

import json
from math import exp, log1p
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NOTES = ROOT / "docs/research_notes/omega_v2"
OUT = NOTES / "lattice_corridor_v0"
DAMAGE = NOTES / "lattice_template_damage_v0"


def difference(left, right, j, key):
    x = np.array(left["cuts"][j]["chain_means"][key])
    y = np.array(right["cuts"][j]["chain_means"][key])
    return {"difference": float((x-y).mean()),
            "chain_se": float((x-y).std(ddof=1)/np.sqrt(len(x)))}


def main():
    data = json.loads((OUT/"summary.json").read_text(encoding="utf-8"))
    manifest = json.loads((OUT/"manifest.json").read_text(encoding="utf-8"))
    rows = {(r["regime"], r["barrier"], r["preparation"]): r for r in data["groups"]}
    comparisons, stationarity = [], []
    for g in range(9):
        for b in (0, 1, 2):
            for left, right in (("refueled_equilibrium", "equilibrium"),
                                ("dispersed_fueled", "equilibrium"),
                                ("refueled_equilibrium", "dispersed_fueled")):
                a, z = rows[g, b, left], rows[g, b, right]
                comparisons.append({"regime": g, "barrier": b, "left": left, "right": right,
                                    "cuts": [{"time": cut["time"], "readouts": {
                                        k: difference(a, z, j, k) for k in cut["mean"]}}
                                        for j, cut in enumerate(a["cuts"])]})
            a = rows[g, b, "equilibrium"]
            drift = {}
            for k in ("bonds", "contacts", "exposed", "largest", "energy", "fuel"):
                values = (np.array(a["cuts"][-1]["chain_means"][k])
                          - np.array(a["cuts"][0]["chain_means"][k]))
                drift[k] = {"difference": float(values.mean()),
                            "chain_se": float(values.std(ddof=1)/np.sqrt(len(values)))}
            stationarity.append({"regime": g, "barrier": b, "cut20_minus_cut0": drift})
    for g in range(9):
        for prep in manifest["preparations"]:
            for high, low in ((1, 0), (2, 0), (2, 1)):
                a, z = rows[g, high, prep], rows[g, low, prep]
                comparisons.append({"regime": g, "preparation": prep,
                                    "high_barrier": high, "low_barrier": low,
                                    "cuts": [{"time": cut["time"], "readouts": {
                                        k: difference(a, z, j, k) for k in cut["mean"]}}
                                        for j, cut in enumerate(a["cuts"])]})
    (OUT/"comparisons.json").write_text(json.dumps(
        {"comparisons": comparisons, "equilibrium_stationarity": stationarity}, indent=2),
        encoding="utf-8")
    rhats = [v for r in data["equilibrium_diagnostics"] for v in r["split_rhat"].values()
             if v is not None]
    drift_flags = [(r["regime"], r["barrier"], k, v)
                   for r in stationarity for k, v in r["cut20_minus_cut0"].items()
                   if v["chain_se"] and abs(v["difference"]) > 3*v["chain_se"]]
    lines = [
        "# Thermal baselines and a finite contribution corridor", "", "2026-10-05.", "",
        (f"Completed {data['trajectories']:,} full trajectories and {data['events']:,} physical "
         f"events in {data['runtime_seconds']:.2f} seconds with ten workers. The chemical "
         "generator is unchanged. This panel examines where construction leads to subsequent "
         "construction; it does not impose final survival as the criterion."), "",
        ("[Roadmap](contribution_corridor_roadmap_2026-10-05.md) · "
        "[Protocol](lattice_corridor_protocol_v0.md) · "
        "[Full summaries](lattice_corridor_v0/summary.json) · "
        "[All comparisons and stationarity checks](lattice_corridor_v0/comparisons.json)"), "",
        "## Main findings", "",
        ("1. The actual thermal preparation already contains assemblies. At stronger binding, "
        "nearly all particles belong to one component. Calling this baseline dispersed gas "
        "would misdescribe the model's equilibrium."),
        ("2. At b=2, refueling the same equilibrium configurations increases the observed "
        "probability of a newly formed catalytic product subsequently catalysing another "
        "formation in all nine density/strength cells. The fueled dispersed preparation "
        "also exceeds equilibrium on this diagnostic in all nine cells. This is a finite "
        "mechanism corridor, not a lushness ordering or an independent discovery of catalysis."),
        ("3. For refueled equilibrium, intermediate bond strength has the highest reuse "
        "probability among the three tested strengths at every density, for both b=1 and b=2. "
        "Strong binding leaves bigger assemblies and more fuel, but fewer unbound template "
        "opportunities. These observations support a stability/availability tradeoff; they "
        "do not isolate which mechanism causes the whole difference or establish a global optimum."),
        ("4. Some products assist a subsequent formation and then disappear before the final "
        "cut. A final-survival criterion would omit those contributions. These counts retain "
        "construction, repair and repeated material use without assigning an ethical sign."), "",
        "## Thermal preparation and accounting", "",
        ("The target equilibrium is analytically specified by the existing energy law. "
        "Positions and conformations are sampled by a separate collapsed Markov-chain "
        "sampler; bonds and fuel are then drawn from their exact conditional distributions. "
        "Sampler relocations are preparation calculations, not physical motion in the histories."), "",
        (f"Four source chains per regime, each retaining 24 draws after 4,000 burn sweeps "
         f"and 128-sweep spacing, give 96 initial draws. Basic split R-hat ranges "
         f"{min(rhats):.3f}–{max(rhats):.3f} over the five reported observables. This is a "
         "mixing diagnostic, not a certificate of exact equilibrium or independent samples. "
         "The full chain traces and resulting physical-time drift checks are retained."), "",
        (f"There are {len(drift_flags)} physical stationarity coordinates with absolute "
         "cut20-minus-cut0 change greater than three estimated chain standard errors, among "
         "162 inspected coordinates. Only four independent chains underlie those errors; "
         "these multiple exploratory comparisons are neither formal rejection tests nor "
         "proof of stationarity. The approximate baseline remains a material limitation."), "",
        (f"The target's exact mean fuel is 16/(1+exp(4))={16/(1+exp(4)):.6f}. Refueling "
         "changes only the fuel register of each paired equilibrium draw, setting it to 16. "
         f"For the ideal exact-equilibrium preparation the refueled law has a nonequilibrium free-energy "
         f"excess D(q||pi)=16 log(1+exp(4))={16*log1p(exp(4)):.6f} in kBT units. "
         "This includes the distributional cost; the saved state G values alone do not."), "",
        ("Refueled equilibrium versus dispersed fueled matter shares fuel inventory, "
        "particle count and physical laws, but differs in bond/conformation energy and "
        "ensemble information. It is an initial-organization bracket, not a fully "
        "free-energy-matched causal comparison. No seed was manually planted in this panel."), "",
        "## Corridor on subsequent use", "",
        ("P(reuse) is the probability that, by t=20, at least one bond formed through a "
        "catalytic pathway has itself assisted a later formation. The helping bond need "
        "not survive to t=20. Initial bonds have no assigned pre-cut ancestry. Material "
        "pair recurrence is retained; this is not a count of new chemical species."), "",
        "| Density | Strength | Thermal b2 | Refueled b1 | Refueled b2 ± chain SE | Dispersed fueled b2 |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for g, config in enumerate(manifest["regimes"]):
        values = [rows[g, b, p]["cuts"][-1]["mean"]["ever_product_reused"] for b, p in
                  ((2, "equilibrium"), (1, "refueled_equilibrium"),
                   (2, "refueled_equilibrium"), (2, "dispersed_fueled"))]
        se = rows[g, 2, "refueled_equilibrium"]["cuts"][-1]["chain_se"]["ever_product_reused"]
        lines.append(f"| {config['density']:.3f} | {config['parameters']['bond_strength']:.0f} | "
                     f"{values[0]:.3f} | {values[1]:.3f} | {values[2]:.3f} ± {se:.3f} | {values[3]:.3f} |")
    lines += ["", ("The no-catalysis b=0 control is zero on this particular readout by definition; "
              "it is not evidence that b=0 has no consequences or lower lushness. All "
              "noncatalytic reactions, histories and other diagnostics remain in the data. "
              "The grid is an experimental bracket, not a probability measure over worlds."), "",
              "## Stability, available targets and contributions before loss", "",
              ("Refueled equilibrium, b=2, t=20. Productive episodes are newly catalytically "
              "formed bond episodes that subsequently helped construction; loss ends an "
              "episode even if the same pair later reforms. Other histories remain included."), "",
              "| Density | Strength | Largest component | Fuel | Open template opportunities | Productive episodes | Of those, later lost |",
              "|---:|---:|---:|---:|---:|---:|---:|"]
    for g, config in enumerate(manifest["regimes"]):
        m = rows[g, 2, "refueled_equilibrium"]["cuts"][-1]["mean"]
        lines.append(f"| {config['density']:.3f} | {config['parameters']['bond_strength']:.0f} | "
                     + " | ".join(f"{m[k]:.3f}" for k in (
                         "largest", "fuel", "template_opportunities", "productive_products",
                         "productive_products_later_lost")) + " |")
    lines += ["", ("Open template opportunities are geometric opportunities, not independently "
              "executable options: shared fuel, subsequent competition and reversals remain "
              "in the actual dynamics. Dwell integrals and native hazards are provided "
              "separately; summing these quantities would double count different views of "
              "the same history. No such lushness scalar is adopted."), "",
              "## What comes next", "",
              ("The adjacent cells supply a real exploratory corridor for the specified "
              "construction-reuse mechanism. Its thermodynamic baseline is assembled, so "
              "this panel does not settle a dilute-gas comparison. The useful next question "
              "is whether the intermediate-strength advantage survives accounting for "
              "preparation and changes in mobility/fuel availability, and what residual "
              "joint developments the products enable. Expand resolution only when those "
              "questions reveal a missing physical mechanism. Permanence is not required."), "",
              ("Reproduce with `python -m omega_v2.validation.lattice_corridor_v0`, followed "
              "by `python -m omega_v2.validation.lattice_corridor_analysis_v0`. Existing output "
              "directories are protected from overwrite. Four new focused checks cover "
              "analytic marginalization, a tiny exact equilibrium comparison, contribution "
              "after original-template loss, and native class-weight accounting; fourteen "
              "focused checks including earlier chemistry/failure tests passed.")]
    (NOTES/"lattice_corridor_report_v0.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    damage_report()


def damage_report():
    data = json.loads((DAMAGE/"summary.json").read_text(encoding="utf-8"))
    group = data["groups"]["all"]
    eligible = [r for r in data["contexts"] if r["eligible"]]
    weights = np.array([r["total_hazard"] for r in eligible])
    weights /= weights.sum()
    context_errors = []
    for j, cut in enumerate(group["cuts"]):
        errors = {}
        for key in cut["readouts"]:
            values = np.array([r["cuts"][j]["readouts"][key]["difference"] for r in eligible])
            errors[key] = float(np.sqrt(np.sum(weights**2*(values-weights@values)**2)
                                       / (1-weights@weights)))
        context_errors.append({"lag": cut["lag"], "weighted_context_se": errors})
    (DAMAGE/"context_errors.json").write_text(json.dumps(context_errors, indent=2), encoding="utf-8")
    lines = ["# Failures of working catalytic templates", "", "2026-10-05.", "",
             (f"All 384 prior source cuts were retained; {len(eligible)} supported a currently "
              f"working template. 64 native continuations per arm give {len(eligible)*128:,} "
              f"trajectories and {sum(r['events'] for r in data['contexts']):,} events, in "
              f"{data['runtime_seconds']:.2f} seconds with ten workers. Physical rules unchanged."), "",
             ("[Protocol](lattice_corridor_protocol_v0.md) · "
             "[Full results](lattice_template_damage_v0/summary.json) · "
             "[Context variation](lattice_template_damage_v0/context_errors.json)"), "",
             (f"Working-template thermal failures carry {100*data['selected_class_native_flux_share']:.3f}% "
              "of all native thermal bond-failure flux in this empirical source mixture. "
              "Within that class, contexts and selected edges receive their native rate "
              "weights once. This is a conditional dependency experiment, not an estimate "
              "of the typical effect of every failure. Each arm can subsequently undergo "
              "the same native reactions, including loss and repair."), "",
             "## Consequences and recovery over time", "",
             ("Other catalytic formations exclude re-forming the originally broken pair. "
             "Errors below describe conditional continuation sampling; source-state and "
             "selected-edge uncertainty is additional. Separate context variation estimates "
             "are retained, not silently added as if they were independent errors."), "",
             "| Lag | Other formation count: broken / skipped | Count difference ± conditional SE | Current formation hazard: broken / skipped | Endpoints connected: broken / skipped |",
             "|---:|---:|---:|---:|---:|"]
    for row in group["cuts"]:
        r = row["readouts"]
        c, h, p = (r[k] for k in ("other_catalytic_formations", "other_catalytic_formation_rate",
                                  "endpoints_connected"))
        lines.append(f"| {row['lag']:.1f} | {c['broken']:.3f} / {c['skipped']:.3f} | "
                     f"{c['difference']:+.3f} ± {c['conditional_se']:.3f} | "
                     f"{h['broken']:.3f} / {h['skipped']:.3f} | "
                     f"{p['broken']:.3f} / {p['skipped']:.3f} |")
    final = group["cuts"][-1]["readouts"]
    cse = context_errors[-1]["weighted_context_se"]["other_catalytic_formations"]
    lines += ["", "## Interpretation", "",
              ("Taking a native working-template failure suppresses immediate construction "
              "and leaves fewer subsequent catalytic formations over the observed window. "
              "By lag5 the current formation hazards are close again, while the accumulated "
              "histories still differ. Endpoint activity alone misses that historical effect."), "",
              (f"At lag5 the count difference is {final['other_catalytic_formations']['difference']:+.3f}; "
               f"the weighted context-variation SE is {cse:.3f}. The selected empirical "
               "mixture and limited source contexts constrain extrapolation."), "",
              (f"Original bond restored at least once: {final['ever_original_bond']['broken']:.3f}; "
               f"present at lag5: {final['original_bond_present']['broken']:.3f}; connected "
               f"by any path: {final['endpoints_connected']['broken']:.3f}. Recovery remains "
               "multidimensional, and connection is not identical chemical function."), "",
              ("Far spatial response is small and varies across lags; the late far-cell "
              "response is comparable to the sham estimate. The panel does not establish "
              "persistent long-range damage. Shared fuel and rigid-cluster movement remain "
              "coarse-model limitations. Additional reaction counts are not automatically "
              "additional value; this test identifies an actual dependency and its history."), "",
              ("This finding makes fragility informative about how contribution is supported. "
              "It supplies no rule that a useful construction must survive indefinitely."), "",
              ("Reproduce with `python -m omega_v2.validation.lattice_damage_v0 --templates-only "
              "--replicates 64 --workers 10 --out docs/research_notes/omega_v2/lattice_template_damage_v0`. "
              "The summary's inherited `mean_thermal_failure_rate` field denotes the selected "
              "working-template class in this panel; all-failure hazards and class rarity "
              "are stored separately.")]
    (NOTES/"lattice_template_damage_report_v0.md").write_text("\n".join(lines)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
