"""Independent race formulas, causal witnesses, and the frozen profile collision."""

import json
from dataclasses import replace
from fractions import Fraction
from math import exp, factorial

import numpy as np
import pytest
from scipy.stats import poisson

from omega_v2.experiments.timing_volume_counterexample_v0 import (
    FUEL,
    HORIZONS,
    calibration_nets,
    preparations,
    relay_net,
)
from omega_v2.finite.timed_execution import (
    Net,
    Transition,
    closed_region,
    condition_on,
    endpoint_from_matrix,
    endpoint_from_paths,
    enumerate_paths,
    hitting_probability,
    jump_law,
    marginal,
    reachable_states,
    state,
    timing_profile,
)


@pytest.fixture(scope="module")
def apparatus():
    net, initial = relay_net(), preparations()
    paths = {name: enumerate_paths(net, law, FUEL) for name, law in initial.items()}
    return net, initial, paths


@pytest.mark.parametrize("horizon", (0.5, 1.0, 2.0))
def test_known_races_include_no_event_partial_and_final_survival(horizon):
    expected = {
        "independent": [exp(-2*horizon), 2*exp(-horizon)*(1-exp(-horizon)),
                        (1-exp(-horizon))**2],
        "exclusive": [exp(-2*horizon), 1-exp(-2*horizon)],
        "enabling": [exp(-horizon), horizon*exp(-horizon),
                     1-(1+horizon)*exp(-horizon)],
    }
    extents = {"independent": [1, 2*horizon, horizon**2],
               "exclusive": [1, 2*horizon],
               "enabling": [1, horizon, horizon**2/2]}
    for name, (net, initial, bound) in calibration_nets().items():
        paths = enumerate_paths(net, initial, bound)
        profile = timing_profile(net, paths, horizon)
        assert profile["count_law"] == pytest.approx(expected[name], abs=2e-13)
        assert profile["V"] == pytest.approx(extents[name], abs=2e-13)
        assert profile["mass"] == pytest.approx(1, abs=2e-13)


def test_independent_interleavings_form_one_cube_not_six_cubes():
    net = Net(tuple(Transition(k, state(**{k: 0}), state(**{k: 1})) for k in "abc"))
    initial = {state(a=0, b=0, c=0): Fraction(1)}
    profile = timing_profile(net, enumerate_paths(net, initial, 3), 2)
    complete = [c for c in profile["classes"] if len(c["word"]) == 3]
    assert len(complete) == 1
    assert complete[0]["presentations"] == 6
    assert complete[0]["timing_volume"] == 8
    assert complete[0]["probability"] == pytest.approx((1-exp(-2))**3)


def test_subdivision_is_integration_not_a_new_weighted_class():
    net, initial, bound = calibration_nets()["independent"]
    profile = timing_profile(net, enumerate_paths(net, initial, bound), 1)
    whole = next(c for c in profile["classes"] if len(c["word"]) == 2)
    p, v = whole["probability"], whole["timing_volume"]
    assert (p/2 + p/2) * (v/2 + v/2) == pytest.approx(profile["L"][2])
    # Negative control: applying probability-times-volume to each patch is wrong.
    assert 2 * (p/2) * (v/2) == pytest.approx(profile["L"][2] / 2)


def test_positive_duration_update_is_not_erased_as_a_dummy():
    direct = Net((Transition("finish", state(stage=0), state(stage=2)),))
    delayed = Net((Transition("advance", state(stage=0), state(stage=1)),
                   Transition("finish", state(stage=1), state(stage=2))))
    initial = {state(stage=0): Fraction(1)}
    assert endpoint_from_matrix(direct, initial, 1)[state(stage=2)] == pytest.approx(1-exp(-1))
    assert endpoint_from_matrix(delayed, initial, 1)[state(stage=2)] == pytest.approx(1-2*exp(-1))
    assert max(p.cost for p in enumerate_paths(delayed, initial, 2)) == (2, 2)


@pytest.mark.parametrize("name", ("intact", "damaged", "erased", "cycling"))
def test_complete_path_law_agrees_with_independent_ctmc_and_cut_composition(apparatus, name):
    net, initial, paths = apparatus
    for horizon in (0.5, 2.0, 8.0):
        direct = endpoint_from_matrix(net, initial[name], horizon)
        from_paths = endpoint_from_paths(net, paths[name], horizon)
        cut = endpoint_from_matrix(net, initial[name], horizon, cut=horizon/3)
        assert sum(from_paths.values()) == pytest.approx(1, abs=3e-13)
        for s, p in direct.items():
            assert from_paths.get(s, 0) == pytest.approx(p, abs=3e-13)
            assert cut[s] == pytest.approx(p, abs=3e-13)


def test_all_horizon_collision_has_an_independent_poisson_certificate(apparatus):
    net, _initial, paths = apparatus
    for horizon in HORIZONS:
        counts = list(poisson.pmf(np.arange(FUEL), horizon)) + [poisson.sf(FUEL-1, horizon)]
        expected = [p * horizon**n / factorial(n) for n, p in enumerate(counts)]
        for histories in paths.values():
            observed = timing_profile(net, histories, horizon)
            assert observed["count_law"] == pytest.approx(counts, abs=3e-13)
            assert observed["L"] == pytest.approx(expected, rel=2e-12, abs=3e-13)
    # The underlying unweighted history supports are not being made identical.
    assert timing_profile(net, paths["erased"], 1)["V"] != timing_profile(net, paths["intact"], 1)["V"]


def test_real_fuel_and_costs_bound_execution_without_pruning(apparatus):
    net, initial, paths = apparatus
    for name, histories in paths.items():
        for path in histories:
            n, final = len(path.events), dict(path.states[-1])
            assert final["fuel"] == FUEL-n and final["spent"] == n
            assert path.cost == (n, n)
            assert net.exit_rate(path.states[-1]) == (1 if n < FUEL else 0)
        with pytest.raises(ValueError, match="discard physical continuations"):
            enumerate_paths(net, initial[name], FUEL-1)
    # Shared registers replenish and phases recur; this is not a once-only net.
    after_six = jump_law(net, initial["intact"], 6)
    assert all(dict(s)["phase"] == 1 and dict(s)["record"] == dict(s)["source"] for s in after_six)


def test_record_erasure_changes_access_not_the_analysts_past(apparatus):
    net, initial, paths = apparatus
    for name in ("intact", "erased"):
        acquired = jump_law(net, initial[name], 1)
        assert marginal(acquired, ("source", "record")) == {(0, 0): Fraction(1, 2), (1, 1): Fraction(1, 2)}
    erased = jump_law(net, initial["erased"], 2)
    frames = condition_on(erased, ("record",))
    assert set(frames) == {(-1,)}
    assert marginal(frames[(-1,)][1], ("source",)) == {(0,): Fraction(1, 2), (1,): Fraction(1, 2)}
    responded = jump_law(net, initial["erased"], 3)
    assert marginal(responded, ("source", "relay")) == {
        (source, output): Fraction(1, 4) for source in (0, 1) for output in (0, 1)
    }
    assert all("source" not in t.footprint for t in net.transitions if "blank_reader" in t.name)
    assert all(dict(p.states[1])["record"] == dict(p.states[0])["source"]
               for p in paths["erased"] if len(p.events) >= 2)


def test_frame_conditioning_recombines_without_reinventing_weights(apparatus):
    net, initial, _paths = apparatus
    for name in ("intact", "erased"):
        law = jump_law(net, initial[name], 2)
        frames = condition_on(law, ("record",))
        reconstructed = {}
        for mass, conditional in frames.values():
            for s, p in conditional.items():
                reconstructed[s] = reconstructed.get(s, Fraction()) + mass*p
        assert reconstructed == law
        broad = timing_profile(net, enumerate_paths(net, law, FUEL-2), 2)["L"]
        mixed = np.zeros(FUEL-1)
        for mass, conditional in frames.values():
            mixed += float(mass) * np.array(timing_profile(
                net, enumerate_paths(net, conditional, FUEL-2), 2)["L"])
        assert mixed == pytest.approx(broad, abs=3e-13)


def test_damage_propagates_despite_permanent_repair_and_tied_volume(apparatus):
    net, initial, paths = apparatus
    blank_law = {(0, -1): Fraction(1, 2), (1, -1): Fraction(1, 2)}
    source_law = {(0, 0): Fraction(1, 2), (1, 1): Fraction(1, 2)}
    assert marginal(jump_law(net, initial["damaged"], 3), ("source", "relay")) == blank_law
    repaired = jump_law(net, initial["damaged"], 4)
    assert all(dict(s)["wire"] == 1 for s in repaired)
    assert closed_region(net, reachable_states(net, initial["damaged"]), lambda s: dict(s)["wire"] == 1)
    assert marginal(jump_law(net, initial["damaged"], 5), ("source", "downstream")) == blank_law
    assert marginal(jump_law(net, initial["damaged"], 10), ("source", "downstream")) == source_law
    for name, first_delivery in (("intact", 5), ("damaged", 10)):
        observed = hitting_probability(net, paths[name], 4,
                                       lambda s: dict(s)["downstream"] != -1)
        assert observed == pytest.approx(poisson.sf(first_delivery-1, 4), abs=3e-13)


def test_assembly_changes_a_downstream_channel_at_matched_activity(apparatus):
    net, initial, _paths = apparatus
    for n in (5, 10):
        built, cycled = (jump_law(net, initial[name], n) for name in ("intact", "cycling"))
        assert marginal(built, ("link",)) == {(1,): Fraction(1)}
        assert marginal(cycled, ("link",)) == {(0,): Fraction(1)}
        assert marginal(built, ("source", "downstream")) == {(0, 0): Fraction(1, 2), (1, 1): Fraction(1, 2)}
        assert marginal(cycled, ("source", "downstream")) == {(0, -1): Fraction(1, 2), (1, -1): Fraction(1, 2)}
        assert marginal(built, ("spent",)) == marginal(cycled, ("spent",)) == {(n,): Fraction(1)}


def test_arbitrary_register_event_and_input_order_redescription():
    net, initial, bound = calibration_nets()["independent"]
    renamed = {"a": "right", "b": "left"}

    def rename(s):
        return tuple(sorted((renamed[k], v) for k, v in s))

    changed = Net(tuple(replace(t, name=f"renamed-{2-i}", guard=rename(t.guard), writes=rename(t.writes))
                        for i, t in enumerate(reversed(net.transitions))))
    changed_initial = {rename(s): p for s, p in initial.items()}
    a = timing_profile(net, enumerate_paths(net, initial, bound), 2)
    b = timing_profile(changed, enumerate_paths(changed, changed_initial, bound), 2)
    assert a["V"] == pytest.approx(b["V"])
    assert a["L"] == pytest.approx(b["L"])


def test_report_and_full_evidence_export_are_reproducible(tmp_path):
    from omega_v2.validation import timing_volume_counterexample_v0 as runner

    output, report = tmp_path / "results", tmp_path / "report.md"
    assert runner.main(["--output", str(output), "--report", str(report)]) == 0
    evidence = json.loads((output / "evidence.json").read_text(encoding="utf-8"))
    assert evidence["candidate_status"] == "rejected_as_complete_comparison"
    assert evidence["machinery_passes"] is True
    assert len(evidence["arrangements"]) == 4
    for arrangement in evidence["arrangements"].values():
        assert arrangement["paths"] and arrangement["states"]
        assert all(row["mass"] == pytest.approx(1) for row in arrangement["horizons"])
    assert "candidate rejected" in report.read_text(encoding="utf-8")


def test_frozen_contract_digest_ignores_checkout_line_endings(tmp_path):
    from omega_v2.validation.timing_volume_counterexample_v0 import protocol_digest

    lf, crlf = tmp_path / "lf.md", tmp_path / "crlf.md"
    lf.write_bytes(b"First line\nSecond line\n")
    crlf.write_bytes(b"First line\r\nSecond line\r\n")
    assert protocol_digest(lf) == protocol_digest(crlf)
