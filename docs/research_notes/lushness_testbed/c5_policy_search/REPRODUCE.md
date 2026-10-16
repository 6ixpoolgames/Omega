# Reproduction and retained data

From the Omega repository root, using the project Python environment:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_reactive_allocation.py -q
.venv/Scripts/python.exe scripts/run_c5_policy_search.py --smoke --jobs 1 --seconds 240 --budget 600
.venv/Scripts/python.exe scripts/run_c5_policy_search.py --jobs 2 --seconds 600 --budget 14400
.venv/Scripts/python.exe scripts/report_c5_policy_search.py
```

The first engineering smoke preceded the addition of the no-command response
and used its own frozen snapshot. The complete survey uses one later snapshot
covering all 36 tables, including no-command. Every numerical case is executed
from that immutable source; report-only changes do not alter those executions.

`SURVEY_PLAN.json` contains the complete executable table family and frozen
numerical-source hash. `SURVEY_STATUS.json` and `receipts/` retain cap measurements,
configuration, source/import evidence and result hashes. `cases/` retains compact
histories, HMM bounds, physical ledgers and numerical residuals. The report checks
the receipts, bounds' numerical residual envelope and shared physics before ranking.

`source_archives/` contains exact code, tests and specification used by each
execution snapshot. Reconstruct an older execution by extracting the corresponding
archive, using the parameters/controller/horizons in its receipt, and invoking
the same capped worker through the workflow runner. Running the current command
uses current source and creates new source/configuration identities when changed.

Full kernels are numerical intermediates, not retained publication artifacts.
Ignored local bundles live under `results/local_runs/lushness_testbed/c5_policy_search`.
They contain reconstructible source copies and compact worker outputs, not a new
canonical theory document. Keep compact results, receipts, source archives and
their SHA-256 indexes before any later cleanup of local bundles.

The streamed two-observation calculation avoids an N-by-G-by-G array. At the
primary 3,000-state inventory, one 72 MB full transition kernel is held temporarily
for each cadence. The assay has a 192 MiB full-kernel allocation gate and a 3 GiB
process-tree cap. Larger models must either raise the declared allocation gate
after profiling or select a genuinely streamed kernel/query backend, rather than
silently reducing inventory. HDD storage can hold caches;
it does not reduce this kernel's RAM requirement unless the implementation is
explicitly changed to stream or memory-map that array.

No commit, push, Drive upload or automated deletion occurs in these commands.
