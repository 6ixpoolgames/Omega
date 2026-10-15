"""Immutable, capped local batches for attribution, world swap and discovery."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, UTC
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from threading import Event
from time import monotonic, sleep

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import freeze_bundle, atomic_json
from omega_v2.testbed.workflow.runner import run_frozen
from run_domination_friction import sources
DOC = ROOT/'docs/research_notes/lushness_testbed/domination_b1'
LOCAL = ROOT/'results/local_runs/lushness_testbed/domination_b1'


def write(path, content):
    for attempt in range(8):
        try:
            atomic_json(path, content)
            return
        except PermissionError:
            if attempt == 7:
                raise
            sleep(.05*(attempt+1))


def plan(mode):
    if mode == 'smoke':
        return [{'id': 'smoke-half-grid', 'parameters': {'discovery': True, 'd_energy_capacity': 3,
                    'd_energy_quantum': .5, 'kappa': 1}, 'policy': {'cost': .5, 'phi': .55},
                 'cadences': [.25], 'horizons': [16, 64]}]
    if mode == 'fine-smoke':
        return [{'id': 'smoke-tenth-grid', 'parameters': {'discovery': True, 'd_energy_capacity': 3,
                    'd_energy_quantum': .1, 'kappa': 1}, 'policy': {'cost': .3, 'phi': .55},
                 'cadences': [.25], 'horizons': [16, 64]}]
    if mode == 'full-smoke':
        return [{'id': 'smoke-full-clocks-tenth-grid',
                 'parameters': {'discovery': True, 'd_energy_capacity': 3,
                    'd_energy_quantum': .1, 'kappa': 1},
                 'policy': {'cost': .3, 'phi': .55}, 'block_rows': 128}]
    if mode == 'backend-calibration':
        return [{'id': 'calibration-poisson-full-clocks-tenth-grid',
                 'parameters': {'discovery': True, 'd_energy_capacity': 3,
                    'd_energy_quantum': .1, 'kappa': 1},
                 'policy': {'cost': .3, 'phi': .55}, 'block_rows': 128,
                 'entropy_backend': 'uniformized', 'entropy_threads': 4}]
    if mode == 'followup':
        cases = []
        for supply, kappa in ((.04, 0), (.12, 0), (.12, 1)):
            base = {'supply': supply, 'kappa': kappa}
            prefix = f's{supply}-k{kappa}'
            cases += [dict(id=prefix+'-idle', parameters=base, policy={'phi': 0}),
                      dict(id=prefix+'-ordinary', parameters={**base, 'device_role': 'ordinary'}, policy={'phi': 0})]
            for mode in ('blocking', 'sham'):
                cases.append(dict(id=prefix+'-'+mode, parameters=base,
                                  policy={'mode': mode, 'phi': .95, 'cost': 1}))
        return cases
    # Fixed tenth-energy grid throughout the discovery frontier. Targets/costs
    # vary; capacities, bath, energy density and native law remain matched.
    cases = []
    for opportunity in (0, 1, 4):
        base = {'discovery': True, 'opportunity_yield': opportunity, 'kappa': 1,
                'd_energy_capacity': 3, 'd_energy_quantum': .1}
        prefix = f'y{opportunity}'
        cases.append(dict(id=prefix+'-idle', parameters=base, policy={'phi': 0}))
        for cost in (.1, .3, 1.):
            for phi in (.55, .95):
                cases.append(dict(id=f'{prefix}-trap-c{cost:g}-p{phi:g}', parameters=base,
                    policy={'mode': 'steering', 'direction': 'entry', 'region': [2], 'phi': phi, 'cost': cost}))
    base = {'discovery': True, 'opportunity_yield': 1, 'kappa': 0,
            'd_energy_capacity': 3, 'd_energy_quantum': .1}
    cases.append(dict(id='exclusion-idle', parameters=base, policy={'phi': 0}))
    for cost in (.1, .3, 1.):
        for phi in (.55, .95):
            cases.append(dict(id=f'exclusion-access-c{cost:g}-p{phi:g}', parameters=base,
                policy={'mode': 'blocking', 'direction': 'entry', 'region': [0], 'phi': phi, 'cost': cost}))
    for case in cases:
        case['entropy_backend'] = 'uniformized'
        case['entropy_threads'] = 4
        case['block_rows'] = 128
    return cases


def execute(cases, mode, jobs=1, seconds=600, budget=14400, worker='scripts/domination_b1_worker.py'):
    DOC.mkdir(parents=True, exist_ok=True)
    caps = {'seconds': seconds, 'memory': 3*1024**3, 'output_cap': 32*1024**2}
    paths = sorted(set(sources()+[worker, 'scripts/run_domination_b1.py']))
    payload = {p: (ROOT/p).read_bytes() for p in paths}
    digest = hashlib.sha256(b''.join(p.encode()+b'\0'+data for p, data in payload.items())).hexdigest()
    source = LOCAL/('batch-source-'+digest)
    for p, data in payload.items():
        target = source/p
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != data:
            raise RuntimeError('Immutable source mismatch')
        if not target.exists():
            target.write_bytes(data)
    write(DOC/(mode.upper()+'_PLAN.json'), {'cases': cases, 'source_hash': digest, 'caps': caps})
    start = monotonic()
    stopped = Event()
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

    def one(case):
        config = {'cadences': [.125, .25, .5], 'horizons': [16, 64, 256, 1024],
                  'block_rows': 512, 'entropy_cache': str(LOCAL/'entropy-blocks'),
                  **case, 'caps': caps}
        identity = hashlib.sha256(json.dumps([digest, config], sort_keys=True).encode()).hexdigest()
        if stopped.is_set():
            return {'id': case['id'], 'status': 'stopped_after_engineering_error'}
        cached, receipt = DOC/'cases'/(identity+'.json'), DOC/'receipts'/(identity+'.json')
        if cached.exists() and receipt.exists():
            old = json.loads(receipt.read_text())
            if old['status'] == 'complete' and old['result_sha256'] == hashlib.sha256(cached.read_bytes()).hexdigest():
                return old
        if monotonic()-start+seconds > budget:
            return {'id': case['id'], 'status': 'budget_pending'}
        used = sum(p.stat().st_size for base in (DOC, LOCAL) if base.exists() for p in base.rglob('*') if p.is_file())
        if used+(jobs+1)*caps['output_cap'] > 2*1024**3 or shutil.disk_usage(ROOT).free < 4*1024**3:
            return {'id': case['id'], 'status': 'storage_pending'}
        out = LOCAL/(identity[:12]+'-'+datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ'))
        freeze_bundle(source, out, paths, config)
        measured = run_frozen(out, worker, [str(out)], caps)
        complete = measured['exit_code'] == 0 and not measured['cap_reason']
        result = {'id': case['id'], 'identity': identity, 'configuration': config,
                  'status': 'complete' if complete else 'incomplete', 'profile': measured, 'run': str(out)}
        if complete:
            write(cached, json.loads((out/'RESULTS.json').read_text()))
            result['result_sha256'] = hashlib.sha256(cached.read_bytes()).hexdigest()
        else:
            stopped.set()
            result['log_tail'] = (out/'worker.log').read_text(encoding='utf-8')[-3000:]
        write(receipt, result)
        return result

    results = {}
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        tasks = {pool.submit(one, c): c for c in cases}
        for task in as_completed(tasks):
            result = task.result()
            results[result['id']] = result
            status = {'status': 'running', 'mode': mode, 'source_hash': digest,
                      'total_cases': len(cases), 'jobs': jobs,
                      'elapsed_seconds': monotonic()-start,
                      'cases': [results[c['id']] for c in cases if c['id'] in results]}
            write(DOC/(mode.upper()+'_STATUS.json'), status)
            print(json.dumps({'id': result['id'], 'status': result['status'],
                              'profile': result.get('profile'), 'log_tail': result.get('log_tail')}), flush=True)
    status['status'] = 'complete' if all(r['status'] == 'complete' for r in results.values()) else 'incomplete'
    write(DOC/(mode.upper()+'_STATUS.json'), status)
    return int(status['status'] != 'complete')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['smoke', 'fine-smoke', 'full-smoke', 'backend-calibration', 'followup', 'survey'])
    parser.add_argument('--jobs', type=int, default=1)
    parser.add_argument('--seconds', type=float, default=600)
    parser.add_argument('--budget', type=float, default=14400)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 4 or args.seconds <= 0:
        raise ValueError('Use one to four capped workers')
    raise SystemExit(execute(plan(args.mode), args.mode, args.jobs, args.seconds, args.budget))
