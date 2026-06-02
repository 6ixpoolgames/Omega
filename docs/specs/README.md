# Specs

This folder holds implementation specs, handoffs, runbooks, and branch-specific
design documents. Keep public onboarding docs at `docs/` root; keep executable
or historical run instructions here.

## Current

- `current/` contains live instrument specs that define the current empirical
  machinery.
- `current/` is the active spec inbox. Future Codex instances should check this
  folder first whenever the user says a new spec is in the repo.

Current active spec:

- `current/FUTURE_FIELD_ATLAS_INSTRUMENT_SPEC.md`

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

Recommended active spec naming:

```text
docs/specs/current/FUTURE_FIELD_ATLAS_<SHORT_NAME>_SPEC.md
```
