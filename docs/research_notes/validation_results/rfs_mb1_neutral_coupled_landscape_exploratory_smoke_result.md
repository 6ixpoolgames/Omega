# RFS-MB1 Neutral Coupled Landscape Exploratory Smoke Result

Date: 2026-05-26  
Spec: `docs/RFS_MB1_NEUTRAL_COUPLED_LANDSCAPE_AUDIT_SPEC.md`  
Runner: `omega/rfs_mb1/run_neutral_coupled_landscape_audit.py`  
Output: `results/rfs_mb1_coupled_landscape/20260526_exploratory_smoke/`

## Claim Boundary

This is an exploratory coupled-landscape smoke. It does not claim Omega,
agency, identity, value, consciousness, or scientific-gate passage.

The question tested was narrower:

```text
Can neutral coupling maps between independently generated relation landscapes
produce support/distribution deformation beyond matched controls?
```

## Run Shape

```text
paired landscapes requested: 72
fresh seeds per pair: 1
coupling maps: frontier_signature, constraint_profile, asymmetry_profile
coupling modes: uncoupled, full A->B, full B->A, bidirectional, source shuffled,
                magnitude-matched random, target shuffled, direction reversed,
                A/B swapped
horizons: 4, 8, 16, 24, 32
start samples: 3
probe limit: 5
workers requested: 18
jobs requested: 2160
jobs completed: 2160
metric rows: 19440
errors: 0
wall clock: 250.3 seconds
promotion enabled: false
```

## Required Outputs

The run wrote the required first-pass MB1 artifacts:

```text
neutral_coupled_landscape_audit_report.md
coupled_landscape_sampling_plan.csv
coupling_map_summary.csv
coupling_mode_metric_rows.csv
coupling_specificity_summary.csv
coupling_horizon_lag_profile.csv
coupling_matched_controls.csv
coupling_fakeout_summary.csv
coupling_phenotype_summary.csv
coupling_start_probe_recurrence.csv
coupling_case_studies.md
status.json
```

## Headline Result

The runner is operational and the neutral coupling audit pattern is feasible.

Full A-to-B rows:

```text
full A->B rows: 2160
mean full A->B deformation: 0.1214
specific non-fakeout full rows: 7
magnitude-only full-row fakeouts: 128
source-structure margin full rows: 44
target-specificity margin full rows: 167
directional imbalance full rows: 499
```

Coupling-map specificity rates for full A-to-B rows:

```text
frontier_signature: positive_specific_excess_rate 0.0514
constraint_profile: positive_specific_excess_rate 0.0778
asymmetry_profile:  positive_specific_excess_rate 0.0611
```

Across all rows, most outcomes remain inactive or control-limited:

```text
no_detectable_coupling: 14818
cap_or_censoring_limited: 2080
magnitude_only_deformation: 925
mixed_support_distribution_coupling: 528
source_structure_specific_deformation: 574
target_specific_deformation: 272
directional_coupling: 166
underdetermined_coupling: 77
```

## Interpretation

The exploratory branch did not collapse technically. It produced the expected
control table, matched-mode comparisons, lag summaries, recurrence summaries,
and case-study artifacts without runtime errors.

Substantively, this is not enough to promote RFS-MB1. The signal is sparse:
only `7` full A-to-B rows were both specific and non-fakeout by the current
rough classifier. Many apparent deformations are explained by magnitude,
source-shuffle equivalence, target-shuffle equivalence, probe collision, or
saturation/censoring.

The most useful takeaway is that neutral coupled-landscape auditing is now a
working measurement surface. It can be used as an exploratory sandbox after the
single-landscape support/distribution branch is better characterized.

## Recommendation

Keep RFS-MB1 as an exploratory sandbox, not the active validation branch.

Next useful work, if we return to this branch:

```text
1. improve coupling-map specificity so source_shuffled controls are not often equivalent
2. add true fresh-seed recurrence for promising rows
3. separate target-shuffle controls from overly destructive target randomization
4. add a small hand-audited case-study check before any larger MB1 atlas
5. keep all agency/identity/value labels out of code and outputs
```

The current active empirical lane should remain RFS-MB0 support/distribution
deformation taxonomy unless MB1 is explicitly selected for a sandbox cycle.

