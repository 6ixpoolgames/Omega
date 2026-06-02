# Future Field Atlas Coupled H64 Mechanism-Resolution Result

Status: completed cleanly

Runner: `omega.future_field_atlas.run_coupled_future_field_atlas`

Summary tool: `omega.future_field_atlas.coupled_mechanism_summary`

## Summary

This pass resolved the main open question from the H64 coupled ladder: whether
the zero-to-positive split was a smooth scalar-strength effect, a near-zero
threshold, a product-baseline artifact, or a pair-specific skew.

Allowed claim:

```text
The H64 mechanism-resolution pass shows that the current scalar mismatch
penalty is meaningful near zero but quickly saturates in this design. The true
product selector is distinct from zero-penalty joint rank-prefix selection.
Pair005 remains a real heavy-pair / critical-pair clue, including in a targeted
H128 depth check.
```

Blocked claims:

```text
Omega validation
agency
identity
valuerhood
value
support / capture / erasure
compatibility detection
interaction detection
```

## Design

Common H64 design:

```text
horizon_max: 64
horizon_schedule: dense
pair_count: 8
groups: 8
workers: 4
raw_topology_output_mode: worker_spool
csv_output_mode: gzip
gzip_compresslevel: 1
selection_operator_a: rank_prefix:m=3
selection_operator_b: rank_subset:m=4:retain=1|2|3:remove=4
macro_invariant_kind: symbol_histogram_distance
macro_invariant_beta: 0.10
rank_boundary_k: 3
joint_effective_out_degree: 4
joint_selection_family: joint_energy_rank_prefix
```

Near-zero ladder:

```text
0.000
0.001
0.002
0.005
0.010
0.020
0.050
```

Additional controls:

```text
product selector:
  joint_selection_family: product
  coupling_strength: 0.000

pair005 H64 forensics:
  pair-indexes: 5
  same near-zero ladder

pair005 H128 depth check:
  coupling_strength: 0.000, 0.020, 0.050
```

## Retained Local Outputs

Compact summary bundle:

```text
results/future_field_atlas/20260602_coupled_mechanism_h64_summary/
  run_gate_summary.csv
  coupling_ladder_summary.csv
  near_zero_threshold_summary.csv
  pair_level_residual_summary.csv
  pair005_forensic_summary.csv
  product_selector_sanity_summary.csv
  horizon_of_divergence_summary.csv
  joint_candidate_crossing_summary.csv
  mechanism_summary_manifest.json
```

Raw worker spools were pruned after compact retention summaries confirmed that
deletion was allowed. The retained root artifacts and `_retention_summary/`
bundles remain local.

## Gate Results

All interpretable H64 and targeted H128 runs satisfied the gate:

```text
status: COMPLETED
coupled_pairs_failed: 0
internal_cap_events: 0
artifact_completeness_statuses: complete
reconstruction audits: PASS
medium_sweep_interpretation_allowed: 1
raw spools pruned after compact retention: yes
```

## Near-Zero Ladder

Run-level summary:

| label | mean residual | mean joint retention | mean A retention | mean B retention | edge rows | node rows |
|---:|---:|---:|---:|---:|---:|---:|
| 0.000 | 0.191149 | 0.808851 | 0.980608 | 0.972859 | 22866722 | 3419750 |
| 0.001 | 0.203497 | 0.796503 | 0.971088 | 0.953918 | 22835142 | 3411805 |
| 0.002 | 0.210525 | 0.789475 | 0.961445 | 0.927643 | 22966410 | 3445351 |
| 0.005 | 0.215783 | 0.784217 | 0.984413 | 0.968058 | 21957746 | 3187986 |
| 0.010 | 0.183676 | 0.816324 | 0.999725 | 0.999588 | 22126114 | 3230615 |
| 0.020 | 0.183363 | 0.816637 | 1.000000 | 1.000000 | 22127782 | 3231039 |
| 0.050 | 0.183363 | 0.816637 | 1.000000 | 1.000000 | 22127782 | 3231039 |

Topology-digest read:

```text
0.001 differs from 0.000.
0.001, 0.002, 0.005, and 0.010 are each distinct from the first positive.
0.020 and 0.050 are topology-identical in the compact digest.
```

Interpretation:

```text
The earlier "any positive strength collapses to one topology" read was too
coarse. At near-zero resolution, the operator changes immediately at 0.001 and
continues to change through 0.010, but appears saturated by 0.020 in this
design.
```

## Product-Selector Sanity Check

The true product selector completed cleanly:

```text
mean residual: 0.0
max residual: 0.0
mean joint retention: 1.0
mean A/B marginal retention: 1.0 / 1.0
edge rows: 33926940
node rows: 3834246
```

The product selector does not match zero-penalty joint rank-prefix selection.

Conclusion:

```text
coupling_strength = 0.000 is not neutral product behavior. It is already a
joint rank-prefix selector over additive energy. Future coupled reports should
separate product-selector behavior from zero-penalty joint-selector behavior.
```

## Pair005 Forensics

Pair005 remains anomalous and is not explained away by the near-zero ladder.

H64 pair005:

| label | mean residual | final residual | mean joint retention | final joint retention | mean A retention | mean B retention |
|---:|---:|---:|---:|---:|---:|---:|
| 0.000 | 0.322116 | 0.244091 | 0.677884 | 0.755909 | 0.948288 | 0.976898 |
| 0.001 | 0.328054 | 0.246273 | 0.671946 | 0.753727 | 0.938573 | 0.973628 |
| 0.002 | 0.266498 | 0.172364 | 0.733502 | 0.827636 | 0.942971 | 0.871588 |
| 0.005 | 0.756350 | 0.755909 | 0.243650 | 0.244091 | 0.971808 | 0.978950 |
| 0.010 | 0.749576 | 0.752545 | 0.250424 | 0.247455 | 1.000000 | 1.000000 |
| 0.020 | 0.749628 | 0.752364 | 0.250372 | 0.247636 | 1.000000 | 1.000000 |
| 0.050 | 0.749628 | 0.752364 | 0.250372 | 0.247636 | 1.000000 | 1.000000 |

Targeted H128 check:

| label | mean residual | final residual | mean joint retention | final joint retention | mean A retention | mean B retention |
|---:|---:|---:|---:|---:|---:|---:|
| 0.000 | 0.284759 | 0.244091 | 0.715241 | 0.755909 | 0.973943 | 0.988359 |
| 0.020 | 0.752270 | 0.752364 | 0.247730 | 0.247636 | 1.000000 | 1.000000 |
| 0.050 | 0.752270 | 0.752364 | 0.247730 | 0.247636 | 1.000000 | 1.000000 |

Interpretation:

```text
Pair005 behaves like a real critical-pair / heavy-pair clue under this operator.
The high residual persists at H128 and saturates at the same 0.020/0.050
geometry. This is joint-combination restriction/reorganization, not primary
marginal erasure in the retained readout.
```

## Horizon Of Divergence

Positive strengths diverge from zero early:

```text
pair002, pair006, pair007: horizon 2
pair001, pair003, pair004, pair005: horizon 3
pair000: horizon 4 at 0.001, horizon 2 at 0.002 and above
```

The product selector diverges from zero-penalty joint rank-prefix selection at
horizon 1 for every pair.

Pair005 has its largest residual delta against zero near horizon 16:

```text
0.005 vs 0.000: max residual delta 0.511818 at horizon 16
0.020/0.050 vs 0.000: max residual delta 0.508273 at horizon 16
```

## Candidate Crossing Audit

Selected-edge crossing was computed for pair005 before raw spools were pruned.

```text
0.000 vs 0.005:
  selected_at_zero_not_positive_count: 1679414
  selected_at_positive_not_zero_count: 460246
  selected_intersection_count: 141746
  selected_union_count: 2281406

0.000 vs 0.020:
  selected_at_zero_not_positive_count: 1707269
  selected_at_positive_not_zero_count: 503897
  selected_intersection_count: 113891
  selected_union_count: 2325057
```

The selected-set overlap is low, consistent with large joint candidate
reorganization. This is not yet a full rank-order crossing audit because the
runner currently emits selected topology, not all unselected local candidate
ranks and near ties.

## Mechanism Interpretation

Current read:

```text
The scalar mismatch penalty is not simply exhausted at "any positive" strength.
It has a near-zero response region, but the current topology saturates by 0.020
in the tested H64 pair8 design.

The zero-penalty joint rank-prefix selector is already a coupled constraint.
The true product selector is the proper product-equivalence sanity reference.

Pair005 is a real mechanism clue: a heavy pair where positive mismatch penalty
preserves component marginals while sharply restricting joint combinations.
```

Next recommendation:

```text
Do not broaden to H128 yet.
Run a narrow bracket around pair005's apparent transition between 0.002 and
0.005 if scalar-threshold detail remains important.
In parallel, begin designing a rank-order-native or shared-capacity coupled
operator, with shared-capacity currently the most principled next candidate.
```

## Claim Boundary

This result is a coupled-instrument mechanism-resolution result only. It does
not validate Omega or establish coupled-field interaction. It shows that the
current coupled selector can be interrogated cleanly, that product behavior and
zero-penalty joint selection are distinct, and that pair-aware analysis is
mandatory before further coupled scale expansion.
