# Answerable Scope v0

Status: retained Lean bridge / Omega close checkpoint
Scope: reachability-indexed answerable scope as controllable-and-foreclosable facts
Claim boundary: not blame, not liability, not moral responsibility, not agency,
not value, not standing, not patienthood, not identity, not Omega validation

## Purpose

This note records the minimal reachability-indexed bridge formerly discussed as
"responsibility." The Lean surface deliberately uses the lower-claim name:

```text
AnswerableScope
```

## Formal File

```text
formal/lean/OmegaProper/Decision/AnswerableScope.lean
```

## Core Definition

```text
InScope agent fact :=
  Controllable agent fact
  and
  Foreclosable agent fact
```

The predicates are supplied by a `ScopeFrame`. The file does not infer agency,
blame, value, or authority.

## Retained Lemmas

```text
not_inScope_of_not_controllable
not_inScope_of_not_foreclosable
past_facts_not_answerable
scope_monotone_in_reach
```

## Reading

The past/future asymmetry is reach-structural: if a fact is outside the
controllable reach image, it is outside answerable scope. Enlarging the
controllable and foreclosable reach predicates cannot remove a fact that was
already in scope.

## Validation

```text
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaProper.Decision
```

## Public Compression

Answerable scope is the intersection of what can be controlled and what can be
foreclosed from the current position. This is a reach predicate, not a moral
verdict.
