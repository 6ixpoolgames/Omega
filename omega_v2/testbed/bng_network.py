"""Strict small-network BNGL adapter; unsupported kinetics fail closed.

BNG-generated mass-action prefactors already include rule symmetry. Stochastic
population factors are falling factorials, with no second symmetry division.
This adapter supports literal parameters and arithmetic mass-action coefficients,
not arbitrary functions, compartments, observables or enzyme rate laws.
"""
from __future__ import annotations

import ast
from collections import Counter, deque
from dataclasses import dataclass
import math
from pathlib import Path

import numpy as np
from scipy.linalg import expm


def arithmetic(expression: str, parameters: dict[str, float]) -> float:
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.Name) and node.id in parameters:
            return parameters[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -visit(node.operand)
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add): return left + right
            if isinstance(node.op, ast.Sub): return left - right
            if isinstance(node.op, ast.Mult): return left * right
            if isinstance(node.op, ast.Div): return left / right
        raise ValueError(f"Unsupported expression: {expression}")
    result = float(visit(ast.parse(expression, mode="eval").body))
    if not math.isfinite(result):
        raise ValueError("Nonfinite parameter/rate")
    return result


@dataclass(frozen=True)
class Reaction:
    reactants: tuple[int, ...]
    products: tuple[int, ...]
    coefficient: float

    def rate(self, state: tuple[int, ...]) -> float:
        rate = self.coefficient
        for index, count in Counter(self.reactants).items():
            for offset in range(count):
                rate *= max(state[index] - offset, 0)
        return rate

    def apply(self, state: tuple[int, ...]) -> tuple[int, ...]:
        result = list(state)
        for index in self.reactants: result[index] -= 1
        for index in self.products: result[index] += 1
        if min(result) < 0:
            raise ValueError("Infeasible reaction")
        return tuple(result)


@dataclass
class Network:
    species: list[str]
    initial: tuple[int, ...]
    reactions: list[Reaction]


def parse_net(path: Path) -> Network:
    sections: dict[str, list[str]] = {}
    current = None
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line: continue
        if line.startswith("begin "):
            current = line.split()[1]
            sections[current] = []
        elif line.startswith("end "):
            current = None
        elif current:
            sections[current].append(line)
    if any(sections.get(s) for s in ("functions", "compartments", "energy patterns")):
        raise ValueError("Unsupported network feature")
    parameters: dict[str, float] = {}
    for line in sections.get("parameters", []):
        _, name, expression = line.split(maxsplit=2)
        parameters[name] = arithmetic(expression, parameters)
    species, initial = [], []
    for line in sections["species"]:
        index, name, amount = line.split()
        if int(index) != len(species) + 1:
            raise ValueError("Species indices must be contiguous")
        value = arithmetic(amount, parameters)
        if value < 0 or value != int(value):
            raise ValueError("Finite population requires integer initial counts")
        species.append(name)
        initial.append(int(value))
    reactions = []
    for line in sections["reactions"]:
        _, reactants, products, expression = line.split(maxsplit=3)
        coefficient = arithmetic(expression, parameters)
        if coefficient < 0: raise ValueError("Negative reaction rate")
        sides = []
        for side in (reactants, products):
            indices = tuple(int(i) - 1 for i in side.split(",") if i != "0")
            if any(i < 0 or i >= len(species) for i in indices):
                raise ValueError("Invalid species reference")
            sides.append(indices)
        reactions.append(Reaction(*sides, coefficient))
    return Network(species, tuple(initial), reactions)


def enumerate_generator(network: Network, state_cap: int = 1000):
    states = [network.initial]
    indices = {network.initial: 0}
    pending = deque(states)
    rows = []
    while pending:
        state = pending.popleft()
        rates: dict[int, float] = {}
        for reaction in network.reactions:
            rate = reaction.rate(state)
            if rate <= 0: continue
            target = reaction.apply(state)
            if target == state: continue  # this state-history readout sees no change
            if target not in indices:
                if len(states) >= state_cap:
                    raise RuntimeError("State cap reached; law was not truncated")
                indices[target] = len(states)
                states.append(target)
                pending.append(target)
            j = indices[target]
            rates[j] = rates.get(j, 0.0) + rate
        rows.append(rates)
    q = np.zeros((len(states), len(states)))
    for i, rates in enumerate(rows):
        for j, rate in rates.items(): q[i, j] = rate
        q[i, i] = -sum(rates.values())
    return states, q


def transition(q: np.ndarray, delta: float) -> np.ndarray:
    if delta <= 0: raise ValueError("Positive physical cadence required")
    p = expm(delta * q)
    if p.min() < -1e-12 or np.max(np.abs(p.sum(axis=1) - 1)) > 1e-11:
        raise ArithmeticError("Invalid transition matrix")
    return p


def history_bits(p: np.ndarray, steps: int) -> np.ndarray:
    if steps < 0: raise ValueError("Negative horizon")
    logs = np.zeros_like(p)
    np.log2(p, out=logs, where=p > 0)
    g = -(p * logs).sum(axis=1)
    value = np.zeros(len(p))
    for _ in range(steps): value = g + p @ value
    return value


def ssa_endpoints(network: Network, horizon: float, samples: int, seed: int):
    """Direct Gillespie sampling of the SAME elementary reaction specification."""
    rng = np.random.default_rng(seed)
    endpoints = Counter()
    for _ in range(samples):
        t, state = 0.0, network.initial
        while True:
            rates = np.array([r.rate(state) for r in network.reactions])
            total = rates.sum()
            if total == 0: break
            t += rng.exponential(1 / total)
            if t > horizon: break
            j = rng.choice(len(rates), p=rates / total)
            state = network.reactions[j].apply(state)
        endpoints[state] += 1
    return endpoints
