# Recovery / Policy Consolidation Audit v0

Status: consolidation audit
Scope: finite recovery, stochastic recovery, robust recovery, randomized families, policy-conditioned hit profiles, retained adapter parity
Claim boundary: organizational audit only; not new theory, not empirical validation, not value, agency, identity, or Omega validation

## Purpose

The recovery and policy-conditioned layers have grown quickly. This note audits
the new machinery for possible consolidation before more theory is added.

The goal is not to compress every surface into one abstraction. Some axes are
intentionally separate because collapsing them would hide real assumptions.

## Current Shape

The Lean recovery stack currently separates these axes:

```text
finite exact channel:
  RatChannel

source-indexed deterministic profile:
  Success
  RecoveryProfile
  DeclaredRecoveryAt
  RecoveryExistsAt
  RecoveryExistsInAt

support-exact endpoint:
  ExactRecoverySupport
  supportExactRecovery_iff_recoveryAt_one

observation refinement:
  liftDecoder
  recovery monotonicity under refinement
  coarsening failure permanence

randomized decoder axis:
  RandomizedDecoder
  RandomizedSuccess
  RandomizedRecoveryAt
  RandomizedRecoveryInAt

declared randomized family axis:
  RandomizedFamilyAllowed
  RandomizedFamilyRecoveryAt
  RobustRandomizedFamilyRecoveryAt

robust ambiguity axis:
  RobustRecoveryAt
  RobustRecoveryInAt
  RobustRandomizedRecoveryAt
  RobustRandomizedRecoveryInAt

prior-relative axis:
  RatPrior
  ExpectedSuccess
  ExpectedRecoveryExistsAt
  ExpectedRecoveryExistsInAt

joint axis:
  jointTarget
  pairDecoder
  joint-to-marginal projection
  same-panel Frechet / union-bound floor

policy-conditioned continuation axis:
  RatActionKernel
  inducedKernel
  HitWithin
  HitProfile
  RobustPolicyHitAt
  PolicyFamilyRobustHitAt
```

The Python adapter stack mirrors much of this in exact rational finite studies:

```text
stochastic_recovery.py:
  deterministic success vectors;
  optimized deterministic decoders;
  randomized decoder families;
  robust ambiguity-set checks;
  joint/marginal and union-bound checks.

stochastic_continuation_loss.py:
  finite transition kernels;
  finite-horizon hit profiles;
  stale/reflected hidden loss.

stochastic_policy_dynamics.py:
  action kernels;
  deterministic policies;
  robust policy-family hit optimization;
  correlated-shock joint robustness witness.
```

## Good Separation

These distinctions should remain explicit.

### Deterministic vs randomized decoders

Randomized recovery is not just an implementation detail of deterministic
recovery. The one-label strictness witness makes this separation load-bearing.

Keep:

```text
RecoveryExistsAt / RecoveryExistsInAt
RandomizedRecoveryAt / RandomizedRecoveryInAt
```

### Unrestricted existence vs declared decoder access

The `InAt` forms prevent hidden decoder power from entering a claim. This is
central to the registry/bounded-observer discipline.

Keep:

```text
RecoveryExistsAt        as unrestricted shorthand
RecoveryExistsInAt      as declared-class form
RandomizedRecoveryInAt  as declared randomized-class form
```

### Per-channel recovery vs robust ambiguity-set recovery

The identity/flipped-channel witness proves that per-channel recovery does not
imply one common robust decoder over an ambiguity set.

Keep robust forms separate.

### Worst-case vs prior-relative recovery

Prior-relative expected recovery can hide bad source states. This must not be
collapsed into worst-case threshold recovery.

### Marginal vs joint recovery

The same-panel union-bound theorem gives a safe lower bound, not a replacement
for joint characterization. Separate marginal panels remain insufficient for
joint recovery.

### Fixed transition kernels vs policy-conditioned kernels

`HitWithin` over a fixed kernel and `HitWithin (inducedKernel K policy)` are
related but not identical modeling surfaces. Policy-conditioned results carry
extra supplied structure: actions, action kernel, policy class, and ambiguity
set.

## Consolidation Status

### 1. Checkpoint docs

`recovery_layer_checkpoint_v0.md` was updated in this consolidation pass to
reflect:

```text
RandomizedFamily.lean;
RobustRandomizedFamilyRecoveryAt;
ConfusionBound.lean;
CoarseningPermanence.lean;
RobustPolicyHitAt;
PolicyFamilyRobustHitAt;
jointShock_individual_robust_not_joint_robust.
```

It now also includes a vocabulary table for the main recovery suffixes and
explicitly warns against compressing all recovery surfaces into one overloaded
predicate.

### 2. Remove stale "next theorem" wording

`stochastic_recovery_theorem_spine_v0.md` previously listed:

```text
Lean theorem for support-exact recovery iff support disjointness
```

as future work. The repo already has:

```text
ExactRecoverySupport.exactRecoveryExists_iff_observedSupportDisjoint;
Deterministic.supportExactRecovery_iff_recoveryAt_one.
```

The future target should instead be:

```text
package the two facts as a single public bridge statement, if useful.
```

This wording has now been updated in the theorem-spine note.

### 3. Vocabulary table

The checkpoint note now records:

```text
At      = unrestricted existential threshold claim
InAt    = existential threshold claim inside an allowed witness class
Family  = InAt over the image of an indexed declared family
Robust  = uniform witness over an ambiguity set
Prior   = expected threshold under a declared prior
Policy  = finite-horizon hit under induced action kernel
Support-exact = threshold-one positive-support endpoint
```

This reduces apparent jargon without changing Lean semantics.

## Safe Future Refactors

### 1. Split `Examples.lean` later if it keeps growing

`Examples.lean` now contains deterministic, randomized, robust, prior, joint,
and policy-conditioned examples. This is acceptable now, but it is becoming a
mixed witness file.

Safe future split:

```text
Recovery/Examples/Channel.lean
Recovery/Examples/Joint.lean
Recovery/Examples/Policy.lean
Recovery/Examples.lean as umbrella
```

Do not split immediately unless edits in `Examples.lean` become painful.

### 2. Consider a small `AllowedImage` helper

The family pattern appears in randomized family recovery and policy-family
robust hit:

```text
family : I -> Witness
Allowed witness := exists i, family i = witness
```

A generic helper could reduce repetition:

```text
ImageAllowed family witness := exists i, family i = witness
```

This is a safe Lean refactor only if it reduces imports and does not make
proofs harder. It is not urgent.

### 3. Consider a generic Python optimization result later

Python currently has parallel result dataclasses:

```text
OptimizedDecoderResult
RobustOptimizedDecoderResult
OptimizedRandomizedFamilyDecoderResult
RobustOptimizedRandomizedFamilyDecoderResult
RobustPolicyFamilyResult
```

They share a pattern:

```text
selected witness;
per-source or per-kernel profile;
worst-case scalar.
```

A generic result shape might reduce duplication. This is lower priority because
typed, explicit dataclasses currently help readability and auditability.

## Risky Over-Compression

Avoid these consolidations for now.

### Do not collapse all recovery forms into one mega-definition

A single generalized `Recovery` structure parameterized by witness type,
criterion, prior, ambiguity, and target would be mathematically possible but
bad for the current project. It would hide the exact assumptions each theorem
uses.

### Do not treat randomized family enumeration as global optimization

Declared finite randomized-family recovery is deliberately not global
randomized maximin. It should stay bounded until an explicit rational LP
surface exists.

### Do not merge policy hit with recovery profiles

Policy hit is a continuation fact over a transition system. Recovery is a
source/output/decoder fact over a channel. They can be related later, but
forcing one into the other now would erase useful modeling distinctions.

### Do not replace support-exact recovery with approximate recovery

Support-exact recovery remains useful as the zero-error endpoint and as a
support-disjointness bridge. The graded layer generalizes it; it does not make
it obsolete.

## Recommended Consolidation Batch

Do this before adding more theory:

```text
1. Update recovery_layer_checkpoint_v0.md.
2. Update stochastic_recovery_theorem_spine_v0.md to remove stale future work.
3. Add the vocabulary table for At / InAt / Family / Robust / Prior / Policy.
4. Add a short "do not over-compress" section to the checkpoint.
5. Leave Lean code unchanged unless a tiny `ImageAllowed` helper becomes clearly useful.
```

After that batch, the recovery/policy stack will be easier to audit without
erasing the distinctions that make it useful.

## Bottom Line

The new machinery is not random sprawl, but it is beginning to look sprawling
because the same few axes recur under different names.

The right consolidation is mostly documentary and naming-level:

```text
explain the axes;
mark which ones are load-bearing;
remove stale future-work text;
avoid premature mega-abstractions.
```

Only after that should we consider Lean refactors such as `ImageAllowed` or an
examples-file split.
