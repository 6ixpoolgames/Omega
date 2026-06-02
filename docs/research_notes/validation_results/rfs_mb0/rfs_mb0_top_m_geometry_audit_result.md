# RFS-MB0 Top-m Geometry Audit Result

Date: 2026-06-01 local / 2026-05-31 UTC
Runner: `omega.rfs_mb0_future_landscape.run_horizon_transport_spectral_response_repair`
Spec: `docs/specs/archive/rfs_mb0/RFS_MB0_TOP_M_GEOMETRY_AUDIT_SPEC.md`
Raw local output: `results/local_runs/20260601_top_m_geometry_audit/`
Tiny smoke output: `results/local_runs/20260601_top_m_geometry_audit_tiny_smoke/`
Claim boundary: substrate instrumentation only; no Omega, agency, value, identity, valuerhood, holdout, candidate-promotion, or broad MaxEnt expansion claim.

## Executive Read

The narrow top-m geometry audit completed cleanly and returned:

```text
readiness_level: algorithmically_narrow_top_m_geometry
next_action_fork: audit_hard_top_m_mechanism
```

The deterministic preservation-asymmetry top-m branch reproduced the
symbol-histogram response. The stochastic comparators did not:

```text
deterministic_top_m:
  aligned response present

softmax_gibbs_energy:
  no aligned response

rank_conditioned_local:
  no aligned response

max_entropy_macro_marginal:
  no aligned response
```

The current best read is therefore narrow: the preservation-asymmetry response is not recovered by the tested low-temperature energy sampler, local rank-window sampler, or macro-marginal MaxEnt comparator. In this run it remains tied to the hard deterministic top-m transition rule.

## Run Shape

```text
status: COMPLETED
workers: 18
jobs_completed: 2240 / 2240
elapsed_seconds: 228.005
errors: 0
matrix_count: 5600
perturbation_response_rows: 4480
context_recommendation_rows: 1120
null_replicates: 9
terminal_saturation_flagged_rows: 0
```

Families:

```text
preservation_asymmetry
softmax_preservation_asymmetry
rank_conditioned_max_entropy
max_entropy_macro_invariant
```

Primary invariant:

```text
symbol_histogram_distance
```

Diagnostic comparator:

```text
hamming_weight_or_nonzero_count
```

Betas:

```text
0.05, 0.075, 0.10, 0.15
```

Softmax/Gibbs temperatures:

```text
0.02, 0.05, 0.10
```

Rank-window multipliers:

```text
2, 3
```

## Gates

All required instrument gates passed:

```text
horizon_transport_matrix_coverage: passed
detector_null_sections_separate: passed
structure_detector_null_separation: passed
detector_null_replicate_power: passed
matched_marginal_detector_null_separation: passed
synthetic_fixture_contract: passed
```

No paired-baseline failures were observed for MaxEnt/rank-window variants:

```text
paired_baseline_missing_rows: 0
paired_baseline_status: ok
```

The primary MaxEnt macro-marginal sampler status for `symbol_histogram_distance` was `ok`. The hamming-weight comparator showed `repair_required` in the macro-marginal match table, but hamming was diagnostic only and did not carry any positive response.

## Post-run Implementation Audit

The follow-up code audit identified tightening requirements before the next mechanism run:

```text
enforce identical no-reversibility/no-rewire post-processing for all top-m audit families;
emit primary-invariant sampler response tables instead of only all-invariant aggregates;
emit context-level paired-baseline availability by sampler/probe/flow/horizon/perturbation;
make top-m audit readiness fail closed when required families or primary rows are missing;
label the rank-conditioned comparator as a top-rank-window local sampler, not full rank-bucket MaxEnt.
```

These changes are guardrails against the formal-core false-positive class named `deterministic substrate artifact`.

## Sampler Response

Across all invariants:

| sampler_family | response rows | aligned fraction | dominant response |
|---|---:|---:|---|
| deterministic_top_m | 640 | 0.103 | transport_stable |
| softmax_gibbs_energy | 1920 | 0.000 | transport_stable |
| rank_conditioned_local | 1280 | 0.000 | transport_stable |
| max_entropy_macro_marginal | 640 | 0.000 | transport_stable |

For the primary `symbol_histogram_distance` invariant only:

| sampler_family | aligned rows | response rows | aligned fraction |
|---|---:|---:|---:|
| deterministic_top_m | 66 | 320 | 0.206 |
| softmax_gibbs_energy | 0 | 960 | 0.000 |
| rank_conditioned_local | 0 | 640 | 0.000 |
| max_entropy_macro_marginal | 0 | 320 | 0.000 |

The diagnostic `hamming_weight_or_nonzero_count` comparator had:

```text
aligned rows: 0
response rows: 2240
dominant response: transport_stable
```

This keeps the positive read localized to symbol-histogram preservation, not generic invariant bookkeeping.

## Deterministic Beta Profile

For deterministic top-m preservation-asymmetry under `symbol_histogram_distance`:

| beta | aligned rows | response rows | aligned fraction |
|---:|---:|---:|---:|
| 0.05 | 0 | 80 | 0.000 |
| 0.075 | 14 | 80 | 0.175 |
| 0.10 | 14 | 80 | 0.175 |
| 0.15 | 38 | 80 | 0.475 |

The first aligned response again appears above beta `0.05`, with a stronger read at beta `0.15`.

Threshold table highlights:

```text
beta 0.075 and 0.10:
  small_edge_resample_control at strength 0.005
  first amplified-aligned horizon: 8->16

beta 0.15:
  small_edge_resample_control at strength 0.005
  first amplified-aligned horizon: 8->16

beta 0.15:
  asymmetric_edge_flip_control at strengths 0.0025 and 0.005
  first amplified-aligned horizon: 16->24
```

In all positive threshold rows, the latest interpretable horizon remained `96->128`.

## Geometry Audit

The sampler diagnostics compared each stochastic graph against the deterministic top-m calibration graph.

For `symbol_histogram_distance`:

| sampler | beta / setting | selected-edge overlap vs top-m | rank match error | energy match error | response |
|---|---|---:|---:|---:|---|
| deterministic_top_m | all betas | 1.000 | 0.000 | 0.000 | positive at 0.075+ |
| max_entropy_macro_marginal | beta 0.05 | 0.694 | 0.306 | 0.180 | stable |
| max_entropy_macro_marginal | beta 0.075 | 0.759 | 0.241 | 0.147 | stable |
| max_entropy_macro_marginal | beta 0.10 | 0.773 | 0.227 | 0.133 | stable |
| max_entropy_macro_marginal | beta 0.15 | 0.774 | 0.226 | 0.137 | stable |
| rank_conditioned_local | window 2 | about 0.493-0.503 | about 0.497-0.507 | about 0.346-0.365 | stable |
| rank_conditioned_local | window 3 | about 0.391-0.402 | about 0.598-0.609 | about 0.445-0.460 | stable |
| softmax_gibbs_energy | temp 0.02 | 0.468-0.609 | 0.391-0.532 | 0.265-0.377 | stable |
| softmax_gibbs_energy | temp 0.05 | 0.428-0.484 | 0.516-0.572 | 0.378-0.417 | stable |
| softmax_gibbs_energy | temp 0.10 | 0.409-0.438 | 0.562-0.591 | 0.419-0.434 | stable |

The MaxEnt macro-marginal comparator actually reached the highest non-deterministic edge overlap, but it still stayed stable. That argues against a simple global edge-overlap or macro-marginal explanation. The tested softmax and rank-window samplers also failed to recover the response, even where overlap increased at lower temperature and higher beta.

## Interpretation

This run supports the narrow interpretation:

```text
The current preservation-asymmetry response is algorithmically narrow to
hard deterministic top-m edge selection in this design-set audit.
```

It does not show that preservation asymmetry is false or uninteresting. It shows that the currently observed aligned response is not reproduced by the first principled stochastic relaxations we tested.

The strongest remaining technical question is what exact feature of hard top-m is doing the work:

```text
local discontinuity at the top-m cutoff;
per-state exact rank boundary;
edge-core versus fringe replacement;
deterministic tie / near-tie behavior;
or a response-taxonomy interaction with the deterministic graph.
```

## Recommendation

Do not expand the broad MaxEnt branch yet.

Next best run:

```text
audit_hard_top_m_mechanism
```

Suggested target:

```text
Compare exact deterministic top-m against minimal controlled variants:
  top-m core preserved, fringe randomized;
  top-m fringe preserved, core randomized;
  m +/- 1 rank boundary perturbations;
  deterministic top-m with near-tie jitter;
  very-low-temperature softmax below 0.02 only if it does not simply become top-m.
```

Keep the same primary invariant:

```text
symbol_histogram_distance
```

Keep hamming-weight only as a diagnostic comparator.

Do not promote Omega/agency/value claims from this result.
