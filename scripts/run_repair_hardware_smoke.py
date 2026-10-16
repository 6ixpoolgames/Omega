"""Hard-capped frozen-source smoke for the damage consequence module."""
import argparse
import json
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow import freeze_bundle
from omega_v2.testbed.workflow.runner import run_frozen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exact', action='store_true')
    args = parser.parse_args()
    sources = [p.relative_to(ROOT).as_posix()
               for p in (ROOT / "omega_v2/testbed").rglob("*.py")]
    sources += ["omega_v2/__init__.py", "scripts/run_bng_binding_calibration.py",
                "scripts/repair_hardware_smoke_worker.py", "scripts/run_repair_hardware_smoke.py",
                "docs/research_notes/lushness_testbed/structural_harm/PROTOCOL_DRAFT.json"]
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    out = ROOT / "results/local_runs/lushness_testbed/structural_harm" / ("smoke-"+stamp)
    caps = {"seconds": 120, "memory": 1024**3, "output_cap": 32*1024**2}
    freeze_bundle(ROOT, out, sources, {"mode": "engineering_only", "caps": caps,
                                     "exact_entropy_feasibility": args.exact})
    worker_args = [str(out)] + (["exact"] if args.exact else [])
    profile = run_frozen(out, "scripts/repair_hardware_smoke_worker.py", worker_args, caps)
    (out / "PROFILE.json").write_text(json.dumps(profile, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(dict(out=str(out), **profile), indent=2))
    return 0 if profile.get("exit_code") == 0 and not profile.get("cap_reason") else 1


if __name__ == "__main__":
    raise SystemExit(main())
