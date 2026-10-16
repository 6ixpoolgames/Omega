from dataclasses import asdict
import numpy as np
import pytest
from scipy.sparse import csr_matrix
from omega_v2.testbed import growing_population as legacy
from omega_v2.testbed.controllers.reserve import candidate_family
from omega_v2.testbed.experiments.reserve_batch import scientific,validate,retained_first_entry,tied_ids


def tiny_protocol():
    return {'id':'fixture','law_id':'fixture','status':'frozen_before_scientific_ranking',
        'world':{'inventory':[1,1],'params':asdict(legacy.DEFAULT),
                 'damage':{'mode':'reversible','rate':.04,'energy':-1,'exposure':[0,1,0]},
                 'actuation':{'mode':'embodied','basal_rate':.003},
                 'shocks':{'enabled':False,'mode':'independent','hazard':0,'p':1}},
        'controllers':{'candidates':[p.manifest() for p in candidate_family(1)]},
        'measurement':{'cadence':.25,'max_dense_bytes':64*1024**2},
        'queries':{'roots':{'distributed_seed':[[0,1,0,1,0],[0,0,0,0,0]]},
                  'rank_root':'distributed_seed','reference_energy':4,'horizons':[1,4],
                  'common_deadline':64,'recovery_root':[[1,0,0,1,0],[0,0,0,0,0]]},
        'analysis':{'primary':'complete conditional history bits at each horizon',
                    'rank_tolerance':1e-8,'residual_tolerance':1e-8,'probe_p':.5}}


def test_retained_first_return_matches_two_state_analytic_value():
    q=csr_matrix([[-2.,2.],[1.,-1.]])
    value=retained_first_entry(q,np.array([1.,0.]),np.array([False,True]),1.)
    assert value==pytest.approx(2*(np.exp(-1)-np.exp(-2)))


def test_draft_protocol_cannot_launch_scientific_solver():
    p=tiny_protocol();p['status']='draft'
    with pytest.raises(ValueError,match='Frozen'):validate(p)


def test_aliases_and_numerical_ties_are_not_counted_as_new_policies():
    rows=[{'canonical_id':'a','score':1.},{'canonical_id':'a','score':1.},
          {'canonical_id':'b','score':1.+1e-10}]
    assert tied_ids(rows,lambda x:x['score'],1e-8)==['a','b']


def test_small_batch_retains_horizon_winners_and_full_native_process():
    out=scientific(tiny_protocol())
    assert out['states']==256 and out['unique_models']==6
    assert set(out['winners'])=={'1','4'}
    assert out['reference_law']['support_size']>1
    assert out['max_residual']<1e-8
    for row in out['policies']:
        assert row['bits']['4']['distributed_seed']>=row['bits']['1']['distributed_seed']
        assert row['readouts']['recovery_retained64']<=row['readouts']['recovery_firsthit64']+1e-9
        assert row['nonconstant_reachable'] is False
    assert set(out['fixed_comparators']['best_nonrandom'])=={'1','4'}
