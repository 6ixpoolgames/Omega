# Implementation checks

2026-10-01, on the local working tree, after the export fix and lint cleanup:

- `python -m pytest tests/test_timing_volume_counterexample.py -q`:
  **19 passed in 6.39s**.
- `python -m ruff check omega_v2/finite/timed_execution.py omega_v2/experiments/timing_volume_counterexample_v0.py omega_v2/validation/timing_volume_counterexample_v0.py tests/test_timing_volume_counterexample.py`:
  **All checks passed**.

The tests verify the race integrals, process laws, physical accounting,
conditioning, structural witnesses, profile collision and evidence export.
They are implementation checks. The candidate's comparison fails the
registered adequacy condition. No full-repository test run is claimed.

An initial evidence-export attempt failed on a NumPy boolean. The exporter now
uses a native boolean; the end-to-end export regression test is included in
the 19 tests. The model and frozen volume formula were not changed.
