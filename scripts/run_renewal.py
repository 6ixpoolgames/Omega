"""Per-law capped calibration and source-identical renewal frontier batches."""
import argparse
import json
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.aversive_signals import SignalParameters
from omega_v2.testbed.exploration import ExplorationParameters
from omega_v2.testbed.paid_sensing import SensorParameters
from omega_v2.testbed.renewal import RenewalParameters
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle, verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen

BASE = 'docs/research_notes/lushness_testbed/renewal'
DOC = ROOT/BASE
PLAN, REG, SPEC = BASE+'/MATCHING_PLAN.json', BASE+'/PROTOCOL.json', BASE+'/SPEC.md'


def sources(extra):
    return ([p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
            + ['omega_v2/__init__.py', 'scripts/run_bng_binding_calibration.py', 'scripts/run_renewal.py', SPEC, *extra])


def outpath(mode, law):
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    return ROOT/'results/local_runs/lushness_testbed/renewal'/(f'{mode}-{law}-'+stamp)


def laws():
    rows = []
    for cap, supplies, wears in ((1, [.15, .3, .6, 1.2, 2.4], [.02, .08]), (2, [.3, .6, 1.2], [.02])):
        for supply in supplies:
            for wear in wears:
                name = f'C{cap}-s{supply:g}-w{wear:g}'
                row = {'id': name, 'kind': 'primary', 'parent': None,
                       'physiology': vars(SignalParameters(signal_upkeep=.02, struggle_cost=.5)),
                       'parameters': vars(ExplorationParameters(supply_rate=supply, contrast=.8, coupling=0.)),
                       'sensor': vars(SensorParameters()),
                       'renewal': vars(RenewalParameters(capacity=cap, wear_rate=wear)),
                       'roots': [[8, 1, 0, 1, 1, 0, 1], [8, 1, 0, 1, 0, 1, 1]]}
                if supply == .6 and wear == .02:
                    row['preparation_roots'] = [[e, 1, 0, 1, *stocks, a] for stocks in ((1, 0), (0, 1)) for e, a in ((6, 1), (8, 0))]
                rows.append(row)
    for row in list(rows):
        if row['renewal']['wear_rate'] == .02 and row['parameters']['supply_rate'] in (.3, .6, 1.2):
            cap = row['renewal']['capacity']
            rows.append({**row, 'id': row['id']+('-repair0' if cap == 1 else '-gamma0'),
                         'kind': 'repair_ablation' if cap == 1 else 'autocatalysis_ablation', 'parent': row['id'],
                         'renewal': {**row['renewal'], **({'repair_enabled': False} if cap == 1 else {'autocatalytic_gain': 0.})}})
    return rows


def calibrate():
    engineering = json.loads((DOC/'ENGINEERING_STATUS.json').read_text(encoding='utf-8'))
    if engineering['status'] != 'complete':
        raise RuntimeError('Both-capacity engineering profile required')
    if (ROOT/PLAN).exists():
        plan = json.loads((ROOT/PLAN).read_text(encoding='utf-8'))
    else:
        plan = {'status': 'frozen_before_moment_fitting', 'date': '2026-10-14', 'laws': laws(),
                'horizon': 64., 'relative_tolerance': 1e-6, 'history_entropy_used': False,
                'fit_reference': 'zero coupling, two primary roots',
                'ablation_matching': 'replay parent controller; no intervention refit',
                'caps': {'seconds': 120, 'memory': 512*1024**2, 'output_cap': 64*1024**2}}
        atomic_json(ROOT/PLAN, plan)
    status_path = DOC/'CALIBRATION_STATUS.json'
    statuses = json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else {'laws': {}}
    for law in plan['laws']:
        if law['kind'] != 'primary' or statuses['laws'].get(law['id'], {}).get('status') == 'complete':
            continue
        out = outpath('calibration', law['id'])
        freeze_bundle(ROOT, out, sources([PLAN, 'scripts/renewal_calibration_worker.py']),
                      {'mode': 'physical_calibration', 'law': law, 'plan': plan})
        execution = run_frozen(out, 'scripts/renewal_calibration_worker.py', [str(out)], plan['caps'])
        atomic_json(out/'PROFILE.json', execution)
        success = execution['exit_code'] == 0 and not execution['cap_reason']
        statuses['laws'][law['id']] = {'status': 'complete' if success else 'incomplete', 'run': str(out), 'profile': execution}
        atomic_json(status_path, statuses)
        print(json.dumps({'law': law['id'], **execution}), flush=True)
        if not success:
            return 1
    statuses['status'] = 'complete'
    atomic_json(status_path, statuses)
    return 0


def prepare():
    if (ROOT/REG).exists():
        raise FileExistsError('Scientific protocol already frozen')
    plan = json.loads((ROOT/PLAN).read_text(encoding='utf-8'))
    statuses = json.loads((DOC/'CALIBRATION_STATUS.json').read_text(encoding='utf-8'))
    if statuses.get('status') != 'complete':
        raise RuntimeError('Complete calibration required')
    fits = {}
    for law in plan['laws']:
        if law['kind'] != 'primary':
            continue
        gate = statuses['laws'][law['id']]
        manifest = verify_bundle(gate['run'])
        fit = json.loads((Path(gate['run'])/'MATCHING_RESULTS.json').read_text(encoding='utf-8'))
        if fit['input_hash'] != manifest['input_hash'] or not fit['fit']['success']:
            raise RuntimeError('Unverified moment fit')
        fits[law['id']] = fit
    rows = []
    for law in plan['laws']:
        fit = fits[law['parent'] or law['id']]['fit']
        rows.append({**law, 'sensor': {**law['sensor'], 'noise_on': fit['noise_on'], 'noise_retain': fit['noise_retain']}})
    protocol = {'id': 'paid-renewal-frontier', 'version': '1', 'date': '2026-10-14',
        'status': 'frozen_before_scientific_ranking', 'laws': rows, 'calibration_fits': fits,
        'arms': ['R0', 'I0', 'RX', 'IX'], 'coupling': 4.,
        'pairs': [['IX', 'R0'], ['IX', 'RX'], ['I0', 'R0'], ['IX', 'I0'], ['RX', 'R0']],
        'horizons': [16, 64, 256, 1024], 'cadences': [.125, .25, .5],
        'primary_horizon': 64, 'primary_cadence': .25,
        'coordinate_order': [3, 4, 5, 0, 1, 2, 6], 'hidden_fields': [0, 1, 3, 4, 5, 6],
        'horizon_query_maximum': 4096, 'horizon_probe_estimate_multipliers': [.5, 1., 2.],
        'operating_marker': {'stationary_functionality': .05, 'paid_construction_rate': 1e-4},
        'tolerances': {'bits': 1e-5, 'rate': 1e-8, 'residual': 1e-8, 'physical': 1e-6},
        'predictions': {'U1': 'some interior capacity1 primary supply has pooled IX-R0 positive at all cadences T64',
                        'U2': 'positive capacity1 region bounded by nonpositive supply endpoints at T64 primary cadence',
                        'U3': 'high wear has fewer positive capacity1 primary supply points',
                        'U4': 'paid repair has more positive points than repair ablation at the three low-wear supplies',
                        'U5': 'capacity2 records ongoing hardware-assisted second-unit construction; compare gamma0'},
        'T6': 'completed temporal_profile/RESULTS.md; analytic estimate plus exact verification',
        'physical_temporal_band': None, 'scope': 'capacity1 sustenance, capacity2 bounded expansion; neither compounding against gas',
        'caps': {'seconds': 180, 'memory': 512*1024**2, 'output_cap': 64*1024**2}}
    atomic_json(ROOT/REG, protocol)
    print(ROOT/REG)


def run(mode, requested):
    p = json.loads((ROOT/REG).read_text(encoding='utf-8'))
    if p['status'] != 'frozen_before_scientific_ranking':
        raise RuntimeError('Frozen protocol required')
    chosen = [v for v in p['laws'] if requested in ('all', v['id'])]
    if not chosen:
        raise ValueError('Unknown frozen law')
    if mode == 'smoke':
        chosen = [v for v in chosen if v['id'] in ('C1-s0.6-w0.02', 'C2-s0.6-w0.02')]
    status_path = DOC/f'{mode.upper()}_STATUS.json'
    statuses = json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else {'laws': {}}
    for law in chosen:
        if statuses['laws'].get(law['id'], {}).get('status') == 'complete':
            continue
        if mode == 'science':
            smoke = json.loads((DOC/'SMOKE_STATUS.json').read_text(encoding='utf-8'))
            smoke_id = f"C{law['renewal']['capacity']}-s0.6-w0.02"
            gate = smoke['laws'][smoke_id]
            if gate['status'] != 'complete' or verify_bundle(gate['run'])['config']['protocol'] != p:
                raise RuntimeError('Source-identical smoke required for capacity')
        out = outpath(mode, law['id'])
        manifest = freeze_bundle(ROOT, out, sources([REG, 'scripts/renewal_worker.py']),
                                {'mode': mode, 'law': law, 'protocol': p})
        if mode == 'science' and manifest['source_hash'] != verify_bundle(gate['run'])['source_hash']:
            raise RuntimeError('Source changed since smoke')
        execution = run_frozen(out, 'scripts/renewal_worker.py', [str(out), mode],
                              {**p['caps'], 'seconds': 120 if mode == 'smoke' else p['caps']['seconds']})
        atomic_json(out/'PROFILE.json', execution)
        success = execution['exit_code'] == 0 and not execution['cap_reason']
        statuses['laws'][law['id']] = {'status': 'complete' if success else 'incomplete', 'run': str(out), 'profile': execution}
        atomic_json(status_path, statuses)
        print(json.dumps({'law': law['id'], **execution}), flush=True)
        if not success:
            return 1
    statuses['status'] = 'complete' if len(statuses['laws']) == (2 if mode == 'smoke' else len(p['laws'])) else 'partial'
    atomic_json(status_path, statuses)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('calibrate', 'prepare', 'smoke', 'science'))
    parser.add_argument('--law', default='all')
    args = parser.parse_args()
    raise SystemExit(calibrate() if args.mode == 'calibrate' else prepare() if args.mode == 'prepare' else run(args.mode, args.law))
