"""Bounded integration run for the reusable multiway carrier; no extent score."""

import json
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.stats import poisson

from omega_v2.finite.extent_probe_models import (
    deterministic_builder,
    reconvergent,
    reversible_gate,
)
from omega_v2.finite.lattice_chemistry import LatticeChemistry, Parameters, State
from omega_v2.finite.lattice_compartment import CompartmentChemistry, Reservoir
from omega_v2.finite.lattice_transport_exact import exact_generator
from omega_v2.finite.multiway import MultiwaySystem
from omega_v2.finite.multiway_adapters import LatticeAdapter, ProductAdapter, TableAdapter
from omega_v2.finite.multiway_composition import (
    audit_factorization,
    audit_projection,
    audit_square,
)
from omega_v2.finite.native_joint_continuation import FiniteContinuationLaw, Observation


def run():
    start = perf_counter()
    output = Path("docs/research_notes/omega_v2/multiway_carrier_v0")
    output.mkdir(parents=True, exist_ok=True)
    report = {"scope": "classical carrier integration; no new physics or extent ranking"}
    q = np.array([[-2., 2.], [2., -2.]])
    bit = TableAdapter(FiniteContinuationLaw(((0,), (1,)), q, clock="continuous"))
    system = MultiwaySystem(bit)
    root = system.intern((0,))
    report["frontier"] = []
    for depth in (0, 1, 3, 5, 8):
        tree = system.unfold(root, max_depth=depth)
        partition = tree.partition(.75)
        report["frontier"].append({"depth": depth, "mass": partition.mass,
                                   "frontier_mass": partition.frontier_mass,
                                   "expected_poisson_tail": float(poisson.sf(depth - 1, 1.5))})
    product_system = MultiwaySystem(ProductAdapter((bit, bit)))
    product_root = product_system.intern(((0,), (0,)))
    product_view = product_system.explore(product_root)
    product_law = product_system.joint_law(product_view)
    audit = audit_factorization(product_law, ((0,), (1,)))
    report["independent_product"] = {"states": len(product_view.nodes),
                                     "factorizes": audit.holds, "error": audit.max_error,
                                     "endpoint_mass": product_system.at(product_view, 1).mass}
    report["contextual_gate"] = []
    for on in (False, True):
        gate = FiniteContinuationLaw.from_device(reversible_gate(on))
        # Existing logical clock. A lazy random-scan K is not a product K even
        # off-gate; test the declared CTMC analogue Q=K-I separately.
        continuous = FiniteContinuationLaw(gate.states, gate.operator - np.eye(4),
                                           clock="continuous")
        audit = audit_factorization(continuous, ((0,), (1,)))
        square = audit_square(continuous, (0, 0), (1, 0), (0, 1))
        report["contextual_gate"].append({"catalytic": on, "factorizes": audit.holds,
                                          "error": audit.max_error, "square": asdict(square)})
    report["deterministic"] = []
    for kind in ("parallel", "chain", "fork_join"):
        native = MultiwaySystem(TableAdapter.from_device(deterministic_builder(kind)))
        initial = native.intern((0, 0, 0))
        closed = native.explore(initial)
        law = native.joint_law(closed)
        observations = [Observation(t, (0, 1, 2)) for t in (0, 1, 2, 3)]
        joint = law.joint((0, 0, 0), observations)
        index = np.unravel_index(np.argmax(joint.probabilities), joint.probabilities.shape)
        report["deterministic"].append({"kind": kind, "states": len(closed.nodes),
                                        "path": [alphabet[i] for alphabet, i in
                                                 zip(joint.alphabets, index, strict=True)],
                                        "probability": float(joint.probabilities[index])})
    recon = MultiwaySystem(TableAdapter.from_device(reconvergent()))
    r = recon.intern((0,))
    tree = recon.unfold(r, max_depth=2)
    report["reconvergence"] = {"residuals": len(recon), "occurrences": len(tree.occurrences),
                                "frontier_residuals": [tree.occurrences[i].residual for i in tree.frontier],
                                "mass": tree.partition(2).mass}
    report["chemistry"] = []
    p = Parameters(side=2, particles=4, capacity=1, catalytic_barrier=2, diffusion=0)
    initial = State([(0, 0), (1, 0), (0, 1), (1, 1)], [1]*4, {(0, 1)}, 1)
    shared = LatticeChemistry(p)
    local = CompartmentChemistry(p, Reservoir(transport=1))
    for name, model, preparation in (("shared", shared, initial),
                                      ("local", local, local.lift(initial, np.random.default_rng(8)))):
        native = MultiwaySystem(LatticeAdapter(model))
        root = native.intern(preparation)
        partial = native.explore(root, max_expanded=12)
        early = native.at(partial, 1)
        cache = json.loads(json.dumps(native.snapshot((root,))))
        restored = MultiwaySystem.restore(native.adapter, cache)
        closed = restored.explore(root, max_states=3000, max_expanded=3000)
        if not closed.complete:
            raise AssertionError("bounded chemistry unexpectedly not closed")
        reference = exact_generator(model, preparation)
        order = [reference["index"][restored.state(i)] for i in closed.nodes]
        difference = restored.operator(closed) - reference["q"][order][:, order]
        generator_error = float(np.max(np.abs(difference.data), initial=0))
        cut = restored.at(closed, 1)
        sample = restored.sample(root, 5, seed=21)
        replay_error = abs(restored.replay(sample) - sample.log_weight)
        row = {"model": name, "states": len(closed.nodes),
               "branches": sum(len(restored.row(i)) for i in closed.expanded),
               "generator_error": generator_error, "mass_error": abs(cut.mass - 1),
               "partial_states": len(partial.nodes), "partial_frontier_mass": early.frontier_mass,
               "sample_events": len(sample.events), "replay_error": replay_error,
               "law_id": restored.law_id}
        if name == "local":
            projection = audit_projection(restored.joint_law(closed),
                                          lambda state: state[:3] + (sum(state[3]),))
            row["shared_fuel_projection_markov"] = projection.markov
            row["projection_generator_defect"] = projection.max_error
        report["chemistry"].append(row)
        (output / f"{name}_cache.json").write_text(
            json.dumps(restored.snapshot((root,)), separators=(",", ":")), encoding="utf-8")
    report["seconds"] = perf_counter() - start
    (output / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    run()
