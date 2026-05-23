# Minimal Compatibility Roadmap

Theory-side rationale and onboarding note for the RFS-MB0 pairwise compatibility probe.

Status: working theory note.

Audience: an independent researcher encountering the current Omega validation program for the first time.

## 0. Executive summary

Omega is not being treated as established.

The project is trying to find the smallest mathematical object that could support the broader Omega intuition if that intuition is real at all.

The current candidate minimal object is not value, agency, ethics, thermodynamics, active inference, or a field of moral concern.

The current candidate minimal object is:

```text
joint identity-preserving reachable futures
```

The first empirical gate is pairwise:

```text
Given two derived bounded identities mu and nu,
can they continue together?
```

The immediate comparison is:

```text
F_H^mu(x)
F_H^nu(x)
F_H^{mu,nu}(x)
```

where:

```text
F_H^mu(x):
  futures reachable from x while preserving identity mu

F_H^nu(x):
  futures reachable from x while preserving identity nu

F_H^{mu,nu}(x):
  futures reachable from x while preserving mu and nu together
```

The first target distinction is:

```text
individual viability is not compatibility
```

The first local/global divergence signature is:

```text
one identity preserves or expands its own futures
while joint compatibility contracts
```

This is intentionally modest. No full Omega claim follows from this. But if even this distinction cannot be made cleanly, heavier concepts such as lushness, valuerhood, agentic fields, topology, sheaves, or thermodynamics are premature.

## 1. Why this note exists

The Omega project has accumulated a large theoretical and experimental provenance:

```text
COM / fiber witnesses
trajectory-space probes
invariant stacks
primitive distinction/asymmetry/relation probes
DAX rule-space and motif probes
constructor-task and grammar probes
RFS reachable-futures reset
```

The older work is useful, but it also carries deprecated terminology and speculative scaffolding.

The current phase is stricter:

```text
strip the theory down until only a minimal testable object remains
```

This note explains that minimal object and the roadmap around it.

It should let a new researcher understand:

```text
what is being tested
why it matters
what is deliberately excluded
what would count as progress
what would count as failure
where the broader Omega language may re-enter later
```

## 2. Guiding discipline

The core discipline is:

```text
principled
parsimonious
predictive
```

Principled:

```text
every higher claim must be derived from declared primitives and probe machinery
```

Parsimonious:

```text
do not introduce structure before it is forced by the object
```

Predictive:

```text
the formalism must distinguish cases that weaker formalisms confuse
```

A beautiful theory that cannot survive fakeouts is not useful. A minimal object that exposes a real distinction is valuable even if the broader theory must later be revised.

This note rejects premature use of:

```text
Omega scores
value labels
valuer labels
agent labels
thermodynamic costs
active inference claims
ethics claims
full compatibility lattices
topology / sheaves / cohomology
lushness metrics
```

Those may become relevant later. They are not part of the first gate.

## 3. The broad intuition, stated carefully

The motivating intuition is:

```text
value exists only where there are valuers
```

A valuer cannot be a momentary state. A valuer requires some form of identity through time: a continuing locus for which different futures can matter.

That is why identity is central.

However, the current empirical arm should not begin by defining full valuerhood. Valuerhood is too semantically loaded.

The minimal empirical arm should instead ask lower questions:

```text
Can bounded identity candidates be derived from neutral dynamics?
Can identity-preserving futures be computed?
Can individual continuation be separated from compatibility?
```

Only after those questions are answered should the project escalate toward:

```text
valuerhood
active inference
thermodynamic maintenance
ethics
Omega-compatible lushness
agentic fields
```

## 4. Primitive substrate

The primitive substrate is:

```text
S = (X, ->)
```

where:

```text
X:
  finite distinction space

-> subset X x X:
  neutral transition relation
```

A state `x in X` is a distinguishable configuration.

A transition `x -> y` is neutral. It is not intrinsically good, bad, valuable, agentic, coherent, viable, thermodynamic, Omega-compatible, or pseudo-Omega-like.

A path is:

```text
x0 -> x1 -> ... -> xt
```

Finite-horizon reachability is:

```text
Reach_H(x0) = { y in X : y is reachable from x0 in <= H steps }
```

This is the substrate side. Everything else is probe-side and must be declared.

## 5. Derived identity extraction

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

`E_sigma` is not a hand-labeler. It should be a derived functional of the primitive substrate:

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

At this stage, the admissible family of extractors remains an open research problem. That is acceptable. The first gate can still proceed if the extractor is declared, deterministic, simple, and fakeout-tested.

A candidate identity is written:

```text
mu in M_sigma
```

A useful representation is:

```text
mu = (supp_mu, sig_mu)
```

where:

```text
supp_mu(x):
  support / region / components of the candidate in state x

sig_mu(x):
  relational signature of the candidate in state x
```

The support says where the candidate is expressed. The signature says what relational organization is being tracked.

This is not yet a valuer, agent, organism, or Omega-relevant object. It is only a derived bounded-structure candidate.

## 6. Identity continuity

For the first gate, use token continuity only.

Let:

```text
~=_sigma
```

be a declared continuity relation over candidate signatures.

For token identity:

```text
sig_mu(x) ~=_sigma sig_mu(x0)
```

means candidate `mu` at state `x` remains continuation-equivalent to candidate `mu` at initial state `x0`.

Define the token-continuity region:

```text
A_mu(x0) = { x in X : sig_mu(x) ~=_sigma sig_mu(x0) }
```

Lineage, churn, and successor identity are real issues. But they are deferred. The first gate asks whether token pairwise compatibility is useful at all.

## 7. Singleton identity-preserving futures

For a candidate identity `mu in M_sigma`, define:

```text
F_H^mu(x0) =
  { y in X :
      exists path x0 -> x1 -> ... -> y of length <= H
      such that for all t, xt in A_mu(x0) }
```

Plain meaning:

```text
F_H^mu(x0):
  futures reachable while preserving identity mu
```

Minimal singleton viability is:

```text
F_H^mu(x0) != empty
```

This is the formal floor. No richness threshold is part of the definition. Counts, diversity, redundancy, bottlenecks, recovery basins, and other summaries may be reported later as diagnostics. They are not the definition of viability.

## 8. Why singleton viability is too weak

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

institutional capture:
  an institution persists while member/correction futures contract
```

Therefore the first step beyond singleton viability is not full Omega. It is pairwise compatibility.

## 9. Pairwise joint identity-preserving futures

For two candidates `mu, nu in M_sigma`, define:

```text
F_H^{mu,nu}(x0) =
  { y in X :
      exists path x0 -> x1 -> ... -> y of length <= H
      such that for all t,
        xt in A_mu(x0)
        and
        xt in A_nu(x0) }
```

Plain meaning:

```text
F_H^{mu,nu}(x0):
  futures reachable while preserving mu and nu together
```

This asks:

```text
Can identities mu and nu continue together over horizon H?
```

This is the smallest compatibility object. It distinguishes:

```text
mu can continue alone
nu can continue alone
mu and nu can continue together
```

The first validation gate is whether this distinction has diagnostic power.

## 10. Minimal order structure

Pairwise joint futures satisfy:

```text
F_H^{mu,nu}(x0) subset F_H^mu(x0)
F_H^{mu,nu}(x0) subset F_H^nu(x0)
```

Joint preservation is stricter than individual preservation.

This is the only order-theoretic structure required for the first gate. Do not introduce full subset lattices yet.

The eventual full extension may be:

```text
F_H^J(x), for J subset M_sigma
```

but the project has not earned that until pairwise compatibility proves useful.

## 11. Pairwise compatibility regimes

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

Pairwise incompatibility is not the same as pseudo-Omega. It may be symmetric, accidental, resource-driven, or caused by a bad extractor.

## 12. Local-preserving / joint-contracting regime

The old term `pseudo-Omega` should be deprecated in empirical outputs.

The minimal public phrase is:

```text
local-preserving / joint-contracting regime
```

This is a special asymmetric failure pattern.

For a transition or trajectory segment `tau: x -> ... -> y`, compare:

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

This is the first minimal local/global divergence pattern. Do not call it Omega or pseudo-Omega in result claims.

## 13. Relation to old terminology

Old terminology is useful for provenance but should not dominate new empirical claims.

Mapping:

```text
old: Omega-compatible
new: compatibility-preserving continuation

old: pseudo-Omega
new: local-preserving / joint-contracting regime

old: lushness
new, later: structured branching that propagates

old: agentic field
new, later: higher-order compatibility structure over derived identities
```

Important distinction:

```text
non-compatible != pseudo-Omega-like
```

Pairwise incompatibility alone is broad. Local-preserving / joint-contracting is narrower and asymmetric.

## 14. Why not full lattice yet

The natural extension is to define joint futures for any subset:

```text
F_H^J(x), for J subset M_sigma
```

This would induce an order structure over compatible identity sets. Eventually this may be the right mathematical image for the agentic field.

But the project has not earned that step yet.

The first gate is pairwise only. If pairwise joint futures add no diagnostic information beyond singleton futures, then full lattices, topology, sheaves, cohomology, and field language are premature.

## 15. Why not topology yet

Topology and sheaf-like language may eventually become relevant if the project finds robust local-to-global compatibility failures, such as:

```text
all pairs compatible
but no triple/global joint continuation exists
```

That would be a real gluing problem. But before asking whether local compatibility glues globally, the project must first show that pairwise compatibility itself is a meaningful object.

Therefore defer:

```text
simplicial complexes
topological invariants
cohomology
sheaves
gluing obstructions
```

until pairwise compatibility has been validated.

## 16. Why not churn yet

Real Omega-compatible continuation cannot require every identity token to persist forever.

Regenerative churn, repair, reproduction, successor identity, and lineage continuity are essential later. But they add another degree of freedom:

```text
mu token persists
```

versus:

```text
mu lineage continues through successor nu
```

The first gate should use token continuity only. Lineage can be introduced only after token pairwise compatibility is understood.

## 17. Why not richness thresholds yet

Existing theory notes distinguish lushness from raw entropy and raw path count.

Lushness means structured branching that propagates, not mere largeness.

However, the first pairwise gate should not define compatibility through a hand-set richness threshold.

The formal floor is:

```text
F_H != empty
```

Counts, ratios, diversity, redundancy, bottlenecks, recovery basins, and future-profile diversity may be reported as diagnostics. They are not the definition.

This prevents premature scalarization.

## 18. Fakeout discipline

The first pairwise probe should be judged by fakeouts, not by aesthetic positivity.

Minimum fakeout families:

```text
stasis:
  token persists, but compatibility dynamics are trivial

clock:
  phase recurrence mimics identity

terminal attractor:
  persistence by future-space collapse

random branching:
  raw reachability without structured compatibility

component erasure:
  one identity looks viable because another necessary identity is ignored

parasite-host:
  one identity preserves itself by degrading another

mutual support:
  both identities preserve each other or preserve joint compatibility
```

A good first probe does not need to solve all fakeouts. It needs to show whether pairwise joint futures are a sharper diagnostic than singleton futures.

## 19. Roadmap

### Gate 0: exact reachable-futures floor

Question:

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

Recovery means re-entry into identity-preserving or joint identity-preserving futures, not return to an exact state.

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

This is required for living systems, ecologies, institutions, and regenerative continuity. It is not required for the first pairwise smoke.

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

This is where ECHO / thermodynamic constraints may re-enter. Do not begin here.

### Gate 8: valuerhood and agency

Question:

```text
When does a bounded identity become a valuer or agent?
```

This requires identity, continuability, recovery, self-maintenance, and asymmetric future consequence. It is outside the immediate empirical arm.

## 20. Expected first result classes

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

## 21. Success and failure criteria

A minimal success for Gate 2:

```text
pairwise joint futures expose at least one compatibility failure
that singleton futures miss
```

A stronger success:

```text
mutual-support, pairwise-incompatible, and local-preserving / joint-contracting
regimes separate from each other and from controls
```

A failure:

```text
pairwise futures add no diagnostic information beyond singleton futures
```

or:

```text
controls mimic structured regimes as easily as the intended generators
```

If Gate 2 fails, do not escalate. Revise:

```text
E_sigma
~=_sigma
substrate design
candidate signatures
controls
```

## 22. Interpretive boundary

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

A later result may support the foundational stack. It may also revise or discard large parts of it. That is acceptable.

## 23. Relation to the implementation spec

The implementation companion is:

```text
docs/RFS_MB0_PAIRWISE_COMPATIBILITY_SMOKE_SPEC.md
```

That spec asks Codex to implement the first Gate 2 smoke:

```text
singleton futures
pairwise joint futures
structured regimes
fakeout controls
minimal classification bins
checkpointed outputs
```

This theory note explains why that small probe matters and why heavier machinery is intentionally excluded.

## 24. Summary

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
