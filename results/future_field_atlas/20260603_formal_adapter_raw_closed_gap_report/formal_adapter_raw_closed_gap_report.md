# FFA Formal Adapter Raw/Closed Gap Report

## Summary

- input adapter status: `generated_presentation_conformance`
- input bundle digest: `ec392eb6a78f05e810497c99`
- input directory: `results\future_field_atlas\20260603_formal_adapter_conformance_package`

This is a compact A-lite audit over the existing adapter package. It does not run a new empirical sweep.

## Law Gap Summary

| Law | Raw pass | Closed pass | Gap | Gap fraction | Dependency |
|---|---:|---:|---:|---:|---|
| `identity_transport` | 0 | 55120 | 55120 | 1.000000 | `full_generated_closure` |
| `source_weakening` | 59811 | 195463 | 135652 | 0.694003 | `partial_generated_closure` |
| `target_strengthening` | 60541 | 225655 | 165114 | 0.731710 | `partial_generated_closure` |
| `lax_composition` | 28823 | 44211 | 15388 | 0.348058 | `partial_generated_closure` |

## Closed Transport Support

| Support kind | Rows | Fraction |
|---|---:|---:|
| `derived_identity` | 55120 | 0.482840 |
| `derived_target_strengthening` | 19248 | 0.168608 |
| `raw_observed` | 39790 | 0.348552 |

## Theorem Transfer Dependency

| Theorem | Transfer | Closure dependency | Raw gap fraction |
|---|---|---|---:|
| `disttrans_identity` | `transfers_to_closed_presentation` | `depends_on_generated_closure` | 1.000000 |
| `disttrans_source_weakening` | `transfers_to_closed_presentation` | `depends_on_generated_closure` | 0.694003 |
| `disttrans_target_strengthening` | `transfers_to_closed_presentation` | `depends_on_generated_closure` | 0.731710 |
| `compositional_recoverability` | `transfers_to_closed_presentation` | `depends_on_generated_closure` | 0.348058 |
| `non_erasure_monotonicity` | `transfers_to_closed_presentation` | `depends_on_generated_closure` | 0.714208 |
| `finite_chain_recurrent_recoverability` | `transfers_to_closed_presentation` | `depends_on_generated_closure` | 0.348058 |
| `marginal_non_erasure_not_joint_non_erasure` | `partial_transfer` | `not_law_based_or_not_applicable` | 0.000000 |
| `finite_completion_existence` | `not_applicable` | `not_law_based_or_not_applicable` | 0.000000 |

## Non-Erasure Gap

| Requirement | Raw non-erasing | Closed non-erasing | Closure-only |
|---|---:|---:|---:|
| `req_high_yield_signature` | 717 | 717 | 0 |
| `req_joint_restriction_signature` | 866 | 866 | 0 |
| `req_marginal_preservation` | 3764 | 3764 | 0 |
| `req_operator_delta_signature` | 3024 | 3024 | 0 |

## Recommendations

- `identity_transport`: Emit explicit raw identity witnesses only if strict raw model status is a goal; generated identity is mathematically ordinary for presentations.
- `target_strengthening`: Add an explicit derived-raw witness table for target strengthening from observed witnesses and declared preorder before changing the empirical substrate.
- `source_weakening`: Add an explicit derived-raw witness table for source weakening if the formal arm wants raw-closure rows materialized as evidence artifacts.
- `lax_composition`: Materialize composite witness provenance linking step, horizon-to-final, and composite transports; do not run broader FFA until this provenance is audited.
- `closed_transport_support_kind`: Keep generated closure explicit. Do not collapse raw_observed and closure-derived rows in future reports.

## Read

The formal adapter remains safe to consume as a generated closed presentation. The raw empirical witness relation remains below strict raw conformance. The next repair, if requested, should materialize explicit raw/derived witness provenance for target strengthening, source weakening, and composition before adding candidate-family or admissibility machinery.

## Claim Boundary

raw/closed adapter-gap audit only; no Omega validation, no compatibility detection, no proto-valuer / valuer detection, no support/capture/erasure detection