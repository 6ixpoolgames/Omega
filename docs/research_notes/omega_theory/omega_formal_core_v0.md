# Omega Formal Core v0

Distinction, Relation, and Asymmetry in Viable Future Propagation

Status: draft theory/process note  
Scope: clean-slate formal core after current and historical empirical branches  
Claim boundary: no Omega validation, no agency detection, no value detection, no valuerhood detection, no holdout claim, no universal signature claim.

## 0. Purpose

This note proposes a clean formal core for Omega after the empirical arm has ruled out or narrowed several earlier candidates.

The purpose is not to prove Omega. The purpose is to define the smallest formal stack that can explain why the surviving empirical objects matter, why the failed objects failed, and what future substrates should test.

This document is intentionally process-bearing. It is not elegant in the way a mature theory should eventually be elegant. It records the current layered structure of the project because the project has learned by failing through several simpler formulations.

The core thesis is:

```text
Distinctions matter only through relations.
Relations matter only through asymmetric future consequences.
Asymmetric future consequences become Omega-relevant only when viable
distinctions propagate, remain recoverable, survive quotienting, avoid
non-erasure failures, and remain compatible with broader future-bearing
structure.
```

Omega is therefore not raw entropy, survival, persistence, reachability, compression, reward, utility, or value. These may be diagnostics, gates, or downstream interpretations. The formal target is viable future-bearing propagation under admissible coarse-grainings, with recoverability, non-erasure, and compatibility constraints.

## 1. What the empirical arm has ruled out

The historical empirical arm suggests the following demotions.

### 1.1 Survival is not enough

A trajectory may persist while becoming trapped, brittle, unrecoverable, or destructive to broader future-bearing structure.

Survival is therefore a gate or background condition, not the Omega object.

### 1.2 Raw entropy is not enough

High entropy over future states can arise from noise, diffusion, bad quotienting, uncontrolled branching, or measurement artifacts.

Entropy may diagnose breadth after viability and propagation have already been established. It is not the primary object.

### 1.3 Static reachability is not enough

A state may have many reachable futures without preserving the distinctions that make those futures meaningful across horizon.

The object must be directional and horizon-indexed.

### 1.4 Static fibers are not enough

A quotient may expose large fibers at a time slice without showing that those fibers transport through time.

The object is not fiber size. The object is certified fiber transport.

### 1.5 Hand quotients are not enough

COM-like quotients can witness structure in toy substrates, but hand quotients do not solve the quotient problem.

The final object must be expressed relative to admissible quotients, and the search for a minimal predictive quotient remains open.

### 1.6 Learned quotients are not automatically enough

A learned quotient can split real structure, merge incompatible structure, inflate small fibers, overfit validation metrics, or erase component preservation.

Quotient learning must be audited, not assumed.

### 1.7 Scalar summaries are not enough

A scalar can summarize a structured signature, but it cannot replace the signature.

The primary Omega object should initially be a tuple or anatomy, not a single number.

### 1.8 Substrate response is not theory validation

A toy substrate can produce meaningful response structure without showing value, agency, identity, valuerhood, or Omega.

Positive substrate results are precursor evidence only.

## 2. Primitive substrate

Let a substrate be a tuple:

```text
S = (X, U, R, P, H)
```

where:

```text
X:
  state space

U:
  admissible interventions, transformations, controls, or transition-generating acts

R:
  admissible relation structure over states

P:
  transition kernel or stochastic transition rule, when available

H:
  admissible horizon set
```

In finite deterministic settings, `R` may be a directed graph. In stochastic settings, `P(x' | x, u)` may induce `R` by positive-probability support.

No agent, valuer, value function, reward, preference, or moral label is assumed at this level.

## 3. Primitive I: distinction

A distinction is a difference that can make a downstream difference under admissible dynamics.

Given states `x, y in X`, define future distributions under policy or intervention sequence `pi` over horizon `T`:

```text
F_T^pi(x) = distribution over X_T induced by starting at x and acting by pi
```

A pair `(x, y)` carries a future-relevant distinction over horizon `T` if:

```text
exists pi in Pi such that D(F_T^pi(x), F_T^pi(y)) > epsilon
```

where `D` is an admissible divergence or distinguishability measure.

A raw syntactic difference is not yet an Omega-relevant distinction. It becomes relevant only if it can affect future structure.

### 3.1 Action-relevant distinction

A distinction is action-relevant if there exist admissible interventions whose future consequences depend on it:

```text
A_T(x, y) = sup_{pi,pi'} D(F_T^pi(x), F_T^pi'(y))
```

A distinction is action-relevant when `A_T(x, y) > epsilon`.

### 3.2 Distinction field

For a substrate and horizon, the distinction field is the set or measure of distinctions that remain future-relevant:

```text
D_T(S) = { (x,y) in X x X : exists pi, D(F_T^pi(x), F_T^pi(y)) > epsilon }
```

This is not yet value. It is the substrate-level condition that differences can continue to matter.

## 4. Primitive II: relation

A relation is admissible continuity through transformation.

For states `x, y in X`:

```text
x R_u y
```

means that `y` can follow `x` under admissible transformation or intervention `u`.

The unlabelled transition relation is:

```text
x R y iff exists u in U such that x R_u y
```

In stochastic settings:

```text
x R_u y iff P(y | x, u) > 0
```

Relations define possible continuation. Without relation, distinction cannot propagate.

### 4.1 Relation is not mere adjacency

A relation is not merely graph adjacency. It is continuity under the substrate's admissible transformations.

Two states can be close under a metric and unrelated under admissible dynamics. Two states can be distant under a metric but related by an admissible transformation.

### 4.2 Relation-induced futures

For horizon `T`, define the reachable future set:

```text
Reach_T(x) = { y in X : exists path x = x_0 R x_1 R ... R x_T = y }
```

For stochastic systems, this may be replaced by positive-probability support or by a thresholded support.

Reachability is necessary but insufficient. Omega concerns what future-relevant distinctions do under this relation.

## 5. Primitive III: asymmetry

Asymmetry is non-equivalence of transformations in their future consequences.

A relation is asymmetric at horizon `T` if:

```text
x R y does not imply equivalent future structure from y back to x
```

More formally, define forward and reverse future structure:

```text
F_T(x -> y) = future structure after transition x -> y
F_T(y -> x) = future structure after transition y -> x
```

An asymmetric relation satisfies:

```text
D(F_T(x -> y), F_T(y -> x)) > epsilon
```

for an admissible future-structure divergence.

### 5.1 Forms of asymmetry

Asymmetry includes but is not limited to:

```text
directional asymmetry:
  one direction across a field is favored over the reverse

preservation asymmetry:
  changes to a macro-invariant are less available than preserving it

irreversibility:
  prior distinctions cannot be reconstructed from later states

trap asymmetry:
  entry into a region is easier than exit

horizon asymmetry:
  short-horizon and long-horizon consequences differ

component-erasure asymmetry:
  a joint structure persists by eliminating lower-rank variation
```

### 5.2 Asymmetry is the first nontrivial primitive

Distinctions without relations are inert.

Relations without asymmetry may produce motion but not directed future-structure consequences.

Asymmetry is where future-relevant structure first becomes nontrivial.

## 6. Horizons and future structure

Omega is horizon-indexed.

Let `H` be a set of horizons. For `T in H`, define a future structure object:

```text
Phi_T(x)
```

where `Phi_T(x)` may be a reachable set, transition distribution, frontier profile, quotient-fiber structure, or horizon-transport object.

A candidate Omega object must specify which future structure it uses.

### 6.1 Static endpoint objects are insufficient

Endpoint support alone may miss propagation, transport, recoverability, or non-erasure.

Therefore, the preferred empirical object is directional:

```text
T_{H_a -> H_b}
```

which asks how structure at an earlier horizon becomes structure at a later horizon.

### 6.2 Horizon response

A substrate may be stable at short horizons and unstable or amplified at long horizons.

Therefore horizon is a response coordinate:

```text
ResponseClass = f(horizon_pair, perturbation_family, perturbation_strength, probe, flow_mode)
```

A formal Omega proxy should not collapse all horizons into one number before response anatomy is inspected.

## 7. Viability as a gate

Let `V` be a viability predicate over trajectories:

```text
V(tau_{0:T}) in {0,1}
```

A trajectory is viable if it satisfies the relevant viability predicate across the horizon.

The viable future set is:

```text
F_T^V(x) = { tau_{0:T} : tau_0 = x and V(tau_{0:T}) = 1 }
```

Viability is necessary but not sufficient.

A system may be viable while:

```text
erasing distinctions;
collapsing recoverability;
destroying component structure;
capturing other future landscapes;
preserving only a brittle singleton path;
optimizing local continuation while degrading broader compatibility.
```

Thus viability is a gate. Omega concerns propagation of viable future-bearing structure through time.

## 8. Propagation

Propagation asks whether future-relevant distinctions continue to make a difference across horizon.

Given a distinction `d = (x,y)`, define its propagated distinguishability at horizon `T`:

```text
Prop_T(d) = sup_pi D(F_T^pi(x), F_T^pi(y))
```

A distinction propagates when:

```text
Prop_T(d) > epsilon
```

A substrate supports distinction propagation when a nontrivial set of future-relevant distinctions remains propagated across horizon.

### 8.1 Viable propagation

Viable propagation restricts to viable trajectories:

```text
Prop_T^V(d) = sup_pi D(F_T^{V,pi}(x), F_T^{V,pi}(y))
```

where `F_T^{V,pi}` is the future distribution conditioned or restricted to viable trajectories.

Viable propagation is stronger than reachability and stronger than survival.

### 8.2 Propagation is directional

Propagation is not a static property of a state. It depends on how distinctions move through relations across horizon.

Empirically, this motivates transport objects rather than endpoint counts.

## 9. Recoverability

Recoverability asks whether a degraded distinction or structure can be re-established by admissible dynamics.

Let `Pert` be a class of perturbations. For a structure `sigma`, perturbation `eta`, and recovery policy `rho`, define:

```text
Rec_T(sigma, eta) = sup_rho Similarity(sigma, Recover_T(eta(sigma), rho))
```

A structure is recoverable when:

```text
Rec_T(sigma, eta) > r_min
```

for relevant perturbations.

### 9.1 Recoverability is not exact restoration

Recoverability does not require returning to the identical microstate.

It requires restoring the future-relevant distinctions or quotient-level structure that support viable propagation.

### 9.2 Fragility

Fragility is low recoverability under relevant perturbations:

```text
Frag_T(sigma) = 1 - E_eta[Rec_T(sigma, eta)]
```

High local performance with high fragility is not Omega-compatible.

## 10. Quotients

A quotient or macro-map is:

```text
kappa: X -> Z
```

where `Z` is a macro-state space.

Quotients determine which macro-structures are treated as equivalent.

### 10.1 Admissible quotient

A quotient is admissible for Omega analysis only if it preserves enough future-relevant structure.

A quotient `kappa` is predictive over horizon `T` if:

```text
kappa(x) = kappa(y) implies D(F_T(x), F_T(y)) <= epsilon
```

for the future structure being studied.

A quotient is minimally admissible if it balances predictive sufficiency against complexity:

```text
kappa* = arg min_kappa [ L_prop(kappa) + lambda L_quotient(kappa) ]
```

where:

```text
L_prop:
  loss of viable propagation information under kappa

L_quotient:
  complexity or description length of kappa
```

The quotient problem remains unsolved. Current hand quotients and learned quotients are provisional instruments, not final objects.

### 10.2 Quotient failure modes

A bad quotient can:

```text
launder entropy:
  inflate breadth by merging incompatible states

split structure:
  fragment a coherent propagating macro-structure

merge incompatibles:
  hide future-relevant distinctions

erase components:
  preserve a joint macro-label while deleting lower-rank support

overfit:
  validate on a finite batch while losing horizon generalization

become identity:
  preserve everything but explain nothing

become all-one:
  erase everything while appearing simple
```

A formal Omega claim requires quotient audits.

## 11. Fibers

Given quotient `kappa`, the fiber over macro-state `z` is:

```text
kappa^{-1}(z) = { x in X : kappa(x) = z }
```

In trajectory form, the fiber at time or segment `t` is:

```text
R_t(z) = { tau in F_T^V : kappa(tau_t) = z }
```

Fibers represent lower-rank realizations of macro-structure.

### 11.1 Fiber mass

Fiber mass:

```text
M_t(z) = |R_t(z)|
```

or, in stochastic settings, probability mass.

Fiber mass alone is not Omega. A large fiber can be noisy, fragmented, unrecoverable, or non-transporting.

### 11.2 Fiber quality

A certified fiber should satisfy:

```text
sufficient mass;
non-singleton support;
nonfragmentation;
component preservation;
recoverability;
future-transport capacity.
```

## 12. Certified transport

A macro path under quotient `kappa` is:

```text
z_0 -> z_1 -> ... -> z_K
```

A transport edge is observed when viable lower-rank trajectories move from one fiber to another:

```text
M(z_i, z_{i+1}) > 0
```

A certified macro path requires:

```text
node certification:
  each fiber has sufficient viable support

edge certification:
  each transition carries sufficient viable mass

component preservation:
  lower-rank components are not erased

nonfragmentation:
  transported mass is not only singleton or tiny isolated fibers

recoverability:
  relevant perturbations do not destroy the transport channel

matched-null separation:
  transport is not explained by detector artifacts or marginal structure alone
```

### 12.1 Static fibers versus transport fibers

Static certified fibers are not enough.

Omega-like structure requires certified transport:

```text
fiber support at horizon H_a
  becomes
fiber support at horizon H_b
```

without erasure, fragmentation, or collapse.

## 13. Non-erasure

Non-erasure is a central Omega constraint.

A macro-structure is not Omega-like if it persists by eliminating the lower-rank structures that make it meaningful.

Given a coupled system:

```text
X = X_A x X_B
```

A quotient `kappa_AB` over the joint system must be audited for component preservation.

Let:

```text
C_A:
  preservation of component A distinctions

C_B:
  preservation of component B distinctions

E_lower:
  lower-rank erasure score
```

A joint macro-transport channel is non-erasing only if:

```text
C_A >= c_min
C_B >= c_min
E_lower <= e_max
```

or if a justified domain-specific component criterion replaces these.

### 13.1 Local success can hide erasure

A system can preserve a joint macro-label while destroying one component's future-bearing structure.

Such a system may be locally viable but not Omega-compatible.

## 14. Compatibility

Compatibility concerns interaction among future-bearing structures.

Let there be two subsystems or future landscapes:

```text
S_A, S_B
```

Local viable propagation for `S_A` is not sufficient if it degrades the future-bearing propagation of `S_B`.

Define a compatibility relation:

```text
Compat_T(S_A, S_B) in [0,1]
```

which measures whether viable propagation in one system preserves, supports, or at least does not destructively collapse viable propagation in the other.

### 14.1 Capture and erasure

Important coupled failure modes include:

```text
capture:
  one system preserves its own future landscape by constraining another into a
  narrow compatible channel

erasure:
  one system destroys another's future-bearing distinctions

lock-in:
  future possibilities remain viable only inside a brittle narrowing corridor

singleton domination:
  apparent stability arises from eliminating alternative continuations

pseudo-cooperation:
  joint viability exists but one component's recoverable structure is lost
```

### 14.2 Omega-compatible viability

Local viability:

```text
system continues on its own terms
```

Omega-compatible viability:

```text
system continues while preserving compatibility with broader future-bearing
structure
```

This is where alignment relevance begins. It should not be imported earlier.

## 15. Candidate Omega signature

The primary object should be a structured signature, not a scalar.

For quotient `kappa`, horizon `T`, substrate `S`, perturbation family `Pert`, and compatibility scope `C`, define:

```text
Omega_sig(S, kappa, T, Pert, C) =
  (
    V_gate,
    D_prop,
    R_rec,
    Q_adm,
    F_transport,
    N_nonfrag,
    E_nonerase,
    C_compat,
    B_breadth,
    A_asymmetry,
    M_null
  )
```

where:

```text
V_gate:
  viable trajectory support exists

D_prop:
  future-relevant distinctions propagate

R_rec:
  propagated structure is recoverable under perturbation

Q_adm:
  quotient is predictive/admissible enough for the claim

F_transport:
  fibers or horizon-frontier structures transport through time

N_nonfrag:
  support is not singleton-fragmented or tiny-fiber fakeout

E_nonerase:
  lower-rank component structure is preserved

C_compat:
  propagation remains compatible with broader future-bearing structures

B_breadth:
  entropy/breadth diagnostic after the above gates

A_asymmetry:
  relevant asymmetry structure is present and audited

M_null:
  matched controls and detector nulls do not explain the signal
```

A scalar may be defined only after the tuple is reported:

```text
Omega_index = g(Omega_sig)
```

The scalar is a summary. The tuple is primary.

## 16. Minimal Omega-compatible condition

A candidate structure is minimally Omega-compatible only if:

```text
V_gate passes;
D_prop > threshold;
R_rec > threshold;
Q_adm passes quotient audit;
F_transport passes transport audit;
N_nonfrag passes nonfragmentation audit;
E_nonerase passes lower-rank preservation audit;
C_compat is not known to fail;
M_null passes detector and matched-control requirements.
```

If compatibility is outside scope, the result must be labeled a precursor:

```text
Omega-precursor:
  viable, recoverable, non-erasing propagation under an admissible quotient,
  but not yet tested for coupled compatibility.
```

Current MB0 results are at most precursor-level.

## 17. Pseudo-Omega failure classes

The formalism should name false positives.

### 17.1 Entropy laundering

A quotient creates apparent breadth by merging incompatible states.

### 17.2 Static fiber fakeout

Large fibers exist, but they do not transport.

### 17.3 Singleton capture

A system appears stable because alternatives were eliminated.

### 17.4 Component erasure

A joint macro-structure persists by deleting lower-rank component distinctions.

### 17.5 Local viability trap

A system remains viable while degrading broader future landscapes.

### 17.6 Measurement-marginal artifact

A detector sees structure explained by row/column marginals or other matched controls.

### 17.7 Deterministic substrate artifact

A positive response depends on a hand-authored edge-selection rule rather than a substrate-general constraint.

### 17.8 Quotient overfit

A learned quotient works on a finite validation batch but fails horizon transfer or perturbation robustness.

## 18. Mapping to empirical programs

### 18.1 Historical entropy / single-field branch

Tested future breadth and viable reachability.

Import:

```text
viability matters;
entropy is secondary;
traps and irreversibility matter;
horizon coherence matters.
```

Demote:

```text
raw entropy as Omega;
single scalar future richness as the main object.
```

### 18.2 Historical COM / multifield branch

Tested quotient fibers and viable propagation through a hand coordinate.

Import:

```text
quotients matter;
fibers matter;
component preservation matters;
non-erasure matters;
learned quotient recovery is hard.
```

Demote:

```text
COM as universal;
hand quotient as final;
certified static fibers without transport.
```

### 18.3 RFS-MB0 horizon transport

Tests directional future-structure transport under matched controls.

Import:

```text
horizon-indexed transport is a better precursor than static co-occurrence;
null controls and perturbation response must be separated;
response classes should remain neutral.
```

Current interpretation:

```text
matched-marginal-separated horizon transport is a live instrument;
not Omega validation.
```

### 18.4 Preservation asymmetry

Tests whether penalizing changes in coarse macro-invariants affects future-transport response.

Import:

```text
preservation of coarse distinctions is a live substrate ingredient;
low-beta threshold behavior suggests graph deformation precedes transport response.
```

Current interpretation:

```text
preservation asymmetry is a promising non-template substrate hook;
not value, agency, or Omega.
```

### 18.5 MaxEnt-P preflight

Tests whether preservation survives when moved from deterministic top-m energy scoring to an ensemble-level macro-invariant marginal constraint.

Formal role:

```text
tests whether preservation asymmetry is substrate-level or top-m artifact.
```

### 18.6 MB2 coupled landscapes

Future decisive layer.

Formal role:

```text
tests compatibility, capture, erasure, and multi-system future-landscape
interaction.
```

This is where alignment relevance becomes directly testable.

## 19. Relationship to Gradient Field Theory

Gradient Field Theory contributes a coherence subfunctional.

Its useful object is something like:

```text
C_info:
  persistence and recoverability of action-relevant distinctions under dynamics
```

In this formal core:

```text
C_info > 0
```

is a necessary condition for Omega-relevant structure, but not sufficient.

Omega additionally requires:

```text
admissible quotienting;
fiber or horizon transport;
non-erasure;
nonfragmentation;
matched-null separation;
compatibility with broader future-bearing structure.
```

Therefore:

```text
GFT-like coherence:
  necessary substrate condition

Omega-compatible viable propagation:
  stronger structured condition
```

## 20. Relationship to ethics and alignment

This formal core does not derive ethics.

It provides a substrate-level vocabulary for future-preserving structure.

Ethical or alignment interpretation becomes available only after:

```text
bounded historical identities;
valuerhood;
recoverable continuability;
multi-system compatibility;
capture / erasure / preservation dynamics
```

are formally in scope.

Before that, the formalism should speak only of:

```text
distinctions;
relations;
asymmetries;
viability;
propagation;
recoverability;
quotients;
transport;
non-erasure;
compatibility.
```

## 21. Open problems

### 21.1 Quotient problem

How is `kappa*` learned or characterized without hand coordinates?

### 21.2 Compatibility problem

How should compatibility be measured in coupled future landscapes without smuggling in value labels?

### 21.3 Non-erasure problem

How can lower-rank erasure be defined across arbitrary substrates?

### 21.4 Recoverability problem

Which perturbation families are admissible, and how much recovery is enough?

### 21.5 Scalarization problem

Can a scalar Omega index be defined without hiding the tuple anatomy?

### 21.6 Substrate-generalization problem

Which positive results survive beyond finite toy graphs?

### 21.7 Observer / valuer bridge

When does a future-bearing propagating structure become a bounded historical identity or valuer?

## 22. Minimal formal commitments

This draft commits to:

```text
1. Omega is not raw entropy.
2. Omega is not survival alone.
3. Omega is not static reachability.
4. Omega is horizon-indexed.
5. Omega requires future-relevant distinctions.
6. Distinctions require relations to propagate.
7. Relations matter through asymmetric future consequences.
8. Viability is a gate, not the target.
9. Propagation must be recoverable.
10. Quotients must be admissible and audited.
11. Macro persistence must not erase lower-rank support.
12. Local viability can be globally degrading.
13. Omega-compatible propagation is a structured signature before it is a scalar.
```

## 23. Bottom line

The clean formal core is:

```text
Omega is the structured compatibility of viable future-bearing propagation.

At the precursor level, this means:
  future-relevant distinctions propagate through admissible relations across
  horizon, remain recoverable under perturbation, survive quotienting, and avoid
  non-erasure failures.

At the full level, this propagation must also remain compatible with broader
future-bearing structures in coupled systems.
```

Current empirical work has not validated Omega.

It has clarified the path:

```text
single-field entropy:
  demoted

COM:
  historical witness

horizon transport:
  live instrument

preservation asymmetry:
  live substrate ingredient

MaxEnt-P:
  next artifact audit

coupled landscapes:
  later compatibility test
```
