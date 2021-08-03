from setuptools import setup
from Cython.Build import cythonize

setup(
    name='algo',
    ext_modules=cythonize("CustomAlgorithm.pyx"),
    zip_safe=False,
    extra_compile_args=["-O3"]
)
