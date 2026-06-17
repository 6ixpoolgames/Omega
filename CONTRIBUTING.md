# Contributing

Omega is an active research repo. Contributions are welcome, especially if
they make the formal stack easier to audit, extend finite witnesses, improve
adapter provenance, or clarify claim boundaries.

## Project Posture

The current contribution is best read as:

```text
a continuation-map integrity discipline for alignment-relevant abstraction.
```

The repo does not currently prove value, valuerhood, agency, identity,
selfhood, moral truth, or Omega-terminal structure.

## Good Contributions

High-value contributions include:

```text
small Lean theorems with explicit assumptions;
finite counterexamples that block tempting inferences;
Python witnesses with retained artifacts and tests;
adapter provenance templates;
visual worked examples;
documentation that makes the claim boundary clearer;
translations to standard mathematical language that do not erase domain
meaning.
```

## Before Opening A Change

Please identify:

```text
1. What exact claim is being added or clarified?
2. What assumptions does it require?
3. What does it not claim?
4. What validation command checks it?
5. Does it duplicate an existing theorem shape?
6. Is there a negative control or strictness witness?
```

## Adding Witnesses

Start with:

```text
docs/HOW_TO_ADD_A_WITNESS.md
```

Preferred witness form:

```text
same summary, different target
```

or another explicit finite failure of an abstraction, quotient, presentation,
or proxy.

## Lean Work

Keep Lean contributions small and local.

Expected checks:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaOmega
rg -n "\b(sorry|admit|axiom)\b" formal\lean -g "*.lean"
git diff --check
```

Do not introduce `sorry`, `admit`, or new axioms into the checked stack.

## Python / Empirical Work

For Python witnesses or validation tools, include tests and retained artifacts
where appropriate.

Useful checks:

```powershell
python -m pytest
python -m omega.validation.baseline_witness_smoke
python -m omega.validation.baseline_witness_family_smoke
```

If a result depends on a run artifact, document the artifact path and the
expected pass/fail gates.

For adapters or empirical probes, start from:

```text
docs/templates/ADAPTER_PROVENANCE_TEMPLATE.md
```

## Documentation Work

Docs should distinguish:

```text
proved theorem;
empirical result;
instrument audit;
conjecture;
motivation;
historical note.
```

Use:

```text
docs/CLAIMS_LEDGER.md
docs/research_notes/omega_theory/layer_a_derivation_audit_v0.md
docs/research_notes/omega_theory/compression_guardrails_v0.md
```

as style references.

## Claim Hygiene

Do not promote:

```text
toy witness -> real-world safety;
sound abstraction -> correct exact target;
support predicate -> object identity;
recurrence -> agency;
proto-teleology -> value;
Omega motivation -> Omega validation.
```

Make the non-claim explicit.

## Human-AI Workflow

The repo uses a human-AI research workflow. See:

```text
docs/HUMAN_AI_WORKFLOW.md
```

Contributions should still be auditable on their own terms: checked proofs,
tests, retained artifacts, and clear claim boundaries matter more than who or
what generated a draft.
