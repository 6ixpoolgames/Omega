# Generated Continuation Dynamics v0 Report

Status: PASS
Verdict: retained
Protocol: `docs/research_notes/omega_v2/generated_continuation_dynamics_protocol_v0.md`

## Case Results

- GN1_manifest: True
- GN2_downward_closure: True
- GN3_generated_nonflag: True
- GN4_matched_filled_control: True
- GN5_independent_action_negative_control: True
- GN6_relabeling: True
- GN7_deadlock: True
- GN8_lushness_bridge: True
- DD1_manifest: True
- DD2_distributions: True
- DD3_relabeling: True
- DD4_duplicate_weighting: True
- DD5_classifier_controls: True
- DD6_horizon_rows: True
- DD7_no_synthetic_reverse_edges: True

## Generated Joint Compatibility

- Exhaustive assignments: 216
- Hollow assignments: 24
- Filled assignments: 102
- Matched filled controls: 24
- Downward-closure failures: 0
- Kernel/intersection correspondence failures: 0

### Retained hollow witness

- Allowed actions: `{"A": ["a0", "a1"], "B": ["a0", "a2"], "C": ["a1", "a2"]}`
- Maximal faces: `[['A', 'B'], ['A', 'C'], ['B', 'C']]`
- One-skeleton: `[['A', 'B'], ['A', 'C'], ['B', 'C']]`
- Flag: False

### Matched filled control

- Allowed actions: `{"A": ["a0", "a1"], "B": ["a0", "a2"], "C": ["a0", "a3"]}`
- Maximal faces: `[['A', 'B', 'C']]`
- One-skeleton: `[['A', 'B'], ['A', 'C'], ['B', 'C']]`
- Flag: True

- Independent-action triple viable: True
- Relabeling preserved: True
- Deadlock singleton viable: False
- Derived-face bridge exact: True

The maximal faces above are outputs of shared-action greatest fixed-point computations. They were not supplied to the search.

## Generated Deformation Distributions

- Complete systems: 5832
- Reversible systems: 288
- Absorbing systems: 440

| Class | h | Expansion | Contraction | Mixed | Equivalent |
|---|---:|---:|---:|---:|---:|
| complete | 0 | 0.166667 | 0.166667 | 0.000000 | 0.666667 |
| complete | 1 | 0.148148 | 0.148148 | 0.088889 | 0.614815 |
| complete | 2 | 0.137654 | 0.138066 | 0.111111 | 0.613169 |
| reversible | 0 | 0.166667 | 0.166667 | 0.000000 | 0.666667 |
| reversible | 1 | 0.141667 | 0.141667 | 0.116667 | 0.600000 |
| reversible | 2 | 0.125000 | 0.133333 | 0.141667 | 0.600000 |
| absorbing | 0 | 0.142570 | 0.142570 | 0.000000 | 0.714859 |
| absorbing | 1 | 0.138554 | 0.152610 | 0.036145 | 0.672691 |
| absorbing | 2 | 0.138554 | 0.152610 | 0.036145 | 0.672691 |

Primary rows count each unique `(source,target)` edge once per system. Per-system means and action-edge diagnostics are retained in the CSV output.

## Sensitivity

- Deformation relabeling preserved: True
- Duplicate action preserved structural verdicts: True
- Duplicate action changed diagnostic action weights: True
- Synthetic reverse edge excluded: True
- Retained classifier verdicts: ['contraction', 'equivalent', 'expansion', 'mixed']

## Evidence Classification

Generator counts, closure, relabeling, deadlock, duplicate-action, and reverse-edge cases are correctness controls.

The hollow/filled pair is a constructive strictness witness: pairwise continuation compatibility does not imply joint continuation compatibility.

The deformation frequencies are risky generated results relative to each declared class and horizon. No pooled frequency is a universal probability.

## Claim Boundary

Graph direction is not a thermodynamic orientation. The absorbing class is not an entropy model, and the reversible class is only a finite structural null. This pass does not prove value, agency, lushness, or Omega.
