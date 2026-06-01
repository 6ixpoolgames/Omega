from __future__ import annotations

import csv
import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from omega.rfs_mb0_future_landscape.substrate import State


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def state_id(state: State) -> str:
    return "(" + ",".join(str(part) for part in state) + ")"


def stable_hash(value: object, length: int = 16) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:length]


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def safe_token(value: object) -> str:
    token = "".join(char if char.isalnum() else "_" for char in str(value))
    return token.strip("_") or "empty"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]], *, gzip_compresslevel: int = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        with open_text(path, "wt", gzip_compresslevel=gzip_compresslevel) as handle:
            handle.write("empty\n")
        return
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with open_text(path, "wt", gzip_compresslevel=gzip_compresslevel) as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        writer.writerows(([row.get(field, "") for field in fields] for row in rows))


def read_csv(path: Path) -> list[dict[str, object]]:
    if not path.exists() or not is_csv_path(path):
        return []
    with open_text(path, "rt") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames == ["empty"]:
            return []
        return [dict(row) for row in reader]


def csv_row_count(path: Path) -> int:
    if not path.exists() or not is_csv_path(path):
        return 0
    opener = gzip.open if is_gzip_path(path) else open
    with opener(path, "rt", newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return 0
        if header == ["empty"]:
            return 0
        return sum(1 for _row in reader)


def is_csv_path(path: Path) -> bool:
    suffixes = [suffix.lower() for suffix in path.suffixes]
    return suffixes[-1:] == [".csv"] or suffixes[-2:] == [".csv", ".gz"]


def is_gzip_path(path: Path) -> bool:
    suffixes = [suffix.lower() for suffix in path.suffixes]
    return suffixes[-2:] == [".csv", ".gz"]


def open_text(path: Path, mode: str, *, gzip_compresslevel: int = 1):
    if is_gzip_path(path):
        return gzip.open(
            path,
            mode,
            newline="",
            encoding="utf-8",
            compresslevel=max(1, min(9, int(gzip_compresslevel))),
        )
    return open(path, mode, newline="", encoding="utf-8")


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def entropy_from_weights(values: list[float]) -> float:
    import math

    total = sum(values)
    if total <= 0:
        return 0.0
    entropy = 0.0
    for value in values:
        if value <= 0:
            continue
        probability = value / total
        entropy -= probability * math.log2(probability)
    return entropy
