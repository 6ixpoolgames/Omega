"""Open, costed W1/W2 signal/escape adapter; no semantic rewards.

Engineering fixture, not a frozen physiological model. Energy is quantized;
every action pays a fixed bill. Randomness is in native event propensities.
One escape and one forage pathway are represented, not abstract action labels.
"""
from dataclasses import dataclass, replace
from itertools import product
from math import isfinite

from .contracts import Event, RuleModule, WorldSpec

H, O = 0, 1
ARMS = {
    "E": ("tracking", True, True),
    "A": ("tracking", False, True),
    "B": ("none", False, True),
    "C": ("none", False, False),
    "N": ("none", True, True),
    "D": ("hijacked", True, True),
    "E_prime": ("tracking", True, True),
    "N_prime": ("none", True, True),
}


@dataclass(frozen=True)
class SignalParameters:
    energy_cap: float = 4.0
    quantum: float = 0.5
    forage_cost: float = 0.5
    food_yield: float = 2.0
    struggle_cost: float = 1.0
    signal_energy: float = 0.5
    metabolism: float = 0.4  # mean energy dissipated per unit time
    signal_upkeep: float = 0.1
    attempt_rate: float = 0.6
    normal_escape: float = 0.1
    escape_bias: float = 0.7
    escape_success: float = 0.8
    forage_outside: float = 0.8
    forage_hazard: float = 0.5
    hazard_foraging_factor: float = 0.5
    hazard_damage_rate: float = 0.15
    hazard_on: float = 0.1
    hazard_off: float = 0.2
    patch_rate: float = 0.2
    signal_hit: float = 0.8
    signal_hijack: float = 0.2
    signal_off: float = 0.3

    def __post_init__(self):
        for name, value in vars(self).items():
            if not isfinite(value) or value < 0:
                raise ValueError(f"Nonnegative finite {name} required")
        if self.quantum <= 0 or self.energy_cap <= 0:
            raise ValueError("Positive quantum and energy cap required")
        for name in ("energy_cap", "forage_cost", "food_yield", "struggle_cost",
                     "signal_energy"):
            value = getattr(self, name) / self.quantum
            if abs(value - round(value)) > 1e-10 or value < 1:
                raise ValueError(f"{name} must be a positive quantum multiple")
        if self.food_yield <= self.forage_cost or self.food_yield > self.energy_cap:
            raise ValueError("Food yield must exceed the bill and fit the store")
        for name in ("normal_escape", "escape_bias", "escape_success", "forage_outside",
                     "forage_hazard", "hazard_foraging_factor", "signal_hit"):
            if getattr(self, name) > 1:
                raise ValueError(f"{name} is a probability")
        if self.forage_hazard >= self.forage_outside:
            raise ValueError("Hazard-zone foraging must be less productive")

    def units(self, energy):
        return round(energy / self.quantum)


def build_world(arm="E", parameters=None):
    p = parameters or SignalParameters()
    if arm not in ARMS:
        raise ValueError("Unknown signal arm")
    signal, escape_available, behaviour = ARMS[arm]
    cap = p.units(p.energy_cap)
    # One canonical dead signal value; the body's location remains physical.
    states = tuple((e, loc, s, z, patch)
                   for e, loc, s, z, patch in product(range(cap + 1), range(2), range(2),
                                                    range(2), range(3)) if e or s == 0)

    def validate(state):
        if len(state) != 5:
            raise ValueError("Five physical coordinates required")
        e, loc, s, z, patch = state
        if (type(e) is not int or not 0 <= e <= cap or loc not in (H, O)
                or s not in (0, 1) or z not in (0, 1) or patch not in range(3)
                or (e == 0 and s)):
            raise ValueError("Invalid signal state")

    def events(state):
        e, loc, s, z, patch = state

        def emit(target, rate, family, increments=None, work=0.):
            if rate <= 0:
                return None
            changed = tuple(i for i, (x, y) in enumerate(zip(state, target)) if x != y)
            if not changed:
                raise ValueError("No-op action cannot generate history breadth")
            return Event(family, family, target, rate, tuple(range(5)), work,
                         increments or {})

        def spent(bill, new_location=loc, new_signal=s):
            remaining = max(0, e - bill)
            return (remaining, new_location, new_signal if remaining else 0, z, patch)

        yield emit((e, loc, s, 1-z, patch), p.hazard_off if z else p.hazard_on,
                   "hazard_toggle")
        for neighbour in (patch-1, patch+1):
            if neighbour in range(3):
                yield emit((e, loc, s, z, neighbour), p.patch_rate, "patch_thermal")
        if e == 0:
            return  # environment continues; no immortal controller or body reward
        yield emit(spent(1), p.metabolism / p.quantum, "metabolism",
                   {"metabolic_bill": min(e, 1)*p.quantum})
        if s:
            yield emit(spent(1), p.signal_upkeep / p.quantum, "signal_upkeep",
                       {"signal_upkeep_bill": min(e, 1)*p.quantum})
            yield emit((e, loc, 0, z, patch), p.signal_off, "signal_off")
        elif signal == "hijacked":
            bill = p.units(p.signal_energy)
            if e > bill:
                yield emit(spent(bill, new_signal=1), p.signal_hijack, "signal_on",
                           {"signal_charge": p.signal_energy})
        if z and loc == H:
            rate = p.hazard_damage_rate
            hit = p.signal_hit if signal == "tracking" and not s else 0.
            # Damage and signal activation are outcomes of one native injury event.
            yield emit(spent(1), rate*(1-hit), "hazard_damage", {"damage": p.quantum})
            bill = p.units(p.signal_energy)
            target = spent(1+bill, new_signal=1)
            yield emit(target, rate*hit, "hazard_damage",
                       {"damage": p.quantum,
                        "signal_charge": min(bill, max(0, e-1))*p.quantum,
                        "signal_activation": float(target[2] == 1)})
        if not behaviour:
            return
        escape = p.normal_escape + (1-p.normal_escape)*p.escape_bias*s*(signal != "none")
        forage_rate = p.attempt_rate*(1-escape)
        bill = p.units(p.forage_cost)
        if e >= bill:
            success = (p.forage_hazard if loc == H else p.forage_outside)*(patch+1)/3
            if loc == H and z:
                success *= p.hazard_foraging_factor
            # A completed forage attempt pays its bill, including on failure.
            target_energy = min(cap, e-bill+p.units(p.food_yield))
            target = (target_energy, loc, s, z, patch)
            if target == state:
                # No storage headroom: reject the food but still pay the attempt.
                target_energy = e-bill
                target = spent(bill)
            accepted = (target_energy-e+bill)*p.quantum
            yield emit(target, forage_rate*success,
                       "forage_success" if accepted else "forage_rejected",
                       {"forage_bill": p.forage_cost, "food_input": accepted}, accepted)
            yield emit(spent(bill), forage_rate*(1-success), "forage_failure",
                       {"forage_bill": p.forage_cost})
        # Outside, the same motor attempt remains costly but cannot escape twice.
        bill = p.units(p.struggle_cost)
        if e >= bill:
            success = p.escape_success if escape_available and loc == H else 0.
            rate = p.attempt_rate*escape
            yield emit(spent(bill, new_location=O), rate*success, "escape_success",
                       {"struggle_bill": p.struggle_cost})
            yield emit(spent(bill), rate*(1-success), "escape_failure",
                       {"struggle_bill": p.struggle_cost})

    def clean_events(state):
        return (event for event in events(state) if event is not None)

    return WorldSpec(
        f"aversive-{arm}", "engineering-1", states, validate,
        lambda x: p.quantum*x[0] + p.signal_energy*x[2],
        {"alive": lambda x: float(x[0] > 0),
         "stored_energy": lambda x: p.quantum*x[0],
         "aversive_occupancy": lambda x: float(x[0] > 0 and x[2] == 1),
         "hazard_exposure": lambda x: float(x[0] > 0 and x[1] == H and x[3] == 1)},
        (RuleModule("signal-world", "1", clean_events),),
        {"fields": ("energy", "location", "signal", "hazard", "patch"),
         "arm": arm, "parameters": vars(p), "status": "engineering_only",
         "escape_available": escape_available, "signal_mode": signal,
         "thermal_model": "coarse environmental process; not a microscopic gas",
         "thermodynamics": "open driven dissipative kinetics; no detailed-balance claim",
         "death": "energy zero absorbing for valuer; location and environment retained",
         "action_repertoire": "one forage and one physical motor/escape pathway"})


def matched_parameters(parameters, hazard_on=None, hazard_damage_rate=None):
    """Explicit environmental matching for D/E-prime/N-prime, never arm magic."""
    changes = {}
    if hazard_on is not None:
        changes["hazard_on"] = hazard_on
    if hazard_damage_rate is not None:
        changes["hazard_damage_rate"] = hazard_damage_rate
    return replace(parameters, **changes)
