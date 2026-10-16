"""Prospective oracle scores with physical cost and population readouts."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    from omega_v2.testbed.workflow.manifest import verify_bundle
    folder = ROOT/'docs/research_notes/lushness_testbed/controlled_feedback'
    status = json.loads((folder/'SCIENCE_STATUS.json').read_text())
    if status['status'] != 'complete':
        raise ValueError('Complete science required')
    run = Path(status['run']); manifest = verify_bundle(run)
    result = json.loads((run/'result.json').read_text())
    protocol = manifest['config']['protocol']
    if result['input_hash'] != manifest['input_hash'] or [c['case'] for c in result['cases']] != protocol['cases']:
        raise ValueError('Frozen case mismatch')
    primary = next(c for c in result['cases'] if c['case']['capacity'] == 2 and c['case']['cadence'] == .25)
    def constant(row):
        return len({tuple(v) for v in row['responses'][1:]}) == 1
    best_constant = max(r['bits']['64'] for r in primary['rows'] if constant(r))
    best = max(r['bits']['64'] for r in primary['rows'])
    byid = {r['id']:r for r in primary['rows']}
    identities = [primary['winners'][str(t)] for t in protocol['horizons']]
    maxstock = max(r['active64'] for r in primary['rows'])
    signs = []
    for case in result['cases']:
        if case['case']['capacity'] != 2:
            continue
        rows = {r['id']: r for r in case['rows']}
        reference = max(r['bits']['64'] for r in rows.values() if constant(r))
        for pid in primary['winners']['64']:
            delta = rows[pid]['bits']['64']-reference
            signs.append({'policy':pid,'cadence':case['case']['cadence'],'gain_over_best_constant':delta})
    findings = {'O1': any(ids != identities[0] for ids in identities[1:]),
                'O2': best-best_constant > 1e-8,
                'S1': any(x['gain_over_best_constant'] > 1e-8 for x in signs)
                      and any(x['gain_over_best_constant'] < -1e-8 for x in signs),
                'M1': any(byid[pid]['active64'] < maxstock-1e-8 for pid in primary['winners']['64'])}
    summary = {'findings': findings, 'cases': result['cases'], 'cadence_signs': signs,
               'protocol': protocol, 'profile': status['profile'],'input_hash': result['input_hash']}
    (folder/'SUMMARY.json').write_text(json.dumps(summary,separators=(',',':'),allow_nan=False)+'\n')
    lines = ['# First oracle-controlled feedback results','',
             'Full-model evaluator, restricted apparatus-count stationary controllers. No uncertainty, receding horizon or abstract action entropy.', '',
             '| Capacity | Cadence | T1 | T4 | T16 | T64 | T256 |', '|---:|---:|---|---|---|---|---|']
    for c in result['cases']:
        winners = [' / '.join(c['winners'][str(t)]) for t in protocol['horizons']]
        lines.append(f"| {c['case']['capacity']} | {c['case']['cadence']} | "+' | '.join(winners)+' |')
    lines += ['', 'Registered outcomes: '+', '.join(f'{k}={v}' for k,v in findings.items()), '',
              'False O1/O2 means the predicted horizon-dependent/state-dependent advantage was not found.',
              'False S1/M1 means those registered alerts did not fire.', '',
              'Controller names identify forward command channels, not achieved gate position. Physical reverse actuation returns carriers and is accounted separately.',
              'Construction is paired and gate-dependent, so gate occupancy changes both construction and deconstruction. Stock gains cannot be attributed to repair alone.',
              'All native thermal branching, bodily wear, failure and reverse channels remain in the objective.', '']
    (folder/'RESULTS.md').write_text('\n'.join(lines))
    print(json.dumps(findings))


if __name__ == '__main__':
    main()
