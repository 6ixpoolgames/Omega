"""Parameters and state helpers for material that can enter inaccessible D."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Literal


@dataclass(frozen=True)
class MaterialSink:
    enabled: bool = True
    mode: Literal['reversible', 'absorbing'] = 'reversible'
    rate: float = .04
    energy: float = -6.
    exposure: tuple[float, float, float] = (1., 1., 1.)
    boundary: str = 'idealized_inaccessible_product'

    def __post_init__(self):
        object.__setattr__(self, 'exposure', tuple(self.exposure))
        if type(self.enabled) is not bool:
            raise ValueError('enabled must be boolean')
        if self.mode not in ('reversible', 'absorbing'):
            raise ValueError("mode must be 'reversible' or 'absorbing'")
        if not isfinite(self.rate) or self.rate < 0:
            raise ValueError('sink rate must be finite and nonnegative')
        if not isfinite(self.energy):
            raise ValueError('D energy must be finite')
        if len(self.exposure) != 3 or any(not isfinite(c) or c < 0 for c in self.exposure):
            raise ValueError('exposure must give finite nonnegative P, W, A coefficients')
        if self.mode == 'absorbing' and not self.boundary:
            raise ValueError('absorbing mode must declare its boundary interpretation')


def precursor(state, inventory):
    """Free P count in one local ``(w,a,d,f,g)`` state."""
    w, a, d, _f, _g = state
    return inventory - w - a - d


def usable(state, inventory):
    """Material count still in the P/W/A accessible classes."""
    return inventory - state[2]


def local_energy(state, e_d=-6.):
    w, a, d, f, _g = state
    return w + 2 * a + e_d * d + 2 * f
