"""Validation entry point for Agency Diamond Blind Discovery v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.agency_diamond.run_blind_discovery import run_blind_discovery
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Agency Diamond Blind Discovery v1.")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/agency_diamond_blind_discovery"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_agency_diamond_blind_discovery(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_agency_diamond_blind_discovery(
    *,
    out_root: Path = Path(".tmp/agency_diamond_blind_discovery"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return run_blind_discovery(run_root)


if __name__ == "__main__":
    main()
