# Stage2: damage to capability, restoration and irreversible access loss

Status: implementation design, 2026-10-14. Read README.md for shared commitments.
The current A/W/D model remains a versioned control. Damage is a physical change
in what transitions are enabled, not an externally assigned harm penalty.

## Minimal typed body

Represent each material unit by a two-bit capability profile:

- `A11`: functioning capture and repair/control.
- `A10`: capture remains; repair/control is impaired.
- `A01`: repair/control remains; capture is impaired.
- `W`: neither capability functions, but material is repairable.
- `P`: unassembled precursor.
- `D`: trapped material with declared reversible or absorbing boundary.

Each compartment records counts `(n11,n10,n01,w,d,f,g)` with
`p=M-n11-n10-n01-w-d`. Healthy units can perform both roles, so the one-slot
compartment is not incapable by construction. These are coarse physical species,
not semantic labels for valuers. Separate transport, memory and construction
roles can later extend a capability registry without assuming all roles are
independent or giving their counts a reward.

Declare native capture capacity `n11+n10` and repair/control capacity `n11+n01`.
Capture modifies paired carrier-charge channels, including reverse channels;
control modifies paired commanded selector transitions. Existing policy-free
basal relaxation and passive carrier transport remain. Damage to capture therefore
reduces access to the gradient without directly deleting the control machinery.
Damage to control can leave capture operational while impairing directed repair
and transport. These provide distinct, physically interpretable failure modes.

A tentative energy calibration is P=0,W=1,A10=A01=1.5,A11=2, with D energy taken
from the declared trap arm and charged fuel energy2. This is an adapter assumption,
not established biophysics. Final energies/rates and all boundary conditions must
be listed in the implementation note and frozen before scientific ranking.

## Native transitions and accounting

Provide thermal capability loss/restoration pairs A11<->A10, A11<->A01,
A10<->W and A01<->W; assembly/disassembly P<->W; paid construction and repair
using explicit fuel stoichiometry; and W<->D or a separately declared absorbing
W->D boundary. A repair removes a specific impairment; it does not automatically
restore every role or set all gates to their favored positions.

When functional repair apparatus catalyzes repair, it must exist as a spectator
to the reaction. Do not let the unit being repaired supply an unavailable
capability to itself. Reverse-event multiplicities must count the corresponding
spectators consistently. Basal repair can remain slow but positive where declared;
zero basal repair is an explicit idealization, not a way to force protection.

For every reversible transition pair x<->y, use declared energies, degeneracies
and external work to audit the native ratio, at beta1:

    q(x,y)/q(y,x) = d(y)/d(x) * exp(W_xy - (E(y)-E(x))).

This applies per paired physical channel with W_yx=-W_xy. Either use verified
mass-action multiplicities or a symmetric nonnegative pair mobility giving this
ratio. Do not independently tune directional rates to get a desired verdict.
Same-state event labels do not add entropy to the count-state history grain.

Every action pays its declared material/fuel bill and competes for finite
throughput. Record gross and net role loss/restoration, construction, fuel, drive
work, heat and boundary transfers. Subtracting mean random costs is not allowed
as a correction; any deterministic-cost ablation is a different physical law.

## Damage modes

Expose named modules rather than one universal damage scalar:

1. Capability impairment: A11->A10 or A01, then degraded roles->W.
2. Material sequestration: W->D with explicit return kinetics.
3. Resource depletion: transfer charged fuel to its discharged state through a
   declared physical energy boundary; do not just edit a query's balance sheet.

For the first typed shock, each selected healthy unit loses exactly one capability,
with predeclared probabilities; a selected single-capability unit becomes W;
selected W becomes D. Multiple stages never occur to one unit in a single shock.
Independent/common-arrival laws match conditional expected losses separately for
each capability, material and energy, not merely a summed damage count. Preserve
the old shock module on the old adapter. This new shock law is a mechanism change.

Use an explicit external nonthermal boundary for one-way shocks. In a thermal
damage bath, reverse rates and temperature must be present. The driven world as a
whole need not be at equilibrium; each channel's accounting still must be correct.

## Access and restoration queries

Declare target predicates for capture availability, repair/control availability,
paid construction, local operation and joint operation. Recompute structural
reachability over all physically admissible actions and fixed-policy reachability
separately. Do not declare a target closed merely because current capacity is zero.

For each impairment, record first target hit, function at deadline, integrated
function, and relapse after restoration. Include consumed resources and heat.
Full restoration means returning to a declared set of physically equivalent
capability/resource states; restored function alone is a weaker predicate.
Restored future law does not refund elapsed time or foregone opportunities.

An actual damage/repair intervention is a native transition or declared external
channel with a bill. A counterfactual intact-versus-impaired root comparison is
allowed, but state whether resources and energy match. It is not a free physical
operation. Compare complete future breadth under the same law and frame; no
extra history variable is needed beyond the physically sufficient present.

The first slice measures energetic/resource cost along native recoveries. Minimum
restoration cost or optimal recovery probability requires a separate constrained
control problem; do not infer either from the winning breadth policy's average.

## Compute and compatibility

With six material categories and binary gates, the Cartesian local state bound is
`choose(M+5,5)*(M+1)*2`. Thus1+1 has576 states,2+1 has3024, and3+1 has10752.
Eight dense float64 work arrays at3+1 need about6.9GiB before other overhead; the
current1GiB process cap cannot support that exact implementation. At2+1 the same
array estimate is about558MiB before overhead, so full preflight remains necessary.

Implement1+1 exact engineering first. Treat2+1 as a separate explicitly named
scientific adapter if it passes profiling. Keep3+1 for sparse/sampled queries or
a later validated solver; no claim of exact entropy optimization from an ordinary
Monte Carlo trace entropy estimate. Do not silently replace the existing3+1 law.

Disabling capability typing must invoke the old state enumerator and recover its
Q/ledgers exactly. Do not add unused label dimensions and call them new physical
states. Exchangeability/lumping is allowed only with a generator-level check;
matching state counts or stationary probabilities is insufficient.

Acceptance fixtures: targeted impairment leaves the other capacity available;
repair without its needed catalyst is absent unless a basal route exists;
reversible-pair ratios and degeneracy balance; material/energy closure; partial
versus full restoration; expensive but positive recovery versus true closure;
typed shock moment matching; disabled legacy equality; and full-query resource cap.
