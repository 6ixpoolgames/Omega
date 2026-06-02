# RFS-MB0 Future Landscape Smoke Result

Date: 2026-05-23

Status: future-landscape substrate implemented; smoke passed; scientific gate not passed

Result directory:

```text
results/rfs_mb0_future_landscape/20260523_future_landscape_smoke/
```

Primary summary:

```text
results/rfs_mb0_future_landscape/20260523_future_landscape_smoke/summary.md
```

## Purpose

This run implements the future-landscape reset specified in:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_FUTURE_LANDSCAPE_PATTERN_SPEC.md
```

The pivot is from named actors, evaluators, or outcome semantics toward the neutral deformation of reachable futures. The implemented object is a future-profile map:

```text
Phi_H(x)
```

derived from finite distinction states, neutral relations, exact frontiers, horizon reachability, and probe-signature distributions.

## Implementation

Added:

```text
omega/rfs_mb0_future_landscape/substrate.py
omega/rfs_mb0_future_landscape/probes.py
omega/rfs_mb0_future_landscape/landscape.py
omega/rfs_mb0_future_landscape/detectors.py
omega/rfs_mb0_future_landscape/controls.py
omega/rfs_mb0_future_landscape/run_smoke.py
```

The runner emits:

```text
results.csv
future_profiles.csv
signature_distributions.csv
control_comparison.csv
profile_classes.csv
divergence_summary.csv
deformation_summary.csv
summary.md
status.json
```

The implementation includes graceful checkpoint outputs, a wall-clock cap, task-level error capture, and neutral profile classes:

```text
noise_like
collapse_like
cycle_like
permissive_blur
strict_fragmentation
structured_propagation
underdetermined
```

## Run Shape

```text
systems: 33
future profiles: 672
families: 11
seeds per family: 3
workers: 18
errors: 0
status: COMPLETED
elapsed: about 2.9 seconds
```

This was intentionally a tiny-to-small smoke. It validates the machinery, not the theory.

## Main Read

The implementation gate passed.

Expected simple controls separated:

```text
fixed_point_control:
  collapse_like

cyclic_relation / phase_cycle_control:
  cycle_like

permissive_probe_control:
  permissive_blur

strict_probe_control:
  strict_fragmentation
```

The future-profile machinery is producing interpretable horizon summaries:

```text
reach_count_by_h
exact_count_by_h
growth_rate_by_h
signature_entropy_by_h
signature_support_size_by_h
recurrence_rate_by_h
transition_motif_count_by_h
predictive_information_by_h
compression_proxy_by_h
JS_to_null
smoothed_KL_to_null
```

## Control Risk

The scientific gate is not passed.

The current `structured_propagation` detector also classifies the main null-style controls as structured:

```text
structured_relation:
  structured_propagation

expanding_relation:
  structured_propagation

random_relation_control:
  structured_propagation

degree_preserving_control:
  structured_propagation

coordinate_permutation_control:
  structured_propagation
```

This means the present class boundary is too broad. It is detecting high-reach, high-recurrence, high-compression future landscapes, but not yet distinguishing deliberately structured relation families from matched controls.

The issue is substrate/detector specificity, not compute.

## Gate Status

```text
Neutral future-landscape package implemented:
  passed

Required output files emitted:
  passed

Graceful status and checkpoint behavior:
  passed

No task errors:
  passed

Collapse/cycle/permissive/strict control separation:
  passed

Structured relation separation from random/degree controls:
  not passed
```

## Recommendation

Do not scale this exact detector yet.

Next revision should stay neutral but strengthen the matched-control problem:

1. Add relation-local descriptors that preserve or compare coordinate footprint, transform arity, and horizon-local motif structure.
2. Compare structured families against controls that preserve degree, exact-frontier size, coordinate locality, and probe marginal distributions.
3. Make `structured_propagation` require separation from matched nulls, not only high entropy, recurrence, and compression.
4. Preserve this package as the active future-landscape branch because the instrumentation is now clean enough to iterate on.

The useful outcome is negative in the right way: the smoke says the reset object is runnable, but the present detector would overcall structure.
