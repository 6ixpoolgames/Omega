# Omega Primitive Calculus v0 Lean Root Skeleton

Status: Lean-checked support-level root skeleton
Date: 2026-06-03
Claim boundary: formal skeleton only; not empirical validation, not valuer detection, not Omega validation, not ethical completion

## Purpose

This pass updates the Lean target from the earlier witness-calculus smoke to the
refined Omega Primitive Calculus v0 root formalism.

The current compact root object is:

```text
A : C -> DistTrans
```

where:

```text
C:
  category of relational contexts and unfoldings

DistTrans:
  category of preorder-indexed support-level distinction transports

A:
  normal lax assignment of distinction fibers and transport relations
```

This is a support-level calculus. Weighted, probabilistic, cost-valued,
rank-valued, rate-valued, information-theoretic, quantale-valued, and
Boolean-algebraic versions are presentations or enrichments, not the root
formalism.

## Checked Lean Artifacts

Files:

```text
formal/lean/OmegaCore/DistTrans.lean
formal/lean/OmegaCore/AdapterFailures.lean
formal/lean/OmegaCore/NormalLax.lean
formal/lean/OmegaCore/Recurrent.lean
formal/lean/OmegaCore/Completion.lean
formal/lean/OmegaCore/Counterexamples.lean
formal/lean/OmegaCore/MarginalJoint.lean
formal/lean/OmegaCore/Presentations/FiniteBoolean.lean
formal/lean/OmegaCore/Presentations/FiniteChannel.lean
formal/lean/OmegaCore/Presentations/ProbabilisticChannel.lean
```

Build command:

```powershell
$env:PATH = (Resolve-Path '.tools\lean-4.30.0\lean-4.30.0-windows\bin').Path + ';' + $env:PATH
cd formal\lean
lake build OmegaCore
```

Build status:

```text
PASS
Build completed successfully.
```

The checked Lean files contain no:

```text
sorry
admit
axiom
```

## Batch 1: DistTrans

`DistTrans.lean` defines:

```text
PreorderFrame:
  minimal preorder frame

DistTransport:
  relation Phi(p,q) closed under source weakening and target strengthening

id:
  identity transport, Id_P(p,q) iff p <= q

compose:
  ordinary relational composition of transports
```

Checked laws:

```text
identity transport is closed
composition of transports is closed
left identity, relation-level iff
right identity, relation-level iff
associativity, relation-level iff
```

The category laws are expressed as relation-level equivalences. This is the
mathematically relevant extensional equality for support relations.

## Batch 2: Normal Lax Consequences

`NormalLax.lean` defines:

```text
ContextCategory:
  relational contexts and composable unfoldings

NormalLaxDistinctionTransport:
  object part assigns distinction preorders
  morphism part assigns DistTrans transports
  identity is normal
  composition is lax by transport inclusion
```

Checked consequences:

```text
identity recoverability
recoverability weakening
recoverability strengthening
compositional recoverability from laxity
non-erasure monotonicity
```

## Batch 3: Recurrent Recoverability

`Recurrent.lean` defines:

```text
Chain:
  finite composable chain of relational unfoldings

Chain.toHom:
  composite unfolding induced by a chain

RecoverChain:
  local stepwise recovery along the chain
```

Checked theorem:

```text
recoverChain_sound:
  local finite-chain recovery implies recovery through the composite unfolding
```

Interpretation:

```text
Recurrent recoverability is finite-chain compositional recoverability.
It formalizes repeated recovery across a declared unfolding sequence.
Nontriviality / churn is adapter-specific and not part of the Lean root
skeleton.
```

## Batch 4: Finite Maximal Completion

`Completion.lean` defines:

```text
SubsetMaximal:
  admissible family with no one-way admissible extension

MaxSizedInList:
  admissible listed family whose size dominates all listed admissible families

exists_subsetMaximal_of_finite_enumeration:
  finite-enumeration maximal completion existence

exists_subsetMaximal_finset:
  Finset/Fintype maximal completion existence
```

Interpretation:

```text
If admissible candidate families are covered by an explicit finite enumeration
and at least one family is admissible, then a subset-maximal admissible family
exists.

If the candidate universe is finite, then the same subset-maximal existence
result specializes to `Finset` candidate families.
```

This proves the finite completion skeleton only. It does not define
compatibility, proto-valuers, valuers, value, empirical adapters, or Future
Field Atlas semantics.

Implementation note:

```text
The Lean sandbox now includes mathlib v4.30.0. The explicit List theorem is
retained as the minimal finite-search constructor, and the Finset/Fintype
specialization is checked with mathlib.
```

## Batch 5: Finite Completion Counterexamples

`Counterexamples.lean` defines:

```text
AdmAtMostTwo:
  abstract admissibility on Fin 3 where families of size at most two are
  admissible

AdmFork:
  downward-closed fork admissibility with two incompatible maximal branches

GreatestFinset:
  admissible family containing every admissible family
```

Checked counterexamples:

```text
pairwise_admissible_not_joint:
  all two-element families are admissible under AdmAtMostTwo, but the full
  three-element family is not

distinct_maximal_completions:
  the downward-closed fork has two distinct subset-maximal admissible families

no_greatest_completion:
  the downward-closed fork has no greatest admissible family
```

Interpretation:

```text
Finite completion structure is n-ary, subset-maximal, and generally
family-valued. Pairwise admissibility does not force joint admissibility;
maximal completions need not be unique; and maximal completions need not
assemble into a greatest completion.
```

These are abstract finite completion counterexamples only. They do not define
compatibility, valuerhood, empirical adapters, or Omega validation.

## Batch 6: Marginal-Like Non-Erasure Is Not Joint Non-Erasure

`MarginalJoint.lean` defines:

```text
SrcD:
  source distinctions bot, margA, margB, joint

TgtD:
  target distinctions bot, outA, outB

Phi:
  a DistTransport carrying margA to outA and margB to outB, with no target
  distinction capable of carrying the strictly joint source distinction

TransportNonErasing:
  transport-level non-erasure for a declared source requirement set
```

Checked counterexample:

```text
marginal_non_erasure_not_joint_non_erasure:
  Phi is non-erasing for the marginal requirement set {margA, margB}, but is
  not non-erasing for the joint requirement set {joint}
```

Interpretation:

```text
Preserving each component/marginal distinction does not force preservation of
a strictly joint distinction. This is the support-level root-calculus analogue
of the empirical lesson that marginal continuation is not compatibility.
```

This result remains at the abstract distinction-transport layer. It does not
define compatibility, joint field semantics, Future Field Atlas semantics,
valuerhood, or Omega validation.

## Batch 7: Adapter Failure Examples

`AdapterFailures.lean` defines finite failure examples for invalid adapters:

```text
RawPhi:
  raw relation that carries a source distinction a but fails to carry the
  weaker distinction bot

RawPsi:
  raw relation that carries a target distinction out but fails to carry the
  stronger target top

R01, R12, R02:
  valid one-step DistTrans transports and a valid declared composite transport
  where the required lax composition inclusion fails
```

Checked failures:

```text
raw_source_weakening_failure:
  a raw non-closed relation can fail recoverability weakening

rawPhi_not_distTransport_exact:
  no exact DistTransport can package that source-weakening-failing relation

raw_target_strengthening_failure:
  a raw non-closed relation can fail recoverability strengthening

rawPsi_not_distTransport_exact:
  no exact DistTransport can package that target-strengthening-failing relation

raw_laxity_failure:
  local recoveries can exist while the declared composite recovery is absent

laxity_subset_failure:
  valid one-step transports still fail theorem transfer when the declared
  composite transport does not contain their composed support
```

Interpretation:

```text
Theorem transfer requires actual satisfaction of the root laws. Invalid or
extended adapters must report which laws fail and which theorems no longer
apply.
```

These are failure examples only. They do not define empirical adapters, Future
Field Atlas semantics, compatibility, valuerhood, or Omega validation.

## Batch 8: Boolean Relation Support Presentation

`Presentations/FiniteBoolean.lean` defines the first worked presentation layer:

```text
Event alpha:
  Boolean event predicates alpha -> Prop

Rel alpha beta:
  binary relations alpha -> beta -> Prop

EventLe:
  support-inclusion order, P <= Q iff every P-point is also a Q-point

SupportRecovers:
  existential forward-image support recovery

supportTransport:
  relation-induced DistTransport on event frames
```

Checked presentation facts:

```text
supportTransport:
  satisfies the DistTransport source-weakening / target-strengthening closure
  laws

supportTransport_id_iff:
  the identity relation induces the root identity transport at relation level

supportTransport_comp_subset:
  relational composition induces the required lax composition inclusion

changed_carrier_composite_recovery:
  support recovery composes across changed carrier types with no shared literal
  state identity
```

Interpretation:

```text
The Boolean relation support presentation instantiates the root calculus in a
classical support setting. It validates possibility/support recovery, not
universal preservation.
```

This is a worked presentation of Omega Primitive Calculus v0. It is not an
empirical adapter, not Future Field Atlas semantics, not compatibility
semantics, not valuerhood, and not Omega validation.

## Batch 9: Finite Channel / Partition Presentation

`Presentations/FiniteChannel.lean` defines an exact channel recovery
presentation:

```text
ObsDist X:
  observable labeling / partition of a carrier X

Refines D E:
  E is fine enough to decode D

ExactRecovers K D E:
  every output allowed by channel support K carries enough target distinction
  to decode the source distinction

channelTransport:
  support-channel-induced DistTransport over observable distinctions
```

Checked presentation facts:

```text
channelTransport:
  satisfies the DistTransport closure laws by composing decoders

exactRecovers_id_iff_refines:
  identity channel recovery is exactly distinction refinement

exactRecovers_comp:
  exact channel recovery composes through support-channel composition

channelTransport_comp_subset:
  channel composition induces the required lax composition inclusion

exact_recovers_changed_carrier_comp:
  exact recovery composes across changed carrier types with no shared literal
  state identity

not_exact_recovers_constant_bit:
  a constant channel erases a nontrivial bit distinction

exact_recovers_constant_trivial:
  the same constant channel recovers the trivial source distinction
```

Interpretation:

```text
The finite channel / partition presentation instantiates the root calculus in
an exact decoder-reconstruction setting. Distinctions are observable labelings,
and recoverability is exact reconstruction through channel support.
```

This is not probabilistic Shannon theory, not an empirical adapter, not Future
Field Atlas semantics, not compatibility semantics, not valuerhood, and not
Omega validation.

## Batch 10: Probabilistic Channel Presentation

`Presentations/ProbabilisticChannel.lean` defines a finite natural-weight
stochastic channel enrichment:

```text
Supports K x y:
  positive natural-number channel support

successMass K pi D E dec:
  unnormalized finite decoder-success mass

totalMass K pi:
  unnormalized finite channel/prior mass

PerfectProbRecovers:
  successMass = totalMass

ProbRecoversAtLeast:
  cross-multiplied finite threshold comparison

chanComp / cascadeTotalMass:
  natural-weight finite channel cascade and path-ensemble mass
```

Checked presentation facts:

```text
exactSupport_implies_perfectProb:
  exact support recovery implies perfect probabilistic recovery for every prior

perfectProb_fullPrior_implies_exactSupport:
  perfect probabilistic recovery under a full-support prior implies exact
  support recovery

perfectProb_not_exact_without_full_prior:
  perfect probabilistic recovery under a non-full-support prior need not imply
  exact support recovery

highProb_not_exactSupport:
  high probabilistic recovery can coexist with support-level ambiguity

cascade_composite_error_le_stage_errors:
  composite decoder error over a finite channel cascade is bounded by the
  union of first-stage and second-stage decoder errors over the same path
  ensemble

cascade_error_bound_same_denominator:
  same-denominator threshold form of the finite cascade error bound

cascadeTotalMass_eq_totalMass_chanComp:
  path-ensemble total mass agrees with composed-channel total mass

cascadeCompositeErrorMass_eq_errorMass_chanComp:
  path-ensemble composite error agrees with composed-channel error mass
```

Interpretation:

```text
Probabilistic channel recovery enriches the finite channel presentation. Exact
support recovery remains the root theorem-transfer object; probabilistic
success is measured by finite natural-weight mass comparisons.
```

Pending:

```text
fixed-declared versus Bayes-best separation:
  Bayes-best target selection should be able to exceed a fixed declared target
  policy in finite examples
```

## Scientific Read

This is a stronger root formalization target than the earlier quantale-presheaf
kernel and the witness-calculus smoke.

The quantale-presheaf kernel remains useful as a strict enriched presentation,
but it is not the root formalism. The witness calculus remains useful as a
prior pressure test, but the normal-lax `DistTrans` formulation is cleaner
because associativity and unit behavior live in ordinary relational
composition.

This pass does not show:

```text
that Omega is empirically realized;
that any Future Field Atlas adapter instantiates the root calculus;
that a substrate exposes relation, distinction, and asymmetry honestly;
that value, valuerhood, agency, identity, compatibility, support, capture, or
erasure has been detected.
```

## Remaining Lean Targets

1. Nontrivial finite normal-lax models.
2. A universal-preservation Boolean presentation variant, if needed.
3. A finite transition-system adapter sketch.
4. Fixed-declared versus Bayes-best policy separation.
5. Normalized or constant-row-total cascade variants, if needed for adapter
   transfer.
6. Richer finite examples connecting abstract admissibility to declared
   distinction-transport obligations without adding valuer semantics.

## Allowed Claim

```text
The support-level normal lax distinction-transport skeleton for Omega Primitive
Calculus v0 is Lean-checkable for DistTrans closure/category laws, the basic
recoverability/non-erasure consequences, and finite-chain recurrent
recoverability, finite-enumeration maximal completion existence, and
Finset/Fintype maximal completion existence. It also checks finite completion
counterexamples showing that pairwise admissibility does not imply joint
admissibility, maximal admissible completions need not be unique, and a
greatest admissible completion need not exist. Finally, it checks a finite
DistTransport counterexample showing that marginal-like non-erasure does not
imply strictly joint non-erasure, and finite adapter-failure examples showing
that theorem transfer fails without source-weakening closure,
target-strengthening closure, or lax composition inclusion. The first worked
Boolean relation support presentation also checks that relation-induced support
transport instantiates the root laws and composes across changed carrier types.
The finite channel / partition presentation checks exact decoder recovery,
identity-channel refinement, channel composition, changed-carrier exact
recovery, and erasure of nontrivial distinctions by a constant channel. The
probabilistic channel presentation checks that exact support recovery implies
perfect probabilistic recovery and that perfect recovery under a full-support
prior implies exact support recovery, while perfect recovery under a
non-full-support prior and high probabilistic recovery do not in general imply
exact support recovery. It also checks a finite cascade union bound: composite
decoder error is bounded by first-stage plus second-stage decoder error over the
same natural-weight path ensemble. Bridge lemmas tie the path-ensemble total and
composite-error masses back to the composed natural-weight channel `chanComp`.
```

## Blocked Claim

```text
Omega proper is empirically validated, value-bearing, or adapter-instantiated.
```
