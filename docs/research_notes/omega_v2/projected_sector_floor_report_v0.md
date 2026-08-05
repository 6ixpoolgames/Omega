# Projected-Sector Floor Report v0

Status:

```text
retained finite exact support-level foundation fragment
```

Protocol:
[Projected-Sector Floor Protocol v0](projected_sector_floor_protocol_v0.md)

Theory ledger:
[Alpha-Omega Fundamental Theory Ledger v0](alpha_omega_fundamental_theory_ledger_v0.md)

Protocol commit:

```text
62fb6c9 Preregister projected sector floor
```

Retained run:
[20260805_194734](../validation_results/projected_sector_floor_v0/20260805_194734/)

Summary digest:

```text
5166685c7b47f25026522c64d0bae7c474762faf7803ee20944199dd391e5363
```

## Verdict

The retained verdict is:

```text
projected_order_retained_and_sector_properties_separate
```

All 19 preregistered cases passed. No kill condition fired.

The sprint establishes a clean support-level floor beneath the existing
controlled-Markov, controller, realization, and compatibility machinery:

```text
finite labelled transition system
+ declared ordered projection
-> nondecreasing transition relation
-> projected reach preorder
-> mutual-reach equivalence
-> antisymmetrized partial order
```

It also shows on exact finite fixtures that:

```text
termination;
recurrence;
branching;
local and global confluence;
projection polarity;
and independent commutation
```

are distinct properties. They do not collapse into one defensible
`coherence` Boolean.

## Reusable Machinery

The clean Python package now includes:

```text
FiniteTransitionSystem
FiniteProjection
ProjectionPolarity
FiniteHistory
FiniteSystemIsomorphism
DeclaredIndependence
CommutingDiamond
DiamondAudit
ProjectionProfile
SectorProfile
```

The transition system permits:

```text
partial dynamics;
nondeterministic branching;
cycles;
termination;
and empty outgoing rows.
```

It does not assume a controller, action policy, probability kernel, protected
predicate, process boundary, valuer, or objective.

The history API keeps four comparisons separate:

```text
exact equality;
declared relabeling equivalence;
declared length-two commuting-diamond equivalence;
projection-level equality.
```

## Formal Fragment

Formal file:

```text
formal/lean/OmegaV2/Finite/ProjectedOrder.lean
```

The file uses a generic `Preorder` index rather than the integer levels used
by the finite executable adapter.

Retained definitions and theorems:

```text
TransitionSystem;
OrderedProjection;
ProjectedStep;
ProjectedReach;
MutualProjectedReach;

ProjectedReach.refl;
ProjectedReach.trans;
ProjectedReach.level_mono;

MutualProjectedReach.refl;
MutualProjectedReach.symm;
MutualProjectedReach.trans;

projectedReachIsPreorder;
projectedPreorder;
ProjectedOrder;
projectedOrderPartialOrder;
mutualProjectedReach_is_equivalence.
```

The quotient is not bespoke. It uses Mathlib's standard
`Antisymmetrization` construction.

The formal result assumes:

```text
a transition relation;
an ordered projection;
and projection-nondecreasing step selection.
```

It derives the order structure that follows from those inputs. It does not
derive or privilege the projection.

## Fixture Panel

### Terminating confluent disintegration

```text
root -> left  -> dust
root -> right -> dust
```

Retained:

```text
terminating: true
branching states: 1
locally confluent: true
globally confluent: true
recurrent components: 0
```

This is the required control showing that a stable transition law may
lawfully disintegrate. Persistence is not a prerequisite for lawfulness.

### Recurrent cycle

```text
a -> b -> a
```

Retained:

```text
terminating: false
recurrent components: 1
branching states: 0
```

Recurrence therefore does not imply branching.

### Genuine nonconfluent branch

```text
root -> left
root -> right
```

with distinct terminal children.

Retained:

```text
terminating: true
locally confluent: false
globally confluent: false
```

Termination therefore does not imply confluence.

### Independent commuting diamond

Two exact histories are retained:

```text
root -a-> left  -b-> joined
root -b-> right -a-> joined
```

Retained:

```text
exactly equal: false
same projection sequence: true
commuting-diamond equivalent: true
detected diamonds: 1
diamond failures: 0
```

This is a minimal local concurrency audit. It is not a general trace-monoid,
event-structure, or higher-dimensional rewriting implementation.

### Projection controls

The null cycle retains:

```text
polarity: NULL
level transitions: 2
projected components: 1
```

The one-sided chain retains:

```text
polarity: POSITIVE_ONLY
projected source classes: 1
projected sink classes: 1
```

The Janus source retains:

```text
polarity: BIDIRECTIONAL
Janus sources: center
```

The Janus control does not select either polarity as preferred. It records
that one source has outgoing transitions in both directions of the declared
projection.

## What This Pays

The immediate debt paid is structural:

```text
before:
  controller and Markov adapters supplied directed dynamics first;

now:
  the clean floor accepts any finite labelled support relation and derives
  only projection-relative order and exact sector diagnostics from it.
```

This gives future adapters a common target:

```text
physical law adapter;
probabilistic support adapter;
graph-rewrite adapter;
bounded all-rules completion adapter.
```

The abstract all-rules or "rulial" move is therefore available without
becoming the ontology or mandatory execution model of every theorem.

The sprint also pays a terminology debt. The implementation reports named
standard properties rather than using `coherence` as an undifferentiated
classifier.

## Fundamental Theory Position

The accompanying theory ledger records the current intended stack:

```text
relational structures
-> rewrite completion or supplied law sector
-> declared projection/order
-> projected sector profile
-> histories and continuation classes
-> Alpha-capable pattern dynamics
-> valuer-bearing trajectories
-> Capital Omega compatibility object
-> Gradient Ethics after the remaining normative bridge
```

This sprint lands only the first executable portion of that ladder. The
larger objective remains visible, but no upper-layer term is read backward
into the foundation.

## Validation

Canonical commands:

```text
.\.venv\Scripts\python.exe -m pytest tests\test_omega_v2_projected_sector_floor.py -q

.\.venv\Scripts\python.exe -m omega_v2.validation.projected_sector_floor_v0 --out-root docs\research_notes\validation_results\projected_sector_floor_v0

powershell -ExecutionPolicy Bypass -File scripts\setup\invoke_lake.ps1 build OmegaV2
```

The retained run includes:

```text
summary.json
fixtures.csv
sector_profiles.csv
projection_profiles.csv
projected_components.csv
history_comparisons.csv
commuting_diamonds.csv
report.md
```

## Claim Boundary

This sprint establishes:

```text
finite exact projection-relative reachability;
the generic projected-reach preorder;
mutual-reach equivalence;
the standard antisymmetrized partial order;
finite termination, recurrence, branching, and confluence diagnostics;
and one exact length-two commuting-diamond audit.
```

It does not establish:

```text
selection of the laws of an actual universe;
a canonical projection;
a measure over rule space;
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

## Next Debt

The cleanest next debt is not another upper-layer instrument. It is one
adapter-level test of the new floor:

```text
bounded rewrite-completion adapter
-> projected-sector interface
-> compare retained sector profiles across rule-language exhaustion
```

That protocol must specify:

```text
the finite relational signature;
the bounded rewrite language;
the exhaustion order;
the projection family;
and the stabilization or non-stabilization verdict.
```

No distribution over all rules is needed for that bounded audit.

The alternative next move is to define a persistence/pattern candidate over
projected histories. That should wait until the rewrite adapter determines
which history invariants are actually stable rather than installing a desired
identity condition by hand.

## Public Compression

A projection turns a finite transition sector into an ordered continuation
view, but it does not create persistence, identity, or value. Termination,
recurrence, confluence, and independent commutation are distinct properties
and must be reported separately.
