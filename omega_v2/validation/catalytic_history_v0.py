"""Follow moving catalytic-production ancestry under the unchanged physical laws."""

import os

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"

import hashlib
import json
import time
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import expm_multiply

from omega_v2.finite.catalytic_binding import CatalyticBinding
from omega_v2.finite.catalytic_history import CatalyticHistory

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research_notes/omega_v2/catalytic_history_v0"
CUTS = (0, 1, 2, 5, 10, 20, 50)
FOLLOWUP_LAGS = (1, 5)


def run(barrier):
    start = time.perf_counter()
    model = CatalyticBinding(barrier=barrier)
    observer = CatalyticHistory(model)
    print(f"b={barrier}: {len(observer.states)} reachable history states", flush=True)
    rows, laws, occupations, conditional_arrays = [], [], [], {}
    checks = {
        "lumping_error": observer.lumping_error(),
        "physical_marginal_error": 0.0,
        "mass_error": 0.0,
        "occupation_mass_error": 0.0,
        "root_accounting_error": 0.0,
        "descendant_accounting_error": 0.0,
        "resource_accounting_error": 0.0,
    }
    killed = observer.no_descendant_formation_generator()
    no_event = {
        lag: expm_multiply(killed * lag, np.ones(len(observer.states))) for lag in FOLLOWUP_LAGS
    }
    for t in CUTS:
        law, occupation = observer.evolve(observer.initial, t)
        physical = observer.physical_law(law)
        summary = observer.summary(law, occupation)
        history_counts, resources = summary["history_event_counts"], summary["resource_profile"]
        checks["physical_marginal_error"] = max(
            checks["physical_marginal_error"],
            float(np.max(abs(physical - model.advance(observer.physical_initial, t)))),
        )
        checks["mass_error"] = max(checks["mass_error"], float(abs(law.sum() - 1)))
        checks["occupation_mass_error"] = max(
            checks["occupation_mass_error"], float(abs(occupation.sum() - t))
        )
        checks["root_accounting_error"] = max(
            checks["root_accounting_error"],
            abs(summary["original_survival"] + history_counts[4] - 1),
        )
        checks["descendant_accounting_error"] = max(
            checks["descendant_accounting_error"],
            abs(
                summary["descendant_bonds_mean"]
                - history_counts[0]
                - history_counts[1]
                + history_counts[5]
            ),
        )
        checks["resource_accounting_error"] = max(
            checks["resource_accounting_error"],
            float(
                abs(
                    observer.physical_initial @ model.fuel
                    - physical @ model.fuel
                    - resources[0]
                    + resources[1]
                )
            ),
        )
        row = {"cut": t, **summary}
        rows.append(row)
        laws.append(law)
        occupations.append(occupation)
        if t in (1, 5, 20):
            mask = ~observer.original_present & observer.descendants_present
            mass = float(law @ mask)
            followup = {"conditioning_probability": mass, "present": mass > 0, "rows": []}
            if mass > 0:
                initial = law * mask / mass
                conditional_arrays[f"after_original_cut_{t}"] = initial
                for lag in FOLLOWUP_LAGS:
                    later, occupied = observer.evolve(initial, lag)
                    followup["rows"].append(
                        {
                            "lag": lag,
                            "first_descendant_assisted_formation_probability": float(
                                1 - initial @ no_event[lag]
                            ),
                            **observer.summary(later, occupied),
                        }
                    )
                    conditional_arrays[f"after_original_cut_{t}_lag_{lag}"] = later
            row["original_gone_descendants_present_followup"] = followup
    if max(checks.values()) > 1e-8:
        raise ValueError(checks)
    q = observer.q
    np.savez_compressed(
        OUT / f"barrier_{barrier}_histories.npz",
        states=observer.states,
        physical_states=model.states,
        initial=observer.initial,
        event_sources=observer.event_sources,
        event_targets=observer.event_targets,
        event_channels=observer.event_channels,
        event_rates=observer.event_rates,
        Q_data=q.data,
        Q_indices=q.indices,
        Q_indptr=q.indptr,
        Q_shape=np.array(q.shape),
        resource_rates=observer.resource_rates,
        history_rates=observer.history_rates,
        cuts=np.array(CUTS),
        laws=np.array(laws),
        occupation_integrals=np.array(occupations),
        **conditional_arrays,
    )
    print(f"b={barrier}: history, continuation and resource profiles complete", flush=True)
    return {
        "parameters": model.parameters,
        "physical_state_count": len(model.ids),
        "history_state_count": len(observer.states),
        "event_channels": model.channel_names,
        "history_state_columns": [
            "physical_state_index",
            "original_bond_mask",
            "descendant_bond_mask",
            "history_flag",
        ],
        "history_flag_meanings": [
            "no_descendant_yet",
            "descendant_born",
            "descendant_has_assisted_formation",
        ],
        "resource_columns": model.reward_names,
        "history_count_columns": observer.history_columns,
        "rows": rows,
        "checks": checks,
        "runtime_seconds": time.perf_counter() - start,
    }


def main():
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    models = {str(b): run(b) for b in (0, 1, 2)}
    files = [
        Path(__file__),
        *[
            ROOT / f"omega_v2/finite/{s}.py"
            for s in ("spatial_binding", "catalytic_binding", "catalytic_history")
        ],
    ]
    result = {
        "schema": "catalytic-history-v0",
        "date": "2026-10-04",
        "cuts": CUTS,
        "models": models,
        "runtime_seconds": time.perf_counter() - started,
        "source_hashes": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files
        },
    }
    (OUT / "results.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "runtime_seconds": result["runtime_seconds"],
                "checks": {b: m["checks"] for b, m in models.items()},
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
