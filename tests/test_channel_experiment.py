"""Tiny integration checks for the channel experiment contract, not research evidence."""
from dataclasses import asdict

import pytest

from omega_v2.testbed import growing_population as legacy
from omega_v2.testbed.experiments.channel_comparison import scientific, validate_protocol
from omega_v2.testbed.experiments.channel_comparison import root_for


def _frozen_tiny_protocol():
    root = root_for((1, 1))
    return {
        "id": "channel-experiment-test",
        "version": "test-only",
        "status": "frozen_before_scientific_ranking",
        "world": {"inventory": [1, 1], "params": asdict(legacy.DEFAULT), "damage": None},
        "controllers": {
            "responses": {"service": [1.0, 0.0], "mixed": [0.5, 0.5]},
            "scope": "test-only two-table subset",
            "selected_tables": [["service", "service"], ["mixed", "mixed"]],
        },
        "measurement": {"cadence": 0.25, "max_dense_bytes": 64 * 1024 * 1024},
        "queries": {
            "roots": {"distributed_seed": root},
            "reference_energy": 4,
            "horizons": [1],
            "rank_root": "distributed_seed",
        },
        "analysis": {
            "rank_tolerance": 1e-9,
            "registered_outcomes": [{"id": "test_marker", "metric": "winner_rate", "operator": "record"}],
        },
        "limits": {"wall_seconds": 120, "memory_mib": 1024, "output_mib": 256},
    }


def test_protocol_refuses_draft():
    protocol = _frozen_tiny_protocol()
    protocol["status"] = "draft"
    with pytest.raises(ValueError, match="frozen"):
        validate_protocol(protocol)


def test_tiny_frozen_subset_preserves_limiting_queries_and_records():
    protocol = _frozen_tiny_protocol()
    result = scientific(protocol)

    assert result["status"] == "complete"
    assert result["scope"] == "test-only two-table subset"
    assert len(result["policies"]) == 2
    assert len(result["rate_ties"]) >= 1
    for row in result["policies"]:
        assert set(row["limiting"]) == {"distributed_seed", "matched_reference"}
        assert all("rate" in record and "offset" in record and "class_weights" in record
                   for record in row["limiting"].values())
        assert "1" in row["profiles_bits"]
        assert "1" in row["surveys"]
    # The profile uses integer protocol horizon keys. The same canonical key
    # must address first-entry results in findings (no int/float key mismatch).
    assert result["findings"] is not None
    assert result['registered_outcomes'][0]['status']=='open_outcome'
