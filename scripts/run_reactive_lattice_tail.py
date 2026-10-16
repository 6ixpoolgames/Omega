"""Extend every filed law under a disclosed, source-verified query plan."""
import hashlib
import json
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle, verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen

BASE = 'docs/research_notes/lushness_testbed/same_law_gas'
DOC = ROOT/BASE


def main():
    protocol = json.loads((DOC/'PROTOCOL.json').read_text())
    original = json.loads((DOC/'SCIENCE_STATUS.json').read_text())
    if original['status'] != 'complete':
        raise RuntimeError('Original grid must be complete')
    caps = {'seconds': 120, 'memory': 512*1024**2, 'output_cap': 32*1024**2}
    plan_path = DOC/'TAIL_QUERY_PLAN.json'
    if not plan_path.exists():
        atomic_json(plan_path, {'status': 'frozen_before_extension_queries', 'retrospective': True,
            'known_original_outcomes': True, 'extension_horizons': [4096, 16384],
            'cadences': protocol['cadences'], 'tail_tolerance_bits': .001, 'caps': caps,
            'laws': [r['id'] for r in protocol['laws']],
            'rule': 'all laws; stop extension only when global Markov tail oscillation plus Poisson residual bound is below1e-3bits',
            'score': 'no alteration of original preregistered predictions'})
    plan = json.loads(plan_path.read_text())
    status_path = DOC/'TAIL_STATUS.json'
    status = json.loads(status_path.read_text()) if status_path.exists() else {'laws': {}}
    for law in protocol['laws']:
        if status['laws'].get(law['id'], {}).get('status') == 'complete':
            continue
        if law['id'] in status['laws']:
            status.setdefault('prior_incomplete_attempts', []).append({'law': law['id'], **status['laws'][law['id']]})
        used = sum(r['profile']['wall_seconds'] for r in status['laws'].values())
        used += sum(r['profile']['wall_seconds'] for r in status.get('prior_incomplete_attempts', []))
        if used+caps['seconds'] > 1800:
            raise RuntimeError('Horizon extension total budget exhausted')
        parent = verify_bundle(original['laws'][law['id']]['run'])
        for record in parent['sources']:
            if hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest() != record['sha256']:
                raise RuntimeError('Original physical/query sources changed')
        files = [r['path'] for r in parent['sources']]+['scripts/reactive_lattice_tail_worker.py',
            'scripts/run_reactive_lattice_tail.py', BASE+'/TAIL_QUERY_PLAN.json']
        stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
        out = ROOT/'results/local_runs/lushness_testbed/same_law_gas'/f"tail-{law['id']}-{stamp}"
        freeze_bundle(ROOT, out, files, {'law': law, **plan, 'parent_hash': parent['input_hash']})
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
        profile = run_frozen(out, 'scripts/reactive_lattice_tail_worker.py', [str(out)], caps)
        complete = profile['exit_code'] == 0 and not profile['cap_reason']
        status['laws'][law['id']] = {'status': 'complete' if complete else 'incomplete', 'run': str(out), 'profile': profile}
        atomic_json(status_path, status)
        print(json.dumps({'law': law['id'], **profile}), flush=True)
        if not complete:
            return 1
        data = json.loads((out/'RESULTS.json').read_text())
        # Validate T1024 against the original finite-history calculation.
        previous = json.loads((DOC/'laws'/(law['id']+'.json')).read_text())
        for row in data['rows']:
            if row['horizon'] != 1024:
                continue
            expected = next(r['delta_bits'] for r in previous['contrasts']
                if r['horizon'] == 1024 and r['cadence'] == row['cadence'] and r['reference'] == row['reference'])
            if abs(row['delta_bits']-expected) > 1e-6:
                raise ArithmeticError('Original finite-history scores did not reproduce')
        atomic_json(DOC/'tails'/(law['id']+'.json'), data)
    status['status'] = 'complete'
    atomic_json(status_path, status)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
