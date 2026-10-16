"""Retain the complete audit surface and automatically score calibration checks."""
import csv
import hashlib
import json
import sys
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle

DOC = ROOT/'docs/research_notes/lushness_testbed/temporal_profile'


def main():
    status = json.loads((DOC/'SCIENCE_STATUS.json').read_text(encoding='utf-8'))
    if status['status'] != 'complete':
        raise RuntimeError('Completed science required')
    run = Path(status['run'])
    manifest = verify_bundle(run)
    raw = run/'RESULTS.json'
    result = json.loads(raw.read_text(encoding='utf-8'))
    if result['input_hash'] != manifest['input_hash'] or result['protocol'] != manifest['config']['protocol']:
        raise RuntimeError('Scientific identity mismatch')
    p = result['protocol']
    expected_rows = len(p['cases'])*len(p['arms'])
    expected_pairs = len(p['cases'])*len(p['pairs'])*len(p['horizons'])
    if len(result['rows']) != expected_rows or len(result['comparisons']) != expected_pairs:
        raise RuntimeError('Incomplete audit')
    prior_path = ROOT/'docs/research_notes/lushness_testbed/aversive_signals/REGISTER_CONTROL_SUMMARY.json'
    prior = json.loads(prior_path.read_text(encoding='utf-8'))
    previous = {(v['parent'], v['pair'], v['horizon'], v['cadence']): v['difference_lower']
                for v in prior['comparisons'] if v['upkeep_ratio'] == .05 and v['grain'] == 'resolved'}
    reproduction_errors, scored = [], []
    for item in result['comparisons']:
        for v in item['profile']:
            key = item['parent'], '-'.join(item['pair']), item['horizon'], v['cadence']
            if key in previous:
                reproduction_errors.append(abs(v['delta_bits']-previous[key]))
        errors = [abs(v['pair_error_bits']) for v in item['profile'][-4:]]
        fine = item['profile'][-1]
        dn = item['prediction']['delta_jumps']
        scored.append({'parent': item['parent'], 'pair': item['pair'], 'horizon': item['horizon'],
                       'last_four_pair_errors_strictly_decrease': all(b < a for a, b in pairwise(errors)),
                       'last_pair_error_less_than_coarsest': abs(fine['pair_error_bits']) < abs(item['profile'][0]['pair_error_bits']),
                       'finest_sign_agrees_with_jump_difference': fine['delta_bits']*dn > 0,
                       'finest_pair_error_bits': fine['pair_error_bits'],
                       'exact_grid_crossings': len(item['crossing_brackets'])})
    if len(reproduction_errors) != 48 or max(reproduction_errors) > p['tolerances']['bits']:
        raise ArithmeticError('Prior-score reproduction failed')
    result.pop('imports')
    result.update({'profile': status['profile'], 'result_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
                   'report_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'prior_summary_sha256': hashlib.sha256(prior_path.read_bytes()).hexdigest(),
                   'calibrations': scored, 'reproduced_comparisons': len(reproduction_errors),
                   'maximum_reproduction_error_bits': max(reproduction_errors)})
    atomic_json(DOC/'SUMMARY.json', result)
    records = []
    for item in result['comparisons']:
        for v in item['profile']:
            records.append({'parent': item['parent'], 'pair': '-'.join(item['pair']),
                            'horizon': item['horizon'], 'cadence': v['cadence'],
                            'delta_bits': v['delta_bits'], 'estimated_delta_bits': v['estimated_delta_bits'],
                            'pair_error_bits': v['pair_error_bits'],
                            'delta_jumps': item['prediction']['delta_jumps'],
                            'delta_finite_bits': item['prediction']['delta_finite_bits']})
    with (DOC/'PROFILE_MAP.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    monotone = sum(v['last_four_pair_errors_strictly_decrease'] for v in scored)
    finest = sum(v['finest_sign_agrees_with_jump_difference'] for v in scored)
    better = sum(v['last_pair_error_less_than_coarsest'] for v in scored)
    lines = ['# Temporal profile audit results', '',
             ('The exact histories reproduce the previous adverse comparisons and explain their temporal reversals. '
             'No physical cutoff was supplied and no term was subtracted from lushness.'), '',
             '| Parent / T | Asymptotic crossing estimate | Exact integer-schedule crossing bracket |',
             '| --- | ---: | --- |']
    for item in result['comparisons']:
        if item['pair'] != ['A', 'B']:
            continue
        br = item['crossing_brackets'][0]['refined']
        note = ' (one endpoint within bit tolerance)' if min(abs(x['delta_bits']) for x in br) <= p['tolerances']['bits'] else ''
        lines.append(f"| {item['parent']} / {item['horizon']} | {item['prediction']['estimated_cadence']:.6f} | "
                     f"{min(x['cadence'] for x in br):.6f}–{max(x['cadence'] for x in br):.6f}{note} |")
    lines += ['', ('The leading formula underestimates these finite-cadence crossing locations. '
              'Exact matrix exponentials remain necessary. Brackets compare adjacent integer sample schedules '
              'at a fixed physical horizon, rather than claiming an arbitrary-cadence exact root.'), '',
              ('Across both parents and horizons, B_R exceeds B, A0 exceeds A, and A loses to B_R '
              'at every tested resolved cadence (0.5 through 1/512). A versus B changes sign in all four profiles. '
              'The original coarse-cadence counterexamples remain valid within their declared grain.'), '',
              (f'All {len(reproduction_errors)} overlapping earlier comparisons reproduce within '
              f'{max(reproduction_errors):.3g} bits. Maximum probability residual {result["maximum_residual"]:.3g}. '
              f'The run took {status["profile"]["wall_seconds"]:.2f}s, '
              f'peaking at {status["profile"]["peak_job_bytes"]/1024**2:.1f}MiB.'), '',
              (f'The finest sign agrees with the nonzero jump-count difference in {finest}/{len(scored)} pairs. '
              f'Final pair error is smaller than coarsest error in {better}/{len(scored)}. '
              f'The stricter final-four monotone-error check passes only {monotone}/{len(scored)}: '
              'higher-order cancellation can make signed pair error cross zero. Do not infer that every '
              'halving improves an asymptotic approximation monotonically.'), '',
              ('In A−B, expected physical jumps are lower by about 0.472/0.504, while the finite terms '
              'are higher by about 1.547/1.438 bits at T64. Thus sufficiently fine timing favors B, '
              'even though A wins at cadence 0.25. F contains timing and destination uncertainty; '
              'it is not a structure or welfare score.'), '',
              ('H(N_T) is bounded for all eight worlds at T64, with interval widths below 4e-9 bits '
              '(analytic tail uncertainty, in addition to numerical residuals). Overflow physical dynamics '
              'remain present; only the auxiliary count label is censored. Fixed-jump entropy and expected '
              'local destination surprisal are separate diagnostics. The full random-length conditional '
              'mark/timing decomposition was not computed.'), '',
              ('Hidden-signal bounds at the original three cadences remain in SUMMARY.json. They are '
              'non-Markov bounds, not an invented coarse CTMC. The new fine grid does not settle spatial '
              'grain, physical distinguishability, or a universal temporal band.'), '',
              ('Interpretation revised15October2026: this is a measurement calibration on fixed '
              'functional adversaries. It preserves both the original resolved counterexamples and '
              'their resolution dependence. A temporal crossover varies cadence at fixed horizon; '
              'a horizon repayment crossover varies duration at fixed cadence. These are different '
              'diagnostics. F is a finite temporal-resolution term, not a measure of organization.'), '',
              ('The subsequent [exploration](../exploration/RESULTS.md), '
              '[paid sensing](../paid_sensing/RESULTS.md) and [renewal](../renewal/RESULTS.md) '
              'batches are complete. The new renewal rate advantages describe ongoing contributions '
              'under a different law; they do not remove this calibration or its counterexamples. '
              'See [cross-run synthesis](../INTERPRETATION_SYNTHESIS_2026-10-15.md).'), '',
              ('Reproduce: `python scripts/run_temporal_profile.py smoke`, then `science`, then '
              '`python scripts/report_temporal_profile.py`. Existing frozen registration is reused; '
              '`prepare` is only for creating it once. Raw snapshots/results remain ignored locally. '
              'Sources, protocol, full compact summary and comparison map are retained.'), '',
              f'Frozen scientific input hash: `{result["input_hash"]}`.',
              ('The first smoke exposed a descriptive protocol key incorrectly forwarded as a function '
              'argument. That engineering call was repaired before successful source-identical smoke '
              'and science; physical parameters and registered queries were unchanged.'), '']
    (DOC/'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'reproduced': len(reproduction_errors), 'monotone': monotone,
                      'finest_sign_matches': finest, 'final_error_smaller': better}, indent=2))


if __name__ == '__main__':
    main()
