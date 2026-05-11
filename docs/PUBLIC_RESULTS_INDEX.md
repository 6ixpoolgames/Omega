# Public Results Index

This repository intentionally exposes only the most relevant current result
artifacts. Older exploratory outputs remain summarized in the manual/running log
but are not tracked as top-level result folders.

## Current Result Sets

### Probe 09: Robust Fiber Reachability

Directory:

- `probe_09_robust_fiber_reachability_results/`

Primary files:

- `summary.json`
- `viable_propagation_summary.csv`
- `baseline_comparisons.csv`
- `bootstrap_intervals.csv`
- `breadth_depth_decomposition.csv`

Reason retained:

- Probe 09 is where the current candidate object was isolated:
  `center_of_mass` multi-step viable propagation through certified fibers.

### Probe 10: COM Robustness, Extended Run

Directory:

- `probe_10_com_viable_propagation_robustness_extended_results/`

Primary files:

- `summary.json`
- `robustness_by_family.csv`
- `robustness_by_variant.csv`
- `propagation_deltas.csv`
- `bootstrap_intervals.csv`
- `perturbation_metadata.csv`

Reason retained:

- This is the broad robustness run with controls across perturbation families.

### Probe 10: Targeted Fragility Refinement

Directory:

- `probe_10_com_targeted_fragility_refinement_results/`

Primary files:

- `summary.json`
- `robustness_by_family.csv`
- `robustness_by_variant.csv`
- `propagation_deltas.csv`
- `bootstrap_intervals.csv`

Reason retained:

- This is the higher-coverage COM-only refinement for the weaker perturbation
  families: noise, potential shape, and time discretization.

### Probe 11: Learned Predictive Kappa

Directory:

- `probe_11_learned_predictive_kappa_revised_results/`

Primary files:

- `summary.json`
- `learned_kappa_validation_loss.csv`
- `learned_kappa_test_propagation.csv`
- `learned_vs_com_comparison.csv`
- `learned_vs_random_matched.csv`
- `learned_label_anatomy.csv`
- `bootstrap_intervals.csv`

Reason retained:

- Probe 11 is the first learned-quotient test. It asks whether a simple
  predictive k-means quotient can discover viable propagation without being
  handed COM bins as labels.

Result in one line:

- The learned quotients found partial propagation-positive structure, but did
  not recover COM as a strong coordinate and mostly underperformed or fragmented
  on heldout moderate perturbations.

## Current Public Interpretation

The current executable candidate is:

```text
COM-like multi-step viable propagation through certified fibers
in the F,T attractive multifield toy substrate
```

Probe 11 updates the interpretation:

```text
The COM object remains the stronger analytic coordinate. Simple learned
predictive quotients can see part of the signal, but are not yet a replacement
for COM.
```

The important public caveat:

```text
These are toy-substrate validation probes. They do not prove the broader Omega
theory. They provide a candidate object, controls, and failure modes.
```

## Why Older Results Are Hidden From The Main Tree

Older probes are valuable internally, but public readers do not need every
intermediate CSV/plot to understand the current state. They are summarized in:

- `docs/OMEGA_PROJECT_MANUAL.md`
- `docs/OMEGA_RUNNING_LOG.md`

If older artifacts need to be restored publicly, they can be regenerated from
the scripts or recovered from local storage/history.
