"""Native site/bond/carrier geometry; identical particles, one law for all roots.

The carrier shares sites with matter but transports its charge locally. Pair
coefficients depend only on unchanged spectator bonds, so native forward/reverse
ratios follow the declared Hamiltonian even in the catalysed channels.
"""
from dataclasses import dataclass
from itertools import combinations, product
from math import exp, isfinite

from .contracts import Event, RuleModule, WorldSpec


@dataclass(frozen=True)
class LatticeParameters:
    sites: int = 6
    monomers: int = 4
    beta: float = 3.
    mobility: float = .5
    thermal_join: float = .001
    basal_build: float = .0001
    assisted_build: float = .02
    basal_capture: float = .002
    assisted_capture: float = .1
    supply: float = .6
    packet_exchange: float = .05
    charge_leak: float = .002
    upkeep: float = .01
    damage: float = .005

    def __post_init__(self):
        if type(self.sites) is not int or type(self.monomers) is not int:
            raise ValueError('Integer geometry required')
        if not 2 <= self.monomers < self.sites or self.sites < 4:
            raise ValueError('At least two monomers and a vacancy on a ring >=4')
        for key, value in vars(self).items():
            if not isfinite(value) or value < 0:
                raise ValueError(f'Invalid {key}')
        if min(self.beta, self.mobility, self.thermal_join, self.basal_build,
               self.basal_capture, self.packet_exchange, self.charge_leak) <= 0:
            raise ValueError('Positive native basal and reverse rates required')


def geometry(sites, monomers):
    """Occupancy and legal ring matchings, with no particle-ID multiplicity."""
    edges = tuple((i, (i+1) % sites) for i in range(sites))
    for positions in combinations(range(sites), monomers):
        occupied = sum(1 << i for i in positions)
        candidates = [i for i, (a, b) in enumerate(edges)
                      if occupied & (1 << a) and occupied & (1 << b)]
        for choice in range(1 << len(candidates)):
            bonds, used = 0, 0
            for bit, edge in enumerate(candidates):
                if choice & (1 << bit):
                    a, b = edges[edge]
                    pair = (1 << a) | (1 << b)
                    if pair & used:
                        break
                    bonds |= 1 << edge
                    used |= pair
            else:
                yield occupied, bonds


def build_world(parameters=None):
    p = parameters or LatticeParameters()
    edges = tuple((i, (i+1) % p.sites) for i in range(p.sites))
    geometries = tuple(geometry(p.sites, p.monomers))
    legal_geometry = set(geometries)
    states = tuple((occupied, bonds, carrier, charge, packet)
                   for occupied, bonds in geometries
                   for carrier, charge, packet in product(range(p.sites), range(3), range(2)))

    def distance(a, b):
        d = abs(a-b)
        return min(d, p.sites-d)

    def bond_list(bonds):
        return [i for i in range(p.sites) if bonds & (1 << i)]

    def near_count(bonds, site):
        return sum(min(distance(site, v) for v in edges[i]) <= 1 for i in bond_list(bonds))

    def assistants(bonds, edge):
        return sum(min(distance(a, b) for a in edges[edge] for b in edges[i]) <= 1
                   for i in bond_list(bonds) if i != edge)

    def validate(s):
        if len(s) != 5 or any(type(v) is not int for v in s):
            raise ValueError('Integer physical coordinates required')
        if ((s[0], s[1]) not in legal_geometry or not 0 <= s[2] < p.sites
                or s[3] not in (0, 1, 2) or s[4] not in (0, 1)):
            raise ValueError('Invalid matter/bond/carrier state')

    def energy(s):
        return float(s[1].bit_count()+s[3]+3*s[4])

    def event(s, target, rate, family, work=0., increments=None):
        return Event(family, family, target, rate,
                     tuple(i for i in range(5) if s[i] != target[i]), work, increments or {})

    def diffusion(s):
        occupied, bonds, carrier, charge, packet = s
        used = 0
        for i in bond_list(bonds):
            a, b = edges[i]
            pair = (1 << a) | (1 << b)
            used |= pair
            for direction in (-1, 1):
                new_edge = (i+direction) % p.sites
                c, d = edges[new_edge]
                moved = (1 << c) | (1 << d)
                if moved & (occupied ^ pair):
                    continue
                target = ((occupied ^ pair) | moved,
                          (bonds ^ (1 << i)) | (1 << new_edge), carrier, charge, packet)
                yield event(s, target, p.mobility/2, 'cluster_hop')
        free = occupied & ~used
        for a in range(p.sites):
            if not free & (1 << a):
                continue
            for direction in (-1, 1):
                b = (a+direction) % p.sites
                if not occupied & (1 << b):
                    yield event(s, (occupied ^ (1 << a) ^ (1 << b), bonds, carrier, charge, packet),
                                p.mobility, 'monomer_hop')
        for direction in (-1, 1):
            yield event(s, (occupied, bonds, (carrier+direction) % p.sites, charge, packet),
                        p.mobility, 'carrier_hop')

    def chemistry(s):
        occupied, bonds, carrier, charge, packet = s
        for i, (a, b) in enumerate(edges):
            other = bonds & ~(1 << i)
            if bonds & (1 << i):
                yield event(s, (occupied, other, carrier, charge, packet),
                            p.thermal_join*exp(p.beta/2), 'thermal_break')
                if charge == 0 and min(distance(carrier, v) for v in (a, b)) <= 1:
                    coefficient = p.basal_build+p.assisted_build*assistants(other, i)
                    yield event(s, (occupied, other, carrier, 2, packet),
                                coefficient*exp(-p.beta/2), 'paid_reverse',
                                increments={'returned_charge': 2., 'recycled_bond_energy': 1.,
                                            'reverse_bath_import': 1.})
                if p.damage:
                    yield event(s, (occupied, other, carrier, charge, packet),
                                p.damage, 'external_damage')
            elif (occupied, bonds | (1 << i)) in legal_geometry:
                yield event(s, (occupied, bonds | (1 << i), carrier, charge, packet),
                            p.thermal_join*exp(-p.beta/2), 'thermal_join')
                if charge == 2 and min(distance(carrier, v) for v in (a, b)) <= 1:
                    count = assistants(bonds, i)
                    coefficient = p.basal_build+p.assisted_build*count
                    yield event(s, (occupied, bonds | (1 << i), carrier, 0, packet),
                                coefficient*exp(p.beta/2), 'paid_join',
                                increments={'construction_charge': 2., 'assisted_join': float(count > 0)})

    def resource(s):
        occupied, bonds, carrier, charge, packet = s
        if packet:
            yield event(s, (occupied, bonds, carrier, charge, 0), p.packet_exchange, 'packet_decay')
        else:
            target = (occupied, bonds, carrier, charge, 1)
            yield event(s, target, p.packet_exchange*exp(-3*p.beta), 'packet_bath_return')
            if p.supply:
                yield event(s, target, p.supply, 'packet_inflow', work=3., increments={'accepted_work': 3.})
        if carrier != 0:
            return
        coefficient = p.basal_capture+p.assisted_capture*near_count(bonds, 0)
        if packet and charge == 0:
            yield event(s, (occupied, bonds, carrier, 2, 0), coefficient*exp(p.beta/2), 'capture',
                        increments={'captured_charge': 2.})
        elif not packet and charge == 2:
            yield event(s, (occupied, bonds, carrier, 0, 1), coefficient*exp(-p.beta/2), 'capture_reverse',
                        increments={'reverse_capture_charge': 2.})

    def maintenance(s):
        occupied, bonds, carrier, charge, packet = s
        coefficient = p.charge_leak+p.upkeep*near_count(bonds, carrier)
        if charge:
            yield event(s, (occupied, bonds, carrier, charge-1, packet), coefficient, 'charge_drain')
        if charge < 2:
            yield event(s, (occupied, bonds, carrier, charge+1, packet),
                        coefficient*exp(-p.beta), 'charge_bath_return')

    return WorldSpec('reactive-lattice', '1', states, validate, energy,
        {'bonds': lambda s: float(s[1].bit_count()),
         'charge': lambda s: float(s[3]), 'packet': lambda s: float(s[4]),
         'source_catalyst': lambda s: float(near_count(s[1], 0) > 0),
         'G1': lambda s: float(s[1] != 0),
         'G2': lambda s: float(s[2] == 0 and near_count(s[1], 0) > 0),
         'G3': lambda s: float(s[1].bit_count() >= 2)},
        tuple(RuleModule(name, '1', fn) for name, fn in
              (('diffusion', diffusion), ('chemistry', chemistry), ('resource', resource),
               ('maintenance', maintenance))),
        {'fields': ('occupied_sites', 'bond_edges', 'carrier_site', 'charge', 'packet'),
         'parameters': vars(p), 'energy': 'H=bond_count+charge+3*packet',
         'contact': 'ring distance <=1; carrier at source for capture; spectators unchanged',
         'density': p.monomers/p.sites, 'grain': 'site/bond/carrier resolved; no particle IDs',
         'drive': 'packet inflow delivers work3; external damage explicitly nonequilibrium',
         'scope': 'finite dense reactive lattice, not microscopic dilute gas'})


def organized_root(parameters):
    p = parameters
    return ((1 << p.monomers)-1, 1, 0, 0, 1)


def reference_masks(compiled, root):
    """Equal-energy thermal shell, unbound subset, and placement-only shell.

    All states have unit physical multiplicity at this site/bond grain.
    Conditioning exp(-beta E) makes beta cancel from the shell weights.
    """
    import numpy as np
    energy = compiled['world'].energy(root)
    shell = np.isclose(compiled['energy'], energy, atol=1e-12, rtol=0.)
    states = compiled['states']
    masks = {'thermal': shell,
             'unbound': shell & np.array([s[1] == 0 for s in states]),
             'arrangement': shell & np.array([s[1].bit_count() == root[1].bit_count()
                                              and s[3:] == root[3:] for s in states])}
    for name, mask in masks.items():
        if not mask.any():
            raise ValueError(f'Empty {name} reference; no energy fudging')
    return {name: mask.astype(float)/mask.sum() for name, mask in masks.items()}
