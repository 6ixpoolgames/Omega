# Same Chain Evidence, Different Class Soundness Witness

Witness ID: `same_chain_evidence_different_class_soundness_v0`

Status: `same_chain_evidence_different_class_soundness`

## Controlled Baseline

```text
baseline_controls_matched: True
proposed_class_count: 2
fragment_count: 6
```

Both proposed classes have the same member count, the same declared adjacent
chain-edge count, the same internal-pair count, and a declared connected chain.

## Class Soundness

```text
valid_class_id: valid_triangle_class
invalid_class_id: invalid_chain_class
valid_class_declared_chain_edges_pass: True
invalid_class_declared_chain_edges_pass: True
valid_class_sound: True
invalid_class_sound: False
invalid_class_unsound_pair_count: 1
```

## Read

Declared chain evidence does not determine full class soundness against an
exact merge profile. Connectedness is not a substitute for pairwise
consequence compatibility.

## Not Claimed

```text
transitivity
identity detection
cluster validity
value detection
agency detection
Omega validation
substrate-general class validity
```
