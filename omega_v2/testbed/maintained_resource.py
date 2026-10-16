"""Tiny driven locked-resource adapter; v1 has an explicit bounded boundary."""
from __future__ import annotations

from itertools import product
from math import exp

from .contracts import Event, RuleModule, WorldSpec

# Resource code: empty, locked, usable, downstream-used/waste.
EMPTY, LOCKED, USABLE, WASTE = range(4)
BETA = 1.0
ENERGY = {"empty": 0.0, "locked": 0.5, "usable": 0.0, "waste": 0.25,
          "apparatus": 2.0, "charged_carrier": 2.0}
RATES = {
    "basal_release": 0.002,
    "paid_release": 0.05,
    "downstream_use": 0.04,
    "maintenance": 0.015,
    "resource_inlet": 0.03,
    "locked_export": 0.008,
    "waste_export": 0.02,
    "carrier_recharge": 0.04,
    "carrier_export": 0.006,
}
STATES = tuple(product(range(4), (0, 1), (0, 1)))


def validate(state):
    if state not in STATES:
        raise ValueError(f"Invalid maintained-resource state: {state}")


def energy(state):
    resource, apparatus, charged = state
    resource_energy = (ENERGY["empty"], ENERGY["locked"],
                       ENERGY["usable"], ENERGY["waste"])[resource]
    return (resource_energy + ENERGY["apparatus"] * apparatus
            + ENERGY["charged_carrier"] * charged)


def _paired(state, target, rate, family, rule, support, increments=None):
    delta = energy(target) - energy(state)
    return Event(rule, family, target, rate * exp(-BETA * delta / 2), support,
                 0.0, increments or {})


def _boundary(state, target, rate, family, rule, support, increments=None):
    # Boundary work supplies/removes the exact local energy change; no hidden
    # bath subtraction or free change to the local energy ledger.
    return Event(rule, family, target, rate, support,
                 energy(target) - energy(state), increments or {})


def _events(state, paid_path=True):
    resource, apparatus, charged = state
    if resource == EMPTY:
        yield _boundary(state, (LOCKED, apparatus, charged), RATES["resource_inlet"],
                        "resource_inlet", "bounded-resource-inlet", (0,),
                        {"accepted_resource_inlet": 1.0})
    elif resource == LOCKED:
        yield _boundary(state, (EMPTY, apparatus, charged), RATES["locked_export"],
                        "locked_export", "locked-resource-outlet", (0,),
                        {"locked_resource_outflow": 1.0})
        yield _paired(state, (USABLE, apparatus, charged), RATES["basal_release"],
                      "basal_release", "paired-basal-release", (0,))
        if paid_path and apparatus and charged:
            yield _paired(state, (USABLE, apparatus, 0), RATES["paid_release"],
                          "paid_release", "paired-fueled-release", (0, 2),
                          {"stored_fuel_energy_consumed": ENERGY["charged_carrier"]})
    elif resource == USABLE:
        yield _paired(state, (LOCKED, apparatus, charged), RATES["basal_release"],
                      "basal_release", "paired-basal-release", (0,))
        if paid_path and apparatus and not charged:
            yield _paired(state, (LOCKED, apparatus, 1), RATES["paid_release"],
                          "paid_release", "paired-fueled-release", (0, 2),
                          {"stored_fuel_energy_consumed": -ENERGY["charged_carrier"]})
        yield _paired(state, (WASTE, apparatus, charged), RATES["downstream_use"],
                      "downstream_use", "paired-downstream-use", (0,))
    else:  # consumed material is an explicit waste state, then exported
        yield _paired(state, (USABLE, apparatus, charged), RATES["downstream_use"],
                      "downstream_use", "paired-downstream-use", (0,))
        yield _boundary(state, (EMPTY, apparatus, charged), RATES["waste_export"],
                        "waste_export", "waste-outlet", (0,),
                        {"waste_outflow": 1.0})

    # One conserved apparatus/precursor slot: active=1 or precursor=1.
    # Construction/maintenance consumes a charged carrier; reverse deactivation
    # returns that carrier. Both directions obey the same thermal energy law.
    if not apparatus and charged:
        yield _paired(state, (resource, 1, 0), RATES["maintenance"],
                      "maintenance", "paired-maintenance", (1, 2),
                      {"stored_fuel_energy_consumed": ENERGY["charged_carrier"]})
    elif apparatus and not charged:
        yield _paired(state, (resource, 0, 1), RATES["maintenance"],
                      "maintenance", "paired-maintenance", (1, 2),
                      {"stored_fuel_energy_consumed": -ENERGY["charged_carrier"]})

    # The carrier pool has capacity one. Recharge is a one-way driven inflow;
    # export is a separate outlet. No full-pool no-op events are enumerated.
    if not charged:
        yield _boundary(state, (resource, apparatus, 1), RATES["carrier_recharge"],
                        "carrier_recharge", "charged-carrier-inlet", (2,),
                        {"accepted_carrier_recharge": 1.0})
    else:
        yield _boundary(state, (resource, apparatus, 0), RATES["carrier_export"],
                        "carrier_export", "charged-carrier-outlet", (2,),
                        {"charged_carrier_outflow": 1.0})


def build_world(paid_path=True) -> WorldSpec:
    module = RuleModule("maintained-locked-resource", "1",
                        lambda state: _events(state, paid_path),
                        provides=("bounded-inlet-outlet", "finite-apparatus-slot",
                                  "charged-spent-carrier", "maintained-resource"))
    return WorldSpec(
        "maintained-locked-resource-v1", "1", STATES, validate, energy,
        {"resource_locked": lambda s: float(s[0] == LOCKED),
         "resource_usable": lambda s: float(s[0] == USABLE),
         "resource_waste": lambda s: float(s[0] == WASTE),
         "resource_present": lambda s: float(s[0] != EMPTY),
         "apparatus": lambda s: float(s[1]), "precursor": lambda s: float(1 - s[1]),
         "charged_carrier": lambda s: float(s[2]), "spent_carrier": lambda s: float(1 - s[2]),
         "fuel_inventory_energy": lambda s: ENERGY["charged_carrier"] * s[2]},
        (module,), {"fields": (), "adapter": "finite-buffer maintained inflow toy",
                    "paid_path": bool(paid_path), "beta": BETA,
                    "bath_temperature": 1.0,
                    "boundary_prescription": {k: RATES[k] for k in
                        ("resource_inlet", "locked_export", "waste_export",
                         "carrier_recharge", "carrier_export")},
                    "boundary_source_energies": {"resource": ENERGY["locked"],
                                                  "carrier": ENERGY["charged_carrier"]},
                    "resource_capacity": 1, "apparatus_precursor_capacity": 1,
                    "charged_spent_carrier_capacity": 1})


def roots():
    # Same total energy and all other inventories: apparatus/precursor exchange
    # is offset by charged/spent carrier exchange.
    capable = (LOCKED, 1, 0)
    unorganized = (LOCKED, 0, 1)
    return {"organized": capable, "unorganized": unorganized,
            "matched_ablation": capable}

