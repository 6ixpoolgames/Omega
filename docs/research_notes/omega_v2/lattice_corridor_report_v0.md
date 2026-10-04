# Thermal baselines and a finite contribution corridor

2026-10-05.

Completed 7,776 full trajectories and 1,456,420 physical events in 34.74 seconds with ten workers. The chemical generator is unchanged. This panel examines where construction leads to subsequent construction; it does not impose final survival as the criterion.

[Roadmap](contribution_corridor_roadmap_2026-10-05.md) · [Protocol](lattice_corridor_protocol_v0.md) · [Full summaries](lattice_corridor_v0/summary.json) · [All comparisons and stationarity checks](lattice_corridor_v0/comparisons.json)

## Main findings

1. The actual thermal preparation already contains assemblies. At stronger binding, nearly all particles belong to one component. Calling this baseline dispersed gas would misdescribe the model's equilibrium.
2. At b=2, refueling the same equilibrium configurations increases the observed probability of a newly formed catalytic product subsequently catalysing another formation in all nine density/strength cells. The fueled dispersed preparation also exceeds equilibrium on this diagnostic in all nine cells. This is a finite mechanism corridor, not a lushness ordering or an independent discovery of catalysis.
3. For refueled equilibrium, intermediate bond strength has the highest reuse probability among the three tested strengths at every density, for both b=1 and b=2. Strong binding leaves bigger assemblies and more fuel, but fewer unbound template opportunities. These observations support a stability/availability tradeoff; they do not isolate which mechanism causes the whole difference or establish a global optimum.
4. Some products assist a subsequent formation and then disappear before the final cut. A final-survival criterion would omit those contributions. These counts retain construction, repair and repeated material use without assigning an ethical sign.

## Thermal preparation and accounting

The target equilibrium is analytically specified by the existing energy law. Positions and conformations are sampled by a separate collapsed Markov-chain sampler; bonds and fuel are then drawn from their exact conditional distributions. Sampler relocations are preparation calculations, not physical motion in the histories.

Four source chains per regime, each retaining 24 draws after 4,000 burn sweeps and 128-sweep spacing, give 96 initial draws. Basic split R-hat ranges 0.962–1.077 over the five reported observables. This is a mixing diagnostic, not a certificate of exact equilibrium or independent samples. The full chain traces and resulting physical-time drift checks are retained.

There are 3 physical stationarity coordinates with absolute cut20-minus-cut0 change greater than three estimated chain standard errors, among 162 inspected coordinates. Only four independent chains underlie those errors; these multiple exploratory comparisons are neither formal rejection tests nor proof of stationarity. The approximate baseline remains a material limitation.

The target's exact mean fuel is 16/(1+exp(4))=0.287779. Refueling changes only the fuel register of each paired equilibrium draw, setting it to 16. For the ideal exact-equilibrium preparation the refueled law has a nonequilibrium free-energy excess D(q||pi)=16 log(1+exp(4))=64.290399 in kBT units. This includes the distributional cost; the saved state G values alone do not.

Refueled equilibrium versus dispersed fueled matter shares fuel inventory, particle count and physical laws, but differs in bond/conformation energy and ensemble information. It is an initial-organization bracket, not a fully free-energy-matched causal comparison. No seed was manually planted in this panel.

## Corridor on subsequent use

P(reuse) is the probability that, by t=20, at least one bond formed through a catalytic pathway has itself assisted a later formation. The helping bond need not survive to t=20. Initial bonds have no assigned pre-cut ancestry. Material pair recurrence is retained; this is not a count of new chemical species.

| Density | Strength | Thermal b2 | Refueled b1 | Refueled b2 ± chain SE | Dispersed fueled b2 |
|---:|---:|---:|---:|---:|---:|
| 0.250 | 1 | 0.010 | 0.052 | 0.198 ± 0.046 | 0.146 |
| 0.250 | 2 | 0.062 | 0.208 | 0.542 ± 0.056 | 0.146 |
| 0.250 | 3 | 0.042 | 0.156 | 0.354 ± 0.027 | 0.208 |
| 0.327 | 1 | 0.000 | 0.062 | 0.240 ± 0.043 | 0.198 |
| 0.327 | 2 | 0.073 | 0.333 | 0.687 ± 0.055 | 0.229 |
| 0.327 | 3 | 0.052 | 0.083 | 0.354 ± 0.043 | 0.240 |
| 0.444 | 1 | 0.010 | 0.167 | 0.344 ± 0.057 | 0.208 |
| 0.444 | 2 | 0.073 | 0.344 | 0.719 ± 0.036 | 0.250 |
| 0.444 | 3 | 0.042 | 0.115 | 0.438 ± 0.055 | 0.260 |

The no-catalysis b=0 control is zero on this particular readout by definition; it is not evidence that b=0 has no consequences or lower lushness. All noncatalytic reactions, histories and other diagnostics remain in the data. The grid is an experimental bracket, not a probability measure over worlds.

## Stability, available targets and contributions before loss

Refueled equilibrium, b=2, t=20. Productive episodes are newly catalytically formed bond episodes that subsequently helped construction; loss ends an episode even if the same pair later reforms. Other histories remain included.

| Density | Strength | Largest component | Fuel | Open template opportunities | Productive episodes | Of those, later lost |
|---:|---:|---:|---:|---:|---:|---:|
| 0.250 | 1 | 8.708 | 2.417 | 0.344 | 0.271 | 0.094 |
| 0.250 | 2 | 12.854 | 3.375 | 0.781 | 0.938 | 0.302 |
| 0.250 | 3 | 15.708 | 9.719 | 0.219 | 0.479 | 0.042 |
| 0.327 | 1 | 9.698 | 1.573 | 0.667 | 0.333 | 0.156 |
| 0.327 | 2 | 14.094 | 2.938 | 0.562 | 1.250 | 0.302 |
| 0.327 | 3 | 15.750 | 10.000 | 0.208 | 0.469 | 0.062 |
| 0.444 | 1 | 10.656 | 1.208 | 0.781 | 0.604 | 0.292 |
| 0.444 | 2 | 15.323 | 2.573 | 0.802 | 1.531 | 0.323 |
| 0.444 | 3 | 15.927 | 9.469 | 0.167 | 0.552 | 0.042 |

Open template opportunities are geometric opportunities, not independently executable options: shared fuel, subsequent competition and reversals remain in the actual dynamics. Dwell integrals and native hazards are provided separately; summing these quantities would double count different views of the same history. No such lushness scalar is adopted.

## What comes next

The adjacent cells supply a real exploratory corridor for the specified construction-reuse mechanism. Its thermodynamic baseline is assembled, so this panel does not settle a dilute-gas comparison. The useful next question is whether the intermediate-strength advantage survives accounting for preparation and changes in mobility/fuel availability, and what residual joint developments the products enable. Expand resolution only when those questions reveal a missing physical mechanism. Permanence is not required.

Reproduce with `python -m omega_v2.validation.lattice_corridor_v0`, followed by `python -m omega_v2.validation.lattice_corridor_analysis_v0`. Existing output directories are protected from overwrite. Four new focused checks cover analytic marginalization, a tiny exact equilibrium comparison, contribution after original-template loss, and native class-weight accounting; fourteen focused checks including earlier chemistry/failure tests passed.
