"""Registered controller-grid extension and optional Rule A interpretation."""
from __future__ import annotations
from itertools import product
import json
from pathlib import Path
import time

import numpy as np
from scipy.linalg import solve
from . import controlled_slice as world
from .bng_network import transition
from .rule_a_assessment import retention_profile

SPEC=world.ROOT/'docs/research_notes/lushness_testbed/access_extension'
ENERGIES=np.array([world.energy(s) for s in world.STATES])
ACTIVE=np.array([sum(b==2 for b,f,g in s) for s in world.STATES])
SHELL=np.array([i for i,s in enumerate(world.STATES) if world.energy(s)==4 and all(g==0 for b,f,g in s)])


def load_protocol():
    p=json.loads((SPEC/'PROTOCOL.json').read_text())
    if p['status']!='frozen_before_scientific_ranking':raise RuntimeError('Unfrozen protocol')
    base=json.loads((world.SPEC/'PROTOCOL.json').read_text())['parameters']
    if base['beta']!=1 or base['body_energies']!=[0,1,2] or base['fuel_energy']!=2:
        raise RuntimeError('Energy adapter incompatible with declared parameters')
    return p,base


def basis(parameters):
    idle=((0.,0.),)*4
    base,_=world.generator(idle,parameters)
    pieces=[]
    for c in range(4):
        for a in (0,1):
            pol=list(idle);pol[c]=tuple(float(j==a) for j in (0,1))
            q,_=world.generator(tuple(pol),parameters)
            pieces.append(q-base)
    return base,np.stack(pieces)


def compile_policy(pol,parameters,linear=None):
    base,pieces=linear if linear is not None else basis(parameters)
    q=base+np.tensordot(np.array(pol).reshape(-1),pieces,axes=1)
    fixed=[all(sum(pol[2*c+o])==0 for o in (0,1)) for c in (0,1)]
    keep=np.array([i for i,s in enumerate(world.STATES) if all(not fixed[c] or s[c][2]==0 for c in (0,1))])
    sub=q[np.ix_(keep,keep)]
    if np.max(abs(sub.sum(axis=1)))>1e-11:raise AssertionError('Reachable class not closed')
    if not set(SHELL).issubset(set(keep)):raise AssertionError('Matched root missing')
    return q,sub,keep


def evaluate(q,keep,delta,horizons):
    p=transition(q,delta);g=world.entropy_rows(p)
    pi=world.stationary(q);h=float(pi@g)
    z=solve(np.eye(len(q))-p+np.ones((len(q),1))*pi[None,:],g-h)
    residual=float(max(abs(z-p@z-g+h)))
    if residual>1e-9:raise ArithmeticError('Offset solve')
    index={v:i for i,v in enumerate(keep)}
    organized=index[world.ROOT_ORGANIZED];disassembled=index[world.ROOT_DISASSEMBLED]
    ref=np.zeros(len(q));ref[[index[i] for i in SHELL]]=1/len(SHELL)
    bits=np.zeros(len(q));rows={};steps={round(t/delta):t for t in horizons}
    for n in range(1,max(steps)+1):
        bits=g+p@bits
        if n in steps:
            rows[str(steps[n])]={'organized':float(bits[organized]),'disassembled':float(bits[disassembled]),
                                'matched_shell':float(ref@bits),'stationary_conditional':float(n*h)}
    return {'rate':h/delta,'offsets':{'organized':float(z[organized]),'disassembled':float(z[disassembled]),
                                     'matched_shell':float(ref@z)},
            'stationary_active_total':float(pi@ACTIVE[keep]),'states':len(q),'profiles':rows,
            'residuals':{'stationary':float(max(abs(pi@q))),'poisson':residual}},pi,ref


def one_hot(n,i):
    x=np.zeros(n);x[i]=1;return x


def rule_a(q,keep,pi,ref,delta,lags):
    index={v:i for i,v in enumerate(keep)}
    roots={'organized':one_hot(len(q),index[world.ROOT_ORGANIZED]),
           'disassembled':one_hot(len(q),index[world.ROOT_DISASSEMBLED]),
           'matched_shell':ref,'stationary':pi}
    return retention_profile(q,delta,lags,roots)


def chain_rule_rate(q,keep,pi,delta):
    p=transition(q,delta)
    keys=sorted({tuple((b,f) for b,f,g in world.STATES[i]) for i in keep})
    projection=np.zeros((len(q),len(keys)))
    for row,i in enumerate(keep):projection[row,keys.index(tuple((b,f) for b,f,g in world.STATES[i]))]=1
    g=world.entropy_rows(p);small=world.entropy_rows(p@projection)
    return {'next_body_fuel_given_full_previous':float(pi@small/delta),
            'next_gate_given_next_body_fuel_and_full_previous':float(pi@(g-small)/delta)}


def rate_best(rows):
    high=max(r['rate'] for r in rows);tied=[r for r in rows if high-r['rate']<=1e-9]
    return max(tied,key=lambda r:r['offsets']['organized']),[r['policy'] for r in tied]


def run(out,factor,smoke=False):
    start=time.perf_counter();out.mkdir(parents=True,exist_ok=True)
    protocol,params=load_protocol()
    if factor not in protocol['active_capture_factors']:raise ValueError('Unregistered capture factor')
    params={**params,'active_capture_factor':factor}
    names=list(protocol['responses']);responses={k:tuple(v) for k,v in protocol['responses'].items()}
    linear=basis(params)
    if smoke:
        # Algebra/compiler checks only; no policy rankings or scientific readouts.
        audits=[]
        for labels in (('idle',)*4,('service','mix50','export','idle'),('mix25','mix75','service','mix50')):
            pol=tuple(responses[k] for k in labels);q,sub,keep=compile_policy(pol,params,linear)
            hand,_=world.generator(pol,params)
            error=float(np.max(abs(q-hand)))
            if error>1e-12:raise AssertionError('Linear compiler differs from native channels')
            world.stationary(sub)
            audits.append({'policy':labels,'states':len(keep),'generator_error':error})
        legacy=((1.,0.),(0.5,0.5),(1.,0.),(0.5,0.5))
        q,_,_=compile_policy(legacy,params,linear);hand,_=world.generator((0.,.5,0.,.5),params)
        if np.max(abs(q-hand))>1e-12:raise AssertionError('Legacy mismatch')
        (out/'smoke.json').write_text(json.dumps({'compiler_checks':audits,'legacy_error':float(np.max(abs(q-hand)))},indent=2))
        return
    rows=[];max_stationary=max_poisson=0.
    for count,labels in enumerate(product(names,repeat=4),1):
        pol=tuple(responses[k] for k in labels);_,sub,keep=compile_policy(pol,params,linear)
        r,_,_=evaluate(sub,keep,protocol['primary_cadence'],protocol['horizons'])
        rows.append({'policy':list(labels),**r})
        max_stationary=max(max_stationary,r['residuals']['stationary']);max_poisson=max(max_poisson,r['residuals']['poisson'])
        if count%100==0:
            (out/'progress.json').write_text(json.dumps({'completed':count,'total':protocol['controller_count'],'factor':factor}))
    if len(rows)!=protocol['controller_count']:raise AssertionError('Policy enumeration count')
    legacy_weights=((1.,0.),(.5,.5),(1.,0.),(.5,.5))
    legacy_full,_,_=compile_policy(legacy_weights,params,linear)
    legacy_native,_=world.generator((0.,.5,0.,.5),params)
    legacy_error=float(np.max(abs(legacy_full-legacy_native)))
    if legacy_error>1e-12:raise AssertionError('Legacy controller regression')
    idle_full,idle_sub,idle_keep=compile_policy(((0.,0.),)*4,params,linear)
    _,idle_flows=world.generator(((0.,0.),)*4,params)
    idle_switch_rate=float(max(abs(idle_flows['switches'])))
    if idle_switch_rate!=0:raise AssertionError('Idle changes gate')
    winner,ties=rate_best(rows)
    det=[r for r in rows if all(k in ('idle','service','export') for k in r['policy'])]
    detwin,_=rate_best(det)
    activewin=max(rows,key=lambda r:r['stationary_active_total'])
    chosen={tuple(r['policy']) for r in (winner,detwin,activewin)}
    chosen.update((k,)*4 for k in ('idle','service','mix50','export'))
    chosen.add(('service','mix50','service','mix50'))
    diagnostics=[]
    for labels in sorted(chosen):
        pol=tuple(responses[k] for k in labels);full,sub,keep=compile_policy(pol,params,linear)
        _,pi,ref=evaluate(sub,keep,.25,protocol['horizons'])
        q,flows=world.generator(pol,params)
        if np.max(abs(q-full))>1e-12:raise AssertionError('Survey law mismatch')
        diagnostic={'policy':list(labels),'rule_a':rule_a(sub,keep,pi,ref,.25,protocol['rule_a']['lags']),
                    'chain_rule_rate':chain_rule_rate(sub,keep,pi,.25),
                    'organized_T64':world.survey(full,flows,64,world.ROOT_ORGANIZED),
                    'disassembled_T64':world.survey(full,flows,64,world.ROOT_DISASSEMBLED),
                    'recovery_T64':world.recovery(full,64,world.ROOT_DISASSEMBLED),'cadence_sensitivity':[]}
        for delta in protocol['sensitivity_cadences']:
            r,_,_=evaluate(sub,keep,delta,protocol['horizons'])
            diagnostic['cadence_sensitivity'].append({'cadence':delta,**r})
        diagnostics.append(diagnostic)
    shell_states=[world.STATES[i] for i in SHELL]
    result={'experiment':protocol['id'],'capture_factor':factor,'controller_count':len(rows),
            'deterministic_or_idle_count':len(det),'shell_states':shell_states,'shell_count':len(SHELL),
            'winner':winner,'rate_optimal_set':ties,'best_deterministic_or_idle':detwin,
            'max_functioning_benchmark':activewin,'finite_winners':{str(t):max(rows,key=lambda r:r['profiles'][str(t)]['organized'])['policy'] for t in protocol['horizons']},
            'policies':rows,'diagnostics':diagnostics,
            'audits':{'max_stationarity_residual':max_stationary,'max_poisson_residual':max_poisson,
                      'legacy_generator_error':legacy_error,'idle_switch_rate':idle_switch_rate,
                      'reachable_state_counts':sorted({r['states'] for r in rows}),
                      'rule_a_nonnegative_and_monotone':'checked in diagnostic module at all known roots',
                      'resource_residual':max(abs(d[k]['first_law_residual']) for d in diagnostics for k in ('organized_T64','disassembled_T64'))},
            'runtime_seconds':time.perf_counter()-start}
    if result['audits']['resource_residual']>1e-8:raise AssertionError('Ledger')
    (out/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result
