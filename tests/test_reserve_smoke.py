from omega_v2.testbed.experiments.reserve_smoke import engineering


def test_fixed_controller_smoke_exercises_queries_without_scientific_scores():
    result = engineering({
        'inventory': [1,1],
        'fixed_controller': {'id':'fixed-smoke','threshold':2,'surplus':'mix50',
                             'service_if_worn':True},
        'shocks': {'enabled':True,'mode':'correlated','hazard':.02,'p':1.},
        'cadence':.25,'horizons':[1.], 'common_deadline':1.,
        'max_dense_bytes':64*1024**2,
    })
    assert result['status']=='engineering_smoke_pass'
    assert result['candidate_count']==22
    assert result['unique_kernel_ledger_models']==6
    assert result['scientific_scores_withheld'] is True
    assert 'winner' not in result and 'rate' not in result
    assert result['history_checks']=={'1':'finite and nondecreasing'}
    assert max(result['numerical_residuals'].values()) < 1e-8
