# Embodied friction on access — implemented first slice

15 October 2026. Model and measurement version 1.

## Physical carrier

The state is `(packet, D_location, D_apparatus, D_charge, S_location,
S_apparatus, S_charge, D_friction_device)`. There are 2,304 states with one
apparatus/precursor constituent per subject, two charged/spent carrier
constituents per subject, one friction-device/precursor constituent, and one
shared resource-packet slot. Inventories are conserved inside each pool; the
packet source and export are declared open boundaries.

Four coarse physical compartments have distinct native functions:

- Access: shared packet capture, enhanced by local working apparatus.
- Construction: a paid carrier-to-apparatus reaction and its reverse.
- Trap: low mobility and a lower location energy, giving slow return.
- Neutral: native motion and chemistry without capture or paid construction.

These role labels are analysis descriptions, not moral labels or additional
state. Thermal assembly, carrier fluctuations, device formation/loss and packet
fluctuations continue in every arm. The apparatus-to-capture-to-construction loop
is paid. Capacity one tests reconstruction and sustenance, not depth-three
compounding. The existing multi-type experiment establishes the latter separately.

The total energy is

    H = 2*packet + D_apparatus + D_charge + S_apparatus + S_charge
        + D_friction_device - [D_location=trap] - [S_location=trap].

State multiplicities are the binomial count multiplicities of the apparatus and
carrier pools. Native reversible rates use mass-action propensity times
`exp(-beta*deltaH/2)`. Construction assistance depends on apparatus that remains
as a spectator in both forward and reverse reactions. Trap mobility is 0.012;
other mobility is 0.12. Beta is 1. Supply is 0.04 or 0.12 in the first map.

Kappa changes D's apparatus-assisted capture by `1+kappa*S_apparatus`, equally
for forward and reverse capture. S therefore supplies a physical complementary
capability to D. At kappa zero, resource rivalry still couples the subjects.

## Friction module

The first module targets S's movement into or out of a selected compartment.
S's native chemical channels remain present. It operates only with D's working
apparatus, an intact friction device and enough D charge to pay the selected
bill. Hardware construction consumes charge; native upkeep and loss continue
with phi zero. There is no immortal external actuator.

Blocking splits a native movement attempt into an unblocked movement at rate
`(1-phi)*q` and a blocked attempt at `phi*q`. A paid blocked attempt changes D's
charge and leaves S unchanged. At zero cost it changes no state and is absent
from the physical generator; its suppressed-attempt intensity remains a query.
With a positive bill, blocking replaces the rejected S movement by a real
D-charge transition. Whole-world exit activity therefore need not fall even
when S's movement rate does. No global entropy loss is imposed by deleting the
attempt's physical cost consequence.

Steering retains the unblocked movement and redirects the remaining rate to
other physically available S outcomes, weighted by their native rates. These
include local chemistry as well as movement. This gives a real alternative
when confinement targets every exit from a single compartment. A redirected
event pays D's bill and preserves the destination's physical state and ledger
updates, including construction or capture if those occur.

Steering matches S's total exit rate at the same full state. It does not match
long-horizon activity, occupancy, accepted source work or thermal exchange.
Costs above storage capacity are rejected rather than silently becoming an
inactive intervention. All-mobility steering is not provided: the design's
all-transitions version needs further physical destination definitions.

Active friction is an explicit one-way nonequilibrium kinetic-control boundary.
Its D fuel and released/absorbed bath heat enter the first-law ledger. Native
chemistry is detailed-balanced with both the source and active friction removed.
This does not certify thermodynamic reversibility of the active control
implementation: its reverse chemical realization and entropy budget are separate
physical refinements. The module exposes this assumption rather than presenting
energy conservation alone as a full thermodynamic proof.

## Reference preparations and actions

Three roots have H=6 and the same shared packet and S state:

| Root | D apparatus | D charge | D device | D compartment |
| --- | ---: | ---: | ---: | --- |
| Device present | 1 | 0 | 1 | access |
| Ordinary preparation | 1 | 1 | 0 | access |
| Unassembled preparation | 0 | 2 | 0 | neutral |

The unassembled root retains the same degrees of freedom and native formation
routes. It is a coarse count preparation, not microscopic gas. The programme's
universal subject reading is retained; no extra value weights are assigned to
the organized constituents.

Preparation comparisons under the idle law are reported separately from
friction-policy contrasts using the device-present root. Their energy accounting
is explicit. None models the action of excising an existing subject: that would
need a common-start conversion, its costs and consequences.

## Measurements

Complete conditional sampled-history entropy is primary, with cadences
0.125/0.25/0.5 and horizons 16/64/256/1024. Exact class-aware sampled-Poisson
queries produce the finite scores and diagnostic rates. All physical events
count; duplicate event routes are aggregated by full physical destination.

D projects to its location, apparatus, charge and device. S projects to its
location, apparatus and charge. D/S joint histories exclude the packet background.
Hidden-history conditioning bounds certify intervals for their marginal
entropies. Exact short-prefix enumeration validates the query on a tiny fixture.
Overlapping difference intervals are unresolved, not ties. Possible subject
maximizers retain every candidate not excluded by those bounds.

History mutual information is bounded from D, S and D/S joint intervals,
conditional on the common exact initial frame. Background-first coordinate
contributions are reported under both D/S orders. They are explanatory shares,
not subject objectives or unique causal entropy contributions.

Every case records capture, construction and reverse flows, device costs,
stock/deadline/occupancy profiles, suppressed attempt intensity, first passage,
expected physical jump count and the finite temporal term. The asymptotic
temporal crossover remains an estimate, beside the exact cadence profiles.
The initial S compartment is access; its first-passage-to-access probability
therefore includes unit initial target mass and is not a diagnostic of later
return. Occupancy and capture comparisons remain informative.

## First mechanism map

INITIAL_MAP.json contains 24 configurations: two supplies, two kappa values,
and six fixed interventions per environment:

1. Idle friction device.
2. Blocking entry to access.
3. Steering entry away from access.
4. Blocking entry to construction.
5. Steering entry away from the trap.
6. Steering exits back into the trap's internal alternatives.

Active cases use phi0.5 and a one-quantum bill. Idle cases additionally evaluate
the ordinary and unassembled roots. This initial slice maps kind and coupling;
it is not the full strength/cost/region sweep. The report compares every active
case with its same-environment idle case. Whole-field and subject choices refer
only to this fixed candidate family, not arbitrary adaptive control.

## Expansion and execution

Separate native chemistry, background and mobility/friction modules expose
versioned event laws through the shared compiler. Capacities and coefficients
are explicit physical parameters. State budgets reject an oversized carrier
rather than truncate inventories. Future damage/recovery, more apparatus,
alternative friction mechanisms, sensing and shared control need their own
declared physical supports and energy updates.

The current marginal-history occupation solver requires an irreducible law.
An absorbing damage extension must use a class-aware projection query rather
than reuse this assumption. Future population and cross-scale extensions should
preserve the existing native whole and treat higher-level roles as queries until
their causal dynamics are explicitly implemented.

Run snapshots record the source/configuration and execute under 120-second,
512-MiB, 32-MiB-output process-tree caps. Compact JSON retains the measurements;
large transition matrices remain ephemeral. Identical source/configuration
requests reuse verified result files. A 900-second default batch budget keeps
surveys bounded and resumable.

Reproduce:

    python -m pytest tests/test_domination_friction.py -q
    python scripts/run_domination_friction.py smoke
    python scripts/run_domination_friction.py survey --config docs/research_notes/lushness_testbed/domination_friction/INITIAL_MAP.json
    python scripts/report_domination_friction.py

Working expectations guide investigation; no guessed numerical threshold
defines success of the programme. Report the signed outcomes and structural
explanation, including gains from intervention churn and unresolved rankings.
