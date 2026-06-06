# Stochastic Registry-First Probe Medium Result

Date: 2026-06-06
Module: `omega.stochastic_distinction_channel.registry_first_probe`
Panel: `medium`

## Executive Summary

The medium registry-first pass keeps the same 4-state finite channel substrate
but expands the channel panel from 5 to 13 deterministic/natural-weight
channels. This increases the provenance gap surface while preserving the key
discipline: registries, requirement sets, and thresholds are frozen and hashed
before scoring, and cascade evidence is retained as path rows.

Output:

```text
results/stochastic_distinction_channel/20260606_registry_first_probe_medium_v0/
```

## Run Summary

```text
overall_status: registry_first_theorem_transfer_ready
panel: medium
channel_count: 13
registered_rows: 91
provenance_gap_rows: 91
registry_digest: 7339316e1efaa9778c963da5
manifest_bundle_digest: d352e73c5ba844a3ed4ae68a
cascade_evidence_status: path_rows_retained
output_size: ~146 KB
adversarial_audit_status: PASS
adversarial_audit_rows: 67
```

Gap classes:

```text
declared_registered_recovery_ready: 26
existence_capacity_only: 11
optimized_diagnostic_only: 6
not_recovered: 48
```

The registry digest matches the tiny run because the pre-score registry,
requirements, and thresholds are unchanged. The probe digest differs through
the scored channel panel and row counts.

## Medium Channels Added

```text
b_preserved_a_erased_channel
a_flip_noise_9_1_channel
b_flip_noise_3_1_channel
independent_bit_noise_81_9_9_1_channel
parity_preserved_scramble_channel
joint_cycle_channel
swap_bits_channel
copy_a_to_b_channel
```

These add policy/provenance stress cases without enlarging the carrier:
deterministic relabeling, bit swapping, asymmetric projection, parity-preserved
joint scrambling, and graded natural-weight noise.

## Readiness Vector

```text
support_exact_capacity_ready: ready
registered_recovery_ready: ready
declared_registered_recovery_ready: ready
probability_measurement_ready: ready
cascade_union_bound_ready: ready
policy_substitution_blocked: ready
optimized_diagnostic_only: ready
substrate_bridge_ready: not_ready
```

## Adversarial Provenance Audit

Audit output:

```text
results/stochastic_distinction_channel/20260606_registry_first_probe_medium_adversarial_audit_v0/
```

The audit verifies:

```text
required artifacts are present
pre-score artifact digests match current files
scored artifact digests match current files
scored rows carry the frozen registry and manifest digests
optimized rows remain diagnostic only
cascade readiness has retained path evidence
```

Result:

```text
overall_status: PASS
audit_rows: 67
failure_count: 0
```

The generator now emits:

```text
manifest_digest_chain.json
```

so post-run mutation of registry, requirement, threshold, scored-row, or path
evidence artifacts is detectable from retained files.

## Read

This confirms the probe does not need to remain tiny, but the useful scaling
axis here is controlled channel breadth, not larger state carriers yet. The
medium panel produces more recovery-provenance gaps while preserving exact
natural-weight semantics and retained path evidence.

The strongest next empirical move is a staged carrier-size increase only after
we keep the same digest/order/path-evidence guarantees.
