# Omega v2 Robust Joint Separation Protocol v0

Status: preregistration / finite May-versus-Robust separation protocol

Date: 2026-08-04

## Purpose

The retained May and Robust realization core already distinguishes:

```text
May(G):
  some witness jointly realizes G;

Robust_E(G):
  one policy produces a G-realizing witness for every environment in E.
```

The original Robust hollow-triangle fixture had:

```text
May({A,B,C}) = false.
```

Its failed Robust triple could therefore be explained by joint
unrealizability alone.

This sprint asks the stricter question:

> Can a triple be jointly realizable, with every pair robustly securable over
> one fixed environment scope, while no policy robustly secures the triple?

The target is joint indefensibility after joint realizability has been held
fixed.

## Claim Boundary

This sprint is:

```text
a finite exact separation inside the existing May/Robust lookup-table model.
```

It is not:

```text
dynamic control under partial observation;
stochastic or adversarial control;
empirical robustness;
candidate correctness;
identity;
agency;
valuerhood;
standing;
value;
moral license;
or Omega validation.
```

`PolicyEnvironmentRuns` is a total deterministic table. `Robust` retains its
existing quantifiers:

```text
exists one policy;
for every environment in a declared nonempty scope.
```

## Fixed Candidates and Witnesses

Candidates:

```text
A, B, C
```

Witnesses:

```text
w_ab:
  realizes A, B

w_ac:
  realizes A, C

w_bc:
  realizes B, C

w_abc:
  realizes A, B, C
```

Required May fibers:

```text
Real({A,B})   = {w_ab, w_abc}
Real({A,C})   = {w_ac, w_abc}
Real({B,C})   = {w_bc, w_abc}
Real({A,B,C}) = {w_abc}
```

Thus the triple is jointly realizable before any policy or environment
quantifier is applied.

## Fixed Environments and Policies

Environment scope:

```text
E_full = {north, south}
```

Policies:

```text
p_ab;
p_ac;
p_bc;
p_try.
```

Outcome table:

```text
              north    south

p_ab          w_ab     w_ab
p_ac          w_ac     w_ac
p_bc          w_bc     w_bc
p_try         w_abc    w_ab
```

No rows may be added after the run.

## Preregistered Verdict

Over `E_full`:

```text
Robust({A,B}):
  true
  securing policies = {p_ab, p_try}

Robust({A,C}):
  true
  securing policies = {p_ac}

Robust({B,C}):
  true
  securing policies = {p_bc}

Robust({A,B,C}):
  false
  securing policies = {}
```

Over the restricted scope:

```text
E_north = {north}

Robust_north({A,B,C}):
  true
  securing policies = {p_try}
```

The strict separation is retained only if all of those exact policy sets
match.

## Positive Control

Use the same candidates, witnesses, incidence relation, and environments.
Add one policy:

```text
p_abc:
  north -> w_abc
  south -> w_abc
```

The positive control must return:

```text
Robust_full({A,B,C}) = true
securing policies = {p_abc}
```

The strict fixture and positive control may differ only in the policy table
required to add `p_abc`.

## Duplicate-Invariance Control

Add:

```text
A_copy
```

with the exact realization signature of `A`.

After quotienting exact candidate duplicates:

```text
candidate-class count is unchanged;
May structural payload is unchanged;
Robust structural payload is unchanged.
```

No duplicated candidate may create a new robust face.

## Structural-Law Controls

The strict fixture must return no:

```text
May downward-closure failures;
May restriction failures;
Robust candidate-antitonicity failures;
Robust restriction failures;
Robust-implies-May failures;
environment-antitonicity failures between E_full and E_north.
```

Every Robust fiber must retain complete environment-indexed run evidence.

Pair and triple queries must use the same full environment scope.

## Batch A: Fixture

Add:

```text
omega_v2/experiments/robust_joint_separation_v0.py
```

Required exported functions:

```text
strict_joint_fixture;
strict_joint_case;
robust_positive_case;
robust_joint_separation_summary.
```

The implementation must reuse:

```text
FiniteRealizationRelation;
PolicyEnvironmentRuns;
FiniteOmega.
```

No new May or Robust semantics may be introduced.

## Batch B: Validation

Add:

```text
omega_v2/validation/robust_joint_separation_v0.py
tests/test_omega_v2_robust_joint_separation.py
docs/research_notes/omega_v2/robust_joint_separation_report_v0.md
```

The retained run must include:

```text
summary.json;
may_fibers.csv;
robust_fibers.csv;
policy_environment_runs.csv;
environment_scope.csv;
structural_controls.csv;
report.md.
```

## Success Conditions

The sprint is retained only if:

```text
1. the May triple is nonempty and equals {w_abc};
2. every pair is Robust over north|south;
3. the full triple is not Robust over north|south;
4. exact pair policy sets match the preregistration;
5. the triple becomes Robust over north alone via p_try;
6. environment narrowing changes no May fiber;
7. the matched p_abc control robustly secures the triple;
8. exact candidate duplication changes no quotient payload;
9. all May/Robust structural laws pass;
10. every retained Robust witness carries a run for each queried environment;
11. existing Python and Lean regressions remain green.
```

## Kill Conditions

Stop and report failure if:

```text
the triple May fiber is empty;
any pair fails Robust over the full scope;
the triple is Robust over the full scope;
the north-only triple is not Robust through p_try;
pair and triple checks use different full scopes;
the positive control does not secure the triple;
candidate duplication changes the structural payload;
any structural law fails;
run evidence is discarded;
or the report upgrades table-level robustness to dynamic or moral robustness.
```

## Public Compression

Joint realizability does not guarantee joint robust securability. In the
retained finite model, all three patterns can coexist and every pair can be
secured by one policy across the full environment scope, yet no policy secures
the triple across that same scope. Restricting the environment scope restores
the triple, showing that the obstruction lies in robust control over declared
variation rather than in coexistence itself.
