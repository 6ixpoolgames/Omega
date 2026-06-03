# Future Field Atlas Formal Adapter Raw/Closed Gap Report Spec

Status: completed v0
Target package: `omega.future_field_atlas`
Module: `omega.future_field_atlas.formal_adapter_gap_report`
Input: `results/future_field_atlas/20260603_formal_adapter_conformance_package/`
Output: `results/future_field_atlas/20260603_formal_adapter_raw_closed_gap_report/`

## Purpose

Produce a compact A-lite report over the formal adapter package showing where
formal theorem transfer depends on generated closure rather than raw empirical
witness rows.

This pass answers:

```text
Which closed transport rows are closure-derived only?
Which closure rules contribute most?
Which law checks depend most on closure?
Which theorem transfers are closure-heavy?
Can explicit raw witnesses be emitted cheaply?
```

This is not a new empirical sweep.

## Inputs

Required input bundle:

```text
formal_consumption_bundle.json
closed_transport_relation.csv.gz
adapter_law_check_summary.csv.gz
adapter_theorem_transfer_summary.csv.gz
identity_transport_check.csv.gz
source_weakening_check.csv.gz
target_strengthening_check.csv.gz
lax_composition_check.csv.gz
non_erasure_by_unfolding.csv.gz
unfolding_manifest.csv.gz
context_manifest.csv.gz
```

## Outputs

```text
law_raw_closed_gap_summary.csv.gz
closure_support_kind_summary.csv.gz
closure_depth_summary.csv.gz
law_detail_gap_by_cell.csv.gz
closure_only_law_gap_examples.csv.gz
closure_only_token_pair_summary.csv.gz
theorem_transfer_closure_dependency.csv.gz
non_erasure_raw_closed_gap_summary.csv.gz
raw_witness_recommendations.csv.gz
formal_adapter_raw_closed_gap_report.md
formal_adapter_raw_closed_gap_bundle.json
```

## Required Read

The report must preserve this distinction:

```text
generated presentation:
  formal closure can satisfy DistTrans laws and theorem transfer

strict raw model:
  raw empirical witness relation itself satisfies the laws
```

Do not collapse closure-derived rows into raw evidence.

## Claim Boundary

Allowed:

```text
raw/closed gap quantification
closure dependency by law
closure dependency by theorem transfer
recommendations for explicit witness provenance
```

Blocked:

```text
Omega validation
proto-valuer detection
valuer detection
agency / identity / value detection
compatibility detection
support / capture / erasure detection
finite completion existence over FFA candidates
candidate-family or admissibility-predicate expansion
new broad FFA sweeps
```

## Smoke Command

```powershell
.\.venv\Scripts\python.exe -m omega.future_field_atlas.formal_adapter_gap_report `
  --input results\future_field_atlas\20260603_formal_adapter_conformance_package `
  --out results\future_field_atlas\20260603_formal_adapter_raw_closed_gap_report `
  --gzip-compresslevel 1 `
  --csv-output-mode gzip `
  --sample-limit 250
```

## Completed v0 Result

Result note:

```text
docs/research_notes/validation_results/future_field_atlas/future_field_atlas_formal_adapter_raw_closed_gap_report_result.md
```

v0 status:

```text
strict raw conformance: not achieved
generated presentation: still consumable
non-erasure pass rows: no closure-only inflation detected
```
