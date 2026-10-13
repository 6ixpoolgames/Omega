from dataclasses import replace
import numpy as np
import pytest
from omega_v2.testbed.contracts import Event, RuleModule, WorldSpec, ExperimentSpec
from omega_v2.testbed.compiler import compile_world
from omega_v2.testbed.analysis.registry import ReadoutRegistry, SurveySpec, interpret_channel


def fixture():
    def events(s):
        yield Event("flip", "bath", ((1-s[0][0],),), 1., (0,))
    return WorldSpec("binary", "1", (((0,),), ((1,),)), lambda s: None,
                     lambda s: s[0][0], {"active": lambda s: s[0][0]},
                     (RuleModule("flip", "1", events),))


def test_compile_central_energy_and_no_channel_label_entropy():
    world = fixture(); m = compile_world(world)
    split = replace(world, modules=(RuleModule("a", "1", lambda s: [
        Event("a", "bath", ((1-s[0][0],),), .25, (0,))]),
        RuleModule("b", "1", lambda s: [Event("b", "bath", ((1-s[0][0],),), .75, (0,))])))
    q = compile_world(split)["Q"]
    assert np.allclose(q.toarray(), m["Q"].toarray())
    assert np.allclose(m["Q"]@m["energy"], m["flows"]["drive_work"]-m["flows"]["bath_heat"])
    assert np.allclose(compile_world(replace(split, modules=split.modules[::-1]))["Q"].toarray(), q.toarray())


def test_bad_dependencies_targets_and_support_fail():
    w = fixture()
    with pytest.raises(ValueError, match="Duplicate"):
        compile_world(replace(w, modules=w.modules*2))
    with pytest.raises(ValueError, match="dependencies"):
        compile_world(replace(w, modules=(replace(w.modules[0], requires=("unknown",)),)))
    with pytest.raises(ValueError, match="support"):
        compile_world(replace(w, modules=(RuleModule("bad", "1", lambda s: [
            Event("bad", "bad", ((1-s[0][0],),), 1, ())]),)))


def test_readout_requirements_and_margin_not_ethical_failure():
    registry = ReadoutRegistry()
    registry.register(SurveySpec("unavailable", "1", "bits", lambda m,c: 9, ("quantum",)))
    assert registry.evaluate(compile_world(fixture()), {})["unavailable"]["status"] == "unsupported"
    records=interpret_channel({"winner_active":1,"benchmark_active":2,"winner_closure":.3,"benchmark_closure":.1})
    assert {x["id"] for x in records} == {"margin_tradeoff", "closure_tension"}
    assert all(x["status"]=="open_outcome" for x in records)


def test_draft_science_rejected():
    with pytest.raises(ValueError, match="frozen"):
        ExperimentSpec("x","1","draft",{},{},{},{},{},{}).require_scientific_freeze()


def test_state_order_transport_preserves_the_generator():
    world=fixture();first=compile_world(world)
    second=compile_world(replace(world,states=world.states[::-1]))
    assert np.allclose(second['Q'].toarray(),first['Q'].toarray()[::-1,::-1])


def test_registered_outcomes_score_negative_results():
    from omega_v2.testbed.analysis.registry import score_outcomes
    result=score_outcomes({'gap':-2},[{'id':'prediction','metric':'gap','operator':'ge','threshold':0},
                                   {'id':'report','metric':'gap','operator':'record'}])
    assert result[0]['status']=='fail' and result[1]['value']==-2
