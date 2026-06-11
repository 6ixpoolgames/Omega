# Same Intervention Effect, Different Declared Recovery Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_intervention_effect_different_declared_recovery`
Witness ID: `same_intervention_effect_different_declared_recovery_v0`

## Executive Summary

This is a baseline-controlled witness for the causal abstraction /
intervention row in `docs/KNOWN_REDUCTIONS_AND_BASELINES.md`.

It constructs two deterministic intervention systems over the same four-state
carrier:

```text
source state = (d, n)
interventions = set_effect_0, set_effect_1
declared source distinction = d
declared effect observation = target_effect_bit
declared recovery observation = target_recovery_bit
```

Both systems implement the same declared intervention effect:

```text
set_effect_0 -> target_effect_bit = 0
set_effect_1 -> target_effect_bit = 1
```

They also match transition edge count, target support, target support by
intervention, and target count by intervention. They differ on declared
post-intervention recovery:

```text
effect_with_declared_d_carried: declared recovery passes
effect_with_nuisance_n_carried: declared recovery fails
```

## Retained Output

```text
results/baseline_witnesses/20260611_same_intervention_effect_different_declared_recovery_v0/
```

Expected artifacts:

```text
state_manifest.csv
intervention_manifest.csv
system_manifest.csv
intervention_transition_edges.csv
intervention_effect_baseline_by_system.csv
declared_recovery_by_system.csv
baseline_comparison.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_intervention_effect_different_declared_recovery
carrier_id: X2_dn_intervention_panel
source_count: 4
intervention_count: 2
system_count: 2
baseline_controls_hold: true
all_expected_relations_hold: true
declared_system_id: effect_with_declared_d_carried
nuisance_system_id: effect_with_nuisance_n_carried
declared_system_exact_declared_recovery: true
nuisance_system_exact_declared_recovery: false
baseline_rows_digest: de055ea586a682e9d9f4899f
recovery_rows_digest: 14b3a3b817688f2a38ae5b6d
comparison_rows_digest: 51db6becb54f1e3fca2c5024
summary_digest: 5c0027abd4043f8ee3780c39
```

## Read

A matched declared intervention-effect summary does not determine declared
post-intervention recovery.

This does not show that causal abstraction or intervention analysis is useless.
It shows that this finite intervention-effect summary and declared recovery
are different claims.

## Validation

Focused test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_same_intervention_effect_different_declared_recovery.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_intervention_effect_different_declared_recovery --out results\baseline_witnesses\20260611_same_intervention_effect_different_declared_recovery_v0
```

## Not Claimed

This witness does not claim:

```text
causal discovery;
causal abstraction;
counterfactual semantics;
full intervention calculus;
semantic recovery;
value detection;
agency detection;
identity detection;
Omega validation;
substrate-general theory validation.
```
