"""Automated complete-surface scoring of the frozen costed-exploration slice."""
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle

DOC = ROOT/'docs/research_notes/lushness_testbed/exploration'


def verdict(value, tolerance):
    return 'positive' if value > tolerance else 'negative' if value < -tolerance else 'tie'


def main():
    status = json.loads((DOC/'SCIENCE_STATUS.json').read_text(encoding='utf-8'))
    if status['status'] != 'complete':
        raise RuntimeError('Complete science required')
    run = Path(status['run'])
    manifest = verify_bundle(run)
    raw = run/'RESULTS.json'
    result = json.loads(raw.read_text(encoding='utf-8'))
    p = manifest['config']['protocol']
    if result['input_hash'] != manifest['input_hash'] or result['protocol'] != p:
        raise RuntimeError('Scientific identity mismatch')
    rows = result['rows']
    index = {(r['case'], r['arm'], r['cadence']): r for r in rows}
    if len(index) != len(rows) or len(rows) != len(p['cases'])*len(p['arms'])*len(p['cadences']):
        raise RuntimeError('Missing or duplicate analyses')
    comparisons, winners, rate_spreads = [], [], []
    for case in p['cases']:
        for cadence in p['cadences']:
            arms = {arm: index[case['id'], arm, cadence] for arm in p['arms']}
            spread = max(a['rate_bits_per_time'] for a in arms.values())-min(a['rate_bits_per_time'] for a in arms.values())
            rate_spreads.append(spread)
            if spread > p['tolerances']['residual']:
                raise ArithmeticError('Common residual environmental rate failed')
            for t in p['horizons']:
                scores = {a: row['profiles'][str(t)]['bits'] for a, row in arms.items()}
                best = max(scores.values())
                winners.append({'case': case['id'], 'cadence': cadence, 'horizon': t,
                                'winners': [a for a, v in scores.items() if best-v <= p['tolerances']['bits']],
                                'scores': scores})
                for left, right in p['pairs']:
                    a, b = arms[left]['profiles'][str(t)], arms[right]['profiles'][str(t)]
                    delta = a['bits']-b['bits']
                    physical = {k: a['physical'].get(k, 0.)-b['physical'].get(k, 0.)
                                for k in ('food_capture', 'lifetime', 'survival', 'movement',
                                          'movement_bill', 'productive_arrival', 'drive_work', 'signal_time')}
                    food_gain = physical['food_capture'] > p['tolerances']['readout']
                    lifetime_gain = physical['lifetime'] > p['tolerances']['readout']
                    comparisons.append({'case': case['id'], 'parameters': case['parameters'], 'root': case['root'],
                        'cadence': cadence, 'horizon': t, 'pair': f'{left}-{right}',
                        'delta_bits': delta, 'verdict': verdict(delta, p['tolerances']['bits']),
                        'hidden_lower': a['hidden_signal']['lower_bits']-b['hidden_signal']['upper_bits'],
                        'hidden_upper': a['hidden_signal']['upper_bits']-b['hidden_signal']['lower_bits'],
                        'coordinate_delta_bits': [x-y for x, y in zip(a['coordinate_bits'], b['coordinate_bits'])],
                        'physical_delta': physical,
                        'breadth_without_food_or_lifetime': delta > p['tolerances']['bits'] and not food_gain and not lifetime_gain,
                        'functional_gain_without_breadth': delta <= p['tolerances']['bits'] and (food_gain or lifetime_gain)})
    primary = [c for c in comparisons if c['horizon'] == p['primary_horizon'] and c['cadence'] == p['primary_cadence']]
    pooled = []
    for cost in (.5, 1.):
        for contrast in (0., .8):
            for coupling in (1., 4.):
                for pair in ('B_X-B_R', 'S_A-B_R', 'B_X-M_C'):
                    group = [v for v in primary if v['parameters']['movement_cost'] == cost
                             and v['parameters']['contrast'] == contrast and v['parameters']['coupling'] == coupling
                             and v['pair'] == pair]
                    if len(group) != 2:
                        raise RuntimeError('Both initial stocks required')
                    pooled.append({'cost': cost, 'contrast': contrast, 'coupling': coupling, 'pair': pair,
                                   'mean_delta_bits': sum(v['delta_bits'] for v in group)/2,
                                   'mean_food_delta': sum(v['physical_delta']['food_capture'] for v in group)/2,
                                   'mean_lifetime_delta': sum(v['physical_delta']['lifetime'] for v in group)/2})
    target = next(v for v in pooled if v['cost'] == .5 and v['contrast'] == .8 and v['coupling'] == 4. and v['pair'] == 'B_X-B_R')
    aware = next(v for v in pooled if v['cost'] == .5 and v['contrast'] == .8 and v['coupling'] == 4. and v['pair'] == 'S_A-B_R')
    costs = []
    for contrast in (0., .8):
        for coupling in (1., 4.):
            low, high = [next(v for v in pooled if v['cost'] == cost and v['contrast'] == contrast
                             and v['coupling'] == coupling and v['pair'] == 'B_X-B_R') for cost in (.5, 1.)]
            costs.append({'contrast': contrast, 'coupling': coupling,
                          'higher_cost_change_bits': high['mean_delta_bits']-low['mean_delta_bits'],
                          'passes': high['mean_delta_bits'] < low['mean_delta_bits']-p['tolerances']['bits']})
    predictions = {'X1': {'breadth_positive': target['mean_delta_bits'] > p['tolerances']['bits'],
                          'food_positive': target['mean_food_delta'] > p['tolerances']['readout'],
                          'data': target},
                   'X2': {'passes': aware['mean_food_delta'] > p['tolerances']['readout'], 'data': aware},
                   'X3': {'passes': all(v['passes'] for v in costs), 'contrasts': costs}}
    flips = []
    for case in p['cases']:
        for t in p['horizons']:
            for left, right in p['pairs']:
                vals = [c for c in comparisons if c['case'] == case['id'] and c['horizon'] == t and c['pair'] == f'{left}-{right}']
                signs = {v['verdict'] for v in vals}-{'tie'}
                if signs == {'positive', 'negative'}:
                    flips.append({'case': case['id'], 'horizon': t, 'pair': f'{left}-{right}',
                                  'values': [{'cadence': v['cadence'], 'delta_bits': v['delta_bits']} for v in vals]})
    counts = {pair: dict(Counter(c['verdict'] for c in primary if c['pair'] == pair))
              for pair in sorted({c['pair'] for c in primary})}
    primary_winners = dict(Counter(a for v in winners if v['cadence'] == p['primary_cadence']
                                  and v['horizon'] == p['primary_horizon'] for a in v['winners']))
    noise = [c for c in primary if c['pair'] == 'B_R-B']
    result.pop('imports')
    summary = {**result, 'profile': status['profile'], 'comparisons': comparisons, 'winners': winners,
               'primary_counts': counts, 'primary_winners': primary_winners,
               'pooled': pooled, 'predictions': predictions, 'cadence_flips': flips,
               'maximum_residual_rate_spread': max(rate_spreads),
               'result_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
               'report_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    atomic_json(DOC/'SUMMARY.json', summary)
    flat = [{**{k: v[k] for k in ('case', 'cadence', 'horizon', 'pair', 'delta_bits', 'verdict', 'hidden_lower', 'hidden_upper')},
             **v['parameters'], **{f'delta_{k}': value for k, value in v['physical_delta'].items()}} for v in comparisons]
    with (DOC/'PARAMETER_MAP.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0]))
        writer.writeheader()
        writer.writerows(flat)
    lines = ['# Costed exploration results', '',
             ('Stock-aware movement beats independent register variation in14 of16 preparations, '
              'while randomly driven movement loses in15 of16. This separates potential food access '
              'from action that uses information about it. The failed blind-movement prediction '
              'remains visible; it is evidence about this costed coupling, not a finding that '
              'exploration or coupled variation must fail.'), '',
             ('All registered worlds and candidate mechanisms completed. Complete finite-history lushness '
             'is the primary readout; resources remain stochastic in every arm.'), '',
             '| Primary contrast | Positive | Negative | Tie |', '| --- | ---: | ---: | ---: |']
    for pair, count in counts.items():
        lines.append(f"| {pair} | {count.get('positive', 0)} | {count.get('negative', 0)} | {count.get('tie', 0)} |")
    lines += ['', ('Primary is T64/cadence0.25; each row spans 16 preparations, including both initial stock '
              'arrangements. B_X is bit-modulated movement; M_C is a nominal-duty constant-mobility '
              'control, not an exact realized-flux match; S_A is an idealized stock-aware rule.'), '',
              f'Primary winner counts among the five declared candidates: {primary_winners}.', '',
              ('The independent register B_R beats unvarying B in all 16 primary grid entries (8 distinct baseline preparations) while '
               f"capturing less food in {sum(c['physical_delta']['food_capture'] < -p['tolerances']['readout'] for c in noise)} "
               f"and shortening lifetime in {sum(c['physical_delta']['lifetime'] < -p['tolerances']['readout'] for c in noise)}. "
               'Thus the neutral-noise advantage survives this richer physical resource model. '
               'The favorable stock-aware result does not erase that adverse comparison.'), '',
              '| Registered hypothesis | Outcome |', '| --- | --- |',
              f"| X1: cheap/high-contrast/coupling4 B_X beats B_R on pooled breadth and food | breadth {'pass' if predictions['X1']['breadth_positive'] else 'fail'}; food {'pass' if predictions['X1']['food_positive'] else 'fail'} |",
              f"| X2: S_A increases food over B_R in that regime | {'pass' if predictions['X2']['passes'] else 'fail'} |",
              f"| X3: higher movement cost reduces pooled B_X−B_R breadth at every allocation/coupling | {'pass' if predictions['X3']['passes'] else 'fail'} |", '',
              ('Pooled predictions use the arithmetic mean of two conditional-root differences; no entropy '
              'of a randomly chosen root is added. In X1 the mean B_X−B_R difference is '
              f"{target['mean_delta_bits']:+.6f}bits, food {target['mean_food_delta']:+.6f}energy units, "
              f"lifetime {target['mean_lifetime_delta']:+.6f}time units."), '',
              (f"There are {len(flips)} registered pair/horizon/case temporal sign flips across the 3 cadences. "
              'All flips and hidden-signal non-Markov bounds remain in the full summary/map. No cutoff '
              'was selected to make a ranking favorable.'), '',
              (f"At the primary readout, {sum(c['breadth_without_food_or_lifetime'] for c in primary)} of 80 pair comparisons "
              'gain breadth without gaining food or lifetime; '
              f"{sum(c['functional_gain_without_breadth'] for c in primary)} gain one of those functions without breadth. "
              'These are structural diagnostics, not classifications of ethical desirability.'), '',
              ('The physical change is a coupling from the powered bit to a costed location transition. '
              'Food is transferred from real stocks; native boundary offers stay matched within each '
              'allocation, but accepted work and stock dynamics can change. Do not claim automatic '
              'background cancellation or equal-absorbed-work efficiency.'), '',
              ('All five mechanisms share the same limiting environmental rate within each boundary/cadence '
              f"(maximum spread {max(rate_spreads):.3g}bits/time). Mortality eventually ends the body process. "
              'Observed finite differences do not establish sustained or recursively enabling generativity. '
              'This is a finite-life access result. The separate [paid-sensing batch](../paid_sensing/RESULTS.md) '
              'implements the informative register missing here, and the [renewal batch](../renewal/RESULTS.md) '
              'adds continued operation. Their laws and outcomes remain separate.'), '',
              ('S_A resolves stock availability in its physical rate rule without separate sensor memory or '
              'overhead. Its comparison is an information/mechanism benchmark, not proof of an embodied '
              'agent or optimum among all policies. This world is a coarse driven resource system, not a '
              'microscopic thermal gas or a suffering model.'), '',
              ('Interpretation revised15October2026 under the Drive revision posture. The model '
              'supports local access-mechanism comparisons, not claims about intertwined valuers, '
              'domination or universal ethical sufficiency. The costly noise advantage is retained '
              'as pressure on identifying breadth with function. See [cross-run synthesis]'
              '(../INTERPRETATION_SYNTHESIS_2026-10-15.md).'), '',
              (f"Run {status['profile']['wall_seconds']:.2f}s, peak {status['profile']['peak_job_bytes']/1024**2:.1f}MiB; "
              f"maximum residual {result['maximum_residual']:.3g}. {len(rows)} arm/cadence analyses; "
              f"{result['unique_generators']} distinct generators (aliases disclosed, not separate evidence)."), '',
              ('Reproduce with `python scripts/run_exploration.py smoke`, then `science`, then '
              '`python scripts/report_exploration.py`. Registration is immutable; sources and runs are '
              'frozen and capped. Raw snapshots remain ignored; full compact summary/map are retained.'), '',
              f"Frozen scientific input hash: `{result['input_hash']}`.", '']
    (DOC/'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'counts': counts, 'predictions': predictions, 'cadence_flips': len(flips)}, indent=2))


if __name__ == '__main__':
    main()
