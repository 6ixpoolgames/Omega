"""Exact, capped capacity/boundary worker; no outcomes before engineering gate."""
import sys

if __name__ == '__main__' and sys.stdin.readline().strip() != 'GO':
    raise SystemExit('Caps must be installed before imports')

import json
from pathlib import Path
from time import perf_counter


def main(out):
    source=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(source))
    import numpy as np
    from scipy.linalg import expm, lu_factor, lu_solve

    from omega_v2.testbed.analysis.finite_classes import analyze
    from omega_v2.testbed.analysis.renewal_profile import SampledHorizons, coordinate_shares
    from omega_v2.testbed.analysis.temporal_profile import coefficient_rows
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.compounding import (
        CompoundingParameters,
        build_world,
        local_feedback_certificate,
        physical_readouts,
    )
    from omega_v2.testbed.workflow.manifest import verify_bundle

    manifest=verify_bundle(out)
    config=manifest['config']
    engineering=config['mode']=='engineering'
    protocol=config.get('protocol')
    if not engineering and protocol['status']!='frozen_before_scientific_ranking':
        raise RuntimeError('Frozen scientific protocol required')
    parameter_rows=([{'capacity':m} for m in config['capacities']] if engineering else [config['law']['parameters']])
    rows=[]; physical={}; stationary={}; recovery={}; profile=[]; maximum_residual=0.
    for fields in parameter_rows:
        params=CompoundingParameters(**fields)
        for mechanism in (['loop'] if engineering else protocol['mechanisms']):
            start=perf_counter()
            compiled=compile_world(build_world(params,mechanism))
            q=compiled['Q']; n=len(compiled['states'])
            compilation=perf_counter()-start
            analysis=analyze(q,.25)
            if len(analysis['class_indices'])!=1 or len(analysis['class_indices'][0])!=n:
                raise RuntimeError('This finite funding solve requires one irreducible class')
            pi=np.zeros(n); pi[analysis['class_indices'][0]]=analysis['stationary'][0]
            factor=lu_factor(-q.toarray()+np.ones((n,1))*pi[None,:])
            exits, finite, _=coefficient_rows(q)
            residual=max(analysis['residuals'].values())
            maximum_residual=max(maximum_residual,residual)
            cadences=[.25] if engineering else protocol['cadences']
            roots={'seed':[6,1,1]} if engineering else protocol['roots']
            horizons=[64] if engineering else protocol['horizons']
            for cadence in cadences:
                if cadence!=.25:
                    analysis=analyze(q,cadence)
                    maximum_residual=max(maximum_residual,max(analysis['residuals'].values()))
                kernel=analysis['P']
                cache=SampledHorizons(kernel,round(max(horizons)/cadence))
                shares=coordinate_shares(kernel,compiled['states'],[1,0,2])
                for name,state in roots.items():
                    root=compiled['index'][tuple(state)]
                    initial=np.zeros(n); initial[root]=1.
                    score={}
                    for horizon in horizons:
                        weights,final=cache.occupation(root,round(horizon/cadence))
                        bits=float(weights @ analysis['row_entropy'])
                        coordinate=shares @ weights
                        maximum_residual=max(maximum_residual,abs(float(coordinate.sum())-bits))
                        score[str(horizon)]={'bits':bits,'coordinate_bits':coordinate.tolist()}
                        if cadence==.25:
                            # Exact integral from the CTMC Poisson equation and exact endpoint.
                            continuous=horizon*pi+lu_solve(factor,initial-final,trans=1)
                            integral_residual=float(np.max(np.abs(continuous @ q-(final-initial))))
                            maximum_residual=max(maximum_residual,integral_residual)
                            if np.min(continuous)<-1e-8 or abs(continuous.sum()-horizon)>1e-7:
                                raise ArithmeticError('Continuous occupation identity failed')
                            value=physical_readouts(compiled,final,continuous,initial)
                            value['expected_jumps']=float(continuous @ exits)
                            value['finite_temporal_term']=float(continuous @ finite)
                            if not engineering:
                                physical.setdefault(f'{mechanism}:{name}',{})[str(horizon)]=value
                    if not engineering:
                        rows.append({'mechanism':mechanism,'root':name,'cadence':cadence,
                                     'rate':float(analysis['rate_per_step'][root]/cadence),
                                     'offset':float(analysis['offset'][root]),'scores':score})
                if not engineering and cadence==.25:
                    stationary[mechanism]=physical_readouts(compiled,pi,pi,pi)
                    stationary[mechanism]['coordinate_rate']=(shares @ pi/cadence).tolist()
                    stationary[mechanism]['rate']=float(pi @ analysis['row_entropy']/cadence)
                    # Killed process is only a first-passage query, never the lushness law.
                    root=compiled['index'][tuple(roots['seed'])]
                    recovery[mechanism]={}
                    for threshold in sorted({2,max(2,(params.capacity+1)//2)}):
                        keep=np.array([i for i,s in enumerate(compiled['states']) if s[2]<threshold])
                        killed=q[keep][:,keep].toarray()
                        row=np.zeros(len(keep)); row[int(np.flatnonzero(keep==root)[0])]=1.
                        recovery[mechanism][str(threshold)]={str(t):float(1-row @ expm(killed*t) @ np.ones(len(keep)))
                                                              for t in protocol['horizons']}
                del cache, shares
            profile.append({'capacity':params.capacity,'states':n,'compile_seconds':compilation,
                            'total_seconds':perf_counter()-start,'residual':residual})
            print(json.dumps({'capacity':params.capacity,'mechanism':mechanism,'seconds':profile[-1]['total_seconds']}),flush=True)
    if maximum_residual>1e-7:
        raise ArithmeticError('Numerical residual gate failed')
    imports={name:str(module.__file__) for name,module in sys.modules.items()
             if name.startswith('omega_v2') and getattr(module,'__file__',None)}
    if any(not Path(path).resolve().is_relative_to(source) for path in imports.values()):
        raise RuntimeError('Unfrozen import')
    result={'status':'complete','input_hash':manifest['input_hash'],'source_hash':manifest['source_hash'],
            'mode':config['mode'],'profile':profile,'maximum_residual':maximum_residual}
    if not engineering:
        result.update({'law':config['law'],'rows':rows,'physical':physical,'stationary':stationary,
                       'recovery':recovery,'feedback_certificate':local_feedback_certificate(params)})
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')


if __name__=='__main__':
    main(Path(sys.argv[1]))
