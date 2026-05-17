from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from .generators import generate_algebra
from .policies import evaluate_decision
from .simulation import run_condition
from .summarize import write_jsonl


CASES = ("case_brittle_peak", "case_flat", "case_lock_in", "case_sparse_collapse")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run deterministic VAL0-CT divergence cases.")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--num-tasks", type=int, default=64)
    parser.add_argument("--num-constructors", type=int, default=2)
    parser.add_argument("--sample-size", type=int, default=256)
    parser.add_argument("--max-paths", type=int, default=512)
    parser.add_argument("--h", type=int, default=2)
    parser.add_argument("--H", type=int, default=8)
    parser.add_argument("--T", type=int, default=32)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out or Path("results") / "val0_ct" / f"{run_id}_deterministic_cases"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    summary: list[str] = [
        "# VAL0-CT Deterministic Case Summary",
        "",
        "These are hand-built go/no-go cases for R1 vs R0-lookahead divergence.",
        "",
        "| case | R1 task | R0-lookahead task | same choice | R1 LHR | R0-lookahead LHR | pass note |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for case in CASES:
        algebra = generate_algebra(case, seed=0, num_tasks=args.num_tasks, num_constructors=args.num_constructors)
        decision = evaluate_decision(
            algebra,
            algebra.initial_state,
            h=args.h,
            H=args.H,
            seed=0,
            sample_size=args.sample_size,
            max_paths=args.max_paths,
        )
        decision.pop("_paths", None)
        r1_row = run_condition(algebra, args.h, args.H, args.T, "R1", args.sample_size, 0, args.max_paths)
        r0_row = run_condition(algebra, args.h, args.H, args.T, "R0_lookahead", args.sample_size, 0, args.max_paths)
        note = "diagnostic"
        if case == "case_brittle_peak":
            note = (
                "PASS"
                if decision["R1_chosen_task"] != decision["R0_lookahead_chosen_task"]
                and float(r1_row["global_lhr"]) > float(r0_row["global_lhr"])
                else "FAIL"
            )
        elif case == "case_lock_in":
            pseudo_row = run_condition(algebra, args.h, args.H, args.T, "pseudo_omega", args.sample_size, 0, args.max_paths)
            note = "PASS" if pseudo_row["pseudo_omega_flag"] else "CHECK"
        rows.append(
            {
                "case": case,
                **decision,
                "R1_global_lhr": r1_row["global_lhr"],
                "R0_lookahead_global_lhr": r0_row["global_lhr"],
                "note": note,
            }
        )
        summary.append(
            "| {case} | {r1} | {r0} | {same} | {r1_lhr:.3f} | {r0_lhr:.3f} | {note} |".format(
                case=case,
                r1=decision["R1_chosen_task"],
                r0=decision["R0_lookahead_chosen_task"],
                same=decision["R1_R0lookahead_same_choice"],
                r1_lhr=float(r1_row["global_lhr"]),
                r0_lhr=float(r0_row["global_lhr"]),
                note=note,
            )
        )
    config = vars(args)
    config["run_id"] = run_id
    (out_dir / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True, default=str), encoding="utf-8")
    write_jsonl(out_dir / "results.jsonl", rows)
    (out_dir / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(json.dumps({"out_dir": str(out_dir), "rows": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

