# Stochastic Distinction Channel Probe v0 Result

Date: 2026-06-03
Branch: stochastic distinction-channel empirical-formal bridge
Spec: `docs/specs/current/STOCHASTIC_DISTINCTION_CHANNEL_EMPIRICAL_SPEC.md`
Runner: `omega.stochastic_distinction_channel.probe`

## Executive Summary

The v0 stochastic channel probe built a tiny finite prebiotic substrate with
declared channels, distinctions, priors, decoders, thresholds, support exports,
and composition checks. Identity recovered the joint distinction; total erasure
did not; nonzero stochastic channels separated support-level exact recovery from
probabilistic decoder success. This is a formal-consumption bridge only, not an
Omega or semantic-detection result.

## Local Artifacts

Output directory:

```text
results/stochastic_distinction_channel/20260603_stochastic_channel_probe_v0/
```

Primary report:

```text
stochastic_channel_probe_report.md
```

Manifest:

```text
channel_probe_manifest.json
artifact_manifest.json
```

Output size:

```text
about 3.302 MB
```

## Run Summary

```text
channel_count: 22
distinction_count: 15
recoverability_rows: 849
artifact_manifest_digest: a9c7a29dbf4cc5f2aa4422ed
```

Audit failures:

```text
channel_row_stochastic_audit: 0
distinction_partition_audit: 0
decoder_totality_audit: 0
threshold_application_audit: 0
```

## Sanity Checks

Identity channel:

```text
D_joint best decoder success: 1.000000
```

Total erasure channel:

```text
D_joint best decoder success: 0.250000
```

Read:

```text
identity recovers declared source distinctions;
total erasure leaves only chance-level recovery for nontrivial distinctions.
```

## Marginal-Versus-Joint Diagnostic

Diagnostic class counts:

```text
all_nontrivial_lost: 8
marginal_and_joint_recovered: 2
marginal_recovered_joint_not_recovered: 3
mixed_or_partial: 6
```

Key finite-channel examples:

| Channel | A success | B success | Joint success | Diagnostic |
|---|---:|---:|---:|---|
| `identity_channel` | 1.000000 | 1.000000 | 1.000000 | `marginal_and_joint_recovered` |
| `total_erasure_channel` | 0.500000 | 0.500000 | 0.250000 | `all_nontrivial_lost` |
| `bit_flip_p_0_05` | 0.950000 | 0.950000 | 0.902500 | `marginal_recovered_joint_not_recovered` |
| `marginal_joint_degrade_q_0_10` | 0.950000 | 0.950000 | 0.900000 | `marginal_recovered_joint_not_recovered` |

This is a finite stochastic-channel diagnostic only. It is not compatibility
detection or ethical erasure.

## Support Versus Probability

The implementation emits both:

```text
support_relation.csv:
  K(y|x) > 0

support_recoverability.csv:
  exact support-recoverability candidates

recoverability_by_distinction.csv:
  probabilistic decoder success, chance baseline, excess success, and
  normalized recovery advantage
```

This matters because nonzero stochastic noise can destroy exact support recovery
while preserving high probabilistic recovery.

## Non-Erasure Requirement Sets

At threshold `high_recovery = success >= 0.95`:

```text
identity_channel:
  req_marginals: 2 / 2
  req_joint: 1 / 1
  req_parity: 1 / 1
  req_all_nontrivial: 4 / 4

marginal_joint_degrade_q_0_10:
  req_marginals: 2 / 2
  req_joint: 0 / 1
  req_parity: 0 / 1
  req_all_nontrivial: 2 / 4

total_erasure_channel:
  all nontrivial requirement sets fail
```

## Composition

Composition artifacts emitted:

```text
channel_composition_manifest.csv
composed_channel_matrix.csv
composition_recoverability_check.csv
```

Composition check rows:

```text
10
```

These rows report measured composed success and a simple product-success
reference. They are measurement rows, not standalone theorems.

## Claim Boundary

Allowed:

```text
A finite stochastic channel probe was constructed with declared distinctions,
channels, priors, decoders, recoverability metrics, support projections, audits,
and non-erasure requirement sets.

Declared distinctions are recovered or not recovered under specified channels,
decoders, priors, and thresholds.

Marginal and joint distinction recovery can be compared in this finite channel
substrate.
```

Blocked:

```text
Omega validation
proto-valuer detection
valuer detection
agency / identity / value detection
compatibility detection
support / capture / erasure in the ethical or Omega sense
maintenance gap
identity-decay null
substrate-general validation
```

## Next Recommendation

Ask the formal arm to consume support-level exact recovery and probabilistic
decoder recovery separately.

The next useful formal target is probably a probabilistic composition-bound
statement or audit. Do not broaden to larger channels until the formal arm says
which stochastic theorem-transfer object it wants.
