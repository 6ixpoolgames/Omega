# Validation Design Notes

This folder contains current validation designs for the Omega project.

Omega should be introduced to new readers as a structural theory of
value-bearing futures. VAL0-CT is the current minimal executable precursor to
that larger theory: it asks whether future-bearing reachability can be detected
in constructor-style task space before making any claim about full Omega.

The current public-facing validation target is **VAL0-CT**:

```text
single-field proto-Omega validation in constructor-style task algebras
```

VAL0-CT does not attempt to validate full Omega, valuerhood, ethics, or
multifield compatibility. It tests a narrower precursor:

```text
future-bearing reachability under constraint
```

## Current Entry Points

1. [`val0_ct_implementation_spec.md`](val0_ct_implementation_spec.md)

   Buildable implementation plan. Start here when writing code.

2. [`val0_constructor_task_algebra_probe.md`](val0_constructor_task_algebra_probe.md)

   Theory-side validation design and interpretation rules.

## Current Primary Question

```text
Does persistence-conditioned reachability, R1, predict long-horizon
reachability retention better than raw reachability, R0, and matched
R0-lookahead controls in structured task algebras?
```

## Implementation Stance

- CPU-first.
- Deterministic toy tests before large runs.
- Equal planning budget for `R1` and `R0_lookahead`.
- First smoke only: `low_resolution_dense`, `structured_asymmetric`, and
  `lock_in_seeded`.
- Defer embodied agents, multifield coupling, noise branching, mixed generators,
  and GPU acceleration until the first smoke is clean.

## Results Location

Write future VAL0-CT outputs under:

```text
results/val0_ct/<timestamp-or-run-id>/
```

Use `results/local_runs/` for ignored smoke, calibration, stress, and scratch
outputs. Do not create new root-level `*_results` folders.
