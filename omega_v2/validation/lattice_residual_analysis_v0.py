"""Mechanism decomposition of the exact atlas's complete next-two-jump law."""

import hashlib
import json
from pathlib import Path

import numpy as np

from omega_v2.finite.lattice_chemistry import Parameters
from omega_v2.finite.lattice_residual import exact_square, two_wait_cdf
from omega_v2.validation.lattice_residual_v0 import LAGS, OUT, ROOT


def two_step_vectors(square, horizon):
    names = ("two_jumps", "two_fuel_bindings", "fuel_bindings_new_template",
             "fuel_bindings_existing_template", "fuel_bindings_uncatalyzed_second",
             "new_template_forward_second", "new_template_reverse_second")
    result = {k: np.zeros(len(square["states"])) for k in names}
    for i, firsts in enumerate(square["channels"]):
        a = square["escape"][i]
        for first in firsts:
            j = first["to"]
            b = square["escape"][j]
            weight1 = first["rate"] / a * two_wait_cdf(a, b, horizon) / b
            first_binds = (first["kind"] != "switch"
                           and tuple(first["members"]) not in square["states"][i].bonds)
            first_fuel = first_binds and first["kind"] in ("fuel", "catalytic")
            for second in square["channels"][j]:
                weight = weight1 * second["rate"]
                result["two_jumps"][i] += weight
                second_binds = (second["kind"] != "switch"
                                and tuple(second["members"]) not in square["states"][j].bonds)
                new_template = first_binds and second["catalyst"] == first["members"]
                if new_template:
                    name = "new_template_forward_second" if second_binds else "new_template_reverse_second"
                    result[name][i] += weight
                if first_fuel and second_binds and second["kind"] in ("fuel", "catalytic"):
                    result["two_fuel_bindings"][i] += weight
                    if new_template:
                        result["fuel_bindings_new_template"][i] += weight
                    elif second["catalyst"]:
                        result["fuel_bindings_existing_template"][i] += weight
                    else:
                        result["fuel_bindings_uncatalyzed_second"][i] += weight
    return result


def main():
    summary = json.loads((OUT / "summary.json").read_text())
    manifest = json.loads((OUT / "manifest.json").read_text())
    for name, digest in manifest["source_sha256"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise AssertionError(f"Original atlas source changed: {name}")
    output, max_error = [], 0.
    for regime in summary["regimes"]:
        square = exact_square(Parameters(**regime["parameters"]))
        columns = np.load(OUT / f"g{regime['id']:02d}" / "laws_support.npz")["cut_laws"]
        for lag in LAGS:
            values = {k: v @ columns for k, v in two_step_vectors(square, lag).items()}
            for j, cut in enumerate(regime["cuts"]):
                row = {"regime": regime["id"], "cut": cut["cut"],
                       "preparation": cut["preparation"], "lag": lag,
                       **{k: float(v[j]) for k, v in values.items()}}
                original = next(r for r in regime["residuals"] if r["cut"] == cut["cut"]
                                and r["preparation"] == cut["preparation"] and r["lag"] == lag)
                expected = 1 - sum(original["jump_probabilities_0_to_depth"][:2])
                error = max(abs(expected - row["two_jumps"]),
                            abs(original["two_next_jumps_fuel_bind"] - row["two_fuel_bindings"]),
                            abs(row["two_fuel_bindings"] - row["fuel_bindings_new_template"]
                                - row["fuel_bindings_existing_template"]
                                - row["fuel_bindings_uncatalyzed_second"]))
                max_error = max(max_error, error)
                output.append(row)
    if max_error > 1e-10:
        raise AssertionError(max_error)
    result = {"rows": output, "native_law_agreement_error": max_error,
              "analysis_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT / "two_step_followup.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"rows": len(output), "native_law_agreement_error": max_error}))


if __name__ == "__main__":
    main()
