# Identity-Decay Null Taxonomy v0

Status: working formalism / control-discipline draft  
Date: 2026-06-02  
Claim boundary: null taxonomy for future tests only; not empirical validation, not proto-valuer detection, not Omega validation

## 0. Purpose

This note locks down the first taxonomy of **identity-decay nulls** for future pre-proto-valuer and proto-valuer tests.

The core move is:

```text
not:
  dissolution is a primitive feature of the substrate

but:
  for each candidate process bundle P, define a matched identity-decay null N_P
  under declared dynamics, observables, perturbations, and horizon.
```

An identity-decay null is a declared reference dynamics or comparison condition in which a candidate pattern's maintaining structure is absent, passivized, randomized, ablated, or unsupported while relevant nuisance structure is preserved.

The purpose is to make anti-dissolution operational:

```text
maintenance_gap_N(P,H) = C_K^Pi(P,H) - C_{N_P}^Pi(P,H)
```

This gap is meaningful only if `N_P` is principled, parsimonious, predictive, reproducible, and auditable.

## 1. Relation to the current formal stack

Current stack:

```text
v0.2:
  Future-Distinction Dynamics

admissibility enrichment:
  process bundles, activity channels, identity-decay nulls, maintenance gaps

proto-valuer layer:
  pre-proto-valuers, proto-valuers, induced asymmetry-preferences

completion layer:
  maximal admissible compatibility completions
```

This note supports the **admissibility enrichment** layer.

It does not define proto-valuers by itself. It defines the null controls needed before pre-proto-valuer claims can be meaningful.

## 2. Core schema

Let:

```text
D = (X, R, K, Q_adm, Pi)
```

where:

```text
X:
  finite or measurable state / trajectory space

R:
  admissible transition relation

K:
  actual transition law, successor-selection rule, or stochastic kernel

Q_adm:
  declared admissible observable / quotient family

Pi:
  declared perturbation class or perturbation distribution family
```

Let:

```text
P:
  admissible process-bundle designation

[P]:
  fiber, class, or ensemble of trajectories matching P

a_P:
  declared activity channel associated with P

K^{act(P)}:
  transition law with P-associated activity present

N_P:
  matched identity-decay null for P

C_K^Pi(P,H):
  recoverable distinction-maintenance of P under actual / activity-present dynamics

C_{N_P}^Pi(P,H):
  recoverable distinction-maintenance of P under the identity-decay null
```

Then a maintenance-gap test has the form:

```text
C_K^Pi(P,H) - C_{N_P}^Pi(P,H) >= eta.
```

The gap does not mean `P` is a valuer. It is only one ingredient for pre-proto-valuer status.

## 3. Universal admissibility contract for identity-decay nulls

Every identity-decay null must satisfy the following contract before it can support a formal claim.

### 3.1 Predeclared

The null must be specified before the comparison is interpreted.

Required:

```text
null_id
null_family
candidate_process_bundle_id
horizon_regime
perturbation_class
observable_family
preserved_quantities
disrupted_quantities
matching_policy
random_seed_policy if stochastic
```

### 3.2 Candidate-specific but conclusion-independent

The null may depend on the declared candidate process bundle `P`, but it must not depend on whether `P` succeeds under the test.

Invalid:

```text
choosing the null after seeing which null produces a positive maintenance gap;
defining the null using future success labels;
preserving exactly the structure later claimed as nontrivially maintained.
```

### 3.3 Nuisance-preserving

The null must preserve enough low-level structure that a positive gap cannot be explained by trivial mismatches.

Potential nuisance variables:

```text
state-space size
frontier size
out-degree / effective out-degree
row / column marginals
component marginal support
horizon schedule
selection budget
energy distribution or rank distribution
artifact completeness status
perturbation schedule
```

Not every null must preserve every nuisance variable. Each null must explicitly state what it preserves and what it does not.

### 3.4 Target-disrupting

The null must disrupt the candidate maintaining structure enough to be a real identity-decay reference.

If the null leaves the P-maintaining mechanism intact, then failure to separate from the null is not informative; success against that null may be too weak.

### 3.5 Not overdestructive

The null must not destroy the entire substrate in a way that makes the candidate look good by comparison.

Invalid:

```text
null collapses all frontiers when actual K does not;
null removes unrelated support needed by all patterns;
null changes horizon, state space, or selection budget without accounting for it;
null creates artifact incompleteness or truncation asymmetry.
```

### 3.6 Reconstructible and auditable

A null comparison must be reconstructible from retained artifacts or exact rebuild metadata.

Required outputs for future implementations:

```text
identity_decay_null_manifest.csv
maintenance_gap_by_horizon.csv
null_frontier_profile_by_horizon.csv
null_reconstruction_audit_summary.csv
null_artifact_completeness_summary.csv
```

### 3.7 Failure-reporting

Null failures must be reported, not silently discarded.

A failed null can mean:

```text
null construction invalid;
null artifacts incomplete;
null not matched on required nuisance variables;
pattern does not separate from the null;
positive gap depends on null choice.
```

## 4. Null family taxonomy

The families below are not equally strong and are not universally ordered. Their strength depends on the claim being tested and the nuisance variables preserved.

Each future pre-proto-valuer claim should declare one primary null family and, where possible, a null battery.

## 4.1 Passive null

### Definition

A passive null removes or suppresses the candidate process bundle's activity channel while leaving the surrounding substrate context as intact as possible.

```text
N_P = dynamics with a_P absent or inactive
```

### Preserves

```text
state space
background transition relation
external perturbation schedule
non-P substrate context
as much frontier scale as possible
```

### Destroys / disrupts

```text
P-associated activity channel
self-maintaining action or intervention pathway
P-conditioned transition differences
```

### Valid when

The candidate has a declared activity channel `a_P` that can be removed or set inactive without changing unrelated substrate structure too much.

### Invalid when

```text
there is no separable activity channel;
passivization changes the entire substrate class;
passivization destroys unrelated support needed by all patterns;
the passive condition is not matched on obvious nuisance variables.
```

### Required artifacts

```text
process_bundle_manifest.csv
activity_channel_manifest.csv
active_vs_passive_condition_identity.csv
frontier_profile_by_horizon for active and passive conditions
maintenance_gap_by_horizon.csv
```

### Claim supported if passed

A positive gap against a passive null supports:

```text
P-associated activity contributes to maintaining recoverable distinction-content.
```

It does not by itself support proto-valuerhood unless the self-conditioning criterion is also met.

## 4.2 Ablation null

### Definition

An ablation null removes, masks, or disables candidate maintaining transitions, coordinates, edges, or activity components while preserving as much of the background system as possible.

```text
N_P = K with declared P-maintaining components ablated
```

### Preserves

```text
state space
horizon schedule
most transition relation outside ablated components
baseline frontier scale where possible
artifact schema
```

### Destroys / disrupts

```text
candidate maintaining transitions
candidate repair pathway
candidate coupling term
candidate invariant channel
candidate process-bundle mechanism
```

### Valid when

The candidate maintaining components are declared before ablation and can be removed without redefining the entire substrate.

### Invalid when

```text
ablation target was selected after observing success;
ablation deletes too much of the system;
ablation destroys all comparable dynamics;
ablation is not matched against a non-candidate ablation control.
```

### Required artifacts

```text
ablation_manifest.csv
ablated_component_list.csv
active_vs_ablation_condition_identity.csv
frontier_profile_by_horizon
recoverability_summary_by_horizon
maintenance_gap_by_horizon.csv
```

### Claim supported if passed

A positive gap against an ablation null supports:

```text
the ablated P-maintaining structure is functionally relevant to recoverable
continuation of P's distinction-content.
```

## 4.3 Randomized-activity null

### Definition

A randomized-activity null preserves activity rate, count, energy budget, or local statistics while scrambling the P-conditioned structure.

```text
N_P = randomized version of K^{act(P)} preserving declared low-level statistics
```

### Preserves

Possible preserved quantities:

```text
activity count
activity timing distribution
out-degree / effective out-degree
edge-weight distribution
energy or rank distribution
row / column marginals
frontier size envelope
```

### Destroys / disrupts

```text
structured relation between P activity and P distinction-maintenance
specific activity-to-continuation alignment
candidate process-bundle coherence
```

### Valid when

The goal is to test whether maintenance depends on structured activity rather than mere activity quantity or budget.

### Invalid when

```text
randomization fails to preserve the claimed nuisance variables;
randomization accidentally preserves P's maintaining structure;
randomization creates impossible transitions;
randomization changes artifact completeness or cap status;
only favorable random seeds are reported.
```

### Required artifacts

```text
randomization_policy_manifest.csv
seed_policy
preserved_statistic_audit.csv
randomized_activity_runs.csv
maintenance_gap_distribution_by_seed.csv
```

### Claim supported if passed

A positive gap against randomized activity supports:

```text
P maintenance depends on structured activity, not merely activity volume or local budget.
```

## 4.4 Matched-marginal null

### Definition

A matched-marginal null preserves component marginals while destroying or randomizing candidate joint/process-specific structure.

In coupled settings:

```text
N_P preserves A and B marginal support but disrupts joint combinations or
process-specific coupling.
```

### Preserves

```text
A marginal support
B marginal support
marginal retention fractions
component frontier sizes
possibly row / column marginals of a transport or support matrix
```

### Destroys / disrupts

```text
joint support structure
cross-field coupling pattern
process-specific joint distinction-content
higher-order combination constraints
```

### Valid when

The claim concerns joint-field structure rather than component survival.

This null is especially relevant because current FFA results show:

```text
marginal continuation is not compatibility.
```

### Invalid when

```text
marginal preservation is itself the phenomenon being tested;
matched marginals are computed using future semantic labels;
joint structure is destroyed in a way that changes frontier-size or cap status;
component marginals are not actually matched.
```

### Required artifacts

```text
marginal_retention_by_horizon.csv
joint_vs_product_residual_by_horizon.csv
matched_marginal_null_manifest.csv
joint_density_vs_marginal_product_by_horizon.csv
marginal_matching_audit.csv
```

### Claim supported if passed

A positive gap against a matched-marginal null supports:

```text
P's recoverable distinction-content depends on joint/process-specific structure,
not merely marginal continuation.
```

## 4.5 Product-composition null

### Definition

A product-composition null uses independent product composition as the reference for coupled future fields.

```text
N_P = product of component future fields under their independent selectors
```

### Preserves

```text
component selected successor rules
component frontiers
component marginal availability
product baseline semantics
```

### Destroys / disrupts

```text
coupled selector effects
joint rank-prefix constraints
cross-field coupling terms
shared-capacity constraints
```

### Valid when

The goal is to test whether a coupled operator produces product-breaking future-field geometry.

### Invalid when

```text
zero-penalty joint selection is treated as product-neutral;
component selectors differ between product and coupled comparisons;
product baseline is not explicitly emitted;
product/coupled artifacts differ in completeness or cap status.
```

### Required artifacts

```text
product_baseline_manifest.csv
coupled_operator_manifest.csv
joint_vs_product_residual_by_horizon.csv
marginal_retention_by_horizon.csv
artifact_completeness_summary.csv
reconstruction_audit_summary.csv
```

### Claim supported if passed

A positive product-vs-coupled gap supports:

```text
structured product-breaking deformation under the declared coupled operator.
```

It does not by itself support interaction, compatibility, support, capture, erasure, agency, or value.

## 4.6 Unsupported-evolution null

### Definition

An unsupported-evolution null lets the candidate pattern evolve without the repair, maintenance, selection support, or stabilizing asymmetry hypothesized to maintain it.

```text
N_P = evolution with maintaining support removed but without targeted deletion of P
```

### Preserves

```text
state space
background local dynamics
initial condition or initial pattern designation
horizon schedule
```

### Destroys / disrupts

```text
ongoing repair
maintenance support
selection reinforcement
stabilizing asymmetry
```

### Valid when

The claim is that P persists because of active maintenance rather than inert stability.

### Invalid when

```text
unsupported evolution is just a different substrate;
removing support also removes P's initial distinction-content;
null is not matched on initial condition;
no perturbation class is declared.
```

### Required artifacts

```text
initial_process_bundle_manifest.csv
support_channel_manifest.csv
supported_vs_unsupported_condition_identity.csv
recoverability_by_horizon.csv
maintenance_gap_by_horizon.csv
```

### Claim supported if passed

A positive gap supports:

```text
ongoing support or maintenance contributes to recoverable persistence of P.
```

## 4.7 Degree / frontier-size matched null

### Definition

A degree/frontier-size matched null preserves coarse graph or frontier statistics while disrupting candidate maintaining structure.

### Preserves

Possible preserved quantities:

```text
out-degree / effective out-degree
frontier size by horizon
row / column marginals
edge count
node count
rank distribution
component count if declared
```

### Destroys / disrupts

```text
candidate invariant structure
candidate rank-boundary alignment
candidate quotient/fiber coherence
candidate process-bundle transport pattern
```

### Valid when

The goal is to rule out trivial explanations based on size, degree, budget, or cap artifacts.

### Invalid when

```text
matching is too coarse to address the claim;
matched null still preserves the candidate mechanism;
frontier size is matched by changing unrelated substrate semantics;
truncated or incomplete topology is treated as complete.
```

### Required artifacts

```text
frontier_profile_by_horizon.csv
rank_boundary_geometry_by_horizon.csv
edge_count / node_count summaries
matched_null_generation_manifest.csv
null_matching_audit.csv
reconstruction_audit_summary.csv
```

### Claim supported if passed

A positive gap supports:

```text
the observed maintenance is not explained solely by coarse degree, frontier size,
or budget geometry.
```

## 5. Null batteries

A single null usually supports only a narrow claim. Stronger future claims should use a null battery.

Example progression:

```text
product-composition null:
  product-breaking geometry exists

matched-marginal null:
  structure is not just marginal continuation

degree/frontier-size matched null:
  structure is not just size or budget

randomized-activity null:
  structure is not just activity amount

passive / ablation / unsupported null:
  candidate maintaining activity matters
```

This is not a universal strength ordering. The correct battery depends on the claim.

A claim should state:

```text
primary_null_family
secondary_null_families
failed_nulls
unrun_nulls
claim_supported
claim_blocked
```

## 6. Null shopping prohibition

Null shopping is a failure mode.

Invalid practice:

```text
run many nulls;
report only the one that gives the desired maintenance gap;
ignore nulls where P fails to separate;
change the null after seeing the result;
use one null for positive claims and a different null for controls without
explaining why.
```

Required practice:

```text
predeclare candidate P;
predeclare primary null N_P;
predeclare nuisance variables to preserve;
report all nulls attempted;
report failed and inconclusive nulls;
state the strongest claim allowed by the full null battery.
```

## 7. Minimal future artifact schema

Future FFA or theorem-sandbox runs that attempt identity-decay comparisons should emit at least:

```text
process_bundle_manifest.csv
activity_channel_manifest.csv
identity_decay_null_manifest.csv
identity_decay_null_matching_audit.csv
active_condition_identity_manifest.csv
null_condition_identity_manifest.csv
recoverability_by_horizon.csv
maintenance_gap_by_horizon.csv
null_artifact_completeness_summary.csv
null_reconstruction_audit_summary.csv
```

Suggested `identity_decay_null_manifest.csv` columns:

```text
null_id
null_family
candidate_process_bundle_id
active_condition_id
null_condition_id
horizon_regime
perturbation_class_id
observable_family
preserved_quantities_json
disrupted_quantities_json
matching_policy_json
random_seed_policy
validity_notes
claim_boundary
```

Suggested `maintenance_gap_by_horizon.csv` columns:

```text
candidate_process_bundle_id
null_id
horizon
C_active
C_null
maintenance_gap
threshold_eta
gap_status
artifact_completeness_status
reconstruction_audit_status
```

## 8. Claim ladder supported by nulls

### 8.1 Maintenance precursor

Allowed claim:

```text
P maintains recoverable distinction-content better than null N_P under declared
observables, perturbations, and horizon.
```

Blocked claims:

```text
proto-valuer;
valuer;
agent;
identity as primitive;
value;
Omega.
```

### 8.2 Pre-proto-valuer candidate

Allowed only when combined with nontrivial distinction maintenance and perturbation-robust recoverability.

```text
P satisfies declared pre-proto-valuer criteria under null N_P.
```

Blocked:

```text
full proto-valuerhood unless self-conditioning is tested.
```

### 8.3 Proto-valuer candidate

Requires a declared activity channel and active-vs-passive self-conditioning gap toward future pre-proto-valuerhood.

```text
P satisfies declared proto-valuer criteria.
```

Blocked:

```text
full valuerhood unless induced asymmetry-preferences survive compatibility audits.
```

## 9. Current Future Field Atlas status

Current FFA results do **not** instantiate identity-decay null tests.

They provide precursors:

```text
product baselines;
zero-penalty joint selector controls;
scalar mismatch operator sensitivity;
pair-level morphology;
marginal retention;
joint-vs-product residuals;
shared-capacity v1 negative diagnostic;
artifact completeness and reconstruction audits.
```

Useful current lesson:

```text
marginal continuation is not compatibility.
```

Future identity-decay tests require explicit process-bundle designations, activity channels, null manifests, and maintenance-gap artifacts.

## 10. Falsifiers and blockers

Identity-decay claims weaken or fail if:

```text
N_P is not declared before interpretation;
N_P changes unrelated substrate structure too much;
N_P preserves the candidate maintaining mechanism;
N_P destroys the entire frontier or creates artifact incompleteness;
P separates only from weak nulls and fails matched nuisance-preserving nulls;
maintenance gap is explained by frontier size, degree, cap artifacts, or seed skew;
null failures are omitted;
reconstruction audits fail;
observable coverage is too narrow for the intended claim.
```

Pre-proto-valuer language remains blocked if:

```text
P has no declared process-bundle designation;
P has no reconstructible distinction-content measure;
P fails perturbation-robust recoverability;
P fails to separate from its primary identity-decay null;
```

Proto-valuer language remains blocked if:

```text
no activity channel a_P is declared;
active and passive conditions are not matched;
self-conditioning toward future pre-proto-valuerhood is not measured;
passive persistence explains the result.
```

## 11. Next theorem targets enabled by this taxonomy

This taxonomy enables finite separation theorems such as:

```text
Passive persistence does not imply pre-proto-valuerhood.

A structure can persist under K while failing the maintenance-gap test against
N_P.

A structure can satisfy pre-proto-valuer criteria under one null but fail under a
stronger nuisance-preserving null.

A structure can satisfy pre-proto-valuer criteria but fail proto-valuer criteria
if no self-conditioning gap exists.

A proto-valuer can fail valuerhood if its induced asymmetry-preferences collapse
under compatibility audit.
```

## 12. Summary

Identity-decay nulls are the control surface for future proto-valuer tests.

Compact formulation:

```text
An identity-decay null N_P is a declared matched reference for a candidate process
bundle P in which P's maintaining structure is absent, passivized, randomized,
ablated, or unsupported while stated nuisance structure is preserved.

A maintenance gap against N_P is evidence only relative to what the null preserves
and destroys.

No pre-proto-valuer or proto-valuer claim is admissible until the process bundle,
activity channel, distinction measure, perturbation class, null family, matching
policy, and reconstruction audits are declared.
```
