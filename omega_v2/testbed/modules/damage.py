"""Finite-barrier or absorbing material transfers into the D compartment."""
from __future__ import annotations

from math import exp, isfinite

from ..contracts import Event, RuleModule
from .material_sink import MaterialSink

_SPECIES = ('P', 'W', 'A')
_ENERGY = {'P': 0., 'W': 1., 'A': 2.}


def events(state, inventories, config: MaterialSink):
    if not config.enabled or config.rate == 0:
        return ()
    out = []
    for c, (w, a, d, f, g) in enumerate(state):
        counts = (inventories[c] - w - a - d, w, a)
        for species, n, exposure in zip(_SPECIES, counts, config.exposure):
            if not exposure:
                continue
            if n:
                target = [list(x) for x in state]
                target[c][2] += 1
                if species == 'W': target[c][0] -= 1
                elif species == 'A': target[c][1] -= 1
                inc = {f'gross_sink_from_{species}': 1., 'gross_sink_to_D': 1.}
                if species in ('W', 'A'):
                    inc['gross_built_loss'] = 1.
                out.append(Event('material-damage', f'sink_{species.lower()}',
                                 tuple(tuple(x) for x in target), config.rate*exposure*n,
                                 (c,), increments=inc))
            if config.mode == 'reversible' and d:
                exponent = config.energy - _ENERGY[species]
                try:
                    reverse_factor = exp(exponent)
                except OverflowError as exc:
                    raise ArithmeticError('Material return rate overflow') from exc
                if reverse_factor == 0. or not isfinite(reverse_factor):
                    raise ArithmeticError('Material return rate underflow/overflow; reversible channel cannot be silently closed')
                reverse_rate = config.rate*exposure*d*reverse_factor
                if reverse_rate == 0. or not isfinite(reverse_rate):
                    raise ArithmeticError('Material return rate product underflow/overflow; reversible channel cannot be silently closed')
                target = [list(x) for x in state]
                target[c][2] -= 1
                if species == 'W': target[c][0] += 1
                elif species == 'A': target[c][1] += 1
                inc = {f'gross_sink_return_to_{species}': 1.,
                       'gross_sink_return_to_built': float(species in ('W', 'A')),
                       'gross_sink_return_to_active': float(species == 'A')}
                out.append(Event('material-damage', f'return_{species.lower()}',
                                 tuple(tuple(x) for x in target),
                                 reverse_rate, (c,), increments=inc))
    return tuple(out)


def module(inventories, config: MaterialSink):
    return RuleModule(
        id=f'material-sink-{config.mode}' if config.enabled else 'material-sink-disabled',
        version='1', events=lambda state: events(state, inventories, config),
        requires=('material-PWA-D',), provides=('material-damage-events',))
