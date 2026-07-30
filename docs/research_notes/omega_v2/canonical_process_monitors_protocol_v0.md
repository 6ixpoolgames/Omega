# Canonical Process Monitors Protocol v0

Status: preregistration / post-freeze quarantined finite pilot

Scope: finite control systems, certified finite edge observations,
deterministic finite-state property monitors, passive history lifts, bounded
process-relative continuation profiles, and recovery of property-relative
admissible actions

Provenance: successor to `dynamic_continuation_profiles_report_v0.md` and
`bounded_behavioral_logic_protocol_v0.md`; the frozen Omega checkpoint
`cc4c89c` and its retained verdicts remain unchanged

Claim boundary: not identity, selfhood, consciousness, will, agency,
valuerhood, standing, patienthood, intrinsic continuation relevance, moral
license, or Omega validation

## Purpose

The exact world state used by the dynamic pilot is Markovian. A passive history
tracker cannot add physical actions or physical successors to that system. It
can only expose declared path-sensitive facts or track progress through a
declared path-sensitive specification.

This pilot therefore asks two bounded questions:

1. Can deterministic process memory be derived canonically from a finite trace
   property rather than hand-authored as a tracker?
2. Can a history distinction alter future process-relative profiles or
   property-relative admissible actions after current world behavior and
   current monitor output are matched?

## Certified Observation Interface

Let a finite world edge be:

```text
e = (x, a, y)
```

An observation interface supplies:

```text
observe(e) =
  (Atom(x), ActionClass(a), Atom(y)).
```

Requirements:

```text
ActionClass is total on world actions;
state identifiers never enter the symbol;
renaming world states preserves every symbol;
renaming actions preserves symbols when ActionClass is transported with the
renaming.
```

The positive atoms and action classes remain declared interface content.

## Property Automata

Use a complete deterministic Moore automaton:

```text
P = (Q, q0, Sigma, Update, Emit)
```

where:

```text
Update : Q x Sigma -> Q
Emit   : Q -> finite set of declared process facts.
```

A safety-property monitor additionally declares:

```text
SafeQ : Q -> Prop.
```

Generic trace monitors can support history-profile checks. Only monitors with
`SafeQ` feed the property-relative corridor and admissible-action checks.

Input properties are automata, not LTL formulas. The v0 scope is bounded
horizon or otherwise explicitly finite-index. No claim is made for arbitrary
omega-regular properties.

## Canonical Residual Monitor

For one presented property automaton, quotient reachable monitor states by
future-output equivalence:

```text
q ~ r
iff
for every finite observation continuation w,
  Emit(Update*(q,w)) = Emit(Update*(r,w))
  and, when SafeQ exists,
  SafeQ(Update*(q,w)) = SafeQ(Update*(r,w)).
```

The quotient is the minimal deterministic Moore presentation of the declared
finite-index property, unique up to state renaming.

Predictive relevance is relative to the declared property. Minimality does not
show that the property matters for physical continuation.

## Passive Lift And Unique Lifting

The lifted states are:

```text
(x, q)
```

and:

```text
(x,q) -a-> (y,q')
iff
x -a-> y
and
q' = Update(q, observe(x,a,y)).
```

For every lifted state and every concrete outgoing edge, total deterministic
update supplies exactly one lifted edge above it.

Elementary target:

```text
every concrete finite path has exactly one lift from a chosen fibre point;
projection of that lift is the original concrete path.
```

Categorical interpretation:

```text
the monitor induces a covariant finite-set functor on the concrete path
category;
the lifted system is its category of elements;
the projection is a discrete opfibration.
```

The elementary path-lifting result is the implementation contract. No category
library is required in v0.

## Projection Conservation

Construct a world-atom-only view of the lift by excluding monitor emissions
from lifted state atoms.

Required bounded theorem check:

```text
B_h^lift_without_emit(x,q) = B_h^world(x)
```

for every reachable lifted state and every audited horizon.

This is the no-new-physical-capability control. `Update` determines the
available process-memory ceiling; without monitor-dependent emitted facts or a
property-relative gate, passive memory cannot change world behavior.

## Nontrivial Residues

Let `z = (x,q)` and `z' = (x',q')`.

### History residue

```text
HistoryResidue_h^P(z,z')
iff
  B_h^world(x) = B_h^world(x')
  and Emit(q) = Emit(q')
  and DerivedCap_h^lift(z) != DerivedCap_h^lift(z').
```

Matching current monitor emissions blocks direct label injection from counting
as a result. Any retained difference must arise from future process behavior.

### Corridor residue

For safety-property monitors, compute the greatest fixed point inside `SafeQ`
on the lifted system. Define:

```text
Admissible_P(z) =
  action classes with at least one outcome
  whose every lifted outcome remains in the property-relative kernel.
```

Then:

```text
CorridorResidue^P(z,z')
iff
  HistoryResidue_h^P(z,z')
  and Admissible_P(z) != Admissible_P(z').
```

This is continuation relevance relative to `P`, not intrinsic relevance.

## Invariance Axes

Do not conflate monitor implementation and property choice:

```text
implementation-invariant:
  unchanged across sound-complete automaton presentations of the same property;

property-relative:
  retained for at least one preregistered property;

family-core:
  retained under every property in the preregistered property family;

family-dependent:
  retained under some but not all properties;

absent:
  retained under none.
```

An empty family-core residue is a valid outcome.

## Shared Fork Fixture

Use one finite world:

```text
origin
  -- route_alpha --> hub
  -- route_beta  --> hub

hub
  -- choose_alpha --> alpha_future
  -- choose_beta  --> beta_future
```

The terminal futures have distinct positive world atoms and persistent
self-loops. The two route histories end at the same exact world state.

Use three declared automaton properties:

```text
ancestry_match:
  the completion branch must match the observed route;

completion:
  either completion branch is acceptable;

fixed_hazard:
  one fixed completion branch is refused independently of route history.
```

The run asks whether the route-history pair has a history or corridor residue
for each property and whether any residue survives the whole family.

## Symmetric Copy Control

Build a copy fork whose two branches have:

```text
equal world atoms;
equal action classes;
isomorphic continuations.
```

The observation interface must give both branches the same symbols. A monitor
that separates them through raw state identifiers fails the sprint. Without
certified symmetry-breaking evidence, the fixture verdict is `unresolved`.

## Preregistered Cases

### PM1 - Observation equivariance

State relabeling and transported action relabeling preserve observed edge
symbols.

### PM2 - Canonical minimization

Two automata presenting the same property, one with redundant future-equivalent
states, minimize to the same canonical payload.

### PM3 - Unique lifting

Every reachable lifted state and concrete outgoing edge has exactly one lift.
Every audited concrete path has exactly one projected-equal lifted path.

### PM4 - Projection conservation

The world-atom-only lift has exactly the projected world behavior signature at
every audited horizon.

### PM5 - Direct-emission negative control

Two histories with different current emissions do not qualify as a nontrivial
history residue.

### PM6 - Property-relative residue

Run the exact history- and corridor-residue predicates on the shared fork for
all three declared properties.

### PM7 - Symmetric copy

The no-identifier copy fork remains unresolved.

### PM8 - Family-core residue

Classify the shared history pair as:

```text
family-core;
family-dependent;
absent.
```

No outcome is required for retention. The test fails only if the classification
is ambiguous, changes under equivalent monitor implementation, or depends on
raw identifiers.

## Evidence Classes

Instrument correctness:

```text
PM1 through PM5;
PM7;
canonical implementation invariance in PM2.
```

Risky finite result:

```text
the PM6 per-property residue vector;
the PM8 family classification.
```

The report must publish correctness and risky-result sections separately.

## Success Conditions

The pass succeeds only if:

1. property automata are complete and deterministic;
2. minimization preserves future outputs and safety status;
3. unique step and path lifting pass;
4. projection conservation passes;
5. raw identifiers cannot distinguish the symmetric copy;
6. current emitted-label differences cannot satisfy `HistoryResidue`;
7. per-property and family verdicts are reported exactly;
8. empty residue remains an accepted result;
9. no old retained verdict changes.

## Kill Conditions

Stop and report rather than widening the object if:

1. arbitrary tracker states are used instead of property residuals;
2. state identifiers enter observation symbols;
3. lifted memory changes physical behavior without emitted facts or a declared
   property gate;
4. a property-relative result is described as intrinsic process identity;
5. unbounded monitorability is assumed;
6. category language replaces rather than explains the elementary lift.

## Public Compression

A finite path property induces a canonical passive memory state. Lifting exact
world dynamics through that memory cannot create physical capabilities, but it
can expose history-dependent future obligations relative to the declared
property. Whether any such distinction survives a family of properties is an
experimental result, and an empty residue is allowed.
