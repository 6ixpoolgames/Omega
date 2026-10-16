"""Resumable Stage A map, with bounded concurrent local workers.

Each worker has its own Windows Job Object. Matrices never leave workers;
only compact results and source/configuration receipts are retained.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
import hashlib
from itertools import combinations
import json
import os
from pathlib import Path
import random
import shutil
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle
from omega_v2.testbed.workflow.runner import run_frozen
from run_domination_friction import sources

DOC = ROOT/'docs/research_notes/lushness_testbed/domination_stage_a'
LOCAL = ROOT/'results/local_runs/lushness_testbed/domination_stage_a'
CAPS = {'seconds': 150, 'memory': 768*1024**2, 'output_cap': 32*1024**2}
TARGETS = {'access_entry': ('entry', [0]), 'construction_entry': ('entry', [1]),
           'trap_entry': ('entry', [2]), 'trap_exit': ('exit', [2]),
           'access_exit': ('exit', [0]), 'construction_exit': ('exit', [1]),
           'neutral_entry': ('entry', [3]), 'all_mobility': ('all', [0, 1, 2, 3])}


def case_id(supply, kappa, target, mode, phi, cost):
    return f's{supply:g}-k{kappa:g}-{target}-{mode}-p{phi:g}-c{cost}'


def make_plan():
    cases = []
    for supply in (.04, .12):
        for kappa in (0, 1):
            reference = f's{supply:g}-k{kappa}-idle'
            cases.append({'id': reference, 'slice': 'A4',
                'parameters': {'supply': supply, 'kappa': kappa}, 'policy': {'phi': 0},
                'roots': ['device_present', 'ordinary_preparation', 'unassembled_preparation']})
            strengths = (.1, .25, .4, .55, .7, .85, .95) if supply == .12 else (.25, .55, .95)
            for target, (direction, region) in TARGETS.items():
                for mode in ('blocking', 'steering'):
                    for phi in strengths:
                        cases.append({'id': case_id(supply, kappa, target, mode, phi, 1),
                            'slice': 'A1', 'target': target, 'reference_id': reference,
                            'parameters': {'supply': supply, 'kappa': kappa},
                            'policy': {'mode': mode, 'direction': direction, 'region': region,
                                       'phi': phi, 'cost': 1}})
            for target, mode in (('access_entry', 'blocking'), ('access_entry', 'steering'),
                                ('construction_entry', 'blocking'), ('trap_entry', 'steering'),
                                ('trap_exit', 'steering')):
                direction, region = TARGETS[target]
                cases.append({'id': case_id(supply, kappa, target, mode, .5, 1),
                    'slice': 'A5', 'target': target, 'reference_id': reference,
                    'parameters': {'supply': supply, 'kappa': kappa},
                    'policy': {'mode': mode, 'direction': direction, 'region': region,
                               'phi': .5, 'cost': 1}})
            if supply == .12:
                for target, mode in (('access_entry', 'blocking'), ('access_entry', 'steering'),
                                    ('construction_entry', 'blocking'), ('trap_entry', 'steering'),
                                    ('access_exit', 'steering'), ('construction_exit', 'steering')):
                    direction, region = TARGETS[target]
                    for cost in (0, 2):
                        for phi in (.25, .55, .95):
                            cases.append({'id': case_id(supply, kappa, target, mode, phi, cost),
                                'slice': 'A2', 'target': target, 'reference_id': reference,
                                'parameters': {'supply': supply, 'kappa': kappa},
                                'policy': {'mode': mode, 'direction': direction, 'region': region,
                                           'phi': phi, 'cost': cost}})
    # All ordinary entry/exit targets contain three directed location edges.
    # Reuse one fixed uniform sample of eight sets, rather than rerunning the
    # same random controls under seven different role labels. The 12-edge
    # all-mobility target has only one possible same-size control: itself.
    universe = [(a, b) for a in range(4) for b in range(4) if a != b]
    random_sets = random.Random(15102026).sample(list(combinations(universe, 3)), 8)
    for number, edges in enumerate(random_sets):
        for mode in ('blocking', 'steering'):
            for phi in (.25, .55, .95):
                cases.append({'id': f'random{number}-{mode}-p{phi:g}', 'slice': 'A3',
                    'target': f'random{number}', 'reference_id': 's0.12-k1-idle',
                    'parameters': {'supply': .12, 'kappa': 1},
                    'policy': {'edges': edges, 'phi': phi, 'cost': 1, 'mode': mode}})
    # A conservative device-supported potential, not a fuel-matched driven
    # gate. The common preparation initially has f=0, so all start at H=6.
    for location, target in enumerate(('access', 'construction', 'trap')):
        for shift in (.5, 1.):
            cases.append({'id': f'field-{target}-u{shift:g}', 'slice': 'A6', 'target': target,
                'reference_id': 's0.12-k1-idle', 'comparison_root': 'ordinary_preparation',
                'parameters': {'supply': .12, 'kappa': 1, 'field_location': location,
                               'field_shift': shift}, 'policy': {'phi': 0},
                'roots': ['ordinary_preparation']})
    return {'version': 'stage-a-revised-1', 'random_seed': 15102026, 'cases': cases,
            'cost_revision': 'integer fuel bills 0,1,2; fractional reservoir refinement deferred',
            'field_comparison': 'conservative energy-coupling probe, not claimed fuel-matched'}


def smoke_plan():
    plan = make_plan()
    wanted = ('s0.12-k1-idle', 's0.12-k1-all_mobility-steering-p0.55-c1',
              's0.12-k1-access_entry-blocking-p0.55-c0',
              's0.12-k1-access_exit-steering-p0.55-c2', 'random0-steering-p0.55',
              'field-trap-u1')
    return [c for name in wanted for c in plan['cases'] if c['id'] == name]


def execute(cases, mode, jobs=1, budget_seconds=18000, output_budget=512*1024**2):
    DOC.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(ROOT).free < 2*output_budget:
        raise RuntimeError('Insufficient free storage for bounded local batch')
    source_files = sources()+['scripts/run_domination_stage_a.py']
    payload = {path: (ROOT/path).read_bytes() for path in sorted(source_files)}
    source_hash = hashlib.sha256(b''.join(
        path.encode()+b'\0'+content for path, content in payload.items())).hexdigest()
    recorded_source = LOCAL/('batch-source-'+source_hash)
    for path, content in payload.items():
        destination = recorded_source/path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.read_bytes() != content:
            raise RuntimeError('Existing batch snapshot is not immutable')
        if not destination.exists():
            destination.write_bytes(content)
    start = monotonic()
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

    def one(case):
        config = {'mode': mode, 'roots': ['device_present'], 'cadences': [.125, .25, .5],
                  'horizons': [16, 64, 256, 1024], 'max_kernel_bytes': 160*1024**2,
                  'subject_depth': 2, **case, 'caps': CAPS}
        identity = hashlib.sha256(json.dumps([source_hash, config], sort_keys=True).encode()).hexdigest()
        cached, receipt_path = DOC/'cases'/(identity+'.json'), DOC/'receipts'/(identity+'.json')
        if cached.exists() and receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            if receipt['status'] == 'complete' and receipt['result_sha256'] == hashlib.sha256(cached.read_bytes()).hexdigest():
                return receipt
        if monotonic()-start+CAPS['seconds'] > budget_seconds:
            return {'id': case['id'], 'status': 'budget_pending', 'configuration': config}
        # Bound retained run outputs and source snapshots together. No deletion.
        used = sum(p.stat().st_size for base in (DOC, LOCAL) if base.exists()
                   for p in base.rglob('*') if p.is_file())
        if used+(jobs+1)*CAPS['output_cap'] > output_budget:
            return {'id': case['id'], 'status': 'storage_pending', 'configuration': config}
        stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')
        out = LOCAL/(identity[:12]+'-'+stamp)
        freeze_bundle(recorded_source, out, source_files, config)
        measured = run_frozen(out, 'scripts/domination_friction_worker.py', [str(out)], CAPS)
        complete = measured['exit_code'] == 0 and not measured['cap_reason']
        receipt = {'id': case['id'], 'identity': identity,
                   'status': 'complete' if complete else 'incomplete', 'run': str(out),
                   'profile': measured, 'configuration': config}
        if complete:
            atomic_json(cached, json.loads((out/'RESULTS.json').read_text()))
            receipt['result_sha256'] = hashlib.sha256(cached.read_bytes()).hexdigest()
        atomic_json(receipt_path, receipt)
        atomic_json(out/'PROFILE.json', receipt)
        if not complete:
            receipt['log_tail'] = (out/'worker.log').read_text(encoding='utf-8')[-2500:]
        return receipt

    summaries = {}
    status_path = DOC/(mode.upper()+'_STATUS.json')
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        pending = {executor.submit(one, c): c for c in cases}
        for future in as_completed(pending):
            receipt = future.result()
            summaries[receipt['id']] = receipt
            status = {'mode': mode, 'status': 'running', 'jobs': jobs,
                      'source_hash': source_hash,
                      'completed': sum(x['status'] == 'complete' for x in summaries.values()),
                      'total': len(cases), 'elapsed_seconds': monotonic()-start,
                      'cases': [summaries[c['id']] for c in cases if c['id'] in summaries]}
            atomic_json(status_path, status)
            print(json.dumps({k: receipt[k] for k in ('id', 'status')}
                             | {'profile': receipt.get('profile'), 'completed': status['completed'],
                                'total': len(cases), 'elapsed_seconds': status['elapsed_seconds']}), flush=True)
            if receipt['status'] == 'incomplete':
                for task in pending:
                    task.cancel()
                status['status'] = 'incomplete'
                atomic_json(status_path, status)
                print(receipt.get('log_tail', ''), flush=True)
                return 1
    status['status'] = 'complete' if status['completed'] == len(cases) else 'budget_limited'
    atomic_json(status_path, status)
    return 0 if status['status'] == 'complete' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['plan', 'smoke', 'survey'])
    parser.add_argument('--jobs', type=int, default=1)
    parser.add_argument('--budget-seconds', type=float, default=18000)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        raise ValueError('One to eight bounded local workers supported')
    plan = make_plan()
    atomic_json(DOC/'PLAN.json', plan)
    if args.mode == 'plan':
        print(json.dumps({'cases': len(plan['cases']), 'path': str(DOC/'PLAN.json')}))
        return 0
    return execute(smoke_plan() if args.mode == 'smoke' else plan['cases'],
                   args.mode, args.jobs, args.budget_seconds)


if __name__ == '__main__':
    raise SystemExit(main())
