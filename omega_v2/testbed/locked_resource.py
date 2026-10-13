"""Tiny finite-store access fixture with paired basal and fuel-coupled routes.

State coordinates are (locked, product, apparatus, fuel). Exactly one resource
is locked, available (neither locked nor product), or converted to product.
"""
from __future__ import annotations

from itertools import product
from math import exp

from .contracts import Event, RuleModule, WorldSpec

BASE_BARRIER = 0.001
CATALYTIC_BARRIER = 0.04
ASSEMBLY_BARRIER = 0.08
CONVERSION_BARRIER = 0.04
BETA = 1.0
FUEL_ENERGY = 2.0
APPARATUS_ENERGY = 2.0
RESOURCE_ENERGY = (0.0, 0.0, -1.0)  # locked, available, converted
STATES = tuple((l, p, a, f) for l, p, a, f in product((0, 1), (0, 1), (0, 1), range(3))
               if l + p <= 1 and a + f <= 2)


def validate(s):
    if s not in STATES:
        raise ValueError(f"Invalid locked-resource state: {s}")


def energy(s):
    locked, product_state, apparatus, fuel = s
    resource_index = 0 if locked else (2 if product_state else 1)
    return RESOURCE_ENERGY[resource_index] + APPARATUS_ENERGY * apparatus + FUEL_ENERGY * fuel


def _paired(s, target, barrier, family, rule, support, increments=None):
    """Return both directions with kf/kr=exp(-beta*deltaE)."""
    delta = energy(target) - energy(s)
    forward = barrier * exp(-BETA * delta / 2)
    reverse = barrier * exp(BETA * delta / 2)
    return (Event(rule, family, target, forward, support, 0.0, increments or {}),
            Event(rule, family, s, reverse, support,
                  0.0, {k: -v for k, v in (increments or {}).items()}))


def _events(s):
    locked, product_state, apparatus, fuel = s
    # High-barrier, positive basal exchange; equilibrium ratio follows energy.
    if locked:
        yield _paired(s, (0, product_state, apparatus, fuel), BASE_BARRIER,
                      "basal_release", "basal-release-pair", (0,))[0]
    elif not product_state:
        yield _paired(s, (1, product_state, apparatus, fuel), BASE_BARRIER,
                      "basal_release", "basal-release-pair", (0,))[0]
    # Apparatus assembly consumes one finite fuel unit; disassembly restores it.
    if not apparatus and fuel:
        yield _paired(s, (locked, product_state, 1, fuel - 1), ASSEMBLY_BARRIER,
                      "assembly", "fuel-paid-assembly-pair", (2, 3),
                      {"stored_fuel_energy_consumed": FUEL_ENERGY})[0]
    if apparatus and fuel < 2:
        yield _paired(s, (locked, product_state, 0, fuel + 1), ASSEMBLY_BARRIER,
                      "assembly", "fuel-paid-assembly-pair", (2, 3),
                      {"stored_fuel_energy_consumed": -FUEL_ENERGY})[0]
    # Catalyst unlocks the resource only by consuming fuel; reverse relocks it
    # and returns the fuel. Both directions are present and thermodynamically paired.
    if locked and apparatus and fuel:
        yield _paired(s, (0, product_state, apparatus, fuel - 1), CATALYTIC_BARRIER,
                      "fuel_release", "fuel-coupled-release-pair", (0, 3),
                      {"stored_fuel_energy_consumed": FUEL_ENERGY})[0]
    if not locked and not product_state and apparatus and fuel < 1:
        yield _paired(s, (1, product_state, apparatus, fuel + 1), CATALYTIC_BARRIER,
                      "fuel_release", "fuel-coupled-release-pair", (0, 3),
                      {"stored_fuel_energy_consumed": -FUEL_ENERGY})[0]
    # Downstream conversion and its reverse keep total resource fixed.
    if not locked and not product_state:
        yield _paired(s, (0, 1, apparatus, fuel), CONVERSION_BARRIER,
                      "downstream_conversion", "resource-conversion-pair", (1,))[0]
    if product_state:
        yield _paired(s, (0, 0, apparatus, fuel), CONVERSION_BARRIER,
                      "downstream_conversion", "resource-conversion-pair", (1,))[0]


MODULE = RuleModule("locked-resource", "1", _events,
                    provides=("finite-resource", "paid-access", "paired-basal-exchange"))


def build_world() -> WorldSpec:
    return WorldSpec(
        "locked-resource-finite-store", "1", STATES, validate, energy,
        {"locked": lambda s: float(s[0]), "product": lambda s: float(s[1]),
         "apparatus": lambda s: float(s[2]), "fuel": lambda s: float(s[3]),
         "fuel_inventory_energy": lambda s: FUEL_ENERGY * s[3]},
        (MODULE,), {"fields": (), "adapter": "single-resource paid catalyst fixture",
                    "comparison": "same-generator roots; finite store",
                    "beta": BETA, "fuel_energy": FUEL_ENERGY,
                    "basal_barrier": BASE_BARRIER})


def make_root(organized: bool):
    """Equal-energy roots: organized apparatus+one fuel; unorganized two fuel."""
    root = (1, 0, 1, 1) if organized else (1, 0, 0, 2)
    validate(root)
    return root


def describe():
    return {"states": len(STATES), "organized_root": make_root(True),
            "unorganized_root": make_root(False),
            "root_energy": energy(make_root(True)),
            "parameters": {"beta": BETA, "fuel_energy": FUEL_ENERGY,
                           "apparatus_energy": APPARATUS_ENERGY,
                           "basal_barrier": BASE_BARRIER,
                           "catalytic_barrier": CATALYTIC_BARRIER}}
