"""Snapshot and hard-cap the engineering W1/W2 smoke. No scientific ranking."""
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
    sources = [p.relative_to(ROOT).as_posix()
               for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
    sources += ['omega_v2/__init__.py', 'scripts/aversive_signal_smoke_worker.py',
                'scripts/run_bng_binding_calibration.py',
                'scripts/run_aversive_signal_smoke.py',
                'docs/research_notes/lushness_testbed/aversive_signals/PROTOCOL_DRAFT.json']
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out = ROOT/'results/local_runs/lushness_testbed/aversive_signals'/('smoke-'+stamp)
    caps = {'seconds': 90, 'memory': 512*1024**2, 'output_cap': 8*1024**2}
    freeze_bundle(ROOT, out, sources, {'mode': 'engineering_only', 'caps': caps})
    profile = run_frozen(out, 'scripts/aversive_signal_smoke_worker.py', [str(out)], caps)
    (out/'PROFILE.json').write_text(json.dumps(profile, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'out': str(out), **profile}, indent=2))
    return 0 if profile.get('exit_code') == 0 and not profile.get('cap_reason') else 1


if __name__ == '__main__':
    raise SystemExit(main())
