from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_repository_artifacts.py"
POLICY = "docs/implementation/ARTIFACT_POLICY.json"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Artifact Guard Test")
    policy = repo / POLICY
    policy.parent.mkdir(parents=True)
    policy.write_text('{"version": 1, "exceptions": []}\n', encoding="utf-8")
    git(repo, "add", POLICY)
    git(repo, "commit", "-qm", "initial policy")
    return repo


def run_guard(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--repo", str(repo), *args],
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )


def test_rejects_staged_generated_npz(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    raw = repo / "docs/research_notes/run/kernels.npz"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"small but generated")
    git(repo, "add", str(raw.relative_to(repo)))

    result = run_guard(repo)

    assert result.returncode == 1
    assert "generated .npy/.npz" in result.stderr


def test_checks_index_blob_when_worktree_differs(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    path = repo / "docs/research_notes/run/large.json"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"x" * 32)
    git(repo, "add", str(path.relative_to(repo)))
    path.write_bytes(b"small")  # The staged blob remains 32 bytes.

    result = run_guard(repo, "--max-bytes", "16")

    assert result.returncode == 1
    assert "32 bytes exceeds 16-byte limit" in result.stderr


def test_allows_deleting_legacy_raw_artifact(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    path = repo / "results/legacy.npy"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"legacy")
    git(repo, "add", str(path.relative_to(repo)))
    git(repo, "commit", "-qm", "legacy artifact")
    path.unlink()
    git(repo, "add", "-u", "results/legacy.npy")

    result = run_guard(repo)

    assert result.returncode == 0, result.stderr


def test_ignores_unchanged_legacy_large_artifact(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    path = repo / "results/legacy.bin"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"x" * 32)
    git(repo, "add", str(path.relative_to(repo)))
    git(repo, "commit", "-qm", "legacy artifact")

    result = run_guard(repo, "--max-bytes", "16")

    assert result.returncode == 0, result.stderr


def test_allows_exact_path_exception_with_reason(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    policy = {"version": 1, "exceptions": [{
        "path": "docs/research_notes/reference/retained.npz",
        "reason": "Required source data for a published comparison.",
    }]}
    (repo / POLICY).write_text(json.dumps(policy) + "\n", encoding="utf-8")
    raw = repo / "docs/research_notes/reference/retained.npz"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"approved")
    git(repo, "add", POLICY, str(raw.relative_to(repo)))

    result = run_guard(repo)

    assert result.returncode == 0, result.stderr


def test_ci_mode_checks_root_commit_from_empty_tree(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    path = repo / "results/first.npy"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"initial commit data")
    git(repo, "add", str(path.relative_to(repo)))
    git(repo, "commit", "-qm", "first artifact")

    result = run_guard(repo, "--base", "0" * 40, "--head", "HEAD")

    assert result.returncode == 1
    assert "generated .npy/.npz" in result.stderr
