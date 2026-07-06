# Ensemble Span Report v0

Status: retained finite joint-tier instrument report
Scope: ensemble orientation/span after matched marginal scalar summaries
Claim boundary: not value, not standing, not agency, not population ethics, not aggregation, not relational surplus, not population optimum, not Omega validation

## Protocol

Protocol note:

```text
docs/research_notes/omega_theory/ensemble_span_protocol_v0.md
```

Validation command:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_ensemble_span --out-root docs\research_notes\validation_results\ensemble_span_v0
```

Retained run:

```text
docs/research_notes/validation_results/ensemble_span_v0/20260707_010015/
```

Retained files:

```text
summary.json
marginal_control_comparison.csv
span_profiles.csv
report.md
```

## Verdict

```text
separated
```

The retained finite witness separates redundant and orthogonal ensembles after
the declared marginal scalar controls are matched.

This makes ensemble orientation a live joint-tier instrument. It does not prove
population value, standing, aggregation, or relational surplus.

## Candidate Pair

Axes:

```text
A, B
```

Redundant ensemble:

```text
redundant_AA = {A, A}
```

Orthogonal ensemble:

```text
orthogonal_AB = {A, B}
```

Matched marginal scalar controls:

```text
valuer_count: 2 = 2
vector_dimension: 2 = 2
per_valuer_l1_norms: [1, 1] = [1, 1]
total_l1_amount: 2 = 2
max_individual_l1_norm: 1 = 1
```

Span separation:

```text
rank(redundant_AA) = 1
rank(orthogonal_AB) = 2

span(orthogonal_AB) includes span(redundant_AA)
span(redundant_AA) does not include span(orthogonal_AB)
```

Full vector census:

```text
not equal
```

This is intentional. Pure span is not claimed to separate identical full-vector
census. The sprint only claims separation after matched marginal scalar census.

## Diminishing Returns

Base:

```text
base_A = {A}
```

Correlated addition:

```text
correlated_A_plus_A = {A, A}
rank gain = 0
```

Orthogonal addition:

```text
orthogonal_A_plus_B = {A, B}
rank gain = 1
```

The added vector has the same individual L1 norm in both additions. The
difference is orientation relative to the existing ensemble span.

## Negative Controls

Identical-vector control:

```text
all vectors identical -> rank reduces to singleton orientation
```

Full-vector-census control:

```text
same full vector census -> pure span equivalent
```

This second control blocks an overread:

```text
pure ensemble span is not relational composability.
```

Relational surplus requires separate coupling data and is out of scope.

## Implementation Surface

Adapter:

```text
omega/adapters/finite_relational/ensemble_span.py
```

Validation:

```text
omega/validation/finite_relational_ensemble_span.py
```

Tests:

```text
tests/test_finite_relational_ensemble_span.py
```

Core exact functions:

```text
marginal_summary
span_rank
gram_matrix
span_includes
span_profile
ensemble_span_summary
```

The rank and span-inclusion checks use exact rational row reduction, not
floating linear algebra.

## Nonclaims

This report does not claim:

```text
population value;
standing;
agency;
population ethics;
aggregation;
relational surplus;
population optimum;
large-deformer ethics;
Omega validation.
```

## Next Steps

The next possible directions are:

```text
1. independent ensemble-span variants with more axes and non-unit vectors;
2. relational composability as a separate coupling instrument;
3. NOLP / CompensationClaim after the expansion mirror has external audit;
4. endogenous register/no-laundering after compensation is typed.
```

Do not use this result to rank populations or patients. It is a finite
instrument showing that marginal scalar summaries can miss ensemble
orientation.

## Public Compression

The ensemble-span pilot separates redundant and orthogonal ensembles after
matching marginal scalar summaries. This makes ensemble orientation a live
joint-tier instrument. It does not prove population value, standing,
aggregation, or relational surplus.
