# Constraint Stage A — numerical map

> **Updated interpretation, 16 October 2026:** Historical `native_events` steering may redirect into chemistry. Exit/all steering is not mobility evidence; B1 also intercepted pocket returns. See [the audit correction](../C5_AUDIT_CORRECTIONS_2026-10-16.md) before using these rows. Original numerical results are retained.

Status: **complete**. 470/470 cases retained;
5592 case/horizon/cadence comparisons. Complete finite-history lushness is
primary. Limiting rates and temporal asymptotic coefficients are diagnostics.

## T256, cadence 0.25

| Target / mode | Bill | T256 Δ bits range | D resolved / cases | S positive / negative |
| --- | --- | ---: | ---: | ---: |
| access / field | potential probe | -13.560 to -7.123 | 0/2 | 0 / 2 |
| access_entry / blocking | 0 (limit) | -48.998 to -9.227 | 0/6 | 0 / 6 |
| access_entry / blocking | 1 | -14.784 to -1.300 | 5/24 | 0 / 24 |
| access_entry / blocking | 2 | -3.894 to -0.675 | 0/6 | 0 / 4 |
| access_entry / steering | 0 (limit) | -38.351 to -7.406 | 0/6 | 0 / 6 |
| access_entry / steering | 1 | -16.497 to -1.219 | 5/24 | 0 / 22 |
| access_entry / steering | 2 | -4.814 to -0.953 | 0/6 | 0 / 3 |
| access_exit / blocking | 1 | -5.412 to +1.388 | 0/20 | 0 / 0 |
| access_exit / steering | 0 (limit) | +7.413 to +50.810 | 0/6 | 6 / 0 |
| access_exit / steering | 1 | -2.824 to +3.370 | 0/20 | 16 / 0 |
| access_exit / steering | 2 | -0.151 to +0.452 | 0/6 | 0 / 0 |
| all_mobility / blocking | 1 | -18.542 to -0.943 | 4/20 | 0 / 20 |
| all_mobility / steering | 1 | -16.327 to +0.645 | 5/20 | 0 / 2 |
| construction / field | potential probe | -10.129 to -5.114 | 0/2 | 0 / 2 |
| construction_entry / blocking | 0 (limit) | -35.271 to -7.009 | 0/6 | 0 / 6 |
| construction_entry / blocking | 1 | -11.646 to -0.802 | 5/24 | 0 / 22 |
| construction_entry / blocking | 2 | -2.758 to -0.399 | 0/6 | 0 / 3 |
| construction_entry / steering | 1 | -12.341 to -0.566 | 4/20 | 0 / 16 |
| construction_exit / blocking | 1 | -6.383 to +0.190 | 1/20 | 0 / 12 |
| construction_exit / steering | 0 (limit) | +3.706 to +25.180 | 0/6 | 6 / 0 |
| construction_exit / steering | 1 | -5.619 to +1.091 | 1/20 | 10 / 0 |
| construction_exit / steering | 2 | -1.664 to +0.139 | 0/6 | 0 / 0 |
| neutral_entry / blocking | 1 | -11.535 to -0.702 | 4/20 | 0 / 18 |
| neutral_entry / steering | 1 | -12.130 to -0.415 | 4/20 | 0 / 16 |
| random0 / blocking | 1 | -14.240 to -3.393 | 0/3 | 0 / 3 |
| random0 / steering | 1 | -32.987 to -11.137 | 0/3 | 0 / 3 |
| random1 / blocking | 1 | -11.535 to -2.735 | 0/3 | 0 / 3 |
| random1 / steering | 1 | -33.209 to -11.397 | 0/3 | 0 / 3 |
| random2 / blocking | 1 | -2.681 to -0.026 | 0/3 | 0 / 2 |
| random2 / steering | 1 | -1.540 to +0.634 | 0/3 | 0 / 0 |
| random3 / blocking | 1 | -9.950 to -2.265 | 0/3 | 0 / 3 |
| random3 / steering | 1 | -9.990 to -2.001 | 0/3 | 0 / 3 |
| random4 / blocking | 1 | -5.314 to -0.959 | 0/3 | 0 / 2 |
| random4 / steering | 1 | -4.476 to -0.530 | 0/3 | 0 / 1 |
| random5 / blocking | 1 | -2.633 to +0.233 | 0/3 | 0 / 2 |
| random5 / steering | 1 | -3.123 to +0.577 | 0/3 | 0 / 0 |
| random6 / blocking | 1 | -6.765 to -1.607 | 0/3 | 0 / 3 |
| random6 / steering | 1 | -10.012 to -2.540 | 0/3 | 0 / 3 |
| random7 / blocking | 1 | -1.311 to +0.218 | 0/3 | 0 / 1 |
| random7 / steering | 1 | +1.647 to +2.392 | 0/3 | 2 / 0 |
| trap / field | potential probe | +10.403 to +16.999 | 0/2 | 2 / 0 |
| trap_entry / blocking | 1 | +2.154 to +23.400 | 0/20 | 19 / 0 |
| trap_entry / steering | 0 (limit) | +9.888 to +50.203 | 0/6 | 6 / 0 |
| trap_entry / steering | 1 | +2.412 to +25.536 | 0/24 | 24 / 0 |
| trap_entry / steering | 2 | +1.458 to +5.906 | 0/6 | 4 / 0 |
| trap_exit / blocking | 1 | -22.038 to -1.870 | 0/20 | 0 / 19 |
| trap_exit / steering | 1 | -20.755 to -1.663 | 0/24 | 0 / 22 |

These ranges combine the stated strengths, costs and environments, rather than
averaging away signs. The full map retains each one separately. There are
79 case/horizon sign flips across cadences; 135 adjacent
strength brackets contain a sign crossing at one or more cadences. All brackets
are labeled for corridor stability. No crossing means none found on this grid.

The tighter subject-history intervals resolve D in
1485/5592 comparisons and S in
3880/5592. There are 850 strictly
resolved D/global divergences; unresolved intervals do not establish alignment,
ties or personal gains. No midpoint selects a winner.

## Physical accounts and scope

Capture is measured before friction or upkeep. Partial D energy advantage is
incremental net capture minus friction fuel minus incremental device upkeep,
all in charge-energy units. It is not personal lushness. The full bank balance
and energy conservation are reported independently. Apparatus stock, output,
access and trap occupancy accompany all comparisons.

Random controls target physical directed mobility edges. Fuel interpolation is
descriptive, inside observed support, and retains nonmonotonic branches. It
does not certify a ranking at an uncomputed strength. Preparation comparisons
are not a modeled replacement action. Field probes are conservative potential
contrasts; they are not claimed to match fuel spent by the driven interventions.

Maximum worker memory: 517.2 MiB. Summed worker time:
217.71 minutes. Largest generator energy residual:
6.99e-15; integrated residual:
7.74e-13; sampled occupation residual:
5.39e-12.

The [execution account](EXECUTION_ACCOUNT.json) records the full approximately
40.73-minute worker span across
the initial run and cached completion. The final status timer alone measures
the last cache-reconciliation invocation, not the duration of the science batch.

[Implemented specification](SPECIFICATION.md) · [Full map](COMPARISON_MAP.csv) ·
[Crossings](CROSSINGS.csv) · [Subject divergences](DIVERGENCE.csv) ·
[Preparation controls](PREPARATIONS.csv) · [Fuel interpolation](FUEL_MATCH.csv) ·
[Fixed-family choices](FIXED_CHOICES.csv) ·
[Structural reading](INTERPRETATION.md)
