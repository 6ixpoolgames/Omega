"""Small standard-library artifact helpers."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Mapping


def timestamped_output_dir(root: Path) -> Path:
    path = root / datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    retained = list(rows)
    if not retained:
        raise ValueError(f"cannot write empty CSV artifact: {path}")
    fieldnames = tuple(retained[0])
    if any(tuple(row) != fieldnames for row in retained):
        raise ValueError("CSV rows must have identical ordered fields")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(retained)
