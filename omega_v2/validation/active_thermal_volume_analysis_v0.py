"""Summarize the retained finite historical-volume run without rerunning physics."""

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2/active_thermal_volume_v0"
REPORT = OUT.parent / "active_thermal_volume_report_v0.md"
TOL = 1e-9


def signs(delta):
    return {
        "greater": int(np.sum(delta > TOL)),
        "lower": int(np.sum(delta < -TOL)),
        "tied": int(np.sum(abs(delta) <= TOL)),
    }


def compare(a, b):
    dh = np.asarray(a["history_bits"]) - b["history_bits"]
    dv = np.asarray(a["history_log2_volume"]) - b["history_log2_volume"]
    ea, eb = a["coverage_envelope"], b["coverage_envelope"]
    assert [r["coverage"] for r in ea] == [r["coverage"] for r in eb]
    de = np.array([x["log2_volume"] - y["log2_volume"] for x, y in zip(ea, eb, strict=True)])
    ta = {r["mask"]: r for r in a["three_cut"]["frames"]}
    tb = {r["mask"]: r for r in b["three_cut"]["frames"]}
    flips = [
        m
        for m in ta
        if abs(dv[m]) > TOL
        and abs(ta[m]["log2_volume"] - tb[m]["log2_volume"]) > TOL
        and dv[m] * (ta[m]["log2_volume"] - tb[m]["log2_volume"]) < 0
    ]
    return {
        "fixed_frame_volume": signs(dv),
        "fixed_frame_history_bits": signs(dh),
        "volume_greater_without_history_bits_greater": int(np.sum((dv > TOL) & (dh <= TOL))),
        "coverage_envelope_volume": signs(de),
        "whole_history_bits_difference": a["whole_history_bits"] - b["whole_history_bits"],
        "three_cut_whole_history_bits_difference": (
            a["three_cut"]["whole_history_bits"] - b["three_cut"]["whole_history_bits"]
        ),
        "temporal_refinement_volume_sign_flips": flips,
    }


def counts(row):
    return "/".join(str(row[key]) for key in ("greater", "lower", "tied"))


def main():
    data = json.loads((OUT / "results.json").read_text(encoding="utf-8"))
    models = data["models"]
    pairs = [
        ("aligned_seed", "thermal"),
        ("aligned_seed", "misaligned_seed"),
        ("aligned_seed", "dispersed_free_energy_matched"),
        ("natural_cut5_ready", "thermal"),
    ]
    comparisons = []
    for barrier, model in models.items():
        preps = model["preparations"]
        for left, right in pairs:
            for a, b in zip(preps[left]["windows"], preps[right]["windows"], strict=True):
                comparisons.append(
                    {
                        "barrier": int(barrier),
                        "left": left,
                        "right": right,
                        "times": a["times"],
                        **compare(a, b),
                    }
                )
    kinetic = []
    for name in models["0"]["preparations"]:
        for i in range(2):
            a = models["2"]["preparations"][name]["windows"][i]
            b = models["0"]["preparations"][name]["windows"][i]
            kinetic.append(
                {
                    "preparation": name,
                    "times": a["times"],
                    "same_initial_law": name not in ("natural_cut5", "natural_cut5_ready"),
                    **compare(a, b),
                }
            )
    summary = {
        "tolerance": TOL,
        "counts_are_not_frame_weights": True,
        "comparisons": comparisons,
        "barrier2_minus_barrier0": kinetic,
    }
    (OUT / "comparison_summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )

    names = {
        "thermal": "Thermal",
        "aligned_seed": "Aligned seed",
        "misaligned_seed": "Misaligned seed",
        "seeded_fair": "Fair seed",
        "dispersed": "Dispersed",
        "dispersed_free_energy_matched": "Matched dispersal",
        "contact_unbound": "Contact, unbound",
        "assembled": "Assembled",
        "natural_cut5": "Natural cut 5",
        "natural_cut5_ready": "Ready at cut 5",
    }
    strong = models["2"]["preparations"]
    prep_rows = []
    for name, p in strong.items():
        s = p["snapshot"]
        prep_rows.append(
            f"| {names[name]} | {s['stored_energy']:.6f} | {s['fuel_mean']:.6f} | "
            f"{s['free_energy_nats']:.6f} | {p['windows'][0]['initial_bits'][-1]:.6f} |"
        )
    comparison_rows = []
    for c in comparisons:
        if c["barrier"] == 2:
            comparison_rows.append(
                f"| {names[c['left']]} vs {names[c['right']]} | {c['times'][-1]} | "
                f"{counts(c['fixed_frame_volume'])} | {counts(c['fixed_frame_history_bits'])} | "
                f"{counts(c['coverage_envelope_volume'])} |"
            )
    history_rows = []
    for barrier in ("0", "2"):
        for name in ("thermal", "aligned_seed", "misaligned_seed"):
            w = models[barrier]["preparations"][name]["windows"][0]
            h2, h3 = w["whole_history_bits"], w["three_cut"]["whole_history_bits"]
            history_rows.append(
                f"| {barrier} | {names[name]} | {h2:.6f} | {h3:.6f} | {h3 - h2:.6f} |"
            )
    witness_rows = []
    for name in ("thermal", "aligned_seed"):
        w = strong[name]["windows"][0]
        t = next(r for r in w["three_cut"]["frames"] if r["mask"] == 12)
        for times, whole, local, logv in (
            ("0, 2", w["whole_history_bits"], w["history_bits"][12], w["history_log2_volume"][12]),
            ("0, 1, 2", w["three_cut"]["whole_history_bits"], t["history_bits"], t["log2_volume"]),
        ):
            witness_rows.append(
                f"| {names[name]} | {times} | {whole:.6f} | {local:.6f} | {np.exp2(logv):.9f} |"
            )
    kinetic_rows = []
    for c in kinetic:
        if c["preparation"] == "aligned_seed":
            kinetic_rows.append(
                f"| {c['times'][-1]} | {c['whole_history_bits_difference']:+.6f} | "
                f"{c['three_cut_whole_history_bits_difference']:+.6f} | "
                f"{counts(c['fixed_frame_volume'])} |"
            )
    checks = {key: max(m["checks"][key] for m in models.values()) for key in models["0"]["checks"]}
    report = r"""# Active organization versus thermal: historical frame-volume probe v0

Exploratory run, 4 October 2026. The question is whether active generative organization improves the proposed lushness comparison while present. There is no required winner.

**Result: this finite application does not establish that generativity beats thermal.** The normalized profiles cross. Some apparent advantages occur without catalytic assistance. Retaining an intermediate observation changes both whole-history entropy comparisons and some normalized frame rankings. The useful result is a concrete separation of represented history, its local share, and catalytic effects; these cannot be substituted for one another.

## What was computed

The physical substrate is unchanged from the [catalytic continuation run](catalytic_binding_report_v0.md): four identical bit-bearing particles on five sites, reversible bonds, three fuel packets, 1,792 states and 43 native channels. An aligned bond accelerates a neighboring reversible reaction; its products can do the same. Assistance accelerates both directions and leaves equilibrium unchanged. Barrier reductions b = 0, 1, 2 include a no-assistance control. Noise, motion, dissolution, reverse reactions and subsequent failure remain in every law.

This is a dense finite classical reactive lattice model with a well-mixed fuel stock and an implicit heat bath. Thermal means its exact equilibrium preparation, not a simulation of a dilute universal gas. The three kinetic laws are alternative physical models, not equiprobable branches. Equilibrium and resource-matched dispersal answer different questions.

The adopted local candidate is applied to sampled histories. Let X be the complete physical state at times (0,H), and R_m its projection onto a coordinate subset at both times. Since R_m is a function of X:

    I(X; R_m) = H(R_m)
    log2 V_m = H(R_m) - H(X).

All 1,024 subsets of the ten physical variables are evaluated: five sites, four bonds and fuel. Each site's value includes vacancy and the internal bit. Whole-history volume is one in every preparation by construction. Empty-frame volume is 2^(-H(X)), not zero. Present-only information and volume are retained separately.

The sampled law is exact for the declared finite generator: p(x0) K_H(x0,xH). This integrates intervening dynamics but does not retain its entire event history. At H = 2 and 10, a second calculation inserts the middle observation, giving (0,1,2) and (0,5,10). The refined whole-history entropy and all 56 frames containing at most two coordinates are exact; the whole frame is also recorded. Larger intermediate-time frames were not evaluated.

Joint entropy counts redundant content once. A catalog retains information-equivalent projections with every physical location and minimal coverage footprint. No physical histories are merged. A 60-cell envelope records the largest jointly observed content available with at most (s,b,f) site, bond and fuel variables. This is an observational restriction of the earlier [joint-content envelope](frame_aggregation_report_v0.md). Coverage is not a measured physical decoder cost. The envelope is existential and carries no probability on its maximizing frames.

**Historical observations are not free archives available to an agent at H.** This run has not implemented the apparatus needed to collect and preserve them, or completed the encompassing physical access aggregation. It tests the adopted local formula on an explicit temporal restriction, while preserving the source laws beside it.

## Preparations and matching

Ten preparations evolve under each of the three laws, over two windows: 60 cases in total. Nothing is conditioned on surviving the future evaluation window.

- The aligned and misaligned seeds each have one bond, two fuel packets and eight equally weighted internal configurations. Only the aligned seed initially provides catalytic assistance. Both have exactly the same energy, fuel and free energy relative to equilibrium. Alignment also changes ordinary spin-exchange kinetics; the b = 0 control is therefore essential.
- Matched dispersal has no bond and three fuel packets. A declared mixture over three possible vacancy locations matches the aligned seed's stored energy and D(p||pi). The central vacancy has probability 0.8961426583; each outer vacancy has probability 0.0519286709. These are physical preparation weights, not scoring coefficients. The preparations do not have identical uncertainty decompositions or usable fuel.
- The natural cut-5 law is the fair seed evolved freely for five time units. Its ready subset has an aligned bond positioned to assist a forward reaction with fuel available. Conditioning masses are 0.248856, 0.244553 and 0.241750 for b = 0, 1, 2. The same geometric predicate defines the b = 0 control. All later losses remain included.
- Exact equilibrium is not free-energy-matched to an out-of-equilibrium preparation. Comparing both it and matched dispersal makes the resource distinction explicit.

Initial quantities below are for b = 2. Energy is in the model's units; D(p||pi) is the dimensionless free-energy excess in nats, including the finite fuel degeneracy.

| Preparation | Stored energy | Usable fuel | D(p\|\|pi) | Initial state entropy, bits |
|---|---:|---:|---:|---:|
{prep_rows}

Consumption, reverse returns, transport and other expected reaction totals are retained as a separate resource profile. No resource component is added to entropy as a reward.

## Profiles cross

Each entry is the number of coordinates greater/lower/tied for the left preparation. These counts describe crossings; **they are not a vote or a measure over frames**. Comparisons use a 1e-9 tolerance. Fixed profiles have 1,024 coordinates; coverage envelopes have 60.

| Comparison, b = 2 | H | Fixed normalized volume | Fixed joint history entropy | Normalized coverage envelope |
|---|---:|---|---|---|
{comparison_rows}

The active seed has some larger and some smaller normalized coordinates than thermal. Relative to matched dispersal, its late envelope dominates, but its fixed-location profile still crosses. An envelope can change its best observation location separately for each preparation; it is a further compression of the fixed profile.

At the naturally reached ready cut, most fixed frames contain *more* joint history entropy than their thermal counterparts while most hold a *smaller* normalized volume. This is not contradictory: the represented whole also contains more entropy. Neither raw entropy nor the number of favorable frames is adopted as lushness.

## The normalization effect is explicit

For two preparations A and B:

    delta log2 V_m = delta H(R_m) - delta H(X).

At b = 2, H = 2, the aligned seed exceeds thermal in normalized volume at 664 fixed frames, but only 340 frames have greater joint history entropy. Of its normalized advantages, 324 occur without a joint-entropy gain. Against the misaligned seed the corresponding counts are 943 normalized advantages, 201 entropy advantages, and 742 normalized advantages without an entropy gain.

This does not reject normalization. It shows that **within-preparation shares cannot simply be promoted to an absolute comparison of differently sized historical objects**. Both totals and their distribution must remain visible while the encompassing comparison is implemented. No missing probability prior is supplied here; every calculation uses its declared actual law.

The issue is particularly clear in the b = 0 control: the aligned seed has greater normalized volume at 1,023 frames and ties at the whole, at both horizons, despite the absence of catalytic assistance. An aligned-over-misaligned result alone therefore cannot establish a generativity benefit.

## More of the history changes the answer

The same physical duration H = 2 gives the following whole-history entropies. The last column is exactly the additional intermediate-state information conditional on both endpoints.

| b | Preparation | H(X0,X2) | H(X0,X1,X2) | Extra intermediate history |
|---|---|---:|---:|---:|
{history_rows}

For the active preparation, endpoint history is smaller than thermal, but three-observation history is larger. This reversal also occurs without catalytic assistance. It demonstrates a loss from the endpoint summary; it does not identify all the extra history with generativity. Thermal fluctuations and reaction turnover remain real contributions.

There is also a fixed-frame normalized ranking reversal. Observe physical sites 2 and 3, the same two locations in both preparations (mask 12), under b = 2:

| Preparation | Observation times | Whole entropy | Frame entropy | Normalized V |
|---|---|---:|---:|---:|
{witness_rows}

The aligned preparation has the larger normalized share at the two endpoints and the smaller share after the middle observation is included. Among the 56 small frames evaluated at both resolutions, 25 such strict sign reversals occur at H = 2 and 30 at H = 10. This is a physical observation refinement, not a harmless redescription, so invariance was not required. It establishes that the endpoint result is not a stable conclusion about the full history.

## Isolating the catalytic change

The aligned initial law is identical for b = 0 and b = 2. Direct differences therefore isolate the changed catalytic kinetics, unlike a seed-versus-equilibrium comparison. The normalized fixed-frame counts again describe crossings, not aggregate value.

| H | b2 minus b0, endpoint whole entropy | b2 minus b0, three-cut whole entropy | Fixed normalized volume, greater/lower/tied |
|---|---:|---:|---|
{kinetic_rows}

At H = 2 the additional pathways raise represented whole-history entropy at both resolutions; by H = 10 that increase is nearly absent in the three-cut restriction and negative at the endpoints. This is a finite entropy result under reversible construction, not a proof that more entropy is more lushness. The saved summary also compares every other preparation; natural cut-5 ensembles differ across kinetic laws and are flagged accordingly.

## What this says about the program

The originator clarified the mechanism during analysis: **"Catalysis tells us how generativity wins. By reducing cost to access."** This directs the next comparison toward physically costed continuation. In this adapter, assistance lowers a kinetic barrier and accelerates a reaction and its reverse; the fuel debit per forward reaction is unchanged. Construction can therefore make a subsequent transformation more accessible within a time window without adding an elementary transition or an entropy bonus. Whether that yields a sustained net access advantage depends on the full residual law, preparation, maintenance, reversal and resource use. Reach and cheaper access facilitate lushness; neither alone defines it.

The present observational entropy envelope does not implement that cost-to-access comparison. Its footprint is not a transformation's physical resource profile. Consequently, mixed entropy or normalized-share results do not refute the catalytic mechanism, and increased entropy is not a necessary condition for the proposed advantage. A direct follow-up should compare the joint residual laws attainable within the same time and physical resources, retaining construction overhead and actual endogenous dynamics, rather than grade catalysis by whether it produces more uncertainty.

The field-first target survives as the question being tested. These calculations do not establish its proposed preference for maintaining generative structure. They also do not establish a universal thermal advantage.

The run locates two concrete obligations inside the adopted construction: retain consequential intermediate history rather than substitute endpoint states; and implement the encompassing comparison so that a larger normalized share is not mistaken for a larger underlying field. Physical access is a further obligation: a projected mathematical observation is not automatically a realizable record or decoder.

A principled continuation would retain the compatible family of temporal restrictions and their actual joint laws, then attach explicit record/acquisition routes to it. The current local share remains a diagnostic in that family. Whether a count-once physical aggregation distinguishes construction from dispersion under matched resources remains open. No noise deletion, fitted coefficient, hand-picked winner or new scalar is introduced to repair the observed crossings.

## Reproduction and checks

The numerical run took **{runtime:.2f} seconds** with one numerical worker. Existing physical transition kernels were reused after exact state/rate comparison; their paths and hashes are recorded. This is not a new independent validation of those kernels.

Three focused tests cover direct tiny-history enumeration, joint copies versus distinct content, physical state relabeling, retained randomness and whole normalization. Focused lint passed. Maximum kernel normalization residual: {rows:.3g}; pair-history chain-rule discrepancy: {chain:.3g}; negative refinement-entropy residual: {refine:.3g}. These checks verify this calculation, not the motivating value bridge.

From the repository root:

    python -m omega_v2.validation.active_thermal_volume_v0
    python -m omega_v2.validation.active_thermal_volume_analysis_v0
    python -m pytest tests/test_history_volume.py -q

Evidence:

- [Full profiles, laws, resources and manifest](active_thermal_volume_v0/results.json)
- [Every physical frame and content/coverage catalog](active_thermal_volume_v0/frame_catalog.json)
- [Comparison summary, all controls and refinement reversals](active_thermal_volume_v0/comparison_summary.json)
- [Historical readout implementation](../../../omega_v2/finite/history_volume.py)
- [Numerical runner](../../../omega_v2/validation/active_thermal_volume_v0.py)
- [Report generator](../../../omega_v2/validation/active_thermal_volume_analysis_v0.py)
- [Focused tests](../../../tests/test_history_volume.py)
""".format(
        prep_rows="\n".join(prep_rows),
        comparison_rows="\n".join(comparison_rows),
        history_rows="\n".join(history_rows),
        witness_rows="\n".join(witness_rows),
        kinetic_rows="\n".join(kinetic_rows),
        runtime=data["runtime_seconds"],
        rows=checks["kernel_rows"],
        chain=checks["pair_chain_entropy"],
        refine=checks["three_cut_refinement"],
    )
    REPORT.write_text(report, encoding="utf-8")
    print(
        json.dumps(
            {
                "report": str(REPORT.relative_to(ROOT)),
                "comparison_rows": len(comparisons),
                "kinetic_rows": len(kinetic),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
