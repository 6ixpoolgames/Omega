# Closure Implication Basis v2.2

Status: retained finite implication-basis result / guard-accounted closure
checkpoint
Scope: minimal seed and guard antecedents over the current Closure v2.1.5
current and held-out families
Claim boundary: not global invariance, not natural admissibility, not a modal
fixed-point theorem, not a canonical implication basis for all finite systems,
not agency, not identity, not value, not valuerhood, not moral standing, not
Omega validation

## Purpose

Closure v2.1.5 attached every retained surplus fact to a named finite guard
rule. Closure v2.2 asks:

```text
After known guard consequences are accounted for, are there classifier-only or
residual implication rows left?
```

This pass does not run a larger sweep and does not add new fact kinds. It
extracts implication rows from the existing v2.1.5 current and held-out
families.

## Implementation

The implication-basis layer lives at:

```text
omega/adapters/finite_relational/closure_implication_basis_v22.py
```

The validation runner is:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_closure_implication_basis_v22 `
  --out-root .tmp\finite_relational_closure_implication_basis_v22
```

The retained result is:

```text
docs/research_notes/validation_results/finite_relational_closure_implication_basis_v22/
```

Tests:

```text
tests/test_finite_relational_closure_implication_basis_v22.py
```

## Basis Row

Each surplus fact produces one implication row:

```text
minimal seed antecedent facts
minimal guard antecedent facts
consequent fact
bucket
theorem id
proof status
basis kind
```

Minimality is checked inside the generated finite presentation universe for the
case. A candidate antecedent is accepted only when at least one generated
presentation satisfies it and all such presentations satisfy the consequent.

## Current Result

The retained run reports:

```text
case_count: 204
implication_count: 2567
guard_accounted_implication_count: 2567
classifier_only_implication_count: 0
residual_implication_count: 0
unique_seed_implication_count: 56
unique_guard_implication_count: 87
```

Basis-kind counts:

```text
globally_valid: 754
process_coherence_profile_guard: 202
process_coherence_structural_guard: 54
profile_fiber_visibility_guard: 864
seed_profile_functionality_guard: 249
step_to_path_guard: 444
```

Antecedent size counts:

```text
seed antecedent size 0: 754
seed antecedent size 1: 1813
guard antecedent size 0: 754
guard antecedent size 1: 1813
```

## Interpretation

The v2.2 read is:

```text
the current closure implication surface is fully guard-accounted;
no classifier-only implication rows remain;
no residual implication rows remain.
```

This means the Closure v2 branch has now been calibrated through:

```text
v2:
  richer dynamic surplus appears;

v2.1:
  surplus attributes to fixed process-coherence/profile-fiber rules;

v2.1.5:
  every surplus fact is backed by named finite guard rules;

v2.2:
  implication rows over the retained families are fully guard-accounted.
```

The process-coherence guard now has a named Lean spine theorem:

```text
formal/lean/OmegaProper/Trajectory/ObservedWordMonotonicity.lean
processCoherence_entails_boundedObservedProfileInclusion
```

The v2.2 implication rows remain finite adapter-key rows. They become global
theorem instances only after their generated fact keys are mapped to the Lean
theorem's hypotheses.

## Repricing

The closure branch is currently not producing unexplained positive structure.
That is not a failure. It means the instrument is now mostly reporting known
finite guard consequences over the selected fact language.

The next productive step is one of:

```text
pause closure branch and return to formal theorem extraction;

run residual search on larger or stratified held-out families, retaining only
classifier-only or residual rows as new signal;

quotient implication rows by relabeling/complement if future sweeps produce
many redundant rows.
```

## Nonclaims

This note does not claim:

```text
global invariance;
natural admissibility;
canonical implication basis for all finite systems;
modal mu-calculus theorem;
semantic adequacy of generated facts;
agency;
identity;
value;
valuerhood;
moral standing;
Omega validation.
```

## Public Compression

Closure v2.2 extracts a guard-accounted finite implication basis over the
retained Closure v2.1.5 families: all 2,567 implication rows are
guard-accounted, with zero classifier-only and zero residual rows.
