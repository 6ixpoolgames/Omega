@echo off
for %%I in ("%~dp0..\..") do set "WORKSPACE=%%~fI\"

rem Ryzen 5900X: 12 physical cores / 24 logical threads.
set "OMP_NUM_THREADS=12"
set "OPENBLAS_NUM_THREADS=12"
set "MKL_NUM_THREADS=12"
set "NUMEXPR_MAX_THREADS=12"
set "NUMBA_NUM_THREADS=12"

set "UV_CACHE_DIR=%WORKSPACE%.uv-cache"
set "UV_PYTHON_INSTALL_DIR=%WORKSPACE%.tools\python"
set "CUPY_CACHE_DIR=%WORKSPACE%.cupy-cache"

rem CuPy uses the CUDA 13 NVRTC DLLs bundled with torch in this environment.
if exist "%WORKSPACE%.venv\Lib\site-packages\torch\lib" (
  set "PATH=%WORKSPACE%.venv\Lib\site-packages\torch\lib;%PATH%"
)

call "%WORKSPACE%.venv\Scripts\activate.bat"
