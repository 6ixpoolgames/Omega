# Same Viability Kernel, Different Declared Recovery Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_viability_kernel_different_declared_recovery`
Witness ID: `same_viability_kernel_different_declared_recovery_v0`

## Executive Summary

This is a baseline-controlled witness for the viability-kernel row in
`docs/KNOWN_REDUCTIONS_AND_BASELINES.md`.

It constructs two deterministic one-step systems over the same four-state
carrier:

```text
state = (d, n)
declared viability predicate = state first bit d = 1
declared source distinction = d
declared recovery observation = target_recovery_bit
```

Both systems have the same finite declared viability kernel:

```text
kernel states = 10;11
kernel size = 2
source-to-target viability signature = 00:0;01:0;10:1;11:1
```

They differ on declared recovery:

```text
kernel_with_declared_d_carried: declared recovery passes
kernel_with_nuisance_n_carried: declared recovery fails
```

## Retained Output

```text
results/baseline_witnesses/20260611_same_viability_kernel_different_declared_recovery_v0/
```

Expected artifacts:

```text
state_manifest.csv
system_manifest.csv
transition_edges.csv
viability_kernel_by_system.csv
declared_recovery_by_system.csv
baseline_comparison.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_viability_kernel_different_declared_recovery
carrier_id: X2_dn_viability_kernel
source_count: 4
system_count: 2
declared_viability_predicate: state first bit d = 1
viability_kernel_size: 2
viability_kernel_signature: 10;11
kernel_controls_hold: true
all_expected_relations_hold: true
declared_system_id: kernel_with_declared_d_carried
nuisance_system_id: kernel_with_nuisance_n_carried
declared_system_exact_declared_recovery: true
nuisance_system_exact_declared_recovery: false
kernel_rows_digest: de59919581579464b37d6a6e
recovery_rows_digest: abf1667ddf194bdfec0169dc
comparison_rows_digest: a6f3a599e1693dfcc202db6a
summary_digest: a4ab8b898777e19087e138ed
```

## Read

A matched finite viability-kernel summary does not determine declared recovery.

This does not show that viability kernels are useless. It shows that this
finite kernel summary and declared recovery are different claims.

## Validation

Focused test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_same_viability_kernel_different_declared_recovery.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_viability_kernel_different_declared_recovery --out results\baseline_witnesses\20260611_same_viability_kernel_different_declared_recovery_v0
```

## Not Claimed

This witness does not claim:

```text
real-world viability;
optimal control;
control synthesis;
semantic recovery;
value detection;
agency detection;
identity detection;
Omega validation;
substrate-general theory validation.
```
