# Reversible 2D chemistry: exploratory pilot v0

2026-10-04.

The first 2D substrate run is complete: 32 configurations, 12 trajectories each, 384 trajectories and 158,675 physical events. Simulation took 5.79 seconds with ten workers. No lushness score was computed. This is a small bracket of physical behavior, not an exhaustive survey or an equilibrium-gas comparison.

[Model and rationale](lattice_chemistry_protocol_v0.md); [comparison with established models](model_comparison_map_2026-10-04.md); [run manifest](lattice_chemistry_v0/manifest.json); [full summary](lattice_chemistry_v0/summary.json); [historical audit](lattice_chemistry_v0/history_audit.json). The data directory also contains all 384 compressed event histories.

## What changed from the line model

Particles increased from four to 16/36 and can move in two dimensions. Loops, bypasses, compact clusters and local crowding can occur. Bonds are favorable contacts whose energies depend on two conformations; fuel energy is a separate parameter. Local templates accelerate a reversible chemical path. The shared finite reservoir and implicit heat bath remain. This is a coarse hybrid of established ingredients, not a replication of a particular molecular system. The square template rule is an explicit mechanistic hypothesis, not a newly observed law of chemistry.

## Descriptive results

All figures below refer to t=20 unless a time curve is shown. Twelve replicates support an initial description, not precise boundaries. A dispersed initial condition is fuelled and unbonded; it is not equilibrium.

### Bond strength and density

N=36, dispersed start. Entries are mean ± one Monte Carlo standard error. b is the catalytic barrier reduction in kBT units, not composition depth.

| Density | Bond strength | b | Bonds | Largest component | Fuel remaining |
|---|---:|---:|---:|---:|---:|
| 0.250 | 1 | 0 | 23.42 ± 0.51 | 9.92 ± 0.82 | 4.67 ± 0.61 |
| 0.250 | 1 | 2 | 24.50 ± 0.68 | 11.33 ± 1.24 | 3.83 ± 0.47 |
| 0.250 | 3 | 0 | 34.00 ± 1.03 | 16.33 ± 1.39 | 8.42 ± 0.73 |
| 0.250 | 3 | 2 | 35.33 ± 0.72 | 17.17 ± 1.79 | 6.75 ± 0.89 |
| 0.444 | 1 | 0 | 27.50 ± 1.06 | 14.92 ± 1.88 | 1.83 ± 0.37 |
| 0.444 | 1 | 2 | 29.25 ± 1.05 | 15.75 ± 1.77 | 0.83 ± 0.27 |
| 0.444 | 3 | 0 | 41.75 ± 0.78 | 29.33 ± 2.01 | 5.00 ± 0.49 |
| 0.444 | 3 | 2 | 42.25 ± 0.90 | 30.42 ± 1.92 | 1.58 ± 0.23 |

Stronger contacts produce larger retained assemblies in these runs. They also leave more fuel at the deadline in each listed density/catalysis comparison. That is consistent with reduced turnover and stronger passive assembly; bond stock is not simply proportional to fuel spent. Contact energetics, kinetics and preparation jointly determine the result. More densely packed systems retain larger components here, but larger is not itself a continuation or lushness verdict.


### Catalysis changes history more than the final bond stock

Paired differences b=2 minus b=0, using identical initial configurations per replicate and independent reaction randomness. SE is computed across replicate differences. No multiple-comparison significance claim is made.

| N | Density | Strength | Start | Change in bonds ± SE | Change in fuel ± SE | Catalytic formations | Catalytic reversals |
|---:|---:|---:|---|---:|---:|---:|---:|
| 16 | 0.250 | 1 | dispersed | +1.00 ± 1.15 | -1.83 ± 0.46 | 1.67 | 0.25 |
| 16 | 0.250 | 1 | seeded | -0.08 ± 1.10 | -0.67 ± 0.47 | 3.67 | 0.92 |
| 16 | 0.250 | 3 | dispersed | +0.33 ± 0.94 | -1.17 ± 0.89 | 3.25 | 0.33 |
| 16 | 0.250 | 3 | seeded | +1.42 ± 0.86 | -0.92 ± 0.61 | 5.58 | 0.50 |
| 36 | 0.250 | 1 | dispersed | +1.08 ± 0.75 | -0.83 ± 0.61 | 5.33 | 1.00 |
| 36 | 0.250 | 1 | seeded | +0.92 ± 1.62 | -0.92 ± 0.92 | 7.25 | 1.17 |
| 36 | 0.250 | 3 | dispersed | +1.33 ± 1.23 | -1.67 ± 0.97 | 6.50 | 0.75 |
| 36 | 0.250 | 3 | seeded | +0.83 ± 1.49 | -2.83 ± 1.04 | 8.08 | 1.08 |
| 16 | 0.444 | 1 | dispersed | -0.25 ± 0.70 | +0.58 ± 0.26 | 2.67 | 0.83 |
| 16 | 0.444 | 1 | seeded | -1.67 ± 0.72 | -0.25 ± 0.35 | 6.17 | 1.17 |
| 16 | 0.444 | 3 | dispersed | +0.33 ± 0.82 | -1.75 ± 0.59 | 3.67 | 0.50 |
| 16 | 0.444 | 3 | seeded | +2.00 ± 1.17 | -2.67 ± 0.70 | 8.25 | 0.75 |
| 36 | 0.444 | 1 | dispersed | +1.75 ± 1.29 | -1.00 ± 0.52 | 12.08 | 3.33 |
| 36 | 0.444 | 1 | seeded | -0.67 ± 1.18 | -1.08 ± 0.71 | 10.42 | 2.92 |
| 36 | 0.444 | 3 | dispersed | +0.50 ± 0.98 | -3.42 ± 0.47 | 11.92 | 2.25 |
| 36 | 0.444 | 3 | seeded | +0.92 ± 1.78 | -2.33 ± 0.47 | 14.75 | 2.33 |

The endpoint differences are small or mixed in several conditions, despite many extra catalytic firings. A forward catalytic event is not automatically an extra surviving bond: it can replace a later background event, reverse, or accelerate fuel depletion. Most forward firings need not be promptly reversed through the same channel; thermal loss is a separate route.

### Construction history

- Catalytic construction occurred in 88/96 catalysis-enabled dispersed runs, without a prebuilt seed.
- 87/192 catalysis-enabled trajectories reached at least two successive catalytic production steps.
- Of 1,335 catalytic formation events, 835 first joined that physical particle pair and 500 re-formed a previously present pair.
- 68 catalytic formation events returned to a pair already in the catalyst's production ancestry. Raw depth can therefore count recycling; it is not an open-endedness measure.

The no-catalysis arm is zero on specifically catalytic events by construction. That is not an independent discovery. The nontrivial observations concern how often templates arise, their subsequent history, resource use and the retained structures under the same local rules.

## Checks and interpretation limits

Five focused tests passed: exhaustive per-mechanism balance over 768 tiny states, movement/replay and conservation, rotation/renaming symmetry, kinetic-only catalysis with inventory concentration scaling, and quiescent deadline handling. All 158,675 saved events were replayed with valid geometry and inventory and reproduced the final states. Lint passed.

Full microscopic reversibility does not prevent a transient net chemical current: the initial fuel-rich distribution is out of equilibrium. Catalysis leaves equilibrium unchanged but changes relaxation times. The sampled state free-energy coordinate is not an ensemble free-energy estimate; no distribution entropy was estimated.

Limitations: short horizons and 12 repeats per condition; a chosen template geometry; rapid-release catalysis without explicit saturation; square-lattice anisotropy; reflecting boundaries; rigid components without rotation; shared fuel without transport; and an implicit bath. Strong attractive contacts naturally favor aggregation, so a large persistent cluster cannot be called generativity merely because it contains many bonds.

## Next useful probe

Retain this as the inexpensive spatial substrate. Before introducing more chemical detail, compare residual response to the same native local perturbations in retained aggregates and dispersed configurations. Ask whether composition changes later physical access, beyond bond stock, fuel use or templating turnover. Add rotation or local fuel when a specific observed bottleneck makes their missing resolution relevant. A thermal comparison needs an actual equilibrium preparation or a controlled relaxation reference, not an unbonded picture labeled gas.
