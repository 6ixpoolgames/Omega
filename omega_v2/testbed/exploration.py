"""Costed register-to-mobility coupling with physically present resource patches.

Finite mortality slice. Native resource, physiology and mobility modules share
the compiler/sampler contract. No rewards, event-label entropy or persistence filter.
"""
from dataclasses import dataclass
from itertools import product
from math import isfinite

from .aversive_signals import SignalParameters
from .contracts import Event, RuleModule, WorldSpec

H, O0, O1 = 0, 1, 2
ARMS = ('B', 'B_R', 'B_X', 'M_C', 'S_A')


@dataclass(frozen=True)
class ExplorationParameters:
    supply_rate: float = .6  # total nominal packet offers/time
    contrast: float = 0.  # refill split (1+contrast)/2, (1-contrast)/2
    decay: float = .1
    mobility: float = .1
    coupling: float = 1.
    movement_cost: float = .5
    flicker_on: float = .05871485218977088
    flicker_off: float = .36126583291983255

    def __post_init__(self):
        for name, value in vars(self).items():
            if not isfinite(value) or value < 0:
                raise ValueError(f'Nonnegative finite {name} required')
        if self.contrast >= 1 or self.supply_rate <= 0 or self.movement_cost <= 0:
            raise ValueError('Positive supplies at both patches and movement bill required')
        if self.flicker_on <= 0 or self.flicker_off <= 0:
            raise ValueError('Positive on/off rates required')


def build_world(arm='B_X', physiology=None, parameters=None):
    if arm not in ARMS:
        raise ValueError('Unknown exploration arm')
    p = physiology or SignalParameters(signal_upkeep=.02, struggle_cost=.5)
    x = parameters or ExplorationParameters()
    cap, move = p.units(p.energy_cap), p.units(x.movement_cost)
    if abs(move*p.quantum-x.movement_cost) > 1e-10 or move < 1:
        raise ValueError('Movement bill must be a positive quantum multiple')
    states = tuple((e, loc, s, z, a, b)
                   for e, loc, s, z, a, b in product(range(cap+1), range(3), range(2),
                                                     range(2), range(2), range(2))
                   if e or not s)
    fields = ('energy', 'location', 'signal', 'hazard', 'stock0', 'stock1')
    rho = x.flicker_on/(x.flicker_on+x.flicker_off)

    def validate(state):
        if (len(state) != 6 or any(type(v) is not int for v in state)
                or not 0 <= state[0] <= cap or state[1] not in (H, O0, O1)
                or any(v not in (0, 1) for v in state[2:])
                or (not state[0] and state[2])):
            raise ValueError('Invalid exploration physical state')

    def emit(state, target, rate, family, increments=None, work=0.):
        if rate <= 0:
            return None
        if target == state:
            raise ValueError('No-op label cannot contribute physical breadth')
        support = tuple(i for i, (a, b) in enumerate(zip(state, target)) if a != b)
        return Event(family, family, target, rate, support, work, increments or {})

    def spent(state, bill, loc=None, signal=None):
        e, old_loc, s, z, a, b = state
        remaining = max(0, e-bill)
        return (remaining, old_loc if loc is None else loc,
                (s if signal is None else signal) if remaining else 0, z, a, b)

    def resource_events(state):
        e, loc, s, z, a, b = state
        yield emit(state, (e, loc, s, 1-z, a, b), p.hazard_off if z else p.hazard_on,
                   'hazard_toggle')
        for patch, stock in enumerate((a, b)):
            target = list(state)
            target[4+patch] = 1-stock
            if stock:
                yield emit(state, tuple(target), x.decay, 'packet_decay',
                           {'packet_decay_energy': p.food_yield})
            else:
                rate = x.supply_rate*(1+(1 if patch == 0 else -1)*x.contrast)/2
                yield emit(state, tuple(target), rate, 'packet_inflow',
                           {'accepted_resource_work': p.food_yield}, p.food_yield)

    def physiology_events(state):
        e, loc, s, z, a, b = state
        if not e:
            return
        yield emit(state, spent(state, 1), p.metabolism/p.quantum, 'metabolism',
                   {'metabolic_bill': p.quantum})
        if s:
            yield emit(state, spent(state, 1), p.signal_upkeep/p.quantum, 'signal_upkeep',
                       {'signal_upkeep_bill': p.quantum})
            yield emit(state, (e, loc, 0, z, a, b), x.flicker_off, 'signal_off')
        elif arm != 'B':
            bill = p.units(p.signal_energy)
            if e > bill:
                yield emit(state, spent(state, bill, signal=1), x.flicker_on, 'signal_on',
                           {'signal_charge': p.signal_energy})
        if z and loc == H:
            yield emit(state, spent(state, 1), p.hazard_damage_rate, 'hazard_damage',
                       {'damage': p.quantum})
        # Fixed native basal repertoire in every arm. Register never reads escape.
        bill = p.units(p.forage_cost)
        if e >= bill:
            patch = 0 if loc in (H, O0) else 1
            success = (p.forage_hazard if loc == H else p.forage_outside)*(a if patch == 0 else b)
            if loc == H and z:
                success *= p.hazard_foraging_factor
            rate = p.attempt_rate*(1-p.normal_escape)
            target = list(state)
            target[0] = min(cap, e-bill+p.units(p.food_yield))
            target[4+patch] = 0
            accepted = (target[0]-e+bill)*p.quantum
            yield emit(state, tuple(target), rate*success, 'forage_success',
                       {'forage_bill': p.forage_cost, 'food_capture': accepted,
                        'discarded_food': p.food_yield-accepted})
            yield emit(state, spent(state, bill), rate*(1-success), 'forage_failure',
                       {'forage_bill': p.forage_cost})
        bill = p.units(p.struggle_cost)
        if e >= bill:
            rate = p.attempt_rate*p.normal_escape
            success = p.escape_success if loc == H else 0.
            yield emit(state, spent(state, bill, loc=O0), rate*success, 'escape_success',
                       {'struggle_bill': p.struggle_cost})
            yield emit(state, spent(state, bill), rate*(1-success), 'escape_failure',
                       {'struggle_bill': p.struggle_cost})

    def mobility_events(state):
        e, loc, s, _z, a, b = state
        if e < move or loc == H:
            return
        if arm == 'B_X':
            extra = x.coupling*s
        elif arm == 'M_C':
            extra = x.coupling*rho
        elif arm == 'S_A':
            current, other = (a, b) if loc == O0 else (b, a)
            extra = x.coupling*float(not current and other)
        else:
            extra = 0.
        rate = x.mobility*(1+extra)
        target_loc = O1 if loc == O0 else O0
        yield emit(state, spent(state, move, loc=target_loc), rate, 'movement',
                   {'movement_bill': x.movement_cost,
                    'productive_arrival': float((b if target_loc == O1 else a) == 1)})

    def clean(events):
        return lambda state: (event for event in events(state) if event is not None)

    return WorldSpec(
        f'exploration-{arm}', '1', states, validate,
        lambda state: p.quantum*state[0]+p.signal_energy*state[2]+p.food_yield*(state[4]+state[5]),
        {'alive': lambda state: float(state[0] > 0),
         'signal_occupancy': lambda state: float(state[2]),
         'stored_energy': lambda state: p.quantum*state[0],
         'hazard_exposure': lambda state: float(state[0] > 0 and state[1] == H and state[3]),
         'stock0': lambda state: float(state[4]), 'stock1': lambda state: float(state[5]),
         'outside1_alive': lambda state: float(state[0] > 0 and state[1] == O1)},
        (RuleModule('resource-patches', '1', clean(resource_events)),
         RuleModule('physiology', '1', clean(physiology_events)),
         RuleModule('costed-mobility', '1', clean(mobility_events))),
        {'fields': fields, 'arm': arm, 'physiology': vars(p), 'parameters': vars(x),
         'constant_control_duty': rho,
         'constant_control_is_flux_matched': False,
         'observation': 'S_A reads physical stocks; no separate sensor memory; idealized information benchmark',
         'death': 'absorbing body; resource and hazard processes continue',
         'nominal_offered_work_rate': x.supply_rate*p.food_yield,
         'thermodynamics': 'open dissipative resource boundary; energy ledger, not detailed balance',
         'thermal_model': 'coarse stochastic stocks and hazard; not microscopic thermal gas',
         'compounding': 'not represented; no paid reconstruction loop'})
