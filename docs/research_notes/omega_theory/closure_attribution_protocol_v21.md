# Closure Attribution Protocol v2.1

Status: protocol note / fixed classifier for Closure v2.1
Scope: attribution of Closure v2 surplus before additional fact-language
expansion
Claim boundary: not global invariance, not natural admissibility, not a modal
fixed-point theorem, not agency, not identity, not value, not valuerhood, not
Omega validation

## Purpose

Closure v2 produced a new positive bucket:

```text
unclassified_dynamic_profile_surplus
```

The v2.1 question is not whether more surplus can be generated. It is:

```text
Can the v2 surplus be attributed to fixed, named explanatory sources?
```

This protocol fixes the attribution rules before interpreting held-out
families.

## Fixed Buckets

The classifier checks surplus facts in this order.

```text
globally_valid:
  the fact holds for every generated presentation, independent of the seed.

seed_determined_profile:
  the profile fact is a function of the seed profile facts.

step_implies_path_lifting:
  a path-lifting structural fact is attributed to step lifting when
  struct:step_lifting is in the closure.

seed_forced_structural:
  another structural fact is forced by an already present process-coherence
  support.

seed_profile_separation:
  a visible-pair fact is explained by a seed profile that separates the pair.

profile_fiber_separation:
  a visible-pair fact is explained by a closure profile that separates the pair.

bounded_process_coherence_invariance:
  a dynamic profile fact is explained when all finite presentations satisfying
  one fixed process-coherence support fact also respect that profile.

process_coherence_separation:
  a visible-pair fact is explained when a fixed process-coherence support fact
  alone forces that pair to remain visible.

residual:
  none of the fixed rules explains the fact.
```

## Process-Coherence Support Facts

The fixed support facts are:

```text
struct:step_lifting
struct:path_lifting:h=1
struct:path_lifting:h=2
struct:path_lifting:h=3
```

The v2.1 classifier does not add new fact kinds. It reuses the Closure v2 fact
universe and asks whether surplus facts are attributable to these supports.

## Held-Out Families

After the classifier is fixed, v2.1 applies it to:

```text
current_v2_attribution:
  the retained n=3 Closure v2 families.

heldout_n4_step_lifting_sample:
  32 sampled loop-free four-state graphs, seed struct:step_lifting.

heldout_n4_observed_word_sample:
  32 sampled loop-free four-state graphs, seed horizon-1 observed word profile.

heldout_n4_constant_control:
  8 sampled loop-free four-state graphs, seed profile:constant_all.
```

The n=4 families are sampled, not exhaustive. This is a held-out pilot, not a
scaling theorem.

## Decision Rule

Interpretation:

```text
residual_count = 0:
  v2 surplus is attributed by the fixed classifier. Treat v2 as instrument
  calibration for known process-coherence invariance.

residual_count > 0:
  freeze residual representatives and inspect whether they indicate a missing
  theorem or an artifact of the classifier/fact language.
```

Either outcome is useful. A zero-residual result is not a failure; it means the
instrument rediscovered theorem-shaped structure.

## Nonclaims

This protocol does not claim:

```text
global invariance;
natural admissibility;
canonical implication basis;
modal mu-calculus formalization;
agency;
identity;
value;
valuerhood;
moral standing;
Omega validation.
```

## Public Compression

Closure v2.1 fixes the attribution rules before adding more fact languages:
explain current surplus first, then treat only residuals as genuinely new
closure targets.
