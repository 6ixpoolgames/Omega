# Failures of working catalytic templates

2026-10-05.

All 384 prior source cuts were retained; 60 supported a currently working template. 64 native continuations per arm give 7,680 trajectories and 674,635 events, in 29.91 seconds with ten workers. Physical rules unchanged.

[Protocol](lattice_corridor_protocol_v0.md) · [Full results](lattice_template_damage_v0/summary.json) · [Context variation](lattice_template_damage_v0/context_errors.json)

Working-template thermal failures carry 0.893% of all native thermal bond-failure flux in this empirical source mixture. Within that class, contexts and selected edges receive their native rate weights once. This is a conditional dependency experiment, not an estimate of the typical effect of every failure. Each arm can subsequently undergo the same native reactions, including loss and repair.

## Consequences and recovery over time

Other catalytic formations exclude re-forming the originally broken pair. Errors below describe conditional continuation sampling; source-state and selected-edge uncertainty is additional. Separate context variation estimates are retained, not silently added as if they were independent errors.

| Lag | Other formation count: broken / skipped | Count difference ± conditional SE | Current formation hazard: broken / skipped | Endpoints connected: broken / skipped |
|---:|---:|---:|---:|---:|
| 0.0 | 0.000 / 0.000 | +0.000 ± 0.000 | 0.921 / 1.851 | 0.242 / 1.000 |
| 0.5 | 0.414 / 0.688 | -0.275 ± 0.023 | 0.740 / 1.032 | 0.391 / 0.987 |
| 2.0 | 1.328 / 1.743 | -0.415 ± 0.037 | 0.519 / 0.550 | 0.562 / 0.964 |
| 5.0 | 2.642 / 3.039 | -0.397 ± 0.052 | 0.356 / 0.359 | 0.650 / 0.920 |

## Interpretation

Taking a native working-template failure suppresses immediate construction and leaves fewer subsequent catalytic formations over the observed window. By lag5 the current formation hazards are close again, while the accumulated histories still differ. Endpoint activity alone misses that historical effect.

At lag5 the count difference is -0.397; the weighted context-variation SE is 0.044. The selected empirical mixture and limited source contexts constrain extrapolation.

Original bond restored at least once: 0.508; present at lag5: 0.439; connected by any path: 0.650. Recovery remains multidimensional, and connection is not identical chemical function.

Far spatial response is small and varies across lags; the late far-cell response is comparable to the sham estimate. The panel does not establish persistent long-range damage. Shared fuel and rigid-cluster movement remain coarse-model limitations. Additional reaction counts are not automatically additional value; this test identifies an actual dependency and its history.

This finding makes fragility informative about how contribution is supported. It supplies no rule that a useful construction must survive indefinitely.

Reproduce with `python -m omega_v2.validation.lattice_damage_v0 --templates-only --replicates 64 --workers 10 --out docs/research_notes/omega_v2/lattice_template_damage_v0`. The summary's inherited `mean_thermal_failure_rate` field denotes the selected working-template class in this panel; all-failure hazards and class rarity are stored separately.
