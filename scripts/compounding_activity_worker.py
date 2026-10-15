"""Fixed-jump histories and temporal coefficients; original physics unchanged."""
import sys

if __name__=='__main__' and sys.stdin.readline().strip()!='GO':
    raise SystemExit('Install caps before imports')

import json
from pathlib import Path


def main(out):
    source=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(source))
    import numpy as np
    from scipy.linalg import lu_factor, lu_solve

    from omega_v2.testbed.analysis.finite_classes import _stationary, analyze
    from omega_v2.testbed.analysis.observed_history import entropy_rows
    from omega_v2.testbed.analysis.renewal_profile import SampledHorizons
    from omega_v2.testbed.analysis.temporal_profile import coefficient_rows
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.compounding import CompoundingParameters, build_world
    from omega_v2.testbed.workflow.manifest import verify_bundle
    manifest=verify_bundle(out);plan=manifest['config']['plan']
    laws={};maximum_residual=0.
    for parent in plan['parents']:
        original=json.loads((source/parent['data_path']).read_text())
        if original['input_hash']!=parent['input_hash']:
            raise RuntimeError('Wrong scientific parent')
        by_mechanism={}
        for mechanism in original['stationary']:
            c=compile_world(build_world(CompoundingParameters(**original['law']['parameters']),mechanism))
            q=c['Q'];n=len(c['states']);pi=_stationary(q)
            exits,finite,jump=coefficient_rows(q,plan['reference_time'])
            g=entropy_rows(jump)
            jcache=SampledHorizons(jump,max(plan['fixed_jump_counts']))
            a=analyze(q,.25);tcache=SampledHorizons(a['P'],4096)
            factor=lu_factor(-q.toarray()+np.ones((n,1))*pi[None,:])
            roots={}
            for name,state in {'seed':(6,1,1),'unorganized':(8,1,0)}.items():
                root=c['index'][state];initial=np.zeros(n);initial[root]=1.
                fixed={str(k):float(jcache.occupation(root,k)[0] @ g) for k in plan['fixed_jump_counts']}
                physical={}
                for t in plan['horizons']:
                    _,final=tcache.occupation(root,round(t/.25))
                    weights=t*pi+lu_solve(factor,initial-final,trans=1)
                    count=float(weights @ exits);f=float(weights @ finite)
                    saved=original['physical'][f'{mechanism}:{name}'][str(t)]
                    error=max(abs(count-saved['expected_jumps']),abs(f-saved['finite_temporal_term']))
                    maximum_residual=max(maximum_residual,error)
                    if error>1e-7:
                        raise ArithmeticError('Existing temporal coefficients did not reproduce')
                    physical[str(t)]={'expected_jumps':count,'finite_term_bits':f,
                         'local_destination_surprisal_bits':float(weights @ (exits*g))}
                roots[name]={'fixed_jump_bits':fixed,'physical_horizons':physical}
            activity=float(pi @ exits)
            by_mechanism[mechanism]={'stationary_jump_rate':activity,
                   'stationary_local_destination_surprisal_rate':float(pi @ (exits*g)),
                   'embedded_jump_entropy_rate_bits_per_jump':float(pi @ (exits*g)/activity),
                   'stationary_finite_term_per_time':float(pi @ finite),'roots':roots}
            del jcache,tcache,a,c
        laws[parent['law']]={'parent':parent,'parameters':original['law']['parameters'],
                             'mechanisms':by_mechanism}
        print(parent['law'],flush=True)
    imports={name:str(module.__file__) for name,module in sys.modules.items()
             if name.startswith('omega_v2') and getattr(module,'__file__',None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen physics import')
    result={'status':'complete','input_hash':manifest['input_hash'],'source_hash':manifest['source_hash'],
            'plan':plan,'maximum_reproduction_error':maximum_residual,'laws':laws,
            'fixed_jumps_are_physical_time_entropy':False,'random_length_joint_entropy_computed':False}
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')


if __name__=='__main__':
    main(Path(sys.argv[1]))
