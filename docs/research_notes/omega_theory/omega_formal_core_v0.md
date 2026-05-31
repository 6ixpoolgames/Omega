# Omega Formal Core v0

Distinction, Relation, and Asymmetry in Viable Future Propagation

Status: draft theory/process note  
Scope: clean-slate formal core after current and historical empirical branches  
Claim boundary: no Omega validation, no agency detection, no value detection, no valuerhood detection, no holdout claim, no universal signature claim.

## 0. Purpose

This note records the current formal core left standing after several simpler empirical and theoretical formulations failed or narrowed.

It is intentionally process-bearing. It is not the final elegant form of the theory. It is a working stack that preserves what the project currently knows not to say.

Core thesis:

```text
Distinctions matter only through relations.
Relations matter only through asymmetric future consequences.
Asymmetric future consequences become Omega-relevant only when viable
distinctions propagate, remain recoverable, survive quotienting, avoid
non-erasure failures, and remain compatible with broader future-bearing
structure.
```

Boundary addendum:

```text
Agents, valuers, identities, selves, objects, and value-bearing substrates are
not primitive boundaries. They are admissible designations only when a candidate
process-bundle earns that role by predictive, transport, recoverability,
non-erasure, and compatibility performance under explicit audits.
```

Omega is therefore not raw entropy, survival, persistence, reachability, compression, reward, utility, value, identity, or agenthood. These may be diagnostics, gates, or downstream interpretations. The formal target is viable future-bearing propagation under boundary-nonprivileged admissible coarse-grainings, with recoverability, non-erasure, and compatibility constraints.

## 1. What the empirical arm has ruled out

The project imports lessons, not historical objects.

```text
survival:
  necessary background condition, not Omega

raw entropy:
  breadth diagnostic only after viability and propagation pass

static reachability:
  insufficient without horizon-indexed propagation

static fibers:
  insufficient without certified transport

hand quotients:
  useful witnesses, not solved quotient theory

learned quotients:
  must be audited for splitting, merging, overfit, and component loss

scalar summaries:
  secondary diagnostics, never substitutes for tuple anatomy

substrate response:
  precursor evidence only, not value/agency/Omega validation

boundary labels:
  useful designations only if earned; not primitive agents, selves, or valuers
```

## 2. Primitive substrate

Let a substrate be:

```text
S = (X, U, R, P, H)
```

where:

```text
X:
  state space

U:
  admissible transformations, interventions, controls, or transition-generating acts

R:
  admissible relation structure over states

P:
  transition kernel or stochastic transition rule, when available

H:
  admissible horizon set
```

In finite deterministic settings, `R` may be a directed graph. In stochastic settings, `P(x' | x, u)` may induce `R` by positive-probability support.

No agent, valuer, value function, reward, preference, moral label, or privileged boundary is assumed at this level.

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

A raw syntactic difference is not yet Omega-relevant. It becomes relevant only if it can affect future structure.

## 4. Primitive II: relation

A relation is admissible continuity through transformation.

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

## 5. Primitive III: asymmetry

Asymmetry is non-equivalence of transformations in their future consequences.

A relation is asymmetric at horizon `T` when forward and reverse transformations do not preserve equivalent future structure:

```text
D(F_T(x -> y), F_T(y -> x)) > epsilon
```

Forms of asymmetry include:

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

Distinctions without relations are inert. Relations without asymmetry may produce motion but not directed future-structure consequences. Asymmetry is where future-relevant structure first becomes nontrivial.

## 6. Horizons and future structure

Omega is horizon-indexed.

For `T in H`, define a future structure object:

```text
Phi_T(x)
```

where `Phi_T(x)` may be a reachable set, transition distribution, frontier profile, quotient-fiber structure, or horizon-transport object.

Endpoint support alone may miss propagation, transport, recoverability, or non-erasure. The preferred empirical object is directional:

```text
T_{H_a -> H_b}
```

which asks how structure at an earlier horizon becomes structure at a later horizon.

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

Viability is necessary but not sufficient. A system may be viable while losing recoverability, lower-rank support, alternative continuation, or compatibility with broader future-bearing structure.

Viability is therefore a gate. Omega concerns propagation of viable future-bearing structure through time.

## 8. Propagation and recoverability

Propagation asks whether future-relevant distinctions continue to make a difference across horizon.

For distinction `d = (x,y)`:

```text
Prop_T(d) = sup_pi D(F_T^pi(x), F_T^pi(y))
```

Viable propagation restricts to viable trajectories:

```text
Prop_T^V(d) = sup_pi D(F_T^{V,pi}(x), F_T^{V,pi}(y))
```

Recoverability asks whether degraded distinction-structure can be re-established by admissible dynamics.

For structure `sigma`, perturbation `eta`, and recovery policy `rho`:

```text
Rec_T(sigma, eta) = sup_rho Similarity(sigma, Recover_T(eta(sigma), rho))
```

Recoverability does not require exact microstate restoration. It requires restoring the future-relevant distinctions or quotient-level structure that support viable propagation.

## 9. Boundary non-privileging and admissible designation

Boundary non-privileging is a core methodological and formal constraint.

No candidate boundary, identity, agent, valuer, self, object, or value-bearing substrate is taken as ontologically primitive. Such boundaries are admissible designations only if they earn their role through predictive, transport, recoverability, non-erasure, and compatibility performance under explicit audits.

Compact rule:

```text
Boundaries are instruments of measurement, not objects of validation.
```

A designation is a proposed boundary or process-bundle map:

```text
delta: X -> B
```

where `B` labels candidate bounded structures, process bundles, components, or subsystems.

A designation may be useful if it supports prediction, transport analysis, recovery analysis, non-erasure analysis, or compatibility analysis. It is not thereby ontologically privileged.

An admissible designation must pass the relevant audits:

```text
predictive usefulness:
  preserves future-relevant distinctions enough to support analysis

transport usefulness:
  can be tracked across horizon without pure label drift

recoverability usefulness:
  perturbation and recovery can be defined over the designation

non-erasure usefulness:
  does not hide lower-rank collapse or component loss

compatibility usefulness:
  can expose constructive or destructive interaction with other future-bearing
  structures
```

A value-bearing substrate is not an ontologically privileged agent or object.

```text
value-bearing substrate:
  an admissibly designated process-bundle supporting recoverable, non-erasing,
  viable propagation of future-relevant distinctions.
```

This definition intentionally avoids starting from agent, valuer, identity, or self. Those categories may later be recovered as special designations that pass stronger audits.

Empirical consequence:

```text
Do not ask first:
  Did we find an agent?
  Did we find a valuer?
  Did we find identity?

Ask first:
  Does some future-field deformation support an admissible designation under
  which recoverable, non-erasing, value-bearing propagation is present?
```

## 10. Quotients and fibers

A quotient or macro-map is:

```text
kappa: X -> Z
```

where `Z` is a macro-state space.

Quotients are a special case of admissible designation focused on macro-state equivalence rather than bounded process-bundle identification.

A quotient `kappa` is predictive over horizon `T` if:

```text
kappa(x) = kappa(y) implies D(F_T(x), F_T(y)) <= epsilon
```

A quotient is minimally admissible if it balances predictive sufficiency against complexity:

```text
kappa* = arg min_kappa [ L_prop(kappa) + lambda L_quotient(kappa) ]
```

The quotient problem remains unsolved. Current hand quotients and learned quotients are provisional instruments, not final objects.

Given quotient `kappa`, the fiber over macro-state `z` is:

```text
kappa^{-1}(z) = { x in X : kappa(x) = z }
```

Fiber mass alone is not Omega. A large fiber can be noisy, fragmented, unrecoverable, or non-transporting.

A certified fiber should satisfy sufficient mass, non-singleton support, nonfragmentation, component preservation, recoverability, and future-transport capacity.

## 11. Certified transport and non-erasure

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
  relevant perturbations do not eliminate the transport channel

matched-null separation:
  transport is not explained by detector artifacts or marginal structure alone
```

Non-erasure is central: a macro-structure is not Omega-like if it persists by eliminating the lower-rank structures that make it meaningful.

Given a coupled system:

```text
X = X_A x X_B
```

A joint macro-transport channel is non-erasing only if component-preservation is sufficient and lower-rank erasure remains below threshold.

## 12. Compatibility

Compatibility concerns interaction among future-bearing structures.

Local viable propagation for `S_A` is not sufficient if it degrades the future-bearing propagation of `S_B`.

Define a compatibility relation:

```text
Compat_T(S_A, S_B) in [0,1]
```

which measures whether viable propagation in one system preserves, supports, or at least does not destructively collapse viable propagation in the other.

Important coupled failure modes include capture, erasure, lock-in, singleton domination, and pseudo-cooperation.

```text
local viability:
  system continues on its own terms

Omega-compatible viability:
  system continues while preserving compatibility with broader future-bearing
  structure
```

This is where alignment relevance begins. It should not be imported earlier.

## 13. Candidate Omega signature

The primary object should be a structured signature, not a scalar.

For quotient `kappa`, designation `delta`, horizon `T`, substrate `S`, perturbation family `Pert`, and compatibility scope `C`, define:

```text
Omega_sig(S, delta, kappa, T, Pert, C) =
  (
    V_gate,
    D_prop,
    R_rec,
    B_designation,
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

B_designation:
  boundary/designation is admissible for the claim and not reified as primitive

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

## 14. Minimal Omega-compatible condition

A candidate structure is minimally Omega-compatible only if:

```text
V_gate passes;
D_prop > threshold;
R_rec > threshold;
B_designation passes boundary-nonprivileging audit;
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
  viable, recoverable, non-erasing propagation under an admissible designation
  and quotient, but not yet tested for coupled compatibility.
```

Current MB0 results are at most precursor-level.

## 15. Definition closure

Working closure:

```text
Omega is the boundary-nonprivileged compatibility structure of futures that
support recoverable, non-erasing propagation of value-bearing substrates.
```

Where:

```text
value-bearing substrate:
  an admissibly designated process-bundle supporting recoverable, non-erasing,
  viable propagation of future-relevant distinctions.
```

Equivalent form:

```text
Omega is the future-trajectory structure that preserves the possibility of
value-bearing propagation under boundary-nonprivileged designation.
```

This maps the intuitive statement:

```text
Omega is the set of trajectories across futures that contain value-bearing
substrates.
```

to the stricter formal statement:

```text
Omega is the class/structure of trajectories that preserve or support compatible
propagation of admissibly designated value-bearing substrates without collapse,
erasure, or incompatible capture.
```

Containment is too weak. A future may contain one value-bearing substrate while eliminating the possibility of compatible propagation elsewhere. Omega requires compatible propagation, not mere presence.

## 16. Pseudo-Omega failure classes

The formalism should name false positives.

```text
entropy laundering:
  quotient creates apparent breadth by merging incompatible states

static fiber fakeout:
  large fibers exist but do not transport

singleton capture:
  apparent stability comes from eliminating alternatives

component erasure:
  joint macro-structure persists by losing lower-rank distinctions

local viability trap:
  local persistence degrades broader future landscapes

measurement-marginal artifact:
  detector signal is explained by matched controls

deterministic substrate artifact:
  response depends on a hand-authored edge-selection rule

quotient overfit:
  learned quotient works on finite batch but fails horizon transfer

boundary reification:
  useful measurement boundary is mistaken for primitive agent/self/valuer
```

## 17. Mapping to empirical programs

```text
historical entropy / single-field branch:
  imports viability, irreversibility, horizon coherence;
  demotes raw entropy and single scalar richness

historical COM / multifield branch:
  imports quotients, fibers, component preservation, non-erasure;
  demotes COM as universal or final

RFS-MB0 horizon transport:
  imports directional future-structure transport under matched controls;
  remains instrument, not Omega validation

boundary non-privileging:
  explains why the empirical arm avoids defining agents/valuers/identity first

preservation asymmetry:
  live substrate ingredient for preserving coarse distinctions;
  not value, agency, or Omega

MaxEnt-P:
  next artifact audit for whether preservation is substrate-level or top-m artifact

MB2 coupled landscapes:
  later compatibility test for capture, erasure, support, and interference
```

## 18. Relationship to Gradient Field Theory

Gradient Field Theory contributes a coherence subfunctional.

```text
C_info:
  persistence and recoverability of action-relevant distinctions under dynamics
```

In this formal core, `C_info > 0` is necessary but not sufficient.

Omega additionally requires:

```text
boundary-nonprivileged admissible designation;
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

## 19. Relationship to Gradient Ethics and the normative layer

Gradient Ethics should be read as a downstream normative specialization of this formal core, not as the root definition of Omega.

The formal core stays below agent/value labels. It defines the boundary-nonprivileged substrate conditions under which value-bearing propagation can be meaningfully designated. Gradient Ethics begins later, once coherent agentic or valuer-like systems are in scope and asks what constraints follow under uncertainty and irreversibility.

Mapping:

```text
Omega future-bearing propagation:
  substrate-level condition that value-bearing process-bundles can continue

Gradient Ethics future reachability:
  normative-layer interpretation of what persistent agents must preserve under
  uncertainty

Omega non-erasure / compatibility:
  formal precursor to rights, non-interference, and anti-capture constraints

Omega recoverability:
  formal precursor to corrigibility, oversight, and repairability

Omega boundary non-privileging:
  prevents premature reification of agent/valuer boundaries while still allowing
  functional designations to earn normative relevance

Omega coupled compatibility:
  substrate-level precursor to cooperation, justice, trust, and distributed
  agency arguments
```

The normative layer remains conditional, not categorical:

```text
If a system is an admissibly designated persistent agent or valuer operating
under uncertainty, then it is constrained to preserve the future-bearing
conditions that make its own and others' agency possible.
```

This is not a utility function or decision procedure. It is a constraint layer. Ethical norms are interpreted as guardrails against irreversible loss, erasure, capture, and collapse of future-bearing propagation.

Thus:

```text
Omega formal core:
  What future-trajectory structures can support value-bearing propagation?

Gradient Ethics:
  What constraints must persistent agents obey once such future-bearing
  structures and agentic interactions are in scope?
```

## 20. Relationship to ethics and alignment

This formal core does not derive ethics by itself.

Ethical or alignment interpretation becomes available only after:

```text
admissible value-bearing substrate designation;
bounded historical identities;
valuerhood;
recoverable continuability;
multi-system compatibility;
capture / erasure / preservation dynamics
```

are formally in scope.

Before that, the formalism should speak only of distinctions, relations, asymmetries, viability, propagation, recoverability, admissible designations, quotients, transport, non-erasure, and compatibility.

## 21. Open problems

```text
designation problem:
  how to learn admissible process-bundle designations without reifying boundaries

quotient problem:
  how to characterize kappa* without hand coordinates

compatibility problem:
  how to measure coupled compatibility without smuggling in value labels

non-erasure problem:
  how to define lower-rank erasure across arbitrary substrates

recoverability problem:
  which perturbations are admissible and how much recovery is enough

scalarization problem:
  whether any scalar Omega index can avoid hiding tuple anatomy

substrate-generalization problem:
  which positive results survive beyond finite toy graphs

observer / valuer bridge:
  when future-bearing propagation earns bounded historical identity or valuer
  designation
```

## 22. Minimal formal commitments

This draft commits to:

```text
1. Omega is not raw entropy.
2. Omega is not survival alone.
3. Omega is not static reachability.
4. Omega is not an ontologically privileged boundary.
5. Omega is horizon-indexed.
6. Omega requires future-relevant distinctions.
7. Distinctions require relations to propagate.
8. Relations matter through asymmetric future consequences.
9. Viability is a gate, not the target.
10. Propagation must be recoverable.
11. Boundaries and quotients must be admissible and audited.
12. Macro persistence must not erase lower-rank support.
13. Local viability can be globally degrading.
14. Omega-compatible propagation is a structured signature before it is a scalar.
15. Normative claims are downstream conditional constraints, not primitive axioms.
```

## 23. Bottom line

The clean formal core is:

```text
Omega is the boundary-nonprivileged compatibility structure of futures that
support recoverable, non-erasing propagation of value-bearing substrates.

At the precursor level, this means:
  future-relevant distinctions propagate through admissible relations across
  horizon, remain recoverable under perturbation, survive admissible designation
  and quotient audits, and avoid non-erasure failures.

At the full level, this propagation must also remain compatible with broader
future-bearing structures in coupled systems.
```

Current empirical work has not validated Omega. It has clarified the path:

```text
single-field entropy:
  demoted

COM:
  historical witness

boundary non-privileging:
  formalized as admissible designation rather than primitive identity

horizon transport:
  live instrument

preservation asymmetry:
  live substrate ingredient

MaxEnt-P:
  next artifact audit

coupled landscapes:
  later compatibility test

Gradient Ethics:
  downstream normative layer once admissible agent/valuer designations are in
  scope
```
