from dataclasses import asdict

import pytest

from omega_v2.testbed.controllers.reserve import ReservePolicy
from omega_v2.testbed.experiments.structural_harm import physical_roots, scientific
from omega_v2.testbed.growing_population import DEFAULT


def case():
    return {'status': 'frozen_before_scientific_ranking', 'id': 'test', 'mode': 'fast',
            'hazard': .02, 'inventory': [1, 1], 'params': asdict(DEFAULT),
            'slow_factor': .1, 'hardware_energy': 1., 'present_root': [[0,1,0,1,0], [0,1,0,1,0], [1,1]],
            'candidates': [ReservePolicy('service').manifest()], 'rank_tolerance': 1e-8,
            'primary': 'complete conditional history bits at each horizon', 'cadence': .25,
            'horizons': [1], 'deadline': 64, 'block_rows': 64, 'max_kernel_bytes': 256*1024**2}


def test_matched_fault_map_and_declared_energy_difference():
    cfg = case()
    fast = physical_roots(cfg)
    cfg['mode'] = 'hardware_loss'
    lost = physical_roots(cfg)
    assert fast['present'] == lost['present']
    assert fast['post_fault'][:2] == lost['post_fault'][:2]
    assert fast['post_fault'][2] == (1,1)
    assert lost['post_fault'][2] == (0,1)


def test_scientific_schema_no_survival_conditioning():
    result = scientific(case())
    assert result['winners']['1'] == ['service']
    row = result['policies'][0]
    assert row['bits']['1']['present'] > 0
    assert row['readouts']['post_fault_retained64'] <= row['readouts']['post_fault_firsthit64']+1e-9
    assert row['readouts']['closure64'] == 0
    assert row['readouts']['hardware_loss_hit64'] == 0
    assert row['readouts']['stationary_hardware'] == pytest.approx(2)
    assert result['root_energies']['present']-result['root_energies']['post_fault'] == 1
