# RFS-MB0 Horizon-Transport Viscosity / Horizon / Breadth Sweep Spec

Status: small set of design-set sweeps after H128 aligned-amplification result
Builds on: `docs/research_notes/omega_theory/horizon_transport_aligned_amplification.md` and `docs/research_notes/validation_results/rfs_mb0/rfs_mb0_horizon_transport_response_surface_h128_scaleup_result.md`
Claim boundary: no holdout scoring, no candidate promotion, no Omega detection, no agency detection, no identity detection, no valuer detection

## 0. One-sentence purpose

Probe whether the current matched-marginal-separated horizon-transport object is a low-complexity, high-viscosity aligned amplifier; a horizon-scale-mismatched precursor whose richer response appears only at longer horizons; or a substrate-breadth-limited object channeled through too narrow a design space.

Plainly:

```text
Do we have a simple transport amplifier because that is all the substrate can produce,
or because our current horizon / breadth / perturbation view is too narrow?
```

## 1. Background

The H128 response-surface scaleup produced the cleanest empirical object in the branch so far:

```text
matched-marginal-separated horizon transport;
full H128 coverage;
no terminal saturation flags;
stable short horizons;
amplified-aligned middle/deep horizons;
first amplified horizon moves earlier as perturbation strength rises;
no empirical weakened / rerouted / reopened / collapsed rows.
```

This supports a theory/instrument update but also raises a new concern:

```text
The detected structure may be simple.
It may be more like transport amplification or prebiotic/self-replicator-like persistence
than life-like adaptive regulation.
```

Possible explanations:

```text
substrate_viscosity:
  perturbation changes mass but not route identity; high alignment persists and response taxonomy stays simple

horizon_scale_mismatch:
  richer response classes appear only beyond H128 or at different horizon spacing

substrate_breadth_limitation:
  current focused selection channels the substrate through a narrow design region, suppressing response diversity

instrument_resolution_limit:
  richer dynamics exist but current response classes / probes / flow modes cannot resolve them

true_low_complexity_object:
  the substrate currently supports aligned amplification but not adaptive regulation
```

This spec defines a small set of sweeps to distinguish these possibilities without opening validation claims.

## 2. Claim boundary

Allowed claims:

```text
horizon transport does or does not remain interpretable out to a 10x horizon extension;
terminal saturation does or does not dominate long horizons;
response diversity does or does not increase with horizon, perturbation strength, or substrate breadth;
transport viscosity appears high, medium, low, or unresolved under the tested settings;
substrate breadth does or does not reveal more response classes;
this branch is or is not ready for further horizon-transport work.
```

Forbidden claims:

```text
Omega detected;
agent detected;
valuer detected;
identity detected;
life detected;
self-replication detected;
candidate promoted;
holdout ready;
graph-channel causality shown.
```

Required counters:

```text
holdout_scoring_count: 0
n6_run_count: 0
alphabet_expansion_count: 0
candidate_promotion_enabled: false
```

## 3. Sweep set overview

Run a small set of complementary sweeps.

```text
Sweep A: 10x Horizon Extension
  Ask whether richer response appears beyond H128, up to roughly H1280.

Sweep B: Substrate Breadth / Breathing Room
  Ask whether broader design-set diversity exposes richer response classes.

Sweep C: Viscosity / Response Ladder
  Ask whether stronger but still classified perturbations produce weakening, rerouting, reopening, or collapse.

Optional Sweep D: Breadth-Horizon Cross Mini
  Run only if A and B are both promising or ambiguous.
```

Do not combine every axis into one large undiagnosable run.

## 4. Required shared controls and outputs

All sweeps must preserve the current control architecture.

Required detector-null families:

```text
context_shuffle_transport_null
horizon_pair_shuffle_transport_null
row_marginal_matched_transport_null
column_marginal_matched_transport_null
row_column_marginal_matched_transport_null
```

Required detector statistic:

```text
marginal_residual_fraction
```

Required response classes:

```text
transport_stable
transport_amplified_aligned
transport_weakened
transport_rerouted
transport_reopens
transport_collapses
transport_control_equivalent
transport_resolution_mismatch
transport_response_underpowered
```

Required diagnostics:

```text
terminal_saturation_flag
horizon_pair_undercoverage_flag
latest_interpretable_horizon
first_nonstable_horizon
first_amplified_aligned_horizon
first_weakened_horizon
first_rerouted_horizon
first_reopened_horizon
first_collapsed_horizon
transport_viscosity_score
response_diversity_score
```

Generated CSV/JSON outputs remain local-only under `results/local_runs/`.

## 5. New diagnostic: transport viscosity

Add a compact viscosity diagnostic for each context and aggregate.

Working intuition:

```text
High viscosity:
  perturbations change mass but preserve alignment and do not produce response-class diversity.

Medium viscosity:
  aligned amplification appears first, then weakening / rerouting / reopening / collapse appears at higher perturbation or longer horizon.

Low viscosity:
  response classes change quickly, possibly noisily or destructively.
```

Suggested fields:

```text
probe_key
flow_mode
horizon_pair
condition_id
perturbation_family
perturbation_strength
mean_alignment
mass_delta_fraction
entropy_delta
subspace_rotation
response_class
response_class_diversity_by_context
first_nonstable_horizon
first_non_amplified_response_horizon
latest_interpretable_horizon
terminal_saturation_flag
transport_viscosity_score
transport_viscosity_read
```

Allowed viscosity reads:

```text
high_viscosity_aligned_amplifier
medium_viscosity_response_threshold
low_viscosity_unstable_response
terminal_saturation_limited
underpowered_or_unresolved
```

A simple first-pass score may combine:

```text
high alignment persistence;
low response-class diversity;
low subspace rotation;
low entropy response;
absence of weakening/rerouting/reopening/collapse.
```

## 6. Sweep A: 10x Horizon Extension

### 6.1 Purpose

Test horizon-scale mismatch directly.

Question:

```text
Do richer response classes appear when horizon is extended roughly 10x beyond H128,
or does aligned amplification persist as the dominant response until saturation?
```

### 6.2 Horizon design

Use logarithmic / sparse horizon pairs to control compute.

Required continuation from H128:

```text
128->256
256->512
512->1024
1024->1280
```

Include reference pairs from the previous run:

```text
16->24
24->32
64->96
96->128
```

Optional aggregate pairs if feasible:

```text
128->512
512->1280
32->128
128->1280
```

### 6.3 Suggested shape

```text
groups: 24 to 36
design_groups: 8 to 12
fresh_seeds_per_group: 4
start_samples_list: 4,8,16
null_replicates: 9 or 11
perturbation families:
  small_edge_resample_control
  asymmetric_edge_flip_control
perturbation strengths:
  0.006,0.015,0.030
optional boundary strength:
  0.040 if already implemented as boundary_probe
```

This sweep should prioritize horizon reach over breadth.

### 6.4 Decision reads

```text
horizon_scale_mismatch_live:
  richer response classes appear beyond H128 without terminal saturation

simple_aligned_amplifier_persists:
  aligned amplification remains dominant through long horizons without saturation

terminal_saturation_limits_long_horizon:
  long horizons saturate or undercover before richer response appears

long_horizon_detector_null_failure:
  matched marginal nulls fail at extended horizons
```

## 7. Sweep B: Substrate Breadth / Breathing Room

### 7.1 Purpose

Test whether the substrate is being channeled through too narrow a design selection.

Question:

```text
Does expanding design-set breadth reveal response diversity that the focused H128 selection suppressed?
```

### 7.2 Breadth expansion

Expand design breadth before changing primitives.

Recommended:

```text
groups: 64 to 128 if available
design_groups: 24 to 40
fresh_seeds_per_group: 6 to 8
start_samples_list: 2,4,8,16,32
null_replicates: 9 or 11
```

Include a broader selection policy if available:

```text
focused recurrent groups;
weak control-bundle recurrence groups;
collision-limited but nondegenerate groups;
high entropy / high transport support groups;
low but nonzero A/C residue groups;
```

Do not add semantic labels.

### 7.3 Horizon design

Keep horizons more modest than Sweep A:

```text
0->1
1->2
2->4
4->8
8->16
16->24
24->32
32->48
48->64
64->96
96->128
```

### 7.4 Perturbation design

Use a compact ladder:

```text
0.006
0.010
0.015
0.020
0.030
```

for:

```text
small_edge_resample_control
asymmetric_edge_flip_control
```

### 7.5 Required breadth diagnostics

```text
design_group_diversity_summary.csv
substrate_transport_capacity_summary.csv
response_diversity_by_group_class.csv
response_diversity_by_start_count.csv
response_diversity_by_design_group.csv
```

Suggested metrics:

```text
reachable_support_growth
frontier_support_size
transport_entropy
transport_branch_count
row/column support size
matched_marginal_residual_strength
response_class_diversity
first_nonstable_horizon_distribution
```

### 7.6 Decision reads

```text
breadth_unmasks_response_diversity:
  broader design selection produces weakened/rerouted/reopened/collapsed classes

breadth_preserves_aligned_amplifier:
  broader design selection remains mostly stable/amplified-aligned

substrate_capacity_low:
  broader groups still have low support/diversity and few branches

instrument_resolution_limit_possible:
  substrate capacity metrics are high but response taxonomy remains simple
```

## 8. Sweep C: Viscosity / Response Ladder

### 8.1 Purpose

Probe whether aligned amplification is only the first phase before weakening, rerouting, reopening, or collapse.

Question:

```text
As perturbation strength rises, does the response transition from stable -> amplified -> differentiated response,
or does it remain high-alignment mass growth until saturation/collapse?
```

### 8.2 Horizon focus

Use horizons where amplification already appeared, plus longer diagnostic horizons:

```text
4->8
8->16
16->24
24->32
64->96
96->128
```

Optional if Sweep A is implemented first:

```text
128->256
256->512
```

### 8.3 Perturbation ladder

Use finer and stronger ladder.

```text
0.006
0.008
0.010
0.012
0.015
0.020
0.030
0.040
0.060
0.080
0.100
```

Label strengths by interpretation role:

```text
0.006 to 0.030:
  nonlethal_perturbation unless evidence says otherwise

0.040 and above:
  boundary_probe by default
  viability_boundary_mapping only
```

### 8.4 Perturbation families

Required:

```text
small_edge_resample_control
asymmetric_edge_flip_control
```

Optional if already cleanly implemented and named:

```text
out_degree_preserving_rewire
constraint_weight_jitter
support_preserving_target_resample
```

Do not introduce a new perturbation family without honest preservation metadata.

### 8.5 Decision reads

```text
aligned_amplification_precedes_differentiation:
  higher strengths reveal weakening/rerouting/reopening/collapse after amplified phase

high_viscosity_persists:
  response remains stable/amplified with high alignment across the ladder

boundary_collapse_without_differentiation:
  response jumps from amplified to collapse without rerouting/reopening

perturbation_family_specific_response:
  edge resampling and asymmetric flips produce different thresholds or classes
```

## 9. Optional Sweep D: Breadth-Horizon Cross Mini

Run only if Sweep A and Sweep B are both promising or ambiguous.

Purpose:

```text
Check whether long-horizon response diversity requires broader substrate selection.
```

Suggested minimal cross:

```text
groups: 64
design_groups: 16
fresh_seeds_per_group: 4
start_samples_list: 4,16
horizons: 96->128,128->256,256->512,512->1024
strengths: 0.006,0.015,0.030
null_replicates: 9
```

## 10. Run order and stop rules

Recommended order:

```text
1. Sweep A: 10x Horizon Extension
2. Sweep B: Substrate Breadth / Breathing Room
3. Sweep C: Viscosity / Response Ladder
4. Optional Sweep D only if needed
```

Stop or repair if:

```text
matched marginal detector nulls fail globally;
terminal saturation dominates all extended horizons;
coverage falls below interpretability threshold;
fixture response classes fail after runner changes;
errors or job accounting become inconsistent.
```

If a sweep is very cheap, do not automatically over-scale it. Prefer completing all three sweeps so the hypotheses can be compared.

## 11. Required output bundle

Each sweep should emit a retained note under:

```text
docs/research_notes/validation_results/
```

Suggested result names:

```text
rfs_mb0_horizon_transport_10x_horizon_sweep_result.md
rfs_mb0_horizon_transport_breadth_sweep_result.md
rfs_mb0_horizon_transport_viscosity_ladder_result.md
rfs_mb0_horizon_transport_breadth_horizon_cross_mini_result.md
```

Required summaries:

```text
executive_summary
claim_boundary
run_shape
matrix_coverage
matched_marginal_null_results
terminal_saturation_results
response_class_by_strength_and_horizon
horizon_response_threshold_table
transport_viscosity_summary
response_diversity_summary
substrate_capacity_summary if applicable
next_action_fork
output_manifest
```

A final combined comparison note is recommended after all completed sweeps:

```text
rfs_mb0_horizon_transport_viscosity_horizon_breadth_sweep_synthesis.md
```

## 12. Next-action forks

Each sweep emits one fork:

```text
extend_horizon_scale
expand_substrate_breadth
probe_viscosity_boundary
repair_detector_or_response_taxonomy
compare_resolution_views
write_low_complexity_amplifier_note
write_measurement_limits_note
pause_horizon_transport_branch
```

The synthesis note emits one combined fork:

```text
continue_horizon_transport_response_surface
switch_to_resolution_or_scale_view
return_to_direct_channel_diagnostics
write_replicator_like_transport_amplifier_note
write_measurement_limits_note
```

No fork may open holdout, graph perturbation, direct channel causality, candidate promotion, or Omega/agency/value claims directly.

## 13. Interpretation guide

### 13.1 If Sweep A finds richer classes only beyond H128

Interpretation:

```text
horizon-scale mismatch was live;
H128 was too short for richer response.
```

Next:

```text
focus on long-horizon response thresholds;
keep saturation gates central.
```

### 13.2 If Sweep B finds richer classes with broader substrate selection

Interpretation:

```text
focused selection channeled the substrate too narrowly;
breadth matters for response diversity.
```

Next:

```text
build broader design-set atlas;
avoid overfitting to focused recurrence groups.
```

### 13.3 If Sweep C finds amplified -> differentiated transition

Interpretation:

```text
aligned amplification may be an early phase of richer response.
```

Next:

```text
map response thresholds;
consider functional perturbation only after clear differentiation.
```

### 13.4 If all sweeps preserve stable/amplified only

Interpretation:

```text
current substrate may support a low-complexity transport amplifier but not adaptive regulation;
self-replicating-molecule analogy becomes more plausible than life analogy.
```

Next:

```text
write low-complexity amplifier note;
consider scale/resolution changes or substrate redesign.
```

### 13.5 If terminal saturation dominates

Interpretation:

```text
long-horizon instrument range exceeded useful horizon;
H beyond saturation is not informative.
```

Next:

```text
trim horizon range;
work below latest interpretable horizon;
repair saturation-aware metrics.
```

## 14. 3P check

### Principled

The sweeps directly test the three live explanations raised by the H128 result: horizon mismatch, substrate breadth limitation, and transport viscosity.

### Parsimonious

Only one live object is used: directional horizon transport. The sweeps vary horizon, breadth, and perturbation strength without adding semantic labels.

### Predictive

Each hypothesis has a distinct expected pattern:

```text
horizon mismatch:
  richer response appears only at longer horizons

breadth limitation:
  richer response appears only with broader substrate selection

high viscosity / low complexity:
  stable/amplified-aligned responses persist across horizon, breadth, and perturbation ladders
```

## 15. Bottom line

This sweep set asks:

```text
Is the current object merely a simple aligned transport amplifier,
or have we not yet given the substrate enough horizon, breadth, or perturbation range to show richer dynamics?
```

No result from these sweeps is an Omega, agency, value, identity, or life claim.
