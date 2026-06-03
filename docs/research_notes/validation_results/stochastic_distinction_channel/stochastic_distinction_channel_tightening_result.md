# Stochastic Distinction Channel Instrument Tightening Result

Date: 2026-06-04
Branch: stochastic distinction-channel empirical-formal bridge
Spec: `docs/specs/current/STOCHASTIC_DISTINCTION_CHANNEL_TIGHTENING_SPEC.md`
Runner: `omega.stochastic_distinction_channel.probe`

## Executive Summary

The v0 stochastic-channel probe was tightened for formal consumption. The pass
adds explicit decoder policies, selected target-observation provenance,
support-versus-probability summaries, theorem-transfer readiness, and a formal
consumption bundle. It preserves the tiny prebiotic channel substrate and makes
no Omega, agency, identity, value, compatibility, or ethical claim.

## Local Artifacts

Output directory:

```text
results/stochastic_distinction_channel/20260604_stochastic_channel_probe_v0_tightened/
```

Primary report:

```text
stochastic_channel_probe_report.md
```

Formal bundle:

```text
formal_channel_consumption_bundle.json
```

Output size:

```text
about 3.375 MB
```

## Run Summary

```text
channel_count: 22
distinction_count: 15
recoverability_rows: 849
artifact_count: 33
artifact_manifest_digest: 1e662b260ea92303a91df284
formal_consumption_status: support_level_ready_probabilistic_measurement_only
```

Audit failures:

```text
channel_row_stochastic_audit: 0
distinction_partition_audit: 0
decoder_totality_audit: 0
threshold_application_audit: 0
```

## Tightening Changes

New compact artifacts:

```text
decoder_policy_manifest.csv
support_vs_probability_summary.csv
theorem_transfer_readiness_summary.csv
formal_channel_consumption_bundle.json
```

Schema repair:

```text
non_erasure_by_channel.csv:
  selected_target_distinction_ids
  selected_decoder_ids
  decoder_policy_id

marginal_joint_recoverability_diagnostic.csv:
  selected target-distinction IDs
  selected decoder IDs

support_recoverability.csv:
  support_target_nonambiguous
  support_source_label_coverage_complete
  support_source_label_count
  support_recovered_source_label_count
  ambiguous_support_target_label_count
```

Exact support recovery now requires both:

```text
target support non-ambiguity
positive-prior source-label coverage
```

## Support Versus Probability

Summary counts:

```text
exact_and_high_probability: 40
probabilistic_without_exact_support: 8
neither_exact_nor_high: 62
```

Key rows:

| Channel | Distinction | Best target | Success | Relation |
|---|---|---|---:|---|
| `identity_channel` | `D_joint` | `E_joint` | 1.000000 | `exact_and_high_probability` |
| `bit_flip_p_0_05` | `D_A` | `E_A` | 0.950000 | `probabilistic_without_exact_support` |
| `bit_flip_p_0_05` | `D_joint` | `E_joint` | 0.902500 | `neither_exact_nor_high` |
| `marginal_joint_degrade_q_0_10` | `D_A` | `E_A` | 0.950000 | `probabilistic_without_exact_support` |
| `marginal_joint_degrade_q_0_10` | `D_joint` | `E_joint` | 0.900000 | `neither_exact_nor_high` |
| `total_erasure_channel` | `D_joint` | `E_trivial_star` | 0.250000 | `neither_exact_nor_high` |

Read:

```text
High probabilistic recovery can remain present after exact support recovery
fails. The tightened outputs now make that distinction explicit.
```

## Marginal-Versus-Joint Diagnostic

Diagnostic class counts are unchanged from v0:

```text
all_nontrivial_lost: 8
marginal_and_joint_recovered: 2
marginal_recovered_joint_not_recovered: 3
mixed_or_partial: 6
```

For `marginal_joint_degrade_q_0_10`:

```text
req_marginals:
  2 / 2 recovered
  selected targets: D_A=E_A;D_B=E_B

req_joint:
  0 / 1 recovered
  selected target: D_joint=E_joint

req_all_nontrivial:
  2 / 4 recovered
```

This is finite channel measurement only. It is not compatibility detection or
ethical erasure.

## Theorem Transfer Readiness

```text
support_level_exact_channel_presentation:
  ready_for_formal_support_consumption

probabilistic_recovery_layer:
  measurement_only_pending_formal_theorem

thresholded_non_erasure_layer:
  measurement_only_thresholded

composition_probability_bounds:
  measurement_only_pending_formal_bound

completion_or_candidate_family:
  not_applicable
```

## Verification

```text
python -m pytest tests\test_stochastic_distinction_channel.py -q
  1 passed

python -m compileall omega\stochastic_distinction_channel tests\test_stochastic_distinction_channel.py
  passed
```

## Claim Boundary

Allowed:

```text
The stochastic-channel probe now emits formal-consumption-ready support-level
artifacts and explicitly separates support exactness from probabilistic decoder
success.
```

Blocked:

```text
Omega validation
proto-valuer / valuer detection
agency / identity / value detection
compatibility detection
support / capture / erasure in the ethical or Omega sense
substrate-general validation
```

## Next Recommendation

Send the formal arm the tightened consumption bundle first. If it accepts the
support-level layer, the next useful target is a probabilistic channel
presentation or composition-bound theorem. Do not broaden channel size until the
formal arm says which stochastic theorem-transfer object it wants.
