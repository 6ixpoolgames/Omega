$workspace = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

# Ryzen 5900X: 12 physical cores / 24 logical threads. These defaults keep
# CPU numeric kernels parallel without oversubscribing every workload.
$env:OMP_NUM_THREADS = "12"
$env:OPENBLAS_NUM_THREADS = "12"
$env:MKL_NUM_THREADS = "12"
$env:NUMEXPR_MAX_THREADS = "12"
$env:NUMBA_NUM_THREADS = "12"

$env:UV_CACHE_DIR = Join-Path $workspace ".uv-cache"
$env:UV_PYTHON_INSTALL_DIR = Join-Path $workspace ".tools\python"
$env:CUPY_CACHE_DIR = Join-Path $workspace ".cupy-cache"

# CuPy can use the CUDA 13 NVRTC DLLs bundled with torch in this environment.
# Put that directory on PATH so CuPy kernels compile without a system CUDA
# Toolkit install.
$torchLib = Join-Path $workspace ".venv\Lib\site-packages\torch\lib"
if (Test-Path $torchLib) {
    $env:PATH = "$torchLib;$env:PATH"
}

& (Join-Path $workspace ".venv\Scripts\Activate.ps1")
