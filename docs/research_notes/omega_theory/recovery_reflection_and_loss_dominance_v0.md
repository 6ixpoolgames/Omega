# Recovery Reflection and Nonrecoverable-Loss Dominance v0

Status: Lean theorem checkpoint / recovery-gate and declared-profile order
Scope: recovery-frame reflection, local-vs-joint loss stress witnesses, and finite declared loss-profile dominance
Claim boundary: not harm, not rights, not patienthood, not moral standing, not final value, not agency, not identity, not Omega validation

## Purpose

The recovery-aware corridor already had the negative gate:

```text
if a successor nonrecoverably contracts a declared recovery fact,
then the action is not licensed against that recovery-aware corridor.
```

This checkpoint adds three pieces around that gate:

```text
1. a positive reflection theorem:
   if the believed recovery frame reflects into the true recovery frame,
   believed recovery-aware licenses are true recovery-aware licenses;

2. a local-vs-joint stress witness:
   locally total nonrecoverable loss can be joint-corridor licensed,
   while local persistence can still be joint-corridor refused;

3. a thin nonrecoverable-loss dominance order:
   declared contraction profiles can be compared by down-closed inclusion
   in the declared fact preorder.
```

The result is still below moral theory. It compares declared profile facts and
gates licenses relative to declared recovery frames.

## Lean Surface

Formal files:

```text
formal/lean/OmegaProper/Decision/RecoveryAwareCorridor.lean
formal/lean/OmegaProper/Decision/RecoveryLossStress.lean
formal/lean/OmegaProper/Decision/NonrecoverableLossDominance.lean
formal/lean/OmegaProper/Decision/NonrecoverableLossDominanceExamples.lean
```

## Recovery-Frame Reflection

Definition:

```text
RecoveryFrameReflects Believed True h :=
  every bounded recovery fact accepted by Believed
  is accepted by True.
```

Main theorems:

```text
recoveryAwareCorridor_reflects_of_recoveryFrameReflects
recoveryFrame_reflection_preserves_license
```

Reading:

```text
If a believed recovery frame cannot fabricate bounded recoverability relative
to the true frame, then a license against the believed recovery-aware corridor
transports to the true recovery-aware corridor.
```

This is the positive twin of the phantom-recoverability witness. Corruption can
counterfeit a license; reflection blocks that failure mode.

## Local-Vs-Joint Stress Witness

Formal theorem:

```text
W_sacrifice_cancer_joint_stress
```

Shape:

```text
sacrifice move:
  locally nonrecoverable;
  joint-recoverable;
  licensed by the joint recovery-aware corridor.

cancer move:
  local fact persists;
  joint fact is nonrecoverably contracted;
  refused by the joint recovery-aware corridor.
```

This is the apoptosis stress test in formal, claim-bounded language. It blocks
the naive proxy:

```text
local nonrecoverable contraction = harm
```

The theorem does not say sacrifice is morally good or that cancer is morally
bad. It says the relevant comparison has to be indexed to the declared joint
profile, not just to the local self-maintenance profile.

## Declared Loss-Profile Dominance

Definitions:

```text
ContractionProfile Fact := Fact -> Prop

DownClosedProfile P f :=
  exists g, P g and f <= g

LossDominates P Q :=
  every down-closed declared loss of Q
  is also a down-closed declared loss of P.
```

Main theorems:

```text
lossDominates_refl
lossDominates_trans
lossDominates_iff_hoareDominates
not_lossDominates_iff_exists_failure_certificate
lossDominates_iff_all_monotone_valuation_covers
```

The acceptance bridge reuses ODT1:

```text
loss dominance
iff
unanimous pointwise cover across monotone valuations of declared facts.
```

This is value-parametric, not value-free. The fact preorder and admissible
monotone valuations are registered inputs.

## Incomparability Witness

Formal theorem:

```text
W_disjoint_loss_profiles_incomparable
```

It uses two declared facts:

```text
local
joint
```

Under a discrete declared fact order:

```text
loss of local
and
loss of joint
```

are incomparable unless the register supplies an order connecting them.

## Register Liability

The layer preserves the registry-first discipline:

```text
undeclared vulnerable facts are invisible to the gate;
overdeclared vulnerable facts can paralyze the floor;
corrupted recovery frames can counterfeit licenses;
declared fact orders control which losses compare.
```

That is the point of the positive and negative pair:

```text
reflection blocks phantom licenses;
failure of reflection can create phantom licenses.
```

## Public Compression

```text
The recovery gate now has both halves: if recovery evidence reflects to the
true frame, licenses are preserved; if the recovery register is corrupted,
phantom licenses can appear. Separately, nonrecoverable-loss comparison is now
a declared-profile partial order, and the sacrifice/cancer witness shows why
local self-loss is not the same thing as joint loss.
```

## Nonclaims

This note does not claim:

```text
that nonrecoverable loss is always harm;
that local persistence is morally better than local sacrifice;
that joint profiles are automatically morally authoritative;
that patienthood, standing, rights, value, agency, identity, or Omega has been
derived.
```

## Next Pressure

The next natural target is endogenous register update:

```text
which register updates preserve the reflection condition that prevents
phantom licenses?
```

That is the no-laundering problem for recovery-aware gates.
