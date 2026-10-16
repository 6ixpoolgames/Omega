import numpy as np
import pytest

from omega_v2.finite.rooted_path_signature import (
    concatenate,
    retained_coordinates,
    signature,
    timed_state_increments,
)


def test_level_two_distinguishes_parallel_from_serial_updates():
    parallel = signature(np.array([[1.0, 1.0]]), 2)
    serial = signature(np.array([[1.0, 0.0], [0.0, 1.0]]), 2)

    # Flattened level two uses words (00, 01, 10, 11).
    assert parallel[2][1] == pytest.approx(0.5)
    assert parallel[2][2] == pytest.approx(0.5)
    assert serial[2][1] == pytest.approx(1.0)
    assert serial[2][2] == pytest.approx(0.0)


def test_chen_concatenation_matches_whole_path_and_collinear_subdivision():
    first = np.array([[0.5, 0.0]])
    second = np.array([[0.5, 0.0], [0.0, 1.0]])
    split = concatenate(signature(first, 4), signature(second, 4))
    whole = signature(np.vstack((first, second)), 4)
    flatten = lambda levels: np.concatenate([level.reshape(-1) for level in levels])
    np.testing.assert_allclose(flatten(split), flatten(whole))

    one_segment = signature(np.array([[2.0, 0.0]]), 4)
    subdivided = concatenate(signature(np.array([[1.0, 0.0]]), 4),
                             signature(np.array([[1.0, 0.0]]), 4))
    np.testing.assert_allclose(flatten(one_segment), flatten(subdivided))


def test_terminal_wait_does_not_change_retained_coordinates():
    path = signature(np.array([[0.0, 1.0], [1.0, 0.0]]), 3)
    with_wait = concatenate(path, signature(np.array([[2.0, 0.0]]), 3))
    values, words = retained_coordinates(path, physical_dim=1)
    wait_values, wait_words = retained_coordinates(with_wait, physical_dim=1)
    assert words == wait_words
    np.testing.assert_allclose(values, wait_values)


def test_delay_before_change_changes_mixed_time_physical_word():
    early = signature(np.array([[0.0, 1.0], [1.0, 0.0]]), 2)
    delayed = signature(np.array([[1.0, 0.0], [0.0, 1.0]]), 2)
    early_values, early_words = retained_coordinates(early, physical_dim=1)
    delayed_values, delayed_words = retained_coordinates(delayed, physical_dim=1)
    assert early_words == delayed_words
    xy = early_words.index((0, 1))
    assert early_values[xy] == pytest.approx(0.0)
    assert delayed_values[xy] == pytest.approx(1.0)


def test_native_clock_lift_separates_wait_and_state_change():
    increments = timed_state_increments(np.array([[0.0], [2.0], [2.0]]),
                                        np.array([0.0, 1.0, 3.0]))
    np.testing.assert_array_equal(increments, [[1.0, 0.0], [0.0, 2.0],
                                                [2.0, 0.0], [0.0, 0.0]])


@pytest.mark.parametrize('increments, degree', [
    (np.array([1.0, 2.0]), 2),
    (np.array([[np.nan]]), 1),
    (np.array([[1.0]]), 0),
    (np.array([[1.0]]), 5),
])
def test_signature_rejects_invalid_inputs(increments, degree):
    with pytest.raises(ValueError):
        signature(increments, degree)


def test_concatenate_rejects_mismatched_signature_shapes():
    with pytest.raises(ValueError):
        concatenate(signature(np.array([[1.0]]), 2),
                    signature(np.array([[1.0, 0.0]]), 2))


def test_timed_lift_rejects_decreasing_times():
    with pytest.raises(ValueError):
        timed_state_increments(np.array([[0.0], [1.0]]), np.array([1.0, 0.0]))
