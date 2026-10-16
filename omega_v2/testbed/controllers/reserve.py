"""Memoryless spectator-count controllers for native paired gate reactions."""
from __future__ import annotations

from dataclasses import asdict, dataclass

RESPONSES = {
    'idle': (0., 0.), 'service': (1., 0.), 'mix25': (.75, .25),
    'mix50': (.5, .5), 'mix75': (.25, .75), 'export': (0., 1.),
}


@dataclass(frozen=True)
class ReservePolicy:
    id: str
    threshold: int = 1
    surplus: str = 'service'
    service_if_worn: bool = False
    observation: str = 'local-active-worn-counts'
    version: str = '1'

    def __post_init__(self):
        if type(self.threshold) is not int or self.threshold < 1:
            raise ValueError('Positive integer reserve threshold required')
        if self.surplus not in RESPONSES:
            raise ValueError('Unknown native response')
        if type(self.service_if_worn) is not bool:
            raise ValueError('Worn response must be boolean')
        if self.observation != 'local-active-worn-counts':
            raise ValueError('Fuel/gate/foreign feedback needs a physical mechanism')
        if not self.id:
            raise ValueError('Stable policy ID required')

    def response(self, local):
        w, a, _d, _f, _gate = local
        if a == 0:
            return RESPONSES['idle']
        if a < self.threshold or (self.service_if_worn and w > 0):
            return RESPONSES['service']
        return RESPONSES[self.surplus]

    def manifest(self):
        return asdict(self)

    def audit_vector(self, capacity):
        """Full feasible (active,worn) surface, independent of occupancy."""
        return [{'active': a, 'worn': w, 'response': list(self.response((w,a,0,0,0)))}
                for a in range(capacity+1) for w in range(capacity-a+1)]


def candidate_family(max_capacity=3):
    """Six constant controls plus complete threshold/surplus/worn coverage."""
    if type(max_capacity) is not int or max_capacity < 1:
        raise ValueError('Positive capacity required')
    policies = [ReservePolicy('constant-'+name, surplus=name) for name in RESPONSES]
    for k in range(2, max_capacity+1):
        for name in ('mix25', 'mix50', 'mix75', 'export'):
            policies.append(ReservePolicy(f'reserve-{k}-{name}', k, name))
            policies.append(ReservePolicy(f'reserve-{k}-{name}-worn-service', k, name, True))
    if len(policies) > 48:
        raise ValueError('Family exceeds initial declared candidate cap')
    return tuple(policies)
