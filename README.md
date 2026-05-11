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
- [Progenitor drafts](docs/progenitor_drafts/README.md)

## Current Result Sets

The public tree keeps only the current/relevant compact results:

- `probe_09_robust_fiber_reachability_results/`
- `probe_10_com_viable_propagation_robustness_extended_results/`
- `probe_10_com_targeted_fragility_refinement_results/`
- `probe_11_learned_predictive_kappa_revised_results/`
- `probe_12_batch_results/`
- `probe_12a_com_formal_object_audit_results/`
- `probe_12b_learned_kappa_failure_diagnosis_results/`
- `probe_12c_improved_learner_smoke_results/`

Older exploratory outputs are summarized in the docs but not exposed as result
folders in the current public tree.

The `docs/progenitor_drafts/` folder contains early theory-side draft papers.
They are included for provenance only and should not be read as current
validation results.

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

For GPU/CuPy work on the original machine, use `omega_env.bat` or run
`omega_env.ps1` with a PowerShell execution-policy bypass. The environment
scripts add Torch's bundled CUDA 13 NVRTC DLL directory to `PATH` and point
CuPy's kernel cache at `.cupy-cache/`.

## Main Scripts

- `probe_09_robust_fiber_reachability.py`
- `probe_10_com_viable_propagation_robustness.py`
- `probe_11_learned_predictive_kappa_revised.py`
- `probe_12_batch_com_audit_learned_diagnosis.py`

Historical scripts remain in the repository because they document how the
current object was reached, but new work should normally start from Probe 09/10
or from the next formalization probe described in the manual.

## Current Next Step

Current latest probe:

```text
Probe 12: COM Formalization + Learned-Kappa Diagnosis
```

Probe 12 found that COM remains a positive fiber-transport witness, while simple
learned k-means mostly fails by splitting/merging COM fibers and inflating
small-fiber structure. The recommended next step is formal COM fiber transport,
not scaling learned-kappa yet.
