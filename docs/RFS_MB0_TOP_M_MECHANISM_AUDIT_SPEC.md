# RFS-MB0 Hard Top-m Mechanism Audit Spec

Status: small smoke implemented / medium run pending
Builds on:
- `docs/RFS_MB0_TOP_M_GEOMETRY_AUDIT_SPEC.md`
- `docs/research_notes/validation_results/rfs_mb0_top_m_geometry_audit_result.md`
- `docs/research_notes/omega_theory/omega_formal_core_v0.md`

Scope: RFS-MB0 horizon-transport / transition-energy substrate branch  
Claim boundary: substrate instrumentation only; no Omega, agency, value, identity, valuerhood, holdout, candidate-promotion, or broad MaxEnt expansion claim.

## 0. One-sentence purpose

Determine which part of the hard deterministic top-m mechanism carries the preservation-asymmetry response.

## 1. Why this spec exists

The top-m geometry audit found that deterministic `preservation_asymmetry` reproduced the `symbol_histogram_distance` response, while softmax/Gibbs, rank-window local sampling, and MaxEnt macro-marginal comparators stayed stable. The resulting fork was:

```text
algorithmically_narrow_top_m_geometry -> audit_hard_top_m_mechanism
```

This spec stays inside that fork. It does not open a new substrate family or promote a theory claim. It asks whether the response survives principled perturbations of hard top-m selection itself.

## 2. Required mechanism comparison

Run these on the same design set:

```text
1. deterministic preservation_asymmetry top-m
2. top_m_core_preserved_fringe_randomized
3. top_m_core_randomized_fringe_preserved
4. top_m_boundary_jitter
5. top_m_m_minus_1
6. top_m_m_plus_1
```

All variants use the same preservation energy:

```text
E(s,t) = hamming_distance(s,t)
       + beta * abs(symbol_histogram_distance(t) - symbol_histogram_distance(s))
       + seeded_roughness(s,t)
```

All compared variants must use:

```text
no reversibility transform;
no random rewire transform;
paired baseline availability gating;
matched-marginal detector gates;
fixture contract gates.
```

## 3. Primary Invariant

Primary invariant:

```text
symbol_histogram_distance
```

Diagnostic invariants are allowed, but they cannot promote a positive read by themselves.

## 4. Beta and Horizon Focus

Use the previously observed response region:

```text
beta: 0.075, 0.10, 0.15
```

Small smokes should include the first response region:

```text
4->8
8->16
16->24
24->32
```

Medium runs should restore the broader H128 horizon ladder if the smoke gates pass.

## 5. Required Outputs

The runner must emit the standard horizon-transport outputs plus:

```text
top_m_geometry_sampler_diagnostics.csv
top_m_geometry_rank_energy_match_summary.csv
top_m_geometry_per_state_rank_bucket_match_summary.csv
top_m_geometry_edge_match_to_calibration.csv
response_by_sampler_family.csv
response_by_beta_or_temperature.csv
response_by_sampler_family_and_invariant.csv
response_by_beta_or_temperature_and_invariant.csv
paired_baseline_availability_by_sampler_context.csv
horizon_response_threshold_table.csv
```

The edge/rank diagnostics must include the mechanism rule where applicable.

## 6. Interpretation Fork

```text
If boundary jitter recovers the response:
  exact edge identity may be less loadbearing than near-boundary ordinal geometry.

If core/fringe randomized variants recover the response:
  identify whether the low-rank core or boundary/fringe structure carries the response.

If m-1 recovers but m+1 does not:
  the response may be tied to sparse strict pruning rather than full top-m identity.

If m+1 recovers but randomized variants do not:
  the selected top-m set may be loadbearing while added near-boundary edges are tolerated.

If only deterministic top-m recovers:
  the current response should be treated as hard-top-m exact-selection narrow until repaired or replaced.
```

## 7. Non-goals

```text
No holdout.
No n=6 transfer.
No alphabet expansion.
No candidate promotion.
No Omega, agency, identity, valuer, or value claims.
No broad MaxEnt expansion.
```
