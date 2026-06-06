# Registry-First Stochastic Channel Probe X3 v0

## Executive Summary

This staged carrier-size pass increases the finite channel carrier from X2 to X3 while keeping registry-first provenance and retained path evidence. It uses exact finite recovery criteria instead of brute-force decoder search.

- registry digest: `04d7e4966300f0b823be24bf`
- manifest bundle digest: `963969f9025c172447f53735`
- channel panel digest: `989ada7432d0852e02e1df77`
- scored outputs digest: `d7e1060ddae6ed60dd552bf0`
- registered vs existence gaps: 13
- registered vs optimized gaps: 21

## Scope

finite registry-first X3 stochastic channel probe; provenance gap measurement only

## Registry Controls

- `reg_empty_D_joint_E_joint`: `empty_registry_control`

## Provenance Gap Classes

- `declared_registered_recovery_ready`: 36
- `existence_capacity_only`: 13
- `not_recovered`: 63
- `optimized_diagnostic_only`: 8

## Cascade Evidence

- `D_A`: composite 0 <= 0 + 0 (`path_rows_retained`)
- `D_B`: composite 8 <= 0 + 8 (`path_rows_retained`)
- `D_C`: composite 0 <= 0 + 0 (`path_rows_retained`)

## Theorem-Transfer Readiness

- `support_exact_capacity_ready`: `ready` (existence_capacity)
- `registered_recovery_ready`: `ready` (registered)
- `declared_registered_recovery_ready`: `ready` (declared_registered)
- `probability_measurement_ready`: `ready` (measurement)
- `cascade_union_bound_ready`: `ready` (declared_registered)
- `policy_substitution_blocked`: `ready` (audit_guard)
- `optimized_diagnostic_only`: `ready` (optimized_diagnostic)
- `substrate_bridge_ready`: `not_ready` (not_applicable)

## Read

This result tests carrier-size scaling of the registry-first protocol. Optimized rows remain diagnostic, and substrate bridge readiness remains out of scope for this finite presentation probe.