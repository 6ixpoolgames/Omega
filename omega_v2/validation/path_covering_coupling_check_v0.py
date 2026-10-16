"""Repeat the physical coupling contrast with the same initial joint preparation."""

from math import exp, log2
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.linalg import expm

from omega_v2.finite.path_covering import markov_histories, project_law, sampled_distance
from omega_v2.validation.path_covering_v0 import append_profiles, generator, save


def main():
    start = perf_counter()
    root = Path(__file__).resolve().parents[2]
    folder = root/'docs/research_notes/omega_v2/path_covering_v0/coupling_check'
    folder.mkdir(parents=True, exist_ok=True)
    q = np.kron(np.eye(2), generator(.1, 1.))
    initial = np.full(4, .25)
    rows, laws, diagnostics = [], [], []
    for horizon in (.5, 1., 4.):
        paths, weights = markov_histories(initial, expm(q*horizon/4), 4)
        for name in ('coupled', 'disconnected'):
            states = [(s, s ^ e if name == 'coupled' else e)
                      for s in (0, 1) for e in (0, 1)]
            physical = [2*s+d for s, d in states]
            inverse = np.argsort(physical)
            maps = {'source': [s for s, _ in states],
                    'destination': [d for _, d in states], 'whole': physical}
            for frame, mapping in maps.items():
                observed, p = project_law(paths, weights, mapping)
                distance = sampled_distance(observed, [horizon/4]*4)
                append_profiles(rows, name, frame, horizon, observed, p, distance)
                laws.append({'case': name, 'T': horizon, 'frame': frame,
                             'physical_states': [(0, 0), (0, 1), (1, 0), (1, 1)],
                             'physical_Q': q[np.ix_(inverse, inverse)].tolist(),
                             'physical_initial': initial.tolist(), 'mapping': mapping,
                             'paths': observed.tolist(), 'weights': p.tolist()})
            error = .1/1.1+(.5-.1/1.1)*exp(-1.1*horizon)
            h = -error*log2(error)-(1-error)*log2(1-error)
            diagnostics.append({'case': name, 'T': horizon,
                                'I_source_destination_at_T': 1-h if name == 'coupled' else 0.,
                                'conditional_response_TV': 1-2*error if name == 'coupled' else 0.})
    save(folder/'profiles.json', rows)
    save(folder/'laws.json', laws)
    save(folder/'diagnostics.json', diagnostics)
    lines = ['# Coupling contrast with identical initial preparation', '',
             'Follow-up to path_covering_report_v0.md. Metric, rates and frames are unchanged.',
             'This time S and D are initially independent fair bits in both physical apparatuses.',
             'Thus initial joint distribution, component entropies and correlations match.',
             'No initial source record has already been installed at the destination.', '',
             'The source is static. In the coupled generator D moves toward S at rate1 and',
             'away from S at rate.1; in the disconnected generator D moves toward0 at rate1',
             'and away from0 at rate.1. Both mechanisms are reversible conditional on S.',
             'The full state permutation (S,D)->(S,D xor S) preserves path probabilities and',
             'whole-state mismatch, and preserves the uniform initial law. It does not preserve',
             'the physical destination frame. The event-count law is consequently identical.', '',
             '| Frame | Equal cover coordinates | Total coordinates |', '|---|---:|---:|']
    ties = {}
    for frame in ('source', 'destination', 'whole'):
        left = {(r['T'], r['epsilon_fraction'], r['alpha']): r for r in rows
                if r['case'] == 'coupled' and r['frame'] == frame}
        right = {(r['T'], r['epsilon_fraction'], r['alpha']): r for r in rows
                 if r['case'] == 'disconnected' and r['frame'] == frame}
        assert all(r['optimal'] for r in (*left.values(), *right.values()))
        same = sum(left[k]['upper'] == right[k]['upper'] for k in left)
        ties[frame] = [same, len(left)]
        lines.append(f'| {frame} | {same} | {len(left)} |')
    lines += ['', '| T | I(S;D), coupled | I(S;D), disconnected |', '|---:|---:|---:|']
    for row in diagnostics:
        if row['case'] == 'coupled':
            lines.append(f"| {row['T']:g} | {row['I_source_destination_at_T']:.6f} | 0 |")
    lines += ['', 'The whole-frame tie persists with matched initial preparation. Local frames',
              'retain some distinctions lost by whole-state mismatch. The metric is invariant',
              'under a larger class of state-symbol bijections than the physical apparatus is.',
              'This is a specific loss of structural information, not a demand that every',
              'physically different apparatus have a different volume.', '',
              'All coordinates are certified optima for the four-observation projected law,',
              'using exhaustive covers or MILP. Full continuous-time covering is not inferred.',
              f'Runtime: {perf_counter()-start:.2f} seconds.', '',
              'Reproduce: `python -m omega_v2.validation.path_covering_coupling_check_v0`.', '']
    report = folder.parent.parent/'path_covering_coupling_check_v0.md'
    report.write_text('\n'.join(lines), encoding='utf-8')
    print({'ties': ties, 'diagnostics': diagnostics, 'seconds': perf_counter()-start})


if __name__ == '__main__':
    main()
