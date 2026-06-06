# Stochastic Registry-First Probe X3 Result

Date: 2026-06-06
Module: `omega.stochastic_distinction_channel.registry_first_x3_probe`
Carrier: `X3`

## Executive Summary

This staged carrier-size pass moves the registry-first stochastic-channel probe
from two binary coordinates to three binary coordinates. It keeps the same
contract as the X2 probe: decoder registries, requirement sets, and thresholds
are frozen and hashed before scoring; scored rows carry frozen digests; optimized
rows remain diagnostic; and cascade theorem transfer requires retained path
evidence.

Output:

```text
results/stochastic_distinction_channel/20260606_registry_first_probe_x3_v0/
```

Adversarial audit:

```text
results/stochastic_distinction_channel/20260606_registry_first_probe_x3_adversarial_audit_v0/
```

## Run Summary

```text
overall_status: registry_first_theorem_transfer_ready
carrier_id: X3
state_count: 8
channel_count: 15
registered_rows: 120
provenance_gap_rows: 120
registry_digest: 04d7e4966300f0b823be24bf
manifest_bundle_digest: 963969f9025c172447f53735
channel_panel_digest: 989ada7432d0852e02e1df77
scored_outputs_digest: d7e1060ddae6ed60dd552bf0
cascade_evidence_status: path_rows_retained
output_size: ~273 KB
```

Gap classes:

```text
declared_registered_recovery_ready: 36
existence_capacity_only: 13
optimized_diagnostic_only: 8
not_recovered: 63
```

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

Result:

```text
overall_status: PASS
audit_rows: 105
failure_count: 0
```

The retained audit verifies digest-chain completeness, scored-row registry and
manifest digests, optimized-policy containment, and retained path evidence for
cascade theorem transfer.

## Read

The carrier-size increase did not break the registry-first discipline or the
adversarial audit. The useful readout remains the provenance gap surface:
declared registry recovery, existence/capacity recovery, and optimized
diagnostic recovery stay separate at the artifact level.

The next empirical step can increase breadth or carrier size further, but only
under the same rule: no theorem-transfer row without frozen registry provenance
and retained or losslessly reconstructible path evidence.
