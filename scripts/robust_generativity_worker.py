"""Capped validation/profiling only; no preparation or mechanism winner search."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Caps must be installed before imports')

import json
from dataclasses import replace
from pathlib import Path
from time import perf_counter


def main(out):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle
    manifest = verify_bundle(out)
    config = manifest['config']
    if config['mode'] == 'tests':
        import pytest
        code = pytest.main([str(source/'tests/test_robust_generativity.py'),
                            str(source/'tests/test_generativity_experiment.py'), '-q', '-p', 'no:cacheprovider',
                            '--rootdir='+str(source), '--confcutdir='+str(source)])
        if code:
            raise SystemExit(code)
        atomic_json(out/'RESULTS.json', {'tests_passed': True, 'input_hash': manifest['input_hash']})
        return
    if config['mode'] in ('integration', 'science'):
        from robust_generativity_science import execute
        return execute(out, manifest)
    if config['mode'] != 'engineering':
        raise RuntimeError('Scientific execution is not implemented in this runner')
    import numpy as np

    from omega_v2.testbed.analysis.class_queries import ClassQueries, occupation_distribution
    from omega_v2.testbed.analysis.generativity_depth import (
        compile_monitor,
        detected_chain_profile,
        initial_distribution,
    )
    from omega_v2.testbed.analysis.generativity_robustness import (
        closure_targets,
        depth_profile,
        endpoint,
        pulse_readout,
    )
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.robust_generativity import (
        GenerativityParameters,
        build_world,
        matched_roots,
        physical_readouts,
    )
    results = []
    for case in config['cases']:
        start = perf_counter()
        p = GenerativityParameters(**case['parameters'])
        mechanism = case.get('mechanism', 'full')
        world = build_world(p, mechanism)
        n = len(world.states)
        row = {'parameters': vars(p), 'mechanism': mechanism, 'states': n, 'kernel_bytes': 8*n*n}
        if 8*n*n > config['max_kernel_bytes']:
            row['status'] = 'kernel_budget_exceeded_before_ranking'
            results.append(row); print(json.dumps(row), flush=True)
            continue
        c = compile_world(world)
        row['generator_seconds'] = perf_counter()-start
        targets = closure_targets(c)
        row['closure_counts'] = {name: int(v['mask'].sum()) for name, v in targets.items()}
        mu = matched_roots(c)['seed']
        # Independent dark equilibrium including every populated sink sector.
        # Disable only the external source and damage boundary, retain D space.
        dark_world = replace(world, modules=tuple(replace(m, events=lambda s: iter(())) if m.id == 'damage' else m
                                                  for m in world.modules))
        dark_base = build_world(replace(p, supply_rate=0.), mechanism)
        dark_world = replace(dark_world, modules=tuple(
            next(k for k in dark_base.modules if k.id == 'resource') if m.id == 'resource' else m
            for m in dark_world.modules))
        dark = compile_world(dark_world)
        weights = np.array([world.degeneracy(s)*np.exp(-p.beta*world.energy(s)) for s in world.states])
        # All fixed-D sectors weighted positively; detailed balance must hold on each edge.
        weights /= weights.sum()
        flux = dark['Q'].multiply(weights[:, None]); difference = flux-flux.T
        row['dark_balance_residual'] = float(max(abs(difference.data), default=0.))
        if row['dark_balance_residual'] > 1e-12:
            raise ArithmeticError('Dark balance failed')
        del dark, dark_world, dark_base, flux, difference
        before = perf_counter()
        queries = ClassQueries(c['Q'])
        sampled = queries.sampled(config['cadence'], config['max_kernel_bytes'])
        # Finite vector is validated by one-step identity. Values are deliberately
        # not compared across roots/arms or retained as scientific results.
        one_step = queries.finite(sampled, config['cadence'])
        error = float(max(abs(one_step-sampled['g'])))
        if error > 1e-7:
            raise ArithmeticError('One-step exact entropy identity failed')
        row.update(kernel_and_class_seconds=perf_counter()-before,
                   recurrent_classes=len(queries.classes), transient_states=len(queries.transient),
                   one_step_identity_residual=error, poisson_residual=sampled['poisson_residual'],
                   harmonic_rate_residual=sampled['harmonic_rate_residual'],
                   kernel_residuals=sampled['kernel_diagnostics'], gmres_iterations=sampled['iterations'])
        row['finite_profile_seconds'] = {}
        for horizon in config.get('profile_horizons', []):
            before = perf_counter()
            finite = queries.finite(sampled, horizon)
            if min(finite) < -1e-7 or not np.all(np.isfinite(finite)):
                raise ArithmeticError('Finite-history vector invalid')
            row['finite_profile_seconds'][str(horizon)] = perf_counter()-before
            del finite
        del sampled, queries, one_step
        final, occ = occupation_distribution(c['Q'], mu, config['validation_horizon'])
        ledger = physical_readouts(c, final, occ, mu)
        row['bank_ledger_residual'] = ledger['bank_balance_residual']
        row['energy_ledger_residual'] = ledger['energy_balance_residual']
        before = perf_counter()
        for mode in ('initial_seed', 'any_start'):
            monitor = compile_monitor(c, mode)
            initial = initial_distribution(c, monitor, mu)
            lifted_end = endpoint(monitor['Q'], initial, config['validation_horizon'])
            projection_error = float(max(abs(lifted_end @ monitor['projection']-final)))
            if projection_error > 1e-9:
                raise ArithmeticError('Monitored process changes physical propagation')
            row[mode] = {'query_states': len(initial), 'query_edges': monitor['Q'].nnz,
                         'generator_projection_residual': monitor['projection_residual'],
                         'endpoint_projection_residual': projection_error}
            if mode == 'initial_seed':
                joint = depth_profile(c, monitor, initial, startup=1.,
                                      horizon=config['validation_horizon'], pulse=True)
                if not all(0 <= v <= 1+1e-10 for v in joint.values()):
                    raise ArithmeticError('Joint probability invalid')
                if config.get('full_query_profile'):
                    before_joint = perf_counter()
                    # Execute the intended costly query, retaining only numerical
                    # feasibility/timing. No C/R/L thresholds or comparisons.
                    checked = depth_profile(c, monitor, initial, startup=64., horizon=256., pulse=True)
                    if not all(0 <= v <= 1+1e-10 for v in checked.values()):
                        raise ArithmeticError('Full-window joint probability invalid')
                    row['joint_query_seconds'] = perf_counter()-before_joint
            else:
                readout = detected_chain_profile(monitor, initial, config['validation_horizon'])
                if readout['detected_chain_rate'] < 0:
                    raise ArithmeticError('Negative detector completion rate')
            del monitor, initial, lifted_end
        row['monitor_seconds'] = perf_counter()-before
        recovery = pulse_readout(c, mu, pulse_time=1., delays=(1.,))
        if recovery['delays']['1.0']['pre_function_and_endpoint_recovery'] > recovery['pre_function_probability']+1e-10:
            raise ArithmeticError('Recovery conditioned away failed startup')
        row.update(status='complete', seconds=perf_counter()-start)
        results.append(row); print(json.dumps(row), flush=True)
        del c, world
    imports = {name: str(m.__file__) for name, m in sys.modules.items()
               if name.startswith('omega_v2') and getattr(m, '__file__', None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen import')
    atomic_json(out/'RESULTS.json', {'input_hash': manifest['input_hash'], 'mode': 'engineering',
                                   'rows': results, 'rankings_inspected': False})


if __name__ == '__main__':
    main(Path(sys.argv[1]))
