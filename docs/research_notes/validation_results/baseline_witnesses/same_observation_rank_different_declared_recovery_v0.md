# Same Observation Rank, Different Declared Recovery Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_observation_rank_different_declared_recovery`
Witness ID: `same_observation_rank_different_declared_recovery_v0`

## Executive Summary

This is a baseline-controlled witness for the observability / controllability
row in `docs/KNOWN_REDUCTIONS_AND_BASELINES.md`.

It constructs two deterministic one-bit observers over the same four-state
carrier:

```text
state = (d, n)
declared source distinction = d
observer output = one binary bit
```

The first observer emits `d`. The second observer emits nuisance bit `n`.

Both observers have:

```text
same state count;
same output support;
same finite observation rank;
same observation block count;
same observation block-size signature;
same output-to-state count signature;
same deterministic-observer status.
```

They differ on declared recovery:

```text
observe_declared_d: declared recovery passes
observe_nuisance_n: declared recovery fails
```

## Retained Output

```text
results/baseline_witnesses/20260611_same_observation_rank_different_declared_recovery_v0/
```

Expected artifacts:

```text
state_manifest.csv
observer_manifest.csv
output_manifest.csv
observation_mapping.csv
observability_baseline_by_observer.csv
declared_recovery_by_observer.csv
baseline_comparison.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_observation_rank_different_declared_recovery
carrier_id: X2_dn_observation_panel
state_count: 4
observer_count: 2
finite_observation_rank: 1
baseline_controls_hold: true
all_expected_relations_hold: true
declared_observer_id: observe_declared_d
nuisance_observer_id: observe_nuisance_n
declared_observer_exact_declared_recovery: true
nuisance_observer_exact_declared_recovery: false
baseline_rows_digest: dcaa455b0718c37ec9191f37
recovery_rows_digest: 6440c0d202af9ecb3dd73dec
comparison_rows_digest: a7b23234093e28265a091b2a
summary_digest: 3c98a5592d7787c2ac9f875e
```

## Read

Finite observation-rank and partition-shape summaries do not determine
declared distinction recovery.

This does not show that observability or controllability are useless. It shows
that this finite rank/partition summary and declared recovery are different
claims.

## Validation

Focused test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_same_observation_rank_different_declared_recovery.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_observation_rank_different_declared_recovery --out results\baseline_witnesses\20260611_same_observation_rank_different_declared_recovery_v0
```

## Not Claimed

This witness does not claim:

```text
full linear observability;
control synthesis;
semantic recovery;
value detection;
agency detection;
identity detection;
Omega validation;
substrate-general theory validation.
```
