# Recovery Layer Checkpoint v0

Status: formal checkpoint note
Scope: exact rational finite recovery, decoder classes, robustness, randomized robustness, priors, joint recovery, and finite-horizon policy hit profiles
Claim boundary: not empirical channel validity, not value, not agency, not valuerhood, not identity, not Omega validation

## Purpose

The recovery arm is now a compact finite theorem surface rather than a set of
isolated examples. It supplies the fact vocabulary needed for later
admissibility, decomposition-invariance, and Gradient Ethics bridge work.

The central lesson is:

```text
recovery is not one scalar.
```

The formal layer separates:

```text
support-exact recovery;
graded per-source recovery;
restricted decoder-class recovery;
randomized decoder recovery;
robust randomized recovery over ambiguity sets;
joint versus marginal recovery;
policy-conditioned finite-horizon hit profiles;
robust recovery over ambiguity sets;
prior-relative expected recovery.
```

## Formal Surface

Main Lean files:

```text
formal/lean/OmegaProper/Recovery/FiniteChannel.lean
formal/lean/OmegaProper/Recovery/ConfusionBound.lean
formal/lean/OmegaProper/Recovery/CoarseningPermanence.lean
formal/lean/OmegaProper/Recovery/Deterministic.lean
formal/lean/OmegaProper/Recovery/ObservationRefinement.lean
formal/lean/OmegaProper/Recovery/Randomized.lean
formal/lean/OmegaProper/Recovery/Robust.lean
formal/lean/OmegaProper/Recovery/RobustRandomized.lean
formal/lean/OmegaProper/Recovery/Prior.lean
formal/lean/OmegaProper/Recovery/Joint.lean
formal/lean/OmegaProper/Recovery/PolicyContinuation.lean
formal/lean/OmegaProper/Recovery/Examples.lean
```

Umbrella:

```text
formal/lean/OmegaProper/Recovery.lean
```

## Main Distinctions

### Exact Versus Graded

Support-exact recovery is the zero-error endpoint:

```text
support-exact recovery iff RecoveryExistsAt 1.
```

High-confidence graded recovery can exist without support-exact recovery.

Shared observed mass creates a quantitative obstruction:

```text
if two target-distinct sources put at least epsilon probability on outputs
with the same observed label, deterministic recovery above 1 - epsilon is
impossible.
```

### Unrestricted Versus Declared Decoder Class

Unrestricted existence is separated from allowed decoder-class access:

```text
RecoveryExistsAt
RecoveryExistsInAt
RandomizedRecoveryAt
RandomizedRecoveryInAt
RandomizedFamilyRecoveryAt
ExpectedRecoveryExistsAt
ExpectedRecoveryExistsInAt
RobustRecoveryAt
RobustRecoveryInAt
RobustRandomizedRecoveryAt
RobustRandomizedRecoveryInAt
RobustRandomizedFamilyRecoveryAt
```

This prevents hidden decoder power from being confused with declared recovery
capacity.

### Worst-Case Versus Expected

Worst-case threshold recovery implies expected threshold recovery under any
declared prior. The converse fails: a skewed prior can hide a bad source.

### Per-Channel Versus Robust

Each channel in an ambiguity set may be exactly recoverable with its own
decoder while no single decoder recovers the whole ambiguity set. Robust
recovery is a uniform-decoder claim.

Robust randomized recovery has the same uniform-over-ambiguity-set shape using
one randomized decoder, optionally restricted by an allowed randomized-decoder
class.

The current layer also names declared randomized-decoder family recovery and
robust declared randomized-decoder family recovery. The adapter can optimize
exactly over such a supplied finite family. This is still not global randomized
maximin optimization.

### Marginal Versus Joint

Joint recovery safely projects to marginal recovery. Separate marginal panels
do not automatically recover the joint target.

### Observation Refinement Versus Coarsening

If a coarse observation factors through a fine observation, the fine observation
can simulate any coarse decoder. Coarsening cannot create recovery capacity for
an unrestricted decoder class over an already available fine observation.

The formal layer now records the contrapositive as coarsening permanence:
failed deterministic, support-exact, robust, or randomized recovery claims
persist under deterministic coarsening. Robust randomized failures also persist
under this deterministic coarsening discipline. Restricted decoder-class
variants require explicit decoder lifting.

## Guardrail Witnesses

The finite examples now include:

```text
99/100 recovery need not be support-exact;
same positive support can have different recovery thresholds;
randomized decoding can beat deterministic decoding in a one-label case;
finite declared randomized-family enumeration selects the uniform decoder in
  that one-label case;
separate marginal observations do not recover the joint target;
per-channel exact recovery does not imply robust common-decoder recovery;
finite declared robust randomized-family enumeration selects the uniform
  decoder in the identity/flipped ambiguity case;
high expected recovery under a skewed prior does not imply worst-case recovery.
```

## Why This Matters

The recovery arm now supplies candidate continuation facts for the
admissibility program:

```text
which recovery facts survive a presentation?
which are lost by coarsening?
which require decoder-class access?
which persist across uncertainty?
which disappear under a prior/worst-case switch?
```

These questions are now theorem-shaped. They can be used to test whether a
candidate presentation preserves consequence-bearing continuation facts rather
than merely looking good under one summary.

## Current Non-Claims

The recovery layer does not claim:

```text
that a declared channel is empirically correct;
that a declared prior is empirically correct;
that a declared ambiguity set is complete;
that a decoder class is natural unless supplied by provenance;
that recovery is value;
that recovery is agency;
that recovery is identity;
that recovery validates Omega.
```

## Next Bridge Targets

Near-term theorem targets:

```text
recovery facts become entries in a presentation/fact admissibility ledger.
```

Near-term pilot target:

```text
adversarially test whether admissible presentation families collapse recovery
facts to constants.
```
