# Minimal Compatibility Roadmap

Theory-side rationale for the RFS-MB0 pairwise compatibility probe

Status: working theory note

## Guiding discipline

The current goal is not to validate Omega directly.

The goal is to chisel toward the smallest mathematical object that could support Omega if such an object exists at all.

The core discipline is:

```text
principled
parsimonious
predictive
```

Principled:
  every higher claim must be derived from declared primitives and probe machinery.

Parsimonious:
  do not introduce structure before it is forced by the object.

Predictive:
  the formalism must distinguish cases that weaker formalisms confuse.

A beautiful theory that cannot survive fakeouts is not useful.

A minimal object that exposes a real distinction is valuable even if the broader theory must later be revised.

## Starting point

The current minimal substrate is:

```text
S = (X, ->)
```

where:

```text
X:
  finite distinction space

->:
  neutral transition relation
```

The substrate is intentionally austere.

It does not contain:

```text
value
valuerhood
agency
reward
utility
preference
energy
thermodynamic cost
free energy
coherence score
Omega label
pseudo-Omega label
moral status
```

Those may become interpretations or later constraints.

They are not primitives.

## Why identity is central

The broader intuition is:

```text
value exists only where there are valuers
```

A valuer cannot be a momentary state.

A valuer requires some form of identity through time: a continuing locus for which different futures can matter.

Therefore the empirical arm must first ask whether bounded identities can be derived from neutral dynamics.

But the current minimal program should not start by defining full valuerhood.

It should start lower:

```text
Can bounded identity candidates be derived?
Can their identity-preserving futures be measured?
Can individual continuation be separated from compatibility?
```

Only after this should the project escalate toward valuerhood, active inference, thermodynamics, or ethics.

## Derived identity extractor

The probe-side extraction rule is written:

```text
E_sigma(S) -> M_sigma
```

where:

```text
sigma:
  scale / resolution parameter

M_sigma:
  finite set of derived bounded-structure candidates
```

`E_sigma` is not a hand-labeler.

It should be a derived functional of the primitive substrate:

```text
E_sigma = Extract_sigma(X, ->)
```

The experimenter may choose which admissible extraction functional to test, but once declared it must use only relational information from `(X, ->)` and the scale parameter `sigma`.

It must not use:

```text
Omega labels
value labels
reward labels
semantic object labels
hand-coded viability labels
post-hoc result classes
```

At this stage, the admissible family of extractors remains an open research problem.

That is acceptable.

The first gate can still proceed if the extractor is declared, deterministic, simple, and fakeout-tested.

## Identity-preserving futures

For a candidate identity:

```text
mu in M_sigma
```

let:

```text
A_mu(x0)
```

be the token-continuity region for `mu` from initial state `x0` under the declared continuity relation.

Define singleton identity-preserving futures:

```text
F_H^mu(x0) =
  { y in X :
      exists path x0 -> x1 -> ... -> y of length <= H
      such that for all t, xt in A_mu(x0) }
```

This asks:

```text
Can identity mu continue over horizon H?
```

This is necessary but not sufficient.

A locally viable identity may still degrade broader compatibility.

## Why singleton viability is too weak

Individual identity preservation can overcall positives.

Examples:

```text
stasis:
  token persists without meaningful continuation dynamics

clock:
  phase recurrence mimics identity

terminal attractor:
  persistence by future-space collapse

parasite:
  one identity persists by degrading another

singleton optimizer:
  one identity expands by erasing alternatives
```

Therefore the first step beyond singleton viability is not full Omega.

It is pairwise compatibility.

## Pairwise joint identity-preserving futures

For two candidates:

```text
mu, nu in M_sigma
```

define:

```text
F_H^{mu,nu}(x0) =
  { y in X :
      exists path x0 -> x1 -> ... -> y of length <= H
      such that for all t,
        xt in A_mu(x0)
        and
        xt in A_nu(x0) }
```

This asks:

```text
Can identities mu and nu continue together over horizon H?
```

This is the smallest compatibility object.

It distinguishes:

```text
mu can continue alone
nu can continue alone
mu and nu can continue together
```

The first validation gate is whether this distinction has diagnostic power.

## Pairwise compatibility regimes

For a pair `(mu, nu)`, the basic regimes are:

```text
neither viable:
  F_H^mu empty
  F_H^nu empty

one viable:
  exactly one singleton future set is nonempty

pairwise compatible:
  F_H^mu nonempty
  F_H^nu nonempty
  F_H^{mu,nu} nonempty

pairwise incompatible:
  F_H^mu nonempty
  F_H^nu nonempty
  F_H^{mu,nu} empty
```

Pairwise incompatibility is not the same as pseudo-Omega.

It may be symmetric, accidental, resource-driven, or caused by a bad extractor.

## Local-preserving / joint-contracting regime

The old term `pseudo-Omega` should be deprecated in empirical outputs.

The minimal public phrase is:

```text
local-preserving / joint-contracting regime
```

This is a special asymmetric failure pattern.

For a transition or trajectory segment:

```text
tau: x -> ... -> y
```

compare:

```text
F_H^mu(x)       vs F_H^mu(y)
F_H^nu(x)       vs F_H^nu(y)
F_H^{mu,nu}(x)  vs F_H^{mu,nu}(y)
```

A local-preserving / joint-contracting signature is:

```text
F_H^mu(y) remains viable or expands
while
F_H^nu(y) and/or F_H^{mu,nu}(y) contracts or vanishes
```

Plain meaning:

```text
mu preserves itself while reducing compatibility with nu
```

This is the first minimal local/global divergence pattern.

Do not call it Omega or pseudo-Omega in result claims.

## Why not full lattice yet

The natural extension is to define joint futures for any subset:

```text
F_H^J(x), for J subset M_sigma
```

This would induce an order structure over compatible identity sets.

Eventually this may be the right mathematical image for the agentic field.

But the project has not earned that step yet.

The first gate is pairwise only.

If pairwise joint futures add no diagnostic information beyond singleton futures, then full lattices, topology, sheaves, cohomology, and field language are premature.

## Why not topology yet

Topology and sheaf-like language may eventually become relevant if the project finds robust local-to-global compatibility failures, such as:

```text
all pairs compatible
but no triple/global joint continuation exists
```

That would be a real gluing problem.

But before asking whether local compatibility glues globally, the project must first show that pairwise compatibility itself is a meaningful object.

Therefore defer:

```text
simplicial complexes
topological invariants
cohomology
sheaves
gluing obstructions
```

until pairwise compatibility has been validated.

## Why not churn yet

Real Omega-compatible continuation cannot require every identity token to persist forever.

Regenerative churn, repair, reproduction, successor identity, and lineage continuity are essential later.

But they add another degree of freedom:

```text
mu token persists
```

versus:

```text
mu lineage continues through successor nu
```

The first gate should use token continuity only.

Lineage can be introduced only after token pairwise compatibility is understood.

The likely roadmap is:

```text
RFS-MB0a:
  singleton token futures

RFS-MB0b:
  pairwise token joint futures

RFS-MB1:
  perturbation and recovery

RFS-MB1.5:
  lineage / churn-compatible futures

RFS-MB2:
  coupled bounded-process compatibility and local/global divergence
```

The current probe is RFS-MB0b.

## Why not richness thresholds yet

Existing theory notes distinguish lushness from raw entropy and raw path count.

Lushness means structured branching that propagates, not mere largeness.

However, the first pairwise gate should not define compatibility through a hand-set richness threshold.

The formal floor is:

```text
F_H != empty
```

Counts, ratios, diversity, redundancy, bottlenecks, recovery basins, and future-profile diversity may be reported as diagnostics.

They are not the definition.

This prevents premature scalarization.

## Roadmap

### Gate 0: exact reachable-futures floor

Already underway through RFS0.

Purpose:

```text
Can finite reachable futures, viability kernels, capture basins, and strict filters
be computed exactly and cheaply enough to support substrate work?
```

Status:

```text
promising as measurement floor
not validation
controls remain strong
```

### Gate 1: derived token identity

Question:

```text
Can candidate bounded identities be derived from (X, ->) through E_sigma?
```

Necessary outputs:

```text
M_sigma
A_mu(x)
F_H^mu(x)
```

Failure modes:

```text
everything is one identity
only exact recurrence counts
clock/phase fakeout
terminal attractor fakeout
random recurrence fakeout
label dependence
```

### Gate 2: pairwise compatibility

Question:

```text
Can pairwise joint identity-preserving futures reveal compatibility failures
that singleton futures miss?
```

Necessary outputs:

```text
F_H^mu(x)
F_H^nu(x)
F_H^{mu,nu}(x)
```

Target distinctions:

```text
pairwise compatible
pairwise incompatible
local-preserving / joint-contracting
mutual support
component erasure
capture-like degradation
```

This is the immediate next probe.

### Gate 3: perturbation and recovery

Question:

```text
Do identity and pairwise compatibility survive perturbation?
```

Move from:

```text
can continue
```

to:

```text
can recover
```

This should remain non-semantic: recovery means re-entry into identity-preserving or joint identity-preserving futures, not return to an exact state.

### Gate 4: lineage and churn

Question:

```text
Can compatibility be preserved through successor identities rather than exact tokens?
```

Introduce:

```text
mu =>_sigma nu
```

and lineage-compatible future sets.

This is required for living systems, ecologies, institutions, and regenerative continuity.

It is not required for the first pairwise smoke.

### Gate 5: higher-order compatibility

Question:

```text
Do pairwise compatibilities compose into larger compatible sets?
```

Introduce:

```text
F_H^J(x), for |J| > 2
```

Only here does the full compatibility-lattice picture become justified.

### Gate 6: generativity / lushness

Question:

```text
Do compatible futures preserve the capacity for further compatible futures?
```

This is where existing lushness language may re-enter:

```text
structured branching that propagates
```

But it must be grounded in prior gates.

### Gate 7: physical realization constraints

Question:

```text
What does it cost to maintain identity, compatibility, recovery, and generativity
in a physical substrate?
```

This is where ECHO / thermodynamic constraints may re-enter.

Do not begin here.

### Gate 8: valuerhood and agency

Question:

```text
When does a bounded identity become a valuer or agent?
```

This requires identity, continuability, recovery, self-maintenance, and asymmetric future consequence.

It is outside the immediate empirical arm.

## Expected first result classes

For the pairwise smoke, use modest result language:

```text
singleton_overcall:
  singleton futures viable but pairwise future empty

pairwise_compatible:
  both singleton futures and joint future viable

pairwise_incompatible:
  both singleton futures viable but joint future empty

local_A_joint_contracting:
  A singleton future preserved or expanded while joint future contracts

local_B_joint_contracting:
  B singleton future preserved or expanded while joint future contracts

mutual_support_like:
  both singleton and joint futures robustly viable

control_mimic:
  null/control produces the same pattern as structured regime
```

Do not use:

```text
Omega-positive
pseudo-Omega detected
valuer detected
agent detected
```

## Interpretive boundary

This roadmap treats the foundational papers as speculative provenance, not doctrine.

They helped motivate the search for:

```text
identity
recoverability
future-bearing continuation
compatibility
local/global divergence
lushness
thermodynamic feasibility
valuerhood
```

But the current empirical arm should not import those concepts as primitives.

The new formalism is trying to resolve their handwaving by deriving the smallest testable objects from neutral dynamics.

## Summary

The immediate next object is:

```text
F_H^{mu,nu}(x)
```

The immediate next question is:

```text
Can two derived bounded identities continue together?
```

The immediate local/global divergence question is:

```text
Can one identity preserve itself while joint compatibility contracts?
```

The immediate discipline is:

```text
no full lattice
no topology
no churn
no richness threshold
no Omega claim
```

The project earns each later abstraction only by passing the previous gate.
