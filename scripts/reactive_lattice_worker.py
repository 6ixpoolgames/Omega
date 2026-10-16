"""Capped spatial calibration; engineering never computes preparation rankings."""
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
    import numpy as np
    from scipy.sparse.csgraph import connected_components

    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.reactive_lattice import (
        LatticeParameters,
        build_world,
        organized_root,
        reference_masks,
    )
    from omega_v2.testbed.workflow.manifest import verify_bundle

    manifest = verify_bundle(out)
    config = manifest['config']
    if config['mode'] != 'engineering':
        from reactive_lattice_science import science
        return science(out, manifest)
    rows = []
    for sites, monomers in config['geometries']:
        start = perf_counter()
        p = LatticeParameters(sites=sites, monomers=monomers)
        world = build_world(p)
        n = len(world.states)
        if n*n*8 > config['max_kernel_bytes'] or n > 10000:
            rows.append({'sites': sites, 'monomers': monomers, 'states': n,
                         'status': 'exact_kernel_budget_exceeded_before_ranking',
                         'kernel_bytes': n*n*8})
            print(json.dumps(rows[-1]), flush=True)
            continue
        c = compile_world(world)
        count, _ = connected_components(c['Q'], directed=True, connection='strong')
        refs = reference_masks(c, organized_root(p))
        dark = compile_world(build_world(replace(p, supply=0., damage=0.)))
        weights = np.exp(-p.beta*dark['energy'])
        weights /= weights.sum()
        flux = dark['Q'].multiply(weights[:, None])
        asymmetry = flux-flux.T
        balance = float(max(abs(asymmetry.data), default=0.))
        if balance > 1e-12 or count != 1:
            raise ArithmeticError('Balance/class calibration failed')
        row = {'sites': sites, 'monomers': monomers, 'states': n,
               'kernel_bytes': n*n*8, 'generator_bytes': sum(a.nbytes for a in
                  (c['Q'].data, c['Q'].indices, c['Q'].indptr)),
               'strong_classes': int(count), 'dark_detailed_balance_residual': balance,
               'density': monomers/sites, 'references': {}, 'temperature_calibration': []}
        for name, mu in refs.items():
            row['references'][name] = {'support': int(np.count_nonzero(mu)),
                'initial_bonds': float(mu @ c['observables']['bonds']),
                'initial_charge': float(mu @ c['observables']['charge']),
                'G1_mass_at_zero': float(mu @ c['observables']['G1']),
                'G2_mass_at_zero': float(mu @ c['observables']['G2'])}
        for beta in config['beta_grid']:
            canonical = np.exp(-beta*c['energy'])
            canonical /= canonical.sum()
            row['temperature_calibration'].append({'beta': beta,
                'canonical_bonds': float(canonical @ c['observables']['bonds']),
                'thermal_association_per_match': p.thermal_join*np.exp(-beta/2),
                'thermal_dissociation_per_bond': p.thermal_join*np.exp(beta/2),
                'shell_weights_depend_on_beta': False})
        if config['kernel_profile']:
            from omega_v2.testbed.analysis.blocked_entropy import sampled_kernel
            begin = perf_counter()
            kernel, _, residuals = sampled_kernel(c['Q'], .25, block_rows=32,
                                                  max_kernel_bytes=config['max_kernel_bytes'])
            row['kernel_seconds'] = perf_counter()-begin
            row['kernel_residuals'] = residuals
            # Kernel generated only for timing/memory, no root entropy compared.
            del kernel
        from reactive_lattice_science import calibrate_numerics
        row['numerical_calibration'] = calibrate_numerics(c)
        row.update({'seconds': perf_counter()-start, 'status': 'complete'})
        rows.append(row)
        print(json.dumps(row), flush=True)
        del c, dark, world
    imports = {name: str(m.__file__) for name, m in sys.modules.items()
               if name.startswith('omega_v2') and getattr(m, '__file__', None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen import')
    (out/'RESULTS.json').write_text(json.dumps({'mode': 'engineering', 'rows': rows,
        'input_hash': manifest['input_hash'], 'rankings_inspected': False}, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
