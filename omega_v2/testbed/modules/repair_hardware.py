"""Physical repair-hardware extension; it adds no objective reward.

Extended state: (left PWA-D compartment, right compartment, hardware bits).
The hardware bit distinguishes intact from irreversibly damaged hardware, not
an observer's label. Basal assembly and thermal recovery remain in every arm.
"""
from dataclasses import asdict, dataclass, replace
from itertools import product
from math import isfinite

from ..contracts import Event, RuleModule, WorldSpec
from .actuation import ActuationSpec
from .growth import build_world as build_growth_world
from .material_sink import MaterialSink


@dataclass(frozen=True)
class RepairHardware:
    mode: str = "fast"
    hazard: float = 0.02
    slow_factor: float = 0.1
    hardware_energy: float = 1.0

    def __post_init__(self):
        if self.mode not in ("fast", "slow", "hardware_loss"):
            raise ValueError("Unknown damage consequence")
        for value in (self.hazard, self.slow_factor, self.hardware_energy):
            if not isfinite(value) or value < 0:
                raise ValueError("Finite nonnegative parameters required")
        if self.slow_factor > 1:
            raise ValueError("Slow repair factor must not exceed one")


def build_world(inventories=(1, 1), policy=None, config=None, params=None,
                max_states=10000):
    config = config or RepairHardware()
    kwargs = {} if params is None else {"params": params}
    base = build_growth_world(inventories, policy=policy,
                             damage=MaterialSink(enabled=False),
                             actuation=ActuationSpec(mode="embodied", basal_rate=.003),
                             max_states=max_states, **kwargs)
    if len(base.states) * 4 > max_states:
        raise RuntimeError("State cap: physical law was not truncated")
    states = tuple((*state, hardware) for state in base.states
                   for hardware in product((0, 1), repeat=2))

    def validate(state):
        if not isinstance(state, tuple) or len(state) != 3:
            raise ValueError("Two compartments and physical hardware bits required")
        base.validate(state[:2])
        if (not isinstance(state[2], tuple) or len(state[2]) != 2
                or any(type(bit) is not int or bit not in (0, 1) for bit in state[2])):
            raise ValueError("Invalid hardware state")

    def energy(state):
        return base.energy(state[:2]) + config.hardware_energy * sum(state[2])

    def lift(module):
        def events(state):
            hardware = state[2]
            for event in module.events(state[:2]):
                rate = event.rate
                if event.family == "repair":
                    c, = event.support
                    factor = config.slow_factor if config.mode == "slow" else 1.0
                    rate *= hardware[c] * factor
                if rate:
                    yield replace(event, target=(*event.target, hardware), rate=rate)
        return RuleModule(module.id, module.version + "-hardware1", events,
                          module.requires, module.provides)

    def faults(state):
        for c, local in enumerate(state[:2]):
            active = local[1]
            if not active or not config.hazard:
                continue
            target = [list(x) for x in state[:2]]
            target[c][0] += 1
            target[c][1] -= 1
            hardware = list(state[2])
            if config.mode == "hardware_loss":
                hardware[c] = 0
            lost = state[2][c] - hardware[c]
            yield Event("external-functional-fault", "functional_fault",
                        (*map(tuple, target), tuple(hardware)),
                        config.hazard * active, (c, 2) if lost else (c,),
                        increments={"fault_impairments": 1.,
                                    "repair_hardware_losses": float(lost)})

    observables = {name: (lambda state, fn=fn: fn(state[:2]))
                   for name, fn in base.observables.items()}
    observables["repair_hardware"] = lambda state: sum(state[2])
    metadata = dict(base.metadata)
    metadata.update(repair_hardware=asdict(config),
                    fields=(*base.metadata["fields"], "repair-hardware"),
                    fault_boundary="one-way external damage; not equilibrium detailed balance",
                    repair_scope="powered repair only; basal substitutes retained")
    modules = (*map(lift, base.modules),
               RuleModule("repair-hardware-faults", "1", faults,
                          requires=("repair-hardware",), provides=("functional-faults",)))
    return WorldSpec("growth-with-repair-hardware", "1", states, validate, energy,
                     observables, modules, metadata,
                     degeneracy=lambda state: base.degeneracy(state[:2]))
