"""Validation entry point for Agency Diamond Stochastic Exploration v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.agency_diamond.run_stochastic_exploration import run_stochastic_exploration
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Agency Diamond Stochastic Exploration v1."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/agency_diamond_stochastic_exploration"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_agency_diamond_stochastic_exploration(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_agency_diamond_stochastic_exploration(
    *,
    out_root: Path = Path(".tmp/agency_diamond_stochastic_exploration"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return run_stochastic_exploration(run_root)


if __name__ == "__main__":
    main()
