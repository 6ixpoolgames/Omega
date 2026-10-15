# Reproduction and retained evidence

The scientific sources, physical rules, exact parameters, reference measures,
queries and predictions are frozen in PROTOCOL.json and the per-run manifests.
ENGINEERING_STATUS/RESULTS.json record feasibility before rankings. Per-law JSON
and CSV maps contain signed results for every root/reference and cadence. Raw
source bundles and worker logs remain under the ignored local result directory.
No large kernel or trajectory dump is needed for these exact calculations.

Initial execution used the repository's local Python environment:

```powershell
& .venv/Scripts/python.exe -m pytest tests/test_reactive_lattice.py tests/test_same_law_profile.py tests/test_temporal_profile.py -q
& .venv/Scripts/python.exe scripts/run_reactive_lattice.py engineering
& .venv/Scripts/python.exe scripts/run_reactive_lattice.py prepare
& .venv/Scripts/python.exe scripts/run_reactive_lattice.py science
& .venv/Scripts/python.exe scripts/report_same_law_gas.py
```

Do not replace an existing frozen protocol. The execution runner resumes only
incomplete cases; completed cases are not silently rerun. For independent replay,
use the retained manifest/config and matching source bundle in a new run output
directory through the shared frozen runner. Validate source hashes and result
receipts; changing an irrelevant bundled source still requires a disclosed new
snapshot. A new physical variant receives its own versioned protocol/directory.

The separate horizon follow-up uses a disclosed retrospective query plan:

```powershell
& .venv/Scripts/python.exe scripts/run_reactive_lattice_tail.py
& .venv/Scripts/python.exe scripts/report_reactive_lattice_tail.py
& .venv/Scripts/python.exe scripts/plot_same_law_horizon.py
```

The tail runner verifies original source bytes before extending every law and
reproduces T1024 contrasts before saving follow-up results. Original prediction
scores remain unchanged. EXECUTION_INCIDENTS.md retains the writer-only repair.

The equal-work companion has its own calibration and protocol:

```powershell
& .venv/Scripts/python.exe scripts/run_throughput_match.py calibration
& .venv/Scripts/python.exe scripts/run_throughput_match.py prepare
& .venv/Scripts/python.exe scripts/run_throughput_match.py science
& .venv/Scripts/python.exe scripts/report_throughput_match.py
```

Its results live in compounding/matched_throughput. Do not describe those
different source-rate mechanisms as a same-law gas preparation comparison.
Calibration matches stationary accepted work; finite cumulative work is reported,
not matched. Storage cleanup must preserve referenced/pinned snapshots or retain
their exact sources, manifests and receipts before evicting reconstructable data.
