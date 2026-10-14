"""Physical moment calibration followed by prospective scientific freeze."""
import argparse
import json
import sys
import uuid
from datetime import UTC, datetime
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.aversive_signals import SignalParameters
from omega_v2.testbed.exploration import ExplorationParameters
from omega_v2.testbed.paid_sensing import SensorParameters
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle, verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen

BASE = 'docs/research_notes/lushness_testbed/paid_sensing'
DOC = ROOT/BASE
PLAN, REG, SPEC = BASE+'/MATCHING_PLAN.json', BASE+'/PROTOCOL.json', BASE+'/SPEC.md'


def files(extra):
    return ([p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
            + ['omega_v2/__init__.py', 'scripts/run_bng_binding_calibration.py',
               'scripts/run_paid_sensing.py', SPEC, *extra])


def output(mode):
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    return ROOT/'results/local_runs/lushness_testbed/paid_sensing'/(mode+'-'+stamp)


def calibration():
    if (ROOT/PLAN).exists():
        raise FileExistsError('Physical matching plan already frozen')
    groups = []
    for i, (cost, contrast, refresh) in enumerate(product((.5, 1.), (0., .8), (.2, .8))):
        groups.append({'id': f'S-{i:02}', 'physiology': vars(SignalParameters(signal_upkeep=.02, struggle_cost=.5)),
                       'parameters': vars(ExplorationParameters(movement_cost=cost, contrast=contrast, coupling=0.)),
                       'sensor': vars(SensorParameters(refresh_rate=refresh)),
                       'roots': [[8, 1, 0, 1, 1, 0], [8, 1, 0, 1, 0, 1]]})
    plan = {'status': 'frozen_before_physical_moment_calibration', 'date': '2026-10-14',
            'groups': groups, 'horizon': 64., 'relative_tolerance': 1e-6,
            'entropy_used': False, 'targets': ['pooled_signal_time', 'pooled_activation_count'],
            'caps': {'seconds': 120, 'memory': 512*1024**2, 'output_cap': 64*1024**2}}
    atomic_json(ROOT/PLAN, plan)
    out = output('calibration')
    freeze_bundle(ROOT, out, files([PLAN, 'scripts/paid_sensor_calibration_worker.py']),
                  {'mode': 'physical_calibration', 'plan': plan})
    execution = run_frozen(out, 'scripts/paid_sensor_calibration_worker.py', [str(out)], plan['caps'])
    atomic_json(out/'PROFILE.json', execution)
    success = execution['exit_code'] == 0 and not execution['cap_reason']
    if success:
        result = json.loads((out/'MATCHING_RESULTS.json').read_text(encoding='utf-8'))
        atomic_json(DOC/'MATCHING_RESULTS.json', result)
        success = result['status'] == 'complete'
    atomic_json(DOC/'CALIBRATION_STATUS.json',
                {'status': 'complete' if success else 'incomplete', 'run': str(out), 'profile': execution})
    print(json.dumps({'run': str(out), **execution}, indent=2))
    return 0 if success else 1


def prepare():
    if (ROOT/REG).exists():
        raise FileExistsError('Scientific protocol already frozen')
    gate = json.loads((DOC/'CALIBRATION_STATUS.json').read_text(encoding='utf-8'))
    matching = json.loads((DOC/'MATCHING_RESULTS.json').read_text(encoding='utf-8'))
    if gate['status'] != 'complete' or matching['input_hash'] != verify_bundle(gate['run'])['input_hash']:
        raise RuntimeError('Verified complete physical matching required')
    cases = []
    for group in matching['plan']['groups']:
        fit = next(v for v in matching['fits'] if v['group'] == group['id'])
        if not fit['success']:
            raise RuntimeError('Physical matching failed')
        for root_id, root in enumerate(group['roots']):
            cases.append({'id': f"{group['id']}-r{root_id}", 'group': group['id'], 'root': root,
                          'physiology': group['physiology'], 'parameters': group['parameters'],
                          'sensor': {**group['sensor'], 'noise_on': fit['noise_on'], 'noise_retain': fit['noise_retain']}})
    protocol = {'id': 'paid-stock-information-first-slice', 'version': '1', 'date': '2026-10-14',
        'status': 'frozen_before_scientific_ranking', 'cases': cases, 'matching': matching,
        'arms': ['R0', 'I0', 'RX', 'IX'], 'coupling': 4.,
        'pairs': [['IX', 'RX'], ['I0', 'R0'], ['IX', 'I0'], ['RX', 'R0']],
        'horizons': [16, 64, 256], 'cadences': [.125, .25, .5],
        'primary_horizon': 64, 'primary_cadence': .25,
        'coordinate_order': [3, 4, 5, 0, 1, 2], 'hidden_fields': [0, 1, 3, 4, 5],
        'temporal_reference': 1., 'physical_temporal_band': None,
        'predictions': {
            'T1': 'cheap/highcontrast/slow refresh pooled roots: IX-RX positive breadth AND food',
            'T2': 'same regime: (IX-I0)-(RX-R0) positive breadth AND food',
            'T3': 'faster refresh reduces IX-RX pooled primary breadth there'},
        'tolerances': {'bits': 1e-5, 'readout': 1e-6, 'residual': 1e-8},
        'objective': 'complete finite conditional sampled-history lushness; randomness counts',
        'scope': 'matched-unit-cost sensing and access; not sustained generativity',
        'smoke_case': 'S-03-r1',
        'caps': {'seconds': 600, 'memory': 512*1024**2, 'output_cap': 64*1024**2}}
    atomic_json(ROOT/REG, protocol)
    print(ROOT/REG)


def run(mode):
    p = json.loads((ROOT/REG).read_text(encoding='utf-8'))
    if p['status'] != 'frozen_before_scientific_ranking':
        raise ValueError('Frozen scientific protocol required')
    if mode == 'science':
        gate = json.loads((DOC/'SMOKE_STATUS.json').read_text(encoding='utf-8'))
        if gate['status'] != 'complete' or verify_bundle(gate['run'])['config']['protocol'] != p:
            raise RuntimeError('Source-identical smoke required')
    out = output(mode)
    manifest = freeze_bundle(ROOT, out, files([REG, 'scripts/paid_sensing_worker.py']), {'mode': mode, 'protocol': p})
    if mode == 'science' and manifest['source_hash'] != verify_bundle(gate['run'])['source_hash']:
        raise RuntimeError('Source differs from smoke')
    execution = run_frozen(out, 'scripts/paid_sensing_worker.py', [str(out), mode],
                          {**p['caps'], 'seconds': 120 if mode == 'smoke' else 600})
    atomic_json(out/'PROFILE.json', execution)
    success = execution['exit_code'] == 0 and not execution['cap_reason']
    atomic_json(DOC/f'{mode.upper()}_STATUS.json',
                {'status': 'complete' if success else 'incomplete', 'run': str(out), 'profile': execution})
    print(json.dumps({'run': str(out), **execution}, indent=2))
    return 0 if success else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('calibrate', 'prepare', 'smoke', 'science'))
    args = parser.parse_args()
    raise SystemExit(calibration() if args.mode == 'calibrate' else prepare() if args.mode == 'prepare' else run(args.mode))
