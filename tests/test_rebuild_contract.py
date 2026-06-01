from __future__ import annotations

from omega.future_field_atlas.rebuild import rebuild_contract_payload


def test_rebuild_contract_marks_clean_committed_source_exact() -> None:
    payload = rebuild_contract_payload(
        runner_module="omega.future_field_atlas.fake_runner",
        config={"base_seed": 1},
        raw_data_retention="retained_local_raw_topology",
        argv=["python", "-m", "omega.future_field_atlas.fake_runner"],
        git={"source_commit": "abc123", "source_branch": "master", "source_dirty": False},
        dependency_versions={"numpy": "1.0"},
    )

    assert payload["rebuild_status"] == "exact_rebuild_supported"
    assert payload["git"]["source_commit"] == "abc123"  # type: ignore[index]
    assert payload["artifact_schema_version"]


def test_rebuild_contract_marks_dirty_source_logical_only() -> None:
    payload = rebuild_contract_payload(
        runner_module="omega.future_field_atlas.fake_runner",
        config={"base_seed": 1},
        raw_data_retention="discarded",
        git={"source_commit": "abc123", "source_branch": "master", "source_dirty": True},
        dependency_versions={},
    )

    assert payload["rebuild_status"] == "logical_rebuild_only"
    assert payload["raw_data_retention"] == "discarded"
