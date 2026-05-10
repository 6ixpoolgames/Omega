$workspace = Split-Path -Parent $MyInvocation.MyCommand.Path

# Ryzen 5900X: 12 physical cores / 24 logical threads. These defaults keep
# CPU numeric kernels parallel without oversubscribing every workload.
$env:OMP_NUM_THREADS = "12"
$env:OPENBLAS_NUM_THREADS = "12"
$env:MKL_NUM_THREADS = "12"
$env:NUMEXPR_MAX_THREADS = "12"
$env:NUMBA_NUM_THREADS = "12"

$env:UV_CACHE_DIR = Join-Path $workspace ".uv-cache"
$env:UV_PYTHON_INSTALL_DIR = Join-Path $workspace ".tools\python"

& (Join-Path $workspace ".venv\Scripts\Activate.ps1")

