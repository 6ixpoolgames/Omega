# Omega Validation

This repository contains the executable validation workspace for the Omega
theory project.

The current goal is modest and scientific:

> extract candidate mathematical objects, test them against controls, and record
> what survives.

The strongest current toy-substrate candidate is:

```text
COM-like multi-step viable propagation through certified fibers
```

In plain terms: coupled futures are interesting here not because they are
maximally entropic, but because viable structure can be propagated through
certified macro-fibers while preserving component information.

## Start Here

- [Project manual](docs/OMEGA_PROJECT_MANUAL.md)
- [Running log](docs/OMEGA_RUNNING_LOG.md)
- [Public results index](docs/PUBLIC_RESULTS_INDEX.md)

## Current Result Sets

The public tree keeps only the current/relevant compact results:

- `probe_09_robust_fiber_reachability_results/`
- `probe_10_com_viable_propagation_robustness_extended_results/`
- `probe_10_com_targeted_fragility_refinement_results/`
- `probe_11_learned_predictive_kappa_revised_results/`

Older exploratory outputs are summarized in the docs but not exposed as result
folders in the current public tree.

## Important Caveat

This repository does not prove Omega as a scientific theory. The current results
come from a local toy multifield substrate. They are evidence for a candidate
formal object and for a workflow that can reject weaker alternatives.

## Environment

Use the local virtual environment directly when working on the original machine:

```powershell
.\.venv\Scripts\python.exe -c "import numpy, pandas, matplotlib; print('ready')"
```

For CPU-heavy probes, the calibrated default is:

```text
18 worker processes
```

## Main Scripts

- `probe_09_robust_fiber_reachability.py`
- `probe_10_com_viable_propagation_robustness.py`
- `probe_11_learned_predictive_kappa_revised.py`

Historical scripts remain in the repository because they document how the
current object was reached, but new work should normally start from Probe 09/10
or from the next formalization probe described in the manual.

## Current Next Step

Current latest probe:

```text
Probe 11: Learned Predictive Kappa
```

Probe 11 found partial learned propagation candidates, but did not recover COM
as a strong learned coordinate. The next step should formalize the COM fiber
transport object and tighten the learned quotient target before broadening the
substrate.
