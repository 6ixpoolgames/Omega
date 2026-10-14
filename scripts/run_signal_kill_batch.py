"""Prospectively register, engineering-gate, then cap the first W1/W2 batch."""
import argparse
import json
import sys
import uuid
from dataclasses import replace
from datetime import UTC, datetime
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omega_v2.testbed.aversive_signals import SignalParameters
from omega_v2.testbed.workflow.manifest import atomic_json, freeze_bundle, verify_bundle
from omega_v2.testbed.workflow.runner import run_frozen

DOC = ROOT/'docs/research_notes/lushness_testbed/aversive_signals'
REG = 'docs/research_notes/lushness_testbed/aversive_signals/FIRST_BATCH_PROTOCOL.json'


def prepare():
    if (ROOT/REG).exists():
        raise FileExistsError('Frozen registration cannot be overwritten')
    base = SignalParameters()
    cases = []
    for family in ('W1', 'W2'):
        for index, (ratio, upkeep, bias, fourth) in enumerate(product(
                (1., 2.), (.05, .25), (.25, .9), (.15, .6) if family == 'W1' else (.05, .5))):
            p = replace(base, struggle_cost=base.forage_cost*ratio,
                        signal_upkeep=base.metabolism*upkeep, escape_bias=bias)
            if family == 'W1':
                p = replace(p, hazard_damage_rate=fourth)
                arms = ['E', 'A', 'B', 'C', 'N']
                z = 1
            else:
                p = replace(p, hazard_on=.002, hazard_damage_rate=.015, signal_hijack=fourth)
                arms = ['D', 'E_prime', 'N_prime']
                z = 0
            cases.append({'id': f'{family}-{index:02d}', 'family': family,
                          'parameters': vars(p), 'arms': arms,
                          'root': [p.units(p.energy_cap), 0, 0, z, 1]})
    protocol = {
        'id': 'central-wager-w1-w2-first-batch', 'version': '1',
        'date': '2026-10-14', 'status': 'frozen_before_scientific_ranking',
        'scope': 'first bounded functional slice; not full r2 exhaustive grid or W3/W4',
        'cases': cases, 'cadences': [.125, .25, .5], 'primary_cadence': .25,
        'horizons': [16, 64, 256, 1024], 'primary_horizon': 64,
        'main_kill_horizons': [256, 1024],
        'primary': 'complete conditional sampled-state history entropy; randomness counts',
        'rate_role': 'asymptotic diagnostic; no replacement of finite objective',
        'layer': 'oracle comparison of fixed native physiology, no bounded-agent uncertainty',
        'qualification': {
            'tracking': {'mi_threshold_bits': .001, 'direction_tolerance': 1e-6,
                         'window': 1., 'decline_tolerance': 1e-6,
                         'definition': 'signal MI with a future decrease of matched signal-disabled one-window energy/location breadth; positive direction required'},
            'disposition_threshold': .05, 'minimum_signal_time': .05,
            'minimum_signal_fraction': .001, 'minimum_obstructed_index': .01,
            'suffering_index': 'integral of active obstructed signal times positive affordable escape propensity shift',
            'phenomenal_suffering_claim': False,
        },
        'tolerances': {'bits': 1e-5, 'rate': 1e-9, 'physical_comparison': 1e-6,
                       'residual': 1e-8,
                       'basis': 'conservative numerical tolerance above engineering and exact-reference residuals; no scientific differences inspected'},
        'grains': ['resolved', 'signal_merged_bounds'],
        'merged_method': 'conditioning lower; time-averaged conditional-entropy upper capped by full entropy; no Markov projection',
        'merged_limit': 'offset bounds only when projection is injective on recurrent states and disjoint from transient states',
        'coordinate_order': [3, 4, 0, 1, 2],
        'K1': {'comparison': 'A minus B', 'prerequisites': 'A tracking, disposition and obstructed; B no signal',
               'main': 'strict positive or compression at both grains, all three cadences, every T>=256, and offset limit'},
        'K2': {'comparison': 'D minus max(E_prime,N_prime)',
               'prerequisites': 'D low-MI nontracking and disposition; E_prime tracking and disposition; N_prime no signal',
               'functional_gain_veto': ['survival_at_deadline', 'food_input', 'escape_success'],
               'functional_gain_rule': 'any increase over the maximum comparator above tolerance vetoes clean K2; keep raw ranking',
               'main': 'same full corridor as K1; clean functional proxy result only'},
        'interpretation': {
            'single_point': 'valid adapter-relative functional counterexample if instantiated, independent of main robustness',
            'corridor': 'stronger registered main result; no flips or unresolved bounds permitted',
            'overlap': 'unresolved, never automatically a compression tie',
            'noninstantiation': 'report independently of ranking; no theory verdict',
            'no_hit': 'survival of these targets in this finite model, not confirmation',
            'cost_box': 'positive-cost model assumptions, not empirically calibrated physiological universal bounds',
        },
        'sources': ['COST_ANCHORS.md', 'FIRST_BATCH_SPEC.md'],
        'caps': {'seconds': 600, 'memory': 512*1024**2, 'output_cap': 64*1024**2},
        'smoke_case_ids': ['W1-15', 'W2-15'],
        'scientific_execution_allowed': True,
    }
    atomic_json(ROOT/REG, protocol)
    print(ROOT/REG)


def run(mode):
    protocol = json.loads((ROOT/REG).read_text(encoding='utf-8'))
    if protocol['status'] != 'frozen_before_scientific_ranking':
        raise ValueError('Scientific registration required')
    if mode == 'science':
        gate = json.loads((DOC/'FIRST_BATCH_SMOKE_STATUS.json').read_text(encoding='utf-8'))
        if gate['status'] != 'complete':
            raise RuntimeError('Engineering gate required')
        if verify_bundle(gate['run'])['config']['protocol'] != protocol:
            raise RuntimeError('Engineering gate used a different registration')
    stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6]
    out = ROOT/'results/local_runs/lushness_testbed/aversive_signals'/('first-'+mode+'-'+stamp)
    sources = [p.relative_to(ROOT).as_posix()
               for p in (ROOT/'omega_v2/testbed').rglob('*.py')]
    sources += ['omega_v2/__init__.py', REG,
                'scripts/run_bng_binding_calibration.py', 'scripts/run_signal_kill_batch.py',
                'scripts/signal_kill_batch_worker.py',
                'docs/research_notes/lushness_testbed/aversive_signals/COST_ANCHORS.md',
                'docs/research_notes/lushness_testbed/aversive_signals/FIRST_BATCH_SPEC.md']
    frozen = freeze_bundle(ROOT, out, sources, {'mode': mode, 'protocol': protocol})
    if mode == 'science' and frozen['source_hash'] != verify_bundle(gate['run'])['source_hash']:
        raise RuntimeError('Source changed since the engineering gate; rerun registered smoke')
    caps = dict(protocol['caps'])
    if mode == 'smoke':
        caps['seconds'] = 90
    execution = run_frozen(out, 'scripts/signal_kill_batch_worker.py', [str(out), mode], caps)
    atomic_json(out/'PROFILE.json', execution)
    status = 'complete' if execution['exit_code'] == 0 and not execution['cap_reason'] else 'incomplete'
    atomic_json(DOC/f'FIRST_BATCH_{mode.upper()}_STATUS.json',
                {'status': status, 'run': str(out), 'profile': execution})
    print(json.dumps({'run': str(out), **execution}, indent=2))
    return 0 if status == 'complete' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('prepare', 'smoke', 'science'))
    args = parser.parse_args()
    raise SystemExit(prepare() if args.mode == 'prepare' else run(args.mode))
