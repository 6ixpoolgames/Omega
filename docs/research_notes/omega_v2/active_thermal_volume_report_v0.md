# Active organization versus thermal: historical frame-volume probe v0

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
| Thermal | 0.388816 | 0.053959 | 0.000000 | 6.940342 |
| Aligned seed | 12.000000 | 2.000000 | 13.302022 | 3.000000 |
| Misaligned seed | 12.000000 | 2.000000 | 13.302022 | 3.000000 |
| Fair seed | 12.000000 | 2.000000 | 12.608875 | 4.000000 |
| Dispersed | 12.000000 | 3.000000 | 13.707487 | 4.000000 |
| Matched dispersal | 12.000000 | 3.000000 | 13.302022 | 4.584963 |
| Contact, unbound | 12.000000 | 3.000000 | 13.707487 | 4.000000 |
| Assembled | 12.000000 | 0.000000 | 13.707487 | 4.000000 |
| Natural cut 5 | 8.776484 | 1.243682 | 5.402675 | 10.032219 |
| Ready at cut 5 | 10.268700 | 1.342198 | 8.265646 | 7.772081 |

Consumption, reverse returns, transport and other expected reaction totals are retained as a separate resource profile. No resource component is added to entropy as a reward.

## Profiles cross

Each entry is the number of coordinates greater/lower/tied for the left preparation. These counts describe crossings; **they are not a vote or a measure over frames**. Comparisons use a 1e-9 tolerance. Fixed profiles have 1,024 coordinates; coverage envelopes have 60.

| Comparison, b = 2 | H | Fixed normalized volume | Fixed joint history entropy | Normalized coverage envelope |
|---|---:|---|---|---|
| Aligned seed vs Thermal | 2 | 664/359/1 | 340/683/1 | 44/15/1 |
| Aligned seed vs Thermal | 10 | 613/410/1 | 312/711/1 | 40/19/1 |
| Aligned seed vs Misaligned seed | 2 | 943/80/1 | 201/822/1 | 42/17/1 |
| Aligned seed vs Misaligned seed | 10 | 1023/0/1 | 7/1016/1 | 59/0/1 |
| Aligned seed vs Matched dispersal | 2 | 868/155/1 | 127/896/1 | 54/5/1 |
| Aligned seed vs Matched dispersal | 10 | 935/88/1 | 192/831/1 | 59/0/1 |
| Ready at cut 5 vs Thermal | 2 | 289/734/1 | 982/41/1 | 22/37/1 |
| Ready at cut 5 vs Thermal | 10 | 237/786/1 | 987/36/1 | 19/40/1 |

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
| 0 | Thermal | 12.438958 | 16.087458 | 3.648501 |
| 0 | Aligned seed | 11.201245 | 16.444660 | 5.243415 |
| 0 | Misaligned seed | 11.713226 | 17.548770 | 5.835544 |
| 2 | Thermal | 12.439149 | 16.088461 | 3.649312 |
| 2 | Aligned seed | 11.331282 | 16.996001 | 5.664720 |
| 2 | Misaligned seed | 11.778883 | 17.859068 | 6.080184 |

For the active preparation, endpoint history is smaller than thermal, but three-observation history is larger. This reversal also occurs without catalytic assistance. It demonstrates a loss from the endpoint summary; it does not identify all the extra history with generativity. Thermal fluctuations and reaction turnover remain real contributions.

There is also a fixed-frame normalized ranking reversal. Observe physical sites 2 and 3, the same two locations in both preparations (mask 12), under b = 2:

| Preparation | Observation times | Whole entropy | Frame entropy | Normalized V |
|---|---|---:|---:|---:|
| Thermal | 0, 2 | 12.439149 | 5.821964 | 0.010186590 |
| Thermal | 0, 1, 2 | 16.088461 | 8.365237 | 0.004732360 |
| Aligned seed | 0, 2 | 11.331282 | 4.773573 | 0.010615319 |
| Aligned seed | 0, 1, 2 | 16.996001 | 7.134643 | 0.001075066 |

The aligned preparation has the larger normalized share at the two endpoints and the smaller share after the middle observation is included. Among the 56 small frames evaluated at both resolutions, 25 such strict sign reversals occur at H = 2 and 30 at H = 10. This is a physical observation refinement, not a harmless redescription, so invariance was not required. It establishes that the endpoint result is not a stable conclusion about the full history.

## Isolating the catalytic change

The aligned initial law is identical for b = 0 and b = 2. Direct differences therefore isolate the changed catalytic kinetics, unlike a seed-versus-equilibrium comparison. The normalized fixed-frame counts again describe crossings, not aggregate value.

| H | b2 minus b0, endpoint whole entropy | b2 minus b0, three-cut whole entropy | Fixed normalized volume, greater/lower/tied |
|---|---:|---:|---|
| 2 | +0.130037 | +0.551341 | 97/926/1 |
| 10 | -0.013410 | +0.000428 | 826/197/1 |

At H = 2 the additional pathways raise represented whole-history entropy at both resolutions; by H = 10 that increase is nearly absent in the three-cut restriction and negative at the endpoints. This is a finite entropy result under reversible construction, not a proof that more entropy is more lushness. The saved summary also compares every other preparation; natural cut-5 ensembles differ across kinetic laws and are flagged accordingly.

## What this says about the program

The originator clarified the mechanism during analysis: **"Catalysis tells us how generativity wins. By reducing cost to access."** This directs the next comparison toward physically costed continuation. In this adapter, assistance lowers a kinetic barrier and accelerates a reaction and its reverse; the fuel debit per forward reaction is unchanged. Construction can therefore make a subsequent transformation more accessible within a time window without adding an elementary transition or an entropy bonus. Whether that yields a sustained net access advantage depends on the full residual law, preparation, maintenance, reversal and resource use. Reach and cheaper access facilitate lushness; neither alone defines it.

The present observational entropy envelope does not implement that cost-to-access comparison. Its footprint is not a transformation's physical resource profile. Consequently, mixed entropy or normalized-share results do not refute the catalytic mechanism, and increased entropy is not a necessary condition for the proposed advantage. A direct follow-up should compare the joint residual laws attainable within the same time and physical resources, retaining construction overhead and actual endogenous dynamics, rather than grade catalysis by whether it produces more uncertainty.

The field-first target survives as the question being tested. These calculations do not establish its proposed preference for maintaining generative structure. They also do not establish a universal thermal advantage.

The run locates two concrete obligations inside the adopted construction: retain consequential intermediate history rather than substitute endpoint states; and implement the encompassing comparison so that a larger normalized share is not mistaken for a larger underlying field. Physical access is a further obligation: a projected mathematical observation is not automatically a realizable record or decoder.

A principled continuation would retain the compatible family of temporal restrictions and their actual joint laws, then attach explicit record/acquisition routes to it. The current local share remains a diagnostic in that family. Whether a count-once physical aggregation distinguishes construction from dispersion under matched resources remains open. No noise deletion, fitted coefficient, hand-picked winner or new scalar is introduced to repair the observed crossings.

## Reproduction and checks

The numerical run took **78.91 seconds** with one numerical worker. Existing physical transition kernels were reused after exact state/rate comparison; their paths and hashes are recorded. This is not a new independent validation of those kernels.

Three focused tests cover direct tiny-history enumeration, joint copies versus distinct content, physical state relabeling, retained randomness and whole normalization. Focused lint passed. Maximum kernel normalization residual: 8.22e-15; pair-history chain-rule discrepancy: 3.38e-14; negative refinement-entropy residual: 1.92e-15. These checks verify this calculation, not the motivating value bridge.

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
