# FFA Adapter Formal Consumption Audit v0

Status: formal-arm consumption audit  
Date: 2026-06-03  
Input result: `docs/research_notes/validation_results/future_field_atlas/future_field_atlas_formal_adapter_conformance_package_result.md`  
Adapter ID: `ffa_finite_reachable_frontier_support_v0`  
Claim boundary: formal adapter consumption only; not Omega validation, not compatibility detection, not proto-valuer / valuer detection, not support/capture/erasure detection

## 0. Purpose

This note records the formal arm's first consumption audit of the Future Field Atlas formal adapter conformance package.

The question is not:

```text
Did FFA detect Omega?
```

The question is:

```text
Can the retained FFA formal-interface panel be consumed as a presentation of
Omega Primitive Calculus v0, and which Lean-checked root theorems transfer?
```

The relevant root formalism is the support-level normal-lax distinction transport calculus:

```text
A : C -> DistTrans
```

where:

```text
C:
  contexts and relational unfoldings

DistTrans:
  preorder-indexed distinction transports closed under source weakening and
  target strengthening

A:
  normal lax assignment of distinction transports to unfoldings
```

## 1. Input package summary

The adapter package compiled the retained formal-interface distinction panel into:

```text
contexts
unfoldings
distinction fibers
distinction preorder rows
raw transport witnesses
closed transport relation
root law checks
recoverability / non-erasure tables
theorem-transfer summary
formal consumption bundle
```

Final package status:

```text
adapter_status: generated_presentation_conformance
input_panel_digest: f7a2c13f1b192751c0334936
```

Emitted counts:

```text
contexts: 2600
unfoldings: 7720
distinction fiber rows: 26520
preorder rows: 55120
raw witnesses: 40141
closed transport rows: 114158
```

Audit summary from the result note:

```text
preorder failures: 0
root law check failures: 0
```

## 2. Formal status distinction

The adapter package has two different meanings depending on which relation is consumed.

### 2.1 Raw witness relation

The raw witness relation is empirical/derived support directly emitted from retained panel artifacts.

It does **not** satisfy the root laws as-is.

Raw pass counts:

```text
identity transport:      0 / 55,120
source weakening:   59,811 / 195,463
target strengthening: 60,541 / 225,655
lax composition:    28,823 / 44,211
```

Therefore:

```text
strict_raw_conformance: not achieved
```

### 2.2 Generated closed presentation

The closed transport relation is the least formal closure generated from raw witnesses and declared preorder / law closure.

Closed pass counts:

```text
identity transport:      55,120 / 55,120
source weakening:       195,463 / 195,463
target strengthening:   225,655 / 225,655
lax composition:         44,211 / 44,211
```

Therefore:

```text
generated_presentation_conformance: achieved
```

This is the formal arm's primary consumption target in this audit.

## 3. Formal consumption judgment

The formal arm accepts the package as:

```text
a generated finite measure-token presentation of Omega Primitive Calculus v0.
```

The formal arm does **not** accept the package as:

```text
a strict raw empirical DistTrans model;
a compatibility detector;
a valuer / proto-valuer detector;
a support/capture/erasure detector;
a substrate-general validation of Omega.
```

More compactly:

```text
The generated closed presentation is formally consumable.
The raw witness relation is evidence feeding that presentation, not itself a
law-satisfying presentation.
```

## 4. Theorem-transfer status

### 4.1 Transfers to generated closed presentation

The following Lean-checked root results transfer to the generated closed presentation:

```text
disttrans_identity
disttrans_source_weakening
disttrans_target_strengthening
compositional_recoverability
non_erasure_monotonicity
finite_chain_recurrent_recoverability
```

Interpretation:

```text
Within the generated closed presentation, recoverability weakening,
recoverability strengthening, compositional recoverability, non-erasure
monotonicity, and finite-chain recurrent recoverability may be used.
```

### 4.2 Does not transfer to raw witness relation

The same theorems do not transfer to the raw witness relation unless the raw relation is explicitly shown to satisfy the root laws.

The adapter-failure Lean checks are relevant here: theorem transfer requires actual closure and laxity.

### 4.3 Partial / diagnostic transfer

The marginal-versus-joint result remains:

```text
partial_transfer:
  finite-measure diagnostic only
```

The adapter emits a marginal-versus-joint diagnostic with class counts:

```text
marginal_and_joint_preserved: 1513
marginal_loss_joint_restrictive: 91
marginal_loss_product_dense: 584
marginal_preserved_joint_restricted: 412
```

Formal read:

```text
The package can express finite measure-token cases in which marginal-like
conditions and joint-like conditions separate.
```

Blocked read:

```text
This does not establish compatibility, erasure, support, capture, agency,
identity, valuerhood, or Omega.
```

### 4.4 Not applicable

Finite completion existence remains:

```text
not_applicable
```

Reason:

```text
The adapter package does not declare a candidate family space T or an
admissibility predicate Adm : P(T) -> Prop.
```

Completion theorems cannot transfer until those objects are declared.

## 5. Raw-vs-closed gap analysis

The raw/closed gap is load-bearing.

### 5.1 Identity transport

Raw identity pass:

```text
0 / 55,120
```

Closed identity pass:

```text
55,120 / 55,120
```

Interpretation:

```text
Identity transport is currently formal generated structure, not directly emitted
empirical witness structure.
```

This is acceptable for generated presentation conformance. It blocks strict raw conformance.

### 5.2 Source weakening and target strengthening

Raw source weakening pass:

```text
59,811 / 195,463
```

Raw target strengthening pass:

```text
60,541 / 225,655
```

Interpretation:

```text
Most weakening/strengthening support is generated by closure rather than directly
observed as raw witnesses.
```

This is acceptable for formal presentation generation. It is not acceptable if the next aim is strict raw empirical conformance.

### 5.3 Lax composition

Raw lax composition pass:

```text
28,823 / 44,211
```

Closed lax composition pass:

```text
44,211 / 44,211
```

Interpretation:

```text
A substantial portion of compositional recovery support is generated by normal-lax
closure. The adapter can be consumed as a generated normal-lax presentation, but
not as raw empirical evidence that every composite witness was directly emitted.
```

## 6. Claim boundary after audit

Allowed:

```text
The retained FFA formal-interface panel has been compiled into a generated
finite measure-token presentation consumable by Omega Primitive Calculus v0.

The generated closed presentation satisfies the checked root laws.

Lean-checked recoverability, non-erasure, and recurrent recoverability theorems
transfer to the generated closed presentation.
```

Blocked:

```text
strict raw conformance;
Omega validation;
proto-valuer detection;
valuer detection;
compatibility detection;
support / capture / erasure detection;
identity or agency detection;
finite completion existence over FFA candidates;
substrate-general validation.
```

## 7. Formal decision

The formal arm's decision is:

```text
CONSUME AS GENERATED PRESENTATION.
DO NOT CONSUME AS STRICT RAW MODEL.
DO NOT PROMOTE TO COMPATIBILITY OR OMEGA CLAIMS.
```

This is a valid bridge artifact from empirics to formalism.

It is not yet a scientific validation of any substantive Omega-layer object.

## 8. Recommended next formal request to empirics

The formal arm should not request a broad FFA sweep.

The next request depends on which objective is chosen.

### Option A: pursue stricter empirical conformance

Ask empirics to emit explicit raw witnesses for:

```text
identity transport;
source weakening closure;
target strengthening closure;
lax composition witnesses.
```

Goal:

```text
move from generated_presentation_conformance toward strict_raw_conformance.
```

This is useful if we want the empirical witness relation itself to satisfy the root laws, rather than relying on formal closure.

### Option B: pursue completion-layer applicability

Ask empirics to declare:

```text
candidate_family_manifest
admissibility_predicate_manifest
completion_candidate_manifest
completion_audit_summary
```

Goal:

```text
make finite completion existence and completion counterexamples applicable to an
FFA candidate family space.
```

This should not happen until the formal arm is satisfied that the finite measure-token distinctions are stable enough to support an `Adm` predicate.

### Option C: hold FFA and move to cleaner channel presentation empirics

Use the finite channel presentation as the next empirical target.

Goal:

```text
test recoverability / non-erasure in a cleaner prebiotic channel substrate with
lower semantic smuggling risk.
```

## 9. Recommendation

Proceed with **Option A-lite**, not full strict raw repair and not completion-layer expansion yet.

Request a small raw/closed gap report from empirics:

```text
Which closed transport rows are closure-derived only?
Which closure rules contribute most?
Which theorem transfers depend most heavily on generated closure?
Can identity, weakening, strengthening, and composition witnesses be emitted
explicitly without rerunning broad FFA?
```

Then decide whether strict raw conformance is worth pursuing.

Do not proceed to candidate-family admissibility or identity-decay nulls yet.

## 10. Summary

The FFA adapter conformance package is formally consumable as a generated presentation of Omega Primitive Calculus v0.

It successfully bridges retained FFA outputs to the Lean-backed root calculus at the level of contexts, unfoldings, finite distinction tokens, preorders, closed transports, law checks, non-erasure rows, and theorem-transfer status.

The result is important but narrow:

```text
It earns theorem transfer to the generated closed presentation.
It does not earn strict raw conformance or any substantive Omega-layer claim.
```
