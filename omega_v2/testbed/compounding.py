"""Resource-funded construction feedback, with damage independent of bath kinetics.

Three physical coordinates: a quantized bank, a resource packet, apparatus.
Apparatus plus precursor is conserved. No controller, identity or label entropy.
Both directions of each construction pair have the same catalytic coefficient.
"""
from dataclasses import dataclass
from itertools import product
from math import exp, isfinite

from .contracts import Event, RuleModule, WorldSpec


@dataclass(frozen=True)
class CompoundingParameters:
    capacity: int = 8
    bank_quanta: int = 8
    quantum: float = .5
    packet_energy: float = 3.
    capture_loss: float = .5
    apparatus_energy: float = 1.
    construction_cost: float = 2.
    supply_rate: float = .6
    packet_decay: float = .05
    basal_capture: float = .002
    assisted_capture: float = .1
    basal_construction: float = .0001
    assisted_construction: float = .008
    thermal_attempt: float = .00001
    damage_rate: float = .005
    starvation_damage: float = .02
    upkeep: float = .01
    bank_leak: float = .002
    beta: float = 6.

    def __post_init__(self):
        for key in ('capacity', 'bank_quanta'):
            if type(getattr(self, key)) is not int or getattr(self, key) < 1:
                raise ValueError('Positive integer inventory and bank required')
        for key, value in vars(self).items():
            if not isfinite(value) or value < 0:
                raise ValueError(f'Invalid {key}')
        if min(self.quantum, self.beta, self.basal_capture,
               self.basal_construction, self.thermal_attempt) <= 0:
            raise ValueError('Positive native basal/bath rates required')
        if not self.packet_energy > self.capture_loss >= 0:
            raise ValueError('Positive net packet yield required')
        if not self.construction_cost > self.apparatus_energy > 0:
            raise ValueError('Construction stores hardware energy and dissipates a remainder')
        for value in (self.packet_energy-self.capture_loss, self.construction_cost,
                      self.apparatus_energy):
            if abs(value/self.quantum-round(value/self.quantum)) > 1e-10:
                raise ValueError('Bills and yields must fit the fixed physical quantum')
        if self.construction_cost > self.bank_quanta*self.quantum:
            raise ValueError('Construction exceeds bank capacity')


def build_world(parameters=None, mechanism='loop'):
    p = parameters or CompoundingParameters()
    if mechanism not in ('loop', 'no_construction_assistance', 'no_capture_assistance', 'basal'):
        raise ValueError('Unknown mechanism')
    h = 0. if mechanism in ('no_capture_assistance', 'basal') else p.assisted_capture
    k = 0. if mechanism in ('no_construction_assistance', 'basal') else p.assisted_construction
    states = tuple(product(range(p.bank_quanta+1), range(2), range(p.capacity+1)))
    bill = round(p.construction_cost/p.quantum)
    yield_quanta = round((p.packet_energy-p.capture_loss)/p.quantum)

    def validate(s):
        if len(s) != 3 or any(type(v) is not int for v in s):
            raise ValueError('Invalid physical state')
        e, r, a = s
        if not 0 <= e <= p.bank_quanta or r not in (0, 1) or not 0 <= a <= p.capacity:
            raise ValueError('State outside the declared finite world')

    def energy(s):
        return p.quantum*s[0]+p.packet_energy*s[1]+p.apparatus_energy*s[2]

    def emit(s, target, rate, family, increments=None, work=0.):
        if rate > 0:
            return Event(family, family, target, rate,
                         tuple(i for i in range(3) if s[i] != target[i]),
                         work, increments or {})
        return None

    def source(s):
        e, r, a = s
        if not r:
            yield emit(s, (e, 1, a), p.supply_rate, 'packet_inflow',
                       {'resource_work': p.packet_energy}, p.packet_energy)
        else:
            yield emit(s, (e, 0, a), p.packet_decay, 'packet_decay',
                       {'unused_packet_energy': p.packet_energy})

    def capture(s):
        e, r, a = s
        if not r:
            return
        target = (min(p.bank_quanta, e+yield_quanta), 0, a)
        loaded = (target[0]-e)*p.quantum
        for coefficient, family in ((p.basal_capture, 'basal_capture'), (h*a, 'assisted_capture')):
            yield emit(s, target, coefficient, family,
                       {'captured_energy': loaded,
                        'assisted_captured_energy': loaded if family == 'assisted_capture' else 0.,
                        'conversion_loss': p.capture_loss,
                        'overflow_energy': p.packet_energy-p.capture_loss-loaded})

    def construction(s):
        e, r, a = s
        precursor = p.capacity-a
        dissipated = p.construction_cost-p.apparatus_energy
        if precursor and e >= bill:
            coefficient = p.basal_construction+k*a
            yield emit(s, (e-bill, r, a+1), precursor*coefficient*exp(p.beta*dissipated/2),
                       'paid_build', {'construction_bank_debit': p.construction_cost,
                        'construction_dissipation': dissipated,
                        'assisted_build_increment': k*a/coefficient,
                        'build_with_existing_apparatus': float(a > 0)})
        if a and e+bill <= p.bank_quanta:
            coefficient = p.basal_construction+k*(a-1)
            yield emit(s, (e+bill, r, a-1), a*coefficient*exp(-p.beta*dissipated/2),
                       'reverse_build', {'reverse_bank_return': p.construction_cost,
                        'reverse_recycled_hardware_energy': p.apparatus_energy,
                        'reverse_bath_import': dissipated})

    def bath(s):
        e, r, a = s
        if a < p.capacity:
            yield emit(s, (e, r, a+1), p.thermal_attempt*(p.capacity-a)*exp(-p.beta*p.apparatus_energy/2),
                       'thermal_build', {'thermal_hardware_import': p.apparatus_energy})
        if a:
            yield emit(s, (e, r, a-1), p.thermal_attempt*a*exp(p.beta*p.apparatus_energy/2),
                       'thermal_break', {'thermal_hardware_release': p.apparatus_energy})
        if e == 0 and a < p.capacity:
            yield emit(s, (e, r, a+1), p.starvation_damage*(p.capacity-a)*exp(-p.beta*p.apparatus_energy),
                       'starvation_reconstruction', {'starvation_bath_import': p.apparatus_energy})

    def damage(s):
        e, r, a = s
        if a:
            yield emit(s, (e, r, a-1), p.damage_rate*a, 'external_damage',
                       {'damage_release': p.apparatus_energy})
            if e == 0:
                yield emit(s, (e, r, a-1), p.starvation_damage*a, 'starvation_damage',
                           {'starvation_release': p.apparatus_energy})

    def expenditure(s):
        e, r, a = s
        if e:
            yield emit(s, (e-1, r, a), p.upkeep*a/p.quantum, 'hardware_upkeep',
                       {'upkeep_bank_debit': p.quantum})
            yield emit(s, (e-1, r, a), p.bank_leak/p.quantum, 'bank_leak',
                       {'leak_bank_debit': p.quantum})
        if e < p.bank_quanta:
            # Thermal reverses are retained and diagnosed, not free reconstruction.
            reverse_factor = exp(-p.beta*p.quantum)/p.quantum
            yield emit(s, (e+1, r, a), p.upkeep*a*reverse_factor, 'upkeep_reverse',
                       {'upkeep_bath_import': p.quantum})
            yield emit(s, (e+1, r, a), p.bank_leak*reverse_factor, 'leak_reverse',
                       {'leak_bath_import': p.quantum})

    def clean(fn):
        return lambda s: (event for event in fn(s) if event is not None)

    return WorldSpec(f'compounding-{mechanism}', '1', states, validate, energy,
        {'apparatus': lambda s: float(s[2]), 'precursor': lambda s: float(p.capacity-s[2]),
         'bank_energy': lambda s: p.quantum*s[0], 'packet_energy': lambda s: p.packet_energy*s[1],
         'expanded': lambda s: float(s[2] >= 2),
         'half_capacity': lambda s: float(s[2] >= max(2, (p.capacity+1)//2)),
         'unpowered': lambda s: float(s[0] == 0),
         'functional': lambda s: float(s[2] > 0 and s[0] >= bill)},
        tuple(RuleModule(name, '1', clean(fn)) for name, fn in
              (('resource', source), ('capture', capture), ('construction', construction),
               ('bath', bath), ('damage', damage), ('expenditure', expenditure))),
        {'fields': ('bank', 'packet', 'apparatus'), 'parameters': vars(p), 'mechanism': mechanism,
         'material': 'apparatus+precursor=capacity; damage preserves precursor material',
         'damage': 'one-way dissipative external damage; bath assembly fixed across damage sweep',
         'thermodynamics': 'construction and thermal pairs local energy-ratio consistent; open resource boundary',
         'scope': 'bounded chemical apparatus reproduction, not valuers or open-ended growth'})


def physical_readouts(compiled, final, occupation, initial):
    values = {name: float(occupation @ vector) for name, vector in compiled['flows'].items()}
    values.update({name+'_deadline': float(final @ vector) for name, vector in compiled['observables'].items()})
    values.update({name+'_time': float(occupation @ vector) for name, vector in compiled['observables'].items()})
    bank_change = float((final-initial) @ compiled['observables']['bank_energy'])
    costs = sum(values.get(name, 0.) for name in ('construction_bank_debit','upkeep_bank_debit','leak_bank_debit'))
    captured = values.get('captured_energy', 0.)
    reverse = values.get('reverse_bank_return', 0.)
    direct_bath = values.get('upkeep_bath_import', 0.)+values.get('leak_bath_import', 0.)
    values.update({'bank_change': bank_change,
                   'bank_balance_residual': bank_change-captured-reverse-direct_bath+costs,
                   'all_bank_costs': costs,
                   'capture_funding_fraction': captured/costs if costs else None,
                   'recycled_hardware_bank_fraction': values.get('reverse_recycled_hardware_energy', 0.)/costs if costs else None,
                   'bath_bank_fraction': (values.get('reverse_bath_import', 0.)+direct_bath)/costs if costs else None,
                   'thermal_build_fraction': values.get('thermal_build', 0.)/(values.get('thermal_build', 0.)+values.get('paid_build', 0.))
                      if values.get('thermal_build', 0.)+values.get('paid_build', 0.) else None,
                   'net_paid_hardware_creation': values.get('paid_build', 0.)-values.get('reverse_build', 0.),
                   'net_bath_hardware_import': values.get('thermal_hardware_import', 0.)-values.get('thermal_hardware_release', 0.),
                   'net_bath_import_excluding_packet_decay': values.get('reverse_bath_import', 0.)
                       +direct_bath+values.get('starvation_bath_import', 0.)
                       +values.get('thermal_hardware_import', 0.)-values.get('thermal_hardware_release', 0.)
                       -values.get('construction_dissipation', 0.)-values.get('upkeep_bank_debit', 0.)
                       -values.get('leak_bank_debit', 0.)-values.get('damage_release', 0.)
                       -values.get('starvation_release', 0.)-values.get('conversion_loss', 0.)-values.get('overflow_energy', 0.)})
    if abs(values['bank_balance_residual']) > 1e-7*max(1., costs):
        raise ArithmeticError('Independent bank funding balance failed')
    return values


def local_feedback_certificate(parameters):
    """Exact enabled-state propensity increments, including precursor depletion.

    A descendant increases capture propensity by h when a packet is present.
    It increases the next paid birth rate only below a stated density threshold.
    This alone does not prove realized or persistent growth.
    """
    p = parameters
    prefactor = exp(p.beta*(p.construction_cost-p.apparatus_energy)/2)
    return {'capture_increment_per_descendant': p.assisted_capture,
            'construction_increments': {str(a):
                (p.assisted_construction*(p.capacity-2*a-1)-p.basal_construction)*prefactor
                for a in range(1, p.capacity)},
            'conditions': 'packet present for capture; bank >= bill for paid construction',
            'is_realized_growth_proof': False}
