# External Reader Guide

Status: onboarding guide for outside collaborators
Scope: current public framing, checked formal stack, empirical bridges, and contribution paths
Claim boundary: this repository does not claim Omega validation, value detection, valuer detection, agency detection, identity detection, life detection, candidate promotion, holdout readiness, or substrate-general validation.

## 0. What This Repository Is

This repository is a research workspace for the Omega / Reachable Futures
project.

The current project is not trying to detect value directly. It is trying to
build a formal and empirical discipline for a lower question:

```text
When does a difference matter because erasing it changes what can follow?
```

The current public framing is:

```text
Alpha names the primitive grammar by which differences can become
consequence-bearing.

Omega names the possible maximal compatible unfolding of consequence-bearing
structure across admissible continuations.
```

This is a one-object thesis. Alpha and Omega are not two unrelated objects.
Alpha is the primitive face. Omega is the terminal face, if a substrate can
support one.

Value remains downstream. Value requires valuers. Valuers require robust,
recoverable, continuation-bearing trajectories. This repository has not
detected valuers or value.

## 1. What Changed Recently

Earlier public summaries over-centered future fields, distinction transport,
and Future Field Atlas. Those remain useful, but they are no longer the
conceptual front door.

The current front door is:

```text
continuation, not time;
consequence-induced separation, not labels;
primitive nondegeneracy, not decorative fields;
proto-teleological seed, not purpose or value.
```

The important correction is that "future" is now treated as the temporal
adapter of a more general notion: continuation. A continuation can be a
transition, path, derivation, completion, composition, deformation, or other
admissible unfolding supplied by a substrate.

## 2. Current Checked Formal Stack

The current primitive floor is `AlphaCore`:

```text
relation;
distinction;
asymmetry.
```

Lean now checks that:

```text
asymmetry implies relation;
asymmetry implies distinction;
asymmetry separates its endpoints;
relation, distinction, asymmetry, and reach irreversibility do not collapse
into one another;
joint primitive witnesses block total relation collapse and total
identification collapse.
```

The lower Omega trajectory layer then defines consequence systems:

```text
fragments;
continuation contexts;
outcomes;
consequence maps;
comparison relations;
evaluated context panels.
```

The key rule is:

```text
A proposed identification is forbidden when some evaluated continuation
context separates the consequences.
```

Recent Lean guardrails check:

```text
directional allowance is not symmetric identification;
merge separation blocks symmetric identification;
classes must be pairwise consequence-compatible unless transitivity is proven;
vacuous evaluation collapses the apparatus;
universal comparison collapses the apparatus;
all-refusing panels are noncollapsed but still pathological;
Alpha primitive witness endpoints can be consequence-separated;
proto-teleological seed requires primitive Alpha contact plus evaluated
consequence merge-separation;
primitive nondegeneracy alone is not sufficient for such a seed.
```

The main Lean umbrellas are:

```text
formal/lean/AlphaOmega.lean
formal/lean/AlphaCore.lean
formal/lean/AlphaCalculus.lean
formal/lean/AlphaAdapters.lean
formal/lean/Omega.lean
```

The most relevant current files are:

```text
formal/lean/AlphaCore/Primitive.lean
formal/lean/AlphaCore/Nondegenerate.lean
formal/lean/AlphaCore/Independence.lean
formal/lean/OmegaProper/Trajectory/ConsequenceRelation.lean
formal/lean/OmegaProper/Trajectory/ConsequenceClasses.lean
formal/lean/OmegaProper/Trajectory/ConsequenceDiscipline.lean
formal/lean/OmegaProper/Trajectory/ConsequenceComparison.lean
formal/lean/OmegaProper/Trajectory/ConsequencePanelDiscipline.lean
formal/lean/OmegaProper/Trajectory/AlphaConsequenceSeed.lean
formal/lean/OmegaProper/Trajectory/ProtoTeleologicalSeed.lean
```

The older `OmegaCore`, `ProtoOmega`, `OmegaAdapters`, and `OmegaProper`
namespaces remain important checked implementation/provenance surfaces. They
should not be read as separate metaphysical objects.

## 3. Empirical Arms

The cleanest current empirical-formal bridge is the registry-first stochastic
channel branch.

It separates:

```text
declared registry recovery:
  a predeclared decoder registry works

existence / capacity recovery:
  some decoder exists

optimized diagnostic recovery:
  a best available target/decoder succeeds after search
```

This branch is designed to prevent a self-validating inference:

```text
some decoder exists = the declared instrument recovered the distinction
```

Current retained result:

```text
results/stochastic_distinction_channel/20260606_registry_first_probe_x3_v0/
docs/research_notes/validation_results/stochastic_distinction_channel/stochastic_registry_first_probe_x3_result.md
```

Future Field Atlas is retained but demoted:

```text
Future Field Atlas v0:
  preformal reachable-frontier morphology instrument
```

FFA is still useful for finite-dynamics stress testing and morphology feature
extraction. It is not the central empirical object for valuerhood, and it does
not detect Omega, value, valuers, agency, identity, support, capture, erasure,
or compatibility.

## 4. What This Repository Is Not Claiming

This repository does not currently claim:

```text
Omega validated;
Omega-terminal exists in any physical substrate;
agent detected;
valuer detected;
identity detected;
self detected;
life detected;
value detected;
compatibility detected;
support / capture / erasure detected;
candidate promoted;
holdout ready;
substrate-general theory validated.
```

Positive results should be read as formal guardrails, finite presentations,
instrument checks, provenance checks, or substrate-characterization results
unless a stronger theorem-transfer path is explicitly shown.

## 5. Best First Reading Path

### 15-Minute Orientation

Read:

```text
1. README.md
2. docs/OMEGA_FORMALISM_PRIMER.md
3. docs/EXTERNAL_READER_GUIDE.md
```

Goal: understand the current one-object framing, claim boundary, and live stack.

### 60-Minute Technical Orientation

Read:

```text
1. docs/research_notes/omega_theory/README.md
2. docs/research_notes/omega_theory/alphaomega_continuation_proto_teleology_v0.md
3. docs/research_notes/omega_theory/alpha_primitive_core_v0.md
4. docs/research_notes/omega_theory/probabilistic_channel_presentation_v0.md
5. docs/research_notes/validation_results/stochastic_distinction_channel/stochastic_registry_first_probe_x3_result.md
6. docs/PUBLIC_RESULTS_INDEX.md
```

Goal: understand how the core theory, checked Lean layer, and retained
empirical bridges currently fit together.

### Lean Orientation

Read:

```text
1. formal/lean/AlphaCore/Primitive.lean
2. formal/lean/AlphaCore/Nondegenerate.lean
3. formal/lean/AlphaCore/Independence.lean
4. formal/lean/OmegaProper/Trajectory/ConsequenceRelation.lean
5. formal/lean/OmegaProper/Trajectory/ConsequenceClasses.lean
6. formal/lean/OmegaProper/Trajectory/AlphaConsequenceSeed.lean
7. formal/lean/OmegaProper/Trajectory/ProtoTeleologicalSeed.lean
```

Goal: see the current checked lower-stack object without importing older
semantic language.

### Historical Orientation

Read only after the current front door is clear:

```text
1. docs/OMEGA_RUNNING_LOG.md
2. docs/OMEGA_PROJECT_MANUAL.md
3. docs/research_notes/omega_theory/historical_probe_terms.md
4. docs/research_notes/omega_theory/omega_formal_core_v0_2_future_distinction_dynamics.md
5. docs/research_notes/validation_results/future_field_atlas/
```

Goal: understand how older FFA, horizon-transport, and distinction-dynamics
branches led to the current consequence/continuation framing.

## 6. How To Validate The Local Formal Stack

Use:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaOmega
rg -n "\b(sorry|admit|axiom)\b" formal\lean -g "*.lean"
git diff --check
```

The repository also has an observed-passing GitHub Actions workflow that runs
the same Lean build, proof-placeholder scan, and whitespace check on pushes and
pull requests targeting `master`.

## 7. How To Read A Result Note

Ask:

```text
What exact substrate or presentation was tested?
Were the inputs, contexts, thresholds, registries, or decoders declared before
scoring?
Are path-level evidence rows retained or losslessly reconstructible?
Does the result separate existence/capacity from declared provenance?
Does the result separate optimized diagnostics from theorem-transfer evidence?
Are nulls, degenerate controls, or collapse cases present?
Does the note explicitly block value, valuerhood, agency, identity, and Omega
validation claims?
```

A result can be useful while making no Omega claim.

## 8. How A Collaborator Can Help

Useful contributions include:

```text
reviewing Lean definitions for hidden semantic assumptions;
checking whether a theorem surface permits self-validating evidence routes;
proposing cleaner consequence-system adapters;
auditing comparison relations for collapse, over-separation, and provenance;
stress-testing registry-first stochastic outputs;
designing trajectory-level toy substrates with actions, perturbations, and
recoverable process-bundles;
improving documentation and reproducibility;
identifying where old FFA morphology can become subordinate diagnostics rather
than central claims.
```

The project especially benefits from criticism that distinguishes:

```text
formal theorem;
presentation artifact;
adapter artifact;
empirical measurement;
semantic overpromotion;
real but low-level consequence structure;
stronger value-relevant structure not yet proven.
```

## 9. Current Open Problems

Near-term formal questions:

```text
How should continuation contexts be instantiated over richer Alpha structures?
When can consequence-bearing witnesses recur under transformation?
How should drift and pivot be represented without identity claims?
When does a consequence-respecting class remain valid under changing contexts?
What is the smallest bridge from consequence-bearing recurrence to
process-bundle persistence?
```

Near-term empirical questions:

```text
How do registry-first recovery gaps behave in larger finite probes?
Which consequence-system adapters can be generated without post-hoc tuning?
What controls expose vacuous, universal, or all-refusing comparison apparatuses?
Which FFA morphology features remain useful as subordinate diagnostics?
```

## 10. Working Standard

The current standard is:

```text
Principled:
  define objects from primitives, consequence, and provenance, not from labels

Parsimonious:
  add only the structure needed to block invalid inference or expose a real
  distinction

Predictive / revelatory:
  every theory move should imply a concrete next test, theorem, counterexample,
  or failure mode
```

The short version:

```text
Do not start from names.
Start from what continuation refuses to erase.
```
