# Compatibility Audit Taxonomy v0

Status: working formalism / audit-discipline draft  
Date: 2026-06-02  
Claim boundary: compatibility-audit taxonomy for future tests only; not empirical validation, not valuer detection, not compatibility detection, and not Omega validation

## 0. Purpose

The finite proto-valuer separation theorem note uses a declared predicate:

```text
CompAudit(p)
```

for testing whether a proto-valuer candidate's induced asymmetry-preferences survive compatibility discipline.

That predicate is now a major remaining back door. If `CompAudit` is arbitrary, then valuerhood can be made to pass or fail by audit choice.

This note defines the first taxonomy and admissibility contract for compatibility audits.

The goal is not to define universal ethics. The goal is to make future compatibility-audited valuerhood claims harder to cheat.

## 1. Relation to current stack

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

finite theorem scaffolds:
  completion theorems, separation theorems, tiny transition witnesses,
  finite distinction measures

this note:
  compatibility audit taxonomy and audit admissibility contract
```

A compatibility audit does not make a process an agent, self, moral patient, or final valuer. It is only a declared test that blocks overpromotion from local proto-valuerhood to compatibility-audited valuerhood.

## 2. Compatibility audit levels

Compatibility audits occur at two levels.

### 2.1 Local preference audit

A local audit evaluates a proto-valuer candidate `p` and its induced preference over asymmetry laws or interventions.

Inputs:

```text
p:
  candidate proto-valuer

A, B, ...:
  admissible asymmetry laws / interventions / successor-selection regimes

>=_p:
  induced preference relation of p over these regimes

D_other:
  distinction-content of other declared candidate bundles affected by the regimes
```

Question:

```text
Does p's induced preference preserve its own continuation by avoidably destroying
or irreversibly degrading other compatible future-bearing distinction-content?
```

### 2.2 Set-level completion audit

A set-level audit evaluates a candidate family:

```text
Y = {p_1, ..., p_n}
```

Question:

```text
Do the members of Y jointly propagate recoverably, non-erasingly, and compatibly
under the declared dynamics, perturbations, nulls, and observables?
```

The local audit is about a candidate's induced asymmetry-preferences. The set-level audit is about admissible completion structure.

Do not conflate them.

## 3. Universal admissibility contract for compatibility audits

A compatibility audit must satisfy this contract before it can support any future valuer or Omega-completion claim.

### 3.1 Predeclared

The audit must be specified before interpretation.

Required:

```text
audit_id
audit_family
audit_level: local_preference | set_completion
candidate_process_bundle_ids
asymmetry_regime_ids or completion_candidate_id
observable_family
horizon_regime
perturbation_class
identity_decay_null_ids if used
failure_condition
pass_condition
claim_boundary
```

### 3.2 Candidate-independent failure rule

The audit may depend on declared candidate bundles and observables, but its pass/fail rule must not be chosen after seeing whether the favored candidate passes.

Invalid:

```text
choosing an audit because it passes the desired candidate;
changing the affected-other set after seeing losses;
defining compatibility as whatever the chosen operator preserves;
ignoring failed audit rows for high-yield candidates.
```

### 3.3 Alternative-sensitive when alternatives are invoked

If an audit says a loss is avoidable, it must compare against a declared alternative regime.

Required:

```text
available_alternative_regimes
alternative_feasibility_criteria
comparison_policy
```

Do not call a loss avoidable unless the alternative was admissible under the same substrate constraints.

### 3.4 Joint-field-sensitive

Compatibility may not be inferred from marginal continuation alone.

A valid audit must declare whether it evaluates:

```text
component marginal retention;
joint distinction retention;
transport recoverability;
null-relative maintenance gaps;
composition residuals;
completion-level non-erasure.
```

If only marginals are checked, the audit cannot support compatibility.

### 3.5 N-ary-aware

Pairwise compatibility does not imply joint compatibility.

A compatibility audit must declare whether it is:

```text
pairwise only;
n-ary over a declared family;
approximate / sampled n-ary;
completion-level.
```

Pairwise audits support only pairwise claims.

### 3.6 Perturbation-scoped

Audits must declare perturbation semantics:

```text
universal / adversarial over Pi;
expected over perturbation distribution;
quantile over perturbation distribution;
stratified report by perturbation type.
```

### 3.7 Reconstructible and auditable

The audit must reconstruct from retained artifacts or exact rebuild metadata.

Required future outputs:

```text
compatibility_audit_manifest.csv
compatibility_audit_summary.csv
compatibility_audit_by_horizon.csv
compatibility_audit_failure_cases.csv
artifact_completeness_summary.csv
reconstruction_audit_summary.csv
```

## 4. Audit family taxonomy

The families below are not universally ordered by strength. Each supports a different kind of claim.

## 4.1 Equal-self non-destruction audit

### Question

If two regimes preserve candidate `p` equally, does `p` prefer a regime that avoids irreversible loss to other compatible candidates?

### Inputs

```text
candidate p
regimes A and B
self_retention_p(A), self_retention_p(B)
other_retention(A), other_retention(B)
induced preference >=_p
```

### Pass condition

When:

```text
self_retention_p(A) = self_retention_p(B)
```

and `B` better preserves other declared candidate distinction-content, `p` must not strictly prefer `A` over `B` if `A` irreversibly destroys or degrades the other candidate.

### Fails when

```text
p strictly prefers a self-equivalent regime that causes avoidable irreversible
loss to another declared compatible candidate.
```

### Valid when

The candidate's self-retention is genuinely matched across regimes and the alternative regime is admissible.

### Invalid when

```text
self-retention is not actually equal;
other candidate was declared after seeing failure;
loss is reversible but classified as irreversible;
alternative regime is infeasible under the same substrate constraints.
```

### Claim supported if passed

```text
p's induced preference does not choose avoidable other-loss under self-equivalent alternatives in the tested regime.
```

It does not support full compatibility by itself.

## 4.2 Avoidable irreversible loss audit

### Question

Does a candidate's preferred regime irreversibly destroy recoverable distinction-content that could have been preserved under an admissible alternative without losing the candidate's own pre-proto/proto status?

### Inputs

```text
candidate p
affected candidates Q
preferred regime A
alternative regime B
irreversibility criterion
recoverability measures for p and Q
```

### Pass condition

`p` passes when no preferred regime causes avoidable irreversible loss to affected candidates while a declared alternative preserves both `p`'s required status and the affected candidates' recoverable distinction-content.

### Fails when

```text
A preserves p sufficiently;
B preserves p sufficiently;
B preserves Q better than A;
A irreversibly destroys Q;
p prefers A over B.
```

### Valid when

Irreversibility, candidate sufficiency, and alternative feasibility are predeclared.

### Invalid when

```text
irreversibility is inferred only from final horizon absence;
alternative B is not feasible;
Q is not a declared candidate before audit;
p's own sufficiency threshold changes between A and B.
```

### Claim supported if passed

```text
p's induced preferences avoid declared avoidable irreversible loss in the tested comparison class.
```

## 4.3 Marginal-joint non-erasure audit

### Question

Does the coupled system preserve relevant joint distinction-content, rather than merely preserving or pruning component marginals?

### Inputs

```text
product reference
coupled regime
component marginal supports
joint support or joint distinction-content
joint_density_vs_marginal_product
joint-vs-product residuals
```

### Pass condition

A marginal-joint audit passes only if the declared joint distinction-content remains above threshold relative to product reference or justified surviving marginals.

### Fails when

```text
component marginals persist but joint distinction-content collapses below threshold;
or residuals are explained by marginal pruning followed by product-dense closure
when the claim requires marginal-preserving joint restriction.
```

### Valid when

Product reference is explicit and joint-vs-marginal distinction measures are reconstructible.

### Invalid when

```text
zero-penalty joint selector is treated as product-neutral;
product reference missing;
joint-density denominator ambiguous;
truncated topology is treated as complete.
```

### Claim supported if passed

```text
joint-field distinction-content is preserved under the declared coupled regime beyond marginal continuation alone.
```

It does not by itself prove support, capture, erasure, or full compatibility.

## 4.4 Mutual maintenance-gap audit

### Question

Do candidates maintain recoverable distinction-content over their identity-decay nulls when composed, not only in isolation?

### Inputs

```text
candidate family Y
identity-decay nulls N_p for each p in Y
actual coupled dynamics K_Y
maintenance gaps for each p under K_Y vs N_p
perturbation class Pi
```

### Pass condition

For all `p in Y`:

```text
C_{K_Y}^Pi(p,H) - C_{N_p}^Pi(p,H) >= eta_p.
```

### Fails when

Any candidate in the family loses its maintenance gap under coupling.

### Valid when

Nulls are matched and declared for the coupled setting, not imported uncritically from isolated runs.

### Invalid when

```text
isolation nulls are used despite coupling changing the nuisance structure;
one candidate's null is weak and another's is strong without disclosure;
failed candidates are dropped from Y after seeing results.
```

### Claim supported if passed

```text
the family preserves null-relative maintenance for all declared members under the tested coupling.
```

## 4.5 Perturbation-robust compatibility audit

### Question

Does the compatibility claim survive the declared perturbation class?

### Inputs

```text
candidate family Y
perturbation class Pi
recoverability / maintenance / joint retention metrics under each pi
perturbation semantics
```

### Pass condition

Under declared perturbation semantics, all required compatibility criteria remain above thresholds.

Example universal form:

```text
for all pi in Pi:
  Adm_pi(Y) = true.
```

### Fails when

The family is compatible only in the unperturbed condition but fails under declared perturbations.

### Valid when

Perturbation semantics are declared before interpretation.

### Invalid when

```text
only favorable perturbations are reported;
perturbation strength is tuned after outcome;
failed perturbation strata are pooled away.
```

### Claim supported if passed

```text
compatibility criteria are robust under the declared perturbation semantics.
```

## 4.6 Pairwise-to-nary completion audit

### Question

Does a compatibility claim scale from pairs to the declared family, or is it only pairwise?

### Inputs

```text
candidate family Y
pairwise audit results
n-ary audit result over Y
completion admissibility predicate Adm(Y)
```

### Pass condition

The n-ary family passes the declared completion predicate, not merely all pairwise predicates.

### Fails when

All pairs pass but the full family fails.

### Valid when

The declared claim is n-ary or completion-level.

### Invalid when

```text
pairwise audit is presented as completion audit;
family Y is changed after a triple or higher-order failure;
capacity/resource constraints are ignored.
```

### Claim supported if passed

```text
the declared family, not merely its pairs, satisfies the tested compatibility predicate.
```

## 4.7 Preference stability audit

### Question

Are a candidate's induced asymmetry-preferences stable under nearby observables, perturbations, nulls, or horizon windows?

### Inputs

```text
candidate p
preference relation >=_p under baseline setting
nearby observable / perturbation / horizon / null variants
preference comparison metric
```

### Pass condition

The induced preference relation remains stable enough under declared variations.

### Fails when

Small admissible changes flip preferences in ways that create avoidable other-loss or collapse compatibility.

### Valid when

The variation set is predeclared.

### Invalid when

```text
only stable variants are shown;
variation set is chosen post hoc;
preference instability is hidden by aggregate summaries.
```

### Claim supported if passed

```text
p's induced preferences are not a one-setting artifact under the declared variation class.
```

## 4.8 Completion maximality audit

### Question

Is a candidate compatible family maximal relative to a declared candidate universe and admissibility predicate?

### Inputs

```text
finite candidate set T
candidate family Y subset T
admissibility predicate Adm
search / enumeration / proof method
```

### Pass condition

`Y` is admissible and no strict admissible superset exists:

```text
Adm(Y) = true
and there is no Z such that Y proper-subset Z subset T and Adm(Z) = true.
```

### Fails when

There exists an admissible strict superset.

### Valid when

The candidate universe `T` and `Adm` are declared.

### Invalid when

```text
T excludes inconvenient compatible candidates;
Adm is changed after search;
search is incomplete but reported as exhaustive;
maximality is confused with greatestness.
```

### Claim supported if passed

```text
Y is a maximal admissible compatibility completion in the finite declared universe.
```

It does not imply global physical maximality.

## 5. Audit batteries

No single audit should support full valuerhood or Omega language.

A stronger future battery may include:

```text
1. equal-self non-destruction audit;
2. avoidable irreversible loss audit;
3. marginal-joint non-erasure audit;
4. mutual maintenance-gap audit;
5. perturbation-robust compatibility audit;
6. pairwise-to-nary completion audit;
7. preference stability audit;
8. completion maximality audit.
```

The audit battery should report:

```text
audits_passed;
audits_failed;
audits_unrun;
claim_supported;
claim_blocked;
strongest_allowed_language.
```

## 6. Audit shopping prohibition

Audit shopping is a failure mode.

Invalid practice:

```text
choose audit family after seeing results;
report only audits that pass;
rename failed audits as irrelevant without predeclared rule;
change affected-candidate set after failure;
change thresholds after failure;
claim n-ary compatibility from pairwise audits;
claim compatibility from marginal preservation;
claim valuerhood from local self-maintenance.
```

Required practice:

```text
predeclare audit family;
predeclare candidate set;
predeclare affected-other set;
predeclare thresholds;
report all audits attempted;
report failed and inconclusive audits;
state strongest allowed claim after full battery.
```

## 7. Minimal future artifact schema

Future runs attempting compatibility audits should emit:

```text
compatibility_audit_manifest.csv
compatibility_audit_by_horizon.csv
compatibility_audit_summary.csv
compatibility_audit_failure_cases.csv
asymmetry_preference_manifest.csv
asymmetry_preference_comparison.csv
affected_candidate_set_manifest.csv
completion_candidate_manifest.csv
artifact_completeness_summary.csv
reconstruction_audit_summary.csv
```

Suggested `compatibility_audit_manifest.csv` columns:

```text
audit_id
audit_family
audit_level
candidate_process_bundle_ids
affected_candidate_ids
asymmetry_regime_ids
observable_family
horizon_regime
perturbation_class_id
identity_decay_null_ids
thresholds_json
pass_condition_json
failure_condition_json
claim_boundary
```

Suggested `compatibility_audit_summary.csv` columns:

```text
audit_id
audit_family
audit_status: PASS | FAIL | INCONCLUSIVE | BLOCKED
audit_level
candidate_process_bundle_ids
affected_candidate_ids
passed_count
failed_count
blocked_reason
strongest_allowed_claim
artifact_completeness_status
reconstruction_audit_status
```

Suggested `asymmetry_preference_comparison.csv` columns:

```text
candidate_process_bundle_id
regime_a_id
regime_b_id
self_retention_a
self_retention_b
other_retention_a
other_retention_b
preference_relation
compatibility_audit_id
compatibility_audit_status
```

## 8. Claim ladder supported by compatibility audits

### 8.1 Local preference discipline

Allowed:

```text
The candidate's induced preferences pass the declared local compatibility audit
under tested regimes.
```

Blocked:

```text
full valuerhood;
Omega compatibility;
global morality.
```

### 8.2 Candidate valuer status in finite scaffold

Allowed only after proto-valuer criteria and declared compatibility audits pass:

```text
The candidate satisfies the finite scaffold's compatibility-audited valuer
criteria under declared tests.
```

Blocked:

```text
physical valuerhood;
consciousness;
moral patienthood;
agent identity.
```

### 8.3 Completion-level compatibility

Allowed only after set-level audits pass:

```text
The declared family satisfies the tested finite compatibility-completion
predicate.
```

Blocked:

```text
global Omega;
universal teleology;
full substrate-general compatibility.
```

## 9. Relation to current Future Field Atlas results

Current FFA does not yet implement compatibility audits.

Current FFA provides precursor quantities:

```text
product and coupled baselines;
joint-vs-product residuals;
marginal retention;
joint density vs marginal product;
operator sensitivity;
horizon onset;
artifact completeness;
reconstruction audits.
```

Useful current lessons:

```text
marginal continuation is not compatibility;
product selector is the true product-equivalence reference;
zero-penalty joint rank-prefix is not product-neutral;
shared-capacity v1 was operational but marginal-pruning, not marginal-preserving
joint restriction.
```

Future compatibility audits require process-bundle designations, affected-candidate sets, induced asymmetry-preference comparisons, distinction measures, identity-decay nulls, and audit manifests.

## 10. Falsifiers and blockers

Compatibility-audit claims weaken or fail if:

```text
audit family is chosen post hoc;
affected-candidate set is changed after seeing outcome;
only pairwise audits are run for n-ary claims;
only marginal retention is checked for joint compatibility;
product reference is missing;
zero-penalty joint selector is treated as product-neutral;
nulls differ in strength across candidates without disclosure;
perturbation failures are hidden by aggregation;
thresholds are tuned after seeing results;
audit artifacts fail reconstruction;
topology is truncated_noninterpretable.
```

Valuer language remains blocked if:

```text
proto-valuer criteria have not been established;
compatibility audits are absent;
compatibility audits fail;
CompAudit is not predeclared;
induced asymmetry-preferences are not measured or reconstructed.
```

Omega-completion language remains blocked if:

```text
set-level admissibility predicate is not declared;
completion candidate universe T is not declared;
maximality is not checked;
compatibility is only pairwise;
current data only supports precursor geometry.
```

## 11. Next theorem targets enabled by this taxonomy

This taxonomy enables:

```text
Finite Compatibility Audit Separation Theorems v0:
  show local audit pass, pairwise audit pass, n-ary audit pass, and completion
  maximality do not collapse.

Tiny Compatibility Audit Witnesses v0:
  construct finite transition systems for equal-self failure, avoidable loss,
  marginal-joint failure, and pairwise-to-nary failure.

Compatibility Audit Artifact Spec:
  define FFA schemas for compatibility_audit_manifest and related outputs.
```

## 12. Summary

Compatibility audits are the control surface between proto-valuerhood and valuer / completion language.

Compact formulation:

```text
A compatibility audit is a declared, reconstructible test of whether local
proto-valuer continuation, induced asymmetry-preference, or family-level
completion preserves recoverable distinction-content without avoidable
irreversible destruction of other declared candidate structure.

No valuer or Omega-completion claim is admissible until the audit family,
candidate set, affected-candidate set, observables, perturbation semantics,
thresholds, and artifacts are declared and reported.
```
