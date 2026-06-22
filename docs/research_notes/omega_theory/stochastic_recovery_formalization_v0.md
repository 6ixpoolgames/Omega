# Stochastic Recovery Formalization v0

Status: Lean theorem-spine checkpoint
Scope: exact rational finite recovery, observation refinement, randomized decoder embedding, joint recovery, and finite-horizon policy continuation
Claim boundary: not identity, not agency, not value, not valuerhood, not empirical channel validity, not a moral threshold, not Omega validation

## Compression

Support-exact recovery is not the general recovery object. It is the zero-error
endpoint of a source-indexed recovery profile.

The central finite profile is:

```text
Rec_delta(x) = Pr[delta(observe(Y)) = target(x) | X = x]
```

The Lean layer models this with exact rational finite channels:

```text
RatChannel X Y
Success C target observe decoder x
DeclaredRecoveryAt C target observe tau decoder
RecoveryExistsAt C target observe tau
```

The main bridge theorem is:

```text
support-exact recovery iff RecoveryExistsAt 1
```

This keeps exact support recovery as a sharp boundary condition while giving the
stochastic layer a graded form.

## Lean Modules

Current files:

```text
formal/lean/OmegaProper/Recovery/FiniteChannel.lean
formal/lean/OmegaProper/Recovery/Deterministic.lean
formal/lean/OmegaProper/Recovery/ObservationRefinement.lean
formal/lean/OmegaProper/Recovery/Randomized.lean
formal/lean/OmegaProper/Recovery/Joint.lean
formal/lean/OmegaProper/Recovery/PolicyContinuation.lean
formal/lean/OmegaProper/Recovery/Examples.lean
formal/lean/OmegaProper/Recovery.lean
```

They are imported by:

```text
formal/lean/OmegaProper.lean
```

## Proved Shape

The current Lean layer proves:

```text
Success is nonnegative.
FailureMass is nonnegative.
Success + FailureMass = 1.
Success <= 1.
Success = 1 iff FailureMass = 0.
RecoveryExistsAt is monotone downward in threshold.
RecoveryExistsAt 1 iff some decoder has Success = 1 for every source.
No nonempty source type has RecoveryExistsAt tau when 1 < tau.
Support-exact decoder iff Success = 1 for every source.
Support-exact recovery iff RecoveryExistsAt 1.
```

It also proves:

```text
Coarse decoder lifting under deterministic observation refinement.
Recovery monotonicity under observation refinement.
Support-exact recovery monotonicity under observation refinement.
Deterministic decoders embed into randomized decoders.
Deterministic recovery implies randomized recovery.
Randomized recovery is monotone under observation refinement.
Joint recovery implies each projected marginal recovery.
Same-panel exact marginal decoders pair into exact joint recovery.
Policy-conditioned action kernels induce ordinary rational kernels.
Finite-horizon hit probabilities are nonnegative, bounded by 1, and monotone
  in the horizon.
Equal selected policy rows imply equal induced hit profiles.
```

## Strictness Witnesses

The finite examples show:

```text
99/100 deterministic recovery can fail support-exact recovery.
Two channels can have the same positive support but different threshold
  recovery.
One constant observation cannot deterministically recover two source classes
  at threshold 1/2.
A uniform randomized decoder can reach threshold 1/2 on that same one-label
  observation.
Separate marginal observations can each recover their own marginal target
  while neither marginal observation recovers the joint target.
```

These are toy finite witnesses, not empirical results.

## Python Parity Map

The Lean layer corresponds to the current finite relational adapter vocabulary:

```text
RatChannel                     <-> Channel / TransitionKernel
PositiveSupport                <-> positive-probability support
Success                        <-> success_by_source
DeclaredRecoveryAt             <-> per-source threshold check
RecoveryExistsAt               <-> deterministic capacity-at-threshold
RandomizedSuccess              <-> randomized_success_by_source
FactorsThrough fine coarse     <-> observation refinement / coarsening
HitWithin                      <-> hit_probability_within_horizon
HitProfile                     <-> hit_profile / policy horizon profile
```

Lean does not depend on retained Python JSON. Shared examples are parity
witnesses only.

## Claim Boundary

Approximate recovery is always relative to supplied structure:

```text
declared source states;
declared target;
declared observation;
declared decoder class;
declared threshold;
and, later, declared prior or ambiguity set when those are introduced.
```

The current layer does not claim:

```text
empirical channel validity;
Bayes-optimal policy validation;
general randomized optimization;
prior-relative value;
robust ambiguity-set recovery;
identity;
agency;
value;
valuerhood;
Omega validation.
```

## Validation

Local theorem check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaOmega
rg -n "\b(sorry|admit|axiom)\b" formal\lean -g "*.lean"
git diff --check
```

Relevant Python parity checks:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests\test_finite_relational_stochastic_recovery.py `
  tests\test_stochastic_recovery_theorem_spine.py `
  tests\test_finite_relational_policy_dynamics.py `
  -q --basetemp .tmp\pytest-formal-recovery -p no:cacheprovider

.\.venv\Scripts\python.exe -m omega.validation.finite_relational_stochastic_recovery
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_policy_dynamics
```

## Next Formal Work

Next likely extensions:

```text
prior-relative expected recovery;
robust recovery over ambiguity sets;
finite randomized optimization only after a clear finite rational LP surface;
joint approximate recovery bounds when paired decoders are used.
```

These should remain separate axes rather than being collapsed into one scalar.
