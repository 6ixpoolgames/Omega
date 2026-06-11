# Baseline Witness Suite v0

Status: stable finite witness suite.

This page freezes the current baseline witness program as `Baseline Witness
Suite v0`. The goal is to stop witness proliferation long enough to make the
existing evidence easy to reproduce, critique, and formalize.

This is not an Omega validation run.

## Scope

`Baseline Witness Suite v0` consists of:

```text
13 retained finite baseline witnesses
13 parameterized finite witness families
165 default finite family cases at k = 1..5
5 finite Lean baseline witness conversions currently landed
```

The retained witnesses cover:

```text
same reachability / different declared recovery
same entropy / different recovery profile
same frontier morphology / different declared loss profile
same intervention effect / different declared recovery
same mutual information / different declared recovery
same observation rank / different declared recovery
same control reach / different declared recovery
same optimized success / different declared recovery
same viability kernel / different declared recovery
same marginal success / different joint success
same compression score / different merge soundness
same chain evidence / different class soundness
same coarse bisimulation / different consequence profile
```

The parameterized family smoke checks finite extensions of all thirteen
patterns. It does not prove an infinite-family theorem.

## Current Lean Transfers

The current Lean transfers are exact finite witness conversions:

```text
reachability / declared recovery
mutual information / declared recovery
chain evidence / class soundness
compression score / merge soundness
coarse bisimulation / consequence profile
```

They are adapter-level guardrails. They do not extend the core ontology and do
not define recoverability, identity, valuerhood, agency, boundary, deformer
structure, Omega-seed, or Omega-terminal.

## Reproduction

Run the retained finite witness smoke:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_smoke.ps1
```

Run the parameterized family smoke:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validation\run_baseline_witness_family_smoke.ps1
```

Run the active Lean stack:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaOmega
```

For cross-platform Python entry points, see [VALIDATION.md](VALIDATION.md).

## Suite Claim

The suite supports this narrow claim:

```text
Familiar finite summaries can match while declared consequence/recovery,
merge-soundness, or class-soundness facts differ.
```

The suite does not claim:

```text
Omega is validated;
value, valuerhood, agency, identity, life, selfhood, or compatibility were
detected;
the finite witnesses transfer to physical, biological, or agentic substrates;
the parameterized families have been proved as infinite-family Lean theorems;
all possible baselines have been defeated.
```

## Freeze Rule

Do not add witness pattern 14 by default.

Near-term work should prefer:

```text
distilling common theorem schemas;
promoting selected finite witnesses into Lean;
improving external validation;
adding adversarial search tools;
documenting fair attacks and stronger controls.
```

## Search MVP

The first finite search helper covers two retained patterns:

```bash
python -m omega.baseline_witnesses.search --match-baseline mutual_information --separate declared_recovery --states 8 --trials 10000
python -m omega.baseline_witnesses.search --match-baseline reachability --separate declared_recovery --states 8 --trials 10000
```

This is not an exhaustive search theorem. It is a reviewer-facing way to
rediscover matched-baseline / different-declared-recovery examples in small
finite channel spaces.
