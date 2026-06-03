# Stochastic Distinction Channel Fixed Policy Result

Date: 2026-06-04
Branch: stochastic distinction-channel empirical-formal bridge
Spec: `docs/specs/current/STOCHASTIC_DISTINCTION_CHANNEL_FIXED_POLICY_SPEC.md`
Runner: `omega.stochastic_distinction_channel.probe`

## Executive Summary

The stochastic-channel bridge now reports Bayes-best and fixed declared target
policies side by side. This closes the main instrumentation concern: recovery
summaries no longer depend only on whichever target observation scores best.
Primary finite-channel reads are unchanged, while target-observation provenance
is clearer.

## Local Artifacts

Output directory:

```text
results/stochastic_distinction_channel/20260604_stochastic_channel_probe_v0_fixed_policy/
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
about 3.280 MB
```

## Run Summary

```text
channel_count: 22
distinction_count: 15
recoverability_rows: 849
artifact_count: 34
artifact_manifest_digest: df8b6413e001f4e5cf30b79c
formal_bundle_digest: 9777bb7e5f3fba4f554bfb42
formal_consumption_status: support_level_ready_probabilistic_measurement_only
```

Audit failures:

```text
channel_row_stochastic_audit: 0
distinction_partition_audit: 0
decoder_totality_audit: 0
threshold_application_audit: 0
```

## What Changed

New artifact:

```text
declared_target_policy_summary.csv
```

Updated artifacts:

```text
formal_channel_consumption_bundle.json:
  includes declared_target_policy_summary.csv

non_erasure_by_channel.csv:
  includes bayes_best_target_distinction rows
  includes fixed_declared_target_distinction rows

marginal_joint_recoverability_diagnostic.csv:
  includes bayes_best_target_distinction rows
  includes fixed_declared_target_distinction rows
```

The generated report now uses a concise `Scope` section instead of repeating
long negative claim lists.

## Policy Comparison

For the main rows, fixed declared target observations agree with Bayes-best:

| Channel | Distinction | Fixed target | Success | Delta vs Bayes-best |
|---|---|---|---:|---:|
| `identity_channel` | `D_joint` | `E_joint` | 1.000000 | 0.000000 |
| `bit_flip_p_0_05` | `D_A` | `E_A` | 0.950000 | 0.000000 |
| `bit_flip_p_0_05` | `D_joint` | `E_joint` | 0.902500 | 0.000000 |
| `marginal_joint_degrade_q_0_10` | `D_A` | `E_A` | 0.950000 | 0.000000 |
| `marginal_joint_degrade_q_0_10` | `D_joint` | `E_joint` | 0.900000 | 0.000000 |

Useful visible divergences:

```text
projection_A_channel:
  D_B, D_joint, and D_parity have no fixed declared target on Y_A.
  Bayes-best can still choose E_A_marg diagnostically.

projection_B_channel:
  D_A, D_joint, and D_parity have no fixed declared target on Y_B.
  Bayes-best can still choose E_B_marg diagnostically.

random_channel_same_output_entropy_seed_17:
  D_A fixed target E_A differs from Bayes-best E_joint.
  D_parity fixed target E_parity differs from Bayes-best E_A.

total_erasure_channel:
  nontrivial distinctions have no fixed declared target on Y_star.
  Bayes-best reports chance-level recovery through E_trivial_star.
```

## Support Versus Probability

Summary counts are unchanged:

```text
exact_and_high_probability: 40
probabilistic_without_exact_support: 8
neither_exact_nor_high: 62
```

The core distinction remains:

```text
High probabilistic recovery can exist without exact support recovery.
```

## Marginal-Versus-Joint Diagnostic

Bayes-best and fixed-declared policies agree on diagnostic class counts:

```text
bayes_best_target_distinction:
  all_nontrivial_lost: 8
  marginal_and_joint_recovered: 2
  marginal_recovered_joint_not_recovered: 3
  mixed_or_partial: 6

fixed_declared_target_distinction:
  all_nontrivial_lost: 8
  marginal_and_joint_recovered: 2
  marginal_recovered_joint_not_recovered: 3
  mixed_or_partial: 6
```

## Scope

This result concerns finite stochastic channel recovery under declared
distinctions, target observations, decoders, priors, and thresholds. Broader
interpretation depends on subsequent formal and empirical work.

## Verification

```text
pytest -q
  25 passed

compileall omega/stochastic_distinction_channel
  passed
```

## Next Recommendation

Hand the fixed-policy bundle to the formal arm. If accepted, the next useful
formal request is a probabilistic channel presentation or composition-bound
statement. Empirically, the instrument is ready for small 3P channel probes
without another schema repair.
