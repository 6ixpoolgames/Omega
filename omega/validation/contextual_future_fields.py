"""Validation entry point for finite contextual future-field witnesses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.contextual_future_fields.run_witnesses import run_contextual_future_fields
from omega.validation._common import timestamped_run_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run finite contextual future-field witnesses."
    )
    parser.add_argument(
        "--out-root",
        type=Path,
        default=Path(".tmp/contextual_future_fields"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_contextual_future_fields_validation(out_root=args.out_root)
    print(json.dumps(result, indent=2, sort_keys=True))


def run_contextual_future_fields_validation(
    *,
    out_root: Path = Path(".tmp/contextual_future_fields"),
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    return run_contextual_future_fields(run_root)


if __name__ == "__main__":
    main()
