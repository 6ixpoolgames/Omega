"""Physical finite-window flux calibration; no entropy queried or optimized."""
from dataclasses import replace
from functools import lru_cache
import numpy as np
from scipy.optimize import brentq, least_squares
from scipy.sparse import coo_matrix

from ..compiler import compile_world
from ..domination_friction import matched_roots
from ..resource_transfer import TransferPolicy, build_world, transfer_events
from .streamed_history import StreamedQueries


class TransferFlux:
    def __init__(self, parameters, cost=.5, horizon=256.):
        self.p,self.cost,self.horizon=parameters,cost,horizon
        policy=TransferPolicy(mode='extract',cost=cost,assistance=0)
        self.world=build_world(parameters,policy)
        self.compiled=compile_world(self.world,max_states=12000)
        n=len(self.world.states); index=self.compiled['index']
        components=[]
        for direction in ('extract_forward','extract_reverse'):
            rows,cols,values=[],[],[]
            for i,s in enumerate(self.world.states):
                for e in transfer_events(s,parameters,policy):
                    if e.increments.get(direction):
                        rate=e.rate/policy.basal
                        rows.extend((i,i));cols.extend((index[e.target],i));values.extend((rate,-rate))
            components.append(coo_matrix((values,(rows,cols)),shape=(n,n)).tocsr())
        self.forward,self.reverse=components
        self.other=self.compiled['Q']-policy.basal*(self.forward+self.reverse)
        self.basal=policy.basal
        self.active=np.array([float(s[2]>0 and s[7]>0) for s in self.world.states])
        self.root=index[matched_roots(parameters)['device_present']]

    def kernel(self,assistance,affinity):
        work=affinity if self.p.drive else 0.
        f=(self.basal+assistance*self.active)*np.exp(self.p.beta*work/2)
        r=(self.basal+assistance*self.active)*np.exp(-self.p.beta*work/2)
        return (self.other+self.forward.multiply(f[:,None])+self.reverse.multiply(r[:,None])).tocsr(),f*(-self.forward.diagonal()),r*(-self.reverse.diagonal())

    @lru_cache(maxsize=256)
    def evaluate(self,assistance,affinity):
        Q,f,r=self.kernel(float(assistance),float(affinity))
        solver=StreamedQueries(Q)
        _,occupation,residual=solver.continuous_occupation(self.root,self.horizon)
        forward,reverse=float(occupation@f),float(occupation@r)
        return {'forward':forward,'reverse':reverse,'gross':forward+reverse,'net':forward-reverse,
                'occupation_residual':residual,'stationary_residual':solver.stationary_residual}


def calibrate(parameters, cost=.5, horizon=256.):
    model=TransferFlux(parameters,cost,horizon)
    affinities=(-3.,0.,3.)
    lower=max(model.evaluate(0.,A)['gross'] for A in affinities)
    upper=min(model.evaluate(2.,A)['gross'] for A in affinities)
    if not upper>lower+1e-4:
        raise ValueError('No common turnover interval within declared amplitude bounds')
    points=[]
    for fraction in (.25,.75):
        target=lower+fraction*(upper-lower)
        for A in affinities:
            a=brentq(lambda a:model.evaluate(float(a),A)['gross']-target,0.,2.,xtol=1e-8)
            points.append({'id':f'g{fraction:g}-A{A:g}','fraction':fraction,'target_gross':target,
                           'assistance':a,'affinity':A,**model.evaluate(float(a),A)})
        initial=next(p for p in points if p['fraction']==fraction and p['affinity']==0.)
        def residual(x):
            value=model.evaluate(float(x[0]),float(x[1]))
            return np.array([value['gross']-target,value['net']])/max(target,1.)
        fit=least_squares(residual,[initial['assistance'],0.],bounds=([0.,-3.],[2.,3.]),
                          xtol=1e-9,ftol=1e-9,gtol=1e-9,max_nfev=40)
        a,A=map(float,fit.x);value=model.evaluate(a,A)
        if abs(value['gross']-target)>2e-5 or abs(value['net'])>2e-5:
            raise ArithmeticError('Zero-net/gross-matched point not physically achieved')
        points.append({'id':f'g{fraction:g}-zero','fraction':fraction,'target_gross':target,
                       'assistance':a,'affinity':A,**value,'zero_net':True})
    # Check interpolation template against the independently compiled event law.
    errors=[]
    for point in points:
        w=build_world(parameters,TransferPolicy(mode='extract',cost=cost,
                      assistance=point['assistance'],affinity=point['affinity']))
        c=compile_world(w,max_states=12000)
        Q,_,_=model.kernel(point['assistance'],point['affinity'])
        errors.append(float(max(abs((Q-c['Q']).data),default=0)))
    if max(errors)>1e-11:raise ArithmeticError('Calibration kernel differs from native compiler')
    return {'points':points,'horizon':horizon,'cost':cost,'common_gross_interval':[lower,upper],
            'kernel_bridge_maximum':max(errors),'physical_matching_only':True,
            'zero_net_controls_total':2,'entropy_computed_during_calibration':False}
