"""Compact prospective feedback scoring; full original rows remain visible."""
import json
from pathlib import Path


def summarize(folder):
    from omega_v2.testbed.workflow.manifest import verify_bundle
    status = json.loads((folder/'SCIENCE_STATUS.json').read_text())
    if status['status'] != 'complete':
        raise ValueError('Complete capped science required')
    run = Path(status['run'])
    manifest = verify_bundle(run)
    result = json.loads((run/'result.json').read_text())
    if result.get('input_hash') != manifest['input_hash']:
        raise ValueError('Result does not belong to the verified frozen run')
    protocol = manifest['config']['protocol']
    if result['status'] != 'complete' or [r['case'] for r in result['rows']] != protocol['cases']:
        raise ValueError('Results do not match frozen prospective cases')
    rows = result['rows']

    def row(capacity, drive, mode, cadence):
        matches = [r for r in rows if r['case']['parameters']['apparatus_capacity'] == capacity
                   and r['case']['parameters']['inflow_enabled'] == drive
                   and r['case']['parameters']['feedback'] == mode
                   and r['case']['cadence'] == cadence]
        if len(matches) != 1:
            raise ValueError('Missing or duplicate matched row')
        return matches[0]

    deltas = []
    dark_spreads = []
    for capacity in (1, 2):
        for cadence in (.125, .25, .5):
            a, b, u = (row(capacity, True, mode, cadence) for mode in ('catalytic', 'absent', 'uncatalytic'))
            deltas.append({'capacity': capacity, 'cadence': cadence,
                           'catalytic_minus_absent_rate': a['rates']['organized']-b['rates']['organized'],
                           'uncatalytic_minus_catalytic_rate': u['rates']['organized']-a['rates']['organized']})
            rates = [row(capacity, False, mode, cadence)['rates']['organized']
                     for mode in ('catalytic', 'uncatalytic', 'absent')]
            dark_spreads.append(max(rates)-min(rates))
    a, b = (row(1, True, mode, .25) for mode in ('catalytic', 'absent'))
    claims = {
        'F1': all(r['catalytic_minus_absent_rate'] > 1e-10 for r in deltas if r['capacity'] == 1),
        'F2': a['stationary_apparatus'] > b['stationary_apparatus']+1e-10
              and a['recovery_endpoint64'] > b['recovery_endpoint64']+1e-10,
        'F3': a['stationary_flows']['net_feedback_fuel'] > 1e-10,
        'D1': max(dark_spreads) < 1e-10}
    summary = {'claims': claims, 'deltas': deltas, 'max_dark_rate_spread': max(dark_spreads),
               'profile': status['profile'], 'input_hash': result['input_hash'],
               'protocol': protocol, 'rows': rows,
               'fuel_replacement_ratio_primary': a['stationary_flows']['net_feedback_fuel']
                                                 /a['stationary_flows']['access_fuel_cost']}
    output = folder/'report'
    output.mkdir(exist_ok=True)
    (output/'SUMMARY.json').write_text(json.dumps(summary, separators=(',', ':'), allow_nan=False)+'\n')
    lines = ['# Bounded resource feedback results', '',
             'Frozen mechanism comparison; no controller optimization or ethical verdict.', '',
             '| Capacity | Mode | History bits T64 | Mean active | Recovery endpoint T64 |',
             '|---:|---|---:|---:|---:|']
    for capacity in (1, 2):
        for mode in ('catalytic', 'uncatalytic', 'absent'):
            r = row(capacity, True, mode, .25)
            lines.append(f"| {capacity} | {mode} | {r['bits']['64']['organized']:.6f} | {r['stationary_apparatus']:.6f} | {r['recovery_endpoint64']:.6f} |")
    lines += ['', '## Rate contrasts across cadences', '',
              '| Capacity | Cadence | Catalytic minus absent | Uncatalytic minus catalytic |',
              '|---:|---:|---:|---:|']
    for d in deltas:
        lines.append(f"| {d['capacity']} | {d['cadence']} | {d['catalytic_minus_absent_rate']:.6f} | {d['uncatalytic_minus_catalytic_rate']:.6f} |")
    lines += ['', 'Frozen predictions: '+', '.join(f'{key}: {"passed" if value else "failed"}' for key, value in claims.items()), '',
              'Every native thermal pathway is retained in every arm. Boundary prescriptions match; accepted work can differ.',
              ('The uncatalytic control wins these breadth contrasts. The catalytic route replaces only '
              f"{summary['fuel_replacement_ratio_primary']*100:.2f}% of net access fuel expenditure in the primary regime. "
              'Thermal carrier excitation remains consequential; autonomous upkeep is unconfirmed.'),
              'Population growth is limited to available precursor slots. Composition tests certify independent products and costed coupling, not cross-scale agency.', '']
    (output/'RESULTS.md').write_text('\n'.join(lines))
    return summary


if __name__ == '__main__':
    import sys
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    summary = summarize(root/'docs/research_notes/lushness_testbed/resource_feedback')
    print(json.dumps({'claims': summary['claims'], 'fuel_replacement_ratio': summary['fuel_replacement_ratio_primary']}))
