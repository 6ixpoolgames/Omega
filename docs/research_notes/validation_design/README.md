# Validation Design Notes

This folder contains validation and substrate-design notes for the Omega
project.

Current posture:

```text
The empirical arm has reset around reachable-futures substrate design.
VAL0/VAL1 notes are retained as reconnaissance and calibration material, not as
the final validation center.
```

Omega should be introduced to new readers as the broader structural theory of
value-bearing futures. The current empirical object is narrower:

```text
reachable futures under viability and compatibility constraints
```

The current public-facing target is **RFS0**:

```text
a minimal finite reachable-futures substrate with exact reachability,
viability-kernel, and capture/recovery-basin measurements
```

## Current Entry Points

1. [`../../REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md`](../../REACHABLE_FUTURES_SUBSTRATE_PROGRAM.md)

   Current empirical reset and substrate ladder.

2. [`val_ecology_viability_reorientation.md`](val_ecology_viability_reorientation.md)

   Theory-side reorientation after VAL0/VAL1 reconnaissance.

3. [`../../VAL0_G_NEUTRAL_GRAMMAR_GEOMETRY_ATLAS_SPEC.md`](../../VAL0_G_NEUTRAL_GRAMMAR_GEOMETRY_ATLAS_SPEC.md)

   Historical neutral-grammar reconnaissance design.

4. [`../validation_results/val0_ct_12h_unlabeled_geometry_battery_result.md`](../validation_results/val0_ct_12h_unlabeled_geometry_battery_result.md)

   Result note explaining why the project moved from direct R1 validation to
   neutral geometry discovery.

5. [`val0_ct_implementation_spec.md`](val0_ct_implementation_spec.md)

   Prior VAL0-CT implementation plan. Still useful for task-algebra machinery.

6. [`val0_constructor_task_algebra_probe.md`](val0_constructor_task_algebra_probe.md)

   Theory-side validation design and interpretation rules.

## Current Primary Question

```text
What minimal substrate resolution is required to distinguish generic viable
continuation from trivial persistence, recoverability, local capture, and
compatibility-preserving viable propagation?
```

## Implementation Stance

- CPU-first for RFS0 unless exact algorithms become too slow.
- Established vocabulary first: reachable sets, viability kernels, capture
  basins, recovery basins, transition systems, constructor candidates.
- No Omega-positive labels in the substrate.
- Treat VAL0/VAL1 as reconnaissance evidence, not current validation center.
- Defer broad multifield scaling, GPU acceleration, and full constructor agency
  until RFS0 definitions and controls are clean.

## Results Location

Write future VAL0-CT outputs under:

```text
results/val0_ct/<timestamp-or-run-id>/
```

Write future VAL0-G outputs under:

```text
results/val0_g/<timestamp-or-run-id>/
```

Write future RFS outputs under:

```text
results/rfs/<timestamp-or-run-id>/
```

Use `results/local_runs/` for ignored smoke, calibration, stress, and scratch
outputs. Do not create new root-level `*_results` folders.
