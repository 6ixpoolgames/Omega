from __future__ import annotations

import importlib
import os
import platform
import time


def version(module_name: str) -> str:
    module = importlib.import_module(module_name)
    return getattr(module, "__version__", "unknown")


def main() -> None:
    print(f"python: {platform.python_version()}")
    print(f"platform: {platform.platform()}")
    print(f"cpu threads requested: {os.environ.get('OMP_NUM_THREADS', 'unset')}")

    packages = [
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "sympy",
        "sklearn",
        "statsmodels",
        "networkx",
        "fitz",
        "numba",
        "torch",
        "torchvision",
        "torchaudio",
        "cupy",
    ]
    for package in packages:
        try:
            print(f"{package}: {version(package)}")
        except Exception as exc:
            print(f"{package}: unavailable ({exc})")

    import numpy as np
    import torch

    size = 2048
    rng = np.random.default_rng(42)
    a = rng.normal(size=(size, size)).astype(np.float32)
    b = rng.normal(size=(size, size)).astype(np.float32)

    start = time.perf_counter()
    cpu_result = a @ b
    print(f"numpy cpu matmul {size}x{size}: {time.perf_counter() - start:.3f}s")
    print(f"numpy checksum: {float(cpu_result[0, 0]):.6f}")

    torch.set_num_threads(min(12, os.cpu_count() or 12))
    print(f"torch cpu threads: {torch.get_num_threads()}")
    print(f"torch cuda available: {torch.cuda.is_available()}")
    print(f"torch cuda build: {torch.version.cuda}")
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"torch gpu: {torch.cuda.get_device_name(0)}")
        x = torch.randn((size, size), device=device)
        y = torch.randn((size, size), device=device)
        torch.cuda.synchronize()
        start = time.perf_counter()
        z = x @ y
        torch.cuda.synchronize()
        print(f"torch gpu matmul {size}x{size}: {time.perf_counter() - start:.3f}s")
        print(f"torch checksum: {float(z[0, 0].detach().cpu()):.6f}")

    try:
        import cupy as cp

        print(f"cupy cuda runtime: {cp.cuda.runtime.runtimeGetVersion()}")
        x = cp.random.standard_normal((size, size), dtype=cp.float32)
        y = cp.random.standard_normal((size, size), dtype=cp.float32)
        cp.cuda.Stream.null.synchronize()
        start = time.perf_counter()
        z = x @ y
        cp.cuda.Stream.null.synchronize()
        print(f"cupy gpu matmul {size}x{size}: {time.perf_counter() - start:.3f}s")
        print(f"cupy checksum: {float(z[0, 0].get()):.6f}")
    except Exception as exc:
        print(f"cupy gpu check failed: {exc}")


if __name__ == "__main__":
    main()

