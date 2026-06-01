from __future__ import annotations

import importlib.metadata
import platform
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from . import INSTRUMENT_VERSION
from .util import canonical_json, stable_hash, utc_now, write_json


ARTIFACT_SCHEMA_VERSION = "0.1.0"
RUNNER_VERSION = "0.1.0"
PROTOCOL_VERSION = "future_field_atlas_infrastructure_v0"
REBUILD_CONTRACT_VERSION = "0.1.0"
DEFAULT_DEPENDENCIES = ("numpy",)


def rebuild_contract_payload(
    *,
    runner_module: str,
    config: dict[str, object],
    raw_data_retention: str,
    argv: Sequence[str] | None = None,
    git: dict[str, object] | None = None,
    dependency_versions: dict[str, str] | None = None,
) -> dict[str, object]:
    git_payload = git if git is not None else git_metadata()
    source_commit = str(git_payload.get("source_commit", "") or "")
    source_dirty = bool(git_payload.get("source_dirty", True))
    rebuild_status = "exact_rebuild_supported" if source_commit and not source_dirty else "logical_rebuild_only"
    return {
        "rebuild_contract_version": REBUILD_CONTRACT_VERSION,
        "rebuild_status": rebuild_status,
        "raw_data_retention": raw_data_retention,
        "contract_written_utc": utc_now(),
        "instrument_version": INSTRUMENT_VERSION,
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "runner_version": RUNNER_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "runner_module": runner_module,
        "command_line": " ".join(argv if argv is not None else current_argv()),
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "config_digest": stable_hash(canonical_json(config), length=24),
        "git": git_payload,
        "dependency_versions": dependency_versions if dependency_versions is not None else dependency_version_map(),
        "exact_rebuild_requirements": [
            "same source_commit",
            "source_dirty must be false",
            "same runner_module and command_line arguments",
            "same run_config and formal manifests",
            "same Python and dependency versions where numeric kernels are used",
        ],
        "raw_discard_policy": (
            "Raw topology may be discarded for exploratory or calibration runs after compact summaries, "
            "manifests, audits, and retained notes are preserved. Discarding raw topology downgrades "
            "practical verification unless this contract is exact-rebuild-supported."
        ),
    }


def write_rebuild_contract(
    out_dir: Path,
    *,
    runner_module: str,
    config: dict[str, object],
    raw_data_retention: str,
    argv: Sequence[str] | None = None,
) -> dict[str, object]:
    payload = rebuild_contract_payload(
        runner_module=runner_module,
        config=config,
        raw_data_retention=raw_data_retention,
        argv=argv,
    )
    write_json(out_dir / "future_field_atlas_rebuild_contract.json", payload)
    return payload


def git_metadata() -> dict[str, object]:
    return {
        "source_commit": git_output("rev-parse", "HEAD"),
        "source_branch": git_output("branch", "--show-current"),
        "source_dirty": bool(git_output("status", "--short")),
    }


def current_argv() -> Sequence[str]:
    return getattr(sys, "orig_argv", sys.argv)


def git_output(*args: str) -> str:
    try:
        result = subprocess.run(
            ("git", *args),
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:  # noqa: BLE001
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def dependency_version_map(names: Sequence[str] = DEFAULT_DEPENDENCIES) -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not_installed"
    return versions
