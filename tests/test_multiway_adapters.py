"""Focused checks for adapters into the reusable classical multiway core."""

from collections import defaultdict

import numpy as np

from omega_v2.finite.extent_probe_models import deterministic_builder, independent_flips
from omega_v2.finite.lattice_chemistry import LatticeChemistry, Parameters, State
from omega_v2.finite.lattice_compartment import CompartmentChemistry, LocalState, Reservoir
from omega_v2.finite.multiway import MultiwaySystem
from omega_v2.finite.multiway_adapters import LatticeAdapter, ProductAdapter, TableAdapter


def _branch_weights(system, node):
    result = defaultdict(float)
    for branch in system.expand(node):
        result[branch.target] += branch.weight
    return result


def _native_lattice_row(adapter, state):
    result = defaultdict(float)
    for step in adapter.steps(state):
        result[adapter.key(step.target)] += step.weight
    return result


def test_table_adapter_uses_complete_rows_and_ignores_device_preparation():
    first = TableAdapter.from_device(independent_flips(2, 0.25, "first"))
    device = independent_flips(2, 0.25, "second")
    device.initial = {(1, 1): 1.0}
    second = TableAdapter.from_device(device)

    assert first.identity == second.identity
    assert first.decode(first.encode((0, 1))) == (0, 1)
    assert first.key((0, 1)) == (0, 1)
    assert {(step.target, step.weight) for step in first.steps((0, 0))} == {
        ((0, 0), 0.5625), ((0, 1), 0.1875), ((1, 0), 0.1875), ((1, 1), 0.0625)
    }
    assert all(step.channel is None and step.incidence is None
               for step in first.steps((0, 0)))


def test_ctmc_table_adapter_exposes_only_positive_off_diagonal_rates():
    from omega_v2.finite.native_joint_continuation import FiniteContinuationLaw

    law = FiniteContinuationLaw(((0,), (1,)), ((-2.0, 2.0), (3.0, -3.0)),
                                clock="continuous")
    adapter = TableAdapter(law)
    row = tuple(adapter.steps((0,)))
    assert len(row) == 1
    assert (row[0].target, row[0].weight) == ((1,), 2.0)
    system = MultiwaySystem(adapter)
    node = system.intern((0,))
    branches = system.expand(node)
    assert len(branches) == 1
    assert branches[0].weight == 2.0


def test_ctmc_product_is_the_kronecker_sum():
    from omega_v2.finite.native_joint_continuation import FiniteContinuationLaw

    left = TableAdapter(FiniteContinuationLaw(((0,), (1,)),
                                               ((-2.0, 2.0), (2.0, -2.0)),
                                               clock="continuous"))
    right = TableAdapter(FiniteContinuationLaw(((0,), (1,)),
                                                ((-5.0, 5.0), (5.0, -5.0)),
                                                clock="continuous"))
    product_adapter = ProductAdapter((left, right))
    system = MultiwaySystem(product_adapter)
    root = system.intern(((0,), (0,)))
    weights = _branch_weights(system, root)
    targets = {system.state(node): weight for node, weight in weights.items()}
    assert targets == {((1,), (0,)): 2.0, ((0,), (1,)): 5.0}


def test_discrete_native_parallel_update_is_not_serialized():
    device = deterministic_builder("parallel")
    adapter = TableAdapter.from_device(device)
    system = MultiwaySystem(adapter)
    root = system.intern((0, 0, 0))
    branches = system.expand(root)
    assert len(branches) == 1
    assert system.state(branches[0].target) == (1, 1, 1)
    assert branches[0].weight == 1.0


def test_lattice_shared_native_rows_and_particle_relabeling():
    model = LatticeChemistry(Parameters(side=2, particles=3, capacity=2,
                                        diffusion=0.0, switching=0.2))
    state = State([(0, 0), (1, 0), (0, 1)], [1, 0, 1], {(0, 1)}, 1)
    model.validate(state)
    adapter = LatticeAdapter(model)
    canonical = adapter.canonical(state)
    permuted = State([state.positions[i] for i in (2, 0, 1)],
                     [state.internal[i] for i in (2, 0, 1)], {(1, 2)}, state.fuel)

    assert adapter.key(state) == adapter.key(permuted)
    assert adapter.decode(adapter.encode(state)) == canonical
    expected = defaultdict(float)
    for event in model.events(state):
        after = state.copy()
        model.apply(after, event)
        expected[adapter.key(after)] += event.rate
    observed = _native_lattice_row(adapter, state)
    assert observed.keys() == expected.keys()
    assert all(np.isclose(observed[key], expected[key]) for key in expected)


def test_lattice_local_state_keeps_each_fuel_and_waste_coordinate():
    parameters = Parameters(side=2, particles=2, capacity=2, diffusion=0.0,
                            switching=0.0, thermal_binding=0.0, fuel_binding=0.0)
    model = CompartmentChemistry(parameters, Reservoir(grid=(2, 1), transport=1.0))
    state = LocalState([(0, 0), (1, 0)], [1, 1], set(), [1, 0], [0, 1])
    model.validate(state)
    adapter = LatticeAdapter(model)

    encoded = adapter.encode(state)
    decoded = adapter.decode(encoded)
    assert decoded == adapter.canonical(state)
    assert decoded[3:] == ((1, 0), (0, 1))
    expected = _native_lattice_row(adapter, state)
    observed = _native_lattice_row(adapter, decoded)
    assert expected.keys() == observed.keys()
    assert all(np.isclose(expected[key], observed[key]) for key in expected)


def test_physical_route_refinement_keeps_generator_and_carries_template_location():
    p = Parameters(side=2, particles=4, capacity=1, catalytic_barrier=2, diffusion=0)
    model = LatticeChemistry(p)
    state = State([(0, 0), (1, 0), (0, 1), (1, 1)], [1]*4, {(0, 1)}, 1)
    systems = [MultiwaySystem(LatticeAdapter(model, resolve_routes=refine))
               for refine in (False, True)]
    rows = []
    for system in systems:
        root = system.intern(state)
        row = system.expand(root)
        rows.append(row)
    assert len(rows[1]) > len(rows[0])
    assert any(b.channel == ("template_at", ((0, 0), (1, 0))) for b in rows[1])
    by_state = []
    for system, row in zip(systems, rows, strict=True):
        rates = defaultdict(float)
        for branch in row:
            rates[system.state(branch.target)] += branch.weight
        by_state.append(rates)
    assert by_state[0] == by_state[1]
    assert systems[0].law_id != systems[1].law_id  # different declared path resolutions
