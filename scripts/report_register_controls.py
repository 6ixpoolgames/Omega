"""Full contrast surface and registered predictions for the four-arm follow-up."""
import csv
import hashlib
import json
import sys
from collections import Counter
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.experiments.signal_kills import compare_intervals
from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle

DOC = ROOT/'docs/research_notes/lushness_testbed/aversive_signals'


def main():
    status = json.loads((DOC/'REGISTER_SCIENCE_STATUS.json').read_text(encoding='utf-8'))
    if status['status'] != 'complete':
        raise RuntimeError('Complete scientific batch required')
    run = Path(status['run'])
    manifest = verify_bundle(run)
    raw = run/'RESULTS.json'
    results = json.loads(raw.read_text(encoding='utf-8'))
    protocol = manifest['config']['protocol']
    if results['input_hash'] != manifest['input_hash'] or results['protocol'] != protocol:
        raise RuntimeError('Scientific identity mismatch')
    for relative in ('omega_v2/testbed/experiments/signal_kills.py',
                     'omega_v2/testbed/analysis/observed_history.py'):
        record = next(row for row in manifest['sources'] if row['path'] == relative)
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != record['sha256']:
            raise RuntimeError('Scoring helper differs from frozen source')
    expected = len(protocol['cases'])*len(protocol['arms'])*len(protocol['cadences'])
    index = {(row['case'], row['arm'], row['cadence']): row for row in results['rows']}
    if len(index) != expected or len(results['rows']) != expected:
        raise RuntimeError('Missing or duplicate arm analyses')
    rounded = 0
    for row in results['rows']:
        intervals = [row['merged_offset']]+[x['signal_merged_bounds'] for x in row['horizons'].values()]
        for interval in intervals:
            if interval['lower_bits'] > interval['upper_bits']:
                if interval['lower_bits']-interval['upper_bits'] > protocol['tolerances']['residual']:
                    raise ArithmeticError('Inverted interval exceeds registered residual tolerance')
                interval['lower_bits'], interval['upper_bits'] = interval['upper_bits'], interval['lower_bits']
                rounded += 1
    comparisons, limiting, physical = [], [], []
    for case in protocol['cases']:
        for cadence in protocol['cadences']:
            arms = {arm: index[(case['id'], arm, cadence)] for arm in protocol['arms']}
            for horizon in protocol['horizons']:
                for a, b in protocol['pairs']:
                    for grain in protocol['grains']:
                        comparison = compare_intervals(arms[a]['horizons'][str(horizon)][grain],
                            [arms[b]['horizons'][str(horizon)][grain]], protocol['tolerances']['bits'])
                        comparisons.append({'case': case['id'], 'parent': case['parent'],
                            'upkeep_ratio': case['upkeep_ratio'], 'cadence': cadence,
                            'horizon': horizon, 'grain': grain, 'pair': f'{a}-{b}', **comparison})
            rates = [arms[arm]['rate_bits_per_time'] for arm in protocol['arms']]
            if max(rates)-min(rates) > protocol['tolerances']['rate']:
                raise ArithmeticError('Unexpected policy-dependent residual environmental rate')
            for a, b in protocol['pairs']:
                for grain in protocol['grains']:
                    if grain == 'resolved':
                        left = {'lower_bits': arms[a]['resolved_offset'], 'upper_bits': arms[a]['resolved_offset']}
                        right = {'lower_bits': arms[b]['resolved_offset'], 'upper_bits': arms[b]['resolved_offset']}
                    else:
                        left, right = arms[a]['merged_offset'], arms[b]['merged_offset']
                    comparison = compare_intervals(left, [right], protocol['tolerances']['bits'])
                    limiting.append({'case': case['id'], 'parent': case['parent'],
                        'upkeep_ratio': case['upkeep_ratio'], 'cadence': cadence,
                        'grain': grain, 'pair': f'{a}-{b}', **comparison})
        primary_arms = {arm: index[(case['id'], arm, protocol['primary_cadence'])]
                        for arm in protocol['arms']}
        for arm, row in primary_arms.items():
            data = row['horizons'][str(protocol['primary_horizon'])]
            readouts = data['readouts']
            physical.append({'case': case['id'], 'parent': case['parent'],
                'upkeep_ratio': case['upkeep_ratio'], 'arm': arm,
                'moments': data['moments'], 'live_time': readouts['live_occupancy_time'],
                'survival': readouts['survival_at_deadline'],
                'tracking_mi_bits': readouts['tracking_counterfactual_breadth_drop_mi_bits'],
                'external_hazard_mi_bits': readouts['tracking_external_hazard_mi_bits'],
                'escape_shift': readouts['escape_disposition_shift'],
                'food_input': readouts['event_counts'].get('food_input', 0.),
                'effort_bill': readouts['event_counts'].get('struggle_bill', 0.),
                'coordinate_bits': data['coordinate_bits']})
    primary = [row for row in comparisons if row['horizon'] == protocol['primary_horizon']
               and row['cadence'] == protocol['primary_cadence'] and row['grain'] == 'resolved']
    parents = sorted({case['parent'] for case in protocol['cases']})
    predictions = {}
    for name, pair, ratio, wanted in (
            ('R1', 'B_R-B', .05, 'strict_positive'),
            ('R2', 'B_R-B', 4., 'strict_negative'),
            ('R3', 'A0-A', .05, 'strict_positive')):
        rows = [row for row in primary if row['pair'] == pair and row['upkeep_ratio'] == ratio]
        predictions[name] = {'passed': len(rows) == len(parents) and all(row['verdict'] == wanted for row in rows),
                             'definition': protocol['predictions'][name], 'rows': rows}
    brackets = []
    for parent in parents:
        for cadence in protocol['cadences']:
            for horizon in protocol['horizons']:
                for grain in protocol['grains']:
                    rows = sorted([row for row in comparisons if row['parent'] == parent
                        and row['cadence'] == cadence and row['horizon'] == horizon
                        and row['grain'] == grain and row['pair'] == 'B_R-B'],
                        key=lambda row: row['upkeep_ratio'])
                    found = []
                    for left, right in pairwise(rows):
                        if {left['verdict'], right['verdict']} == {'strict_positive', 'strict_negative'}:
                            found.append([left['upkeep_ratio'], right['upkeep_ratio']])
                    brackets.append({'parent': parent, 'cadence': cadence, 'horizon': horizon,
                                     'grain': grain, 'brackets': found,
                                     'statuses': [row['verdict'] for row in rows]})
    summary = {'status': 'complete', 'input_hash': manifest['input_hash'], 'source_hash': manifest['source_hash'],
        'result_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
        'report_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'rows': expected, 'cases': len(protocol['cases']), 'predictions': predictions,
        'primary': primary, 'comparisons': comparisons, 'limiting_comparisons': limiting,
        'primary_physical_readouts': physical, 'break_even_brackets': brackets,
        'profile': status['profile'], 'maximum_residual': results['maximum_residual'],
        'outward_roundoff_repairs': rounded,
        'primary_pair_counts': {f'{a}-{b}': dict(Counter(row['verdict'] for row in primary
                                  if row['pair'] == f'{a}-{b}')) for a, b in protocol['pairs']}}
    atomic_json(DOC/'REGISTER_CONTROL_SUMMARY.json', summary)
    with (DOC/'REGISTER_CONTROL_PARAMETER_MAP.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(comparisons[0]))
        writer.writeheader()
        writer.writerows(comparisons)
    lines = ['# Four-arm register control — results', '',
             f"All {expected} registered arm/cadence analyses completed.",
             'A0 is the tracking/no-response control also called B_T. B_R has no escape drive.', '',
             '## Primary resolved differences: T64, cadence 0.25', '',
             '| Parent | Upkeep / basal | B_R-B | A0-A | A-B_R |',
             '| --- | ---: | ---: | ---: | ---: |']
    for case in protocol['cases']:
        values = {row['pair']: row['difference_lower'] for row in primary if row['case'] == case['id']}
        lines.append(f"| {case['parent']} | {case['upkeep_ratio']:g} | {values['B_R-B']:+.6f} | "
                     f"{values['A0-A']:+.6f} | {values['A-B_R']:+.6f} |")
    lines += ['', '## Registered predictions', '']
    for name, verdict in predictions.items():
        lines.append(f"- {name}: {'passed' if verdict['passed'] else 'failed'} — {verdict['definition']}")
    lines += ['', '## Matching and scope', '',
              'Rates were calibrated using physical occupancy and switch count only, then held fixed.',
              'Matching applies at upkeep ratio 0.05/T64; moments elsewhere are outcomes, not refit targets.',
              'Total charging differs despite identical unit bills. Correlations are not matched.',
              'The remaining cost/correlation differences limit causal attribution to internal variation alone.',
              'No new suffering kill or subjective-valence verdict is scored from these controls.', '',
              '## Execution', '',
              f"Wall time {status['profile']['wall_seconds']:.3f}s; peak {status['profile']['peak_job_bytes']/1024**2:.1f} MiB.",
              f"Maximum residual {results['maximum_residual']:.3g}; no cap hit.",
              f"Input hash `{manifest['input_hash']}`.",
              f"Outward corrections of equal-bound floating-point reversals: {rounded}, within frozen residual tolerance.",
              'Full finite/limiting surfaces and physical readouts: REGISTER_CONTROL_SUMMARY.json.',
              'Adjacency brackets are not exact roots; multiple or absent crossings are retained.', '']
    (DOC/'REGISTER_CONTROL_RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'rows': expected, 'predictions': {key: value['passed'] for key, value in predictions.items()},
                      'primary_pair_counts': summary['primary_pair_counts'],
                      'reference': [row for row in primary if row['upkeep_ratio'] == .05]}, indent=2))


if __name__ == '__main__':
    main()
