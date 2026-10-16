# Reproduce controlled growth comparison

Run from the original Omega checkout with its existing Windows `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_growing_population.py tests/test_growing_comparison.py -q
.\.venv\Scripts\python.exe scripts/run_growing_comparison.py profile
.\.venv\Scripts\python.exe scripts/run_growing_comparison.py full
.\.venv\Scripts\python.exe scripts/run_growing_comparison.py no_assistance
.\.venv\Scripts\python.exe scripts/run_growing_comparison.py no_capture_benefit
.\.venv\Scripts\python.exe scripts/run_growing_comparison.py neither
```

The timing profile does not inspect entropy or rank policies. Each scientific arm
enumerates all36 shared local tables, and retains all preparation signs. Resource
caps are120s/1GiB process-tree/256MiB outputs per worker, one numerical thread.
All inputs and executable sources are hashed and snapshotted before the worker
starts. Raw tables remain under ignored results/local_runs/lushness_testbed/.

Recreate the compact registered-outcome report from the completed runs:

```powershell
.\.venv\Scripts\python.exe scripts/report_growing_comparison.py results/local_runs/lushness_testbed/growing-full-20261013T064138Z-f91bb6 results/local_runs/lushness_testbed/growing-no_assistance-20261013T064207Z-94ff18 results/local_runs/lushness_testbed/growing-no_capture_benefit-20261013T064400Z-3b88ab results/local_runs/lushness_testbed/growing-neither-20261013T064400Z-983b84 --output docs/research_notes/lushness_testbed/growing_population/comparison_report
```

Use new run directories after reproduction. The reporting step automatically
scores G1–G7, preserves unfavorable effects, calculates fixed-table mechanism
contrasts and separates same-law preparation offsets from different-law rates.
Candidate-only cost/cadence comparisons do not certify full-grid optima there.
Rule A is parked and is not called by this scientific comparison.

No cache deletion, Git operation or publication occurs in these commands.
