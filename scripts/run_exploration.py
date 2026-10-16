"""Prospectively frozen, capped finite register-to-exploration comparison."""
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
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle, verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen

BASE = 'docs/research_notes/lushness_testbed/exploration'
DOC = ROOT/BASE
REG, SPEC = BASE+'/PROTOCOL.json', BASE+'/SPEC.md'


def prepare():
    if (ROOT/REG).exists():
        raise FileExistsError('Scientific registration already frozen')
    physiology = vars(SignalParameters(signal_upkeep=.02, struggle_cost=.5))
    cases = []
    for i, (cost, contrast, coupling, stocks) in enumerate(product((.5, 1.), (0., .8), (1., 4.), ((1, 0), (0, 1)))):
        cases.append({'id': f'BX-{i:02}', 'root': [8, 1, 0, 1, *stocks],
                      'physiology': physiology,
                      'parameters': {'movement_cost': cost, 'contrast': contrast, 'coupling': coupling,
                                     'supply_rate': .6, 'decay': .1, 'mobility': .1,
                                     'flicker_on': .05871485218977088, 'flicker_off': .36126583291983255}})
    protocol = {'id': 'costed-exploration-first-slice', 'version': '1', 'date': '2026-10-14',
        'status': 'frozen_before_scientific_ranking', 'cases': cases,
        'arms': ['B', 'B_R', 'B_X', 'M_C', 'S_A'],
        'pairs': [['B_R', 'B'], ['B_X', 'B_R'], ['B_X', 'M_C'], ['S_A', 'B_R'], ['S_A', 'B_X']],
        'horizons': [16, 64, 256], 'cadences': [.125, .25, .5],
        'primary_horizon': 64, 'primary_cadence': .25,
        'objective': 'complete conditional sampled-history entropy; native randomness counts',
        'coordinate_order': [3, 4, 5, 0, 1, 2], 'hidden_fields': [0, 1, 3, 4, 5],
        'temporal_reference': 1., 'physical_temporal_band': None,
        'predictions': {
            'X1': 'at cost0.5/contrast0.8/coupling4 pooled two roots: B_X-B_R breadth and food both positive',
            'X2': 'same pooled regime: S_A-B_R captured food positive',
            'X3': 'cost1 reduces pooled B_X-B_R breadth versus cost0.5 at every contrast/coupling'},
        'hits': ['breadth gain without resource/lifetime improvement', 'cadence sign reversal',
                 'functional access gain with nonpositive breadth'],
        'tolerances': {'bits': 1e-5, 'readout': 1e-6, 'residual': 1e-8},
        'scope': 'finite mortality and costed access; not compounding, valence or ethical proof',
        'smoke_case': 'BX-06',
        'caps': {'seconds': 600, 'memory': 512*1024**2, 'output_cap': 64*1024**2}}
    atomic_json(ROOT/REG, protocol)
    print(ROOT/REG)


def run(mode):
    protocol = json.loads((ROOT/REG).read_text(encoding='utf-8'))
    if protocol['status'] != 'frozen_before_scientific_ranking':
        raise ValueError('Frozen scientific registration required')
    if mode == 'science':
        gate = json.loads((DOC/'SMOKE_STATUS.json').read_text(encoding='utf-8'))
        if gate['status'] != 'complete' or verify_bundle(gate['run'])['config']['protocol'] != protocol:
            raise RuntimeError('Source-identical smoke required')
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out = ROOT/'results/local_runs/lushness_testbed/exploration'/(mode+'-'+stamp)
    files = ([p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
             + ['omega_v2/__init__.py', 'scripts/run_bng_binding_calibration.py',
                'scripts/run_exploration.py', 'scripts/exploration_worker.py', REG, SPEC])
    frozen = freeze_bundle(ROOT, out, files, {'mode': mode, 'protocol': protocol})
    if mode == 'science' and frozen['source_hash'] != verify_bundle(gate['run'])['source_hash']:
        raise RuntimeError('Source differs from smoke')
    execution = run_frozen(out, 'scripts/exploration_worker.py', [str(out), mode],
                          {**protocol['caps'], 'seconds': 120 if mode == 'smoke' else 600})
    atomic_json(out/'PROFILE.json', execution)
    success = execution['exit_code'] == 0 and not execution['cap_reason']
    atomic_json(DOC/f'{mode.upper()}_STATUS.json',
                {'status': 'complete' if success else 'incomplete', 'run': str(out), 'profile': execution})
    print(json.dumps({'run': str(out), **execution}, indent=2))
    return 0 if success else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('prepare', 'smoke', 'science'))
    args = parser.parse_args()
    raise SystemExit(prepare() if args.mode == 'prepare' else run(args.mode))
