"""Freeze and execute only the capped locked-resource engineering smoke."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow import freeze_bundle
from omega_v2.testbed.workflow.runner import run_frozen


SOURCES = [
    "scripts/run_bng_binding_calibration.py",
    "scripts/locked_resource_smoke_worker.py",
    "omega_v2/__init__.py",
    "omega_v2/testbed/__init__.py",
    "omega_v2/testbed/contracts.py",
    "omega_v2/testbed/compiler.py",
    "omega_v2/testbed/locked_resource.py",
    "omega_v2/testbed/workflow/__init__.py",
    "omega_v2/testbed/workflow/manifest.py",
    "omega_v2/testbed/workflow/runner.py",
]
CAPS = {"seconds": 120, "memory": 1024**3, "output_cap": 256 * 1024**2}


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    out = ROOT / "results/local_runs/lushness_testbed/locked-resource" / stamp
    out.mkdir(parents=True)
    config = {"run": "engineering-smoke-only", "scientific_ranking": False,
              "state_cap": 32, "caps": CAPS}
    manifest = freeze_bundle(ROOT, out, SOURCES, config)
    profile = run_frozen(out, "scripts/locked_resource_smoke_worker.py",
                         args=[str(out)], caps=CAPS)
    (out / "PROFILE.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    records = []
    for path in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "artifacts.json"):
        records.append({"path": path.relative_to(out).as_posix(), "bytes": path.stat().st_size,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (out / "artifacts.json").write_text(json.dumps({
        "schema_version": "omega-artifacts/1", "input_hash": manifest["input_hash"],
        "files": records,
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out), **profile}, indent=2), flush=True)
    return int(profile["exit_code"]) if profile.get("exit_code") is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
