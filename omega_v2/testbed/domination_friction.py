"""Embodied interference with mobility in a shared-resource count world.

Location is a physical coarse compartment, not a moral state label. All native
chemistry and background fluctuations survive in every preparation. Active
blocking/steering is an explicitly driven, energy-spending intervention.
"""
from dataclasses import asdict, dataclass
from itertools import product
from math import comb, exp, isfinite

from .contracts import Event, RuleModule, WorldSpec

ACCESS, BUILD, TRAP, NEUTRAL = range(4)
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
    cost: int = 1

    def __post_init__(self):
        object.__setattr__(self, 'region', tuple(self.region))
        if self.mode not in ('blocking', 'steering'):
            raise ValueError('Blocking or steering required')
        if self.direction not in ('entry', 'exit', 'all'):
            raise ValueError('Unknown direction')
        if (not self.region or len(set(self.region)) != len(self.region)
                or any(type(x) is not int or x not in range(4) for x in self.region)):
            raise ValueError('A nonempty unique set of physical locations is required')
        if not isfinite(self.phi) or not 0 <= self.phi <= 1:
            raise ValueError('Friction strength must lie in [0,1]')
        if type(self.cost) is not int or self.cost < 0:
            raise ValueError('Cost is a nonnegative integer number of fuel quanta')
        if self.direction == 'all' and (len(self.region) != 4 or self.mode == 'steering'):
            raise ValueError('This adapter implements all-mobility blocking only')
        if len(self.region) == 4 and self.direction != 'all':
            raise ValueError('An all-location region requires all-mobility blocking')

    def targets(self, source, target):
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

    def __post_init__(self):
        for name in ('d_capacity', 's_capacity', 'charge_capacity'):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError('Positive integer capacities required')
        if type(self.drive) is not bool:
            raise ValueError('drive must be boolean')
        for name, value in asdict(self).items():
            if name in ('d_capacity', 's_capacity', 'charge_capacity', 'drive'):
                continue
            if not isfinite(value) or value < 0 or (name != 'kappa' and value == 0):
                raise ValueError(f'Invalid positive physical coefficient: {name}')


def energy(state):
    r, ld, ad, ed, ls, ass, es, f = state
    return float(2*r + ad + ed + ass + es + f - (ld == TRAP) - (ls == TRAP))


def projection(state, fields):
    return tuple(state[i] for i in fields)


def _degeneracy(s, p):
    return comb(p.d_capacity, s[2])*comb(p.s_capacity, s[5])*comb(
        p.charge_capacity, s[3])*comb(p.charge_capacity, s[6])


def _event(s, target, coefficient, p, family, mass=1., increments=None, work=0.,
           thermal=True):
    delta = energy(target)-energy(s)
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
        loc, a, e = s[li], s[ai], s[ei]
        spent = p.charge_capacity-e
        if loc == ACCESS:
            boost = (1+p.kappa*s[5]) if name == 'D' else 1.
            k = p.capture_basal+p.capture_assistance*a*boost
            if s[0] and spent:
                yield _event(s, _replace(s, {0: 0, ei: e+1}), k, p, name+'.capture',
                             spent, {'capture_'+name: 1., 'net_capture_'+name: 1.})
            if not s[0] and e:
                yield _event(s, _replace(s, {0: 1, ei: e-1}), k, p, name+'.capture',
                             e, {'reverse_capture_'+name: 1., 'net_capture_'+name: -1.})
        if loc == BUILD:
            # Existing spectator apparatus catalyses both directions equally.
            if a < cap and e:
                k = p.construction*(1+p.construction_assistance*a)
                yield _event(s, _replace(s, {ai: a+1, ei: e-1}), k, p, name+'.build',
                             (cap-a)*e, {'build_'+name: 1., 'build_fuel_'+name: 1.})
            if a and spent:
                k = p.construction*(1+p.construction_assistance*(a-1))
                yield _event(s, _replace(s, {ai: a-1, ei: e+1}), k, p, name+'.build',
                             a*spent, {'unbuild_'+name: 1., 'build_fuel_'+name: -1.})
        if a < cap:
            yield _event(s, _replace(s, {ai: a+1}), p.thermal_assembly, p,
                         name+'.assembly', cap-a, {'thermal_birth_'+name: 1.})
        if a:
            yield _event(s, _replace(s, {ai: a-1}), p.thermal_assembly, p,
                         name+'.assembly', a, {'thermal_loss_'+name: 1.})
        for delta, mass in ((1, spent), (-1, e)):
            if mass:
                target = _replace(s, {ei: e+delta})
                yield _event(s, target, p.thermal_charge, p, name+'.charge', mass)
                if a:
                    yield _event(s, target, p.upkeep*a, p, name+'.upkeep', mass,
                                 {'upkeep_'+name: float(-delta)})
    if s[1] == BUILD:
        if not s[7] and s[3]:
            yield _event(s, _replace(s, {7: 1, 3: s[3]-1}), p.device_construction,
                         p, 'D.device_build', s[3], {'device_build': 1.})
        if s[7] and s[3] < p.charge_capacity:
            yield _event(s, _replace(s, {7: 0, 3: s[3]+1}), p.device_construction,
                         p, 'D.device_build', p.charge_capacity-s[3], {'device_unbuild': 1.})
    yield _event(s, _replace(s, {7: 1-s[7]}), p.device_wear, p, 'D.device_thermal')
    if s[7]:
        for delta, mass in ((1, p.charge_capacity-s[3]), (-1, s[3])):
            if mass:
                yield _event(s, _replace(s, {3: s[3]+delta}), p.device_upkeep, p,
                             'D.device_upkeep', mass, {'device_upkeep': float(-delta)})


def _mobility_events(s, p, li, name):
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
        return event.family == 'S.move' and policy.targets(s[4], event.target[4])
    active = policy.phi > 0 and s[7] > 0 and s[2] > 0 and s[3] >= policy.cost
    targeted = [e for e in options if targetted(e)]
    if not active or not targeted:
        yield from options
        return
    alternatives = [e for e in options if not targetted(e)]
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
            if policy.cost:
                target = _replace(s, {3: s[3]-policy.cost})
                yield _event(s, target, diverted, p, 'friction.block', thermal=False,
                             increments={'blocked_attempt': 1.,
                                         'friction_fuel': float(policy.cost)})
            # A zero-cost rejected attempt changes no physical state. Its rate
            # is an analysis query, never an entropy-producing event.
        else:
            total = sum(e.rate for e in alternatives)
            for alternative in alternatives:
                target = _replace(alternative.target, {3: s[3]-policy.cost})
                yield _event(s, target, diverted*alternative.rate/total, p,
                             'friction.steer', thermal=False,
                             increments={**alternative.increments, 'redirected_attempt': 1.,
                                         'friction_fuel': float(policy.cost)})


def suppressed_rate(state, parameters, policy):
    """Counterfactual suppressed/redirected attempts, query-side only."""
    if not (state[7] and state[2] and state[3] >= policy.cost):
        return 0.
    return policy.phi*sum(e.rate for e in _mobility_events(state, parameters, 4, 'S')
                          if policy.targets(state[4], e.target[4]))


def build_world(parameters=None, policy=None, max_states=4000):
    p, policy = parameters or FrictionParameters(), policy or FrictionPolicy()
    if policy.cost > p.charge_capacity:
        raise ValueError('Bill exceeds storage capacity; this would be an inactive-cost arm')
    count = 2*16*(p.d_capacity+1)*(p.s_capacity+1)*(p.charge_capacity+1)**2*2
    if count > max_states:
        raise RuntimeError('Physical state cap exceeded; no inventory was truncated')
    states = tuple(product(range(2), range(4), range(p.d_capacity+1),
                           range(p.charge_capacity+1), range(4), range(p.s_capacity+1),
                           range(p.charge_capacity+1), range(2)))
    state_set = frozenset(states)

    def validate(state):
        if (not isinstance(state, tuple) or any(type(x) is not int for x in state)
                or state not in state_set):
            raise ValueError('Invalid full physical state')

    observables = {name: (lambda s, i=i: float(s[i])) for i, name in enumerate(FIELDS)}
    for name, li, ai in (('D', 1, 2), ('S', 4, 5)):
        for region, location in (('access', ACCESS), ('construction', BUILD), ('trap', TRAP)):
            observables[name+'.'+region] = lambda s, i=li, r=location: float(s[i] == r)
        observables[name+'.functional'] = lambda s, i=ai: float(s[i] > 0)
    observables['friction_enabled'] = lambda s: float(s[2] > 0 and s[7] > 0
                                                     and s[3] >= policy.cost and policy.phi > 0)
    observables['suppressed_rate'] = lambda s: suppressed_rate(s, p, policy)
    return WorldSpec('domination-friction-count-world', '1', states, validate, energy,
                     observables,
                     (RuleModule('background', '1', lambda s: _background(s, p)),
                      RuleModule('chemistry', '1', lambda s: (
                          e for e in _chemistry(s, p) if e.family.startswith('D.'))),
                      RuleModule('mobility-friction', '1', lambda s: _mobility(s, p, policy))),
                     {'fields': FIELDS, 'parameters': asdict(p), 'policy': asdict(policy),
                      'subjects': {'D': D_FIELDS, 'S': S_FIELDS, 'background': B_FIELDS},
                      'grain': 'full physical compartment/count state',
                      'constraint_scope': 'targets S mobility; steering alternatives are actual S mobility/chemistry',
                      'friction_physics': 'rejected or redirected attempts spend D fuel; no work reservoir',
                      'steering_match': 'total S state-changing exit rate at the same full physical state only',
                      'energies': 'packet2, apparatus1, charge1, device1, trap location -1',
                      'thermal_pairs': 'mass action times exp(-beta delta energy/2)',
                      'active_friction': 'device AND working D apparatus AND affordable bill',
                      'gas_scope': 'unassembled count preparation, not microscopic gas',
                      'no_suffering_variable': True},
                     degeneracy=lambda s: _degeneracy(s, p))


def matched_roots():
    """All H=6 with identical shared packet and S. No excision action asserted."""
    return {'device_present': (1, ACCESS, 1, 0, ACCESS, 1, 1, 1),
            'ordinary_preparation': (1, ACCESS, 1, 1, ACCESS, 1, 1, 0),
            'unassembled_preparation': (1, NEUTRAL, 0, 2, ACCESS, 1, 1, 0)}
