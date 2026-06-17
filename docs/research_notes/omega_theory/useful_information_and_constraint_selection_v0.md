# Useful Information And Constraint Selection V0

Status: integration note
Scope: lessons imported from adjacent complexity/information work into the
finite relational adapter and lushness roadmap
Claim boundary: not an implementation of epiplexity, not a new complexity
measure, not Omega validation

## Sources

This note uses the archived reference records in:

```text
../../references/useful_information_and_constraint_selection_refs.md
```

The relevant adjacent papers are:

- Bennett, "Is Complexity an Illusion?", arXiv:2404.07227.
- Finzi et al., "From Entropy to Epiplexity", arXiv:2601.03220.

## Imported Lessons

The useful import from Bennett is not "complexity is irrelevant" as a slogan.
It is narrower:

```text
simple form is not automatically the source of generalization;
the functional constraint being selected matters.
```

In repo terms:

```text
same simple-form summary
does not imply
same declared consequence/recovery target.
```

The useful import from Finzi et al. is similarly narrow:

```text
entropy, Kolmogorov-style complexity, and unordered data summaries can miss
useful structure for computationally bounded observers.
```

In repo terms:

```text
same entropy / same histogram / same unordered bag
does not imply
same bounded recovery or order-sensitive continuation fact.
```

## Translation Into The Current Stack

The current standard compression already has the right language:

```text
summary f : A -> B
target  g : A -> C

If g does not factor through f, f is not a safe proxy for g.
```

The adapter version is:

```text
finite source
-> finite relational IR
-> declared summary / observation / decoder family
-> audit whether the declared target is preserved or recoverable.
```

The bounded-useful-structure batch adds these concrete surfaces:

```text
simple_form_nonfactorization_fail:
  same simple-form summary, different declared functional target.

entropy_controlled_nonfactorization_fail:
  same entropy/histogram summary, different bounded-recoverability target.

ordered_trace_nonfactorization_fail:
  same unordered bag summary, different order-sensitive recovery target.

bounded_recovery:
  declared observation + declared decoder family + declared target predicate;
  asks whether any bounded decoder in the family exactly recovers the target.
```

This is the smallest adapter-level import from the two papers. It does not
claim to estimate epiplexity. It only forces proxy metrics to show that they
preserve the declared recovery target.

## Bounded Recovery Audit

The bounded recovery audit has the shape:

```text
observation : state -> observation_label
decoders    : observation_label -> truth_label
target      : state -> Bool
```

The audit reports:

```text
recoverable:
  whether any declared decoder exactly recovers target membership;

successful_decoders:
  the decoders that recover the target;

ambiguous_observation_labels:
  labels whose preimage mixes target-true and target-false states.
```

The audit is family-relative. A failure means:

```text
no declared decoder in this bounded family recovers the target.
```

It does not mean:

```text
no possible decoder in any richer class could recover the target.
```

That restriction is deliberate. It keeps the bounded-observer assumption visible
rather than smuggling in an unbounded recovery oracle.

## Lushness Consequence

This note tightens the current lushness language.

Avoid:

```text
lushness = state count
lushness = branch count
lushness = entropy
lushness = complexity
```

Use, as a provisional Layer A target:

```text
lushness candidate =
  soundly presented,
  boundedly recoverable,
  consequence-bearing continuation structure
  inside the relevant viability / compatibility constraints.
```

This is still not value. It is a candidate substrate measure for future
value-bearing continuation. The point of the bounded recovery audit is to keep
that candidate from collapsing into raw entropy or simple branching.

## Near-Term Implications

Immediate adapter discipline:

```text
1. Keep simple-form, entropy, and unordered summaries as audit targets, not as
   trusted measures.
2. Require bounded decoder families whenever a useful-information claim is
   observer-relative.
3. Record when a target fact changes while a proxy summary remains fixed.
4. Prefer retained JSON audit results for validation surfaces; use markdown only
   for explanatory summaries.
```

Future formal work:

```text
summary invariant + bounded recovery target changes
-> non-factorization
```

This is likely just the existing invariance/non-factorization theorem applied
to bounded recovery facts. Do not formalize epiplexity itself until the adapter
surface has stabilized.

## Non-Claims

This note does not claim:

```text
complexity never matters;
entropy is useless;
epiplexity has been implemented;
bounded recovery proves value;
bounded recovery proves agency;
the finite fixtures scale to real systems;
Omega has been validated.
```

The claim is smaller and operational:

```text
proxy summaries of complexity, entropy, or unordered data must be audited
against declared consequence/recovery targets before they can support
continuation claims.
```
