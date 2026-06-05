# Stochastic Registry-First Probe Result

Date: 2026-06-05
Branch: stochastic distinction-channel empirical-formal bridge
Module: `omega.stochastic_distinction_channel.registry_first_probe`

## Executive Summary

This tiny deterministic pass freezes decoder registries, requirement sets, and
thresholds before scoring. It then separates three recovery surfaces:

```text
declared registry recovery:
  a supplied declared decoder registry works

existence recovery:
  some decoder exists for exact support recovery

optimized diagnostic recovery:
  the best available target/decoder choice works or scores best
```

The useful result is the gap table. Identity-channel controls show that a
recoverable distinction can be present while an empty registry or a bad declared
decoder fails. That makes the provenance split operational rather than only
formal.

## Local Artifacts

Output:

```text
results/stochastic_distinction_channel/20260605_registry_first_probe_v0/
```

Primary report:

```text
registry_first_probe_report.md
```

Formal bundle:

```text
registry_first_formal_consumption_bundle.json
```

## Run Summary

```text
overall_status: registry_first_theorem_transfer_ready
registry_digest: 7339316e1efaa9778c963da5
manifest_bundle_digest: d352e73c5ba844a3ed4ae68a
registered_rows: 35
provenance_gap_rows: 35
registered_vs_existence_gaps: 4
registered_vs_optimized_gaps: 4
cascade_evidence_status: path_rows_retained
```

## Key Controls

Identity-channel provenance examples:

| Registry | Registered | Existence | Optimized | Read |
|---|---:|---:|---:|---|
| `reg_declared_D_joint_E_joint` | 1 | 1 | 1 | declared registry succeeds |
| `reg_bad_declared_D_A_E_A` | 0 | 1 | 1 | declared decoder fails despite capacity |
| `reg_empty_D_joint_E_joint` | 0 | 1 | 1 | empty registry fails despite capacity |

This blocks the shortcut:

```text
some decoder exists = declared instrument recovered
```

## Cascade Evidence

The cascade evidence object is retained as rows, not only as summary rates:

```text
path_ensemble_rows.csv
cascade_evidence_summary.csv
```

Summary:

```text
D_A: composite 0 <= 0 + 0
D_B: composite 4 <= 0 + 4
```

Both rows use `cascade_evidence_status = path_rows_retained`, so they are
eligible for the finite cascade union-bound theorem surface.

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

The important operational rule is now explicit: optimized rows remain
diagnostic and do not substitute for declared registry recovery.

## Verification

```text
.venv\Scripts\python.exe -m pytest tests\test_stochastic_registry_first_probe.py -q
  4 passed

.venv\Scripts\python.exe -m omega.stochastic_distinction_channel.registry_first_probe --out results\stochastic_distinction_channel\20260605_registry_first_probe_v0
  registry_first_theorem_transfer_ready
```

## Next Recommendation

Use this as the empirical template for future stochastic-channel probes: freeze
registries before scoring, retain or reconstruct path evidence, and report
registered/existence/optimized gaps as first-class outputs.
