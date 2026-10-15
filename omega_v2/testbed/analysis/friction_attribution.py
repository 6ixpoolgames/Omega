"""Native D-coordinate activity, grouped by physical outcome before attribution.

This is a fine-time conditional diagnostic, not the entropy of the marginal
D history. Shared destinations are apportioned by declared rate responsibility;
the family name never creates an additional physical distinction.
"""
import numpy as np
from ..domination_friction import D_FIELDS, projection


def activity_rows(world):
    n = len(world.states)
    rows = {kind: {name: np.zeros(n) for name in ('jumps', 'finite_bits', 'mark_bits')}
            for kind in ('friction', 'capture', 'other')}
    for i, state in enumerate(world.states):
        outcomes = {}
        origin = projection(state, D_FIELDS)
        for module in world.modules:
            for event in module.events(state):
                destination = projection(event.target, D_FIELDS)
                if destination == origin or event.rate <= 0:
                    continue
                family = ('friction' if event.family.startswith('friction.') else
                          'capture' if event.family == 'D.capture' else 'other')
                group = outcomes.setdefault(destination, {})
                group[family] = group.get(family, 0.)+event.rate
        total = sum(sum(x.values()) for x in outcomes.values())
        for sources in outcomes.values():
            rate = sum(sources.values())
            for family, part in sources.items():
                rows[family]['jumps'][i] += part
                rows[family]['finite_bits'][i] += part*(np.log2(np.e)-np.log2(rate))
                rows[family]['mark_bits'][i] += part*np.log2(total/rate)
    return rows


def integrate(rows, occupation):
    return {'families': {family: {k: float(occupation @ v) for k, v in values.items()}
                         for family, values in rows.items()},
            'reference_time': 1.,
            'definition': 'native D outcome rates conditioned on full physical state',
            'allocation': 'aggregate identical D destinations first; allocate by rate responsibility',
            'is_marginal_D_history_entropy': False,
            'is_random_length_jump_history_entropy': False}
