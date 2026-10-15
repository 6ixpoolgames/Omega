# Execution incidents

The first retrospective horizon-extension worker propagated its native law to
T1024 andT4096, then failed writing RESULTS.json because the convergence flag
was a NumPy boolean rather than a Python boolean. Its log and frozen source
snapshot remain retained in the original tail run. This was not a physical,
entropy or convergence-calculation failure.

The flag is explicitly converted to bool for JSON serialization. No generator,
solver formula, target, tolerance, root, prediction or time query changed.
The failed execution receipt remains in TAIL_STATUS.json's prior attempts; its
cost is charged to the total budget. The unsuccessful first case is rerun with
the corrected writer and all other laws are retained. Original scientific runs
and prediction scores are untouched.
