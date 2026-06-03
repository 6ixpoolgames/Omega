# Stochastic Distinction Channel Fixed Policy Spec

Status: completed
Target package: `omega.stochastic_distinction_channel`
Runner: `omega.stochastic_distinction_channel.probe`
Output: `results/stochastic_distinction_channel/20260604_stochastic_channel_probe_v0_fixed_policy/`

## Purpose

Make fixed declared target observations co-primary with Bayes-best target
selection in the stochastic-channel bridge.

Bayes-best target selection is useful diagnostically, but by itself it can hide
which target observation did the work. The fixed policy keeps the declared
source-target observation pairing visible:

```text
D_A      -> E_A
D_B      -> E_B
D_joint  -> E_joint
D_parity -> E_parity
```

with degraded-carrier variants where a direct target exists.

## Required Changes

```text
1. Emit declared_target_policy_summary.csv.
2. Include declared_target_policy_summary.csv in the formal consumption bundle.
3. Emit non-erasure rows under both:
     bayes_best_target_distinction
     fixed_declared_target_distinction
4. Emit marginal/joint diagnostic rows under both policies.
5. Keep support-vs-probability summary as the Bayes-best probability layer.
6. Keep exact support recovery strict:
     target support non-ambiguity
     positive-prior source-label coverage
7. Reduce repetitive scope disclaimers in generated reports.
```

## Completed Command

```powershell
.\.venv\Scripts\python.exe -m omega.stochastic_distinction_channel.probe `
  --out results\stochastic_distinction_channel\20260604_stochastic_channel_probe_v0_fixed_policy `
  --csv-output-mode plain
```

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
