import numpy as np
from scipy.linalg import expm
from omega_v2.testbed.compiler import compile_world, sample_events
from omega_v2.testbed.modules.growth import build_world
from omega_v2.testbed.modules.material_sink import MaterialSink


def test_native_event_sampler_uses_the_compiled_world_law():
    world=build_world((1,1), ((1,0),(.75,.25))*2,
                      damage=MaterialSink(mode='absorbing',rate=.23))
    model=compile_world(world);root=((0,1,0,1,0),(0,0,0,0,0))
    expected=expm(model['Q'].toarray()*.7)[model['index'][root]]
    counts=np.zeros(len(expected));rng=np.random.default_rng(261013)
    samples=2500
    for _ in range(samples):
        end,_=sample_events(world,root,.7,rng)
        counts[model['index'][end]]+=1
    standard=np.sqrt(samples*expected*(1-expected))
    assert np.all(abs(counts-samples*expected)<=6*standard+2)
