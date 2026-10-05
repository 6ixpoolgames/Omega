"""Written report from retained refinement outputs; no physical rerun."""

import argparse
import gzip
import json

from omega_v2.validation.lattice_refinement_v0 import OUT, ROOT, mean_se, write_json


def load(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf8") as stream:
            return json.load(stream)
    return json.loads(path.read_text(encoding="utf8"))


def value(row, field):
    if field == "chemical_events":
        return row["events"]-row["counts"].get("hop", 0)
    if field in row:
        return row[field]
    return row["counts"].get(field, 0)


def analyze(folder):
    run = load(folder / "summary.json")
    exacts = sorted((p for p in run["panels"] if p["panel"] == "exact"), key=lambda x: x["barrier"])
    mobiles = sorted((p for p in run["panels"] if p["panel"] == "mobile"), key=lambda x: x["config"]["id"])
    by_config = {(m["config"]["barrier"], m["config"]["gamma"], m["config"]["transport"]): m for m in mobiles}
    samples = {}
    for m in mobiles:
        for prep in ("dispersed_fueled", "seeded_fueled", "equilibrium", "refueled"):
            histories = load(folder / f"mobile_{m['config']['id']:02d}" / f"{prep}_histories.json.gz")
            samples[m["config"]["id"], prep] = [h["snapshots"] for h in histories]
    fields = ("bonds", "fuel", "move", "hop", "chemical_events", "catalytic_forward",
              "max_construction_depth", "template_opportunities")
    contrasts = []
    for m in mobiles:
        b, g, t = (m["config"][k] for k in ("barrier", "gamma", "transport"))
        comparisons = []
        if g == .5:
            comparisons.append(("mobility_0.5_minus_1", by_config[b, 1., t]))
        if b == 2:
            comparisons.append(("catalytic_2_minus_0", by_config[0, g, t]))
        if t is not None:
            comparisons.append(("local_minus_shared", by_config[b, g, None]))
        for label, other in comparisons:
            for prep in ("dispersed_fueled", "seeded_fueled", "equilibrium", "refueled"):
                left = samples[m["config"]["id"], prep]
                right = samples[other["config"]["id"], prep]
                for cut_index, cut in enumerate(run["manifest"]["cuts"]):
                    differences = {f: mean_se([value(a[cut_index], f)-value(c[cut_index], f)
                                              for a, c in zip(left, right, strict=True)]) for f in fields}
                    contrasts.append({"contrast": label, "left": m["config"], "right": other["config"],
                                      "preparation": prep, "cut": cut, "differences": differences})
    write_json(folder / "paired_contrasts.json", contrasts)
    checks = [load(p) for p in folder.glob("exact*/transport*/checks.json")]
    exact_rows = [r for p in exacts for r in p["rows"]]
    n_histories = sum(m["histories"] for m in mobiles)
    n_events = sum(m["events"] for m in mobiles)
    raw_bytes = sum(p.stat().st_size for p in folder.rglob("*") if p.is_file())
    lines = ["# Residual sharing, local fuel and mobility: results v0", "",
             "2026-10-05. Exploratory implementation and crossed probe authorized together.", "",
             "**Main finding:** fuel locality changes timed continuation while preserving the",
             "matched equilibrium law. Faster transport converges to the previous shared-pool",
             "model. The catalytic two-binding advantage survives the slow-transport case",
             "tested here. Mobility changes physical trajectories without changing equilibrium.",
             "These are results about this adapter; no lushness extent has been selected.", "",
             "## Scope and implementation", "",
             f"Run `{folder.name}`: {run['seconds']:.2f} seconds, up to ten workers.",
             "Two shared generators (768 states each), eight local generators (2,560 each),",
             f"and 16 mobile laws with {n_histories:,} trajectories / {n_events:,} physical events.",
             "The exact panel has no motion (full 2x2 occupancy). The mobile panel uses four",
             "particles on a 4x4 lattice, four preparations, and 48 trajectories per cell.",
             "The finite-sample uncertainties below are Monte Carlo standard errors, not a",
             "phase-boundary or robust-corridor certificate.", "",
             "The history atlas retains every event, timing, rule provenance, prefix density,",
             "cut and incoming particle-rename map. Equal complete residual states reuse a",
             "continuation table. Fuel allocation remains part of residual identity. All",
             "enabled channels, including untaken ones, retain successor states and rates.",
             "This is a lazy native residual table plus history records, not exhaustive",
             "mobile multiway enumeration or a completed concurrency equivalence.", "",
             "## Exact transport result", "",
             "Maximum total-variation discrepancy from the shared-pool endpoint law, across",
             "unbound, seeded, adjacent, opposite and equilibrium preparations and horizons",
             "0.25, 1 and 4. All have the same projected initial law; local allocations start",
             "conditionally mixed. This compares complete projected state laws, not bond means.", "",
             "| Fuel transport | No catalysis | Catalytic barrier 2 |",
             "|---|---:|---:|"]
    for speed in (.05, 1, 20, 400):
        numbers = [max(r["tv_from_shared"] for r in e["rows"] if r["transport"] == speed) for e in exacts]
        lines.append(f"| {speed:g} | {numbers[0]:.8f} | {numbers[1]:.8f} |")
    lines += ["", "The same equilibrium distribution does not imply the same continuation law.",
              "Even at equilibrium the two-event history probabilities differ with transport,",
              "although all one-time projected equilibrium laws agree. Conditional rate",
              "averaging is exact at initialization; finite-rate local depletion then retains",
              "memory in the projected process. The reported lumpability defect remains",
              "nonzero at finite transport; fast convergence is an averaging limit.", "",
              "Probability that the next two chemistry events both bind with fuel by time 1,",
              "from exposed/unbound F=B=2. Reservoir hops may occur between them; all other",
              "chemistry events compete normally. The suffix after success is unrestricted.", "",
              "| Fuel model | No catalysis | Catalytic barrier 2 |", "|---|---:|---:|"]
    for speed in (None, .05, 1, 20, 400):
        values = []
        for e in exacts:
            r = next(r for r in e["rows"] if r["preparation"] == "unbound" and r["time"] == 1
                     and r["transport"] == (.05 if speed is None else speed))
            values.append(r["shared_two_bindings_by_1"] if speed is None else r["two_chemical_bindings_by_1"])
        lines.append(f"| {'Shared' if speed is None else speed} | {values[0]:.6f} | {values[1]:.6f} |")
    lines += ["", "With no opening bond there is no opening template. The first binding can",
              "create one and change the next residual law. This conditional construction",
              "advantage survives the local-fuel extension in this case; it is not a result",
              "that all structured arrangements dominate thermal continuation.", "",
              "For the adjacent two-bond preparation, barrier 2 and slow transport 0.05, the",
              "same timed probability is 0.429846 versus 0.613270 with shared fuel. Spatial",
              "supply therefore matters materially even though total stock and equilibrium",
              "are matched. These values use B=2, unlike the earlier B=4/F=2 witness.", "",
              "## History and residual sharing", ""]
    for e in exacts:
        lines.append(f"- Barrier {e['barrier']}: {e['shared_prefix_nodes_depth2']} marked prefix nodes "
                     f"through depth two share {e['shared_cached_residuals']} complete residual states.")
    lines += ["- Analytic two-switch control: seven prefix nodes share four residual states;",
              "  two different two-event histories return to the root. Their timed cylinder",
              "  probabilities sum to 1 - 1.2 exp(-0.2) at T=1, as required by the native clock.",
              f"- The sampled mobile records cache {sum(m['cached_residuals'] for m in mobiles):,} residual states across laws.",
              "", "These counts describe storage and retained distinctions. They are not a",
              "definition of possibility volume. Independent orders remain in the archive;",
              "no diamond-based removal of physical timing was introduced.", "",
              "## Mobility and combined effects", "",
              "For an unobstructed n-particle component, changing gamma=1 to gamma=0.5",
              "multiplies its translation rate by sqrt(n). The energy law is unchanged.",
              "The exact mobile three-particle check confirms common equilibrium. The",
              "sampled four-particle panel then measures consequences including encounters,",
              "assembly and depletion rather than presuming their direction.", "",
              "Paired differences at T=10 for the seeded/fueled preparation: gamma=0.5 minus",
              "gamma=1. Each pair uses the same initial physical configuration, with independent",
              "dynamics seeds; SE is computed from the 48 paired outcome differences.", "",
              "| Barrier | Fuel model | Move count difference +/- SE | Bond difference +/- SE |",
              "|---|---|---:|---:|"]
    for c in contrasts:
        if c["contrast"] == "mobility_0.5_minus_1" and c["preparation"] == "seeded_fueled" and c["cut"] == 10:
            d = c["differences"]
            t = c["left"]["transport"]
            lines.append(f"| {c['left']['barrier']} | {'Shared' if t is None else t} | "
                         f"{d['move']['mean']:.3f} +/- {d['move']['se']:.3f} | "
                         f"{d['bonds']['mean']:.3f} +/- {d['bonds']['se']:.3f} |")
    lines += ["", "The panel does not establish a uniform mobility benefit for assembly or",
              "generativity. Endpoint bond differences are small relative to this sample's",
              "uncertainty. Catalytic construction and local transport remain active under",
              "both mobility laws; there is no manufactured required winner.", "",
              "At transport 10, the four ideal reservoir molecules generate about 400 hops",
              "over ten time units. Those events stay in the physical archive. Their count",
              "cannot be read as an automatic 400-unit lushness gain. Comparisons to the",
              "old model use a common chemistry projection while retaining full histories.", "",
              "## Thermodynamics, sampling and reproducibility", "",
              f"- Maximum exact detailed-balance flux error: {max(c['balance_error'] for c in checks):.3g}.",
              f"- Equilibrium marginal error: {max(c['equilibrium_projection_error'] for c in checks):.3g}.",
              f"- Conditional-average generator error: {max(c['averaged_generator_error'] for c in checks):.3g}.",
              f"- Maximum propagated mass error: {max(r['mass_error'] for r in exact_rows):.3g}.",
              "- Total entropy production uses the system term via KL decrease; equilibrium",
              "  values vanish to numerical precision. It is a consistency diagnostic.",
              f"- Equilibrium sampler split R-hat: {run['manifest']['equilibrium_rhat']}.",
              "  This uses the retained chain diagnostic trace, including its recorded burn-in",
              "  segment, and is not a convergence certificate. Only 48 baseline states were",
              "  retained; uncertainty from residual chain correlation is not fully captured",
              "  by the simple trajectory SE. The exact full-occupancy results do not depend",
              "  on this sampler. The mobile equilibrium control may contain assemblies.",
              f"- Generated files at analysis: approximately {raw_bytes/1048576:.2f} MiB, local/ignored.",
              "", "Run:", "", "```powershell",
              ".venv/Scripts/python.exe -m omega_v2.validation.lattice_refinement_v0 --workers 10",
              f".venv/Scripts/python.exe -m omega_v2.validation.lattice_refinement_analysis_v0 --run {folder.name}",
              "```", "", "All initial states, timed events, provenance, residual channels, exact",
              "generators and laws, manifests and paired contrasts remain in the ignored run",
              "directory. Source and written reports are the publication artifacts.", "",
              "## What this changes next", "",
              "The model now exposes spatial resource memory and mobility without losing its",
              "thermodynamic reference or earlier histories. The useful next extent attempt",
              "can operate on retained joint residual laws and compare shared versus local",
              "resource coupling. It should preserve the demonstrated kinetic differences",
              "without treating reservoir hopping, residual cache count or path density as",
              "the answer by definition. No broader chemistry sweep is needed merely to",
              "establish that these refinements are executable.", "",
              "[Protocol](lattice_refinement_protocol_v0.md) ·",
              "[Rationale and assessment](sol_modelling_refinement_assessment_2026-10-05.md)"]
    report = ROOT / "docs/research_notes/omega_v2/lattice_refinement_report_v0.md"
    report.write_text("\n".join(lines)+"\n", encoding="utf8")
    print(report)
    print(f"{len(contrasts)} paired comparison rows; raw outputs {raw_bytes/1048576:.2f} MiB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True)
    args = parser.parse_args()
    analyze(OUT / args.run)


if __name__ == "__main__":
    main()
