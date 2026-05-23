# RFS-MB0 Neutral Transform Reset Spec

Status: corrected implementation spec after semantic substrate drift

Purpose: reset the MB0 empirical substrate to neutral primitive dynamics before continuing pairwise compatibility work

## 0. Why this reset exists

The first MB0 pairwise smoke successfully validated the runner/workflow, but the substrate drifted into semantic toy language:

```text
alive
strained
damaged
lost
captured
shared
hazard
repair
mutual support
capture
```

That is not the intended object.

The Omega empirical arm is supposed to begin from neutral primitive dynamics and ask which derived identities persist through transformation.

The substrate should not label transformations as good, bad, harmful, supportive, repaired, degraded, captured, alive, dead, or anything morally/biologically suggestive.

The corrected principle is:

```text
Apply neutral transformations.
Derive candidate identities.
Measure which identities persist and co-persist.
Interpret only after controls.
```

This reset supersedes the semantic toy substrate for future MB0 work.

The old smoke branch remains useful as workflow validation only.

## 1. Core discipline

```text
principled
parsimonious
predictive
```

Principled:
  all measured structure must derive from primitives plus declared probe machinery.

Parsimonious:
  no semantic state labels, no value labels, no built-in support/recover/degrade language.

Predictive:
  the probe must separate persistence/co-persistence profiles from controls without using labels that already imply the answer.

## 2. Forbidden implementation language

Do not use these terms in substrate state names, transition names, generator names, readout bins, or endpoint classes:

```text
alive
strained
damaged
lost
dead
captured
capture
repair
hazard
support
harm
help
recover
degrade
improve
worse
better
health
viability
agent
valuer
Omega
pseudo-Omega
```

Some of these concepts may later be derived or interpreted, but they must not appear as primitive state or transition labels in MB0.

Use neutral language instead:

```text
coordinate
band
block
signature
transform
operation
relation
constraint
endpoint
delta
exits_band
enters_band
co-persists
contracts
expands
flatlines
```

## 3. Primitive substrate

The primitive substrate is:

```text
S = (X, T)
```

where:

```text
X:
  finite distinction configurations

T:
  finite set/family of neutral transformations
```

A transition relation is induced by transformations:

```text
x -> y iff exists t in T such that y in t(x)
```

States should be neutral finite tuples, for example:

```text
x = (q0, q1, q2, ..., qk, phase)
```

where each coordinate ranges over a small finite alphabet.

Coordinates may have declared ordinal or modular structure only if used operationally and neutrally:

```text
band coordinate:
  values 0..m with declared continuity bands

modular coordinate:
  values modulo m

block coordinate:
  grouped only for transformation/signature extraction tests
```

Do not name coordinates by biological, moral, or functional roles.

## 4. Neutral transformations

Transformations should be operationally named, not semantically named.

Allowed examples:

```text
shift_i(+1)
shift_i(-1)
rotate_i
swap_i_j
copy_i_to_j
project_i_to_const
merge_i_j
split_i
couple_i_j
anti_couple_i_j
scramble_block
contract_block
expand_block
phase_advance
identity_op
```

These names describe formal action on coordinates only.

They do not say whether the transformation helps, harms, repairs, supports, captures, or degrades anything.

## 5. Derived identity extraction

The extractor remains probe-side but must be a functional of the neutral substrate:

```text
E_sigma = Extract_sigma(X, T)
E_sigma(S) -> M_sigma
```

Each candidate identity is a derived relational/signature object:

```text
mu in M_sigma
```

A candidate may be represented as:

```text
mu = (support_mu, signature_mu)
```

where:

```text
support_mu(x):
  neutral coordinate/block support or relational footprint

signature_mu(x):
  neutral relational/transform signature used for continuity
```

The extractor must not use semantic labels or post-hoc readout classes.

Candidate extractor families for MB0 reset may be simple:

```text
coordinate-block signatures
local transition-role signatures
small relational motifs
invariant/approximately invariant coordinate relations
blockwise response profiles under T
```

The exact extractor may be crude in the first reset run, but it must be declared before evaluation and tested against controls.

## 6. Identity continuity

Identity continuity should be expressed as signature equivalence:

```text
signature_mu(x_t) ~=_sigma signature_mu(x_0)
```

For MB0 reset, use token continuity only.

Define:

```text
A_mu(x0) = { x in X : signature_mu(x) ~=_sigma signature_mu(x0) }
```

Do not define continuity using semantic status sets like:

```text
alive/strained/damaged
```

If continuity bands are needed, they must be neutral bands over coordinates and explicitly declared:

```text
coordinate q_i remains in band B_i
relation q_i - q_j remains in allowed residue class
block signature remains equivalent under declared quotient
```

## 7. Futures to compute

Compute singleton identity-preserving futures:

```text
F_H^mu(x0) =
  { y in X :
      exists path x0 -> ... -> y of length <= H
      such that every state on the path lies in A_mu(x0) }
```

Compute pairwise joint identity-preserving futures:

```text
F_H^{mu,nu}(x0) =
  { y in X :
      exists path x0 -> ... -> y of length <= H
      such that every state on the path lies in A_mu(x0) and A_nu(x0) }
```

Also compute exact-H frontiers:

```text
Exact_H^mu(x0)
Exact_H^nu(x0)
Exact_H^{mu,nu}(x0)
```

The core question remains:

```text
Can two derived identities persist together through neutral transformations?
```

## 8. Endpoint-change audit, not semantic taxonomy

Do not classify endpoints as support/recover/degrade.

Instead report neutral endpoint-change descriptors.

For state:

```text
x = (q0, q1, ..., qk, phase)
```

report:

```text
changed_coordinate_count
changed_nonphase_coordinate_count
changed_support_mu_count
changed_support_nu_count
changed_outside_support_count
mu_signature_changed
nu_signature_changed
mu_exits_continuity_band
nu_exits_continuity_band
joint_exits_continuity_band
phase_only_change
nonphase_change
block_relation_changed
```

If ordinal bands are declared, report only neutral movement relative to declared bands:

```text
q_i_delta
q_i_moves_toward_band_boundary
q_i_moves_away_from_band_boundary
q_i_exits_band
q_i_enters_band
```

Do not call these improvement, degradation, repair, support, or harm.

Endpoint descriptors are explanatory diagnostics only. They must not define success.

## 9. Horizon-filtration diagnostics

Because relation induces path geometry, report futures across horizons:

```text
H = 0, 1, 2, 4, 8, 12, 16
```

Report curves:

```text
H -> |F_H^mu|
H -> |F_H^nu|
H -> |F_H^{mu,nu}|
H -> |Exact_H^mu|
H -> |Exact_H^nu|
H -> |Exact_H^{mu,nu}|
```

Report neutral geometry summaries:

```text
first_mu_H
first_nu_H
first_joint_H
first_nonphase_joint_H
joint_delay
exact_joint_delay
joint_flatline_flag
joint_saturates_early_flag
last_joint_change_H
```

Path geometry is diagnostic, not objective.

Do not define success as shorter path length.

## 10. Neutral transform families for reset smoke

Implement a small set of neutral transform families designed to test persistence/co-persistence without semantic labels.

Suggested families:

### 10.1 independent_block_transforms

Coordinates in block A and block B transform independently.

Expected use:

```text
baseline for independent persistence
```

### 10.2 coupled_block_transforms

A/B block transformations preserve a shared neutral relation, such as equality, residue, parity, or bounded difference.

Expected use:

```text
baseline for co-persistence under coupling
```

### 10.3 anti_correlated_block_transforms

Transformations that preserve one block signature tend to alter the other block signature by construction.

Do not call this capture or harm.

Expected use:

```text
neutral analog of local-preserving / joint-contracting pressure
```

### 10.4 shared_constraint_conflict

A and B each have preserving transformations that require incompatible values of a neutral shared coordinate.

Expected use:

```text
pairwise co-persistence contraction without semantic labels
```

### 10.5 phase_cycle_control

Only phase-like coordinates cycle while nonphase signatures remain unchanged.

Expected use:

```text
clock/phase fakeout control
```

### 10.6 fixed_point_control

Transformations collapse states into fixed points or tiny recurrent sets.

Expected use:

```text
stasis/terminal persistence control
```

### 10.7 random_transform_control

Random transformations with matched edge count.

Expected use:

```text
raw graph-density control
```

### 10.8 degree_preserving_transform_control

Scramble targets while preserving degree sequence.

Expected use:

```text
degree/control artifact test
```

### 10.9 equivalence_permissive_control

Use an overbroad continuity relation.

Expected use:

```text
permissive identity fakeout control
```

### 10.10 equivalence_strict_control

Use exact-state or near-exact continuity.

Expected use:

```text
overstrict identity fakeout control
```

## 11. Result bins

Use neutral result bins only:

```text
singleton_persists
pair_persists
singleton_overcall
pairwise_contracted
local_mu_persists_joint_contracts
local_nu_persists_joint_contracts
phase_only_persistence
fixed_point_persistence
permissive_equivalence_artifact
strict_equivalence_artifact
random_control_mimic
```

Avoid:

```text
mutual_support_like
capture_like
recovery
degradation
harm
Omega-positive
pseudo-Omega
```

## 12. Success criteria for reset smoke

Minimal reset success:

```text
neutral substrate implemented
semantic labels removed
singleton and pairwise filtrations computed
phase/fixed/permissive controls identified by neutral diagnostics
```

Scientific success for current gate:

```text
some neutral transform families show singleton persistence with joint contraction
and this pattern separates from random/degree/permissive/strict controls
```

Failure:

```text
pairwise filtrations add no information beyond singleton filtrations
controls mimic all structured transform families
continuity extractor dominates outcomes
```

If failure occurs, revise extractor or transform families before adding machinery.

## 13. What not to implement yet

Do not implement:

```text
full compatibility lattice
three or more identities
lineage/churn
support/recovery/degradation taxonomy
weighted cost
resource budget
thermodynamic model
valuerhood
agency
Omega score
```

The reset is about restoring substrate neutrality.

## 14. Implementation target

Preferred new package path:

```text
omega/rfs_mb0_neutral_transform/
```

Suggested files:

```text
substrate.py
extractors.py
exact.py
run_smoke.py
```

Responsibilities:

```text
substrate.py:
  neutral state enumeration and transformation families

extractors.py:
  declared E_sigma extractor families and continuity predicates

exact.py:
  reachable futures, exact-H frontiers, pairwise futures, filtration diagnostics

run_smoke.py:
  batch runner, controls, summaries, checkpoint/salvage behavior
```

Do not continue evolving the semantic `rfs_mb0_pairwise` substrate as the main empirical branch.

It may remain as an archived workflow smoke.

## 15. Claim boundary

Allowed after reset smoke:

```text
We implemented a neutral finite transformation substrate and measured singleton
and pairwise identity-preserving horizon filtrations for derived candidate signatures.
```

Allowed if supported:

```text
Pairwise co-persistence detected contractions that singleton persistence missed
under neutral transform families and controls.
```

Not allowed:

```text
Omega detected
pseudo-Omega detected
support/recovery/degradation detected
valuerhood detected
agency detected
```

## 16. Bottom line

The empirical arm should look like nature:

```text
neutral transformations occur
some patterns persist
some patterns dissolve
some patterns co-persist
some patterns exclude each other
```

Labels come later, if earned.

MB0 reset returns to that discipline.
