# Future Field Atlas Formal Adapter Raw/Closed Gap Report Result

Date: 2026-06-03
Branch: Future Field Atlas / formal adapter conformance
Spec: `docs/specs/current/FUTURE_FIELD_ATLAS_FORMAL_ADAPTER_RAW_CLOSED_GAP_REPORT_SPEC.md`
Postprocessor: `omega.future_field_atlas.formal_adapter_gap_report`

## Summary

The raw/closed gap report completed.

This was a compact A-lite audit over the existing formal adapter package. It
did not run a new Future Field Atlas empirical sweep.

Input:

```text
results/future_field_atlas/20260603_formal_adapter_conformance_package/
input adapter status: generated_presentation_conformance
input bundle digest: ec392eb6a78f05e810497c99
```

Output:

```text
results/future_field_atlas/20260603_formal_adapter_raw_closed_gap_report/
report digest: 8ff5e37fad6f14b0c5661116
total compressed output size: about 0.120 MB
```

## Law Gap Summary

| Law | Raw pass | Closed pass | Raw gap | Gap fraction | Dependency |
|---|---:|---:|---:|---:|---|
| identity transport | 0 | 55,120 | 55,120 | 1.000000 | full generated closure |
| source weakening | 59,811 | 195,463 | 135,652 | 0.694003 | partial generated closure |
| target strengthening | 60,541 | 225,655 | 165,114 | 0.731710 | partial generated closure |
| lax composition | 28,823 | 44,211 | 15,388 | 0.348058 | partial generated closure |

Read:

```text
strict raw conformance remains blocked.
generated-presentation theorem transfer remains valid.
```

## Closed Transport Support

Closed transport rows:

```text
raw_observed: 39790
derived_identity: 55120
derived_target_strengthening: 19248
```

Fraction of closed relation:

```text
raw_observed: 0.348552
derived_identity: 0.482840
derived_target_strengthening: 0.168608
```

Interpretation:

```text
The generated closed relation is not a disguised raw model. Roughly 34.9% of
closed transport rows are raw observed rows; the rest are explicit generated
presentation structure.
```

## Theorem Transfer Dependency

All root-law theorem transfers remain closure-dependent:

```text
disttrans_identity:
  raw gap fraction 1.000000

disttrans_source_weakening:
  raw gap fraction 0.694003

disttrans_target_strengthening:
  raw gap fraction 0.731710

compositional_recoverability:
  raw gap fraction 0.348058

non_erasure_monotonicity:
  raw gap fraction 0.714208

finite_chain_recurrent_recoverability:
  raw gap fraction 0.348058
```

The marginal-versus-joint diagnostic remains partial / finite-measure-only.
Finite completion existence remains not applicable.

## Non-Erasure Gap

The non-erasure rows did not require closure-only promotion:

| Requirement | Raw non-erasing | Closed non-erasing | Closure-only |
|---|---:|---:|---:|
| req_high_yield_signature | 717 | 717 | 0 |
| req_joint_restriction_signature | 866 | 866 | 0 |
| req_marginal_preservation | 3,764 | 3,764 | 0 |
| req_operator_delta_signature | 3,024 | 3,024 | 0 |

This is a useful sanity result: finite non-erasure summaries are not being
inflated by closure-only recoveries in this package. The root-law transfer
still depends on closure, but the emitted non-erasure pass rows are raw-supported
where they pass.

## Recommendations

Do not broaden FFA or add completion/candidate-family machinery yet.

If the formal arm wants stricter empirical conformance, the next repair should
materialize explicit raw/derived witness provenance:

```text
target strengthening:
  highest raw gap count; add explicit derived-raw witness table from observed
  witnesses plus declared preorder.

source weakening:
  add explicit derived-raw witness table if strict raw model status is a real
  target.

lax composition:
  materialize composite witness provenance linking step, horizon-to-final, and
  composite transports.

identity:
  only worth emitting as raw if strict raw model status is prioritized; generated
  identity is ordinary for presentations.
```

Keep `raw_observed` and closure-derived support kinds separate in every future
report.

## Claim Boundary

Allowed:

```text
The raw/closed gap report quantifies how much of the adapter's law satisfaction
comes from raw witnesses versus generated closure.

The existing adapter remains formally consumable as a generated presentation.

Strict raw conformance remains blocked.
```

Blocked:

```text
Omega validation
proto-valuer detection
valuer detection
agency / identity / value detection
compatibility detection
support / capture / erasure detection
finite completion existence over FFA candidates
substrate-general validation
```

## Next Recommendation

Ask the formal arm whether strict raw model status is worth pursuing.

If yes, implement a provenance materialization pass. If no, keep the generated
presentation and move only when the formal arm provides the next minimal object
needed for theorem transfer.
