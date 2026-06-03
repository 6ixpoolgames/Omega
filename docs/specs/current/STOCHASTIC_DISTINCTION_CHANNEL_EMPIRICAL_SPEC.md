# Stochastic Distinction Channel Empirical Spec v0

Status: completed v0
Target package: `omega.stochastic_distinction_channel`
Runner: `omega.stochastic_distinction_channel.probe`
Initial output: `results/stochastic_distinction_channel/20260603_stochastic_channel_probe_v0/`
Current output: `results/stochastic_distinction_channel/20260604_stochastic_channel_probe_v0_fixed_policy/`

## Purpose

Build a tiny finite stochastic-channel substrate that exposes:

```text
relation:
  stochastic channel K(y|x)

distinction:
  declared finite source and target labelings / partitions

asymmetry:
  selective preservation or degradation of distinctions under the channel

recoverability:
  named decoder success under declared priors and thresholds
```

This is a formal-consumption probe only. It does not validate Omega and does
not make agency, identity, value, compatibility, valuerhood, or ethical claims.

## Required Tightening

The v0 implementation must keep these distinctions explicit:

```text
support/exact recoverability:
  exact decoder exists over support projection K(y|x) > 0

probabilistic recoverability:
  decoder success probability under a declared source prior

thresholded recovery:
  whether a predeclared threshold is passed
```

Marginal-versus-joint diagnostics must include:

```text
observation_scope
chance_success_probability
excess_success_over_chance
normalized_recovery_advantage
```

This prevents a marginal/joint result from being a hidden artifact of what the
target observation exposes.

The current tightened implementation also emits:

```text
decoder_policy_manifest.csv
declared_target_policy_summary.csv
support_vs_probability_summary.csv
theorem_transfer_readiness_summary.csv
formal_channel_consumption_bundle.json
```

Exact support recoverability requires both target support non-ambiguity and
positive-prior source-label coverage.

## Required Artifacts

```text
channel_probe_manifest.json
artifact_manifest.json
carrier_manifest.csv
channel_manifest.csv
channel_matrix.csv
channel_support.csv
source_prior_manifest.csv
distinction_manifest.csv
source_observation_table.csv
target_observation_table.csv
decoder_manifest.csv
decoder_policy_manifest.csv
decoder_table.csv
threshold_manifest.csv
recoverability_by_distinction.csv
declared_target_policy_summary.csv
asymmetry_summary_by_channel.csv
confusion_matrix_by_distinction.csv
non_erasure_requirement_manifest.csv
non_erasure_by_channel.csv
marginal_joint_recoverability_diagnostic.csv
channel_baseline_manifest.csv
channel_baseline_comparison.csv
channel_composition_manifest.csv
composed_channel_matrix.csv
composition_recoverability_check.csv
support_relation.csv
support_recoverability.csv
support_vs_probability_summary.csv
theorem_transfer_readiness_summary.csv
channel_row_stochastic_audit.csv
distinction_partition_audit.csv
decoder_totality_audit.csv
threshold_application_audit.csv
formal_channel_consumption_bundle.json
stochastic_channel_probe_report.md
```

The report must start with a very short executive summary.

## Implemented Channel Families

```text
identity
total erasure
coordinate projections
independent bit flip
asymmetric bit noise
asymmetric bit erasure
marginal-preserving joint-degrading one-bit shuffle
output-marginal matched uniform baseline
deterministic entropy-matched random-like baseline
two cascaded composition channels
```

## Pass Criteria

```text
all required carriers emitted
all required distinctions emitted
all channel rows stochastic
support projection emitted
decoders emitted and total over target labels
recoverability rows emitted
non-erasure rows emitted
marginal/joint diagnostic emitted
baseline comparisons emitted
composition checks emitted
report emitted with executive summary
no semantic promotion
```

## Completed Command

```powershell
.\.venv\Scripts\python.exe -m omega.stochastic_distinction_channel.probe `
  --out results\stochastic_distinction_channel\20260603_stochastic_channel_probe_v0 `
  --csv-output-mode plain
```

Current tightening command:

```powershell
.\.venv\Scripts\python.exe -m omega.stochastic_distinction_channel.probe `
  --out results\stochastic_distinction_channel\20260604_stochastic_channel_probe_v0_fixed_policy `
  --csv-output-mode plain
```

## Claim Boundary

Allowed:

```text
finite stochastic channel construction
declared distinction recovery or non-recovery under named decoders
support-level exact recovery comparison against probabilistic decoder success
marginal-versus-joint finite channel diagnostics
```

Blocked:

```text
Omega validation
proto-valuer / valuer detection
agency
identity
value
compatibility detection
support / capture / erasure in the ethical or Omega sense
maintenance gap
identity-decay null
substrate-general validation
```
