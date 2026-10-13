"""Actuation availability and policy-free basal gate relaxation."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite

from ..contracts import Event, RuleModule


@dataclass(frozen=True)
class ActuationSpec:
    mode: str = 'legacy'
    basal_rate: float = 0.

    def __post_init__(self):
        if self.mode not in ('legacy', 'embodied'):
            raise ValueError("actuation mode must be 'legacy' or 'embodied'")
        if not isfinite(self.basal_rate) or self.basal_rate < 0:
            raise ValueError('basal gate rate must be finite and nonnegative')

    def availability(self, active: int, capacity: int) -> float:
        if capacity <= 0 or not 0 <= active <= capacity:
            raise ValueError('Invalid actuation capacity or active apparatus')
        return active / capacity if self.mode == 'embodied' else 1.


def events(state, spec: ActuationSpec):
    """Independent symmetric gate relaxation; it consumes no fuel or energy."""
    if spec.basal_rate == 0:
        return ()
    out = []
    for c, local in enumerate(state):
        target = [list(x) for x in state]
        target[c][4] = 1 - local[4]
        out.append(Event('actuation-gate-relaxation', 'gate_relaxation',
                         tuple(tuple(x) for x in target), spec.basal_rate,
                         (c,), 0., {}))
    return tuple(out)


def module(spec: ActuationSpec):
    if spec.basal_rate == 0:
        return None
    return RuleModule('actuation', '1', lambda state: events(state, spec),
                      requires=('gate',), provides=('basal-gate-relaxation',))


def metadata(spec: ActuationSpec):
    return asdict(spec)
