"""Compare saved response coordinates without rerunning or fitting the dynamics."""

import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parents[2] / "docs/research_notes/omega_v2/thermal_binding_v0"


def main():
    data = json.loads((OUT / "profiles.json").read_text(encoding="utf-8"))
    summary = {}
    for name, model in data["mobile"].items():
        rows = []
        for a, b in (
            ("assembled", "dispersed"),
            ("assembled", "contact_unbound"),
            ("contact_unbound", "dispersed"),
        ):
            for x, y in zip(
                model["preparations"][a]["cuts"], model["preparations"][b]["cuts"], strict=True
            ):
                for px, py in zip(x["profiles"], y["profiles"], strict=True):
                    present = np.array(px["event_present"]) & np.array(py["event_present"])
                    delta = (
                        np.array(px["reaction_response_tv"]) - np.array(py["reaction_response_tv"])
                    )[:, present]
                    rows.append(
                        {
                            "A": a,
                            "B": b,
                            "cut": x["time"],
                            "lag": px["lag"],
                            "common_event_channels": int(present.sum()),
                            "A_greater": int((delta > 1e-9).sum()),
                            "B_greater": int((delta < -1e-9).sum()),
                            "ties": int((abs(delta) <= 1e-9).sum()),
                        }
                    )
        summary[name] = rows
    result = {
        "tolerance": 1e-9,
        "scope": "Counts of unaggregated common-event response coordinates; not a measure over frames or a lushness score. All arrays retained in profiles.json.",
        "mobile": summary,
    }
    (OUT / "comparison_summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print("Saved common-event response comparisons; no simulation rerun.")


if __name__ == "__main__":
    main()
