"""Validation entry point for the operational-causal-diamond midscale pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.agency_diamond.run_midscale import run_midscale
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the agency diamond midscale validation."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/agency_diamond_midscale"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_agency_diamond_midscale(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_agency_diamond_midscale(
    *,
    out_root: Path = Path(".tmp/agency_diamond_midscale"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return run_midscale(run_root)


if __name__ == "__main__":
    main()
