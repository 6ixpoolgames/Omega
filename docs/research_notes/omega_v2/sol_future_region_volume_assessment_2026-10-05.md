# Sol's future-region volume proposal: assessment

2026-10-05. Assessment of the user-supplied revision. No new physical simulation,
extent adoption, commit or push accompanies this note.

## What advances

The proposal makes relations between continuations enter the calculation:
accessible regions, their intersections, and distances can affect an extent.
That addresses the previous proposal's specific defect, where attaching a
residual process to a history left every Hill number unchanged.

Keep the separation between native path probability, physical access geometry,
and structural extent. Existing frames already supply the first. Keep a common
physical adapter, finite resolutions and horizons, full consequential history,
all physical noise, and no required winner. Reach facilitates lushness; a
reachable-state count does not become lushness by renaming it.

## 1. Support is too weak for the catalytic mechanism already represented

Consider two states x and y with reversible rates lambda in both directions.
Starting at x, both states have positive probability of being visited by every
T>0, for lambda=1 and lambda=10 alike. Both systems have the same equilibrium,
state support and per-transition energy difference. But

    P_x(first hit of y by T=1) = 1-exp(-lambda)

is 0.632120559 versus 0.999954600. Accelerating both directions is the elementary
kinetic effect of lowering a reversible barrier. A support union with counting
measure ties, while finite-time access changes substantially.

More generally, exp(Q*T) has strictly positive entries for finite irreducible
continuous-time Markov chains at T>0. Existing thermal reverse paths can make
the support insensitive to catalytic acceleration. A shortest possible waiting
time is also inadequate for exponential clocks: its infimum is zero.

This is not missing probability machinery in Omega. It is probability machinery
omitted by a bare support-cone formula. If mu is instead intended to incorporate
native probabilities, specify how it does so alongside structural extent;
substituting normalized probability mass alone does not settle extent.

Retain joint laws of time, resources, outcomes and failure, rather than just
existence of a route. Resource constraints may be vector valued, and physical
access is generally directed. Native dynamics cannot silently be replaced by
an external controller choosing the cheapest favorable path.

## 2. Pairwise overlap cannot reconstruct the whole region

Here is an exact finite example:

    A1={1,2}, A2={1,3}, A3={1,4}
    B1={1,2}, B2={2,3}, B3={1,3}

Every set has size two and every pair within either family intersects in one
element. Both pairwise Jaccard matrices therefore have diagonal one and
off-diagonal one third. But the A union has size four and the B union size
three: their triple intersections differ. A similarity spectrum computed from
these identical matrices and identical weights cannot recover this distinction.

Full set unions retain higher intersections; the proposed pairwise compression
does not generally retain them. This is a limit of that compression, not a
requirement that every valid volume distinguish every nonidentical structure.

There is a separate issue: overlap between alternative cones does not establish
joint physical feasibility. Two developments can each be reachable but compete
for the same token. Conversely a combined development can open continuation
available to neither component alone. The carrier must retain these physically
compatible combinations, not just unions of singleton targets.

## 3. Reconvergence does not erase earlier consequence

Two histories can share a future suffix at a common state, time and resource
condition. Their earlier consequential developments remain different. A damaged
and repaired system need not receive a second copy of the same residual suffix,
but repair must not retroactively remove the damage from the completed history.

Likewise two routes to the same output can differ in location, timing, resource
occupation and resilience. These are part of the physical object, even if a
particular extent assigns equal volume. Counting a shared destination once is
not permission to quotient away the routes or their apparatus.

## 4. Magnitude is relevant mathematics with a direction-of-comparison trap

Ordinary metric-space magnitude uses a similarity such as Z_ij=exp(-d_ij),
after specifying a distance scale. For two points separated by distance d,

    magnitude = 2/(1+exp(-d)).

This increases with distance: d=2 gives 1.761594156; d=1 gives 1.462117157.
If d means physical difficulty of access, catalysis lowering that difficulty
can lower magnitude on the unchanged carrier. This is mathematically sensible
as distinctness, but it is not automatically an extent of improved access.
Expanding an accessible ball and contracting its internal distances may have
opposing effects. They must be investigated, not conflated.

This does not reject magnitude. It separates two geometric questions:
how difficult it is to reach a development, and how distinct developments are
once reached. A single distance need not answer both. Standard metric-space
results also do not automatically apply to directed, resource-vector access.

The published connection between similarity-sensitive diversity and magnitude
is real. But maximum diversity optimizes the distribution; the resulting
weights are not generally the native physical distribution. Do not replace
frame-conditioned weights by the diversity-maximizing distribution. The
relation to magnitude can involve a subset/support, not unconditional equality
with magnitude of the whole space.

## Recommended next construction

Pursue a probability-weighted geometry of jointly compatible physical
developments. Define a finite common carrier and elementary extent in one tiny
existing adapter; keep native timing, resource and residual-process laws over
it. Identify the same continuation physically, including its embedding,
rather than by abstract output labels. Retain historical prefixes when future
suffixes reconverge. No named task family or privileged valuer is needed.

Then evaluate union/coverage and similarity-sensitive extent as candidate
compressions, alongside ordinary path diversity. Do not claim that the full
relational data structure already supplies its own extent. In particular mu
remains a real mathematical choice: counting states, updates, history cells
and physical configurations yields different objects, and subdivision can
change those counts. No conservation of primitive possibility follows from
conservation of matter or energy.

Before a larger atlas, use three cheap discriminators: kinetic acceleration
with unchanged support; individual versus joint access under a shared resource;
and reconvergent histories with different earlier physical consequences.
These check what a formula measures without demanding that gas lose, that
catalysis increase every coordinate, or that any structure be a universal
winner. Once the carrier and extent rule are explicit, small numerical
exploration is appropriate; a uniqueness theorem is unnecessary.

## Primary sources checked

- [Leinster and Meckes, Maximizing diversity in biology and beyond](https://arxiv.org/html/1512.06314).
- [Leinster and Meckes, The magnitude of a metric space: from category theory to geometric measure theory](https://arxiv.org/abs/1606.00095).
- [Leinster and Roff, The maximum entropy of a metric space](https://academic.oup.com/qjmath/article/72/4/1271/6141851).

The finite set, rate and two-point calculations above are direct mathematical
checks, not new chemical simulation results.
