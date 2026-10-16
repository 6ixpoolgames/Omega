"""Sparse growing population with paid local gates and thermal reverse events.

Histograms are the declared well-mixed readout, not a fine-site entropy shortcut.
Each compartment has its own fixed body inventory and carrier pool.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from math import comb,exp,factorial,isfinite
import numpy as np
from scipy.sparse import coo_matrix

@dataclass(frozen=True)
class Params:
    capture: float=.04
    fuel_bath: float=.04
    build: float=.3
    repair: float=.5
    wear: float=.04
    disassembly: float=.08
    switch: float=.15
    exchange: float=.4
    capture_benefit: float=6.
    assisted_birth: float=.4
    chemical_potential: float=4.
    switch_tokens: int=1
    def __post_init__(self):
        for name,value in vars(self).items():
            if not isfinite(value) or value<0:raise ValueError(f'Invalid {name}')
        if type(self.switch_tokens)!=int or self.switch_tokens<1:raise ValueError('Integer positive switch bill required')
        if self.capture_benefit<1:raise ValueError('Capture benefit must be >=1')

DEFAULT=Params()
FAMILIES=('drive_charge','bath_charge','wear','disassembly','basal_build','repair',
          'assisted_birth','switch_service','switch_export','exchange')
LEDGERS=('drive_work','bath_heat','gross_basal_birth','gross_assisted_birth','gross_thermal_reconstruction','gross_built_loss',
         'net_built','net_active','switches','gross_switch_fuel','net_switch_fuel',
         'gross_service_fuel','net_service_fuel')

@dataclass(frozen=True)
class Event:
    family: str
    source: tuple
    target: tuple
    rate: float
    work: float
    heat: float
    built_change: int
    active_change: int

def _inventory(inventories):
    if type(inventories)==int:inventories=(inventories,inventories)
    inv=tuple(inventories)
    if len(inv)!=2 or any(type(m)!=int or m<1 for m in inv):raise ValueError('Two positive inventories required')
    return inv

def states(inventories):
    inv=_inventory(inventories)
    local=[[(w,a,f,g) for w in range(m+1) for a in range(m-w+1)
            for f in range(m+1) for g in (0,1)] for m in inv]
    yield from product(*local)

def validate(state,inv):
    if len(state)!=2:raise ValueError('Two compartments required')
    for c,x in enumerate(state):
        if len(x)!=4 or any(type(v)!=int for v in x):raise ValueError('Integer local state required')
        w,a,f,g=x
        if min(w,a,f)<0 or w+a>inv[c] or f>inv[c] or g not in (0,1):raise ValueError('Invalid local inventory')

def energy(state):return sum(w+2*a+2*f for w,a,f,g in state)
def built(state):return sum(w+a for w,a,f,g in state)
def active(state):return sum(a for w,a,f,g in state)

def degeneracy(state,inventories):
    inv=_inventory(inventories);validate(state,inv);value=1
    for m,(w,a,f,g) in zip(inv,state):value*=factorial(m)//(factorial(m-w-a)*factorial(w)*factorial(a))*comb(m,f)
    return value

def _policy_entries(policy):
    if policy is None:return ((0.,0.),)*4
    if len(policy)!=4:raise ValueError('Four local inactive/active responses required')
    out=[]
    for response in policy:
        pair=(1-response,response) if isinstance(response,(int,float)) else tuple(response)
        if len(pair)!=2 or any(not isfinite(v) or v<0 for v in pair) or sum(pair)>1+1e-12:
            raise ValueError('Invalid service/export response')
        out.append(pair)
    return tuple(out)

def events(state,inventories,policy=None,params=DEFAULT):
    inv=_inventory(inventories);validate(state,inv);response=_policy_entries(policy);out=[]
    def emit(family,target,rate,work=0.):
        if rate==0:return
        if rate<0 or not isfinite(rate):raise ArithmeticError('Invalid rate')
        target=tuple(tuple(x) for x in target);validate(target,inv)
        delta=energy(target)-energy(state)
        out.append(Event(family,state,target,float(rate),float(work),float(work-delta),
                         built(target)-built(state),active(target)-active(state)))
    def change(c,dw=0,da=0,df=0,dg=0):
        target=[list(x) for x in state]
        for j,d in enumerate((dw,da,df,dg)):target[c][j]+=d
        return target
    for c,(w,a,f,g) in enumerate(state):
        m=inv[c];p=m-w-a
        if p:emit('disassembly',change(c,dw=1),params.disassembly*p*exp(-.5))
        if w:emit('disassembly',change(c,dw=-1),params.disassembly*w*exp(.5))
        if w:emit('wear',change(c,dw=-1,da=1),params.wear*w*exp(-.5))
        if a:emit('wear',change(c,dw=1,da=-1),params.wear*a*exp(.5))
        lam=params.capture*(1+(params.capture_benefit-1)*a/m)
        if f<m:
            emit('drive_charge',change(c,df=1),lam*(m-f)*exp((params.chemical_potential-2)/2),params.chemical_potential)
            emit('bath_charge',change(c,df=1),params.fuel_bath*(m-f)*exp(-1))
        if f:
            emit('drive_charge',change(c,df=-1),lam*f*exp(-(params.chemical_potential-2)/2),-params.chemical_potential)
            emit('bath_charge',change(c,df=-1),params.fuel_bath*f*exp(1))
        if g==0:
            if p and f:
                emit('basal_build',change(c,da=1,df=-1),params.build*p*f/m)
                if a:emit('assisted_birth',change(c,da=1,df=-1),params.assisted_birth*p*a*f/(m*m))
            if a and f<m:
                emit('basal_build',change(c,da=-1,df=1),params.build*a*(m-f)/m)
                if a>=2:emit('assisted_birth',change(c,da=-1,df=1),params.assisted_birth*a*(a-1)*(m-f)/(m*m))
            if w and f:emit('repair',change(c,dw=-1,da=1,df=-1),params.repair*w*f/m*exp(.5))
            if a and f<m:emit('repair',change(c,dw=1,da=-1,df=1),params.repair*a*(m-f)/m*exp(-.5))
        service,export=response[2*c+int(a>0)];k=params.switch_tokens
        if k<=m:
            denom=comb(m,k)
            if g==0:
                if f>=k:emit('switch_export',change(c,df=-k,dg=1),params.switch*export*comb(f,k)/denom*exp(k))
                if f+k<=m:emit('switch_service',change(c,df=k,dg=1),params.switch*service*comb(m-f,k)/denom*exp(-k))
            else:
                if f>=k:emit('switch_service',change(c,df=-k,dg=-1),params.switch*service*comb(f,k)/denom*exp(k))
                if f+k<=m:emit('switch_export',change(c,df=k,dg=-1),params.switch*export*comb(m-f,k)/denom*exp(-k))
    open_paths=sum(x[3] for x in state)
    if open_paths:
        for c in (0,1):
            other=1-c;fc=state[c][2];fo=state[other][2]
            if fc and fo<inv[other]:
                target=change(c,df=-1);target[other][2]+=1
                emit('exchange',target,params.exchange*open_paths*fc/inv[c]*(inv[other]-fo)/inv[other])
    return out

def build(inventories=(1,1),policy=None,params=DEFAULT,max_states=10000):
    inv=_inventory(inventories)
    expected=np.prod([(m+1)*(m+2)//2*(m+1)*2 for m in inv])
    if expected>max_states:raise RuntimeError('State cap; physical law was not truncated')
    st=tuple(states(inv));index={s:i for i,s in enumerate(st)};n=len(st)
    rows=[];cols=[];rates=[];flows={name:np.zeros(n) for name in FAMILIES+LEDGERS}
    for i,s in enumerate(st):
        total=0.
        for ev in events(s,inv,policy,params):
            rows.append(i);cols.append(index[ev.target]);rates.append(ev.rate);total+=ev.rate
            flows[ev.family][i]+=ev.rate;flows['drive_work'][i]+=ev.rate*ev.work;flows['bath_heat'][i]+=ev.rate*ev.heat
            flows['net_built'][i]+=ev.rate*ev.built_change;flows['net_active'][i]+=ev.rate*ev.active_change
            if ev.family=='basal_build' and ev.built_change>0:flows['gross_basal_birth'][i]+=ev.rate
            if ev.family=='assisted_birth' and ev.built_change>0:flows['gross_assisted_birth'][i]+=ev.rate
            if ev.family=='disassembly' and ev.built_change>0:flows['gross_thermal_reconstruction'][i]+=ev.rate
            if ev.built_change<0:flows['gross_built_loss'][i]+=ev.rate*(-ev.built_change)
            debit=-sum(y[2]-x[2] for x,y in zip(s,ev.target))
            if ev.family.startswith('switch'):
                flows['switches'][i]+=ev.rate;flows['gross_switch_fuel'][i]+=ev.rate*max(0,debit)
                flows['net_switch_fuel'][i]+=ev.rate*debit
            if ev.family in ('basal_build','assisted_birth','repair'):
                flows['gross_service_fuel'][i]+=ev.rate*max(0,debit);flows['net_service_fuel'][i]+=ev.rate*debit
        rows.append(i);cols.append(i);rates.append(-total)
    q=coo_matrix((rates,(rows,cols)),shape=(n,n)).tocsr()
    return {'states':st,'index':index,'Q':q,'flows':flows,'families':FAMILIES,'inventory':inv,
            'carriers':sum(inv),'parameters':params,'policy':_policy_entries(policy)}
