# Setup Scripts

Local environment helpers for the Omega workspace.

Files:

- `omega_env.ps1`: PowerShell environment activation and CPU/GPU cache paths.
- `omega_env.bat`: Windows batch equivalent.
- `invoke_lake.ps1`: Lean/Lake wrapper that runs from `formal/lean`, preferring
  the installed pinned toolchain binary and falling back to Elan/PATH discovery.
- `requirements-gpu-cu130.txt`: optional GPU dependency pin file for the local
  CUDA 13 / PyTorch / CuPy setup.

These scripts are convenience helpers for local runs. They are not required for
reading the repo or reviewing the research notes.
