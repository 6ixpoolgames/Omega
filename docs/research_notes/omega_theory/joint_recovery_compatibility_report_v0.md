# Joint Recovery Compatibility Report v0

Status: retained finite recovery-grounded coupling report
Scope: joint recovery under coupling after fixed individual recovery profiles and vector/span controls
Claim boundary: not value, not standing, not agency, not plurality theory, not moral aggregation, not patienthood, not population optimum, not Omega validation

## Protocol

Protocol note:

```text
docs/research_notes/omega_theory/joint_recovery_compatibility_protocol_v0.md
```

Validation command:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_joint_recovery_compatibility --out-root docs\research_notes\validation_results\joint_recovery_compatibility_v0
```

Retained run:

```text
docs/research_notes/validation_results/joint_recovery_compatibility_v0/20260707_015243/
```

Retained files:

```text
summary.json
control_comparison.csv
joint_recovery_profiles.csv
report.md
```

## Verdict

```text
separated
```

The retained finite witness separates joint recovery under coupling while
holding individual recovery profiles, marginal scalar controls, full vector
census, and pure span fixed.

This is the recovery-grounded bridge from registered coupling to joint
compatibility. It does not prove value, standing, plurality theory, moral
aggregation, patienthood, or a population optimum.

## Candidate Pair

Held-fixed individual vectors:

```text
vA = A
vB = B
```

Held-fixed individual recovery:

```text
vA individually recovers A_recovery_fact
vB individually recovers B_recovery_fact
```

Compatible case:

```text
compatible_joint_recovery:
  joint recovered facts = {A_recovery_fact, B_recovery_fact}
  joint recovery succeeds
```

Interfering case:

```text
interfering_joint_recovery:
  joint recovered facts = {A_recovery_fact}
  joint recovery fails because B_recovery_fact is missing
```

Matched controls:

```text
marginal scalar controls equal: true
full vector census equal: true
pure span equivalent: true
span rank separates: false
individual recovery profiles equal: true
```

Separation:

```text
joint recovery succeeds: true vs false
joint missing facts: [] vs [B_recovery_fact]
```

## Negative Controls

Identical joint recovery:

```text
same individual recovery + same joint recovery -> no separation
```

Individual-profile difference:

```text
if individual recovery differs, the case is not credited as joint-only
```

These controls keep the result from reducing to individual recovery or vector
surface changes.

## Implementation Surface

Adapter:

```text
omega/adapters/finite_relational/joint_recovery_compatibility.py
```

Validation:

```text
omega/validation/finite_relational_joint_recovery_compatibility.py
```

Tests:

```text
tests/test_finite_relational_joint_recovery_compatibility.py
```

Core functions:

```text
recovery_profile
joint_recovery_compatible
compare_joint_recovery_cases
compatible_vs_interfering_witness
joint_recovery_compatibility_summary
```

## Nonclaims

This report does not claim:

```text
value;
standing;
agency;
plurality theory;
moral aggregation;
patienthood;
population optimum;
Omega validation.
```

## Next Steps

The next possible directions are:

```text
1. phantom composability: corrupted joint recovery claims license a coupling
   that the true recovery profile refuses;
2. typed coupling labels tied to declared recovery modes;
3. NOLP / CompensationClaim after loss, expansion, span, coupling, and joint
   recovery compatibility are audited;
4. plurality theory only after joint recovery is tied to corridor dynamics.
```

Do not use this result to rank populations or patients. It is a finite bridge
showing that individual recovery can leave joint recovery under coupling open.

## Public Compression

Joint Recovery Compatibility v0 shows that same individual vectors and same
individual recovery profiles can still differ in joint recovery under coupling.
It bridges registered coupling toward recovery-grounded compatibility without
claiming value, standing, plurality, or patienthood.
