"""Small exact covers and out-of-sample checks of native continuous-time path covers."""

import argparse
import json
import platform
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
from math import exp, log2
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy
from scipy.linalg import expm

from omega_v2.finite.path_covering import (
    cover_profile,
    jump_distances,
    markov_histories,
    project_law,
    sample_telegraph,
    sampled_distance,
    wilson,
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT/'docs/research_notes/omega_v2/path_covering_v0'
ALPHAS = (.5, .9, .99, 1.0)
EPSILONS = (0.0, .25, .5)
HORIZONS = (.5, 1.0, 4.0)


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def generator(forward, backward=None):
    backward = forward if backward is None else backward
    return np.asarray([[-forward, forward], [backward, -backward]], dtype=float)


def append_profiles(rows, name, frame, horizon, paths, weights, distance):
    for epsilon in EPSILONS:
        solutions = cover_profile(distance, weights, epsilon*horizon, ALPHAS)
        for alpha, result in zip(ALPHAS, solutions, strict=True):
            rows.append({'case': name, 'frame': frame, 'T': horizon,
                         'epsilon_fraction': epsilon, 'epsilon_absolute': epsilon*horizon,
                         'alpha': alpha, 'path_count': len(paths), **result})


def exact_panel(output):
    rows, ensembles, diagnostics = [], [], []
    for horizon in HORIZONS:
        for stationary, rates in ((True, (.05, 1, 10)), (False, (.1, 1, 10))):
            for rate in rates:
                name = f"{'stationary' if stationary else 'accelerated'}_{rate:g}"
                q = generator(rate)
                initial = np.asarray([.5, .5] if stationary else [1.0, 0.0])
                paths, weights = markov_histories(initial, expm(q*horizon/4), 4)
                distance = sampled_distance(paths, [horizon/4]*4)
                append_profiles(rows, name, 'whole', horizon, paths, weights, distance)
                ensembles.append({'case': name, 'T': horizon, 'frame': 'whole',
                                  'Q': q.tolist(), 'initial': initial.tolist(),
                                  'paths': paths.tolist(), 'weights': weights.tolist(),
                                  'durations': [horizon/4]*4})
                if not stationary:
                    diagnostics.append({'case': name, 'T': horizon,
                                        'first_hit_other_by_T': 1-exp(-rate*horizon)})
        for mode, rates in (('noise', (0, .1, 10)), ('coupling', (.1,))):
            for rate in rates:
                # State index is 2*S+E; S does not change, E follows the native two-state law.
                eq = generator(rate, 1 if mode == 'coupling' else rate)
                q = np.kron(np.eye(2), eq)
                initial = np.asarray([.5, 0, .5, 0])
                paths, weights = markov_histories(initial, expm(q*horizon/4), 4)
                variants = ('coupled', 'disconnected') if mode == 'coupling' else ('noise',)
                for variant in variants:
                    name = variant if mode == 'coupling' else f'noise_{rate:g}'
                    states = [(s, s ^ e if variant == 'coupled' else e)
                              for s in (0, 1) for e in (0, 1)]
                    maps = {'source': [s for s, _ in states],
                            'destination': [d for _, d in states],
                            'whole': [2*s+d for s, d in states]}
                    for frame, mapping in maps.items():
                        observed, p = project_law(paths, weights, mapping)
                        distance = sampled_distance(observed, [horizon/4]*4)
                        append_profiles(rows, name, frame, horizon, observed, p, distance)
                        ensembles.append({'case': name, 'T': horizon, 'frame': frame,
                                          'Q_in_SE_coordinates': q.tolist(),
                                          'initial_in_SE_coordinates': initial.tolist(),
                                          'physical_SD_states': states, 'mapping': mapping,
                                          'paths': observed.tolist(), 'weights': p.tolist(),
                                          'durations': [horizon/4]*4})
                    if mode == 'coupling':
                        error = .1/1.1*(1-exp(-1.1*horizon))
                        entropy = -error*log2(error)-(1-error)*log2(1-error)
                        diagnostics.append({'case': name, 'T': horizon,
                                            'I_source_destination_bits_at_T':
                                                1-entropy if variant == 'coupled' else 0.0,
                                            'error_probability_at_T': error})
        print(f'Exact sampled-time panel finished T={horizon}', flush=True)

    # Full continuous paths with finite support: no sampled-time approximation here.
    finite_rows, finite_ensembles = [], []
    for horizon in (1., 2., 4.):
        pair = [([0., .25, .75], [0, 1, 3]), ([0., .25, .75], [0, 2, 3])]
        distance = jump_distances(pair, pair, horizon)
        for mode, epsilons in (('absolute', (.2, .4, .6)), ('fractional', (.25,))):
            for epsilon in epsilons:
                absolute = epsilon if mode == 'absolute' else epsilon*horizon
                results = cover_profile(distance, [.5, .5], absolute, ALPHAS)
                for alpha, result in zip(ALPHAS, results, strict=True):
                    finite_rows.append({'case': 'reconvergence', 'T': horizon,
                                        'epsilon_mode': mode, 'epsilon': epsilon,
                                        'epsilon_absolute': absolute, 'alpha': alpha, **result})
        finite_ensembles.append({'case': 'reconvergence', 'T': horizon,
                                 'paths': pair, 'weights': [.5, .5],
                                 'distance': distance.tolist()})
    for success in (.5, .9, .99, 1.):
        pair = [([0., 1/3, 2/3], [0, 1, 2]), ([0., 1/3, 2/3], [0, 1, 3])]
        weights = [success, 1-success]
        if success == 1:
            pair, weights = pair[:1], weights[:1]
        distance = jump_distances(pair, pair, 1)
        for epsilon in EPSILONS:
            for alpha, result in zip(ALPHAS, cover_profile(distance, weights, epsilon, ALPHAS),
                                     strict=True):
                finite_rows.append({'case': f'construction_{success:g}', 'T': 1.,
                                    'epsilon_mode': 'absolute', 'epsilon': epsilon,
                                    'epsilon_absolute': epsilon, 'alpha': alpha, **result})
        finite_ensembles.append({'case': f'construction_{success:g}', 'T': 1.,
                                 'paths': pair, 'weights': weights,
                                 'distance': distance.tolist()})
    idle = cover_profile([[0]], [1.], .25, [.9])[0]
    finite_rows.append({'case': 'deterministic_idle', 'T': 1., 'epsilon_mode': 'absolute',
                        'epsilon': .25, 'epsilon_absolute': .25, 'alpha': .9, **idle})
    save(output/'exact_profiles.json', rows)
    save(output/'exact_laws.json', ensembles)
    save(output/'physical_diagnostics.json', diagnostics)
    save(output/'finite_path_profiles.json', finite_rows)
    save(output/'finite_path_laws.json', finite_ensembles)
    return rows, finite_rows, diagnostics


def continuous_job(config):
    stationary, rate, seed, folder = config
    name = f"{'stationary' if stationary else 'fixed_zero'}_{rate:g}"
    horizon = 1.
    training = sample_telegraph(rate, horizon, 64, seed, stationary)
    evaluation = sample_telegraph(rate, horizon, 2048, seed+100000, stationary)
    merged = {}
    for times, states in training:
        key = (tuple(times), tuple(states))
        merged[key] = merged.get(key, 0)+1
    centers = list(merged)
    weights = np.asarray(list(merged.values()))/64
    distance = jump_distances(centers, centers, horizon)
    validation = jump_distances(evaluation, centers, horizon)
    rows = []
    for epsilon in (.25, .5):
        fit = cover_profile(distance, weights, epsilon, [.9])[0]
        covered = (validation[:, fit['centers']] <= epsilon+1e-12).any(axis=1)
        successes = int(covered.sum())
        rows.append({'case': name, 'T': 1., 'epsilon_absolute': epsilon, 'alpha': .9,
                     'unique_training_paths': len(centers), 'training_count': 64,
                     'evaluation_count': 2048, 'training_seed': seed,
                     'evaluation_seed': seed+100000, **fit,
                     'evaluation_mass': successes/2048,
                     'evaluation_95_interval': wilson(successes, 2048)})
    folder = Path(folder)
    save(folder/f'{name}_paths.json', {'case': name, 'training': training,
                                     'centers': centers, 'weights': weights.tolist(),
                                     'evaluation': evaluation, 'results': rows})
    np.savez_compressed(folder/f'{name}_distances.npz', training=distance, evaluation=validation)
    return rows


def build_report(rows, finite, diagnostics, sampled, seconds, output):
    def pick(case, frame='whole', T=1., epsilon=.25, alpha=.9):
        return next(r for r in rows if r['case'] == case and r['frame'] == frame
                    and r['T'] == T and r['epsilon_fraction'] == epsilon and r['alpha'] == alpha)

    lines = ['# Weighted trajectory-covering probe v0', '',
             '2026-10-05. Exploratory measurement run on mathematical controls. No new chemistry,',
             'no selected lushness invariant and no required winner.', '',
             '## Main finite-resolution results', '',
             'Four observations at 0,T/4,T/2,3T/4, held for T/4 each. The table uses T=1,',
             'fractional mismatch tolerance .25 and probability depth .90. These are exact',
             'minimum covers of the finite observed law (floating-point probabilities).', '',
             '| Case | Frame | Minimum representatives |', '|---|---|---:|']
    for case in ('stationary_0.05', 'stationary_1', 'stationary_10',
                 'accelerated_0.1', 'accelerated_1', 'accelerated_10',
                 'noise_0', 'noise_0.1', 'noise_10', 'coupled', 'disconnected'):
        for frame in (('whole', 'destination') if case in ('coupled', 'disconnected')
                      else ('whole',)):
            row = pick(case, frame)
            lines.append(f"| {case} | {frame} | {row['upper']} |")
    lines += ['', '## Reversible kinetic access', '',
              'Probability of first visiting the other state by the deadline, starting at zero.',
              'This is a physical access diagnostic, not a new score or an ethical target.', '',
              '| Rate | T | First-hit probability | Cover at fractional .25, alpha .90 |',
              '|---:|---:|---:|---:|']
    for d in diagnostics:
        if d['case'].startswith('accelerated'):
            row = pick(d['case'], T=d['T'])
            lines.append(f"| {d['case'].split('_')[1]} | {d['T']:g} | "
                         f"{d['first_hit_other_by_T']:.6f} | {row['upper']} |")
    lines += ['', '## Coupling contrast', '',
              'Coupled D=S xor E versus disconnected D=E, with S static/fair and the same',
              'error-clock law. A bijection of full state symbols makes whole-state distances',
              'and probabilities identical. It does not make the physical wirings equivalent.',
              'The event-count law also matches. Local destination frames can break the tie.', '',
              '| Case | I(S;D) at T=1, bits |', '|---|---:|']
    for d in diagnostics:
        if d['case'] in ('coupled', 'disconnected') and d['T'] == 1:
            lines.append(f"| {d['case']} | {d['I_source_destination_bits_at_T']:.6f} |")
    left = {(r['T'], r['epsilon_fraction'], r['alpha']): r['upper'] for r in rows
            if r['case'] == 'coupled' and r['frame'] == 'whole'}
    right = {(r['T'], r['epsilon_fraction'], r['alpha']): r['upper'] for r in rows
             if r['case'] == 'disconnected' and r['frame'] == 'whole'}
    lines += ['', f'Whole-frame ties: {sum(left[k] == right[k] for k in left)}/{len(left)}.', '',
              '## Reconvergence and concentration', '',
              '| Case | T | Tolerance type | Tolerance | Alpha | Cover |',
              '|---|---:|---|---:|---:|---:|']
    for r in finite:
        if r['alpha'] == .9 and ((r['case'] == 'reconvergence' and
                                 (r['epsilon_mode'] == 'fractional' or r['epsilon'] == .4))
                                or r['case'].startswith('construction') and r['epsilon'] == .25
                                or r['case'] == 'deterministic_idle'):
            lines.append(f"| {r['case']} | {r['T']:g} | {r['epsilon_mode']} | "
                         f"{r['epsilon']:g} | {r['alpha']:g} | {r['upper']} |")
    lines += ['', 'Reconvergent histories differ for exactly .5 physical time units. Fractional',
              'tolerance dilutes that fixed prefix as T increases; fixed absolute tolerance does',
              'not. Construction succeeds more reliably as its law concentrates, so required',
              'representatives can decrease. A deterministic construction and idle both need one.',
              'These scheduled finite-support paths are exact mathematical controls, not',
              'thermodynamically matched chemical preparations.', '',
              '## Continuous jump-time check', '',
              '64 training histories and 2048 independent evaluation histories per row family.',
              'Distances use the exact jump times of supplied histories. Centers are restricted',
              'to the training sample; fitted alpha is .90. Solver bounds concern the empirical',
              'optimization only. The interval measures held-out coverage of that fixed cover,',
              'not uncertainty in the unknown optimal population covering number.', '',
              '| Case | Absolute tolerance | Empirical N bounds | Training coverage | Held-out coverage (95% interval) |',
              '|---|---:|---:|---:|---|']
    for r in sampled:
        lo, hi = r['evaluation_95_interval']
        lines.append(f"| {r['case']} | {r['epsilon_absolute']:g} | {r['lower']}–{r['upper']} | "
                     f"{r['mass']:.3f} | {r['evaluation_mass']:.3f} ({lo:.3f}–{hi:.3f}) |")
    lines += ['', '## Assessment', '',
              '- The extent avoids the one-time occupancy collapse and detects temporal laws.',
              '- Rapid independent noise can increase the cover. It remains in the physical law.',
              '- Greater reliability need not increase the cover; it can lower diversity.',
              '- Whole-state equality distance can tie physically different couplings. The local',
              '  frame profile retains some distinctions that the whole-frame number loses.',
              '- Common-suffix dilution is a scale effect, not deletion from the full history.',
              '- Finite empirical optimization does not establish coverage of rare population',
              '  histories. Small samples may substantially underestimate the required cover.',
              '- These results support trajectory covering as a temporal-diversity extent.',
              '  They do not establish it as lushness or identify harm with fewer covers.', '',
              '## Reproduction and scope', '',
              '`python -m omega_v2.validation.path_covering_v0 --workers 6`', '',
              f'Runtime: {seconds:.2f} seconds. Finite coordinates: {len(rows)}; complete',
              f'finite-support coordinates: {len(finite)}; continuous empirical fits: {len(sampled)}.',
              'Native laws, frame maps, all finite probabilities, witnesses, simulation seeds,',
              'training/evaluation paths and distance matrices are saved in [raw evidence](path_covering_v0/).',
              'The continuous-time support can require infinite covers; no finite-dimension',
              'or whole-support claim follows from this finite-resolution study.', '',
              '[Protocol](path_covering_protocol_v0.md).',
              '[Candidate assessment](sol_path_covering_assessment_2026-10-05.md).', '']
    report = output.parent/'path_covering_report_v0.md'
    report.write_text('\n'.join(lines), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=6)
    args = parser.parse_args()
    start = perf_counter()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows, finite, diagnostics = exact_panel(OUTPUT)
    jobs = [(stationary, rate, 501_005+i, str(OUTPUT))
            for i, (stationary, rate) in enumerate((s, r) for s in (True, False)
                                                   for r in (.05, 1, 10))]
    sampled = []
    with ProcessPoolExecutor(max_workers=min(args.workers, 10, len(jobs))) as pool:
        for result in pool.map(continuous_job, jobs):
            sampled.extend(result)
            print(f"Continuous check finished {result[0]['case']}", flush=True)
    save(OUTPUT/'continuous_profiles.json', sampled)
    seconds = perf_counter()-start
    files = ('omega_v2/finite/path_covering.py', 'omega_v2/validation/path_covering_v0.py',
             'docs/research_notes/omega_v2/path_covering_protocol_v0.md',
             'tests/test_path_covering.py')
    save(OUTPUT/'manifest.json', {'runtime_seconds': seconds, 'python': platform.python_version(),
                                  'numpy': np.__version__, 'scipy': scipy.__version__,
                                  'workers': min(args.workers, 10, len(jobs)),
                                  'source_hashes': {p: sha256((ROOT/p).read_bytes()).hexdigest()
                                                    for p in files}})
    report = build_report(rows, finite, diagnostics, sampled, seconds, OUTPUT)
    print(f'Report: {report}; seconds={seconds:.2f}', flush=True)


if __name__ == '__main__':
    main()
