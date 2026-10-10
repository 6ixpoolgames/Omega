# Reusable present-rooted multiway carrier v0

Implemented 6 October 2026. This is an expandable classical carrier for the
existing physics, not an extent formula or a claim to complete physical ontology.

## Physical boundary and law

The primitive remains a sufficient present configuration and a reusable native
law. No preparation prior, past-cut average, or ancestry coordinate is added.
Queries develop that present forward. Rerooting at the same physical state under
the same law gives the same residual, regardless of its computational ancestry.

An adapter supplies:

- A discrete synchronous clock or time-homogeneous continuous-time jump clock.
- Owned immutable canonical states, stable keys, and a JSON state codec.
- Native outcome probabilities or event rates at every queried state.
- A versioned law identity, including physical configuration and implementation
  fingerprint where supplied by the concrete adapter.
- Optional physical channel refinement and native rule incidence. Neither is
  required to manufacture an additional state property or an independence claim.

Rates are not probabilities. A CTMC with outgoing rates a_e has next-event
density a_e exp(-sum_e a_e t). Finite horizons do not bound its jump-count support.
The framework assumes valid nonexplosive dynamics for a full infinite rollout;
finite-state adapters satisfy this with finite rates. General infinite adapters
must justify that assumption separately.

Only consistent bookkeeping canonicalization is permitted. The lattice adapter
removes particle numbering by sorting physical positions. It preserves geometry,
conformations, bonds, and the full resolved resource allocation. Physical copies
or isomorphic arrangements at different locations are not collapsed.

## Residual graph, occurrences, and probability

`MultiwaySystem` caches sufficient states and complete outgoing rows lazily.
Interning a state does not enumerate its future. An expansion validates the entire
row before inserting it; an insufficient cache budget leaves the row unexpanded.
Duplicate descriptions of a target/channel sum their weights. Incidence is united
conservatively and never used as another branching axis.

The residual graph can have cycles and reconvergence. A separately requested
`Unfolding` retains prefix occurrences, parent links and shared residual references.
Distinct prefixes can point to the same residual. These reference numbers are
computational addresses, not physical identities or extra extent.

There are two bounded views:

1. **Residual exploration.** Unexpanded states form an explicit frontier.
   Sparse propagation stops at first entry to that frontier. Frontier mass is
   unresolved continuation, not a prediction that the system remains there.
   It bounds the contribution of paths that could subsequently return to known
   states. Enlarging the explored domain refines this bound.
2. **Occurrence unfolding.** Interior nodes receive the probability of exactly
   that prefix through the horizon; frontier leaves receive the probability that
   their prefix has been completed, including all subsequent continuation. These
   disjoint cases sum to one. No arbitrary depth-based renormalization occurs.

`embedded_weight` is a jump-chain prefix weight for CTMCs, not a physical-horizon
weight. Timed cylinder probabilities are obtained by the finite prefix generator.
Sampling uses native discrete updates or SSA waits and returns a replayable path
and log probability/density. Exceeding its event cap raises instead of returning
a biased collection of unusually short successful samples.

Exploration and replay references are checked against both law identity and state
indexing. A JSON checkpoint contains native states, known rows and unknown rows;
restoration checks native law identity and recomputes cached rows. It is a cache
of the adapter, not a replacement for its unexpanded physics. No pickle execution
or arbitrary source reconstruction is involved.

## Composition and causal claims

`ProductAdapter` provides explicit independent composition. CTMC generators add
on separate factors; discrete kernels multiply as simultaneous outcome bundles.
It never serializes an existing parallel tick or assigns independent race orders
an additional probability beyond the native law. Interconnecting shared resources
requires a joint physical adapter; it is not an independent product.

`audit_factorization` checks a complete finite law on a partition of all native
coordinates. It verifies Cartesian state support and the full K-product or
Q-Kronecker-sum identity, including context-dependent marginal rates. The result
certifies the resolved state process to numerical tolerance, not an omitted bath
or unexamined microscopic channel law. No coordinates may be silently dropped.

`audit_square` reports a concrete two-update witness and its before/after rates.
It does not assign a concurrency cell. A diamond can survive while an update
changes another update's hazard. Higher-order independence requires the full
factorization check or a future stronger physical composition certificate.

`audit_projection` checks strong lumpability before exporting a smaller Markov
law. If it fails, the frame remains a legitimate observation of the full process;
its omitted physical context must remain in propagation. Failure is not a reason
to append fictitious ancestry or delete the frame.

## Existing adapters and readouts

- `TableAdapter`: existing finite native K/Q and logical calibration devices.
  It ignores their preparation mixture and optional semantic event metadata.
- `LatticeAdapter`: current shared-pool and compartment chemistry. Same physical
  states and rates; no new mechanics, bath model, or reaction assumptions.
- `ProductAdapter`: independent compositions of any adapters with a common clock.
- `joint_law`: closed native tuple-state graphs export to the existing exact
  joint-continuation engine. Observation regions/times are downstream queries.

The default lattice path resolution aggregates native pathways with the same
physical state update. `resolve_routes=True` also retains the physical locations
of participating catalytic templates, preserving the model's extra assisted
routes. Summing over that optional refinement gives the same state generator.
The option does not claim that reaction names or unresolved bath microhistories
are physical distinctions. Native read/write declarations use source-canonical
coordinates, and are not automatically a transported causal provenance graph.

The old `HistoryAtlas` remains available for its established marked reaction
logs and last-writer diagnostics. New general continuation work should use this
carrier; the integration run compares it directly with the existing chemistry
generator. No old evidence or model is rewritten.

## Minimal usage

```python
from omega_v2.finite.multiway import MultiwaySystem
from omega_v2.finite.multiway_adapters import LatticeAdapter

system = MultiwaySystem(LatticeAdapter(model))
root = system.intern(native_present)
view = system.explore(root, max_states=3000, max_expanded=100)
cut = system.at(view, horizon=1.0)
print(cut.mass, cut.frontier_mass)

# More exploration reuses the same sufficient-state cache.
larger = system.explore(root, max_states=10000, max_expanded=10000)
cache = system.snapshot((root,))  # JSON-compatible; store outside tracked outputs.
restored = MultiwaySystem.restore(system.adapter, cache)
path = restored.sample(root, 5.0, seed=21)
restored.replay(path)
```

## Extension boundaries

The generic adapter and separated readouts allow different state dimensions,
local geometries, resource rules, reaction intermediates and explicit physical
environment variables. A new physical model must supply its own canonical state
and law contract. Existing lattice adapters deliberately reject unknown subclasses
rather than silently claim their state codec is sufficient.

This release does not construct a universal event structure, arbitrary higher
concurrency cells, a minimal causal graph, or a trace quotient from an unlabelled
transition graph. Rule incidence is preserved where available, while the finite
composition checks make narrower claims. An interleaving tree alone is not the
full compositional object.

Sparse state propagation scales beyond the prior dense-only interface; explicit
prefix trees and dense joint tables still grow rapidly. Expansion limits bound
committed cached states and occurrences, not every temporary allocation inside
an adapter's row enumeration. An already larger cache is not shrunk by a smaller
later limit. Disk eviction, distributed expansion and automatic tensor-network
contraction are not implemented.

Quantum interference, non-Markovian reduced dynamics, general non-exponential
event clocks and continuous fields require appropriate new dynamics interfaces.
They must not be smuggled in as ordinary scalar probabilities in this interface.

Extent remains open. The carrier retains enough structure to compare candidate
composition rules and geometric measures without rebuilding the native process.
Residual count, occurrence count, activity, and frontier mass are operational
diagnostics; none is assigned the name lushness here.
