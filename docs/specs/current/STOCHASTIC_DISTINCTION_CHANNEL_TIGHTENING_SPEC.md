# Stochastic Distinction Channel Instrument Tightening Spec

Status: completed
Target package: `omega.stochastic_distinction_channel`
Runner: `omega.stochastic_distinction_channel.probe`
Output: `results/stochastic_distinction_channel/20260604_stochastic_channel_probe_v0_tightened/`

## Purpose

Tighten the v0 finite stochastic-channel probe so the formal arm can consume the
outputs without guessing which decoder policy, target observation, support
semantics, or theorem-transfer status is being used.

This is an instrumentation repair over the existing tiny channel substrate. It
is not a broader channel sweep and not a new scientific claim.

## Required Repairs

```text
1. Emit decoder_policy_manifest.csv.
2. Add selected target-distinction and decoder provenance to non-erasure and
   marginal/joint diagnostic rows.
3. Emit support_vs_probability_summary.csv.
4. Emit theorem_transfer_readiness_summary.csv.
5. Emit formal_channel_consumption_bundle.json.
6. Tighten exact support recoverability so exact support requires:
     target support non-ambiguity
     positive-prior source-label coverage
7. Preserve the very short executive summary in the report.
```

## Claim Boundary

Allowed:

```text
instrument schema tightening
formal consumption readiness status
support-level exact recovery versus probabilistic recovery separation
declared decoder policy and selected-observation provenance
```

Blocked:

```text
Omega validation
agency / identity / value / valuer claims
compatibility detection
ethical erasure
substrate-general validation
```

## Completed Command

```powershell
.\.venv\Scripts\python.exe -m omega.stochastic_distinction_channel.probe `
  --out results\stochastic_distinction_channel\20260604_stochastic_channel_probe_v0_tightened `
  --csv-output-mode plain
```

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_stochastic_distinction_channel.py -q
.\.venv\Scripts\python.exe -m compileall omega\stochastic_distinction_channel tests\test_stochastic_distinction_channel.py
```
