"""Paid stock-dependent writing versus costed stock-independent writing.

Extends the exploration adapter without changing legacy generators. Native
resources, body and motor are shared; the only new relation is the sensor write.
"""
from dataclasses import dataclass, replace
from math import isfinite

import numpy as np
from scipy.optimize import least_squares

from .analysis.signal_readouts import mutual_information, occupation_integral
from .aversive_signals import SignalParameters
from .compiler import compile_world
from .contracts import Event, RuleModule
from .exploration import O0, ExplorationParameters, H
from .exploration import build_world as exploration_world


@dataclass(frozen=True)
class SensorParameters:
    refresh_rate: float = .2
    read_cost: float = .5
    error: float = .1
    noise_on: float = .2
    noise_retain: float = .5

    def __post_init__(self):
        for name, value in vars(self).items():
            if not isfinite(value) or value < 0:
                raise ValueError(f'Nonnegative finite {name} required')
        if self.refresh_rate <= 0 or self.read_cost <= 0 or self.error > .5:
            raise ValueError('Positive paid sensing and error in [0, .5] required')
        if self.noise_on > 1 or self.noise_retain > 1:
            raise ValueError('Noise probabilities required')


def cue(state):
    _, loc, _, _, a, b = state
    if loc == H:
        return 0
    current, other = (a, b) if loc == O0 else (b, a)
    return int(not current and other)


def build_world(mode='I', physiology=None, parameters=None, sensor=None):
    if mode not in ('I', 'R'):
        raise ValueError('Informative I or independent R required')
    p = physiology or SignalParameters(signal_upkeep=.02, struggle_cost=.5)
    x = parameters or ExplorationParameters()
    v = sensor or SensorParameters()
    bill, charge = p.units(v.read_cost), p.units(p.signal_energy)
    if bill < 1 or abs(bill*p.quantum-v.read_cost) > 1e-10:
        raise ValueError('Sensor read bill must be a positive quantum multiple')
    parent = exploration_world('B_X', p, x)
    physiology_module = next(m for m in parent.modules if m.id == 'physiology')

    def body(state):
        return (ev for ev in physiology_module.events(state) if ev.family != 'signal_on')

    def reads(state):
        e, loc, s, z, a, b = state
        if e < bill:
            return
        probability = v.error+(1-2*v.error)*cue(state) if mode == 'I' else (v.noise_retain if s else v.noise_on)
        for desired, prob in ((0, 1-probability), (1, probability)):
            if prob <= 0:
                continue
            activating = desired == 1 and s == 0
            powered = not activating or e > bill+charge
            paid_charge = charge if activating and powered else 0
            remaining = e-bill-paid_charge
            target_s = (desired if powered else s) if remaining else 0
            target = (remaining, loc, target_s, z, a, b)
            support = tuple(i for i, (old, new) in enumerate(zip(state, target)) if old != new)
            yield Event('paid-sensor-read', 'sensor_read', target, v.refresh_rate*prob, support, 0.,
                        {'sensor_bill': v.read_cost, 'signal_charge': paid_charge*p.quantum,
                         'register_activation': float(activating and powered),
                         'register_write_failure': float(activating and not powered),
                         'sensor_bit_change': float(target_s != s)})

    modules = tuple(replace(m, events=body) if m.id == 'physiology' else m for m in parent.modules)
    metadata = {**parent.metadata, 'mode': mode, 'sensor': vars(v),
                'observation': 'stock cue writes a paid bit; motor reads only the bit',
                'noise_reads_stocks': False, 'unit_bills_matched': True,
                'realized_total_costs_assumed_matched': False}
    return replace(parent, id=f'paid-sensing-{mode}', modules=(*modules, RuleModule('paid-sensor', '1', reads)),
                   metadata=metadata)


def readouts(compiled, root, horizon, prepared=None):
    final, occupation = prepared or occupation_integral(compiled['Q'], root, horizon)
    obs = compiled['observables']
    physical = {'survival': float(final @ obs['alive']), 'lifetime': float(occupation @ obs['alive']),
                'signal_time': float(occupation @ obs['signal_occupancy']),
                'stock0_time': float(occupation @ obs['stock0']), 'stock1_time': float(occupation @ obs['stock1']),
                'nominal_offered_work': horizon*compiled['metadata']['nominal_offered_work_rate']}
    physical.update({name: float(occupation @ flow) for name, flow in compiled['flows'].items()
                     if not name.startswith('net_')})
    # Instantaneous conditional sensor write information, not phenomenal or
    # ethical tracking. R's bit may correlate with stocks through action feedback.
    tables = {}
    reader = next(m for m in compiled['world'].modules if m.id == 'paid-sensor')
    for i, state in enumerate(compiled['states']):
        if state[0] == 0:
            continue
        context = state[:3]
        table = tables.setdefault(context, np.zeros((2, 2)))
        for event in reader.events(state):
            table[cue(state), event.target[2]] += occupation[i]*event.rate
    total = sum(table.sum() for table in tables.values())
    physical['conditional_sensor_write_information_bits'] = sum(
        table.sum()*(mutual_information(table) or 0.) for table in tables.values())/total if total else 0.
    physical['sensor_write_conditioning'] = 'pre-read energy, location, bit; conditioned on read occurrence'
    return physical


def calibrate(physiology, parameters, sensor, roots, horizon=64., tolerance=1e-6):
    """Match occupancy/activation moments at zero motor coupling; never entropy.

    Two constant write probabilities are fitted. Refresh rate, unit bills,
    relaxation, resource law and body remain unchanged. Fit is fixed for science.
    """
    x = replace(parameters, coupling=0.)
    info = compile_world(build_world('I', physiology, x, sensor))

    def moments(compiled):
        values = [readouts(compiled, int(compiled['index'][tuple(root)]), horizon) for root in roots]
        return np.array([sum(v['signal_time'] for v in values)/len(values),
                         sum(v.get('register_activation', 0.) for v in values)/len(values)])

    target = moments(info)
    if min(target) <= 0:
        raise ValueError('Positive calibration moments required')

    def objective(probs):
        control = replace(sensor, noise_on=float(probs[0]), noise_retain=float(probs[1]))
        return (moments(compile_world(build_world('R', physiology, x, control)))-target)/target

    fit = least_squares(objective, [.2, .5], bounds=(1e-6, 1-1e-6),
                        ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=80)
    error = float(np.max(abs(fit.fun)))
    return {'noise_on': float(fit.x[0]), 'noise_retain': float(fit.x[1]),
            'target_signal_time': float(target[0]), 'target_activation_count': float(target[1]),
            'relative_error': error, 'success': bool(fit.success and error <= tolerance),
            'function_evaluations': fit.nfev, 'entropy_used': False,
            'matching': 'pooled two-root T64 occupancy/activation, zero coupling only'}
