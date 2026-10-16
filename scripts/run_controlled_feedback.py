"""Freeze and cap the first oracle evaluator over costed feedback controllers."""
import argparse
import json
import sys
import uuid
from datetime import UTC, datetime
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.resource_feedback import DEFAULT_PARAMETERS
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle, verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen

DOC = ROOT/'docs/research_notes/lushness_testbed/controlled_feedback'
REG = 'docs/research_notes/lushness_testbed/controlled_feedback/PROTOCOL.json'


def prepare():
    if (ROOT/REG).exists():
        raise FileExistsError('Frozen registration cannot be overwritten')
    responses = {'idle': (0.,0.), 'service': (1.,0.), 'mix25': (.75,.25),
                 'mix50': (.5,.5), 'mix75': (.25,.75), 'use': (0.,1.)}
    base = dict(vars(DEFAULT_PARAMETERS))
    base['rates'] = dict(base['rates'])
    base['feedback'] = 'basal_catalytic'
    cases = []
    for capacity in (1,2):
        policies = [{'id': '-'.join(names), 'responses': [(0.,0.), *(responses[name] for name in names)]}
                    for names in product(responses, repeat=capacity)]
        for cadence in (.125,.25,.5):
            cases.append({'capacity': capacity, 'cadence': cadence, 'policies': policies,
                          'parameters': {**base, 'apparatus_capacity': capacity, 'carrier_capacity': capacity}})
    atomic_json(ROOT/REG, {'status': 'frozen_before_scientific_ranking', 'cases': cases,
                          'horizons': [1,4,16,64,256], 'rank_root': [1,1,0,0],
                          'deadline': 64, 'switch': .015, 'relaxation': .003,
                          'rank_tolerance': 1e-8,
                          'primary': 'complete conditional sampled-history bits at each horizon',
                          'primary_capacity': 2, 'primary_cadence': .25,
                          'method': 'oracle evaluator, restricted stationary apparatus-count controllers; no receding horizon or uncertainty',
                          'predictions': {'O1': 'At least one primary horizon winner differs from T1',
                                          'O2': 'State-dependent policy strictly beats all constant controls at T64, primary capacity/cadence'},
                          'adverse': {'S1': 'Positive-negative primary winner lead over best constant at T64 across cadences',
                                      'M1': 'Winner maintains fewer apparatus than maximal-stock control at T64'},
                          'caps': {'seconds': 120, 'memory': 1024**3, 'output_cap': 32*1024**2}})
    print(ROOT/REG)


def run(mode):
    protocol = json.loads((ROOT/REG).read_text())
    if mode == 'science':
        gate = json.loads((DOC/'SMOKE_STATUS.json').read_text())
        if gate['status'] != 'complete':
            raise RuntimeError('Engineering gate required')
        if verify_bundle(gate['run'])['config']['protocol'] != protocol:
            raise RuntimeError('Engineering gate used a different protocol')
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out = ROOT/'results/local_runs/lushness_testbed/controlled_feedback'/(mode+'-'+stamp)
    files = [p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
    files += ['omega_v2/__init__.py', REG, 'scripts/run_bng_binding_calibration.py',
              'scripts/run_controlled_feedback.py','scripts/controlled_feedback_worker.py']
    freeze_bundle(ROOT, out, files, {'mode': mode, 'protocol': protocol})
    execution = run_frozen(out, 'scripts/controlled_feedback_worker.py', [str(out), mode], protocol['caps'])
    atomic_json(out/'PROFILE.json', execution)
    atomic_json(DOC/(mode.upper()+'_STATUS.json'), {'status': 'complete' if execution['exit_code'] == 0
                and not execution['cap_reason'] else 'incomplete', 'run': str(out), 'profile': execution})
    print(json.dumps({'run': str(out), **execution}))
    return execution['exit_code']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('prepare','smoke','science'))
    args = parser.parse_args()
    raise SystemExit(prepare() if args.mode == 'prepare' else run(args.mode))
