"""Frozen single-law scientific execution, or non-ranking integration profile."""
import sys
from pathlib import Path
from time import perf_counter


def execute(out, manifest):
    from omega_v2.testbed.analysis.generativity_experiment import run_experiment
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.robust_generativity import GenerativityParameters, build_world
    from omega_v2.testbed.workflow.manifest import atomic_json
    config = manifest['config']; case = config['case']; protocol = config['protocol']
    if config['mode'] == 'science' and protocol['status'] != 'frozen_before_scientific_ranking':
        raise RuntimeError('Scientific freeze missing')
    started = perf_counter()
    world = build_world(GenerativityParameters(**case['parameters']), case['mechanism'])
    c = compile_world(world)
    result = run_experiment(c, protocol, pulse=case['pulse'])
    imports = {name: str(m.__file__) for name, m in sys.modules.items()
               if name.startswith('omega_v2') and getattr(m, '__file__', None)}
    source = Path(__file__).resolve().parents[1]
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen scientific import')
    if config['mode'] == 'integration':
        residuals = {k: {'poisson': v['poisson_residual'], 'harmonic': v['harmonic_rate_residual']}
                     for k, v in result['sampled'].items()}
        result = {'mode': 'integration_only', 'states': result['states'],
                  'rankings_inspected': False, 'residuals': residuals}
    else:
        result.update(case=case, mode='science')
    result.update(input_hash=manifest['input_hash'], seconds=perf_counter()-started)
    atomic_json(out/'RESULTS.json', result)
