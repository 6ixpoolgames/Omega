"""Renewable, embodied access with conserved apparatus and precursor pools.

New interpretation: e=0 is an unpowered reservoir, not an identity resurrection.
Legacy mortal exploration/paid-sensing worlds are unchanged. Hardware pairs
obey a declared local energy-ratio prescription; the retained sensor/body
kinetics are open dissipative mechanisms, not a complete microscopic bath.
"""
from dataclasses import dataclass
from itertools import product
from math import exp, isfinite

import numpy as np
from scipy.optimize import least_squares

from .analysis.signal_readouts import mutual_information, occupation_integral
from .aversive_signals import SignalParameters
from .compiler import compile_world
from .contracts import Event, RuleModule, WorldSpec
from .exploration import O0, O1, ExplorationParameters, H
from .paid_sensing import SensorParameters, cue
from .paid_sensing import build_world as sensor_world


@dataclass(frozen=True)
class RenewalParameters:
    capacity: int = 1
    apparatus_energy: float = 1.
    construction_cost: float = 1.5
    construction_rate: float = .08
    wear_rate: float = .02
    hardware_upkeep: float = .02
    basal_harvest: float = .02
    assisted_harvest: float = .98
    autocatalytic_gain: float = 2.
    beta: float = 1.
    repair_enabled: bool = True

    def __post_init__(self):
        if type(self.capacity) is not int or self.capacity < 1:
            raise ValueError('Positive integer capacity required')
        if type(self.repair_enabled) is not bool:
            raise ValueError('Boolean repair flag required')
        for name, value in vars(self).items():
            if name in ('capacity', 'repair_enabled'):
                continue
            if not isfinite(value) or value < 0:
                raise ValueError(f'Nonnegative finite {name} required')
        if min(self.beta, self.basal_harvest, self.construction_rate, self.wear_rate) <= 0:
            raise ValueError('Positive bath/pair and basal rates required')
        if self.construction_cost <= self.apparatus_energy or self.apparatus_energy <= 0:
            raise ValueError('Paid construction stores positive hardware energy and dissipates a remainder')


def build_world(mode='I', physiology=None, parameters=None, sensor=None, renewal=None):
    p = physiology or SignalParameters(signal_upkeep=.02, struggle_cost=.5)
    x = parameters or ExplorationParameters()
    v = sensor or SensorParameters()
    n = renewal or RenewalParameters()
    parent = sensor_world(mode, p, x, v)
    cap, build_bill, forage_loss = p.units(p.energy_cap), p.units(n.construction_cost), p.units(p.forage_cost)
    if build_bill > cap or abs(build_bill*p.quantum-n.construction_cost) > 1e-10:
        raise ValueError('Construction bill must be representable in the fixed reservoir')
    if p.food_yield <= p.forage_cost:
        raise ValueError('Positive net resource transduction required')
    # The charged bit is an actual physical coordinate at e=0 until relaxation.
    states = tuple(product(range(cap+1), range(3), range(2), range(2), range(2), range(2), range(n.capacity+1)))

    def validate(state):
        if (len(state) != 7 or any(type(z) is not int for z in state)
                or not 0 <= state[0] <= cap or state[1] not in (H, O0, O1)
                or any(z not in (0, 1) for z in state[2:6]) or not 0 <= state[6] <= n.capacity):
            raise ValueError('Invalid renewable physical state')

    def energy(state):
        return p.quantum*state[0]+p.signal_energy*state[2]+p.food_yield*(state[4]+state[5])+n.apparatus_energy*state[6]

    def emit(state, target, rate, family, increments=None):
        if rate <= 0:
            return None
        support = tuple(i for i, (a, b) in enumerate(zip(state, target)) if a != b)
        return Event(family, family, target, rate, support, 0., increments or {})

    base_modules = {m.id: m for m in parent.modules}

    def resources(state):
        for event in base_modules['resource-patches'].events(state[:6]):
            yield Event(event.rule_id, event.family, event.target+(state[6],), event.rate,
                        event.support, event.work, event.increments)

    def retained_body(state):
        e, loc, s, z, a, b, apparatus = state
        for event in base_modules['physiology'].events(state[:6]):
            if event.family.startswith('forage_') or event.family == 'signal_off':
                continue
            if event.family.startswith('escape_') and not apparatus:
                continue
            if event.family == 'signal_upkeep' and not apparatus:
                continue
            # Hardware is required for the physical motor, not reservoir leakage.
            factor = apparatus if event.family.startswith('escape_') else 1.
            yield Event(event.rule_id, event.family, event.target+(apparatus,), event.rate*factor,
                        event.support+(6,), event.work, event.increments)
        if s:
            yield emit(state, (e, loc, 0, z, a, b, apparatus), x.flicker_off, 'signal_off')
        if e and apparatus and n.hardware_upkeep:
            yield emit(state, (e-1, loc, s, z, a, b, apparatus),
                       n.hardware_upkeep*apparatus/p.quantum, 'hardware_upkeep',
                       {'hardware_upkeep_bill': p.quantum})

    def sensor_events(state):
        if state[6] == 0:
            return
        for event in base_modules['paid-sensor'].events(state[:6]):
            yield Event(event.rule_id, event.family, event.target+(state[6],), event.rate*state[6],
                        event.support+(6,), event.work, event.increments)

    def mobility(state):
        if state[6] == 0:
            return
        for event in base_modules['costed-mobility'].events(state[:6]):
            yield Event(event.rule_id, event.family, event.target+(state[6],), event.rate*state[6],
                        event.support+(6,), event.work, event.increments)

    def harvest(state):
        e, loc, _s, z, a, b, apparatus = state
        patch = 0 if loc in (H, O0) else 1
        if not (a if patch == 0 else b):
            return
        rate = p.attempt_rate*(1-p.normal_escape)*(p.forage_hazard if loc == H else p.forage_outside)
        if loc == H and z:
            rate *= p.hazard_foraging_factor
        target = list(state)
        target[0] = min(cap, e+p.units(p.food_yield)-forage_loss)
        target[4+patch] = 0
        captured = (target[0]-e)*p.quantum
        for coefficient, family in ((n.basal_harvest, 'basal_capture'),
                                    (n.assisted_harvest*apparatus, 'assisted_capture')):
            yield emit(state, tuple(target), rate*coefficient, family,
                       {'captured_energy': captured, 'assisted_captured_energy': captured if family == 'assisted_capture' else 0.,
                        'capture_conversion_loss': p.forage_cost,
                        'capture_overflow_loss': p.food_yield-p.forage_cost-captured})

    def hardware(state):
        e, loc, s, z, a, b, apparatus = state
        precursor = n.capacity-apparatus

        def paired(target, coefficient, count, family, increments):
            delta = energy(target)-energy(state)
            return emit(state, target, coefficient*count*exp(-n.beta*delta/2), family, increments)

        if apparatus:
            yield paired((e, loc, s, z, a, b, apparatus-1), n.wear_rate, apparatus,
                         'thermal_disassembly', {'hardware_disassembly': 1.})
        if precursor:
            yield paired((e, loc, s, z, a, b, apparatus+1), n.wear_rate, precursor,
                         'thermal_assembly', {'hardware_thermal_assembly': 1.})
        if not n.repair_enabled:
            return
        if precursor and e >= build_bill:
            coefficient = n.construction_rate*(1+n.autocatalytic_gain*apparatus)
            yield paired((e-build_bill, loc, s, z, a, b, apparatus+1), coefficient, precursor,
                         'paid_construction', {'construction_bill': n.construction_cost,
                          'hardware_paid_construction': 1., 'construction_assisted_by_hardware': float(apparatus > 0)})
        if apparatus and e+build_bill <= cap:
            # Same reaction-pair coefficient, evaluated at the lower apparatus count.
            coefficient = n.construction_rate*(1+n.autocatalytic_gain*(apparatus-1))
            yield paired((e+build_bill, loc, s, z, a, b, apparatus-1), coefficient, apparatus,
                         'reverse_construction', {'construction_energy_return': n.construction_cost,
                          'hardware_reverse_construction': 1.})

    def clean(fn):
        return lambda state: (ev for ev in fn(state) if ev is not None)

    observables = {name: (lambda state, fn=fn: fn(state[:6])) for name, fn in parent.observables.items()}
    observables.update({'apparatus': lambda state: float(state[6]),
                        'precursor': lambda state: float(n.capacity-state[6]),
                        'functional': lambda state: float(state[6] > 0 and state[0] >= p.units(v.read_cost+p.signal_energy+x.movement_cost)),
                        'unpowered': lambda state: float(state[0] == 0),
                        'expanded': lambda state: float(state[6] >= 2)})
    return WorldSpec(f'renewal-{mode}', '1', states, validate, energy, observables,
        (RuleModule('renewal-resources', '1', clean(resources)),
         RuleModule('renewal-body', '1', clean(retained_body)),
         RuleModule('paid-sensor', '2', clean(sensor_events)),
         RuleModule('renewal-mobility', '1', clean(mobility)),
         RuleModule('passive-transduction', '1', clean(harvest)),
         RuleModule('apparatus-construction', '1', clean(hardware))),
        {**parent.metadata, 'fields': (*parent.metadata['fields'], 'apparatus'), 'renewal': vars(n),
         'death': 'new adapter: e=0 unpowered, not identity resurrection',
         'compounding': 'capacity1 self-maintenance; capacity2 bounded construction feedback; not open-ended',
         'material': 'apparatus+precursor fixed; reservoir/packets energy-accounted',
         'thermodynamics': 'hardware pairs energy-ratio consistent at beta; remaining kinetics open dissipative',
         'readout_alive_is_identity_claim': False})


def physical_readouts(compiled, root, horizon, prepared=None, stationary=False):
    final, occupation = prepared or occupation_integral(compiled['Q'], root, horizon)
    physical = {name+'_time': float(occupation @ values) for name, values in compiled['observables'].items()}
    physical.update({name+'_deadline': float(final @ values) for name, values in compiled['observables'].items()})
    physical.update({name: float(occupation @ values) for name, values in compiled['flows'].items() if not name.startswith('net_')})
    n = compiled['metadata']['renewal']
    capital = 0. if stationary else compiled['states'][root][6]*n['apparatus_energy']
    assisted = physical.get('assisted_captured_energy', 0.)
    hardware_bill = capital+physical.get('construction_bill', 0.)+physical.get('hardware_upkeep_bill', 0.)
    all_bill = hardware_bill+sum(physical.get(name, 0.) for name in
        ('sensor_bill', 'signal_charge', 'signal_upkeep_bill', 'movement_bill', 'metabolic_bill', 'struggle_bill'))
    physical.update({'initial_hardware_capital': capital,
                     'hardware_gross_return_ratio': assisted/hardware_bill if hardware_bill else None,
                     'all_running_cost_coverage_ratio': assisted/all_bill if all_bill else None,
                     'return_ratio_is_causal_or_net_loop_gain': False,
                     'thermal_and_reverse_repair_subsidies': physical.get('hardware_thermal_assembly', 0.)})
    reader = next(m for m in compiled['world'].modules if m.id == 'paid-sensor')
    tables = {}
    for i, state in enumerate(compiled['states']):
        table = tables.setdefault((*state[:3], state[6]), np.zeros((2, 2)))
        for event in reader.events(state):
            table[cue(state[:6]), event.target[2]] += occupation[i]*event.rate
    total = sum(t.sum() for t in tables.values())
    physical['conditional_write_information_bits'] = sum(t.sum()*(mutual_information(t) or 0.) for t in tables.values())/total if total else 0.
    return physical


def calibrate(physiology, parameters, sensor, renewal, roots, horizon=64., tolerance=1e-6):
    x = ExplorationParameters(**{**vars(parameters), 'coupling': 0.})

    def moments(world):
        compiled = compile_world(world)
        values = []
        for root in roots:
            _, occ = occupation_integral(compiled['Q'], int(compiled['index'][tuple(root)]), horizon)
            values.append((float(occ @ compiled['observables']['signal_occupancy']),
                           float(occ @ compiled['flows']['register_activation'])))
        return np.mean(values, axis=0)

    target = moments(build_world('I', physiology, x, sensor, renewal))
    if min(target) <= 0:
        raise ValueError('Positive physical calibration moments required')

    def objective(probs):
        v = SensorParameters(**{**vars(sensor), 'noise_on': float(probs[0]), 'noise_retain': float(probs[1])})
        return (moments(build_world('R', physiology, x, v, renewal))-target)/target

    fit = least_squares(objective, [.2, .5], bounds=(1e-6, 1-1e-6),
                        ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=80)
    error = float(np.max(abs(fit.fun)))
    return {'noise_on': float(fit.x[0]), 'noise_retain': float(fit.x[1]), 'relative_error': error,
            'target_signal_time': float(target[0]), 'target_activation_count': float(target[1]),
            'success': bool(fit.success and error <= tolerance), 'evaluations': fit.nfev,
            'history_entropy_used': False, 'root_moments_are_pooled': True}
