# Constraint-Based Alignment Floor v0

Status: public-facing milestone note
Scope: current constraint-based alignment result supported by Layer A theorem and adapter surfaces
Claim boundary: not a complete alignment theory, not value, not agency, not identity, not valuerhood, not Omega validation

## The Claim

The current stack supports a weak but meaningful alignment result:

```text
Even before a full theory of value, agency, or Omega, we can formally reject
representations that erase, fake, or hide consequence-bearing continuation
facts.
```

This is the constraint-based alignment floor.

It does not say what to maximize. It says that some maps are already unsafe as
maps:

```text
they merge states whose declared consequences differ;
they preserve a proxy while the target changes;
they fabricate reachability or viability;
they hide loss of a continuation fact;
they report individual robust attainability while the joint target fails.
```

That is a real interim result because many alignment failures are failures of
representation before they are failures of final value theory.

## Why This Matters

AI systems act through compressed presentations:

```text
benchmarks;
reward models;
world models;
policy classes;
abstractions;
state summaries;
boundaries;
safety monitors.
```

If the presentation hides that a future has lost a necessary distinction, or
claims a path exists when the exact dynamics do not support it, then the system
can look aligned under the presentation while the exact continuation has
already crossed a dangerous boundary.

The floor says:

```text
do not trust a map, metric, policy, or abstraction merely because it is useful;
trust it only when it preserves the consequence-bearing facts it is being used
to reason about.
```

This is not a total value function. It is "yellow paint" for part of the
viability corridor: a set of formal constraints saying which representations
cannot certify safe continuation.

## Evidence Bundle

The result is not a single theorem. It is a small theorem spine with matching
finite witnesses and adapter checks.

### Unsafe Merges

Sound quotient and presentation discipline say that a proposed merge is safe
only when it is licensed by consequence-identifiability.

If a quotient merges consequence-separated states, it is not a sound map for
that target.

Relevant files:

```text
formal/lean/OmegaProper/Trajectory/SoundQuotient.lean
formal/lean/OmegaProper/Trajectory/PresentationSoundness.lean
docs/research_notes/omega_theory/standard_core_compression_v0.md
```

### Proxy Failure

Non-factorization says that when a summary stays fixed while the declared
target changes, the target cannot be recovered from that summary.

This is the anti-Goodhart component:

```text
same proxy score;
different safety-relevant target;
therefore the proxy does not determine the target.
```

Relevant files:

```text
formal/lean/OmegaProper/BaselineWitnesses/NonFactorization.lean
formal/lean/OmegaProper/BaselineWitnesses/InvarianceNonFactorization.lean
docs/research_notes/omega_theory/nonfactorization_witness_index_v0.md
```

### Phantom Continuation

Bad presentations can fabricate future structure:

```text
abstract system says a path exists;
exact system has no such path.
```

Relevant files:

```text
formal/lean/OmegaProper/Trajectory/PhantomReachability.lean
formal/lean/OmegaProper/Trajectory/PhantomViability.lean
docs/research_notes/omega_theory/phantom_reachability_under_unsound_quotient_v0.md
```

### Hidden Loss

Bad presentations can also hide loss:

```text
before system had a continuation fact;
after system loses it;
abstract presentation still reports it.
```

Relevant files:

```text
formal/lean/OmegaProper/Trajectory/HiddenLossUnderBadPresentation.lean
formal/lean/OmegaProper/Trajectory/HiddenViabilityLossUnderBadPresentation.lean
docs/research_notes/omega_theory/hidden_reach_loss_under_bad_presentation_v0.md
docs/research_notes/omega_theory/hidden_viability_loss_under_bad_presentation_v0.md
```

### Stochastic Recovery

Support-exact recovery is not the whole recovery object. It is the
threshold-one endpoint of a source-indexed recovery profile.

The recovery layer separates:

```text
support-exact;
approximate threshold;
restricted decoder class;
randomized decoder;
robust ambiguity set;
prior-relative;
marginal vs joint;
policy-conditioned hit profile.
```

This matters because stochastic safety claims can fail by changing the axis:

```text
high expected recovery does not imply worst-case recovery;
per-channel recovery does not imply robust common-decoder recovery;
marginal recovery does not determine joint recovery.
```

Relevant files:

```text
formal/lean/OmegaProper/Recovery/
docs/research_notes/omega_theory/recovery_layer_checkpoint_v0.md
docs/research_notes/omega_theory/stochastic_recovery_theorem_spine_v0.md
```

### Individual Robustness Is Not Joint Robustness

The policy-conditioned layer includes a finite correlated-shock witness:

```text
target A is robustly attainable by a declared policy;
target B is robustly attainable by a declared policy;
the joint target is not robustly attainable by any declared policy.
```

This blocks a tempting inference:

```text
individual robust attainability implies joint robust attainability.
```

Relevant files:

```text
formal/lean/OmegaProper/Recovery/PolicyContinuation.lean
formal/lean/OmegaProper/Recovery/Examples.lean
docs/research_notes/omega_theory/policy_conditioned_stochastic_dynamics_v0.md
docs/research_notes/validation_results/finite_relational_policy_dynamics_v0.json
```

## What This Does Not Prove

This floor does not prove:

```text
what value is;
which targets are morally correct;
that a declared target is semantically right;
that a supplied adapter is empirically faithful;
that an agent has been detected;
that a valuer has been detected;
that Omega exists or has been validated.
```

The result is conditional:

```text
given declared consequence, recovery, transition, policy, or adapter surfaces,
these representations fail or pass exact integrity checks.
```

That is enough to reject some unsafe maps. It is not enough to certify a full
alignment solution.

## Why It Is Still Significant

The floor gives the project a practical output before the full Alpha-Omega
ambition is solved.

It supports a weak alignment workflow:

```text
1. declare the consequence-bearing target;
2. declare the presentation, proxy, policy, or adapter;
3. test whether the representation preserves the relevant continuation fact;
4. reject it if it hides loss, fabricates continuation, or fails
   non-factorization.
```

This is the current useful bridge to Gradient Ethics / value preservation under
uncertainty:

```text
under uncertainty and irreversibility, preserving the conditions for
value-bearing continuation becomes a safety constraint even before final value
theory is complete.
```

The current stack does not complete that program. It gives the lower
constraint floor the program needs.

