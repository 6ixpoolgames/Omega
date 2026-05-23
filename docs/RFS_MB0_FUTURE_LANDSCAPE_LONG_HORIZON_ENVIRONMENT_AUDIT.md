# RFS-MB0 Future Landscape Long-Horizon Environment Audit

Status: implementation spec after detector v1.1 smoke

Purpose: keep the current future-landscape substrate, extend horizon length, and diagnose whether non-detection is caused by horizon truncation, saturation, viscosity, null mismatch, or trivial environment design.

## 0. Context

Detector v1.1 did the right methodological thing:

```text
local profile false positives remained visible
aggregate degree-control passes dropped to zero
aggregate structured family count dropped to zero
scientific gate remained not passed
```

This is a clean negative result, but not a reason to abandon the current substrate yet.

The current runs finish cheaply. Therefore the next pass should stress horizon length before changing substrate families.

Current concern:

```text
We may be stopping too early for viscous relations,
or summarizing too late for fast-saturating relations,
or using horizon grids too sparse to see transient future-landscape deformation.
```

## 1. Do not move on from the substrate yet

Do not add a new relation atlas yet.

Do not add new hand-designed positive families yet.

Do not tune the detector to pass.

This audit keeps the current substrate and asks:

```text
Does the same finite relation environment reveal structured future-landscape
signals under longer and denser horizon measurement?
```

If not, then the failure is better localized to substrate/environment design.

## 2. Primary objective

Run a longer-horizon audit at least:

```text
3x to 5x current horizon length
```

and, if runtime remains manageable, also try:

```text
10x to 100x current horizon length
```

Current max horizon is approximately:

```text
H = 16
```

Minimum next horizon target:

```text
H_max = 64 or 80
```

Preferred exploratory target if cheap:

```text
H_max = 160
```

Stretch target:

```text
H_max = 512 or 1024
```

Because the state space is finite and small, exact frontiers may enter cycles/saturation. This is not a problem; it is part of the audit.

## 3. Horizon grids

Use at least two grids.

### 3.1 Dense early grid

Required:

```text
H = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16
```

Purpose:

```text
resolve pre-saturation and transient deformation
```

### 3.2 Log/long grid

Required minimum:

```text
H = 0,1,2,3,4,5,6,7,8,10,12,16,24,32,48,64,80
```

Preferred:

```text
H = 0,1,2,3,4,5,6,7,8,10,12,16,24,32,48,64,80,96,128,160
```

Stretch:

```text
H = 0,1,2,3,4,5,6,7,8,10,12,16,24,32,48,64,80,96,128,160,224,320,512,768,1024
```

The runner should allow horizon grid selection by CLI flag:

```text
--horizon-grid dense_early
--horizon-grid long_5x
--horizon-grid long_10x
--horizon-grid long_100x
--horizons custom comma-separated list
```

## 4. Metrics must be horizon-local

The v1.1 aggregate summary is useful, but long-horizon work must avoid collapsing everything into H16-style means.

For each horizon `H`, report:

```text
reach_count_H
exact_count_H
reach_saturation_fraction_H
exact_saturation_fraction_H
signature_entropy_H
signature_support_size_H
JS_to_null_H
KL_to_null_H
transition_MI_H
transition_conditional_entropy_H
transition_motif_reuse_H
transition_grammar_size_H
```

Also report derived horizon windows:

```text
pre_saturation_window
saturation_onset_H
post_saturation_window
cycle_onset_H
frontier_repeat_onset_H
max_non_saturated_H
```

Do not rely only on horizon-averaged metrics.

## 5. Window-level classes

Add window-level aggregate classes in addition to full-run aggregate classes.

Required windows:

```text
early_window: H <= 4
pre_saturation_window: reach_saturation_fraction_H < 0.95
near_saturation_window: 0.75 <= reach_saturation_fraction_H < 0.95
post_saturation_window: reach_saturation_fraction_H >= 0.95
long_cycle_window: horizons after frontier repeat/cycle onset
```

For each family/probe_family/window, compute:

```text
mean_MI_delta_vs_null
median_MI_delta_vs_null
mean_motif_delta_vs_null
median_motif_delta_vs_null
mean_JS_bundle
mean_KL_bundle
local_candidate_fraction
saturation_fraction
cycle_fraction
```

Add:

```text
aggregate_window_class_v1_2
```

Possible neutral classes:

```text
structured_candidate_window
saturation_dominated_window
cycle_dominated_window
null_mimic_window
underdetermined_window
```

This is diagnostic only.

## 6. Viscosity diagnostics

Add explicit measures for substrates that are too slow to show structure by H16.

For each family/probe/probe_family:

```text
first_nonzero_transition_MI_H
first_positive_MI_delta_H
first_positive_motif_delta_H
first_JS_separation_H
peak_MI_delta_H
peak_motif_delta_H
peak_JS_H
peak_signal_before_saturation
```

Define:

```text
viscous_candidate
```

only as a diagnostic flag:

```text
signal appears only after H16 and before saturation/cycle dominance
```

Do not classify it as structured_propagation yet.

## 7. Saturation diagnostics

The current substrate saturates quickly in some families.

Long-horizon run must clearly distinguish:

```text
fast saturation
late saturation
never saturation within horizon
frontier cycling after saturation
full-space mixing
```

Add outputs:

```text
saturation_onset_by_family.csv
horizon_window_summary.csv
long_horizon_profile_classes.csv
```

If a family saturates before meaningful separation can be measured, report:

```text
fast_saturation_environment
```

This is not a detector failure; it is environment design information.

## 8. Nulls for long horizon

Keep existing nulls:

```text
degree
random
probe_marginal
frontier_size
```

But in long-horizon summaries, null comparisons must be horizon-local and window-local.

For each horizon/window, compare against nulls matched at that horizon.

Required additions if cheap:

```text
saturation_matched_null_summary
frontier_repeat_matched_null_summary
```

If saturation-matched nulls are not implemented, saturated windows must remain withheld.

Do not call saturated profiles structured without saturation-matched comparison.

## 9. Output files to add

Add:

```text
horizon_local_profiles.csv
horizon_local_nulls.csv
horizon_window_summary.csv
aggregate_window_classes.csv
saturation_onset_by_family.csv
viscosity_diagnostics.csv
long_horizon_status.json
```

Keep existing v1.1 files:

```text
results.csv
future_profiles.csv
transition_information.csv
signature_distributions.csv
control_comparison.csv
profile_classes.csv
control_relative_profile_classes.csv
aggregate_family_classes.csv
aggregate_probe_family_classes.csv
degree_control_false_positives.csv
matched_null_summary.csv
summary.md
status.json
```

## 10. Summary.md required sections

Add:

```text
## Horizon Grid
```

Include the exact horizons used.

```text
## Saturation Onset
```

For each family:

```text
saturation_onset_H
frontier_repeat_onset_H
max_non_saturated_H
fast_saturation_flag
```

```text
## Window-Level Classes
```

For each family/window:

```text
aggregate_window_class_v1_2
mean_MI_delta_vs_null
median_MI_delta_vs_null
mean_motif_delta_vs_null
mean_JS_bundle
saturation_fraction
cycle_fraction
```

```text
## Viscosity Diagnostics
```

For each family:

```text
first_positive_MI_delta_H
peak_MI_delta_H
peak_signal_before_saturation
viscous_candidate_flag
```

```text
## Long-Horizon Gate Read
```

Answer:

```text
Are we ending too early?
Are we measuring too late?
Are signals only transient/pre-saturation?
Are families saturation-dominated?
Are controls still clean at long horizons?
```

## 11. Gate interpretation

The scientific gate remains strict.

A long-horizon run can produce these outcomes:

### 11.1 Early transient signal

```text
structured/non-control family separates from nulls before saturation
then becomes saturation_dominated
```

Interpretation:

```text
horizon grid was too coarse/late; substrate may still contain transient future-landscape structure
```

### 11.2 Viscous signal

```text
family separates only at H > 16 before saturation/cycle dominance
```

Interpretation:

```text
prior horizon was too short
```

### 11.3 No signal, clean controls

```text
no non-control family separates in any window
controls remain withheld/no-pass
```

Interpretation:

```text
current substrate likely does not produce detectable future-landscape structure under current probes/nulls
```

### 11.4 Saturation only

```text
apparent positives are always saturated or saturation-matched nulls also pass
```

Interpretation:

```text
environment design is too saturating; revise substrate only after documenting this
```

### 11.5 Control leakage

```text
random/degree controls pass at any aggregate window
```

Interpretation:

```text
detector/nulls still too weak for that horizon/window
```

## 12. Do not do

Do not:

```text
tune thresholds to make structured_relation pass
add agents/identities/viable paths
add cost/resource coordinates
add new semantic relation families
change the substrate before this audit
scale seeds massively before horizon behavior is understood
```

## 13. Suggested CLI examples

Minimum:

```bash
python -m omega.rfs_mb0_future_landscape.run_smoke \
  --out results/rfs_mb0_future_landscape/20260523_long_horizon_5x \
  --horizon-grid long_5x \
  --seeds-per-family 3 \
  --start-samples 4 \
  --sigma 2 \
  --workers 18
```

Stretch:

```bash
python -m omega.rfs_mb0_future_landscape.run_smoke \
  --out results/rfs_mb0_future_landscape/20260523_long_horizon_100x \
  --horizon-grid long_100x \
  --seeds-per-family 3 \
  --start-samples 4 \
  --sigma 2 \
  --workers 18 \
  --max-runtime-seconds 900
```

If the stretch run times out, checkpointed partial results are still useful.

## 14. Bottom line

Before changing substrates, use the cheap runtime to answer:

```text
Was the detector looking at the wrong horizon window?
```

The next run should keep the current substrate, extend horizon 3-5x minimum, preferably 10x or more if cheap, and report horizon-local/window-local evidence rather than only final aggregate classes.
