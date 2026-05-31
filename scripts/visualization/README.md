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

When the run includes `horizon_transport_matrix_entries.csv`, the utility also
emits:

```text
raw_transport_matrix_atlas.png
```

This is an instrument-native view: rows are source-horizon probe items, columns
are target-horizon probe items, and color is raw transport mass on a `log1p`
scale. It is a view of the retained transport matrix, not response-class
interpretation and not necessarily raw substrate state.

The runner also writes the retained transport matrices in compact sparse form:

```text
horizon_transport_matrix_sparse.npz
```

That artifact stores matrix index, row index, column index, and transport mass
arrays, with row/column labels in the existing matrix and item manifest CSVs.
Use it for larger raw-matrix analysis rather than expanding every entry into a
large CSV.

When the run opts into raw frontier state sampling with
`--raw-state-sample-jobs`, the utility emits:

```text
raw_substrate_state_frontier_heatmap.png
```

Rows are actual raw substrate state tuples from `X`, columns are sampled
exact-frontier contexts/horizons, and color is frontier presence count. The
matching compact sparse artifact is:

```text
horizon_transport_raw_state_frontier_sparse.npz
```
