import copy
import json
import math

import numpy as np
import pytest
from scipy.stats import poisson

from omega_v2.finite.extent_probe_models import deterministic_builder, reconvergent
from omega_v2.finite.multiway import ExpansionLimit, MultiwaySystem, NativeStep
from omega_v2.finite.multiway_adapters import TableAdapter
from omega_v2.finite.native_joint_continuation import FiniteContinuationLaw, Observation


def switch():
    law = FiniteContinuationLaw(((0,), (1,)), ((-2., 2.), (2., -2.)), clock="continuous")
    system = MultiwaySystem(TableAdapter(law))
    return system, system.intern((0,))


def test_lazy_frontier_is_unknown_not_dead_and_row_cap_is_atomic():
    system, root = switch()
    assert system.row(root) is None
    with pytest.raises(ExpansionLimit):
        system.expand(root, max_states=1)
    assert len(system) == 1 and system.row(root) is None
    view = system.explore(root, max_states=1)
    assert not view.complete and system.at(view, 3).frontier_mass == 1
    view = system.explore(root, max_states=2)
    assert view.complete and len(view.nodes) == 2
    assert np.isclose(system.at(view, .7).probabilities[1], (1 - math.exp(-2.8))/2)


def test_stopped_frontier_mass_is_first_exit_not_final_endpoint():
    system, root = switch()
    partial = system.explore(root, max_depth=1)
    result = system.at(partial, 1)
    assert np.isclose(result.frontier_mass, 1 - math.exp(-2))
    full = system.explore(root)
    assert system.at(full, 1).probabilities[1] < result.frontier_mass
    assert result.mass == pytest.approx(1)


def test_ctmc_unfolding_has_exact_poisson_tail_partition_and_shared_residuals():
    system, root = switch()
    tree = system.unfold(root, max_depth=3)
    assert len(system) == 2 and len(tree.occurrences) == 4
    partition = tree.partition(.75)
    assert partition.mass == pytest.approx(1)
    assert partition.frontier_mass == pytest.approx(poisson.sf(2, 1.5))
    assert tree.probability(2, .75) == pytest.approx(poisson.pmf(2, 1.5))
    assert tree.probability(2, .75, prefix=True) == pytest.approx(poisson.sf(1, 1.5))
    assert system.unfold(root, max_depth=5).partition(.75).frontier_mass < partition.frontier_mass


def test_reconvergence_preserves_occurrences_not_extra_present_properties():
    system = MultiwaySystem(TableAdapter.from_device(reconvergent()))
    root = system.intern((0,))
    tree = system.unfold(root, max_depth=2)
    leaves = [tree.occurrences[i] for i in tree.frontier]
    assert len(leaves) == 2 and leaves[0].residual == leaves[1].residual
    assert leaves[0].parent != leaves[1].parent
    assert tree.partition(2).mass == pytest.approx(1)
    terminal = leaves[0].residual
    rerooted = system.explore(terminal)
    assert len(rerooted.nodes) == 1
    assert system.at(rerooted, 3).probabilities == (1.,)


def test_occurrence_limit_keeps_entire_unexpanded_cylinder():
    system = MultiwaySystem(TableAdapter.from_device(reconvergent()))
    root = system.intern((0,))
    tree = system.unfold(root, max_depth=5, max_occurrences=2)
    assert len(tree.occurrences) == 1
    assert tree.partition(10).frontier_mass == 1


def test_synchronous_update_and_native_joint_export():
    system = MultiwaySystem(TableAdapter.from_device(deterministic_builder("parallel")))
    root = system.intern((0, 0, 0))
    view = system.explore(root)
    law = system.joint_law(view)
    table = law.joint((0, 0, 0), [Observation(1, (0, 1, 2))])
    assert table.probability(((1, 1, 1),)) == 1
    with pytest.raises(ValueError, match="closed"):
        system.joint_law(system.explore(root, max_depth=0))


def test_checkpoint_roundtrip_resume_and_reject_wrong_law_or_tampering():
    system, root = switch()
    system.explore(root, max_depth=1)
    record = json.loads(json.dumps(system.snapshot((root,))))
    restored = MultiwaySystem.restore(system.adapter, record)
    assert restored.snapshot((root,)) == record
    assert restored.row(1) is None
    full = restored.explore(root)
    expected = system.at(system.explore(root), .4).probabilities
    assert restored.at(full, .4).probabilities == pytest.approx(expected)
    bad = copy.deepcopy(record)
    bad["rows"][0][0]["weight"] *= 2
    with pytest.raises(ValueError, match="row"):
        MultiwaySystem.restore(system.adapter, bad)
    bad = copy.deepcopy(record)
    bad["law_id"] = "different law"
    with pytest.raises(ValueError, match="mismatch"):
        MultiwaySystem.restore(system.adapter, bad)


def test_invalid_weights_are_rejected_before_row_or_state_mutation():
    class Invalid(TableAdapter):
        def steps(self, state):
            yield NativeStep((1,), .5)
            yield NativeStep((1,), -.5)
    adapter = Invalid(FiniteContinuationLaw(((0,), (1,)), ((.5, .5), (0, 1))))
    system = MultiwaySystem(adapter)
    root = system.intern((0,))
    with pytest.raises(ValueError):
        system.expand(root)
    assert len(system) == 1 and system.row(root) is None


def test_duplicate_rows_do_not_create_extra_branches_or_change_law():
    class Split(TableAdapter):
        def steps(self, state):
            for step in super().steps(state):
                yield NativeStep(step.target, step.weight / 2)
                yield NativeStep(step.target, step.weight / 2)
    law = FiniteContinuationLaw(((0,), (1,)), ((.25, .75), (.5, .5)))
    normal, split = MultiwaySystem(TableAdapter(law)), MultiwaySystem(Split(law))
    for system in (normal, split):
        system.intern((0,))
    assert normal.expand(0) == split.expand(0)
    assert normal.at(normal.explore(0), 3) == split.at(split.explore(0), 3)


def test_absorbing_ctmc_and_zero_horizon_keep_unit_mass():
    system = MultiwaySystem(TableAdapter(FiniteContinuationLaw(((0,),), ((0.,),), clock="continuous")))
    root = system.intern((0,))
    tree = system.unfold(root, max_depth=10)
    assert tree.frontier == () and tree.partition(100).mass == 1
    assert system.at(system.explore(root), 0).probabilities == (1.,)


def test_native_sampling_replay_and_event_limit_do_not_bias_returned_law():
    system, root = switch()
    path = system.sample(root, 2, seed=7)
    assert system.replay(path) == pytest.approx(path.log_weight)
    assert path.log_weight == pytest.approx(len(path.events)*math.log(2) - 4)
    with pytest.raises(ExpansionLimit):
        system.sample(root, 100, seed=7, max_events=0)
    discrete = MultiwaySystem(TableAdapter.from_device(reconvergent()))
    start = discrete.intern((0,))
    sample = discrete.sample(start, 5, seed=2)
    assert len(sample.events) == 5
    assert discrete.replay(sample) == pytest.approx(math.log(.5))


def test_views_and_samples_cannot_silently_use_different_residual_numbering():
    system, root = switch()
    view = system.explore(root)
    sample = system.sample(root, 1, seed=2)
    other = MultiwaySystem(system.adapter)
    other.intern((1,))
    other.intern((0,))
    assert other.law_id == system.law_id
    with pytest.raises(ValueError, match="indexing"):
        other.at(view, 1)
    with pytest.raises(ValueError, match="indexing"):
        other.replay(sample)
