"""Apply frozen C/R/L/J criteria to every case; retain complete signed maps."""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from scipy.stats import spearmanr

from omega_v2.testbed.workflow.manifest import atomic_json

DOC = ROOT/'docs/research_notes/lushness_testbed/robust_generativity'


def allowance(case, cadence, time):
    row = case['sampled'][str(cadence)]
    return time/cadence*row['poisson_residual']+.5*time*time*row['harmonic_rate_residual']+1e-7


def contrast(left, right, protocol, right_root='seed', time=256):
    differences = {}
    tolerance = protocol['tolerances']['bits']
    for cadence in protocol['measurement']['cadences']:
        l = left['sampled'][str(cadence)]['profiles']['seed']['bits'][str(time)]
        r = right['sampled'][str(cadence)]['profiles'][right_root]['bits'][str(time)]
        delta = l-r; error = allowance(left, cadence, time)+allowance(right, cadence, time)
        differences[str(cadence)] = {'delta_bits': delta, 'solver_allowance': error,
            'positive': delta > tolerance+error, 'negative': delta < -tolerance-error,
            'rate_difference': left['sampled'][str(cadence)]['profiles']['seed']['limiting_rate']-
                               right['sampled'][str(cadence)]['profiles'][right_root]['limiting_rate']}
    positive = all(r['positive'] for r in differences.values())
    negative = all(r['negative'] for r in differences.values())
    flip = any(r['positive'] for r in differences.values()) and any(r['negative'] for r in differences.values())
    return {'cadences': differences, 'all_positive': positive, 'all_negative': negative, 'sign_flip': flip}


def markers(case, protocol):
    m = protocol['markers']; tol = protocol['tolerances']['rate_or_physical']
    depth = case['structure']['initial_seed']
    primary = case['physical']['seed']['256']
    persistence = case['physical']['seed']['persistence']
    C = (depth['depth_by_deadline']+tol >= m['three_link_witness_probability'] and
         depth['depth_and_retained_expansion']+tol >= m['witness_and_retained_expansion_probability'])
    funding = primary['ledger']['external_funding_spent_lower_bound']
    thermal = primary['thermal_forward_fraction']
    funded = (funding is not None and funding+tol >= m['external_spent_funding_lower_bound_fraction'] and
              thermal is not None and thermal <= m['maximum_thermal_forward_construction_fraction']+tol)
    R_base = (persistence['post_startup_uptime_fraction']+tol >= m['functional_loop_uptime_fraction'] and
              primary['closure']['loop'] <= m['maximum_structural_loop_closure_probability']+tol)
    recovery = case['structure']['pulse_recovery']
    R_recovery = None
    if recovery is not None:
        r = recovery['delays']['64.0']
        R_recovery = (r['conditional_endpoint_recovery'] is not None and
                      r['conditional_endpoint_recovery']+tol >= m['conditional_endpoint_recovery_at_delay64'] and
                      r['pre_function_and_endpoint_recovery']+tol >= m['unconditional_pre_function_and_recovery_probability'])
    R = R_base and (R_recovery is not False)
    strong = depth['depth_by_startup_loop_then_expansion_no_closure']+tol >= m['strong_initial_seed_compounding_and_later_function_probability']
    return {'C': C, 'funding': funded, 'C_funded': C and funded, 'R_base': R_base,
            'R_recovery': R_recovery, 'R': R, 'strong_path': strong}


def summarize(protocol, cases):
    rows = []
    for setting in protocol['settings']:
        arms = {m: cases[cid] for m, cid in setting['case_ids'].items()}
        full = arms['full']; row = {**setting, 'markers': markers(full, protocol)}
        contrasts = {'thermal': contrast(full, full, protocol, 'thermal'),
                     'unbound': contrast(full, full, protocol, 'unbound')}
        for m, data in arms.items():
            if m != 'full':
                contrasts[m] = contrast(full, data, protocol)
        joint_base = row['markers']['C_funded'] and row['markers']['R']
        row['contrasts'] = contrasts
        row['J_thermal'] = joint_base and contrasts['thermal']['all_positive']
        row['J_unbound'] = joint_base and contrasts['unbound']['all_positive']
        row['J_mechanism'] = joint_base and contrasts['all_assistance_off']['all_positive'] and contrasts['cut_C_to_A']['all_positive']
        row['strong_J_thermal'] = row['J_thermal'] and row['markers']['strong_path']
        row['strong_J_unbound'] = row['J_unbound'] and row['markers']['strong_path']
        row['strong_J_mechanism'] = row['J_mechanism'] and row['markers']['strong_path']
        row['primary_depth'] = full['structure']['initial_seed']
        row['persistence'] = full['physical']['seed']['persistence']
        row['closure_T256'] = full['physical']['seed']['256']['closure']['loop']
        row['external_funding_LB'] = full['physical']['seed']['256']['ledger']['external_funding_spent_lower_bound']
        row['bath_forward_birth_fraction'] = full['physical']['seed']['256']['thermal_forward_fraction']
        row['ongoing_detector'] = full['structure']['ongoing_detector']
        row['profiles'] = {reference: {str(t): contrast(full, full, protocol, reference, t)
                          for t in protocol['measurement']['horizons']} for reference in ('thermal', 'unbound')}
        row['mechanism_profiles'] = {m: {str(t): contrast(full, arms[m], protocol, time=t)
                                    for t in protocol['measurement']['horizons']}
                                    for m in ('all_assistance_off', 'cut_C_to_A')}
        # A rate crossing is an estimate only; finite profiles retain all signs.
        row['repayment_estimates'] = {}
        for m in ('all_assistance_off', 'cut_C_to_A'):
            left = full['sampled']['0.25']['profiles']['seed']
            right = arms[m]['sampled']['0.25']['profiles']['seed']
            dh = left['limiting_rate']-right['limiting_rate']
            db = left['limiting_offset']-right['limiting_offset']
            row['repayment_estimates'][m] = {'delta_rate': dh, 'delta_offset': db,
                'asymptotic_T_cross': -db/dh if dh > protocol['tolerances']['rate_or_physical'] else None,
                'finite_window_prediction_run': False}
        row['largest_T4096_tail'] = max(abs(v['profiles'][r]['tail_bits']['4096'])
                                       for v in full['sampled'].values() for r in ('seed', 'thermal', 'unbound'))
        rows.append(row)
    shape = [r for r in rows if r['batch'] == 'shape']
    byid = {r['id']: r for r in rows}
    p1 = []
    for r in shape:
        full = cases[r['case_ids']['full']]
        probability = full['physical']['seed']['256']['deadline']['expanded']
        passed = r['markers']['C'] and all(probability > cases[r['case_ids'][m]]['physical']['seed']['256']['deadline']['expanded']+
                    protocol['tolerances']['rate_or_physical'] for m in ('cut_A_to_B', 'cut_B_to_C', 'cut_C_to_A'))
        if passed:
            p1.append(r['id'])
    p3, p4, p7, damage = [], [], [], []
    for alpha in (.5, 1.):
        for supply in (.15, .6):
            prefix = f'B-a{alpha:g}-s{supply:g}-'
            group = [byid[prefix+'R'+str(i)] for i in range(7)]
            closure = [byid[prefix+'R'+str(i)]['closure_T256'] for i in (1, 3, 6)]
            recovery = []
            for i in (4, 5):
                row = byid[prefix+'R'+str(i)]
                full = cases[row['case_ids']['full']]
                cut = cases[row['case_ids']['cut_C_to_A']]
                a = full['structure']['pulse_recovery']['delays']['64.0']['pre_function_and_endpoint_recovery']
                b = cut['structure']['pulse_recovery']['delays']['64.0']['pre_function_and_endpoint_recovery']
                recovery.append(a)
                p4.append({'setting': row['id'], 'joint_recovery_difference': a-b})
            p3.append({'anchor': prefix, 'closures_R1_R3_R6': closure, 'recovery_R4_R5': recovery,
                       'closure_order': closure[0] <= closure[1]+1e-8 and closure[1] <= closure[2]+1e-8
                                        and closure[2]-closure[0] > 1e-8,
                       'recovery_order': recovery[0]-recovery[1] > 1e-8})
            tau = [r['persistence']['tau_up'] for r in group]
            for reference in ('all_assistance_off', 'unbound'):
                delta = [r['contrasts'][reference]['cadences']['0.25']['delta_bits'] for r in group]
                if np.std(tau) == 0 or np.std(delta) == 0:
                    correlation = None
                else:
                    correlation = float(spearmanr(tau, delta).statistic)
                p7.append({'anchor': prefix, 'contrast': reference, 'spearman_r': correlation,
                           'tau_up': tau, 'delta_bits': delta})
            for low, high in ((0, 1), (1, 2)):
                l, h = byid[prefix+'R'+str(low)], byid[prefix+'R'+str(high)]
                left = cases[h['case_ids']['full']]; right = cases[l['case_ids']['full']]
                comp = contrast(left, right, protocol)
                if comp['cadences']['0.25']['positive'] and h['persistence']['tau_up'] < l['persistence']['tau_up']-1e-8:
                    damage.append({'from': l['id'], 'to': h['id'], 'contrast': comp})
    predictions = {
        'P1': {'passed': bool(p1), 'witness_settings': p1},
        'P2': {'passed': any(r['alpha'] == .5 and r['markers']['C'] for r in shape)},
        'P3': {'passed': all(r['closure_order'] and r['recovery_order'] for r in p3), 'anchors': p3},
        'P4': {'passed': any(r['joint_recovery_difference'] > 1e-8 for r in p4), 'comparisons': p4},
        'P5': {'passed': any(r['J_thermal'] for r in rows)},
        'P6': {'passed': any(r['J_mechanism'] for r in rows)},
        'P7a': {'passed': all(r['spearman_r'] is not None and r['spearman_r'] > 0 for r in p7), 'descriptive_associations': p7},
        'P7b': {'passed': None, 'status': 'separate opportunity-window freeze, not run'}}
    counts = {flag: sum(bool(r[flag]) for r in rows) for flag in
              ('J_thermal', 'J_unbound', 'J_mechanism', 'strong_J_thermal', 'strong_J_unbound', 'strong_J_mechanism')}
    counts.update({k: sum(r['markers'][k] is True for r in rows) for k in
                   ('C', 'C_funded', 'funding', 'R', 'R_base', 'R_recovery', 'strong_path')})
    counts['cadence_flips_T256'] = sum(c['sign_flip'] for r in rows for c in r['contrasts'].values())
    return {'counts': counts, 'predictions': predictions, 'settings': rows,
            'damage_as_breadth': damage,
            'complete_parameter_maps_retained': True}


def main():
    protocol_path = DOC/'PROTOCOL.json'
    protocol = json.loads(protocol_path.read_text())
    status = json.loads((DOC/'SCIENCE_STATUS.json').read_text())
    if status['status'] != 'complete':
        raise RuntimeError('Incomplete grid; do not score as complete')
    cases = {c['id']: json.loads((DOC/'cases'/(c['id']+'.json')).read_text()) for c in protocol['cases']}
    result = summarize(protocol, cases)
    result['protocol_sha256'] = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    result['run_status'] = status['status']
    result['wall_seconds'] = sum(r['profile']['wall_seconds'] for r in status['cases'].values())
    result['peak_job_bytes'] = max(r['profile']['peak_job_bytes'] for r in status['cases'].values())
    atomic_json(DOC/'SUMMARY.json', result)
    fields = ['setting', 'C_probability', 'C_retained_probability', 'tau_up', 'post_startup_uptime',
              'closure', 'external_funding_LB', 'thermal_birth_fraction', 'C', 'C_funded', 'R',
              'J_thermal', 'J_unbound', 'J_mechanism', 'strong_path', 'unbound_delta_primary', 'mechanism_delta_primary']
    flat = []
    for row in result['settings']:
        flat.append(dict(zip(fields, [row['id'], row['primary_depth']['depth_by_deadline'],
            row['primary_depth']['depth_and_retained_expansion'], row['persistence']['tau_up'],
            row['persistence']['post_startup_uptime_fraction'], row['closure_T256'], row['external_funding_LB'],
            row['bath_forward_birth_fraction'], row['markers']['C'], row['markers']['C_funded'], row['markers']['R'],
            row['J_thermal'], row['J_unbound'], row['J_mechanism'], row['markers']['strong_path'],
            row['contrasts']['unbound']['cadences']['0.25']['delta_bits'],
            row['contrasts']['all_assistance_off']['cadences']['0.25']['delta_bits']])))
    with (DOC/'SETTING_MAP.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fields); writer.writeheader(); writer.writerows(flat)
    table = ['| Setting | Depth + retained | Uptime 64–256 | Closure | External funding LB | Δ unbound bits | Δ all-off bits | C / R / J mechanism |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for r in flat:
        table.append(f"| {r['setting']} | {r['C_retained_probability']:.4f} | {r['post_startup_uptime']:.3f} | "
            f"{r['closure']:.3f} | {r['external_funding_LB']:.3f} | {r['unbound_delta_primary']:+.2f} | "
            f"{r['mechanism_delta_primary']:+.2f} | {int(r['C'])} / {int(r['R'])} / {int(r['J_mechanism'])} |")
    counts = result['counts']
    text = f'''# Robust three-link compounding — complete frozen results

Finite-history lushness is primary. Rates diagnose ongoing contribution under
the maintained boundary; neither rates nor structural markers replace the full
continuation. No entropy is removed for damage, turnover, noise or thermal events.

All {len(protocol['cases'])} unique cases completed, covering 12 shape and 28
robustness settings, six mechanism arms in shape and three in robustness, three
cadences and five horizons. Identical cases were reused by exact key, not
averaged or chosen by outcome. Total capped worker time {result['wall_seconds']/60:.1f}
minutes; maximum process-tree memory {result['peak_job_bytes']/1024**2:.1f} MiB.

## Separate and joint results

{chr(10).join('- '+k+': '+str(v)+' / 40 settings' for k,v in counts.items() if k != 'cadence_flips_T256')}

At T256 there are {counts['cadence_flips_T256']} positive/negative sign reversals
across the declared cadence corridor among reported full-mechanism comparisons.
The full JSON retains every signed comparison and the solver residual allowance.
No representative cadence is selected to rescue a result.

The C flag means the conservative initial-seed three-link certificate and its
retained-expansion joint probability both reach 0.01. C_funded additionally
requires external-spending lower bound at least 0.8 and thermal forward birth
share at most 0.05. A funding-marker failure is not renamed an absence of
compounding. R requires actual post-startup functional uptime at least 0.5 and
closure at most 0.1; actual pulse arms additionally require the frozen conditional
and unconditional restoration benchmarks. Non-pulse arms are not credited with
passing an unperformed recovery test.

J_mechanism adds positive T256 full-minus-all-off AND full-minus-C-to-A-cut at
every cadence. J_thermal and J_unbound instead require the corresponding same-law
preparation advantage; those are different claims. Strong J further connects
depth by 64, function at 64, expansion at 256 and no structural closure on the
same paths. These are prospective reporting thresholds, not bonuses in lushness.

## Filed predictions

{chr(10).join('- '+k+': '+('not run' if v['passed'] is None else 'passed' if v['passed'] else 'failed') for k,v in result['predictions'].items())}

Exact component scores and P7 descriptive associations are in SUMMARY.json.
P7 is a restricted persistence/repayment hypothesis, not a theorem. Opportunity
windows, whole-type knockouts, single-type/network comparisons and spatial
replication were not added to this batch. Removing a named link tautologically
kills the corresponding named witness; the independent ablation readouts are
retained physical expansion, arrival, capture and recovery.

## Complete setting map

Differences below are T256, cadence0.25, for compact reading. The J flags still
require all three cadences. All C/R/L outcomes, positive and negative, remain.

{chr(10).join(table)}

## Structural interpretation and scope

The physical carrier is well-mixed count chemistry with three actual catalytic
roles, paid construction/capture, basal reconstruction and matched native
stochastic processes. Irreversible material loss is a nonequilibrium boundary;
post-loss thermal/background dynamics continue. Pulse scores include their
pre-damage history and pulse heat closes the energy ledger. Known-root thermal
reference averaging adds no entropy for drawing the initial frame.

The tracker is query-side, conservative and may miss many true chains. Its
ongoing completion rate is a lower-bound detector rate, not population genealogy.
The coordinate decomposition conditions on full previous physical state and a
fixed next-coordinate order; it explains the result without changing it.
Fixed-jump diagnostics use the maintained native generator, not equal durations
or an augmented pulse clock. Expected event count and finite temporal term are
reported beside finite-history scores; the finite term is not a structure score.

{len(result['damage_as_breadth'])} registered adjacent damage contrasts gain
primary-cadence breadth while losing functional uptime. These remain adverse
readouts. Late finite profiles and residual offsets are retained, including
unresolved T4096 tails; a diagnostic limiting rate never overrides them.

This is not a spatial gas experiment: no translational motion is present. A
count-stage pass cannot overturn the earlier lattice seed-versus-unbound result.
The apparatus types are not valuers; this batch establishes no ethical ranking,
network superiority or open-ended/unbounded expansion.

Sources/configs were frozen before comparisons. See [protocol](PROTOCOL.json),
[full scores](SUMMARY.json), [complete table](SETTING_MAP.csv), and per-case JSON
under cases/. All raw kernels are reconstructable ignored output; no deletion,
commit, push or Drive edit was performed by this run.
'''
    (DOC/'RESULTS.md').write_text(text, encoding='utf-8')
    print(json.dumps({'counts': counts, 'predictions': {k: v['passed'] for k,v in result['predictions'].items()},
                      'minutes': result['wall_seconds']/60}, indent=2))


if __name__ == '__main__':
    main()
