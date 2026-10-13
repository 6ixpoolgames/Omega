"""Finite, driven two-compartment CTMC with paid gates and reversible chemistry.

The reaction table is shared by the native solver and emitted BNGL. No utility
reward or action-label entropy is added. Numerical search is outside the world.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess

import numpy as np
from scipy.linalg import expm, solve
from scipy.sparse.csgraph import connected_components
from .bng_network import parse_net, enumerate_generator, transition

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / 'docs/research_notes/lushness_testbed/controlled'
LOCAL = tuple(product(range(3), range(2), range(2)))  # body, fuel, gate
STATES = tuple(product(LOCAL, repeat=2))
INDEX = {s: i for i, s in enumerate(STATES)}
ENERGY_BODY = (0., 1., 2.)
ROOT_ORGANIZED = INDEX[((2, 0, 0), (2, 0, 0))]
ROOT_DISASSEMBLED = INDEX[((0, 1, 0), (0, 1, 0))]
POLICIES = tuple(product((0., .5, 1.), repeat=4))


def energy(s):
    return sum(ENERGY_BODY[b] + 2*f for b, f, g in s)


@dataclass(frozen=True)
class Channel:
    source: tuple
    target: tuple
    support: tuple[int, ...]
    family: str
    rate: float
    work: float
    heat: float


def channels(policy, parameters, speed=1.):
    """Each local pair is emitted once; energies in kBT, time in reference units."""
    result = []

    def pair(source, target, support, family, attempt, work=0.):
        de = energy(target)-energy(source)
        for a, b, sign in ((source, target, 1), (target, source, -1)):
            rate = speed*attempt*math.exp(sign*(work-de)/2)
            result.append(Channel(a, b, support, family, rate, sign*work, sign*(work-de)))

    for c in (0, 1):
        other = 1-c
        def state(b, f, g):
            s = [(0, 0, 0), (0, 0, 0)]
            s[c] = (b, f, g)
            return tuple(s)
        for b, g in product(range(3), range(2)):
            a, z = state(b, 0, g), state(b, 1, g)
            capture = parameters['capture']*(parameters['active_capture_factor'] if b == 2 else 1)
            pair(a, z, (c,), 'drive', capture, parameters['chemical_potential'])
            pair(a, z, (c,), 'fuel_bath', parameters['fuel_bath'])
        for f, g in product(range(2), range(2)):
            pair(state(2, f, g), state(1, f, g), (c,), 'wear_restore', parameters['wear'])
            pair(state(1, f, g), state(0, f, g), (c,), 'disassemble_restore', parameters['disassembly'])
        pair(state(0, 1, 0), state(2, 0, 0), (c,), 'build', parameters['build'])
        pair(state(1, 1, 0), state(2, 0, 0), (c,), 'repair', parameters['repair'])
        for b in range(3):
            p = policy[2*c+int(b == 2)] if policy is not None else None
            if p is not None:
                pair(state(b, 1, 0), state(b, 0, 1), (c,), 'switch_export', parameters['switch']*p)
                pair(state(b, 1, 1), state(b, 0, 0), (c,), 'switch_service', parameters['switch']*(1-p))
        # One reversible exchange pathway controlled by each end. Both may open.
        for bc, bo, go in product(range(3), range(3), range(2)):
            a = [(0, 0, 0), (0, 0, 0)]
            a[c], a[other] = (bc, 1, 1), (bo, 0, go)
            z = list(a); z[c] = (bc, 0, 1); z[other] = (bo, 1, go)
            pair(tuple(a), tuple(z), (0, 1), 'exchange', parameters['exchange'])
    return result


def generator(policy, parameters, speed=1.):
    q = np.zeros((len(STATES), len(STATES)))
    names = ('drive_work', 'bath_heat', 'build', 'repair', 'wear', 'dismantle',
             'switches', 'exchange', 'fuel_spent_service', 'fuel_spent_switch')
    flows = {name: np.zeros(len(STATES)) for name in names}
    for ch in channels(policy, parameters, speed):
        if ch.rate == 0: continue
        for i, s in enumerate(STATES):
            if any(s[c] != ch.source[c] for c in ch.support): continue
            target = list(s)
            for c in ch.support: target[c] = ch.target[c]
            j = INDEX[tuple(target)]
            q[i, j] += ch.rate
            flows['drive_work'][i] += ch.rate*ch.work
            flows['bath_heat'][i] += ch.rate*ch.heat
            c = ch.support[0]
            db = target[c][0]-s[c][0]
            df = target[c][1]-s[c][1]
            if ch.family in ('build', 'repair'):
                if db > 0: flows[ch.family][i] += ch.rate
                flows['fuel_spent_service'][i] -= ch.rate*df
            if ch.family == 'wear_restore' and db < 0: flows['wear'][i] += ch.rate
            if ch.family == 'disassemble_restore' and db < 0: flows['dismantle'][i] += ch.rate
            if ch.family.startswith('switch'):
                flows['switches'][i] += ch.rate
                flows['fuel_spent_switch'][i] -= ch.rate*df
            if ch.family == 'exchange': flows['exchange'][i] += ch.rate
    np.fill_diagonal(q, -q.sum(axis=1))
    return q, flows


def bng_text(policy, parameters):
    chs = channels(policy, parameters)
    def molecule(c, local):
        b, f, g = local
        return f'C{c}(b~{b},f~{f},g~{g})'
    lines = ['begin model', 'begin parameters']
    lines += [f' r{i} {ch.rate:.17g}' for i, ch in enumerate(chs) if ch.rate > 0]
    lines += ['end parameters', 'begin molecule types']
    lines += [f' C{c}(b~0~1~2,f~0~1,g~0~1)' for c in (0, 1)]
    lines += ['end molecule types', 'begin seed species']
    lines += [f' {molecule(c, (2, 0, 0))} 1' for c in (0, 1)]
    lines += ['end seed species', 'begin reaction rules']
    for i, ch in enumerate(chs):
        if ch.rate == 0: continue
        left = ' + '.join(molecule(c, ch.source[c]) for c in ch.support)
        right = ' + '.join(molecule(c, ch.target[c]) for c in ch.support)
        lines.append(f' {left} -> {right} r{i}')
    lines += ['end reaction rules', 'end model', 'generate_network({overwrite=>1})']
    return '\n'.join(lines)+'\n'


def engine_check(out, parameters):
    engine = Path(importlib.util.find_spec('bionetgen').origin).parent/'bng-win'
    env = dict(os.environ, BNGPATH=engine.as_posix())
    checks = []
    for k, pol in enumerate(((0.,0.,1.,1.),(.5,.5,.5,.5),(1.,0.,.5,1.))):
        folder = out/f'bng-{k}'; folder.mkdir()
        (folder/'model.bngl').write_text(bng_text(pol, parameters))
        with (folder/'engine.log').open('w') as log:
            subprocess.run(['C:/Program Files/Git/usr/bin/perl.exe', (engine/'BNG2.pl').as_posix(), 'model.bngl'],
                cwd=folder, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=30)
        net = parse_net(folder/'model.net'); states, q = enumerate_generator(net, state_cap=200)
        mapping = []
        for state in states:
            s = [None, None]
            for name, count in zip(net.species, state):
                if count:
                    match = re.fullmatch(r'C([01])\(b~([012]),f~([01]),g~([01])\)',name)
                    if count != 1 or match is None: raise AssertionError('BNG state decoding')
                    c,b,f,g = map(int,match.groups()); s[c]=(b,f,g)
            mapping.append(INDEX[tuple(s)])
        native, _ = generator(pol, parameters)
        error = float(np.max(abs(q-native[np.ix_(mapping,mapping)])))
        if len(states) != 144 or error > 1e-10: raise AssertionError('BNG generator mismatch')
        checks.append({'policy':pol,'states':len(states),'generator_error':error})
    return checks


def entropy_rows(p):
    logs=np.zeros_like(p); np.log2(p,out=logs,where=p>0)
    return -(p*logs).sum(axis=1)


def stationary(q):
    classes=connected_components(q>0,directed=True,connection='strong',return_labels=False)
    if classes != 1: raise ArithmeticError('Limiting solver requires one irreducible class')
    a=q.T.copy(); a[-1]=1
    rhs=np.zeros(len(q)); rhs[-1]=1
    pi=solve(a,rhs)
    if min(pi)<-1e-10 or max(abs(pi@q))>1e-10: raise ArithmeticError('Stationary solve')
    return pi


def evaluate(q, delta, horizons, roots, limiting=True):
    p=transition(q,delta); g=entropy_rows(p)
    value=np.zeros(len(q)); profiles={}
    steps={int(round(t/delta)):t for t in horizons}
    for n in range(1,max(steps)+1):
        value=g+p@value
        if n in steps: profiles[str(steps[n])] = [float(value[r]) for r in roots]
    result={'profiles':profiles,'row_error':float(max(abs(p.sum(axis=1)-1)))}
    if limiting:
        pi=stationary(q); h=float(pi@g)
        z=solve(np.eye(len(q))-p+np.ones((len(q),1))*pi[None,:],g-h)
        residual=float(max(abs(z-p@z-(g-h))))
        if residual>1e-9: raise ArithmeticError('Poisson residual')
        result.update(rate_bits_per_time=h/delta,offset_bits=[float(z[r]) for r in roots],
                      stationary_conditional_bits={str(t):float(t*h/delta) for t in horizons},
                      communicating_classes=1,
                      stationary_residual=float(max(abs(pi@q))),poisson_residual=residual)
    return result


def survey(q, flows, horizon, root):
    # Block exponential integrates expected event fluxes, including reverse flows.
    keys=list(flows); rates=np.column_stack([flows[k] for k in keys])
    block=np.zeros((len(q)+len(keys),len(q)+len(keys)))
    block[:len(q),:len(q)]=q; block[:len(q),len(q):]=rates
    e=expm(horizon*block); dist=e[root,:len(q)]
    vals=e[root,len(q):]
    energies=np.array([energy(s) for s in STATES])
    record={k:float(v) for k,v in zip(keys,vals)}
    record.update(active_expected=[float(dist@np.array([s[c][0]==2 for s in STATES])) for c in (0,1)],
                  both_active=float(dist@np.array([all(x[0]==2 for x in s) for s in STATES])),
                  fuel_expected=[float(dist@np.array([s[c][1] for s in STATES])) for c in (0,1)],
                  energy_change=float(dist@energies-energies[root]))
    record['first_law_residual']=record['energy_change']-record['drive_work']+record['bath_heat']
    if abs(record['first_law_residual'])>1e-8: raise AssertionError('First-law ledger')
    return record


def recovery(q, horizon, root):
    targets=[i for i,s in enumerate(STATES) if all(x[0]==2 for x in s)]
    killed=q.copy(); killed[targets,:]=0
    hit=float(expm(horizon*killed)[root,targets].sum())
    present=float(expm(horizon*q)[root,targets].sum())
    return {'both_active_hit_by_horizon':hit,'both_active_at_horizon':present,
            'meaning':'functional reconstruction; no claim about individual identity'}


def run(out):
    out.mkdir(parents=True,exist_ok=True)
    protocol=json.loads((SPEC/'PROTOCOL.json').read_text())
    params=protocol['parameters']
    checks=engine_check(out,params)
    eqparams={**params,'chemical_potential':0.}
    eq,_=generator((.5,)*4,eqparams)
    energies=np.array([energy(s) for s in STATES]); boltz=np.exp(-energies); boltz/=sum(boltz)
    db=float(np.max(abs(boltz[:,None]*eq-(boltz[:,None]*eq).T)))
    if db>1e-11: raise AssertionError('Closed equilibrium detailed balance')
    results=[]
    queries=[(1.,d) for d in protocol['cadences']]+[(v,.25) for v in protocol['speeds'] if v!=1]
    for speed,delta in queries:
        records=[]
        for pol in POLICIES:
            q,_=generator(pol,params,speed)
            r=evaluate(q,delta,protocol['horizons'],(ROOT_ORGANIZED,ROOT_DISASSEMBLED))
            records.append({'policy':list(pol),**r})
        results.append({'speed':speed,'cadence':delta,'policies':records})
        (out/'progress.json').write_text(json.dumps({'completed_queries':len(results),'total':len(queries)}))
    main=next(x for x in results if x['speed']==1 and x['cadence']==.25)
    candidates=main['policies']
    def rate_set(rows):
        top=max(x['rate_bits_per_time'] for x in rows)
        return [x for x in rows if top-x['rate_bits_per_time']<=1e-9]
    winner=max(rate_set(candidates),key=lambda x:x['offset_bits'][0])
    deterministic=[x for x in candidates if .5 not in x['policy']]
    bestdet=max(rate_set(deterministic),key=lambda x:x['offset_bits'][0])
    finite={str(t):max(candidates,key=lambda x:x['profiles'][str(t)][0])['policy'] for t in protocol['horizons']}
    chosen={tuple(winner['policy']),tuple(bestdet['policy']),(0.,)*4,(1.,)*4,(.5,)*4}
    surveys=[]
    for pol in sorted(chosen):
        q,flows=generator(pol,params)
        for t in protocol['horizons']:
            surveys.append({'policy':pol,'horizon':t,'organized':survey(q,flows,t,ROOT_ORGANIZED),
                            'disassembled':survey(q,flows,t,ROOT_DISASSEMBLED),
                            'recovery':recovery(q,t,ROOT_DISASSEMBLED)})
    # Passive means both gates fixed at service, not different apparatus/drive.
    q,flows=generator(None,params)
    kept=[i for i,s in enumerate(STATES) if all(x[2]==0 for x in s)]
    passive=evaluate(q[np.ix_(kept,kept)],.25,protocol['horizons'],
                     (kept.index(ROOT_ORGANIZED),kept.index(ROOT_DISASSEMBLED)))
    # Sampled-path information cross-check from exactly the declared transition law.
    q,_=generator(tuple(winner['policy']),params); p=transition(q,.25)
    # Chain rule at each next sample, conditional on the FULL previous state.
    # This is not the entropy rate of a marginal hidden-state observation process.
    bodyfuel=sorted({tuple((b,f) for b,f,g in s) for s in STATES})
    projection=np.zeros((144,len(bodyfuel)))
    for i,s in enumerate(STATES):projection[i,bodyfuel.index(tuple((b,f) for b,f,g in s))]=1
    pi=stationary(q)
    physical_rate=float(pi@entropy_rows(p@projection)/.25)
    gate_rate=float(pi@(entropy_rows(p)-entropy_rows(p@projection))/.25)
    rng=np.random.default_rng(protocol['seed']); sample=np.zeros(10000); positions=np.full(10000,ROOT_ORGANIZED)
    cdf=np.cumsum(p,axis=1); cdf[:,-1]=1
    for _ in range(16):
        u=rng.random(len(positions)); target=(u[:,None]>cdf[positions]).sum(axis=1)
        sample-=np.log2(p[positions,target]); positions=target
    target=winner['profiles']['4'][0]; se=float(sample.std(ddof=1)/np.sqrt(len(sample)))
    mc={'mean':float(sample.mean()),'exact':target,'se':se,'passed':bool(abs(sample.mean()-target)<=6*se)}
    if not mc['passed']: raise AssertionError('Path information sampling check')
    rng=np.random.default_rng(10); permutation=rng.permutation(len(q))
    pr=transition(q[np.ix_(permutation,permutation)],.25)
    rename=float(np.max(abs(pr-p[np.ix_(permutation,permutation)])))
    timeunits=float(np.max(abs(transition(q/10,2.5)-p)))
    semigroup=float(np.max(abs(p@p-transition(q,.5))))
    for err in (rename,timeunits,semigroup):
        if err>1e-10: raise AssertionError('Representation audit')
    summary={'fixture':'B','states':144,'controller_count':81,'deterministic_count':16,
             'queries':results,'winner':winner,'best_deterministic':bestdet,'finite_winners':finite,
             'passive_service':passive,'surveys':surveys,
             'winner_rate_chain_rule':{'next_body_fuel_given_full_previous':physical_rate,
                                      'next_gate_given_next_body_fuel_and_full_previous':gate_rate},
             'optimal_sets':[{'speed':r['speed'],'cadence':r['cadence'],
                 'rate_optimal_policies':[x['policy'] for x in rate_set(r['policies'])],
                 'overlap_primary':[x['policy'] for x in rate_set(r['policies'])
                     if x['policy'] in [y['policy'] for y in rate_set(candidates)]]} for r in results],
             'audits':{'bng':checks,'closed_detailed_balance':db,'sampling':mc,'renaming':rename,
                       'unit_conversion':timeunits,'semigroup':semigroup},
             'scope':'Exact enumeration of fixed local response grid; no unrestricted optimum or ethical verdict.'}
    (out/'result.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    return summary
