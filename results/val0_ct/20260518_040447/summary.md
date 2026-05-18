# VAL0-CT Overnight Attempt Summary

Status: timed out before completion.

This run attempted the full lower-bound overnight grid from
`docs/VAL0_CT_OVERNIGHT_BATCH_SPEC.md`:

```text
families:
  brittle_peak=150 seeds
  structured_asymmetric_v2=100 seeds
  lock_in_seeded=50 seeds
  low_resolution_dense=50 seeds

h: 1, 2, 4
H: 4, 8, 16
T: 16, 32, 64
policies: random, R0, R0_lookahead, R1, pseudo_omega
workers: 18
sample_size: 256
max_paths: 512
```

The process consumed the full 10-hour wall-clock cap and was terminated by the
runner timeout. Because the previous runner buffered rows in memory until normal
completion, this attempt produced only `config.json` and no analyzable result
rows.

Interpretation:

- The deterministic go/no-go gate passed in
  `results/val0_ct/deterministic_cases_overnight_prep_v2/`.
- The local calibration in `results/local_runs/val0_ct_overnight_calibration/`
  showed promising R1/R0-lookahead separation, but it is intentionally local and
  ignored.
- The full grid was too large for the current implementation and 10-hour cap.

Immediate workflow fix:

```text
run_smoke.py now streams JSONL rows as they complete so future interrupted runs
leave salvageable partial results.
```

Recommended next allocation:

```text
Drop T=64 and H=16 for the main randomized sweep, or split the run into
separate family/horizon batches. Keep brittle_peak prioritized.
```

