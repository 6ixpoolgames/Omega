# VAL0-CT Deterministic Case Summary

These are hand-built go/no-go cases for R1 vs R0-lookahead divergence.

| case | R1 task | R0-lookahead task | same choice | R1 LHR | R0-lookahead LHR | pass note |
|---|---:|---:|---:|---:|---:|---|
| case_brittle_peak | 1 | 0 | 0 | 0.929 | 0.857 | PASS |
| case_flat | 0 | 0 | 1 | 1.000 | 1.000 | diagnostic |
| case_lock_in | 2 | 2 | 1 | 1.133 | 1.067 | PASS |
| case_sparse_collapse | 0 | 0 | 1 | 0.000 | 0.000 | diagnostic |
