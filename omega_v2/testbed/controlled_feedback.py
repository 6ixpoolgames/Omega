"""Costed, oracle-controlled access to resource feedback through a paid gate."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from itertools import product
from math import comb, exp, isfinite

from .contracts import ControllerSpec, Event, RuleModule, WorldSpec
from .resource_feedback import ResourceFeedbackParameters, build_resource_feedback_module


@dataclass(frozen=True)
class ControlledFeedbackController:
    """Fixed response probabilities (service, use) indexed by apparatus count."""

    id: str
    responses: tuple[tuple[float, float], ...]
    observation: str = "apparatus count a"

    def __post_init__(self):
        normalized = tuple(tuple(row) for row in self.responses)
        if not self.id or not normalized:
            raise ValueError("Controller id and at least one response are required")
        if self.observation != 'apparatus count a':
            raise ValueError('Additional observations need a physical sensing extension')
        for row in normalized:
            if (
                len(row) != 2
                or any(isinstance(x, bool) or not isfinite(x) or x < 0 for x in row)
                or sum(row) > 1 + 1e-12
            ):
                raise ValueError(
                    "Each response (service, use) must be nonnegative and sum at most one"
                )
        object.__setattr__(self, "responses", normalized)

    def at(self, apparatus: int) -> tuple[float, float]:
        if type(apparatus) is not int or not 0 <= apparatus < len(self.responses):
            raise ValueError("Controller response is undefined for this apparatus count")
        return self.responses[apparatus]

    def spec(self):
        return ControllerSpec(
            self.id,
            "1",
            self.observation,
            self.responses,
            memory="none",
            execution="native reversible gate channels",
        )


@dataclass(frozen=True)
class ControlledFeedbackParameters:
    resource: ResourceFeedbackParameters = field(
        default_factory=lambda: ResourceFeedbackParameters(
            feedback="basal_catalytic",
            rates={**ResourceFeedbackParameters().rates, "feedback": 0.04},
            feedback_basal=0.002,
        )
    )
    controller: ControlledFeedbackController = field(
        default_factory=lambda: ControlledFeedbackController(
            "service-use", ((0.0, 0.0), (0.5, 0.5))
        )
    )
    gate_capacity: int = 1
    gate_energy: float = 0.0
    gate_relaxation: float = 0.003
    command_switch: float = 0.015

    def __post_init__(self):
        if self.resource.feedback != "basal_catalytic":
            raise ValueError("Controlled feedback requires basal_catalytic resource feedback")
        if "feedback" not in self.resource.rates:
            raise ValueError("Resource feedback coefficient is required")
        if len(self.controller.responses) != self.resource.apparatus_capacity + 1:
            raise ValueError("Controller needs one fixed response for each apparatus count")
        if type(self.gate_capacity) is not int or self.gate_capacity != 1:
            raise ValueError("The controlled gate has capacity one")
        if (
            self.gate_energy != 0
            or not isfinite(self.gate_energy)
            or not isfinite(self.gate_relaxation)
            or self.gate_relaxation <= 0
        ):
            raise ValueError("Gate energy is zero and relaxation must be positive and finite")
        if not isfinite(self.command_switch) or self.command_switch <= 0:
            raise ValueError("Command switch coefficient must be positive and finite")

    @property
    def basal_feedback(self):
        return self.resource.feedback_basal

    @property
    def assisted_feedback(self):
        return self.resource.rates["feedback"] if self.resource.catalysis_enabled else 0.0


def build_world(parameters: ControlledFeedbackParameters, max_states: int = 10000) -> WorldSpec:
    p = parameters.resource
    nstates = 4 * (p.apparatus_capacity + 1) * (p.carrier_capacity + 1) * 2
    if nstates > max_states:
        raise RuntimeError("State cap: controlled population pools were not truncated")
    states = tuple(
        product(range(4), range(p.apparatus_capacity + 1), range(p.carrier_capacity + 1), range(2))
    )
    state_set = frozenset(states)
    base_module = build_resource_feedback_module(p)

    def energy(s):
        return (
            p.resource_energies[s[0]]
            + p.apparatus_energy * s[1]
            + p.charged_carrier_energy * s[2]
            + parameters.gate_energy * s[3]
        )

    def events(state):
        resource, apparatus, charged, gate = state
        base_state = (resource, apparatus, charged)
        for event in base_module.events(base_state):
            family = event.family
            # Construction requires the gate open. Basal catalytic turnover remains
            # available everywhere; only the controller-assisted increment is gated.
            if family == "construction" and gate != 0:
                continue
            if family == "fueled_access" and gate != 1:
                continue
            rate = event.rate
            if family == "resource_feedback" and gate == 0:
                # Base law carries the full basal+assisted coefficient. Remove only
                # the assisted part while closed, preserving the reversible pair.
                full_coefficient = parameters.basal_feedback + (
                    p.rates["feedback"] * apparatus if p.catalysis_enabled else 0.0
                )
                rate *= parameters.basal_feedback / full_coefficient
            yield Event(
                event.rule_id,
                family,
                event.target + (gate,),
                rate,
                event.support + (3,),
                event.work,
                event.increments,
            )

        # Policy-conditioned command pairs use the same fixed observation value in
        # both directions. A command spends a carrier; its reverse returns one.
        service, use = parameters.controller.at(apparatus)
        carrier_e = p.charged_carrier_energy
        beta = p.beta
        spent = p.carrier_capacity - charged
        if use and apparatus and gate == 0 and charged:
            yield Event(
                "use-gate-command",
                "actuation_use",
                (resource, apparatus, charged - 1, 1),
                parameters.command_switch
                * use
                * apparatus
                / max(1, p.apparatus_capacity)
                * charged
                * exp(beta * carrier_e / 2),
                (1, 2, 3),
                0.0,
                {"switches": 1.0, "gross_actuation_fuel": 1.0, "net_actuation_fuel": 1.0},
            )
        if use and apparatus and gate == 1 and spent:
            yield Event(
                "use-gate-command",
                "actuation_use",
                (resource, apparatus, charged + 1, 0),
                parameters.command_switch
                * use
                * apparatus
                / max(1, p.apparatus_capacity)
                * spent
                * exp(-beta * carrier_e / 2),
                (1, 2, 3),
                0.0,
                {
                    "switches": 1.0,
                    "gross_actuation_fuel": 0.0,
                    "gross_actuation_return": 1.0,
                    "net_actuation_fuel": -1.0,
                },
            )
        if service and apparatus and gate == 1 and charged:
            yield Event(
                "service-gate-command",
                "actuation_service",
                (resource, apparatus, charged - 1, 0),
                parameters.command_switch
                * service
                * apparatus
                / max(1, p.apparatus_capacity)
                * charged
                * exp(beta * carrier_e / 2),
                (1, 2, 3),
                0.0,
                {"switches": 1.0, "gross_actuation_fuel": 1.0, "net_actuation_fuel": 1.0},
            )
        if service and apparatus and gate == 0 and spent:
            yield Event(
                "service-gate-command",
                "actuation_service",
                (resource, apparatus, charged + 1, 1),
                parameters.command_switch
                * service
                * apparatus
                / max(1, p.apparatus_capacity)
                * spent
                * exp(-beta * carrier_e / 2),
                (1, 2, 3),
                0.0,
                {
                    "switches": 1.0,
                    "gross_actuation_fuel": 0.0,
                    "gross_actuation_return": 1.0,
                    "net_actuation_fuel": -1.0,
                },
            )

        # Physical policy-independent gate relaxation, present at every inventory.
        yield Event(
            "basal-gate-relaxation",
            "gate_relaxation",
            (resource, apparatus, charged, 1 - gate),
            parameters.gate_relaxation,
            (3,),
            0.0,
        )

    module = RuleModule(
        "controlled-resource-feedback",
        "1",
        events,
        provides=(
            "controlled-resource-feedback",
            "bounded-resource-buffer",
            "finite-apparatus-pool",
            "charged-spent-carrier-pool",
            "paid-native-gate",
        ),
    )

    def validate(s):
        if (
            not isinstance(s, tuple)
            or len(s) != 4
            or any(type(x) is not int for x in s)
            or s not in state_set
        ):
            raise ValueError(f"Invalid controlled-feedback state: {s}")

    a_cap, c_cap = p.apparatus_capacity, p.carrier_capacity
    observables = {
        "resource_locked": lambda s: float(s[0] == 1),
        "resource_usable": lambda s: float(s[0] == 2),
        "resource_waste": lambda s: float(s[0] == 3),
        "resource_present": lambda s: float(s[0] != 0),
        "apparatus": lambda s: float(s[1]),
        "precursor": lambda s: float(a_cap - s[1]),
        "charged_carrier": lambda s: float(s[2]),
        "spent_carrier": lambda s: float(c_cap - s[2]),
        "gate": lambda s: float(s[3]),
        "fuel_inventory_energy": lambda s: float(p.charged_carrier_energy * s[2]),
    }
    return WorldSpec(
        "controlled-resource-feedback-world",
        "1",
        states,
        validate,
        energy,
        observables,
        (module,),
        {
            "fields": (),
            "adapter": "finite resource-use feedback with oracle-controlled paid gate",
            "beta": p.beta,
            "bath_temperature": 1 / p.beta,
            "feedback_mode": "basal_catalytic",
            "basal_feedback": parameters.basal_feedback,
            "assisted_feedback_coefficient": parameters.assisted_feedback,
            "controller": asdict(parameters.controller.spec()),
            "controller_observation": parameters.controller.observation,
            "controller_cost": "physical charged-carrier transfer and symmetric gate relaxation",
            "gate_energy": parameters.gate_energy,
            "gate_capacity": 1,
            "actuation_switch_coefficient": parameters.command_switch,
            "resource_inflow_enabled": p.inflow_enabled,
            "policy_independent_gate_relaxation": parameters.gate_relaxation,
            "boundary_prescription": {
                k: p.rates[k] for k in ("resource_inlet", "locked_export", "waste_export")
            },
            "external_controlled_oracles": False,
            "action_label_entropy": False,
        },
        degeneracy=lambda s: comb(a_cap, s[1]) * comb(c_cap, s[2]),
    )
