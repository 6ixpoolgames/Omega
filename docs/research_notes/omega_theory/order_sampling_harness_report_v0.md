# Order Sampling Harness Report v0

Status: retained finite declared-order sensitivity report
Scope: sampled fact orders over known loss/expansion profile witnesses before NOLP verdicts
Claim boundary: not final value, not correct fact order, not aggregation, not arbitration, not standing, not agency, not identity, not moral standing, not Omega validation

## Protocol

Protocol note:

```text
docs/research_notes/omega_theory/order_sampling_harness_protocol_v0.md
```

Validation command:

```powershell
.\.venv\Scripts\python.exe -m omega.validation.finite_relational_order_sampling --out-root docs\research_notes\validation_results\order_sampling_harness_v0
```

Retained run:

```text
docs/research_notes/validation_results/order_sampling_harness_v0/20260707_070710/
```

Retained files:

```text
summary.json
order_sampling_rows.csv
report.md
```

## Verdict

```text
calibrated
```

## Calibration Results

Loss dependency witness:

```text
lose_local vs lose_joint
classification: dependent
```

Sampled orders:

```text
discrete:
  false

local_below_joint:
  false

joint_below_local:
  true
```

Reading:

```text
local-vs-joint loss comparison is order-content unless the register supplies
the connecting order.
```

Expansion invariant witness:

```text
expand_task_and_revision vs expand_task
classification: invariant_true
```

Across the sampled orders, the enriched expansion profile covers the task-only
profile.

## What This Permits

NOLP can now use order sampling as a guardrail:

```text
if a compensation verdict depends on the declared fact order, the verdict must
be reported as order-dependent rather than treated as free structure.
```

## Nonclaims

This report does not claim:

```text
the correct fact order;
final value;
standing;
aggregation;
arbitration;
patienthood;
Omega validation.
```

## Public Compression

Order sampling turns fact-order sensitivity into an explicit verdict. Some
profile comparisons are invariant across the sampled orders; others are
declared-order content. NOLP should not treat the latter as unpriced facts.
