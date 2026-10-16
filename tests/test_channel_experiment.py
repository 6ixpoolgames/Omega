"""Tiny integration checks for the channel experiment contract, not research evidence."""
from dataclasses import asdict

import pytest

from omega_v2.testbed import growing_population as legacy
from omega_v2.testbed.experiments.channel_comparison import scientific, validate_protocol
from omega_v2.testbed.experiments.channel_comparison import root_for


def _frozen_tiny_protocol(ed_energy=-1.0):
    root = root_for((1, 1))
    return {
        "id": "channel-experiment-test",
        "version": "test-only",
        "status": "frozen_before_scientific_ranking",
        "world": {"inventory": [1, 1], "params": asdict(legacy.DEFAULT),
                  "damage": {"enabled": True, "mode": "reversible", "rate": 0.04,
                             "energy": ed_energy, "exposure": [1.0, 1.0, 1.0],
                             "boundary": "finite_barrier"}},
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
            "registered_outcomes": [
                {"id": "test_marker", "metric": "winner_rate", "operator": "record"},
                {"id": "export_baseline_prediction", "metric": "usable_fraction_vs_export",
                 "operator": "ge", "threshold": 0.0},
            ],
        },
        "limits": {"wall_seconds": 120, "memory_mib": 1024, "output_mib": 256},
    }


def test_protocol_refuses_draft():
    protocol = _frozen_tiny_protocol()
    protocol["status"] = "draft"
    with pytest.raises(ValueError, match="frozen"):
        validate_protocol(protocol)


def test_embodied_aliases_reuse_exact_kernels_and_preserve_every_policy():
    protocol=_frozen_tiny_protocol()
    protocol['world']['actuation']={'mode':'embodied','basal_rate':.003}
    protocol['world']['shocks']={'enabled':True,'mode':'correlated','hazard':.02,'p':.5}
    protocol['controllers']['selected_tables']=[['service','service'],['mixed','service'],
                                               ['service','mixed'],['mixed','mixed']]
    result=scientific(protocol)
    assert len(result['policies'])==4
    assert result['unique_kernels']==2
    first,alias,other,other_alias=result['policies']
    assert first['kernel_hash']==alias['kernel_hash']
    assert alias['alias_of']==first['table']
    assert first['profiles_bits']==alias['profiles_bits']
    assert other_alias['alias_of']==other['table']
    for row in result['policies']:
        probe=row['shock_readout']['common_probe_stationary']
        assert 0<=probe['function_loss_given_pre_active']<=1
        assert row['surveys']['1']['energy_residual']<1e-8


@pytest.mark.parametrize("ed_energy", [0.0, -1.0, -2.0, -4.0])
def test_tiny_frozen_subset_preserves_limiting_queries_and_records(ed_energy):
    protocol = _frozen_tiny_protocol(ed_energy)
    result = scientific(protocol)

    assert result["status"] == "complete"
    assert result["scope"] == "test-only two-table subset"
    assert len(result["policies"]) == 2
    assert len(result["rate_ties"]) >= 1
    for row in result["policies"]:
        assert set(row["limiting"]) == {"distributed_seed", "matched_reference"}
        assert all("rate" in record and "offset" in record and "class_weights" in record
                   for record in row["limiting"].values())
        assert all(0.0 <= record["stationary_observables"]["usable"] / 2 <= 1.0
                   for record in row["limiting"].values())
        assert "1" in row["profiles_bits"]
        assert "1" in row["surveys"]
        trap = row["recovery_from_trap"]
        assert trap["status"] == "supported"
        assert trap["eD_energy_parameter"] == ed_energy
        assert trap["initial_resource_energy"] == 2 * ed_energy
        assert trap["matched_to_reference_energy"] is False
        assert trap["interpretation"].startswith("diagnostic only")
        assert (trap["profile"]["1"]["hit_probability"] >=
                trap["profile"]["1"]["endpoint_target_probability"])
    # The profile uses integer protocol horizon keys. The same canonical key
    # must address first-entry results in findings (no int/float key mismatch).
    assert result["findings"] is not None
    assert result['registered_outcomes'][0]['status']=='open_outcome'
    assert result['metrics']['usable_fraction_vs_service'] is not None
    assert result['metrics']['usable_fraction_vs_export'] is None
    assert result['registered_outcomes'][1]['status']=='unsupported'
