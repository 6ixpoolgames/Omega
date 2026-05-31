# Visualization Utilities

These scripts consume existing run outputs and write local figures. They should
not be imported by validation runners.

## Horizon Transport Spectrogram

```powershell
.venv\Scripts\python.exe scripts\visualization\plot_horizon_transport_spectrogram.py --run-dir results\local_runs\<run_id>
```

Default output:

```text
results/local_runs/<run_id>/figures/
```

Generated figures are local diagnostics and are not committed unless explicitly
promoted.
