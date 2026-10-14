"""Separate physical calibration, prospective registration and capped science."""
import argparse
import json
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle, verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen

DOC = ROOT/'docs/research_notes/lushness_testbed/aversive_signals'
REG = 'docs/research_notes/lushness_testbed/aversive_signals/REGISTER_CONTROL_PROTOCOL.json'
PLAN = 'docs/research_notes/lushness_testbed/aversive_signals/REGISTER_MATCHING_PLAN.json'
SPEC = 'docs/research_notes/lushness_testbed/aversive_signals/REGISTER_CONTROL_SPEC.md'


def _files(extra):
    return ([p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
            +['omega_v2/__init__.py', 'scripts/run_bng_binding_calibration.py',
              'scripts/run_register_controls.py', SPEC, *extra])


def _out(mode):
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    return ROOT/'results/local_runs/lushness_testbed/aversive_signals'/(f'register-{mode}-'+stamp)


def calibration():
    if (ROOT/PLAN).exists():
        raise FileExistsError('Physical matching plan already frozen')
    prior = json.loads((DOC/'FIRST_BATCH_PROTOCOL.json').read_text(encoding='utf-8'))
    parents = [case for case in prior['cases'] if case['id'] in ('W1-00', 'W1-08')]
    plan = {'status': 'frozen_before_physical_matching', 'parents': parents,
            'selection': 'known first-batch counterexamples, explanatory follow-up',
            'horizon': 64., 'relative_tolerance': 1e-6,
            'targets': ['signal_occupancy_time', 'physical_signal_switch_count'],
            'fit_uses_entropy': False,
            'caps': {'seconds': 120, 'memory': 512*1024**2, 'output_cap': 16*1024**2}}
    atomic_json(ROOT/PLAN, plan)
    out = _out('calibration')
    freeze_bundle(ROOT, out, _files([PLAN, 'scripts/register_control_calibration_worker.py']),
                  {'mode': 'physical_matching', 'plan': plan})
    execution = run_frozen(out, 'scripts/register_control_calibration_worker.py', [str(out)], plan['caps'])
    atomic_json(out/'PROFILE.json', execution)
    success = execution['exit_code'] == 0 and not execution['cap_reason']
    if success:
        result = json.loads((out/'MATCHING_RESULTS.json').read_text(encoding='utf-8'))
        success = result['status'] == 'complete'
        atomic_json(DOC/'REGISTER_MATCHING_RESULTS.json', result)
    atomic_json(DOC/'REGISTER_CALIBRATION_STATUS.json',
                {'status': 'complete' if success else 'incomplete', 'run': str(out), 'profile': execution})
    print(json.dumps({'run': str(out), **execution}, indent=2))
    return 0 if success else 1


def prepare():
    if (ROOT/REG).exists():
        raise FileExistsError('Scientific registration already frozen')
    gate = json.loads((DOC/'REGISTER_CALIBRATION_STATUS.json').read_text(encoding='utf-8'))
    if gate['status'] != 'complete':
        raise RuntimeError('Successful physical-moment matching required')
    matching = json.loads((DOC/'REGISTER_MATCHING_RESULTS.json').read_text(encoding='utf-8'))
    if matching['input_hash'] != verify_bundle(gate['run'])['input_hash']:
        raise RuntimeError('Physical matching identity mismatch')
    ratios = [0., .01, .05, .1, .25, .5, 1., 2., 4.]
    cases = []
    for parent in matching['plan']['parents']:
        fit = next(row for row in matching['fits'] if row['parent'] == parent['id'])
        if not fit['success']:
            raise RuntimeError('Unmatched parent')
        for ratio in ratios:
            parameters = {**parent['parameters'],
                          'signal_upkeep': parent['parameters']['metabolism']*ratio}
            cases.append({'id': f"{parent['id']}-u{ratio:g}", 'parent': parent['id'],
                          'upkeep_ratio': ratio, 'parameters': parameters, 'root': parent['root'],
                          'on_rate': fit['on_rate'], 'off_rate': fit['off_rate']})
    prior = json.loads((DOC/'FIRST_BATCH_PROTOCOL.json').read_text(encoding='utf-8'))
    protocol = {'id': 'matched-register-follow-up', 'version': '1',
        'status': 'frozen_before_scientific_ranking', 'date': '2026-10-14',
        'scope': 'physical control at two known adverse points, not new suffering kill',
        'matching_input_hash': matching['input_hash'], 'matching': matching,
        'cases': cases, 'arms': ['B', 'B_R', 'A0', 'A'],
        'cadences': [.125, .25, .5], 'horizons': [16, 64, 256, 1024],
        'primary_cadence': .25, 'primary_horizon': 64, 'reference_upkeep_ratio': .05,
        'grains': ['resolved', 'signal_merged_bounds'],
        'primary': 'complete conditional sampled-history entropy; randomness counts',
        'coordinate_order': [3, 4, 0, 1, 2],
        'qualification': prior['qualification'], 'tolerances': prior['tolerances'],
        'pairs': [['B_R', 'B'], ['A0', 'A'], ['B_R', 'A0'], ['A', 'B_R'], ['A', 'B']],
        'predictions': {
            'R1': 'B_R beats B at positive-cost reference for both parents, primary horizon/cadence',
            'R2': 'B_R loses to B at upkeep ratio4 for both parents, primary horizon/cadence',
            'R3': 'A0 beats A at reference for both parents, primary horizon/cadence'},
        'break_even': 'all adjacent upkeep-grid sign-change brackets; no monotonicity assumed',
        'fit_policy': 'rates fixed across upkeep and cadence; no refitting to outcomes',
        'limits': 'zero upkeep diagnostic still pays charging; common dead environmental tail',
        'caps': {'seconds': 600, 'memory': 512*1024**2, 'output_cap': 64*1024**2},
        'smoke_cases': ['W1-00-u0.05', 'W1-08-u4'],
    }
    atomic_json(ROOT/REG, protocol)
    print(ROOT/REG)


def run(mode):
    protocol = json.loads((ROOT/REG).read_text(encoding='utf-8'))
    if protocol['status'] != 'frozen_before_scientific_ranking':
        raise ValueError('Scientific registration required')
    if mode == 'science':
        gate = json.loads((DOC/'REGISTER_SMOKE_STATUS.json').read_text(encoding='utf-8'))
        if gate['status'] != 'complete' or verify_bundle(gate['run'])['config']['protocol'] != protocol:
            raise RuntimeError('Source-identical registered smoke required')
    out = _out(mode)
    frozen = freeze_bundle(ROOT, out, _files([REG, 'scripts/register_controls_worker.py']),
                           {'mode': mode, 'protocol': protocol})
    if mode == 'science' and frozen['source_hash'] != verify_bundle(gate['run'])['source_hash']:
        raise RuntimeError('Source changed since smoke')
    caps = {**protocol['caps'], 'seconds': 90 if mode == 'smoke' else protocol['caps']['seconds']}
    execution = run_frozen(out, 'scripts/register_controls_worker.py', [str(out), mode], caps)
    atomic_json(out/'PROFILE.json', execution)
    success = execution['exit_code'] == 0 and not execution['cap_reason']
    atomic_json(DOC/f'REGISTER_{mode.upper()}_STATUS.json',
                {'status': 'complete' if success else 'incomplete', 'run': str(out), 'profile': execution})
    print(json.dumps({'run': str(out), **execution}, indent=2))
    return 0 if success else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('calibrate', 'prepare', 'smoke', 'science'))
    args = parser.parse_args()
    raise SystemExit(calibration() if args.mode == 'calibrate' else
                     prepare() if args.mode == 'prepare' else run(args.mode))
