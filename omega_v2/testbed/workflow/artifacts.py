"""Small SQLite run/artifact index and non-destructive cache planning."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import time
from contextlib import contextmanager
from typing import Any, Iterable, Mapping

from .manifest import _canonical

GIB = 1024 ** 3


class ArtifactIndex:
    """A local index; artifact payloads remain ordinary files."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY, input_hash TEXT, status TEXT NOT NULL,
                    cache_key TEXT, manifest_json TEXT NOT NULL, updated REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id TEXT PRIMARY KEY, run_id TEXT, path TEXT NOT NULL,
                    bytes INTEGER NOT NULL, sha256 TEXT, retention TEXT NOT NULL,
                    locked INTEGER NOT NULL DEFAULT 0, pinned INTEGER NOT NULL DEFAULT 0,
                    cited INTEGER NOT NULL DEFAULT 0, cache_key TEXT,
                    metadata_json TEXT NOT NULL, updated REAL NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                );
                CREATE INDEX IF NOT EXISTS artifacts_cache_key ON artifacts(cache_key);
            """)

    @contextmanager
    def _connect(self):
        db = sqlite3.connect(self.path)
        db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def register_run(self, run_id: str, *, status: str, manifest: Mapping[str, Any],
                     input_hash: str | None = None, cache_key: str | None = None) -> None:
        if status not in {"active", "complete", "incomplete", "cap_hit", "failed", "numerical_failure"}:
            raise ValueError(f"unsupported run status: {status}")
        packed = json.dumps(manifest, sort_keys=True, separators=(",", ":"), allow_nan=False)
        with self._connect() as db:
            db.execute("""INSERT INTO runs(run_id,input_hash,status,cache_key,manifest_json,updated)
                VALUES(?,?,?,?,?,?) ON CONFLICT(run_id) DO UPDATE SET
                input_hash=excluded.input_hash,status=excluded.status,cache_key=excluded.cache_key,
                manifest_json=excluded.manifest_json,updated=excluded.updated""",
                       (run_id, input_hash, status, cache_key, packed, time.time()))

    def register_artifact(self, artifact_id: str, path: str | Path, *, bytes: int,
                          retention: str, run_id: str | None = None,
                          sha256: str | None = None, locked: bool = False,
                          pinned: bool = False, cited: bool = False,
                          cache_key: str | None = None,
                          metadata: Mapping[str, Any] | None = None) -> None:
        if bytes < 0:
            raise ValueError("artifact bytes must be nonnegative")
        packed = json.dumps(metadata or {}, sort_keys=True, separators=(",", ":"), allow_nan=False)
        with self._connect() as db:
            db.execute("""INSERT INTO artifacts(artifact_id,run_id,path,bytes,sha256,retention,
                locked,pinned,cited,cache_key,metadata_json,updated) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(artifact_id) DO UPDATE SET run_id=excluded.run_id,path=excluded.path,
                bytes=excluded.bytes,sha256=excluded.sha256,retention=excluded.retention,
                locked=excluded.locked,pinned=excluded.pinned,cited=excluded.cited,
                cache_key=excluded.cache_key,metadata_json=excluded.metadata_json,updated=excluded.updated""",
                       (artifact_id, run_id, os.fspath(path), bytes, sha256, retention,
                        int(locked), int(pinned), int(cited), cache_key, packed, time.time()))

    def set_status(self, run_id: str, status: str) -> None:
        if status == "complete":
            pass
        elif status not in {"active", "incomplete", "cap_hit", "failed", "numerical_failure"}:
            raise ValueError(f"unsupported run status: {status}")
        with self._connect() as db:
            cur = db.execute("UPDATE runs SET status=?,updated=? WHERE run_id=?", (status, time.time(), run_id))
            if cur.rowcount != 1:
                raise KeyError(run_id)

    def cache_manifest(self, cache_key: str) -> dict[str, Any] | None:
        """Return only a completed cache record; failures never become hits."""
        with self._connect() as db:
            row = db.execute("""SELECT run_id,input_hash,status,manifest_json FROM runs
                WHERE cache_key=? ORDER BY updated DESC LIMIT 1""", (cache_key,)).fetchone()
            if row is None or row[2] != "complete":
                return None
            artifacts = db.execute("""SELECT artifact_id,path,bytes,sha256,retention FROM artifacts
                WHERE run_id=? ORDER BY artifact_id""", (row[0],)).fetchall()
        if not artifacts:
            return None
        verified_artifacts = []
        for artifact_id, raw_path, size, claimed_hash, retention in artifacts:
            path = Path(raw_path)
            try:
                resolved = path.resolve(strict=True)
                if not resolved.is_file() or resolved.stat().st_size != size:
                    return None
                digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
            except OSError:
                return None
            if claimed_hash is None or digest != claimed_hash:
                return None
            verified_artifacts.append({"artifact_id": artifact_id, "path": str(resolved),
                                       "bytes": size, "sha256": digest,
                                       "retention": retention})
        return {"run_id": row[0], "input_hash": row[1], "status": row[2],
                "manifest": json.loads(row[3]),
                "artifacts": verified_artifacts}

    def artifacts(self) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("""SELECT artifact_id,run_id,path,bytes,sha256,retention,
                locked,pinned,cited,cache_key,metadata_json FROM artifacts ORDER BY updated""").fetchall()
        return [{"artifact_id": r[0], "run_id": r[1], "path": r[2], "bytes": r[3],
                 "sha256": r[4], "retention": r[5], "locked": bool(r[6]),
                 "pinned": bool(r[7]), "cited": bool(r[8]), "cache_key": r[9],
                 "metadata": json.loads(r[10])} for r in rows]


def _validated_path(root: Path, record: Mapping[str, Any]) -> Path:
    raw = Path(os.fspath(record["path"]))
    lexical = raw if raw.is_absolute() else root / raw
    try:
        # Resolve existing parent links first so traversal and escaping links
        # are rejected even when the final path does not exist.
        root_real = root.resolve(strict=True)
        prospective = lexical.resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"cache artifact path cannot be resolved: {raw}") from exc
    try:
        prospective.relative_to(root_real)
    except ValueError as exc:
        raise ValueError(f"cache artifact escapes cache root: {raw}") from exc
    try:
        resolved = lexical.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"cache artifact path cannot be resolved: {raw}") from exc
    try:
        resolved.relative_to(root_real)
    except ValueError as exc:
        raise ValueError(f"cache artifact escapes cache root: {raw}") from exc
    if not resolved.is_file():
        raise ValueError(f"cache artifact is not a regular file: {raw}")
    return resolved


def dry_run_eviction(cache_root: str | Path, records: Iterable[Mapping[str, Any]],
                     budget: int = 5 * GIB, target: int = 4 * GIB) -> dict[str, Any]:
    """Plan LRU eviction toward target. This function never deletes anything."""
    root = Path(cache_root).resolve(strict=True)
    if budget < 0 or target < 0 or target > budget:
        raise ValueError("target must be between zero and budget")
    validated: list[tuple[Mapping[str, Any], Path, int]] = []
    seen: set[Path] = set()
    total = 0
    for row in records:
        path = _validated_path(root, row)
        if path in seen:
            raise ValueError(f"duplicate cache artifact path: {path}")
        seen.add(path)
        size = path.stat().st_size
        if "bytes" in row and int(row["bytes"]) != size:
            raise ValueError("cache artifact size differs from manifest")
        if size < 0:
            raise ValueError("cache artifact bytes must be nonnegative")
        total += size
        validated.append((row, path, size))
    ordered = sorted(validated, key=lambda item: float(item[0].get("last_used", 0)))
    eligible_total = total
    protected: list[str] = []
    evict: list[dict[str, Any]] = []
    # Evict only if the budget is exceeded, then stop at the target.
    if total > budget:
        for row, path, size in ordered:
            if (row.get("locked") or row.get("pinned") or row.get("cited") or row.get("active")
                    or row.get("retention") not in ("cache", "scratch")):
                protected.append(str(row.get("artifact_id", path.name)))
                continue
            evict.append({"artifact_id": row.get("artifact_id", path.name),
                          "path": str(path), "bytes": size})
            eligible_total -= size
            if eligible_total <= target:
                break
    return {"mode": "dry_run", "cache_root": str(root), "budget_bytes": budget,
            "target_bytes": target, "current_bytes": total,
            "projected_bytes": eligible_total, "over_budget": total > budget,
            "eligible_bytes": sum(row["bytes"] for row in evict),
            "protected": protected, "eviction_candidates": evict,
            "deleted": False}


def summaries_match(actual: Any, expected: Any, tolerance: float = 0.0) -> bool:
    """Compare canonical JSON summaries, allowing numeric tolerance if requested."""
    if tolerance < 0 or not math.isfinite(tolerance):
        raise ValueError("tolerance must be finite and nonnegative")
    if isinstance(actual, bool) or isinstance(expected, bool):
        return type(actual) is type(expected) and actual == expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return math.isfinite(float(actual)) and math.isfinite(float(expected)) and math.isclose(
            float(actual), float(expected), rel_tol=tolerance, abs_tol=tolerance)
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            summaries_match(actual[key], expected[key], tolerance) for key in actual)
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        return len(actual) == len(expected) and all(
            summaries_match(a, b, tolerance) for a, b in zip(actual, expected))
    return type(actual) is type(expected) and _canonical(actual) == _canonical(expected)


def validate_reconstruction(actual: Any, expected: Any, tolerance: float = 0.0) -> dict[str, Any]:
    return {"status": "pass" if summaries_match(actual, expected, tolerance) else "fail",
            "tolerance": tolerance}
