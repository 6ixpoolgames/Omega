"""Frozen source bundles and semantic cache identities.

Callers enumerate the complete transitive source set. In particular, a worker
using the testbed should include every imported testbed ``.py`` file.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

SCHEMA = "omega-frozen-bundle/1"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_value(value: Any) -> str:
    return _hash_bytes(_canonical(value))


def _relative_name(name: str | os.PathLike[str]) -> str:
    raw = os.fspath(name).replace("\\", "/")
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"unsafe bundle path: {name!r}")
    if path.parts and ":" in path.parts[0]:
        raise ValueError(f"unsafe bundle path: {name!r}")
    return path.as_posix()


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def _source_path(repo: Path, rel: str) -> Path:
    source = repo.joinpath(*PurePosixPath(rel).parts)
    # Resolve first to reject symlinks that escape the declared checkout.
    resolved = source.resolve(strict=True)
    root = repo.resolve(strict=True)
    if not _inside(root, resolved) or not resolved.is_file():
        raise ValueError(f"bundle source is not a regular file inside repo_root: {rel}")
    return resolved


def freeze_bundle(repo_root: str | Path, out: str | Path,
                  files: Iterable[str | os.PathLike[str]],
                  config: Mapping[str, Any]) -> dict[str, Any]:
    """Copy an explicit relative source list and config into ``out/source``.

    The destination may be under the checkout's run-output tree. It must not
    contain the checkout, and no selected source may be inside the destination.
    Existing bundles are immutable and are never overwritten.
    """
    repo = Path(repo_root).resolve(strict=True)
    destination = Path(out).resolve()
    source_root = destination / "source"
    if _inside(destination, repo):
        raise ValueError("bundle output cannot contain the source checkout")
    if (destination / "manifest.json").exists():
        raise FileExistsError(f"frozen bundle already exists: {destination / 'manifest.json'}")
    names = sorted({_relative_name(name) for name in files})
    if not names:
        raise ValueError("a frozen bundle requires at least one source file")
    source_root.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for rel in names:
        original = _source_path(repo, rel)
        if _inside(destination, original):
            raise ValueError(f"selected source lies inside bundle output: {rel}")
        data = original.read_bytes()
        target = source_root.joinpath(*PurePosixPath(rel).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise FileExistsError(f"frozen source already exists: {target}")
        target.write_bytes(data)
        records.append({"path": rel, "bytes": len(data), "sha256": _hash_bytes(data)})
    config_data = json.loads(_canonical(config).decode("utf-8"))
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA,
        "config": config_data,
        "sources": records,
        "source_hash": _hash_value(records),
    }
    manifest["input_hash"] = _hash_value(manifest)
    destination.mkdir(parents=True, exist_ok=True)
    with (destination / "manifest.json").open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
    return manifest


def verify_bundle(out: str | Path) -> dict[str, Any]:
    """Verify manifest self-hash, source list hash, and every copied source."""
    root = Path(out).resolve(strict=True)
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != SCHEMA:
        raise ValueError("unsupported frozen bundle schema")
    claimed_input_hash = manifest.get("input_hash")
    unhashed = dict(manifest)
    unhashed.pop("input_hash", None)
    if claimed_input_hash != _hash_value(unhashed):
        raise ValueError("frozen bundle manifest hash mismatch")
    records = manifest.get("sources")
    if not isinstance(records, list) or manifest.get("source_hash") != _hash_value(records):
        raise ValueError("frozen bundle source-list hash mismatch")
    seen: set[str] = set()
    for record in records:
        rel = _relative_name(record.get("path", ""))
        if rel in seen:
            raise ValueError(f"duplicate source path in frozen bundle: {rel}")
        seen.add(rel)
        path = root / "source" / Path(*PurePosixPath(rel).parts)
        resolved = path.resolve(strict=True)
        if not _inside(root / "source", resolved) or not resolved.is_file():
            raise ValueError(f"frozen source escapes bundle or is not a file: {rel}")
        data = resolved.read_bytes()
        if len(data) != record.get("bytes") or _hash_bytes(data) != record.get("sha256"):
            raise ValueError(f"frozen source hash mismatch: {rel}")
    return manifest


def semantic_keys(world: Any, controller: Any, measurement: Any,
                  queries: Any, analysis: Any, sources: Any) -> dict[str, str]:
    """Return operator, query, and report cache keys.

    ``sources`` may be role grouped as ``operator``/``query``/``analysis``.
    A flat mapping is conservatively treated as operator source. ``analysis``
    is absent from the operator identity. Cadence remains in the operator key
    because it changes a sampled transition matrix.
    """
    # Source hashes may be supplied as explicit role groups. A plain mapping is
    # treated as operator/compiler source for compatibility with simple callers.
    grouped = (isinstance(sources, Mapping) and
               set(sources).issubset({"operator", "query", "analysis"}) and
               bool(sources))
    if grouped:
        operator_sources = sources.get("operator", {})
        query_sources = sources.get("query", {})
        analysis_sources = sources.get("analysis", {})
    else:
        operator_sources, query_sources, analysis_sources = sources, {}, {}
    operator = _hash_value({"world": world, "controller": controller,
                            "measurement": measurement, "sources": operator_sources})
    query = _hash_value({"operator": operator, "queries": queries,
                         "sources": query_sources})
    report = _hash_value({"query": query, "analysis": analysis,
                          "sources": analysis_sources})
    return {"operator_hash": operator, "query_hash": query, "report_hash": report}


def atomic_json(path: str | Path, value: Any) -> None:
    """Write JSON by replacing a sibling temporary file atomically."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + f".tmp-{os.getpid()}")
    try:
        temp.write_text(json.dumps(value, sort_keys=True, indent=2,
                                   ensure_ascii=False, allow_nan=False) + "\n",
                        encoding="utf-8")
        os.replace(temp, target)
    finally:
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass
