# Minimal Reachable Futures Formalism

Theory note for the substrate reset

## Status

This is the current working formalism for the reachable-futures empirical program.

It supersedes recent attempts to encode boundary, coherence, capacity, dissipation, repair, or energy as primitive state variables. Those terms remain useful, but in the current formulation they are derived from a minimal relational substrate and its reachable futures.

The guiding concern is overfit risk. If we place too much theory inside the state vector, the probe can only rediscover what we put there. The substrate should therefore be as neutral as possible.

## Core principle

The substrate should contain only:

```text
distinction
relation
```

Asymmetry should be measured from non-equivalent future consequences.

Everything else should be derived.

## Primitive substrate

The minimal substrate is:

```text
S = (X, ->)
```

where:

```text
X:
  finite distinction space

-> subset X x X:
  neutral transformation relation
```

A state `x in X` is a distinguishable configuration.

A transformation `x -> y` is neutral. It is not intrinsically coherent, dissipative, good, bad, viable, agentic, Omega-like, or pseudo-Omega-like.

A path is:

```text
x0 -> x1 -> ... -> xH
```

Time is derived from such chains of relation. It is not a separate primitive.

## Derived reachability

Reachable futures are derived in the usual way:

```text
Reach_H(x) = { y in X : y is reachable from x in <= H steps }
```

Capacity, at this level, is just available future transformation space:

```text
Capacity_H(x) = Reach_H(x)
```

or as a count:

```text
cap_H(x) = |Reach_H(x)|
```

Do not implement capacity as an energy, slack, or resource coordinate at this level. That risks turning the substrate into a resource-management game.

## Asymmetry

Asymmetry is not a primitive tuple element.

It is the non-equivalence of future consequences.

For states:

```text
Asym_H(x, y) iff Reach_H(x) != Reach_H(y)
```

For transitions:

```text
Asym_H(x -> y)
```

is measured by how the reachable future set changes after taking the transition.

Asymmetry becomes meaningful when neutral transformations open, preserve, contract, or redirect reachable futures differently.

## Why admissibility cannot stay opaque

The earlier minimal tuple:

```text
RFS = (X, ->, A)
```

where `A subset X` is an admissible set, is mathematically convenient but too opaque. If `A` is arbitrary, the probe can be hand-designed by choosing the admissible set.

The empirical question requires a more explicit answer to:

```text
reachable futures of what?
```

Whole-field reachability answers this by treating the whole graph as the object. That loses the dynamics that produce bounded identity and agency-like structure.

The current answer is:

```text
reachable futures of derived bounded structures.
```

## Boundary as scaled distinction

Boundary is not a primitive.

Boundary is distinction at a higher relational scale:

```text
boundary = scaled distinction over relations
```

Equivalently, boundary is a Markov-blanket-like inside/outside/interface separation derived from the relational substrate.

We should not import full Free Energy Principle machinery here. The relevant idea is only the minimal boundary concept: a bounded process is a relational structure whose internal, external, and interface relations can be distinguished.

## Boundary extraction is probe-side

Let:

```text
E_sigma(S) -> M_sigma
```

where:

```text
E_sigma:
  boundary extraction rule at scale sigma

M_sigma:
  set of derived bounded-structure candidates at that scale
```

The extraction rule is not part of the primitive substrate. It is a probe/analysis choice.

This distinction matters:

```text
substrate:
  (X, ->)

analysis/probe machinery:
  E_sigma, continuity criterion, horizon, perturbation relation
```

A full experiment can therefore be written:

```text
Experiment = (X, -> ; E_sigma, ~=_sigma, H, P)
```

The semicolon is intentional. The substrate is left of the semicolon. Probe choices are right of it.

## Minimal identity

Identity is the unavoidable derived object.

Reachable futures require an anchor:

```text
reachable futures of what?
```

A derived bounded structure `mu in M_sigma` supplies that anchor.

Identity is:

```text
identity = continuity of a derived bounded structure through neutral transformations
```

or:

```text
identity = maintained scaled distinction through relation
```

Let `~=_sigma` be a structural continuity relation between boundary signatures at scale `sigma`.

For an initial state `x0` and bounded-structure candidate `mu0`, identity-relative admissibility is:

```text
A_mu(x0) = { x in X : mu(x) ~=_sigma mu0 }
```

This is not a goodness condition. It only says that the bounded structure under study remains identifiable as itself or a valid successor.

## Identity-preserving futures

The central object becomes:

```text
F_H^mu(x0) =
  { y in X :
      exists path x0 -> x1 -> ... -> y
      such that for all t, mu(xt) ~=_sigma mu0 }
```

Plain meaning:

```text
F_H^mu(x0):
  reachable futures of the bounded structure mu
```

This replaces whole-field reachability as the object of interest.

## Coherence and dissipation

Coherence and dissipation should not be primitive state variables.

At this level, transformation is neutral.

Relative to a bounded identity `mu`, a transformation can be read by how it changes identity-preserving futures.

For `x -> y`:

```text
rho_H^mu(x -> y) = |F_H^mu(y)| / max(1, |F_H^mu(x)|)
```

Interpretation:

```text
rho > 1:
  future-expanding relative to the bounded identity

rho approximately 1:
  coherence-preserving relative to the bounded identity

rho < 1:
  future-contracting / dissipative-like relative to the bounded identity
```

Dissipation is therefore not an intrinsic property of transformation. It is a viability-relative reading of transformation that contracts identity-preserving futures.

Coherence is the inverse reading: transformation that preserves the bounded identity's future-bearing continuity.

## Viability

Viability is identity-preserving reachability.

A bounded structure is viable at horizon H when:

```text
F_H^mu(x0) is nonempty
```

or, for stricter probes:

```text
|F_H^mu(x0)| exceeds a predeclared threshold
```

The threshold must be declared before results and audited against controls.

## Recovery

Perturbation is probe-side, not substrate-side.

Let:

```text
P subset X x X
```

be a perturbation relation.

The capture basin back into identity-continuity is:

```text
Capt_H(A_mu) =
  { x in X : exists path from x into A_mu within H steps }
```

Recovery means:

```text
Recover_H^mu(x) iff
  for perturbations y of x,
  y in Capt_H(A_mu)
```

The universal or existential quantifier over perturbations should be stated explicitly in each probe.

## Interference and coupled bounded processes

The older internal term `multifield` should be treated as historical.

The broader term is:

```text
coupled bounded processes
```

In the current formalism, interference is native but derived.

If the same substrate yields multiple bounded structures:

```text
M = { mu1, mu2, ..., mun }
```

then for each identity:

```text
F_H^mui(x)
```

and for a set of identities J:

```text
F_H^J(x)
```

means reachable futures preserving all identities in J.

For two identities:

```text
F_H^{mu1, mu2}(x)
```

is the joint identity-preserving future set.

Compatibility:

```text
both bounded structures retain identity-preserving futures together
```

Capture / local-global divergence:

```text
F_H^{mu1} preserved or expanded
while F_H^{mu2} or F_H^{mu1,mu2} contracts
```

This replaces hand-coded cross-field enable/obstruct effects. Interference is now the geometry of overlapping identity-preserving reachable futures in the same transition substrate.

## Current empirical ladder

The next empirical ladder should be:

```text
RFS-MB0:
  derive bounded structures and compute identity-preserving futures

RFS-MB1:
  perturbation and recovery of identity-continuity

RFS-MB2:
  coupled bounded processes; compatibility, capture, erasure

RFS-MB3:
  scale hierarchy; nested or composable blankets / bounded structures

RFS-MB4:
  constructor candidates; repeatable transformation capacity of bounded processes
```

The first step should not add energy economies, scalar objectives, or hand-designed viability vectors.

## Guardrails

Do not encode these as primitive state variables in the next substrate:

```text
energy
slack
coherence
dissipation
capacity
repair
optionality
Omega score
pseudo-Omega label
```

Instead derive them from:

```text
reachable futures
identity-continuity
capture/recovery basins
future contraction
joint identity preservation
```

## Claim boundary

Allowed current claim:

```text
We are developing a minimal transition-system formalism in which bounded structures
are derived from relational dynamics, and the object of study is the reachable
futures that preserve those derived identities.
```

Not yet allowed:

```text
Omega has been detected.
The extracted bounded structures are agents.
Markov blankets fully solve identity.
Coupled-process interference demonstrates alignment relevance.
```

## Bottom line

The current minimal formalism is:

```text
Substrate:
  S = (X, ->)

Probe:
  E_sigma, ~=_sigma, H, optional P

Object:
  F_H^mu(x) = identity-preserving reachable futures of a derived bounded structure
```

This keeps the substrate minimal while making explicit the missing object: the bounded identity whose futures are being tracked.
