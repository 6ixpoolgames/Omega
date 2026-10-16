"""Composable funded pump, constructed access and material-sink modules."""
from dataclasses import asdict,dataclass,replace
from itertools import product
from math import comb,exp,isfinite,sqrt
from .contracts import Event,RuleModule
from .domination_friction import (
    FrictionParameters,FrictionPolicy,build_world as native_world,d_bank,s_bank,field_energy)


@dataclass(frozen=True)
class ExtensionSpec:
    pump: bool=False
    pump_mode: str='passive'
    fuel_energy: float=.5
    assistance: float=.4
    basal: float=.0002
    charging: float=.08
    opportunity: bool=False
    local_source: float=.12
    access_strength: float=1.2
    enabler_build: float=.04
    enabler_upkeep: float=.01
    enabler_thermal: float=.00005
    irreversible_loss: float=0.

    def __post_init__(self):
        if self.pump_mode not in ('passive','extract','donate'):raise ValueError('Unknown pump channel')
        if type(self.pump) is not bool or type(self.opportunity) is not bool:raise ValueError('Physical feature flags required')
        for key,value in asdict(self).items():
            if key in ('pump','opportunity','pump_mode'):continue
            if not isfinite(value) or value<0 or (key not in ('irreversible_loss','assistance') and value==0):
                raise ValueError('Invalid physical coefficient: '+key)


def build_world(parameters=None,extension=None,policy=None,max_states=32000):
    p=parameters or FrictionParameters(d_energy_capacity=2,d_energy_quantum=.5)
    x=extension or ExtensionSpec();policy=policy or FrictionPolicy(phi=0,cost=0)
    if x.opportunity and not p.discovery:raise ValueError('Constructed access requires the physical pocket')
    db,sb=d_bank(p),s_bank(p);du,su=db.ticks(1),sb.ticks(1)
    bill=db.ticks(x.fuel_energy) if x.pump else 0
    if x.pump and bill>db.maximum:raise ValueError('Fuel charge exceeds D bank capacity')
    base=native_world(p,policy,max_states=max_states)
    names=[]
    if x.pump:names.append('D.pump_fuel')
    if x.opportunity:names+=['pocket.packet','S.access_device']
    if x.irreversible_loss:names.append('S.lost_material')
    indices={name:8+i for i,name in enumerate(names)}
    if len(base.states)*2**len(names)>max_states*2:raise RuntimeError('Physical feature state cap; no truncation')
    states=tuple(s+tail for s in base.states for tail in product(range(2),repeat=len(names))
                 if s[5]+(tail[names.index('S.lost_material')] if 'S.lost_material' in names else 0)<=p.s_capacity)
    if len(states)>max_states:raise RuntimeError('Physical feature state cap; no truncation')
    if x.irreversible_loss and p.s_capacity!=1:raise ValueError('First material-sink adapter has one S apparatus slot')
    allowed=frozenset(states)
    def value(s,name):return s[indices[name]] if name in indices else 0
    def validate(s):
        if not isinstance(s,tuple) or s not in allowed or any(type(v) is not int for v in s):raise ValueError('Invalid extended physical state')
    def energy(s):
        return base.energy(s[:8])+x.fuel_energy*value(s,'D.pump_fuel')+2*value(s,'pocket.packet')+value(s,'S.access_device')
    def density(s):return base.degeneracy(s[:8])
    def change(s,updates):
        out=list(s)
        for i,v in updates.items():out[i]=v
        return tuple(out)
    def event(s,t,k,family,increments=None,work=0.,thermal=True):
        rate=k*sqrt(density(t)/density(s))*(exp(-p.beta*(energy(t)-energy(s)-work)/2) if thermal else 1.)
        return Event(family,family,t,rate,tuple(i for i,(a,b) in enumerate(zip(s,t)) if a!=b),work,increments or {})
    def owned(s,subject):
        if subject=='D':return db.energy(s[3])+s[2]+s[7]-(s[1]==2)+x.fuel_energy*value(s,'D.pump_fuel')
        return sb.energy(s[6])+s[5]-(s[4]==2)+field_energy(s,p)+value(s,'S.access_device')
    def accounted(events,s):
        for e in events:
            increments={sub+'_energy_by_family.'+e.family:float(owned(e.target,sub)-owned(s,sub)) for sub in ('D','S')}
            yield replace(e,increments={**e.increments,**increments})
    def lift(module):
        def events(s):
            lost=value(s,'S.lost_material')
            for e in module.events(s[:8]):
                if e.target[5]+lost>p.s_capacity:continue
                yield replace(e,target=e.target+s[8:])
        return RuleModule(module.id,module.version,lambda s:accounted(events(s),s))
    modules=[lift(m) for m in base.modules]

    def pump_events(s):
        f=indices['D.pump_fuel'];active=float(s[2]>0 and s[7]>0)
        for direction in (1,-1):
            ed=s[3]-direction*bill
            if s[f]==(0 if direction==1 else 1) and 0<=ed<=db.maximum:
                t=change(s,{3:ed,f:1-s[f]})
                yield event(s,t,x.basal+x.charging*active,'pump.fuel_charge',
                    {'pump_charge_forward':float(direction==1),'pump_charge_reverse':float(direction==-1),
                     'pump_charging_net_bill':direction*x.fuel_energy})
        if s[1]!=s[4]:return
        for mode in ('extract','donate'):
            sign=1 if mode=='extract' else -1
            k=x.basal+(x.assistance*active if x.pump_mode==mode else 0.)
            for direction in (1,-1):
                ed,es=s[3]+direction*sign*du,s[6]-direction*sign*su
                if s[f]!=(1 if direction==1 else 0) or not(0<=ed<=db.maximum and 0<=es<=sb.maximum):continue
                t=change(s,{3:ed,6:es,f:1-s[f]})
                yield event(s,t,k,'pump.'+mode,{'pump_'+mode+'_forward':float(direction==1),
                    'pump_'+mode+'_reverse':float(direction==-1),'pump_transport_D':float(direction*sign),
                    'pump_transport_S':float(-direction*sign),'pump_fuel_consumed':float(direction)})
    if x.pump:modules.append(RuleModule('funded-pump','1',lambda s:accounted(pump_events(s),s)))

    def access_events(s):
        r,a=indices['pocket.packet'],indices['S.access_device']
        t=change(s,{r:1-s[r]})
        yield event(s,t,p.packet_thermal,'access.packet_thermal')
        if p.drive:
            if not s[r]:yield event(s,t,x.local_source,'access.source',{'local_source_input':2.},work=2.,thermal=False)
            else:yield event(s,t,p.packet_export,'access.export',{'local_source_export':2.},work=-2.,thermal=False)
        # A maintained physical access device can connect to this source after
        # S leaves the pocket; without it only a slow local route is available.
        k=x.basal*float(s[4]==4)+x.access_strength*s[a]*s[5]
        for direction in (1,-1):
            es=s[6]+direction*su
            if s[r]!=(1 if direction==1 else 0) or not 0<=es<=sb.maximum:continue
            t=change(s,{6:es,r:1-s[r]})
            yield event(s,t,k,'access.capture',{'access_capture_net':float(direction),
                'access_capture_forward':float(direction==1),'access_capture_reverse':float(direction==-1)})
        if s[4]==4 and s[5]:
            for direction in (1,-1):
                es=s[6]-direction*su
                if s[a]!=(0 if direction==1 else 1) or not 0<=es<=sb.maximum:continue
                t=change(s,{6:es,a:1-s[a]})
                yield event(s,t,x.enabler_build,'access.build',{'access_build_net':float(direction),
                    'access_build_forward':float(direction==1),'access_build_reverse':float(direction==-1)})
        yield event(s,change(s,{a:1-s[a]}),x.enabler_thermal,'access.thermal_assembly')
        if s[a]:
            for direction in (1,-1):
                es=s[6]-direction*su
                if 0<=es<=sb.maximum:
                    yield event(s,change(s,{6:es}),x.enabler_upkeep,'access.upkeep',
                                {'access_upkeep_net':float(direction)})
    if x.opportunity:modules.append(RuleModule('constructed-access','1',lambda s:accounted(access_events(s),s)))
    def damage(s):
        if p.drive and s[5] and not value(s,'S.lost_material'):
            t=change(s,{5:s[5]-1,indices['S.lost_material']:1})
            yield event(s,t,x.irreversible_loss*s[5],'material.irreversible_loss',{'permanent_capacity_loss':1.},thermal=False)
    if x.irreversible_loss:modules.append(RuleModule('material-sink','1',lambda s:accounted(damage(s),s)))
    observables={name:(lambda s,fn=fn:fn(s[:8])) for name,fn in base.observables.items()}
    for name,i in indices.items():observables[name]=lambda s,i=i:float(s[i])
    for sub in ('D','S'):observables[sub+'.owned_energy']=lambda s,sub=sub:float(owned(s,sub))
    subjects={k:tuple(v) for k,v in base.metadata['subjects'].items()}
    for name,i in indices.items():subjects['D' if name.startswith('D.') else 'S' if name.startswith('S.') else 'background']+=(i,)
    return replace(base,id='physical-access-pump-extensions',version='1',states=states,validate=validate,
        energy=energy,degeneracy=density,modules=tuple(modules),observables=observables,
        metadata={**base.metadata,'fields':tuple(base.metadata['fields'])+tuple(names),
            'subjects':subjects,'extension':asdict(x),'allow_transients':bool(x.irreversible_loss and p.drive),
            'scope':'physical fuel/access devices and explicit conserved-material sink; no valence or persistence reward'})


def root(world,parameters,preparation='balanced'):
    from .domination_friction import matched_roots
    base=matched_roots(parameters)['device_present']
    if preparation=='D_supplied':base=base[:3]+(d_bank(parameters).ticks(2),)+base[4:6]+(0,)+base[7:]
    if preparation not in ('balanced','D_supplied'):raise ValueError('Unknown matched preparation')
    tail=tuple(1 if name=='pocket.packet' else 0 for name in world.metadata['fields'][8:])
    result=base+tail;world.validate(result);return result
