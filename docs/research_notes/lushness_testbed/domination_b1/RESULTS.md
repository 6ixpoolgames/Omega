# Fractional-cost control and paid discovery

**COMPLETE: 28/28 distinct cases completed.**

All comparisons use the 29,760-state adapter with the same bank capacity, energy grid, source, bath and preparation within each context. Finite physical-history lushness is primary; stationary rate, activity and stocks are explanatory readouts. The main map varies pocket yield, intervention bill and strength. The C5 companion varies the bill for resource-entry exclusion at κ=0, with the same shared-resource coupling.

## T256, cadence 0.25

Strong interventions (strength 0.95), relative to the matched idle world. Intervals are conditioning bounds, not sampling confidence intervals.

| Target | Yield | Bill | Whole Δ bits | D interval | S interval |
| --- | ---: | ---: | ---: | ---: | ---: |
| access_entry | 1 | 0.1 | -13.040 | [15.011, 23.435] | [-34.469, -22.263] |
| access_entry | 1 | 0.3 | -10.081 | [12.348, 21.452] | [-29.262, -17.408] |
| access_entry | 1 | 1 | -12.563 | [-2.627, 4.603] | [-18.024, -7.088] |
| trap_entry | 0 | 0.1 | 37.062 | [1.519, 13.152] | [29.278, 35.482] |
| trap_entry | 0 | 0.3 | 33.470 | [2.420, 14.257] | [26.229, 32.315] |
| trap_entry | 0 | 1 | 18.071 | [-5.363, 6.208] | [15.667, 21.278] |
| trap_entry | 1 | 0.1 | 38.232 | [1.420, 13.056] | [28.576, 39.426] |
| trap_entry | 1 | 0.3 | 34.697 | [2.309, 14.135] | [25.452, 36.238] |
| trap_entry | 1 | 1 | 19.190 | [-5.310, 6.280] | [14.551, 25.044] |
| trap_entry | 4 | 0.1 | 32.408 | [1.492, 12.905] | [12.355, 42.567] |
| trap_entry | 4 | 0.3 | 29.460 | [2.393, 13.984] | [9.706, 40.047] |
| trap_entry | 4 | 1 | 15.535 | [-5.169, 6.196] | [0.333, 31.009] |

## Access, persistence and resource use

For cheap strong trap-entry steering at T256: first arrival, mean time in the pocket, net S capture and accepted source work are separate quantities. Both positive and negative changes are retained.

| Yield | First-arrival probability Δ | Mean pocket occupancy Δ | Net S capture Δ | Accepted work Δ |
| ---: | ---: | ---: | ---: | ---: |
| 0 | -0.1131 | -0.0092 | 0.2533 | 0.3849 |
| 1 | -0.1131 | -0.0378 | 0.0074 | 0.0193 |
| 4 | -0.1131 | -0.0451 | -0.0926 | -0.1317 |

Yield acts only after entering the pocket, so first-arrival probabilities are unchanged by yield for a given intervention. Trap-entry control also intercepts return from the pocket into the trap. It can obstruct arrival and prolong residence; this is not a pure first-entry restriction. The oracle knows the law; discovery here is physical access, not acquisition of a hidden model.

## Resource exclusion: breadth gain and material flow

| Bill | Additional D net capture | Intervention fuel | Capture minus bill |
| ---: | ---: | ---: | ---: |
| 0.1 | 0.0812 | 0.3295 | -0.2483 |
| 0.3 | 0.1158 | 0.8053 | -0.6895 |
| 1 | 0.1600 | 1.3813 | -1.2212 |

The last column is a partial flow margin, not a complete energy profit. See [the completed priority C5 comparison](C5_RESULTS.md) for the resolved private/whole conflict through T1024.

## Complete candidate families

144 completed family/horizon/cadence searches compare idle with strengths 0.55 and 0.95 at a fixed physical bill. GLOBAL_CHOICES.csv includes whole-field maximizers and conservative D/S possible maximizers. It does not optimize interval midpoints or declare the first arriving candidate a winner.

CORRIDOR_MAP.csv groups signs across all three tested clocks. Counts are case × horizon comparisons, not independent trials: negative: 22, mixed_or_unresolved: 2, positive: 72.

## Model and numerical scope

The fractional reservoir is explicitly physical in this adapter, with a common reversible bath and declared reference density. Active friction remains a coarse nonequilibrium control boundary. Native equilibrium and full energy accounting are checked; a closed microscopic reversible controller is not claimed. Both subjects are functional controller/apparatus proxies.

All physical stochasticity at the declared grain counts. No noise, intervention or environmental entropy is subtracted. D/S histories remain hidden-Markov; unresolved signs remain unresolved. The temporal audit covers the declared sample points, not every intermediate cadence.

Numerical source: `1449c792d18313900d65f17258a0f3afbb518b541554526e27a66b5a65153e98`. Configurations, receipts, compact maps, small code archives and validation records are retained. No dense kernels are saved.
