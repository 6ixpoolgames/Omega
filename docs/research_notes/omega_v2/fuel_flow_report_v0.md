# Finite fuel and repairable coupling — exploratory run v0

Run date: 2026-10-03. Twelve exact finite classical generators; two preparations each.
No fitted lushness score or prescribed winning mechanism. All 32 frames and seven native reaction channels are retained.

## Physical model and bill

State is (S,R,D,G,F): three signal registers, the assembly state of the R→D link, and fuel count 0…B. The material scaffold is present in both preparations. There are 16(B+1) states. The source-to-relay coupling is always present; the relay-to-destination coupling requires G=1. Every signal bit has native thermal noise, and the link can both disassemble and assemble thermally.

The temperature unit is one. Stored energy is E=μ(F+G), μ=4. With B−F spent packets, the equilibrium law is proportional to binomial(B,F) exp(−E). The inventory degeneracy is explicit. Channel rates are:

- Thermal S/R/D flips: 0.1 / 0.02 / 0.02 in either direction.
- Thermal link assembly: d exp(−μ/2); breakdown: d exp(+μ/2).
- A copying correction consumes one fuel packet at rate c F exp(+μ/2), c=0.25. Its reverse breaks the match and restores fuel at rate c(B−F) exp(−μ/2). The R→D pair is enabled only with G=1.
- Assembly transfers one packet's stored energy into the link: (G=0,F)→(G=1,F−1) at rate a F. Its reverse is a(B−F). All reverse reactions remain in the actual generator.

Sweep: B∈{1,4,8}, a∈{0.25,1}, d∈{0.005,0.05}. Parameters specify kinetic laws, not scoring coefficients. Each law is run from an unbuilt preparation (G=0,F=B) and a prebuilt preparation (G=1,F=B−1); both start with a fair S and R=D=S. Initial signal content and stored energy are matched. Initial thermodynamic free energy is NOT matched: the prebuilt fuel macrostate has B-fold inventory degeneracy, making its relative entropy to equilibrium smaller by ln B. Both free-energy values are retained; the comparison is not a general equal-resource dominance claim.

This is a finite fuel inventory coupled to an implicit heat bath. Zero fuel is not absorbing: reverse reactions can restore fuel, and the link can assemble through thermal fluctuations. The first-hit-to-zero calculation uses a separate absorbing construction only to report that event; it never truncates actual continuation.

## Readouts

For every cut and lag, held information I(X_i(cut); X_frame(cut+lag)) uses the actual law. The response to each reaction is the average total-variation distance between future frame laws with that reaction taken and skipped, weighted by its actual reaction flux at the cut. Its rate is reported separately. This is a counterfactual contrast, not a newly inserted random event, policy, or ethical sign. When a channel has no events its response array uses zero with event_present=false, not an inferred zero effect.

Snapshots also retain link occupancy, fuel stock, current source/destination mutual information, stored energy and D(p||π). The last is a thermodynamic diagnostic, not a lushness measure. Fuel-consuming and fuel-restoring reaction counts are integrated separately. Because copying and assembly change multiple coordinates jointly, the previous single-coordinate signed information-flow formula is not applied here.

## Matched stored energy, changing residual access

Illustrative common law: B=4, a=1, d=0.05. Response below is a native source flip's effect on D at lag 1; information is present-time I(S;D). All sweep entries are in the evidence.

| Cut | Preparation | Mean fuel | Link on | I(S;D), bits | Source→D response | First fuel-zero hit | Now at zero |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | unbuilt | 4.000000 | 0.000000 | 1.000000 | 0.576549 | 0.000000 | 0.000000 |
| 0 | prebuilt | 3.000000 | 1.000000 | 1.000000 | 0.632233 | 0.000000 | 0.000000 |
| 1 | unbuilt | 2.944741 | 0.689311 | 0.609330 | 0.511659 | 0.004208 | 0.002380 |
| 1 | prebuilt | 2.881987 | 0.680855 | 0.603039 | 0.490969 | 0.006038 | 0.003294 |
| 10 | unbuilt | 0.828691 | 0.197355 | 0.042294 | 0.044030 | 0.708748 | 0.423857 |
| 10 | prebuilt | 0.810756 | 0.193115 | 0.039853 | 0.042197 | 0.718018 | 0.432282 |
| 50 | unbuilt | 0.072945 | 0.018224 | 0.000000 | 0.001248 | 0.999993 | 0.929038 |
| 50 | prebuilt | 0.072920 | 0.018218 | 0.000000 | 0.001247 | 0.999993 | 0.929061 |
| 100 | unbuilt | 0.071945 | 0.017986 | 0.000000 | 0.001231 | 1.000000 | 0.929973 |
| 100 | prebuilt | 0.071945 | 0.017986 | 0.000000 | 0.001231 | 1.000000 | 0.929973 |

## Native damage and subsequent repair

At time 5, condition on a native thermal G=1→0 event. The initial law is weighted by that event's flux, and its rate is retained. Evolve the post-event law using the unchanged generator. The comparison law skips that one event from the same pre-event distribution. It is a conditional effect comparison, not an external free reset. Link occupancy after damage records repeated assembly and breakdown; it is neither first repair nor permanent recovery.

For the same B=4, a=1, d=0.05 law, from the unbuilt preparation:

| Elapsed after event | Link on, damaged | Link on, skip event | Source→D response, damaged | Source→D response, skip event |
|---:|---:|---:|---:|---:|
| 0 | 0.000000 | 1.000000 | 0.083422 | 0.279734 |
| 1 | 0.293074 | 0.447205 | 0.074228 | 0.202713 |
| 5 | 0.167385 | 0.251830 | 0.026810 | 0.067679 |
| 20 | 0.030560 | 0.038413 | 0.002273 | 0.003135 |
| 50 | 0.018070 | 0.018123 | 0.001237 | 0.001241 |

The conditioned event has instantaneous rate 0.148948 at time 5. This rate is not the probability of a breakdown during a unit interval.

## What changes the interpretation

The prebuilt preparation has the larger lag-1 response at cut 0, but the initially unbuilt preparation has the larger response at cut 1 in the illustrated law. The cuts retain fuel, link state and correlations together. Neither the opening link state nor initial content alone fixes later access. The free-energy mismatch above prevents interpreting this crossing as a universal construction advantage.

Faster assembly is also faster reversible disassembly in this model. Increasing that kinetic prefactor improves early response but can lower later response. For B=4, d=0.05 and the same unbuilt preparation:

| Assembly prefactor | Cut | Source→D response | Mean fuel | Assembly fuel debits | Assembly fuel credits |
|---:|---:|---:|---:|---:|---:|
| 0.25 | 1 | 0.427694 | 3.278750 | 0.674581 | 0.083533 |
| 0.25 | 10 | 0.049856 | 0.999391 | 3.319554 | 1.796805 |
| 1 | 1 | 0.511659 | 2.944741 | 1.556848 | 0.652814 |
| 1 | 10 | 0.044030 | 0.828691 | 9.958304 | 8.255802 |

Repeated assembly events are not repeated creation of distinct access. The faster case records nearly ten fuel-consuming assemblies by time 10, but most are paired with fuel-restoring disassembly. Gross activity, net fuel use and residual access must remain distinguishable. This is a concrete reason to keep the physical bill and residual law beside any flow summary.

First fuel exhaustion also differs from present exhaustion: at cut 10 in the illustrated unbuilt law the probabilities are 0.708748 and 0.423857. Restored fuel is part of the dynamics, not an accounting reset. After a conditioned breakdown, the link-on probability rises from zero to 0.293074 at elapsed 1, then declines. Reopening a channel does not establish durable recovery or restore its earlier response.

At the late cuts, present I(S;D) approaches zero while the lagged response remains positive. A native perturbation can still propagate through transient coupling without leaving a persistent present-time record. This separation limits both information-only and response-only summaries; it supplies no positive or negative ethical sign.

## Evidence and numerical scope

Runtime: 3.45 seconds, one numerical worker. Maximum per-channel detailed-balance residual: 3.47e-18. Maximum expected-fuel accounting residual: 1.1e-13. Maximum upward D(p||π) difference between successive cuts: 0 (zero means none).

The analytic equilibrium has independent fair signal bits, link-on probability 1/(1+exp(μ)), and mean fuel B/(1+exp(μ)). The preparations under any fixed generator approach this same distribution. Their transient laws and retained finite-time differences remain distinct; a shared equilibrium is not equivalence of completed continuations or a universal thermal floor.

This extension models maintenance of an already specified coupling repertoire. It does not demonstrate open-ended generativity, invent new transition types, represent bath microrecords, solve quantum continuation, or select a scalar lushness extent. All native noise and reverse reactions remain present. Finite-time physical access can now be inspected alongside the fuel it uses and the repair pathways it leaves.

Reproduce:

    .venv/Scripts/python.exe -m omega_v2.validation.fuel_flow_v0

[All profiles and declarations](fuel_flow_v0/profiles.json) · [Generators, reaction maps and kernels](fuel_flow_v0/kernels.npz) · [Preceding maintained-reservoir run](local_flow_report_v0.md)
