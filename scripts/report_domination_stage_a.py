"""Physical Stage A curves, honest marginal intervals and bounded interpolation."""
import csv
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.analysis.observed_history import interval_comparison
from omega_v2.testbed.analysis.temporal_profile import crossover
from omega_v2.testbed.workflow.manifest import atomic_json

DOC = ROOT/'docs/research_notes/lushness_testbed/domination_stage_a'


def csv_write(name, rows, fields=None):
    if fields is None:
        fields = list(dict.fromkeys(k for r in rows for k in r))
    with (DOC/name).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sign(value, tolerance):
    return 1 if value > tolerance else -1 if value < -tolerance else 0


def subject_sign(verdict):
    return {'strict_positive': 1, 'strict_negative': -1}.get(verdict, 0)


def load_status(mode='survey'):
    status = json.loads((DOC/(mode.upper()+'_STATUS.json')).read_text())
    loaded, configs = {}, {}
    for receipt in status['cases']:
        if receipt['status'] != 'complete':
            continue
        path = DOC/'cases'/(receipt['identity']+'.json')
        if hashlib.sha256(path.read_bytes()).hexdigest() != receipt['result_sha256']:
            raise RuntimeError('Result hash mismatch')
        loaded[receipt['id']] = json.loads(path.read_text())
        configs[receipt['id']] = receipt['configuration']
    return status, loaded, configs


def comparisons(loaded, configs):
    rows = []
    preparations = []
    for name, case in configs.items():
        result = loaded[name]
        if 'reference_id' not in case:
            for cadence, clock in result['cadences'].items():
                for time, base in clock['profiles']['device_present'].items():
                    for root in ('ordinary_preparation', 'unassembled_preparation'):
                        a = clock['profiles'][root][time]
                        preparations.append({'id': name, 'root': root, 'cadence': float(cadence),
                            'horizon': float(time), 'global_delta': a['global_bits']-base['global_bits'],
                            **{f'{s}_{k}': v for s in ('D', 'S') for k, v in interval_comparison(
                                a['subjects'][s], base['subjects'][s], 1e-5).items()}})
            continue
        reference = loaded.get(case['reference_id'])
        if reference is None:
            continue
        root = case.get('comparison_root', 'device_present')
        for cadence, clock in result['cadences'].items():
            for time, a in clock['profiles'][root].items():
                b = reference['cadences'][cadence]['profiles'][root][time]
                pa, pb = (r['physical'][root][time] for r in (result, reference))
                ledger, idle_ledger = pa['ledger'], pb['ledger']
                tolerance = 1e-5+a['global_numerical_allowance']+b['global_numerical_allowance']
                gain = ledger.get('net_capture_D', 0)-idle_ledger.get('net_capture_D', 0)
                loss = idle_ledger.get('net_capture_S', 0)-ledger.get('net_capture_S', 0)
                fuel = ledger.get('friction_fuel', 0)
                upkeep_change = ledger.get('device_upkeep', 0)-idle_ledger.get('device_upkeep', 0)
                native_events = pb['average']['S_event_rate']*float(time)
                ordinary = reference['cadences'][cadence]['profiles']['ordinary_preparation'][time]
                policy = case['policy']
                row = {'id': name, 'slice': case['slice'], 'target': case['target'],
                    'supply': case['parameters'].get('supply', .12),
                    'kappa': case['parameters'].get('kappa', 0),
                    'mode': 'field' if case['slice'] == 'A6' else policy.get('mode', 'blocking'),
                    'phi': policy.get('phi', 0),
                    'cost': None if case['slice'] == 'A6' else policy.get('cost', 1),
                    'field_shift': case['parameters'].get('field_shift', 0),
                    'horizon': float(time), 'cadence': float(cadence), 'comparison_root': root,
                    'global_delta': a['global_bits']-b['global_bits'], 'tolerance': tolerance,
                    'global_sign': sign(a['global_bits']-b['global_bits'], tolerance),
                    'global_vs_ordinary_preparation': a['global_bits']-ordinary['global_bits'],
                    'capture_D_gain': gain, 'capture_S_loss': loss,
                    'capture_total_change': gain-loss, 'friction_fuel': fuel,
                    'incremental_device_upkeep': upkeep_change,
                    'D_partial_energy_advantage': gain-fuel-upkeep_change,
                    'D_bank_change_vs_idle': ledger.get('net_D.charge', 0)-idle_ledger.get('net_D.charge', 0),
                    'appropriation_ratio': gain/loss if loss > 0 else None,
                    'suppressed_attempts': pa['suppressed_attempts'],
                    'idle_S_events': native_events,
                    'sigma': pa['suppressed_attempts']/native_events if native_events > 0 else None,
                    'S_access_change': pa['average']['S.access']-pb['average']['S.access'],
                    'S_build_location_change': pa['average']['S.construction']-pb['average']['S.construction'],
                    'S_trap_change': pa['average']['S.trap']-pb['average']['S.trap'],
                    'S_apparatus_change': pa['average']['S.apparatus']-pb['average']['S.apparatus'],
                    'S_paid_build_change': ledger.get('build_S', 0)-idle_ledger.get('build_S', 0),
                    'S_capture_change': -loss,
                    'rate_difference_diagnostic': clock['limiting_rate']-reference['cadences'][cadence]['limiting_rate'],
                    'delta_jumps': pa['expected_jumps']-pb['expected_jumps'],
                    'delta_finite_term': pa['finite_term_bits']-pb['finite_term_bits'],
                    'delta_local_destination_surprisal': pa['destination_surprisal_bits']-pb['destination_surprisal_bits'],
                    'estimated_temporal_crossover': crossover(pa, pb)['estimated_cadence'],
                    'temporal_crossover_status': crossover(pa, pb)['status'],
                    'temporal_crossover_is_asymptotic_not_exact': True}
                for subject in ('D', 'S'):
                    difference = interval_comparison(a['subjects'][subject], b['subjects'][subject], tolerance)
                    row.update({subject+'_'+k: v for k, v in difference.items()})
                    row[subject+'_sign'] = subject_sign(difference['verdict'])
                    old = a['subjects'][subject].get('one_observation_bounds')
                    if old:
                        row[subject+'_old_width'] = old['upper_bits']-old['lower_bits']
                        row[subject+'_new_width'] = a['subjects'][subject]['upper_bits']-a['subjects'][subject]['lower_bits']
                rows.append(row)
    return rows, preparations


def crossing_brackets(rows):
    grouped = defaultdict(dict)
    for r in rows:
        if r['slice'] not in ('A1', 'A2', 'A5'):
            continue
        key = tuple(r[k] for k in ('target', 'mode', 'supply', 'kappa', 'cost', 'horizon'))
        grouped[key].setdefault(r['phi'], []).append(r)
    result = []
    for key, curve in grouped.items():
        for subject in ('global', 'D', 'S'):
            for left, right in zip(sorted(curve), sorted(curve)[1:]):
                lrows, rrows = curve[left], curve[right]
                ls, rs = {r[subject+'_sign'] for r in lrows}, {r[subject+'_sign'] for r in rrows}
                lc = {r['cadence']: r[subject+'_sign'] for r in lrows}
                rc = {r['cadence']: r[subject+'_sign'] for r in rrows}
                crossings = [c for c in lc.keys() & rc.keys() if lc[c]*rc[c] == -1]
                if not crossings:
                    continue
                robust = len(ls) == len(rs) == 1 and next(iter(ls))*next(iter(rs)) == -1
                result.append(dict(zip(('target', 'mode', 'supply', 'kappa', 'cost', 'horizon'), key))
                              | {'subject': subject, 'phi_lower': left, 'phi_upper': right,
                                 'status': 'corridor_stable_bracket' if robust else 'cadence_conditional_bracket',
                                 'crossing_cadences': ';'.join(map(str, sorted(crossings)))})
    return result


def fuel_matches(rows):
    grouped = defaultdict(list)
    for r in rows:
        if r['supply'] == .12 and r['kappa'] == 1 and r['cost'] == 1 and r['slice'] in ('A1', 'A3'):
            grouped[(r['target'], r['mode'], r['horizon'], r['cadence'])].append(r)
    random_keys = [key for key in grouped if key[0].startswith('random')]
    output = []
    for key, role in grouped.items():
        if key[0].startswith('random') or key[0] == 'all_mobility':
            continue
        for random_key in random_keys:
            if key[1:] != random_key[1:]:
                continue
            curve = sorted(grouped[random_key], key=lambda r: r['phi'])
            for point in role:
                for left, right in zip(curve, curve[1:]):
                    a, b, x = left['friction_fuel'], right['friction_fuel'], point['friction_fuel']
                    if a == b or not min(a, b) <= x <= max(a, b):
                        continue
                    fraction = (x-a)/(b-a)
                    other = left['global_delta']+fraction*(right['global_delta']-left['global_delta'])
                    output.append({'role_id': point['id'], 'random_target': random_key[0],
                        'mode': key[1], 'horizon': key[2], 'cadence': key[3], 'fuel': x,
                        'random_phi_lower': left['phi'], 'random_phi_upper': right['phi'],
                        'global_role_minus_interpolated_random': point['global_delta']-other,
                        'role_delta_per_fuel': point['global_delta']/x if x else None,
                        'interpolated_random_delta_per_fuel': other/x if x else None,
                        'status': 'descriptive_interpolation_not_a_certified_physical_comparison'})
    return output


def main(mode='survey'):
    status, loaded, configs = load_status(mode)
    rows, preparations = comparisons(loaded, configs)
    clock_groups = defaultdict(list)
    for row in rows:
        clock_groups[(row['id'], row['horizon'])].append(row)
    for points in clock_groups.values():
        ds = {r['D_sign'] for r in points}
        gs = {r['global_sign'] for r in points}
        stable = len(points) == 3 and len(ds) == len(gs) == 1 and next(iter(ds))*next(iter(gs)) == -1
        for r in points:
            r['corridor_stable_D_global_divergence'] = stable
    csv_write('COMPARISON_MAP.csv', rows)
    csv_write('PREPARATIONS.csv', preparations)
    crossings = crossing_brackets(rows)
    csv_write('CROSSINGS.csv', crossings, ['target', 'mode', 'supply', 'kappa', 'cost',
              'horizon', 'subject', 'phi_lower', 'phi_upper', 'status', 'crossing_cadences'])
    divergence = [r for r in rows if r['D_sign']*r['global_sign'] == -1]
    csv_write('DIVERGENCE.csv', divergence, list(rows[0]) if rows else ['id'])
    csv_write('FUEL_MATCH.csv', fuel_matches(rows))
    primary = [r for r in rows if r['cadence'] == .25 and r['horizon'] == 256]
    agreements = Counter((r['global_sign'], r['S_sign']) for r in rows)
    flips = []
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r['id'], r['horizon'])].append(r)
    for (name, time), points in grouped.items():
        if {r['global_sign'] for r in points} >= {-1, 1}:
            flips.append({'id': name, 'horizon': time})
    choices = defaultdict(list)
    bills = defaultdict(set)
    for case in configs.values():
        if case['slice'] in ('A1', 'A2', 'A5'):
            bills[(case['parameters']['supply'], case['parameters']['kappa'])].add(case['policy']['cost'])
    for name, case in configs.items():
        if case['slice'] not in ('A1', 'A2', 'A3', 'A4', 'A5'):
            continue
        env = (case['parameters']['supply'], case['parameters']['kappa'])
        for cadence, clock in loaded[name]['cadences'].items():
            for time, profile in clock['profiles']['device_present'].items():
                costs = bills[env] if case['slice'] == 'A4' else [case['policy']['cost']]
                for bill in costs:
                    choices[(*env, bill, float(cadence), float(time))].append((name, profile))
    winner_rows = []
    for key, points in sorted(choices.items()):
        best_score = max(p['global_bits']-p['global_numerical_allowance'] for _, p in points)
        possible = [name for name, p in points
                    if p['global_bits']+p['global_numerical_allowance']+1e-5 >= best_score]
        best = max(points, key=lambda x: x[1]['global_bits'])
        self_choices = {}
        for subject in ('D', 'S'):
            max_lower = max(p['subjects'][subject]['lower_bits'] for _, p in points)
            candidates = [name for name, p in points
                          if p['subjects'][subject]['upper_bits']+1e-5 >= max_lower]
            self_choices[subject+'_possible_maximizers'] = ';'.join(candidates)
            self_choices['global_winner_possible_'+subject+'_optimum'] = best[0] in candidates
        winner_rows.append(dict(zip(('supply', 'kappa', 'fixed_bill', 'cadence', 'horizon'), key))
            | {'largest_computed_score': best[0], 'global_bits': best[1]['global_bits'],
               'possible_maximizers': ';'.join(possible), 'candidate_count': len(points),
               'scope': 'listed fixed interventions at fixed physical bill, not all adaptive strategies'}
            | self_choices)
    csv_write('FIXED_CHOICES.csv', winner_rows)
    complete = [r for r in status['cases'] if r['status'] == 'complete']
    summary = {'status': status['status'], 'cases': len(loaded), 'planned': status['total'],
        'comparison_rows': len(rows), 'cadence_flip_pairs': flips,
        'resolved_divergence_rows': len(divergence),
        'corridor_stable_divergence_pairs': sum(points[0]['corridor_stable_D_global_divergence']
                                               for points in clock_groups.values()),
        'paid_long_horizon_corridor_divergence_pairs': sum(
            points[0]['corridor_stable_D_global_divergence'] and points[0]['horizon'] >= 256
            and points[0]['cost'] in (1, 2) for points in clock_groups.values()),
        'resolved_D_rows': sum(r['D_sign'] != 0 for r in rows),
        'resolved_S_rows': sum(r['S_sign'] != 0 for r in rows),
        'S_global_sign_counts': {str(k): v for k, v in agreements.items()},
        'strength_crossing_brackets': len(crossings),
        'worker_seconds': sum(r['profile']['wall_seconds'] for r in complete),
        'peak_worker_MiB': max((r['profile']['peak_job_bytes']/1024**2 for r in complete), default=0),
        'elapsed_seconds': status.get('elapsed_seconds'),
        'max_energy_residual': max((x['energy_residual'] for x in loaded.values()), default=0),
        'max_integrated_energy_residual': max((abs(x['integrated_energy_residual']) for r in loaded.values()
            for root in r['physical'].values() for x in root.values()), default=0),
        'max_occupation_residual': max((x['sampled_occupation_residual'] for r in loaded.values()
            for clock in r['cadences'].values() for root in clock['profiles'].values() for x in root.values()), default=0)}
    account_path = DOC/'EXECUTION_ACCOUNT.json'
    if account_path.exists():
        account = json.loads(account_path.read_text())
        if account['source_hash'] == status['source_hash']:
            summary['recorded_worker_span_seconds'] = account['recorded_worker_span_seconds']
    atomic_json(DOC/'SUMMARY.json', summary)
    table = ['| Target / mode | Bill | T256 Δ bits range | D resolved / cases | S positive / negative |',
             '| --- | --- | ---: | ---: | ---: |']
    targets = defaultdict(list)
    for r in primary:
        targets[(r['target'], r['mode'], r['cost'])].append(r)
    for (target, mode_name, cost), points in sorted(targets.items()):
        bill = 'potential probe' if cost is None else f'{cost}'+(' (limit)' if cost == 0 else '')
        table.append(f"| {target} / {mode_name} | {bill} | {min(r['global_delta'] for r in points):+.3f} to "
                     f"{max(r['global_delta'] for r in points):+.3f} | "
                     f"{sum(r['D_sign'] != 0 for r in points)}/{len(points)} | "
                     f"{sum(r['S_sign'] == 1 for r in points)} / {sum(r['S_sign'] == -1 for r in points)} |")
    (DOC/'RESULTS.md').write_text(f'''# Constraint Stage A — numerical map

Status: **{status['status']}**. {len(loaded)}/{status['total']} cases retained;
{len(rows)} case/horizon/cadence comparisons. Complete finite-history lushness is
primary. Limiting rates and temporal asymptotic coefficients are diagnostics.

## T256, cadence 0.25

{chr(10).join(table)}

These ranges combine the stated strengths, costs and environments, rather than
averaging away signs. The full map retains each one separately. There are
{len(flips)} case/horizon sign flips across cadences; {len(crossings)} adjacent
strength brackets contain a sign crossing at one or more cadences. All brackets
are labeled for corridor stability. No crossing means none found on this grid.

The tighter subject-history intervals resolve D in
{summary['resolved_D_rows']}/{len(rows)} comparisons and S in
{summary['resolved_S_rows']}/{len(rows)}. There are {len(divergence)} strictly
resolved D/global divergences; unresolved intervals do not establish alignment,
ties or personal gains. No midpoint selects a winner.

## Physical accounts and scope

Capture is measured before friction or upkeep. Partial D energy advantage is
incremental net capture minus friction fuel minus incremental device upkeep,
all in charge-energy units. It is not personal lushness. The full bank balance
and energy conservation are reported independently. Apparatus stock, output,
access and trap occupancy accompany all comparisons.

Random controls target physical directed mobility edges. Fuel interpolation is
descriptive, inside observed support, and retains nonmonotonic branches. It
does not certify a ranking at an uncomputed strength. Preparation comparisons
are not a modeled replacement action. Field probes are conservative potential
contrasts; they are not claimed to match fuel spent by the driven interventions.

Maximum worker memory: {summary['peak_worker_MiB']:.1f} MiB. Summed worker time:
{summary['worker_seconds']/60:.2f} minutes. Largest generator energy residual:
{summary['max_energy_residual']:.3g}; integrated residual:
{summary['max_integrated_energy_residual']:.3g}; sampled occupation residual:
{summary['max_occupation_residual']:.3g}.

The [execution account](EXECUTION_ACCOUNT.json) records the full approximately
{summary.get('recorded_worker_span_seconds', 0)/60:.2f}-minute worker span across
the initial run and cached completion. The final status timer alone measures
the last cache-reconciliation invocation, not the duration of the science batch.

[Implemented specification](SPECIFICATION.md) · [Full map](COMPARISON_MAP.csv) ·
[Crossings](CROSSINGS.csv) · [Subject divergences](DIVERGENCE.csv) ·
[Preparation controls](PREPARATIONS.csv) · [Fuel interpolation](FUEL_MATCH.csv) ·
[Fixed-family choices](FIXED_CHOICES.csv) ·
[Structural reading](INTERPRETATION.md)
''', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'survey')
