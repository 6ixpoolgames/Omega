"""Paired, costed resource transfer composed with the existing physical world.

No extra state or immortal actuator. Native transfer is present in every arm;
the device changes symmetric kinetic coefficients, never equilibrium ratios.
"""
from dataclasses import asdict, dataclass, replace
from math import exp, isfinite, sqrt

from .contracts import RuleModule
from .domination_friction import (
    FrictionParameters, FrictionPolicy, build_world as base_world, d_bank,
    _degeneracy, _event, _replace, s_bank)


@dataclass(frozen=True)
class TransferPolicy:
    mode: str = 'passive'
    cost: float = .5
    assistance: float = .2
    basal: float = .0002
    affinity: float = 0.

    def __post_init__(self):
        if self.mode == 'bank_bath_exchange':object.__setattr__(self,'mode','sham')
        if self.mode not in ('passive', 'extract', 'cooperate', 'sham', 'ordinary'):
            raise ValueError('Unknown resource-transfer mode')
        if not isfinite(self.cost) or self.cost <= 0:
            raise ValueError('Positive handling bill required; bank capacity is checked by adapter')
        if not isfinite(self.assistance) or self.assistance < 0:
            raise ValueError('Nonnegative catalytic assistance required')
        if not isfinite(self.basal) or self.basal <= 0:
            raise ValueError('Native forward and reverse pathways must remain positive')
        if not isfinite(self.affinity) or abs(self.affinity) > 12:
            raise ValueError('Finite declared transfer affinity within [-12,12] required')


def transfer_events(state, p, policy):
    bank = d_bank(p)
    sbank=s_bank(p);sunit=sbank.ticks(1)
    unit, bill = bank.ticks(1), bank.ticks(policy.cost)
    # Contact is physical. Spatial separation blocks both directions equally.
    if state[1] != state[4]:
        return
    embodied = state[2] > 0 and state[7] > 0
    for channel in ('extract', 'cooperate'):
        coefficient = policy.basal + (policy.assistance if embodied and policy.mode == channel else 0.)
        # Forward extraction: D prepays c, receives 1; S loses 1.
        # Forward cooperation: D pays 1+c; S receives 1.
        delta_d = unit-bill if channel == 'extract' else -(unit+bill)
        delta_s = -sunit if channel == 'extract' else sunit
        for direction in (1, -1):
            ed, es = state[3]+direction*delta_d, state[6]+direction*delta_s
            if not (0 <= ed <= bank.maximum and 0 <= es <= sbank.maximum):
                continue
            # The pair includes a real prepayment gate. Its reverse is tested
            # against the corresponding forward source, so support is symmetric.
            forward_d = state[3] if direction == 1 else ed
            if channel == 'extract' and forward_d < bill:
                continue
            target = _replace(state, {3: ed, 6: es})
            mass = sqrt(_degeneracy(target, p)/_degeneracy(state, p))
            increments = {
                channel+'_forward': float(direction == 1),
                channel+'_reverse': float(direction == -1),
                'transfer_D': direction*delta_d*float(bank.quantum),
                'transfer_S': float(direction*delta_s*sbank.quantum),
                channel+'_gross_bill': policy.cost if direction == 1 else 0.,
                channel+'_reverse_refund': policy.cost if direction == -1 else 0.,
                channel+'_net_bill': direction*policy.cost}
            # A declared external work boundary can bias the extraction pair.
            # It is disabled in the dark along with the native external source.
            # Work is energy per reaction, not an uncharged direction multiplier.
            work = direction*policy.affinity if p.drive and channel == 'extract' else 0.
            event = _event(state, target, coefficient, p, 'transfer.'+channel,
                           mass=mass, increments={**increments,
                               'transfer_boundary_work': work})
            yield replace(event, rate=event.rate*exp(p.beta*work/2), work=work)
    # Matched hardware activity control, not a claim of equal realized flux.
    # Its reverse absorbs heat; it is a reversible thermal channel, not a
    # one-way externally powered randomizer.
    coefficient = policy.basal + (policy.assistance if embodied and policy.mode == 'sham' else 0.)
    for direction in (1, -1):
        ed = state[3]-direction*bill
        if 0 <= ed <= bank.maximum:
            target = _replace(state, {3: ed})
            mass = sqrt(_degeneracy(target, p)/_degeneracy(state, p))
            yield _event(state, target, coefficient, p, 'transfer.sham', mass=mass,
                         increments={'sham_net_bill': direction*policy.cost,
                                     'sham_gross_bill': policy.cost if direction == 1 else 0.,
                                     'sham_reverse_refund': policy.cost if direction == -1 else 0.})


def build_world(parameters=None, policy=None, max_states=12000):
    p = parameters or FrictionParameters(d_energy_capacity=3, d_energy_quantum=.25)
    policy = policy or TransferPolicy()
    if p.field_shift or p.device_role not in ('friction', 'ordinary', 'inert'):
        raise ValueError('First transfer adapter excludes a conservative device field')
    bank = d_bank(p)
    bank.ticks(policy.cost)
    if bank.ticks(1+policy.cost) > bank.maximum:
        raise ValueError('Bank must accommodate cooperative payment 1+cost')
    p = replace(p, device_role='ordinary' if policy.mode == 'ordinary' else 'inert')
    world = base_world(p, FrictionPolicy(phi=0, cost=0), max_states=max_states)
    observations = dict(world.observables)
    observations['transfer_enabled'] = lambda s: float(s[2] > 0 and s[7] > 0 and s[1] == s[4])
    def owned_energy(s, subject):
        return (bank.energy(s[3])+s[2]+s[7]-(s[1] == 2)) if subject == 'D' else (
            s_bank(p).energy(s[6])+s[5]-(s[4] == 2))
    for subject in ('D', 'S'):
        observations[subject+'.owned_energy'] = lambda s, subject=subject: float(owned_energy(s, subject))
    def accounted(module):
        def events(s):
            for event in module.events(s):
                # Query counters only. No extra physical coordinate or outcome.
                changes = {subject+'_energy_by_family.'+event.family:
                           float(owned_energy(event.target, subject)-owned_energy(s, subject))
                           for subject in ('D', 'S')}
                yield replace(event, increments={**event.increments, **changes})
        return replace(module, events=events)
    modules = world.modules+(RuleModule('resource-transfer', '1',
                       lambda s: transfer_events(s, p, policy)),)
    return replace(world, id='paired-resource-transfer', version='1', observables=observations,
                   modules=tuple(accounted(m) for m in modules),
                   metadata={**world.metadata, 'transfer_policy': asdict(policy),
                       'transfer_scope': 'costed direct stored-resource transfer, not population or packet sequestration',
                       'transfer_thermodynamics': 'all added reactions paired and enabled in dark detailed-balance check',
                       'sham_scope': 'same catalytic coefficient, not equal realized fuel or event count',
                       'mode_label': {'extract':'reversible receiver pathway','cooperate':'reversible donor pathway',
                                      'sham':'reversible bank-bath exchange'}.get(policy.mode,policy.mode),
                       'bill_scope': 'handling loss dissipates to bath; reverse pathway restores it from bath'})
