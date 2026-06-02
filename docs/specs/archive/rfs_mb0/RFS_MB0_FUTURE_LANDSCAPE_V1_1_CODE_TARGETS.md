# RFS-MB0 Future Landscape v1.1 Code Targets

Status: Codex implementation target after detector v1 smoke

Purpose: clarify exactly what the code needs next. This is not a theory expansion. This is a detector/null hardening pass.

## 0. Current state

The detector v1 smoke made real progress:

```text
v0 broad overcall reduced
random_relation_control no longer called structured_propagation
structured_relation / expanding_relation withheld as saturation_dominated
simple controls still separate correctly
```

Remaining failure:

```text
degree_preserving_control still produces some structured_propagation calls
```

This is narrower than v0, but still blocks the scientific gate.

The current issue is not compute scale.

The current issue is:

```text
profile-level false positives under strong matched controls
```

## 1. Do not tune thresholds first

Do not simply change:

```text
control_relative_pass_count >= 3
```

to another number.

That would be detector tuning.

Instead, change the decision structure so isolated profile-level passes cannot promote a family/control to structured_propagation.

## 2. Separate local candidate from aggregate decision

Add two levels of classification:

```text
local_profile_class_v1_1
aggregate_family_class_v1_1
```

Optional third level:

```text
aggregate_probe_family_class_v1_1
```

### 2.1 Local profile class

Per-profile classification may keep a permissive label such as:

```text
local_structured_candidate
```

This means only:

```text
this individual probe/start/system profile passed local control-relative checks
```

It must not be summarized as a scientific pass.

### 2.2 Aggregate family class

A family can be labeled:

```text
structured_propagation
```

only if the aggregate family-level readout passes.

A few passing profiles inside a family must not be sufficient.

## 3. Required family-level aggregation

Add a family/probe-family aggregation pass after all profiles are computed.

Group by:

```text
family
probe_family
```

and by:

```text
family
```

For each group, compute:

```text
n_profiles
local_candidate_fraction
saturation_dominated_fraction
null_mimic_fraction
mean_transition_MI
mean_MI_delta_vs_null
mean_motif_delta_vs_null
mean_JS_bundle
mean_KL_bundle
mean_reach_saturation_fraction
mean_exact_saturation_fraction
mean_signature_transition_motif_reuse
mean_signature_transition_conditional_entropy
```

Also compute robust summaries:

```text
median_MI_delta_vs_null
median_motif_delta_vs_null
lower_quartile_MI_delta_vs_null
lower_quartile_motif_delta_vs_null
```

The robust summaries matter because a few outlier probes should not carry the family.

## 4. Aggregate pass rule

Add a conservative aggregate rule. Example starting rule:

```text
aggregate_family_class_v1_1 = structured_propagation only if:

1. saturation_dominated_fraction < 0.25
2. local_candidate_fraction >= 0.50
3. mean_MI_delta_vs_null > 0.05
4. median_MI_delta_vs_null > 0.00
5. mean_motif_delta_vs_null > 0.02
6. at least two probe families pass their own aggregate checks
7. family is not one of the declared null/control families
```

If this rule is too strict, return:

```text
underdetermined
```

Do not relax it to make structured_relation pass in this smoke.

The purpose is diagnostic clarity.

## 5. Degree-control guardrail

Add an explicit guardrail:

```text
If degree_preserving_control has any aggregate_probe_family_class_v1_1 = structured_propagation,
then detector v1.1 scientific gate fails.
```

A few local profile candidates inside degree_preserving_control may be reported, but they must not promote the family or probe-family aggregate.

Report them as:

```text
degree_control_local_false_positive_count
```

and:

```text
degree_control_local_false_positive_fraction
```

## 6. Saturation guardrail

Current v1 correctly labels saturated families as saturation_dominated.

Keep and harden this.

A family with:

```text
mean_reach_saturation_fraction >= 0.95
```

or:

```text
saturation_dominated_fraction >= 0.50
```

must not receive aggregate structured_propagation.

It should be:

```text
saturation_dominated
```

or:

```text
underdetermined_saturated
```

This is why current structured_relation and expanding_relation should not pass yet.

## 7. Add matched nulls that target the remaining failure

The current null bundle includes:

```text
degree
random
probe_marginal
```

Add at least one of:

```text
frontier_size_preserving_null
saturation_matched_null
degree_plus_probe_marginal_null
```

Preferred order:

### 7.1 frontier_size_preserving_null

For each observed `(system, start, H, probe)`, create expected signature counts by drawing from global/probe marginals with the same exact frontier size.

This is similar to probe_marginal, but should be explicit and reported as frontier-size preserving.

### 7.2 saturation_matched_null

For saturated systems, compare only to nulls with similar reach saturation / exact saturation.

If matched saturated nulls are not available, do not classify saturated profiles as structured.

### 7.3 degree_plus_probe_marginal_null

Construct a null that preserves degree-scrambled graph structure and expected probe marginals.

This is specifically aimed at the degree-preserving false positive.

If implementation time is limited, add `frontier_size_preserving_null` first and expose the columns. Do not overbuild.

## 8. Probe-family balance

The v1 smoke shows probe families differ strongly.

Do not let one probe family dominate the aggregate decision.

Add per-probe-family pass reports:

```text
projection
ordered_pair
pair_relation
pairwise_modular_difference
pairwise_equality_indicator
pairwise_unordered_multiset
```

Aggregate structured_propagation should require support from at least two distinct non-control probe families.

If only `ordered_pair` passes, label:

```text
probe_family_concentrated
```

or:

```text
underdetermined_probe_concentrated
```

## 9. Output files to add

Add:

```text
aggregate_family_classes.csv
aggregate_probe_family_classes.csv
degree_control_false_positives.csv
matched_null_summary.csv
```

Keep:

```text
control_relative_profile_classes.csv
null_bundle_summary.csv
transition_information.csv
saturation_summary.csv
summary.md
status.json
```

## 10. Summary.md required sections

Add these sections to `summary.md`:

```text
## v1.1 Aggregate Family Classes
```

Columns:

```text
family
aggregate_family_class_v1_1
n_profiles
local_candidate_fraction
saturation_dominated_fraction
mean_MI_delta_vs_null
median_MI_delta_vs_null
mean_motif_delta_vs_null
median_motif_delta_vs_null
passing_probe_family_count
```

```text
## v1.1 Probe-Family Classes
```

Columns:

```text
family
probe_family
aggregate_probe_family_class_v1_1
n_profiles
local_candidate_fraction
mean_MI_delta_vs_null
mean_motif_delta_vs_null
```

```text
## Degree-Control False Positive Audit
```

Columns:

```text
family
probe_family
local_false_positive_count
local_false_positive_fraction
aggregate_pass
```

```text
## Matched Null Summary
```

Columns:

```text
family
null_name
mean_JS
mean_KL
mean_MI_delta
mean_motif_delta
```

## 11. Expected v1.1 outcome

It is acceptable, and maybe likely, that v1.1 returns:

```text
no aggregate structured_propagation pass
```

That is not a failure if the report is clearer.

The desired improvement is:

```text
local profile false positives are visible but cannot promote controls
saturated families are withheld
family-level decisions are conservative
remaining failure mode is explicit
```

## 12. Gate condition

Scientific gate remains not passed unless:

```text
1. no declared null/control family receives aggregate structured_propagation
2. at least one non-control, non-saturated family receives aggregate structured_propagation
3. the pass is supported by at least two independent probe families
4. the pass separates from degree, random, and frontier/probe-marginal nulls
```

If those do not occur, report:

```text
implementation passed; scientific gate not passed
```

## 13. Do not add

Do not add:

```text
agents
identities
viable paths
resource/cost coordinates
support/recover/degrade labels
lattice/sheaf machinery
large scaling run
```

This is a hardening pass only.

## 14. Bottom line

What the code needs now:

```text
Do not tune the detector.
Add aggregation.
Add null matching for degree/frontier/saturation artifacts.
Prevent local profile false positives from becoming family-level claims.
Make the summary expose exactly why the gate does or does not pass.
```
