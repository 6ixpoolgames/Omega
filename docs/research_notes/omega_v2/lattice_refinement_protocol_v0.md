# Residual sharing, compartment fuel and mobility: exploratory protocol v0

2026-10-05. The user requested all three recommended refinements together and
a push. This supersedes the assessment's proposed sequential execution. The
crossed panel retains individual and combined effects; there is no required
ranking, no new lushness functional and no mandatory frozen evaluation.

## Representation and physics

`HistoryAtlas` retains timed history occurrences, physical rule reads/writes,
last-writer provenance, native path log densities, cut-to-residual maps, and
all enabled channels with complete successor states. This is not identified
counterfactual causality or a completed concurrency quotient. Prefix trees
retain every marked order; residual sharing never deletes prefixes. Particle
IDs are canonically renamed by physical positions, with maps retained at
each boundary. No rotation, location, fuel allocation, noise or time is erased.
The model's parameter record identifies the law attached to each atlas.

`CompartmentChemistry` adds an ideal reservoir overlay, initially two equal
vertical compartments. Total fuel plus waste B is conserved. Default volume
V=B reproduces the old concentration unit; each endpoint of a target bond
couples with weight 1/2 to its reservoir compartment. Shared-compartment
endpoints combine to weight 1. The reversible reaction changes local F to W
or W to F. Templates accelerate both directions under the old geometry.

Per-molecule fuel/waste hopping from c to d has rate
transport*mean_volume/v_c for adjacent compartments. Thus v_c*d_cd=v_d*d_dc.
The free energy is E_structure + 4*sum(F_c) plus ideal local log-factorial
terms minus local inventory*log(volume). Conditional allocations are
multinomial in volume fractions. Their equilibrium marginal recovers the old
binomial inventory law. Fast mixing gives F/V and W/V reaction propensities.
The full process retains hopping; common chemistry observations project it
out only when comparing the shared-pool limit. Finite transport need not be
Markovian in that projection. Both transport and rigid cluster motion remain
nonrelativistic effective dynamics.

Cluster translations use D/n**gamma per unobstructed cardinal direction.
gamma=1 recovers the old code; gamma=1/2 tests weaker size dependence. Energy,
bond geometry, boundary conditions and equilibrium weights are unchanged.
No rotations, saturation cap, alternate barrier law, or preferred-value
coefficient is added. The parameter report also gives p0, chi, reservoir
capacity ratio and kinetic prefactor ratios; these are coordinates of the
same model, not extra weights.

## Exact panel

Full 2x2 occupancy with four particles, B=2, bond energy=2, catalytic b=0/2.
For each, shared fuel and local transport .05, 1, 20, 400. Enumerate the native
generator; abort rather than silently truncate if the state limit is exceeded.
Initial states: unbound/exposed, one seeded bond, adjacent/opposite two bonds,
and exact equilibrium. All non-equilibrium exact states start with F=2.
Local initial allocation is conditional multinomial mixing, keeping the same
projected state. Compare projected endpoint laws at .25, 1 and 4, total
variation, next-two-chemical-events fuel-binding probability by T=1, and
equilibrium/stationarity errors. Fuel hops are allowed between those chemical
events; switching, thermal events, moves and reversals fail this particular
query. The suffix after two successful bindings is unrestricted.

Compute equilibrium projection and the conditional-average instantaneous
generator identity, but separately report failure of exact lumpability at
finite transport. Derive total entropy production from relative-entropy
decrease in the closed reversible model. Do not rename a count or entropy
diagnostic lushness. Full occupancy cannot probe mobility or gas.

A two-switch process provides an analytic residual-sharing witness: distinct
prefixes reconverge while exact timed cylinder masses remain. The chemistry
atlas additionally unfolds the native square to depth two. Neither is an
empirical discovery claim.

## Mobile crossed panel

N=B=4 on side 4; bond energy 2; catalytic b=0/2; gamma=1/0.5;
shared fuel or two-compartment transport .1/1/10. This gives 16 laws.
Four preparations per law, 48 histories each, horizons 0/.25/1/4/10:

- dispersed, unbound, fueled;
- one centrally seeded bond, fueled;
- sampled equilibrium;
- the same sampled equilibrium configurations refueled to B.

Equilibrium is sampled once from the common physical Gibbs distribution using
the existing collapsed sampler: four chains, 4000 burn sweeps, 128 spacing,
12 samples per chain, alternating dispersed and compact starts. Report the
existing split R-hat diagnostic, without treating it as a mixing certificate.
The equilibrium preparation may already contain assemblies; do not call it
gas merely because it is the control.

Initial physical states are shared across kinetic settings; local fuel is
drawn from the conditional allocation law. Independent dynamics seeds are
declared. Report per-preparation means and Monte Carlo standard errors for
chemistry events, transport events, fuel, bonds, mobile components, template
availability and production depth. Depth is an observer of actual catalytic
production, not repertoire growth. Report complete residual cache counts as
storage diagnostics, never as an extent estimate. No histories are filtered.

Ten workers maximum, bounded exact panel plus a short sampled panel. Store
all initial states, events, provenance and residual tables in the ignored
`lattice_refinement_v0/` directory. Publish only implementation, protocol,
tests, analysis and written results.

## Checks

Per-channel physical reverses, global detailed balance, ideal equilibrium
marginalization, conditional rate averaging, finite-transport discrepancy,
fast-mixing convergence, unchanged mobility equilibrium, complete event
replay, state/inventory validity, particle renaming and prefix mass retention.
Existing chemistry/residual tests must remain valid at gamma=1. These checks
test faithful implementation, not the ethical premise.

Rationale and primary literature:
[modelling assessment](sol_modelling_refinement_assessment_2026-10-05.md).
