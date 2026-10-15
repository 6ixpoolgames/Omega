"""Frozen capped engineering, integration and scientific cyclic experiments."""
import argparse
import hashlib
import json
import os
import sys
import uuid
from datetime import UTC, datetime
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle
from omega_v2.testbed.workflow.runner import run_frozen

BASE = 'docs/research_notes/lushness_testbed/robust_generativity'
DOC = ROOT/BASE


def sources():
    return ([p.relative_to(ROOT).as_posix() for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
            + ['omega_v2/__init__.py', 'scripts/run_bng_binding_calibration.py',
               'scripts/run_robust_generativity.py', 'scripts/robust_generativity_worker.py',
               'scripts/robust_generativity_science.py',
               'scripts/report_robust_generativity.py',
               'tests/test_generativity_experiment.py',
               'tests/test_robust_generativity.py', BASE+'/ENGINEERING_PROTOCOL.json',
               BASE+'/PROPOSED_SPEC_r1.md', BASE+'/PROTOCOL_DRAFT_r1.json', BASE+'/MONITOR_CONTRACT.md'])


def run_case(config, name):
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out = ROOT/'results/local_runs/lushness_testbed/robust_generativity'/f'{name}-{stamp}'
    freeze_bundle(ROOT, out, sources(), config)
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    profile = run_frozen(out, 'scripts/robust_generativity_worker.py', [str(out)], config['caps'])
    complete = profile['exit_code'] == 0 and not profile['cap_reason']
    status = {'status': 'complete' if complete else 'incomplete', 'run': str(out), 'profile': profile}
    atomic_json(DOC/(name+'_STATUS.json'), status)
    # Retain receipts for failed attempts too; never overwrite frozen runs.
    atomic_json(out/'PROFILE.json', status)
    if complete and (out/'RESULTS.json').exists():
        atomic_json(DOC/(name+'_RESULTS.json'), json.loads((out/'RESULTS.json').read_text()))
    print(json.dumps(status, indent=2), flush=True)
    if not complete:
        print((out/'worker.log').read_text(encoding='utf-8')[-6000:])
    return complete


def proposed_protocol():
    from omega_v2.testbed.robust_generativity import MECHANISMS, GenerativityParameters
    draft = json.loads((DOC/'PROTOCOL_DRAFT_r1.json').read_text())
    protocol = {'status': 'integration_not_scientific', 'date': '2026-10-15',
        'measurement': draft['measurement'], 'markers': draft['proposed_markers'],
        'tolerances': draft['proposed_tolerances'], 'funding_diagnostic': draft['funding_diagnostic'],
        'max_kernel_bytes': 160*1024**2,
        'caps': {'seconds': 120, 'memory': 512*1024**2, 'output_cap': 32*1024**2},
        'batch_budgets_seconds': {'shape': 2400, 'robustness': 3600},
        'budget_basis': 'pre-freeze complete high-stress integration profile ~62 seconds; original proposal budgets were provisional; per-case caps unchanged',
        'reference_rule': 'same H7, D0; conditional known-root average, no root-draw entropy',
        'decomposition': 'packet,bank,D,A,B,C next-state chain rule given full past physical state; T256 at dt.25',
        'physical_profiles': 'stocks, flows, uptime and activity at all five horizons; first arrival at16/64/256',
        'pulse_convention': 'T64 score/occupancy just before deterministic pulse; all later scores include prefix and post-pulse history',
        'robustness_definition': 'R=post-startup loop uptime>=.5 and closure<=.1; actual pulse arms also require conditional recovery>=.8 and joint prefunction/recovery>=.5 at delay64',
        'compounding_definition': 'C=depth3>=.01 AND depth3+retainedexpansion>=.01; funded C additionally external-spent lowerbound>=.8 and all thermal-forward birth share<=.05',
        'joint_definition': 'J requires funded C,R,and strict positive T256 difference across all cadences; strong J adds depthby64+loop64+expanded256+no closure>=.01',
        'undefined_recovery': 'no actual pulse: recovery clause not applicable, not counted as a recovery pass',
        'rate_role': 'diagnostic only; finite-history lushness primary',
        'predictions': {
            'P1': 'some shape setting C and full retained-expansion probability exceeds each of three individual link cuts at T256',
            'P2': 'some alpha.5 shape setting C',
            'P3': 'at fixed anchors irreversible damage raises closure and lowers recovery: compare R1/R3/R6 closure and R4/R5 joint recovery',
            'P4': 'at least one pulse anchor full improves joint prefunction+endpoint restoration over C-to-A cut at delay64',
            'P5': 'some full setting funded C/R and positive seed-minus-thermal at T256 at every cadence; unbound scored separately',
            'P6': 'some full setting funded C/R and positive full-minus-alloff AND full-minus-C-to-A-cut at T256 at every cadence',
            'P7a': 'per fixed anchor, Spearman association across seven stresses is positive between tau_up and full-minus-alloff and seed-minus-unbound T256 differences; descriptive, not a theorem',
            'P7b': 'not run: separate opportunity-window freeze required'},
        'sign_rule': 'delta>bits_tolerance+both numerical residual allowances; no cadence selecting or activity subtraction',
        'error_allowance': 'T/dt*PoissonResidual + .5*T^2*harmonicResidual + 1e-7; solver allowance, not a formal interval proof',
        'scope': 'coarse three-type chemistry; not spatial gas, valuers, open-ended growth or an ethical verdict',
        'followups': draft['deferred_separate_freezes'],
        'cases': [], 'settings': []}
    case_by_key = {}

    def setting(identity, batch, parameters, mechanisms, pulse=False, **labels):
        row = {'id': identity, 'batch': batch, 'pulse': pulse, **labels, 'case_ids': {}}
        for mechanism in mechanisms:
            key = json.dumps([vars(parameters), mechanism, pulse], sort_keys=True)
            if key not in case_by_key:
                case_id = 'case-'+hashlib.sha256(key.encode()).hexdigest()[:14]
                case_by_key[key] = case_id
                protocol['cases'].append({'id': case_id, 'batch': batch,
                    'parameters': vars(parameters), 'mechanism': mechanism, 'pulse': pulse})
            row['case_ids'][mechanism] = case_by_key[key]
        protocol['settings'].append(row)

    for alpha, strength, supply in product((.5, 1.), (.1, 1.), (.15, .6, 2.4)):
        p = GenerativityParameters(feedback_exponent=alpha, assistance_multiplier=strength, supply_rate=supply)
        setting(f'A-a{alpha:g}-k{strength:g}-s{supply:g}', 'shape', p, MECHANISMS,
                alpha=alpha, strength=strength, supply=supply)
    for alpha, supply in product((.5, 1.), (.15, .6)):
        for stress in draft['robustness_batch']['stress_settings']:
            p = GenerativityParameters(feedback_exponent=alpha, supply_rate=supply,
                damage_rate=stress['damage'], irreversible_fraction=stress['irreversible_fraction'])
            setting(f'B-a{alpha:g}-s{supply:g}-{stress["id"]}', 'robustness', p,
                    ('full', 'all_assistance_off', 'cut_C_to_A'), stress['pulse'],
                    alpha=alpha, supply=supply, stress=stress['id'])
    return protocol


def integration():
    protocol = proposed_protocol()
    case = {'id': 'max-workload-calibration', 'parameters': {
        'capacity': 6, 'irreversible_fraction': .25, 'damage_rate': .08,
        'supply_rate': 2.4}, 'mechanism': 'full', 'pulse': True}
    return 0 if run_case({'mode': 'integration', 'case': case, 'protocol': protocol,
                         'caps': protocol['caps']}, 'INTEGRATION') else 1


def prepare():
    from omega_v2.testbed.workflow.manifest import verify_bundle
    for gate in ('TESTS', 'INTEGRATION'):
        receipt = json.loads((DOC/(gate+'_STATUS.json')).read_text())
        if receipt['status'] != 'complete':
            raise RuntimeError('Tests and full integration profile required before freeze')
        manifest = verify_bundle(receipt['run'])
        if any(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest() != r['sha256'] for r in manifest['sources']):
            raise RuntimeError('Source changed since validation; rerun affected gate')
    target = DOC/'PROTOCOL.json'
    if target.exists():
        raise FileExistsError('Do not replace a scientific freeze')
    protocol = proposed_protocol()
    protocol['status'] = 'frozen_before_scientific_ranking'
    protocol['source_hashes'] = {r['path']: r['sha256'] for r in manifest['sources']}
    atomic_json(target, protocol)
    print(json.dumps({'status': protocol['status'], 'settings': len(protocol['settings']),
                      'unique_cases': len(protocol['cases'])}))
    return 0


def science():
    protocol = json.loads((DOC/'PROTOCOL.json').read_text())
    if protocol['status'] != 'frozen_before_scientific_ranking':
        raise RuntimeError('Scientific freeze required')
    for path, digest in protocol['source_hashes'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != digest:
            raise RuntimeError('Source changed after freeze')
    path = DOC/'SCIENCE_STATUS.json'
    status = json.loads(path.read_text()) if path.exists() else {'cases': {}, 'status': 'running'}
    for case in protocol['cases']:
        if status['cases'].get(case['id'], {}).get('status') == 'complete':
            continue
        used = sum(r['profile']['wall_seconds'] for cid, r in status['cases'].items()
                   if next(c['batch'] for c in protocol['cases'] if c['id'] == cid) == case['batch'])
        if used+protocol['caps']['seconds'] > protocol['batch_budgets_seconds'][case['batch']]:
            status.update(status='budget_limited', pending=case['id']); atomic_json(path, status)
            raise RuntimeError('Frozen batch budget exhausted before next full case')
        stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
        out = ROOT/'results/local_runs/lushness_testbed/robust_generativity'/f'{case["id"]}-{stamp}'
        config = {'mode': 'science', 'case': case, 'protocol': protocol, 'caps': protocol['caps']}
        frozen = freeze_bundle(ROOT, out, sources()+[BASE+'/PROTOCOL.json'], config)
        if {r['path']: r['sha256'] for r in frozen['sources'] if r['path'] != BASE+'/PROTOCOL.json'} != protocol['source_hashes']:
            raise RuntimeError('Snapshot differs from validated source')
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
        profile = run_frozen(out, 'scripts/robust_generativity_worker.py', [str(out)], protocol['caps'])
        complete = profile['exit_code'] == 0 and not profile['cap_reason']
        receipt = {'status': 'complete' if complete else 'incomplete', 'run': str(out), 'profile': profile}
        status['cases'][case['id']] = receipt
        atomic_json(out/'PROFILE.json', receipt)
        if complete:
            atomic_json(DOC/'cases'/(case['id']+'.json'), json.loads((out/'RESULTS.json').read_text()))
        atomic_json(path, status)
        print(json.dumps({'case': case['id'], 'completed': sum(r['status'] == 'complete' for r in status['cases'].values()),
                          'total': len(protocol['cases']), **profile}), flush=True)
        if not complete:
            print((out/'worker.log').read_text(encoding='utf-8')[-5000:])
            return 1
    status['status'] = 'complete'; atomic_json(path, status)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['tests', 'engineering', 'integration', 'prepare', 'science'])
    args = parser.parse_args()
    if args.mode in ('integration', 'prepare', 'science'):
        return globals()[args.mode]()
    protocol = json.loads((DOC/'ENGINEERING_PROTOCOL.json').read_text())
    if protocol['status'] != 'engineering_only_no_scientific_ranking':
        raise RuntimeError('Engineering protocol required')
    jobs = ([{'id': 'TESTS', 'mode': 'tests'}] if args.mode == 'tests' else protocol['jobs'])
    for job in jobs:
        config = {**protocol, **job}
        if not run_case(config, job['id']):
            return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
