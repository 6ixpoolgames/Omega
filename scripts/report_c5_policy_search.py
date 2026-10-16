"""Verify and report complete physical-controller searches without midpoint ranks."""
import csv
import hashlib
import json
from math import isfinite
from itertools import combinations
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.reactive_allocation import policies
from omega_v2.testbed.workflow.manifest import verify_bundle

DOC = ROOT/'docs/research_notes/lushness_testbed/c5_policy_search'
LOCAL = ROOT/'results/local_runs/lushness_testbed/c5_policy_search'


def archive_sources():
    """Include the specification/tests actually hashed with the numerical code."""
    manifests = sorted(LOCAL.glob('*/manifest.json'))
    packets = {}
    for path in manifests:
        manifest = json.loads(path.read_text())
        payload = {r['path']: (path.parent/'source'/r['path']).read_bytes() for r in manifest['sources']}
        if any(hashlib.sha256(payload[r['path']]).hexdigest() != r['sha256'] for r in manifest['sources']):
            raise RuntimeError('Source archive input changed')
        digest = hashlib.sha256(b''.join(p.encode()+b'\0'+payload[p] for p in sorted(payload))).hexdigest()
        packets[digest] = payload
    folder = DOC/'source_archives'
    folder.mkdir(exist_ok=True)
    records = []
    for digest, payload in sorted(packets.items()):
        path = folder/(digest+'.zip')
        if not path.exists():
            with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as stream:
                for name, data in sorted(payload.items()):
                    info = zipfile.ZipInfo(name, date_time=(2026, 10, 16, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    stream.writestr(info, data)
        with zipfile.ZipFile(path) as stream:
            if {p: stream.read(p) for p in stream.namelist()} != payload:
                raise RuntimeError('Source archive bytes changed')
        records.append({'source_hash': digest, 'files': len(payload),
                        'archive': path.relative_to(DOC).as_posix(), 'bytes': path.stat().st_size,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'contains_kernels_or_run_dumps': False})
    (DOC/'SOURCE_ARCHIVES.json').write_text(json.dumps(records, indent=2)+'\n', encoding='utf-8')


def write_csv(path, rows):
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, keys)
        writer.writeheader()
        writer.writerows(rows)


def allowance(result, cadence, horizon):
    return 1e-5+2*horizon/float(cadence)*result['cadences'][cadence]['poisson_residual']


def possible_maxima(scores, subject, tolerances):
    lower = max(row['subjects'][subject]['lower_bits']-tolerances[key] for key, row in scores.items())
    return sorted(key for key, row in scores.items()
                  if row['subjects'][subject]['upper_bits']+tolerances[key] >= lower)


def main():
    status = json.loads((DOC/'SURVEY_STATUS.json').read_text())
    plan = json.loads((DOC/'SURVEY_PLAN.json').read_text())
    expected = {p.id for p in policies()}
    tables = {p.id: list(p.responses) for p in policies()}
    if (status['status'] != 'complete' or len(status['cases']) != len(expected)
            or {c['id'] for c in status['cases']} != expected):
        raise RuntimeError('Complete declared controller family is required')
    if {c['id'] for c in plan['cases']} != expected or status['source_hash'] != plan['source_hash']:
        raise RuntimeError('Plan or frozen numerical source changed')
    results, max_residual, metrics = {}, 0., []
    for receipt in status['cases']:
        if receipt['status'] != 'complete':
            raise RuntimeError('Incomplete policy')
        measured = receipt['profile']
        caps = receipt['configuration']['caps']
        if (measured['exit_code'] or measured['cap_reason']
                or measured['peak_job_bytes'] > caps['memory']
                or measured['wall_seconds'] > caps['seconds']+2
                or measured['output_bytes'] > caps['output_cap']):
            raise RuntimeError('Execution did not respect its caps')
        path = DOC/'cases'/(receipt['identity']+'.json')
        if hashlib.sha256(path.read_bytes()).hexdigest() != receipt['result_sha256']:
            raise RuntimeError('Result checksum mismatch')
        bundle = verify_bundle(receipt['run'])
        if bundle['config'] != receipt['configuration']:
            raise RuntimeError('Frozen configuration mismatch')
        result = json.loads(path.read_text())
        if not result['imports_from_snapshot'] or result['case'] != receipt['id']:
            raise RuntimeError('Source import or identity error')
        if (receipt['configuration']['controller']['responses'] != tables[receipt['id']]
                or result['metadata']['policy']['responses'] != tables[receipt['id']]):
            raise RuntimeError('Executed table differs from the declared family')
        snapshot = Path(receipt['run'])/'source'
        if any(not Path(p).is_relative_to(snapshot) for p in result['imported_source_paths'].values()):
            raise RuntimeError('Import escaped source snapshot')
        residuals = [result['stationary_residual'], result['energy_residual']]
        for clock in result['cadences'].values():
            residuals += [clock['poisson_residual'], clock['kernel_diagnostics']['kernel_mass'],
                          clock['kernel_diagnostics']['negative_probability']]
            residuals += [r['sampled_occupation_residual'] for r in clock['profiles'].values()]
            for row in clock['profiles'].values():
                if not isfinite(row['global_bits']) or row['global_bits'] < -1e-7:
                    raise ArithmeticError('Invalid full-history entropy')
                for bound in row['subjects'].values():
                    lo, hi = bound['lower_bits'], bound['upper_bits']
                    if (not isfinite(lo) or not isfinite(hi) or lo < -1e-7
                            or lo > hi+1e-7 or hi > row['global_bits']+1e-7):
                        raise ArithmeticError('Invalid marginal-history bounds')
        for row in result['physical'].values():
            residuals += [row['occupation_residual'], abs(row['integrated_energy_residual']),
                          *row['owned_energy_residual'].values()]
        if any(not isfinite(v) for v in residuals) or max(map(abs, residuals)) > 1e-7:
            raise ArithmeticError('Numerical acceptance limit exceeded')
        max_residual = max(max_residual, max(map(abs, residuals)))
        results[receipt['id']] = result
        metrics.append({'id': receipt['id'], **measured, 'result_sha256': receipt['result_sha256']})
    if len({r['states'] for r in results.values()}) != 1:
        raise RuntimeError('Policies do not share a state space')
    if any(r['metadata']['parameters'] != results['hold__hold']['metadata']['parameters'] for r in results.values()):
        raise RuntimeError('Physics parameters changed between controller tables')
    whole_rows, choices, comparisons, physical, pairwise = [], [], [], [], []
    constant = {p.id for p in policies() if len(set(p.responses)) == 1}
    reference = results['hold__hold']
    for cadence, clock in reference['cadences'].items():
        for time in clock['profiles']:
            horizon = float(time)
            scores = {k: r['cadences'][cadence]['profiles'][time] for k, r in results.items()}
            tolerances = {k: allowance(r, cadence, horizon) for k, r in results.items()}
            maximum = max(row['global_bits'] for row in scores.values())
            winners = sorted(k for k, row in scores.items() if maximum-row['global_bits'] <= tolerances[k])
            constants = max(constant, key=lambda k: scores[k]['global_bits'])
            adaptive = max(set(scores)-constant, key=lambda k: scores[k]['global_bits'])
            possible = {sub: possible_maxima(scores, sub, tolerances) for sub in ('D', 'S')}
            choices.append({'cadence': float(cadence), 'horizon': horizon, 'whole_maximizers': winners,
                'whole_maximum_bits': maximum, 'best_constant': constants, 'best_nonconstant': adaptive,
                'best_nonconstant_minus_best_constant': scores[adaptive]['global_bits']-scores[constants]['global_bits'],
                'D_possible_maximizers': possible['D'], 'S_possible_maximizers': possible['S'],
                'subject_sets_are_outer_sets': True})
            base = scores['hold__hold']
            for key, row in scores.items():
                report = {'id': key, 'cadence': float(cadence), 'horizon': horizon,
                    'global_bits': row['global_bits'], 'limiting_full_rate': results[key]['cadences'][cadence]['limiting_rate'],
                    'whole_maximizer': key in winners, 'D_possible_maximizer': key in possible['D'],
                    'S_possible_maximizer': key in possible['S'], 'allowance_bits': tolerances[key]}
                delta = {'id': key, 'cadence': float(cadence), 'horizon': horizon, 'reference': 'hold__hold',
                         'whole_delta': row['global_bits']-base['global_bits'],
                         'tolerance_bits': tolerances[key]+tolerances['hold__hold']}
                for sub in ('D', 'S'):
                    bounds, bb = row['subjects'][sub], base['subjects'][sub]
                    report[sub+'_lower'] = bounds['lower_bits']
                    report[sub+'_upper'] = bounds['upper_bits']
                    rate_bounds = results[key]['cadences'][cadence]['subject_rate_bounds'][sub]
                    report[sub+'_rate_lower'] = rate_bounds['lower_bits_per_time']
                    report[sub+'_rate_upper'] = rate_bounds['upper_bits_per_time']
                    delta[sub+'_lower'] = bounds['lower_bits']-bb['upper_bits']
                    delta[sub+'_upper'] = bounds['upper_bits']-bb['lower_bits']
                    if key == 'hold__hold':
                        delta[sub+'_lower'] = delta[sub+'_upper'] = 0.
                whole_rows.append(report)
                comparisons.append(delta)
            for a, b in combinations(sorted(scores), 2):
                left, right = scores[a], scores[b]
                eps = tolerances[a]+tolerances[b]
                row = {'id': a, 'reference': b, 'cadence': float(cadence), 'horizon': horizon,
                       'whole_delta': left['global_bits']-right['global_bits'], 'tolerance_bits': eps}
                for sub in ('D', 'S'):
                    row[sub+'_lower'] = left['subjects'][sub]['lower_bits']-right['subjects'][sub]['upper_bits']
                    row[sub+'_upper'] = left['subjects'][sub]['upper_bits']-right['subjects'][sub]['lower_bits']
                row['D_whole_opposition'] = ((row['D_lower'] > eps and row['whole_delta'] < -eps)
                    or (row['D_upper'] < -eps and row['whole_delta'] > eps))
                row['D_S_opposition'] = ((row['D_lower'] > eps and row['S_upper'] < -eps)
                    or (row['D_upper'] < -eps and row['S_lower'] > eps))
                pairwise.append(row)
    temporal = []
    for key in results:
        for horizon in (16., 64., 256., 1024.):
            rows = sorted((r for r in comparisons if r['id'] == key and r['horizon'] == horizon),
                          key=lambda r: r['cadence'])
            signs = [('positive' if r['whole_delta'] > r['tolerance_bits'] else
                      'negative' if r['whole_delta'] < -r['tolerance_bits'] else 'unresolved') for r in rows]
            temporal.append({'id': key, 'horizon': horizon, 'whole_sign_flip': 'positive' in signs and 'negative' in signs,
                **{str(r['cadence']): sign for r, sign in zip(rows, signs)}})
    for key, result in results.items():
        for time, row in result['physical'].items():
            physical.append({'id': key, 'horizon': float(time), 'expected_jumps': row['expected_jumps'],
                'temporal_finite_bits': row['finite_term_bits'],
                **{'ledger.'+k: v for k, v in row['ledger'].items()},
                **{'deadline.'+k: v for k, v in row['deadline'].items()},
                **{'average.'+k: v for k, v in row['average'].items()}})
    write_csv(DOC/'SCORES.csv', whole_rows)
    write_csv(DOC/'COMPARISONS.csv', comparisons)
    write_csv(DOC/'PHYSICAL.csv', physical)
    write_csv(DOC/'TEMPORAL_SIGNS.csv', temporal)
    write_csv(DOC/'PAIRWISE.csv', pairwise)
    choices.sort(key=lambda row: (row['horizon'], row['cadence']))
    (DOC/'CHOICE_SETS.json').write_text(json.dumps(choices, indent=2)+'\n', encoding='utf-8')
    aliases = {}
    for key, result in results.items():
        aliases.setdefault(result['kernel_sha256'], []).append(key)
    archive_sources()
    archived = json.loads((DOC/'SOURCE_ARCHIVES.json').read_text())
    if status['source_hash'] not in {r['source_hash'] for r in archived}:
        raise RuntimeError('Numerical source archive is missing')
    validation = {'complete_policies': len(results), 'expected_policies': len(expected),
        'unique_kernels': len(aliases), 'maximum_checked_residual': max_residual,
        'source_hash': status['source_hash'], 'receipts_caps_imports_checked': True,
        'peak_job_bytes': max(m['peak_job_bytes'] for m in metrics),
        'sum_worker_wall_seconds_not_cpu': sum(m['wall_seconds'] for m in metrics),
        'batch_elapsed_seconds': status['elapsed_seconds'],
        'aliases': [v for v in aliases.values() if len(v) > 1],
        'artifacts': {name: hashlib.sha256((DOC/name).read_bytes()).hexdigest()
                      for name in ('SCORES.csv', 'COMPARISONS.csv', 'PHYSICAL.csv', 'CHOICE_SETS.json', 'TEMPORAL_SIGNS.csv', 'PAIRWISE.csv', 'SOURCE_ARCHIVES.json')}}
    (DOC/'VALIDATION.json').write_text(json.dumps(validation, indent=2)+'\n', encoding='utf-8')
    lines = ['# Exhaustive reactive allocation: results', '',
        f"All {len(results)} declared tables completed; {len(aliases)} distinct physical kernels.",
        f"Maximum checked residual {max_residual:.3g}; peak worker {validation['peak_job_bytes']/2**20:.1f} MiB.", '',
        'Finite whole-history lushness is primary. D/S values bound actual marginal histories.',
        'Possible subject maximizers are outer sets; overlapping intervals do not resolve a winner.',
        'Policies differ in hardwired apparatus-dependent control, with the same paid selector and physical substrate.', '',
        '| T | Cadence | Whole winner (response at 1 / 2 units) | Gain vs hold | Best nonconstant minus best constant | D possible | S possible |',
        '| ---: | ---: | --- | ---: | ---: | ---: | ---: |']
    for choice in choices:
        dt, time = str(choice['cadence']), str(int(choice['horizon']))
        baseline = reference['cadences'][dt]['profiles'][time]['global_bits']
        lines.append(f"| {choice['horizon']:g} | {choice['cadence']:g} | {', '.join(choice['whole_maximizers'])} | {choice['whole_maximum_bits']-baseline:+.6f} | {choice['best_nonconstant_minus_best_constant']:+.6f} | {len(choice['D_possible_maximizers'])} | {len(choice['S_possible_maximizers'])} |")
    lines += ['', '## Full policy map at T256, cadence 0.25', '',
        '| Policy | Whole gain vs hold | D gain interval | S gain interval | Net transfer to D | D energy change vs hold | S energy change vs hold |',
        '| --- | ---: | --- | --- | ---: | ---: | ---: |']
    for row in sorted((r for r in comparisons if r['horizon'] == 256 and r['cadence'] == .25), key=lambda r: -r['whole_delta']):
        p, b = results[row['id']]['physical']['256'], reference['physical']['256']
        lines.append(f"| {row['id']} | {row['whole_delta']:+.6f} | [{row['D_lower']:+.4f}, {row['D_upper']:+.4f}] | [{row['S_lower']:+.4f}, {row['S_upper']:+.4f}] | {p['ledger'].get('pump_transport_D',0):+.6f} | {p['deadline']['D.owned_energy']-b['deadline']['D.owned_energy']:+.6f} | {p['deadline']['S.owned_energy']-b['deadline']['S.owned_energy']:+.6f} |")
    lines += ['', '## Scope', '',
        'All policies include the same physical registers; hold still permits autonomous selector relaxation.',
        'Constant tables command a target rather than pinning the selector. No abstract action-label entropy is counted.',
        'Material gains, net flow and breadth are separate. Donating/extracting mode names do not establish actual net direction.',
        'This fixed-contact count assay includes paid transfer, production and their combination, but no spatial confinement, irreversible harm, discovery or certified conscious valuers.',
        'A whole-field rate difference across policies is not a same-generator root advantage. No unbounded asymptotic moral priority is used.',
        'The three-cadence map is temporal sensitivity evidence, not invariance across state grains.',
        'SCORES.csv preserves every policy, horizon and cadence; PHYSICAL.csv preserves full signed resource/event ledgers.',
        f"PAIRWISE.csv retains {len(pairwise)} pair/clock/horizon comparisons; {sum(r['D_whole_opposition'] for r in pairwise)} have certified D/whole opposition and {sum(r['D_S_opposition'] for r in pairwise)} have certified D/S opposition. These counts are comparisons, not independent observations or domination verdicts.",
        f"TEMPORAL_SIGNS.csv flags {sum(r['whole_sign_flip'] for r in temporal)} policy/horizon sign reversals against hold across the three cadences.",
        'Matching realized work or activity is a diagnostic follow-up, not a restriction imposed on the primary optimizer.', '']
    (DOC/'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(validation))


if __name__ == '__main__':
    main()
