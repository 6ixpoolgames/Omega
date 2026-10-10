# Multiway carrier upgrade: implementation and integration result

6 October 2026. The reusable classical layer is implemented and exercised on
existing chemistry. Physics is unchanged; no extent candidate was selected.

The main advance is a clean separation between native law, cached residual
states, queried development occurrences, and downstream readouts. The carrier
supports cyclic/reconvergent systems, lazy expansion, sparse timed propagation,
explicit frontier mass, resumable JSON caches, native sampling/replay, independent
composition, and export to the exact joint-law reference.

## Integration results

One 2x2 patch of four particles, one fuel/waste unit, catalytic barrier 2 and
zero translation was used for generator comparison. The local reservoir has two
compartments with transport rate 1. Both state spaces were explored to closure.
These are existing finite chemistry regimes, not new gas/generativity experiments.

| Check | Shared fuel | Local fuel |
|---|---:|---:|
| Reachable residual states | 512 | 1,024 |
| Aggregated state-transition branches | 5,120 | 10,752 |
| Maximum difference from existing native generator | 1.78e-15 | 1.78e-15 |
| Probability-mass error at time 1 | 4.45e-16 | 2.23e-16 |
| Frontier mass with only 12 residuals expanded | 0.539253 | 0.821478 |
| Sample replay log-density error | 0 | 0 |

Each partial cache was serialized, reloaded, and expanded to closure. The large
frontier masses show why treating a small explored graph as the whole future
would be wrong. The upgraded representation retains that uncertainty explicitly.

Dropping local fuel allocation and retaining only total fuel fails the exact
Markov projection check: generator defect 7.370786. This agrees with the known
physical role of local availability. The frame is still readable from the native
law; its total fuel cannot replace the full present for propagation.

## Composition and unfolding controls

- Independent two-bit CTMC composition factorizes exactly. The explicit product
  adapter uses the same native clocks and preserves synchronous discrete bundles.
- In the CTMC analogue of the existing gate, both update orders exist with or
  without catalysis. With catalysis, one residual rate changes 0.0625 to 0.4375;
  the whole-law factorization defect is 0.375. A graph diamond is not independence.
- Shared-coin, contextual-enabling and exclusive-token controls fail independence
  for the corresponding joint-law/support reasons. Rule footprints are not used
  as the definition of independence.
- A rate-2 flipping process at horizon 0.75 has frontier probabilities 0.776870,
  0.191153, 0.018576 and 0.000170 at prefix depths 1, 3, 5 and 8. These agree with
  the exact Poisson tails; resolved plus frontier mass remains one.
- Reconvergent two-step developments retain two prefixes pointing to one residual.
  Rerooting there removes no needed state and adds no historical credit.
- Probability-one parallel, chain and fork-join devices retain their different
  native configuration sequences. No diversity or extent ranking is imposed.
- Duplicate row encodings aggregate, particle relabeling preserves native states,
  and optional catalytic-route resolution preserves the aggregate state generator.

The integration run takes about 2.3 seconds locally. All 48 focused tests pass,
covering the carrier/adapters/composition, the prior joint-law engine, and existing
lattice refinement; focused lint also passes. Raw caches
and results are ignored under `multiway_carrier_v0/`; source, specification and
this report are the publication-sized artifacts. No commit or push was requested.

## What this makes possible next

Extent candidates can now consume one common process rather than separate event,
endpoint and persistence approximations. Independent composition, coupled native
laws, finite-time behavior, and physical frame restrictions are available from
the same carrier. The next comparison should use explicit rival extent formulas
on independent composition and matched geometric rearrangements.

This is not yet a universal causal multiway implementation: automatic higher
concurrency structure, general physical realization comparison, quantum dynamics
and a lushness measure remain absent. It is an extensible present-rooted classical
foundation, with those missing claims separated from what the integration checks
actually establish.

Implementation: `omega_v2/finite/multiway.py`, `multiway_adapters.py`,
`multiway_composition.py`. Runnable integration:
`python -m omega_v2.validation.multiway_carrier_v0` from the repository root.
Full contract: [multiway_carrier_v0_spec.md](multiway_carrier_v0_spec.md).
