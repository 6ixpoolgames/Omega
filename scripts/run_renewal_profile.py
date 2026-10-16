"""Engineering-only capped profile; no policy ranking is exposed."""
import json
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle
from omega_v2.testbed.workflow.runner import run_frozen

if __name__ == '__main__':
    out = ROOT/'results/local_runs/lushness_testbed/renewal'/('profile-'+datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6])
    config = {'mode': 'engineering_only', 'capacities': [1, 2], 'cadence': .25,
              'horizons': [16, 64, 256, 1024], 'parameters': 'default frozen in source',
              'caps': {'seconds': 120, 'memory': 512*1024**2, 'output_cap': 64*1024**2}}
    sources = ([p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
               + ['omega_v2/__init__.py', 'scripts/run_bng_binding_calibration.py',
                  'scripts/run_renewal_profile.py', 'scripts/renewal_profile_worker.py'])
    freeze_bundle(ROOT, out, sources, config)
    execution = run_frozen(out, 'scripts/renewal_profile_worker.py', [str(out)], config['caps'])
    atomic_json(out/'PROFILE.json', execution)
    doc = ROOT/'docs/research_notes/lushness_testbed/renewal'
    success = execution['exit_code'] == 0 and not execution['cap_reason']
    atomic_json(doc/'ENGINEERING_STATUS.json', {'status': 'complete' if success else 'incomplete',
                'run': str(out), 'profile': execution})
    if success:
        atomic_json(doc/'ENGINEERING_PROFILE.json', json.loads((out/'RESULTS.json').read_text(encoding='utf-8')))
    print(json.dumps({'run': str(out), **execution}, indent=2))
    raise SystemExit(0 if success else 1)
