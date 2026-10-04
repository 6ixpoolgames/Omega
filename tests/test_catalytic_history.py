import numpy as np

from omega_v2.finite.catalytic_binding import CatalyticBinding
from omega_v2.finite.catalytic_history import CatalyticHistory


def test_history_observer_preserves_physics_and_mass():
    model = CatalyticBinding(barrier=1)
    observer = CatalyticHistory(model)
    assert observer.lumping_error() < 1e-12
    killed = observer.no_descendant_formation_generator()
    assert np.allclose(np.asarray(killed.sum(axis=1)).ravel(), -observer.history_rates[:, 1])
    law, occupation = observer.evolve(observer.initial, 0.5)
    assert abs(law.sum() - 1) < 1e-12
    assert abs(occupation.sum() - 0.5) < 1e-12
    assert np.allclose(observer.physical_law(law), model.advance(model.initial("seeded"), 0.5))
    summary = observer.summary(law, occupation)
    assert np.isclose(1 - summary["original_survival"], summary["history_event_counts"][4])
    assert np.isclose(
        summary["descendant_bonds_mean"],
        summary["history_event_counts"][0]
        + summary["history_event_counts"][1]
        - summary["history_event_counts"][5],
    )


def test_production_marks_follow_motion_and_do_not_resurrect():
    model = CatalyticBinding(barrier=1)
    observer = CatalyticHistory(model)
    x = model.index[(0, 0, 0, 0, -1, 1, 2)]
    c = model.channel_names.index("catalytic_bond_1_via_0")
    y = model.targets[c, x]
    r, d, h, _ = observer.step(x, 1, 0, 0, c, y)
    assert (r, d, h) == (1, 2, 1)
    c = model.channel_names.index("thermal_bond_0_1")
    z = model.targets[c, y]
    r, d, h, _ = observer.step(y, r, d, h, c, z)
    assert (r, d, h) == (0, 2, 1)
    # Independent reassembly at the former original position is not ancestry.
    c = model.channel_names.index("fuel_bond_0_1")
    y2 = model.targets[c, z]
    assert observer.step(z, r, d, h, c, y2)[:3] == (0, 2, 1)
    c = model.channel_names.index("catalytic_bond_0_via_1")
    assert observer.step(z, r, d, h, c, model.targets[c, z])[:3] == (0, 3, 2)
    # A whole bonded trimer moves; both historical marks move with its bonds.
    x = model.index[(0, 0, 0, -1, 0, 3, 1)]
    c = model.channel_names.index("move_0_3_1")
    assert observer.step(x, 1, 2, 1, c, model.targets[c, x])[:3] == (2, 4, 1)


def test_no_catalytic_ancestry_when_pathway_absent():
    model = CatalyticBinding(barrier=0)
    observer = CatalyticHistory(model)
    assert np.all(observer.states[:, 2:] == 0)
    assert observer.lumping_error() < 1e-12
