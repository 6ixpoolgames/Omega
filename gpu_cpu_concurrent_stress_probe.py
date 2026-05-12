#!/usr/bin/env python
"""Small concurrent CPU/GPU stress probe for the Omega workstation.

This is an environment validation probe, not a scientific Omega test. It runs a
NumPy CPU workload and a CuPy GPU workload at the same time for a fixed duration
and writes compact throughput results.
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import threading
import time
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--duration-sec", type=float, default=180.0)
    p.add_argument("--out-dir", type=Path, default=Path("environment_stress_results"))
    p.add_argument("--cpu-size", type=int, default=1400)
    p.add_argument("--gpu-size", type=int, default=4096)
    p.add_argument("--cpu-threads", type=int, default=int(os.environ.get("OMEGA_STRESS_CPU_THREADS", "8")))
    return p.parse_args()


def cpu_worker(stop_at: float, size: int, out: queue.Queue) -> None:
    rng = np.random.default_rng(123)
    a = rng.normal(size=(size, size)).astype(np.float32)
    b = rng.normal(size=(size, size)).astype(np.float32)
    loops = 0
    checksum = 0.0
    started = time.perf_counter()
    while time.perf_counter() < stop_at:
        c = a @ b
        checksum += float(c[0, 0])
        loops += 1
        a, b = b, c / max(float(size), 1.0)
    elapsed = time.perf_counter() - started
    flops = 2.0 * (size ** 3) * loops
    out.put({
        "worker": "cpu_numpy",
        "loops": loops,
        "elapsed_seconds": elapsed,
        "approx_tflops": flops / max(elapsed, 1e-9) / 1e12,
        "checksum": checksum,
        "size": size,
    })


def gpu_worker(stop_at: float, size: int, out: queue.Queue) -> None:
    import cupy as cp

    rng = cp.random.default_rng(456)
    a = rng.standard_normal((size, size), dtype=cp.float32)
    b = rng.standard_normal((size, size), dtype=cp.float32)
    cp.cuda.Stream.null.synchronize()
    loops = 0
    checksum = 0.0
    started = time.perf_counter()
    while time.perf_counter() < stop_at:
        c = a @ b
        checksum += float(c[0, 0].get())
        loops += 1
        a, b = b, c / max(float(size), 1.0)
    cp.cuda.Stream.null.synchronize()
    elapsed = time.perf_counter() - started
    flops = 2.0 * (size ** 3) * loops
    props = cp.cuda.runtime.getDeviceProperties(0)
    name = props["name"].decode() if isinstance(props["name"], bytes) else str(props["name"])
    free_mem, total_mem = cp.cuda.runtime.memGetInfo()
    out.put({
        "worker": "gpu_cupy",
        "device": name,
        "loops": loops,
        "elapsed_seconds": elapsed,
        "approx_tflops": flops / max(elapsed, 1e-9) / 1e12,
        "checksum": checksum,
        "size": size,
        "free_mem_bytes": int(free_mem),
        "total_mem_bytes": int(total_mem),
    })


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stop_at = time.perf_counter() + args.duration_sec
    results: queue.Queue = queue.Queue()
    started_wall = time.time()
    threads = [
        threading.Thread(target=cpu_worker, args=(stop_at, args.cpu_size, results), daemon=True),
        threading.Thread(target=gpu_worker, args=(stop_at, args.gpu_size, results), daemon=True),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    rows = []
    while not results.empty():
        rows.append(results.get())
    summary = {
        "probe": "gpu_cpu_concurrent_stress_probe",
        "status": "COMPLETE",
        "duration_requested_seconds": args.duration_sec,
        "wall_started": started_wall,
        "cpu_threads_env": {
            "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
            "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
            "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
        },
        "workers": rows,
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    csv_lines = ["worker,size,loops,elapsed_seconds,approx_tflops,device"]
    for row in rows:
        csv_lines.append(",".join([
            str(row.get("worker", "")),
            str(row.get("size", "")),
            str(row.get("loops", "")),
            f"{float(row.get('elapsed_seconds', 0.0)):.6f}",
            f"{float(row.get('approx_tflops', 0.0)):.6f}",
            str(row.get("device", "")),
        ]))
    (args.out_dir / "throughput.csv").write_text("\n".join(csv_lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
