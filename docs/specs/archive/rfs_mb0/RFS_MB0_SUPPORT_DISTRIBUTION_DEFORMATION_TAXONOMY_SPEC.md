# RFS-MB0 Support/Distribution Deformation Taxonomy Spec

Status: next-run spec after probe-resolution calibration branch-B decision

Purpose: pause path-process escalation and re-center empirical work on support/distribution deformation phenotypes, where the relation-generator branch has produced more stable signals.

This spec follows the branch decision from the probe-resolution calibration smoke:

```text
B. Downgrade path-process for now and focus on support/distribution deformation taxonomy.
```

Path metrics should be retained as optional diagnostics, but they are not the target of this run.

## 0. Strategic context

The empirical branch has established:

```text
1. the original detector was too permissive;
2. hand-named substrates were replaced with a neutral action-generated relation atlas;
3. the relation generator remains worth keeping;
4. roughness-artifact interpretation was mostly repaired;
5. candidate phenotypes are mostly not start-fragile;
6. the generator is strongly constraint-dominated;
7. path-process metrics are currently blocked by probe-resolution/collision and matched-control fakeouts.
```

The path branch is not abandoned permanently, but it is downgraded for now.

The near-term empirical target is:

```text
reproducible support/distribution deformation phenotypes in neutral relation-generated future landscapes
```

not:

```text
path-process objects
agency
identity
valuerhood
viability
Omega
```

## 1. Core question

Ask:

```text
Which neutral relation-generator parameter regimes reproducibly deform reachable future support and endpoint/signature distributions, after triviality controls and matched controls?
```

Do not ask:

```text
Do we have path-process structure?
```

for this run.

## 2. Conceptual levels

Use a conservative deformation ladder.

### 2.1 Support deformation

Definition:

```text
the set of reachable signatures/futures differs from matched null/control expectations
```

Examples:

```text
some signatures become unreachable
some signatures become newly reachable
reachable support is concentrated, widened, split, or shifted
```

This is a legitimate lower-level future-landscape phenotype.

It is not a scientific gate pass.

### 2.2 Distribution deformation

Definition:

```text
the frequency/count distribution over reachable signatures differs from matched expectations, beyond support alone
```

Examples:

```text
same support but different mass concentration
signature frequency skew
distributional divergence from matched controls
```

### 2.3 Transition/path deformation

Deferred for now.

Path metrics may be recorded as optional diagnostics but should not drive classification.

## 3. Required output classes

Every candidate row should receive one support/distribution phenotype class.

Allowed primary classes:

```text
support_deformation_candidate
distribution_deformation_candidate
mixed_support_distribution_candidate
support_only_fakeout
distribution_only_fakeout
matched_control_equivalent
probe_collision_limited
support_ceiling_limited
start_local_support_deformation
basin_local_support_deformation
environment_level_support_deformation
underdetermined
```

Additional mechanism/dependency tags:

```text
constraint_dependent
asymmetry_dependent
roughness_sensitive
roughness_noise_tolerant
edge_stable
edge_brittle
outdegree_ablation_sensitive
support_matched_sensitive
probe_family_local
cross_probe_recurrent
```

## 4. Do not overfilter by destructive ablations

Keep the corrected control taxonomy.

### 4.1 Triviality controls

Use as fair filters:

```text
frontier_size_only
probe_marginal_only
frontier_size_plus_probe_marginal
```

These test whether support/distribution effects are explainable by endpoint count or global probe bias.

### 4.2 Support controls

Use to type the deformation, not reject it:

```text
signature_support_matched
horizon_local_frontier_matched
window_local_frontier_matched
```

If a candidate fails support-matched controls, classify the effect as support-dependent.

### 4.3 Mechanistic ablations

Use as mechanism probes, not must-survive gates:

```text
constraint_shuffled
asymmetry_shuffled
```

Expected meaningful relation-specific candidates may die under these.

### 4.4 Strong relation/graph ablations

Use as destructive ablation diagnostics:

```text
out_degree_preserving_random
current degree_preserving_rewire / out_degree_rewire_without_replacement
```

Report whether candidates are sensitive to generic branching randomization, but do not require survival as a primary gate.

### 4.5 Robustness perturbations

Use graded robustness:

```text
multiple starts
roughness strength/reseed profile
small relation perturbations if available
```

## 5. Multiple starts remain mandatory

Use at minimum:

```text
start_samples = 3, 8
```

Optional if cheap:

```text
start_samples = 16
```

Classify support/distribution phenotypes by start coverage:

```text
start_local
basin_local
environment_level
start_diverse
start_fragile
```

Do not strongly interpret rows without start coverage.

## 6. Probe-family handling

Do not let path-probe collision lessons disappear.

For support/distribution work, probe resolution still matters, but the bar is lower than for path metrics.

For every row, report:

```text
probe_family
probe_signature_alphabet_size
observed_signature_support_size
observed_signature_support_fraction
probe_collision_rate
support_ceiling_flag
probe_resolution_class
```

Classify whether the deformation is:

```text
probe_family_local
cross_probe_recurrent
probe_collision_limited
support_ceiling_limited
```

Use multiple probe families:

```text
existing low-resolution probes
coordinate_tuple_k3/k4 where available
constraint-profile probes
relation-role probes as diagnostics
strict-state probes only as resolution controls, not evidence probes
```

## 7. Matched controls

Every candidate row must have matched controls where possible.

Matched controls should include:

```text
matched non-candidate middle-regime environment
same-environment non-candidate window, if available
same parameter region fresh-seed environment, if available
```

Matching should use:

```text
parameter region
out-degree target
constraint density
constraint strength
asymmetry strength
reversibility fraction
roughness strength
probe family
horizon window
start_samples
```

Rows without matched controls must be marked:

```text
descriptive_only_no_matched_control
```

and cannot be promoted beyond descriptive phenotype status.

## 8. Support/distribution metrics

Compute by horizon and window.

### 8.1 Support metrics

```text
reachable_signature_support_size
reachable_signature_support_fraction
support_jaccard_vs_null
support_jaccard_vs_matched_control
support_gain_count
support_loss_count
support_symmetric_difference_fraction
support_concentration_index
```

### 8.2 Distribution metrics

```text
signature_entropy
signature_entropy_ceiling_fraction
JS_to_triviality_nulls
KL_to_triviality_nulls where safe
TV_distance_to_matched_control
Wasserstein_like_rank_distance if applicable/simple
mass_concentration_top_k
mass_shift_vs_control
```

### 8.3 Horizon/window shape

```text
support_growth_curve
support_growth_slope
support_growth_curvature
support_stabilization_H
support_saturation_H
distribution_stabilization_H
pre_saturation_deformation_score
near_saturation_deformation_score
post_saturation_deformation_score
```

### 8.4 Cross-start/cross-probe recurrence

```text
support_phenotype_recurrence_across_starts
distribution_phenotype_recurrence_across_starts
support_phenotype_recurrence_across_probe_families
distribution_phenotype_recurrence_across_probe_families
```

## 9. Candidate phenotype construction

For each row, classify:

```text
support_result:
  none / weak / support_deformation / support_fakeout

distribution_result:
  none / weak / distribution_deformation / distribution_fakeout

matched_control_result:
  candidate_exceeds_control / control_equivalent / control_exceeds_candidate / no_control

probe_result:
  usable / probe_collision_limited / support_ceiling_limited / identity_like_control

start_result:
  start_local / basin_local / environment_level / start_diverse / start_fragile

mechanism_result:
  constraint_dependent / asymmetry_dependent / roughness_sensitive / no_mechanism_signal / underdetermined
```

Then assign primary class.

Suggested rules:

```text
support_deformation_candidate:
  support_result = support_deformation
  matched_control_result = candidate_exceeds_control or control unavailable but flagged descriptive
  probe_result usable or explicitly low-resolution-descriptive

distribution_deformation_candidate:
  distribution_result = distribution_deformation
  support_result not solely explanatory
  matched_control_result = candidate_exceeds_control

mixed_support_distribution_candidate:
  both support and distribution deformation present

matched_control_equivalent:
  matched control has comparable or stronger deformation metric

probe_collision_limited:
  probe collision/support ceiling prevents interpretation

support_only_fakeout:
  support result fails triviality or matched-control filters

underdetermined:
  insufficient controls or inconsistent results
```

Do not call anything path-process-like in this run.

## 10. Regime mapping

Aggregate phenotype rates by parameter region.

Group by:

```text
out_degree_target
constraint_density
constraint_strength
constraint_change_weight
constraint_arity
asymmetry_strength
reversibility_fraction
rewire_probability
roughness_strength
update_footprint
```

Report:

```text
support_deformation_rate
distribution_deformation_rate
mixed_deformation_rate
matched_control_equivalent_rate
probe_limited_rate
start_local_rate
environment_level_rate
constraint_dependent_rate
roughness_sensitive_rate
```

The main scientific product is a deformation regime map, not a pass count.

## 11. Outputs

Required outputs:

```text
support_distribution_taxonomy_report.md
support_distribution_candidate_summary.csv
support_distribution_metric_by_horizon.csv
support_distribution_metric_by_window.csv
support_distribution_matched_controls.csv
support_distribution_probe_diagnostics.csv
support_distribution_start_recurrence.csv
support_distribution_regime_map.csv
support_distribution_fakeout_summary.csv
support_distribution_mechanism_tags.csv
status.json
```

Optional:

```text
support_growth_curves_sample.json
matched_control_examples.json
probe_family_deformation_matrix.csv
```

## 12. Suggested run shape

This should be a focused taxonomy/regime pass, not a massive atlas.

Suggested:

```text
workers: 18
wall clock: 1-3 hours
coordinate_count: 5
candidate environments: 20-40
matched controls: 20-40
start_samples: 3 and 8
horizon_grid: long_10x
probe families: existing low + k3/k4 + constraint-profile + relation-role diagnostics + strict-state controls
null_replicates: 5
roughness profile reuse if available
promotion_enabled: false for scientific gate
```

If runtime is cheap, expand breadth by:

```text
more parameter regions
more fresh seeds
more matched controls
```

rather than path metrics.

## 13. Final report requirements

The report must answer:

```text
Which support/distribution deformation phenotypes recur?
Are they start-local, basin-local, or environment-level?
Are they probe-family-local or cross-probe recurrent?
Are they explained by frontier size, probe marginals, support ceilings, or matched controls?
Which parameter regimes produce which phenotypes?
Do constraint-dominated regimes produce stable support deformation?
Do distribution effects remain after support is matched?
Which fakeout modes dominate?
Should the next empirical focus remain support/distribution, return to path metrics, or pause?
```

## 14. Decision outcomes

### 14.1 Continue support/distribution taxonomy

If:

```text
support/distribution phenotypes recur across starts/seeds/probes
matched controls are lower or different
fakeout modes are classifiable
```

Then:

```text
run a broader support/distribution regime map
write theory note tying support deformation to future-landscape shadow concept
```

### 14.2 Return to path metrics later

If:

```text
support/distribution phenotypes stabilize and probe-resolution issues improve
```

Then:

```text
revisit path-process with better probes and stricter matched controls
```

### 14.3 Pause empirical branch

If:

```text
support/distribution phenotypes collapse into fakeouts or matched-control equivalence
```

Then:

```text
write measurement-limits note and reassess substrate/probe design
```

## 15. Claim boundary

Allowed:

```text
We classified support/distribution deformation phenotypes.
A parameter regime reproducibly produces support/distribution deformation under specified controls.
A phenotype is start-local, basin-local, environment-level, probe-local, or cross-probe recurrent.
```

Not allowed:

```text
Omega detected
agency detected
identity detected
valuer detected
viability detected
path-process object detected
scientific gate passed
```

## 16. Bottom line

This branch now focuses on the first stable empirical object:

```text
support/distribution deformation in future landscapes generated from neutral relation/asymmetry/constraint substrates
```

Path metrics remain available for later, but they should not drive the next pass.
