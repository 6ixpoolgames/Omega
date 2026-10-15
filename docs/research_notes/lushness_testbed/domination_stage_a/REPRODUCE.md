# Reproduce Stage A

From the Omega repository, using its existing Python environment:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_domination_friction.py tests/test_domination_stage_a.py tests/test_temporal_profile.py -q
.venv/Scripts/python.exe scripts/run_domination_stage_a.py plan
.venv/Scripts/python.exe scripts/run_domination_stage_a.py smoke --jobs 2 --budget-seconds 900
.venv/Scripts/python.exe scripts/run_domination_stage_a.py survey --jobs 6 --budget-seconds 18000
.venv/Scripts/python.exe scripts/validate_domination_stage_a.py
.venv/Scripts/python.exe scripts/audit_domination_stage_a_aliases.py
.venv/Scripts/python.exe scripts/report_domination_stage_a.py
.venv/Scripts/python.exe scripts/plot_domination_stage_a.py
```

Plan emits the full case list; smoke emits engineering evidence. Survey uses the
same physical law and all declared horizons/cadences, with exact source and
configuration identities. Complete cache entries are verified and reused.
Incomplete entries do not stand in for completed cases. No run deletes files.

The batch freezes its source bytes once, then every worker imports only its
recorded copy. Editing the live research files afterward cannot change a running
worker. Each result includes imported paths and the manifest input hash. The
validator checks every receipt, every source snapshot and continuity with the
first map's 20 unchanged physical interventions.

The command's elapsed batch budget is separate from each worker's process-tree
caps. Storage accounting includes compact case files, receipts and local source
snapshots, with a conservative allowance for concurrent workers. A completed
case keeps only compact numerical outputs, metadata and source; its dense
transition matrices are not saved. Reconstruct them from the source/configuration
if needed. Source/configuration changes deliberately produce different caches.

The completed local batch used the initial 512 MiB storage ceiling, then reused
458 completed entries to finish the final 12 under a 1 GiB ceiling. The increased
ceiling affects admission only, not cache identity or physics. The explicit
resume call is:

```powershell
.venv/Scripts/python.exe -c "import sys;sys.path.insert(0,'scripts');from run_domination_stage_a import execute,make_plan;raise SystemExit(execute(make_plan()['cases'],'survey',jobs=6,budget_seconds=18000,output_budget=1024*1024**2))"
```

Windows can briefly hold the status file open while it is being replaced. The
following coordinator-only wrapper retries those writes and uses the same
source/configuration cache identities and unchanged numerical worker:

```powershell
.venv/Scripts/python.exe scripts/resume_domination_stage_a.py
```

It was used to reconcile the final complete status after a progress-file lock;
the numerical calculations had finished and their receipts were reused. The
complete execution timeline is in EXECUTION_ACCOUNT.json. ALIASES.json audits
equivalent effective target sets; every original random sample remains in its
control distribution even if an equivalent role case is found.

Reports are regenerated from verified compact files. Their figures and CSV maps
are reconstructable; no manual winner selection is needed. INTERPRETATION.md is
the explicitly labeled structural reading. The original proposal remains in
OPUS_PROPOSAL_r1.md; the implemented revisions are in SPECIFICATION.md.

## Mathematical scope

Full sampled-history entropy is computed from the native full-state generator.
Subject histories are deterministic projections of it and are generally
hidden-Markov. Their two-observation conditioning intervals are bounds, not
entropies of a substitute merged generator. Unresolved signs remain unresolved.
Rate is diagnostic; finite-history scores determine the listed family choices.

The cadence corridor tests temporal resolution only. It is not a universal
microscopic grain test. The temporal crossover coefficient is asymptotic and
is labeled accordingly. No random event or thermodynamic contribution is
subtracted to improve a ranking.

## Original numerical source retained

`SOURCE_ARCHIVES.json` indexes a small code-only archive of the exact 68-file
Stage A source. Later fractional-bank work changed the working implementation;
this archive preserves the original bytes independently of local run bundles.
It contains no kernels or result dumps. Use the recorded configuration with
this source when reproducing the original source identities.
