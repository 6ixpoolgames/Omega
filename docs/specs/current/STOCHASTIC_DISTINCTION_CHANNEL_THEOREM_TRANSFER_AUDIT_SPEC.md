# Stochastic Distinction Channel Theorem-Transfer Audit Spec

Status: implemented 2026-06-04
Target package: `omega.stochastic_distinction_channel`
Module: `omega.stochastic_distinction_channel.theorem_transfer_audit`
Primary input: `results/stochastic_distinction_channel/20260604_stochastic_channel_probe_v0_fixed_policy/`

## Purpose

Compile the tightened stochastic-channel output into a formal-consumption audit
package for the Lean probabilistic channel presentation.

The audit checks whether the empirical artifacts can instantiate the finite
cascade theorem:

```text
composite decoder error over a finite channel cascade
<=
first-stage decoder error + second-stage decoder error
```

where all three error masses are measured on the same path ensemble:

```text
mass(x,y,z) = pi(x) * K(y|x) * L(z|y)
```

This is not a new channel sweep.

## Inputs

Required source artifacts include:

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
support_recoverability.csv
support_vs_probability_summary.csv
non_erasure_requirement_manifest.csv
non_erasure_by_channel.csv
marginal_joint_recoverability_diagnostic.csv
declared_target_policy_summary.csv
channel_composition_manifest.csv
composed_channel_matrix.csv
composition_recoverability_check.csv
theorem_transfer_readiness_summary.csv
formal_channel_consumption_bundle.json
channel_row_stochastic_audit.csv
distinction_partition_audit.csv
decoder_totality_audit.csv
threshold_application_audit.csv
```

Input must have:

```text
missing required artifacts: 0
channel row-stochastic audit failures: 0
distinction partition audit failures: 0
decoder totality audit failures: 0
threshold application audit failures: 0
```

## Required Outputs

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
stochastic_channel_theorem_transfer_audit_report.md
```

## Critical Rules

Use exact rational/natural weights where possible.

Do not use independently normalized stage errors as theorem-transfer evidence.
The denominator alignment audit must explicitly report whether first-stage,
second-stage, and composite errors share the same path ensemble.

Keep fixed-declared and Bayes-best decoder policies separate. Bayes-best rows
may be diagnostic, but must not silently replace a declared composable decoder
chain.

Allowed recovery decoders must consume declared target-observation labels only.
Source-state IDs, source distinction labels, hidden states, and candidate IDs
are oracle inputs for this purpose.

Separate exact support recovery from probabilistic recovery in all summaries.

## Pass Criteria

The audit passes if:

```text
all required inputs exist;
input audits pass;
natural-weight realization succeeds;
cascade path ensemble rows are emitted;
path totals equal generated composed-channel totals;
fixed-policy cascade bound rows pass;
same-denominator status is explicit;
decoder policy alignment is explicit;
no-self-evidencing audit passes;
support/probability theorem boundary table is emitted;
threshold sensitivity is emitted;
formal theorem-transfer bundle is emitted.
```

The audit fails or blocks if:

```text
composition bounds are claimed from independently normalized stage errors;
Bayes-best is silently substituted for fixed declared policy;
oracle decoder inputs are allowed for recovery claims;
support exactness and probabilistic success are collapsed;
missing values are treated as successes or failures without blocked status.
```

## Command

```powershell
.venv\Scripts\python.exe -m omega.stochastic_distinction_channel.theorem_transfer_audit --source results\stochastic_distinction_channel\20260604_stochastic_channel_probe_v0_fixed_policy --out results\stochastic_distinction_channel\20260604_stochastic_channel_theorem_transfer_audit_v0
```
