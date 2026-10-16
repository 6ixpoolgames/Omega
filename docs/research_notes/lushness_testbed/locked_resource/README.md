# Locked-resource companion fixture

This tiny finite-state adapter represents one resource as locked, available, or
converted to a downstream product, alongside one apparatus and a finite fuel
store. Its four coordinates are `(locked, product, apparatus, fuel)`. The
resource inventory is fixed at one; the apparatus/fuel slot is capped at two
coarse energy units. This is a finite adapter accounting convention, not a
complete molecular material stoichiometry.

Basal exchange is slow but strictly positive in both directions and obeys the
same energy-based rate pairing used by the paid route. Apparatus assembly uses
one stored fuel unit. Catalytic release also consumes fuel, and its reverse
relocks the resource and restores fuel. Available resource can be converted to
product through a reversible downstream channel. No catalytic release event
exists without apparatus. `stored_fuel_energy_consumed` records depletion of
the stored fuel inventory (negative on the reverse event). It is an internal
state-energy transfer, not external work: all fixture events have
`Event.work == 0`, and the compiler's `drive_work` ledger remains zero. Fuel
chemical energy remains in the complete state energy, so it is not counted a
second time as incoming drive work.

The two roots in `PROTOCOL_DRAFT.json` have equal total energy: the organized
root has apparatus plus one fuel, and the unorganized root has two fuel. They
are compared under the same finite-store generator, so any difference is a
transient profile. This fixture has no maintained-supply arm.

The only authorized execution so far is the engineering smoke: compile the
15-state world, check its ledgers and short-time transition propagation, and
start from both roots. It runs from an immutable source bundle in a Windows Job
Object with 120 s, 1 GiB, and 256 MiB wall, memory, and output caps.
`PROTOCOL_DRAFT.json` is deliberately not frozen and does not authorize
scientific rankings.
