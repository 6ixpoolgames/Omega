"""Execute and export the frozen record-routing and bath-spreading follow-up."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import UTC, datetime
from itertools import combinations
from pathlib import Path

import networkx as nx
import numpy as np

from omega_v2.experiments.quantum_record_structure_v0 import (
    PROTOCOL,
    PROTOCOL_SHA256,
    Gate,
    apparatus_graph,
    bath_bill,
    bath_layers,
    bath_setup,
    bath_start,
    diagonal_source,
    embedded_routes,
    evolve,
    gate_rows,
    inverse,
    isomorphic,
    rename_check,
    routing_bill,
    routing_setup,
    routing_state,
)
from omega_v2.finite.quantum_profile import (
    Density,
    contract_inputs,
    dephase,
    ensemble_density,
    mutual_information,
    profile,
)
from omega_v2.validation.quantum_frame_profile_v0 import git, matrix_rows

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = "docs/research_notes/validation_results/quantum_record_structure_v0/20261002"
SOURCES = (
    PROTOCOL,
    "omega_v2/finite/quantum_profile.py",
    "omega_v2/experiments/quantum_record_structure_v0.py",
    "omega_v2/validation/quantum_record_structure_v0.py",
    "omega_v2/validation/quantum_frame_profile_v0.py",
    "tests/test_quantum_record_structure.py",
)


def protocol_digest():
    return hashlib.sha256((ROOT/PROTOCOL).read_text(encoding="utf-8").encode()).hexdigest()


def state_checks(state):
    matrix = state.matrix()
    eig = np.linalg.eigvalsh(matrix)
    return {"trace_error": abs(state.trace()-1),
            "hermiticity_error": float(np.max(np.abs(matrix-matrix.conj().T))),
            "negative_eigenvalue_magnitude": max(0.0, -float(eig.min()))}


def delivery(state, sources, bank):
    measured = dephase(state)
    matrix = {source: {r: mutual_information(measured, [source], [r]) for r in bank}
              for source in sources}
    return {
        "source_register_information_bits": matrix,
        "source_pooled_information_bits": {s: mutual_information(measured, [s], bank)
                                            for s in sources},
        "singleton_90_percent_readers": {
            s: [r for r in bank if matrix[s][r] >= .9*measured.partial([s]).entropy()]
            for s in sources},
        "joint_content_bits": measured.partial(bank).entropy(),
        "joint_bank_law": {format(b, f"0{len(bank)}b"): p
                           for b, p in measured.partial(bank).law().items()},
    }


def fragment_rows(full):
    """CQ Holevo information, fixed Z readout, and explicitly ideal Helstrom ceiling."""
    bath = tuple(f"E{i}" for i in range(4))
    measured = dephase(full)
    rows = []
    for k in range(1, 5):
        for fragment in combinations(bath, k):
            joint = full.partial(("X", *fragment))
            size, mask = 2**k, 2**k-1
            weighted_difference = np.zeros((size, size), complex)
            for (r, c), v in joint.entries.items():
                if r >> k == c >> k:
                    weighted_difference[r & mask, c & mask] += v if r >> k == 0 else -v
            ceiling = .5*(1+sum(abs(np.linalg.eigvalsh(weighted_difference))))
            rows.append({
                "fragment": fragment, "size": k,
                "holevo_information_bits": mutual_information(full, ["X"], fragment),
                "z_readout_information_bits": mutual_information(measured, ["X"], fragment),
                "ideal_binary_guess_success": float(ceiling),
            })
    grouped = []
    for k in range(1, 5):
        members = [r for r in rows if r["size"] == k]
        grouped.append({"size": k, **{
            metric: {"min": min(r[metric] for r in members),
                     "mean": float(np.mean([r[metric] for r in members])),
                     "max": max(r[metric] for r in members)}
            for metric in ("holevo_information_bits", "z_readout_information_bits",
                           "ideal_binary_guess_success")}})
    return rows, grouped


def relational_controls():
    checks, graphs = {}, {}
    for mode in ("broadcast", "plural"):
        labels, sources, gates, _ = routing_setup(mode)
        observations = [(3, ("R0", "R1", "R2")), (6, ("D0", "D1", "D2")),
                        (9, ("G0", "G1", "G2"))]
        bus = [(s, f"R{i}") for s in sources for i in range(3)]
        result, original, back = rename_check(labels, sources, gates, diagonal_source(.8),
                                               observations, bus)
        result["mapped_record_profile_error"] = max(
            abs(x["mutual_information_bits"]-y["mutual_information_bits"])
            for x, y in zip(profile(original.partial(("R0", "R1", "R2")))["labelled_fragments"],
                            profile(back.partial(("R0", "R1", "R2")))["labelled_fragments"],
                            strict=True))
        checks[mode] = result
        graphs[mode] = apparatus_graph(labels, sources, gates, observations, bus)
    checks["broadcast_plural_isomorphic"] = isomorphic(graphs["broadcast"], graphs["plural"])
    a, ga = embedded_routes(False)
    b, gb = embedded_routes(True)
    checks["embedded_routing"] = {
        "isomorphic": isomorphic(ga, gb),
        "identity_anchor_reader_bits": mutual_information(a, ["A"], ["D"]),
        "swap_anchor_reader_bits": mutual_information(b, ["A"], ["D"]),
        "identity_state": matrix_rows(a), "swap_state": matrix_rows(b),
    }
    labels, start = bath_setup()
    gates = start+[g for layer in bath_layers("spreading")[:2] for g in layer]
    chain = [(f"E{i}", f"E{i+1}") for i in range(3)]
    result, _, _ = rename_check(labels, ("X",), gates, diagonal_source(.8),
                                 [(len(gates), ("E0", "E1", "E2", "E3"))], chain)
    checks["bath"] = result
    return checks


def run():
    if protocol_digest() != PROTOCOL_SHA256:
        raise RuntimeError("frozen protocol changed")
    errors = {"trace_error": 0.0, "hermiticity_error": 0.0,
              "negative_eigenvalue_magnitude": 0.0, "choi_contraction": 0.0,
              "channel_trace": 0.0, "bath_whole_information": 0.0,
              "bath_spectrum": 0.0}

    def check(state):
        for key, value in state_checks(state).items():
            errors[key] = max(errors[key], value)

    routing = {}
    for mode in ("broadcast", "plural"):
        results = []
        for cut in (3, 6, 9):
            choi, full_choi = routing_state(mode, cut, diagonal_source(.8), choi=True)
            check(choi)
            check(full_choi)
            refs = tuple(f"I{i}" for i in range(3))
            mm = Density(refs, {(i, i): 1/8 for i in range(8)})
            errors["channel_trace"] = max(errors["channel_trace"],
                                           choi.partial(refs).distance_max(mm))
            row = {"time": cut, "bill": routing_bill(cut), "choi_state": matrix_rows(choi),
                   "choi_profile": profile(choi), "preparations": []}
            for label, prep in (("p0_0.8", diagonal_source(.8)), ("p0_0.5", diagonal_source(.5)),
                                ("plus", np.ones((2, 2))/2),
                                ("y_plus", np.array([[1, -1j], [1j, 1]])/2)):
                actual, full = routing_state(mode, cut, prep)
                check(full)
                linked = contract_inputs(choi, {r: prep for r in refs})
                error = actual.distance_max(linked)
                errors["choi_contraction"] = max(errors["choi_contraction"], error)
                item = {"preparation": label, "contraction_error": error,
                        "full_state": matrix_rows(full), "interface_state": matrix_rows(actual)}
                if label.startswith("p0_"):
                    bank = tuple(label for label in actual.labels if not label.startswith("S"))
                    item.update({"delivery": delivery(actual, ("S0", "S1", "S2"), bank),
                                 "record_profile": profile(actual.partial(bank)),
                                 "source_and_record_profile": profile(actual),
                                 "full_entropy_bits": full.entropy()})
                row["preparations"].append(item)
            results.append(row)
        routing[mode] = results
        print(f"Completed matched routing: {mode}.", flush=True)
    bath = {}
    for mode in ("spreading", "echo"):
        per_prior = {}
        layers = bath_layers(mode)
        for p in (.8, .5):
            labels, ensemble = bath_start(p)
            snapshots = [ensemble]
            for layer in layers:
                ensemble = evolve(labels, ensemble, layer)
                snapshots.append(ensemble)
            boundaries = []
            expected_entropy = -p*np.log2(p)-(1-p)*np.log2(1-p)
            for depth, state_ensemble in enumerate(snapshots):
                full = ensemble_density(labels, state_ensemble)
                check(full)
                bath_names = tuple(f"E{i}" for i in range(4))
                whole_info = mutual_information(full, ["X"], bath_names)
                errors["bath_whole_information"] = max(errors["bath_whole_information"],
                                                       abs(whole_info-expected_entropy))
                # Compare all nonzero/zero eigenvalues on a fixed 128-dimensional space.
                spectrum = np.linalg.eigvalsh(full.matrix())
                target = np.zeros_like(spectrum)
                target[-2:] = sorted([p, 1-p])
                errors["bath_spectrum"] = max(errors["bath_spectrum"],
                                              float(max(abs(spectrum-target))))
                fragments, by_size = fragment_rows(full)
                boundaries.append({
                    "layer": depth, "bill": bath_bill(depth), "full_state": matrix_rows(full),
                    "prior_only_guess_success": max(p, 1-p),
                    "whole_source_information_bits": whole_info,
                    "source_record_information_bits": mutual_information(full, ["X"], ["R"]),
                    "bath_profile": profile(full.partial(bath_names)),
                    "source_bath_profile": profile(full.partial(("X", *bath_names))),
                    "fragments": fragments, "by_fragment_size": by_size,
                })
            recoveries = []
            if mode == "spreading":
                for depth in (0, 2, 4, 8):
                    prefixes = []
                    for undone in range(depth+1):
                        suffix = [g for layer in layers[depth-undone:depth] for g in layer]
                        undo = inverse(suffix)
                        decoder = [*undo, Gate("CX", "D", ("E0",))]
                        recovered = ensemble_density(labels, evolve(labels, snapshots[depth], decoder))
                        measured = dephase(recovered)
                        xd = measured.partial(("X", "D"))
                        law = xd.law()
                        prefixes.append({
                            "layers_undone": undone, "added_rotations": undone*8,
                            "added_CZ": undone*3, "readout_CNOT": 1,
                            "added_serial_time": 11*undone+1,
                            "total_time": 4+11*depth+11*undone+1,
                            "delivered_information_bits": mutual_information(measured, ["X"], ["D"]),
                            "correct_record_probability": law.get(0, 0)+law.get(3, 0),
                            "source_output_state": matrix_rows(xd),
                        })
                    recoveries.append({"depth": depth, "prefixes": prefixes})
            per_prior[str(p)] = {"boundaries": boundaries, "inverse_recovery": recoveries}
        bath[mode] = per_prior
        print(f"Completed bath control: {mode}.", flush=True)
    relational = relational_controls()
    if any(value > (1e-9 if key == "bath_whole_information" else 1e-11)
           for key, value in errors.items()):
        raise RuntimeError(f"representation validation failed: {errors}")
    for name in ("broadcast", "plural", "bath"):
        if (not relational[name]["graph_isomorphic"]
                or relational[name]["full_state_error_after_mapping_back"] > 1e-11):
            raise RuntimeError(f"relabel validation failed: {name}")
    return {"routing": routing, "bath": bath, "relational_controls": relational,
            "representation_errors": errors,
            "gate_catalogue": {
                "routing": {m: gate_rows(routing_setup(m)[2]) for m in ("broadcast", "plural")},
                "bath_initial": gate_rows(bath_setup()[1]),
                "bath_layers": {m: [gate_rows(layer) for layer in bath_layers(m)]
                                for m in ("spreading", "echo")},
            }}


def summary(results):
    routing = {mode: [{"time": r["time"], "bill": r["bill"],
                      "choi_by_size": r["choi_profile"]["by_size"],
                      "actual": [{"preparation": p["preparation"], **p["delivery"],
                                  "record_profile_by_size": p["record_profile"]["by_size"]}
                                 for p in r["preparations"] if "delivery" in p]}
                     for r in rows] for mode, rows in results["routing"].items()}
    bath = {mode: {prior: {
        "boundaries": [{"layer": b["layer"], "bill": b["bill"],
                        "whole_information_bits": b["whole_source_information_bits"],
                        "fragments_by_size": b["by_fragment_size"],
                        "bath_profile_by_size": b["bath_profile"]["by_size"]}
                       for b in case["boundaries"]],
        "inverse_recovery": case["inverse_recovery"]}
        for prior, case in priors.items()} for mode, priors in results["bath"].items()}
    return {"routing": routing, "bath": bath, "representation_errors": results["representation_errors"],
            "relational_controls": results["relational_controls"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    results = run()
    results["provenance"] = {
        "generated_utc": datetime.now(UTC).isoformat(), "protocol_sha256": PROTOCOL_SHA256,
        "python": platform.python_version(), "numpy": np.__version__, "networkx": nx.__version__,
        "branch": git("branch", "--show-current"), "head": git("rev-parse", "HEAD"),
        "source_sha256": {s: hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in SOURCES},
        "method": "Finite enumeration, deterministic circuit, no fitting or Monte Carlo.",
    }
    destination = ROOT/args.output
    destination.mkdir(parents=True, exist_ok=True)
    for filename, content in (("evidence.json", results), ("summary.json", summary(results))):
        (destination/filename).write_text(json.dumps(content, indent=2, allow_nan=False)+"\n",
                                          encoding="utf-8")
    print(json.dumps({"output": str(destination), "errors": results["representation_errors"]}))


if __name__ == "__main__":
    main()
