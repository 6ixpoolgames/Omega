# RFS-MB0 Substrate-Untethering Transition-Energy Larger Smoke Result

Date: 2026-05-31

Spec: `docs/specs/archive/rfs_mb0/RFS_MB0_SUBSTRATE_UNTETHERING_TRANSITION_ENERGY_SWEEP_SPEC.md`

Local output:

`results/local_runs/20260531_substrate_untethering_larger_smoke_powered_v2/`

## Executive Summary

Decision: `horizon_transport_generalizes_beyond_constraint_vocabulary`.

Next action: `continue_transition_energy_substrates`.

The larger smoke completed cleanly after repairing two reporting/decision issues:

- the substrate-untethering decision guard was changed from a detector-null-row proxy to a response-row power check;
- substrate-aware grouping was added to response/diversity/viscosity/context summaries so all transition-energy families are visible in by-substrate audit tables.

This is the first powered substrate-untethering smoke to show the horizon-transport object surviving beyond the original hand-built constraint vocabulary inside this instrument. It is still not a validation claim, holdout result, candidate promotion, Omega detection, agency detection, value detection, or identity detection.

## Run Shape

```text
status: completed
finalization_reason: all_jobs_completed
workers: 18
jobs_completed: 896 / 896
elapsed_seconds: 142.856
errors: 0
null_replicates: 13
matrix_count: 1160
perturbation_response_rows: 1002
matched_marginal_detector_null_gate_passed: 1
detector_null_replicate_powered: 1
synthetic_fixture_contract: passed, 8 / 8
response_diversity_score_mean: 0.364583
```

Substrate families:

```text
constraint_template_current
locality_only
smooth_random_potential
budget_conservation
```

Grammar-neutral probes:

```text
relation_role
full_state_hash
```

Perturbation families:

```text
small_edge_resample_control: 0.006, 0.010, 0.015
asymmetric_edge_flip_control: 0.006, 0.010, 0.015
```

## Substrate Generation Diagnostics

| substrate_family | metric rows | mean source frontier states | mean target frontier states |
|---|---:|---:|---:|
| budget_conservation | 14784 | 115.640 | 131.290 |
| constraint_template_current | 14784 | 59.839 | 67.695 |
| locality_only | 14784 | 165.667 | 187.495 |
| smooth_random_potential | 14784 | 97.462 | 110.118 |

All four families generated nontrivial transport capacity. Locality-only produced the largest frontier state counts but no aligned-amplification rows in this smoke.

## By-Substrate Transport Read

| substrate_family | contexts | matched/interpretable contexts | context read mode |
|---|---:|---:|---|
| budget_conservation | 44 | 4 | transport_matrix_undercovered |
| constraint_template_current | 44 | 5 | matched_marginal_mixed |
| locality_only | 44 | 2 | matched_marginal_mixed |
| smooth_random_potential | 44 | 4 | matched_marginal_mixed |

## Response By Substrate

| substrate_family | response rows | aligned amplification rows | aligned fraction | dominant response |
|---|---:|---:|---:|---|
| budget_conservation | 210 | 42 | 0.200 | transport_stable |
| constraint_template_current | 264 | 17 | 0.064 | transport_rerouted |
| locality_only | 264 | 0 | 0.000 | transport_reopens |
| smooth_random_potential | 264 | 19 | 0.072 | transport_rerouted |

The important observation is not that all families behave the same. They do not. The object appears to persist as a detectable horizon-transport response surface while the response profile changes by substrate family.

## Matched Null Pass By Substrate

| substrate_family | matched null rows | mean pass fraction | mean min observed percentile |
|---|---:|---:|---:|
| budget_conservation | 78 | 0.833 | 0.833 |
| constraint_template_current | 132 | 0.841 | 0.934 |
| locality_only | 132 | 0.833 | 0.834 |
| smooth_random_potential | 132 | 0.803 | 0.817 |

The matched-marginal detector gate passed globally. The row-column matched null remains the hardest family, which is consistent with prior horizon-transport runs.

## Transport Viscosity By Substrate

| substrate_family | viscosity rows | mean viscosity score | viscosity read mode |
|---|---:|---:|---|
| budget_conservation | 210 | 0.832 | high_viscosity_aligned_amplifier |
| constraint_template_current | 264 | 0.551 | medium_viscosity_response_threshold |
| locality_only | 264 | 0.571 | medium_viscosity_response_threshold |
| smooth_random_potential | 264 | 0.692 | underpowered_or_unresolved |

## Response Diversity By Substrate

| substrate_family | diversity rows | mean diversity score |
|---|---:|---:|
| budget_conservation | 24 | 0.281 |
| constraint_template_current | 24 | 0.438 |
| locality_only | 24 | 0.333 |
| smooth_random_potential | 24 | 0.406 |

## Local Artifact Policy

The raw run artifacts remain local-only and are not committed. The largest local files from this run are:

| artifact | size |
|---|---:|
| `horizon_transport_matrix_entries.csv` | 27.579 MB |
| `horizon_transport_column_item_manifest.csv` | 21.685 MB |
| `horizon_transport_row_item_manifest.csv` | 20.386 MB |
| `horizon_transport_detector_null_anatomy.csv` | 3.110 MB |
| `horizon_transport_matrix_sparse.npz` | 0.303 MB |

Only this retained note, the relevant documentation updates, and the reporting/decision code repair are intended for the public repositories.

## Audit Read

This run is a real positive for the instrument, not for the full theory.

What it supports:

```text
Horizon transport remains measurable after leaving the original
constraint-template vocabulary.

Transition-energy substrate families produce distinct but interpretable
response profiles under matched-marginal detector controls.

The live branch should continue into more principled substrate generation
rather than returning to hand-labeled constraint vocabularies.
```

What it does not support:

```text
Omega validated
agent detected
valuer detected
identity detected
holdout ready
candidate promoted
graph-channel causality established
```

## Max-Entropy Transition Ensemble Direction

The next substrate target should move toward a `max_entropy_local_transition` ensemble:

```text
primitive state space
local transition constraints
maximum-entropy transition distribution subject to those constraints
matched nulls preserved
horizon transport measured without hand-picked constraint vocabulary
```

The goal is to make the substrate less semantic while preserving enough local structure for horizon transport to be falsifiable.
