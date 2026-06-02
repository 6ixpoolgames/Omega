# RFS-MB0 Max Entropy Local Transition Phase 0 Result

Date: 2026-05-31

Local output:

```text
results/local_runs/20260531_max_entropy_local_transition_phase0_v3/
```

Runner:

```text
omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair
```

Spec:

```text
docs/specs/archive/rfs_mb0/RFS_MB0_MAX_ENTROPY_LOCAL_TRANSITION_PREFLIGHT_SPEC.md
```

## Purpose

This run implemented and smoked the first maximum-entropy local-transition
substrate branch.

The key question was:

```text
If locality and exact out-degree are preserved, and the sampled transition graph
is matched to the deterministic preservation-asymmetry macro-invariant
delta_I marginal, does the aligned horizon-transport response reappear?
```

This remains design-set substrate instrumentation only. It is not holdout
validation, candidate promotion, graph causality, Omega detection, agency
detection, identity detection, value detection, or valuer detection.

## Implementation Added

The runner now supports:

```text
max_entropy_local
max_entropy_macro_invariant
```

The MaxEnt local family samples uniformly from local Hamming-ball candidate
edges while preserving exact out-degree.

The MaxEnt macro-invariant family:

```text
1. builds a deterministic preservation_asymmetry calibration graph;
2. extracts its macro-invariant delta_I edge marginal;
3. fits bucket weights for local candidate edges;
4. samples exact-out-degree local edges;
5. selects the sampled graph with the lowest total-variation marginal error.
```

The runner now emits the MaxEnt-specific audit files requested by the spec:

```text
max_entropy_constraint_manifest.csv
max_entropy_marginal_match_summary.csv
max_entropy_sampler_diagnostics.csv
max_entropy_edge_match_to_calibration.csv
response_by_max_entropy_family.csv
response_by_equivalent_beta_target.csv
paired_baseline_availability_by_max_entropy_variant.csv
```

Two instrumentation repairs were needed before retaining the final Phase 0 run:

```text
1. substrate system IDs now include substrate_variant, preventing beta variants
   from collapsing in sampler diagnostics;
2. max_entropy_edge_match_to_calibration.csv now samples round-robin across
   family / invariant / beta buckets instead of taking the first N jobs.
```

The spec and formatting guide were also normalized to use ASCII `delta_I`
instead of the Unicode delta symbol in implementation-facing text.

## Run Shape

```text
status: COMPLETED
workers: 18
jobs_completed: 160 / 160
elapsed_seconds: 24.326
errors: 0
matrix_count: 400
perturbation_response_rows: 320
substrate_family_variant_count: 4
null_replicates: 5
selected_edge_overlap_sample_jobs: 24
matched_marginal_detector_null_gate_passed: 1
synthetic_fixture_contract: passed
terminal_saturation_flagged_rows: 0
readiness_level: max_entropy_preflight_smoke_completed
next_action_fork: run_max_entropy_phase1_preflight
```

All detector gates passed:

```text
horizon_transport_matrix_coverage: passed
structure_detector_null_separation: passed
detector_null_replicate_power: passed
matched_marginal_detector_null_separation: passed
synthetic_fixture_contract: 8 / 8
```

All paired baselines were available:

```text
max_entropy_local beta 0.05:           80 / 80 available
max_entropy_local beta 0.10:           80 / 80 available
max_entropy_macro_invariant beta 0.05: 80 / 80 available
max_entropy_macro_invariant beta 0.10: 80 / 80 available
```

## Marginal Match

The macro-invariant MaxEnt sampler met the Phase 0 match tolerance.

Tolerance:

```text
macro_invariant_delta_match_error_max <= 0.10
```

Observed:

| family | invariant | beta | baseline systems | target applied | mean match error | max match error |
|---|---|---:|---:|---:|---:|---:|
| max_entropy_local | symbol_histogram_distance | 0.05 | 4 | 0 | n/a | n/a |
| max_entropy_local | symbol_histogram_distance | 0.10 | 4 | 0 | n/a | n/a |
| max_entropy_macro_invariant | symbol_histogram_distance | 0.05 | 4 | 4 | 0.0661 | 0.0679 |
| max_entropy_macro_invariant | symbol_histogram_distance | 0.10 | 4 | 4 | 0.0808 | 0.0813 |

The beta 0.10 target is harder to match than beta 0.05 but still passes the
preflight tolerance.

## Edge Calibration Audit

The sampled MaxEnt macro-invariant graphs overlap their deterministic
preservation-asymmetry calibration graphs much more than the unconstrained
local MaxEnt graphs.

| family | beta | sample count | Jaccard vs calibration | overlap fraction vs calibration |
|---|---:|---:|---:|---:|
| max_entropy_local | 0.05 | 6 | 0.253 | 0.403 |
| max_entropy_local | 0.10 | 6 | 0.253 | 0.404 |
| max_entropy_macro_invariant | 0.05 | 6 | 0.518 | 0.682 |
| max_entropy_macro_invariant | 0.10 | 6 | 0.628 | 0.772 |

This supports the instrumentation claim that the MaxEnt macro branch is not
just relabeling local random graphs. It is actually moving the sampled graph
toward the deterministic preservation calibration while preserving local
sampling and exact out-degree.

## Response Readout

No aligned response appeared in this Phase 0 smoke.

| family | response rows | interpretable rows | dominant response | aligned fraction |
|---|---:|---:|---|---:|
| max_entropy_local | 160 | 160 | transport_stable | 0.000 |
| max_entropy_macro_invariant | 160 | 160 | transport_stable | 0.000 |

By equivalent beta target:

| beta | response rows | interpretable rows | dominant response | aligned fraction |
|---:|---:|---:|---|---:|
| 0.05 | 160 | 160 | transport_stable | 0.000 |
| 0.10 | 160 | 160 | transport_stable | 0.000 |

## Interpretation

The implementation smoke passed. The MaxEnt sampler is now usable for the next
preflight stage: it preserves locality and out-degree, matches the requested
macro-invariant delta_I marginal within tolerance, emits paired-baseline
diagnostics, and produces transport matrices under the existing detector gates.

The scientific readout is deliberately limited. In this small Phase 0 design
set, matched macro-invariant edge marginals did not recover the previously
observed preservation-asymmetry aligned response. That does not falsify the
MaxEnt branch, because this was an implementation preflight with only four
baseline systems and two beta targets. It does, however, make the next test
important: deterministic preservation_asymmetry and MaxEnt macro-invariant
should be run side-by-side on the same design set.

## Recommendation

Proceed to the narrow Phase 1 preflight, but include deterministic comparators
in the same run:

```text
locality_only
preservation_asymmetry
max_entropy_local
max_entropy_macro_invariant
constraint_template_current
```

Use:

```text
macro_invariant_kind: symbol_histogram_distance
equivalent_beta_target: 0.04, 0.05, 0.075, 0.10, 0.15
null_replicates: 9
selected-edge calibration audit: mandatory
paired-baseline availability: mandatory
```

The key fork is now:

```text
If deterministic preservation_asymmetry responds but MaxEnt macro-invariant
does not, deterministic top-m geometry is load-bearing.

If MaxEnt macro-invariant responds while MaxEnt local remains stable, the
preservation signal is less tied to the deterministic top-m rule.

If MaxEnt local responds too, the response may be generic local random graph
structure rather than macro-invariant preservation.
```
