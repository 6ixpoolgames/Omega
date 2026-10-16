"""Run the frozen quantum frame-profile probe and export reproducible evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from omega_v2.experiments.quantum_frame_profile_v0 import (
    PREPARATIONS,
    PROTOCOL,
    PROTOCOL_SHA256,
    calibrations,
    causal_trace_error,
    network,
    source_state,
)
from omega_v2.finite.quantum_profile import (
    contract_inputs,
    dephase,
    mutual_information,
    profile,
    record_diagnostics,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = "docs/research_notes/validation_results/quantum_frame_profile_v0/20261001"
SOURCES = (
    PROTOCOL,
    "omega_v2/finite/quantum_profile.py",
    "omega_v2/experiments/quantum_frame_profile_v0.py",
    "omega_v2/validation/quantum_frame_profile_v0.py",
    "tests/test_quantum_frame_profile.py",
)


def protocol_digest():
    return hashlib.sha256((ROOT / PROTOCOL).read_text(encoding="utf-8").encode()).hexdigest()


def matrix_rows(state):
    return {"labels": state.labels, "entries_row_col_real_imag": [
        [r, c, float(v.real), float(v.imag)] for (r, c), v in sorted(state.entries.items()) if v != 0]}


def compare_profiles(a, b, tolerance=1e-10):
    if a["labels"] != b["labels"]:
        raise ValueError("comparison must retain the same physical labels")
    differences = [x["mutual_information_bits"] - y["mutual_information_bits"]
                   for x, y in zip(a["labelled_fragments"], b["labelled_fragments"], strict=True)]
    positive = sum(x > tolerance for x in differences)
    negative = sum(x < -tolerance for x in differences)
    return {"positive_fragments": positive, "negative_fragments": negative,
            "tied_fragments": len(differences)-positive-negative,
            "max_absolute_difference_bits": max(abs(x) for x in differences),
            "relation": ("crossing" if positive and negative else "equal" if not positive
                         and not negative else "first_greater" if positive else "second_greater")}


def run():
    if protocol_digest() != PROTOCOL_SHA256:
        raise RuntimeError("protocol changed; write a new version instead of changing the freeze")
    controls = calibrations()
    cases = {}
    errors = {"trace": 0.0, "causal_trace": 0.0, "source_contraction": 0.0}
    plus = np.ones((2, 2), dtype=complex)/2
    y_plus = np.array([[1, -1j], [1j, 1]], dtype=complex)/2
    for name in PREPARATIONS:
        rounds_data, previous = [], None
        for horizon in (1, 2):
            choi, full_choi, metadata = network(name, horizon, choi=True)
            errors["trace"] = max(errors["trace"], abs(choi.trace()-1), abs(full_choi.trace()-1))
            errors["causal_trace"] = max(errors["causal_trace"], causal_trace_error(choi, previous))
            choi_profile = profile(choi)
            actual_rows = []
            for label, prep in (("p0_0.8", source_state(.8)), ("p0_0.5", source_state(.5)),
                                ("plus", plus), ("y_plus", y_plus)):
                actual, full, actual_metadata = network(name, horizon, preparation=prep)
                contracted = contract_inputs(choi, {f"I{j}": prep for j in range(1, horizon+1)})
                error = actual.distance_max(contracted)
                errors["source_contraction"] = max(errors["source_contraction"], error)
                errors["trace"] = max(errors["trace"], abs(full.trace()-1), abs(actual.trace()-1))
                # Validate coherent states too; save complete interface matrices for replay.
                actual.entropy()
                row = {"preparation": label, "output_state": matrix_rows(actual),
                       "choi_contraction_error": error}
                if label.startswith("p0_"):
                    law = actual.law()
                    row.update({
                        "profile": profile(actual), "records": record_diagnostics(actual, horizon),
                        "joint_z_output_law": [{"bits": format(i, f"0{len(actual.labels)}b"),
                                                 "probability": mass} for i, mass in sorted(law.items())],
                        "bath_source_information_bits": [mutual_information(
                            dephase(full), [f"S{j}"], [f"E{j}"]) for j in range(1, horizon+1)],
                        "bill": actual_metadata["bill"],
                    })
                actual_rows.append(row)
            rounds_data.append({"rounds": horizon, "horizon": 5*horizon, **metadata,
                                "choi_state": matrix_rows(choi), "choi_profile": choi_profile,
                                "actual_preparations": actual_rows})
            previous = choi
        cases[name] = rounds_data
        print(f"Computed {name}: both horizons and all frozen source preparations.", flush=True)
    comparisons = {}
    for horizon in (1, 2):
        base = cases["intact"][horizon-1]["choi_profile"]
        comparisons[str(horizon)] = {
            name: compare_profiles(base, cases[name][horizon-1]["choi_profile"])
            for name in PREPARATIONS if name != "intact"}
    if max(errors.values()) > 1e-12:
        raise RuntimeError(f"representation check failed: {errors}")
    return {"controls": controls, "cases": cases, "representation_errors": errors,
            "intact_minus_other_labelled_profile_comparisons": comparisons}


def git(*args):
    result = subprocess.run(["git", "-c", f"safe.directory={ROOT.as_posix()}", *args],
                            cwd=ROOT, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    results = run()
    results["provenance"] = {
        "generated_utc": datetime.now(UTC).isoformat(), "protocol_sha256": PROTOCOL_SHA256,
        "python": platform.python_version(), "numpy": np.__version__,
        "branch": git("branch", "--show-current"), "head": git("rev-parse", "HEAD"),
        "git_status_before_export": git("status", "--short"),
        "source_sha256": {source: hashlib.sha256((ROOT/source).read_bytes()).hexdigest()
                          for source in SOURCES},
        "method": "Exact finite enumeration and floating-point eigenspectra; no Monte Carlo.",
    }
    output = ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    (output / "evidence.json").write_text(json.dumps(results, indent=2, allow_nan=False)+"\n",
                                         encoding="utf-8")
    summary = {
        "representation_errors": results["representation_errors"],
        "intact_minus_other": results["intact_minus_other_labelled_profile_comparisons"],
        "rounds": {name: [{"horizon": r["horizon"],
                          "choi_size_summary": r["choi_profile"]["by_size"],
                          "actual_p0_08": r["actual_preparations"][0]["records"]}
                         for r in data] for name, data in results["cases"].items()},
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n",
                                        encoding="utf-8")
    print(json.dumps({"output": str(output), "representation_errors": results["representation_errors"]}))


if __name__ == "__main__":
    main()
