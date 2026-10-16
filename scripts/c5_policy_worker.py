"""Capped immutable worker for one physical allocation controller."""
import sys
if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Process caps required')
import json
import hashlib
from pathlib import Path
from time import perf_counter


def main(out):
    source = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(source))
    from omega_v2.testbed.workflow.manifest import verify_bundle, atomic_json
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.reactive_allocation import AllocationParameters, AllocationPolicy, build_world, root
    from omega_v2.testbed.analysis.policy_search_profile import profile
    config = verify_bundle(out)['config']
    started = perf_counter()
    progress = lambda stage: print(json.dumps({'stage': stage, 'seconds': perf_counter()-started}), flush=True)
    p, policy = AllocationParameters(**config['parameters']), AllocationPolicy(**config['controller'])
    world = build_world(p, policy)
    compiled = compile_world(world, max_states=12000)
    q = compiled['Q']
    kernel_hash = hashlib.sha256(q.indptr.tobytes()+q.indices.tobytes()+q.data.tobytes()).hexdigest()
    progress('compiled')
    result = profile(world, compiled, root(world, p), config['cadences'], config['horizons'],
                     config.get('subject_depth', 2), progress)
    imports = {k: str(Path(v.__file__).resolve()) for k, v in sys.modules.items()
               if k.startswith('omega_v2') and getattr(v, '__file__', None)}
    if any(not Path(x).is_relative_to(source) for x in imports.values()):
        raise RuntimeError('Source escaped immutable snapshot')
    result.update(case=config['id'], total_seconds=perf_counter()-started, kernel_sha256=kernel_hash,
                  imported_source_paths=imports, imports_from_snapshot=True)
    atomic_json(out/'RESULTS.json', result)
    progress('complete')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
