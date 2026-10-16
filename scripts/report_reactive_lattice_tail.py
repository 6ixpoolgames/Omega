"""Horizon sufficiency is measured separately from filed finite-window scores."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/research_notes/lushness_testbed/same_law_gas'


def main():
    status = json.loads((DOC/'TAIL_STATUS.json').read_text())
    if status.get('status') != 'complete':
        raise RuntimeError('Complete every filed horizon audit before summary')
    protocol = json.loads((DOC/'PROTOCOL.json').read_text())
    data = [json.loads((DOC/'tails'/(law['id']+'.json')).read_text()) for law in protocol['laws']]
    rows, final_rows = [], []
    for result in data:
        for row in result['rows']:
            rows.append({'law': result['law']['id'], **row})
            if row['horizon'] == result['last_horizon']:
                final_rows.append({'law': result['law']['id'], **row})
    with (DOC/'HORIZON_EXTENSION_MAP.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    tol = protocol['tolerances']['bits']
    counts = {}
    for name in ('thermal', 'unbound', 'arrangement'):
        primary = [r for r in final_rows if r['reference'] == name and r['cadence'] == .25]
        robust = [law for law in protocol['laws'] if min(r['delta_bits'] for r in final_rows
                  if r['law'] == law['id'] and r['reference'] == name) > tol]
        counts[name] = {'positive_final_primary': sum(r['delta_bits'] > tol for r in primary),
                       'negative_final_primary': sum(r['delta_bits'] < -tol for r in primary),
                       'robust_positive_final_all_cadences': len(robust)}
    largest_tail = max(max(h['global_tail_oscillation']) for d in data for h in d['horizons'] if h['horizon'] == 1024)
    final_bound = max(max(d['horizons'][-1]['global_tail_oscillation']) for d in data)
    final_error = max(max(d['horizons'][-1]['sampled_poisson_accumulated_pair_error_bound']) for d in data)
    summary = {'counts': counts, 'all_converged': all(d['converged_at_last_query'] for d in data),
        'last_horizons': {d['law']['id']: d['last_horizon'] for d in data},
        'maximum_global_tail_at1024': largest_tail, 'maximum_global_tail_final': final_bound,
        'maximum_poisson_pair_error_bound_final': final_error,
        'seconds': sum(r['profile']['wall_seconds'] for r in status['laws'].values())
                  +sum(r['profile']['wall_seconds'] for r in status.get('prior_incomplete_attempts', []))}
    (DOC/'HORIZON_AUDIT.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    central_id = 'N6-L7-b3-m0.25-native'
    central = [r for r in final_rows if r['law'] == central_id]
    lines = ['# Horizon sufficiency audit', '',
        'Retrospective follow-up prompted by the user\'s horizon question. The original protocol, finite-history scores and prediction outcomes remain unchanged. Every original law is extended under the same frozen physical source; no winning subset is selected.', '',
        '![Exact horizon and cadence profile](horizon_profile.png)', '',
        '## Objective and rate', '',
        'Complete conditional finite-history lushness remains primary. Rate is a diagnostic of sustained contribution under maintained boundaries. All preparation roots in one finite irreducible Q have a common rate. The horizon audit therefore compares actual finite-history differences with their preparation offsets, rather than using a rate to replace those scores.', '',
        'For sampled Poisson vectorb, the seed-minus-reference tail is -(mu_seed-mu_reference) exp(QT)b. Its absolute value is at most the oscillation max(exp(QT)b)-min(exp(QT)b). This Markov bound covers every pair of roots or root mixtures. The accumulated sampled-Poisson residual bound2*(T/delta)*||residual||_infinity is reported separately. These are validated numerical calculations, not interval-arithmetic certificates.', '',
        f"AtT1024 the largest global tail oscillation was{largest_tail:.6g}bits. The extended queries ended at{sorted(set(summary['last_horizons'].values()))}; all laws satisfied the filed1e-3bit tail-plus-Poisson-error criterion: **{summary['all_converged']}**. Largest final oscillation{final_bound:.6g}bits; largest accumulated pair-error bound{final_error:.6g}bits. This supports asymptotic interpretation to that diagnostic tolerance, not a unique ethical horizon.", '',
        '## Final signs', '',
        '| Reference | Positive at cadence0.25 | Negative at cadence0.25 | Positive at all three cadences |',
        '| --- | ---: | ---: | ---: |']
    for name, values in counts.items():
        lines.append(f"| {name} | {values['positive_final_primary']} | {values['negative_final_primary']} | {values['robust_positive_final_all_cadences']} |")
    lines += ['', '## Positive-target case', '',
        'N6/L7, beta3, mobility0.25, native assistance. AtT64/cadence0.25 the seed leads the unbound reference by7.62767bits. AtT1024 it trails by3.65497bits. The extended scores below retain the reversal and show its temporal-resolution dependence.', '',
        '| Reference | Cadence | Last horizon | Actual finite-history difference | Offset |',
        '| --- | ---: | ---: | ---: | ---: |']
    for row in central:
        lines.append(f"| {row['reference']} | {row['cadence']} | {row['horizon']} | {row['delta_bits']:+.6f} | {row['delta_offset']:+.6f} |")
    lines += ['',
        'The observed preparation advantage over the full thermal mixture is distinct from robust advantage over an initially unbound gas-like preparation. Some thermal-mixture wins occur without catalytic assistance; the reference\'s greater initial assembly content and transient motion contribute. The original positive thermal-target prediction passed, but cannot be broadened into an unconditional generativity-against-gas claim.', '',
        'The useful physical opportunity may end before or after a crossover. Those finite windows need explicit source-lifetime experiments. Infinite maintained drive and a numerically converged offset are diagnostics of this toy, not a replacement for the actual physical continuation or a universal moral ordering.', '',
        f"Tail audit cost{summary['seconds']:.1f}seconds including the retained writer-failure attempt. All cases used120s/512MiB caps. Failed receipt and serialization repair are documented in EXECUTION_INCIDENTS.md.", '']
    (DOC/'HORIZON_AUDIT.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
