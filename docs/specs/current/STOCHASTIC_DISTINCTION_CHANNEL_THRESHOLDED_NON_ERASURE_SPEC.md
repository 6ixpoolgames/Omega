# Stochastic Distinction Channel Thresholded Probabilistic Non-Erasure Spec

Status: implemented 2026-06-04
Target package: `omega.stochastic_distinction_channel`
Module: `omega.stochastic_distinction_channel.thresholded_non_erasure`
Primary input: `results/stochastic_distinction_channel/20260604_stochastic_channel_theorem_transfer_audit_v0/`
Secondary input: `results/stochastic_distinction_channel/20260604_stochastic_channel_probe_v0_fixed_policy/`

## Purpose

Compile existing stochastic-channel outputs into finite thresholded
probabilistic non-erasure artifacts over declared requirement sets.

The formal target is:

```text
ProbNonErasing(K, pi, Req, threshold, target_policy)
```

where a channel is thresholded-probabilistically non-erasing for `Req` when
every required source distinction has an allowed decoder whose success
probability meets or exceeds the declared threshold under the declared prior.

This is a formal-consumption pass over retained outputs, not a new channel
sweep.

## Namespace Discipline

Allowed formal terms include:

```text
support
exact_support
non_erasure
thresholded_non_erasure
requirement_set
recovery
distinction
decoder
target_policy
```

Reserved interpretation terms should not appear as primary measurement claims:

```text
identity
agency
value
valuer
compatibility
capture
ethical_erasure
Omega_validation
```

This is namespace discipline, not a ban on formal vocabulary.

## Inputs

From the theorem-transfer audit:

```text
probabilistic_channel_theorem_transfer_bundle.json
no_self_evidencing_decoder_audit.csv
support_probability_theorem_boundary.csv
probabilistic_theorem_transfer_readiness_summary.csv
```

From the fixed-policy probe:

```text
channel_probe_manifest.json
artifact_manifest.json
channel_manifest.csv
distinction_manifest.csv
decoder_manifest.csv
decoder_policy_manifest.csv
decoder_table.csv
threshold_manifest.csv
recoverability_by_distinction.csv
non_erasure_requirement_manifest.csv
non_erasure_by_channel.csv
marginal_joint_recoverability_diagnostic.csv
declared_target_policy_summary.csv
```

Missing required inputs produce:

```text
thresholded_non_erasure_status: blocked_missing_input
```

## Requirement Sets

Emit:

```text
probabilistic_requirement_manifest.csv
requirement_subset_manifest.csv
```

Declared sets:

```text
req_A: D_A
req_B: D_B
req_marginals: D_A, D_B
req_joint: D_joint
req_parity: D_parity
req_joint_and_parity: D_joint, D_parity
req_all_nontrivial: D_A, D_B, D_joint, D_parity
```

`semantic_status` must be:

```text
finite_distinction_requirement_only
```

## Thresholds

Emit:

```text
probabilistic_threshold_manifest.csv
```

Thresholds:

```text
0.80
0.90
0.95
0.99
1.00
```

No single threshold is treated as the only truth.

## Target-Policy And Decoder Eligibility

Emit:

```text
prob_non_erasure_decoder_eligibility.csv
```

The fixed-declared target policy is the default formal-consumption target.
Bayes-best target policy is emitted diagnostically unless the formal arm later
declares a Bayes-best theorem-transfer object.

This distinction is about target policy, not decoder kind. Fixed-declared target
rows may use Bayes-optimal decoders over the fixed declared target observation.

Allowed recovery decoders must consume target-observation labels only. Source
state IDs, source distinction labels, hidden states, and candidate IDs are
oracle inputs for this purpose.

## Core Outputs

Emit:

```text
thresholded_prob_recovery_by_distinction.csv
thresholded_prob_non_erasure_by_channel.csv
prob_non_erasure_monotonicity_check.csv
threshold_sensitivity_by_requirement.csv
thresholded_marginal_joint_summary.csv
thresholded_support_probability_boundary.csv
probabilistic_non_erasure_theorem_transfer_summary.csv
thresholded_prob_non_erasure_bundle.json
thresholded_prob_non_erasure_report.md
```

## Predictive/Revelatory Fixtures

The pass should expose these expected finite-channel facts:

```text
identity_channel + req_all_nontrivial + threshold_1_00:
  fixed policy passes

bit_flip_p_0_05 + req_marginals + threshold_0_95:
  fixed policy passes probabilistically without exact support

bit_flip_p_0_05 + req_joint + threshold_0_95:
  fixed policy fails below threshold

total_erasure_channel + req_joint + threshold_0_80:
  fixed policy blocks because no fixed declared target exists on Y_star

if req_all_nontrivial passes, req_marginals must pass
```

Monotonicity failures indicate an instrumentation or requirement-set construction
bug unless the row is explicitly blocked.

## Command

```powershell
.venv\Scripts\python.exe -m omega.stochastic_distinction_channel.thresholded_non_erasure --audit-source results\stochastic_distinction_channel\20260604_stochastic_channel_theorem_transfer_audit_v0 --probe-source results\stochastic_distinction_channel\20260604_stochastic_channel_probe_v0_fixed_policy --out results\stochastic_distinction_channel\20260604_thresholded_prob_non_erasure_v0
```

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_stochastic_distinction_channel.py tests\test_stochastic_theorem_transfer_audit.py tests\test_stochastic_thresholded_non_erasure.py -q

.venv\Scripts\python.exe -m compileall omega\stochastic_distinction_channel tests\test_stochastic_thresholded_non_erasure.py
```
