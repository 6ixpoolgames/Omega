# Run Retention Policy

This policy controls how Future Field Atlas outputs should be retained while
the instrument is still changing.

## Default Posture

Do not commit raw calibration data to Git.

Commit:

```text
code
tests
specs
compact result notes
manual / index updates
small manifests when explicitly useful
```

Keep raw run folders local by default.

## Retention Tiers

### Tier 0: Scratch

Use for failed setup, local smoke, or duplicate calibration runs.

Retain:

```text
nothing required
```

Delete raw folders freely after extracting any useful error.

### Tier 1: Operational

Use for tooling, performance, storage, and graceful-exit checks.

Retain:

```text
status.json
run_config.json
future_field_atlas_rebuild_contract.json
progress.csv
errors.csv
compact report or changelog entry
```

Raw topology can be deleted after the operational fact is logged.

### Tier 2: Calibration

Use for instrument calibration and reproducibility checks.

Retain:

```text
run_config.json
future_field_atlas_manifest.json
future_field_atlas_rebuild_contract.json
status.json
progress.csv
errors.csv
operator / condition / scan manifests
artifact completeness summary
reconstruction audit summary
compact retained result note
```

Raw topology may be deleted if the retained note does not depend on later
manual raw-row inspection.

### Tier 3: Baseline

Use for expensive, clean, hard-to-regenerate runs that define a current
baseline.

Retain locally or archive:

```text
full output folder
raw node/edge shards
manifests
audit summaries
result note
```

Delete only after a newer baseline supersedes it or after an explicit archive
decision.

## Compact Retention Utility

Use the Future Field Atlas retention summarizer before deleting worker-spooled
raw topology:

```powershell
.\.venv\Scripts\python.exe -m omega.future_field_atlas.retention_summary `
  --run results\future_field_atlas\<run_name>
```

This writes a compact bundle under:

```text
results/future_field_atlas/<run_name>/_retention_summary/
```

The bundle includes:

```text
retained_run_summary.json
retained_run_summary.md
retained_deletion_plan.json
retained_pair_skew.csv.gz
retained_metric_summary.csv.gz
retained_artifact_inventory.csv.gz
compact_artifacts/
```

The summarizer copies compact manifests, status/config, rebuild contract,
readiness summaries, reconstruction audits, completeness summaries, profiles,
residuals, and marginal summaries. It does not copy high-volume raw node/edge
spool files.

If the run is complete, uncapped, cleanly audited, and interpretable, the
deletion plan may recommend:

```text
delete_raw_spools_allowed
```

Only then delete worker-spooled raw topology:

```powershell
.\.venv\Scripts\python.exe -m omega.future_field_atlas.retention_summary `
  --run results\future_field_atlas\<run_name> `
  --delete-raw-spools
```

This removes only:

```text
coupled_pair_spool/
```

and writes:

```text
RAW_TOPOLOGY_DELETED.json
```

Use `--force` only when intentionally overriding a blocked recommendation.
Do not use deletion on runs with failed pairs, cap poisoning, failed
reconstruction audits, or `NO_COMPLETE_ROWS` unless the run is explicitly a
truncation/operational stress test.

## Rebuild Contract

New runs should emit:

```text
future_field_atlas_rebuild_contract.json
```

Interpretation:

```text
exact_rebuild_supported:
  source commit exists and worktree was clean at run start

logical_rebuild_only:
  run can be understood from retained metadata, but exact raw regeneration is
  not guaranteed
```

Old runs may be deleted even if not exactly rebuildable. The rebuild contract
is an ideal for future iterations, not a retroactive blocker.

## Reporting Tiers

Use the smallest report surface that preserves project memory:

```text
Tier 0:
  no doc update

Tier 1:
  changelog only

Tier 2:
  running log + changelog

Tier 3:
  retained result note + running log + public index if relevant

Tier 4:
  README/manual/public posture update
```

Not every polish pass should become a full research note.
