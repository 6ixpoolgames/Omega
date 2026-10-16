# First fixed-friction map

Status: complete. This is a small initial mechanism map, not the full
design sweep. All interventions use the same declared world inventory and
shared-source prescription as their idle-device reference. Policy changes
alter the induced generator. Marginal histories remain hidden-Markov.

24 cases are retained. Global finite-history lushness is exact up to
reported numerical residuals; D and S objectives are certified conditioning
intervals. Unresolved signs are not ties. No welfare reward, suffering variable,
persistence filter or subtraction of intervention randomness is used.

## T256, cadence 0.25

| Case | Global Δ bits | D marginal difference | S marginal difference | D capture gain | S capture loss | Friction fuel |
| --- | ---: | --- | --- | ---: | ---: | ---: |
| s0.04-k0-access-block | -6.293 | unresolved | strict_negative | +0.087 | +0.057 | 0.812 |
| s0.04-k0-access-steer | -6.803 | unresolved | strict_negative | +0.087 | +0.066 | 0.801 |
| s0.04-k0-construction-block | -5.206 | unresolved | strict_negative | +0.081 | +0.010 | 0.847 |
| s0.04-k0-trap-entry-steer | +9.547 | unresolved | strict_positive | +0.019 | -0.026 | 0.264 |
| s0.04-k0-trap-exit-steer | -7.555 | unresolved | strict_negative | +0.021 | +0.029 | 0.182 |
| s0.04-k1-access-block | -7.215 | unresolved | strict_negative | +0.103 | +0.065 | 0.869 |
| s0.04-k1-access-steer | -7.860 | unresolved | strict_negative | +0.101 | +0.073 | 0.856 |
| s0.04-k1-construction-block | -6.030 | unresolved | strict_negative | +0.103 | +0.017 | 0.918 |
| s0.04-k1-trap-entry-steer | +10.022 | unresolved | strict_positive | +0.022 | -0.025 | 0.284 |
| s0.04-k1-trap-exit-steer | -7.960 | unresolved | strict_negative | +0.025 | +0.031 | 0.191 |
| s0.12-k0-access-block | -6.655 | unresolved | strict_negative | +0.138 | +0.116 | 0.967 |
| s0.12-k0-access-steer | -7.312 | unresolved | strict_negative | +0.137 | +0.138 | 0.952 |
| s0.12-k0-construction-block | -4.487 | unresolved | strict_negative | +0.126 | -0.011 | 1.000 |
| s0.12-k0-trap-entry-steer | +12.196 | unresolved | strict_positive | +0.030 | -0.075 | 0.309 |
| s0.12-k0-trap-exit-steer | -9.214 | unresolved | strict_negative | +0.034 | +0.065 | 0.220 |
| s0.12-k1-access-block | -7.535 | unresolved | strict_negative | +0.169 | +0.130 | 1.058 |
| s0.12-k1-access-steer | -8.433 | unresolved | strict_negative | +0.163 | +0.155 | 1.039 |
| s0.12-k1-construction-block | -4.921 | unresolved | strict_negative | +0.167 | -0.008 | 1.107 |
| s0.12-k1-trap-entry-steer | +13.206 | unresolved | strict_positive | +0.036 | -0.078 | 0.339 |
| s0.12-k1-trap-exit-steer | -9.890 | unresolved | strict_negative | +0.041 | +0.069 | 0.236 |

The comparison map retains all horizons and cadences. 4 global
comparisons change sign across cadences. Whole-field best candidates and possible
self-objective maximizers are listed separately in COMPARISONS.json; bound
midpoints never decide a self objective. The family contains only the listed
fixed interventions, not all possible adaptive policies. The candidate-choice
table uses cadence0.25; every signed physical comparison retains all three.
Same-idle-law ordinary and unassembled preparation controls are also retained
at every horizon and cadence, without adding entropy for choosing a root.

## Scope

The target is S mobility. Steering can redirect into other physical S mobility
or chemistry channels and preserves S's exit rate at the same full state only.
It does not match integrated event counts, work or occupied states. Apparatus,
charge and the friction device must be present for active intervention.

Native chemistry obeys detailed balance with the source and active drive
removed. Active friction is an explicitly one-way nonequilibrium control
boundary with D fuel expenditure; the first-law ledger closes, but this is not
a complete reversible chemical implementation of a controller. The energy-shift
check and a chemical control implementation remain further modules.

Ordinary and unassembled reference preparations retain the same physical
degrees of freedom and can assemble under native dynamics. Any differences
reported for these roots are preparation comparisons, not an excision action.
The unassembled reference is coarse count matter, not microscopic gas.

All settings and costs are mechanism assumptions to investigate. A gain or loss
under a named intervention must be interpreted through capture, construction,
trap residence, authority and costs. Naming an objective does not establish
its ethical verdict.

[Implemented model](MODEL.md) · [Full comparisons](COMPARISONS.json) ·
[Structural interpretation](INTERPRETATION.md) · [Run records](SURVEY_STATUS.json)
