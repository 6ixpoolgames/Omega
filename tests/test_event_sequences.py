import math
from omega_v2.testbed.contracts import Event,RuleModule,WorldSpec
from omega_v2.testbed.analysis.event_sequences import ordered_event_probability


def test_ordered_event_automaton_matches_two_jump_erlang_cdf():
    def events(s):
        yield Event('flip','flip',((1-s[0][0],),),.7,(0,))
    world=WorldSpec('flip','1',(((0,),),((1,),)),lambda s:None,lambda s:0,{},
                    (RuleModule('flip','1',events),))
    t=1.3;result=ordered_event_probability(world,((0,),),[lambda e:True]*2,t)
    expected=1-math.exp(-.7*t)*(1+.7*t)
    assert abs(result['probability']-expected)<1e-12
    assert result['physical_history_entropy_augmented'] is False
