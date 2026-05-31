# RFS-MB0 Max-Entropy Local Transition Preflight Spec

Status: draft preflight / Codex comment target  
Builds on:
- `docs/research_notes/validation_results/rfs_mb0_low_beta_preservation_sensitivity_scaleup_result.md`
- `docs/research_notes/omega_theory/transition_energy_substrate_atlas.md`
- `docs/RFS_MB0_ASYMMETRY_LADDER_TRANSITION_ENERGY_SUBSTRATE_SPEC.md`
- `docs/SPEC_FORMATTING_GUIDELINES.md`
Scope: RFS-MB0 horizon-transport / transition-energy substrate branch  
Claim boundary: substrate characterization only; no Omega, agency, value, identity, valuerhood, holdout, candidate-promotion, or graph-causality claim.

## 0. One-sentence purpose

Test whether the preservation-asymmetry response survives when preservation is moved from an explicit deterministic top-m transition-energy term into a maximum-entropy local transition ensemble with matched macro-invariant edge-marginals.

## 1. Why this spec exists

The low-beta preservation sensitivity scaleup showed that beta changes the selected transition graph before aligned response appears, with first aggregate aligned response around beta `0.05` and stronger response through `0.10-0.25`. The clean next question is whether this response is caused by the general availability of macro-invariant-preserving local transitions, or by the exact deterministic top-m geometry of the current E2 transition-energy rule.

This is a preflight. It should be narrow enough to fail informatively.

## 2. Inherited rules

Standard Omega claim boundary, 3P discipline, matched-null/perturbation separation, response taxonomy, fixture discipline, artifact policy, and graceful-run discipline apply.

Only spec-specific emphasis:

```text
Do not interpret MaxEnt response classes unless marginal-match diagnostics,
matched-marginal detector gates, paired-baseline availability, and fixture
contracts pass.
```

## 3. Core question

Primary question:

```text
If we keep local graph constraints plus a symbol-histogram `delta_I` edge-marginal,
does aligned horizon transport reappear near the beta 0.05-0.10 threshold
without deterministic top-m preservation scoring?
```

Operational contrast:

```text
deterministic E2 preservation_asymmetry:
  E(s,t) = d(s,t) + beta * |I(t)-I(s)| + roughness
  edges(s) = top_m lowest-energy local candidates

MaxEnt-P preflight:
  sample local transition graphs with matched macro constraints;
  do not rank every candidate edge by explicit preservation energy;
  audit whether the sampled edge ensemble matches the target `delta_I` marginal.
```

## 4. Objects under test

### 4.1 Shared substrate base

Use the same finite state spaces and local proposal neighborhoods as the current transition-energy branch:

```text
X:
  finite tuple state space from current RelationParams

Q(s):
  local proposal set, normally Hamming ball within update_footprint excluding s

out_degree_target:
  inherited from current comparable substrate parameters

horizon-transport runner:
  omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair
```

### 4.2 Required MaxEnt substrate families

Implement these substrate families as new transition-energy substrate options, or equivalent runner-recognized aliases:

```text
max_entropy_local:
  ME0 local maximum-entropy baseline
  constraints: local proposal kernel, out-degree, reversibility/roughness profile
  no macro-invariant marginal constraint

max_entropy_macro_invariant:
  MEP macro-invariant marginal family
  constraints: ME0 constraints plus target `delta_I` edge-marginal
```

Optional after the required preflight works:

```text
max_entropy_directional:
  MED directional marginal family
  constraints: ME0 constraints plus A(t)-A(s) edge-marginal

max_entropy_combined:
  MEC combined marginal family
  constraints: ME0 constraints plus both `delta_I` and directional edge-marginals
```

Do not block the required ME0/MEP preflight on MED/MEC.

### 4.3 Invariants

Primary invariant:

```text
symbol_histogram_distance
```

Required comparator:

```text
hamming_weight_or_nonzero_count
```

Guarded comparator only:

```text
total_coordinate_mass
```

`total_coordinate_mass` may be included only if paired-baseline availability is explicitly reported and excluded from clean-target interpretation when baseline-limited.

### 4.4 Calibration targets

Use deterministic preservation-asymmetry low-beta runs as calibration targets.

```text
equivalent_beta_target:
  0.04
  0.05
  0.075
  0.10
  0.15
```

Each `equivalent_beta_target` means: match the target `delta_I` edge-marginal induced by deterministic E2 preservation asymmetry at that beta, then sample a maximum-entropy local transition graph under that marginal constraint.

If exact beta `0.04` or `0.075` calibration is not available yet, the implementation may either run deterministic calibration jobs for those values or mark those rows `calibration_missing` and skip interpretation.

## 5. MaxEnt sampler requirements

This preflight does not need a proof-grade maximum-entropy sampler. It does need an auditable approximation whose failure modes are visible.

Acceptable implementation strategies include:

```text
conditional local edge sampling:
  sample out_degree_target edges per state from Q(s) while matching target bins;

edge-swap Markov chain:
  start from a local graph and perform swaps preserving out-degree/locality while
  driving the aggregate `delta_I` marginal toward the target;

stratified candidate sampling:
  bin candidate edges by `delta_I` and sample per-state edges to approximate the target
  aggregate marginal.
```

Required sampler diagnostics:

```text
sampler_status
sampler_seed
sampler_method
sampler_attempt_count
sampler_accepted_swap_count, if applicable
locality_violation_count
out_degree_violation_count
empty_successor_state_count
reversibility_fraction_observed
macro_invariant_delta_target_distribution
macro_invariant_delta_observed_distribution
macro_invariant_delta_match_error
edge_count
mean_out_degree
```

Interpretation guard:

```text
If macro_invariant_delta_match_error is too high or locality/out-degree
constraints fail, response rows remain diagnostic only.
```

Use a conservative initial tolerance. Suggested preflight threshold:

```text
macro_invariant_delta_match_error_max: 0.10
```

Codex may propose a better bounded metric, but the retained output must make the tolerance explicit.

## 6. Required run shape

### 6.1 Phase 0: implementation smoke

Purpose: verify sampler, metadata, outputs, and fixture compatibility before a full preflight.

Suggested shape:

```text
substrate_families:
  max_entropy_local
  max_entropy_macro_invariant

macro_invariant_kind:
  symbol_histogram_distance

equivalent_beta_target:
  0.05
  0.10

groups:
  small smoke subset

fresh_seeds_per_group:
  1

start_samples_list:
  2

null_replicates:
  5

selected_edge_overlap_sample_jobs:
  24
```

Smoke must also run the usual fixture smoke path before empirical response interpretation.

### 6.2 Phase 1: narrow preflight

Suggested first interpretable preflight:

```text
substrate_families:
  locality_only
  preservation_asymmetry
  max_entropy_local
  max_entropy_macro_invariant
  constraint_template_current comparator

macro_invariant_kind:
  symbol_histogram_distance
  hamming_weight_or_nonzero_count

equivalent_beta_target:
  0.04
  0.05
  0.075
  0.10
  0.15

perturbation strengths:
  0.006
  0.010
  0.015
  0.020

start_samples_list:
  2,4

null_replicates:
  9
```

Use H128-compatible horizon pairs unless compute pressure forces a smaller horizon smoke. If horizon coverage is reduced, label the run as a reduced-horizon smoke and do not compare directly to the low-beta scaleup threshold.

### 6.3 Optional Phase 2

Only after Phase 1 passes sampler/marginal/paired-baseline diagnostics:

```text
add:
  total_coordinate_mass with paired-baseline guards;
  max_entropy_directional;
  max_entropy_combined;
  stronger beta-equivalent threshold refinement around the first MaxEnt response.
```

## 7. Probes and flow modes

Primary probes should be grammar-neutral:

```text
full_state_hash
relation_role
```

If the current runner does not support these cleanly for all transition-energy substrates, Codex should comment before substituting older constraint-template-specific probes.

Constraint-template-specific probes may be retained only for the `constraint_template_current` comparator and should not drive MaxEnt interpretation.

Required flow modes remain the current horizon-transport flow modes. Report any backward-compatible aliases used by the runner.

## 8. Controls, nulls, and audits

Required detector-null families are inherited from the horizon-transport runner:

```text
context_shuffle_transport_null
horizon_pair_shuffle_transport_null
row_marginal_matched_transport_null
column_marginal_matched_transport_null
row_column_marginal_matched_transport_null
```

Required MaxEnt-specific audits:

```text
max_entropy_constraint_manifest.csv
max_entropy_marginal_match_summary.csv
max_entropy_sampler_diagnostics.csv
response_by_max_entropy_family.csv
response_by_equivalent_beta_target.csv
paired_baseline_availability_by_max_entropy_variant.csv
```

Continue retaining:

```text
selected_edge_overlap_by_beta.csv
horizon_transport_matched_marginal_summary.csv
horizon_transport_detector_null_gate_results.csv
horizon_transport_response_classification.csv
response_class_by_strength_and_horizon_pair.csv
horizon_response_threshold_table.csv
```

The selected-edge audit may be generalized to compare sampled MaxEnt graphs against their deterministic E2 calibration graph. If generalized, name the new artifact clearly rather than overloading the beta table silently.

Suggested new artifact:

```text
max_entropy_edge_match_to_calibration.csv
```

## 9. Required outputs

All standard horizon-transport runner outputs remain required.

Additional retained outputs:

```text
max_entropy_constraint_manifest.csv
max_entropy_marginal_match_summary.csv
max_entropy_sampler_diagnostics.csv
max_entropy_edge_match_to_calibration.csv
response_by_max_entropy_family.csv
response_by_equivalent_beta_target.csv
paired_baseline_availability_by_max_entropy_variant.csv
```

Final result note path:

```text
docs/research_notes/validation_results/rfs_mb0_max_entropy_local_transition_preflight_result.md
```

Local output path:

```text
results/local_runs/<YYYYMMDD>_max_entropy_local_transition_preflight/
```

## 10. Decision rules

Continue / expand MaxEnt-P if:

```text
ME0 remains non-aligned or baseline-like;
MEP produces aligned response near the calibrated beta 0.05-0.10 region;
matched-marginal detector gates pass;
fixture contract passes;
macro-invariant marginal match is within tolerance;
paired-baseline availability is clean for the interpreted rows;
symbol_histogram_distance is the cleanest or tied-clean target.
```

Demote or narrow preservation-asymmetry if:

```text
ME0 produces comparable aligned response to MEP;
random/local MaxEnt structure explains the response without macro-invariant
marginal constraints;
shuffled or nonmeaningful invariant marginals reproduce the response;
response disappears after marginal/paired-baseline repair.
```

Mark deterministic top-m geometry as loadbearing if:

```text
deterministic preservation_asymmetry reproduces the low-beta threshold;
MEP matches the `delta_I` marginal successfully;
MEP does not produce aligned response under otherwise comparable conditions.
```

Repair before interpreting if:

```text
macro_invariant_delta_match_error exceeds tolerance;
locality or out-degree constraints fail;
matched-marginal detector gates fail;
fixture contract fails;
paired-baseline availability differs systematically by MaxEnt family;
MaxEnt rows become measurement-limited at the key horizon pairs.
```

Pause this branch if:

```text
no sampler can produce acceptable local graphs with matched marginals;
ME0, MEP, and deterministic E2 all become control-equivalent under the same
controls;
compute cost exceeds the value of the preflight relative to simpler substrate
repairs.
```

## 11. Next-action forks

The result note should emit exactly one:

```text
expand_max_entropy_macro_invariant_family
repair_max_entropy_sampler
repair_max_entropy_paired_baselines
demote_preservation_asymmetry_to_top_m_artifact
continue_deterministic_preservation_threshold_mapping
pause_max_entropy_branch
```

No fork may directly open holdout, graph perturbation, candidate promotion, or Omega/agency/value claims.

## 12. Codex comment targets before running

Codex should comment on these before executing a full preflight:

```text
1. Which MaxEnt sampler strategy is simplest and least artifact-prone in the
   current codebase?

2. Can the sampler preserve locality and out-degree exactly while matching `delta_I`
   marginals well enough for interpretation?

3. What metric should define macro_invariant_delta_match_error?

4. Should equivalent beta targets be calibrated on the fly or loaded from a
   deterministic calibration run?

5. Are full_state_hash and relation_role available and grammar-neutral for all
   required families? If not, what is the least-bad probe substitution?

6. What is the smallest smoke that exercises all new outputs and failure modes?

7. What run shape keeps the first interpretable preflight within reasonable
   desktop runtime?
```

## 13. Non-goals

This spec does not:

```text
open holdout scoring;
open graph-channel causality;
introduce agent, value, valuerhood, identity, life, or Omega labels;
claim maximum-entropy substrate generality;
replace the horizon-transport instrument;
add new hand-built semantic substrate laws;
interpret total_coordinate_mass without paired-baseline guards;
return to high-beta saturation studies.
```

## 14. 3P check

Principled:

```text
Tests whether macro-invariant preservation survives when moved from an explicit
energy term to an ensemble-level constraint under the same horizon-transport
instrument.
```

Parsimonious:

```text
Keeps locality, out-degree, reversibility/roughness profile, and one
macro-invariant marginal; removes deterministic top-m preservation scoring from
the target family.
```

Predictive:

```text
ME0 amplification demotes preservation or exposes weak controls.
MEP-only amplification strengthens preservation as a substrate-level ingredient.
Deterministic-only amplification identifies top-m transition-energy geometry as
loadbearing.
Sampler or paired-baseline failure blocks interpretation and forces repair.
```
