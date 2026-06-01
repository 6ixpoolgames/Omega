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

