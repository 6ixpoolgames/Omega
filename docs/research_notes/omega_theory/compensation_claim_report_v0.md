# CompensationClaim / NOLP Report v0

Status: retained finite same-frame compensation report
Scope: same-frame compensation claims, certified cover, uncertified cover refusal, incomplete cover refusal, and phantom compensation
Claim boundary: not value, not standing, not aggregation, not population ethics, not patienthood, not cross-valuer compensation, not correct compensation order, not Omega validation

## Protocol

Protocol note:

```text
docs/research_notes/omega_theory/compensation_claim_protocol_v0.md
```

Validation command:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_compensation_claim --out-root docs\research_notes\validation_results\compensation_claim_v0
```

Retained run:

```text
docs/research_notes/validation_results/compensation_claim_v0/20260707_070710/
```

Retained files:

```text
summary.json
compensation_verdicts.csv
report.md
```

## Verdict

```text
retained
```

The v0 harness retains the same-frame NOLP reading:

```text
same-frame nonrecoverable contraction is refused unless a complete certified
compensation cover is registered.
```

## Cases

### Certified Same-Frame Cover

```text
lost fact:
  repair_capacity

expanded facts:
  repair_capacity
  revision_capacity

cover:
  repair_capacity -> repair_capacity

certified:
  true
```

Verdict:

```text
certified compensation: true
NOLP refuses contraction: false
```

### Uncertified Cover

The cover is complete but the certification flag is false.

Verdict:

```text
certified compensation: false
NOLP refuses contraction: true
```

### Incomplete Cover

The cover is certified but does not cover `repair_capacity`.

Verdict:

```text
certified compensation: false
NOLP refuses contraction: true
```

### Phantom Compensation

Believed frame:

```text
repair_capacity is covered.
```

True frame:

```text
repair_capacity remains uncovered.
```

Verdict:

```text
believed certified compensation: true
true certified compensation: false
phantom compensation diverges: true
```

This is the compensation-layer analogue of phantom recoverability: a corrupted
cover register can counterfeit compensation.

## Relation To Order Sampling

Order sampling remains separate. This v0 harness uses a simple same-frame
discrete fact order. More complex order-dependent compensation verdicts must
go through the order-sampling harness before they are treated as stable.

## Nonclaims

This report does not claim:

```text
value;
standing;
aggregation;
population ethics;
patienthood;
cross-valuer compensation;
the correct compensation order;
that compensation is morally final;
Omega validation.
```

## Public Compression

CompensationClaim / NOLP v0 makes compensation a certified same-frame cover
claim. A complete certified cover can defeat the v0 refusal; incomplete or
uncertified covers cannot; corrupted cover registers can create phantom
compensation.
