"""Compare completed fixed interventions without replacing subject intervals."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from omega_v2.testbed.analysis.observed_history import interval_comparison
from omega_v2.testbed.analysis.temporal_profile import crossover
from omega_v2.testbed.workflow.manifest import atomic_json

DOC = ROOT/'docs/research_notes/lushness_testbed/domination_friction'


def main():
    status = json.loads((DOC/'SURVEY_STATUS.json').read_text())
    loaded = {}
    for receipt in status['cases']:
        if receipt['status'] != 'complete':
            continue
        path = DOC/'cases'/(receipt['identity']+'.json')
        if hashlib.sha256(path.read_bytes()).hexdigest() != receipt['result_sha256']:
            raise RuntimeError('Comparison result no longer matches its run receipt')
        loaded[receipt['id']] = json.loads(path.read_text())
    cases = {r['id']: r['configuration'] for r in status['cases']}
    comparisons = []
    families = {}
    for name, result in loaded.items():
        case = cases[name]
        if 'reference_id' not in case:
            continue
        idle = loaded.get(case['reference_id'])
        if idle is None:
            continue
        comparisons_by_clock = {}
        for cadence, data in result['cadences'].items():
            by_time = {}
            for time, a in data['profiles']['device_present'].items():
                b = idle['cadences'][cadence]['profiles']['device_present'][time]
                allowance = a['global_numerical_allowance']+b['global_numerical_allowance']
                delta = a['global_bits']-b['global_bits']
                pa = result['physical']['device_present'][time]
                pb = idle['physical']['device_present'][time]
                gain_d = pa['ledger'].get('net_capture_D', 0)-pb['ledger'].get('net_capture_D', 0)
                loss_s = pb['ledger'].get('net_capture_S', 0)-pa['ledger'].get('net_capture_S', 0)
                by_time[time] = {'global_delta_bits': delta, 'global_error_allowance': allowance,
                    'global_sign': 1 if delta > allowance+1e-5 else -1 if delta < -allowance-1e-5 else 0,
                    'subjects': {subject: interval_comparison(a['subjects'][subject], b['subjects'][subject],
                                                             allowance+1e-5) for subject in ('D', 'S')},
                    'net_capture_D_gain': gain_d, 'net_capture_S_loss': loss_s,
                    'appropriation_ratio': gain_d/loss_s if gain_d > 0 and loss_s > 0 else None,
                    'friction_fuel': pa['ledger'].get('friction_fuel', 0),
                    'suppressed_attempts': pa['suppressed_attempts'],
                    'S_access_occupancy_change': pa['average']['S.access']-pb['average']['S.access'],
                    'S_trap_occupancy_change': pa['average']['S.trap']-pb['average']['S.trap'],
                    'S_apparatus_change': pa['average']['S.apparatus']-pb['average']['S.apparatus'],
                    'S_paid_build_change': pa['ledger'].get('build_S', 0)-pb['ledger'].get('build_S', 0),
                    'coordinate_share_changes': {order: {
                        subject: a['coordinate_orders'][order][subject]-b['coordinate_orders'][order][subject]
                        for subject in ('background', 'D', 'S')} for order in a['coordinate_orders']},
                    'global_rate_difference_diagnostic': data['limiting_rate']-idle['cadences'][cadence]['limiting_rate'],
                    'temporal_crossover': crossover(pa, pb)}
            comparisons_by_clock[cadence] = by_time
        comparisons.append({'id': name, 'reference_id': case['reference_id'],
                            'parameters': case['parameters'], 'policy': case['policy'],
                            'comparisons': comparisons_by_clock})
        families.setdefault(case['reference_id'], []).append(name)
    choices = {}
    for reference, candidates in families.items():
        names = [reference]+candidates
        choice = {}
        for time in loaded[reference]['cadences']['0.25']['profiles']['device_present']:
            score = {n: loaded[n]['cadences']['0.25']['profiles']['device_present'][time] for n in names}
            best = max(names, key=lambda n: score[n]['global_bits'])
            possible = {}
            for subject in ('D', 'S'):
                max_lower = max(score[n]['subjects'][subject]['lower_bits'] for n in names)
                possible[subject] = [n for n in names
                                     if score[n]['subjects'][subject]['upper_bits']+1e-5 >= max_lower]
            max_lower_global = max(score[n]['global_bits']-score[n]['global_numerical_allowance']
                                   for n in names)
            global_possible = [n for n in names if score[n]['global_bits']
                               +score[n]['global_numerical_allowance']+1e-5 >= max_lower_global]
            choice[time] = {'cadence': .25, 'whole_field_largest_computed_score': best,
                            'whole_field_possible_maximizers': global_possible,
                            'possible_self_maximizers_from_bounds': possible,
                            'self_best_not_selected_by_bound_midpoint': True}
        choices[reference] = choice
    preparation_controls = {}
    for reference in families:
        base = loaded[reference]
        controls = {}
        for cadence, data in base['cadences'].items():
            controls[cadence] = {time: {
                name: data['profiles'][name][time]['global_bits']-a['global_bits']
                for name in ('ordinary_preparation', 'unassembled_preparation')}
                for time, a in data['profiles']['device_present'].items()}
        preparation_controls[reference] = controls
    atomic_json(DOC/'COMPARISONS.json', {'status': status['status'], 'cases': comparisons,
                                       'fixed_candidate_choices': choices,
                                       'same_idle_law_preparation_controls': preparation_controls})
    table = ['| Case | Global Δ bits | D marginal difference | S marginal difference | D capture gain | S capture loss | Friction fuel |',
             '| --- | ---: | --- | --- | ---: | ---: | ---: |']
    for row in comparisons:
        x = row['comparisons']['0.25']['256']
        table.append(f"| {row['id']} | {x['global_delta_bits']:+.3f} | "
                     f"{x['subjects']['D']['verdict']} | {x['subjects']['S']['verdict']} | "
                     f"{x['net_capture_D_gain']:+.3f} | {x['net_capture_S_loss']:+.3f} | "
                     f"{x['friction_fuel']:.3f} |")
    flips = []
    for row in comparisons:
        for time in row['comparisons']['0.25']:
            signs = {r[time]['global_sign'] for r in row['comparisons'].values()}
            if -1 in signs and 1 in signs:
                flips.append({'case': row['id'], 'time': time})
    text = f'''# First fixed-friction map

Status: {status['status']}. This is a small initial mechanism map, not the full
design sweep. All interventions use the same declared world inventory and
shared-source prescription as their idle-device reference. Policy changes
alter the induced generator. Marginal histories remain hidden-Markov.

{len(loaded)} cases are retained. Global finite-history lushness is exact up to
reported numerical residuals; D and S objectives are certified conditioning
intervals. Unresolved signs are not ties. No welfare reward, suffering variable,
persistence filter or subtraction of intervention randomness is used.

## T256, cadence 0.25

{chr(10).join(table)}

The comparison map retains all horizons and cadences. {len(flips)} global
comparisons change sign across cadences. Whole-field best candidates and possible
self-objective maximizers are listed separately in COMPARISONS.json; bound
midpoints never decide a self objective. The family contains only the listed
fixed interventions, not all possible adaptive policies. The candidate-choice
table uses cadence0.25; every signed physical comparison retains all three.
Same-idle-law ordinary and unassembled preparation controls are also retained
at every horizon and cadence, without adding entropy for choosing a root.

## Scope

The target is S mobility. Steering can redirect into other physical S mobility
or chemistry channels and preserves S's exit rate at the same full state only.
It does not match integrated event counts, work or occupied states. Apparatus,
charge and the friction device must be present for active intervention.

Native chemistry obeys detailed balance with the source and active drive
removed. Active friction is an explicitly one-way nonequilibrium control
boundary with D fuel expenditure; the first-law ledger closes, but this is not
a complete reversible chemical implementation of a controller. The energy-shift
check and a chemical control implementation remain further modules.

Ordinary and unassembled reference preparations retain the same physical
degrees of freedom and can assemble under native dynamics. Any differences
reported for these roots are preparation comparisons, not an excision action.
The unassembled reference is coarse count matter, not microscopic gas.

All settings and costs are mechanism assumptions to investigate. A gain or loss
under a named intervention must be interpreted through capture, construction,
trap residence, authority and costs. Naming an objective does not establish
its ethical verdict.

[Implemented model](MODEL.md) · [Full comparisons](COMPARISONS.json) ·
[Structural interpretation](INTERPRETATION.md) · [Run records](SURVEY_STATUS.json)
'''
    (DOC/'RESULTS.md').write_text(text, encoding='utf-8')
    print(json.dumps({'cases': len(loaded), 'contrasts': len(comparisons),
                      'global_cadence_flips': flips, 'status': status['status']}, indent=2))


if __name__ == '__main__':
    main()
