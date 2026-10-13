# Paid growing population: engineering substrate

Implementation and capped smoke authorized 2026-10-13. This is a new adapter
combining the earlier prototype's histogram/sparse design with the current
testbed's reaction, controller and thermodynamic contract. Old discrete laws,
assigned behavior rewards and output dependencies are not imported.

## Present, material and energy

Each of two compartments has fixed inventory M_c of body precursors and K_c=M_c
persistent charge carriers. Present state is ((w,a,f,g),(w,a,f,g)): worn and
active body counts, local charged carriers, and gate service0/export1. Free
precursors are p=M-w-a; uncharged carriers K-f. Both pools are conserved.
Exchange moves charge between the local carrier pools, not new material.

E=sum(w+2a+2f) in kBT with beta1. Degeneracy is the product of
M!/(p!w!a!) times binomial(K,f). At chemical potential0 the stationary thermal
weight is that degeneracy times exp(-E). No reservoir energy or body appears
through a software reset. Uphill thermal reconstruction is retained and draws
energy from the bath; functional reconstruction is not identity continuation.

Changing M adds physical precursor/carrier inventory. Within any eventual
comparison, all preparations must have the same M, energy and external drive.
The finite inventory permits population expansion by converting precursors,
followed by saturation. It does not establish unbounded open-endedness.

## Native operations

Temperature and chemical potential4 are shared with the existing control model.
Every operation has a reversible counterpart. Rate ratios include the declared
population degeneracy, rather than applying unit-state formulas to count states.

| Family | Effect and resource account |
|---|---|
| Drive capture | Local charge changes; chemical work +/-4 per charge; active count lowers both capture barriers |
| Thermal carrier exchange | Charge changes with the zero-potential bath; no work |
| Basal construction | P+charged <-> A+empty at service gate; one charge per forward construction |
| Assisted construction | Retained active parent + P+charged <-> retained parent + A+empty; distinct parent and recipient |
| Repair | W+charged <-> A+empty at service gate; one charge, heat from energy difference |
| Wear/restoration | A <-> W with reversible bath exchange |
| Disassembly/restoration | W <-> P, body material retained |
| Control switching | Gate changes, consuming integer k charge tokens forward and retaining the fuel-restoring thermal reverse |
| Between-compartment exchange | Reciprocal charge transfer through an open gate; no material/energy creation |

Capture attempt coefficient per carrier is .04[1+(6-1)a/M]. Assisted construction
uses forward rate .4*p*a*f/(M*K), reverse .4*a*(a-1)*(K-f)/(M*K). The factor a-1
ensures the reverse catalyst is distinct from the dismantled recipient.
Population contact normalizations are declared well-mixed assumptions. Neither
the parent nor the offspring gets an extra score term.

The physical enabling chain is capture -> charged store -> paid construction
-> new active unit -> additional capture and assisted construction. The new
unit obeys exactly the same assistance law as the original seed. A microscopic
coordinate witness checks that a constructed recipient can assist a subsequent
recipient; ancestry labels never become dynamical state or reward evidence.

## Local controllers and costs

Two installed hardwired controllers remain fixed, one per compartment. They
observe only whether their own active count is positive, and expose the four
existing service/export response entries. The smoke uses one declared adaptive
setting; it is not claimed optimal in this growing world. Future controllers can
use richer count observations under a new information/cost specification.

The sensing/table idealization remains passive catalytic coupling. These are
growing functional apparatus populations, not autonomous new valuers or inherited
controllers. Controllers persist after apparatus disassembly. Lineage and personal
identity remain deferred.

Switching consumes k local carriers, default1; the bill2 implementation is also
checked. A compartment with fewer than k carriers cannot execute that pathway.
That is a physical capacity constraint, not a reason to truncate generator rows.
Forward rates use binomial(f,k)/binomial(K,k)*exp(k); reverse rates use the matching
uncharged-carrier factor*exp(-k). Bills change a native actuator reaction, not an
entropy penalty. Idle closes actuator channels and incurs ordinary time, wear
and opportunity cost. Thermal and controller randomness remain admitted.

## Compression, reference and measurement

Population histograms are the declared physical grain of this well-mixed adapter.
An independently constructed body-slot reference verifies exact Markov projection
onto those histograms. This proves count dynamics and count-history readouts, not
equality with fully resolved slot-history entropy. If physical sites become
resolved, their extra alternatives require a separate fine readout; no automatic
log multiplicity bonus is added to the current primary objective.

Use sparse CSR generators and finite-time matrix actions for probability and flux
surveys. Dense transition matrices are permitted only for <=1000 states in the
smoke. Larger count-history entropy and Rule A evaluation are explicitly unsupported
by that dense path, not silently replaced by event-count entropy. Sparse generator
storage alone does not make sampled transition matrices sparse.

A matched preparation prior can be constructed over the exact energy shell with
gates initially service, weighted by declared degeneracy. Its entropy is never
added to known-root future breadth. This smoke constructs that prior but does not
rank prepared/disordered worlds or call it a molecular gas baseline.

## Extension interfaces and gates

The adapter exposes Params, state enumeration, native events with ledger fields,
and build() returning states/index/CSR Q/rate ledgers. The sampler, future controller
solver and survey can share that law. The old prototype remains intact. Larger
population, spatial topology, heterogeneous devices, memory and cross-scale
composition require explicit additions, not current findings.

No scientific sweep, manuscript revision, Git commit, push or Drive publication
is part of the authorized smoke. The protocol separates law/ledger/compression
checks from later optimization and evidence about generativity or ethical behavior.
