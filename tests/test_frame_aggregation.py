from math import isclose

import pytest

from omega_v2.finite.frame_aggregation import (
    SOURCES,
    apply,
    content_frontiers,
    enumerate_routes,
    envelope,
    information,
    partition,
)


def test_negative_syn_is_retained():
    law = [0.5, 0, 0, 0, 0, 0, 0, 0.5]
    summary = information(SOURCES, law)
    assert summary == {"bits": 1.0, "syn": -2.0, "volume": 1.0}
    with pytest.raises(ValueError):
        information(SOURCES, [0.1] * 8)


def test_joint_budget_and_route_replay():
    gates, routes = enumerate_routes(SOURCES)
    profile = envelope(routes, [1 / 8] * 8, nrecords=3, depth=2)
    indexed = {tuple(p["budget"]): p["bits"] for p in profile}
    assert indexed[3, 1, 2] == 1
    assert indexed[3, 2, 0] == 2
    for route in routes:
        outputs = (0, 0)
        for i in route.program:
            outputs = apply(SOURCES, outputs, gates[i])
        assert outputs == route.outputs
    ids = {i for entry in content_frontiers(routes) for i in entry["routes"]}
    assert ids


def test_copy_content_and_partition_relabel():
    fair = [1 / 8] * 8
    s = SOURCES[0]
    assert information((s,), fair)["bits"] == information((s, s, s), fair)["bits"]
    assert partition((s,)) == partition((s ^ 255,))
    assert isclose(information((), fair)["volume"], 1 / 8)


def test_record_permutation_preserves_profile():
    fair = [1 / 8] * 8
    profiles = []
    for bank in (SOURCES, tuple(reversed(SOURCES))):
        _, routes = enumerate_routes(bank)
        profiles.append([p["bits"] for p in envelope(routes, fair, nrecords=3, depth=2)])
    assert profiles[0] == profiles[1]
