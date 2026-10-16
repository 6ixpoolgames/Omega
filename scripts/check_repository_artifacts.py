#!/usr/bin/env python3
"""Reject oversized or raw generated research artifacts before they enter Git."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_LIMIT = 5 * 1024 * 1024
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
POLICY_PATH = "docs/implementation/ARTIFACT_POLICY.json"


class GuardError(RuntimeError):
    pass


def git(repo: Path, *args: str, check: bool = True) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=False,
    )
    if check and result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise GuardError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def load_exceptions(repo: Path, revision: str = "") -> dict[str, str]:
    raw = git(repo, "show", f"{revision}:{POLICY_PATH}", check=False)
    if not raw:
        # Only exceptions retained in the checked index/revision are authoritative.
        return {}
    try:
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GuardError(f"invalid {POLICY_PATH}: {exc}") from exc
    if not isinstance(data, dict) or data.get("version") != 1:
        raise GuardError(f"{POLICY_PATH} must be an object with version: 1")
    rows = data.get("exceptions")
    if not isinstance(rows, list):
        raise GuardError(f"{POLICY_PATH} must contain an exceptions array")
    exceptions: dict[str, str] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise GuardError(f"{POLICY_PATH} exception {index} must be an object")
        path, reason = row.get("path"), row.get("reason")
        if not isinstance(path, str) or not path:
            raise GuardError(f"{POLICY_PATH} exception {index} needs a repository-relative path")
        path = path.replace("\\", "/")
        if path.startswith("/") or ".." in path.split("/"):
            raise GuardError(f"{POLICY_PATH} exception {index} needs a repository-relative path")
        if not isinstance(reason, str) or len(reason.strip()) < 8:
            raise GuardError(f"{POLICY_PATH} exception {index} needs a useful reason")
        if path in exceptions:
            raise GuardError(f"duplicate exception path in {POLICY_PATH}: {path}")
        exceptions[path] = reason.strip()
    return exceptions


def staged_entries(repo: Path) -> dict[str, tuple[str, int]]:
    """Return index path -> (blob oid, mode), never reading staged bytes from disk."""
    raw = git(repo, "ls-files", "--stage", "-z")
    entries: dict[str, tuple[str, int]] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, path_bytes = record.split(b"\t", 1)
        mode, oid, _stage = metadata.decode("ascii").split()
        entries[path_bytes.decode("utf-8", errors="surrogateescape")] = (oid, int(mode, 8))
    return entries


def changed_staged_paths(repo: Path) -> set[str]:
    raw = git(repo, "diff", "--cached", "--name-only", "--no-renames", "-z")
    return {p.decode("utf-8", errors="surrogateescape") for p in raw.split(b"\0") if p}


def generated_raw_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    in_target = normalized.startswith(("docs/research_notes/", "results/"))
    return in_target and normalized.endswith((".npy", ".npz"))


def inspect(repo: Path, paths: set[str], entries: dict[str, tuple[str, int]], limit: int,
            exceptions: dict[str, str]) -> list[str]:
    failures = []
    for path in sorted(paths):
        entry = entries.get(path)
        if entry is None:  # Deleted paths are permitted.
            continue
        if path in exceptions:
            continue
        oid, mode = entry
        if mode == 0o160000:  # Submodule gitlinks do not have a blob size.
            continue
        size_raw = git(repo, "cat-file", "-s", oid)
        size = int(size_raw.strip())
        reasons = []
        if size > limit:
            reasons.append(f"{size:,} bytes exceeds {limit:,}-byte limit")
        if generated_raw_path(path):
            reasons.append("generated .npy/.npz under docs/research_notes or results")
        if reasons:
            failures.append(f"{path}: " + "; ".join(reasons))
    return failures


def staged_check(repo: Path, limit: int) -> tuple[list[str], int]:
    exceptions = load_exceptions(repo)
    entries = staged_entries(repo)
    return inspect(repo, changed_staged_paths(repo), entries, limit, exceptions), len(entries)


def revision_check(repo: Path, base: str, head: str, limit: int) -> list[str]:
    head = head or "HEAD"
    exceptions = load_exceptions(repo, head)
    if not base or set(base) == {"0"}:
        base = EMPTY_TREE
    # A root commit has no parent; compare it with the empty tree.
    parents = git(repo, "rev-list", "--parents", "-n", "1", head).decode().split()
    if len(parents) == 1:
        base = EMPTY_TREE
    changed = git(repo, "diff", "--name-only", "--no-renames", "-z", base, head)
    paths = {p.decode("utf-8", errors="surrogateescape") for p in changed.split(b"\0") if p}
    entries: dict[str, tuple[str, int]] = {}
    tree = git(repo, "ls-tree", "-r", "-z", "--full-tree", head)
    for record in tree.split(b"\0"):
        if not record:
            continue
        metadata, path_bytes = record.split(b"\t", 1)
        mode, object_type, oid = metadata.decode("ascii").split()
        path = path_bytes.decode("utf-8", errors="surrogateescape")
        if object_type == "blob" and path in paths:
            entries[path] = (oid, int(mode, 8))
    return inspect(repo, paths, entries, limit, exceptions)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--base", help="base revision for CI changed-path checking")
    parser.add_argument("--head", default="HEAD", help="head revision for CI checking")
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    if args.max_bytes < 0:
        parser.error("--max-bytes must be nonnegative")
    try:
        if args.base is None:
            failures, count = staged_check(repo, args.max_bytes)
            scope = "staged changes"
        else:
            failures = revision_check(repo, args.base, args.head, args.max_bytes)
            count = None
            scope = f"changes from {args.base} to {args.head}"
    except GuardError as exc:
        print(f"artifact guard error: {exc}", file=sys.stderr)
        return 2
    if failures:
        print(f"Repository artifact guard rejected {scope}:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        print(
            f"Keep generated data locally, or add a narrowly scoped path and reason to {POLICY_PATH}.",
            file=sys.stderr,
        )
        return 1
    if count is not None:
        print(f"Repository artifact guard passed ({scope}; {count} index entries inspected).")
    else:
        print(f"Repository artifact guard passed ({scope}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
