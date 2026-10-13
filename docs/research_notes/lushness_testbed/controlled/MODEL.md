# Controlled access: first finite substrate

Frozen before scientific execution, 2026-10-13. This is an authored, thermodynamically
accounted coarse reaction model, emitted to BioNetGen for generator verification.
It is not a published biological model. The existing binding calibration is the
external engine calibration. Neither the objective nor the rates contain an
ethical reward.

## Physical state and law

Two compartments each hold one reusable material unit in condition precursor
(b=0), worn (b=1), or active apparatus (b=2), one carrier with charge f=0/1,
and a service/export gate g=0/1. Each local state has 12 possibilities; the full
world has 144. No molecule label or reaction name is an extra state. Both controllers
remain installed when apparatus disassembles; this is not death of an embodied
valuer. Population and hardware inventory are fixed. Compartment topology is fixed.

Energy in kBT is E=b+2f per compartment; gates have degenerate energies. beta=1.
Every elementary pair has forward/reverse rates

    k+ = a exp((w - (E_y-E_x))/2)
    k- = a exp(-(w - (E_y-E_x))/2).

Thus log(k+/k-)=w-Delta E and bath heat is w-Delta E. The finite-state sites
have degeneracy one. All reverse channels are retained, including rare reverse
reconstruction and reverse fuel synthesis. Fuel is a two-state carrier, not a
unit of free energy that disappears outside the ledger. Positive temperature
does not imply every event consumes work; uphill thermal events are possible.

| Family | Transition | Attempt factor and consequence |
|---|---|---|
| Gradient capture | f0 <-> f1 | .04 times 6 when active; chemical work +/-4 |
| Fuel bath | f0 <-> f1 | .04; no chemical work |
| Service construction | b0,f1,g0 <-> b2,f0,g0 | .3; charge converted to apparatus energy |
| Service repair | b1,f1,g0 <-> b2,f0,g0 | .5; charge used, excess heat released |
| Wear/thermal restoration | b2 <-> b1 | .04; reversible bath exchange |
| Disassembly/thermal restoration | b1 <-> b0 | .08; material retained |
| Gate export selection | f1,g0 <-> f0,g1 | .15 p(b); fuel-paid switch and thermal reverse |
| Gate service selection | f1,g1 <-> f0,g0 | .15 (1-p(b)); fuel-paid switch and thermal reverse |
| Exchange | f1,f0 <-> f0,f1 | .4 per endpoint whose export gate is open |

An open export gate enables passive exchange in both directions. Opening one's
own end does not require permission from the other controller. It therefore
permits resource withdrawal but does not establish an appropriation verdict.
Both-open pathways add rates, not extra physical endpoint labels. All operations
take stochastic physical time. Competing operations cannot consume the same charge
twice. Rest/passive control closes both switch pathways while native physics runs.

Active apparatus lowers capture barriers in both directions, preserving that
channel's equilibrium ratio. It does not create an extra energy reservoir.
The drive bath has chemical potential 4, the thermal bath zero. Setting the drive
potential to zero gives equilibrium Boltzmann detailed balance under every policy.
With drive, capture and dissipation form a powered cycle. Shared external chemical
potential and attempt scale constitute a matched boundary, not a fixed successful
energy-input budget: better apparatus can capture more work. Report actual work.

## Controller, cost and information

A policy specifies an export bias p for each local inactive/active observation.
Both compartments choose independently from p in {0,.5,1}; all 81 ordered policy
pairs are enumerated. Sixteen pairs have only 0/1 biases. The remaining 65 include
stochastic response settings. These are coarse catalytic barrier selectors with
thermal back-action, not infallible commands: even a deterministic setting retains
reverse physical switches. The factor p weights an actuator pathway and its reverse
together; selecting it cannot supply an unaccounted chemical affinity.

Gate changes expend stored fuel in the forward direction. Local state-dependent
sensing and the hardwired response table are idealized passive catalytic coupling;
there is no independently billed sensor or computation register. Policy search
and its RNG occur outside the world. Random controller choices are represented
through the resulting gate/charge process; there is no retained coin register.
Sub-cadence events are omitted by the declared sampled readout, not denied to be
physical. There is no extra action-label entropy or random bill.

Service and transfer conflict through gate state, finite fuel and elapsed time.
Construction, wear, paid repair and resource exchange therefore alter accessible
future transitions. A paid enabling loop exists: drive charge -> service assembly
-> faster capture -> further charge -> repair or exchange -> service elsewhere.
Only two apparatus sites exist, so this is finite enabling and retention, not
population growth, lineage, or open-ended compounding.

## Comparisons and claims

Organized root is two active empty apparatus, gates service; disassembled root
is two precursors with full carriers, gates service. Both have energy 4 and identical
matter, law, controller, reservoir and hardware. They are not microcanonical gas
ensembles; report them as energy-matched preparations. Same-policy stationary
conditional breadth is the additional background reference, with no prior entropy.

Optimize full-state sampled path entropy. Primary cadence .25 is one quarter
of fixture A's base dissociation time. It is an operational clock, not a universal
resolution. Cadences .125 and .5 are sensitivity queries. Uniform speed factors
.5 and 2 apply to all reactions and controller pathways together, at fixed physical
horizon/cadence; this is a time-scale sweep, not a temperature change. The rate
constants are chosen and frozen for a small mechanism test, not fitted to lushness
rankings. Do not claim a calibrated universe.

Rank by asymptotic bits/time then organized-root offset after irreducibility/residual checks;
also retain finite-horizon winners. Report ties within 1e-9 and actual maximization
scope. Exact means enumerated finite-chain calculation in floating point, not
symbolic arithmetic or a global optimum over all controllers.

For the winning policy, split its entropy rate by the chain rule into next
apparatus/fuel given the full previous state, and next gate given that apparatus/
fuel and the full previous state. This diagnoses how much breadth resides in
the resolved gate state. It is not the entropy of an isolated projected process.

Surveys include expected functioning per compartment, simultaneous function,
stored fuel, work/heat, gross construction/repair/wear, net service/switch fuel,
resource exchange, first functional reconstruction and endpoint retention.
These have zero objective weight. Reconstruction is functional, not identity.
Self-subject histories, coercion, irreversible identity loss, new populations,
long-lived memory and Rule A are deferred and must not be inferred from this run.
