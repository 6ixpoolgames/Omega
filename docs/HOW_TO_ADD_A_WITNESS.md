# How To Add A Witness

Status: contributor guide
Scope: finite witness additions for baseline/proxy/abstraction failures
Claim boundary: process guide only

## What Counts As A Witness

A witness is a small finite construction that blocks a tempting inference.

Common shapes:

```text
same summary, different target;
sound-looking local evidence, unsound global class;
abstract reachability present, exact reachability absent;
exact loss present, abstract loss hidden;
endpoint viability present, recurrent carrying absent.
```

The goal is not to make a toy look realistic. The goal is to make a failure
mode impossible to miss.

## Required Parts

Every new witness should include:

```text
1. Name:
   short, descriptive, and specific.

2. Tempting inference:
   the false shortcut the witness blocks.

3. Exact target:
   the fact being protected or tested.

4. Proposed summary or presentation:
   the proxy, quotient, class, abstraction, benchmark, or score under review.

5. Witness pair or construction:
   the finite objects that agree on the summary but differ on the target, or
   the exact/abstract systems that separate.

6. Claim boundary:
   what the witness does not prove.

7. Validation:
   Lean theorem, Python test, retained result artifact, or smoke command.

8. Documentation:
   a short note under `docs/research_notes/...` or
   `docs/research_notes/validation_results/...`.
```

## Preferred Theorem Shape

Use the generic non-factorization shape when possible:

```text
summary a = summary b
target a != target b
```

This proves:

```text
NonFactorization summary target
```

In plain language:

```text
the summary does not determine the target.
```

## Preferred Failure Shapes

### Proxy failure

```text
same benchmark score;
different safety fact.
```

### Bad quotient

```text
abstract system has a path;
exact system has no path.
```

### Hidden loss

```text
exact system loses a target;
abstract presentation reports no loss.
```

### Class failure

```text
chain-connected evidence exists;
full pairwise clique soundness fails.
```

### Recurrent carrying failure

```text
endpoint viability and forward reachability remain;
return structure is lost;
recurrent carrying fails.
```

## Documentation Template

```text
# Witness Name v0

Status:
Scope:
Claim boundary:

## False Inference

## Construction

## Exact Target

## Summary / Presentation

## Result

## Why This Matters

## What This Does Not Prove

## Validation

## Related Files
```

## Validation Expectations

For Lean witnesses:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaOmega
rg -n "\b(sorry|admit|axiom)\b" formal\lean -g "*.lean"
git diff --check
```

For Python witnesses, prefer:

```powershell
python -m pytest tests\test_<witness>.py
python -m omega.validation.baseline_witness_smoke
```

Use the repo's current validation docs for exact commands:

```text
docs/VALIDATION.md
docs/BASELINE_WITNESS_SMOKE.md
docs/BASELINE_WITNESS_FAMILY_SMOKE.md
```

## Anti-Patterns

Avoid:

```text
post-hoc target selection;
claiming a witness proves all proxies fail;
using toy size as evidence of real-world scale;
omitting the exact target;
omitting the claim boundary;
adding a positive contract without a strictness or failure witness;
calling a carrier/support an object or agent.
```

## Good First Witnesses

Good first contributions are small:

```text
same proxy score, different side-effect target;
same local marginal, different joint coupling;
same reachability count, different declared recovery;
same endpoint viability, different recurrence.
```

The best witnesses are boring and exact.
