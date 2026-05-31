# Horizon-Transport Visualization Bundle

Source run: `results/local_runs/20260531_asymmetry_ladder_preservation_scaleup`

These figures are diagnostic visualizations of local CSV outputs. They do not add claim status.

The raw CSV/NPZ run artifacts remain local and ignored by default. This bundle
promotes only compact review figures and this manifest.

## Figures

- `raw_transport_matrix_atlas.png`
- `horizon_response_metric_rgb_spectrogram.png`
- `horizon_response_class_spectrogram.png`
- `transport_viscosity_score_spectrogram.png`
- `alignment_mass_entropy_panels.png`
- `saturation_coverage_profile.png`
- `response_threshold_ladder.png`

## RGB Spectrogram Mapping

`horizon_response_metric_rgb_spectrogram.png` maps measured variables directly:

- red: positive `spectral_mass_delta_fraction`
- green: `mean_subspace_alignment`
- blue: positive `transport_entropy_delta`

Stable aligned transport appears mostly green. Amplified-aligned transport appears yellow/orange because mass gain adds red while alignment stays green.

## Raw Transport Matrix Atlas

`raw_transport_matrix_atlas.png` uses `horizon_transport_matrix_entries.csv` when available. Rows are source-horizon items, columns are target-horizon items, and color is `log1p(transport_mass)` for retained sparse entries.

This atlas is instrument-native: its row/column items are probe-signature transport items, not necessarily raw substrate states.

## Raw Substrate State Frontier Heatmap

`raw_substrate_state_frontier_heatmap.png` uses `horizon_transport_raw_state_frontier_samples.csv` when available. Rows are actual substrate state tuples from `X`, columns are sampled exact-frontier contexts/horizons, and color is frontier presence count.

## Row Counts

- matrix entry rows: `155781`
- raw state sample rows: `0`
- response rows: `8792`
- viscosity rows: `8792`
- saturation rows: `11`
- threshold rows: `832`

## Response Classes

- transport_amplified_aligned: `877`
- transport_baseline_missing: `360`
- transport_reopens: `448`
- transport_rerouted: `430`
- transport_stable: `6602`
- transport_weakened: `75`

## Viscosity Reads

- high_viscosity_aligned_amplifier: `7479`
- medium_viscosity_response_threshold: `953`
- underpowered_or_unresolved: `360`
