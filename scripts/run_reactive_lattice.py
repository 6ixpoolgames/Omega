"""Frozen/capped calibration and scientific execution for the same-law test."""
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

BASE = 'docs/research_notes/lushness_testbed/same_law_gas'
DOC = ROOT/BASE


def sources():
    return ([p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
            + ['omega_v2/__init__.py', 'scripts/run_bng_binding_calibration.py',
               'scripts/run_reactive_lattice.py', 'scripts/reactive_lattice_worker.py',
               'scripts/reactive_lattice_science.py', BASE+'/SPEC.md'])


def run_case(config, name, source_files=None):
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out = ROOT/'results/local_runs/lushness_testbed/same_law_gas'/f'{name}-{stamp}'
    freeze_bundle(ROOT, out, source_files or sources(), config)
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    profile = run_frozen(out, 'scripts/reactive_lattice_worker.py', [str(out)], config['caps'])
    complete = profile['exit_code'] == 0 and not profile['cap_reason']
    status = {'status': 'complete' if complete else 'incomplete', 'run': str(out), 'profile': profile}
    atomic_json(DOC/(name+'_STATUS.json'), status)
    if complete:
        atomic_json(DOC/(name+'_RESULTS.json'), json.loads((out/'RESULTS.json').read_text()))
    print(json.dumps(status, indent=2), flush=True)
    return complete


def engineering():
    config = {'mode': 'engineering', 'geometries': [[4, 2], [6, 4], [7, 6], [8, 6]],
              'beta_grid': [.5, 1.5, 3.], 'kernel_profile': True,
              'max_kernel_bytes': 160*1024**2,
              'caps': {'seconds': 120, 'memory': 512*1024**2, 'output_cap': 32*1024**2}}
    return 0 if run_case(config, 'ENGINEERING') else 1


def prepare():
    gate = json.loads((DOC/'ENGINEERING_STATUS.json').read_text())
    if gate['status'] != 'complete':
        raise RuntimeError('Capped engineering gate required')
    engineering_sources = verify_bundle(gate['run'])['sources']
    if any(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest() != r['sha256']
           for r in engineering_sources):
        raise RuntimeError('Engineering sources changed; rerun smoke before freeze')
    if (DOC/'PROTOCOL.json').exists():
        raise FileExistsError('Never replace frozen protocol')
    from omega_v2.testbed.reactive_lattice import LatticeParameters
    laws = []
    for beta in (.5, 1.5, 3.):
        for mobility in (.25, 1.):
            for assistance in ('native', 'weak'):
                p = LatticeParameters(sites=7, monomers=6, beta=beta, mobility=mobility,
                    assisted_build=.02 if assistance == 'native' else 0.,
                    assisted_capture=.1 if assistance == 'native' else 0.)
                laws.append({'id': f'N6-L7-b{beta:g}-m{mobility:g}-{assistance}',
                             'parameters': vars(p), 'scope': 'three-assembly finite geometry'})
    for assistance in ('native', 'weak'):
        p = LatticeParameters(assisted_build=.02 if assistance == 'native' else 0.,
                              assisted_capture=.1 if assistance == 'native' else 0.)
        laws.append({'id': f'N4-L6-b3-m0.5-{assistance}', 'parameters': vars(p),
                     'scope': 'second-assembly pilot'})
    protocol = {'status': 'frozen_before_scientific_ranking', 'date': '2026-10-15',
        'laws': laws, 'roots': 'occupied sites0..N-1; bond0-1; carrier0; charge0; packet1; H4',
        'references': ['thermal_equal_H4', 'unbound_equal_H4', 'arrangement_one_bond_charge0_packet1'],
        'reference_average': 'mean conditional known-root entropy; no entropy of drawing root',
        'horizons': [16, 64, 256, 1024], 'cadences': [.25, .125, .5],
        'primary_horizon': 64, 'primary_cadence': .25,
        'targets': {'G1': 'at least one bond', 'G2': 'carrier at source with bond endpoint within distance1',
                    'G3': 'at least two simultaneous bonds; native paid/thermal flows separate'},
        'tolerances': {'bits': 1e-5, 'numerical_residual': 1e-7, 'rate': 1e-8},
        'predictions': {
            'P_access': {'law': 'N6-L7-b3-m0.25-native', 'reference': 'thermal',
                         'claim': 'positive offset and positive T64 difference at all three cadences'},
            'P_diversity': {'law': 'N6-L7-b0.5-m1-weak', 'reference': 'thermal',
                            'claim': 'negative offset or negative T64 difference at all three cadences'}},
        'independent_outputs': ['paid recursive enabling', 'retained assembly', 'breadth against each reference'],
        'calibration_rule': 'retain entire predetermined beta/mobility corridor; no outcome-based point selection',
        'caps': {'seconds': 120, 'memory': 512*1024**2, 'output_cap': 32*1024**2},
        'max_kernel_bytes': 160*1024**2, 'total_seconds': 1800,
        'density': 'dense thermal mixture; no dilute-gas claim',
        'offset_scope': 'one irreducible native Q per setting, common root rate',
        'coarse_state_grain': 'future observation bounds; no projected count CTMC used',
        'excluded': ['Rule A', 'semantic bonuses', 'discarding negative signs', 'holding reference disordered']}
    atomic_json(DOC/'PROTOCOL.json', protocol)
    print('Protocol frozen after capped calibration; no preparation ranking inspected')
    return 0


def science():
    protocol = json.loads((DOC/'PROTOCOL.json').read_text())
    gate = json.loads((DOC/'ENGINEERING_STATUS.json').read_text())
    original = verify_bundle(gate['run'])['sources']
    status_path = DOC/'SCIENCE_STATUS.json'
    status = json.loads(status_path.read_text()) if status_path.exists() else {'laws': {}}
    for law in protocol['laws']:
        if status['laws'].get(law['id'], {}).get('status') == 'complete':
            continue
        used = sum(r['profile']['wall_seconds'] for r in status['laws'].values())
        if used+protocol['caps']['seconds'] > protocol['total_seconds']:
            raise RuntimeError('Insufficient frozen total budget for complete next law')
        config = {'mode': 'science', 'law': law, 'protocol': protocol, 'caps': protocol['caps']}
        stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
        out = ROOT/'results/local_runs/lushness_testbed/same_law_gas'/f"science-{law['id']}-{stamp}"
        manifest = freeze_bundle(ROOT, out, sources()+[BASE+'/PROTOCOL.json'], config)
        if [r for r in manifest['sources'] if r['path'] != BASE+'/PROTOCOL.json'] != original:
            raise RuntimeError('Science differs from calibrated source bytes')
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
        profile = run_frozen(out, 'scripts/reactive_lattice_worker.py', [str(out)], protocol['caps'])
        complete = profile['exit_code'] == 0 and not profile['cap_reason']
        status['laws'][law['id']] = {'status': 'complete' if complete else 'incomplete', 'run': str(out),
                                    'profile': profile}
        if complete:
            data = json.loads((out/'RESULTS.json').read_text())
            atomic_json(DOC/'laws'/(law['id']+'.json'), data)
        atomic_json(status_path, status)
        print(json.dumps({'law': law['id'], **profile}), flush=True)
        if not complete:
            return 1
    status['status'] = 'complete'
    atomic_json(status_path, status)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['engineering', 'prepare', 'science'])
    raise SystemExit(globals()[parser.parse_args().mode]())
