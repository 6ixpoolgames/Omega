# RFS-MB0 Substrate Untethering Transition-Energy Sweep Spec

Status: substrate-design / instrument robustness spec  
Builds on: `docs/research_notes/omega_theory/transition_energy_and_constraint_untethering.md` and `docs/research_notes/omega_theory/horizon_transport_aligned_amplification.md`  
Claim boundary: no holdout scoring, no candidate promotion, no Omega detection, no agency detection, no identity detection, no valuer detection

## 0. One-sentence purpose

Test whether matched-marginal-separated horizon transport with aligned amplification persists when the hand-built modular/equality/difference constraint vocabulary is replaced by generic transition-energy families.

Plainly:

```text
Is the H128 horizon-transport object a property of the current hand-built constraint grammar,
or does it survive in more generic finite transition substrates?
```

## 1. Why this spec exists

The current H128 branch surfaced a clean intermediate object:

```text
matched-marginal-separated horizon transport;
horizon-dependent aligned amplification;
no terminal saturation through H=128;
response threshold shifts earlier with perturbation strength.
```

But the current relation-generated substrate still uses hand-built constraint templates:

```text
local_modular_sum_preference
local_equality_relation
local_difference_relation
```

The instances are generated, but the law vocabulary is selected by us.

This creates a live concern:

```text
The horizon-transport response surface may partially reflect the chosen constraint grammar.
```

Before promoting the horizon-transport instrument beyond the current substrate family, this concern must be tested.

## 2. Claim boundary

Allowed claims:

```text
horizon transport does or does not persist across transition-energy substrate families;
aligned amplification does or does not appear outside the original constraint-template substrate;
locality-only / smooth-potential / budget-conservation substrates are trivial, generative, saturated, or response-diverse;
current instrument is or is not robust to substrate-law untethering.
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

## 3. Core substrate formalism

Implement a substrate family interface based on:

```text
X:
  finite state space

Q(s -> t):
  local proposal kernel / candidate neighborhood

E(s,t):
  transition energy or edge-selection score

R:
  edge selection rule
```

A directed transition exists when `R` selects `t` from `Q(s)` using `E(s,t)`.

Default selection rule:

```text
edges(s) = top_m lowest-energy candidates from Q(s)
```

Optional later selection rule:

```text
P(s -> t) proportional to exp(-beta E(s,t))
```

Do not use probabilistic sampling in the first untethering smoke unless reproducibility and matched-control handling are already clean.

## 4. Required substrate families

### 4.1 Current comparator: constraint-template substrate

Use the current relation generator as comparator.

```text
substrate_family: constraint_template_current
```

Purpose:

```text
confirm that the H128 instrument still reproduces the known current-family response surface under the same run shape.
```

### 4.2 E0: locality-only substrate

```text
substrate_family: locality_only

E_0(s,t) = d_H(s,t) + epsilon * roughness(s,t)
```

Purpose:

```text
lower baseline;
checks whether locality + out-degree alone creates trivial diffusion, saturation, or aligned amplification.
```

Expected possibility:

```text
may be too structureless;
that is informative.
```

### 4.3 E1: locality + smooth random potential

```text
substrate_family: smooth_random_potential

E_1(s,t) = d_H(s,t) + beta * (V(t) - V(s)) + epsilon * roughness(s,t)
```

where `V` is a seeded smooth random scalar field over `X`.

Purpose:

```text
first serious grammar-free replacement;
provides locality, directionality, landscape structure, and roughness without named symbolic laws.
```

Required potential metadata:

```text
potential_seed
potential_smoothness
potential_scale
potential_neighbor_correlation
potential_distribution_summary
```

### 4.4 E2: locality + budget / conservation

```text
substrate_family: budget_conservation

E_2(s,t) = d_H(s,t) + lambda * |B(t) - B(s)| + epsilon * roughness(s,t)
```

where `B` may be:

```text
symbol histogram distance;
Hamming weight;
total coordinate mass;
coarse resource budget.
```

Purpose:

```text
tests whether approximate invariants / conservation-like structure are needed for richer response.
```

Required budget metadata:

```text
budget_kind
budget_weight
budget_distribution_summary
budget_delta_summary
```

### 4.5 Optional E3: maximum-entropy local transition ensemble

Only implement if E0/E1/E2 are clean and time remains.

```text
substrate_family: max_entropy_local_transition
```

Macro constraints:

```text
state count;
locality radius;
out-degree distribution;
reversibility fraction;
roughness level;
optional energy marginal distribution.
```

Purpose:

```text
longer-term anti-smuggling substrate;
not required for the first untethering result.
```

## 5. Shared state-space and proposal settings

Use the same state-space shape as the current branch first:

```text
coordinate_count: current default, e.g. 5 or 6
alphabet_size: current default, e.g. 3
X = {0, ..., alphabet_size-1}^coordinate_count
```

Shared proposal kernel:

```text
Q(s): all states within Hamming distance <= update_footprint
```

Shared edge-selection settings:

```text
out_degree_target: current comparable value
roughness_seed: deterministic
roughness_strength: sweep or fixed comparator
reversibility_fraction: fixed comparator unless explicitly swept
rewire_probability: 0 for first untethering smoke unless needed as control
```

Keep as many non-substrate variables fixed as feasible so differences are attributable to substrate family.

## 6. Horizon-transport detector reuse

Use the current horizon-transport detector unchanged except for substrate-family metadata.

Required detector components:

```text
horizon_transport matrices;
SVD summaries;
matched marginal detector nulls;
response taxonomy with transport_amplified_aligned;
terminal saturation diagnostics;
transport viscosity diagnostics if available.
```

Required detector-null families:

```text
context_shuffle_transport_null
horizon_pair_shuffle_transport_null
row_marginal_matched_transport_null
column_marginal_matched_transport_null
row_column_marginal_matched_transport_null
```

Required statistic:

```text
marginal_residual_fraction
```

## 7. Run shape

Start small but not tiny.

Suggested first smoke:

```text
substrate_families:
  constraint_template_current
  locality_only
  smooth_random_potential
  budget_conservation

groups_per_family: 12 to 24
design_groups_per_family: 6 to 12
fresh_seeds_per_group: 4
start_samples_list: 2,4,8,16
null_replicates: 9 or 11
workers: machine appropriate
max_runtime_seconds: 14400 to 21600
shutdown_cushion_seconds: 1200
```

If runtime is still trivial, increase breadth before increasing horizon:

```text
groups_per_family up to 48
design_groups_per_family up to 16
fresh_seeds_per_group up to 6
```

Do not open holdout.

## 8. Horizon pairs

First untethering run should use a compact but informative horizon set.

Required:

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

Optional if all families remain well-covered:

```text
128->256
256->512
```

Do not jump to H1280 in the first untethering smoke; first determine whether untethered substrates behave at H128.

## 9. Perturbation ladder

Use the same two perturbation families first:

```text
small_edge_resample_control
asymmetric_edge_flip_control
```

Required strengths:

```text
0.006
0.010
0.015
0.020
0.030
```

Optional boundary strengths:

```text
0.040
0.060
```

If boundary strengths are used, label them:

```text
intervention_class: boundary_probe
interpretation_role: viability_boundary_mapping
allowed_claim_level: viability_boundary_only
```

## 10. Required outputs

Core outputs:

```text
substrate_untethering_run_config.json
substrate_untethering_status.json
substrate_untethering_progress_checkpoints.csv
substrate_untethering_errors.csv
substrate_untethering_output_manifest.json
```

Substrate-family outputs:

```text
substrate_family_manifest.csv
transition_energy_family_summary.csv
transition_energy_parameter_summary.csv
substrate_capacity_by_family.csv
substrate_generation_diagnostics.csv
```

Horizon-transport outputs:

```text
horizon_transport_matrix_manifest.csv
horizon_transport_coverage.csv
horizon_transport_svd_summary.csv
horizon_transport_detector_null_gate_results.csv
horizon_transport_matched_marginal_summary.csv
horizon_transport_response_classification.csv
horizon_response_threshold_table.csv
horizon_transport_terminal_saturation_summary.csv
```

Comparison outputs:

```text
horizon_transport_by_substrate_family_summary.csv
aligned_amplification_by_substrate_family.csv
response_diversity_by_substrate_family.csv
transport_viscosity_by_substrate_family.csv
matched_null_pass_by_substrate_family.csv
```

Final report:

```text
rfs_mb0_substrate_untethering_transition_energy_sweep_result.md
```

## 11. Final report requirements

Retain the result note under:

```text
docs/research_notes/validation_results/rfs_mb0_substrate_untethering_transition_energy_sweep_result.md
```

Required sections:

```text
1. Executive summary
2. Claim boundary
3. Substrate family definitions
4. Transition-energy implementation audit
5. Matrix coverage by substrate family
6. Matched marginal detector-null results by substrate family
7. Response classes by substrate family
8. Horizon response threshold by substrate family
9. Transport viscosity by substrate family
10. Artifact risk read
11. Next-action fork
12. Output manifest
```

Executive summary must answer:

```text
Did horizon transport persist outside the current constraint-template substrate?
Did aligned amplification appear in smooth-potential or budget-conservation families?
Was locality-only trivial, generative, saturated, or response-bearing?
Are current H128 results likely grammar-artifact, generic landscape effect, invariant-dependent, or unresolved?
What should run next?
```

## 12. Decision classes

Allowed decision classes:

```text
horizon_transport_generalizes_beyond_constraint_vocabulary
constraint_template_specific_signal
generic_smooth_landscape_sufficient
budget_invariant_needed
locality_only_trivial_baseline
substrate_capacity_low
instrument_resolution_limit_possible
untethering_underpowered
not_ready_repair_required
```

Forbidden decision classes:

```text
Omega_positive
agent_detected
valuer_detected
identity_detected
life_detected
self_replication_detected
candidate_promoted
holdout_ready
```

## 13. Next-action forks

Emit exactly one next-action fork:

```text
continue_transition_energy_substrates
expand_smooth_potential_sweep
expand_budget_conservation_sweep
implement_max_entropy_transition_ensemble
return_to_current_constraint_template_with_caveat
repair_transition_energy_generator
write_substrate_artifact_risk_note
pause_instrument_promotion
```

No fork may open holdout, graph perturbation, direct channel causality, candidate promotion, or Omega/agency/value claims directly.

## 14. Interpretation guide

### 14.1 If E1/E2 reproduce aligned amplification

Interpretation:

```text
The horizon-transport object is not limited to the original hand-built constraint templates.
```

Next:

```text
continue transition-energy substrates;
consider broader E-family sweeps;
keep claim boundary.
```

### 14.2 If only the current constraint-template substrate works

Interpretation:

```text
grammar-artifact risk is high.
```

Next:

```text
write substrate artifact risk note;
do not promote the instrument beyond current substrate family.
```

### 14.3 If locality-only works

Interpretation:

```text
aligned amplification may be a generic property of local bounded-outdegree transition graphs.
```

Next:

```text
tighten nulls and maximum-entropy controls;
check for trivial diffusion/saturation explanations.
```

### 14.4 If smooth potential works but locality-only does not

Interpretation:

```text
generic landscape structure may be sufficient.
```

Next:

```text
sweep potential smoothness, beta, and roughness;
compare viscosity.
```

### 14.5 If budget/conservation works but smooth potential does not

Interpretation:

```text
approximate invariants may be important for richer future-transport structure.
```

Next:

```text
sweep budget types and weights;
look for response differentiation.
```

## 15. 3P check

### Principled

The run replaces named symbolic constraint templates with explicit, generic transition-energy families.

### Parsimonious

Only a few minimal families are tested: current comparator, locality-only, smooth random potential, and budget/conservation.

### Predictive

Each family makes different predictions about whether horizon transport and aligned amplification persist.

## 16. Bottom line

This run asks:

```text
Does matched-marginal-separated horizon transport with aligned amplification survive when the substrate law is untethered from hand-built constraint templates?
```

A positive result strengthens the instrument.

A negative result does not falsify Omega, but it blocks promoting the current instrument beyond the original constraint-template substrate.
