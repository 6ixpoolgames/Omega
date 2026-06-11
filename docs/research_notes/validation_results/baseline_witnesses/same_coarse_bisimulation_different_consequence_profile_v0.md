# Same Coarse Bisimulation, Different Consequence Profile Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_coarse_bisimulation_different_consequence_profile`
Witness ID: `same_coarse_bisimulation_different_consequence_profile_v0`

## Executive Summary

This baseline-controlled witness packages the panel-sensitivity guardrail:
a coarse behavioral partition does not determine every declared consequence
profile.

It uses one four-state identity-transition system:

```text
states: 00, 01, 10, 11
coarse panel: all states emit unit observation
coarse partition: one block containing all states
```

It then compares two declared expanded panels:

```text
declared_d_expanded_panel:
  same d allows merge
  different d blocks merge

declared_n_expanded_panel:
  same n allows merge
  different n blocks merge
```

The expanded panels match on state count, transition-edge count, coarse
partition signature, expanded pair count, allowed-pair count, and blocked-pair
count. They differ on the actual allowed and blocked pair signatures.

## Retained Output

```text
results/baseline_witnesses/20260611_same_coarse_bisimulation_different_consequence_profile_v0/
```

Expected artifacts:

```text
state_manifest.csv
panel_manifest.csv
transition_edges.csv
coarse_partition.csv
exact_profile_pairs.csv
baseline_comparison.csv
profile_difference.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_coarse_bisimulation_different_consequence_profile
carrier_id: X2_dn_identity_transition
state_count: 4
transition_edge_count: 4
coarse_panel_id: coarse_unit_observation
coarse_partition_signature: coarse_all_states:00;01;10;11
baseline_controls_matched: true
expanded_profile_counts_matched: true
expanded_profile_signatures_differ: true
declared_d_allowed_pair_signature: 00,01;10,11
declared_n_allowed_pair_signature: 00,10;01,11
declared_d_blocked_pair_signature: 00,10;00,11;01,10;01,11
declared_n_blocked_pair_signature: 00,01;00,11;01,10;10,11
baseline_rows_digest: 6a5d75e4fa148a4867d615ca
profile_rows_digest: 7dcc7a657d36918f670cbbb9
profile_difference_rows_digest: 1e728176cdc89ae3af298e4d
summary_digest: c0d75cca5cd452cd16b6aa15
```

## Read

The same coarse bisimulation-style partition does not determine the exact
consequence profile under a declared expanded panel.

This does not make arbitrary panel selection valid. It only shows that panel
declaration is load-bearing.

## Validation

Focused test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_same_coarse_bisimulation_different_consequence_profile.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_coarse_bisimulation_different_consequence_profile --out results\baseline_witnesses\20260611_same_coarse_bisimulation_different_consequence_profile_v0
```

## Not Claimed

This witness does not claim:

```text
arbitrary post-hoc panel validity;
global identity;
bisimulation novelty;
value detection;
agency detection;
Omega validation;
substrate-general panel validity.
```
