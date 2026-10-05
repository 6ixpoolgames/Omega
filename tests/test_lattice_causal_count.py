from omega_v2.finite.lattice_causal_count import causal_count, dependencies, graph_profiles
from omega_v2.finite.lattice_chemistry import LatticeChemistry, Parameters, State


def trace(model, initial, steps):
    state, events = initial.copy(), []
    for time, kind, members, catalyst, direction in steps:
        event = next(e for e in model.events(state) if e.kind == kind
                     and e.members == members and e.catalyst == catalyst
                     and e.direction == direction)
        events.append(event.record(time))
        model.apply(state, event)
    return {"initial": initial.record(), "events": events, "final": state.record()}


def test_diamond_counts_unique_cones_but_distinct_routes():
    # Redundant edge 0->3 must not manufacture another causal route.
    rows, reduced = graph_profiles([[], [0], [0], [0, 1, 2]], (4,), (1, 2, 3, 4))
    row = rows[0]
    assert reduced == [[], [0], [0], [1, 2]]
    assert row["ancestor_pairs"] == 5 and row["cone_sum"] == 9
    assert row["routes_exact"] == "10"
    assert row["forks"] == row["mergers"] == 1
    assert row["depth"] == 3 and row["layer_breadth"] == 2


def test_zero_binding_energy_removes_rate_dependency_but_not_motion_guard():
    model = LatticeChemistry(Parameters(side=3, particles=2, bond_strength=0))
    state = State([(0, 0), (1, 0)], [1, 1], {(0, 1)}, 1)
    switch = next(e for e in model.events(state) if e.kind == "switch")
    assert dependencies(model, state, switch)[0] == {("internal", 0)}
    move = next(e for e in model.events(state) if e.kind == "move")
    assert ("bond", 0, 1) in dependencies(model, state, move)[0]
    reaction = next(e for e in model.events(state) if e.kind == "fuel")
    assert not any(k[0] == "internal" for k in dependencies(model, state, reaction)[0])


def test_separate_switches_are_separate_until_read_together():
    model = LatticeChemistry(Parameters(side=4, particles=2))
    initial = State([(0, 0), (3, 3)], [0, 0], set(), 0)
    trajectory = trace(model, initial, [(1, "switch", (0,), (), (0, 0)),
                                       (2, "switch", (1,), (), (0, 0)),
                                       (3, "switch", (0,), (), (0, 0))])
    result = causal_count(model, trajectory, (0, 3))
    assert result["parents"] == [[], [], [0]]
    assert result["full"][0]["events"] == 0
    assert result["full"][-1]["cone_sum"] == 4
    assert initial.internal == [0, 0]


def test_shared_pool_dependency_is_retained_and_decomposed():
    model = LatticeChemistry(Parameters(side=4, particles=4, capacity=4))
    initial = State([(0, 0), (1, 0), (0, 3), (1, 3)], [1]*4, set(), 4)
    trajectory = trace(model, initial, [(1, "fuel", (0, 1), (), (0, 0)),
                                       (2, "fuel", (2, 3), (), (0, 0))])
    result = causal_count(model, trajectory, (2,))
    assert result["parents"] == [[], [0]]
    assert result["parents_without_fuel"] == [[], []]


def test_released_site_and_new_template_supply_later_events():
    model = LatticeChemistry(Parameters(side=3, particles=2))
    initial = State([(0, 0), (1, 0)], [0, 0], set(), 0)
    trajectory = trace(model, initial, [(1, "move", (1,), (), (1, 0)),
                                       (2, "move", (0,), (), (1, 0))])
    assert causal_count(model, trajectory, (2,))["parents"] == [[], [0]]
    model = LatticeChemistry(Parameters(side=3, particles=6, catalytic_barrier=2))
    initial = State([(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)],
                    [1]*6, {(0, 1)}, 16)
    trajectory = trace(model, initial, [(1, "catalytic", (2, 3), (0, 1), (0, 0)),
                                       (2, "catalytic", (4, 5), (2, 3), (0, 0))])
    assert causal_count(model, trajectory, (2,))["parents_without_fuel"] == [[], [0]]
