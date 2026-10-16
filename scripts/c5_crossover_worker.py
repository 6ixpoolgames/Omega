"""Exact finite-horizon probe of a historical rate/offset crossover estimate."""
import sys
if __name__=='__main__' and sys.stdin.readline().strip()!='GO':raise SystemExit('Process caps required')
import json
from pathlib import Path

def main(out):
    source=Path(__file__).resolve().parents[1];sys.path.insert(0,str(source))
    import numpy as np
    from omega_v2.testbed.workflow.manifest import verify_bundle,atomic_json
    from omega_v2.testbed.compiler import compile_world
    from omega_v2.testbed.domination_friction import FrictionParameters,FrictionPolicy,build_world,matched_roots
    from omega_v2.testbed.analysis.streamed_history import StreamedQueries
    from omega_v2.testbed.analysis.uniformized_entropy import entropy_cadences
    cfg=verify_bundle(out)['config'];cadence=.25;models=[]
    for active in (False,True):
        p=FrictionParameters(discovery=True,opportunity_yield=0,kappa=1,
                             d_energy_capacity=3,d_energy_quantum=.1)
        policy=FrictionPolicy(phi=.95 if active else 0,cost=1,mode='steering',
                             region=(2,),steering_scope='native_events')
        w=build_world(p,policy,max_states=32000);c=compile_world(w,max_states=32000)
        solver=StreamedQueries(c['Q'])
        payload=entropy_cadences(c['Q'],[cadence],96,threads=2,
                                progress=lambda s:print(s,flush=True))[cadence]
        sampled=solver.sampled(cadence,96,payload);root=c['index'][matched_roots(p)['device_present']]
        models.append((solver,sampled,root))
        print(json.dumps({'active':active,'states':len(w.states),'stage':'ready'}),flush=True)
    base,active=models
    dh=active[1]['rate']-base[1]['rate']
    db=active[1]['offset'][active[2]]-base[1]['offset'][base[2]]
    estimate=float(-db/dh)
    times=sorted(set([256.,1024.]+[round(estimate*factor/cadence)*cadence for factor in (.95,1.,1.05)]))
    rows=[]
    for t in times:
        values=[float(solver.finite(sampled,t)[root]) for solver,sampled,root in models]
        allowance=1e-6+sum(t/cadence*(m[1]['poisson_residual']+m[1]['diagnostics'].get('row_entropy_error_bits',0)) for m in models)
        row={'horizon':t,'whole_delta':values[1]-values[0],'numerical_allowance':allowance}
        rows.append(row);print(json.dumps(row),flush=True)
    bridge=abs(next(r['whole_delta'] for r in rows if r['horizon']==256)-18.07133626243501)
    if bridge>2e-5:raise ArithmeticError('Historical numerical bridge failed')
    imports={k:str(Path(v.__file__).resolve()) for k,v in sys.modules.items()
             if k.startswith('omega_v2') and getattr(v,'__file__',None)}
    if any(not Path(v).is_relative_to(source) for v in imports.values()):
        raise RuntimeError('Numerical import escaped frozen source')
    atomic_json(out/'RESULTS.json',{'historical_case':'y0-trap-c1-p0.95','steering_scope':'native_events',
        'chemistry_redirection_not_mobility':True,'cadence':cadence,'rate_delta':float(dh),
        'offset_delta':float(db),'asymptotic_horizon_estimate':estimate,
        'exact_sampled_finite_probes':rows,'historical_T256_bridge_error':bridge,
        'is_root_found_exactly':False,'imports_from_snapshot':True,'imported_source_paths':imports})

if __name__=='__main__':main(Path(sys.argv[1]))
