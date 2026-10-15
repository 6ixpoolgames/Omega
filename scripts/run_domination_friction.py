"""Capped physical smoke and resumable user-configured domination surveys.

Run records preserve reproducibility without pass/fail guesses about the theory.
The default command is engineering smoke, not an optimizer ranking batch.
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle
from omega_v2.testbed.workflow.runner import run_frozen

DOC = ROOT/'docs/research_notes/lushness_testbed/domination_friction'
LOCAL = ROOT/'results/local_runs/lushness_testbed/domination_friction'
CAPS = {'seconds': 120, 'memory': 512*1024**2, 'output_cap': 32*1024**2}


def sources():
    return [p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')] + [
        'omega_v2/__init__.py', 'scripts/run_bng_binding_calibration.py',
        'scripts/run_domination_friction.py', 'scripts/domination_friction_worker.py']


def smoke_cases():
    base = {'mode': 'smoke', 'roots': ['device_present'], 'cadences': [.25],
            'horizons': [16, 64, 256, 1024], 'max_kernel_bytes': 160*1024**2}
    return [
        {**base, 'id': 'validation-1024', 'parameters': {'charge_capacity': 1},
         'policy': {'phi': 0}, 'horizons': [16, 64]},
        {**base, 'id': 'blocking-2304', 'parameters': {},
         'policy': {'mode': 'blocking', 'direction': 'entry', 'region': [0], 'cost': 1}},
        {**base, 'id': 'steering-2304', 'parameters': {'kappa': 1.},
         'policy': {'mode': 'steering', 'direction': 'exit', 'region': [2], 'cost': 1}},
    ]


def execute(cases, mode, budget_seconds=900):
    DOC.mkdir(parents=True, exist_ok=True)
    source_files = sources()
    source_hash = hashlib.sha256(b''.join(
        path.encode()+b'\0'+(ROOT/path).read_bytes() for path in sorted(source_files))).hexdigest()
    summaries = []
    used_seconds = 0.
    for case in cases:
        config = {'mode': mode, 'roots': ['device_present'], 'cadences': [.125, .25, .5],
                  'horizons': [16, 64, 256, 1024], 'max_kernel_bytes': 160*1024**2,
                  **case, 'caps': CAPS}
        if config['mode'] != mode:
            raise ValueError('Case mode disagrees with run mode')
        identity = hashlib.sha256(json.dumps([source_hash, config], sort_keys=True).encode()).hexdigest()
        cached = DOC/'cases'/(identity+'.json')
        receipt_path = DOC/'receipts'/(identity+'.json')
        if cached.exists() and receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            if receipt['status'] == 'complete' and receipt['result_sha256'] == hashlib.sha256(cached.read_bytes()).hexdigest():
                summaries.append(receipt)
                print(json.dumps({'case': case['id'], 'cache_reused': True}), flush=True)
                continue
        if used_seconds+CAPS['seconds'] > budget_seconds:
            atomic_json(DOC/(mode.upper()+'_STATUS.json'), {'mode': mode,
                        'status': 'budget_limited', 'pending': case['id'], 'cases': summaries})
            raise RuntimeError('Batch budget reached; completed cases retained for resume')
        stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')
        out = LOCAL/(identity[:12]+'-'+stamp)
        freeze_bundle(ROOT, out, source_files, config)
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
        measured = run_frozen(out, 'scripts/domination_friction_worker.py', [str(out)], CAPS)
        used_seconds += measured['wall_seconds']
        complete = measured['exit_code'] == 0 and not measured['cap_reason']
        receipt = {'id': case['id'], 'identity': identity,
                   'status': 'complete' if complete else 'incomplete', 'run': str(out),
                   'profile': measured, 'configuration': config}
        if complete:
            atomic_json(cached, json.loads((out/'RESULTS.json').read_text()))
            receipt['result_sha256'] = hashlib.sha256(cached.read_bytes()).hexdigest()
        atomic_json(receipt_path, receipt)
        atomic_json(out/'PROFILE.json', receipt)
        summaries.append(receipt)
        atomic_json(DOC/(mode.upper()+'_STATUS.json'), {'mode': mode,
                    'status': 'complete' if len(summaries) == len(cases) and complete else 'partial',
                    'cases': summaries})
        print(json.dumps(receipt, indent=2), flush=True)
        if not complete:
            print((out/'worker.log').read_text(encoding='utf-8')[-6000:])
            return 1
    atomic_json(DOC/(mode.upper()+'_STATUS.json'), {'mode': mode, 'status': 'complete',
                                                  'cases': summaries})
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['smoke', 'survey'])
    parser.add_argument('--config', type=Path)
    parser.add_argument('--budget-seconds', type=float, default=900)
    args = parser.parse_args()
    if args.mode == 'smoke':
        return execute(smoke_cases(), args.mode, args.budget_seconds)
    if args.config is None:
        raise ValueError('A survey requires an explicit list of cases via --config')
    cases = json.loads(args.config.read_text())['cases']
    if not cases or len({case['id'] for case in cases}) != len(cases):
        raise ValueError('Unique nonempty case IDs required')
    return execute(cases, args.mode, args.budget_seconds)


if __name__ == '__main__':
    raise SystemExit(main())
