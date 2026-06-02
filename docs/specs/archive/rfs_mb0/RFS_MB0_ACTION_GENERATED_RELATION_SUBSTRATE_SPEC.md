# RFS-MB0 Action-Generated Relation Substrate Spec

Status: implementation spec

Purpose: replace hand-picked future-landscape relation families with neutral, parameter-generated relation substrates derived from the primitive triad.

This is not a new detector pass. It is an environment/substrate design pass.

## 0. Motivation

The current RFS-MB0 future-landscape detector is methodologically healthier than the first smoke:

```text
v1.1 prevents local profile hits from becoming family-level claims
long-horizon audit shows H16 was not simply too short
controls no longer promote aggregate structure
scientific gate remains not passed
```

The current blocker is now substrate/environment design.

The current relation families are still too hand-picked:

```text
structured_relation
expanding_relation
contracting_relation
cyclic_relation
phase_cycle_control
fixed_point_control
```

Even though these names are less semantic than older alive/repair/harm toy substrates, they still encode expected roles.

The next substrate should not contain a named positive family.

Instead, generate relation environments from neutral primitive parameters, then let the future-landscape detector classify them after the fact.

## 1. Core principle

Start only from:

```text
distinction
relation
asymmetry
```

Do not define:

```text
agent
valuer
identity
viability
goal
reward
support
harm
recovery
degradation
Omega-like
structured-positive family
```

The implementation should generate neutral finite relational worlds and ask:

```text
Which regions of primitive relation-parameter space produce nontrivial
future-landscape profiles above matched nulls?
```

not:

```text
Does the hand-named structured_relation pass?
```

## 2. High-level design

Create a new generator module, either:

```text
omega/rfs_mb0_future_landscape/relation_generator.py
```

or a new package:

```text
omega/rfs_mb0_relation_atlas/
```

Preferred first step: add a generator module inside the existing future-landscape package so the existing detector, nulls, and long-horizon audit can be reused.

The generated substrate should expose the same interface as current `LandscapeSystem`:

```text
system_id
seed
family or generator_id
states
edges
transform_names or generator_metadata
metadata
```

But do not use semantic family names. Use parameterized IDs:

```text
relgen_n6_a3_r1_m2_cd0.30_cs2.00_k4_rev0.20_rw0.02_seed123
```

## 3. Distinction space parameters

The finite distinction space is:

```text
X = A^n
```

where:

```text
n = coordinate_count
A = finite alphabet
```

Initial sweep values:

```text
coordinate_count n: 5, 6, 8
alphabet_size |A|: 3, 4
```

Avoid exploding state count in the first pass.

Example state counts:

```text
3^5 = 243
3^6 = 729
4^5 = 1024
4^6 = 4096
```

Suggested initial calibration:

```text
n = 5 or 6
alphabet_size = 3
```

Only expand if exact computation remains cheap enough.

## 4. Local neighborhoods

Define coordinate neighborhoods mechanically.

Use ring topology first:

```text
coordinates: 0, 1, ..., n-1
neighborhood_radius r
N_i = {i-r, ..., i, ..., i+r} mod n
```

Parameters:

```text
neighborhood_radius: 1, 2
```

No coordinate should have semantic meaning.

If phase/history coordinates are introduced later, they must be generated mechanically and clearly marked as presentation features, not agents or clocks.

For this first relation-atlas pass, avoid dedicated phase coordinates unless needed for comparison with current substrate.

## 5. Candidate transitions

For each state `x`, candidate successor states `y` are local modifications of `x`.

Parameter:

```text
update_footprint m
```

Definition:

```text
candidate y is allowed for scoring if HammingDistance(x, y) <= m
```

Initial values:

```text
m: 1, 2
```

Optional optimization:

Generate candidates by choosing up to `m` coordinates and assigning new alphabet values.

Do not consider all states as candidates unless state count is tiny.

## 6. Neutral local constraints

Generate a set of local constraints mechanically from seed and parameters.

A local constraint applies to a neighborhood or coordinate subset.

Constraint families may include:

```text
local_forbidden_pattern
local_modular_sum_preference
local_equality_relation
local_difference_relation
local_transition_table
```

These are neutral mathematical forms, not semantic conditions.

Parameters:

```text
constraint_count
constraint_density
constraint_arity
constraint_strength
constraint_scope_radius
```

Suggested initial sweep:

```text
constraint_arity: 2, 3
constraint_density: 0.10, 0.25, 0.40
constraint_strength: 0.5, 1.0, 2.0, 4.0
```

Each generated constraint must be serialized in metadata so runs are reproducible.

Example metadata entry:

```json
{
  "constraint_type": "local_modular_sum_preference",
  "coordinates": [0, 1, 2],
  "modulus": 3,
  "preferred_residue": 1,
  "weight": 2.0
}
```

Do not name constraints as viable, preserving, harmful, supportive, etc.

## 7. Action functional

Instead of hand-listing transformations, define an action-like neutral score over candidate transitions:

```text
A(x, y) =
  alpha * local_change_penalty(x, y)
+ beta  * local_constraint_violation(y)
+ gamma * constraint_change_penalty(x, y)
+ delta * nonlocality_penalty(x, y)
+ eta   * asymmetry_term(x, y)
+ rho   * random_roughness_term(x, y)
```

All terms must be neutral.

### 7.1 local_change_penalty

Basic Hamming cost:

```text
local_change_penalty(x, y) = HammingDistance(x, y)
```

This is not resource cost. It is local relation geometry.

### 7.2 local_constraint_violation

Sum of violated local constraints in the candidate successor state `y`:

```text
local_constraint_violation(y) = sum_k weight_k * violation_k(y)
```

### 7.3 constraint_change_penalty

Penalty for changing the constraint-satisfaction profile too abruptly:

```text
constraint_change_penalty(x, y) = distance(C(x), C(y))
```

where `C(x)` is the vector of local constraint evaluations.

This encourages persistent local rule structure without defining persistence semantically.

### 7.4 nonlocality_penalty

For the first pass, this can be zero if candidate transitions are already restricted by Hamming footprint.

If implemented:

```text
nonlocality_penalty = spread of modified coordinates
```

### 7.5 asymmetry_term

A seed-generated directional bias over states or local signatures.

Examples:

```text
asymmetry_term(x, y) = bias(y) - bias(x)
```

or:

```text
asymmetry_term(x, y) = local_potential_delta(x, y)
```

Important: this is not a value/reward function. It is a neutral way to generate directed relation asymmetry.

Parameters:

```text
asymmetry_strength
asymmetry_smoothness
```

Initial values:

```text
asymmetry_strength: 0.0, 0.25, 0.5, 1.0
```

### 7.6 random_roughness_term

Small seeded perturbation to avoid excessive symmetry:

```text
rho * epsilon(x, y)
```

Parameters:

```text
roughness_strength: 0.0, 0.01, 0.05
```

## 8. Edge selection

After scoring candidates, build outgoing edges using one of two neutral methods.

### 8.1 Top-k relation

For each `x`, choose the `k` lowest-action candidate successors:

```text
edges[x] = top_k_y A(x, y)
```

Parameters:

```text
out_degree_target k: 2, 3, 4, 6
```

This gives controlled branching and avoids accidental high-degree saturation.

### 8.2 Threshold relation

Add all candidate successors satisfying:

```text
A(x, y) <= theta
```

Threshold relations are more natural but may create variable degree and saturation. Use after top-k baseline is working.

First pass should use top-k.

## 9. Reversibility and asymmetry controls

After building candidate edges, optionally enforce or perturb reversibility.

Parameter:

```text
reversibility_fraction
```

Definition:

```text
fraction of edges x -> y for which y -> x is also inserted or preserved
```

Initial values:

```text
0.0, 0.25, 0.5, 0.75
```

Report actual measured reversibility:

```text
edge_reciprocity_fraction
```

Do not use labels such as irreversible_bad or reversible_good.

## 10. Rewiring controls

After edges are selected, optionally rewire a fraction of edges:

```text
rewire_probability
```

Initial values:

```text
0.0, 0.01, 0.05, 0.10
```

Rewiring should preserve out-degree unless explicitly testing degree changes.

This lets us test whether detected future-landscape structure degrades smoothly under neutral relation disorder.

## 11. Environment-shape diagnostics before pattern detection

Before applying `structured_propagation` labels, compute environment-shape diagnostics.

Required per generated environment:

```text
state_count
edge_count
mean_out_degree
out_degree_entropy
in_degree_entropy
edge_reciprocity_fraction
strongly_connected_component_count
largest_scc_fraction
reach_saturation_onset_H
reach_saturation_fraction_by_H
exact_frontier_size_by_H
frontier_repeat_onset_H
cycle_onset_proxy
collapse_flag
fast_saturation_flag
nonsaturation_window_length
path_concentration_proxy
bottleneck_proxy
```

These are environment diagnostics, not Omega evidence.

## 12. Calibration categories

Classify environments into neutral environment-shape classes before detector interpretation:

```text
fast_saturation_environment
fast_collapse_environment
cycle_dominated_environment
random_mixing_environment
underconnected_environment
middle_regime_environment
underdetermined_environment
```

Only `middle_regime_environment` should be passed to serious future-landscape detector interpretation.

Definition sketch:

```text
middle_regime_environment if:
  nonsaturation_window_length >= minimum_window
  not fast_collapse
  not pure cycle
  reach_saturation_onset_H is not too early
  largest_scc_fraction is neither tiny nor full immediately
```

Use conservative defaults. Do not tune to obtain positives.

## 13. Nulls for generated relation substrates

For each generated environment, create matched nulls:

```text
degree_preserving_rewire_null
out_degree_preserving_random_null
frontier_size_matched_probe_marginal_null
constraint_shuffled_null
asymmetry_shuffled_null
roughness_resampled_null
```

### 13.1 constraint_shuffled_null

Preserve the number, arity, and weights of constraints but shuffle their coordinate scopes or preferred residues.

Purpose:

```text
Does the specific local constraint arrangement matter?
```

### 13.2 asymmetry_shuffled_null

Preserve asymmetry strength distribution but shuffle bias assignments.

Purpose:

```text
Does directed asymmetry structure matter beyond random potential differences?
```

### 13.3 degree-preserving null

Keep as a strong graph-geometry null.

If generated worlds fail against this null, do not claim structure.

## 14. Detector integration

Run the existing v1.1 future-landscape detector and long-horizon audit on generated environments.

Do not change detector thresholds for this pass.

For every generated environment, report:

```text
environment_shape_class
aggregate_family_class_v1_1
aggregate_probe_family_classes
window_level_classes
horizon-local metrics
matched-null comparison
```

Because generated environments are not semantic families, replace `family` in reports with:

```text
generator_id
parameter_set_id
environment_id
```

## 15. Parameter sweep strategy

First pass should be small and structured.

Suggested grid:

```text
coordinate_count: [5, 6]
alphabet_size: [3]
neighborhood_radius: [1]
update_footprint: [1, 2]
out_degree_target: [2, 3, 4]
constraint_density: [0.10, 0.25, 0.40]
constraint_strength: [0.5, 1.0, 2.0]
asymmetry_strength: [0.0, 0.25, 0.5]
reversibility_fraction: [0.0, 0.25, 0.5]
rewire_probability: [0.0, 0.05]
seeds_per_parameter_set: 2
```

This is already large if fully crossed. Implement either:

```text
random parameter sampling
latin-hypercube-like sampling
small hand-declared neutral grid
```

Do not manually choose parameters because they look likely to pass.

Start with about:

```text
50 to 200 generated environments
```

if runtime allows.

## 16. Outputs

Add output files:

```text
generated_environment_metadata.csv
environment_shape_summary.csv
environment_shape_classes.csv
relation_parameter_sweep.csv
relation_atlas_detector_summary.csv
relation_atlas_null_summary.csv
relation_atlas_window_summary.csv
relation_atlas_status.json
```

Each row should include enough metadata to reproduce the environment:

```text
seed
coordinate_count
alphabet_size
neighborhood_radius
update_footprint
out_degree_target
constraint_density
constraint_strength
asymmetry_strength
reversibility_fraction
rewire_probability
roughness_strength
constraint_seed_json_or_hash
```

## 17. Summary.md required sections

Add a result summary with:

```text
## Run Shape
```

```text
generated environments
state count range
edge count range
horizon grid
errors
elapsed time
```

```text
## Environment Shape Classes
```

Counts by:

```text
fast_saturation_environment
fast_collapse_environment
cycle_dominated_environment
random_mixing_environment
underconnected_environment
middle_regime_environment
underdetermined_environment
```

```text
## Middle-Regime Candidates
```

List environments that are not detector positives, but are suitable for detector interpretation:

```text
environment_id
parameter_set_id
nonsaturation_window_length
saturation_onset_H
largest_scc_fraction
edge_reciprocity_fraction
```

```text
## Detector Results on Middle-Regime Environments
```

Report aggregate classes and null separation.

```text
## Null/Control Failures
```

Report whether any generated environment only passes against weak nulls but fails degree/constraint/asymmetry shuffled nulls.

```text
## Parameter Trends
```

Report coarse trends, not causal claims:

```text
which parameter ranges tend to saturate
which tend to collapse
which produce middle-regime windows
which produce local candidates that fail aggregate checks
```

```text
## Claim Boundary
```

State explicitly:

```text
This is environment calibration, not Omega validation.
Generated relation environments are neutral parameterized substrates.
No agents, identities, viable paths, or value-bearing structures are claimed.
```

## 18. Success criteria

Implementation success:

```text
neutral relation generator implemented
environments reproducible from metadata
environment-shape diagnostics reported
matched nulls generated
existing detector runs on generated environments
```

Calibration success:

```text
some generated environments fall into middle_regime_environment
```

Scientific gate progress:

```text
at least one middle-regime non-control generated environment earns aggregate
structured_propagation against degree, random, constraint-shuffled,
asymmetry-shuffled, and frontier/probe-marginal nulls
```

Scientific gate remains not passed if:

```text
all environments saturate/collapse/cycle/random-mix
or local candidates fail aggregate checks
or positives fail strong matched nulls
```

## 19. Do not do

Do not:

```text
name any generated family structured/expanding/contracting/cyclic
add agents or identities
add viable path labels
add support/recover/degrade labels
add cost/resource coordinates
change detector thresholds to force a pass
select parameters after seeing detector output and present them as neutral
```

If parameter search is adaptive, mark it as adaptive and separate exploratory from confirmatory runs.

## 20. Suggested CLI

Example:

```bash
python -m omega.rfs_mb0_future_landscape.run_relation_atlas \
  --out results/rfs_mb0_relation_atlas/20260523_action_generated_v0 \
  --parameter-samples 100 \
  --seeds-per-parameter-set 2 \
  --horizon-grid long_10x \
  --workers 18 \
  --max-runtime-seconds 900
```

Debug:

```bash
python -m omega.rfs_mb0_future_landscape.run_relation_atlas \
  --out results/rfs_mb0_relation_atlas/debug_action_generated_v0 \
  --parameter-samples 10 \
  --seeds-per-parameter-set 1 \
  --horizon-grid dense_early \
  --workers 4
```

## 21. Bottom line

The next substrate should not be a better hand-named `structured_relation`.

It should be an action-generated neutral relation atlas:

```text
distinction space
+ local neighborhoods
+ generated constraints
+ action-scored local transitions
+ controlled asymmetry/reversibility/rewiring
= neutral relation environments
```

Then the future-landscape detector can ask, blind to intended semantics:

```text
Do any primitive-parameter regimes produce structured future-landscape
propagation above matched nulls?
```
