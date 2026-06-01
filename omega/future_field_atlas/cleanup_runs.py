"""Age-based cleanup utility for local Future Field Atlas run outputs."""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROMOTION_MARKERS = ("PROMOTED", ".promoted", "RETAIN", ".retain", "KEEP", ".keep")


@dataclass(frozen=True)
class CleanupCandidate:
    path: Path
    age_days: float
    size_mb: float
    reason: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean local Future Field Atlas run outputs by age.")
    parser.add_argument("--root", type=Path, default=Path("results/future_field_atlas"))
    parser.add_argument("--older-than-days", type=float, default=3.0)
    parser.add_argument("--match", type=str, default="", help="Optional substring filter for run directory names.")
    parser.add_argument("--include-promoted", action="store_true", help="Allow deletion of directories with retain markers.")
    parser.add_argument("--delete", action="store_true", help="Actually delete candidates. Default is dry-run.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    workspace = Path.cwd().resolve()
    if not root.exists():
        print(f"root_missing\t{root}")
        return
    if not root.is_dir():
        raise NotADirectoryError(root)
    if not is_relative_to(root, workspace):
        raise ValueError(f"refusing to clean outside workspace: {root}")
    candidates = cleanup_candidates(
        root=root,
        older_than_days=float(args.older_than_days),
        name_match=str(args.match or ""),
        include_promoted=bool(args.include_promoted),
    )
    action = "DELETE" if args.delete else "DRY_RUN"
    print(f"action\t{action}")
    print(f"root\t{root}")
    print(f"candidate_count\t{len(candidates)}")
    print("age_days\tsize_mb\treason\tpath")
    for candidate in candidates:
        print(
            f"{candidate.age_days:.2f}\t"
            f"{candidate.size_mb:.3f}\t"
            f"{candidate.reason}\t"
            f"{candidate.path}"
        )
    if args.delete:
        for candidate in candidates:
            if not is_relative_to(candidate.path.resolve(), root):
                raise ValueError(f"refusing to delete outside cleanup root: {candidate.path}")
            shutil.rmtree(candidate.path)


def cleanup_candidates(
    *,
    root: Path,
    older_than_days: float,
    name_match: str,
    include_promoted: bool,
) -> list[CleanupCandidate]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=max(0.0, older_than_days))
    candidates: list[CleanupCandidate] = []
    for path in sorted(item for item in root.iterdir() if item.is_dir()):
        if name_match and name_match not in path.name:
            continue
        if not include_promoted and has_promotion_marker(path):
            continue
        modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        if modified > cutoff:
            continue
        age_days = (datetime.now(timezone.utc) - modified).total_seconds() / 86400.0
        candidates.append(
            CleanupCandidate(
                path=path,
                age_days=age_days,
                size_mb=directory_size_mb(path),
                reason=f"older_than_{older_than_days:g}_days",
            )
        )
    return candidates


def has_promotion_marker(path: Path) -> bool:
    return any((path / marker).exists() for marker in PROMOTION_MARKERS)


def directory_size_mb(path: Path) -> float:
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            total += item.stat().st_size
    return total / (1024 * 1024)


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


if __name__ == "__main__":
    main()
