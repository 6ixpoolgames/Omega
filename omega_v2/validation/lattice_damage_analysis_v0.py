"""Readable report for the native-failure run; no scalar lushness inference."""

import gzip
import json
from pathlib import Path

from omega_v2.finite.lattice_chemistry import LatticeChemistry, Parameters
from omega_v2.finite.lattice_damage import state_at

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2/lattice_damage_v0"


def template_availability():
    """Enumerate the present event class; no additional future outcomes selected."""
    rows = []
    for path in sorted((OUT.parent/"lattice_chemistry_v0").glob("c*_r*.json.gz")):
        source = json.loads(gzip.decompress(path.read_bytes()))
        model = LatticeChemistry(Parameters(**source["parameters"]))
        state = state_at(model, source, 5)
        events = model.events(state)
        active = {e.catalyst for e in events
                  if e.kind == "catalytic" and e.members not in state.bonds}
        rows.append({"configuration_id": source["configuration_id"],
                     "source_replicate": source["replicate"],
                     "total_thermal_break_rate": sum(e.rate for e in events
                                                     if e.kind == "thermal" and e.members in state.bonds),
                     "template_thermal_break_rate": sum(e.rate for e in events
                                                        if e.kind == "thermal" and e.members in active),
                     "template_bonds": len(active)})
    result = {"eligible_contexts": sum(r["template_thermal_break_rate"] > 0 for r in rows),
              "template_failure_flux_share": sum(r["template_thermal_break_rate"] for r in rows)
              / sum(r["total_thermal_break_rate"] for r in rows), "contexts": rows}
    (OUT/"template_availability.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main():
    data = json.loads((OUT/"summary.json").read_text(encoding="utf-8"))
    rows, groups = data["contexts"], data["groups"]
    eligible = [r for r in rows if r["eligible"]]
    trajectories = sum(2*r["replicates_per_arm"] for r in eligible)
    events = sum(r["events"] for r in rows)
    availability = template_availability()
    lines = [
        "# Native bond failures in the reversible 2D substrate", "", "2026-10-04.", "",
        (f"Completed {len(rows)} source contexts, {trajectories:,} residual trajectories "
         f"and {events:,} events in {data['runtime_seconds']:.2f} seconds with ten workers. "
         "The chemical generator is unchanged from the preceding pilot. "
         "No lushness score, new chemical rule or irreversible damage state was introduced."), "",
        ("[Protocol and sampling](lattice_damage_protocol_v0.md); "
         "[manifest](lattice_damage_v0/manifest.json); "
         "[complete compact results](lattice_damage_v0/summary.json). "
         "Each context's compressed archive includes the full physical trajectories, "
         "spatial marginal profiles, selected failure and initial states."), "",
        "## What was compared", "",
        ("At t=5 of each prior trajectory, sample a thermal bond break in proportion to "
         "its native rate. Run 32 independent continuations with the event taken and 32 "
         "with it skipped, at lags 0,0.5,2,5. Both arms remain subject to all native "
         "reactions thereafter. Original-bond restoration, alternate connectivity, "
         "downstream construction and spatial laws are observed separately."), "",
        (f"{len(eligible)}/{len(rows)} contexts had a nonzero thermal failure rate. "
         "Zero-hazard contexts are retained in the source population. Event-conditioned "
         "averages weight source states by their total failure hazard once; the sampled "
         "edge was already selected conditionally by its relative hazard."), "",
        ("The pooled rows below describe this equal-configuration experimental mixture, "
         "not a prior over possible worlds. Bridge and template strata differ in other "
         "physical properties and are not matched interventions on topology alone. "
         "Individual configuration summaries remain available."), "",
        "## What this run resolves", "",
        ("The recovery notions separate: by lag5 the original bond was restored at least "
         "once with probability 0.455, present with probability 0.397, and its endpoints "
         "connected by some path with probability 0.574 (versus 0.866 in the skipped arm). "
         "The first two differ because restored bonds can fail again; alternate paths "
         "explain some connection without the original bond."), "",
        ("For sampled bridge failures, other-bond stock has a small positive mean shift "
         "(+0.145; conditional simulation SE 0.048) while endpoint connection falls by "
         "0.375. That combination matters: extra bonds elsewhere need not restore the "
         "lost relation. Splitting a rigid component can change mobility and encounters, "
         "but this run has not isolated that as the cause of the positive shift."), "",
        ("Near-field distribution changes are clear. Far-field changes are small and "
         "mostly comparable to sampling uncertainty; this run does not establish a "
         "persistent long-range effect."), "",
        (f"Only five selected failures removed a currently working catalytic template. "
         f"Enumerating the source cuts finds such failures available in "
         f"{availability['eligible_contexts']}/384 contexts, carrying "
         f"{100*availability['template_failure_flux_share']:.3f}% of total native thermal "
         "failure flux in the empirical configuration mixture. The native panel therefore "
         "under-samples that rare question. The template row is suggestive only, not a "
         "general catalytic-bottleneck result. A template can also acquire a new target "
         "later; 'no current target' does not mean permanently non-catalytic."), "",
        "## Recovery is not one event", "",
        "Broken arm, lag5. Probabilities are conditional on the sampled native failure.", "",
        ("| Failure role | Source contexts | Original bond ever restored | Original bond present | "
        "Restored then lost at least once | Endpoints connected now | Alternate path now |"),
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    names = {"all": "All", "bridge": "Bridge", "alternate": "Initially alternate path",
             "template": "Currently assists another formation", "non_template": "No current target"}
    for key, group in groups.items():
        r = group["cuts"][-1]["readouts"]
        vals = [r[k]["broken"] for k in ("ever_original_bond", "original_bond_present",
                                          "lost_again_after_bond", "endpoints_connected",
                                          "alternate_path_present")]
        lines.append(f"| {names[key]} | {group['contexts']} | "
                     + " | ".join(f"{v:.3f}" for v in vals) + " |")
    lines += ["",
              ("An alternate bond path can exist while the original bond is missing; it "
               "does not guarantee the same catalytic function. First restoration also "
               "does not guarantee continued restoration. No permanence statement follows "
               "from a finite observation horizon."), "",
              "## Changes outside the original bond", "",
              ("Lag5 means, broken minus skipped. Negative values indicate a lower "
               "quantity in the broken arm, not a general ethical sign."), "",
              ("| Role | Other bonds | Remaining fuel | Other catalytic formations by lag5 | "
              "Other catalytic formation hazard at lag5 |"),
              "|---|---:|---:|---:|---:|"]
    for key, group in groups.items():
        r = group["cuts"][-1]["readouts"]
        vals = [r[k]["difference"] for k in ("bonds_other_than_original", "fuel",
                                              "other_catalytic_formations",
                                              "other_catalytic_formation_rate")]
        lines.append(f"| {names[key]} | " + " | ".join(f"{v:+.4f}" for v in vals) + " |")
    lines += ["",
              ("These are effects of taking a native failure at a given sampled cut. "
               "The counterfactual skipped arm can subsequently lose the same bond. "
               "A higher count after failure can reflect greater mobility, new encounters "
               "or recycling; it is not by itself improved continuation extent."), "",
              "## Spatial response and sampling noise", "",
              ("Every cell records empty/concealed/exposed probabilities, and every "
               "neighboring edge records a physical bond probability. The table reports "
               "a noise-corrected squared difference of mean features per observed cell "
               "or edge in the farther region (distance >=2 from the initial break sites). "
               "The subtraction removes finite-sample inflation in expectation. "
               "Negative estimates remain visible. They mean estimator fluctuation, "
               "not negative influence."), "",
              ("The sham compares two independent halves of the skipped arm. Its "
               "expectation is zero, but its smaller sample count makes it noisier. "
               "Approximate SE below describes variation across sampled contexts; "
               "it is not an exact confidence interval for the entire field."), "",
              ("| Lag | Far-cell response ± context SE | Far-cell sham | "
              "Far-edge response ± context SE | Far-edge sham |"),
              "|---:|---:|---:|---:|---:|"]
    for cut in groups["all"]["cuts"]:
        r, se = cut["response"], cut["response_context_se"]
        lines.append(f"| {cut['lag']:g} | {r['cells_far']:+.6f} ± {se['cells_far']:.6f} | "
                     f"{r['sham_cells_far']:+.6f} | {r['edges_far']:+.6f} ± {se['edges_far']:.6f} | "
                     f"{r['sham_edges_far']:+.6f} |")
    lines += ["",
              ("These marginal projections do not determine the joint continuation law. "
               "Original-bond/alternate-path joint probabilities and all raw trajectories "
               "are retained alongside them. The fixed spatial coordinates define an "
               "observational probe, not a free physically installed decoder."), "",
              ("Far response is relative to the model: rigid-cluster mobility can change "
               "immediately throughout a component when a bridge breaks, and fuel is "
               "well mixed. These are existing coarse assumptions. The response is not "
               "a measured physical signal speed or evidence that influence crossed a "
               "newly discovered channel."), "",
              "## Regime-resolved means", "",
              ("Each row uses 12 source histories and 32 continuations per arm. Full "
               "conditional Monte Carlo errors are in the JSON; uncertainty in the source "
               "histories and the sampled failure edge is additional."), "",
              ("| N | Density | Strength | b | Start | P(original restored by5) | "
              "P(original present at5) | Delta other bonds | Delta other catalytic formations |"),
              "|---:|---:|---:|---:|---|---:|---:|---:|---:|"]
    for cid, group in data["configurations"].items():
        context = next(r for r in rows if r["configuration_id"] == int(cid))
        p = context["parameters"]
        r = group["cuts"][-1]["readouts"]
        lines.append(f"| {p['particles']} | {p['particles']/p['side']**2:.3f} | "
                     f"{p['bond_strength']:g} | {p['catalytic_barrier']:g} | {context['preparation']} | "
                     f"{r['ever_original_bond']['broken']:.3f} | "
                     f"{r['original_bond_present']['broken']:.3f} | "
                     f"{r['bonds_other_than_original']['difference']:+.3f} | "
                     f"{r['other_catalytic_formations']['difference']:+.3f} |")
    lines += ["", "## Scope and checks", "",
              ("Ten focused tests across the physical model and failure observer pass, "
               "including first-hit versus occupancy, thermal energy/fuel accounting, "
               "alternate connectivity, zero native hazard, exact unbiasedness of the "
               "squared-response estimator and the preceding reversibility/symmetry checks. "
               "Lint passes. The new reader does not change the physical generator."), "",
              ("All failures are reversible in this model. Fuel exhaustion is not absorbing. "
               "A native thermal break takes energy from the implicit bath, with no free "
               "fuel refund. The results concern bounded recovery and residual physical "
               "effects, not permanent destruction, universal robustness or an ethical "
               "ordering. A meaningful next refinement should follow an identified "
               "mechanism or missing resolution rather than a preferred sign."), ""]
    lines += ["## Next targeted sample", "",
              ("The cheapest informative continuation is a separately labeled panel "
               "conditioned on currently working-template failures, using the 60 eligible "
               "source contexts and their native rates. Keep its actual rarity alongside "
               "the conditional result. This changes sampling, not chemistry, and avoids "
               "adding mechanisms merely to make bottlenecks easier to observe. "
               "That targeted panel has not been run here."), ""]
    report = OUT.parent/"lattice_damage_report_v0.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print(str(report))
    for key, group in groups.items():
        r = group["cuts"][-1]["readouts"]
        print(key, json.dumps({"contexts": group["contexts"],
                              "ever_repaired": r["ever_original_bond"]["broken"],
                              "present": r["original_bond_present"]["broken"],
                              "connected": r["endpoints_connected"]["broken"],
                              "delta_other_bonds": r["bonds_other_than_original"]["difference"],
                              "delta_other_catalytic": r["other_catalytic_formations"]["difference"]}))


if __name__ == "__main__":
    main()
