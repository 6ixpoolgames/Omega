# Omega Decision Stack Checkpoint v0

Status: documentation checkpoint / stack map
Scope: ODT0 licensing, robust corridor instantiation, ODT1 dominance, finite
acceptance bridges, deterministic and stochastic Blackwell-shaped
conservativity, and ODT2 registered arbitration
Claim boundary: not complete decision theory, not final value, not aggregation,
not arbitration, not agency, not identity, not valuerhood, not moral standing,
not probability-aware risk handling, not full stochastic Blackwell theorem, not
Le Cam deficiency, not Omega validation

## Compression

The current decision stack is:

```text
ODT0 licenses.
ODT1 compares.
Deterministic Blackwell factorization simulates policies.
Stochastic garbling simulates randomized policies.
ODT2 arbitration is registered least-violation only.
```

ODT0 is a conservative decision floor. It licenses an action or plan only when
its justifying route is certified, the action preserves the declared corridor,
and any decision-process identification is consequence-inseparability-certified.

ODT1 consumes already-licensed outcome surfaces. It compares them by declared
preorder dominance rather than choosing a final action. The declared outcome
preorder and monotone valuation discipline remain ledger content.

The deterministic Blackwell wrapper shows that deterministic experiment
factorization is compatible with ODT1: if a coarser observation factors through
a finer observation, every coarser-observation policy compiles into a
finer-observation policy with the same statewise actions and the same outcome
surface. The closure theorem also proves the converse: universal deterministic
policy simulation recovers the factorization map.

The stochastic Blackwell v0 wrapper proves only the forward finite-rational
garbling direction: a randomized policy over the garbled observation compiles
into a randomized policy over the finer observation with the same induced
state/action mass.

ODT2 now exists only as registered arbitration: a nonempty finite frontier with
a declared Nat-valued violation score has a least-violation candidate. The
score is registered input, not moral authority.

## Landed Surface

### ODT0 Floor

Lean files:

```text
formal/lean/OmegaProper/Decision/License.lean
formal/lean/OmegaProper/Decision/Examples.lean
```

Documentation:

```text
omega_decision_floor_v0.md
```

Landed content:

```text
certified-route licensing;
corridor-safe action gate;
plan licenses checked on transported successor surfaces;
route-addition monotonicity at fixed context register;
context-register expansion can revoke quotient inseparability.
```

### Robust Corridor Instantiation

Lean files:

```text
formal/lean/OmegaProper/Decision/RobustCorridor.lean
formal/lean/OmegaProper/Decision/RobustCorridorExamples.lean
```

Documentation:

```text
robust_continuation_corridor_v0.md
```

Landed content:

```text
controlled greatest fixed point for declared constraints and requirements;
corridor states have an allowed enabled action preserving the corridor;
actions with a concrete successor outside the corridor fail the corridor gate.
```

### ODT1 Structural Dominance

Lean files:

```text
formal/lean/OmegaProper/Decision/Dominance.lean
formal/lean/OmegaProper/Decision/DominanceExamples.lean
```

Documentation:

```text
omega_decision_dominance_v0.md
```

Landed content:

```text
Hoare / angelic dominance;
Smyth / demonic dominance;
Plotkin dominance;
failure certificates;
incomparability witness;
angelic/demonic divergence witness;
valuation-class relativity witness.
```

### ODT1 Acceptance Bridges

Lean files:

```text
formal/lean/OmegaProper/Decision/DominanceAcceptance.lean
formal/lean/OmegaProper/Decision/DominanceAcceptanceExamples.lean
formal/lean/OmegaProper/Decision/DominanceFinite.lean
formal/lean/OmegaProper/Decision/DominanceFiniteExamples.lean
```

Landed content:

```text
Hoare dominance iff unanimous pointwise angelic cover across monotone valuations;
Smyth dominance iff unanimous pointwise demonic floor across monotone valuations;
finite best-case acceptance theorem for Hoare dominance;
finite worst-case acceptance theorem for Smyth dominance.
```

### Deterministic Blackwell Conservativity

Lean files:

```text
formal/lean/OmegaProper/Decision/BlackwellDeterministic.lean
formal/lean/OmegaProper/Decision/BlackwellDeterministicExamples.lean
```

Documentation:

```text
omega_decision_blackwell_conservativity_v0.md
```

Landed content:

```text
deterministic experiments as observation maps;
factorization as deterministic informativeness;
factorization iff universal deterministic policy simulation;
policy compilation along a factorization;
statewise action preservation;
exact outcome-surface preservation;
Hoare/Smyth/Plotkin equivalence of compiled and original policy surfaces;
identity-to-constant factorization and constant-not-to-identity strictness.
```

### Stochastic Blackwell Forward Bridge

Lean files:

```text
formal/lean/OmegaProper/Decision/BlackwellStochastic.lean
formal/lean/OmegaProper/Decision/BlackwellStochasticExamples.lean
```

Documentation:

```text
omega_decision_stochastic_blackwell_v0.md
```

Landed content:

```text
finite exact-rational stochastic experiments;
finite exact-rational randomized policies;
finite rational garbling;
randomized policy compilation along a garbling;
compiled randomized policy validity;
preservation of induced state/action mass;
tiny point-to-half garbling example.
```

### ODT2 Registered Arbitration

Lean files:

```text
formal/lean/OmegaProper/Decision/Arbitration.lean
formal/lean/OmegaProper/Decision/ArbitrationExamples.lean
```

Documentation:

```text
omega_decision_arbitration_v0.md
```

Landed content:

```text
NatViolationFrame over a nonempty finite frontier;
LeastViolation predicate;
existence of a least-violation candidate;
leastViolationChoice with correctness theorem;
toy three-option least-violation example.
```

## Current Open Edges

These are open, not claimed:

```text
ODT0 -> ODT1 concrete outcome-surface compiler:
  `LicensedOption` is still abstract in ODT1.

abstract/exact robust-kernel reflection:
  needed before abstract robust continuation certificates should certify exact
  robust continuation.

Phi / Requirement adequacy:
  the formal corridor consumes declared requirements; it does not prove their
  value relevance or moral standing.

full stochastic Blackwell / Le Cam:
  deferred. The current stochastic bridge proves garbling -> randomized policy
  simulation, not the converse theorem over all decision problems.

Bayes risk / expected utility:
  deferred. The stochastic bridge preserves action mass only.

ODT2 authority:
  open. The least-violation procedure consumes a declared violation score; it
  does not decide standing, commensurability, or legitimacy.
```

## Dependency Shape

The current dependency shape is:

```text
certified presentation / route facts
  -> ODT0 G1

declared corridor predicate
  -> ODT0 G2

controlled robust corridor
  -> one concrete instantiation of ODT0 G2

certified quotient inseparability
  -> ODT0 G3

ODT0-licensed option outcome surfaces
  -> ODT1 structural dominance

declared outcome preorder
  -> monotone valuation acceptance bridges

deterministic experiment factorization
  -> policy compilation
  -> exact outcome-surface preservation
  -> ODT1-equivalent comparison

finite rational stochastic garbling
  -> randomized policy compilation
  -> induced action-mass preservation

registered finite frontier + declared violation score
  -> least-violation candidate
```

The non-derived pieces remain explicit:

```text
declared fact language;
declared consequence contexts;
declared corridor / requirement;
declared outcome preorder;
declared valuation discipline;
declared finite outcome surface compiler.
declared violation score / arbitration authority.
```

## Immediate Roadmap

Highest-priority options, in order of current leverage:

```text
1. ODT documentation freeze:
   keep the stack readable while stochastic and arbitration surfaces remain
   deliberately narrow.

2. ODT0 -> ODT1 integration hook:
   define a small certified outcome-surface compiler interface from licensed
   actions/plans into `LicensedOption`.

3. Robust-kernel abstraction reflection:
   prove when abstract robust-corridor membership reflects to exact
   robust-corridor membership.

4. Stochastic Blackwell converse:
   defer unless a paper specifically needs the full iff theorem.

5. ODT2 authority records:
   only after deciding what value input is allowed to enter arbitration.
```

## Nonclaims

The stack does not yet claim:

```text
complete decision theory;
optimal action selection;
final value;
correct valuation class;
standing or moral status;
valuerhood;
agency;
identity or selfhood;
aggregation;
arbitration;
probability-aware risk;
full stochastic Blackwell theory;
Le Cam deficiency;
quantum structure;
Omega validation.
```
