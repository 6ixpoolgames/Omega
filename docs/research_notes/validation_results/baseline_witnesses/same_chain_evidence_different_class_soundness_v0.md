# Same Chain Evidence, Different Class Soundness Witness v0

Date: 2026-06-11
Module: `omega.baseline_witnesses.same_chain_evidence_different_class_soundness`
Witness ID: `same_chain_evidence_different_class_soundness_v0`

## Executive Summary

This baseline-controlled witness packages the class-level guardrail:
chain-connectedness is not full class soundness.

It constructs two proposed three-member classes. Both have:

```text
same member count;
same declared adjacent-chain-edge count;
same internal-pair count;
same declared chain connectedness;
all declared adjacent chain edges allowed by the exact profile.
```

The classes differ on the full internal-pair audit:

```text
valid_triangle_class:
  every internal pair is allowed

invalid_chain_class:
  adjacent chain pairs are allowed
  endpoint pair i0-i2 is blocked
```

## Retained Output

```text
results/baseline_witnesses/20260611_same_chain_evidence_different_class_soundness_v0/
```

Expected artifacts:

```text
fragment_manifest.csv
exact_profile_pairs.csv
class_manifest.csv
declared_chain_edges.csv
class_soundness_audit.csv
baseline_comparison.csv
witness_summary.json
witness_report.md
```

## Run Summary

```text
witness_status: same_chain_evidence_different_class_soundness
carrier_id: chain_vs_clique_triples
proposed_class_count: 2
fragment_count: 6
baseline_controls_matched: true
valid_class_id: valid_triangle_class
invalid_class_id: invalid_chain_class
valid_class_declared_chain_edges_pass: true
invalid_class_declared_chain_edges_pass: true
valid_class_sound: true
invalid_class_sound: false
valid_class_unsound_pair_count: 0
invalid_class_unsound_pair_count: 1
chain_rows_digest: bfd5d56e13b497a328dc855f
soundness_rows_digest: 040389d453098c5e61a8f98b
comparison_rows_digest: 1139c9ad69599eeb860d97f3
summary_digest: 1eb0060d4d305c924704eb7a
```

## Read

Declared chain evidence does not determine full class soundness against an
exact merge profile. Connectedness is not a substitute for pairwise
consequence compatibility.

## Validation

Focused test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_same_chain_evidence_different_class_soundness.py -q --basetemp .tmp\pytest -o cache_dir=.tmp\pytest_cache
```

Retained-output command:

```powershell
.venv\Scripts\python.exe -m omega.baseline_witnesses.same_chain_evidence_different_class_soundness --out results\baseline_witnesses\20260611_same_chain_evidence_different_class_soundness_v0
```

## Not Claimed

This witness does not claim:

```text
transitivity;
identity detection;
cluster validity;
value detection;
agency detection;
Omega validation;
substrate-general class validity.
```
