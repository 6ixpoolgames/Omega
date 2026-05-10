# Omega Validation Workspace

Local simulation and analysis harnesses for the Omega theory validation project.
The current workflow is deliberately narrow: extract candidate mathematical
objects, test them against shuffled/product/independent baselines, and classify
signals without treating raw entropy as the success criterion.

## Environment

Use the local virtual environment directly:

```powershell
.\.venv\Scripts\python.exe -c "import numpy, pandas, matplotlib; print('ready')"
```

The project has been calibrated on local consumer hardware with a Ryzen 5900X
and RTX 4070 Ti. Current CPU-heavy probes use 18 worker processes by default.

## Current Probe Line

- Probe 08a: multifield profile reconciliation.
- Probe 08b: transport-dominant multifield validation.
- Probe 09: robust fiber reachability with viable propagation as the primary
  readout and breadth/entropy as secondary diagnostics.

Large raw graph dumps are intentionally excluded from Git. Compact summaries,
tables, plots, and scripts are suitable for repository tracking.
