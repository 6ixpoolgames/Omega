# RFS-MB0 Neutral Transform Reset Smoke Result

Date: 2026-05-23

Status: neutral substrate reset implemented; instrumentation passed; scientific gate not fully passed

Result directory:

```text
results/rfs_mb0_neutral_transform/20260523_neutral_transform_reset_smoke/
```

Primary summary:

```text
results/rfs_mb0_neutral_transform/20260523_neutral_transform_reset_smoke/summary.md
```

## Purpose

This run implements the substrate reset specified in:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_NEUTRAL_TRANSFORM_RESET_SPEC.md
```

The purpose was to stop evolving the semantic MB0 toy substrate and restart from neutral finite transformations:

```text
S = (X, T)
```

where states are finite coordinate tuples and transformations are formally named coordinate operations.

The older `omega/rfs_mb0_pairwise/` branch remains useful as workflow validation only. The reset implementation lives in:

```text
omega/rfs_mb0_neutral_transform/
```

## Implementation

Added:

```text
omega/rfs_mb0_neutral_transform/substrate.py
omega/rfs_mb0_neutral_transform/extractors.py
omega/rfs_mb0_neutral_transform/exact.py
omega/rfs_mb0_neutral_transform/run_smoke.py
```

The reset uses neutral finite states:

```text
x = (q0, q1, q2, q3, q4, phase)
```

with small modular coordinate alphabets.

The candidate identities are derived by declared extractor machinery:

```text
mu:
  block relation over q0, q1 and a neutral q4 band

nu:
  block relation over q2, q3 and a neutral q4 band
```

The runner computes singleton and joint identity-preserving filtrations:

```text
F_H^mu
F_H^nu
F_H^{mu,nu}
Exact_H^mu
Exact_H^nu
Exact_H^{mu,nu}
```

for:

```text
H = 0, 1, 2, 4, 8, 12, 16
```

It also reports neutral endpoint-change diagnostics:

```text
changed coordinate counts
phase-only endpoint fraction
nonphase endpoint fraction
block-relation changed fraction
signature changed / exits-band fractions
```

## Run Shape

```text
systems: 50
rows: 350
families: 10
seeds per family: 5
workers: 18
errors: 0
status: COMPLETED
elapsed: about 0.4 seconds
```

The run is small because the reset substrate is exact and finite with 729 states per system.

## Main Read

The reset succeeded as an implementation and neutrality repair.

The package and generated summaries avoid the previous semantic toy vocabulary in primitive state names, transform names, generator names, readout bins, and endpoint classes.

The result separates some expected neutral profiles:

```text
coupled_block_transforms:
  mu = 9
  nu = 9
  joint = 9
  joint/min = 1.000
  exact joint/min = 1.000

shared_constraint_conflict:
  mu = 10
  nu = 10
  joint = 1
  joint/min = 0.100
  exact joint = 0

anti_correlated_block_transforms:
  mu = 12
  nu = 12
  joint = 3
  joint/min = 0.250
  exact joint/min = 0.250
```

The control families also behave as useful fakeouts:

```text
phase_cycle_control:
  phase_only_persistence

fixed_point_control:
  fixed_point_persistence

equivalence_permissive_control:
  permissive_equivalence_artifact

equivalence_strict_control:
  strict_equivalence_artifact
```

## Control Risk

The scientific gate is not fully passed.

Randomized controls still mimic contraction:

```text
random_transform_control:
  joint/min = 0.309
  exact joint = 0

degree_preserving_transform_control:
  joint/min = 0.444
  exact joint = 0
```

This means pairwise contraction alone is not yet sufficient. A stronger reset pass must show a structured neutral transform family whose contraction profile separates from random and degree-preserving controls by more than raw sparsity or edge rewiring effects.

## Gate Status

```text
Neutral substrate implemented:
  passed

Semantic toy labels removed from the new implementation:
  passed

Singleton and pairwise filtrations computed:
  passed

Phase/fixed/permissive/strict controls identified:
  passed

Structured singleton persistence with joint contraction:
  partially passed

Separation from random/degree controls:
  not passed
```

## Recommendation

Do not scale yet.

Next revision should remain neutral and should focus on separating structured transform-family contraction from random/degree control contraction.

Good next targets:

1. Add matched controls that preserve more than edge count, such as transform arity, coordinate locality, and block footprint.
2. Report transform-locality descriptors alongside graph-level descriptors.
3. Strengthen the structured families so their contraction has a distinct horizon-filtration profile, not just low joint counts.
4. Keep the reset package as the active MB0 branch and treat `rfs_mb0_pairwise` as archived workflow smoke.

The reset corrected the main implementation drift. The next problem is control separation, not compute scale.

