"""Small exact reader and history-retention comparison."""

import json
from pathlib import Path

from omega_v2.finite.quantum_readers import (
    controlled_reader,
    observational_controls,
    record_retention,
    sequential_readers,
)


def main():
    result = {
        "controlled": {str(r): controlled_reader(r)[0] for r in [.25, .5, .75]},
        "sequential": {order: sequential_readers(order) for order in ["ZX", "XZ"]},
        "retention": {mode: record_retention(mode) for mode in ["retain", "uncompute", "transfer"]},
        "observational": observational_controls(),
    }
    folder = Path("results/local_runs/quantum_readers_v0")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
