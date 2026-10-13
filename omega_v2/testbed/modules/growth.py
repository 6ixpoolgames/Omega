"""Legacy growing-population law adapted to the five-coordinate material state."""
from __future__ import annotations

from dataclasses import asdict
from itertools import product
from math import comb, exp, factorial, isfinite

from .. import growing_population as g
from ..contracts import Event, RuleModule, WorldSpec
from .actuation import ActuationSpec, module as actuation_module
from .shocks import ShockSpec, module as shocks_module
from .damage import module as damage_module
from .material_sink import MaterialSink, local_energy, precursor
from ..controllers.reserve import ReservePolicy


def _inventory(inventories):
    if type(inventories) is int:
        inventories = (inventories, inventories)
    inv = tuple(inventories)
    if len(inv) != 2 or any(type(m) is not int or m < 1 for m in inv):
        raise ValueError('Two positive integer compartment inventories required')
    return inv


def _policy(policy):
    if policy is None:
        return ((0., 0.),) * 4
    if len(policy) != 4:
        raise ValueError('Four local inactive/active service/export responses required')
    out = []
    for response in policy:
        pair = (1-response, response) if isinstance(response, (int, float)) else tuple(response)
        if (len(pair) != 2 or any(not isfinite(v) or v < 0 for v in pair)
                or sum(pair) > 1 + 1e-12):
            raise ValueError('Invalid service/export response')
        out.append(tuple(map(float, pair)))
    return tuple(out)


def _states(inventories):
    local = [[(w, a, d, f, gate)
              for w in range(m+1) for a in range(m-w+1)
              for d in range(m-w-a+1) for f in range(m+1) for gate in (0, 1)]
             for m in inventories]
    yield from product(*local)


def _validate(state, inventories):
    if not isinstance(state, tuple) or len(state) != 2:
        raise ValueError('Two-compartment state required')
    for m, x in zip(inventories, state):
        if not isinstance(x, tuple) or len(x) != 5 or any(type(v) is not int for v in x):
            raise ValueError('Integer local (w,a,d,f,g) state required')
        w, a, d, f, gate = x
        if min(w, a, d, f) < 0 or w+a+d > m or f > m or gate not in (0, 1):
            raise ValueError('Invalid local material/carrier state')


def _energy(state, sink):
    return sum(local_energy(x, sink.energy) for x in state)


def _degeneracy(state, inventories):
    value = 1
    for m, (w, a, d, f, _gate) in zip(inventories, state):
        p = m-w-a-d
        value *= factorial(m)//(factorial(p)*factorial(w)*factorial(a)*factorial(d))*comb(m, f)
    return value


def _growth_events(state, inventories, policy, params, actuation):
    def emit(c, family, target, rate, work=0., increments=None):
        if rate == 0:
            return
        if rate < 0 or not isfinite(rate):
            raise ArithmeticError(f'Invalid {family} rate')
        changed = tuple(i for i, (before, after) in enumerate(zip(state, target)) if before != tuple(after))
        fuel_debit = -sum(target[i][3] - state[i][3] for i in range(2))
        ledger = dict(increments or {})
        if family.startswith('switch'):
            ledger['switches'] = ledger.get('switches', 0.) + 1.
            ledger['gross_switch_fuel'] = ledger.get('gross_switch_fuel', 0.) + max(0., fuel_debit)
            ledger['net_switch_fuel'] = ledger.get('net_switch_fuel', 0.) + fuel_debit
        if family in ('basal_build', 'assisted_birth', 'repair'):
            ledger['gross_service_fuel'] = ledger.get('gross_service_fuel', 0.) + max(0., fuel_debit)
            ledger['net_service_fuel'] = ledger.get('net_service_fuel', 0.) + fuel_debit
        out.append(Event(f'growth-{family}', family, tuple(tuple(x) for x in target),
                         float(rate), changed, float(work), ledger))

    out = []
    for c, (w, a, d, f, gate) in enumerate(state):
        m = inventories[c]
        p = precursor((w, a, d, f, gate), m)
        def change(dw=0, da=0, dd=0, df=0, dg=0):
            target = [list(x) for x in state]
            for j, delta in enumerate((dw, da, dd, df, dg)):
                target[c][j] += delta
            return target

        command_factor = actuation.availability(a, m)

        if p: emit(c, 'disassembly', change(dw=1), params.disassembly*p*exp(-.5),
                   increments={'gross_thermal_reconstruction': 1.})
        if w: emit(c, 'disassembly', change(dw=-1), params.disassembly*w*exp(.5),
                   increments={'gross_built_loss': 1.})
        if w: emit(c, 'wear', change(dw=-1, da=1), params.wear*w*exp(-.5))
        if a: emit(c, 'wear', change(dw=1, da=-1), params.wear*a*exp(.5))

        capture = params.capture*(1+(params.capture_benefit-1)*a/m)
        if f < m:
            emit(c, 'drive_charge', change(df=1), capture*(m-f)*exp((params.chemical_potential-2)/2),
                 params.chemical_potential)
            emit(c, 'bath_charge', change(df=1), params.fuel_bath*(m-f)*exp(-1))
        if f:
            emit(c, 'drive_charge', change(df=-1), capture*f*exp(-(params.chemical_potential-2)/2),
                 -params.chemical_potential)
            emit(c, 'bath_charge', change(df=-1), params.fuel_bath*f*exp(1))

        if gate == 0:
            if p and f:
                emit(c, 'basal_build', change(da=1, df=-1), params.build*p*f/m,
                     increments={'gross_basal_birth': 1.})
                if a:
                    emit(c, 'assisted_birth', change(da=1, df=-1),
                         params.assisted_birth*p*a*f/(m*m),
                         increments={'gross_assisted_birth': 1.})
            if a and f < m:
                emit(c, 'basal_build', change(da=-1, df=1), params.build*a*(m-f)/m,
                     increments={'gross_built_loss': 1.})
                if a >= 2:
                    emit(c, 'assisted_birth', change(da=-1, df=1),
                         params.assisted_birth*a*(a-1)*(m-f)/(m*m),
                         increments={'gross_built_loss': 1.})
            if w and f:
                emit(c, 'repair', change(dw=-1, da=1, df=-1), params.repair*w*f/m*exp(.5))
            if a and f < m:
                emit(c, 'repair', change(dw=1, da=-1, df=1), params.repair*a*(m-f)/m*exp(-.5))

        service, export = (policy.response(state[c]) if isinstance(policy, ReservePolicy)
                           else policy[2*c+int(a > 0)])
        k = params.switch_tokens
        if k <= m:
            denom = comb(m, k)
            if gate == 0:
                if f >= k:
                    emit(c, 'switch_export', change(df=-k, dg=1),
                         params.switch*export*comb(f, k)/denom*exp(k)*command_factor)
                if f+k <= m:
                    emit(c, 'switch_service', change(df=k, dg=1),
                         params.switch*service*comb(m-f, k)/denom*exp(-k)*command_factor)
            else:
                if f >= k:
                    emit(c, 'switch_service', change(df=-k, dg=-1),
                         params.switch*service*comb(f, k)/denom*exp(k)*command_factor)
                if f+k <= m:
                    emit(c, 'switch_export', change(df=k, dg=-1),
                         params.switch*export*comb(m-f, k)/denom*exp(-k)*command_factor)

    open_gates = sum(x[4] for x in state)
    if open_gates:
        for c in (0, 1):
            other = 1-c
            fc, fo = state[c][3], state[other][3]
            if fc and fo < inventories[other]:
                target = [list(x) for x in state]
                target[c][3] -= 1; target[other][3] += 1
                emit(c, 'exchange', target,
                     params.exchange*open_gates*fc/inventories[c]*(inventories[other]-fo)/inventories[other])
    return tuple(out)


def build_world(inventories=(1, 1), policy=None, params=g.DEFAULT, damage=None,
                max_states=10000, actuation=None, shocks=None):
    """Build a finite versioned growth world with optional material damage.

    State coordinates are per compartment ``(w,a,d,f,g)``. Disabled damage
    still uses this adapter's extended state schema, with ``d`` constrained to 0.
    """
    inv = _inventory(inventories)
    responses = policy if isinstance(policy, ReservePolicy) else _policy(policy)
    sink = damage if damage is not None else MaterialSink(enabled=False)
    if not isinstance(sink, MaterialSink):
        raise TypeError('damage must be a MaterialSink configuration')
    actuator = actuation if actuation is not None else ActuationSpec()
    shock = shocks if shocks is not None else ShockSpec()
    if not isinstance(shock,ShockSpec):raise TypeError('shocks must be a ShockSpec configuration')
    if shock.enabled and shock.hazard>0 and not sink.enabled:
        raise ValueError('Shock W->D requires declared material-D state and energy')
    if not isinstance(actuator, ActuationSpec):
        raise TypeError('actuation must be an ActuationSpec configuration')
    if isinstance(responses, ReservePolicy) and actuator.mode != 'embodied':
        raise ValueError('Reserve policies require embodied actuation')
    count = 1
    for m in inv:
        count *= ((m+1)*(m+2)//2*(m+1)*2 if not sink.enabled
                  else comb(m+3, 3)*(m+1)*2)
    if count > max_states:
        raise RuntimeError('State cap; physical law was not truncated')
    if not sink.enabled:
        # Preserve exact legacy state size when the extension is off.
        local = [[(w, a, 0, f, gate) for w in range(m+1) for a in range(m-w+1)
                  for f in range(m+1) for gate in (0, 1)] for m in inv]
        state_iter = product(*local)
    else:
        state_iter = _states(inv)
    states = tuple(state_iter)

    def validate(state):
        _validate(state, inv)
        if not sink.enabled and any(x[2] for x in state):
            raise ValueError('D coordinate must remain zero when material sink is disabled')

    def energy(state): return _energy(state, sink)
    def built(state): return sum(w+a for w, a, d, f, gate in state)
    def active(state): return sum(x[1] for x in state)
    def usable(state): return sum(m-x[2] for m, x in zip(inv, state))
    def fuel(state): return sum(x[3] for x in state)
    def lost(state): return sum(x[2] for x in state)
    growth_version = ('4' if isinstance(responses, ReservePolicy) else
                      '3' if actuator.mode == 'embodied' else '2')
    modules = [RuleModule('growth', growth_version,
                          lambda state: _growth_events(state, inv, responses, params, actuator),
                          requires=('material-PWA-D',),
                          provides=('growth-events',))]
    modules.append(damage_module(inv, sink))
    modules.append(shocks_module(inv,shock,sink.energy))
    gate_module = actuation_module(actuator)
    if gate_module is not None:
        modules.append(gate_module)
    fields = ('material-PWA-D', 'local-fuel', 'gate', 'controller')
    metadata = {'inventory': inv, 'inventories': inv, 'carrier_capacities': inv,
                'parameters': asdict(params), 'params': asdict(params),
                'policy': responses.manifest() if isinstance(responses, ReservePolicy) else responses,
                'material_sink': asdict(sink), 'damage': asdict(sink),
                'actuation': asdict(actuator),
                'shocks': asdict(shock),
                'boundary_assumption': sink.boundary if sink.enabled and sink.mode == 'absorbing' else None,
                'fields': fields}
    return WorldSpec('growing-population-with-material-D', '2', states, validate, energy,
                     {'energy': energy, 'built': built, 'active': active, 'usable': usable,
                      'fuel': fuel, 'damage': lost}, tuple(modules), metadata,
                     degeneracy=lambda state: _degeneracy(state, inv))
