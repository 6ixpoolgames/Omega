# Reproducibility Smoke

This is the smallest current external reproduction path for the registry-first
stochastic-channel branch. It is not an Omega validation run. It checks one
finite X3 probe and its adversarial provenance audit.

## Setup

From the repository root:

```powershell
pip install -e ".[dev]"
```

## Run

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_reproducibility_smoke.ps1
```

By default, outputs are written under:

```text
.tmp/reproducibility_smoke/<timestamp>/
```

The runner also points pytest temp/cache paths under that same timestamped
directory so it does not depend on user-level temp directory permissions.

To skip the focused pytest pass and only run the probe/audit gates:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_reproducibility_smoke.ps1 -SkipPytest
```

## Expected Gates

The script fails if any of these checks fail:

```text
carrier_id = X3
state_count = 8
channel_count = 15
registered_rows = 120
provenance_gap_rows = 120
cascade_evidence_status = path_rows_retained
probe_overall_status = registry_first_theorem_transfer_ready
audit_overall_status = PASS
audit_rows = 105
audit_failure_count = 0
focused X3 pytest passes
```

## Claim Boundary

Passing this smoke means:

```text
the finite X3 registry-first probe reproduced;
the adversarial provenance audit reproduced;
the focused X3 tests passed.
```

It does not mean:

```text
Omega is validated;
value, agency, valuerhood, identity, or compatibility were detected;
the result transfers to physical, biological, or agentic substrates.
```
