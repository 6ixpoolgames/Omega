"""Embodied interference with mobility in a shared-resource count world.

Location is a physical coarse compartment, not a moral state label. All native
chemistry and background fluctuations survive in every preparation. Active
blocking/steering is an explicitly driven, energy-spending intervention.
"""
from dataclasses import asdict, dataclass, replace
from functools import lru_cache
from itertools import product
from math import comb, exp, isfinite, lgamma

from .contracts import Event, RuleModule, WorldSpec
from .energy_grid import EnergyGrid, rational

ACCESS, BUILD, TRAP, NEUTRAL = range(4)
DISCOVERED = 4
REGIONS = {'access': (ACCESS,), 'construction': (BUILD,), 'trap': (TRAP,),
           'neutral': (NEUTRAL,), 'all_mobility': tuple(range(4))}
FIELDS = ('packet', 'D.location', 'D.apparatus', 'D.charge',
          'S.location', 'S.apparatus', 'S.charge', 'D.friction')
D_FIELDS, S_FIELDS, B_FIELDS = (1, 2, 3, 7), (4, 5, 6), (0,)


@dataclass(frozen=True)
class FrictionPolicy:
    mode: str = 'blocking'
    direction: str = 'entry'
    region: tuple[int, ...] = (ACCESS,)
    phi: float = 0.5
    cost: float = 1
    edges: tuple[tuple[int, int], ...] = ()
    steering_scope: str = 'movement_only'

    def __post_init__(self):
        if self.mode == 'driven_debit':object.__setattr__(self,'mode','sham')
        object.__setattr__(self, 'region', tuple(self.region))
        object.__setattr__(self, 'edges', tuple(sorted(tuple(x) for x in self.edges)))
        if self.mode not in ('blocking', 'steering', 'sham'):
            raise ValueError('Blocking, steering or physical sham required')
        if self.steering_scope not in ('native_events', 'movement_only'):
            raise ValueError('Unknown steering destination scope')
        if self.direction not in ('entry', 'exit', 'all'):
            raise ValueError('Unknown direction')
        if (not self.region or len(set(self.region)) != len(self.region)
                or any(type(x) is not int or x not in range(5) for x in self.region)):
            raise ValueError('A nonempty unique set of physical locations is required')
        if not isfinite(self.phi) or not 0 <= self.phi <= 1:
            raise ValueError('Friction strength must lie in [0,1]')
        if rational(self.cost) < 0:
            raise ValueError('Cost is a nonnegative physical energy')
        object.__setattr__(self, 'cost', float(self.cost))
        if (len(set(self.edges)) != len(self.edges) or any(
                len(x) != 2 or any(type(y) is not int or y not in range(5) for y in x)
                or x[0] == x[1] for x in self.edges)):
            raise ValueError('Explicit targets must be unique directed mobility edges')
        if self.direction == 'all' and tuple(sorted(self.region)) not in (tuple(range(4)), tuple(range(5))):
            raise ValueError('All mobility requires all locations')
        if len(self.region) == 5 and self.direction != 'all':
            raise ValueError('An all-location region requires all-mobility blocking')

    def targets(self, source, target):
        if self.edges:
            return (source, target) in self.edges
        if self.direction == 'all':
            return True
        if self.direction == 'entry':
            return source not in self.region and target in self.region
        return source in self.region and target not in self.region


@dataclass(frozen=True)
class FrictionParameters:
    beta: float = 1.0
    d_capacity: int = 1
    s_capacity: int = 1
    charge_capacity: int = 2
    supply: float = 0.12
    kappa: float = 0.0
    drive: bool = True
    mobility: float = 0.12
    trap_mobility: float = 0.012
    capture_basal: float = 0.008
    capture_assistance: float = 0.12
    construction: float = 0.04
    construction_assistance: float = 0.5
    thermal_assembly: float = 0.002
    thermal_charge: float = 0.004
    upkeep: float = 0.012
    device_construction: float = 0.02
    device_wear: float = 0.003
    device_upkeep: float = 0.008
    packet_thermal: float = 0.002
    packet_export: float = 0.015
    field_location: int = 0
    field_shift: float = 0.
    d_energy_capacity: float | None = None
    d_energy_quantum: float = 1.
    fractional_bath: float = .02
    device_role: str = 'friction'
    discovery: bool = False
    discovery_basal: float = .0002
    discovery_rate: float = .05
    opportunity_yield: float = 1.
    s_energy_capacity: float | None = None
    s_energy_quantum: float = 1.
    field_locations: tuple[int, ...] = ()

    def __post_init__(self):
        for name in ('d_capacity', 's_capacity', 'charge_capacity'):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError('Positive integer capacities required')
        if type(self.drive) is not bool or type(self.discovery) is not bool:
            raise ValueError('drive must be boolean')
        for name, value in asdict(self).items():
            if name in ('d_capacity', 's_capacity', 'charge_capacity', 'drive', 'field_location',
                        'd_energy_capacity', 'd_energy_quantum', 's_energy_capacity',
                        's_energy_quantum', 'field_locations', 'device_role', 'discovery'):
                continue
            if name == 'field_shift':
                if not isfinite(value):
                    raise ValueError('Finite field energy required')
                continue
            if not isfinite(value) or value < 0 or (name not in ('kappa', 'opportunity_yield') and value == 0):
                raise ValueError(f'Invalid positive physical coefficient: {name}')
        if type(self.field_location) is not int or self.field_location not in range(5 if self.discovery else 4):
            raise ValueError('Physical field location required')
        if self.device_role not in ('friction', 'ordinary', 'inert'):
            raise ValueError('Unknown physical role for device material')
        d_bank(self).ticks(1)
        s_bank(self).ticks(1)
        object.__setattr__(self,'field_locations',tuple(self.field_locations))
        if len(set(self.field_locations))!=len(self.field_locations) or any(
                type(x) is not int or x not in range(5 if self.discovery else 4) for x in self.field_locations):
            raise ValueError('Distinct physical field locations required')


def d_bank(p):
    return _bank(p.charge_capacity if p.d_energy_capacity is None else p.d_energy_capacity,
                 p.d_energy_quantum)


def s_bank(p):
    return _bank(p.charge_capacity if p.s_energy_capacity is None else p.s_energy_capacity,
                 p.s_energy_quantum)


def field_energy(state,p):
    return p.field_shift*state[7]*(state[4] in (p.field_locations or (p.field_location,)))


@lru_cache(maxsize=128)
def _bank(capacity, quantum=1):
    return EnergyGrid(capacity, quantum)


@lru_cache(maxsize=4096)
def charge_weight(capacity, energy):
    if float(capacity).is_integer() and float(energy).is_integer():
        return float(comb(int(capacity), int(energy)))
    return exp(lgamma(float(capacity)+1)-lgamma(energy+1)-lgamma(float(capacity)-energy+1))


def energy(state):
    r, ld, ad, ed, ls, ass, es, f = state
    return float(2*r + ad + ed + ass + es + f - (ld == TRAP) - (ls == TRAP))


def physical_energy(state, parameters):
    # A device-supported conservative potential. Formation/loss of the device
    # changes this energy too: it is never an uncharged instantaneous field.
    return (energy(state)-state[3]+d_bank(parameters).energy(state[3])
            -state[6]+s_bank(parameters).energy(state[6])+field_energy(state,parameters))


def projection(state, fields):
    return tuple(state[i] for i in fields)


def _degeneracy(s, p):
    return (comb(p.d_capacity, s[2])*comb(p.s_capacity, s[5])
            *charge_weight(d_bank(p).capacity, d_bank(p).energy(s[3]))
            *charge_weight(s_bank(p).capacity,s_bank(p).energy(s[6])))


def _event(s, target, coefficient, p, family, mass=1., increments=None, work=0.,
           thermal=True):
    delta = physical_energy(target, p)-physical_energy(s, p)
    rate = coefficient*mass*(exp(-p.beta*delta/2) if thermal else 1.)
    return Event(family, family, target, rate,
                 tuple(i for i, (a, b) in enumerate(zip(s, target)) if a != b),
                 work, increments or {})


def _replace(s, changes):
    values = list(s)
    for i, x in changes.items():
        values[i] = x
    return tuple(values)


def _background(s, p):
    r = s[0]
    target = _replace(s, {0: 1-r})
    yield _event(s, target, p.packet_thermal, p, 'packet_thermal')
    if p.drive and not r:
        yield _event(s, target, p.supply, p, 'source', thermal=False,
                     work=2., increments={'accepted_work': 2.})
    if p.drive and r:
        yield _event(s, target, p.packet_export, p, 'export', thermal=False, work=-2.)


def _chemistry(s, p):
    for name, li, ai, ei, cap in (('D', 1, 2, 3, p.d_capacity),
                                  ('S', 4, 5, 6, p.s_capacity)):
        bank = d_bank(p) if name == 'D' else s_bank(p)
        loc, a, raw = s[li], s[ai], s[ei]
        e = bank.energy(raw)
        spent = float(bank.capacity)-e
        unit = bank.ticks(1)
        can_spend, can_charge = raw >= unit, raw+unit <= bank.maximum
        if loc == ACCESS or (name == 'S' and p.discovery and loc == DISCOVERED):
            boost = (1+p.kappa*s[5]) if name == 'D' else 1.
            auxiliary = s[7] if name == 'D' and p.device_role == 'ordinary' else 0
            k = p.capture_basal+p.capture_assistance*(a+auxiliary)*boost
            if loc == DISCOVERED:
                k *= p.opportunity_yield
            if s[0] and can_charge:
                yield _event(s, _replace(s, {0: 0, ei: raw+unit}), k, p, name+'.capture',
                             spent, {'capture_'+name: 1., 'net_capture_'+name: 1.})
            if not s[0] and can_spend:
                yield _event(s, _replace(s, {0: 1, ei: raw-unit}), k, p, name+'.capture',
                             e, {'reverse_capture_'+name: 1., 'net_capture_'+name: -1.})
        if loc == BUILD:
            # Existing spectator apparatus catalyses both directions equally.
            if a < cap and can_spend:
                k = p.construction*(1+p.construction_assistance*a)
                yield _event(s, _replace(s, {ai: a+1, ei: raw-unit}), k, p, name+'.build',
                             (cap-a)*e, {'build_'+name: 1., 'build_fuel_'+name: 1.})
            if a and can_charge:
                k = p.construction*(1+p.construction_assistance*(a-1))
                yield _event(s, _replace(s, {ai: a-1, ei: raw+unit}), k, p, name+'.build',
                             a*spent, {'unbuild_'+name: 1., 'build_fuel_'+name: -1.})
        if a < cap:
            yield _event(s, _replace(s, {ai: a+1}), p.thermal_assembly, p,
                         name+'.assembly', cap-a, {'thermal_birth_'+name: 1.})
        if a:
            yield _event(s, _replace(s, {ai: a-1}), p.thermal_assembly, p,
                         name+'.assembly', a, {'thermal_loss_'+name: 1.})
        for delta, mass, possible in ((1, spent, can_charge), (-1, e, can_spend)):
            if possible:
                target = _replace(s, {ei: raw+delta*unit})
                yield _event(s, target, p.thermal_charge, p, name+'.charge', mass)
                if a:
                    yield _event(s, target, p.upkeep*a, p, name+'.upkeep', mass,
                                 {'upkeep_'+name: float(-delta)})
        if unit > 1:
            for step in (-1, 1):
                if 0 <= raw+step <= bank.maximum:
                    target = _replace(s, {ei: raw+step})
                    # Reversible subquantum bath exchange: common in every arm.
                    density = (charge_weight(bank.capacity, bank.energy(raw+step))
                               /charge_weight(bank.capacity, e))**.5
                    k = p.fractional_bath*(.1/float(bank.quantum))**2
                    yield _event(s, target, k, p, name+'.fractional_bath', density)
    bank = d_bank(p)
    unit = bank.ticks(1)
    if s[1] == BUILD:
        if not s[7] and s[3] >= unit:
            yield _event(s, _replace(s, {7: 1, 3: s[3]-unit}), p.device_construction,
                         p, 'D.device_build', bank.energy(s[3]), {'device_build': 1.})
        if s[7] and s[3]+unit <= bank.maximum:
            yield _event(s, _replace(s, {7: 0, 3: s[3]+unit}), p.device_construction,
                         p, 'D.device_build', float(bank.capacity)-bank.energy(s[3]), {'device_unbuild': 1.})
    yield _event(s, _replace(s, {7: 1-s[7]}), p.device_wear, p, 'D.device_thermal')
    if s[7]:
        for delta, mass in ((1, float(bank.capacity)-bank.energy(s[3])), (-1, bank.energy(s[3]))):
            if 0 <= s[3]+delta*unit <= bank.maximum:
                yield _event(s, _replace(s, {3: s[3]+delta*unit}), p.device_upkeep, p,
                             'D.device_upkeep', mass, {'device_upkeep': float(-delta)})
    if p.discovery and s[4] in (TRAP, DISCOVERED):
        forward = s[4] == TRAP
        destination = DISCOVERED if forward else TRAP
        yield _event(s, _replace(s, {4: destination}), p.discovery_basal, p,
                     'S.discovery_basal', increments={'discoveries_basal': float(forward)})
        sbank=s_bank(p);sunit=sbank.ticks(1);se=sbank.energy(s[6])
        if s[5] and (s[6] >= sunit if forward else s[6]+sunit <= sbank.maximum):
            delta = -1 if forward else 1
            mass = se if forward else float(sbank.capacity)-se
            yield _event(s, _replace(s, {4: destination, 6: s[6]+delta*sunit}),
                         p.discovery_rate*s[5], p, 'S.discovery_paid', mass,
                         {'discoveries_paid': float(forward), 'discovery_fuel': float(-delta)})


def _mobility_events(s, p, li, name):
    if s[li] == DISCOVERED:
        return
    for destination in range(4):
        if destination == s[li]:
            continue
        k = p.trap_mobility if TRAP in (destination, s[li]) else p.mobility
        yield _event(s, _replace(s, {li: destination}), k, p, name+'.move')


def _mobility(s, p, policy):
    yield from _mobility_events(s, p, 1, 'D')
    # A confinement region may have no internal spatial exit. Its physically
    # available local chemistry supplies actual alternative outcomes, rather
    # than inventing self-events or silently changing steering into blocking.
    options = list(_mobility_events(s, p, 4, 'S')) + [
        e for e in _chemistry(s, p) if e.family.startswith('S.')]
    def targetted(event):
        return event.target[4] != s[4] and policy.targets(s[4], event.target[4])
    bill = d_bank(p).ticks(policy.cost)
    actual_cost = float(bill*d_bank(p).quantum)
    active = (p.device_role == 'friction' and policy.phi > 0 and s[7] > 0
              and s[2] > 0 and s[3] >= bill)
    targeted = [e for e in options if targetted(e)]
    if not active or not targeted:
        yield from options
        return
    if policy.mode == 'sham':
        yield from options
        if bill:
            yield _event(s, _replace(s, {3: s[3]-bill}),
                         policy.phi*sum(e.rate for e in targeted), p, 'friction.sham',
                         thermal=False, increments={'sham_attempt': 1., 'friction_fuel': actual_cost})
        return
    alternatives = [e for e in options if not targetted(e) and (
        policy.steering_scope == 'native_events' or e.family == 'S.move')]
    if policy.mode == 'steering' and not alternatives:
        raise ValueError('No physical exit available for steering')
    for event in options:
        phi = policy.phi if event in targeted else 0.
        if phi < 1:
            yield Event(event.rule_id, event.family, event.target, event.rate*(1-phi),
                        event.support, event.work, event.increments)
        if not phi:
            continue
        diverted = phi*event.rate
        if policy.mode == 'blocking':
            if bill:
                target = _replace(s, {3: s[3]-bill})
                yield _event(s, target, diverted, p, 'friction.block', thermal=False,
                             increments={'blocked_attempt': 1.,
                                         'friction_fuel': actual_cost})
            # A zero-cost rejected attempt changes no physical state. Its rate
            # is an analysis query, never an entropy-producing event.
        else:
            total = sum(e.rate for e in alternatives)
            for alternative in alternatives:
                target = _replace(alternative.target, {3: s[3]-bill})
                yield _event(s, target, diverted*alternative.rate/total, p,
                             'friction.steer', thermal=False,
                             increments={**alternative.increments, 'redirected_attempt': 1.,
                                         'friction_fuel': actual_cost})


def suppressed_rate(state, parameters, policy):
    """Counterfactual suppressed/redirected attempts, query-side only."""
    if parameters.device_role != 'friction' or policy.mode == 'sham':
        return 0.
    if not (state[7] and state[2] and state[3] >= d_bank(parameters).ticks(policy.cost)):
        return 0.
    options = list(_mobility_events(state, parameters, 4, 'S')) + [
        e for e in _chemistry(state, parameters) if e.family.startswith('S.')]
    return policy.phi*sum(e.rate for e in options if e.target[4] != state[4]
                          and policy.targets(state[4], e.target[4]))


def build_world(parameters=None, policy=None, max_states=4000):
    p, policy = parameters or FrictionParameters(), policy or FrictionPolicy()
    bank = d_bank(p)
    bill = bank.ticks(policy.cost)
    if bill > bank.maximum:
        raise ValueError('Bill exceeds storage capacity; this would be an inactive-cost arm')
    s_locations = 5 if p.discovery else 4
    if any(location >= s_locations for location in policy.region) or any(
            max(edge) >= s_locations for edge in policy.edges):
        raise ValueError('Policy targets a location absent from the physical world')
    sbank=s_bank(p)
    count = 2*4*s_locations*(p.d_capacity+1)*(p.s_capacity+1)*(bank.maximum+1)*(sbank.maximum+1)*2
    if count > max_states:
        raise RuntimeError('Physical state cap exceeded; no inventory was truncated')
    states = tuple(product(range(2), range(4), range(p.d_capacity+1),
                           range(bank.maximum+1), range(s_locations), range(p.s_capacity+1),
                           range(sbank.maximum+1), range(2)))
    state_set = frozenset(states)

    def validate(state):
        if (not isinstance(state, tuple) or any(type(x) is not int for x in state)
                or state not in state_set):
            raise ValueError('Invalid full physical state')

    observables = {name: (lambda s, i=i: float(s[i])) for i, name in enumerate(FIELDS)}
    observables['D.charge'] = lambda s: bank.energy(s[3])
    observables['S.charge'] = lambda s: sbank.energy(s[6])
    observables['S.discovered'] = lambda s: float(s[4] == DISCOVERED)
    for name, li, ai in (('D', 1, 2), ('S', 4, 5)):
        for region, location in (('access', ACCESS), ('construction', BUILD), ('trap', TRAP)):
            observables[name+'.'+region] = lambda s, i=li, r=location: float(s[i] == r)
        observables[name+'.functional'] = lambda s, i=ai: float(s[i] > 0)
    observables['friction_enabled'] = lambda s: float(s[2] > 0 and s[7] > 0
                       and s[3] >= bill and policy.phi > 0 and p.device_role == 'friction')
    observables['suppressed_rate'] = lambda s: suppressed_rate(s, p, policy)
    observables['S_event_rate'] = lambda s: sum(
        e.rate for m in (_mobility(s, p, policy), _background(s, p)) for e in m
        if projection(e.target, S_FIELDS) != projection(s, S_FIELDS))
    def owned(s,subject):
        if subject=='D':return bank.energy(s[3])+s[2]+s[7]-(s[1]==TRAP)
        return sbank.energy(s[6])+s[5]-(s[4]==TRAP)+field_energy(s,p)
    for subject in ('D','S'):
        observables[subject+'.owned_energy']=lambda s,sub=subject:float(owned(s,sub))
    def account(events,s):
        for event in events:
            ledger={sub+'_energy_by_family.'+event.family:float(owned(event.target,sub)-owned(s,sub))
                    for sub in ('D','S')}
            yield replace(event,increments={**event.increments,**ledger})
    return WorldSpec('domination-friction-count-world', '3', states, validate,
                     lambda s: physical_energy(s, p),
                     observables,
                     (RuleModule('background', '1', lambda s: account(_background(s, p),s)),
                      RuleModule('chemistry', '1', lambda s: account((
                          e for e in _chemistry(s, p) if e.family.startswith('D.')),s)),
                      RuleModule('mobility-friction', '1', lambda s: account(_mobility(s, p, policy),s))),
                     {'fields': FIELDS, 'parameters': asdict(p), 'policy': asdict(policy),
                      'subjects': {'D': D_FIELDS, 'S': S_FIELDS, 'background': B_FIELDS},
                      'sham_physics': 'driven one-way bank debit (legacy mode name sham)',
                      'grain': 'full physical compartment/count state',
                      'constraint_scope': 'targets S location changes, including discovery; steering alternatives are actual S events',
                      'friction_physics': 'rejected or redirected attempts spend D fuel; no work reservoir',
                      'steering_match': 'total S state-changing exit rate at the same full physical state only',
                      'energies': 'packet2, apparatus1, physical bank energy, device1, trap location -1',
                      'fractional_bank_scope': 'exact energy ticks; gamma-binomial phenomenological density; common reversible fractional bath',
                      'discovery_scope': 'costed physical route to resource pocket, not a learned or shared permanent unlock',
                      'device_swap_scope': 'same material/energy bank; auxiliary capture replaces friction role, not a removal procedure',
                      'thermal_pairs': 'mass action times exp(-beta delta energy/2)',
                      'active_friction': 'device AND working D apparatus AND affordable bill',
                      'gas_scope': 'unassembled count preparation, not microscopic gas',
                      'no_suffering_variable': True},
                     degeneracy=lambda s: _degeneracy(s, p))


def matched_roots(parameters=None):
    """All H=6 with identical shared packet and S. No excision action asserted."""
    p=parameters or FrictionParameters();bank=d_bank(p);sb=s_bank(p).ticks(1)
    return {'device_present': (1, ACCESS, 1, 0, ACCESS, 1, sb, 1),
            'ordinary_preparation': (1, ACCESS, 1, bank.ticks(1), ACCESS, 1, sb, 0),
            'unassembled_preparation': (1, NEUTRAL, 0, bank.ticks(2), ACCESS, 1, sb, 0)}
