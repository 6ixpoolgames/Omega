# Reproduce engineering smoke

From the original Omega checkout on Windows, using its existing NumPy/SciPy/pytest
environment:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_growing_population.py -q
.\.venv\Scripts\python.exe scripts/run_growing_smoke.py
```

The parent installs the120s/1GiB/256MiB caps before releasing the worker. It hashes
and snapshots model, reference, readout, tests and protocol first. Every attempt
gets a distinct ignored local directory with profile, status and artifact hashes.
No optimizer runs and no automatic cleanup or publication occurs.

The final compact engineering report can be recreated using its completed run:

```powershell
.\.venv\Scripts\python.exe scripts/report_growing_smoke.py results/local_runs/lushness_testbed/growing-smoke-20261013T061035Z-f73909 --output docs/research_notes/lushness_testbed/growing_population
```

The old autonomous prototype remains intact. Its histogram/sparse construction
inspired this implementation; its old transition law, assigned reward and output
dependencies were not imported. The current model's one-unit case regresses to
the already BioNetGen-audited control fixture. New population reactions have an
independent body-coordinate reference and thermodynamic audit; a new upstream
BioNetGen population export has not been generated in this smoke.
