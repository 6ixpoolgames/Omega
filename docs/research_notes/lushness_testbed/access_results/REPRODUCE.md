# Reproduce the first access slices

Run from the original Omega checkout on Windows with its existing `.venv`.
Requires NumPy, SciPy, pytest and BioNetGen package 0.8.7 (bundled engine 2.9.3),
plus Git's Perl runtime at `C:/Program Files/Git/usr/bin/perl.exe`.

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_bng_calibration.py tests/test_assembly_slice.py tests/test_controlled_slice.py -q
.\.venv\Scripts\python.exe scripts/run_access_slices.py smoke
.\.venv\Scripts\python.exe scripts/run_access_slices.py assembly
.\.venv\Scripts\python.exe scripts/run_access_slices.py controlled
```

Each runner prints a new output directory, input hash, exit status and resource
profile. It installs a 1 GiB Windows job memory limit before releasing its worker;
wall cap 120 seconds, output cap 256 MiB. Raw engine files, source snapshots and
results remain under ignored `results/local_runs/lushness_testbed/`. No cleanup
or publication is performed. A capped/incomplete result is not a numerical zero.

To recreate the retained report from the completed original runs:

```powershell
.\.venv\Scripts\python.exe scripts/report_access_slices.py results/local_runs/lushness_testbed/assembly-20261013T014431Z-82ab40 results/local_runs/lushness_testbed/controlled-20261013T014447Z-64057b --output docs/research_notes/lushness_testbed/access_results
```

Use the new run directory names when reproducing. The report scores B1–B8,
retains unfavorable signs, and records result/report hashes. Physical parameters,
controller grid, horizons and clock choices are in the fixture protocols. Exact
mode here means complete finite enumeration and floating-point matrix propagation.

The earlier assembly-check directory was an engineering run outside the shared
resource wrapper; the report discloses that and a non-numerical beta annotation
made before the final capped run. No post-result rate tuning occurred. Controller
smoke checked generator consistency and equilibrium before ranking any policy.

Scope still deferred: general cache eviction/indexing, a genuine matched gas
ensemble, self-subject projected-history optimization, larger controller classes,
population growth, lineage, and embodied sensing/computational hardware.
