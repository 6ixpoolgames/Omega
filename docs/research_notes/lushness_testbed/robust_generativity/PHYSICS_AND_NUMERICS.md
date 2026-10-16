# Physical and numerical contract — engineering v1

This is a new adapter. Earlier compounding and spatial experiments are unchanged.

## What is physically represented

`(e,r,A,B,C,D)` records bank quanta, packet presence, three functional apparatus
types and unavailable material. `P=M-A-B-C-D` is usable precursor. Hardware and
precursor exchange one-for-one; the sink transfers hardware to D without
removing it from the material ledger. State history has no particle identities,
controller, genealogy, signal clock or detector flags.

A catalyses B construction, B catalyses C construction, C catalyses A
construction; A also catalyses resource capture. Both directions of a paid
construction pair use the same parent-dependent coefficient. With parent
distinct from product, the coefficient is identical at the two endpoints.
Sublinear feedback uses the square root of the parent count, not a changed
stoichiometry or energy bill.

The Hamiltonian is `H=0.5e+3r+A+B+C`. The physical count multiplicity is
`g=M!/(P!A!B!C!D!)`. Within a fixed-D dark sector the equilibrium weight is
proportional to `g exp(-beta H)`.

## Balance derivation

For a paid P-to-i build, charge falls by 2 and hardware energy rises by 1.
Thus `deltaH=-1`. The forward/reverse ratio is

    P/(n_i+1) * exp(beta),

which equals `g(target)/g(origin) * exp(-beta*deltaH)`. Catalytic coefficients
cancel, including fractional feedback and bilateral link ablations. Thermal
build/break has ratio `P/(n_i+1) exp(-beta)`; unpowered disassembly and its
reconstruction reverse have the same ratio. Bank leakage/overhead and their
thermal reverses have ratio `exp(beta*0.5)` for a debit. Overhead is an energy
cost; it does not directly stabilize hardware or grant free repair.

Capture converts a packet of energy 3 to bank loading u<=2.5. For each actual
origin its reverse has rate `h exp[-beta(3-u)]` relative to forward rate h.
Saturation has several origins mapping to the same full bank. Every origin has
its own reverse edge, including full-bank packet-to-heat loss with u=0. Packet
decay has thermal return `decay*exp(-3beta)`. Consequently the entire packet/bank
chemistry, not merely a packet-empty subset, obeys dark detailed balance.

Driven packet inflow imports work 3. External damage is an explicitly
nonequilibrium boundary. At fixed total damage delta, repairable P return gets
fraction 1-rho and irreversible D transfer gets fraction rho. Thermal assembly
does not change when damage is swept. Dark tests remove the drive and external
damage while retaining all bath channels and each represented fixed-D sector.

The compiler independently checks energy flow, observable drift, legal state
updates and generator row sums. Identical physical endpoints aggregate before
entropy; native reaction labels are flux/query data only. A single event
enumeration supplies the exact generator and the event sampler.

## Funding

Gross capture loading can include the initial packet, bath return and reverse
capture. It is not all newly accepted external work. The external-spending
lower bound deducts the **entire packet energy** of all such non-external
sources, plus the final bank, from gross capture loading before division by
total bank expenditure. Reverse capture's bank debit belongs in that expenditure.
This intentionally loose bound avoids adding energy-provenance labels to
physical history. The complete ledger reports initial stores, inflow, capture,
reverse return, bath imports, costs and final stores separately. A zero-drive
control must report zero external funding despite capture and recycling.

## Sparse class analysis

The new class-aware backend retains a full sampled physical kernel under a
160 MiB gate, computed in row blocks. Graph analysis finds every closed class.
Each class gets its own stationary entropy rate; transient rates are their
harmonic extension through the actual generator. No irreducibility assumption
is applied to material-loss worlds.

For cadence dt, row entropy g and harmonic rate r, solve

    (I-P_dt)b = g-dt*r.

One anchor per recurrent class fixes the offset gauge. A sparse continuous
generator factor preconditions the sampled solve. An anchor is selected at a
high-probability class state to avoid rare-state residual amplification. The
exact finite sampled-history vector at T=n*dt is

    ell_T = T*r+b-exp(Q*T)b.

No asymptotic approximation is used for finite scores. The limiting offset
removes the harmonic class-average component of b. Tests compare finite scores,
rates and offsets against the existing independent dense class solver, including
multiple closed classes with unequal rates and real sink chemistry. The
query-side depth lifts remain sparse and never require a sampled entropy kernel.

## Scope and next gate

Engineering validates this chemistry, depth/recovery queries, numerical solver
and compute budget. It does not score C/R/L/J, search scientific winners or freeze
predictions. The scientific batch planner, full report/decomposition integration,
piecewise pulse-history entropy and final tolerances/markers still require the
scientific freeze. In particular, a prescribed deterministic pulse contributes
no fresh conditional entropy itself, but pre- and post-pulse physical histories
must both be included in a future pulse-arm score.

This count adapter contains no translational motion. Its results cannot resolve
the prior lattice seed-versus-unbound reversal. Spatial extension, actual valuers,
ethical sufficiency, open-ended expansion, whole-type knockout and a matched
single-type network comparison remain separate questions.
