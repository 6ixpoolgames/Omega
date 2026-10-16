"""Engineering consistency only. No arm comparisons, kills or policy searches."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Caps must be installed before imports')

import json
from pathlib import Path
from time import perf_counter


def main(out):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest = verify_bundle(out)
    import numpy as np

    from omega_v2.testbed.analysis.blocked_entropy import sampled_kernel
    from omega_v2.testbed.analysis.finite_classes import finite_history_bits
    from omega_v2.testbed.analysis.observed_history import exact_prefix_entropy, history_bounds
    from omega_v2.testbed.analysis.signal_readouts import coordinate_shares, physical_readouts
    from omega_v2.testbed.aversive_signals import SignalParameters, build_world, matched_parameters
    from omega_v2.testbed.compiler import compile_world

    draft = json.loads((source/'docs/research_notes/lushness_testbed/aversive_signals/'
                       'PROTOCOL_DRAFT.json').read_text(encoding='utf-8'))
    if draft['status'] != 'engineering_only_unfrozen':
        raise ValueError('Smoke must use an engineering draft')
    params = SignalParameters(**draft['engineering_parameters'])
    rows = []
    for arm in draft['arms']:
        started = perf_counter()
        config = (matched_parameters(params, **draft['rare_hazard_parameters'])
                  if arm in ('D', 'E_prime', 'N_prime') else params)
        compiled = compile_world(build_world(arm, config))
        reference_arm = 'B' if arm in ('A', 'B', 'C') else 'N'
        reference = compile_world(build_world(reference_arm, config))
        root = compiled['index'][(config.units(config.energy_cap), 0, 0, 1, 1)]
        q = compiled['Q']
        kernel, _, residuals = sampled_kernel(q, draft['smoke_cadence'])
        labels = [tuple(x[j] for j in (0, 1, 3, 4)) for x in compiled['states']]
        short = history_bounds(kernel, labels, root, 2)
        exact = exact_prefix_entropy(kernel, labels, root, 2, max_prefixes=50000)
        if not short['lower_bits']-1e-9 <= exact <= short['upper_bits']+1e-9:
            raise ArithmeticError('Merged-signal prefix escaped conditioning bounds')
        bounds = history_bounds(kernel, labels, root, 16)
        fine = float(finite_history_bits(kernel, 16)[root])
        if bounds['lower_bits'] > fine+1e-9:
            raise ArithmeticError('Observed entropy exceeds full history')
        shares = coordinate_shares(kernel, compiled['states'], root, 16)
        share_residual = abs(sum(shares['bits'])-fine)
        energy_residual = float(np.max(abs(q @ compiled['energy']
                             -compiled['flows']['drive_work']+compiled['flows']['bath_heat'])))
        if share_residual > 1e-9 or energy_residual > 1e-9:
            raise ArithmeticError('Chain rule or energy closure failed')
        readouts = physical_readouts(compiled, reference, root, 4.)
        rows.append({'arm': arm, 'states': len(compiled['states']),
                     'seconds': perf_counter()-started,
                     'generator_mass_residual': float(np.max(abs(q.sum(axis=1)))),
                     'energy_residual': energy_residual, 'kernel_residuals': residuals,
                     'chain_rule_residual': share_residual,
                     'merged_short_prefix_validation': 'passed against exact enumeration',
                     'merged_bounds_valid': True,
                     'signal_readouts_finite': all(np.isfinite(readouts[name])
                         for name in ('live_occupancy_time', 'signal_occupancy_time',
                                      'survival_at_deadline', 'obstructed_signal_time')),
                     'qualification': readouts['qualification'],
                     'scientific_scores': 'computed for consistency only; comparisons withheld'})
    imports = {name: str(module.__file__) for name, module in sys.modules.items()
               if name.startswith('omega_v2') and getattr(module, '__file__', None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen Omega import')
    result = {'status': 'engineering_smoke_complete', 'input_hash': manifest['input_hash'],
              'rows': rows, 'imports': imports, 'scientific_run': False,
              'kill_tests_scored': False}
    (out/'RESULTS.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
