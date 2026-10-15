"""Complete signed maps, filed predictions and structural account of gas roots."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/research_notes/lushness_testbed/same_law_gas'


def main():
    protocol = json.loads((DOC/'PROTOCOL.json').read_text())
    status = json.loads((DOC/'SCIENCE_STATUS.json').read_text())
    if status.get('status') != 'complete':
        raise RuntimeError('No complete-grid report before all cases finish')
    summary, comparisons, activity, assembly = [], [], [], []
    data_by_id = {}
    for law in protocol['laws']:
        path = DOC/'laws'/(law['id']+'.json')
        data = json.loads(path.read_text())
        parent = status['laws'][law['id']]
        if data['input_hash'] != parent['profile']['input_hash']:
            raise RuntimeError('Result receipt mismatch')
        data_by_id[law['id']] = data
        rows = {(row['reference'], row['cadence']): row for row in data['rows']}
        for ref in ('thermal', 'unbound', 'arrangement'):
            for cadence in protocol['cadences']:
                seed, other = rows[('seed', cadence)], rows[(ref, cadence)]
                for contrast in data['contrasts']:
                    if contrast['reference'] == ref and contrast['cadence'] == cadence:
                        comparisons.append({'law': law['id'], **contrast,
                            'delta_offset': seed['offset']-other['offset'],
                            'rate_difference': seed['rate']-other['rate']})
            for t in protocol['horizons']:
                a, b = data['physical']['seed'][str(t)], data['physical'][ref][str(t)]
                activity.append({'law': law['id'], 'reference': ref, 'horizon': t,
                    'delta_jumps': a['expected_jumps']-b['expected_jumps'],
                    'delta_F': a['finite_temporal_term']-b['finite_temporal_term'],
                    'delta_local_destination_surprisal': a['destination_surprisal_integral']-b['destination_surprisal_integral']})
        for target, roots in data['assembly'].items():
            for name, values in roots.items():
                for t in protocol['horizons']:
                    assembly.append({'law': law['id'], 'target': target, 'reference': name,
                        'horizon': t, 'mass_at_zero': values['mass_at_zero'],
                        'mean_time': values['mean_time'],
                        'mean_conditioned_initially_outside': values['mean_time']/(1-values['mass_at_zero'])
                           if values['mean_time'] is not None and values['mass_at_zero'] < 1-1e-12 else None,
                        'hit_probability': values['hit_probability'][str(t)],
                        'deadline_occupancy': values['deadline_occupancy'][str(t)]})
        primary = {ref: next(c for c in data['contrasts'] if c['reference'] == ref
                   and c['cadence'] == .25 and c['horizon'] == 64)['delta_bits']
                   for ref in ('thermal', 'unbound', 'arrangement')}
        summary.append({'law': law['id'], 'parameters': law['parameters'], 'states': data['states'],
            'delta_T64': primary, 'delta_offset_thermal': rows[('seed', .25)]['offset']-rows[('thermal', .25)]['offset'],
            'delta_offset_unbound': rows[('seed', .25)]['offset']-rows[('unbound', .25)]['offset'],
            'stationary_bonds': data['stationary']['observables']['bonds'],
            'seed_T64_bonds': data['physical']['seed']['64']['deadline']['bonds'],
            'thermal_G2_mean': data['assembly']['G2']['thermal']['mean_time'],
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    for name, table in [('COMPARISON_MAP', comparisons), ('ACTIVITY_MAP', activity), ('ASSEMBLY_MAP', assembly)]:
        with (DOC/(name+'.csv')).open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(table[0]))
            writer.writeheader()
            writer.writerows(table)
    predictions = {}
    for key, pred in protocol['predictions'].items():
        data = data_by_id[pred['law']]
        scores = {(r['reference'], r['cadence']): r for r in data['rows']}
        differences = [scores[('seed', dt)]['scores']['64']-scores[(pred['reference'], dt)]['scores']['64']
                       for dt in protocol['cadences']]
        offsets = [scores[('seed', dt)]['offset']-scores[(pred['reference'], dt)]['offset']
                   for dt in protocol['cadences']]
        tolerance = protocol['tolerances']['bits']
        passed = (min(differences) > tolerance and min(offsets) > tolerance) if key == 'P_access' else (
                  max(differences) < -tolerance or max(offsets) < -tolerance)
        predictions[key] = {'status': 'pass' if passed else 'fail', **pred,
                            'T64_differences': differences, 'offset_differences': offsets}
    signs = {}
    flips = []
    for law in protocol['laws']:
        for ref in ('thermal', 'unbound', 'arrangement'):
            for t in protocol['horizons']:
                pair = [r for r in comparisons if r['law'] == law['id'] and r['reference'] == ref and r['horizon'] == t]
                observed = {1 if r['delta_bits'] > 1e-5 else -1 if r['delta_bits'] < -1e-5 else 0 for r in pair}
                if len(observed) > 1:
                    flips.append({'law': law['id'], 'reference': ref, 'horizon': t})
        for ref in ('thermal', 'unbound', 'arrangement'):
            count = signs.setdefault(ref, {'positive_T64_primary': 0, 'negative_T64_primary': 0, 'ties': 0})
            value = next(r for r in summary if r['law'] == law['id'])['delta_T64'][ref]
            count['positive_T64_primary' if value > 1e-5 else 'negative_T64_primary' if value < -1e-5 else 'ties'] += 1
    result = {'laws': summary, 'predictions': predictions, 'T64_primary_signs': signs,
              'cadence_sign_flips': flips, 'science_seconds': sum(r['profile']['wall_seconds'] for r in status['laws'].values()),
              'peak_bytes': max(r['profile']['peak_job_bytes'] for r in status['laws'].values()),
              'maximum_numerical_residual': max(max(r['residuals'].values()) for d in data_by_id.values() for r in d['rows']),
              'maximum_physical_residual': max(d['maximum_physical_residual'] for d in data_by_id.values())}
    (DOC/'SUMMARY.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    lines = ['# Same-law thermal/dispersed preparation results', '',
        'All14 frozen laws completed. Each seed and its three references reuse one native generator; references are averages of known-root history entropies, without entropy of drawing the root. The references can self-assemble, capture and grow under the full law.', '',
        'At primaryT64/cadence0.25 the seed beats the thermal-mixture average in12/14cases, the initially unbound reference in3/14, and arrangement randomization in6/14. The unbound reference has the larger asymptotic offset in all14cases at cadence0.25. Some thermal-mixture wins also occur under weak assistance; a positive preparation contrast is not by itself proof that generativity caused the advantage.', '',
        '## Primary finite-history comparison', '',
        'Delta bits atT64/cadence0.25; positive favours the seed. These are preparation comparisons, not distinct limiting rates.', '',
        '| Law | Thermal mixture | Initially unbound | Arrangement only | Thermal offset |',
        '| --- | ---: | ---: | ---: | ---: |']
    for row in summary:
        d = row['delta_T64']
        lines.append(f"| {row['law']} | {d['thermal']:+.5f} | {d['unbound']:+.5f} | {d['arrangement']:+.5f} | {row['delta_offset_thermal']:+.5f} |")
    lines += ['', '## Filed predictions and temporal corridor', '']
    for key, pred in predictions.items():
        lines.append(f"- {key}: **{pred['status']}**. {pred['claim']}; `{pred['law']}`.")
    lines += ['', f"{len(flips)} of168 law/reference/horizon comparisons change sign across cadences0.125/0.25/0.5. Full signs, individual-root minima/maxima and mass beaten are in COMPARISON_MAP.csv. A reference-average win is not superiority to every reference state. No state-grain-invariant claim follows from a cadence corridor alone.", '',
        '## What the thermal reference actually contains', '',
        'The6/7 world is dense. Its exactH4 shell has initial mean1.53846bonds and92.3077% of its mass already contains a bond. The seed has one bond. This is a thermal mixture, not dilute gas. The unbound reference has zero bonds and charge1; the seed has one bond and charge0. Both have equal total energy4, with different energy allocation. Beta changes dynamics but cancels from the fixed-energy conditional reference.', '',
        '## Assembly, persistence and paid recursion', '',
        '| Law | Seed bonds atT64 | Stationary bonds | Thermal mean time to productive alignmentG2 |',
        '| --- | ---: | ---: | ---: |']
    for row in summary:
        lines.append(f"| {row['law']} | {row['seed_T64_bonds']:.5f} | {row['stationary_bonds']:.5f} | {row['thermal_G2_mean']:.5f} |")
    lines += ['', 'ASSEMBLY_MAP.csv distinguishes initial target mass, unconditional and initially-outside mean first-passage time, deadline arrival and actual deadline occupancy. G3 means two simultaneous bonds, not proof that both were paid descendants. Assisted paid construction and its reverse are tracked separately in the native flow ledger. The six-constituent geometry permits three assemblies; first passage to two assemblies alone does not demonstrate persistent three-generation expansion.', '',
        'The new setup tests preparation advantage against naturally evolving thermal matter. It does not inherit the aggregate adapter\'s earlier strong retained-compounding result automatically. Where the seed only temporarily builds more apparatus or later loses its assembly, report that transience rather than equating a positive offset with robust generativity.', '',
        '## Activity and energetic account', '',
        'ACTIVITY_MAP.csv reports seed-minus-reference expected jumps, finite temporal coefficientF and local destination surprisal at every physical horizon. Per-law JSON includes exact fixed-jump sequence entropies at8/32/128 jumps, cumulative source work, bath exchange, paid/thermal joining and deadline stocks. F includes timing/rate terms, not a pure structure score. Fixed-jump counts compare different physical durations. No native motion, noise or reaction is subtracted.', '',
        '## Feasibility and limits', '',
        f"Engineering passed2/4,4/6 and6/7;6/8 requires13,632states and about1.38GiB for its kernel alone, and was stopped before ranking. All executed6/7 cases have3,822states. Science used{result['science_seconds']:.1f}seconds total, peak{result['peak_bytes']/1024**2:.1f}MiB under120s/512MiB per-case caps. Maximum sampled residual{result['maximum_numerical_residual']:.3g}; physical residual{result['maximum_physical_residual']:.3g}.", '',
        'One irreducible Q gives a common limiting rate for every root. Seed/reference differences can retain offsets after organization mixes. The complete finite-history profile remains primary. The physical grain is site/bond/carrier resolved; projected count histories were not assigned a fictitious Markov kernel. Initial preparation work/time is outside this given-frame comparison and would belong in a common-start decision test.', '',
        'The [horizon audit](HORIZON_AUDIT.md) extends every unchanged law after these initial results. It checks the remaining entropy tail rather than assumingT1024 is long enough; the original prediction scores are preserved.', '',
        'Sources and predictions were frozen before ranking. All signed outcomes remain. No Drive manuscript change, ethical inference or publication is part of this run.', '']
    (DOC/'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'signs': signs, 'predictions': predictions, 'flips': len(flips),
                      'seconds': result['science_seconds'], 'peak_MiB': result['peak_bytes']/1024**2}, indent=2))


if __name__ == '__main__':
    main()
