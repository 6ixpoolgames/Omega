# Finite Distinction Measures v0

A small reconstructible menu for finite future-field and process-bundle tests

Status: finite measure scaffold / theory-arm draft  
Date: 2026-06-02  
Claim boundary: mathematical and instrumentation scaffolding only; not empirical validation, not proto-valuer detection, not valuer detection, and not Omega validation

## 0. Purpose

The current formal stack uses a placeholder:

```text
M_Q(D_t(P))
```

for the distinction-content of a candidate process-bundle designation `P` under an admissible observable family `Q_adm`.

That placeholder is now a possible back door. If `M_Q` is too flexible, future claims can smuggle relevance through the metric.

This note defines a small conservative menu of finite distinction measures that are:

```text
predeclared;
finite;
reconstructible;
observable-indexed;
horizon-scoped;
control-auditable;
claim-bounded.
```

These measures do not detect value, valuerhood, agency, identity, support, capture, erasure, compatibility, or Omega. They measure finite distinction structure that may later support stronger claims only after null, recoverability, perturbation, self-conditioning, and compatibility audits.

## 1. General finite setup

Let:

```text
X:
  finite state space

R:
  admissible transition relation

K:
  transition law, successor-selection rule, or stochastic kernel

Q_adm:
  finite declared family of admissible observables / quotients

q in Q_adm:
  q : X -> Z_q

P:
  candidate process-bundle designation

[P]:
  fiber, class, or ensemble of trajectories matching P

F_h(P):
  finite frontier of P at horizon h

W:
  finite horizon window, W subset {0, 1, ..., H}
```

For a set of states `A subset X`, define the quotient support:

```text
q(A) = { q(x) : x in A }.
```

For a process-bundle frontier:

```text
Q_h(P; q) = q(F_h(P)).
```

All measures below are relative to declared `P`, `q`, and horizon regime. There is no measure of distinction-content independent of observable choice.

## 2. Universal admissibility contract for finite distinction measures

A finite distinction measure may support later formal claims only if it satisfies this contract.

### 2.1 Predeclared observable

The observable or quotient must be declared before interpretation.

Required:

```text
observable_id
observable_family
observable_params_json
process_bundle_id
horizon_window
separation_criterion
artifact_sources
claim_boundary
```

### 2.2 Reconstructible from raw or retained artifacts

The measure must reconstruct from retained artifacts or exact rebuild metadata.

No measure may depend on deleted raw topology unless the rebuild contract is exact and the run is reproducible.

### 2.3 Not merely frontier size

A raw frontier count is not by itself a distinction measure. It becomes distinction-relevant only through a declared observable, quotient, separation criterion, or reconstruction map.

### 2.4 Not semantic-label based

Do not count:

```text
agent labels;
valuer labels;
identity labels;
value labels;
support/capture/erasure labels;
human-interpreted semantic classes;
post hoc success labels.
```

### 2.5 Null-auditable

A distinction measure intended for pre-proto-valuer tests must be computable under both actual dynamics and the matched identity-decay null:

```text
M_Q^K(D_t(P))
M_Q^{N_P}(D_t(P))
```

### 2.6 Perturbation-scoped

If the claim involves perturbation robustness, the measure must declare perturbation semantics:

```text
universal / adversarial over Pi;
expected over perturbation distribution;
quantile over perturbation distribution;
stratified report by perturbation type.
```

### 2.7 Failure-reporting

If a measure cannot be reconstructed, is truncated, is single-observable-only, or depends on incomplete artifacts, the claim must be blocked or downgraded.

## 3. Measure 1: binary observable recovery

### Definition

A binary observable recovery measure tests whether a specific declared observable predicate remains recoverable at a horizon.

Let:

```text
q_P : X -> {0,1}
```

where:

```text
q_P(x) = 1:
  P-distinction is recoverable at x

q_P(x) = 0:
  P-distinction is not recoverable at x
```

For a frontier `F_h(P)`, define:

```text
BOR_h(P; q_P) = 1 if there exists x in F_h(P) such that q_P(x) = 1
BOR_h(P; q_P) = 0 otherwise.
```

A universal-support variant is:

```text
BOR_all_h(P; q_P) = 1 if for all x in F_h(P), q_P(x) = 1
BOR_all_h(P; q_P) = 0 otherwise.
```

The existential and universal variants must not be conflated.

### Detects

```text
whether a declared binary distinction remains present in the frontier;
whether a witness state preserving that distinction remains reachable.
```

### Does not detect

```text
how many distinctions persist;
recoverable identity of a pattern through transport;
non-erasure of other distinctions;
compatibility;
valuerhood;
Omega.
```

### Required artifacts

```text
process_bundle_manifest.csv
observable_manifest.csv
frontier_nodes_by_horizon.csv or exact shard equivalent
state_payload / state observable reconstruction
artifact_completeness_summary.csv
reconstruction_audit_summary.csv
```

### Failure modes

```text
observable chosen after seeing outcome;
existential recovery treated as universal recovery;
state payload unavailable;
frontier truncated;
binary observable too coarse to support intended claim.
```

## 4. Measure 2: frontier distinction count

### Definition

For a declared observable `q`, define the frontier distinction count:

```text
FDC_h(P; q) = | q(F_h(P)) |.
```

This counts how many distinct observable labels appear in the frontier at horizon `h`.

A normalized version is:

```text
FDC_norm_h(P; q) = |q(F_h(P))| / |Z_q|
```

when `Z_q` is finite and declared.

### Detects

```text
quotient-level variety in a reachable frontier;
collapse or expansion of observable support at a horizon;
coarse distinction breadth under q.
```

### Does not detect

```text
persistence across horizons;
transport recoverability;
which earlier distinction became which later distinction;
valuerhood;
compatibility.
```

### Required artifacts

```text
frontier_nodes_by_horizon.csv or shards
observable_manifest.csv
state_to_observable_rows.csv if needed
artifact completeness and reconstruction audits
```

### Failure modes

```text
raw state count mistaken for distinction count;
q too coarse or constant;
q hand-picked to maximize separation;
frontier truncation hides support;
normalization denominator not declared.
```

## 5. Measure 3: persistent distinction count

### Definition

For a horizon window `W`, define the persistent distinction set:

```text
Persist_W(P; q) = intersection_{h in W} q(F_h(P)).
```

The persistent distinction count is:

```text
PDC_W(P; q) = | Persist_W(P; q) |.
```

A recurrent variant uses a frequency threshold `theta`:

```text
Recur_{W,theta}(P; q) = { z in union_{h in W} q(F_h(P)) :
                          z appears in at least theta fraction of horizons in W }

RDC_{W,theta}(P; q) = |Recur_{W,theta}(P; q)|.
```

The persistent and recurrent variants must be reported separately.

### Detects

```text
quotient labels that persist or recur across a horizon window;
loss of observable support through time;
rough temporal stability of frontier distinctions.
```

### Does not detect

```text
same-pattern identity through deformation;
causal maintenance;
anti-dissolution;
self-conditioning;
compatibility.
```

### Required artifacts

```text
frontier_nodes_by_horizon.csv or shards
horizon_schedule
observable_manifest.csv
state_to_observable_rows.csv if needed
artifact completeness and reconstruction audits
```

### Failure modes

```text
window W chosen after seeing persistence;
recurrent threshold theta tuned post hoc;
stationary label mistaken for recoverable dynamic identity;
labels persist because observable is too coarse.
```

## 6. Measure 4: transport-recoverable distinction count

### Definition

Transport-recoverable distinction count measures whether earlier quotient distinctions can be transported or reconstructed at a later horizon.

Let:

```text
T_{h -> k}^q(z,z')
```

be a declared support, count, or mass transport matrix between quotient labels at horizons `h < k`.

Let:

```text
r_{k -> h} : Z_q -> Z_q
```

be a declared reconstruction or inverse-like map when available.

A source label `z in q(F_h(P))` is transport-recoverable at `(h,k)` when there exists `z' in q(F_k(P))` such that:

```text
T_{h -> k}^q(z,z') > 0
and
r_{k -> h}(z') = z
```

For mass-valued transport, require a declared threshold `alpha`:

```text
sum_{z' : r(z') = z} T_{h -> k}^q(z,z') >= alpha.
```

Define:

```text
TRDC_{h,k}(P; q, r) = number of transport-recoverable source labels z.
```

### Detects

```text
whether earlier distinctions can be reidentified through horizon transport;
quotient-level recoverability rather than mere support persistence;
transport concentration or dispersion when mass-valued.
```

### Does not detect

```text
ontological identity;
agency;
valuerhood;
compatibility by itself;
semantic continuity unless q and r are justified.
```

### Required artifacts

```text
raw_transport_matrices_adjacent.npz or manifest-equivalent
raw_transport_matrices_multiscale.npz if non-adjacent
transport_matrix_manifest.csv
observable_manifest.csv
reconstruction_map_manifest.csv
composition_residuals if used
artifact completeness and reconstruction audits
```

### Failure modes

```text
reconstruction map r chosen post hoc;
transport matrix skipped but treated as zero residual;
projection required but not declared;
mass threshold alpha tuned after seeing result;
transport labels mismatch across horizons.
```

## 7. Measure 5: joint-vs-marginal distinction retention

### Definition

For coupled fields with component quotient supports:

```text
A_h = q_A(pi_A(F_h^{joint}))
B_h = q_B(pi_B(F_h^{joint}))
```

and joint quotient support:

```text
J_h = q_{AB}(F_h^{joint}) subset A_h x B_h
```

define marginal distinction retention relative to a product reference:

```text
MR_A(h) = |A_h^{coupled}| / |A_h^{product}|
MR_B(h) = |B_h^{coupled}| / |B_h^{product}|
```

when denominators are nonzero and product reference is declared.

Define joint distinction retention over surviving marginals:

```text
JMR(h) = |J_h| / |A_h x B_h|.
```

`JMR(h) = 1` means the coupled joint field is product-dense over its surviving marginals.

`JMR(h) < 1` means there is sparse joint recombination or joint restriction over surviving marginals.

### Detects

```text
whether joint combinations are retained beyond marginal survival;
whether residuals come from marginal pruning or joint restriction;
product-dense closure over surviving marginals;
pair005-like preserved-marginal joint restriction candidates.
```

### Does not detect

```text
compatibility;
support;
capture;
erasure;
interaction;
valuerhood;
Omega.
```

### Required artifacts

```text
product baseline manifest
coupled operator manifest
coupled_marginal_retention_by_horizon.csv
coupled_joint_vs_product_residual_by_horizon.csv
coupled_joint_frontier_profile_by_horizon.csv
joint_density_vs_marginal_product
artifact completeness and reconstruction audits
```

### Failure modes

```text
zero-penalty joint selector treated as product-neutral;
product reference missing;
marginal denominators zero;
component observables not matched;
JMR interpreted as compatibility;
product-dense over pruned marginals mistaken for marginal-preserving joint restriction.
```

## 8. Optional derived measure: distinction loss against null

When an identity-decay null `N_P` is available, any measure above can be converted into a maintenance gap:

```text
Gap_M(P,H; N_P) = M_K(P,H) - M_{N_P}(P,H).
```

This gap is null-relative and measure-relative.

It supports only the claim allowed by the chosen measure and null family.

Example:

```text
FDC_K(P,h;q) - FDC_{N_P}(P,h;q)
```

may show that actual dynamics preserve more quotient-label breadth than the null.

It does not show self-conditioning, valuerhood, or compatibility.

## 9. Measure strength ladder

The measures form a rough evidential ladder, but not a universal total order.

```text
binary observable recovery:
  weakest; one declared distinction remains reachable

frontier distinction count:
  support breadth under q at one horizon

persistent / recurrent distinction count:
  support stability over a horizon window

transport-recoverable distinction count:
  quotient-level reidentification through horizon transport

joint-vs-marginal distinction retention:
  composition-sensitive distinction structure in coupled fields

measure-plus-null maintenance gap:
  distinction maintenance beyond a declared identity-decay reference
```

A stronger measure can still be invalid if the observable is bad, the artifacts are incomplete, or the null is mismatched.

## 10. Disallowed shortcuts

Do not treat the following as distinction measures by themselves:

```text
raw frontier size;
raw entropy without declared q;
agent labels;
valuer labels;
identity labels;
value labels;
semantic class names;
post hoc response labels;
human-interest labels;
Omega-compatible labels;
```

Do not infer:

```text
higher distinction count = more value;
persistent distinction = identity;
recoverable distinction = agent;
margin preservation = compatibility;
joint restriction = erasure;
product-breaking = interaction;
```

Each stronger interpretation requires its own formal criteria and controls.

## 11. Minimal artifact schema for future runs

Future runs that compute finite distinction measures should emit:

```text
distinction_measure_manifest.csv
process_bundle_manifest.csv if P-designations are used
observable_manifest.csv
state_to_observable_rows.csv or reconstructible equivalent
distinction_measure_by_horizon.csv
distinction_persistence_by_window.csv
transport_recoverable_distinction_summary.csv if transport is used
joint_vs_marginal_distinction_retention.csv if coupled fields are used
artifact_completeness_summary.csv
reconstruction_audit_summary.csv
```

Suggested `distinction_measure_manifest.csv` columns:

```text
measure_id
measure_family
process_bundle_id
observable_id
horizon_regime
perturbation_class_id
required_artifacts_json
normalization_policy
thresholds_json
claim_boundary
```

Suggested `distinction_measure_by_horizon.csv` columns:

```text
measure_id
condition_id
process_bundle_id
observable_id
horizon
measure_value
normalization_denominator
artifact_completeness_status
reconstruction_audit_status
notes
```

## 12. Relation to current Future Field Atlas results

Current FFA already emits some precursor quantities relevant to these measures:

```text
frontier nodes by horizon;
frontier profiles by horizon;
rank-boundary geometry;
transport matrices in selected runs;
coupled joint-vs-product residuals;
marginal retention;
joint density vs marginal product;
artifact completeness summaries;
reconstruction audits.
```

But current FFA does not yet emit a general `process_bundle_manifest`, identity-decay-null comparisons, or full finite distinction-measure manifests.

Therefore current FFA results remain precursor geometry only.

## 13. Claim ladder supported by finite measures

### 13.1 Distinction visibility

Allowed:

```text
A declared observable distinguishes frontier structure under the specified condition.
```

Blocked:

```text
recoverability;
identity;
valuerhood;
Omega.
```

### 13.2 Distinction persistence

Allowed:

```text
A declared observable distinction persists or recurs over the horizon window.
```

Blocked:

```text
active maintenance;
self-conditioning;
compatibility.
```

### 13.3 Transport recoverability

Allowed:

```text
A declared quotient-level distinction can be reconstructed through the specified transport map.
```

Blocked:

```text
ontological identity;
agency;
valuerhood.
```

### 13.4 Joint-vs-marginal distinction structure

Allowed:

```text
The coupled joint field is product-dense or joint-restrictive over surviving marginals under the declared observables.
```

Blocked:

```text
support;
capture;
erasure;
compatibility;
interaction.
```

### 13.5 Measure-plus-null gap

Allowed:

```text
Actual dynamics preserve the declared distinction measure better than the declared identity-decay null.
```

Blocked unless separately shown:

```text
self-conditioning;
valuerhood;
Omega-compatible completion.
```

## 14. Falsifiers and blockers

Finite distinction-measure claims weaken or fail if:

```text
observable q is constant or too coarse;
q is chosen after seeing the result;
state-to-observable reconstruction fails;
frontier topology is truncated_noninterpretable;
measure depends on deleted raw data without exact rebuild;
thresholds are tuned after seeing the result;
normalization denominator is undeclared;
measure is interpreted beyond its claim boundary;
measure does not reproduce under matched controls.
```

## 15. Next theorem targets

This measure menu enables more concrete theorem and implementation work.

Candidate next notes:

```text
Finite Measure Separation Theorems v0:
  show binary recovery, frontier count, persistence, and transport recoverability
  do not collapse into one another.

Tiny Transition Systems with Measures v0:
  compute the measures in explicit small systems from the witness note.

Future Field Atlas Distinction Measure Spec:
  define the first instrument artifacts for distinction_measure_manifest and
  distinction_measure_by_horizon.
```

## 16. Summary

This note restricts `M_Q(D_t(P))` to a small finite menu for early theorem and instrument work.

Compact conclusion:

```text
Distinction-content must be measured through declared observables, horizons, and
reconstructible artifacts.

The initial admissible finite measures are binary observable recovery, frontier
distinction count, persistent/recurrent distinction count, transport-recoverable
distinction count, and joint-vs-marginal distinction retention.

None of these measures detects value, valuerhood, agency, identity, compatibility,
or Omega by itself.
```
