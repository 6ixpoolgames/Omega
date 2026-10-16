"""Fractional physical energy expressed by exact lattice coordinates."""
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import isfinite


def rational(value):
    if isinstance(value, bool):
        raise ValueError('Energy must be a number, not boolean')
    try:
        result = value if isinstance(value, Fraction) else Fraction(str(value))
    except (ValueError, TypeError, ZeroDivisionError) as error:
        raise ValueError('Finite rational energy required') from error
    if not isfinite(float(result)):
        raise ValueError('Finite energy required')
    return result


@dataclass(frozen=True)
class EnergyGrid:
    capacity: object
    quantum: object = 1

    def __post_init__(self):
        object.__setattr__(self, 'capacity', rational(self.capacity))
        object.__setattr__(self, 'quantum', rational(self.quantum))
        if self.capacity <= 0 or self.quantum <= 0:
            raise ValueError('Positive energy capacity and quantum required')
        maximum = self.ticks(self.capacity)
        object.__setattr__(self, '_maximum', maximum)
        object.__setattr__(self, '_values', tuple(float(i*self.quantum) for i in range(maximum+1)))

    @lru_cache(maxsize=1024)
    def ticks(self, energy):
        ratio = rational(energy)/self.quantum
        value = round(ratio)
        # Admit only machine representation error, not a different physical bill.
        if abs(float(ratio)-value) > 1e-12*max(1, abs(value)):
            raise ValueError('Energy does not align with the declared quantum')
        if value < 0:
            raise ValueError('Nonnegative energy required')
        return int(value)

    @property
    def maximum(self):
        return self._maximum

    def energy(self, ticks):
        if type(ticks) is not int or not 0 <= ticks <= self.maximum:
            raise ValueError('Invalid stored-energy coordinate')
        return self._values[ticks]
