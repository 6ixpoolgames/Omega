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

The most direct view is:

```text
horizon_response_metric_rgb_spectrogram.png
```

RGB mapping:

```text
red:
  positive spectral_mass_delta_fraction

green:
  mean_subspace_alignment

blue:
  positive transport_entropy_delta
```

So stable aligned transport is mostly green, while amplified-aligned transport
is yellow/orange because mass growth adds red while alignment remains green.
