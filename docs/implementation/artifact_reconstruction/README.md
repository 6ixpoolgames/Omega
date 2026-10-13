# Reconstructible cache cleanup

2026-10-14.11 generated NumPy archives totaling186,052,331bytes were selected for
removal only after independently rebuilding their arrays from retained source.
Every array matched exactly on the recorded environment. No new scientific
comparison, optimizer ranking or reinterpretation was performed.

[RECONSTRUCTION_MANIFEST.json](RECONSTRUCTION_MANIFEST.json) lists each retired
path, original SHA256, exact-array verification, source/configuration provenance,
runtime/environment and reconstruction command. Source commits/history remain;
this cleanup does not rewrite history or force-push. Current uncommitted research
work is preserved. Reports and JSON evidence remain at their existing paths.

## Rebuild

From the Omega root, for example:

```powershell
.venv/Scripts/python.exe scripts/reconstruct_artifact.py --artifact catalytic-binding-1 --output results/local_runs/rebuilt/barrier_1_kernels.npz
```

Every archive has its own command in the manifest. The builder uses retained
model/runner definitions, constants and initial distributions, without reading
the deleted archive or relying on that archive's Git blob. These are deterministic
finite-matrix calculations; RNG seeds are not applicable. Python/NumPy/SciPy versions
are recorded. ZIP container bytes and floating results on different library versions
are not promised byte-identical; schemas and numerical comparisons are explicit.

Thermal-binding used an earlier spatial model. Its original recorded source hash
did not match the current model. The exact historical source is preserved in
[spatial_binding_thermal_20261003.py](spatial_binding_thermal_20261003.py) and used
by the builder, rather than silently regenerating with a changed model.

For larger rebuilds use the shared hard-cap runner and the recorded120s/1GiB
per-process envelope. The verification runs used frozen snapshots and retained
their checks under ignored results/local_runs/artifact_reconstruction. The CLI
example is a reconstruction utility, not itself a process cap.

## What was not purged

Large evidence JSON, legacy tables, figures, external references, pinned scientific
snapshots, context briefs, source, manifests and drafts were left in place. A filename
or size is not enough to establish rebuildability. Other files need their own audit;
this11-file manifest is not permission to delete whole results directories.

Current-clone raw caches are deleted and staged as removals. Old versions remain
in Git history and on the remote until a separately authorized publication/history
operation. Therefore this removes current-tree payload, not all historical clone
cost. There was no commit, push, history rewrite or remote deletion in this pass.

## Preventing recurrence

[check_repository_artifacts.py](../../../scripts/check_repository_artifacts.py)
checks actual staged Git blobs. Changed artifacts over5MiB are blocked; new/changed
raw .npy/.npz under research notes/results are blocked even when small. Existing
unchanged legacy files are grandfathered. Deleted paths are allowed. Exact path
exceptions require a stated reason in the checked
[ARTIFACT_POLICY.json](../ARTIFACT_POLICY.json); there are currently no exceptions.

The local pre-commit hook is enabled through repository-local core.hooksPath.
The committed hook and CI workflow will make this reproducible for other checkouts;
hooks require local installation and can be bypassed, so CI provides another check.
Neither safeguard retroactively purges old blobs.
