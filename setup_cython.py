"""Build hot-path Cython extensions in-place.

Run via build_cython.bat (which sources vcvars64.bat first because
setuptools 82 doesn't auto-detect Visual Studio 2026 yet).

The .pyx modules ship alongside the .py originals; engine modules
import the compiled .pyd at module load if available, falling back
to pure Python on ImportError. This keeps the repo importable on
machines without a C compiler.
"""
from setuptools import setup
from Cython.Build import cythonize


extensions = cythonize(
    [
        "leekwars/_fast/_los.pyx",
    ],
    compiler_directives={
        "language_level": "3",
        "boundscheck": False,
        "wraparound": False,
        "initializedcheck": False,
        "cdivision": True,
    },
)

setup(
    name="leekwars-fast",
    ext_modules=extensions,
)
