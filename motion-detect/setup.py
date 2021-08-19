import Cython
from setuptools import setup
from Cython.Build import cythonize

setup(
    name='algo',
    # extra_compile_args=["-O3"],
    ext_modules=cythonize(
        ["CustomAlgorithm.py", "TriggerInfo.py", "CreateDataset.py"],
        annotate=True,
        # annotate=True,
        # compiler_directives={'O': 3},
        language_level="3"),
    zip_safe=False,
)
