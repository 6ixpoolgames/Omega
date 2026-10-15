"""Flow calibration determines the match before entropy rankings are queried."""
import argparse
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

BASE = 'docs/research_notes/lushness_testbed/compounding/matched_throughput'
DOC = ROOT/BASE
CAPS = {'seconds': 120, 'memory': 512*1024**2, 'output_cap': 32*1024**2}


def sources():
    return ([p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
            + ['omega_v2/__init__.py', 'scripts/run_bng_binding_calibration.py',
               'scripts/compounding_worker.py', 'scripts/throughput_match_worker.py',
               'scripts/run_throughput_match.py', BASE+'/SPEC.md'])


def execute(config, name, extra=()):
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out = ROOT/'results/local_runs/lushness_testbed/throughput_match'/f'{name}-{stamp}'
    manifest = freeze_bundle(ROOT, out, sources()+list(extra), config)
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    profile = run_frozen(out, 'scripts/throughput_match_worker.py', [str(out)], CAPS)
    complete = profile['exit_code'] == 0 and not profile['cap_reason']
    status = {'status': 'complete' if complete else 'incomplete', 'run': str(out),
              'profile': profile, 'input_hash': manifest['input_hash']}
    data = json.loads((out/'RESULTS.json').read_text()) if complete else None
    return status, data


def calibration():
    config = {'mode': 'calibration', 'capacities': [4, 8, 16, 32],
              'source_bracket': [.001, 3.], 'calibration_samples': 17,
              'interior_fractions': [.25, .5, .75], 'flow_tolerance': 1e-8, 'caps': CAPS}
    status, data = execute(config, 'calibration')
    atomic_json(DOC/'CALIBRATION_STATUS.json', status)
    if data:
        atomic_json(DOC/'CALIBRATION.json', data)
    print(json.dumps(status, indent=2), flush=True)
    return 0 if data else 1


def prepare():
    status = json.loads((DOC/'CALIBRATION_STATUS.json').read_text())
    if status['status'] != 'complete':
        raise RuntimeError('Capped physical-flow calibration required')
    receipts = verify_bundle(status['run'])['sources']
    if any(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest() != r['sha256'] for r in receipts):
        raise RuntimeError('Calibration source bytes changed')
    if (DOC/'PROTOCOL.json').exists():
        raise FileExistsError('Do not replace a frozen protocol')
    from omega_v2.testbed.compounding import CompoundingParameters
    calibration_data = json.loads((DOC/'CALIBRATION.json').read_text())
    laws = []
    for match in calibration_data['matches']:
        target_number = calibration_data['targets'].index(match['target'])+1
        p = CompoundingParameters(capacity=match['capacity'], supply_rate=match['supply_rate'])
        laws.append({'id': f"M{p.capacity}-target{target_number}-{match['mechanism']}",
                     'parameters': vars(p), 'target_number': target_number,
                     'target': match['target'], 'mechanism': match['mechanism']})
    protocol = {'status': 'frozen_before_scientific_ranking', 'date': '2026-10-15',
        'laws': laws, 'roots': {'seed': [6, 1, 1], 'unorganized': [8, 1, 0]},
        'horizons': [16, 64, 256, 1024], 'cadences': [.25, .125, .5], 'coordinate_order': [1, 0, 2],
        'primary_horizon': 64, 'primary_cadence': .25,
        'throughput': 'stationary accepted external packet work per physical time; resource_work flux',
        'match_tolerance': 1e-8, 'bits_tolerance': 1e-5, 'rate_tolerance': 1e-8,
        'predictions': {'P1': 'at least one matched point has positive loop-minus-basal rate at every cadence',
                        'P2': 'central target2 positive rate at all capacities and cadences',
                        'P3': 'loop retains more apparatus than basal at every matched point'},
        'caps': CAPS, 'total_seconds': 1200,
        'matching': 'global common feasible interval across all eight capacity/mechanism flow curves; quarter/mid/three-quarter targets',
        'scope': 'mechanism contrast at matched stationary accepted work; different offered source rates, not same-law gas',
        'finite_work': 'not matched at finite horizons; report actual cumulative accepted work',
        'nuisance': 'activity, bath inputs, unused packet loss and useful capture remain measured, not subtracted'}
    atomic_json(DOC/'PROTOCOL.json', protocol)
    print('Throughput protocol frozen from physical-flow calibration only')
    return 0


def science():
    p = json.loads((DOC/'PROTOCOL.json').read_text())
    path = DOC/'SCIENCE_STATUS.json'
    status = json.loads(path.read_text()) if path.exists() else {'laws': {}}
    calibration_status = json.loads((DOC/'CALIBRATION_STATUS.json').read_text())
    sources_at_calibration = verify_bundle(calibration_status['run'])['sources']
    for law in p['laws']:
        if status['laws'].get(law['id'], {}).get('status') == 'complete':
            continue
        if sum(r['profile']['wall_seconds'] for r in status['laws'].values())+CAPS['seconds'] > p['total_seconds']:
            raise RuntimeError('Total scientific budget exhausted')
        case_protocol = dict(p, mechanisms=[law['mechanism']])
        config = {'mode': 'science', 'law': law, 'protocol': case_protocol, 'caps': CAPS}
        # Source equality is checked before execution, not after seeing a result.
        current = [{'path': r['path'], 'bytes': (ROOT/r['path']).stat().st_size,
                    'sha256': hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()} for r in sources_at_calibration]
        if current != sources_at_calibration:
            raise RuntimeError('Scientific source differs from physical calibration')
        record, data = execute(config, law['id'], [BASE+'/PROTOCOL.json', BASE+'/CALIBRATION.json'])
        status['laws'][law['id']] = record
        atomic_json(path, status)
        print(json.dumps({'law': law['id'], **record['profile']}), flush=True)
        if data is None:
            return 1
        flux = data['stationary'][law['mechanism']]['resource_work']
        if abs(flux-law['target']) > p['match_tolerance']:
            raise ArithmeticError('Scientific accepted work misses the frozen target')
        atomic_json(DOC/'laws'/(law['id']+'.json'), data)
    status['status'] = 'complete'
    atomic_json(path, status)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['calibration', 'prepare', 'science'])
    raise SystemExit(globals()[parser.parse_args().mode]())
