"""Cross-platform registry-first stochastic-channel smoke runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from omega.future_field_atlas.util import read_csv
from omega.stochastic_distinction_channel.registry_first_adversarial_audit import (
    audit_registry_first_output,
)
from omega.stochastic_distinction_channel.registry_first_x3_probe import (
    run_registry_first_x3_probe,
)
from omega.validation._common import assert_equal, run_pytest, timestamped_run_root


REGISTRY_TESTS = ["tests/test_stochastic_registry_first_x3_probe.py"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the registry-first reproducibility smoke.")
    parser.add_argument("--out-root", type=Path, default=Path(".tmp/reproducibility_smoke"))
    parser.add_argument("--skip-pytest", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_registry_first_smoke(out_root=args.out_root, skip_pytest=args.skip_pytest)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def run_registry_first_smoke(
    *,
    out_root: Path = Path(".tmp/reproducibility_smoke"),
    skip_pytest: bool = False,
) -> dict[str, Any]:
    run_root = timestamped_run_root(out_root)
    x3_out = run_root / "registry_first_x3"
    audit_out = run_root / "registry_first_x3_audit"

    probe = run_registry_first_x3_probe(out_dir=x3_out)
    audit = audit_registry_first_output(source_dir=x3_out, out_dir=audit_out)
    carrier = read_csv(x3_out / "carrier_manifest.csv")

    assert_equal("carrier_id", probe["carrier_id"], "X3")
    assert_equal("state_count", carrier[0]["state_count"], "8")
    assert_equal("channel_count", probe["channel_count"], "15")
    assert_equal("registered_rows", probe["registered_rows"], "120")
    assert_equal("gap_rows", probe["gap_rows"], "120")
    assert_equal("cascade_evidence_status", probe["cascade_evidence_status"], "path_rows_retained")
    assert_equal(
        "probe_overall_status",
        probe["overall_status"],
        "registry_first_theorem_transfer_ready",
    )
    assert_equal("audit_overall_status", audit["overall_status"], "PASS")
    assert_equal("audit_rows", audit["audit_rows"], "105")
    assert_equal("audit_failure_count", audit["failure_count"], "0")

    if not skip_pytest:
        run_pytest(REGISTRY_TESTS, run_root=run_root)

    return {
        "status": "PASS",
        "run_root": str(run_root),
        "x3_output": str(x3_out),
        "audit_output": str(audit_out),
        "carrier_id": probe["carrier_id"],
        "state_count": int(carrier[0]["state_count"]),
        "channel_count": int(probe["channel_count"]),
        "registered_rows": int(probe["registered_rows"]),
        "provenance_gap_rows": int(probe["gap_rows"]),
        "audit_rows": int(audit["audit_rows"]),
        "audit_failure_count": int(audit["failure_count"]),
        "focused_pytest": "skipped" if skip_pytest else "passed",
    }


if __name__ == "__main__":
    main()

