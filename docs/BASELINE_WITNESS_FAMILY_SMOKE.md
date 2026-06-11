# Baseline Witness Family Smoke

This is the one-command reproduction path for the retained baseline witnesses
that currently have parameterized family extensions. It does not create new
retained artifacts.

It is not an Omega validation run.

## Setup

From the repository root:

```powershell
pip install -e ".[dev]"
```

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_family_smoke.ps1
```

By default, the runner checks all family cases for `k = 1..5` finite extension steps and
then runs the focused family pytest suite. Outputs are written under:

```text
.tmp/baseline_witness_family_smoke/<timestamp>/
```

To skip the focused pytest pass and only run the aggregate family status check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_family_smoke.ps1 -SkipPytest
```

To use a different finite depth:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_family_smoke.ps1 -MaxNuisanceBits 3
```

## Expected Gates

At the default `k = 1..5`, the aggregate check covers:

```text
8 parameterized witness families
90 finite family cases
same-reachability / different-declared-recovery family
same-entropy / different-recovery-profile family
same-frontier-morphology / different-declared-loss-profile family
same-mutual-information / different-declared-recovery family
same-optimized-success / different-declared-recovery family
same-marginal-success / different-joint-success family
same-compression-score / different-merge-soundness family
same-chain-evidence / different-class-soundness family
```

The script fails if any family emits an unexpected `family_case_status`, if any
family has the wrong case count, or if the focused family pytest suite fails.

## Claim Boundary

Passing this smoke means:

```text
eight retained baseline witnesses have parameterized finite family extensions;
all checked finite family cases report the expected non-reduction status;
the focused family tests passed.
```

It does not mean:

```text
an infinite-family theorem was proved;
Lean theorem transfer has been completed;
Omega is validated;
value, valuers, agency, identity, life, selfhood, or compatibility were
detected;
the families transfer to physical, biological, or agentic substrates.
```
