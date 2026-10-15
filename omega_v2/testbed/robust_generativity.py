"""Three distinct catalytic roles, explicit energy and optional material loss.

Count-state chemistry, not a spatial gas. Native event families distinguish
reaction routes for causal queries; the compiler merges identical outcomes.
The fully reversible packet/capture bath extends the older compounding model.
"""
from dataclasses import dataclass
from itertools import product
from math import exp, factorial, isfinite

import numpy as np

from .contracts import Event, RuleModule, WorldSpec

TYPES = ('A', 'B', 'C')
PARENT = {'A': 'C', 'B': 'A', 'C': 'B'}
MECHANISMS = ('full', 'cut_A_to_B', 'cut_B_to_C', 'cut_C_to_A',
              'cut_assisted_capture', 'all_assistance_off')


@dataclass(frozen=True)
class GenerativityParameters:
    capacity: int = 6
    bank_quanta: int = 8
    quantum: float = .5
    packet_energy: float = 3.
    capture_loss: float = .5
    apparatus_energy: float = 1.
    construction_cost: float = 2.
    beta: float = 6.
    supply_rate: float = .6
    packet_decay: float = .05
    basal_capture: float = .002
    assisted_capture: float = .1
    basal_construction: float = .0001
    assisted_construction: float = .008
    assistance_multiplier: float = 1.
    feedback_exponent: float = 1.
    thermal_attempt: float = .00001
    damage_rate: float = .005
    irreversible_fraction: float = 0.
    starvation_damage: float = .02
    upkeep: float = .01
    bank_leak: float = .002

    def __post_init__(self):
        for key in ('capacity', 'bank_quanta'):
            if type(getattr(self, key)) is not int or getattr(self, key) < 1:
                raise ValueError('Positive integer capacity and bank required')
        for key, value in vars(self).items():
            if not isfinite(value) or value < 0:
                raise ValueError(f'Invalid {key}')
        if min(self.quantum, self.beta, self.basal_capture,
               self.basal_construction, self.thermal_attempt, self.packet_decay,
               self.bank_leak, self.feedback_exponent) <= 0:
            raise ValueError('Positive native basal, bath and feedback scales required')
        if not 0 <= self.irreversible_fraction <= 1:
            raise ValueError('Damage fraction outside [0, 1]')
        if not self.packet_energy > self.capture_loss >= 0:
            raise ValueError('Positive net packet yield required')
        if not self.construction_cost > self.apparatus_energy > 0:
            raise ValueError('Construction must store energy and dissipate a remainder')
        for value in (self.packet_energy-self.capture_loss, self.construction_cost):
            if abs(value/self.quantum-round(value/self.quantum)) > 1e-10:
                raise ValueError('Bills and capture must fit the physical quantum')
        if self.construction_cost > self.bank_quanta*self.quantum:
            raise ValueError('Construction exceeds bank capacity')


def build_world(parameters=None, mechanism='full'):
    p = parameters or GenerativityParameters()
    if mechanism not in MECHANISMS:
        raise ValueError('Unknown mechanism')
    # Include the sink only when it is physically reachable from D=0.
    sink = p.damage_rate*p.irreversible_fraction > 0
    counts = tuple((a, b, c, d)
                   for d in range(p.capacity+1 if sink else 1)
                   for a in range(p.capacity-d+1)
                   for b in range(p.capacity-d-a+1)
                   for c in range(p.capacity-d-a-b+1))
    states = tuple((e, r, *n) for e, r in product(range(p.bank_quanta+1), range(2))
                   for n in counts)
    bill = round(p.construction_cost/p.quantum)
    gain = round((p.packet_energy-p.capture_loss)/p.quantum)

    def validate(s):
        if len(s) != 6 or any(type(v) is not int for v in s):
            raise ValueError('Six integer physical coordinates required')
        if not (0 <= s[0] <= p.bank_quanta and s[1] in (0, 1)
                and min(s[2:]) >= 0 and sum(s[2:]) <= p.capacity
                and (sink or s[5] == 0)):
            raise ValueError('State outside declared physical world')

    def energy(s):
        return p.quantum*s[0]+p.packet_energy*s[1]+p.apparatus_energy*sum(s[2:5])

    def degeneracy(s):
        denominator = factorial(p.capacity-sum(s[2:]))
        for n in s[2:]:
            denominator *= factorial(n)
        return factorial(p.capacity)/denominator

    def emit(s, target, rate, family, increments=None, work=0.):
        if rate <= 0:
            return None
        return Event(family, family, tuple(target), rate,
                     tuple(i for i in range(6) if s[i] != target[i]),
                     work, increments or {})

    def updated(s, **changes):
        t = list(s)
        for key, value in changes.items():
            t[int(key)] = value
        return tuple(t)

    def resource(s):
        if s[1] == 0:
            t = updated(s, **{'1': 1})
            yield emit(s, t, p.supply_rate, 'packet_inflow',
                       {'resource_work': p.packet_energy}, p.packet_energy)
            yield emit(s, t, p.packet_decay*exp(-p.beta*p.packet_energy),
                       'packet_bath_return', {'packet_bath_import': p.packet_energy})
        else:
            yield emit(s, updated(s, **{'1': 0}), p.packet_decay, 'packet_decay',
                       {'packet_bath_release': p.packet_energy})

    def capture(s):
        h = 0. if mechanism in ('cut_assisted_capture', 'all_assistance_off') else p.assisted_capture*s[2]
        for coefficient, family in ((p.basal_capture, 'basal_capture'), (h, 'assisted_capture')):
            if s[1]:
                end = min(p.bank_quanta, s[0]+gain)
                loaded = p.quantum*(end-s[0])
                yield emit(s, updated(s, **{'0': end, '1': 0}), coefficient, family,
                           {'captured_energy': loaded,
                            'assisted_captured_energy': loaded if h and family == 'assisted_capture' else 0.,
                            'capture_heat': p.packet_energy-loaded})
            else:
                # Saturation is many-to-one: reverse EVERY actual forward edge.
                for origin in range(p.bank_quanta+1):
                    if min(p.bank_quanta, origin+gain) != s[0]:
                        continue
                    loaded = p.quantum*(s[0]-origin)
                    yield emit(s, updated(s, **{'0': origin, '1': 1}),
                               coefficient*exp(-p.beta*(p.packet_energy-loaded)),
                               'reverse_'+family,
                               {'reverse_capture_bank_debit': loaded,
                                'reverse_capture_packet_energy': p.packet_energy,
                                'reverse_capture_bath_import': p.packet_energy-loaded})

    def construction(s):
        precursor = p.capacity-sum(s[2:])
        dissipated = p.construction_cost-p.apparatus_energy
        for idx, name in enumerate(TYPES, 2):
            parent = TYPES.index(PARENT[name])+2
            link = PARENT[name]+'_to_'+name
            k = (0. if mechanism in ('cut_'+link, 'all_assistance_off') else
                 p.assisted_construction*p.assistance_multiplier*s[parent]**p.feedback_exponent)
            for coefficient, label in ((p.basal_construction, 'basal_'+name),
                                       (k, 'assisted_'+link)):
                if precursor and s[0] >= bill:
                    target = list(s); target[0] -= bill; target[idx] += 1
                    yield emit(s, target, precursor*coefficient*exp(p.beta*dissipated/2),
                               'paid_'+label, {'construction_bank_debit': p.construction_cost,
                                               'paid_births': 1., 'construction_dissipation': dissipated})
                if s[idx] and s[0]+bill <= p.bank_quanta:
                    target = list(s); target[0] += bill; target[idx] -= 1
                    yield emit(s, target, s[idx]*coefficient*exp(-p.beta*dissipated/2),
                               'reverse_'+label, {'reverse_bank_return': p.construction_cost,
                                                  'reverse_births': 1., 'reverse_bath_import': dissipated})

    def apparatus_bath(s):
        precursor = p.capacity-sum(s[2:])
        for idx, name in enumerate(TYPES, 2):
            if precursor:
                target = list(s); target[idx] += 1
                yield emit(s, target, precursor*p.thermal_attempt*exp(-p.beta*p.apparatus_energy/2),
                           'thermal_build_'+name, {'thermal_births': 1., 'thermal_hardware_import': p.apparatus_energy})
                if s[0] == 0:
                    yield emit(s, target, precursor*p.starvation_damage*exp(-p.beta*p.apparatus_energy),
                               'unpowered_reconstruction_'+name,
                               {'unpowered_births': 1., 'unpowered_bath_import': p.apparatus_energy})
            if s[idx]:
                target = list(s); target[idx] -= 1
                yield emit(s, target, s[idx]*p.thermal_attempt*exp(p.beta*p.apparatus_energy/2),
                           'thermal_break_'+name, {'thermal_losses': 1., 'thermal_hardware_release': p.apparatus_energy})
                if s[0] == 0:
                    yield emit(s, target, s[idx]*p.starvation_damage, 'unpowered_break_'+name,
                               {'unpowered_losses': 1., 'unpowered_release': p.apparatus_energy})

    def damage(s):
        for idx, name in enumerate(TYPES, 2):
            if not s[idx]:
                continue
            for fraction, lost in ((1-p.irreversible_fraction, False), (p.irreversible_fraction, True)):
                target = list(s); target[idx] -= 1; target[5] += int(lost)
                yield emit(s, target, p.damage_rate*s[idx]*fraction,
                           ('sink_' if lost else 'damage_')+name,
                           {'irreversible_losses' if lost else 'repairable_losses': 1.,
                            'damage_release': p.apparatus_energy})

    def expenditure(s):
        apparatus = sum(s[2:5])
        for coefficient, family, debit, credit in (
                (p.upkeep*apparatus/p.quantum, 'hardware_upkeep', 'upkeep_bank_debit', 'upkeep_bath_import'),
                (p.bank_leak/p.quantum, 'bank_leak', 'leak_bank_debit', 'leak_bath_import')):
            if s[0]:
                yield emit(s, updated(s, **{'0': s[0]-1}), coefficient, family, {debit: p.quantum})
            if s[0] < p.bank_quanta:
                yield emit(s, updated(s, **{'0': s[0]+1}), coefficient*exp(-p.beta*p.quantum),
                           family+'_reverse', {credit: p.quantum})

    def clean(fn):
        return lambda s: (event for event in fn(s) if event is not None)

    return WorldSpec('robust-generativity-'+mechanism, '1', states, validate, energy,
        {'A': lambda s: float(s[2]), 'B': lambda s: float(s[3]), 'C': lambda s: float(s[4]),
         'apparatus': lambda s: float(sum(s[2:5])), 'unavailable': lambda s: float(s[5]),
         'precursor': lambda s: float(p.capacity-sum(s[2:])),
         'bank_energy': lambda s: p.quantum*s[0], 'packet_energy': lambda s: p.packet_energy*s[1],
         'loop': lambda s: float(min(s[2:5]) >= 1),
         'ready': lambda s: float(min(s[2:5]) >= 1 and s[0] >= bill and sum(s[2:]) < p.capacity),
         'expanded': lambda s: float(min(s[2:5]) >= 1 and sum(s[2:5]) >= 4)},
        tuple(RuleModule(name, '1', clean(fn)) for name, fn in
              (('resource', resource), ('capture', capture), ('construction', construction),
               ('apparatus_bath', apparatus_bath), ('damage', damage), ('expenditure', expenditure))),
        {'fields': ('bank', 'packet', 'A', 'B', 'C', 'unavailable'),
         'parameters': vars(p), 'mechanism': mechanism, 'sink_enumerated': sink,
         'thermodynamics': 'full bath detailed balance when source/damage off, each fixed-D sector',
         'scope': 'well-mixed count chemistry; no translational motion, controllers or valuers'}, degeneracy)


def physical_readouts(compiled, final, occupation, initial, boundary_heat=0.):
    """Complete native ledger; reverse capture is a real bank debit."""
    values = {name: float(occupation @ v) for name, v in compiled['flows'].items()}
    bank_change = float((final-initial) @ compiled['observables']['bank_energy'])
    debit = sum(values.get(k, 0.) for k in
                ('construction_bank_debit', 'upkeep_bank_debit', 'leak_bank_debit', 'reverse_capture_bank_debit'))
    credit = sum(values.get(k, 0.) for k in
                 ('captured_energy', 'reverse_bank_return', 'upkeep_bath_import', 'leak_bath_import'))
    residual = bank_change-credit+debit
    energy_residual = float((final-initial) @ compiled['energy'])-values['drive_work']+values['bath_heat']+boundary_heat
    if max(abs(residual), abs(energy_residual)) > 1e-7*max(1., debit, credit):
        raise ArithmeticError('Independent bank/total-energy ledger failed')
    # Captures can consume the initial packet, bath-return packets or packets
    # made by reverse capture. Without provenance labels, deduct their entire
    # energy as an upper bound on non-external capture loading. This deliberately
    # underestimates funding from the driven source, and adds no physical state.
    nonexternal_packet_budget = (float(initial @ compiled['observables']['packet_energy'])
        +values.get('packet_bath_import', 0.)+values.get('reverse_capture_packet_energy', 0.))
    gross_capture_spent = max(0., values.get('captured_energy', 0.)-
                              float(final @ compiled['observables']['bank_energy']))
    external_spent_lower = max(0., gross_capture_spent-nonexternal_packet_budget)
    values.update(bank_change=bank_change, bank_balance_residual=residual,
                  prescribed_boundary_heat=boundary_heat,
                  energy_balance_residual=energy_residual, all_bank_expenditure=debit,
                  nonexternal_packet_budget=nonexternal_packet_budget,
                  gross_capture_funding_spent_lower_bound=gross_capture_spent/debit if debit else None,
                  external_funding_spent_lower_bound=external_spent_lower/debit if debit else None)
    return values


def matched_roots(compiled, energy=7.):
    """Conditional known-root reference; do not add entropy of drawing a root."""
    states, world = compiled['states'], compiled['world']
    thermal = np.array([world.degeneracy(s) if s[5] == 0 and abs(world.energy(s)-energy) < 1e-10
                        else 0. for s in states])
    if thermal.sum() == 0:
        raise ValueError('Empty reference energy shell')
    thermal /= thermal.sum()
    roots = {'thermal': thermal}
    for name, state in (('seed', (6, 1, 1, 0, 0, 0)), ('unbound', (8, 1, 0, 0, 0, 0))):
        if abs(world.energy(state)-energy) > 1e-10 or state not in compiled['index']:
            raise ValueError('Default matched roots require the declared bank/energy adapter')
        v = np.zeros(len(states)); v[compiled['index'][state]] = 1.
        roots[name] = v
    return roots
