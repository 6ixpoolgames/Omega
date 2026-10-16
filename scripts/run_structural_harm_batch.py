"""Freeze the prospective harm batch and run sequential, capped exact cases."""
import argparse
import hashlib
import json
import math
import sys
import uuid
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.controllers.reserve import candidate_family
from omega_v2.testbed.growing_population import DEFAULT
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle, verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen

DOC = ROOT / 'docs/research_notes/lushness_testbed/structural_harm'
REGISTRATION = 'docs/research_notes/lushness_testbed/structural_harm/PROTOCOL.json'


def prepare():
    target = ROOT / REGISTRATION
    if target.exists():
        raise FileExistsError('Existing registration is not overwritten')
    candidates = [p.manifest() for p in candidate_family(3)]
    cases = []
    for mode in ('fast', 'slow', 'hardware_loss'):
        for hazard, cadences in ((.02, (.25, .125, .5)), (.04, (.25,))):
            for cadence in cadences:
                cases.append({'id': f'harm-r1-{mode}-h{hazard}-dt{cadence}',
                              'status': 'frozen_before_scientific_ranking',
                              'registration': REGISTRATION, 'mode': mode, 'hazard': hazard,
                              'cadence': cadence, 'inventory': [3, 1], 'params': asdict(DEFAULT),
                              'present_root': [[0, 2, 0, 2, 0], [0, 1, 0, 1, 0], [1, 1]],
                              'slow_factor': .1, 'hardware_energy': 1., 'candidates': candidates,
                              'horizons': [1, 4, 16, 64, 256], 'deadline': 64,
                              'primary': 'complete conditional history bits at each horizon',
                              'rank_tolerance': 1e-8, 'block_rows': 64,
                              'max_kernel_bytes': 256*1024**2})
    protocol = {'schema': 'omega-structural-harm/1',
                'status': 'frozen_before_scientific_ranking',
                'created_utc': datetime.now(UTC).isoformat(), 'cases': cases,
                'limits': {'case_seconds': 600, 'batch_seconds': 2400,
                           'memory_bytes': 1024**3, 'output_bytes': 32*1024**2},
                'predictions': {
                    'H1': 'Service response never decreases over adjacent horizons; strict increases counted separately',
                    'C1': 'At least one primary horizon has different winning response between fast and hardware_loss at hazard .02',
                    'R1': 'At least one mode/horizon shows greater service response when hazard rises .02 to .04'},
                'adverse': {
                    'E1': 'Winner stationary exposure increases with hazard within a consequence arm',
                    'S1': 'Positive-to-negative winner lead against idle/service/export/best nonrandom across audited cadences'},
                'tie_scoring': 'Compare all tied winner pairs; mixed or incomparable outcomes retained',
                'service_order': 'Pointwise service coefficient on feasible active>0 left (a,w), capacity3',
                'grain_scope': 'Cadence only; full declared physical count state with hardware',
                'rate_scope': 'Secondary sustained breadth diagnostic; no offset estimate in this batch',
                'root_scope': 'Same pre-fault physical root; post_fault conditional on one left fault is diagnostic',
                'recovery_scope': 'Restore original left active reserve >=2; firsthit/endpoint/retention distinct',
                'limitations': ['Coarse count states, not microscopic thermal baseline',
                                'Hardware loss disables powered repair only; substitutes remain',
                                'Fast/slow contrast changes paired repair law; pre-fault root matches',
                                'Left adaptation only; right capacity one',
                                'External one-way faults are not equilibrium thermal events',
                                'Same boundary prescription does not imply equal accepted work',
                                'Apparatus not established valuers; no protection reward; randomness counts']}
    atomic_json(target, protocol)
    print(json.dumps({'registration': str(target), 'cases': len(cases),
                      'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}), flush=True)


def run():
    protocol_path = ROOT / REGISTRATION
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    if protocol['status'] != 'frozen_before_scientific_ranking':
        raise RuntimeError('Frozen registration required')
    status_path = DOC / 'EXECUTION_STATUS.json'
    if status_path.exists():
        raise RuntimeError('Batch already has execution status; inspect and resume explicitly')
    sources = [p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
    sources += ['omega_v2/__init__.py', 'scripts/run_bng_binding_calibration.py',
                'scripts/structural_harm_worker.py', 'scripts/run_structural_harm_batch.py', REGISTRATION]
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    batch = ROOT / 'results/local_runs/lushness_testbed/structural_harm' / ('batch-'+stamp)
    protocol_hash = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    frozen = freeze_bundle(ROOT, batch, sources, {'protocol': protocol, 'protocol_hash': protocol_hash})
    status = {'status': 'running', 'batch': str(batch), 'input_hash': frozen['input_hash'],
              'protocol_hash': protocol_hash, 'charged_seconds': 0., 'completed': {}, 'failed': {}}
    atomic_json(status_path, status)
    for case in protocol['cases']:
        left = protocol['limits']['batch_seconds']-status['charged_seconds']
        if left < 1:
            status['status'] = 'budget_exhausted'
            atomic_json(status_path, status)
            return 1
        output = batch / 'cases' / case['id']
        freeze_bundle(batch/'source', output, sources, {'case': case, 'protocol_hash': protocol_hash})
        limits = protocol['limits']
        profile = run_frozen(output, 'scripts/structural_harm_worker.py', [str(output)],
                             {'seconds': min(limits['case_seconds'], math.floor(left)),
                              'memory': limits['memory_bytes'], 'output_cap': limits['output_bytes']})
        atomic_json(output/'PROFILE.json', profile)
        status['charged_seconds'] += profile['wall_seconds']
        success = profile.get('exit_code') == 0 and not profile.get('cap_reason')
        atomic_json(output/'status.json', {'status': 'complete' if success else 'incomplete'})
        verify_bundle(output)
        status['completed' if success else 'failed'][case['id']] = str(output)
        if not success:
            status['status'] = 'incomplete'
            atomic_json(status_path, status)
            print(json.dumps({'case': case['id'], **profile}), flush=True)
            return 1
        atomic_json(status_path, status)
        print(json.dumps({'case': case['id'], **profile}), flush=True)
    status['status'] = 'complete'
    verify_bundle(batch)
    atomic_json(status_path, status)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('prepare', 'run'))
    args = parser.parse_args()
    raise SystemExit(prepare() if args.mode == 'prepare' else run())
