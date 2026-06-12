<div align="center">

# Proto-Teleology Without Purpose

## Consequence-Bearing Difference and Sound Identification

Internal Review Draft

S. Poole

June 12, 2026

</div>

---

## Abstract

This paper introduces a minimal formal account of proto-teleology: directed
consequence without purpose, value, agency, selfhood, or moral truth. The
guiding question is simple: when does a difference matter because erasing it
changes what can follow? We answer in two stages. First, a primitive relational
presentation supplies a non-collapse condition: some relata are connected,
distinguished, and asymmetrically arranged in a way that cannot be flattened
into total interchangeability. Second, an admissible continuation apparatus
tests whether that primitive difference changes consequences under declared
contexts. When an evaluated context refuses the erasure of a primitive
difference, the difference becomes consequence-bearing. We call this minimal
structure proto-teleological because it introduces directional non-neutrality
before any notion of goal, utility, organism, agent, or valuer.

The framework treats labels, quotient classes, clusters, and learned
representations as downstream presentations. They are acceptable only when
their proposed identifications respect consequence-induced separation. This
aligns the proposal with standard concerns in quotienting, contextual
equivalence, abstraction soundness, and bisimulation-like reasoning, while
remaining lower than any claim about value or agency. We also describe finite
baseline witnesses: small worlds where familiar summaries agree while declared
consequence or recovery facts differ. These witnesses show why exact guardrails
are needed before scaling to richer substrates.

## 1. Introduction

Many theories of value, agency, and purpose begin with something already
structured: a subject, a utility function, a reward signal, an organism, a
self-maintaining system, a boundary, a preference ordering, or a goal. That is
often appropriate for applied modeling, but it leaves a prior question open:

```text
What makes any difference matter before value or valuers are assumed?
```

This paper addresses that prior question. It does not try to derive morality,
agency, or value. It tries to formalize the first anti-flattening step: a
difference matters in the minimal technical sense when erasing it changes
admissible continuation.

The central claim is:

```text
A primitive difference becomes proto-teleological when admissible continuation
exposes its erasure as consequence-changing.
```

Here "proto-teleological" means directed consequence before purpose. It is a
weak and deliberately constrained term. It says that some continuations,
identifications, or erasures are not neutral. It does not say that the system
wants anything.

### Why This Matters

This lower layer matters for four reasons.

First, it gives a disciplined sense of "mattering" before value. A difference
can be consequence-bearing even in a substrate with no preferences, no agents,
and no moral facts. That is not enough for ethics, but it blocks a premature
flattening move where all distinctions are treated as arbitrary unless a valuer
already exists.

Second, it disciplines abstraction. In science and machine learning, it is
common to compress states, cluster observations, learn representations, or
quotient a system by apparent similarity. The formal lesson here is that a
compression is not trustworthy merely because it is concise or predictive. It
must be checked against the consequences it merges.

Third, it clarifies a possible route from non-neutrality to richer theories of
value-bearing systems. If consequence-bearing differences can recur, compose,
survive abstraction, support compatible continuations, and eventually support
valuer-like trajectories, then value need not be injected at the primitive
layer. This paper does not prove that route. It identifies one lower condition
such a route would have to preserve.

Fourth, it makes small finite worlds useful. In finite settings, profiles can
be exhaustive, failures can be exact, and negative controls can be checked
without appeal to intuition. That gives us a way to test reductions before
making claims about large or physical substrates.

### Contributions

1. We isolate a primitive non-collapse condition using relation, distinction,
   and asymmetry.

2. We define a continuation/consequence apparatus as an operational test of
   whether erasure is neutral.

3. We define proto-teleology as a consequence filter: evaluated contexts may
   allow or refuse proposed identifications.

4. We connect the framework to established formal ideas: quotient soundness,
   contextual equivalence, abstraction contracts, and bisimulation-style
   guardrails.

5. We describe finite baseline witnesses showing that familiar summaries can
   agree while declared consequence or recovery facts differ.

## 2. Terminology in Plain Language

This section fixes the working vocabulary. The goal is not to introduce a new
dictionary but to make precise which standard idea each term is trying to
track.

### Difference, Distinction, and Erasure

A **difference** is an informal contrast between two possible fragments or
relata. A **distinction** is a formal predicate witnessing that two relata are
not freely interchangeable in the primitive presentation.

An **erasure** is the act of identifying two relata, treating them as the same,
or placing them in the same quotient class. In formal implementations this
often appears as a proposed merge.

The central question is:

```text
Is this erasure allowed by the declared continuation consequences?
```

### Continuation and Consequence

A **continuation** is any admissible way the substrate can be extended,
evolved, completed, transformed, derived, composed, perturbed, or probed. Time
evolution is only one kind of continuation.

A **consequence** is what a fragment yields under a continuation context. In a
transition system this may be a reachable future. In a graph it may be
reachability. In a logic it may be derivability. In a stochastic channel it may
be an output distribution. In a constraint system it may be completion
behavior.

### Compatibility, Separation, and Identification

Two fragments are **compatible** under a declared panel if every evaluated
context compares their consequences successfully. A context **separates** them
when it refuses that comparison.

Symmetric **identification** is stronger than one-way compatibility. If the
comparison relation is directional, then allowing `a` as a substitute for `b`
does not automatically allow `b` as a substitute for `a`.

This is close in spirit to contextual equivalence and observational
equivalence: two things may be identified only relative to the contexts that
fail to distinguish them. The difference here is that we keep the comparison
relation and evaluated panel explicit, because a bad panel can create false
collapse or false separation.

### Filter and Gradient

The current formal layer establishes a **filter**, not a full gradient.

A filter says:

```text
this erasure is allowed;
that erasure is refused.
```

A gradient would additionally order continuations or profiles:

```text
this continuation preserves more declared consequence-bearing structure;
that one erases more;
this profile dominates that profile.
```

The filter is currently formalized. The gradient remains future work.

## 3. The Primitive Floor: Non-Collapse

The primitive presentation has three roles:

```text
relation:
  relata stand in structured bearing

distinction:
  two relata are not freely interchangeable under some formal contrast

asymmetry:
  the bearing of a distinction is not neutral in all directions
```

Formally, these can be represented by predicates analogous to:

```text
Rel(x, y)
Sep(d, x, y)
Asym(d, x, y)
```

The theory does not treat those field names as magic. Empty predicates,
decorative predicates, or disconnected predicates do not provide a real
primitive floor. The stack therefore distinguishes vocabulary from witnesses.

### Joint Witnesses

A joint primitive witness says relation and separation touch the same relata:

```text
exists d, x, y:
  Rel(x, y) and Sep(d, x, y)
```

This blocks two total collapses:

```text
RelationCollapse:
  no relation holds anywhere

IdentificationCollapse:
  no distinction separates any two relata
```

### Asymmetry Witnesses

An asymmetry witness says:

```text
exists d, x, y:
  Asym(d, x, y)
```

In the formal stack used by this paper, asymmetry implies both relation and
separation. So an asymmetry witness supplies a joint witness. This factoring
matters: the collapse-blocking work is done by relation/separation contact;
asymmetry is a strong source of that contact.

The result is narrow but important:

```text
An actual primitive witness prevents total flattening.
```

It does not yet say that the distinction changes what can follow. That requires
continuation consequence.

## 4. Continuation as a Contextual Test

The continuation layer asks whether a primitive difference is operationally
exposed. It uses a consequence system with:

```text
Fragment:
  the item being compared

Context:
  an admissible continuation or test condition

Outcome:
  what the fragment yields under that context

consequence:
  Context -> Fragment -> Outcome

Compare:
  context-indexed comparison of outcomes

Evaluated:
  which contexts are actually in the declared panel
```

This structure is intentionally close to familiar ideas:

- Contextual equivalence: two terms are equivalent if no context distinguishes
  them.
- Observational equivalence: two states are equivalent if observations cannot
  tell them apart.
- Bisimulation and quotienting: state merges are valid only when the transition
  or observation structure is respected.
- Abstraction soundness: a coarse model is acceptable only if its claims remain
  true relative to the exact system.

The proposal does not simply import one of these frameworks because it wants a
lower and more general interface. The consequence system can represent temporal
dynamics, graph reachability, logical derivability, stochastic output,
constraint completion, or other continuation forms.

### Compatibility and Separation

Directional compatibility means:

```text
Compatible(a, b) :=
  for every evaluated context k,
  Compare k (consequence k a) (consequence k b)
```

Directional separation means:

```text
Separated(a, b) :=
  some evaluated context k refuses that comparison
```

If comparison is directional, separation is directional. Therefore the formal
stack distinguishes:

```text
one-way allowance:
  a can stand in for b under the declared comparisons

symmetric identification:
  a can stand in for b and b can stand in for a

merge separation:
  at least one direction is separated, so symmetric identification is blocked
```

The core rule is:

```text
If evaluated consequence merge-separates a and b, then a and b cannot be
soundly identified.
```

## 5. Proto-Teleology as a Consequence Filter

A proto-teleological condition exists when:

```text
1. there is a primitive witness, and
2. evaluated consequence merge-separates that witness's endpoints.
```

Equivalently:

```text
primitive non-collapse
+ consequence refusal
= consequence-bearing difference
```

This is the first formal sense in which a difference matters. The difference
does not matter because a subject values it. It matters because erasing it
changes what the declared continuation apparatus permits.

### The Exact Profile

The consequence profile records which pairs are blocked and which are allowed:

```text
Blocks(a, b) := evaluated consequence merge-separates a and b
Allows(a, b) := a and b are symmetrically identifiable
```

The checked bridge is:

```text
ProtoTeleologicalCondition(S)
-> exists a, b, Blocks_S(a, b)
```

So the proto-teleological condition induces a nonempty blocked-merge profile.
That is the filter.

### Why This Is Not Value

This result does not rank outcomes. It does not say a continuation is better.
It does not say the blocked merge is morally wrong. It says only that a
declared consequence test refuses an erasure.

The philosophical significance is lower:

```text
Non-neutrality precedes valuation.
```

If no differences can be consequence-bearing, value has nowhere to attach. But
if consequence-bearing differences exist, the later question of value becomes
well-posed without being answered.

## 6. Why Quotients and Labels Are Downstream

A recurring failure mode in formal and empirical work is to start with a
classification and then treat the classification as ontological. The present
stack reverses that order.

Do not start from:

```text
cluster labels;
learned representation coordinates;
quotient classes;
visual similarity;
predictive success alone.
```

Start from:

```text
which proposed identifications are refused by evaluated consequence?
```

This is a quotient-soundness requirement. A quotient is valid only if every
merge it performs is allowed by the consequence profile. If a quotient class
contains a separated pair, it is invalid relative to the declared apparatus.

### Chain-Connectedness Is Not Identity

One common mistake is to infer class membership from chains:

```text
a is close to b;
b is close to c;
therefore a, b, c belong together.
```

That inference is valid only under additional structure, such as transitivity.
If the comparison relation is nontransitive, `a` may compare with `b`, and `b`
may compare with `c`, while `a` is separated from `c`.

For nontransitive comparisons, a proposed class must be pairwise compatible
unless stronger structure has been proved. This is a small theorem with a large
methodological consequence: connectedness is not identity.

## 7. Abstraction and Coarse-Graining

Coarse-graining is necessary in large systems. The point is not to reject it.
The point is to make it accountable.

The current abstraction layer separates exact profiles from coarse claims.
Given an exact consequence system, an abstraction may claim:

```text
allows(a, b)
blocks(a, b)
```

Those claims are judged by two independent contracts:

```text
soundness:
  abstraction claims imply exact profile facts

completeness:
  exact profile facts imply abstraction claims
```

An abstraction can be sound but incomplete. It can also be complete but
unsound. This distinction matters because a coarse summary can look clean while
erasing the exact consequence facts that made the structure relevant.

This is the connection to scale. We should not claim that all coarse-grainings
preserve primitive or consequence structure. We should ask which
transformations and abstractions preserve the facts required by the theory.

## 8. Finite Baseline Witnesses

Finite worlds let us make exact mistakes on purpose. That is useful.

The baseline witness suite contains finite examples where a familiar summary
matches across two systems while a declared consequence or recovery fact
differs. The retained patterns include:

- same reachability, different declared recovery;
- same mutual information, different declared recovery;
- same chain evidence, different class soundness;
- same compression score, different merge soundness;
- same coarse bisimulation, different consequence profile.

The suite supports this narrow claim:

```text
Familiar finite summaries can match while declared consequence/recovery,
merge-soundness, or class-soundness facts differ.
```

This matters because it attacks a specific reduction strategy. If someone says
"your structure is just mutual information," or "just reachability," or "just
bisimulation," the finite witnesses show that those summaries can agree while
the declared consequence facts disagree.

The finite witnesses do not prove that all reductions fail. They do not prove
physical or biological relevance. They provide exact warning signs and a
reproducible adversarial test surface.

## 9. Validation Discipline

The current validation stack supports three kinds of checks.

### Formal Proofs

The Lean stack checks primitive nondegeneracy, collapse blockers, consequence
separation, class guardrails, panel discipline, proto-teleological conditions,
profile bridges, abstraction contracts, and selected finite baseline witnesses.

### Finite Search and Smoke Tests

Python runners check retained finite witness examples and parameterized finite
families. These are not substitutes for theorems, but they make external
review and adversarial search easier.

### CI and Reproducibility

Cross-platform smoke checks make the finite witness suite easier to validate
outside the development machine. The larger formal build checks the active
proof umbrella.

The validation principle is:

```text
Every positive structure should be paired with failure modes.
```

Vacuous contexts, universal comparisons, all-refusing panels, unsound
abstractions, and reduction baselines are not side issues. They are the
discipline that prevents the definitions from becoming self-validating.

## 10. Larger Ambition

The present paper establishes only the lower floor:

```text
primitive non-collapse
-> evaluated consequence refusal
-> consequence-bearing difference
-> exact allow/block filter
```

A fuller theory of value-bearing continuation would require much more:

```text
filter/profile
-> gradient or preorder over profiles
-> consequence-preserving transformations
-> recurrence
-> recoverability without exact identity
-> support or extent
-> compatibility over longer continuations
-> valuer-capable trajectories
```

The reason this lower floor matters is that it gives that larger program a
non-arbitrary starting point. Instead of assuming value, the proposed path asks
how consequence-bearing differences can recur, compose, survive abstraction,
and eventually support valuers.

That larger program remains open. The paper earns only the first step.

## 11. Limitations

1. Primitive non-collapse alone does not prove proto-teleology.
   Proto-teleology requires consequence responsiveness under an admissible
   continuation apparatus.

2. Apparatus admissibility remains central. Arbitrary contexts and comparisons
   can manufacture separations or collapses.

3. The current structure is a filter, not a gradient. Ordering continuations or
   profiles remains future work.

4. Recoverability is not established. Exact identity is too strong; future work
   needs transformation and abstraction contracts.

5. Finite baseline witnesses are not infinite-family theorems and do not prove
   substrate-general validity.

6. No claim is made about value, morality, agency, selfhood, life, identity,
   boundary, deformer structure, or any terminal theory of value-bearing
   futures.

## 12. Conclusion

The paper's core claim is modest but useful:

```text
A difference matters, in the proto-teleological sense, when erasing it changes
admissible continuation.
```

This gives a formal foothold for directed consequence without purpose. It does
not smuggle in a valuer, a goal, a self, or a utility function. It says only
that some primitive differences become consequence-bearing under declared
continuation tests.

That is enough to block total flattening. It is not enough to validate a theory
of value. It is the first layer from which such a theory can be built without
making value primitive.

## Appendix A. Repository Pointers

The repository paths below use project-internal implementation names. They are
not part of the paper's conceptual vocabulary.

Public onboarding documents:

- `docs/OMEGA_FORMALISM_PRIMER.md`
- `docs/EXTERNAL_READER_GUIDE.md`
- `docs/CLAIMS_LEDGER.md`
- `docs/BASELINE_WITNESS_SUITE_V0.md`

Relevant Lean files:

- `formal/lean/AlphaCore/Primitive.lean`
- `formal/lean/AlphaCore/Nondegenerate.lean`
- `formal/lean/AlphaCore/PrimitiveMap.lean`
- `formal/lean/OmegaProper/Trajectory/ConsequenceRelation.lean`
- `formal/lean/OmegaProper/Trajectory/ConsequenceClasses.lean`
- `formal/lean/OmegaProper/Trajectory/ConsequenceDiscipline.lean`
- `formal/lean/OmegaProper/Trajectory/ConsequenceComparison.lean`
- `formal/lean/OmegaProper/Trajectory/AlphaConsequenceSeed.lean`
- `formal/lean/OmegaProper/Trajectory/ProtoTeleologicalSeed.lean`
- `formal/lean/OmegaProper/Trajectory/ProtoTeleologicalProfile.lean`
- `formal/lean/OmegaProper/Trajectory/ProfileAbstraction.lean`
- `formal/lean/OmegaProper/BaselineWitnesses.lean`

## Appendix B. Reproduction Commands

Lean build:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build AlphaOmega
```

Retained finite witness smoke:

```powershell
python -m omega.validation.baseline_witness_smoke
```

Parameterized finite witness family smoke:

```powershell
python -m omega.validation.baseline_witness_family_smoke
```
