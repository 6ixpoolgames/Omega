"""Execute one recorded configuration under installed process-tree caps."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Process caps must be installed before imports')

import json
from pathlib import Path
from time import perf_counter


def main(out):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.analysis.friction_profile import profile
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.domination_friction import (
        FrictionParameters,
        FrictionPolicy,
        build_world,
        matched_roots,
    )
    from omega_v2.testbed.workflow.manifest import atomic_json, verify_bundle
    imported = {name: str(Path(module.__file__).resolve()) for name, module in sys.modules.items()
                if name.startswith('omega_v2') and getattr(module, '__file__', None)}
    if any(not Path(path).is_relative_to(source) for path in imported.values()):
        raise RuntimeError('Analysis imported source outside the recorded run bundle')
    manifest = verify_bundle(out)
    config = manifest['config']
    start = perf_counter()
    world = build_world(FrictionParameters(**config['parameters']),
                        FrictionPolicy(**{'steering_scope':'native_events',**config['policy']}))
    compiled = compile_world(world)
    build_time = perf_counter()-start
    roots = {name: matched_roots()[name] for name in config['roots']}
    result = profile(compiled, roots, config['cadences'], config['horizons'],
                     config['max_kernel_bytes'], config.get('subject_depth', 1))
    result.update(input_hash=manifest['input_hash'], mode=config['mode'],
                  case=config['id'], build_seconds=build_time,
                  analysis_seconds=perf_counter()-start-build_time,
                  imported_source_paths=imported, imports_from_snapshot=True)
    atomic_json(out/'RESULTS.json', result)
    print(json.dumps({'case': config['id'], 'states': len(world.states),
                      'build_seconds': build_time,
                      'total_seconds': perf_counter()-start}), flush=True)


if __name__ == '__main__':
    main(Path(sys.argv[1]))
