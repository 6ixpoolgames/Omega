from itertools import product

import numpy as np

from omega_v2.finite.history_volume import HistoryVolume, entropy


def test_joint_copies_count_once_and_keep_locations():
    values = np.array([(a, b, a) for a, b in product((0, 1), repeat=2)])
    m = HistoryVolume(values, (0, 0, 0))
    result = m.pair_profile(np.ones(4) / 4, np.eye(4))
    assert np.isclose(result["history_bits"][5], 1)  # Two copies of a.
    assert np.isclose(result["history_bits"][3], 2)  # a and independent b.
    assert np.isclose(result["history_log2_volume"][5], -1)
    same = next(g for g in m.content_catalog() if 1 in g["masks"])
    assert set(same["masks"]) == {1, 4, 5}
    assert set(same["minimal_coverage_masks"]) == {1, 4}


def test_temporal_marginalization_matches_direct_history_enumeration():
    values = np.array([(a, b) for a, b in product((0, 1), repeat=2)])
    m = HistoryVolume(values, (0, 1))
    p = np.array([0.1, 0.2, 0.3, 0.4])
    k = np.array(
        [[0.5, 0.2, 0.2, 0.1], [0.1, 0.6, 0.2, 0.1], [0.3, 0.2, 0.4, 0.1], [0.1, 0.1, 0.2, 0.6]]
    )
    two = m.pair_profile(p, k @ k)
    three = m.three_cut_profile(p, k, "test")
    joint = p[:, None, None] * k[:, :, None] * k[None, :, :]
    assert np.isclose(three["whole_history_bits"], entropy(joint))
    for row in three["frames"]:
        code, width = m.codes[row["mask"]], m.widths[row["mask"]]
        triple = code[:, None, None] * width**2 + code[None, :, None] * width + code[None, None, :]
        observed = np.bincount(triple.ravel(), weights=joint.ravel(), minlength=width**3)
        assert np.isclose(row["history_bits"], entropy(observed))
    # Consistent state relabelling changes no frame quantity.
    perm = np.array([2, 0, 3, 1])
    alt = HistoryVolume(values[perm], (0, 1)).pair_profile(p[perm], (k @ k)[np.ix_(perm, perm)])
    assert np.allclose(two["history_bits"], alt["history_bits"])


def test_random_history_is_retained_and_whole_normalization_is_explicit():
    m = HistoryVolume(np.array([[0], [1]]), (0,))
    p = np.ones(2) / 2
    frozen = m.pair_profile(p, np.eye(2))
    noise = m.pair_profile(p, np.ones((2, 2)) / 2)
    assert frozen["whole_history_bits"] == 1
    assert noise["whole_history_bits"] == 2
    assert frozen["history_log2_volume"][1] == noise["history_log2_volume"][1] == 0
    # Present-only memory holds a smaller share of the more variable history.
    assert noise["present_log2_volume"][1] < frozen["present_log2_volume"][1]
