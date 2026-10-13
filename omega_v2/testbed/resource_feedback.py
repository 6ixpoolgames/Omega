"""Finite count-state resource feedback world for compositional testbeds.

This is a local RuleModule builder.  It does not select global experiment arms;
callers choose feedback and capacities when constructing a WorldSpec.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from itertools import product
from math import comb, exp, isfinite
from types import MappingProxyType

from .contracts import Event, RuleModule, WorldSpec

EMPTY, LOCKED, USABLE, WASTE = range(4)
RESOURCE_NAMES = ("empty", "locked", "usable", "waste")


@dataclass(frozen=True)
class ResourceFeedbackParameters:
    beta: float = 1.0
    resource_energies: tuple[float, float, float, float] = (0.0, 5.0, 4.0, 0.0)
    apparatus_energy: float = 2.0
    charged_carrier_energy: float = 2.0
    apparatus_capacity: int = 1
    carrier_capacity: int = 1
    feedback: str = "catalytic"  # catalytic, uncatalytic, absent
    feedback_basal: float = 0.002
    catalysis_enabled: bool = True
    inflow_enabled: bool = True
    rates: Mapping[str, float] = field(default_factory=lambda: {
        "basal_release": 0.002, "downstream_thermal": 0.04,
        "fueled_access": 0.05, "feedback": 0.04,
        "construction": 0.015, "wear": 0.002,
        "resource_inlet": 0.03, "locked_export": 0.008,
        "waste_export": 0.02, "carrier_thermal": 0.04,
    })

    def __post_init__(self):
        object.__setattr__(self, 'resource_energies', tuple(self.resource_energies))
        object.__setattr__(self, 'rates', MappingProxyType(dict(self.rates)))
        if not isfinite(self.beta) or self.beta <= 0:
            raise ValueError("beta must be finite and positive")
        if len(self.resource_energies) != 4 or any(
                not isfinite(x) for x in self.resource_energies):
            raise ValueError("four finite resource energies are required")
        if not isfinite(self.apparatus_energy) or not isfinite(self.charged_carrier_energy):
            raise ValueError("inventory energies must be finite")
        if self.apparatus_energy <= 0 or self.charged_carrier_energy <= 0:
            raise ValueError("apparatus and charged-carrier energies must be positive")
        if isinstance(self.apparatus_capacity, bool) or self.apparatus_capacity < 1:
            raise ValueError("apparatus_capacity must be a positive integer")
        if isinstance(self.carrier_capacity, bool) or self.carrier_capacity < 1:
            raise ValueError("carrier_capacity must be a positive integer")
        if not isinstance(self.apparatus_capacity, int) or not isinstance(self.carrier_capacity, int):
            raise TypeError("capacities must be integers")
        if self.feedback not in {"catalytic", "uncatalytic", "absent", "basal_catalytic"}:
            raise ValueError("Unknown feedback mode")
        if not isfinite(self.feedback_basal) or self.feedback_basal <= 0:
            raise ValueError('Positive finite basal feedback required')
        if type(self.inflow_enabled) is not bool:
            raise ValueError('inflow_enabled must be boolean')
        if type(self.catalysis_enabled) is not bool:
            raise ValueError('catalysis_enabled must be boolean')
        required = {"basal_release", "downstream_thermal", "fueled_access", "feedback",
                    "construction", "wear", "resource_inlet", "locked_export",
                    "waste_export", "carrier_thermal"}
        if set(self.rates) != required or any(
                not isfinite(v) or v <= 0 for v in self.rates.values()):
            raise ValueError("rates must provide every declared channel with positive finite values")


DEFAULT_PARAMETERS = ResourceFeedbackParameters()


def _states(p: ResourceFeedbackParameters):
    return tuple(product(range(4), range(p.apparatus_capacity + 1),
                         range(p.carrier_capacity + 1)))


def _energy(state, p: ResourceFeedbackParameters):
    resource, apparatus, charged = state
    return (p.resource_energies[resource] + p.apparatus_energy * apparatus
            + p.charged_carrier_energy * charged)


def _events(state, p: ResourceFeedbackParameters):
    resource, apparatus, charged = state
    spent = p.carrier_capacity - charged
    energy = lambda s: _energy(s, p)

    def paired(target, rate, family, rule, support, mass=1.0, increments=None):
        delta = energy(target) - energy(state)
        return Event(rule, family, target,
                     rate * mass * exp(-p.beta * delta / 2), support, 0.0,
                     increments or {})

    def boundary(target, rate, family, rule, support, increments=None):
        return Event(rule, family, target, rate, support,
                     energy(target) - energy(state), increments or {})

    if resource == EMPTY and p.inflow_enabled:
        yield boundary((LOCKED, apparatus, charged), p.rates["resource_inlet"],
                       "resource_inlet", "resource-inlet", (0,), {"accepted_resource_input": 1.0})
    elif resource == LOCKED:
        yield boundary((EMPTY, apparatus, charged), p.rates["locked_export"],
                       "locked_export", "locked-resource-export", (0,),
                       {"locked_resource_export": 1.0})
        yield paired((USABLE, apparatus, charged), p.rates["basal_release"],
                     "basal_release", "paired-basal-release", (0,))
        if apparatus and charged:
            yield paired((USABLE, apparatus, charged - 1), p.rates["fueled_access"],
                         "fueled_access", "paired-fueled-access", (0, 2),
                         mass=float(apparatus * charged),
                         increments={"access_fuel_cost": 1.0})
    elif resource == USABLE:
        yield paired((LOCKED, apparatus, charged), p.rates["basal_release"],
                     "basal_release", "paired-basal-release", (0,))
        if apparatus and spent:
            yield paired((LOCKED, apparatus, charged + 1), p.rates["fueled_access"],
                         "fueled_access", "paired-fueled-access", (0, 2),
                         mass=float(apparatus * spent),
                         increments={"access_fuel_cost": -1.0})
        yield paired((WASTE, apparatus, charged), p.rates["downstream_thermal"],
                     "downstream_thermal", "paired-downstream-thermal", (0,))
    elif resource == WASTE:
        yield paired((USABLE, apparatus, charged), p.rates["downstream_thermal"],
                     "downstream_thermal", "paired-downstream-thermal", (0,))
        yield boundary((EMPTY, apparatus, charged), p.rates["waste_export"],
                       "waste_export", "waste-export", (0,), {"waste_material_export": 1.0})

    # Spent/charged carrier thermal excitation and relaxation remains present
    # in every arm, with count propensities preserving pool combinatorics.
    if spent:
        yield paired((resource, apparatus, charged + 1), p.rates["carrier_thermal"],
                     "carrier_thermal", "paired-carrier-thermal", (2,), mass=float(spent))
    if charged:
        yield paired((resource, apparatus, charged - 1), p.rates["carrier_thermal"],
                     "carrier_thermal", "paired-carrier-thermal", (2,), mass=float(charged))

    # Assembly count and precursor count are complementary bounded pools.
    precursors = p.apparatus_capacity - apparatus
    if precursors and charged:
        yield paired((resource, apparatus + 1, charged - 1), p.rates["construction"],
                     "construction", "paired-construction", (1, 2),
                     mass=float(precursors * charged),
                     increments={"construction_forward": 1.0, "construction_cost": 1.0})
    if apparatus and spent:
        yield paired((resource, apparatus - 1, charged + 1), p.rates["construction"],
                     "construction", "paired-construction", (1, 2),
                     mass=float(apparatus * spent),
                     increments={"construction_reverse": 1.0, "construction_cost": -1.0})

    # Wear is a separate reversible basal channel, independent of feedback.
    if apparatus:
        yield paired((resource, apparatus - 1, charged), p.rates["wear"],
                     "wear", "paired-apparatus-wear", (1,), mass=float(apparatus),
                     increments={"apparatus_wear": 1.0})
    if precursors:
        yield paired((resource, apparatus + 1, charged), p.rates["wear"],
                     "wear", "paired-apparatus-wear", (1,), mass=float(precursors),
                     increments={"apparatus_wear": -1.0})

    if p.feedback != "absent":
        coefficient = (p.feedback_basal + p.rates['feedback']*apparatus*p.catalysis_enabled
                       if p.feedback == 'basal_catalytic' else
                       p.rates['feedback']*(float(apparatus) if p.feedback == "catalytic" else 1.0))
        if resource == USABLE and spent and coefficient:
            yield paired((WASTE, apparatus, charged + 1), coefficient,
                         "resource_feedback", "paired-resource-feedback", (0, 2),
                         mass=float(spent),
                         increments={"net_feedback_fuel": 1.0,
                                     "gross_feedback_forward": 1.0})
        if resource == WASTE and charged and coefficient:
            yield paired((USABLE, apparatus, charged - 1), coefficient,
                         "resource_feedback", "paired-resource-feedback", (0, 2),
                         mass=float(charged),
                         increments={"net_feedback_fuel": -1.0,
                                     "gross_feedback_reverse": 1.0})


def build_resource_feedback_module(parameters: ResourceFeedbackParameters = DEFAULT_PARAMETERS) -> RuleModule:
    """Build the local feedback rule bundle for later world composition."""
    return RuleModule(
        "resource-feedback", "1",
        lambda state: _events(state, parameters),
        provides=("resource-feedback", "bounded-resource-buffer",
                  "finite-apparatus-pool", "charged-spent-carrier-pool"))


def build_world(parameters: ResourceFeedbackParameters = DEFAULT_PARAMETERS, max_states=10000) -> WorldSpec:
    if 4*(parameters.apparatus_capacity+1)*(parameters.carrier_capacity+1) > max_states:
        raise RuntimeError('State cap: population pools were not truncated')
    states = _states(parameters)
    state_set = frozenset(states)

    def validate(state):
        if (not isinstance(state, tuple) or len(state) != 3
                or any(type(value) is not int for value in state) or state not in state_set):
            raise ValueError(f"Invalid resource-feedback state: {state}")

    module = build_resource_feedback_module(parameters)
    a_cap, c_cap = parameters.apparatus_capacity, parameters.carrier_capacity
    return WorldSpec(
        "resource-feedback-count-world", "1", states, validate,
        lambda s: _energy(s, parameters),
        {"resource_locked": lambda s: float(s[0] == LOCKED),
         "resource_usable": lambda s: float(s[0] == USABLE),
         "resource_waste": lambda s: float(s[0] == WASTE),
         "resource_present": lambda s: float(s[0] != EMPTY),
         "apparatus": lambda s: float(s[1]),
         "precursor": lambda s: float(a_cap - s[1]),
         "charged_carrier": lambda s: float(s[2]),
         "spent_carrier": lambda s: float(c_cap - s[2]),
         "fuel_inventory_energy": lambda s: float(parameters.charged_carrier_energy * s[2])},
        (module,),
        {"fields": (), "adapter": "finite count-state resource-use feedback",
         "beta": parameters.beta, "bath_temperature": 1.0 / parameters.beta,
         "resource_energies": dict(zip(RESOURCE_NAMES, parameters.resource_energies)),
         "apparatus_energy": parameters.apparatus_energy,
         "charged_carrier_energy": parameters.charged_carrier_energy,
         "resource_capacity": 1, "apparatus_precursor_capacity": a_cap,
         "charged_spent_carrier_capacity": c_cap, "feedback_mode": parameters.feedback,
         "resource_inflow_enabled": parameters.inflow_enabled,
         "feedback_basal": parameters.feedback_basal,
         "catalysis_enabled": parameters.catalysis_enabled,
         "boundary_prescription": {k: parameters.rates[k] for k in
             ("resource_inlet", "locked_export", "waste_export")},
         "boundary_source_energies": {"locked_resource": parameters.resource_energies[LOCKED]},
         "rate_prescription": dict(parameters.rates),
         "inventory": {"resource": RESOURCE_NAMES,
                       "apparatus_precursor": {"apparatus": "a", "precursor": "capacity-a"},
                       "carrier": {"charged": "c", "spent": "capacity-c"}},
         "thermodynamics": {"paired_law": "mass-action count propensity times exp(-beta*deltaE/2)",
                            "boundary_work": "exact local deltaE", "external_carrier_drive": False},
         "feedback_options": ("catalytic", "uncatalytic", "absent", "basal_catalytic"),
         "basal_catalytic_prescription": 'same law: k_basal + k_catalyst * apparatus_count; paired'},
        degeneracy=lambda state: comb(a_cap, state[1])*comb(c_cap, state[2]))
