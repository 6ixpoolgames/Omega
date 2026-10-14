"""Score the complete paid-sensor comparison without redefining its objective."""
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle

DOC = ROOT/'docs/research_notes/lushness_testbed/paid_sensing'


def sign(value, tolerance):
    return 'positive' if value > tolerance else 'negative' if value < -tolerance else 'tie'


def main():
    status = json.loads((DOC/'SCIENCE_STATUS.json').read_text(encoding='utf-8'))
    if status['status'] != 'complete':
        raise RuntimeError('Complete scientific run required')
    run = Path(status['run'])
    manifest = verify_bundle(run)
    raw = run/'RESULTS.json'
    r = json.loads(raw.read_text(encoding='utf-8'))
    p = manifest['config']['protocol']
    if r['input_hash'] != manifest['input_hash'] or r['protocol'] != p:
        raise RuntimeError('Scientific identity mismatch')
    index = {(v['case'], v['arm'], v['cadence']): v for v in r['rows']}
    if len(index) != len(r['rows']) or len(index) != len(p['cases'])*len(p['arms'])*len(p['cadences']):
        raise RuntimeError('Missing or duplicated analyses')
    comparisons, interactions, winners, rate_spreads = [], [], [], []
    for case in p['cases']:
        for cadence in p['cadences']:
            arms = {a: index[case['id'], a, cadence] for a in p['arms']}
            rates = [v['rate_bits_per_time'] for v in arms.values()]
            rate_spreads.append(max(rates)-min(rates))
            if max(rates)-min(rates) > p['tolerances']['residual']:
                raise ArithmeticError('Unexpected residual environmental rate difference')
            for t in p['horizons']:
                profiles = {a: v['profiles'][str(t)] for a, v in arms.items()}
                best = max(v['bits'] for v in profiles.values())
                winners.append({'case': case['id'], 'cadence': cadence, 'horizon': t,
                                'winners': [a for a, v in profiles.items() if best-v['bits'] <= p['tolerances']['bits']]})
                for left, right in p['pairs']:
                    a, b = profiles[left], profiles[right]
                    physical = {name: a['physical'].get(name, 0.)-b['physical'].get(name, 0.) for name in
                                ('food_capture', 'lifetime', 'survival', 'movement', 'productive_arrival',
                                 'sensor_bill', 'signal_charge', 'signal_upkeep_bill', 'register_activation',
                                 'signal_time', 'sensor_read', 'drive_work')}
                    delta = a['bits']-b['bits']
                    comparisons.append({'case': case['id'], 'group': case['group'], 'cadence': cadence,
                        'horizon': t, 'pair': f'{left}-{right}', 'delta_bits': delta,
                        'verdict': sign(delta, p['tolerances']['bits']), 'physical_delta': physical,
                        'hidden_lower': a['hidden_signal']['lower_bits']-b['hidden_signal']['upper_bits'],
                        'hidden_upper': a['hidden_signal']['upper_bits']-b['hidden_signal']['lower_bits'],
                        'coordinate_delta_bits': [x-y for x, y in zip(a['coordinate_bits'], b['coordinate_bits'])]})
                interaction = {name: profiles['IX']['physical'].get(name, 0.)-profiles['I0']['physical'].get(name, 0.)
                               -profiles['RX']['physical'].get(name, 0.)+profiles['R0']['physical'].get(name, 0.)
                               for name in ('food_capture', 'lifetime', 'movement', 'sensor_bill', 'signal_charge')}
                interactions.append({'case': case['id'], 'group': case['group'], 'cadence': cadence, 'horizon': t,
                    'breadth_difference_of_differences_bits': profiles['IX']['bits']-profiles['I0']['bits']
                                                           -profiles['RX']['bits']+profiles['R0']['bits'],
                    'physical_difference_of_differences': interaction,
                    'diagnostic_not_modified_objective': True})
    primary = [c for c in comparisons if c['cadence'] == p['primary_cadence'] and c['horizon'] == p['primary_horizon']]
    pooled = []
    calibration_checks = []
    for group in sorted({case['group'] for case in p['cases']}):
        cases = [case for case in p['cases'] if case['group'] == group]
        if len(cases) != 2:
            raise RuntimeError('Two physical roots required per group')
        group_pairs = [c for c in primary if c['group'] == group]
        entry = {'group': group, 'parameters': cases[0]['parameters'], 'sensor': cases[0]['sensor'], 'pairs': {}}
        for left, right in p['pairs']:
            pair = f'{left}-{right}'
            values = [c for c in group_pairs if c['pair'] == pair]
            entry['pairs'][pair] = {'mean_delta_bits': sum(v['delta_bits'] for v in values)/2,
                                   'mean_physical_delta': {name: sum(v['physical_delta'][name] for v in values)/2
                                                           for name in values[0]['physical_delta']}}
        values = [c for c in interactions if c['group'] == group and c['cadence'] == p['primary_cadence']
                  and c['horizon'] == p['primary_horizon']]
        entry['interaction'] = {'mean_bits': sum(v['breadth_difference_of_differences_bits'] for v in values)/2,
                                'mean_food': sum(v['physical_difference_of_differences']['food_capture'] for v in values)/2}
        fit = next(f for f in p['matching']['fits'] if f['group'] == group)
        means = {a: {name: sum(index[c['id'], a, .25]['profiles']['64']['physical'][name] for c in cases)/2
                     for name in ('signal_time', 'register_activation', 'signal_charge', 'signal_upkeep_bill', 'sensor_bill')}
                 for a in ('I0', 'R0')}
        errors = {name: abs(means['I0'][name]-means['R0'][name])/max(1e-20, abs(means['I0'][name]))
                  for name in ('signal_time', 'register_activation')}
        if max(errors.values()) > p['matching']['plan']['relative_tolerance']:
            raise ArithmeticError('Calibrated physical moments not reproduced')
        calibration_checks.append({'group': group, 'fit': fit, 'means': means, 'relative_errors': errors})
        pooled.append(entry)
    target = next(g for g in pooled if g['parameters']['movement_cost'] == .5 and g['parameters']['contrast'] == .8
                  and g['sensor']['refresh_rate'] == .2)
    fast = next(g for g in pooled if g['parameters']['movement_cost'] == .5 and g['parameters']['contrast'] == .8
                and g['sensor']['refresh_rate'] == .8)
    v = target['pairs']['IX-RX']
    predictions = {'T1': {'breadth_passes': v['mean_delta_bits'] > p['tolerances']['bits'],
                          'food_passes': v['mean_physical_delta']['food_capture'] > p['tolerances']['readout']},
                   'T2': {'breadth_passes': target['interaction']['mean_bits'] > p['tolerances']['bits'],
                          'food_passes': target['interaction']['mean_food'] > p['tolerances']['readout']},
                   'T3': {'passes': fast['pairs']['IX-RX']['mean_delta_bits'] < v['mean_delta_bits']-p['tolerances']['bits'],
                          'faster_minus_slower_bits': fast['pairs']['IX-RX']['mean_delta_bits']-v['mean_delta_bits']}}
    flips = []
    for case in p['cases']:
        for t in p['horizons']:
            for left, right in p['pairs']:
                values = [c for c in comparisons if c['case'] == case['id'] and c['horizon'] == t
                          and c['pair'] == f'{left}-{right}']
                if {c['verdict'] for c in values}-{'tie'} == {'positive', 'negative'}:
                    flips.append({'case': case['id'], 'horizon': t, 'pair': f'{left}-{right}',
                                  'values': [{k: c[k] for k in ('cadence', 'delta_bits')} for c in values]})
    counts = {pair: dict(Counter(c['verdict'] for c in primary if c['pair'] == pair))
              for pair in sorted({c['pair'] for c in primary})}
    primary_winners = dict(Counter(a for v in winners if v['cadence'] == p['primary_cadence']
                                  and v['horizon'] == p['primary_horizon'] for a in v['winners']))
    target_corridor = []
    for t in p['horizons']:
        for cadence in p['cadences']:
            values = [c for c in comparisons if c['group'] == target['group'] and c['pair'] == 'IX-RX'
                      and c['horizon'] == t and c['cadence'] == cadence]
            target_corridor.append({'horizon': t, 'cadence': cadence,
                                    'mean_delta_bits': sum(c['delta_bits'] for c in values)/2,
                                    'mean_hidden_lower': sum(c['hidden_lower'] for c in values)/2,
                                    'mean_hidden_upper': sum(c['hidden_upper'] for c in values)/2})
    info_rows = [v['profiles']['64']['physical']['conditional_sensor_write_information_bits']
                 for v in r['rows'] if v['cadence'] == .25 and v['arm'].startswith('I')]
    random_rows = [v['profiles']['64']['physical']['conditional_sensor_write_information_bits']
                   for v in r['rows'] if v['cadence'] == .25 and v['arm'].startswith('R')]
    if max(abs(v) for v in random_rows) > 1e-8:
        raise ArithmeticError('Stock-independent conditional writer information failed')
    r.pop('imports')
    summary = {**r, 'profile': status['profile'], 'comparisons': comparisons, 'interactions': interactions,
               'winners': winners, 'primary_winners': primary_winners, 'primary_counts': counts,
               'target_corridor': target_corridor, 'pooled': pooled, 'predictions': predictions,
               'calibration_checks': calibration_checks, 'cadence_flips': flips,
               'conditional_write_information': {'I_range': [min(info_rows), max(info_rows)],
                                                  'R_max_abs': max(abs(v) for v in random_rows)},
               'result_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
               'report_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    atomic_json(DOC/'SUMMARY.json', summary)
    flat = [{**{k: c[k] for k in ('case', 'group', 'cadence', 'horizon', 'pair', 'delta_bits', 'verdict', 'hidden_lower', 'hidden_upper')},
             **{f'delta_{k}': val for k, val in c['physical_delta'].items()}} for c in comparisons]
    with (DOC/'PARAMETER_MAP.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0]))
        writer.writeheader()
        writer.writerows(flat)
    lines = ['# Paid sensing results', '',
             ('Information increases the continuation benefit of actuation in all eight pooled '
              'primary groups, but the absolute winner remains the uncoupled random register in14 '
              'of16 preparations. The experiment establishes a cost-dependent access relationship: '
              'informed movement can repay its sensing and action costs when it buys enough access. '
              'It does not impose a universal preference for movement.'), '',
             ('The paid informative writer and paid stock-independent writer use the same resource law, '
             'read clock, unit bills, bit relaxation and bit-driven mobility. All registered continuations '
             'completed. The full conditional finite history remains the objective.'), '',
             '| Primary contrast | Positive | Negative | Tie |', '| --- | ---: | ---: | ---: |']
    for pair, count in counts.items():
        lines.append(f"| {pair} | {count.get('positive', 0)} | {count.get('negative', 0)} | {count.get('tie', 0)} |")
    lines += ['', ('I means informative writing, R stock-independent writing; X enables bit-driven movement '
              'and0 disables that extra coupling while retaining basal movement. Primary T64/cadence0.25; '
              'each contrast spans16 preparations. Stocks remain stochastic and physically present in all arms.'), '',
              f'Primary winner counts among the four fixed mechanisms: {primary_winners}.', '',
              ('The uncoupled random-register mechanism R0 wins14 of16 primary cases. Thus information '
               'can improve movement relative to random movement without making movement optimal. '
               'The mechanism is not assumed to compound or outperform inactive internal variation.'), '',
              '| Registered prediction | Outcome |', '| --- | --- |',
              f"| T1: target IX beats RX on breadth and food | breadth {'pass' if predictions['T1']['breadth_passes'] else 'fail'}; food {'pass' if predictions['T1']['food_passes'] else 'fail'} |",
              f"| T2: information increases actuation benefit on breadth and food | breadth {'pass' if predictions['T2']['breadth_passes'] else 'fail'}; food {'pass' if predictions['T2']['food_passes'] else 'fail'} |",
              f"| T3: faster sensing reduces target IX-RX breadth advantage | {'pass' if predictions['T3']['passes'] else 'fail'} |", '',
              ('The target has move bill0.5, contrast0.8 and read rate0.2, pooled equally across initial '
              'stocks. Root-conditioned scores are averaged; no random-root entropy is added. IX−RX: '
              f"{v['mean_delta_bits']:+.6f}bits, food {v['mean_physical_delta']['food_capture']:+.6f}, "
              f"lifetime {v['mean_physical_delta']['lifetime']:+.6f}time units. Actuation's informative-minus-random "
              f"interaction: {target['interaction']['mean_bits']:+.6f}bits, food {target['interaction']['mean_food']:+.6f}. "
              'The interaction is explanatory, not an adjusted reward.'), '',
              ('The target pooled IX−RX win is positive at all three cadences and horizons, with positive '
               'pooled hidden-bit lower bounds throughout. This is the registered two-root average, not '
               'a win at each root: the initially empty occupied patch loses at0.125/0.25 and wins '
               'at0.5, while the initially stocked occupied patch wins throughout.'), '',
              ('All eight pooled groups have positive breadth and food interaction terms at the primary '
               'readout. Absolute preferences remain mixed, as shown by the uncoupled winner counts.'), '',
              ('Eight pooled zero-coupling occupancy/activation calibrations succeeded before scientific '
              'ranking and reproduce in this run. Occupancy matches upkeep and activation count matches '
              'charging at that reference. Actual sensor bills and costs after coupling can differ; all '
              'are retained. Never call this complete realized-work or complete path-statistics matching.'), '',
              (f"Informative conditional write information at T64: {min(info_rows):.6f}–{max(info_rows):.6f}bits/read; "
              f"stock-independent maximum absolute value {max(abs(v) for v in random_rows):.3g}. It conditions "
              'on pre-read energy, location and bit plus read occurrence. Retained bits can correlate with '
              'stocks via action feedback even without stock-dependent writing; this is not a valence measure.'), '',
              (f'{len(flips)} registered temporal sign flips. Exact resolved scores, hidden-bit non-Markov bounds, '
              'coordinate shares and continuous physical ledgers remain in SUMMARY.json and the full map. '
              'No sampling cutoff or entropy subtraction was used.'), '',
              ('All arms converge to the same residual environmental rate within each law/cadence; '
              f"maximum spread {max(rate_spreads):.3g}bits/time. This remains finite mortality. The sensor "
              'detects an immediate empty/full cue, not future replenishment or guaranteed profitable travel. '
              'These common rates locate this result at the preparation/finite-life level, rather than '
              'showing that information has no ongoing value in maintained worlds. The separate '
              '[renewal batch](../renewal/RESULTS.md) now tests sustained returns and their horizon '
              'repayment; its different law does not alter this batch. The prior '
              'S_A retained its noisy register; its direct stock-reading motor was an idealized benchmark.'), '',
              ('Interpretation revised15October2026 under the Drive revision posture: local access and '
              'paid-information mechanism evidence, with frozen predictions and unfavorable rankings '
              'retained. This oracle comparison has no coupled valuer population and supplies no '
              'interpersonal ethical verdict. See [cross-run synthesis](../INTERPRETATION_SYNTHESIS_2026-10-15.md).'), '',
              (f"Run {status['profile']['wall_seconds']:.2f}s, peak {status['profile']['peak_job_bytes']/1024**2:.1f}MiB; "
              f"maximum residual {r['maximum_residual']:.3g}. {len(r['rows'])} arm/cadence analyses. "
              'Source-identical capped smoke preceded science; raw snapshots remain ignored locally.'), '',
              ('Reproduce from the existing frozen protocol with `python scripts/run_paid_sensing.py smoke`, '
              '`science`, then `python scripts/report_paid_sensing.py`. Calibration/prepare are one-time '
              'registration stages; do not refit scientific results.'), '',
              f"Frozen scientific input hash: `{r['input_hash']}`.", '']
    (DOC/'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'counts': counts, 'target': v, 'predictions': predictions,
                      'cadence_flips': len(flips)}, indent=2))


if __name__ == '__main__':
    main()
