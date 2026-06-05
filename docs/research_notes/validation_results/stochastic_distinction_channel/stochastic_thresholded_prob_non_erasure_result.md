# Stochastic Thresholded Probabilistic Non-Erasure Result

Date: 2026-06-04
Branch: stochastic distinction-channel empirical-formal bridge
Spec: `docs/specs/current/STOCHASTIC_DISTINCTION_CHANNEL_THRESHOLDED_NON_ERASURE_SPEC.md`
Postprocessor: `omega.stochastic_distinction_channel.thresholded_non_erasure`

## Executive Summary

The stochastic-channel branch now has a finite thresholded probabilistic
non-erasure package. It compiles retained recovery rows into requirement-set
measurements over declared thresholds, keeps fixed-declared target policy
separate from Bayes-best diagnostics, preserves the exact-support versus
probabilistic-recovery boundary, and checks monotonicity under requirement-set
weakening.

The result is measurement-ready for the formal arm. It is not yet a Lean theorem
transfer for `ProbNonErasing`, because that definition and monotonicity theorem
are the next formal target.

## Local Artifacts

Input theorem-transfer audit:

```text
results/stochastic_distinction_channel/20260604_stochastic_channel_theorem_transfer_audit_v0/
```

Input fixed-policy probe:

```text
results/stochastic_distinction_channel/20260604_stochastic_channel_probe_v0_fixed_policy/
```

Output:

```text
results/stochastic_distinction_channel/20260604_thresholded_prob_non_erasure_v0/
```

Primary report:

```text
thresholded_prob_non_erasure_report.md
```

Formal bundle:

```text
thresholded_prob_non_erasure_bundle.json
```

Output size:

```text
about 1.46 MB
```

## Run Summary

```text
overall_status: thresholded_prob_non_erasure_measurement_ready
bundle_digest: ba2f166d8e375dd5524b18f6
registry_digest: unregistered_legacy_source
cascade_evidence_status: path_rows_retained
thresholded_prob_non_erasure_by_channel rows: 1330
prob_non_erasure_monotonicity_check rows: 950
fixed-policy prob_non_erasing rows: 171
Bayes-best measurement-only rows: 665
monotonicity failures: 0
```

Support/probability boundary:

```text
support_exact_and_prob_recovered: 200
prob_recovered_without_support_exact: 142
mixed: 130
neither: 858
```

## Predictive/Revelatory Fixtures

The expected finite-channel fixtures passed:

```text
identity_channel + req_all_nontrivial + threshold_1_00:
  prob_non_erasing

bit_flip_p_0_05 + req_marginals + threshold_0_95:
  prob_non_erasing
  support_probability_relation = prob_recovered_without_support_exact

bit_flip_p_0_05 + req_joint + threshold_0_95:
  not_non_erasing_below_threshold

total_erasure_channel + req_joint + threshold_0_80:
  blocked_missing_fixed_target
```

Read:

```text
The instrument can distinguish exact support recovery, probability-only
threshold recovery, below-threshold recovery, and fixed-policy unavailability.
```

## Monotonicity

The declared requirement-subset audit passed:

```text
monotonicity rows: 950
failures: 0
```

This means the empirical package respects the expected formal shape:

```text
if a larger requirement set is non-erasing, each declared smaller subset is
also non-erasing
```

for fixed-declared target-policy rows.

## Policy Discipline

The runtime separates:

```text
fixed_declared_target_policy:
  default formal-consumption target

bayes_best_target_policy:
  optimized policy-search measurement unless formalized as its own frozen
  policy object
```

This is target-policy separation, not decoder-kind separation. Fixed-declared
target rows may use Bayes-optimal decoders over the fixed declared target
observation.

Because this source predates the registry-first repair, thresholded rows now
carry:

```text
recovery_provenance_class: fixed_declared_policy_no_registry | optimized_policy_search
registry_digest: unregistered_legacy_source
cascade_evidence_status: path_rows_retained
```

The point is not to discard Bayes/optimized rows. The point is to report them as
policy-search measurements until a policy registry or selection rule is frozen
and digest-backed.

## Theorem-Transfer Status

Ready for formal consumption:

```text
support_exact_implies_prob_recovery
prob_recovery_without_support_exact_boundary
cascade_error_bound_relevance
```

Measurement-ready, pending Lean definition/theorem:

```text
thresholded_prob_non_erasure_definition
prob_non_erasure_monotonicity
thresholded_non_erasure_composition
```

Not applicable:

```text
candidate_family_completion
```

## Scope

This result concerns finite stochastic-channel requirement-set recovery under
declared target policies, decoders, priors, and thresholds. It is a
formal-consumption package for a future `ProbNonErasing` definition and
monotonicity theorem.

## Verification

```text
.venv\Scripts\python.exe -m pytest tests\test_stochastic_distinction_channel.py tests\test_stochastic_theorem_transfer_audit.py tests\test_stochastic_thresholded_non_erasure.py -q
  7 passed
```

## Next Recommendation

Ask the formal arm to define:

```text
ProbNonErasing(K, pi, Req, threshold, target_policy)
```

and prove:

```text
if Req' subset Req and K is ProbNonErasing for Req,
then K is ProbNonErasing for Req'
```

Composition of thresholded non-erasure should remain a later theorem because it
must connect threshold choices to the existing cascade error-bound layer.
