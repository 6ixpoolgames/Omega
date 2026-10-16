# Same-law reactive lattice: implementation and run specification

15 October 2026. User authorized execution. Engineering precedes a source-frozen
scientific protocol. Earlier compounding experiments remain unchanged.

## Physical realization

Periodic ring with indistinguishable monomers, disjoint nearest-neighbour bond
matchings, one independently mobile carrier of charge0/1/2 and a binary resource
packet at site0. Occupancy/bond masks encode physical positions, not particle IDs.
Energy H = number of bonds + charge + 3*packet. A catalytic pair has positive
stored energy1. Powered joining consumes two locally available charge units and
retains its energy-ratio-consistent reverse. Cluster mobility is half monomer
mobility. Carrier motion has the monomer rate and no extra free energy transfer.

Native thermal joining has positive coefficient. Spectator catalysis changes
both directions of paid joining equally; spectator bond endpoints must be within
ring distance1 of the joining pair. The carrier must be within distance1 of that
pair. Capture requires carrier at source and charge0; it transforms a packet into
charge2 with its native reverse. Catalysts within distance1 of source assist this
pair symmetrically. Charge1 must drain or receive a thermal increment before
capture; saturation is part of the stipulated chemistry, not a discarded event.

Charge leakage plus bond-local upkeep has its native bath reverse. Packet decay
has a thermal reverse. Driven packet inflow adds work3. Independent external
damage breaks a bond while preserving matter and exports its stored energy.
All channels contribute to the full state-history entropy. Duplicate native
routes to one physical endpoint are summed by the existing compiler. No rule-ID
entropy, random-root entropy, controller, Rule A or semantic reward is added.

With source and external damage off, each elementary bath pair and the total
generator satisfy detailed balance with exp(-beta H) at this physical grain.
These are declared toy constitutive rules, not calibrated molecular chemistry.

## Frames and references

Seed: monomers at sites0..N-1, one bond0-1, carrier at0, charge0, packet1. H4.
Three independent references: uniform native states in H4 shell; that shell
conditioned to have no bonds; placement randomization with seed bond count,
charge and packet. No reference is held disordered after time0. One compiled Q
is reused for every root and reference. Thermal weights include initial useful
assemblies and equal-energy reallocation of fuel into bonds. Conditional-root
histories are averaged; H(reference selection) is never added.

Beta changes rates and canonical calibration, not exact-H4 shell weights.
The complete fixed beta grid0.5/1.5/3 is retained without looking at rankings.
In dense6/7 geometry the full shell mostly contains bonds. It is a thermal
mixture, not a dilute gas. The no-bond preparation remains a distinct comparator.

## Measurement and structure

Primary full site/bond/carrier conditional history at T64/cadence0.25, with
T16/256/1024 and cadences0.125/0.5. Exact row-block sampled kernels retain all
states. Sparse continuous Poisson solves precondition sampled Poisson GMRES;
ell_n = n*h+b-exp(Q*T)b computes exact all-root vectors within numerical gates.
This identity is numerically validated against the earlier dense finite solver.
No stationary approximation replaces finite-history scores. All roots in each
irreducible Q share the same limiting rate; offsets are preparation diagnostics.

G1 means any bond. G2 means carrier at the source and a locally coupled catalyst.
G3 means two simultaneous bonds. G3 does not label their ancestry as paid; native
paid, assisted and thermal reaction flows report that separately. First arrival,
time0 mass, mean assembly time, deadline hit and deadline occupancy are distinct.
Any seed/G1 initial hit is zero-time, not a self-assembly achievement. Additional
quantiles/residence distributions remain downstream queries; they are not claimed
to have been calculated in this initial implementation.

Expected jumps, finite temporal coefficient F and local mark surprisal integral
use continuous occupation. Embedded-jump histories at8/32/128 events preserve
sequence entropy but do not compare equal physical durations. No activity is
subtracted. Full random-length event-count/mark/timing entropy is not claimed.
Paid recursive construction is possible locally in the6-constituent world;
whether it produces retained growth and a positive seed advantage is tested.

## Engineering, freeze and scope

Geometries2/4,4/6,6/7 and6/8 are enumerated without physical pruning. Full kernel
budget160MiB, process cap512MiB and120seconds. An oversized geometry stops before
ranking.6/8 is excluded only from execution after its engineering memory gate;
its actual state count is retained. Density and excluded scope remain explicit.

After balance/class/memory/numerical calibration, freeze twelve6/7 cases from
beta0.5/1.5/3 x mobility0.25/1 x native/weak assistance, plus two4/6 pilots.
Weak assistance sets the catalytic increments to zero as a *different common law*
for its own preparation comparison. No direct cross-law difference is called gas
superiority. Damage0.005, other costs/chemistry fixed. Every law keeps all basal
paths, drive and bath. Predictions identify positive and adverse regimes before
ranking, including their exact comparator and all three cadences. Failure to
obtain a predicted sign remains a failure, not a reason to alter the reference.

Numerical residual gate1e-7, sign tolerance1e-5bits. Per-law120s/512MiB/32MiB,
total1800seconds. Frozen source receipts, compact per-law results and full maps
are retained; kernels remain reconstructable ignored local data. No publication
or Drive change is included. This is a bounded, dense physical-grain experiment,
not a microscopic-gas theorem or ethical demonstration.
