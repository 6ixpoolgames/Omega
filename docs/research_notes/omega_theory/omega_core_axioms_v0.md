# Omega Core Axioms v0

A triadic quantale-presheaf kernel for recoverable distinction propagation

Status: historical strict-presentation exploration  
Date: 2026-06-03  
Claim boundary: axiomatic scaffold only; not empirical validation, not valuer detection, not Omega validation, and not ethical completion

Current posture:

```text
This note is no longer the root formalism. Treat it as a historical
quantale-presheaf / strict enriched-presentation exploration.

The current root support-level formalism is documented in:

omega_primitive_calculus_v0_lean_root_skeleton.md
```

## 0. Purpose

This note defines the first strict axiom-system candidate for Omega's primitive triad:

```text
relation
distinction
asymmetry
```

The aim is to avoid both failure modes:

```text
too loose:
  private vocabulary, flexible admissibility, and informal metaphysics

too narrow:
  collapsing Omega into finite transition systems, automata theory, or any one
  existing framework
```

The core strategy is:

```text
strict kernel:
  a precise mathematical engine where proofs can occur

adapter layer:
  substrate-specific translations into the kernel, or explicit extensions when
  the strict kernel is insufficient
```

The strict kernel is not the whole Omega ontology. It is the first proof engine
for the primitive triad.

## 1. Primitive stance

Omega assumes three primitive roles:

```text
R:
  relation

D:
  distinction

A:
  asymmetry
```

They are role-primitives, not necessarily three separately visible substances in
every substrate. A substrate may bundle relation and asymmetry into one transition
kernel, channel, flow, reaction law, or policy. The adapter must still decompose
that bundle into the three Omega roles.

### 1.1 Relation

Relation is consequential connectedness: what can connect, constrain, compose,
transform, affect, follow, mediate, or carry what.

### 1.2 Distinction

Distinction is non-equivalence capable of preservation, transformation, collapse,
recovery, or separation.

Distinction is not observation, value, identity, agency, or semantic importance.

### 1.3 Asymmetry

Asymmetry is non-neutral relational unfolding with respect to distinctions:
direction, bias, rate, ordering, selection, cost, probability, rank, gradient,
irreversibility, or differential preservation/collapse.

Asymmetry is not purpose, preference, utility, value, or teleology.

## 2. Strict OmegaCore model

A strict OmegaCore model is a tuple:

```text
M = (C, Delta, V, A, mu)
```

where:

```text
C:
  symmetric monoidal category of relational contexts

Delta:
  complete-lattice-valued distinction presheaf

V:
  unital quantale of asymmetry values

A:
  V-valued profunctorial asymmetry assignment over distinction transitions

mu:
  monoidal distinction-composition structure
```

This is deliberately stricter than a generic interface. It is the class of models
for which the first core lemmas are intended to hold.

Adapters that cannot instantiate this tuple are not rejected outright, but they
are not strict OmegaCore models until they provide a translation or an explicitly
weakened extension with stated consequences.

## 3. Axiom R: relational contexts are symmetric monoidal

`C` is a small symmetric monoidal category:

```text
(C, id, composition, tensor, I)
```

with:

```text
objects:
  contexts X, Y, Z, ...

morphisms:
  f : X -> Y

sequential composition:
  g o f : X -> Z

monoidal composition:
  X tensor Y

monoidal unit:
  I
```

The category laws and symmetric monoidal laws are required.

Interpretation:

```text
sequential composition:
  relation through unfolding / transformation

monoidal composition:
  relation through joint context / parallel composition
```

This axiom rules out purely unstructured co-description. A strict model must
support sequential and joint composition.

## 4. Axiom D: distinctions form a complete-lattice presheaf

`Delta` is a functor:

```text
Delta : C^op -> CLat
```

where `CLat` is the category of complete lattices and monotone maps. Adapters may
strengthen the maps to complete lattice homomorphisms, but monotonicity is the
strict minimum.

For each context `X`, `Delta(X)` is a complete lattice of distinctions.

Order convention:

```text
delta <= epsilon
```

means:

```text
epsilon is at least as fine, informative, or distinction-rich as delta.
```

Equivalently, if `epsilon` is recoverable, then `delta` can be recovered from it.

Each `Delta(X)` has:

```text
bottom_X:
  trivial / coarsest distinction

top_X:
  maximally fine distinction available in the model
```

For every morphism:

```text
f : X -> Y
```

there is a reindexing / pullback map:

```text
f* : Delta(Y) -> Delta(X)
```

satisfying functoriality:

```text
id_X* = id_{Delta(X)}

(g o f)* = f* o g*
```

Interpretation:

```text
a distinction at Y can be pulled back to what it implies about X.
```

This is the structural root of recoverability.

## 5. Axiom M: joint distinction composition

For every pair of contexts `X, Y`, there is a monotone map:

```text
mu_{X,Y} : Delta(X) x Delta(Y) -> Delta(X tensor Y)
```

interpreted as component distinction composition into a joint context.

Minimum laws:

```text
monotonicity:
  if delta <= delta' and epsilon <= epsilon', then
  mu(delta, epsilon) <= mu(delta', epsilon')

unit:
  mu_{X,I}(delta, bottom_I) = delta, up to the canonical unit isomorphism
  mu_{I,X}(bottom_I, delta) = delta, up to the canonical unit isomorphism

naturality for product morphisms:
  for f : X -> X' and g : Y -> Y',

  (f tensor g)*(mu_{X',Y'}(delta', epsilon'))
  =
  mu_{X,Y}(f*(delta'), g*(epsilon'))
```

The map `mu` need not be surjective.

Thus `Delta(X tensor Y)` may contain joint distinctions not generated by
component distinctions. This is essential:

```text
marginal distinction preservation does not imply joint distinction preservation.
```

Component marginal embeddings can be defined by:

```text
iota_X(delta) = mu_{X,Y}(delta, bottom_Y)

iota_Y(epsilon) = mu_{X,Y}(bottom_X, epsilon)
```

when the context `Y` is understood.

## 6. Axiom V: asymmetry values form a unital quantale

`V` is a unital quantale:

```text
V = (V, <=, join, bottom, tensor_V, e)
```

with:

```text
(V, <=, join, bottom):
  complete join-semilattice / complete lattice support as required

(V, tensor_V, e):
  monoid

tensor_V distributes over arbitrary joins in each argument
```

Order convention:

```text
larger values mean stronger support, feasibility, likelihood, retention, or
lower effective obstruction, depending on the adapter's declared interpretation.
```

If an adapter uses cost-like values where smaller is better, it must use the
opposite order or an order-dual quantale so the core convention is preserved.

Examples of admissible `V` candidates:

```text
Boolean feasibility:
  {false, true} with and as tensor, or as appropriate

probabilistic support:
  [0,1] with multiplication as tensor and sup as join

cost / distance:
  Lawvere-style quantale with reversed order and addition

rank / lexicographic score:
  only if embedded into or shown to satisfy the required quantale laws
```

This axiom prevents asymmetry from being an arbitrary post-hoc score. The value
structure must be declared and compositional.

## 7. Axiom A: asymmetry is a V-valued distinction-transition profunctor

For every morphism:

```text
f : X -> Y
```

there is a V-valued relation:

```text
A_f : Delta(X)^op x Delta(Y) -> V
```

where:

```text
A_f(delta, epsilon)
```

is the support, feasibility, likelihood, rate, rank, or retention level by which
source distinction `delta` at `X` is carried, transformed, collapsed, or
recoverable as target distinction `epsilon` at `Y` through relation `f`.

### 7.1 Monotonicity

Because `A_f` is contravariant in the source distinction and covariant in the
target distinction:

```text
if delta <= delta', then
  A_f(delta, epsilon) >= A_f(delta', epsilon)
```

Coarser source distinctions are no harder to recover than finer ones.

```text
if epsilon <= epsilon', then
  A_f(delta, epsilon) <= A_f(delta, epsilon')
```

Finer target distinctions can support at least what coarser target distinctions
support.

### 7.2 Identity law

For the identity morphism:

```text
id_X : X -> X
```

require:

```text
A_id(delta, epsilon) = e       if delta <= epsilon
A_id(delta, epsilon) = bottom  otherwise
```

Identity supports recovering a distinction from itself or anything finer.

### 7.3 Composition law

For composable morphisms:

```text
X --f--> Y --g--> Z
```

require exact profunctor composition:

```text
A_{g o f}(delta, zeta)
=
join_{epsilon in Delta(Y)} A_f(delta, epsilon) tensor_V A_g(epsilon, zeta)
```

Interpretation:

```text
the support for carrying delta through the composite relation is the join over
all intermediate distinctions epsilon of support for delta -> epsilon and
support for epsilon -> zeta.
```

This is the main axiom that gives asymmetry deductive force.

## 8. Optional product-asymmetry law

For product morphisms:

```text
f : X -> X'
g : Y -> Y'
```

and component-generated distinctions:

```text
mu(delta_X, delta_Y) in Delta(X tensor Y)
mu(epsilon_X, epsilon_Y) in Delta(X' tensor Y')
```

a product-like adapter may satisfy the factorization law:

```text
A_{f tensor g}(
  mu(delta_X, delta_Y),
  mu(epsilon_X, epsilon_Y)
)
=
A_f(delta_X, epsilon_X) tensor_V A_g(delta_Y, epsilon_Y)
```

This law is not required for all morphisms. It is a reference property of product
composition.

Coupled morphisms may break this factorization. Product-breaking behavior lives
precisely in the deviation from this law.

## 9. Derived definition: structural recoverability

Given:

```text
f : X -> Y
delta in Delta(X)
epsilon in Delta(Y)
theta in V
```

say that `epsilon` recovers `delta` through `f` at level `theta` when:

```text
delta <= f*(epsilon)
```

and:

```text
theta <= A_f(delta, epsilon)
```

The first condition is structural: the target distinction, pulled back through
relation, is at least sufficient to reconstruct the source distinction.

The second condition is asymmetric: the support level for this recovery meets the
declared threshold.

No identity, self, agent, or valuer label appears in this definition.

Slogan:

```text
identity by recoverability,
not recoverability by identity.
```

## 10. Derived definition: non-erasure

Given a declared required distinction set:

```text
D_req subset Delta(X)
```

and threshold function:

```text
theta : D_req -> V
```

say that `f : X -> Y` is non-erasing for `D_req` at threshold `theta` when for
every `delta in D_req` there exists `epsilon in Delta(Y)` such that `epsilon`
recovers `delta` through `f` at level `theta(delta)`.

No distinction is required by the core. Requirement is claim-relative and must be
declared by the adapter or theorem.

## 11. Derived definition: compatibility

Let a process-bundle candidate be a tuple:

```text
P_i = (X_i, D_i, f_i)
```

where:

```text
X_i:
  context or carrier

D_i subset Delta(X_i):
  declared distinction set

f_i:
  unfolding / dynamics associated with the candidate
```

For a finite family:

```text
Y = {P_1, ..., P_n}
```

let the joint context be:

```text
X_Y = X_1 tensor ... tensor X_n
```

and let a joint unfolding be:

```text
f_Y : X_Y -> Z
```

Using the monoidal distinction maps and adapter-specific embeddings, each `D_i`
is embedded into `Delta(X_Y)`.

The family `Y` is compatible relative to `f_Y`, embedded distinction sets, and
thresholds when all required embedded member distinctions are non-erased under
`f_Y`.

Compatibility is n-ary. Pairwise compatibility is not enough unless an adapter
proves pairwise compatibility composes for the class under study.

## 12. Derived definition: Omega completion family

Given a candidate family space:

```text
T
```

and a declared compatibility admissibility predicate:

```text
Adm : P(T) -> {true, false}
```

define:

```text
OmegaFamily(T, Adm) = Max { Y subset T : Adm(Y) }
```

where `Max` means subset-maximal, not greatest.

Omega completion is not scalar optimization, not utility maximization, and not
assumed unique.

## 13. Theorem 1: recoverability weakening in source distinction

### Statement

If `epsilon` recovers `delta` through `f` at level `theta`, and:

```text
delta' <= delta
```

then `epsilon` recovers `delta'` through `f` at level `theta`.

### Proof

Recoverability of `delta` gives:

```text
delta <= f*(epsilon)
```

and:

```text
theta <= A_f(delta, epsilon).
```

Since `delta' <= delta`, transitivity gives:

```text
delta' <= f*(epsilon).
```

By contravariant monotonicity of `A_f` in the source distinction:

```text
A_f(delta', epsilon) >= A_f(delta, epsilon).
```

Therefore:

```text
theta <= A_f(delta', epsilon).
```

So `epsilon` recovers `delta'` through `f` at level `theta`. QED.

## 14. Theorem 2: recoverability strengthening in target distinction

### Statement

If `epsilon` recovers `delta` through `f` at level `theta`, and:

```text
epsilon <= epsilon'
```

then `epsilon'` recovers `delta` through `f` at level `theta`.

### Proof

Recoverability of `delta` from `epsilon` gives:

```text
delta <= f*(epsilon)
```

and:

```text
theta <= A_f(delta, epsilon).
```

Since `f*` is monotone and `epsilon <= epsilon'`:

```text
f*(epsilon) <= f*(epsilon').
```

Thus:

```text
delta <= f*(epsilon').
```

By covariant monotonicity of `A_f` in the target distinction:

```text
A_f(delta, epsilon') >= A_f(delta, epsilon).
```

Therefore:

```text
theta <= A_f(delta, epsilon').
```

So `epsilon'` recovers `delta` through `f` at level `theta`. QED.

## 15. Theorem 3: compositional recoverability

### Statement

Let:

```text
X --f--> Y --g--> Z
```

Suppose `epsilon in Delta(Y)` recovers `delta in Delta(X)` through `f` at level
`theta`, and `zeta in Delta(Z)` recovers `epsilon` through `g` at level `psi`.

Then `zeta` recovers `delta` through `g o f` at level:

```text
theta tensor_V psi.
```

### Proof

Recoverability through `f` gives:

```text
delta <= f*(epsilon)
```

Recoverability through `g` gives:

```text
epsilon <= g*(zeta)
```

By monotonicity of `f*`:

```text
f*(epsilon) <= f*(g*(zeta)).
```

By functoriality:

```text
f*(g*(zeta)) = (g o f)*(zeta).
```

Therefore:

```text
delta <= (g o f)*(zeta).
```

For the asymmetry threshold, the composition law gives:

```text
A_{g o f}(delta, zeta)
=
join_{eta in Delta(Y)} A_f(delta, eta) tensor_V A_g(eta, zeta).
```

The join includes `eta = epsilon`, so:

```text
A_{g o f}(delta, zeta)
>=
A_f(delta, epsilon) tensor_V A_g(epsilon, zeta).
```

Since:

```text
theta <= A_f(delta, epsilon)
psi <= A_g(epsilon, zeta)
```

and `tensor_V` is monotone:

```text
theta tensor_V psi
<=
A_f(delta, epsilon) tensor_V A_g(epsilon, zeta)
<=
A_{g o f}(delta, zeta).
```

Thus `zeta` recovers `delta` through `g o f` at level `theta tensor_V psi`. QED.

## 16. Theorem 4: non-erasure monotonicity

### Statement

If `f` is non-erasing for `D_req`, then `f` is non-erasing for every subset:

```text
D' subset D_req.
```

### Proof

Non-erasure for `D_req` means every `delta in D_req` has a target witness
recovering it at the declared threshold.

Every element of `D'` is also an element of `D_req`, so the same witnesses prove
non-erasure for `D'`. QED.

## 17. Theorem 5: finite completion existence

### Statement

If `T` is finite and the admissible family:

```text
{Y subset T : Adm(Y)}
```

is nonempty, then `OmegaFamily(T, Adm)` is nonempty.

### Proof

The power set of finite `T` is finite. A nonempty finite partially ordered set
under inclusion has at least one maximal element. QED.

## 18. Adapter obligation

Every substrate adapter must provide:

```text
C:
  relational context category

Delta:
  distinction lattice presheaf

V:
  quantale of asymmetry values

A:
  asymmetry assignment satisfying identity and composition laws

mu:
  joint distinction-composition maps
```

and a realization table:

```text
Primitive | Substrate realization | Evidence interface | Failure mode
```

Minimum evidence split:

```text
relation evidence:
  observed dependency, edge, influence, coupling, reaction path, channel relation

distinction evidence:
  distinguishability, separability, decoder accuracy, event difference,
  information separation

asymmetry evidence:
  rate imbalance, transition bias, rank ordering, directed loss, nonuniform
  preservation, irreversible channeling
```

Evidence is not ontology. Distinguishability is evidence for distinction under an
instrument; it does not exhaust distinction.

## 19. Strict models and extended models

A strict model satisfies all axioms above.

An extended model may weaken one or more requirements only if it declares:

```text
which axiom is weakened;
why the substrate requires weakening;
which theorems no longer apply;
what replacement theorem or empirical discipline is used.
```

This avoids using substrate-general ambition as an escape hatch.

## 20. What is not primitive

The following are not primitive in Omega Core:

```text
state
time
transition
observable
measurement
distinguishability
recoverability
non-erasure
compatibility
completion
identity
self
agent
valuer
utility
reward
moral rule
life
consciousness
purpose
teleology
```

Some are derived. Some are adapter-specific. Some are out of scope.

## 21. What this core claims

This core claims:

```text
Relation, distinction, and asymmetry can be given a strict triadic kernel as
relational contexts, distinction lattices, and quantale-valued distinction
transition asymmetries.

Recoverability, non-erasure, compatibility, and completion can be defined as
derived structures over that kernel.

The first basic theorems follow from functoriality, monotonicity, and quantale
profunctor composition.
```

## 22. What this core does not claim

This core does not claim:

```text
Omega is validated;
value is detected;
agency is detected;
valuerhood is defined in full;
finite transition systems are the Omega ontology;
distinguishability exhausts distinction;
asymmetry is purpose;
compatibility has been achieved;
the ethical specifics stack has been solved.
```

## 23. Next required work

This axiom kernel is not complete until supported by:

```text
1. fully worked strict models;
2. non-models and failure examples;
3. stronger theorems involving mu and A;
4. a related-work bridge to quantale-enriched categories, profunctors,
   coalgebra, fibrations, weighted automata, information theory, and viability
   theory;
5. empirical adapters that emit evidence for relation, distinction, and asymmetry
   without smuggling valuerhood.
```

The immediate next worked models should be:

```text
finite transition-system adapter;
finite stochastic channel adapter.
```

## 24. Summary

Compact formal core:

```text
C:
  symmetric monoidal category of relational contexts

Delta : C^op -> CLat:
  complete-lattice-valued distinction presheaf

V:
  unital quantale of asymmetry values

A_f : Delta(X)^op x Delta(Y) -> V:
  asymmetry over distinction-transition

mu:
  monoidal distinction-composition maps
```

Derived ladder:

```text
relation + asymmetry over distinction:
  unfolding

target distinction reconstructs source distinction:
  recoverability

declared distinction set recoverable:
  non-erasure

joint unfolding non-erases member distinctions:
  compatibility

maximal compatible families:
  Omega completion schema
```

This is not the whole Omega project. It is the first strict proof engine for the
primitive triad.
