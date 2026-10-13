# Lushness optimizer test bed

Active design location as of 2026-10-13: the original Omega repository, branch
`codex/operational-continuation-comparison`. Work on a separate repository is
deferred. Drafts initially prepared in the sibling omega-cosmology folder are
historical copies; subsequent revisions belong here.

## Design packet

- [Initial substrate specification](INITIAL_SPEC_r1.md)
- [Measurement contract](MEASUREMENT_r1.md)
- [Reusable experiment workflow](experiment-workflow.md)
- [Machine-readable protocol draft](PROTOCOL_DRAFT_r1.json)
- [Foundation contract](testbed-foundation-contract.md)
- [Opus issue assessment](OPUS_ISSUE_ASSESSMENT_r1.md)

The main substrate and workflow remain design drafts. The first binding
calibration is implemented and passed: [results](calibration/RESULTS_r1.md),
[frozen engineering protocol](calibration/PROTOCOL.json), and
[reproduction](calibration/REPRODUCE.md). BioNetGen 0.8.7 / engine 2.9.3 was
verified locally against hand-derived population-state generators and sampling.
This is not yet the three-arm assembly comparison or a controller experiment.

Implemented workflow pieces: capped process-tree execution, frozen manifests,
source snapshots, compact machine/human reports and final artifact verification.
General caching, eviction, schemas/indexing and optimizer integration remain open.

Generated outputs will live under the already ignored
`results/local_runs/lushness_testbed/`. Source, specifications and compact retained
evidence stay separate. Nothing is committed or pushed without user instruction.
