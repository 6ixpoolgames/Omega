# Baseline Witness Smoke

This is the smallest current one-command reproduction path for the
baseline-controlled witness batch. It reruns the six retained finite witnesses,
checks each regenerated `summary_digest` against the committed retained summary,
and runs the focused witness tests.

It is not an Omega validation run.

The script also supports `-RetainedRoot` for audit tests. CI uses that hook to
copy retained summaries, corrupt digest/status fields, and verify that the smoke
rejects the mutated retained artifacts.

## Setup

From the repository root:

```powershell
pip install -e ".[dev]"
```

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_smoke.ps1
```

By default, outputs are written under:

```text
.tmp/baseline_witness_smoke/<timestamp>/
```

The runner also points pytest temp/cache paths under that same timestamped
directory so it does not depend on user-level temp directory permissions.

To skip the focused pytest pass and only rerun the witness/digest gates:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_smoke.ps1 -SkipPytest
```

To compare regenerated witnesses against a copied retained-summary tree:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_smoke.ps1 -RetainedRoot path\to\baseline_witnesses_copy -SkipPytest
```

## Expected Gates

The script fails if any of these checks fail:

```text
same_reachability_different_recovery_v0 status and retained digest match
same_entropy_different_recovery_profile_v0 status and retained digest match
same_frontier_morphology_different_loss_profile_v0 status and retained digest match
same_optimized_success_different_declared_recovery_v0 status and retained digest match
same_marginal_success_different_joint_success_v0 status and retained digest match
same_compression_score_different_merge_soundness_v0 status and retained digest match
focused pytest suite for all six witnesses passes
```

The CI mutation tests separately fail the smoke against copied retained
summaries with a corrupted `summary_digest` or `witness_status`.

## Claim Boundary

Passing this smoke means:

```text
the six finite baseline witnesses reproduced;
their retained summary digests matched;
the focused witness tests passed.
```

It does not mean:

```text
Omega is validated;
value, valuers, agency, identity, life, selfhood, or compatibility were
detected;
the witnesses transfer to physical, biological, or agentic substrates.
```
