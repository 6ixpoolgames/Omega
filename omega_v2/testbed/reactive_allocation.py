"""Fixed-contact two-party assay with an embodied, paid catalytic selector.

This is a count-grain adapter, not a quotient of the mobile friction world.
The common substrate includes every mode and every basal reverse channel.
Only the hardwired apparatus-to-command coupling varies between policies.
"""
from dataclasses import asdict, dataclass
from itertools import product
from math import comb, exp, isfinite, sqrt

from .contracts import Event, RuleModule, WorldSpec
from .energy_grid import EnergyGrid


MODES = ('idle', 'productive', 'extract', 'donate', 'combined')
RESPONSES = ('hold',)+MODES
# Productive and pump allocations share a single unit of catalytic capacity.
ALLOCATIONS = ((0., 0., 0.), (1., 0., 0.), (0., 1., 0.),
               (0., 0., 1.), (.5, .5, 0.))


@dataclass(frozen=True)
class AllocationParameters:
    beta: float = 1.
    drive: bool = True
    d_capacity: int = 2
    s_capacity: int = 1
    bank_capacity: float = 2.
    quantum: float = .5
    supply: float = .12
    export: float = .015
    packet_thermal: float = .002
    capture_basal: float = .008
    capture_assistance: float = .12
    productive_assistance: float = .12
    construction: float = .04
    construction_assistance: float = .5
    thermal_assembly: float = .002
    bank_thermal: float = .004
    upkeep: float = .012
    operation_leak: float = .008
    pump_basal: float = .0002
    pump_assistance: float = .4
    pump_charging: float = .08
    fuel_energy: float = .5
    switch_cost: float = .5
    command_rate: float = .08
    selector_relaxation: float = .003
    kappa: float = 0.

    def __post_init__(self):
        if type(self.drive) is not bool:
            raise ValueError('drive is a physical boundary flag')
        for key, value in asdict(self).items():
            if key in ('drive', 'd_capacity', 's_capacity'):
                continue
            if isinstance(value, bool) or not isfinite(value) or value < 0:
                raise ValueError('Invalid physical coefficient: '+key)
        if self.beta <= 0 or self.selector_relaxation <= 0 or self.pump_basal <= 0:
            raise ValueError('Positive temperature and basal relaxation required')
        if any(type(v) is not int or v < 1 for v in (self.d_capacity, self.s_capacity)):
            raise ValueError('Positive integer apparatus pools required')
        bank = EnergyGrid(self.bank_capacity, self.quantum)
        for amount in (1., self.fuel_energy, self.switch_cost):
            if amount <= 0 or not 0 < bank.ticks(amount) <= bank.maximum:
                raise ValueError('Physical bills must be positive and fit the energy grid')


@dataclass(frozen=True)
class AllocationPolicy:
    # Row a-1 is the command target at a working D units. No command at a=0.
    responses: tuple[str, ...] = ('idle', 'idle')

    def __post_init__(self):
        object.__setattr__(self, 'responses', tuple(self.responses))
        if not self.responses or any(x not in RESPONSES for x in self.responses):
            raise ValueError('One physical selector target per active apparatus count')

    @property
    def id(self):
        return '__'.join(self.responses)


def policies(capacity=2):
    """All deterministic stationary tables in this declared observation class."""
    if type(capacity) is not int or capacity < 1:
        raise ValueError('Positive controller observation capacity required')
    return tuple(AllocationPolicy(row) for row in product(RESPONSES, repeat=capacity))


def build_world(parameters=None, policy=None, max_states=12000):
    p = parameters or AllocationParameters()
    policy = policy or AllocationPolicy(('idle',)*p.d_capacity)
    if len(policy.responses) != p.d_capacity:
        raise ValueError('Controller table does not cover the physical observation')
    bank = EnergyGrid(p.bank_capacity, p.quantum)
    unit, bill, switch = bank.ticks(1), bank.ticks(p.fuel_energy), bank.ticks(p.switch_cost)
    size = 2*(p.d_capacity+1)*(p.s_capacity+1)*(bank.maximum+1)**2*2*len(MODES)
    if size > max_states:
        raise RuntimeError('Allocation state cap; inventory was not truncated')
    # packet, D apparatus, S apparatus, D bank, S bank, pump fuel, selector
    states = tuple(product(range(2), range(p.d_capacity+1), range(p.s_capacity+1),
                           range(bank.maximum+1), range(bank.maximum+1), range(2), range(len(MODES))))
    state_set = frozenset(states)

    def validate(s):
        if not isinstance(s, tuple) or s not in state_set or any(type(v) is not int for v in s):
            raise ValueError('Invalid allocation state')

    def energy(s):
        return 2*s[0]+s[1]+s[2]+bank.energy(s[3])+bank.energy(s[4])+p.fuel_energy*s[5]

    def density(s):
        return comb(p.d_capacity, s[1])*comb(p.s_capacity, s[2])

    def owned(s, party):
        return (s[1]+bank.energy(s[3])+p.fuel_energy*s[5] if party == 'D'
                else s[2]+bank.energy(s[4]))

    def changed(s, updates):
        t = list(s)
        for i, v in updates.items():
            t[i] = v
        return tuple(t)

    def event(s, t, k, family, increments=None, work=0., thermal=True):
        rate = k*sqrt(density(t)/density(s))
        if thermal:
            rate *= exp(-p.beta*(energy(t)-energy(s)-work)/2)
        counters = {sub+'_energy_by_family.'+family: float(owned(t, sub)-owned(s, sub))
                    for sub in ('D', 'S')}
        return Event(family, family, t, rate,
                     tuple(i for i, (a, b) in enumerate(zip(s, t)) if a != b),
                     work, {**counters, **(increments or {})})

    def background(s):
        t = changed(s, {0: 1-s[0]})
        yield event(s, t, p.packet_thermal, 'background.thermal')
        if p.drive:
            yield event(s, t, p.supply if not s[0] else p.export,
                        'background.source' if not s[0] else 'background.export',
                        work=2. if not s[0] else -2., thermal=False)

    def chemistry(s):
        prod, _, _ = ALLOCATIONS[s[6]]
        for party, ai, ei, cap in (('D', 1, 3, p.d_capacity), ('S', 2, 4, p.s_capacity)):
            a, charge = s[ai], s[ei]
            # All catalytic factors are invariant over the corresponding pair.
            k = p.capture_basal+p.capture_assistance*a
            if party == 'D':
                k += p.productive_assistance*a*prod
                k *= 1+p.kappa*s[2]
            for direction in (1, -1):
                target_charge = charge+direction*unit
                if s[0] == (1 if direction == 1 else 0) and 0 <= target_charge <= bank.maximum:
                    yield event(s, changed(s, {0: 1-s[0], ei: target_charge}), k,
                                party+'.capture', {party+'_capture_net': float(direction)})
                target_a, target_charge = a+direction, charge-direction*unit
                if 0 <= target_a <= cap and 0 <= target_charge <= bank.maximum:
                    # The edge's lower inventory supplies assistance; new products
                    # cannot retroactively catalyse their own birth.
                    lower = min(a, target_a)
                    k_build = p.construction*(1+p.construction_assistance*lower)
                    yield event(s, changed(s, {ai: target_a, ei: target_charge}), k_build,
                                party+'.build', {party+'_build_net': float(direction)})
                if 0 <= a+direction <= cap:
                    yield event(s, changed(s, {ai: a+direction}), p.thermal_assembly,
                                party+'.thermal_assembly')
                target_charge = charge+direction
                if 0 <= target_charge <= bank.maximum:
                    # A declared native fractional-bank bath, present in all arms.
                    yield event(s, changed(s, {ei: target_charge}), p.bank_thermal+p.upkeep*a,
                                party+'.bank_bath')
                    if party == 'D' and s[6] != 0:
                        yield event(s, changed(s, {ei: target_charge}), p.operation_leak*a,
                                    'D.operation_leak')

    def pump(s):
        _, extract, donate = ALLOCATIONS[s[6]]
        for direction in (1, -1):
            charge = s[3]-direction*bill
            if s[5] == (0 if direction == 1 else 1) and 0 <= charge <= bank.maximum:
                yield event(s, changed(s, {3: charge, 5: 1-s[5]}),
                            p.pump_basal+p.pump_charging*s[1]*(extract+donate), 'pump.charge',
                            {'pump_charge_net_bill': direction*p.fuel_energy})
        for name, sign, allocation in (('extract', 1, extract), ('donate', -1, donate)):
            for direction in (1, -1):
                d, v = s[3]+sign*direction*unit, s[4]-sign*direction*unit
                if s[5] == (1 if direction == 1 else 0) and 0 <= d <= bank.maximum and 0 <= v <= bank.maximum:
                    yield event(s, changed(s, {3: d, 4: v, 5: 1-s[5]}),
                                p.pump_basal+p.pump_assistance*s[1]*allocation, 'pump.'+name,
                                {'pump_transport_D': float(sign*direction),
                                 'pump_transport_S': float(-sign*direction),
                                 'pump_fuel_consumed': float(direction),
                                 'pump_forward': float(direction == 1),
                                 'pump_reverse': float(direction == -1)})

    def selector(s):
        # Always-present autonomous relaxation prevents immortal frozen selectors.
        for target_mode in range(len(MODES)):
            if target_mode != s[6]:
                yield event(s, changed(s, {6: target_mode}), p.selector_relaxation/(len(MODES)-1),
                            'selector.relaxation')
        if not s[1]:
            return
        response = policy.responses[s[1]-1]
        if response == 'hold':
            return
        target_mode = MODES.index(response)
        for other_mode in range(len(MODES)):
            if other_mode == target_mode:
                continue
            # Same apparatus observation at both endpoints, including the true
            # reverse. Fuel is spent on a command and returned on its reverse.
            for direction in (1, -1):
                source_mode, dest = ((other_mode, target_mode) if direction == 1
                                     else (target_mode, other_mode))
                charge = s[3]-direction*switch
                if s[6] == source_mode and 0 <= charge <= bank.maximum:
                    yield event(s, changed(s, {3: charge, 6: dest}),
                                p.command_rate*s[1]/p.d_capacity, 'selector.command',
                                {'selector_forward': float(direction == 1),
                                 'selector_reverse': float(direction == -1),
                                 'selector_net_bill': direction*p.switch_cost})

    obs = {sub+'.apparatus': (lambda s, i=i: float(s[i])) for sub, i in (('D', 1), ('S', 2))}
    obs.update({sub+'.owned_energy': (lambda s, sub=sub: float(owned(s, sub))) for sub in ('D', 'S')})
    obs.update({'D.bank': lambda s: bank.energy(s[3]), 'S.bank': lambda s: bank.energy(s[4]),
                'packet': lambda s: float(s[0]), 'D.pump_fuel': lambda s: float(s[5]),
                'both_functional': lambda s: float(s[1] > 0 and s[2] > 0)})
    for i, name in enumerate(MODES):
        obs['selector.'+name] = lambda s, i=i: float(s[6] == i)
    return WorldSpec('reactive-allocation-fixed-contact', '1', states, validate, energy, obs,
        tuple(RuleModule(name, '1', fn) for name, fn in
              (('background', background), ('chemistry', chemistry), ('funded-pump', pump), ('selector', selector))),
        {'fields': ('background.packet', 'D.apparatus', 'S.apparatus', 'D.bank', 'S.bank', 'D.pump_fuel', 'D.selector'),
         'subjects': {'D': (1, 3, 5, 6), 'S': (2, 4), 'background': (0,)},
         'parameters': asdict(p), 'policy': asdict(policy), 'policy_id': policy.id,
         'observation': 'local working D apparatus count; no command at zero',
         'policy_count': len(RESPONSES)**p.d_capacity,
         'scope': 'fixed contact count assay, not a reduction of the spatial friction model; apparatus channels, not certified valuers',
         'sensing': 'direct apparatus-dependent reaction coupling; no remote observation or abstract action events',
         'action_label_entropy': False}, density)


def root(world, parameters=None):
    p = parameters or AllocationParameters()
    bank = EnergyGrid(p.bank_capacity, p.quantum)
    state = (1, 1, 1, 0, bank.ticks(1), 0, 0)
    world.validate(state)
    return state
