# Projected Sector Floor Protocol v0

Status:

```text
preregistration / finite exact support-system protocol
```

## Purpose

Build the first adapter-neutral floor beneath the existing Omega v2
controlled-Markov and controller machinery.

The sprint asks:

```text
Given a finite labelled transition sector and a declared projection, what
ordering, history, and exact structural properties follow without assuming
persistence, identity, valuerhood, or a preferred arrow?
```

The sprint also tests whether several notions previously compressed as
"coherence" separate on explicit finite fixtures.

## Architectural Position

The general semantic interface is a finite labelled transition system. An
adapter may obtain that system from:

```text
an empirically supplied physical law;
a controlled or probabilistic model after taking support;
an algebraic graph-rewrite system;
or a bounded all-rules relational completion.
```

The abstract rulial completion is therefore one adapter, not a prerequisite
for every Alpha theorem.

## Claim Boundary

This sprint may establish:

```text
finite exact projection-relative reachability;
preorder and mutual-reachability structure;
finite termination, recurrence, branching, and confluence diagnostics;
explicit commuting-diamond audits under declared independence;
and separation among those diagnostics.
```

It does not establish:

```text
a unique coherence predicate;
selection of the laws of an actual universe;
a probability measure over rule space;
stabilization of an all-rules limit;
persistence as identity;
vorticality;
observerhood;
agency;
valuerhood;
standing;
value;
Omega compatibility;
Gradient Ethics;
or moral license.
```

## Fixed Finite Objects

### Finite labelled transition sector

Use:

```text
FiniteTransitionSystem:
  system_id;
  finite nonempty state set;
  finite label set;
  unique transition rows (source, label, target).
```

The transition relation need not be:

```text
total;
deterministic;
terminating;
confluent;
recurrent;
or probabilistic.
```

### Projection

Use:

```text
FiniteProjection:
  projection_id;
  total map State -> Int.
```

Integer levels are a finite executable carrier for a more general ordered
index. The formal theorem must use a generic preorder rather than integers.

For a transition `x -a-> y`, classify:

```text
positive:
  p(x) < p(y)

level:
  p(x) = p(y)

negative:
  p(y) < p(x)

nondecreasing:
  p(x) <= p(y)
```

Projection polarity is a diagnostic:

```text
NULL:
  no transition changes level

POSITIVE_ONLY:
  at least one positive transition and no negative transition

NEGATIVE_ONLY:
  at least one negative transition and no positive transition

BIDIRECTIONAL:
  both positive and negative transitions occur
```

`BIDIRECTIONAL` is not automatically Janus structure. A Janus source is a
state with outgoing positive and outgoing negative transitions.

### Projected reachability

Define:

```text
x <=_p y
iff
there is a reflexive-transitive path from x to y using only
projection-nondecreasing transitions.
```

Define mutual projected reachability:

```text
x ~_p y
iff
x <=_p y and y <=_p x.
```

Required theorem fragment:

```text
<=_p is reflexive and transitive;
~_p is an equivalence relation;
projected reachability is monotone in projection level;
the quotient by ~_p carries the induced partial order.
```

The final quotient theorem may use the standard antisymmetrization of a
preorder rather than a bespoke quotient implementation.

## History Layers

Retain distinct notions:

```text
exact history:
  identical state and label rows

relabeling-equivalent history:
  one history maps to the other under a declared system isomorphism

commuting-diamond equivalent:
  two length-two histories differ only by a declared independent swap and
  close at the same target

projected history:
  histories have the same projection-level sequence
```

The v0 machinery must not identify these layers.

A general Mazurkiewicz-trace or higher-dimensional rewrite quotient remains
adapter debt. V0 audits the minimal length-two commuting square exactly.

## Sector Profile

For every finite sector, retain an exact vector:

```text
state count;
transition count;
branching-state count;
sink-state count;
source-state count;
directed-cycle presence;
termination;
recurrent strongly connected components;
bounded-extendable states at the declared horizon;
local confluence;
global confluence;
declared independent-pair count;
commuting-diamond count;
commuting-diamond failures.
```

Definitions:

```text
termination:
  no directed cycle exists.

recurrent component:
  a strongly connected component with more than one state or a self-loop.

bounded extendability at h:
  a path of exactly h transitions exists from the state.

local confluence:
  every pair of immediate successors of one state has a common reachable
  descendant.

global confluence:
  every pair of states reachable from one source has a common reachable
  descendant.
```

Confluence is not called coherence. Termination and recurrence remain
orthogonal to it.

## Preregistered Fixtures

### Terminating confluent disintegration

```text
root -> left -> dust
root -> right -> dust
```

Expected:

```text
terminating;
locally confluent;
globally confluent;
not recurrent;
branching.
```

This is the required control showing that a law may lawfully disintegrate.

### Recurrent cycle

```text
a -> b -> a
```

Expected:

```text
not terminating;
one recurrent component;
not branching.
```

### Genuine nonconfluent branch

```text
root -> left
root -> right
```

with terminal, distinct `left` and `right`.

Expected:

```text
terminating;
not locally confluent;
not globally confluent.
```

### Independent commuting diamond

```text
          a          b
     root -> left  ----> joined
       |                       ^
     b |                       | a
       v                       |
      right -------------------
```

Declare `a` independent of `b`.

Expected:

```text
two exact histories;
one projected history when left and right share a level;
one retained commuting diamond;
zero commuting-diamond failures;
local and global confluence.
```

### Null projection

Assign one level to every state of the recurrent cycle.

Expected:

```text
polarity NULL;
all transitions level;
projected reach retains the original cycle.
```

### One-sided source

```text
s0 -> s1 -> s2
p: 0     1     2
```

Expected:

```text
polarity POSITIVE_ONLY;
one projected source class;
one projected sink class.
```

### Janus source

```text
left <- center -> right
p: -1      0       1
```

Expected:

```text
polarity BIDIRECTIONAL;
center is a Janus source;
the fixture does not select either polarity as globally preferred.
```

## Cross-Checks

The run must verify:

```text
all fixture transition rows are retained exactly;
reachability is reflexive and transitive on every fixture;
mutual projected reachability is an equivalence on every fixture;
the component condensation graph is acyclic;
termination agrees with absence of recurrent components;
local and global confluence separate on the declared controls;
the two diamond histories remain exactly distinct;
the declared diamond closes;
the null projection remains null;
the one-sided source remains one-sided;
the Janus fixture remains bidirectional;
and no single coherence Boolean is emitted.
```

## Kill Conditions

The sprint fails if:

```text
projected reachability is not a preorder;
mutual projected reachability is not an equivalence;
the quotient/condensation relation contains a directed cycle;
the terminating disintegration control is reported nonconfluent;
the genuine branch is reported confluent;
the commuting diamond is not detected;
the two exact diamond histories are merged at the exact layer;
the null projection receives a polarity;
the implementation silently assumes total or deterministic dynamics;
or the report promotes the sector profile to value, agency, or moral status.
```

## Validation Outputs

Retain:

```text
summary.json;
fixtures.csv;
sector_profiles.csv;
projection_profiles.csv;
projected_components.csv;
history_comparisons.csv;
commuting_diamonds.csv;
report.md.
```

## Public Compression

```text
A projection turns a finite transition sector into an ordered continuation
view, but it does not by itself create persistence, identity, or value.
Termination, recurrence, confluence, and independent commutation are distinct
properties and must be reported separately.
```
