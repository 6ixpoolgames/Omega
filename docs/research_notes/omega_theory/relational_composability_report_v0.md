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

## Negative Control

The retained negative control duplicates the compatible pair with the same
full vector census and the same compatibility relation.

Result:

```text
same full vector census + same coupling -> same compatibility profile
```

This prevents the instrument from overclaiming. The separation requires
registered coupling data; pure span alone cannot supply it.

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
1. larger coupling families with three or more vectors;
2. compatibility matrices with typed relation labels, not only binary edges;
3. NOLP / CompensationClaim after span and coupling instruments are audited;
4. plurality theory only after coupling is tied to corridor dynamics.
```

Do not use this result to rank populations or patients. It is a finite
instrument showing that full individual vector data can still leave declared
joint compatibility open.

## Public Compression

Relational Composability v0 separates two ensembles with identical individual
vectors and pure span by changing only the declared compatibility relation.
This is a first finite coupling instrument beyond ensemble span, not a theory
of value or plurality.
