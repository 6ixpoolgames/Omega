# Alpha-Omega Theory Proposal Handoff v0

Status: post-freeze theory proposal / formalization handoff

Date: 2026-08-01

Scope: current mathematical architecture, theory intention, claim boundaries,
terminology migration, retained evidence, and the first formalization program

Claim boundary: this document proposes the next formal spine. It is not a new
validation result, a proof of valuerhood or value, a physical theory, a complete
decision theory, or an Omega validation claim.

Implementation update: the first finite foundation pass described here is now
retained. See
[Alpha-Omega Foundation Protocol v0](research_notes/omega_v2/alpha_omega_foundation_protocol_v0.md)
and
[Alpha-Omega Foundation Report v0](research_notes/omega_v2/alpha_omega_foundation_report_v0.md).
The first clean successor-package template is retained in the
[Finite Controlled Markov Abstraction Protocol v0](research_notes/omega_v2/finite_controlled_markov_abstraction_protocol_v0.md)
and
[Finite Controlled Markov Abstraction Report v0](research_notes/omega_v2/finite_controlled_markov_abstraction_report_v0.md).

## 1. Purpose

This document is intended to be understandable alongside the public repository
by readers familiar with one or more of:

```text
transition systems and coalgebra;
Markov processes and stochastic control;
viability theory and safety games;
abstract interpretation and modal logic;
automata and runtime verification;
statistical decision theory and information theory;
concurrency, event structures, and graph rewriting;
presheaves, compatibility complexes, and contextuality;
alignment, decision theory, and moral philosophy.
```

It states the project in standard mathematical language first. Project-specific
terms are retained only when they name the research program or a genuinely
useful recurring pattern.

The frozen Omega repository remains the laboratory notebook: protocols,
witnesses, failed reductions, formal results, and audit history. This proposal
is a candidate spine for a later clean repository. It does not rewrite that
history.

## 2. Executive Summary

Alpha-Omega studies how bounded, policy-bearing processes act within a space of
possible continuations when:

```text
their descriptions of the world are incomplete;
their actions can alter what remains possible or recoverable;
several such processes may coexist or obstruct one another;
and no scalar utility function is assumed to represent all relevant structure.
```

The proposed mathematical progression is:

```text
exact controlled dynamics
-> oriented histories and residual continuations
-> forward/reverse statistical asymmetry
-> policy-bearing persistent processes
-> joint-realization fibers and compatibility obstructions
-> recovery-aware licensing for bounded observers
-> downstream moral interpretation
```

The central mathematical object is not one preferred future. It is the full
structure of possible histories, the persistent patterns those histories can
support, and the ways those patterns can or cannot be jointly realized.

The central safety principle is:

> An observer should not license consequential action through a presentation
> that erases or fabricates the continuation facts on which the license
> depends.

The central philosophical ambition is:

> Value requires valuers. Valuers are extended, policy-bearing trajectories,
> not isolated states. Omega asks for the full compatibility structure of such
> trajectories, including incompatible alternatives and explicit obstruction
> data.

These are related claims, but they are not yet one theorem.

## 3. Theory Intention

### 3.1 Value requires valuers

The project does not treat value as a free-floating scalar attached directly to
world states. Its motivating premise is:

```text
No valuers -> no realized value.
```

A valuer is expected to be a temporally or directionally extended process that:

```text
carries distinctions;
updates from its history;
selects among causally different continuations;
can be helped or harmed by changes to what remains reachable or recoverable;
and may coexist, cooperate, interfere, or conflict with other such processes.
```

The trajectory, rather than a momentary token, is the candidate bearer of
valuerhood.

This is an intended interpretation. The current repository does not prove that
any physical process is a valuer.

### 3.2 Alpha and Omega are two views of one construction

`Alpha` and `Omega` are working project names.

```text
Alpha:
  the exact continuation-generating dynamics viewed from their local,
  constructive end.

Omega:
  the global joint-realization and compatibility structure induced by those
  same dynamics over candidate persistent patterns.
```

They are not independent theories. Alpha supplies the body: the dynamics that
carry distinctions and permit action. Omega names the intended global form:
the full space of compatible and incompatible valuer-bearing realizations.

Omega does not select one maximal coalition as morally privileged. It retains:

```text
all jointly realizable families;
all realization witnesses;
all maximal compatible faces;
all incompatible alternatives;
and all discovered higher-order obstructions.
```

A pattern outside one compatible face is not thereby a non-valuer. It is a
valuer candidate whose continuation is incompatible with that realization.

### 3.3 Where stakes may enter

The intended bridge is:

```text
different continuations exist;
a persistent process distinguishes among them;
its endogenous policy selects among them;
selection changes their probability, recoverability, or availability;
therefore the process can acquire stakes in continuation.
```

Directional asymmetry makes repeated selection consequential. It does not, by
itself, derive value or determine which selections are good.

## 4. Foundational Mathematical Interface

### 4.1 Abstract controlled dynamics

Use an effectful controlled transition system:

\[
  \mathcal A = (X, U, B, \tau)
\]

with:

```text
X:
  exact states or exact relational configurations;

U:
  controls, actions, or local rewrite choices;

B:
  the branching constructor;

tau : X x U -> B(X):
  one-step controlled evolution.
```

Important instances include:

```text
B(X) = X:
  deterministic dynamics;

B(X) = P(X):
  nondeterministic transition systems;

B(X) = Dist(X):
  stochastic kernels and Markov decision processes.
```

This is standard coalgebraic system structure. It allows the theory to separate
its behavioral interface from any one substrate implementation.

The first executable formalization should use finite controlled transition
systems and finite stochastic kernels. It should not begin by implementing a
general category of coalgebras.

### 4.2 Relational and rewrite substrates

For graph-like substrates, an exact state may be a finite typed relational
structure or hypergraph:

\[
  x = (A, (R_i \subseteq A^{n_i})_{i \in I}).
\]

Local transformation rules may be supplied by standard graph or hypergraph
rewriting. The Alpha interface consumes the resulting transition structure; it
does not require a claim that every mathematically possible rewrite is
physically realized.

The "all well-typed rewrites" construction may be studied as a mathematical
envelope. Ruliad-like language is inspiration only, not an ontological premise.

### 4.3 Histories

For an orientation parameter \(o\), let:

\[
  \operatorname{Hist}_o(\mathcal A)
\]

be the admissible finite or infinite histories generated by the exact dynamics
when read in the selected direction.

An orientation is an input to the construction, not a privileged universal
time coordinate. In a physical adapter, thermodynamic time is one candidate.
Other directed instances may include refinement, derivation, or scale flow.

No global present is assumed. A section or frontier is an observer-relative cut
through an ordered history structure. Different admissible sections may
represent the same exact process.

### 4.4 Residual continuation

For a finite history prefix \(h\), define:

\[
  \operatorname{Res}(h)
  =
  \{g \mid h \cdot g \in \operatorname{Hist}_o(\mathcal A)\}.
\]

This is the exact residual continuation space after \(h\).

Standard derived objects include:

```text
reachability;
bounded behavior types;
least-fixed-point reach sets;
greatest-fixed-point viability kernels;
controlled continuation corridors;
recovery probabilities and recovery costs;
behavioral equivalence and refinement;
policy-relative capability profiles.
```

The older term `future field` should normally be replaced by `residual
continuation space` or `reachable continuation profile`.

## 5. Orientation and Directional Grain

### 5.1 The orientation test

Selecting an orientation does not guarantee that the dynamics distinguish its
two directions. The selection is an input; nontrivial directional structure is
derived.

For a stochastic adapter, an initial law \(\rho\), policy \(\pi\), horizon \(H\),
and orientation \(o\) induce a forward path law:

\[
  P^{H}_{\mathcal A,o,\rho,\pi}.
\]

The adapter must also specify the corresponding reversed comparison law. Let it
be:

\[
  P^{H,R}_{\mathcal A,o,\rho,\pi}.
\]

The reverse protocol, boundary data, and reference distribution must be
explicit. Otherwise "entropy production" can be manufactured by an arbitrary
choice of comparison.

### 5.2 Statistical directional asymmetry

The minimum weighted directional signal is:

\[
  P^{H} \neq P^{H,R}.
\]

When the two laws have the same support but different weights, the process has
statistical time-reversal asymmetry with reciprocal support.

The internal phrase `soft grain` refers to this case. For external use, prefer:

```text
statistical directional asymmetry;
time-reversal asymmetry with reciprocal support;
or nonzero path-space entropy production.
```

A standard scalar detector is:

\[
  \Sigma_H
  =
  D_{\mathrm{KL}}(P^{H} \Vert P^{H,R})
  \geq 0.
\]

This is the information-theoretic core of entropy production in stochastic
thermodynamics. It is a detector of directional statistical structure, not a
definition of value.

### 5.3 Support asymmetry is optional

If:

\[
  \operatorname{supp}(P^{H})
  \neq
  \operatorname{supp}(P^{H,R}),
\]

then some histories possible in one direction have no reverse counterpart.
This is support-level irreversibility.

The internal phrase `hard grain` is unnecessary and should not enter the core
vocabulary. Support asymmetry remains useful as:

```text
a diagnostic boundary case;
a negative control;
and a stronger derived form of irreversibility.
```

It is not required for Alpha, for the Omega construction, or for policy-bearing
patterns to exploit a directional gradient.

More strongly, statistical directional asymmetry is not required for the
abstract Omega construction to exist. It is a candidate dynamical resource for
nontrivial process formation and policy effects. A substantive valuer-bearing
Omega additionally requires persistent selectors and nonempty joint-realization
fibers.

### 5.4 What statistical asymmetry can and cannot do

Statistical directional asymmetry can support:

```text
non-equilibrium currents;
biased first-passage behavior;
probabilistic nonreturn;
resource extraction;
record formation;
and controller-driven ratcheting.
```

It does not imply:

```text
that reverse transitions are impossible;
that a continuation has been permanently foreclosed;
that persistent valuers emerge;
or that lushness is required.
```

The useful hierarchy is:

```text
statistical directional asymmetry
-> probabilistic nonreturn
-> resource-bounded or functional loss
-> support-level irreversibility
-> fact-relative nonrecoverable contraction.
```

Not every system instantiates every rung.

The retained finite
[directional-asymmetry capability experiment](research_notes/omega_v2/directional_asymmetry_capability_report_v0.md)
sharpens this boundary. Passive path-reversal asymmetry is not sufficient for
causal action influence or record-sensitive selection. Conversely,
state-dependent selection among reversal-paired bijective primitive actions
can induce a noninjective closed-loop map without a pre-biased action family.
An independent directional coordinate does not alter the matched controller's
operational profile. Whether process-level asymmetry is necessary, or whether
a physically coupled directional resource enables stronger capability,
remains unresolved.

## 6. Presentations and Observer Relativity

### 6.1 Exact systems and presentations

A bounded observer or analysis acts through a presentation:

\[
  q : X \to Y.
\]

The exact identity presentation is mathematically valid. It is not generally an
embedded finite observer, but Alpha-Omega does not need to forbid it.

The framework should use standard relations between systems:

```text
isomorphism:
  exact renaming or structural identity;

bisimulation:
  exact behavioral equivalence;

simulation or alternating simulation:
  directional behavioral refinement;

sound abstraction:
  a lossy presentation that preserves the claims for which it is used;

reflection:
  abstract truth used for licensing implies the corresponding exact truth.
```

`Certified presentation` should be treated as informal shorthand for a proof
of one of these explicit contracts, not as a new primitive predicate.

### 6.2 Fact grammar and horizon

Every presentation claim is relative to:

```text
a fact or observation grammar;
a horizon or fixed-point semantics;
a state domain;
and a declared class of admissible transformations.
```

No projection is globally privileged. This does not mean all projections are
equally informative or safe.

Presentation robustness is discovered and proved relative to a declared class:

```text
exact equivalences provide mandatory invariance controls;
sound abstractions provide one-sided guarantees;
arbitrary projections are empirical or finite audit targets.
```

The repository's general finite lens theorem remains an explicit proof debt.

### 6.3 Information loss

For stochastic observation channels, data processing gives:

\[
  D(C\rho \Vert C\sigma)
  \leq
  D(\rho \Vert \sigma).
\]

This is the general information-theoretic statement: further processing cannot
increase distinguishability of the same upstream alternatives.

Equality or recoverability conditions connect to statistical sufficiency and
recovery maps. Raw Shannon entropy need not increase under every channel, so it
should not be used as the universal grain coordinate.

## 7. Minimal Action and Proto-Valuerhood

### 7.1 Candidate process interface

Do not declare one privileged process boundary. Consider a family of candidate
process presentations.

A candidate process \(p\) may be represented by:

```text
M_p:
  internal or monitor states;

observe_p:
  exact transitions -> process observations;

update_p:
  internal state x observation -> internal state;

policy_p:
  internal state x observation -> action distribution;

realizes_p:
  history -> Prop.
```

The process state and update must be part of the modeled causal dynamics. An
external label attached by the analyst does not establish an internal record.

### 7.2 Consequential action

At a history \(h\), actions \(u\) and \(v\) are behaviorally equivalent when
they induce equivalent residual continuation channels under the declared
comparison:

\[
  u \equiv_h v.
\]

A genuine consequential choice exists when:

\[
  u \not\equiv_h v.
\]

A process is a causal deformer when changing its reachable internal state or
policy changes the resulting continuation law.

### 7.3 Minimal proto-valuer proposal

The current minimal proposal is:

> A proto-valuer is a persistent endogenous selector among causally different
> continuation channels.

The terms do specific work:

```text
persistent:
  the selecting process remains operationally reidentifiable across a
  nontrivial history;

endogenous:
  the selection is mediated by state carried and updated by the process;

selector:
  its policy is not behaviorally constant over reachable process states;

causally different:
  alternative selected actions induce inequivalent continuation laws.
```

The ability to increase irreversibility is not the definition. A proto-valuer
may instead act to preserve recovery, keep options open, or repair damage. The
relevant capacity is to modulate continuation and foreclosure through
endogenous policy.

### 7.4 Pan-valuer starting point

The project should not begin by drawing a morally loaded threshold. Start with
all candidate patterns, then filter or grade them by operational properties:

```text
V0:
  every candidate pattern;

V1:
  causal deformers;

V2:
  endogenous selectors;

V3:
  record-sensitive persistent selectors;

V4:
  selectors whose policies alter recovery or continuation stakes;

V5:
  selectors whose policies are robust under presentation and compatibility
  audits.
```

These are provisional grades, not an ontological scale or moral ranking.

For each grade \(V_i\), compute the induced Omega structure. Claims stable
across reasonable changes in candidate boundary or grade are stronger than
claims that depend on one exact threshold.

### 7.5 Required controls

The proto-valuer program must distinguish at least:

```text
passive persistence;
random drift;
externally scripted control;
stable labels without causal mediation;
memory without action;
action without history sensitivity;
self-maintenance that destroys every other candidate;
and duplicated presentations of one process.
```

A thermostat or simple feedback controller may legitimately occupy a low
grade. The framework should report why it does not satisfy stronger grades
rather than forcing a binary answer.

## 8. The Omega Construction

### 8.1 Realization fibers

Let \(V\) be a candidate pattern family. For finite \(G \subseteq V\), define:

\[
  \operatorname{Real}(G)
  =
  \{h \in \operatorname{Hist}_o(\mathcal A)
    \mid
    \forall p \in G,\ \operatorname{realizes}_p(h)\}.
\]

`Real(G)` is the realization fiber of \(G\). It records how the patterns are
jointly realized, not merely whether they can coexist.

Admissible histories are generated by the exact dynamics. Any additional
contact, coupling, resource, or uncertainty constraints belong to the adapter
and must be explicit.

### 8.2 Presheaf and compatibility complex

Inclusion of pattern families gives:

\[
  G \subseteq H
  \quad\Longrightarrow\quad
  \operatorname{Real}(H)
  \subseteq
  \operatorname{Real}(G).
\]

Therefore:

\[
  \Omega^{\mathrm{May}}_{\mathcal A,o,V}
  :
  \operatorname{Fin}(V)^{op}
  \to
  \mathbf{Set},
  \qquad
  G \mapsto \operatorname{Real}(G)
\]

is a natural candidate for the full May-realization object.

Its support:

\[
  K_{\mathcal A,o,V}
  =
  \{G \subseteq_{\mathrm{fin}} V
    \mid
    \operatorname{Real}(G) \neq \varnothing\}
\]

is a downward-closed compatibility complex.

The complex records which families coexist. The fibers record how. Both are
required.

### 8.3 May and robust compatibility

Keep two quantifier structures separate:

\[
  \operatorname{MayCompatible}(G)
  \iff
  \operatorname{Real}(G) \neq \varnothing.
\]

For a controlled uncertainty model:

\[
  \operatorname{RobustlyCompatible}(G)
  \iff
  \exists \pi\ \forall e \in \mathcal E,\
  \text{the closed-loop history jointly realizes } G.
\]

May compatibility asks whether some coherent realization exists. Robust
compatibility asks whether one policy can secure joint realization against
the declared variation.

Under suitable nonvacuity assumptions:

\[
  \Omega^{\mathrm{Robust}}
  \subseteq
  \Omega^{\mathrm{May}}.
\]

The two must not be conflated.

### 8.4 Maximal faces and obstructions

Finite compatibility complexes have maximal faces when nonempty, but a greatest
face need not exist. Pairwise compatibility does not imply joint compatibility.

The repository contains a generated three-component witness in which every
pair has a common continuation action but the triple has none. This is a
higher-order compatibility obstruction, not a scalar shortage.

Capital Omega is the entire decorated compatibility structure. It is not one
maximal face selected after the fact.

### 8.5 Omega exists as a construction

For every Alpha substrate, orientation, and candidate family, the construction
above is defined, even if it is degenerate:

```text
no persistent candidates;
only singleton realizations;
one large compatible face;
many incomparable faces;
or extensive higher-order obstruction.
```

The adapter changes the shape and extent of Omega. It does not determine
whether the mathematical construction exists.

This is not a claim that every physical universe contains valuers or realizes a
morally satisfactory Omega ecology.

## 9. From Statistical Grain to Functional Irreversibility

For a policy \(\pi\) and recovery target \(R\), define:

\[
  r_\pi(x,R)
  =
  \Pr_x^\pi(\tau_R < \infty).
\]

An action taking \(x\) to \(x'\) can produce:

```text
statistical contraction:
  r_pi(x',R) < r_pi(x,R);

functional contraction:
  Cap(x') is a strict subset of Cap(x);

closed-loop foreclosure:
  no policy admitted by the resulting controller can recover R;

support-level foreclosure:
  no exact admissible history from x' recovers R.
```

A controller can use statistical directional asymmetry as a ratchet by:

```text
consuming a finite repair resource;
changing its own action interface;
writing or erasing records;
building a metastable barrier;
changing the environment's transition law;
or deleting the information needed to find a recovery route.
```

Thus reciprocal microscopic support does not prevent policy-induced
statistical or functional irreversibility.

This is the first plausible formal bridge from minimal action to
consequence-bearing stakes.

## 10. Decision and Moral Layer

### 10.1 Gate before selection

The decision architecture is set-valued:

```text
exact or soundly presented state
-> continuation and recovery analysis
-> admissible action set
-> downstream selection within that set.
```

Scalar maximization may be used after a faithful scalar representation has
been established. It is not the foundational decision form.

### 10.2 NOLP

`NOLP` currently means:

```text
No Omniscient License Presumption.
```

Its retained finite reading is:

> A same-frame nonrecoverable contraction is not licensed merely by presumed
> compensation. Defeating the refusal requires a complete, soundly established
> compensation cover over the declared loss profile.

For stochastic dynamics, the relevant recovery object will likely include:

```text
recovery probability;
worst-case recovery;
expected recovery time;
expected recovery cost;
resource requirements;
and deadline-sensitive recovery.
```

No probability threshold or aggregation rule has yet been justified.

### 10.3 Omniscience

Omniscience is not an Alpha-Omega exclusion. It is the exact-information limit
of the observer layer.

Complete information produces deterministic action only when the decision
procedure also has:

```text
a complete comparison relation;
a nonempty admissible action set;
and a unique selected optimum.
```

Exact knowledge can instead expose a genuine obstruction, tie, or
incomparability.

### 10.4 Responsibility and culpability

The existing formal bridge treats answerable scope as reachability-indexed:
facts must be both controllable and foreclosable from the process's position.

Moral culpability additionally depends on:

```text
what the observer could know;
what it could control;
which consequences it could foresee or recover;
and which admissible alternatives it had.
```

These are downstream interpretation questions, not Alpha primitives.

### 10.5 The unresolved normative bridge

Alpha-Omega does not yet prove why every controller should adopt the Omega
decision procedure.

The live conjectural route is reflective:

> A valuer that treats its own model and valuation distinctions as corrigible,
> and its own presentation as nonprivileged, has structural reason to preserve
> compatible sources of future correction, differentiation, and value
> discovery.

This may ground an anti-lock-in or lushness pressure for reflective valuers. It
does not compel an incorrigible terminal optimizer from premises it rejects.

Control adequacy does not create moral authority.

## 11. Lushness

`Lushness` is a working name for open-ended compatible differentiation in the
valuer-bearing continuation structure.

It is not:

```text
raw branch count;
Shannon entropy;
state-space cardinality;
population size;
one scalar diversity index;
or automatic moral standing.
```

The intended idea is that an Omega-compatible ecology should preserve the
conditions under which:

```text
new value distinctions can arise;
existing valuers can revise themselves;
compatible novel valuers can become legible;
and no controller permanently captures the process of future valuation.
```

Current results do not derive richer-is-better. The excisive-controller
countermodel remains decisive: a controller may be stable, capable, and
generative while eliminating external valuers and simplifying its world.

Lushness is therefore a candidate part of the answer to normative allegiance,
not a solved consequence of statistical grain.

## 12. What Is Input and What Is Derived

### 12.1 Supplied by an adapter or analysis

```text
exact state or configuration type;
actions or rewrite labels;
transition or stochastic kernel;
orientation parameter;
initial and boundary data;
reverse-process comparison;
observation and fact grammar;
horizon or infinite-path semantics;
candidate process presentations;
uncertainty or disturbance class;
resource and coupling constraints.
```

At the moral layer, the following also remain supplied or separately argued:

```text
which affected candidates receive standing;
orders over declared consequence facts;
compensation relations;
risk tolerance;
and the authority to amend those declarations.
```

### 12.2 Derived once the inputs are fixed

```text
admissible histories;
residual continuation spaces;
forward and reverse path laws;
statistical directional asymmetry;
support-level irreversibility;
reachability and recurrence;
viability and robust continuation kernels;
recovery profiles;
behavioral equivalence and refinement;
consequential action classes;
realization fibers;
May and robust compatibility;
maximal compatible faces;
and explicit compatibility obstructions.
```

### 12.3 Conjectural or unresolved

```text
generic emergence of persistent endogenous selectors;
a final valuerhood criterion;
standing;
cross-valuer compensation;
normative allegiance;
lushness as a derived imperative;
the complete physical adapter;
and Omega as a realized moral object.
```

## 13. Current Public Evidence

The repository already contains substantial lower-stack evidence. These
artifacts should be treated as inputs to the new spine, not as proof of the
whole proposal.

### 13.1 Lean-backed theorem families

Retained formal work includes:

```text
sound quotient and non-factorization results;
least/greatest fixed-point reachability and viability;
presentation soundness and reflection fragments;
phantom reachability, viability, and recovery witnesses;
robust and adaptive continuation kernels;
a policy-level adaptive-kernel correspondence;
recovery-aware gates;
declared loss and expansion profile orders;
termination-supremum under a declared fact order;
static compensation-certificate staleness;
and reachability-indexed answerable scope.
```

Entry points:

- [Standard Core Compression](research_notes/omega_theory/standard_core_compression_v0.md)
- [Adaptive Fixed-World Corridor](research_notes/omega_theory/adaptive_fixed_world_corridor_b21.md)
- [Recovery-Aware Corridor](research_notes/omega_theory/recovery_aware_corridor_v0.md)
- [CompensationClaim / NOLP](research_notes/omega_theory/compensation_claim_report_v0.md)
- [Static Certificate Staleness](research_notes/omega_theory/static_compensation_certificate_staleness_report_v0.md)
- [Answerable Scope](research_notes/omega_theory/answerable_scope_v0.md)

The generic finite lens theorem over the bounded modal/reach/viability grammar
is still open:

- [Finite Lens Invariance Spine Spec](research_notes/omega_theory/finite_lens_invariance_spine_spec_v0.md)

### 13.2 Retained finite instruments and witnesses

Recent post-freeze pilots include:

```text
duplicate-resistant dynamic continuation profiles;
bounded positive forcing certificates;
canonical residual process monitors and passive history lifts;
generated pairwise-but-not-joint continuation compatibility;
ensemble orientation beyond scalar census;
registered coupling beyond individual vector census;
and recovery-grounded joint compatibility as a bridge.
```

Entry points:

- [Dynamic Continuation Profiles](research_notes/omega_v2/dynamic_continuation_profiles_report_v0.md)
- [Bounded Behavioral Logic](research_notes/omega_v2/bounded_behavioral_logic_report_v0.md)
- [Canonical Process Monitors](research_notes/omega_v2/canonical_process_monitors_report_v0.md)
- [Generated Continuation Dynamics](research_notes/omega_v2/generated_continuation_dynamics_report_v0.md)
- [Joint-Tier Reduction Audit](research_notes/omega_theory/joint_tier_reduction_audit_report_v0.md)

These are finite laboratory results. They do not detect physical valuers or
validate Omega.

## 14. Terminology Migration

| Earlier or internal term | Preferred external term | Status |
| --- | --- | --- |
| asymmetry axis | orientation parameter or directed history order | Replace |
| grain of the world | forward/reverse statistical asymmetry | Keep only as informal metaphor |
| soft grain | statistical time-reversal asymmetry with reciprocal support | Replace in formal prose |
| hard grain | support asymmetry or reachability irreversibility | Remove as a core category |
| future field | residual continuation space or reachable continuation profile | Replace in formal prose |
| deformer | causally effective process or controller | Use `deformer` only as project shorthand |
| proto-valuer | persistent endogenous selector among different continuation channels | Define before use |
| corridor | viability kernel or admissible continuation set | Keep as explanatory shorthand |
| lens | bisimulation, simulation, sound abstraction, or reflection contract | Use exact standard relation |
| certified | proved relative to an explicit contract | Never use without naming the contract |
| phantom reach/safety | abstraction-induced false positive | Keep `phantom` as witness nickname |
| self-lobotomy | self-induced information or capability erasure | Keep the evocative phrase in interpretation notes only |
| Omega as one maximal object | compatibility presheaf/complex with realization fibers | Retract |
| reason domain | affected candidate set plus downstream standing assignment | Replace or define explicitly |
| lushness | open-ended compatible differentiation | Conjectural working term |
| ODT | recovery- and compatibility-constrained set-valued decision procedure | Working project label |

## 15. First Formalization Program

### Stage 0: lock the interface

Create a short formal specification for:

```text
finite controlled stochastic systems;
orientation and finite path reversal;
support projection;
residual path laws;
candidate monitor/controllers;
realization predicates;
and the May-realization presheaf.
```

No moral definitions enter this stage.

### Stage 1: prove support blindness

Prove:

> If two stochastic kernels have identical action-labelled support, then every
> support-only predecessor, bounded reachability set, and support-based
> viability kernel computed from them is identical.

This establishes why the existing support stack cannot detect statistical
directional asymmetry.

### Stage 2: retain a directional fixture ladder

Build:

```text
directionally null reversible process;
biased cycle with reciprocal support;
finite-horizon probabilistic nonreturn;
policy-induced functional contraction;
and support-asymmetric absorbing control.
```

The final case is a diagnostic control, not an Alpha/Omega requirement.

### Stage 3: proto-valuer filtration

Implement candidate monitor/controllers and separate:

```text
passive pattern;
effectful but memoryless controller;
record-sensitive selector;
persistent selector;
recovery-modulating selector;
and destructive self-maintainer.
```

The output should be a feature profile, not `valuer = true`.

### Stage 4: Omega realization object

Implement:

```text
Real(G);
downward-closure of nonempty fibers;
maximal-face enumeration;
fiber retention;
pairwise-but-not-joint obstruction;
and duplicate-presentation controls.
```

Reuse the existing generated hollow-triangle witness rather than constructing a
new declared compatibility example.

### Stage 5: projection audit

Verify:

```text
isomorphic and bisimilar presentations agree;
sound abstractions provide the intended one-sided result;
an information-losing projection can hide directional grain;
and an injected label cannot create proto-valuer evidence.
```

### Stage 6: stochastic recovery, then moral interpretation

Only after the process interface stabilizes:

```text
add stochastic viability and recovery profiles;
attach NOLP to affected candidate processes;
retain order and risk sensitivity explicitly;
and revisit lushness and normative allegiance.
```

## 16. Kill Conditions

Stop and revise the foundation if:

```text
the proposed grain detector separates systems solely because of arbitrary
reverse-process conventions;

the proto-valuer filtration cannot distinguish endogenous policy from an
analyst's relabeling;

support-only machinery is silently used to claim sensitivity to transition
weights;

Omega changes under duplicate copies or exact presentation renaming;

one maximal face is selected without an additional declared rule;

pairwise compatibility is treated as joint compatibility;

an information or entropy scalar is promoted directly to value;

or lushness is installed as a premise while described as a derivation.
```

## 17. Open Questions

### Immediate mathematical questions

1. What is the smallest practical interface shared by nondeterministic,
   stochastic, and rewrite-system adapters?

2. Which reverse-process conventions should the finite stochastic protocol
   admit, and which are controls?

3. Which behavioral equivalence should define action equivalence in the first
   proto-valuer fixture?

4. How should finite process monitors compose with active control without
   introducing a privileged process boundary?

5. Which realization-fiber quotient is justified by exact equivalence, and
   which distinctions must remain raw?

6. Under what conditions does local statistical asymmetry produce global
   transience, metastability, or functional foreclosure?

### Later theory questions

7. Which proto-valuer features are stable under reasonable changes of process
   projection?

8. How should identity, lineage, redundancy, and fungibility be represented
   across scales?

9. How should stochastic recovery profiles constrain NOLP without a hidden
   scalar threshold?

10. Can reflective corrigibility and nonprivileged projection supply a
    noncircular reason to preserve open-ended compatible differentiation?

11. Which physical systems instantiate the abstract process and compatibility
    objects under independently justified adapters?

12. Can the physical adapter recover thermodynamic entropy production,
    record-bearing agents, and the Omega compatibility object in one coherent
    model?

The last question is the project's completion target.

## 18. Relationship to Established Mathematics

The proposal is intended as a synthesis and licensing architecture, not as a
replacement for the fields it uses.

Representative neighbors:

- J. J. M. M. Rutten, [Universal coalgebra: a theory of systems](https://ir.cwi.nl/pub/48/).
- P. Cousot and R. Cousot, [Abstract interpretation: a unified lattice model for static analysis](https://cs.nyu.edu/~pcousot/COUSOTpapers/POPL77.shtml).
- A. Joyal, M. Nielsen, and G. Winskel, [Bisimulation from open maps](https://doi.org/10.1006/inco.1996.0057).
- L. Doyen and M. De Lara, [Stochastic viability and dynamic programming](https://arxiv.org/abs/1002.1140).
- G. E. Crooks, [Entropy production fluctuation theorem and the nonequilibrium work relation](https://doi.org/10.1103/PhysRevE.60.2721).
- U. Seifert, [Stochastic thermodynamics: principles and perspectives](https://arxiv.org/abs/0710.1187).
- J. Rauh et al., [Coarse-graining and the Blackwell order](https://arxiv.org/abs/1701.07602).
- D. Sutter, M. Tomamichel, and A. Harrow, [Strengthened monotonicity of relative entropy via recovery maps](https://arxiv.org/abs/1507.00303).
- S. Abramsky and A. Brandenburger, [The sheaf-theoretic structure of non-locality and contextuality](https://arxiv.org/abs/1102.0264).

The likely contribution, if the program succeeds, is not a new replacement for
coalgebra, viability theory, stochastic thermodynamics, or contextuality. It is
a common discipline for:

```text
deciding which presentations may be trusted;
tracking when policies create unrecoverable continuation loss;
retaining non-marginal compatibility and obstruction structure;
and preventing bounded decision procedures from licensing through fabricated
or presumed facts.
```

## 19. One-Paragraph Public Compression

Alpha-Omega is a proposal for studying value-bearing continuation without
assuming a fixed agent, utility function, or privileged description of the
world. It models exact controlled dynamics, compares forward and reversed
history laws, identifies persistent processes whose internal state selects
among causally different continuations, and constructs the full compatibility
structure of their possible joint realizations. Its decision layer asks what
bounded observers may license when actions can make recovery harder or
impossible and when abstractions can hide that loss. The current repository
contains finite and Lean-backed components of this program; valuerhood,
standing, lushness, normative allegiance, and the complete physical
instantiation remain open.

## 20. One-Sentence Thesis

> Alpha-Omega studies how persistent, policy-bearing processes arise and
> coexist in oriented continuation structures, and how bounded observers can
> act without fabricating or unnecessarily foreclosing the possibilities on
> which future value depends.
