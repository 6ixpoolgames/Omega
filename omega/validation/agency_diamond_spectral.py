"""Validation entry point for the bounded agency-diamond spectral pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.agency_diamond.run_spectral import run_spectral
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run bounded finite agency-diamond spectral validation."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/agency_diamond_spectral"),
    )
    parser.add_argument("--horizon", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_agency_diamond_spectral(
        out_root=args.out_root,
        horizon=args.horizon,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def run_agency_diamond_spectral(
    *,
    out_root: Path = Path(".tmp/agency_diamond_spectral"),
    horizon: int = 3,
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return run_spectral(run_root, horizon=horizon)


if __name__ == "__main__":
    main()
