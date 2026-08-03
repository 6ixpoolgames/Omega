# Omega v2 Robust Joint Separation Report v0

Status: retained finite May-versus-Robust separation

Date: 2026-08-04

Protocol:
[Robust Joint Separation Protocol v0](robust_joint_separation_protocol_v0.md)

Protocol checkpoint:
`867788e` (`Preregister robust joint separation`)

Retained run:
[20260803_192323](../validation_results/robust_joint_separation_v0/20260803_192323/)

Summary digest:

```text
189a08b58d46f25e8be66a2176b3b96034af4da54445a890aac1360189148fd5
```

## Verdict

The retained verdict is:

```text
joint_realizability_does_not_imply_joint_robust_securability
```

All 11 preregistered cases passed. No kill condition fired.

The result is:

> A candidate triple can have a concrete joint realization, and every pair can
> be secured by one policy across a fixed environment scope, while no policy
> secures the full triple across that same scope.

This is stricter than the predecessor hollow-triangle fixture. The predecessor
triple was not jointly realizable. Here the joint witness is retained.

## Reused Semantics

The sprint adds no realization abstraction.

It reuses:

```text
FiniteRealizationRelation;
PolicyEnvironmentRuns;
FiniteOmega.
```

The quantifiers remain:

```text
May(G):
  exists a witness jointly realizing G;

Robust_E(G):
  exists one policy such that
  for every environment in E,
  the resulting witness jointly realizes G.
```

The run model is a total deterministic policy/environment lookup table.

## Joint Realization

Candidates:

```text
A, B, C
```

Witness incidence:

| Witness | Realizes |
| --- | --- |
| `w_ab` | A, B |
| `w_ac` | A, C |
| `w_bc` | B, C |
| `w_abc` | A, B, C |

The exact May fibers are:

```text
Real({A,B}):
  {w_ab, w_abc}

Real({A,C}):
  {w_ac, w_abc}

Real({B,C}):
  {w_bc, w_abc}

Real({A,B,C}):
  {w_abc}
```

Therefore:

```text
May({A,B,C}) = true
```

before policy or environment quantification.

## Strict Policy Table

Full environment scope:

```text
{north, south}
```

The fixed table is:

| Policy | north | south |
| --- | --- | --- |
| `p_ab` | `w_ab` | `w_ab` |
| `p_ac` | `w_ac` | `w_ac` |
| `p_bc` | `w_bc` | `w_bc` |
| `p_try` | `w_abc` | `w_ab` |

No policy row is selected after seeing the environment.

## Pairwise Robust Results

Over the same full scope:

```text
Robust({A,B}):
  true
  policies = {p_ab, p_try}

Robust({A,C}):
  true
  policies = {p_ac}

Robust({B,C}):
  true
  policies = {p_bc}
```

All pair fibers retain both environment-indexed run witnesses for every
securing policy.

## Failed Robust Triple

The full triple has:

```text
May witnesses:
  {w_abc}

Robust securing policies over north|south:
  {}
```

`p_try` reaches `w_abc` under `north`, but reaches only `w_ab` under `south`.
The three pair policies never reach a triple witness.

Thus:

```text
Robust_{north,south}({A,B,C}) = false.
```

The Robust maximal faces are the three pairs. There is no selected greatest
face.

## Environment-Scope Isolation

Restricting the environment scope to:

```text
{north}
```

returns:

```text
Robust_north({A,B,C}) = true
securing policies = {p_try}
```

The May object is unchanged under this restriction.

Therefore the failed full-scope triple is caused by the Robust environment
quantifier, not by candidate incoherence or an empty realization fiber.

Environment antitonicity has no failures:

```text
securing policies over a larger environment scope
are a subset of
securing policies over a smaller scope.
```

## Matched Positive Control

The positive control keeps:

```text
the same candidates;
the same realization relation;
the same witnesses;
the same two environments.
```

It adds:

```text
p_abc:
  north -> w_abc
  south -> w_abc
```

The full-scope result becomes:

```text
Robust({A,B,C}) = true
securing policies = {p_abc}
```

The May structural payload remains identical to the strict fixture.

This confirms that the harness can detect a genuinely securable triple.

## Duplicate Invariance

Adding `A_copy` with exactly A's realization signature changes:

```text
raw candidate count:
  3 -> 4
```

but leaves:

```text
quotient candidate-class count:
  3

May structural payload:
  unchanged

Robust structural payload:
  unchanged
```

Duplicated presentation therefore creates no new Robust face.

## Structural Controls

The strict fixture returns no:

```text
May downward-closure failures;
May restriction failures;
Robust candidate-antitonicity failures;
Robust restriction failures;
Robust-implies-May failures;
environment-antitonicity failures.
```

Every nonempty Robust fiber retains its complete environment-indexed run
evidence. Pair and triple checks use the same full environment scope.

## What This Establishes

The finite separation shows:

```text
joint May realization
+ pairwise Robust securability
does not imply
joint Robust securability.
```

Consequently, pairwise Robust certification is not a complete test for a
larger family. The full family must be queried directly.

This is a structural result inside the declared finite semantics. It does not
say that a pairwise check is always useless, or that every larger family
fails.

## Validation

Canonical commands:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_omega_v2_robust_joint_separation.py -q

.\.venv\Scripts\python.exe -m omega_v2.validation.robust_joint_separation_v0 --out-root docs\research_notes\validation_results\robust_joint_separation_v0

powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaV2
```

The retained run includes:

```text
summary.json
may_fibers.csv
robust_fibers.csv
policy_environment_runs.csv
environment_scope.csv
structural_controls.csv
report.md
```

## Kill Conditions

All preregistered kill conditions are false:

```text
May triple empty:
  false

pair not Robust:
  false

pair policy set changed:
  false

full triple Robust:
  false

north triple not Robust:
  false

scope failed to isolate:
  false

positive control failed:
  false

duplicate changed payload:
  false

structural law failed:
  false

run evidence discarded:
  false

pair/triple scope mismatch:
  false
```

## Claim Boundary

This sprint establishes a finite deterministic lookup-table separation.

It does not establish:

```text
dynamic control under partial observation;
stochastic or adversarial control;
empirical robustness;
the correctness of candidate patterns;
identity;
agency;
valuerhood;
standing;
value;
moral license;
or Omega validation.
```

The word `securability` refers only to the retained
exists-policy/forall-environment relation.

## Next Debt

The next technical upgrade should replace table policies with the already
available finite-state controllers and generated runs:

```text
same May triple;
same pairwise/full separation target;
policy witnesses generated by dynamics rather than inserted as table rows.
```

After that control succeeds, the environment layer can move from deterministic
cases toward finite nondeterministic or ambiguity-set semantics.

Neither upgrade is claimed here.

## Public Compression

Three patterns may genuinely coexist, and every pair may be robustly secured,
without there being one policy that secures all three across the same
environment variation. Pairwise robustness therefore does not certify joint
robustness. The obstruction can arise from the environment quantifier rather
than from an inability to coexist.
