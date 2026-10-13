# Structural harm and recovery: first module

The next question is whether policies respond to the consequences of impairment,
when the immediate loss of working apparatus and the per-unit fault hazard match.
This packet is an engineering specification. Scientific candidate lists, exact
score predicates and execution budget must be frozen before policy rankings.

## Physical extension

The existing two-compartment growth law remains the substrate. The new state is
`(left, right, (repair_hardware_left, repair_hardware_right))`. Each hardware bit
denotes a physical intact/broken local assembly with declared energy 1 or 0.
Its fixed material inventory is separate from the apparatus inventory; breaking
it retains its material as broken hardware. It is not a random observation label.

All arms contain the same hardware state space, native thermal events, basal gate
relaxation, fuel drive and paid assembly. A fault changes one active apparatus
unit to one worn unit at hazard times the local active count. The three arms are:

| Consequence | Powered repair | Hardware after fault |
|---|---|---|
| Fast repair | Existing paired rates | Intact |
| Slow repair | Both directions multiplied by 0.1 | Intact |
| Hardware loss | Paired repair requires intact hardware | Permanently broken locally |

Fast repair still costs fuel. Slowing both directions changes kinetics, not the
equilibrium ratio. The third arm removes a particular powered repair capability;
thermal wear reversal, disassembly/reassembly and basal construction remain.
It therefore tests substitutability rather than assuming that any capability
loss closes the whole channel. No controller gains an observation of hardware
unless a later costed sensing module explicitly provides it.

Faults are one-way external damage, with released energy recorded as heat under
the existing first-law ledger. The driven fault law is not an equilibrium control.
Hardware loss changes the energy released by the fault; equal immediate active
stock loss does not imply equal damage energy. Initial pre-fault preparations
have identical hardware, stocks, energy and gates across arms. A post-fault
comparison conditions on the declared physical fault map and must disclose the
different resulting hardware and energy; no entropy of the arm label is added.

## Analysis and scientific gate

Use the full state, including hardware, for complete finite-history lushness.
Retain native failure and thermal tails. Report rates and offsets secondarily,
allowing multiple recurrent classes when hardware is permanently lost. Existing
two-compartment query helpers must be adapted explicitly to this extended schema;
do not silently apply their closure predicate to a third coordinate.

Report working stock, exposure, powered repair availability, hardware-loss first
passage, functional return, uninterrupted retention after return, fuel/heat/work
and reconstruction flux. Functional closure must be derived from reachable native
transitions; a zero powered-repair bit is not itself whole-channel closure.

Use the same prospectively frozen controller family and common T64 deadline in
all arms. Separate fixed-policy replay from changes in the optimizer's choice.
At 3+1 inventory the exact space has 3,840 states: a feasibility gate must precede
the scientific grid. A 1+1 fixed-policy smoke (576 states) checks compilation,
propagation, provenance and caps without inspecting optimizer rankings.

The proposed primary cadence is 0.25, horizons 1/4/16/64/256 and hazards 0.02/0.04.
Audit a frozen subset at 0.125 and 0.5. Keep cadence and state-grain conclusions
distinct. The comparison remains an idealized count-state mechanism experiment.

## Resource-baseline audit and subsequent loop

The maintained-resource v1 already retains paired basal LOCKED/USABLE transitions,
paired USABLE/WASTE downstream transitions, locked export and bounded inflow in
both capable and paid-path-ablated arms. Locked is not physically frozen. The
ablation removes both directions of the paid release pathway only. Those shared
rates must remain when adding feedback; their realized entropy and occupancies
may change when coupling changes access. Boundary prescriptions are matched,
accepted external work is measured rather than assumed equal.

The next feedback module should make downstream conversion supply usable carrier
energy or construction material that can maintain the access mechanism. Declare
resource energy, stoichiometry, reverse route and boundary work before implementing
that link. Compare the loop against its paired-path ablation; diagnose upkeep,
replacement and enabling flux. A finite loop can demonstrate self-maintenance;
open-ended expansion requires a separate growing inventory construction.

Then test controller uncertainty with physical observation costs and model error.
Structural readouts explain the breadth result; they do not add optimizer bonuses.
