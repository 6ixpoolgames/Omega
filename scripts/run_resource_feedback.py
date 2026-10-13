"""Capped, frozen engineering gate and first bounded feedback comparison."""
import argparse
import hashlib
import json
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.resource_feedback import DEFAULT_PARAMETERS
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle
from omega_v2.testbed.workflow.runner import run_frozen

DOC = ROOT / 'docs/research_notes/lushness_testbed/resource_feedback'
REG = 'docs/research_notes/lushness_testbed/resource_feedback/PROTOCOL.json'


def prepare():
    path = ROOT / REG
    if path.exists():
        raise FileExistsError('Registration cannot be overwritten')
    base = dict(vars(DEFAULT_PARAMETERS))
    base['rates'] = dict(base['rates'])
    cases = []
    for capacity in (1, 2):
        for inflow in (True, False):
            for feedback in ('catalytic', 'uncatalytic', 'absent'):
                for cadence in (.125, .25, .5):
                    cases.append({'parameters': {**base, 'apparatus_capacity': capacity,
                                                 'carrier_capacity': capacity,
                                                 'inflow_enabled': inflow, 'feedback': feedback},
                                  'cadence': cadence})
    atomic_json(path, {'status': 'frozen_before_scientific_ranking', 'cases': cases,
                      'horizons': [1, 4, 16, 64, 256], 'primary_cadence': .25,
                      'primary_capacity': 1,
                      'predictions': {
                          'F1': 'Driven catalytic minus absent rate is positive at every cadence, primary capacity1',
                          'F2': 'Driven catalytic stationary apparatus and recovery endpoint64 exceed absent at capacity1',
                          'F3': 'Driven catalytic stationary net feedback fuel flow is positive',
                          'D1': 'Without resource inflow, catalytic/uncatalytic/absent rates agree after depletion at each capacity/cadence'},
                      'controls': 'uncatalytic feedback is a mechanism control, not an activity-matched law',
                      'scope': 'bounded self-maintenance and growth to two; no optimizer/ethical/open-ended claim',
                      'caps': {'seconds': 120, 'memory': 1024**3, 'output_cap': 32*1024**2}})
    print(json.dumps({'registration': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}))


def run(mode):
    config = json.loads((ROOT/REG).read_text(encoding='utf-8'))
    if mode == 'science':
        gate = json.loads((DOC/'SMOKE_STATUS.json').read_text(encoding='utf-8'))
        if gate['status'] != 'complete' or gate['protocol_hash'] != hashlib.sha256((ROOT/REG).read_bytes()).hexdigest():
            raise RuntimeError('Matching engineering gate required')
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out = ROOT/'results/local_runs/lushness_testbed/resource_feedback'/(mode+'-'+stamp)
    files = [p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
    files += ['omega_v2/__init__.py', REG, 'scripts/run_bng_binding_calibration.py',
              'scripts/run_resource_feedback.py', 'scripts/resource_feedback_worker.py']
    freeze_bundle(ROOT, out, files, {'protocol': config, 'mode': mode})
    execution = run_frozen(out, 'scripts/resource_feedback_worker.py', [str(out), mode], config['caps'])
    atomic_json(out/'PROFILE.json', execution)
    complete = execution.get('exit_code') == 0 and not execution.get('cap_reason')
    atomic_json(DOC/(mode.upper()+'_STATUS.json'), {'status': 'complete' if complete else 'incomplete',
                'run': str(out), 'profile': execution,
                'protocol_hash': hashlib.sha256((ROOT/REG).read_bytes()).hexdigest()})
    print(json.dumps({'run': str(out), **execution}))
    return 0 if complete else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('prepare', 'smoke', 'science'))
    parser.add_argument('--protocol', type=Path)
    args = parser.parse_args()
    if args.protocol is not None:
        selected = args.protocol.resolve(strict=True)
        REG = selected.relative_to(ROOT).as_posix()
        DOC = selected.parent
    raise SystemExit(prepare() if args.mode == 'prepare' else run(args.mode))
