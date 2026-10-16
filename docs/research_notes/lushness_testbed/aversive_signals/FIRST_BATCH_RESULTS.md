# First W1/W2 adversarial batch — results

All 384 arm/cadence analyses completed at 32 parameter points.
Whole finite-history lushness is primary. Rates and offsets are diagnostics.

## Primary resolved comparison (T64, cadence 0.25)

| Case | Difference, bits | Raw ranking | Qualification | Tracking MI |
| --- | ---: | --- | --- | ---: |
| W1-00 | +0.257938 | strict_positive | adapter_relative_ranking_counterexample | 0.00954302 |
| W1-01 | -0.302039 | strict_negative | adversary_loses | 0.0323918 |
| W1-02 | -0.773149 | strict_negative | adversary_loses | 0.0143747 |
| W1-03 | -2.330841 | strict_negative | adversary_loses | 0.0483909 |
| W1-04 | -0.088253 | strict_negative | adversary_loses | 0.0119286 |
| W1-05 | -0.961660 | strict_negative | adversary_loses | 0.0386488 |
| W1-06 | -1.024197 | strict_negative | adversary_loses | 0.0169125 |
| W1-07 | -2.807594 | strict_negative | adversary_loses | 0.0551232 |
| W1-08 | +0.153484 | strict_positive | adapter_relative_ranking_counterexample | 0.00872776 |
| W1-09 | -0.482325 | strict_negative | adversary_loses | 0.0301101 |
| W1-10 | -1.003678 | strict_negative | adversary_loses | 0.0110195 |
| W1-11 | -2.760225 | strict_negative | adversary_loses | 0.0391887 |
| W1-12 | -0.150802 | strict_negative | adversary_loses | 0.0110496 |
| W1-13 | -1.074482 | strict_negative | adversary_loses | 0.0361551 |
| W1-14 | -1.195802 | strict_negative | adversary_loses | 0.0135958 |
| W1-15 | -3.141817 | strict_negative | adversary_loses | 0.0459502 |
| W2-00 | +0.802271 | strict_positive | not_instantiated | 0.00316506 |
| W2-01 | -1.498885 | strict_negative | not_instantiated | 0.00973523 |
| W2-02 | -2.506841 | strict_negative | not_instantiated | 0.0082883 |
| W2-03 | -12.847795 | strict_negative | not_instantiated | 0.030488 |
| W2-04 | -0.089959 | strict_negative | not_instantiated | 0.00469919 |
| W2-05 | -4.749762 | strict_negative | not_instantiated | 0.0157504 |
| W2-06 | -3.061597 | strict_negative | not_instantiated | 0.0102765 |
| W2-07 | -14.349758 | strict_negative | not_instantiated | 0.0398984 |
| W2-08 | +0.430365 | strict_positive | not_instantiated | 0.00331926 |
| W2-09 | -2.636581 | strict_negative | not_instantiated | 0.0104593 |
| W2-10 | -2.725287 | strict_negative | not_instantiated | 0.00696058 |
| W2-11 | -13.484886 | strict_negative | not_instantiated | 0.0275396 |
| W2-12 | -0.247719 | strict_negative | not_instantiated | 0.0049297 |
| W2-13 | -5.121533 | strict_negative | not_instantiated | 0.0168423 |
| W2-14 | -3.089360 | strict_negative | not_instantiated | 0.0090597 |
| W2-15 | -14.497521 | strict_negative | not_instantiated | 0.0374283 |

## Registered stronger corridor

{"no_registered_main_kill": 32}

The corridor includes both grains, all three cadences, T256/T1024 and the limiting offset comparison.
No unresolved interval, failed instantiation or functional-gain veto is scored as a main kill.

## Reproduction

Input hash: `d4027d688924ccc02627421b96415e3c3e8f55f00a9ce9be70eeca22f5f5d191`.
Wall time 42.738s; peak job memory 140.8 MiB.
Maximum numerical residual: 1.82e-12.
The full parameter surface is in FIRST_BATCH_PARAMETER_MAP.csv and FIRST_BATCH_SUMMARY.json.
Raw arm/readout results and frozen sources remain in the ignored local run bundle.

Numerical note: 340 equal-bound endpoint reversals were expanded outward below the registered residual tolerance; scientific tolerance unchanged.

This is a finite functional model. W3/W4 and the full r2 grid remain unrun.
The local tracking definition and cost box are declared assumptions; see FIRST_BATCH_SPEC.md and COST_ANCHORS.md.
