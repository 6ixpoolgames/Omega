# RFS-MB0 Future Landscape Detector v1 Handoff

Status: Codex implementation handoff after first future-landscape smoke

Purpose: revise the future-landscape detector without tuning it to pass the desired structured relation family.

## 0. Immediate clarification

JS and KL are already implemented as reported metrics.

Current implementation:

```text
omega/rfs_mb0_future_landscape/detectors.py
  js_divergence(...)
  smoothed_kl(...)

omega/rfs_mb0_future_landscape/landscape.py
  JS_to_null_mean
  smoothed_KL_to_null_mean
```

But they are not yet doing load-bearing classification work.

Current `structured_propagation` is assigned by absolute heuristics:

```text
entropy_mean > 0.3
predictive_information >= 0.08
motif_reuse >= 0.25
not collapse
not cycle
```

This is the main detection-tuning risk.

The next revision must make structure classification depend on matched-control separation, not hand-tuned absolute thresholds.

## 1. Preserve the current smoke result as v0

Do not rewrite history.

Keep the current detector output as:

```text
heuristic_profile_class_v0
```

or preserve current `profile_class` and add a new field:

```text
control_relative_profile_class_v1
```

Do not tune v0 thresholds to make the desired families pass.

The first smoke result is valuable precisely because it overcalled structure and revealed the failure.

## 2. Core audit finding

The current smoke passed implementation/workflow gates:

```text
systems: 33
future profiles: 672
errors: 0
```

It also cleanly separated simple controls:

```text
fixed_point_control -> collapse_like
cyclic_relation / phase_cycle_control -> cycle_like
permissive_probe_control -> permissive_blur
strict_probe_control -> strict_fragmentation
```

But the scientific gate did not pass.

Current detector labels all of these as `structured_propagation`:

```text
structured_relation
expanding_relation
random_relation_control
degree_preserving_control
coordinate_permutation_control
```

Therefore the current detector mostly captures high-reach, high-reuse, non-collapse profiles rather than structured propagation above matched nulls.

## 3. Required implementation changes

### 3.1 Rename misleading metrics

Current names overstate what the metrics measure.

Rename or duplicate fields as follows:

```text
predictive_information
  -> adjacent_distribution_similarity
```

because current implementation computes:

```text
1 - JS(P_h, P_previous_h)
```

between adjacent horizon endpoint-signature distributions. This is useful, but it is not mutual information.

Rename:

```text
compression_proxy
  -> signature_reuse_fraction
```

because current implementation measures repeated signatures over total signature tokens, not a real MDL/compression length.

Rename:

```text
transition_motif_count_mean
  -> signature_reuse_scaled
```

or remove if redundant.

Keep old columns for backward compatibility if useful, but mark them as deprecated in the summary.

### 3.2 Add actual transition-level information measures

Implement true path/transition-level signature statistics.

For each system, start state, probe, and horizon transition `h -> h+1`, compute joint counts:

```text
count(s_h, s_{h+1})
```

where `s_h = sigma(x_h)` and `s_{h+1} = sigma(x_{h+1})`.

This may be computed by exact edge expansion between exact frontiers or by sampled paths if exact path enumeration is too large.

Report:

```text
signature_transition_MI_by_h
signature_transition_MI_mean
signature_transition_conditional_entropy_by_h
signature_transition_conditional_entropy_mean
signature_transition_entropy_rate_proxy
signature_transition_grammar_size_by_h
signature_transition_motif_reuse_by_h
```

The mutual information should be the standard discrete quantity:

```text
I(S_h ; S_{h+1}) = sum_{a,b} P(a,b) log2(P(a,b)/(P(a)P(b)))
```

This replaces the current adjacent-distribution-similarity proxy as the main prediction measure.

### 3.3 Mechanically enumerate probes

Current probes are hand-listed:

```text
projection_q0
projection_q1
projection_q2
relation_q0_q1
relation_q1_q2
parity_q0_q1_q2
```

Replace this with mechanical generation from the state coordinate presentation.

For `sigma <= 2` initially, generate:

```text
all single-coordinate projections
all pairwise ordered projections, if cheap
all pairwise modular differences
all pairwise equality indicators
all pairwise unordered value-multiset signatures
```

Optional if still cheap:

```text
all triple parity/residue signatures up to sigma=3
bounded one-step response-profile probes
```

The implementation must report:

```text
probe_count
probe_family counts
probe_names_json
sigma
```

Do not select probes because they help structured_relation pass.

### 3.4 Add matched-null bundle

Current `null_distribution_by_h` uses only a generated `degree_preserving_control` system.

Replace or supplement with a null bundle:

```text
random_relation_null
degree_preserving_null
frontier_size_preserving_null
probe_marginal_preserving_null
coordinate_permutation_null
```

At minimum, implement:

```text
null_JS_degree
null_KL_degree
null_JS_random
null_KL_random
null_JS_probe_marginal
null_KL_probe_marginal
```

and summary deltas/ranks:

```text
MI_delta_vs_null
recurrence_delta_vs_null
signature_reuse_delta_vs_null
JS_rank_against_nulls
KL_rank_against_nulls
```

If a full null bundle is too much for the first pass, implement degree + random + probe-marginal preserving nulls first.

### 3.5 Treat coordinate permutation correctly

`coordinate_permutation_control` is not a simple negative control. It is closer to a presentation-invariance control.

Split interpretation into:

```text
coordinate_permutation_invariance_control
```

and, if needed later:

```text
coordinate_permutation_probe_leakage_test
```

A truly coordinate-free detector should not necessarily fail under coordinate permutation.

Do not count coordinate-permutation survival as the same kind of failure as random/degree control mimicry.

### 3.6 Make `structured_propagation` control-relative

Add a new classifier:

```text
control_relative_profile_class_v1
```

It may still use neutral classes:

```text
noise_like
collapse_like
cycle_like
permissive_blur
strict_fragmentation
structured_propagation
null_mimic
underdetermined
```

`structured_propagation` must require:

```text
not collapse_like
not cycle_like
not permissive_blur
not strict_fragmentation
```

plus evidence of separation from matched nulls by multiple independent measures.

Example conservative first rule:

```text
structured_propagation if:
  profile is not collapse/cycle/permissive/strict
  AND transition_MI_mean > max(null_transition_MI_mean) + margin
  AND signature_transition_motif_reuse > max(null_motif_reuse) + margin
  AND signature_reuse_fraction is not trivially near 1 from probe blur
  AND at least one divergence metric separates from null bundle
```

But avoid hard-tuning margins after looking at desired-family results.

Better: report ranks and mark `structured_propagation_candidate` only when observed profile ranks above all matched nulls on a predeclared majority of metrics.

Example rank rule:

```text
metrics = [transition_MI, motif_reuse, recurrence, noncollapse_growth, JS_to_probe_marginal_null]
pass if observed structured family beats all matched nulls on >= 3 of 5 metrics
```

Keep this rule explicit in the summary.

If no rule is defensible yet, output `underdetermined` rather than tuning.

## 4. Saturation warning

Many current families saturate reachability quickly:

```text
reach_H16 near full state space
exact_H16 large
```

This causes endpoint signature profiles to be dominated by probe alphabet and frontier size.

Add saturation diagnostics:

```text
reach_saturation_fraction = reach_Hmax / |X|
exact_saturation_fraction = exact_Hmax / |X|
saturation_horizon
```

If reach saturation is too high, the classifier should downweight or flag the profile:

```text
saturation_dominated
```

Do not call a saturated profile structured unless it separates from saturation-matched controls.

## 5. JS/KL usage guidance

JS/KL should remain reported, but do not let divergence alone define structure.

A fixed point and a clock can have high divergence from null.

The correct readout is:

```text
profile class + divergence from null
```

For v1, report:

```text
JS_to_null_bundle_min
JS_to_null_bundle_max
JS_to_null_bundle_mean
KL_to_null_bundle_min
KL_to_null_bundle_max
KL_to_null_bundle_mean
```

Also report per-null columns.

Use JS as the stable headline divergence.

Use smoothed KL as a directional steering-cost proxy.

## 6. Output changes

Add or update outputs:

```text
transition_information.csv
probe_summary.csv
null_bundle_summary.csv
control_relative_profile_classes.csv
saturation_summary.csv
```

Keep existing outputs:

```text
results.csv
future_profiles.csv
signature_distributions.csv
control_comparison.csv
profile_classes.csv
divergence_summary.csv
deformation_summary.csv
summary.md
status.json
```

`summary.md` must include:

```text
v0 heuristic class counts
v1 control-relative class counts
null bundle comparison
transition-level MI summary
probe enumeration summary
saturation warning table
claim boundary
recommendation
```

## 7. Claim boundary

Allowed after v1 smoke:

```text
We implemented a neutral future-landscape detector with mechanically generated probes,
transition-level information measures, matched null bundles, and control-relative classes.
```

Allowed only if supported:

```text
A structured future-landscape profile separated from matched nulls by multiple
predeclared measures.
```

Not allowed:

```text
Omega detected
valuer detected
agent detected
identity detected
viability detected
moral value detected
```

## 8. Do not do yet

Do not add:

```text
resource/cost/fuel coordinates
kappa
agent labels
identity labels
viable path labels
support/recover/degrade semantics
lattice/sheaf machinery
large scaling runs
```

Do not tune thresholds after seeing the structured-relation result.

Do not convert coordinate permutation into a simple failure control.

## 9. Minimum acceptable v1 smoke

Run a small smoke only.

Suggested shape:

```text
families: same as current smoke, with coordinate permutation relabeled as invariance control
seeds_per_family: 3
start_samples: 4
sigma: 2
horizons: 0,1,2,4,8,12,16
workers: 18
```

Success is not expected.

Desired result is diagnostic clarity:

```text
Do current structured families separate from random/degree/probe-marginal nulls?
If yes, weak gate progress.
If no, detector remains underdetermined and substrate/probes need revision.
```

## 10. Bottom line

The v0 future-landscape smoke was useful because it overcalled structure.

v1 should not tune that away.

v1 should make the classifier answer a stricter question:

```text
Does the future landscape contain structured propagation that survives matched-null comparison?
```

not:

```text
Does the profile have enough entropy, recurrence, and compression to look nontrivial?
```
