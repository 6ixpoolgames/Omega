# Stochastic Channel Theorem-Transfer Audit Result

Date: 2026-06-04
Branch: stochastic distinction-channel empirical-formal bridge
Spec: `docs/specs/current/STOCHASTIC_DISTINCTION_CHANNEL_THEOREM_TRANSFER_AUDIT_SPEC.md`
Postprocessor: `omega.stochastic_distinction_channel.theorem_transfer_audit`

## Executive Summary

The fixed-policy stochastic-channel output now compiles into a
theorem-transfer audit package for the Lean probabilistic channel presentation.
The main repair is denominator discipline: first-stage, second-stage, and
composite decoder errors are measured over the same finite cascade path
ensemble, so the checked Lean cascade error-bound theorem applies to the
declared fixed-policy composition rows.

Bayes-best rows remain present as diagnostics, but they are not substituted into
composition proofs.

## Local Artifacts

Source output:

```text
results/stochastic_distinction_channel/20260604_stochastic_channel_probe_v0_fixed_policy/
```

Audit output:

```text
results/stochastic_distinction_channel/20260604_stochastic_channel_theorem_transfer_audit_v0/
```

Primary report:

```text
stochastic_channel_theorem_transfer_audit_report.md
```

Formal bundle:

```text
probabilistic_channel_theorem_transfer_bundle.json
```

## Run Summary

```text
overall_status: support_and_probabilistic_transfer_ready
source_digest: 9777bb7e5f3fba4f554bfb42
bundle_digest: 2e4b7df0859a7fee48fb4648
registry_digest: unregistered_legacy_source
cascade_bound_rows: 10
cascade_bound_passes: 10
theorem_applicable_cascade_rows: 10
cascade_path_rows: 640
decoder_audit_failures: 0
```

Input status:

```text
missing inputs: none
source probe audits: ready
```

## New Audit Artifacts

```text
rational_weight_manifest.csv
natural_weight_realization.csv
natural_weight_realization_audit.csv
cascade_path_ensemble_manifest.csv
cascade_path_ensemble_rows.csv
cascade_total_mass.csv
cascade_error_mass_by_stage.csv
cascade_bound_check.csv
denominator_alignment_audit.csv
decoder_policy_alignment_audit.csv
no_self_evidencing_decoder_audit.csv
support_probability_theorem_boundary.csv
threshold_sensitivity_by_distinction.csv
marginal_joint_theorem_examples.csv
probabilistic_theorem_transfer_readiness_summary.csv
probabilistic_channel_theorem_transfer_bundle.json
```

## Cascade Bound Check

All fixed-policy cascade rows satisfy the finite error-bound inequality:

```text
composite_error_mass <= first_stage_error_mass + second_stage_error_mass
```

over the same path ensemble:

```text
mass(x,y,z) = pi(x) * K(y|x) * L(z|y)
```

Representative rows:

| Cascade | Distinction | Composite | First | Second | Status |
|---|---|---:|---:|---:|---|
| `comp_bitflip_0_10_then_0_25` | `D_A` | 1920 | 640 | 1600 | theorem applicable |
| `comp_bitflip_0_10_then_0_25` | `D_joint` | 3264 | 1216 | 2800 | theorem applicable |
| `comp_identity_then_marginal_degrade_0_10` | `D_A` | 4 | 0 | 4 | theorem applicable |
| `comp_identity_then_marginal_degrade_0_10` | `D_joint` | 8 | 0 | 8 | theorem applicable |

The audit explicitly reports:

```text
aligned_same_path_ensemble: 10 rows
uses_independently_normalized_stage_errors: 0 rows
cascade_evidence_status: path_rows_retained
recovery_provenance_class: fixed_declared_policy_no_registry
```

Because this source predates the registry-first repair, the rows now carry:

```text
registry_digest: unregistered_legacy_source
```

That field is intentionally not backfilled with a synthetic registry digest.

## Support Versus Probability Boundary

The theorem-boundary table separates exact support recovery from probabilistic
success:

```text
exact_support_and_perfect_probability: 302
high_probability_without_exact_support: 24
support_exact_failure_probability_high: 70
support_exact_failure_probability_low: 453
```

This preserves the formal split established in Lean:

```text
exact support recovery can transfer to root support calculus;
high probabilistic recovery alone cannot.
```

## Decoder Policy And No-Self-Evidencing Audit

Decoder policy alignment:

```text
aligned_declared_composition: 10
measurement_only_best_decoder_comparison: 10
```

Bayes-best composition rows are retained as `optimized_policy_search`
measurements. They are useful policy-search readouts, but stagewise Bayes-best
choices need not define a declared composable decoder chain.

Decoder audit:

```text
audit failures: 0
allowed recovery decoders use target-observation labels only
source-state / source-label / hidden-state oracle inputs: 0
```

## Theorem-Transfer Readiness

Ready for formal consumption:

```text
support_level_exact_channel_presentation
exact_implies_perfect_probability
perfect_full_prior_implies_exact
high_probability_not_exact_counterexample
cascade_error_bound
cascade_same_denominator_threshold_bound
bayes_best_vs_fixed_declared_policy_separation
```

Measurement-only:

```text
perfect_nonfull_prior_not_exact_counterexample:
  boundary slot emitted, but this tiny input has no non-full-support prior

thresholded_non_erasure_layer:
  finite thresholded recovery counts are emitted; theorem layer still pending
```

Not applicable:

```text
completion_or_candidate_family:
  no candidate-family/admissibility object is present in this channel audit
```

## Scope

This is an empirical-formal theorem-transfer audit for a tiny finite stochastic
channel substrate. It supports exact support/probability separation,
same-denominator cascade error-bound instantiation, decoder policy provenance,
and threshold sensitivity. Broader semantic interpretation remains outside this
adapter.

## Verification

```text
.venv\Scripts\python.exe -m pytest tests\test_stochastic_theorem_transfer_audit.py tests\test_stochastic_distinction_channel.py
  3 passed

.venv\Scripts\python.exe -m omega.stochastic_distinction_channel.theorem_transfer_audit --source results\stochastic_distinction_channel\20260604_stochastic_channel_probe_v0_fixed_policy --out results\stochastic_distinction_channel\20260604_stochastic_channel_theorem_transfer_audit_v0
  support_and_probabilistic_transfer_ready
```

## Next Recommendation

Do not broaden the stochastic channel substrate yet. The next formal ask should
be either:

```text
thresholded probabilistic non-erasure theorem;
candidate-family/admissibility presentation;
or a deliberate non-full-support prior example for the probability/support
boundary.
```
