@echo off
set "WORKSPACE=%~dp0"

rem Ryzen 5900X: 12 physical cores / 24 logical threads.
set "OMP_NUM_THREADS=12"
set "OPENBLAS_NUM_THREADS=12"
set "MKL_NUM_THREADS=12"
set "NUMEXPR_MAX_THREADS=12"
set "NUMBA_NUM_THREADS=12"

set "UV_CACHE_DIR=%WORKSPACE%.uv-cache"
set "UV_PYTHON_INSTALL_DIR=%WORKSPACE%.tools\python"

call "%WORKSPACE%.venv\Scripts\activate.bat"

