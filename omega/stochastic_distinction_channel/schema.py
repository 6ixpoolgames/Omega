"""Shared helpers for finite stochastic distinction-channel probes."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


CLAIM_BOUNDARY = (
    "prebiotic stochastic channel probe only; no Omega validation, no valuer "
    "detection, no agency, no identity, no compatibility detection, no ethical claim"
)
DEFAULT_OUT = Path("results/stochastic_distinction_channel/20260603_stochastic_channel_probe_v0")


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)


def decimal(value: Fraction) -> float:
    return float(value)


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def safe_id(value: object) -> str:
    return "".join(char if char.isalnum() else "_" for char in str(value)).strip("_")


def bit(state: str, index: int) -> str:
    return state[index]


def flip_bit(state: str, index: int) -> str:
    chars = list(state)
    chars[index] = "1" if chars[index] == "0" else "0"
    return "".join(chars)


def parity(state: str) -> str:
    return str((int(state[0]) + int(state[1])) % 2)


def pair_label(state: str) -> str:
    return state


def ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def fraction_from_text(value: object) -> Fraction:
    if isinstance(value, Fraction):
        return value
    text = str(value)
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return Fraction(int(numerator), int(denominator))
    return Fraction(text)
