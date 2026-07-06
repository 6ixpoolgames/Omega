# Relational Composability Report v0

Status: retained finite coupling-instrument report
Scope: declared compatibility profiles after fixed individual vector census and pure span
Claim boundary: not value, not standing, not agency, not plurality theory, not population ethics, not aggregation, not population optimum, not Omega validation

## Protocol

Protocol note:

```text
docs/research_notes/omega_theory/relational_composability_protocol_v0.md
```

Validation command:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_composability --out-root docs\research_notes\validation_results\relational_composability_v0
```

Retained run:

```text
docs/research_notes/validation_results/relational_composability_v0/20260707_012053/
```

Hardening retained run:

```text
docs/research_notes/validation_results/relational_composability_v01/20260707_013446/
```

Retained files:

```text
summary.json
control_comparison.csv
compatibility_profiles.csv
report.md
```

## Verdict

```text
separated
```

The retained finite witness separates declared compatibility profiles while
holding the individual vector census and pure span fixed.

More precise v0 claim language:

```text
registered compatibility-profile separation
```

Relational Composability v0 does not derive compatibility from individual
profiles. It shows that once coupling data is registered, full individual
profiles and pure span do not determine the joint compatibility profile.

This makes explicit coupling data a live joint-tier instrument. It does not
prove population value, standing, plurality theory, aggregation, or a
population optimum.

## Candidate Pair

Axes:

```text
A, B
```

Held-fixed individual vectors:

```text
vA = A
vB = B
```

Compatible ensemble:

```text
compatible_pair_AB:
  compatible_pairs = {(vA, vB)}
```

Blocked ensemble:

```text
blocked_pair_AB:
  compatible_pairs = {}
```

Matched controls:

```text
marginal scalar controls equal: true
full vector census equal: true
pure span equivalent: true
span rank separates: false
```

Compatibility separation:

```text
compatible pair count: 1 vs 0
max compatible component size: 2 vs 1
all vectors jointly compatible: true vs false
```

## Graph-Structure Robustness

The v0.1 hardening witness keeps simple graph summaries fixed:

```text
same full vector census;
same pure span;
same compatible-pair count;
same degree sequence;
different component structure.
```

Two-triangles ensemble:

```text
two_triangles_same_degree
component sizes = [3, 3]
edge count = 6
degree sequence = [2, 2, 2, 2, 2, 2]
```

Six-cycle ensemble:

```text
six_cycle_same_degree
component sizes = [6]
edge count = 6
degree sequence = [2, 2, 2, 2, 2, 2]
```

This prevents the v0 result from reducing to pair-count or degree-sequence
summaries.

## Negative Control

The retained negative control duplicates the compatible pair with the same
full vector census and the same compatibility relation.

Result:

```text
same full vector census + same coupling -> same compatibility profile
```

This prevents the instrument from overclaiming. The separation requires
registered coupling data; pure span alone cannot supply it.

## Register Liability

Compatibility relations are registered structure:

```text
undeclared compatibility is invisible;
overdeclared compatibility can counterfeit composability;
corrupted compatibility can create phantom composability;
adapter choice controls what the instrument can see.
```

This is the coupling-layer analogue of recovery-register liability. A
compatibility edge is not morally or ontologically given merely because it is
present in the registered relation.

## Implementation Surface

Adapter:

```text
omega/adapters/finite_relational/relational_composability.py
```

Validation:

```text
omega/validation/finite_relational_composability.py
```

Tests:

```text
tests/test_finite_relational_composability.py
```

Core functions:

```text
compatibility_profile
compare_coupled_ensembles
compatible_vs_blocked_witness
identical_coupling_control
relational_composability_summary
```

Future typed-coupling labels should remain declared labels, not moral labels:

```text
repair-compatible;
translation-compatible;
co-learning-compatible;
joint-corridor-compatible;
interference;
capture-risk;
redundancy.
```

## Nonclaims

This report does not claim:

```text
value;
standing;
agency;
plurality theory;
population ethics;
aggregation;
population optimum;
Omega validation.
```

## Next Steps

The next possible directions are:

```text
1. typed relation labels, not only binary edges;
2. corridor/recovery-linked compatibility instead of declared-only edges;
3. phantom-composability witness for corrupted coupling registers;
4. NOLP / CompensationClaim after span and coupling instruments are audited;
5. plurality theory only after coupling is tied to corridor dynamics.
```

Do not use this result to rank populations or patients. It is a finite
instrument showing that full individual vector data can still leave declared
joint compatibility open.

## Public Compression

Relational Composability v0 is registered compatibility-profile separation:
same individual vectors and pure span can still leave declared joint
compatibility open. It is a finite coupling instrument beyond ensemble span,
not a theory of value or plurality.
