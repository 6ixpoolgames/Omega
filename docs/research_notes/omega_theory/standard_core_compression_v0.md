# Standard Core Compression v0

Status: branch exploration note

This note translates the current consequence/proto-teleology stack into more
standard mathematical language. It is not a request to rename the existing code
immediately. The goal is to find the smallest portable core that outside
readers can recognize and audit.

## One-Page Compression

Let:

```text
X        fragments / states / relata
K        declared evaluated contexts
O_k      outcomes in context k
e_k      X -> O_k
C_k      comparison relation on O_k
```

Directional contextual compatibility:

```text
x <=_K y
  iff for every evaluated k, C_k(e_k(x), e_k(y))
```

Symmetric contextual identifiability:

```text
x ~=_K y
  iff x <=_K y and y <=_K x
```

Positive separation/apartness:

```text
x #_K y
  iff some evaluated context separates at least one direction
```

The core rule:

```text
A proposed identification is sound only if it is contained in ~=_K.
```

Equivalently, for a quotient-like map `q : X -> Q`:

```text
q is sound iff kernel(q) subset ~=_K.
```

This is now represented directly in:

```text
formal/lean/OmegaProper/Trajectory/SoundQuotient.lean
```

## Apartness, Not Mere Negation

Apartness should be treated as a positive distinguishability witness, not only
as `not equivalent`. In finite classical settings these can often coincide,
but the positive form is more useful:

```text
some declared evaluated context refuses the proposed identification
```

This is close to coalgebraic apartness as the dual of bisimulation: a positive
way to distinguish states, often with finite derivations. The current stack's
`ConsequenceMergeSeparated` is the appropriate local neighbor.

## Sound Quotients

A quotient-like map:

```text
q : X -> Q
```

has kernel:

```text
ker(q) = {(x,y) | q x = q y}
```

The standard soundness condition is:

```text
ker(q) subset consequence-identifiability
```

This compresses the anti-label principle:

```text
A quotient does not decide what may be merged.
The exact consequence profile constrains which quotient kernels are sound.
```

Important caveat: the relation `~=_K` is not automatically transitive. A
greatest quotient by `~=_K` is available only when the comparison structure
earns equivalence. Without transitivity, valid classes are pairwise-compatible
cliques, not connected components.

## Class Soundness as Clique Soundness

Given a compatibility graph:

```text
edge(x,y) iff x ~=_K y
```

a sound class is a clique. A connected component need not be a clique. The
three-vertex path:

```text
a -- b -- c
```

with no edge `a -- c` is the minimal counterexample. This is the standard
graph-theoretic version of the current guardrail:

```text
chain evidence does not imply class soundness
```

## Baseline Witnesses as Non-Factorization

Most finite baseline witnesses have the form:

```text
f(S1) = f(S2)
g(S1) != g(S2)
```

where:

```text
f = baseline summary
g = declared consequence / recovery / soundness target
```

This proves that `g` does not factor through `f`.

The reusable Lean schema is now:

```text
formal/lean/OmegaProper/BaselineWitnesses/NonFactorization.lean
```

The key theorem:

```text
NonFactorization f g -> not FactorsThrough f g
```

The reverse direction requires a quotient/range formulation or a choice/default
assumption for summary values outside the image of `f`, so it is deliberately
not claimed in the first module.

## Abstraction as Sound Approximation

The existing `ProfileAbstraction` layer is close to abstract interpretation:

```text
exact facts      E
abstract claims  A
soundness        abstract claim -> exact fact
completeness     exact fact -> abstract claim
```

A later version should try to express this as a Galois connection or a
closure/interior pair where the exact and abstract profile spaces have useful
orders. For now, keeping soundness and completeness separate is the right
guardrail.

## Coalgebra as Future Alignment

Coalgebra is a plausible eventual home for a general continuation theory:

```text
c : X -> F X
```

where a functor `F` specifies the behavior/continuation shape. A final
coalgebra, when it exists, supplies a canonical behavior object and behavior
maps from systems into it.

This is not current theory. The project has not yet defined the relevant
continuation functor or compatibility constraints. Coalgebra should be treated
as a future alignment target, not a present claim.

## Immediate Theorem Program

The next useful formal targets are:

```text
1. Sound quotient kernel theorem.
2. Non-factorization schema for baseline witnesses.
3. Clique-vs-connected-component class soundness theorem.
4. Coordinate-split non-factorization theorem.
5. Exact recovery support-disjointness theorem.
```

The first two are landed in this branch. The others should be added only if
they compress existing witnesses without introducing new ontology.
