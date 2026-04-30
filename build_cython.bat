@echo off
REM Build Cython extensions for the engine. Sources vcvars64.bat first
REM because setuptools 82 doesn't auto-detect Visual Studio 2026 yet.
REM
REM Usage:  build_cython.bat
REM
REM After build, the .pyd files land next to their .pyx siblings
REM and are imported transparently. Engine code falls back to pure
REM Python if the compiled extension is missing.

call "C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 goto :err_vcvars

set DISTUTILS_USE_SDK=1
set MSSdk=1

cd /d "%~dp0"
python setup_cython.py build_ext --inplace
if errorlevel 1 goto :err_build

echo.
echo === Cython build OK ===
exit /b 0

:err_vcvars
echo ERROR: vcvars64.bat failed -- is VS 2026 Build Tools installed?
exit /b 1

:err_build
echo ERROR: Cython build failed
exit /b 1
