# Closure Discovery V2

Status: generated finite adapter pilot / closure-language expansion
Scope: richer fact-language closure over finite presentation universes
Claim boundary: adapter-relative finite discovery only; not global invariance,
not natural admissibility, not a canonical implication basis, not agency, not
identity, not value, not valuerhood, not Omega validation

## Purpose

Closure discovery v0 generated:

```text
Boolean predicate facts;
ordered visible-pair facts.
```

Its retained positives were real but modest: they reduced to seed complements
and seed-separated visible pairs.

Closure v2 asks a sharper pilot question:

```text
If the generated fact universe includes dynamic profiles and structural
process-coherence facts, does closure still collapse to trivial predicate
effects?
```

## Implementation

The generator lives at:

```text
omega/adapters/finite_relational/closure_discovery_v2.py
```

The retained validation runner is:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_closure_discovery_v2 `
  --out-root .tmp\finite_relational_closure_discovery_v2
```

The tests are:

```text
tests/test_finite_relational_closure_discovery_v2.py
```

## Fact Universe

Closure v2 facts are still predicates over finite presentations. The universe
now includes:

```text
profile:constant_all
profile:reach:goal
profile:viability:safe_all
profile:safe_prefix_count:h=1
profile:safe_prefix_count:h=2
profile:extendable_safe_prefix_count:h=1
profile:observed_words:goal_status:h=1
profile:observed_words:goal_status:h=2
struct:step_lifting
struct:path_lifting:h=1
struct:path_lifting:h=2
struct:path_lifting:h=3
visible ordered pairs
```

Profile facts hold when a presentation is constant on the profile's fibers.
Structural facts hold when the presentation satisfies the corresponding
process-coherence condition.

## Families

The current v2 sweep has three generated families:

```text
step_lifting_seed_graph_sweep:
  all loop-free directed graphs on three states;
  seed is representative-wise step lifting.

observed_word_seed_graph_sweep:
  all loop-free directed graphs on three states;
  seed is the horizon-1 observed extendable word profile.

constant_seed_control:
  four small graph controls;
  seed is the constant all-states profile.
```

The cases do not include expected surplus annotations.

## Current Result

The retained local run reports:

```text
case_count: 132
dynamic_surplus_case_count: 101
unclassified_dynamic_profile_case_count: 36
collapse_case_count: 31
constant_control_collapsed: true
```

Aggregate surplus counts:

```text
dynamic_surplus_fact_count: 596
seed_determined_dynamic_profile_surplus_fact_count: 146
unclassified_dynamic_profile_surplus_fact_count: 120
seed_forced_structural_surplus_fact_count: 330
```

Family breakdown:

```text
step_lifting_seed_graph_sweep:
  64 cases;
  62 dynamic-surplus cases;
  36 unclassified dynamic-profile cases;
  2 collapse cases.

observed_word_seed_graph_sweep:
  64 cases;
  39 dynamic-surplus cases;
  0 unclassified dynamic-profile cases;
  25 collapse cases.

constant_seed_control:
  4 cases;
  0 dynamic-surplus cases;
  4 collapse cases.
```

## Reading The Result

The v2 result is stronger than v0 in one narrow sense:

```text
richer generated fact languages can produce dynamic closure surplus not
classified as seed-determined profile surplus.
```

The most important positive bucket is:

```text
unclassified_dynamic_profile_surplus
```

These are dynamic profile facts that are forced by the admissible presentation
filter but are not functions of the seed profile facts. In the current sweep,
those cases appear under structural step-lifting pressure.

The result is still a pilot:

```text
it is finite;
it is generated over tiny graphs;
it is not an implication basis;
it does not identify natural admissibility;
it does not certify global invariance.
```

## What Changed Relative To V0

V0 answered:

```text
Can generated closure produce anything beyond the seed?
```

Answer:

```text
Yes, but all retained positives reduce to complements or pair separation.
```

V2 answers:

```text
Can generated closure over richer dynamic facts produce nontrivial pilot
surplus beyond profile-seed determinacy?
```

Answer:

```text
Yes, in small finite graph sweeps with structural process-coherence seeds.
```

## Nonclaims

This note does not claim:

```text
global closure invariance;
natural admissibility;
semantic adequacy of the generated facts;
canonical implication basis;
agency;
identity;
value;
valuerhood;
moral standing;
Omega validation.
```

## Next Questions

The next closure work should not simply add more cases. It should add one of:

```text
canonical implication-basis extraction;
held-out generated graph families;
modal/fixed-point fact grammar;
presentation transport/refinement analysis;
common-refinement or local-coherence diagnostics.
```

## Public Compression

Closure v2 broadens generated closure from Boolean predicates to dynamic
profiles and process-coherence facts. In small finite graph sweeps, structural
step-lifting constraints force dynamic profile surplus not determined by seed
profiles, while constant controls still collapse.
