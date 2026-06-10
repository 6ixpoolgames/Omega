# Omega Formalism Primer

Status: public onboarding / current best formalism
Scope: compact bridge from the repository README to the dense theory notes
Claim boundary: formal orientation only; not empirical validation, not value detection, not valuer detection, not agency detection, not identity detection, and not Omega validation

## One-Sentence Ambition

Omega is an attempt to formalize value-bearing futures without taking reward,
utility, moral rules, fixed agents, fixed selves, fixed boundaries, or
privileged valuers as primitives.

The current reorientation is:

```text
Alpha and Omega are two faces of one object.

Alpha names the primitive grammar by which differences can become
consequence-bearing.

Omega names the possible maximal compatible unfolding of consequence-bearing
structure across admissible continuations.
```

This does not mean value is already present at the primitive layer. It means
the lower stack asks a prior question:

```text
When does a difference matter because erasing it changes what can follow?
```

That technical sense of "mattering" precedes value. Value enters only later,
when consequence-bearing structures can support robust valuer-like trajectories.

## Continuation, Not Time

The project no longer treats "future" as primitive. Future is the temporal
adapter of a broader concept: continuation.

A continuation may be:

```text
a transition;
a path;
a derivation;
a completion;
a composition;
a deformation;
a perturbation response;
an admissible unfolding in a substrate.
```

In a temporal system, continuation appears as future evolution. In a graph it
appears as reachability. In a proof system it may appear as derivation. In a
constraint system it may appear as completion. In a category it may appear as
composition.

So the lower formal target is not "future-bearing distinction" in a narrow
clock-time sense. It is continuation-bearing distinction.

## The Current Primitive Floor

The primitive floor is `AlphaCore`:

```text
relation;
distinction;
asymmetry.
```

The roles are:

```text
relation:
  relata stand in structured bearing with one another

distinction:
  some relata are not freely interchangeable

asymmetry:
  the bearing of a distinction is not neutral in all directions
```

The current Lean core proves basic non-collapse facts:

```text
asymmetry implies relation;
asymmetry implies distinction;
asymmetry separates its endpoints;
relation, distinction, asymmetry, and reach irreversibility do not
automatically supply one another;
an actual asymmetry witness supplies a primitive nondegeneracy witness;
primitive nondegeneracy blocks total relation collapse and total
identification collapse.
```

The important discipline is that merely having fields named `Rel`, `Sep`, and
`Asym` is not enough. The project distinguishes decorative primitives from
jointly instantiated witnesses.

## Consequence Comes Before Quotient

The current lower Omega layer starts from consequence-induced separation, not
labels, clusters, quotients, or representations.

The consequence-native scaffold uses:

```text
Fragment:
  the thing being compared

Context:
  an admissible continuation context

Outcome:
  what a fragment does under that context

consequence:
  Context -> Fragment -> Outcome

Compare:
  context-indexed comparison of outcomes

Evaluated:
  which contexts are actually in the panel
```

The core rule is:

```text
A proposed identification is forbidden when some evaluated continuation
context separates the consequences.
```

This is the anti-label move. The theory does not begin by naming buckets. It
asks which erasures the continuation structure refuses.

The checked consequence layer now separates:

```text
directional allowance:
  one direction of comparison succeeds

symmetric identification:
  both directed allowances succeed

merge separation:
  either direction is separated, blocking symmetric identification

valid class formation:
  proposed classes must be pairwise consequence-compatible unless transitivity
  has been separately earned

collapse:
  no evaluated contexts or universal comparison makes the apparatus toothless

over-separation:
  a panel can refuse everything and still fail as a useful comparison apparatus
```

This blocks a common false move:

```text
a is close to b, and b is close to c, therefore a, b, c form one object.
```

Not unless the relevant comparison is transitive or the proposed class is
pairwise consequence-compatible.

## Proto-Teleological Seed

The newest formal hinge is the narrowly scoped proto-teleological seed.

It means only:

```text
primitive Alpha contact
+ evaluated consequence merge-separation
```

In Lean, the bridge is:

```text
Alpha primitive witness:
  a joint relation/separation witness, or an asymmetry witness that supplies one

Alpha consequence system:
  continuation consequences over the Alpha carrier

Consequence-bearing witness:
  the witness endpoints are merge-separated by evaluated consequence

ProtoTeleologicalSeed:
  an asymmetry witness whose endpoints are consequence merge-separated
```

The checked result is:

```text
if such a seed exists, then the Alpha frame is primitively nondegenerate;
the consequence system is noncollapsed;
there is a primitive witness whose endpoints cannot be symmetrically
identified by consequence.
```

The checked negative examples are equally important:

```text
primitive nondegeneracy alone is not sufficient;
vacuous consequence evaluation gives no seed;
universal consequence comparison gives no seed.
```

This is the first formal version of directed consequence. It is not purpose,
goal-directedness, value, agency, identity, selfhood, deformer theory, valuerhood,
Omega-seed, or Omega-terminal.

## Where The Lean Stack Lives

Main umbrellas:

```text
formal/lean/AlphaOmega.lean
formal/lean/AlphaCore.lean
formal/lean/AlphaCalculus.lean
formal/lean/AlphaAdapters.lean
formal/lean/Omega.lean
formal/lean/OmegaCore.lean
```

Current lower-stack files to read first:

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

The older `OmegaCore` namespace remains checked provenance from the previous
support/recoverability calculus. `ProtoOmega`, `OmegaAdapters`, and
`OmegaProper` remain implementation namespaces during the naming migration.
They should not be read as separate metaphysical objects.

## Adapter And Empirical Roles

Adapters do not create the core seed. They determine manifestation.

An adapter supplies concrete choices for:

```text
the substrate;
the available continuations;
the evaluated contexts;
the consequence map;
the comparison relation;
the provenance and reconstruction discipline.
```

The cleanest current empirical-formal bridge is the registry-first stochastic
channel branch. It separates:

```text
declared registry recovery:
  a predeclared decoder registry works

existence / capacity recovery:
  some decoder exists, whether or not it was declared

optimized diagnostic recovery:
  a best available target/decoder choice succeeds after search
```

This blocks the self-validating shortcut:

```text
some decoder exists = the declared instrument recovered the distinction
```

Future Field Atlas remains useful, but it is no longer the conceptual center.
It is retained as:

```text
Future Field Atlas v0:
  preformal reachable-frontier morphology instrument
```

FFA can still provide finite-dynamics stress tests and feature extraction. It
does not detect value, valuers, agency, identity, compatibility, support,
capture, or erasure.

## What This Is Not

The project does not currently claim:

```text
Omega validation;
Omega-terminal existence;
valuer detection;
agent detection;
identity detection;
self detection;
life detection;
value detection;
compatibility detection;
support / capture / erasure detection;
substrate-general empirical validation.
```

Positive formal results should be read as checked scaffolds and guardrails.
Positive empirical results should be read as instrument or substrate
characterization unless a stricter theorem-transfer route has been explicitly
shown.

## Why The Guardrails Matter

The project is specifically trying to avoid self-validating constructions.

Important blocked shortcuts include:

```text
presentation success = substrate contact;
existence decoder = declared decoder;
summary error rates = path-ensemble theorem evidence;
coarse quotient recovery = identity;
chain-connectedness = valid class;
primitive nondegeneracy = proto-teleological seed;
frontier morphology = value-bearing trajectory.
```

Each recent repair makes one of those routes harder or impossible at the
formal surface.

## Recommended Reading Order

For a new collaborator:

```text
1. README.md
2. docs/OMEGA_FORMALISM_PRIMER.md
3. docs/EXTERNAL_READER_GUIDE.md
4. docs/research_notes/omega_theory/alphaomega_continuation_proto_teleology_v0.md
5. docs/research_notes/omega_theory/alpha_primitive_core_v0.md
6. docs/research_notes/omega_theory/probabilistic_channel_presentation_v0.md
7. docs/PUBLIC_RESULTS_INDEX.md
```

For the checked formal path:

```text
1. formal/lean/AlphaCore/Primitive.lean
2. formal/lean/AlphaCore/Nondegenerate.lean
3. formal/lean/OmegaProper/Trajectory/ConsequenceRelation.lean
4. formal/lean/OmegaProper/Trajectory/ConsequenceClasses.lean
5. formal/lean/OmegaProper/Trajectory/ConsequenceDiscipline.lean
6. formal/lean/OmegaProper/Trajectory/AlphaConsequenceSeed.lean
7. formal/lean/OmegaProper/Trajectory/ProtoTeleologicalSeed.lean
```

For local validation:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaOmega
rg -n "\b(sorry|admit|axiom)\b" formal\lean -g "*.lean"
git diff --check
```

## Current North Star

The compact current formulation is:

```text
Relation makes bearing possible.
Distinction makes non-interchangeability possible.
Asymmetry makes bearing non-neutral.
Continuation exposes consequence.
A difference matters when erasing it changes what can follow.
Proto-teleology is consequence-bearing direction without purpose.
Omega is the possible maximal compatible unfolding of that mattering across
admissible continuations.
Value enters only when such structures support valuers.
```
