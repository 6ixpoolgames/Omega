# Future Field Atlas Rank-Order Boundary Class Expansion Result

Status: completed cleanly

Date: 2026-06-02

## Summary

This pass expanded the H64 rank-order-boundary search from pair indexes `24-47`
after the neighbor / observable sweep found `pair012` and `pair014`.

The run found one additional high-yield marginal-preserving exemplar:

```text
pair026:
  H64 joint support residual: 0.5103896103896104
  H64 joint retention:        0.4896103896103896
  A marginal retention:       1.0
  B marginal retention:       1.0
```

Targeted H128 depth for `pair026` reproduced the same final geometry:

```text
pair026:
  H128 joint support residual: 0.5103896103896104
  H128 joint retention:        0.4896103896103896
  A marginal retention:        1.0
  B marginal retention:        1.0
```

This updates the current rank-order-boundary high-yield representative set to:

```text
pair005
pair012
pair014
pair026
```

## Gates

H64 class expansion:

```text
run dir: results/future_field_atlas/20260602_rank_order_boundary_h64_class_expansion_p24_47
horizon max: 64
pair indexes: 24-47
pairs completed: 24 / 24
pairs failed: 0
internal cap events: 0
artifact completeness: complete
reconstruction audits: PASS 3
medium-sweep interpretation allowed: 1
elapsed seconds: 1716.585
joint edge rows: 85698582
joint node rows: 13112603
raw delete candidate: 4.670432 GiB
raw spools deleted: yes
```

H128 pair026 depth:

```text
run dir: results/future_field_atlas/20260602_rank_order_boundary_h128_pair026_depth
horizon max: 128
pair index: 26
pairs completed: 1 / 1
pairs failed: 0
internal cap events: 0
artifact completeness: complete
reconstruction audits: PASS 3
medium-sweep interpretation allowed: 1
elapsed seconds: 145.529
joint edge rows: 3099785
joint node rows: 424816
raw delete candidate: 0.167905 GiB
raw spools deleted: yes
```

## H64 Class Expansion Readout

Top final H64 residuals from pairs `24-47`:

```text
pair026  residual 0.5103896103896104  joint_retention 0.4896103896103896  A 1.0  B 1.0
pair045  residual 0.12836438923395446 joint_retention 0.8716356107660456  A 1.0  B 1.0
pair036  residual 0.11                joint_retention 0.89                A 1.0  B 1.0
pair039  residual 0.1052910052910053  joint_retention 0.8947089947089947  A 1.0  B 1.0
pair035  residual 0.09414141414141414 joint_retention 0.9058585858585858  A 1.0  B 1.0
```

Only `pair026` crossed the current high-yield threshold while preserving both
component marginals.

## Refreshed Morphology Atlas

The substrate morphology atlas was regenerated after these runs:

```text
source coupled runs: 37
manifest digest: fe1acb0093468d1e3fb48fe6
pair morphology rows: 210
high-residual rows: 27
high-residual marginal-preserving rows: 27
observable coverage:
  hamming_weight_or_nonzero_count
  symbol_histogram_distance
  total_coordinate_mass
```

Updated morphology next target:

```text
rank_order_boundary_class_expansion:
  recommended pairs: pair005;pair012;pair014;pair026
  required controls:
    product_selector
    zero_penalty_joint_selector
    scalar_mismatch_0.020
    shared_capacity_v1_reference
```

## Interpretation

The useful result is narrow but positive:

```text
rank_order_boundary is no longer a pair005-only artifact.
The current symbol_histogram_distance high-yield class has at least four
representatives, three of which are confirmed under targeted H128.
```

The result does not yet establish substrate generality. The tested alternate
observables still did not reproduce the high-yield signature, and the next pass
should separate rank-order-boundary behavior from product selector,
zero-penalty joint rank-prefix selection, scalar mismatch at `0.020`, and
shared-capacity v1 references on the high-yield representative set.

## Claim Boundary

Allowed claim:

```text
The rank-order-boundary coupled selector has a growing
symbol_histogram_distance class of marginal-preserving joint-restriction
examples in the current finite Future Field Atlas substrate.
```

Blocked claims:

```text
Omega validation
agency / identity / valuerhood / value
compatibility detection
support / capture / erasure
interaction detection
holdout readiness
substrate-general theory claim
```

## Next Recommendation

Run a compact high-representative control panel before broad H128:

```text
pairs:
  pair005
  pair012
  pair014
  pair026
  low/medium controls

controls:
  product selector
  zero-penalty joint rank-prefix
  scalar mismatch 0.020
  shared_capacity v1 reference

horizon:
  H64 first
  targeted H128 only for any new or contradictory high-yield behavior
```
