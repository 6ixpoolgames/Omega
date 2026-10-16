"""Disclosed post-run diagnostics. Never changes frozen predictions or J flags."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle
from scripts.report_robust_generativity import contrast

DOC = ROOT/'docs/research_notes/lushness_testbed/robust_generativity'


def main():
    protocol = json.loads((DOC/'PROTOCOL.json').read_text())
    summary = json.loads((DOC/'SUMMARY.json').read_text())
    status = json.loads((DOC/'SCIENCE_STATUS.json').read_text())
    cases = {c['id']: json.loads((DOC/'cases'/(c['id']+'.json')).read_text()) for c in protocol['cases']}
    maxima = {'energy': 0., 'bank': 0., 'monitor_projection': 0., 'sampled_poisson': 0., 'coordinate_sum': 0.}
    for caseid, receipt in status['cases'].items():
        manifest = verify_bundle(receipt['run'])
        case = cases[caseid]
        if manifest['input_hash'] != receipt['profile']['input_hash'] or case['input_hash'] != manifest['input_hash']:
            raise ArithmeticError('Case/manifest/receipt identity mismatch')
        original = json.loads((Path(receipt['run'])/'RESULTS.json').read_text())
        if case != original:
            raise ArithmeticError('Compact result differs from frozen-run output')
        maxima['monitor_projection'] = max(maxima['monitor_projection'], case['structure']['monitor_projection_residual'])
        for root in case['physical'].values():
            for t, row in root.items():
                if t == 'persistence':
                    continue
                maxima['energy'] = max(maxima['energy'], abs(row['ledger']['energy_balance_residual']))
                maxima['bank'] = max(maxima['bank'], abs(row['ledger']['bank_balance_residual']))
        for row in case['sampled'].values():
            maxima['sampled_poisson'] = max(maxima['sampled_poisson'], row['poisson_residual'])
            for root, contributions in row.get('coordinate_bits_T256', {}).items():
                maxima['coordinate_sum'] = max(maxima['coordinate_sum'],
                    abs(sum(contributions.values())-row['profiles'][root]['bits']['256']))
    byid = {r['id']: r for r in summary['settings']}
    loss_contrasts = []
    for alpha in (.5, 1.):
        for supply in (.15, .6):
            prefix = f'B-a{alpha:g}-s{supply:g}-R'
            for lower, higher in ((1, 3), (3, 6)):
                lo, hi = byid[prefix+str(lower)], byid[prefix+str(higher)]
                lcase, hcase = cases[lo['case_ids']['full']], cases[hi['case_ids']['full']]
                loss_contrasts.append({'from': lo['id'], 'to': hi['id'],
                    'uptime_difference': hi['persistence']['tau_up']-lo['persistence']['tau_up'],
                    'profiles': {str(t): contrast(hcase, lcase, protocol, time=t)
                                 for t in protocol['measurement']['horizons']}})
    funding_horizons = {}
    for name in ('A-a1-k1-s2.4', 'A-a1-k1-s0.6'):
        row = byid[name]; case = cases[row['case_ids']['full']]
        funding_horizons[name] = {time: {'external_spent_LB': values['ledger']['external_funding_spent_lower_bound'],
            'gross_capture_spent_LB': values['ledger']['gross_capture_funding_spent_lower_bound'],
            'initial_and_nonexternal_packet_budget': values['ledger']['nonexternal_packet_budget'],
            'all_bank_expenditure': values['ledger']['all_bank_expenditure']}
            for time, values in case['physical']['seed'].items() if time != 'persistence'}
    unique_full = {r['case_ids']['full']: r for r in summary['settings']}
    data = {'status': 'post_run_descriptive_not_registered_verdicts',
        'registered_summary_unchanged': True, 'all_144_frozen_outputs_verified': True,
        'max_residuals': maxima, 'unique_full_case_count': len(unique_full),
        'unique_C': sum(r['markers']['C'] for r in unique_full.values()),
        'unique_R': sum(r['markers']['R'] for r in unique_full.values()),
        'unique_C_R_positive_unbound_and_mechanism_without_funding_clause': [r['id'] for r in unique_full.values()
            if r['markers']['C'] and r['markers']['R'] and r['contrasts']['unbound']['all_positive']
            and r['contrasts']['all_assistance_off']['all_positive'] and r['contrasts']['cut_C_to_A']['all_positive']],
        'all_setting_positive_counts_T256': {name: sum(r['contrasts'][name]['all_positive'] for r in summary['settings'])
                                             for name in ('unbound', 'thermal', 'all_assistance_off', 'cut_C_to_A')},
        'funding_horizon_examples': funding_horizons,
        'irreversibility_contrasts_exploratory': loss_contrasts,
        'irreversibility_gains_breadth_while_losing_uptime_T256': sum(
            row['uptime_difference'] < 0 and row['profiles']['256']['all_positive'] for row in loss_contrasts),
        'tail_resolved_settings_T4096': sum(r['largest_T4096_tail'] < .001 for r in summary['settings']),
        'max_tail_bits_T4096': max(r['largest_T4096_tail'] for r in summary['settings'])}
    atomic_json(DOC/'EXPLORATORY_DIAGNOSTICS.json', data)
    print(json.dumps({k: v for k, v in data.items() if k not in
                     ('irreversibility_contrasts_exploratory', 'funding_horizon_examples')}, indent=2))


if __name__ == '__main__':
    main()
