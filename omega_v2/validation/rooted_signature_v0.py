"""Present-conditioned signature moments: logical calibration, not lushness validation."""

import argparse
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from omega_v2.finite.extent_probe_models import Device, Event, Outcome, devices
from omega_v2.finite.rooted_signature_moments import rooted_signature_moments


@dataclass
class Case:
    device: Device
    root: tuple
    feature_map: object
    view: str = 'physical'


def simultaneous_coin():
    states = ((0, 0), (0, 1), (1, 0), (1, 1))
    events = (Event((0,), (0,)), Event((1,), (1,)))
    rows = {s: (Outcome(s, .5), Outcome((1-s[0], 1-s[1]), .5, events)) for s in states}
    return Device('shared_coin', states, rows, {(0, 0): 1.},
                  'Both resolved bits use one native coin; same local flip marginals as gas_two')


def row_split(device):
    rows = {s: tuple(Outcome(o.target, o.probability/2, o.events)
                     for o in outcomes for _ in range(2))
            for s, outcomes in device.rows.items()}
    return Device(device.name+'_row_split', device.states, rows, device.initial,
                  'Each row split into two half-weight encodings of the SAME physical outcome')


def one_jump(name, probabilities):
    """Native clock/bit system; output-bit view retains actual timing of its one jump."""
    stop = len(probabilities)
    states = tuple((t, bit) for t in range(stop+1) for bit in (0, 1))
    rows = {}
    for t, bit in states:
        if t == stop:
            rows[t, bit] = (Outcome((t, bit), 1.),)
            continue
        timer = Event((0,), (0,))
        tail = sum(probabilities[t:])
        hazard = probabilities[t]/tail if tail > 0 else 0.
        if bit:
            rows[t, bit] = (Outcome((t+1, bit), 1., (timer,)),)
        else:
            outcomes = []
            if hazard > 0:
                outcomes.append(Outcome((t+1, 1), hazard,
                                        (timer, Event((0, 1), (1,)))))
            if hazard < 1:
                outcomes.append(Outcome((t+1, 0), 1-hazard, (timer,)))
            rows[t, bit] = tuple(outcomes)
    return Device(name, states, rows, {(0, 0): 1.},
                  'One bit changes once; timer is retained in dynamics, output-bit view declared')


def cases():
    out = []
    base = devices()
    for device in base:
        root = next(iter(device.initial))
        name = device.name
        if name.endswith('_alias'):
            feature = lambda s: np.asarray(s[:2], dtype=float)
        elif name.startswith(('ring_', 'resource_')) or name in ('reconvergence', 'single_corridor'):
            lookup = {s: np.eye(len(device.states))[i] for i, s in enumerate(device.states)}
            feature = lambda s, lookup=lookup: lookup[s]
        else:
            feature = lambda s: np.asarray(s, dtype=float)
        out.append(Case(device, root, feature))
        if name.startswith('resource_'):
            out.append(Case(device, root, lambda s: np.eye(3)[
                0 if s[0] == s[1] == 0 else 1 if s[0] else 2], 'chemistry'))
    shared = simultaneous_coin()
    out.append(Case(shared, (0, 0), lambda s: np.asarray(s, dtype=float)))
    split = row_split(next(d for d in base if d.name == 'reversible_gate_on'))
    out.append(Case(split, (0, 0), lambda s: np.asarray(s, dtype=float)))
    for name, probabilities in (
        ('early_jump', [1.]), ('delayed_jump', [0., 1.]),
        ('moment_even', [1/16, 0, 10/16, 0, 5/16, 0]),
        ('moment_odd', [0, 5/16, 0, 10/16, 0, 1/16]),
    ):
        device = one_jump(name, probabilities)
        out.append(Case(device, (0, 0), lambda s: np.asarray([s[1]], dtype=float), 'output_bit'))
    return out


def summarize(result):
    words = result['words']
    groups = []
    for degree in sorted({len(w) for w in words}):
        for clocks in range(degree):
            indices = [i for i, w in enumerate(words) if len(w) == degree and w.count(0) == clocks]
            mean = result['mean'][indices]
            second = result['second_moment'][np.ix_(indices, indices)]
            covariance = result['covariance'][np.ix_(indices, indices)]
            groups.append({'degree': degree, 'clock_letters': clocks,
                           'dimension': len(indices), 'mean_squared_norm': float(mean@mean),
                           'second_trace': float(np.trace(second)),
                           'covariance_trace': float(np.trace(covariance)),
                           'second_eigenvalues': np.linalg.eigvalsh(second).tolist(),
                           'covariance_eigenvalues': np.linalg.eigvalsh(covariance).tolist()})
    return groups


def compare_arrays(a, b):
    return {key: float(np.max(np.abs(a[key]-b[key])))
            for key in ('mean', 'second_moment', 'covariance')}


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=Path('docs/research_notes/omega_v2/rooted_signature_v0'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    records, archive, index, model_records = [], {}, {}, []
    for case in cases():
        device = case.device
        initial, kernel = device.arrays()
        model_records.append({'name': device.name, 'view': case.view, 'states': device.states,
                              'root': case.root, 'description': device.description,
                              'features': [case.feature_map(s).tolist() for s in device.states],
                              'kernel': kernel.tolist(),
                              'root_replaces_previous_initial': initial.tolist()})
        for horizon in (2, 4, 6, 12):
            result = rooted_signature_moments(device, case.root, case.feature_map, horizon)
            root_law = np.asarray([float(s == case.root) for s in device.states])
            endpoint_law = np.asarray([result['endpoints'].get(s, 0.) for s in device.states])
            endpoint_error = float(np.max(np.abs(endpoint_law-root_law@np.linalg.matrix_power(
                kernel, horizon))))
            index[device.name, case.view, horizon, 3] = result
            stem = f'{device.name}_{case.view}_H{horizon}'
            for key in ('mean', 'second_moment', 'covariance'):
                archive[f'{stem}_{key}'] = result[key]
            record = {'case': device.name, 'view': case.view, 'horizon': horizon,
                      'degree': 3, 'root': case.root, 'mass': float(result['mass']),
                      'endpoint_error': endpoint_error,
                      'words': [tuple(int(j) for j in w) for w in result['words']],
                      'groups': summarize(result)}
            records.append(record)
            if horizon == 6:
                group = next(g for g in record['groups'] if g['degree'] == 2 and
                             g['clock_letters'] == 0)
                print(device.name, case.view, 'H6 spatial degree2',
                      'second', round(group['second_trace'], 8),
                      'branch covariance', round(group['covariance_trace'], 8))

    checks = {}
    for suffix in ('alias', 'row_split'):
        checks[f'gate_{suffix}'] = compare_arrays(index['reversible_gate_on', 'physical', 6, 3],
            index['reversible_gate_on_'+suffix, 'physical', 6, 3])
    original = index['reversible_gate_on', 'physical', 6, 3]
    renamed = index['reversible_gate_on_renamed', 'physical', 6, 3]
    word_index = {w: i for i, w in enumerate(renamed['words'])}
    permutation = [word_index[tuple(0 if j == 0 else 3-j for j in w)] for w in original['words']]
    reordered = {'mean': renamed['mean'][permutation],
                 'second_moment': renamed['second_moment'][np.ix_(permutation, permutation)],
                 'covariance': renamed['covariance'][np.ix_(permutation, permutation)]}
    checks['gate_renamed'] = compare_arrays(original, reordered)
    for name in ('deterministic_parallel', 'deterministic_chain', 'deterministic_fork_join',
                 'reconvergence', 'single_corridor'):
        checks[name+'_terminal_wait'] = compare_arrays(index[name, 'physical', 6, 3],
                                                      index[name, 'physical', 12, 3])
    checks['moment_collision_degree3'] = compare_arrays(index['moment_even', 'output_bit', 6, 3],
                                                       index['moment_odd', 'output_bit', 6, 3])
    extra = []
    for case in cases():
        if case.device.name.startswith('moment_'):
            result = rooted_signature_moments(case.device, case.root, case.feature_map, 6, degree=4)
            extra.append(result)
            archive[case.device.name+'_degree4_mean'] = result['mean']
            archive[case.device.name+'_degree4_second'] = result['second_moment']
    checks['moment_collision_degree4'] = compare_arrays(*extra)
    print('CHECKS', json.dumps(checks))
    root = Path(__file__).resolve().parents[1]
    files = ['finite/rooted_path_signature.py', 'finite/rooted_signature_moments.py',
             'finite/extent_probe_models.py', 'validation/rooted_signature_v0.py']
    snapshot = args.output/'sources'
    snapshot.mkdir(exist_ok=True)
    hashes = {}
    for file in files:
        content = (root/file).read_bytes()
        hashes[file] = hashlib.sha256(content).hexdigest()
        (snapshot/Path(file).name).write_bytes(content)
    output = {'status': 'present-rooted development signature profile; not an adopted volume',
              'seconds': time.perf_counter()-start, 'checks': checks, 'records': records,
              'models': model_records, 'source_sha256': hashes,
              'max_mass_error': max(abs(r['mass']-1) for r in records),
              'max_endpoint_error': max(r['endpoint_error'] for r in records)}
    (args.output/'results.json').write_text(json.dumps(output, indent=2), encoding='utf-8')
    np.savez_compressed(args.output/'moments.npz', **archive)
    print('COMPLETE', output['seconds'], 'seconds', len(records), 'profiles',
          'mass error', output['max_mass_error'])


if __name__ == '__main__':
    run()
