"""Score the frozen W1/W2 batch, retaining qualification failures and interval uncertainty."""
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.experiments.signal_kills import (
    compare_intervals,
    limiting_order,
    local_verdict,
)
from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle

DOC = ROOT/'docs/research_notes/lushness_testbed/aversive_signals'


def _eligible(arms, horizon, target, protocol):
    readouts = {name: row['horizons'][str(horizon)]['readouts'] for name, row in arms.items()}
    q = {name: stats['qualification'] for name, stats in readouts.items()}
    if target == 'K1':
        eligible = (q['A']['tracking'] and q['A']['disposition'] and q['A']['obstructed']
                    and readouts['B']['signal_occupancy_time'] <= protocol['tolerances']['physical_comparison'])
        reasons = [label for label, passed in (
            ('A_tracking', q['A']['tracking']), ('A_disposition', q['A']['disposition']),
            ('A_obstructed', q['A']['obstructed'])) if not passed]
        return bool(eligible), reasons, []
    eligible = (q['D']['nontracking'] and q['D']['disposition']
                and q['E_prime']['tracking'] and q['E_prime']['disposition']
                and readouts['N_prime']['signal_occupancy_time'] <= protocol['tolerances']['physical_comparison'])
    reasons = [label for label, passed in (
        ('D_nontracking', q['D']['nontracking']), ('D_disposition', q['D']['disposition']),
        ('E_prime_tracking', q['E_prime']['tracking']),
        ('E_prime_disposition', q['E_prime']['disposition'])) if not passed]
    vetoes = []
    for name in protocol['K2']['functional_gain_veto']:
        def value(arm, key=name):
            stats = readouts[arm]
            return stats[key] if key in stats else stats['event_counts'].get(key, 0.)
        if value('D') > max(value('E_prime'), value('N_prime'))+protocol['tolerances']['physical_comparison']:
            vetoes.append(name)
    return bool(eligible), reasons, vetoes


def main():
    status = json.loads((DOC/'FIRST_BATCH_SCIENCE_STATUS.json').read_text(encoding='utf-8'))
    if status['status'] != 'complete':
        raise RuntimeError('Incomplete scientific batch cannot be scored')
    run = Path(status['run'])
    manifest = verify_bundle(run)
    results_path = run/'RESULTS.json'
    results = json.loads(results_path.read_text(encoding='utf-8'))
    protocol = manifest['config']['protocol']
    if results['input_hash'] != manifest['input_hash'] or results['protocol'] != protocol:
        raise RuntimeError('Scientific input identity mismatch')
    # Tiny roundoff can reverse equal endpoints. Expand outward only below the
    # already registered numerical-residual gate; do not change scientific tolerances.
    rounding_count = 0
    for row in results['rows']:
        intervals = [row['merged_offset']]
        intervals += [values['signal_merged_bounds'] for values in row['horizons'].values()]
        for bounds in intervals:
            if bounds['lower_bits'] > bounds['upper_bits']:
                if bounds['lower_bits']-bounds['upper_bits'] > protocol['tolerances']['residual']:
                    raise ArithmeticError('Inverted bounds exceed frozen numerical gate')
                bounds['lower_bits'], bounds['upper_bits'] = bounds['upper_bits'], bounds['lower_bits']
                rounding_count += 1
    # The operative scoring helpers themselves were prospectively snapshotted.
    for relative in ('omega_v2/testbed/experiments/signal_kills.py',
                     'omega_v2/testbed/analysis/observed_history.py'):
        record = next(row for row in manifest['sources'] if row['path'] == relative)
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != record['sha256']:
            raise RuntimeError('Scoring source differs from frozen version')
    expected_rows = sum(len(case['arms']) for case in protocol['cases'])*len(protocol['cadences'])
    if len(results['rows']) != expected_rows:
        raise RuntimeError('Scientific grid incomplete')
    index = {(row['case'], row['cadence'], row['arm']): row for row in results['rows']}
    if len(index) != expected_rows:
        raise RuntimeError('Duplicate scientific rows')
    comparisons, limiting, diagnostics, primary = [], [], [], []
    for case in protocol['cases']:
        target = 'K1' if case['family'] == 'W1' else 'K2'
        worse = 'A' if target == 'K1' else 'D'
        better = ['B'] if target == 'K1' else ['E_prime', 'N_prime']
        for cadence in protocol['cadences']:
            arms = {name: index[(case['id'], cadence, name)] for name in case['arms']}
            for horizon in protocol['horizons']:
                eligible, reasons, vetoes = _eligible(arms, horizon, target, protocol)
                for grain in protocol['grains']:
                    comparison = compare_intervals(arms[worse]['horizons'][str(horizon)][grain],
                        [arms[name]['horizons'][str(horizon)][grain] for name in better],
                        protocol['tolerances']['bits'])
                    record = {'case': case['id'], 'target': target, 'cadence': cadence,
                              'horizon': horizon, 'grain': grain,
                              'instantiates': eligible, 'failed_prerequisites': reasons,
                              'functional_gain_vetoes': vetoes, **comparison,
                              'qualified_verdict': local_verdict(comparison, eligible and not vetoes)}
                    comparisons.append(record)
                    if cadence == protocol['primary_cadence'] and horizon == protocol['primary_horizon'] and grain == 'resolved':
                        primary.append(record)
                if target == 'K1':
                    # C is diagnostic, not a calm primary comparator.
                    for pair in (('A', 'C'), ('B', 'C'), ('E', 'N')):
                        a, b = pair
                        comparison = compare_intervals(arms[a]['horizons'][str(horizon)]['resolved'],
                            [arms[b]['horizons'][str(horizon)]['resolved']], protocol['tolerances']['bits'])
                        diagnostics.append({'case': case['id'], 'cadence': cadence,
                            'horizon': horizon, 'pair': f'{a}-{b}', **comparison})
            eligible, reasons, vetoes = _eligible(arms, max(protocol['horizons']), target, protocol)
            for grain in protocol['grains']:
                pairs = [(arms[name]['rate_bits_per_time'], arms[name]['resolved_offset'])
                         for name in [worse, *better]]
                if grain == 'resolved':
                    raw = limiting_order(pairs[0], pairs[1:], protocol['tolerances']['rate'],
                                         protocol['tolerances']['bits'])
                    comparison = compare_intervals(
                        {'lower_bits': pairs[0][1], 'upper_bits': pairs[0][1]},
                        [{'lower_bits': x[1], 'upper_bits': x[1]} for x in pairs[1:]],
                        protocol['tolerances']['bits'])
                    comparison['verdict'] = raw
                else:
                    if max(x[0] for x in pairs)-min(x[0] for x in pairs) > protocol['tolerances']['rate']:
                        raise RuntimeError('Unexpected rate mismatch in resolved recurrent tail')
                    comparison = compare_intervals(arms[worse]['merged_offset'],
                        [arms[name]['merged_offset'] for name in better], protocol['tolerances']['bits'])
                limiting.append({'case': case['id'], 'target': target, 'cadence': cadence,
                    'grain': grain, 'instantiates': eligible, 'failed_prerequisites': reasons,
                    'functional_gain_vetoes': vetoes, **comparison,
                    'qualified_verdict': local_verdict(comparison, eligible and not vetoes)})
    main_verdicts = []
    for case in protocol['cases']:
        selected = [x for x in comparisons if x['case'] == case['id']
                    and x['horizon'] in protocol['main_kill_horizons']]
        selected += [x for x in limiting if x['case'] == case['id']]
        qualified = {x['qualified_verdict'] for x in selected}
        if qualified == {'adapter_relative_ranking_counterexample'}:
            verdict = 'corridor_robust_functional_ranking_kill'
        elif qualified == {'compression_failure'}:
            verdict = 'corridor_robust_functional_compression_failure'
        else:
            verdict = 'no_registered_main_kill'
        main_verdicts.append({'case': case['id'], 'family': case['family'],
                             'verdict': verdict, 'component_verdicts': sorted(qualified)})
    primary_details = []
    for row in primary:
        worse = 'A' if row['target'] == 'K1' else 'D'
        arm = index[(row['case'], row['cadence'], worse)]
        stats = arm['horizons'][str(row['horizon'])]['readouts']
        primary_details.append({**row, 'tracking_mi_bits': stats['qualification']['tracking_mi_bits'],
            'tracking': stats['qualification']['tracking'], 'nontracking': stats['qualification']['nontracking'],
            'disposition': stats['qualification']['disposition'],
            'suffering_index': stats['operational_obstructed_suffering_index'],
            'signal_time': stats['signal_occupancy_time'],
            'survival': stats['survival_at_deadline']})
    summary = {'status': 'complete', 'scope': protocol['scope'], 'input_hash': manifest['input_hash'],
        'source_hash': manifest['source_hash'],
        'result_sha256': hashlib.sha256(results_path.read_bytes()).hexdigest(),
        'report_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'rows': expected_rows, 'parameter_points': len(protocol['cases']),
        'maximum_numerical_residual': results['maximum_numerical_residual'],
        'outward_roundoff_interval_repairs': rounding_count,
        'profile': status['profile'], 'main_verdicts': main_verdicts,
        'main_counts': dict(Counter(x['verdict'] for x in main_verdicts)),
        'primary': primary_details,
        'finite_comparisons': comparisons, 'limiting_comparisons': limiting,
        'diagnostic_comparisons': diagnostics,
        'local_verdict_counts': dict(Counter(x['qualified_verdict'] for x in comparisons)),
        'primary_raw_counts': {target: dict(Counter(x['verdict'] for x in primary if x['target'] == target))
                               for target in ('K1', 'K2')},
        'primary_qualified_counts': {target: dict(Counter(x['qualified_verdict'] for x in primary if x['target'] == target))
                                     for target in ('K1', 'K2')},
    }
    atomic_json(DOC/'FIRST_BATCH_SUMMARY.json', summary)
    fields = ['case', 'target', 'cadence', 'horizon', 'grain', 'difference_lower',
              'difference_upper', 'verdict', 'instantiates', 'qualified_verdict',
              'failed_prerequisites', 'functional_gain_vetoes']
    with (DOC/'FIRST_BATCH_PARAMETER_MAP.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in comparisons:
            writer.writerow({key: row[key] for key in fields})
    lines = ['# First W1/W2 adversarial batch — results', '',
             f"All {expected_rows} arm/cadence analyses completed at {len(protocol['cases'])} parameter points.",
             'Whole finite-history lushness is primary. Rates and offsets are diagnostics.', '',
             '## Primary resolved comparison (T64, cadence 0.25)', '',
             '| Case | Difference, bits | Raw ranking | Qualification | Tracking MI |',
             '| --- | ---: | --- | --- | ---: |']
    for row in primary_details:
        lines.append(f"| {row['case']} | {row['difference_lower']:+.6f} | {row['verdict']} | "
                     f"{row['qualified_verdict']} | {row['tracking_mi_bits']:.6g} |")
    lines += ['', '## Registered stronger corridor', '',
              json.dumps(summary['main_counts'], sort_keys=True), '',
              'The corridor includes both grains, all three cadences, T256/T1024 and the limiting offset comparison.',
              'No unresolved interval, failed instantiation or functional-gain veto is scored as a main kill.', '',
              '## Reproduction', '',
              f"Input hash: `{manifest['input_hash']}`.",
              (f"Wall time {status['profile']['wall_seconds']:.3f}s; peak job memory "
               f"{status['profile']['peak_job_bytes']/1024**2:.1f} MiB."),
              f"Maximum numerical residual: {results['maximum_numerical_residual']:.3g}.",
              'The full parameter surface is in FIRST_BATCH_PARAMETER_MAP.csv and FIRST_BATCH_SUMMARY.json.',
              'Raw arm/readout results and frozen sources remain in the ignored local run bundle.', '',
              f"Numerical note: {rounding_count} equal-bound endpoint reversals were expanded outward below the registered residual tolerance; scientific tolerance unchanged.", '',
              'This is a finite functional model. W3/W4 and the full r2 grid remain unrun.',
              'The local tracking definition and cost box are declared assumptions; see FIRST_BATCH_SPEC.md and COST_ANCHORS.md.', '']
    (DOC/'FIRST_BATCH_RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({key: summary[key] for key in ('rows', 'main_counts', 'primary_raw_counts',
                        'primary_qualified_counts', 'local_verdict_counts')}, indent=2))


if __name__ == '__main__':
    main()
