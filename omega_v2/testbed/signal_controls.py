"""Physical controls for register variation, tracking and blocked response.

Wrap the original signal adapter without changing its legacy generators.
No new action labels, semantic rewards or hidden observer clocks.
"""
from dataclasses import replace

import numpy as np
from scipy.optimize import least_squares

from .analysis.signal_readouts import occupation_integral
from .aversive_signals import SignalParameters
from .aversive_signals import build_world as original_world
from .compiler import compile_world
from .contracts import RuleModule


def build_world(arm, parameters=None, on_rate=None, off_rate=None):
    p = parameters or SignalParameters()
    if arm not in ('B', 'A', 'A0', 'B_R'):
        raise ValueError('Unknown register control')
    if arm == 'B_R':
        if on_rate is None or off_rate is None or on_rate <= 0 or off_rate <= 0:
            raise ValueError('Positive independent switching rates required')
        p = replace(p, signal_hijack=on_rate, signal_off=off_rate)
    elif on_rate is not None or off_rate is not None:
        raise ValueError('Independent switching rates apply only to B_R')
    native = original_world('D' if arm == 'B_R' else ('B' if arm == 'B' else 'A'), p)
    normal = original_world('B', p)

    def events(state):
        if arm in ('A', 'B'):
            for module in native.modules:
                yield from module.events(state)
            return
        # Injury/independent activation, charging, upkeep and environment remain
        # native. Only the behavioural reading of the bit is disconnected.
        for module in native.modules:
            for event in module.events(state):
                if not event.family.startswith(('escape_', 'forage_')):
                    yield event
        for module in normal.modules:
            for event in module.events(state):
                if event.family.startswith(('escape_', 'forage_')):
                    # Both controls are blocked. D's default escape availability
                    # is not imported into the B_R motor pathway.
                    yield event

    metadata = dict(native.metadata)
    metadata.update({'arm': arm, 'escape_available': False,
                     'behaviour_reads_signal': arm == 'A',
                     'control_mode': 'unvarying' if arm == 'B' else
                         ('blocked-response' if arm == 'A' else
                          'tracking-without-response' if arm == 'A0' else 'independent-flicker'),
                     'signal_is_dynamically_decoupled': False,
                     'cost_coupling': 'charging and upkeep share the valuer energy store'})
    return replace(native, id=f'register-control-{arm}', version='1',
                   modules=(RuleModule('register-control', '1', events),), metadata=metadata)


def moments(compiled, root, horizon):
    """Continuous-time occupancy and physical state-change flux; no entropy."""
    final, occupation = occupation_integral(compiled['Q'], root, horizon)
    states = compiled['states']
    signal = np.array([state[2] for state in states], dtype=float)
    flips = np.zeros(len(states))
    charges = np.zeros(len(states))
    for i, state in enumerate(states):
        for module in compiled['world'].modules:
            for event in module.events(state):
                if event.target[2] != state[2]:
                    flips[i] += event.rate
                charges[i] += event.rate*event.increments.get('signal_charge', 0.)
    return {'occupancy_time': float(occupation @ signal),
            'switch_count': float(occupation @ flips),
            'charging_energy': float(occupation @ charges),
            'upkeep_energy': float(occupation @ compiled['flows'].get(
                'signal_upkeep_bill', np.zeros(len(states)))),
            'signal_at_deadline': float(final @ signal)}


def calibrate(parameters, root_state, horizon=64., relative_tolerance=1e-6):
    """Match A's two physical moments. Scientific lushness is never evaluated."""
    source = compile_world(build_world('A', parameters))
    target = moments(source, source['index'][tuple(root_state)], horizon)
    values = np.array([target['occupancy_time'], target['switch_count']])
    if values.min() <= 0:
        raise ValueError('Positive matching targets required')
    evaluations = 0

    def residual(log_rates):
        nonlocal evaluations
        evaluations += 1
        on, off = np.exp(log_rates)
        compiled = compile_world(build_world('B_R', parameters, float(on), float(off)))
        observed = moments(compiled, compiled['index'][tuple(root_state)], horizon)
        return (np.array([observed['occupancy_time'], observed['switch_count']])-values)/values

    fit = least_squares(residual, np.log([.04, .3]), bounds=(-12., 4.),
                        xtol=1e-10, ftol=1e-10, gtol=1e-10, max_nfev=100)
    on, off = map(float, np.exp(fit.x))
    compiled = compile_world(build_world('B_R', parameters, on, off))
    achieved = moments(compiled, compiled['index'][tuple(root_state)], horizon)
    error = float(np.max(abs((np.array([achieved['occupancy_time'],
                                          achieved['switch_count']])-values)/values)))
    return {'success': bool(fit.success and error <= relative_tolerance),
            'on_rate': on, 'off_rate': off, 'target': target, 'achieved': achieved,
            'maximum_relative_error': error, 'evaluations': evaluations,
            'horizon': horizon, 'relative_tolerance': relative_tolerance,
            'fitted_using_lushness': False,
            'unit_charging_and_upkeep_bills_matched': True,
            'total_charging_energy_difference': achieved['charging_energy']-target['charging_energy'],
            'full_correlations_matched': False}
