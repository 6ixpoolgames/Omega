from __future__ import annotations

from omega.baseline_witnesses.search import run_search


def test_search_finds_mutual_information_declared_recovery_separation() -> None:
    result = run_search(
        match_baseline="mutual_information",
        separate="declared_recovery",
        states=8,
        trials=20,
        seed=7,
    )

    assert result["status"] == "PASS"
    assert result["match_baseline"] == "mutual_information"
    assert result["declared_baseline"] == result["candidate_baseline"]
    assert result["declared_recovery"]["exact_declared_recovery"] is True
    assert result["candidate_recovery"]["exact_declared_recovery"] is False


def test_search_finds_reachability_declared_recovery_separation() -> None:
    result = run_search(
        match_baseline="reachability",
        separate="declared_recovery",
        states=8,
        trials=20,
        seed=11,
    )

    assert result["status"] == "PASS"
    assert result["match_baseline"] == "reachability"
    assert result["declared_baseline"] == result["candidate_baseline"]
    assert result["declared_recovery"]["exact_declared_recovery"] is True
    assert result["candidate_recovery"]["exact_declared_recovery"] is False

