# Publication provenance: 15 October 2026

The temporal, exploration, paid-sensing and renewal scientific snapshots were
audited against the publication index. Model, solver, worker, source registration
and specification bytes are retained. Six paths needed explicit Git attributes
to preserve their original line endings; these changes have no behavioral effect.

The source inventory also captured an unused older test at
`omega_v2/testbed/tests/test_growing_population.py`. Its two-token witness relied
on a default which had since become one token. The current test now explicitly
sets `ReferenceParams(switch_tokens=2)`. Its original frozen bytes are retained
verbatim in [FROZEN_growing_population_test.txt](FROZEN_growing_population_test.txt).
To reconstruct the old source inventory exactly, copy that file to the logical
test path in a separate reproduction checkout. That test was not an imported
scientific dependency; no generator, solver, worker or physical parameter changed.

Report generators and interpretation summaries were revised after science.
The resulting predictions and numerical scores remain unchanged. Compact
results, protocols and source are published; raw run bundles remain local.
