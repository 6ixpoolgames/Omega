# Channel extension: implemented architecture and physical scope

Implemented 13 October 2026 in the original Omega active branch. The governing
handoff is [CHANNEL_EXTENSION_SPEC_r1.md](../CHANNEL_EXTENSION_SPEC_r1.md).
The extension is engineering-validated; its scientific protocol remains a draft.

## Native modules

`contracts.py` defines versioned world, rule, event, controller, measurement and
experiment contracts. `compiler.py` validates their dependencies/support and
aggregates native rates into sparse Q, retaining event-resource exchanges in
separate ledgers. Physical channel labels never add entropy. An event sampler
uses the same registered events as the compiler. State validation/indexing are
currently finite, tuple-based; new backends can implement separate enumeration
and likelihood capabilities without altering the physical rule contract.

`modules/growth.py` is a new adapter; the old `growing_population.py` entry points
and old reports are preserved. All original dynamics and every original flow
agree when damage is disabled, including two-token actuator variants. The new
state is `(w,a,d,f,g)` per compartment, with `p=M-w-a-d` and fixed carrier capacity
M. Existing actors still observe only their own active presence. Controller
hardware is an explicitly surviving boundary idealization, not growing agency.

`modules/material_sink.py` declares damage parameters and physical state helpers.
`modules/damage.py` supplies forward transfers to D and optional thermal returns.
The reversible law has forward rate `lambda*c_v*n_v` and reverse rate
`lambda*c_v*n_D*exp(eD-e_v)` at beta=1. It satisfies the declared coarse
degeneracy-weighted equilibrium law when chemical drive is zero. Numerical
underflow of a nonzero return is an error, not an absorbing approximation.

Absorbing mode omits returns and declares an inaccessible-product boundary. It is
an idealized kinetic model, not closed finite-temperature equilibrium physics.
Both modes conserve counted material and retain carrier/bath/controller dynamics.
The compiler derives work/heat and net observable changes centrally. Gross sink
losses/returns supplement the previous birth/loss ledgers.

Uniform exposure `(1,1,1)` gives a policy-independent material pure-death control.
Worn-only exposure `(0,1,0)` is a stipulated susceptibility mechanism through
which repair can affect loss. It does not establish that organization universally
protects matter. Engineering parameters `lambda=.04,eD=-6` test implementation;
they are not an optimized or preregistered ethical regime.

## Independent checks and analysis

The damage generator is checked against an independent labeled-slot construction;
the unchanged growth law has its earlier independent reference. This is not a new
BioNetGen export of the combined damage adapter. Generator and full original flow
regression, equilibrium flux, and energy closure are checked separately.

`analysis/finite_classes.py` computes positive-rate reachability, closed recurrent
classes, their stationary laws, transient absorption weights, root-relative rates
and normalized offsets. Poisson solves use recurrent/transient blocks, with no
large full limiting projection. Tiny positive rates remain edges. Dense sampled
transition entropy is memory-gated; sparse surveys do not certify large entropy.

`analysis/channel_access.py` reports structural and fixed-policy closure with
separate quantifiers, closure certificates, shortest access witnesses, first
passage, deadline recovery, endpoint occupation and integrated occupation.
The experiment includes any-active, compartment-active and paid-construction
targets. Its all-action graph is an upper envelope of implemented actuator routes,
not an unrestricted controller optimality theorem.

`analysis/event_sequences.py` propagates query-side ordered-event automata without
including their flags in physical entropy. Two assisted events can include
intervening events and turnover. That survey is not lineage-resolved compounding
or proof that the second event used a particular newly built parent.

`analysis/registry.py` provides capability-checked readout registration, structured
numerical predicate scoring and descriptive interpretation records. Missing
capabilities remain unsupported. Greater closure risk and greater breadth remain
a reported tension. Reduced functioning by itself is a margin trade-off.
Rule A and extra protection/viability rewards remain absent.

## Workflow

`workflow/manifest.py` freezes explicit source bundles and rejects overwriting an
existing manifest. Workers execute the copied source, verify it before/after
execution, and report imported local paths. The process cap helper itself is
loaded from that bundle. Runtime dependencies are version-recorded, not vendored.

Operator, query and report identities accept source-role groups so a readout-only
edit need not invalidate the physical operator. Scientific runs validate frozen
roots, controller subsets, physical parameters and registered numerical predicates.
The runner records a local SQLite run/artifact index, hashes artifacts and emits
atomic status/results. Cache lookup rejects incomplete runs or damaged artifacts.

Cache storage/eviction infrastructure currently supplies identities, indexing,
integrity checks, reconstruction comparison and safe dry-run eligibility. It does
not automatically reuse a compiled operator or delete files. Those rollout steps
remain explicit. New readouts may require recomputation from source and config.
No historical data migration, scheduled cleanup, commit or publication is implied.

`run_channel_comparison.py` supports engineering smoke/profile and separately
frozen scientific execution. A draft protocol is rejected. Scientific mode can
search all shared tables or an explicitly declared subset, score frozen predicates,
retain class identities and report native breadth with structural surveys. Its
small synthetic integration tests are software checks, not research evidence.

## Readiness boundary

The 1+1 smoke covers 256 states. The 3+1 timing pilot covers 2,560 states; its
measured matrix exponential costs approximately 4.36 seconds on this machine.
Thirty-six exponentials alone estimate 157 seconds, before class solves, fluxes,
sequence queries, matching and reporting. The old 120-second scientific-arm cap
cannot support that planned complete grid. Freeze a new budget after a complete
single-policy preflight, or explicitly choose a smaller certified controller class.
Do not silently reduce inventory, cadence or physics to fit a cap.

The pilot measured compile, sparse accounting and dense transition construction;
it did not certify a complete 2,560-state rate/offset search. The 25,600-state
3+3 extended world remains outside this dense entropy backend. Larger symbolic,
on-demand state and sampled-likelihood backends remain future additions.

The objective remains native full declared count-history breadth. Frame matching
and mean conditional preparation comparisons follow the existing contract. No
survival conditioning, removal of thermal paths or automatic ethical verdict is
introduced by the new loss/recovery surveys.
