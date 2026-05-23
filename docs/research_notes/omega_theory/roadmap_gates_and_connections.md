# Roadmap Gates and Mathematical Connections

Status: small reorientation note

Purpose: keep the project grounded when theory-side exploration starts branching.

## Core discipline

```text
principled
parsimonious
predictive
```

Do not import machinery because it is interesting.

Import machinery only when a gate creates the problem that machinery solves.

The project should remain killable at every gate.

## Current minimal object

The current empirical object is:

```text
F_H^mu(x)
F_H^nu(x)
F_H^{mu,nu}(x)
```

where:

```text
F_H^mu(x):
  futures preserving candidate identity mu

F_H^nu(x):
  futures preserving candidate identity nu

F_H^{mu,nu}(x):
  futures preserving mu and nu together
```

Immediate question:

```text
Can two derived bounded identities continue together?
```

Immediate divergence question:

```text
Can one identity preserve itself while joint compatibility contracts?
```

No full Omega claim follows from this.

## Gate 0: Exact reachable-futures floor

Question:

```text
Can finite reachable futures be computed exactly and cheaply enough to support substrate work?
```

Natural machinery:

```text
finite graph reachability
BFS / DFS / dynamic programming
finite transition systems
formal-methods-style state exploration
```

Earns:

```text
measurement floor
```

Does not earn:

```text
identity
valuerhood
compatibility
Omega
```

## Gate 1: Derived token identity

Question:

```text
Can candidate bounded identities be derived from (X, ->)?
```

Objects:

```text
E_sigma(S) -> M_sigma
A_mu(x)
F_H^mu(x)
```

Natural machinery:

```text
graph structure
strongly connected components
cuts / separators
role signatures
simulation / bisimulation / approximate bisimulation
quotients and fibers
behavioral equivalence
```

Key warning:

```text
E_sigma must not be a hand-labeler.
```

Failure modes:

```text
everything is one identity
only exact recurrence counts
clock/phase fakeout
terminal attractor fakeout
label dependence
random recurrence
```

## Gate 2: Pairwise compatibility

Question:

```text
Can pairwise joint futures reveal compatibility failures that singleton futures miss?
```

Objects:

```text
F_H^mu(x)
F_H^nu(x)
F_H^{mu,nu}(x)
```

Natural machinery:

```text
constraint satisfaction
conjunction of path constraints
reachability under multiple invariants
safety properties
controlled invariance
```

Key distinction:

```text
pairwise incompatibility != pseudo-Omega-like behavior
```

The narrower asymmetric signature is:

```text
local-preserving / joint-contracting
```

This is the current probe.

## Gate 3: Perturbation and recovery

Question:

```text
Can identity and pairwise compatibility recover after disruption?
```

Move from:

```text
can continue
```

to:

```text
can recover
```

Natural machinery:

```text
viability theory
capture basins
recovery basins
controlled invariant sets
robust control
reach-avoid analysis
```

Key warning:

```text
recovery is re-entry into identity-preserving or joint-preserving futures,
not return to an exact state.
```

## Gate 3.5: Cybernetic regulation

Question:

```text
Is recovery passive, or does the bounded process regulate conditions of its own continuability?
```

Natural machinery:

```text
cybernetics
feedback control
homeostasis
Ashby's law of requisite variety
essential variables
regulation under disturbance
```

Why it matters:

```text
This is a likely bridge from bounded identity to proto-valuerhood.
```

Do not start here.

Earn this only after identity and recovery are meaningful.

## Gate 4: Lineage and churn

Question:

```text
Can compatibility persist through successor identities rather than exact token preservation?
```

Objects:

```text
mu =>_sigma nu
F_H^{mu,lin}(x)
F_H^{mu,nu,lin}(x)
```

Natural machinery:

```text
automata theory
simulation preorders
approximate bisimulation
symbolic dynamics
lineage tracking
state abstraction
```

Why it matters:

```text
Real continuability includes repair, replacement, reproduction, turnover, and succession.
```

## Gate 5: Higher-order compatibility

Question:

```text
Do pairwise compatibilities compose into larger compatible sets?
```

Objects:

```text
F_H^J(x), for |J| > 2
```

Natural machinery:

```text
constraint hypergraphs
higher-order CSP
compatibility complexes
simplicial complexes, if earned
```

Key possible discovery:

```text
all pairs compatible, but triple/global compatibility fails
```

This is the first true local-to-global compatibility problem.

## Gate 6: Local-to-global structure

Question:

```text
Can locally compatible futures glue into a global compatible continuation?
```

Natural machinery:

```text
applied sheaf theory
cohomological obstructions
local-to-global consistency
descent
gluing failures
```

Speculative lens:

```text
local-preserving / joint-contracting regimes are failures of gluing.
```

Do not import this until Gates 2 and 5 force the problem.

## Gate 7: Generativity and lushness

Question:

```text
Do compatible futures preserve the capacity for further compatible futures?
```

Natural machinery:

```text
branching processes
symbolic dynamics
order theory
domain-theoretic approximation
recurrence / regeneration analysis
```

Existing concept:

```text
lushness = structured branching that propagates
```

Not:

```text
raw entropy
raw path count
maximum population
one agent's empowerment
mere noise branching
```

## Gate 8: Physical realization constraints

Question:

```text
What does it cost to maintain identity, recovery, compatibility, and generativity?
```

Natural machinery:

```text
nonequilibrium thermodynamics
information thermodynamics
resource-bounded control
maintenance cost
entropy production
```

Role:

```text
physical realization constraint
```

Not primitive for the first gates.

## Gate 9: Valuerhood and agency

Question:

```text
When does a bounded identity become a valuer or agent?
```

Likely requirements:

```text
identity
continuability
recovery
self-maintenance
asymmetric future consequence
action channels
possibly active inference / internal modeling
```

Natural machinery:

```text
cybernetics
active inference
Markov blankets
autopoiesis
multi-agent systems
game/control theory
major transitions in evolution
```

Claim boundary:

```text
Do not call extracted identities valuers before this gate is earned.
```

## Gate 10: Field / scale structure

Question:

```text
How do identities compose across scale without erasing lower-order continuability?
```

Natural machinery:

```text
category theory as bookkeeping
presheaves over scale
hierarchical systems
major evolutionary transitions
multi-scale control
scale-indexed compatibility
```

Speculative target:

```text
agentic field = higher-order compatibility structure over derived identities
```

Not primitive.

## Cross-cutting lenses

### Constraint satisfaction

Probably the natural home of the early formalism.

```text
identity = path constraint
compatibility = joint satisfiability
capture-like degradation = satisfying one constraint while destroying another
```

### Bisimulation and relatives

Useful for identity continuity.

```text
exact equality:
  too strict

bisimulation:
  strong behavioral equivalence

simulation / approximate bisimulation:
  possible bridge to continuity through transformation

lineage relation:
  successor identity through change
```

### Condensed / sheaf lens

Useful as a speculative hypothesis generator.

```text
Do not define the object only by points.
Define it by coherent behavior under probes.
```

Omega-relevant structure may eventually mean:

```text
stable compatibility under refinement of finite probes
```

Current baby version:

```text
pairwise compatibility = first gluing test
```

### Cybernetics

Not an omission from the theory.

It belongs after identity and recovery:

```text
recovery -> regulation -> self-maintenance -> proto-valuerhood
```

Cybernetics helps distinguish passive restoration from active regulation.

## Import rule

At each gate:

```text
use the nearest mature machinery
invent only the bridge
```

Omega should be bespoke only at the interfaces.

The components should be inherited from mature mathematics wherever possible.

## Bottom line

The project is broad because the object, if real, sits at an interface:

```text
identity
reachability
constraint satisfaction
recovery
regulation
compatibility
scale
generativity
physical realization
valuerhood
```

But the empirical path is narrow.

Current gate:

```text
F_H^mu
F_H^nu
F_H^{mu,nu}
```

Current test:

```text
Does pairwise joint compatibility reveal something singleton viability misses?
```

If yes, the project earns the next import.

If no, stop and revise.
