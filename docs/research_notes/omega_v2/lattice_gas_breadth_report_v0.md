# First local lattice-gas comparison: effective continuation breadth

2026-10-07. Exact finite-state calculation. Final run ~6.93 seconds, excluding
interpreter startup; seven focused tests passed. No chemistry rules reused.

## Result

The new machinery supports the requested base comparison. Some deliberately
arranged colliding presents have greater effective weighted future breadth than
the full invariant gas-reference average, at matched particle number, kinetic
energy, total momentum, box and update law. Spatially separated streams do not.

The main qualification is substantial: this very small gas has many closed
communicating components. Against the invariant reference within its own component,
the colliding preparation has a finite phase advantage on the 3x3 lattice and
ties at the sampled even horizons on 4x4. The large full-sector excess is not
evidence of sustained growth beyond its own accessible equilibrium dynamics.

This is an actual stochastic lattice gas, but four particles on a tiny torus do
not establish a bulk thermodynamic/hydrodynamic result, constructive generativity,
valuerhood, or the adequacy of breadth as lushness.

## Published physical substrate

Implemented FHP-I, six unit-speed velocity channels per triangular-lattice site.
There is exclusion within each velocity channel. Two exactly opposite particles
scatter into either other opposite pair, probability1/2 each. Alternating triples
reverse deterministically. All other occupancies keep their velocities through
the collision stage. All sites collide simultaneously, then particles stream one
link. Random choices are independent across sites/ticks; different serializations
of simultaneous updates are not counted as separate outcomes.

Source: Frisch, d'Humieres, Hasslacher, Lallemand, Pomeau and Rivet,
*Lattice Gas Hydrodynamics in Two and Three Dimensions*, Complex Systems 1 (1987),
Figure4 and section2.2:
https://content.wolfram.com/sites/13/2018/02/01-4-7.pdf .
The collision table and invariant-measure argument received a separate narrow
reference audit before running.

All comparisons use four particles and zero total vector momentum. Unit speed
fixes kinetic energy with particle number. There is no added fuel, drive, binding,
rate coefficient, per-update energy tax or organism/catalyst label. Randomness is
part of the effective classical law; it is not a quantum microscopic derivation.
Periodic boundary conditions create recurrences. Enlarging 3x3 to4x4 changes both
density and recurrence geometry, not merely numerical resolution.

## Exact reference rather than uncertain equilibration

The local collision matrix is doubly stochastic. Streaming is a permutation of
site/velocity channels. Therefore their composition preserves uniform measure
on every closed fixed-(particle number, momentum) sector.

| Torus | Conserved-sector configurations | Transition branches | Closed components | Largest component |
|---|---:|---:|---:|---:|
| 3x3 | 23,571 | 29,079 | 4,707 | 99 |
| 4x4 | 239,808 | 273,288 | 44,909 | 504 |

Rows and columns sum to one exactly. No transitions connect distinct strongly
connected components. The uniform sector law is an exact invariant gas reference,
but not the unique equilibrium reached from every root. We therefore report both
the entire sector and each root's dynamically accessible component.

For each reference configuration x, compute its own rooted future entropy ell_x.
Do not add entropy of choosing x. The reference profile reports mean ell and
log(mean exp ell) separately: exponentiating mean ell gives geometric-mean breadth,
whereas averaging breadth directly gives arithmetic-mean breadth. Neither is
silently selected as a canonical frame aggregator. The full rooted distribution
and its quantiles are retained in the local summaries.

## Predeclared preparations and finite-horizon results

1. Two head-on pairs already at two collision sites.
2. Two pairs positioned to meet after streaming.
3. Oppositely moving streams on disjoint rows, avoiding collisions.
4. Four particles occupying one site in two opposite-direction pairs.

All obey the same law and resources. They are geometrically arranged preparations,
not assumed self-maintaining entities. Stored posthoc maximizing configurations
are labeled as posthoc and are not used as registered winners.

At horizon16, L=exp H(complete sixteen-tick future|exact present):

| Preparation/reference | 3x3 L | 4x4 L |
|---|---:|---:|
| Two colliding pairs | 4,096 | 65,536 |
| Pairs aimed to meet | 1,024 | 65,536 |
| Separated counterstreams | 1 | 1 |
| Packed four | 1 | 6,013.87 |
| Full-sector gas reference: geometric mean | 11.46 | 4.47 |
| Full-sector gas reference: arithmetic mean | 238.22 | 839.58 |

Thus the first prepared arrangement beats even arithmetic-mean reference breadth
by about17.2x and78.1x respectively. This is not a comparison of a known structure
with an initially uncertain gas distribution; every future calculation is rooted
at a definite configuration.

The contrast also appears at shorter horizons. At horizon4 the colliding pairs
give16 on both lattices, versus sector arithmetic means2.41 and1.94. The aimed
preparation has one deterministic first tick, then branches once collisions become
available. Configuration changes when and how branching becomes accessible.

## What conditioning on the accessible component reveals

The colliding preparation belongs to a27-state component on3x3 and a288-state
component on4x4. At horizon16:

| Comparison for colliding preparation | 3x3 | 4x4 |
|---|---:|---:|
| Prepared L | 4,096 | 65,536 |
| Own-component arithmetic-mean L | 2,048 | 65,536 |
| Ratio | 2 | 1 |

On3x3 the log excess over component geometric-mean breadth is0.9242 at horizons
1,4,16,64. It is a bounded phase advantage, not an increasing asymptotic rate
advantage. On4x4 the initial one-tick advantage disappears at tested horizons
4,16,64. Both component means give the same tie there to numerical precision.

The stationary full sector contains many collision-free components. Entering a
collision-rich component by preparation explains much of the full-sector excess.
That is a real structural difference in the chosen ensemble; it must not be
misreported as thermal relaxation from every state toward one common baseline.

## What this candidate measures here, exactly

Each pair-collision site supplies an independent fair binary outcome. Streaming
is bijective, so it cannot merge those outcomes within a tick. If c(x) counts
the pair-collision sites in configuration x, then

    H(K(x,.)) = c(x) log 2
    log L_x(n) = log 2 * E_x[sum_(t=0)^(n-1) c(X_t)].

This is an identity, not a fit. Native weighting enters through the expectation
over subsequent configurations. For four particles c<=2, so L<=4^n. All updates
have the same native tick; no infinitely fast loop or resource creation was used.
Deterministic transport and triple scattering add no branch entropy themselves.

Consequently the observed advantage is a capacity to sustain stochastic collision
opportunities, aided by the periodic geometry. The candidate registers that
physical branching honestly. It does not yet distinguish constructive composition
from repeated collision activity if their complete-path entropy is the same.
No cycling/noise correction has been imposed to force a preferred answer.

The invariant-reference mean obeys exactly

    mean_x log L_x(n) = n * mean_x H(K(x,.)).

Equilibrium branching rates are0.219931 and0.135108 bits/tick on3x3 and4x4. The
maximum error in the identity across reported horizons was2.67e-15.

## Implications and next useful probe

We now have a published local physics adapter and an exact thermal-compatible
reference on the same object. Native weighted breadth can exceed the full-sector
reference for selected arrangements. That supplies a finite witness for this
candidate, not a universal optimum or a finished lushness measure.

The next uncertainty is the severe low-particle/periodic decomposition. A larger
or denser case should compare collision-rich preparations with the correct
accessible equilibrium reference and report boundary-return times. At larger
sizes the entropy identity permits estimating log breadth from collision counts
with uncertainty intervals, without enumerating the full tree. This should precede
claims of a broad viability corridor. Reactive/construction rules should come
from a separately justified published model, not be added merely to beat gas.

## Artifacts and checks

New adapter `omega_v2/finite/lattice_gas.py` exposes native steps to the existing
multiway interface and an exact-sector sparse kernel. Runner:
`python -m omega_v2.validation.lattice_gas_breadth_v0`.

Seven tests cover all64 local configurations (conservation and double
stochasticity), pair/triple rules, streaming, global conservation/probability,
translation equivariance and simultaneous independent collisions. Lint passed.
Raw summary JSON stays local/ignored in lattice_gas_breadth_v0/. No commit/push.
No figure was needed; tables and exact identities carry the result.
