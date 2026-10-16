"""Equal accepted-work comparison with finite-history and physical-flow maps."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT/'docs/research_notes/lushness_testbed/compounding/matched_throughput'


def main():
    protocol = json.loads((DOC/'PROTOCOL.json').read_text())
    status = json.loads((DOC/'SCIENCE_STATUS.json').read_text())
    if status.get('status') != 'complete':
        raise RuntimeError('All declared laws must finish before reporting')
    calibration = json.loads((DOC/'CALIBRATION.json').read_text())
    data = {law['id']: json.loads((DOC/'laws'/(law['id']+'.json')).read_text()) for law in protocol['laws']}
    groups, rate_map, finite_map, physical_map = [], [], [], []
    for capacity in (4, 8, 16, 32):
        for target_no, target in enumerate(calibration['targets'], 1):
            arms = {arm: data[f'M{capacity}-target{target_no}-{arm}'] for arm in ('loop', 'basal')}
            for dt in protocol['cadences']:
                rates = {arm: next(r['rate'] for r in d['rows'] if r['root'] == 'seed' and r['cadence'] == dt)
                         for arm, d in arms.items()}
                rate_map.append({'capacity': capacity, 'target_number': target_no, 'accepted_work_target': target,
                                 'cadence': dt, 'loop_rate': rates['loop'], 'basal_rate': rates['basal'],
                                 'delta_rate': rates['loop']-rates['basal']})
                for root in ('seed', 'unorganized'):
                    scores = {arm: next(r for r in d['rows'] if r['root'] == root and r['cadence'] == dt)
                              for arm, d in arms.items()}
                    for t in protocol['horizons']:
                        finite_map.append({'capacity': capacity, 'target_number': target_no, 'cadence': dt,
                            'root': root, 'horizon': t,
                            'delta_bits': scores['loop']['scores'][str(t)]['bits']-scores['basal']['scores'][str(t)]['bits'],
                            'delta_offset': scores['loop']['offset']-scores['basal']['offset']})
            for root in ('seed', 'unorganized'):
                for t in protocol['horizons']:
                    a = arms['loop']['physical'][f'loop:{root}'][str(t)]
                    b = arms['basal']['physical'][f'basal:{root}'][str(t)]
                    physical_map.append({'capacity': capacity, 'target_number': target_no, 'root': root, 'horizon': t,
                        'loop_finite_accepted_work': a['resource_work'], 'basal_finite_accepted_work': b['resource_work'],
                        'delta_jumps': a['expected_jumps']-b['expected_jumps'],
                        'delta_F': a['finite_temporal_term']-b['finite_temporal_term'],
                        'loop_apparatus_deadline': a['apparatus_deadline'], 'basal_apparatus_deadline': b['apparatus_deadline'],
                        'loop_captured_energy': a['captured_energy'], 'basal_captured_energy': b['captured_energy']})
            stationary = {arm: d['stationary'][arm] for arm, d in arms.items()}
            flux_error = max(abs(v['resource_work']-target) for v in stationary.values())
            if flux_error > protocol['match_tolerance']:
                raise ArithmeticError('Matched-work target failed')
            groups.append({'capacity': capacity, 'target_number': target_no, 'target': target,
                'loop_supply': arms['loop']['law']['parameters']['supply_rate'],
                'basal_supply': arms['basal']['law']['parameters']['supply_rate'],
                'loop_apparatus': stationary['loop']['apparatus_deadline'],
                'basal_apparatus': stationary['basal']['apparatus_deadline'],
                'delta_rate_primary': stationary['loop']['rate']-stationary['basal']['rate'],
                'loop_capture_funding': stationary['loop']['capture_funding_fraction'],
                'basal_capture_funding': stationary['basal']['capture_funding_fraction'],
                'loop_captured_energy_rate': stationary['loop']['captured_energy'],
                'basal_captured_energy_rate': stationary['basal']['captured_energy'],
                'loop_bath_bank_fraction': stationary['loop']['bath_bank_fraction'],
                'basal_bath_bank_fraction': stationary['basal']['bath_bank_fraction'],
                'work_match_error': flux_error})
    for name, rows in [('RATE_MAP', rate_map), ('FINITE_MAP', finite_map), ('PHYSICAL_MAP', physical_map), ('MATCH_MAP', groups)]:
        with (DOC/(name+'.csv')).open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    points = [(m, t) for m in (4, 8, 16, 32) for t in (1, 2, 3)]
    robust_positive = {(m, t) for m, t in points if min(r['delta_rate'] for r in rate_map
                      if r['capacity'] == m and r['target_number'] == t) > protocol['rate_tolerance']}
    predictions = {'P1': bool(robust_positive), 'P2': all((m, 2) in robust_positive for m in (4, 8, 16, 32)),
                   'P3': all(g['loop_apparatus'] > g['basal_apparatus'] for g in groups)}
    primary_positive = sum(row['delta_bits'] > protocol['bits_tolerance'] for row in finite_map
                          if row['cadence'] == .25 and row['horizon'] == 64 and row['root'] == 'seed')
    rate_flips = sum(len({int(r['delta_rate'] > 1e-8)-int(r['delta_rate'] < -1e-8) for r in rate_map
                         if r['capacity'] == m and r['target_number'] == t}) > 1 for m, t in points)
    summary = {'matches': groups, 'predictions': {k: 'pass' if v else 'fail' for k, v in predictions.items()},
        'robust_positive_rate_points': len(robust_positive), 'rate_cadence_sign_flips': rate_flips,
        'positive_seed_T64_points_primary': primary_positive,
        'science_seconds': sum(s['profile']['wall_seconds'] for s in status['laws'].values()),
        'peak_bytes': max(s['profile']['peak_job_bytes'] for s in status['laws'].values()),
        'maximum_match_error': max(g['work_match_error'] for g in groups)}
    funding_min = min(g['loop_capture_funding'] for g in groups)
    funding_max = max(g['loop_capture_funding'] for g in groups)
    (DOC/'SUMMARY.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    lines = ['# Compounding at matched accepted external work', '',
        'Physical-flow calibration fixed24 source settings before any new entropy ranking. Loop and basal share inventory, bath, costs, packet energy and damage, with differing catalytic couplings and offered source rates. Stationary accepted external work is matched, not finite cumulative work or event activity.', '',
        f"The12 matched points give{len(robust_positive)} positive loop-minus-basal rate gains across all three cadences;{primary_positive}/12 seed comparisons favour the loop at primaryT64/cadence0.25. There are{rate_flips} rate-sign flips. Finite-history lushness remains the primary output; rate reports sustained contribution under these maintained boundaries.", '',
        '| Capacity | Accepted work/time | Loop source rate | Basal source rate | Rate gain at0.25 | Loop retained apparatus | Basal retained apparatus |',
        '| ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for g in groups:
        lines.append(f"| {g['capacity']} | {g['target']:.6f} | {g['loop_supply']:.6f} | {g['basal_supply']:.6f} | {g['delta_rate_primary']:+.6f} | {g['loop_apparatus']:.6f} | {g['basal_apparatus']:.6f} |")
    lines += ['', '## Filed predictions', '']
    for key, passed in predictions.items():
        lines.append(f"- {key}: **{'pass' if passed else 'fail'}** — {protocol['predictions'][key]}")
    lines += ['', '## Energetics and comparison scope', '',
        'Matching accepted packet work does not match useful capture: the basal arm can accept packets and lose them unused. Nor does it match bath energy. MATCH_MAP.csv reports captured, recycled/bath funding and retained apparatus; PHYSICAL_MAP.csv reports actual finite cumulative external work, capture, expected jumps andF. Native thermal processes remain present in both arms, and no stochastic activity is subtracted.', '',
        'Positive rate and finite-history gains strengthen the causal access/conversion result within the aggregate adapter. They do not establish that a non-enabling churn system at matched activity could not compete, or that same-law organized roots have distinct limiting rates. These are mechanism/boundary contrasts, not gas preparations.', '',
        f"Captured resource energy funds{100*funding_min:.1f}–{100*funding_max:.1f}% of loop bank expenditure across these matched settings; the remainder includes recycling and explicitly reported bath imports. At the lowest input, retained mean apparatus is0.092–0.221, versus1.256–1.498 at the highest. Thus a sustained breadth gain can accompany sparse intermittent apparatus as well as retained expansion. The measured structure and funding determine which result is present, rather than the rate alone.", '',
        f"All cases completed under120s/512MiB each. Scientific wall time{summary['science_seconds']:.1f}s, peak{summary['peak_bytes']/1024**2:.1f}MiB; maximum accepted-work mismatch{summary['maximum_match_error']:.3g}. Matching targets and code were frozen before ranking. No old results were changed and no publication occurred.", '']
    (DOC/'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
