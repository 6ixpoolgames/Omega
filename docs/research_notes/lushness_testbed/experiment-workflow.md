# Reusable experiment workflow r1

Status: specification, 2026-10-13. No runner, cleanup service or report generator
is claimed implemented here. Existing scripts may be reused only after audit.
No automatic commit/push/publication. User instruction is required for those
actions. Raw results stay under ignored results/local_runs/lushness_testbed/. Source snapshots remain unchanged.

## 1. Single pipeline and contracts

    validate -> compile -> audit -> profile -> freeze -> search -> evaluate
             -> analyze -> report -> retain/prune

World, controller/execution, measurement, structural survey, solver and experiment
are separately versioned modules. Exact and sampled modes use one canonical law;
an independent upstream-engine check guards shared implementation errors.

Proposed interfaces:

- World: enumerate feasible native transitions/propensities, apply updates,
  canonicalize representations, return resource exchanges and physical supports.
- Execution: observation, controller memory and physically implemented gate actions.
- Measurement: declared grain/clock, conditional likelihood/entropy and error bounds.
- Survey: streaming structural/resource statistics and optional event witnesses.
- Solver: search/evaluate controllers with scope, certificates and stopping reason.
- Experiment: manifests, caps, registry, artifacts, comparisons and retention.

Do not require a fully enumerated state space from every future backend. Do require
each backend to declare supported law, measurement and survey operations. Reject
unsupported combinations rather than silently approximate them.

## 2. Identity, preregistration and provenance

Every execution has an immutable run ID and a semantic input hash. The hash covers
canonical configuration, source contents including uncommitted changes, upstream
model/engine versions, dependency lock, measurement version, initial conditions,
controller class, solver settings, seed algorithm/seeds and relevant numerical
backend settings. A Git commit alone is insufficient. Store an executable source
bundle plus hashes; a hash cannot reconstruct a deleted file.

Separate compile-cache key (law/compiler/physical boundaries) from query key
(root, controller, objective, horizons, solver) to share compatible operators.
The same law with a different root should not require duplicate network storage.
Backend or controller changes that change transitions invalidate the operator key.

Machine-readable preregistration includes predictions, comparator IDs, metric IDs,
directions, thresholds/tolerances, horizons, primary/secondary status, tests and
failure/hit criteria. Freeze canonical bytes and hash before scientific execution.
An amendment creates a new version with reason and time; exploratory follow-ups
are labeled. Scoring uses structured operators, never eval of arbitrary strings.

Hashes document the local record; they are not external timestamp attestation or
a proof that post hoc choices are impossible. Formula changes cannot reuse a
frozen result ID. Unimplemented questions are explicitly deferred, not reported
as predictions that passed.

## 3. Proposed artifact layout

    docs/research_notes/lushness_testbed/                  specifications and frozen compact protocols
    results/local_runs/lushness_testbed/registry.sqlite              execution/artifact index (local)
    results/local_runs/lushness_testbed/<run_id>/manifest.json        immutable inputs/provenance
    results/local_runs/lushness_testbed/<run_id>/status.json          progress, caps and terminal status
    results/local_runs/lushness_testbed/<run_id>/summary.json         compact numbers, uncertainty and audits
    results/local_runs/lushness_testbed/<run_id>/policy.json          controller sufficient for reevaluation
    results/local_runs/lushness_testbed/<run_id>/report.html          generated human-readable interpretation
    results/local_runs/lushness_testbed/<run_id>/witnesses/           bounded counterexample and execution traces
    results/local_runs/lushness_testbed/cache/<content_hash>/        rebuildable operators, arrays, checkpoints
    docs/research_notes/lushness_testbed/evidence/         deliberately retained compact evidence

Local registry/outputs are not Git source. Promotion to retained evidence and
publication are explicit actions. Every failed/adverse/completed run stays indexed.

## 4. Encoding and performance

Use packed fixed-width integer states, integer species/rule IDs with dictionaries,
sparse graph edges and typed contiguous arrays. Verify bounds before narrowing
integer widths. Small arrays: NPZ/NPY with no pickled object payloads. Large chunked
arrays: optional Zarr after measured need. Compact tables: CSV/JSON initially;
Parquet when table size or analysis justifies its dependency. SQLite provides the
searchable local index. No universal JSON event dump.

Compressed NPZ is appropriate for snapshots, not memory-mapped random access;
use NPY or chunking when the access pattern needs it. Do not store dense N-by-N
operators by default. Estimating P_delta or its row entropies can densify despite
sparse Q: profile this explicitly and impose a separate operator memory gate.

Compute planned ledgers/fluxes/recovery statistics online. Retain bounded random
trace samples and all selected failure witnesses; selection metadata prevents
mistaking illustrative traces for an unbiased sample. New unplanned readouts may
require rerunning after raw trace eviction. No promise of arbitrary post hoc
analysis from summary statistics alone.

Lossless lumping requires proof/checks for the law AND readout. Heterogeneous
controllers, locations, memories or physical event resolution may invalidate it.
Seeded streams are keyed by run/replicate, not process scheduling. Common random
numbers across arms require an explicit coupling design, not just matching seeds.

## 5. Resource gates

Default initial engineering worker: 120 seconds wall time, 1 GiB process memory,
one worker, one numerical thread, 256 MiB output cap. Draft research batch:
30 minutes per worker, at most two workers, same memory cap until profiling
justifies change. These are computation budgets, not altered physical dynamics.

Parent watchdog enforces wall/memory/output caps including child engine processes;
OS process-tree/job limits where supported. Atomic summary/checkpoint writes and
an interruption status survive failure. Resource-exhausted runs cannot be reused
as successful cache hits. Do not rerun automatically forever.

Engineering profile reports state/reaction counts, operator density, compile time,
propagation throughput, peak memory, artifact sizes and estimated next-case cost.
Approval/readiness for expanded runs uses actual profiles, not the assumption
that all future runs will stay fast.

## 6. Automated analysis

All reports use one versioned results schema, with:

- model/root/controller/readout identity and supported claim scope;
- conservation, bounds, probability, generator and observation audits;
- exact-versus-sampled comparisons and independent-engine check;
- breadth versus horizon, valid rate/offset comparisons and numerical residuals;
- same-law preparation controls separately from changed-law mechanism ablations;
- material, energy/free-energy, capture, dissipation and maintenance accounts;
- access/enabling witnesses, dependency/bottleneck and recovery/retention profiles;
- policy tables, representative executions and differences from reference policies;
- temporal/grain sensitivity and every ranking flip;
- registered prediction verdicts, deviations, missing data and failed runs;
- runtime/memory/storage and rebuild status.

Store units, estimator, sample size, uncertainty, numerical tolerance and missing
reason for each result. Distinguish Monte Carlo error, solver error and model
uncertainty. Search and held-out evaluation use separate seeds. Best-found local
search is not certified optimal; analytic full-information comparisons name
feasible-set assumptions. Graphs are generated from the compact result tables.

Automated reports flag competing interpretations, but do not automatically label
a policy ethical. Before interpreting adverse behavior, inspect numerical validity,
represented consequences and the proxy hypothesis without assuming which failed.

## 7. Retention and cleanup

Three classes:

1. Permanent small evidence: source/config/dependency bundles, frozen protocols,
   manifests, compact results, policies, audit failures, essential witnesses,
   upstream provenance and deletion/rebuild records.
2. Evictable cache: validated rebuildable operators, bulk distributions, redundant
   checkpoints and raw traces not pinned as evidence.
3. Scratch: temporary incomplete computation files, removed after terminal status.

Proposed local disposable-cache budget: 5 GiB. After completed batches, prune
least-recently-used eligible entries toward 4 GiB when over budget; optionally
expire unpinned disposable entries after 14 days. Initially cleanup runs in dry-run
mode. Enable actual pruning only after the deletion and reconstruction tests pass.
No standalone scheduled task is created by this specification.

Never auto-delete an active/locked run, pinned artifact, or artifact directly
cited as evidence by a filed protocol/report/result. A model reference to a
rebuild recipe is not permission to delete a cited raw artifact. Promotion creates
the reference/pin before eviction is allowed; check the dependency graph.
If protected evidence alone exceeds the budget, report and stop growth rather
than deleting it. Negative outcomes are not preferentially pruned.

Only manifest-listed files with validated resolved absolute paths under results/local_runs/lushness_testbed/cache
or an explicit scratch directory are eligible. Reject traversal, links/junctions
escaping the root and external paths. Never recurse through an unverified path.
Use a single native filesystem operation family, log bytes and artifact IDs, and
commit the deletion record independently of the deleted data. Do not touch old
historical output folders under this policy without a separate migration inventory.

Rebuild audit: first regenerate a disposable cache entry into a new directory,
compare, then test eviction/reconstruction on a tiny fixture. Later audit a small
eligible sample every ten completed batches. Byte hashes apply to canonical
deterministic artifacts; floating results use frozen tolerances where platforms
differ, and stochastic results use pinned RNG/environment or statistical checks.
Do not demand identical compressed-file bytes when archive metadata differs.
Failed rebuild pins evidence and disables automatic eviction pending diagnosis.

## 8. Expansion obligations

Keep structural components/interfaces so later assemblies can compose across
scales. Add dynamic topology, population growth, inherited controllers, spatial
transport and richer thermodynamics through versioned adapters. Fixed local
compartments and coarse population are initial assumptions, not ontology.

Quantum backends would require a coherent process/readout contract; the classical
transition interface cannot represent interference. Nothing here settles quantum
extent, individual identity or phenomenal value.
