# RFS-MB0 Top-m Geometry Audit Spec

Status: narrow design-set audit / implemented runner target  
Builds on:
- `docs/research_notes/validation_results/rfs_mb0_max_entropy_local_transition_phase1_preflight_result.md`
- `docs/RFS_MB0_MAX_ENTROPY_LOCAL_TRANSITION_PREFLIGHT_SPEC.md`
- `docs/RFS_MB0_ASYMMETRY_LADDER_TRANSITION_ENERGY_SUBSTRATE_SPEC.md`

Scope: RFS-MB0 horizon-transport / transition-energy substrate branch  
Claim boundary: substrate instrumentation only; no Omega, agency, value, identity, valuerhood, holdout, candidate-promotion, or broad MaxEnt expansion claim.

## 0. One-sentence purpose

Determine whether the preservation-asymmetry response is carried by hard deterministic top-m rank geometry, low-temperature energy-biased sampling, rank-conditioned local structure, or neither.

## 1. Why this spec exists

The MaxEnt preflight found that deterministic `preservation_asymmetry` reproduced the symbol-histogram response region near beta `0.075-0.15`, while the current MaxEnt macro-marginal comparator stayed stable. That is informative but ambiguous:

```text
The response may be caused by:
  hard top-m edge selection;
  energy-rank bias without hard top-m;
  local ordinal/rank-bucket structure;
  an implementation-specific artifact;
  or insufficiently matched stochastic comparators.
```

This audit is deliberately narrow. It compares sampler geometry over the same design set instead of opening a new broad MaxEnt branch.

## 2. Required sampler comparison

Run these on the same design set:

```text
1. deterministic preservation_asymmetry top-m
2. stochastic softmax / Gibbs sampling over the same E(s,t)
3. rank-conditioned local MaxEnt / local-rank-bucket matched sampler
4. existing MaxEnt macro-marginal sampler
```

The deterministic family is the calibration reference. The stochastic families must report edge overlap, rank distribution match, energy distribution match, and per-state rank-bucket match against that reference.

## 3. Invariants

Primary invariant:

```text
symbol_histogram_distance
```

Diagnostic comparator:

```text
hamming_weight_or_nonzero_count
```

The comparator is not allowed to promote a positive read by itself.

## 4. Beta / temperature focus

Use the already observed response region:

```text
beta: 0.075, 0.10, 0.15
```

Include beta `0.05` when cheap enough. Softmax/Gibbs temperatures should be small enough to test low-temperature energy-rank bias without collapsing trivially into deterministic top-m.

## 5. Required audits and outputs

The runner must emit:

```text
top_m_geometry_sampler_diagnostics.csv
top_m_geometry_rank_energy_match_summary.csv
top_m_geometry_per_state_rank_bucket_match_summary.csv
top_m_geometry_edge_match_to_calibration.csv
response_by_sampler_family.csv
response_by_beta_or_temperature.csv
horizon_response_threshold_table.csv
paired baseline availability diagnostics
matched-marginal detector gate diagnostics
```

Response classification must require paired baseline and perturbation matrix availability across substrate variant, probe, flow mode, horizon pair, perturbation family, and perturbation strength. If a perturbation matrix exists without the paired baseline, classify it as `transport_baseline_missing` and exclude it from positive response summaries.

## 6. Interpretation fork

```text
If softmax/Gibbs recovers the response:
  hard top-m is not uniquely loadbearing; energy-rank bias is implicated.

If rank-conditioned MaxEnt recovers the response:
  local ordinal geometry is implicated.

If only deterministic top-m recovers the response:
  the current preservation effect is algorithmically narrow.

If all variants stay stable:
  inspect deterministic reproducibility before interpreting the absence.
```

## 7. Non-goals

```text
No holdout.
No Omega, agency, value, identity, or valuer claims.
No broad MaxEnt expansion.
No new substrate family beyond this sampler comparison unless needed to repair the audit.
```
