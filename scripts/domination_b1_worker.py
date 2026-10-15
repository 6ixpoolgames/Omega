"""Capped worker; imports occur only after process-tree caps are installed."""
import sys
if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Process caps required')
import json
from pathlib import Path
from time import perf_counter


def main(out):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.workflow.manifest import verify_bundle, atomic_json
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.domination_friction import FrictionParameters, FrictionPolicy, build_world, matched_roots
    from omega_v2.testbed.analysis.expanded_friction_profile import profile
    config = verify_bundle(out)['config']
    start = perf_counter()
    progress = lambda stage: print(json.dumps({'stage': stage, 'seconds': perf_counter()-start}), flush=True)
    parameters = FrictionParameters(**config['parameters'])
    if 'transfer_policy' in config:
        from omega_v2.testbed.resource_transfer import TransferPolicy, build_world as transfer_world
        world = transfer_world(parameters, TransferPolicy(**config['transfer_policy']), max_states=32000)
    else:
        world = build_world(parameters, FrictionPolicy(**config['policy']), max_states=32000)
    compiled = compile_world(world, max_states=32000)
    progress('compiled')
    imports = {k: str(Path(v.__file__).resolve()) for k, v in sys.modules.items()
               if k.startswith('omega_v2') and getattr(v, '__file__', None)}
    if any(not Path(x).is_relative_to(source) for x in imports.values()):
        raise RuntimeError('Source escaped immutable snapshot')
    roots = {'device_present': matched_roots(parameters)['device_present']}
    cache=config.get('entropy_cache')
    if cache is not None:
        repository=out.parents[4]
        # This is a declared query-data cache, not executable source.
        local_root=repository/'results/local_runs/lushness_testbed'
        allowed=out.parent
        if not allowed.resolve().is_relative_to(local_root.resolve()):
            raise RuntimeError('Run root escaped declared local testbed')
        if not Path(cache).resolve().is_relative_to(allowed.resolve()):
            raise RuntimeError('Query cache must stay inside the declared local run root')
    if len(world.states) <= 4000 and 'transfer_policy' not in config:
        from omega_v2.testbed.analysis.friction_profile import profile as dense_profile
        from omega_v2.testbed.analysis.friction_attribution import activity_rows, integrate
        from omega_v2.testbed.analysis.class_queries import occupation_distribution
        import numpy as np
        progress('dense two-observation subject bounds')
        result = dense_profile(compiled, roots, config['cadences'], config['horizons'], subject_depth=2)
        rows = activity_rows(world)
        start_distribution = np.zeros(len(world.states))
        start_distribution[compiled['index'][roots['device_present']]] = 1.
        for horizon in config['horizons']:
            _, occupation = occupation_distribution(compiled['Q'], start_distribution, horizon)
            result['physical']['device_present'][str(horizon)]['D_native_attribution'] = integrate(rows, occupation)
    else:
        result = profile(world, compiled, roots, config['cadences'], config['horizons'],
                         config.get('block_rows', 32), progress,
                         entropy_backend=config.get('entropy_backend', 'exponential'),
                         entropy_threads=config.get('entropy_threads', 1),entropy_cache=cache)
    if 'transfer_policy' in config:
        from omega_v2.testbed.analysis.streamed_history import StreamedQueries
        import numpy as np
        solver = StreamedQueries(compiled['Q'])
        result['stationary_ledger'] = {k: float(solver.pi @ v) for k, v in compiled['flows'].items()}
        result['stationary_observables'] = {k: float(solver.pi @ v) for k, v in compiled['observables'].items()}
        result['owned_energy_validation'] = {}
        for subject in ('D', 'S'):
            initial = world.observables[subject+'.owned_energy'](roots['device_present'])
            maximum = 0.
            for row in result['physical']['device_present'].values():
                owned_sum = sum(v for k, v in row['ledger'].items() if k.startswith(subject+'_energy_by_family.'))
                maximum = max(maximum, abs(row['deadline'][subject+'.owned_energy']-initial-owned_sum))
            result['owned_energy_validation'][subject] = maximum
            if maximum > 1e-6:
                raise ArithmeticError('Subject resource ledger did not close')
    imports = {k: str(Path(v.__file__).resolve()) for k, v in sys.modules.items()
               if k.startswith('omega_v2') and getattr(v, '__file__', None)}
    if any(not Path(x).is_relative_to(source) for x in imports.values()):
        raise RuntimeError('Late analysis import escaped immutable snapshot')
    result.update(case=config['id'], total_seconds=perf_counter()-start,
                  imported_source_paths=imports, imports_from_snapshot=True)
    atomic_json(out/'RESULTS.json', result)
    progress('complete')

if __name__ == '__main__':
    main(Path(sys.argv[1]))
