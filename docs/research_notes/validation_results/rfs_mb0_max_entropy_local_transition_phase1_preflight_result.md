# RFS-MB0 Max Entropy Local Transition Phase 1 Preflight Result

Date: 2026-05-31

Local output:

```text
results/local_runs/20260531_max_entropy_local_transition_phase1_preflight_v2/
```

Runner:

```text
omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair
```

Spec:

```text
docs/RFS_MB0_MAX_ENTROPY_LOCAL_TRANSITION_PREFLIGHT_SPEC.md
```

## Purpose

This run tested the first real MaxEnt comparator fork after Phase 0 plumbing.
It placed deterministic preservation-asymmetry and maximum-entropy local
transition substrates on the same design set.

The key question was:

```text
Does the preservation-asymmetry response survive after replacing deterministic
top-m transition-energy selection with a maximum-entropy local transition
ensemble matched to the same macro-invariant edge marginal?
```

This remains design-set substrate characterization only. It is not holdout
validation, candidate promotion, graph causality, Omega detection, agency
detection, identity detection, value detection, or valuer detection.

## Run Shape

```text
status: COMPLETED
workers: 18
jobs_completed: 1280 / 1280
elapsed_seconds: 146.650
errors: 0
matrix_count: 3320
perturbation_response_rows: 2656
substrate_family_variant_count: 32
null_replicates: 9
selected_edge_overlap_sample_jobs: 80
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
terminal_saturation_flagged_rows: 0
readiness_level: deterministic_top_m_geometry_loadbearing
next_action_fork: audit_top_m_geometry_or_refine_max_entropy_sampler
```

All detector gates passed:

```text
horizon_transport_matrix_coverage: passed
structure_detector_null_separation: passed
detector_null_replicate_power: passed
matched_marginal_detector_null_separation: passed
synthetic_fixture_contract: 8 / 8
```

All MaxEnt paired baselines were available:

```text
paired_baseline_available_fraction: 1.0 for all 20 MaxEnt family / invariant / beta variants
paired_baseline_missing_rows: 0
```

## Substrate Families

The run included:

```text
constraint_template_current
locality_only
preservation_asymmetry
max_entropy_local
max_entropy_macro_invariant
```

Invariant tracks:

```text
symbol_histogram_distance
hamming_weight_or_nonzero_count
```

Beta targets:

```text
0.04, 0.05, 0.075, 0.10, 0.15
```

## Primary Result

Deterministic preservation-asymmetry responded. MaxEnt did not.

| substrate family | response rows | interpretable rows | dominant response | aligned fraction | aligned rows |
|---|---:|---:|---|---:|---:|
| constraint_template_current | 176 | 176 | transport_stable | 0.0000 | 0 |
| locality_only | 80 | 80 | transport_stable | 0.0000 | 0 |
| max_entropy_local | 800 | 800 | transport_stable | 0.0000 | 0 |
| max_entropy_macro_invariant | 800 | 800 | transport_stable | 0.0000 | 0 |
| preservation_asymmetry | 800 | 800 | transport_stable | 0.0825 | 66 |

Variant-level deterministic preservation-asymmetry response:

| variant | aligned fraction | aligned rows |
|---|---:|---:|
| hamming_weight_or_nonzero_count beta 0.04 | 0.000 | 0 |
| hamming_weight_or_nonzero_count beta 0.05 | 0.000 | 0 |
| hamming_weight_or_nonzero_count beta 0.075 | 0.000 | 0 |
| hamming_weight_or_nonzero_count beta 0.10 | 0.000 | 0 |
| hamming_weight_or_nonzero_count beta 0.15 | 0.000 | 0 |
| symbol_histogram_distance beta 0.04 | 0.000 | 0 |
| symbol_histogram_distance beta 0.05 | 0.000 | 0 |
| symbol_histogram_distance beta 0.075 | 0.175 | 14 |
| symbol_histogram_distance beta 0.10 | 0.175 | 14 |
| symbol_histogram_distance beta 0.15 | 0.475 | 38 |

This confirms the prior low-beta result qualitatively, but with the turn-on
appearing at beta `0.075` in this smaller design set rather than beta `0.05`.

## MaxEnt Marginal Match

The primary MaxEnt target was `symbol_histogram_distance`. It passed the
preflight match tolerance for all beta values.

Tolerance:

```text
macro_invariant_delta_match_error_max <= 0.10
```

Primary observed match:

| family | invariant | beta | mean match error | max match error | pass fraction |
|---|---|---:|---:|---:|---:|
| max_entropy_macro_invariant | symbol_histogram_distance | 0.04 | 0.0476 | 0.0514 | 1.00 |
| max_entropy_macro_invariant | symbol_histogram_distance | 0.05 | 0.0661 | 0.0679 | 1.00 |
| max_entropy_macro_invariant | symbol_histogram_distance | 0.075 | 0.0715 | 0.0772 | 1.00 |
| max_entropy_macro_invariant | symbol_histogram_distance | 0.10 | 0.0808 | 0.0813 | 1.00 |
| max_entropy_macro_invariant | symbol_histogram_distance | 0.15 | 0.0846 | 0.0864 | 1.00 |

The hamming comparator did not reliably meet the same tolerance:

| invariant | beta values failing full match tolerance |
|---|---|
| hamming_weight_or_nonzero_count | 0.05, 0.075, 0.10, 0.15 |

This is treated as a comparator limitation rather than a primary sampler
failure. The hamming track also produced no deterministic aligned response.

## Edge Calibration Audit

The MaxEnt macro-invariant graphs were substantially closer to their
deterministic preservation-asymmetry calibration graphs than unconstrained
MaxEnt-local graphs.

For `symbol_histogram_distance`:

| family | beta | Jaccard vs calibration | overlap fraction vs calibration |
|---|---:|---:|---:|
| max_entropy_local | 0.04 | 0.246 | 0.395 |
| max_entropy_local | 0.05 | 0.253 | 0.403 |
| max_entropy_local | 0.075 | 0.252 | 0.402 |
| max_entropy_local | 0.10 | 0.253 | 0.404 |
| max_entropy_local | 0.15 | 0.245 | 0.394 |
| max_entropy_macro_invariant | 0.04 | 0.459 | 0.630 |
| max_entropy_macro_invariant | 0.05 | 0.518 | 0.682 |
| max_entropy_macro_invariant | 0.075 | 0.621 | 0.766 |
| max_entropy_macro_invariant | 0.10 | 0.628 | 0.772 |
| max_entropy_macro_invariant | 0.15 | 0.641 | 0.781 |

This confirms the MaxEnt macro branch is moving toward the calibrated
deterministic graph at the edge level. The negative response result is not
because the macro sampler ignored the calibration target.

## Interpretation

This run supports a sharper fork:

```text
The deterministic top-m transition-energy geometry appears load-bearing for
the currently observed preservation-asymmetry response.
```

The strongest evidence is the simultaneous pattern:

```text
1. deterministic preservation_asymmetry responds on symbol_histogram_distance;
2. max_entropy_macro_invariant matches the requested delta_I marginal within
   tolerance;
3. max_entropy_macro_invariant remains transport_stable;
4. max_entropy_local also remains transport_stable;
5. locality_only and current-template comparators remain stable.
```

A minimal read is:

```text
The response is not explained by local random graph structure alone, and not by
the aggregate macro-invariant edge marginal alone. Some additional structure of
the deterministic top-m selection rule is carrying the response.
```

## Recommendation

Do not expand MaxEnt as a positive branch yet.

Recommended next step:

```text
audit_top_m_geometry_or_refine_max_entropy_sampler
```

Concrete follow-up options:

```text
1. Compare deterministic top-m, stochastic softmax over the same energy, and
   MaxEnt macro-marginal sampling on the same design set.
2. Add rank-conditioned MaxEnt or low-temperature Gibbs sampling to test
   whether edge ranking, not just marginal matching, is load-bearing.
3. Keep symbol_histogram_distance as the primary invariant and keep hamming as
   a low-signal comparator, not a gating invariant.
4. Avoid larger MaxEnt-only runs until this geometry question is resolved.
```
