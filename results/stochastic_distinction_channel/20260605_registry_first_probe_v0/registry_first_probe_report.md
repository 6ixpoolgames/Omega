# Registry-First Stochastic Channel Probe v0

## Executive Summary

This run freezes declared decoder registries, requirement sets, and thresholds before scoring finite stochastic channels. It then separates declared registry recovery from existence-style channel capacity and optimized diagnostics. The useful object is the gap: a channel can contain recoverable information while a declared registry fails to recover it.

- registry digest: `7339316e1efaa9778c963da5`
- manifest bundle digest: `d352e73c5ba844a3ed4ae68a`
- registered vs existence gaps: 4
- registered vs optimized gaps: 4

## Scope

finite registry-first stochastic channel probe; provenance gap measurement only

## Generation Order

Carriers, distinctions, requirement sets, thresholds, and declared decoder registries are emitted before scoring. `registry_digest.json` records the frozen registry bytes and every scored row carries the digest.

## Registry Controls

- `reg_empty_D_joint_E_joint`: `empty_registry_control`

## Provenance Gap Examples

- `a_preserved_b_erased_channel` / `reg_bad_declared_D_A_E_A`: registered=0, existence=1, optimized=1 -> `existence_capacity_only`
- `a_preserved_b_erased_channel` / `reg_empty_D_joint_E_joint`: registered=0, existence=0, optimized=0 -> `not_recovered`
- `b_flip_noise_9_1_channel` / `reg_bad_declared_D_A_E_A`: registered=0, existence=1, optimized=1 -> `existence_capacity_only`
- `b_flip_noise_9_1_channel` / `reg_empty_D_joint_E_joint`: registered=0, existence=0, optimized=0 -> `not_recovered`
- `collapse_to_00_channel` / `reg_bad_declared_D_A_E_A`: registered=0, existence=0, optimized=0 -> `not_recovered`
- `collapse_to_00_channel` / `reg_empty_D_joint_E_joint`: registered=0, existence=0, optimized=0 -> `not_recovered`
- `identity_channel` / `reg_bad_declared_D_A_E_A`: registered=0, existence=1, optimized=1 -> `existence_capacity_only`
- `identity_channel` / `reg_empty_D_joint_E_joint`: registered=0, existence=1, optimized=1 -> `existence_capacity_only`
- `parity_projector_channel` / `reg_bad_declared_D_A_E_A`: registered=0, existence=0, optimized=0 -> `not_recovered`
- `parity_projector_channel` / `reg_empty_D_joint_E_joint`: registered=0, existence=0, optimized=0 -> `not_recovered`

## Cascade Evidence

- `D_A`: composite 0 <= 0 + 0 (`path_rows_retained`)
- `D_B`: composite 4 <= 0 + 4 (`path_rows_retained`)

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

Positive declared-registry rows can be used as declared recovery evidence. Existence-only rows are capacity evidence. Optimized rows are diagnostic. The empty-registry and bad-declared-decoder controls intentionally fail so those evidence classes cannot collapse into each other.