"""Tiny, bounded three-arm reversible assembly experiment (fixture A).

The species model is intentionally coarse: M is a free monomer and D a dimer.
BioNetGen generates each arm/root network; an independent hand enumerator
constructs its population generator and audits detailed balance and breadth.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import time

import numpy as np

from .bng_network import (Network, Reaction, enumerate_generator, history_bits,
                          parse_net, ssa_endpoints, transition)

SPEC = Path(__file__).resolve().parents[2] / "docs/research_notes/lushness_testbed/assembly"
PROTOCOL_PATH = SPEC / "PROTOCOL.json"
ARMS = ("reversible_base", "metastable_slow_reversible", "dimer_feedback")


def _json_write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _root(n: int, assembled: bool) -> tuple[int, int]:
    return (n % 2, n // 2) if assembled else (n, 0)


def _model_text(arm: str, n: int, assembled: bool, protocol: dict) -> str:
    multiplier = {"reversible_base": 1.0, "metastable_slow_reversible": 0.01,
                  "dimer_feedback": 1.0}[arm]
    m, d = _root(n, assembled)
    # The factor 2 compensates BNG's identical-reactant symmetry coefficient.
    # The resulting generated .net coefficient is exactly the declared 1.0
    # (or 0.01), used with the adapter's falling-factorial propensity.
    lines = [
        "begin model", "begin parameters",
        f"  SCALE {multiplier:.17g}", "end parameters",
        "begin molecule types", "  M(x)", "  D(x)", "end molecule types",
        "begin seed species", f"  M(x) {m}", f"  D(x) {d}", "end seed species",
        "begin reaction rules",
        "  M(x) + M(x) <-> D(x) 2*SCALE,SCALE"
    ]
    if arm == "dimer_feedback":
        # BNG exports a 1/2 symmetry factor on the two-M forward match. The
        # reverse side exports no extra 1/2, so its rule coefficient is 1.
        lines.append("  D(x) + M(x) + M(x) <-> D(x) + D(x) 2,1")
    lines += ["end reaction rules", "end model", "", "generate_network({overwrite=>1})"]
    return "\n".join(lines)


def _hand_network(arm: str, n: int, root: tuple[int, int]) -> Network:
    states = [(n - 2*d, d) for d in range(n // 2 + 1)]
    index = {s: i for i, s in enumerate(states)}
    reactions: list[Reaction] = []
    scale = 0.01 if arm == "metastable_slow_reversible" else 1.0
    # Species order is M,D. Coefficients below are the generated .net rates.
    reactions.extend((Reaction((0, 0), (1,), scale), Reaction((1,), (0, 0), scale)))
    if arm == "dimer_feedback":
        reactions.extend((Reaction((0, 0, 1), (1, 1), 1.0),
                          Reaction((1, 1), (0, 0, 1), 1.0)))
    net = Network(["M(x)", "D(x)"], root, reactions)
    # Fail if a future edit to the declared reaction set loses a state or
    # leaves the intended fixed-inventory class.
    if root not in index or any(m + 2*d != n for m, d in states):
        raise AssertionError("Invalid hand-enumerated inventory class")
    return net


def _stationary(n: int, states: list[tuple[int, int]]) -> np.ndarray:
    weights = np.array([1.0 / (math.factorial(m) * math.factorial(d))
                        for m, d in states], dtype=float)
    return weights / weights.sum()


def _sampling_check(observed: np.ndarray, expected: np.ndarray) -> dict:
    samples = int(observed.sum())
    frequencies = observed / samples
    margin = 6 * np.sqrt(expected * (1 - expected) / samples) + 1 / samples
    error = np.abs(frequencies - expected)
    return {"samples": samples, "observed": frequencies.tolist(), "expected": expected.tolist(),
            "absolute_errors": error.tolist(), "six_sigma_plus_one_count_margin": margin.tolist(),
            "passed": bool(np.all(error <= margin))}


def _engine_paths():
    package = Path(importlib.util.find_spec("bionetgen").origin).parent
    engine = package / "bng-win"
    perl = shutil.which("perl") or "C:/Program Files/Git/usr/bin/perl.exe"
    if not engine.exists() or not Path(perl).exists():
        raise RuntimeError("Local BioNetGen 2.9.3 and Perl runtime are required")
    if importlib.metadata.version("bionetgen") != "0.8.7" or (engine / "VERSION").read_text().strip() != "2.9.3":
        raise RuntimeError("Fixture A protocol requires BioNetGen package 0.8.7 / engine 2.9.3")
    return engine, Path(perl)


def run(out: Path) -> dict:
    """Generate, audit and measure fixture A into `out`; return compact result."""
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    if protocol["status"] != "frozen_before_scientific_run":
        raise RuntimeError("Fixture A protocol is not frozen")
    engine, perl = _engine_paths()
    env = os.environ.copy()
    env["BNGPATH"] = engine.as_posix()
    source_hash = _digest(PROTOCOL_PATH)
    result = {"schema_version": "omega-assembly-result/1", "protocol_sha256": source_hash,
              "cases": {}, "audits": {}, "scope": protocol["representation"]["scope"]}
    max_q_error = max_balance_error = max_p_row_error = max_semigroup_error = 0.0
    max_inventory_change = 0
    state_count = generated = 0
    sampler_case = None

    for arm in ARMS:
        for n in protocol["representation"]["inventory_values"]:
            for label, root in (("unassembled", _root(n, False)), ("assembled", _root(n, True))):
                case_id = f"{arm}_N{n}_{label}"
                folder = out / "engine" / case_id
                folder.mkdir(parents=True, exist_ok=True)
                model = folder / "model.bngl"
                model.write_text(_model_text(arm, n, label == "assembled", protocol), encoding="utf-8")
                with (folder / "generation.log").open("w", encoding="utf-8") as log:
                    subprocess.run([str(perl), (engine / "BNG2.pl").as_posix(), model.name],
                                   cwd=folder, env=env, stdout=log, stderr=subprocess.STDOUT,
                                   check=True, timeout=20)
                generated += 1
                parsed = parse_net(folder / "model.net")
                molecule_weights = [1 if name.startswith("M(") else 2 if name.startswith("D(") else None
                                    for name in parsed.species]
                if any(weight is None for weight in molecule_weights):
                    raise AssertionError(f"Unexpected species in generated model: {parsed.species}")
                for reaction in parsed.reactions:
                    inventory_delta = (sum(molecule_weights[i] for i in reaction.products)
                                       - sum(molecule_weights[i] for i in reaction.reactants))
                    max_inventory_change = max(max_inventory_change, abs(inventory_delta))
                    if inventory_delta:
                        raise AssertionError(f"Generated reaction changes M+2D in {case_id}")
                hand = _hand_network(arm, n, root)
                states, q = enumerate_generator(parsed, state_cap=protocol["engineering_caps"]["state_cap"])
                hand_states, hand_q = enumerate_generator(hand, state_cap=protocol["engineering_caps"]["state_cap"])
                # Compiler order is BFS-dependent. Compare generator after state mapping.
                if parsed.species != hand.species:
                    raise AssertionError(f"Unexpected BNG species order in {case_id}: {parsed.species}")
                if set(states) != set(hand_states):
                    raise AssertionError(f"Generated and hand state sets differ in {case_id}")
                permutation = [states.index(s) for s in hand_states]
                q = q[np.ix_(permutation, permutation)]
                q_error = float(np.max(np.abs(q - hand_q)))
                max_q_error = max(max_q_error, q_error)
                if q_error > 1e-12:
                    raise AssertionError(f"Generated generator differs from hand law in {case_id}: {q_error}")
                if arm == "reversible_base" and n == 4 and label == "unassembled":
                    sampler_case = (folder / "model.net", parsed, hand_states.copy(), q.copy())
                pi = _stationary(n, hand_states)
                balance_error = float(np.max(np.abs(pi[:, None] * q - (pi[:, None] * q).T)))
                max_balance_error = max(max_balance_error, balance_error)
                if balance_error > 1e-12:
                    raise AssertionError(f"Detailed balance failed in {case_id}: {balance_error}")
                deltas = [protocol["measurement"]["primary_delta"], *protocol["measurement"]["sensitivity_deltas"]]
                profile = []
                for delta in deltas:
                    p = transition(q, delta)
                    row_error = float(np.max(np.abs(p.sum(axis=1) - 1)))
                    p2_error = float(np.max(np.abs(p @ p - transition(q, 2*delta))))
                    max_p_row_error = max(max_p_row_error, row_error)
                    max_semigroup_error = max(max_semigroup_error, p2_error)
                    for horizon in protocol["measurement"]["horizons"]:
                        steps = round(horizon / delta)
                        if abs(steps * delta - horizon) > 1e-12:
                            raise ValueError("A frozen cadence does not divide a horizon")
                        breadth = history_bits(p, steps)
                        assembled_index = hand_states.index(_root(n, True))
                        unassembled_index = hand_states.index(_root(n, False))
                        baseline = float(pi @ breadth)
                        profile.append({"delta": delta, "horizon": horizon,
                                        "unassembled_bits": float(breadth[unassembled_index]),
                                        "assembled_bits": float(breadth[assembled_index]),
                                        "assembled_minus_unassembled_bits": float(breadth[assembled_index] - breadth[unassembled_index]),
                                        "same_law_stationary_conditional_baseline_bits": baseline})
                state_count = max(state_count, len(states))
                result["cases"][case_id] = {
                    "arm": arm, "inventory": n, "root": label, "root_state": list(root),
                    "species": parsed.species, "generated_coefficients": [r.coefficient for r in parsed.reactions],
                    "generated_reactions": len(parsed.reactions), "reachable_states": len(states),
                    "generator_max_abs_error_vs_hand": q_error,
                    "detailed_balance_max_abs_flux_error": balance_error,
                    "stationary_distribution": pi.tolist(), "breadth_profile": profile
                }

    if sampler_case is None:
        raise AssertionError("The predeclared sampler reference case was not generated")
    net_path, sampler_network, sampler_states, sampler_q = sampler_case
    sampler_horizon = 1.0
    expected = transition(sampler_q, sampler_horizon)[0]
    sample_counts = np.zeros(len(sampler_states), dtype=float)
    for state, count in ssa_endpoints(sampler_network, sampler_horizon,
                                      protocol["seeds"]["own_ssa_samples"],
                                      protocol["seeds"]["own_ssa"] ).items():
        sample_counts[sampler_states.index(state)] += count
    own_ssa = _sampling_check(sample_counts, expected)

    engine_ssa_dir = out / "official_ssa"
    engine_ssa_dir.mkdir(parents=True, exist_ok=True)
    engine_counts = np.zeros(len(sampler_states), dtype=float)
    runner = engine / "bin" / "run_network.exe"
    for seed in range(protocol["seeds"]["official_engine_ssa_start"],
                      protocol["seeds"]["official_engine_ssa_start"] + protocol["seeds"]["official_engine_ssa_samples"]):
        prefix = engine_ssa_dir / str(seed)
        subprocess.run([str(runner), "-p", "ssa", "-h", str(seed), "-o", str(prefix),
                        str(net_path), str(sampler_horizon), "1"], cwd=engine_ssa_dir,
                       capture_output=True, text=True, check=True, timeout=10)
        table = np.loadtxt(prefix.with_suffix(".cdat"))
        endpoint = table[-1, 1:]
        if not np.allclose(endpoint, np.rint(endpoint), atol=1e-10):
            raise AssertionError("Official engine SSA returned a noninteger population state")
        engine_counts[sampler_states.index(tuple(np.rint(endpoint).astype(int)))] += 1
    official_ssa = _sampling_check(engine_counts, expected)
    result["sampler_check"] = {"case": "reversible_base_N4_unassembled", "horizon": sampler_horizon,
                               "expected_endpoint_distribution": expected.tolist(),
                               "own_ssa": own_ssa, "official_engine_ssa": official_ssa}
    result["audits"] = {
        "all_engine_networks_generated": generated == protocol["engineering_caps"]["network_generations"],
        "generated_reactions_conserve_M_plus_2D": max_inventory_change == 0,
        "own_direct_ssa_matches_generator": own_ssa["passed"],
        "official_bng_ssa_matches_generator": official_ssa["passed"],
        "generated_vs_hand_generator_max_abs_error": max_q_error,
        "detailed_balance_max_abs_flux_error": max_balance_error,
        "transition_row_sum_max_abs_error": max_p_row_error,
        "semigroup_max_abs_error": max_semigroup_error,
        "maximum_reachable_state_count": state_count,
        "all_pass": (generated == protocol["engineering_caps"]["network_generations"]
                     and max_inventory_change == 0 and own_ssa["passed"] and official_ssa["passed"]
                     and max_q_error <= 1e-12 and max_balance_error <= 1e-12
                     and max_p_row_error <= 1e-11 and max_semigroup_error <= 1e-11)
    }
    result["runtime_seconds"] = time.perf_counter() - start
    _json_write(out / "result.json", result)
    return result
