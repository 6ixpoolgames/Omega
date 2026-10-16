"""Check admissible centers omitted by the sampled-center approximation, without refitting."""

import json
from math import exp
from pathlib import Path

from omega_v2.finite.path_covering import jump_distances, sample_telegraph, wilson


def main():
    root = Path(__file__).resolve().parents[2]
    folder = root/'docs/research_notes/omega_v2/path_covering_v0/center_check'
    folder.mkdir(parents=True, exist_ok=True)
    centers = [([0.], [0]), ([0.], [1]), ([0., .5], [0, 1])]
    results = []
    for i, rate in enumerate((.05, 1., 10.)):
        seed = 901_005+i
        paths = sample_telegraph(rate, 1., 4096, seed, stationary=True)
        distance = jump_distances(paths, centers, 1.)
        pair = (distance[:, :2] <= .5+1e-12).any(axis=1)
        balanced = distance[:, 2] <= .5+1e-12
        assert pair.all()  # d(path,constant0)+d(path,constant1)=1, pathwise.
        successes = int(balanced.sum())
        target = .5*(1+exp(-rate))
        results.append({'rate': rate, 'seed': seed, 'count': len(paths),
                        'constant_pair_mass': float(pair.mean()),
                        'balanced_center_mass': float(balanced.mean()),
                        'balanced_center_95_interval': wilson(successes, len(paths)),
                        'balanced_center_exact_mass': target,
                        'exact_N_at_epsilon_half_alpha_90': 1 if target >= .9 else 2})
        (folder/f'stationary_{rate:g}_paths.json').write_text(
            json.dumps({'paths': paths, 'centers': centers, 'result': results[-1]}, indent=2)+'\n',
            encoding='utf-8')
    (folder/'results.json').write_text(json.dumps(results, indent=2)+'\n', encoding='utf-8')
    lines = ['# Continuous trajectory-covering center check', '',
             'Supplement to path_covering_report_v0.md. The metric and native laws are unchanged.',
             'The first run optimized centers drawn from64 training histories. This check',
             'uses three specified admissible centers and fresh samples; no center selection',
             'is based on the evaluation samples.', '',
             'At T=1 and absolute epsilon=.5, constant-zero and constant-one histories cover',
             'every binary history: their distances to a path sum to one. They are admissible',
             'under every positive-rate stationary binary process. Thus true N is at most two,',
             'even where a particular fitted two-center empirical cover generalizes poorly.', '',
             'One admissible path switches once at .5. Its covering probability is exactly',
             '(.5)*(1+exp(-lambda)). Complement symmetry makes distances symmetric about .5.',
             'The only positive atom at .5 is the no-jump mass exp(-lambda); jump-time densities',
             'make the remaining distance law nonatomic. Any balanced finite-jump center has',
             'this same mass, and unbalanced centers have mass .5. Thus this is also maximal',
             'single-center mass among finite-jump centers, and gives the exact N below.', '',
             '| Rate | Balanced-center exact mass | Fresh observed mass (95% interval) | Exact N at alpha .90 |',
             '|---:|---:|---|---:|']
    for row in results:
        lo, hi = row['balanced_center_95_interval']
        lines.append(f"| {row['rate']:g} | {row['balanced_center_exact_mass']:.6f} | "
                     f"{row['balanced_center_mass']:.6f} ({lo:.6f}–{hi:.6f}) | "
                     f"{row['exact_N_at_epsilon_half_alpha_90']} |")
    lines += ['', 'The slow-process empirical optimum was two because random sampling missed',
              'a center that approximates both constant histories. Its true optimum here is',
              'one. That is a center-approximation error, not a change to the physical field.',
              'At tolerance .25 the initial fast-process undercoverage remains unresolved;',
              'none of its fitted counts is promoted to a population covering number.', '',
              'The exact half-horizon result is a calibration of the estimator, not a new',
              'lushness ordering. Probability-depth and distance-scale coordinates matter.', '',
              'Reproduce: `python -m omega_v2.validation.path_covering_center_check_v0`.',
              'All fresh paths and the center definitions are in path_covering_v0/center_check/.', '']
    report = folder.parent.parent/'path_covering_center_check_v0.md'
    report.write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
