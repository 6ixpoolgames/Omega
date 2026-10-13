"""Freeze then hard-cap one maintained-resource smoke or science run."""
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

CONFIG = "docs/research_notes/lushness_testbed/maintained_resource/PROTOCOL.json"
SOURCES = [
    "scripts/run_bng_binding_calibration.py",
    "scripts/maintained_resource_worker.py",
    "omega_v2/__init__.py",
    "omega_v2/testbed/__init__.py",
    "omega_v2/testbed/contracts.py",
    "omega_v2/testbed/compiler.py",
    "omega_v2/testbed/maintained_resource.py",
    "omega_v2/testbed/workflow/__init__.py",
    "omega_v2/testbed/workflow/manifest.py",
    "omega_v2/testbed/workflow/runner.py",
    CONFIG,
]
CAPS = {"seconds": 120, "memory": 1024**3, "output_cap": 256 * 1024**2}


def main(mode: str) -> int:
    if mode not in ("smoke", "science"):
        raise ValueError("mode must be smoke or science")
    config = json.loads((ROOT / CONFIG).read_text(encoding="utf-8"))
    required = "draft_engineering_gate" if mode == "smoke" else "frozen_before_scientific_ranking"
    if config.get("status") != required:
        raise RuntimeError(f"{mode} requires protocol status {required!r}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    out = ROOT / "results/local_runs/lushness_testbed/maintained_resource" / f"{mode}-{stamp}"
    out.mkdir(parents=True)
    manifest = freeze_bundle(ROOT, out, SOURCES,
                             {"mode": mode, "caps": CAPS,
                              "protocol_status": required})
    profile = run_frozen(out, "scripts/maintained_resource_worker.py",
                         args=[str(out), mode], caps=CAPS)
    (out / "PROFILE.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    if profile.get("exit_code") != 0 or profile.get("cap_reason") is not None:
        (out / "status.json").write_text(json.dumps({"status": "incomplete",
            "exit_code": profile.get("exit_code"), "cap_reason": profile.get("cap_reason")}, indent=2) + "\n")
    artifacts = []
    for path in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "artifacts.json"):
        artifacts.append({"path": path.relative_to(out).as_posix(), "bytes": path.stat().st_size,
                          "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (out / "artifacts.json").write_text(json.dumps({"schema_version": "omega-artifacts/1",
        "input_hash": manifest["input_hash"], "files": artifacts}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out), "input_hash": manifest["input_hash"], **profile}, indent=2), flush=True)
    return int(profile["exit_code"]) if profile.get("exit_code") is not None else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: run_maintained_resource.py smoke|science")
    raise SystemExit(main(sys.argv[1]))
