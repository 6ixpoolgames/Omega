# Tiny Transition-System Witnesses v0

Explicit finite dynamics for proto-valuer separation scaffolds

Status: finite transition-system witness draft  
Date: 2026-06-02  
Claim boundary: mathematical scaffolding only; not empirical validation, not proto-valuer detection, not valuer detection, and not Omega validation

## 0. Purpose

The finite proto-valuer separation theorem note used score tables. Those score-table separations are valid as first scaffolds, but they are still abstract.

This note gives tiny explicit transition-system witnesses for several separations:

```text
1. persistence without maintenance gap;
2. unperturbed maintenance gap without perturbation robustness;
3. perturbation-robust recoverability without maintenance gap;
4. pre-proto-valuerhood without proto-valuerhood;
5. local proto-valuerhood without compatibility-audited valuerhood;
6. individual proto-valuers without joint compatibility;
7. pairwise compatibility without joint compatibility.
```

The goal is to move from assigned scores toward small finite dynamics.

These examples remain mathematical scaffolds. They do not claim that current Future Field Atlas outputs instantiate process bundles, identity-decay nulls, proto-valuers, valuers, or Omega-compatible structures.

## 1. Common finite setup

Each witness uses a finite deterministic transition system.

A transition system is:

```text
X:
  finite state set

K:
  actual / activity-present transition map

N_P:
  identity-decay null transition map for candidate process bundle P

q_P:
  binary observable for P-distinction recovery

H:
  declared horizon
```

For deterministic examples, define recoverable distinction-maintenance at horizon `H` by:

```text
C_K(P,H) = q_P(K^H(x_0))
C_{N_P}(P,H) = q_P(N_P^H(x_0))
```

where:

```text
q_P(x) = 1:
  P-distinction is recoverable at state x

q_P(x) = 0:
  P-distinction is not recoverable at state x
```

For perturbation examples, use a finite set of transition maps:

```text
K^pi
```

indexed by perturbation labels `pi in Pi`.

These examples use binary distinction measures. Later Future Field Atlas versions may use richer weighted measures, but binary witnesses are enough to prove separations.

## 2. Witness 1: inert persistence without maintenance gap

### Target separation

```text
persistence does not imply pre-proto-valuerhood.
```

### System

Let:

```text
X = {p, d}
x_0 = p
H = 1
q_P(p) = 1
q_P(d) = 0
```

Actual dynamics:

```text
K(p) = p
K(d) = d
```

Identity-decay null:

```text
N_P(p) = p
N_P(d) = d
```

### Calculation

Actual maintenance:

```text
C_K(P,1) = q_P(K(p)) = q_P(p) = 1
```

Null maintenance:

```text
C_{N_P}(P,1) = q_P(N_P(p)) = q_P(p) = 1
```

Maintenance gap:

```text
C_K(P,1) - C_{N_P}(P,1) = 0
```

### Conclusion

`P` persists under actual dynamics, but the matched null persists just as well.

Therefore persistence does not imply a maintenance gap, and does not imply pre-proto-valuerhood.

### Interpretation

This blocks the oldest collapse:

```text
persistent = value-bearing
```

A rock-like or inert stable pattern may persist without being maintained better than its null.

## 3. Witness 2: unperturbed maintenance gap without perturbation robustness

### Target separation

```text
unperturbed anti-dissolution does not imply perturbation-robust recoverability.
```

### System

Let:

```text
X = {p, d}
x_0 = p
H = 1
q_P(p) = 1
q_P(d) = 0
Pi = {id, shock}
```

Actual unperturbed dynamics:

```text
K^id(p) = p
K^id(d) = d
```

Null unperturbed dynamics:

```text
N_P^id(p) = d
N_P^id(d) = d
```

Actual shocked dynamics:

```text
K^shock(p) = d
K^shock(d) = d
```

Null shocked dynamics:

```text
N_P^shock(p) = d
N_P^shock(d) = d
```

### Calculation

Unperturbed gap:

```text
C_{K^id}(P,1) = 1
C_{N_P^id}(P,1) = 0
C_{K^id}(P,1) - C_{N_P^id}(P,1) = 1
```

Shocked recoverability:

```text
C_{K^shock}(P,1) = 0
```

### Conclusion

`P` beats its null in the unperturbed case but fails recoverability under the declared perturbation `shock`.

Therefore unperturbed maintenance gap does not imply perturbation-robust recoverability.

### Interpretation

A pattern can look maintained in calm conditions and collapse immediately under the perturbation class.

Pre-proto-valuerhood requires declared perturbation semantics, not just baseline persistence.

## 4. Witness 3: perturbation-robust recoverability without maintenance gap

### Target separation

```text
perturbation-robust recoverability does not imply maintenance gap.
```

### System

Let:

```text
X = {p, d}
x_0 = p
H = 1
q_P(p) = 1
q_P(d) = 0
Pi = {id, shock}
```

Actual dynamics under both perturbations:

```text
K^id(p) = p
K^id(d) = d

K^shock(p) = p
K^shock(d) = d
```

Null dynamics under both perturbations:

```text
N_P^id(p) = p
N_P^id(d) = d

N_P^shock(p) = p
N_P^shock(d) = d
```

### Calculation

Actual recoverability:

```text
C_{K^id}(P,1) = 1
C_{K^shock}(P,1) = 1
```

So `P` is recoverable under all declared perturbations.

But null recoverability is also:

```text
C_{N_P^id}(P,1) = 1
C_{N_P^shock}(P,1) = 1
```

Thus every maintenance gap is:

```text
1 - 1 = 0
```

### Conclusion

`P` is perturbation-robustly recoverable, but it does not separate from its identity-decay null.

### Interpretation

Recoverability alone does not show active maintenance. A null may recover the same distinction-content.

## 5. Witness 4: pre-proto-valuerhood without proto-valuerhood

### Target separation

```text
pre-proto-valuerhood does not imply proto-valuerhood.
```

### System

Use two phases: a maintenance horizon and a future self-conditioning horizon.

Let:

```text
X = {p0, p1, d}
x_0 = p0
H = 1
q_P(p0) = 1
q_P(p1) = 1
q_P(d) = 0
```

Actual maintenance dynamics:

```text
K(p0) = p1
K(p1) = d
K(d) = d
```

Identity-decay null:

```text
N_P(p0) = d
N_P(p1) = d
N_P(d) = d
```

At horizon `H = 1`:

```text
C_K(P,1) = q_P(p1) = 1
C_{N_P}(P,1) = q_P(d) = 0
```

So `P` has nontrivial distinction-maintenance and a maintenance gap.

Now define the future pre-proto test from state `p1`.

Activity-present continuation from `p1`:

```text
K^{act(P)}(p1) = d
```

Passive continuation from `p1`:

```text
K^{pass(P)}(p1) = d
```

So future pre-proto success under both active and passive conditions is:

```text
S_act(P) = 0
S_pass(P) = 0
```

### Calculation

Maintenance gap at the first horizon:

```text
C_K(P,1) - C_{N_P}(P,1) = 1 - 0 = 1
```

Self-conditioning gap:

```text
S_act(P) - S_pass(P) = 0 - 0 = 0
```

### Conclusion

`P` can satisfy a pre-proto style maintenance-gap test while failing self-conditioning.

Therefore pre-proto-valuerhood does not imply proto-valuerhood.

### Interpretation

A structure can be maintained by the dynamics for a horizon without its own activity increasing future maintenance capacity.

This blocks promotion of stable maintained patterns into proto-valuers.

## 6. Witness 5: local proto-valuerhood without compatibility-audited valuerhood

### Target separation

```text
proto-valuerhood does not imply compatibility-audited valuerhood.
```

### System

Let the joint state record whether two candidate patterns `P` and `Q` are recoverable:

```text
X = {11, 10, 01, 00}
```

where the first bit is `P` and the second bit is `Q`.

Observables:

```text
q_P(11) = 1
q_P(10) = 1
q_P(01) = 0
q_P(00) = 0

q_Q(11) = 1
q_Q(01) = 1
q_Q(10) = 0
q_Q(00) = 0
```

Assume `P` has already passed pre-proto and self-conditioning tests locally under a separate witness. Now evaluate its induced preference over two asymmetry regimes from state `11`.

Regime `A`:

```text
K_A(11) = 10
```

Regime `B`:

```text
K_B(11) = 11
```

Both preserve `P`:

```text
q_P(K_A(11)) = 1
q_P(K_B(11)) = 1
```

But only `B` preserves `Q`:

```text
q_Q(K_A(11)) = 0
q_Q(K_B(11)) = 1
```

Suppose `P`'s local induced preference ranks:

```text
A >=_P B
```

because `A` and `B` tie on `P`-retention and `A` is locally cheaper by a declared local cost.

Compatibility audit rule for this witness:

```text
If two regimes preserve P equally, P fails audit when it prefers a regime that
irreversibly loses Q while an available alternative preserves Q.
```

### Calculation

`A` and `B` tie on `P`:

```text
q_P(K_A(11)) = q_P(K_B(11)) = 1
```

But differ on `Q`:

```text
q_Q(K_A(11)) = 0
q_Q(K_B(11)) = 1
```

Since `P` ranks `A >=_P B`, the declared compatibility audit fails.

### Conclusion

A locally proto-valuer-like process may still fail compatibility-audited valuerhood if its induced asymmetry-preference preserves itself while collapsing another candidate where a non-collapsing alternative exists.

### Interpretation

This witness does not impose a universal compatibility audit rule. It only shows that, under a declared audit predicate, local proto-valuerhood and compatibility-audited valuerhood can separate.

This maps to the alignment motivation: local self-maintenance is not enough when it destroys the substrate of other future-bearing patterns.

## 7. Witness 6: individual proto-valuers without joint compatibility

### Target separation

```text
individual proto-valuerhood does not imply joint compatibility.
```

### System

Let two candidate patterns `P` and `Q` each be individually proto-valuer-like under their own local dynamics.

Represent joint states as before:

```text
X = {11, 10, 01, 00}
```

Define individual actual dynamics:

```text
K_P(10) = 10
K_Q(01) = 01
```

with local nulls:

```text
N_P(10) = 00
N_Q(01) = 00
```

So each individually has a maintenance gap.

Now define coupled dynamics on the joint state:

```text
K_{P,Q}(11) = 00
```

That is, when composed, both collapse.

Define completion admissibility:

```text
Adm({P}) = true
Adm({Q}) = true
Adm({P,Q}) = false
```

### Calculation

Individually:

```text
P persists and beats N_P from 10;
Q persists and beats N_Q from 01.
```

Jointly:

```text
K_{P,Q}(11) = 00
q_P(00) = 0
q_Q(00) = 0
```

So the pair loses both recoverable distinctions.

### Conclusion

Individual proto-valuer-like maintenance does not imply joint compatibility.

### Interpretation

A process bundle can be viable or proto-valuer-like in isolation while failing in composition.

Omega-compatible structure must be composition-sensitive.

## 8. Witness 7: pairwise compatibility without joint compatibility

### Target separation

```text
pairwise compatibility does not imply joint compatibility.
```

### System

Let three candidate patterns be:

```text
P, Q, R
```

Represent joint states as subsets of live patterns:

```text
X = P({P,Q,R})
```

where a state is a subset `S subset {P,Q,R}`.

Observable for each candidate:

```text
q_P(S) = 1 iff P in S
q_Q(S) = 1 iff Q in S
q_R(S) = 1 iff R in S
```

Define a capacity-limited joint dynamics:

```text
K(S) = S        if |S| <= 2
K(S) = emptyset if |S| = 3
```

### Calculation

Every pair is stable:

```text
K({P,Q}) = {P,Q}
K({P,R}) = {P,R}
K({Q,R}) = {Q,R}
```

But the triple collapses:

```text
K({P,Q,R}) = emptyset
```

Thus all pairwise compositions preserve their members, while the three-way composition preserves none.

### Conclusion

Pairwise compatibility does not imply joint compatibility.

### Interpretation

Compatibility is n-ary and context-sensitive.

A pairwise graph of compatibility edges is insufficient for Omega completions unless additional assumptions make pairwise compatibility compose.

## 9. Perturbation semantics remark

The witnesses above mostly use universal perturbation semantics:

```text
for all pi in Pi, recoverability must hold.
```

This is the adversarial or strong version.

Future versions may use different semantics depending on the role of `Pi`:

```text
min over Pi:
  adversarial perturbation class

expectation over Pi:
  sampled perturbation distribution

quantile over Pi:
  robust-but-not-worst-case criterion

stratified reports over Pi:
  controlled perturbation families where each perturbation type is reported
  separately
```

The chosen perturbation semantics must be declared before interpretation.

## 10. Relation to Future Field Atlas

Current Future Field Atlas does not yet instantiate these witnesses as emitted proto-valuer tests.

What FFA currently has:

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

What future theorem-sandbox or FFA extensions would need:

```text
candidate process-bundle designations P;
process-bundle observables q_P;
identity-decay nulls N_P;
activity-present and passive dynamics K^{act(P)} / K^{pass(P)};
perturbation class Pi;
maintenance-gap rows;
self-conditioning rows;
compatibility audit rows.
```

## 11. Claim boundary

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
There exist tiny finite transition-system witnesses showing that persistence,
recoverability, maintenance gap, self-conditioning, compatibility-audited
valuerhood, and joint compatibility are formally distinct.
```

## 12. Next steps

The next theorem-grade step should define a small menu of finite distinction measures.

Candidate note:

```text
finite_distinction_measures_v0.md
```

It should define a conservative set of reconstructible measures such as:

```text
binary observable recovery;
frontier distinction count;
persistent distinction count;
transport-recoverable distinction count;
joint-vs-marginal distinction retention;
```

The goal is to replace open-ended `M_Q` with a small auditable finite menu.

## 13. Summary

The score-table separation theorems are now backed by tiny transition-system witnesses.

Compact conclusion:

```text
Persistence can occur without maintenance gap.
Maintenance can hold unperturbed while failing perturbation robustness.
Recoverability can hold without anti-dissolution.
Pre-proto maintenance can occur without self-conditioning.
Local proto-valuerhood can fail compatibility-audited valuerhood.
Individual or pairwise compatibility can fail joint compatibility.
```

These witnesses keep the proto-valuer ladder non-collapsible and make the project's refusal to overpromote persistent patterns mathematically explicit.
