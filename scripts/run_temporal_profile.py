"""Freeze and run the explanatory audit of already observed signal comparisons."""
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

BASE = 'docs/research_notes/lushness_testbed/temporal_profile'
DOC = ROOT/BASE
REG = BASE+'/PROTOCOL.json'
SPEC = BASE+'/SPEC.md'


def prepare():
    if (ROOT/REG).exists():
        raise FileExistsError('Registration already frozen')
    prior = json.loads((ROOT/'docs/research_notes/lushness_testbed/aversive_signals/REGISTER_CONTROL_PROTOCOL.json').read_text(encoding='utf-8'))
    cases = [case for case in prior['cases'] if case['upkeep_ratio'] == .05]
    protocol = {
        'id': 'signal-temporal-profile-audit', 'version': '1', 'date': '2026-10-14',
        'status': 'frozen_before_new_profile_evaluation',
        'selection': 'two known adverse points, explanatory calibration, not new blind kill search',
        'cases': cases, 'arms': ['B', 'B_R', 'A0', 'A'],
        'pairs': [['A', 'B'], ['B_R', 'B'], ['A0', 'A'], ['A', 'B_R']],
        'horizons': [64, 256], 'cadences': [.5/(2**i) for i in range(9)],
        'reference_time': 1., 'physical_temporal_band': None,
        'grid_is_physical_cutoff': False,
        'objective': 'exact complete conditional sampled-history entropy; no subtraction',
        'hidden_signal': 'conditioning bounds at .125/.25/.5; no projected Markov generator',
        'count_query': {'horizon': 64, 'tail_budget': 1e-10, 'max_augmented_states': 100000,
                        'overflow': 'retained; entropy uncertainty bounded analytically'},
        'fixed_jump_counts': [8, 32, 128],
        'full_random_length_mark_timing_decomposition': 'not computed',
        'refinement': {'rule': 'bisect integer sample count between adjacent opposite-sign grid points',
                       'max_iterations': 16, 'same_sign_hidden_crossings': 'not excluded'},
        'tolerances': {'bits': 1e-5, 'residual': 1e-8},
        'calibrations': ['reproduce earlier coarse-cadence scores',
                         'compare exact pair difference with asymptotic estimate',
                         'test decreasing error along final four fine cadences',
                         'check finest sign against nondegenerate jump-count sign'],
        'smoke_case': 'W1-00-u0.05',
        'caps': {'seconds': 600, 'memory': 512*1024**2, 'output_cap': 64*1024**2},
    }
    atomic_json(ROOT/REG, protocol)
    print(ROOT/REG)


def run(mode):
    protocol = json.loads((ROOT/REG).read_text(encoding='utf-8'))
    if protocol['status'] != 'frozen_before_new_profile_evaluation':
        raise ValueError('Frozen protocol required')
    if mode == 'science':
        gate = json.loads((DOC/'SMOKE_STATUS.json').read_text(encoding='utf-8'))
        if gate['status'] != 'complete' or verify_bundle(gate['run'])['config']['protocol'] != protocol:
            raise RuntimeError('Source-identical smoke required')
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out = ROOT/'results/local_runs/lushness_testbed/temporal_profile'/(mode+'-'+stamp)
    files = ([p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
             + ['omega_v2/__init__.py', 'scripts/run_bng_binding_calibration.py',
                'scripts/run_temporal_profile.py', 'scripts/temporal_profile_worker.py', REG, SPEC])
    frozen = freeze_bundle(ROOT, out, files, {'mode': mode, 'protocol': protocol})
    if mode == 'science' and frozen['source_hash'] != verify_bundle(gate['run'])['source_hash']:
        raise RuntimeError('Source changed since smoke')
    caps = {**protocol['caps'], 'seconds': 120 if mode == 'smoke' else protocol['caps']['seconds']}
    execution = run_frozen(out, 'scripts/temporal_profile_worker.py', [str(out), mode], caps)
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
