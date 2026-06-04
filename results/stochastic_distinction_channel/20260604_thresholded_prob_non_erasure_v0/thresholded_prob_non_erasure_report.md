# Thresholded Probabilistic Non-Erasure v0

## Executive Summary

This pass compiles thresholded probabilistic recovery into finite requirement-set non-erasure measurements. It keeps fixed-declared target policy separate from Bayes-best diagnostics, preserves the exact-support versus probabilistic-recovery boundary, and checks requirement-set monotonicity for the declared fixed-policy rows.

- overall status: `thresholded_prob_non_erasure_measurement_ready`
- fixed-policy non-erasing rows: 171
- Bayes-best diagnostic rows: 665
- monotonicity failures: 0

## Scope

finite thresholded probabilistic non-erasure measurement and formal-consumption preparation only

## Inputs

- theorem-transfer audit: `results\stochastic_distinction_channel\20260604_stochastic_channel_theorem_transfer_audit_v0`
- fixed-policy probe: `results\stochastic_distinction_channel\20260604_stochastic_channel_probe_v0_fixed_policy`
- missing inputs: `none`

## Requirement Sets And Thresholds

Requirement sets range from single distinctions (`req_A`, `req_B`) through `req_marginals`, `req_joint`, `req_parity`, and `req_all_nontrivial`. Thresholds are 0.80, 0.90, 0.95, 0.99, and 1.00.

## Decoder Eligibility

Fixed-declared target policy is the default theorem-transfer target. Bayes-best rows are emitted as diagnostics and are not silently substituted into fixed policy non-erasure claims.

## Non-Erasure Measurements

- total non-erasure rows: 1330
- fixed-policy rows with `prob_non_erasing=1`: 171
- Bayes-best measurement-only rows: 665

## Monotonicity

- monotonicity rows: 950
- failures: 0

## Support/Probability Boundary

- `mixed`: 130
- `neither`: 858
- `prob_recovered_without_support_exact`: 142
- `support_exact_and_prob_recovered`: 200

## Theorem-Transfer Status

- `thresholded_prob_non_erasure_definition`: ready_for_measurement_only
- `prob_non_erasure_monotonicity`: ready_for_measurement_only
- `support_exact_implies_prob_recovery`: ready_for_formal_consumption
- `prob_recovery_without_support_exact_boundary`: ready_for_formal_consumption
- `cascade_error_bound_relevance`: ready_for_formal_consumption
- `thresholded_non_erasure_composition`: ready_for_measurement_only
- `candidate_family_completion`: not_applicable

## Next Formal Ask

The formal arm can now define `ProbNonErasing(K, pi, Req, threshold, policy)` and prove monotonicity under requirement-set weakening. Composition of thresholded non-erasure remains a separate theorem target because it must connect thresholds to the existing cascade error-bound layer.