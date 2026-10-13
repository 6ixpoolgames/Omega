"""External matched shocks on the active and worn material pools."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import comb, isfinite
from typing import Literal

from ..contracts import Event, RuleModule


@dataclass(frozen=True)
class ShockSpec:
    enabled: bool = False
    mode: Literal['independent', 'correlated'] = 'independent'
    hazard: float = 0.0
    p: float = 1.0

    def __post_init__(self):
        if type(self.enabled) is not bool:
            raise ValueError('enabled must be boolean')
        if self.mode not in ('independent', 'correlated'):
            raise ValueError("mode must be 'independent' or 'correlated'")
        if not isfinite(self.hazard) or self.hazard < 0:
            raise ValueError('hazard must be finite and nonnegative')
        if not isfinite(self.p) or not 0 < self.p <= 1:
            raise ValueError('p must be finite and in (0, 1]')

    @property
    def intensity(self):
        return self.hazard / self.p


def _energy_delta(k_active, k_worn, trapenergy):
    # A->W changes energy by -1; W->D changes it by trapenergy-1.
    return -k_active + (trapenergy - 1.) * k_worn


def events(state, inventories, spec: ShockSpec, trapenergy=-6.):
    """Enumerate shock outcomes for two local ``(w,a,d,f,g)`` states."""
    if not spec.enabled or spec.hazard == 0:
        return ()
    if len(state) != 2 or len(inventories) != 2:
        raise ValueError('Shocks require two local states and inventories')
    if not isfinite(trapenergy):
        raise ValueError('trapenergy must be finite')
    out = []
    nu = spec.intensity
    for (w, a, d, f, g), inventory in zip(state, inventories):
        if min(w, a, d, f, g) < 0 or w + a + d > inventory:
            raise ValueError('Invalid local material/carrier state')
    if spec.mode == 'independent':
        for c, (w, a, d, f, g) in enumerate(state):
            channels = ((1, 0, 'active', a), (0, 1, 'worn', w))
            for ka, kw, label, n in channels:
                if n == 0:
                    continue
                target_local = (w + ka - kw, a - ka, d + kw, f, g)
                target = list(state); target[c] = target_local; target = tuple(target)
                delta = _energy_delta(ka, kw, trapenergy)
                increments = {'shock_active_hits': float(ka),
                              'shock_worn_hits': float(kw),
                              'shock_events': 1.,
                              'shock_energy_transfer': delta}
                if kw:
                    increments['gross_built_loss'] = float(kw)
                out.append(Event(f'shock-{label}', f'shock_{label}', target,
                                 spec.hazard * n, (c,), work=delta, increments=increments))
    else:
        # One common arrival acts on both compartments. Each of the four
        # pre-event pools is thinned independently conditional on that arrival.
        pools = tuple(count for local in state for count in (local[1], local[0]))
        distributions = [tuple((k, comb(n, k) * spec.p**k * (1-spec.p)**(n-k))
                               for k in range(n+1)) for n in pools]
        for marks in product(*distributions):
            (a0, pa0), (w0, pw0), (a1, pa1), (w1, pw1) = marks
            if a0 + w0 + a1 + w1 == 0:
                continue
            rate = nu * pa0 * pw0 * pa1 * pw1
            if rate == 0:
                continue
            target = []
            for c, (w, a, d, f, g) in enumerate(state):
                ka, kw = (a0, w0) if c == 0 else (a1, w1)
                target.append((w + ka - kw, a - ka, d + kw, f, g))
            target = tuple(target)
            ka_total, kw_total = a0 + a1, w0 + w1
            delta = _energy_delta(ka_total, kw_total, trapenergy)
            increments = {'shock_active_hits': float(ka_total),
                          'shock_worn_hits': float(kw_total),
                          'shock_events': 1.,
                          'shock_energy_transfer': delta}
            if kw_total:
                increments['gross_built_loss'] = float(kw_total)
            support = tuple(c for c, (before, after) in enumerate(zip(state, target))
                            if before != after)
            out.append(Event('shock-correlated', 'shock_correlated', target,
                             rate, support, work=delta, increments=increments))
    return tuple(out)


def module(inventories, spec: ShockSpec, trapenergy=-6.):
    inventories = tuple(inventories)
    if len(inventories) != 2 or any(type(m) is not int or m < 1 for m in inventories):
        raise ValueError('Two positive integer compartment inventories required')
    return RuleModule(
        id='shocks',
        version='1', events=lambda state: events(state, inventories, spec, trapenergy),
        requires=('material-PWA-D',), provides=('matched-shock-events',))
