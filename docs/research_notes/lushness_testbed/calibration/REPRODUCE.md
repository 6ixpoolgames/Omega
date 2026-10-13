# Binding calibration reproduction

This is an engineering calibration. It does not run the three feedback arms or
discover policies. Use the existing Omega branch; no commit/push is automatic.

## Environment

Python 3.12, NumPy and SciPy from the repository environment; pytest for focused
tests. `bionetgen==0.8.7` supplies BioNetGen 2.9.3 and its Windows native simulator.
This calibration invokes BNG2.pl and run_network directly. The Python convenience
API is not used, so its optional dependency tree is not installed. The local
package was installed with `python -m pip install --no-deps bionetgen==0.8.7`.
Perl is required; the tested installation is Git for Windows Perl 5.38.2. BNGPATH
and forward-slash engine paths accommodate this runtime. The first attempt failed
because of module-path discovery; its error log is retained locally.

Manifest records actual dependency versions and engine/source hashes. BioNetGen
package wrapper license and bundled engine license are distinct (MIT wrapper,
GPL engine notices); no binaries or upstream tutorial source are redistributed
in the tracked packet. Custom calibration BNGL files state their adaptation.

## Upstream input

Retrieve the pinned raw tutorial file, without executing its ODE action:

https://raw.githubusercontent.com/RuleWorld/BNGTutorial/d74f5e415b533bb4bb470d024b5dafb03a4261e1/BAB/BAB.bngl

Place it under `results/local_runs/lushness_testbed/upstream/BAB.bngl`. Expected
SHA-256 is in PROTOCOL.json; the worker verifies it before engine execution and
copies it into the local run provenance. Upstream original is not our adapted
population/rate fixture. No claim of empirical parameter calibration is made.

## Commands from repository root

    .venv/Scripts/python.exe -m pytest tests/test_bng_calibration.py -q
    .venv/Scripts/python.exe scripts/run_bng_binding_calibration.py --check-caps
    .venv/Scripts/python.exe scripts/run_bng_binding_calibration.py

The runner creates a new ignored directory and prints its path. It sets a
120-second wall cap and 1-GiB process-tree commit limit before releasing the
worker. A 256-MiB output watchdog is also active. Caps are engineering boundaries,
not changes to the physical law. No old results are overwritten or deleted.

Each run retains protocol/source snapshot, manifest, generated networks, compact
summary/report, simulation outputs, final artifact hashes and resource profile.
The report is generated from numerical results. A successful run requires all
registered checks, including the external engine comparison. Simulation-only
agreement is statistical, not proof; generator matches are the stronger tiny-case
checks. Exact here means state enumeration, with floating numerical propagation.

## Scope and pending workflow work

The parser supports a narrow, explicit mass-action subset and rejects unsupported
kinetics. It does not yet compile energy-based rules, driven reservoirs, physical
controllers or large population graphs. Strong lumping of the law does not mean
the fine history entropy is preserved.

Manifests, source bundles, caps and reports are implemented for this calibration.
General JSON-schema validation, cached rebuilds, SQLite indexing, storage-budget
eviction, arbitrary structural surveys and controller optimization remain pending.
Everything here is pinned; the proposed deletion policy is not active.
