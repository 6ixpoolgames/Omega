"""Event and deadline readouts for externally specified material shocks.

These are mechanism diagnostics. They do not assign a share of native history
entropy to a shock family.
"""
from __future__ import annotations

import numpy as np
from scipy.sparse.linalg import expm_multiply


def _distribution(occupancy, n):
    p = np.asarray(occupancy, dtype=float)
    if p.shape != (n,) or not np.all(np.isfinite(p)) or np.any(p < -1e-12):
        raise ValueError("occupancy must be a finite nonnegative vector matching model states")
    if abs(float(p.sum()) - 1.0) > 1e-10:
        raise ValueError("occupancy must be normalized")
    return np.maximum(p, 0.) / p.sum()


def shock_readout(model, occupancy, structural_closure):
    """Return occupancy-weighted shock fluxes and closure-transition rates.

    ``model`` is the compiled finite model (with ``states`` and ``world``).
    ``structural_closure`` is a boolean mask indexed by its full state list.
    The occupancy can be a stationary mixture over recurrent classes, provided
    it is expressed on that same full state list.
    """
    states = model['states']
    n = len(states)
    p = _distribution(occupancy, n)
    closed = np.asarray(structural_closure, dtype=bool)
    if closed.shape != (n,):
        raise ValueError("structural_closure must be a boolean mask matching model states")
    modules = [m for m in model['world'].modules if m.id == 'shocks']
    if len(modules) != 1:
        raise ValueError("model world must contain exactly one module with id='shocks'")
    module = modules[0]
    idx = model.get('index', {s: i for i, s in enumerate(states)})
    active = np.asarray([sum(local[1] for local in s) for s in states], dtype=float)
    by_state = np.zeros(n)
    function_loss = np.zeros(n)
    any_active_decrease = np.zeros(n)
    closure_flux = np.zeros(n)
    expected_hits = np.zeros(n)
    exposed = np.asarray([sum(local[0] + local[1] for local in s) for s in states], dtype=float)
    for i, state in enumerate(states):
        events = [e for e in module.events(state) if e.family.startswith('shock') and e.rate > 0]
        for event in events:
            j = idx[event.target]
            by_state[i] += event.rate
            expected_hits[i] += event.rate * (
                event.increments.get('shock_active_hits', 0.) +
                event.increments.get('shock_worn_hits', 0.))
            if active[i] > 0 and active[j] == 0:
                function_loss[i] += event.rate
            if active[i] > active[j]:
                any_active_decrease[i] += event.rate
            if not closed[i] and closed[j]:
                closure_flux[i] += event.rate

    metadata = model.get('metadata', model['world'].metadata)
    config = metadata.get('shocks', {})
    if hasattr(config, '__dict__'):
        config = vars(config)
    mode = config.get('mode', 'independent') if isinstance(config, dict) else 'independent'
    hazard = float(config.get('hazard', 0.)) if isinstance(config, dict) else 0.
    p_hit = float(config.get('p', 1.)) if isinstance(config, dict) else 1.
    clock_rate = (hazard / p_hit if mode == 'correlated' and p_hit > 0 and hazard > 0
                  else None)
    denominator_weight = p * (active > 0)
    active_mass = float(denominator_weight.sum())
    result = {
        'mode': mode,
        'event_rate': float(p @ by_state),
        'event_rate_given_active': float(denominator_weight @ by_state / active_mass) if active_mass else None,
        'expected_hits_per_time': float(p @ expected_hits),
        'exposed_expected': float(p @ exposed),
        'shock_event_closes_open_rate': float(p @ closure_flux),
        'shock_event_closes_open_rate_given_open': (
            float((p * (~closed)) @ closure_flux / max(float(p @ (~closed)), 1e-300))
            if float(p @ (~closed)) > 0 else None),
        'function_loss_event_flux_given_pre_active': (
            float(denominator_weight @ function_loss / active_mass) if active_mass else None),
        'any_active_decrease_event_flux_given_pre_active': (
            float(denominator_weight @ any_active_decrease / active_mass)
            if active_mass else None),
        'active_before_mass': active_mass,
        'open_before_mass': float(p @ (~closed)),
        'active_loss_denominator': 'shock-event intensity conditional on pre-event active count > 0',
        'closure_denominator': 'shock-event intensity from structurally open pre-event states',
        'correlated_clock_rate': clock_rate,
    }
    if mode == 'correlated' and clock_rate is not None:
        # Event enumeration omits the (0,0) binomial outcome.  Put its mass
        # back as the identity channel when reporting per-arrival loss risk.
        result['function_loss_probability_per_clock_arrival_given_pre_active'] = (
            float(denominator_weight @ function_loss / (clock_rate * active_mass))
            if active_mass else None)
        result['shock_event_probability_per_clock_arrival'] = float(p @ by_state / clock_rate)
        result['identity_probability_per_clock_arrival_stationary'] = max(
            0., 1. - result['shock_event_probability_per_clock_arrival'])
    else:
        event_flux = float(denominator_weight @ by_state)
        loss_flux = float(denominator_weight @ function_loss)
        result['function_loss_probability_per_event_given_pre_active'] = (
            loss_flux / event_flux if event_flux > 0 else None)
        result['event_denominator'] = 'state-changing shock events; independent mode has no common clock'
    if mode == 'correlated' and clock_rate is None:
        result['function_loss_probability_per_clock_arrival_given_pre_active'] = None
        result['shock_event_probability_per_clock_arrival'] = None
        result['identity_probability_per_clock_arrival_stationary'] = None
    return result


def deadline_function_readout(model, occupancy, horizon, structural_closure):
    """Exact endpoint function-loss and active reserve under the full generator."""
    if not np.isfinite(horizon) or horizon < 0:
        raise ValueError("horizon must be finite and nonnegative")
    states = model['states']
    p0 = _distribution(occupancy, len(states))
    p1 = np.asarray(expm_multiply(model['Q'].T * float(horizon), p0), dtype=float)
    p1 = np.maximum(p1, 0.)
    p1 /= p1.sum()
    active = np.asarray([sum(local[1] for local in s) for s in states], dtype=float)
    closed = np.asarray(structural_closure, dtype=bool)
    if closed.shape != (len(states),):
        raise ValueError("structural_closure must be a boolean mask matching model states")
    function_loss = float(p1[active == 0].sum())
    return {
        'horizon': float(horizon),
        'function_loss_probability': function_loss,
        'function_reserve_probability': 1. - function_loss,
        'function_survival_probability': float(p1[active > 0].sum()),
        'expected_active_reserve': float(p1 @ active),
        'expected_active_reserve_given_function_survival': (
            float(p1 @ active / p1[active > 0].sum()) if p1[active > 0].sum() else None),
        'structural_closure_probability': float(p1[closed].sum()),
    }
