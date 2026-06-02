# Finite Proto-Valuer Separation Theorems v0

Persistence, Recoverability, Maintenance Gap, Self-Conditioning, and Compatibility Are Distinct

Status: finite theorem scaffold / theory-arm draft  
Date: 2026-06-02  
Claim boundary: mathematical scaffolding only; not empirical validation, not proto-valuer detection, not valuer detection, and not Omega validation

## 0. Purpose

This note proves first-pass separation results for the proto-valuer ladder.

It does **not** prove that any current Future Field Atlas result instantiates a pre-proto-valuer, proto-valuer, valuer, agent, identity, value-bearing structure, compatibility relation, or Omega object.

It proves that the ladder properties are formally distinct in finite evaluation models:

```text
persistence
recoverability
maintenance gap against identity-decay null
self-conditioning toward future pre-proto-valuerhood
compatibility-audited valuerhood
Omega-compatible completion
```

The goal is to make the claim boundary theorem-backed:

```text
we do not call persistent structures valuers merely by caution;
persistence and valuerhood are formally separable properties.
```

## 1. Relation to current stack

Current stack:

```text
v0.2:
  Future-Distinction Dynamics

admissibility enrichment:
  process bundles, activity channels, identity-decay nulls, maintenance gaps

identity-decay null taxonomy:
  passive, ablation, randomized-activity, matched-marginal, product-composition,
  unsupported-evolution, and degree/frontier-size matched nulls

finite completion theorems:
  maximal completions exist in finite systems; greatest completion need not;
  pairwise compatibility and marginal continuation are insufficient

this note:
  finite separations among persistence, pre-proto-valuerhood, proto-valuerhood,
  valuerhood, and completion-level compatibility
```

This note relies on the null taxonomy only schematically. It uses finite score tables rather than a full implemented Future Field Atlas null battery.

## 2. Finite evaluation model

### Definition 2.1: Candidate process-bundle token

Let `P` be a finite set of candidate process-bundle tokens.

An element `p in P` is a declared candidate designation. It is not assumed to be an agent, identity, valuer, self, or boundary.

### Definition 2.2: Perturbation class

Let `Pi` be a finite set of perturbation labels.

One element may be called `id` or `unperturbed`, but this is optional.

### Definition 2.3: Distinction content measure

For each candidate `p`, let:

```text
M(p) >= 0
```

be the measured initial distinction-content of `p` under a declared observable family.

`M(p) > 0` means `p` carries nontrivial distinction-content at the start of the test.

### Definition 2.4: Actual and null maintenance scores

For each candidate `p` and perturbation `pi in Pi`, let:

```text
C_K(p, pi) >= 0
C_N(p, pi) >= 0
```

where:

```text
C_K(p, pi):
  recoverable distinction-maintenance under actual or activity-present dynamics

C_N(p, pi):
  recoverable distinction-maintenance under the matched identity-decay null N_p
```

### Definition 2.5: Persistence

Fix a baseline perturbation `id in Pi`.

A candidate `p` is **persistent** when:

```text
C_K(p, id) > 0.
```

This is deliberately weak. It only says some recoverable distinction-content remains under actual dynamics in the baseline condition.

### Definition 2.6: Perturbation-robust recoverability

Fix a threshold `rho > 0`.

A candidate `p` is **perturbation-robustly recoverable** when:

```text
for all pi in Pi:
  C_K(p, pi) >= rho.
```

This finite version abstracts the probabilistic condition used in the higher-level notes.

### Definition 2.7: Maintenance gap

Fix a threshold `eta > 0`.

A candidate `p` has a **maintenance gap** over its identity-decay null when:

```text
for all pi in Pi:
  C_K(p, pi) - C_N(p, pi) >= eta.
```

This is the finite version of:

```text
C_K^Pi(P,H) - C_{N_P}^Pi(P,H) >= eta.
```

### Definition 2.8: Pre-proto-valuer

A candidate `p` is a **pre-proto-valuer** when all three conditions hold:

```text
1. M(p) > 0;
2. p is perturbation-robustly recoverable;
3. p has a maintenance gap over its matched identity-decay null.
```

### Definition 2.9: Self-conditioning

For each candidate `p`, let:

```text
S_act(p) in [0,1]
S_pass(p) in [0,1]
```

where:

```text
S_act(p):
  probability, score, or indicator that p satisfies future pre-proto-valuer
  criteria under p-associated activity-present dynamics

S_pass(p):
  corresponding score under matched passive / non-self-conditioning dynamics
```

Fix `gamma > 0`.

`p` satisfies **self-conditioning** when:

```text
S_act(p) - S_pass(p) >= gamma.
```

### Definition 2.10: Proto-valuer

A candidate `p` is a **proto-valuer** when:

```text
p is a pre-proto-valuer;
p satisfies self-conditioning.
```

### Definition 2.11: Compatibility audit and valuerhood

Let `CompAudit(p)` be a declared compatibility-audit predicate for induced asymmetry-preferences of `p`.

A candidate `p` is a **valuer** in this finite scaffold when:

```text
p is a proto-valuer;
CompAudit(p) holds.
```

This does not define final valuerhood. It only captures the current ladder requirement that full valuer language must survive compatibility audits.

### Definition 2.12: Completion admissibility

For a finite set `Y subset P`, let `Adm(Y)` be a declared compatibility-completion predicate.

`Adm(Y)` may depend on recoverability, non-erasure, compatibility, maintenance gaps, or other declared criteria.

This note uses `Adm` only for separation examples.

## 3. Theorem 1: persistence does not imply pre-proto-valuerhood

### Statement

There exists a finite evaluation model in which a candidate is persistent but is not a pre-proto-valuer.

### Construction

Let:

```text
P = {p}
Pi = {id}
rho = 1
eta = 1/2
```

Set:

```text
M(p) = 1
C_K(p, id) = 1
C_N(p, id) = 1
```

### Proof

Since:

```text
C_K(p, id) = 1 > 0,
```

`p` is persistent.

Since `Pi` contains only `id`, perturbation-robust recoverability also holds at threshold `rho = 1`:

```text
C_K(p, id) = 1 >= rho.
```

But the maintenance gap is:

```text
C_K(p, id) - C_N(p, id) = 1 - 1 = 0 < eta.
```

Therefore `p` fails the maintenance-gap condition and is not a pre-proto-valuer. ∎

### Interpretation

A structure can persist under actual dynamics without maintaining itself better than its matched identity-decay null.

Persistence alone is too weak for pre-proto-valuerhood.

## 4. Theorem 2: unperturbed maintenance gap does not imply perturbation-robust recoverability

### Statement

There exists a finite evaluation model in which a candidate beats its null in the unperturbed case but fails perturbation-robust recoverability.

### Construction

Let:

```text
P = {p}
Pi = {id, shock}
rho = 1
eta = 1/2
```

Set:

```text
M(p) = 1

C_K(p, id) = 1
C_N(p, id) = 0

C_K(p, shock) = 0
C_N(p, shock) = 0
```

### Proof

In the unperturbed case:

```text
C_K(p, id) - C_N(p, id) = 1 - 0 = 1 >= eta.
```

So `p` beats its null under `id`.

However, perturbation-robust recoverability requires:

```text
for all pi in Pi, C_K(p, pi) >= rho.
```

But under `shock`:

```text
C_K(p, shock) = 0 < rho.
```

Therefore perturbation-robust recoverability fails. ∎

### Interpretation

A pattern can appear maintained in the unperturbed case while collapsing under declared perturbation.

Unperturbed anti-dissolution is not enough for pre-proto-valuerhood.

## 5. Theorem 3: perturbation-robust recoverability does not imply maintenance gap

### Statement

There exists a finite evaluation model in which a candidate is perturbation-robustly recoverable but fails to separate from its identity-decay null.

### Construction

Let:

```text
P = {p}
Pi = {id, shock}
rho = 1
eta = 1/2
```

Set:

```text
M(p) = 1

C_K(p, id) = 1
C_K(p, shock) = 1

C_N(p, id) = 1
C_N(p, shock) = 1
```

### Proof

For every perturbation:

```text
C_K(p, pi) = 1 >= rho.
```

So `p` is perturbation-robustly recoverable.

But for every perturbation:

```text
C_K(p, pi) - C_N(p, pi) = 1 - 1 = 0 < eta.
```

So `p` fails the maintenance-gap condition. ∎

### Interpretation

A pattern may remain recoverable because the matched null also remains recoverable.

Recoverability alone does not establish active maintenance or anti-dissolution.

## 6. Theorem 4: pre-proto-valuerhood does not imply proto-valuerhood

### Statement

There exists a finite evaluation model in which a candidate is a pre-proto-valuer but not a proto-valuer.

### Construction

Let:

```text
P = {p}
Pi = {id}
rho = 1
eta = 1/2
gamma = 1/2
```

Set:

```text
M(p) = 1
C_K(p, id) = 1
C_N(p, id) = 0
S_act(p) = 1/2
S_pass(p) = 1/2
```

### Proof

`M(p) > 0`.

`p` is perturbation-robustly recoverable because:

```text
C_K(p, id) = 1 >= rho.
```

`p` has a maintenance gap because:

```text
C_K(p, id) - C_N(p, id) = 1 - 0 = 1 >= eta.
```

Therefore `p` is a pre-proto-valuer.

But self-conditioning requires:

```text
S_act(p) - S_pass(p) >= gamma.
```

Here:

```text
S_act(p) - S_pass(p) = 1/2 - 1/2 = 0 < gamma.
```

So self-conditioning fails, and `p` is not a proto-valuer. ∎

### Interpretation

A process bundle can maintain recoverable distinction-content better than a null without its own activity increasing future pre-proto-valuerhood.

This separates maintained structure from self-conditioning structure.

## 7. Theorem 5: proto-valuerhood does not imply compatibility-audited valuerhood

### Statement

There exists a finite evaluation model in which a candidate is a proto-valuer but not a valuer because its induced asymmetry-preference fails compatibility audit.

### Construction

Let:

```text
P = {p, q}
Pi = {id}
rho = 1
eta = 1/2
gamma = 1/2
```

For `p`, set:

```text
M(p) = 1
C_K(p, id) = 1
C_N(p, id) = 0
S_act(p) = 1
S_pass(p) = 0
```

Thus `p` satisfies pre-proto-valuerhood and self-conditioning.

Now introduce two asymmetry regimes:

```text
A:
  preserves p strongly but destroys q's distinction-content

B:
  preserves p sufficiently and also preserves q
```

Represent this by scores:

```text
under A: p_retention = 1, q_retention = 0
under B: p_retention = 1, q_retention = 1
```

Suppose the induced preference relation of `p` ranks `A >=_p B` because both preserve `p` equally and `A` is locally preferred by a declared tie-breaker or local cost.

Let the compatibility audit require:

```text
if two regimes preserve p equally, p may not prefer a regime that irreversibly
collapses q when an alternative preserves q.
```

Then:

```text
CompAudit(p) = false.
```

### Proof

`p` is a pre-proto-valuer:

```text
M(p) = 1 > 0
C_K(p, id) = 1 >= rho
C_K(p, id) - C_N(p, id) = 1 >= eta
```

`p` satisfies self-conditioning:

```text
S_act(p) - S_pass(p) = 1 - 0 = 1 >= gamma.
```

Therefore `p` is a proto-valuer.

But by construction, `CompAudit(p) = false`.

Since finite valuerhood in this scaffold requires proto-valuerhood plus compatibility audit, `p` is not a valuer. ∎

### Interpretation

Proto-valuerhood is local to a process bundle's distinction-maintaining and self-conditioning structure.

Valuerhood requires compatibility discipline. A proto-valuer whose induced asymmetry-preferences preserve itself by collapsing compatible others has not earned full valuer language.

## 8. Theorem 6: individual proto-valuers need not be jointly compatible

### Statement

There exists a finite evaluation model in which two candidates are both proto-valuers individually, but their pair is not admissible under the declared completion predicate.

### Construction

Let:

```text
P = {p, q}
Pi = {id}
rho = 1
eta = 1/2
gamma = 1/2
```

For each `x in {p,q}`, set:

```text
M(x) = 1
C_K(x, id) = 1
C_N(x, id) = 0
S_act(x) = 1
S_pass(x) = 0
```

Thus both `p` and `q` are proto-valuers.

Define the completion admissibility predicate by:

```text
Adm(emptyset) = true
Adm({p}) = true
Adm({q}) = true
Adm({p,q}) = false
```

### Proof

By the score table, each of `p` and `q` satisfies:

```text
M > 0
C_K >= rho
C_K - C_N >= eta
S_act - S_pass >= gamma
```

So each is a proto-valuer.

However, by definition:

```text
Adm({p,q}) = false.
```

Therefore individual proto-valuerhood does not imply joint compatibility. ∎

### Interpretation

Even if two process bundles each maintain themselves and self-condition, their composition may still erase, capture, overload, or destabilize each other.

Compatibility is an additional condition, not a consequence of individual proto-valuerhood.

## 9. Theorem 7: pairwise compatibility among proto-valuers does not imply joint compatibility

### Statement

There exists a finite evaluation model with three proto-valuers such that every pair is admissible but the triple is not.

### Construction

Let:

```text
P = {p, q, r}
Pi = {id}
rho = 1
eta = 1/2
gamma = 1/2
```

For each `x in P`, set:

```text
M(x) = 1
C_K(x, id) = 1
C_N(x, id) = 0
S_act(x) = 1
S_pass(x) = 0
```

Thus all three are proto-valuers.

Define:

```text
Adm(Y) iff |Y| <= 2.
```

### Proof

Each candidate is a proto-valuer by the score table.

Every pair has size `2`, so every pair is admissible:

```text
Adm({p,q}) = true
Adm({p,r}) = true
Adm({q,r}) = true
```

But the triple has size `3`, so:

```text
Adm({p,q,r}) = false.
```

Therefore pairwise compatibility among proto-valuers does not imply joint compatibility. ∎

### Interpretation

Compatibility remains n-ary even after proto-valuerhood is established.

This supports treating Omega as a compatibility-completion problem over sets or families, not as a pairwise graph property alone.

## 10. Theorem 8: pre-proto-valuerhood under one null need not survive a stronger null

### Statement

There exists a finite evaluation model in which a candidate satisfies pre-proto-valuer criteria against a weak null but fails against a stronger nuisance-preserving null.

### Construction

Let:

```text
P = {p}
Pi = {id}
rho = 1
eta = 1/2
```

Let actual maintenance be:

```text
M(p) = 1
C_K(p, id) = 1
```

Define two nulls:

```text
N_weak:
  C_{N_weak}(p, id) = 0

N_strong:
  C_{N_strong}(p, id) = 3/4
```

### Proof

Against `N_weak`:

```text
C_K(p, id) - C_{N_weak}(p, id) = 1 - 0 = 1 >= eta.
```

So the maintenance-gap condition holds.

Against `N_strong`:

```text
C_K(p, id) - C_{N_strong}(p, id) = 1 - 3/4 = 1/4 < eta.
```

So the maintenance-gap condition fails.

The other pre-proto conditions hold:

```text
M(p) = 1 > 0
C_K(p, id) = 1 >= rho
```

Thus `p` can be a pre-proto-valuer relative to `N_weak` but not relative to `N_strong`. ∎

### Interpretation

Pre-proto-valuerhood is always null-relative.

This is why identity-decay nulls must be declared, justified, and audited. A weak null may support only a weak claim.

## 11. Strict ladder summary

The finite examples establish the following separations:

```text
persistence
  does not imply pre-proto-valuerhood

unperturbed maintenance gap
  does not imply perturbation-robust recoverability

perturbation-robust recoverability
  does not imply maintenance gap

pre-proto-valuerhood
  does not imply proto-valuerhood

proto-valuerhood
  does not imply compatibility-audited valuerhood

individual proto-valuerhood
  does not imply joint compatibility

pairwise compatibility
  does not imply joint compatibility

pre-proto-valuerhood under one null
  does not imply pre-proto-valuerhood under a stronger null
```

Therefore each rung in the ladder adds real content.

## 12. Mapping to Future Field Atlas

Current FFA does not yet implement these theorem predicates.

What FFA currently provides:

```text
frontier topology;
formal condition identity;
product and coupled baselines;
joint-vs-product residuals;
marginal retention;
joint density vs marginal product;
operator sensitivity;
horizon onset;
artifact completeness;
reconstruction audits.
```

What future FFA or theorem-sandbox runs would need:

```text
candidate process-bundle designation P;
reconstructible distinction measure M_Q(D_t(P));
perturbation class Pi;
identity-decay null N_P;
maintenance gap C_K^Pi(P,H) - C_{N_P}^Pi(P,H);
activity channel a_P;
active/passive self-conditioning comparison;
compatibility audit over induced asymmetry-preferences.
```

Thus the theorem ladder is ahead of the empirical instrument, as intended.

## 13. Claim boundary

This note does not claim:

```text
Omega validation;
pre-proto-valuer detection;
proto-valuer detection;
valuer detection;
agency;
identity;
value;
compatibility detection in current data;
support / capture / erasure;
universal teleology.
```

Allowed claim:

```text
In finite evaluation models, persistence, recoverability, maintenance gap,
self-conditioning, compatibility-audited valuerhood, and Omega-compatible
completion are formally separable properties.
```

## 14. Next theorem targets

The next theorem-grade step should lock down finite distinction measures or prove basic null-family relations.

Candidate next notes:

```text
Finite Distinction Measures v0:
  define a small reconstructible menu of M_Q measures for finite future fields.

Null Strength and Claim Strength v0:
  compare null families by what they preserve and destroy; identify when a
  passed null supports only a weak claim.

Finite Maintenance-Gap Examples v0:
  build tiny explicit transition systems, not just score tables, that witness
  persistence without pre-proto status and pre-proto without proto status.
```

The score-table separations here are the first scaffold. The next step should move from abstract score tables to tiny transition systems where possible.

## 15. Summary

Compact conclusion:

```text
The proto-valuer ladder is mathematically non-collapsible in finite evaluation
models.

Persistence, recoverability, null separation, self-conditioning, compatibility
audit, and completion-level compatibility are distinct requirements.

This justifies the project's refusal to promote persistent or recoverable
structures directly into valuers or Omega-compatible structures.
```
