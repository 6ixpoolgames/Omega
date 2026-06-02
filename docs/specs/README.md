# Specs

This folder holds implementation specs, handoffs, runbooks, and branch-specific
design documents. Keep public onboarding docs at `docs/` root; keep executable
or historical run instructions here.

## Current

- `current/` contains live instrument specs that define the current empirical
  machinery.
- `current/` is the active spec inbox. Future Codex instances should check this
  folder first whenever the user says a new spec is in the repo.

Current active and recent live-instrument specs:

- `current/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md`
- `current/FUTURE_FIELD_ATLAS_RANK_ORDER_BOUNDARY_CLASS_EXPANSION_SPEC.md`
  (completed cleanly; added pair026 and opened representative-control target)
- `current/FUTURE_FIELD_ATLAS_RANK_ORDER_BOUNDARY_NEIGHBOR_OBSERVABLE_SWEEP_SPEC.md`
  (completed cleanly; opened rank-order class expansion target)
- `current/FUTURE_FIELD_ATLAS_RANK_ORDER_BOUNDARY_MEDIUM_SWEEP_SPEC.md`
  (completed cleanly; yielded pair005-only H64/H128 result)
- `current/FUTURE_FIELD_ATLAS_RANK_ORDER_NATIVE_SMOKE_SPEC.md` (completed;
  rank-order boundary remains the current live coupled operator)
- `current/FUTURE_FIELD_ATLAS_SUBSTRATE_MORPHOLOGY_SWEEP_SPEC.md`
- `current/FUTURE_FIELD_ATLAS_SHARED_CAPACITY_SMOKE_SPEC.md` (completed; v1 not
  recommended for scale-up)

## Archive

- `archive/rfs_mb0/` keeps the RFS-MB0 horizon-transport, transition-energy,
  and Future Field Atlas precursor specs.
- `archive/rfs_mb1/` keeps the short neutral coupled-landscape branch.
- `archive/rfs0/` keeps the strict reachable-futures measurement-floor branch.
- `archive/val0/` keeps early constructor-task and grammar branch specs.
- `archive/val1/` keeps early multifield compatibility/interference specs.

## Policy

New work should not add root-level spec files. Put active Future Field Atlas or
successor-instrument specs under `docs/specs/current/` unless the spec is a
branch archive. Once a branch is superseded, move its specs under
`docs/specs/archive/<branch>/` and update public-facing indexes.

For project-level orientation, do not use specs as onboarding prose. Use:

```text
README.md
docs/OMEGA_FORMALISM_PRIMER.md
docs/EXTERNAL_READER_GUIDE.md
docs/OMEGA_PROJECT_MANUAL.md
```

Recommended active spec naming:

```text
docs/specs/current/FUTURE_FIELD_ATLAS_<SHORT_NAME>_SPEC.md
```
