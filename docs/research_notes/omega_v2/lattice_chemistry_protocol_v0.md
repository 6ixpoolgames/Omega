# Reversible 2D chemistry: first exploratory pilot

2026-10-04. A substrate probe, not a lushness candidate or a gas-versus-life
ranking. This note records the choices before the sampled run. It can be
revised with a new version; it does not prescribe an outcome.

## Physical representation and rationale

- A reflecting square lattice contains identical excluded-volume building
  blocks. Positions are physical; particle IDs only allow replay. The lattice
  is a coarse physical geometry, not a claimed continuum mesh refinement.
- Each block switches between concealed (0) and exposed (1) conformations.
  State 1 costs delta=0.75 kBT. Two-state interaction models have precedent in
  [Whitelam et al. (2009)](https://wrap.warwick.ac.uk/id/eprint/28672/).
  These names specify physical interactions, not content or value identities.
- Explicit nearest-neighbor bonds have free energy -epsilon when both ends
  are exposed and -epsilon/2 otherwise. This minimal two-affinity table is
  our adaptation of additive contact models, not a fitted molecular force
  field. There is no target aggregate. Both binding and unbinding occur;
  changing conformation includes changes to all existing bond energies.
  See [lattice contact-energy precedent](https://arxiv.org/html/2110.11274v1).
- Rigid bonded components translate by one site in any unobstructed cardinal
  direction at rate D/n per direction, n their particle count; D=1 fixes the
  time unit. No teleportation, overlapping particles, rotation, bending or
  automatic bond formation on contact. D/n is a simple additive-drag
  approximation. Collective motion is relevant to assembly, as in
  [Whitelam et al. (2009)](https://arxiv.org/abs/0806.3903). This is not a
  reproduction of their full simulator. Without rotations some rearrangements
  require disassembly; this remains a declared limitation.
- Fuel F and waste W share an ideal well-mixed inventory, B=F+W=N. The fuel
  standard free energy exceeds waste by 4 kBT, independently of epsilon.
  Pool volume scales with B, so a fixed F/B gives a fixed reservoir
  concentration. This models a shared bath coupled to a 2D assembly layer;
  changing surface occupancy does not silently change reservoir concentration.
  It omits spatial supply and local depletion.

For each full state x, in kBT units:

    E(x) = 0.75*number_exposed + sum_bond_energies + 4*F
    G(x) = E(x) - log binomial(B,F)
    pi(x) proportional to exp(-G(x)).

Spatial configurations are explicit. Only unresolved fuel/waste multiplicity
is folded into G. The sampled state quantity G(x) is not the ensemble's
nonequilibrium free energy; the latter also depends on its distribution.

## Rates and the explicit catalytic hypothesis

Let f(d)=1/(1+exp(d)). It satisfies f(d)/f(-d)=exp(-d).
This bounded rate choice is a declared kinetic approximation, not a measured
rate law. Local detailed balance fixes the ratio, not the absolute speed.
The thermodynamic framework is
[Rao and Esposito (2018), Section III B](https://arxiv.org/abs/1805.12077).

| Transition | Rate |
|---|---|
| Conformation switch with local energy change d | 0.2 f(d) |
| Thermal unbound to bound with bond energy e | 0.2 f(e) |
| Thermal bound to unbound | 0.2 f(-e) |
| Unbound + F to bound + W | 0.5 (F/B) f(e-4) |
| Bound + W to unbound + F | 0.5 (W/B) f(4-e) |

Every mechanism separately obeys q(x,y)/q(y,x)=exp(-(G(y)-G(x))).
Spontaneous thermal breakup does not regenerate fuel. Catalysis adds a
parallel path to the fuel-coupled pair only; both directions are accelerated.

**Template geometry:** for a target nearest-neighbor bond, an exposed bonded
pair on the opposite side of a unit square supplies a catalytic pathway.
Its two members are adjacent to the two reactants. The chemical interpretation
is cooperative transition-state stabilization by two preorganized contacts.
The catalyst's positions, conformations and bond remain unchanged during the
reaction. This is an explicit effective mechanism hypothesis, not a finding
that molecular catalysts universally have this geometry. It replaces the old
line's equal-bit rule. No preferred lattice direction or particle identity is
used. Two sides can provide two parallel pathways.

Each available template contributes (exp(b)-1) times the background fuel
rate. For one template the total rate becomes exp(b) times the background.
Binding and its reverse share the same unchanged catalyst, preserving pi.
The initial b values are 0 and 2, a no-assistance control and a 7.39-fold total
rate with one template. This parameter is kinetic, not an additional reward.
Template binding intermediates, sequestration and saturation are unresolved;
the rule approximates a rapidly releasing catalytic path.

Product bonds can supply the same assistance later. An optional historical
observer records the depth of actual catalytic production: an unassisted bond
starts at depth 0 and a catalytically formed bond inherits catalyst depth+1.
This observer never changes rates. Repeated mutual templating can raise depth,
so depth does not by itself demonstrate a new repertoire or lushness.

## Small parameter bracket and observations

32 configurations, 12 trajectories each, ten workers maximum. Cuts 0,1,5,10,20.
No exhaustive phase survey; the two energy scales probe weak versus stronger
binding relative to kBT, and the density bracket probes encounter/crowding.

- N=16 on sides 8 and 6; N=36 on sides 12 and 9. The matched densities are
  1/4 and 4/9. Boundary fractions differ with size and remain part of the model.
- epsilon=1 or 3; b=0 or 2; all other kinetics held fixed.
- Dispersed preparation: uniform sampled distinct sites, independent fair
  conformations, no bonds, F=B.
- Seeded preparation: a central square of four exposed particles with one
  prebuilt bond; remaining particles placed randomly, F=B. This supplies one
  initial template opportunity. It has different preparation energy/content
  from dispersed, so their difference is a nucleation/initial-condition probe,
  not a resource-matched comparison. Same preparation is used across b.

Record particles bonded, bond count, component sizes, loops, exposed states,
fuel, thermal/chemical/catalytic forward and reverse events, template
opportunities and production ancestry. Retain initial/final states and every
timed physical event for every replicate, including catalyst route IDs.
No trajectories or failure outcomes are filtered. Initial seeds are shared
across kinetic choices; dynamics seeds are independent. Report means and
Monte Carlo standard errors, without declaring precise phase boundaries.

Neither initial preparation is thermal equilibrium. A proper equilibrium-gas
comparison is not supplied by relabeling the dispersed preparation. This run
asks whether the larger substrate exhibits interpretable construction,
reversal, fuel use and geometry; it does not implement the full continuation
access atlas or choose a lushness aggregation.

## Checks needed before the run

Exhaust all 768 fixed-position full-occupancy 2x2 states (four binary conformation variables,
four possible bonds, B=2) for per-mechanism forward/reverse balance. Check
moving partially occupied configurations, inventory/event conservation, event
replay, whole-apparatus rotation and particle renaming. Check that quiescent
paths retain every requested horizon and that b changes kinetics without
changing the energy law. These are consistency checks, not physical calibration.
