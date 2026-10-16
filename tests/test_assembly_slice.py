import json
from pathlib import Path

import numpy as np

from omega_v2.testbed.assembly_slice import (
    PROTOCOL_PATH, _hand_network, _root, _stationary, run,
)
from omega_v2.testbed.bng_network import enumerate_generator


def test_protocol_is_frozen_and_defines_all_three_arms():
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    assert protocol["status"] == "frozen_before_scientific_run"
    assert protocol["representation"]["inventory_values"] == [2, 3, 4]
    assert set(protocol["arms"]) == {
        "reversible_base", "metastable_slow_reversible", "dimer_feedback"
    }
    assert protocol["measurement"]["primary_delta"] == 0.25
    assert protocol["measurement"]["horizons"] == [1, 4, 16, 64]


def test_hand_networks_conserve_inventory_and_preserve_ideal_mixture_balance():
    for arm in ("reversible_base", "metastable_slow_reversible", "dimer_feedback"):
        for n in (2, 3, 4):
            for assembled in (False, True):
                network = _hand_network(arm, n, _root(n, assembled))
                states, q = enumerate_generator(network, state_cap=16)
                assert len(states) == n // 2 + 1
                assert all(m + 2 * d == n for m, d in states)
                pi = _stationary(n, states)
                assert np.max(np.abs(pi[:, None] * q - (pi[:, None] * q).T)) < 1e-12


def test_bng_generated_networks_samplers_and_history_profiles(tmp_path):
    result = run(Path(tmp_path))
    assert result["audits"]["all_pass"]
    assert result["audits"]["generated_vs_hand_generator_max_abs_error"] == 0
    assert result["audits"]["all_engine_networks_generated"]
    assert len(result["cases"]) == 18
    assert result["sampler_check"]["own_ssa"]["passed"]
    assert result["sampler_check"]["official_engine_ssa"]["passed"]
    assert (Path(tmp_path) / "result.json").exists()
