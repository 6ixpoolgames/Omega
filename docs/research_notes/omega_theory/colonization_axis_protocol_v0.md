# Colonization Axis Protocol v0

Status: preregistration / discovery protocol
Scope: finite witness search for a cross-scale viable-refinement coordinate
Claim boundary: not lushness, not value, not moral standing, not agency, not identity, not Omega validation

## Purpose

This sprint tests whether there is an independent cross-scale continuation
coordinate that survives the current control panel:

```text
same ordinary viability / language / recurrence / maintenance summaries,
different certified viable-refinement structure.
```

The sprint is allowed to fail. A negative result is not cleanup; it is the
answer for this protocol.

## Batch 0 Commitment

This note is frozen before building the candidate systems. Later reports must
quote the verdict table below rather than changing the target.

## Fixed Horizon And Equality Mode

All control-panel comparisons in this v0 sprint use exact equality at the
declared horizons:

```text
H = {1, 2, 3}
```

No post-hoc horizon changes are allowed in the v0 report.

## Divergence-Side Control Panel

Two systems count as matched only when all of the following agree exactly:

```text
1. viable-state count;
2. start-state corridor membership;
3. viable-word counts at horizons H = {1, 2, 3};
4. recurrence class count inside the viable subgraph;
5. own-maintenance score;
6. entropy proxy, defined as log2(max(1, viable-word-count at h=3));
7. leading-lambda proxy, defined as the spectral radius proxy used by the
   witness harness if computed, otherwise explicitly recorded as not computed.
```

The v0 sprint may compute a simple exact finite proxy for leading lambda, but
failure to compute it must be recorded before witness evaluation. It may not be
backfilled selectively after seeing a candidate pair.

## Colonization Coordinate v0

The coordinate is defined over registered certified chains, not over a single
chosen presentation.

Finite objects:

```text
System:
  finite transition system with a declared viable predicate and start state.

Presentation:
  a surjective map from concrete states to abstract cells.

Certified viable presentation:
  a presentation whose abstract viable structure is the exact image of the
  concrete viable structure used in this sprint.

Certified chain:
  a finite sequence of certified viable presentations ordered from coarse to
  fine.
```

For v0, a chain level records a **viable-cell partition**: the collection of
abstract cells that contain at least one viable state.

```text
ColonizationProfile(S) =
  the registered finite set of certified viable-refinement chains for S.
```

`A` colonization-refines `B` when there exists a registered certified chain in
`A` and a registered certified chain in `B` such that:

```text
1. every level of B is matched by a level of A;
2. matched A levels map onto matched B levels by a cell-surjection;
3. at some matched level, A has strict viable-cell surplus over B;
4. the surplus level is not visible in any divergence-side control-panel
   quantity listed above.
```

The coordinate is an order/comparison over certified viable-refinement chains.
It is not a scalar dimension, not entropy, and not a value claim.

## Candidate Pair Target

Batch A attempts to build two systems with at most twelve states each:

```text
Branching B:
  viable structure admits a two-level self-similar refinement chain.

Basin F:
  same control-panel values, but only a flat viable refinement chain under the
  registered presentations.
```

The matching constraint is the load-bearing requirement. A pair with different
viable-word counts, viable-state count, recurrence count, or start membership
does not support a separation claim.

## Demotion Gauntlet

Batch B must attack any apparent separation with three checks:

```text
1. Lens / presentation audit:
   does the registered colonization comparison survive the declared certified
   chain transport checks?

2. Converse witness attempt:
   can two systems share the same registered colonization class while differing
   on corridor or joint behavior?

3. Scalar-shadow check:
   do obvious scalar summaries of the refinement chains, such as level count
   and max branching ratio, fail to explain the order comparison?
```

For v0 these are retained finite audits, not a global Lean theorem.

## Verdict Table

The final report must use exactly one of these verdict classes:

```text
separated:
  a matched pair exists, the registered colonization coordinate separates it,
  and the demotion gauntlet does not reduce the difference to the control
  panel or scalar shadows.

reduces:
  every apparent colonization difference in the searched family leaks into a
  control-panel quantity or scalar shadow.

ill-posed:
  the finite coordinate cannot be defined or evaluated cleanly enough to make
  the above comparison.
```

## Kill Condition

If Batch A cannot find a control-panel-matched pair in the searched family, the
report must not claim a new axis. It must report either:

```text
reduces
```

or:

```text
ill-posed
```

with the failure mode named.

## Lushness Boundary

This sprint does not derive lushness. It tests one candidate typed coordinate
that might later be part of a descriptive lushness profile.

Normative lushness remains explicitly undeclared by theorem:

```text
richer-is-better is a declared premise unless certified to align with
protected persistence, recovery, or standing.
```

## Public Compression

```text
The colonization-axis sprint asks whether cross-scale viable refinement has an
independent finite signal after matching ordinary viability, language,
recurrence, entropy, and maintenance summaries. If it does not, lushness remains
an open problem rather than a hidden scalar.
```
