"""Launch a verified worker from its frozen bundle using the shared cap runner."""
from __future__ import annotations

import importlib.util
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Mapping, Sequence

from .manifest import _relative_name, verify_bundle


def _load_capped(snapshot_root: Path, manifest: Mapping[str, Any]):
    rel = "scripts/run_bng_binding_calibration.py"
    if not any(row.get("path") == rel for row in manifest.get("sources", [])):
        raise ValueError(f"frozen bundle does not include required cap runner: {rel}")
    script = snapshot_root / rel
    script = script.resolve(strict=True)
    if not script.is_relative_to(snapshot_root.resolve(strict=True)):
        raise ValueError("frozen cap runner escapes bundle")
    spec = importlib.util.spec_from_file_location("_omega_capped_runner", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load cap runner at {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.capped


def run_frozen(out: str | Path, worker_relative: str,
               args: Sequence[str] = (), caps: Mapping[str, Any] | None = None,
               ) -> dict[str, Any]:
    """Verify then run ``source/<worker_relative>`` under process-tree caps.

    The worker contract is to block on one ``GO`` line on stdin, prepend its
    snapshot root to ``sys.path``, and report imported module paths. The shared
    cap helper sends the gate token after assigning the child to its job object.
    """
    output = Path(out).resolve(strict=True)
    manifest = verify_bundle(output)
    rel = _relative_name(worker_relative)
    source_root = output / "source"
    worker = source_root.joinpath(*PurePosixPath(rel).parts).resolve(strict=True)
    if not worker.is_file() or not worker.is_relative_to(source_root.resolve()):
        raise ValueError("worker must be a file inside the frozen source bundle")
    if not any(row["path"] == rel for row in manifest["sources"]):
        raise ValueError("worker is not listed in the frozen manifest")
    cap = _load_capped(source_root, manifest)
    options = dict(caps or {})
    seconds = options.pop("seconds", 120)
    memory = options.pop("memory", 1024 ** 3)
    output_cap = options.pop("output_cap", 256 * 1024 ** 2)
    if options:
        raise TypeError(f"unknown cap options: {', '.join(sorted(options))}")
    command = [sys.executable, "-u", str(worker), *map(str, args)]
    result = cap(command, output, seconds=seconds, memory=memory,
                 output_cap=output_cap)
    return {"input_hash": manifest["input_hash"], **result}
