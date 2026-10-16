# Reproduction and local resource use

The ordinary-agent and activity controls are complete. The B1 map has its own
`SURVEY_STATUS.json`; do not infer completion from the control report.

Commands from the repository root, using its Python environment:

```powershell
.venv/Scripts/python.exe -m pytest tests/test_fractional_discovery.py tests/test_uniformized_entropy.py tests/test_domination_friction.py tests/test_domination_stage_a.py -q
.venv/Scripts/python.exe scripts/run_domination_b1.py followup --jobs 3 --seconds 150 --budget 1500
.venv/Scripts/python.exe scripts/run_domination_b1.py survey --jobs 4 --seconds 900 --budget 14400
.venv/Scripts/python.exe scripts/report_domination_b1.py
.venv/Scripts/python.exe scripts/validate_domination_b1.py survey
.venv/Scripts/python.exe scripts/plot_domination_b1.py
```

Every case has a frozen source/configuration bundle, process-tree caps, an output
hash and a compact receipt. Cache reuse requires matching source/configuration
identity and a verified completed output. New source versions receive new keys.
The sampler and compiler use the same native event definitions.

`SOURCE_ARCHIVES.json` indexes small code-only snapshots under `source_archives/`.
Each archive contains the exact relative-path bytes of one run source, not
matrices, environments or large result dumps. The combined source hash is SHA256
of sorted `(relative path UTF-8 + zero byte + source bytes)` entries. The original
configuration and caps are in each receipt and frozen manifest. Reconstructing
an old bundle should use its source archive and configuration, rather than
silently using a later implementation. Current code may add a faster backend;
the archive preserves the exact original implementation.

Engineering history is retained in `EXPONENTIAL_ATTEMPT.json`, the smoke status
files and `BACKEND_COMPARISON.json`. The original three-clock exponential smoke
stopped at 900 seconds. Its queued survey was stopped before producing any
scientific score. The Poisson-series backend then matched the completed
exponential smoke within 4×10⁻¹³ bits, and serial/threaded versions agreed on
all twelve full-model finite-history scores. It changes a numerical query,
not the physical transition law or the objective.

Per-case memory cap is 3 GiB, wall cap 900 seconds and output cap 32 MiB. The
batch initially used four workers, each with four row-block threads and BLAS
threads held to one by the process wrapper. Memory fit, but simultaneous cases
took 839–859 seconds, compared with 277 seconds for the isolated calibration.
After retaining four completed receipts, the exact original source/configuration
batch resumed with two workers. CONCURRENCY_RESTART.json records the change;
scripts/resume_domination_b1.py replays the original snapshot without adopting
new working-tree code. These settings follow a 1.14 GiB measured peak and
6.86 GiB available physical RAM. Local retained-data budget is 2 GiB; disk safety reserve
4 GiB. No dense transition matrices are saved. A numerical or resource error
halts queued cases; completed receipts remain reusable.

The Poisson-series omitted probability is bounded before ranking. Its entropy
allowance propagates through the sampled horizon, alongside solver residuals.
Uniformization clocks are numerical auxiliaries and contribute no physical
branching. Projected histories remain hidden-Markov: reported D/S intervals
must not be replaced by midpoint scores or Markov lumpings.

The current implementation additionally checkpoints small entropy-row blocks,
with checksums and keys derived from the actual generator, clocks and numerical
method. A partial or corrupted block is recomputed. These checkpoints contain
entropy vectors, not transition kernels. They are enabled in future new-source
runs. The original frozen B1 batch continues with its original source; completed
cases are not recomputed simply to adopt this newer checkpoint feature.

Code, compact maps, receipts, figures and small source archives are durable
research records. Local run bundles and kernels are reconstructable; no cleanup
or publication is performed by these reproduction commands.
