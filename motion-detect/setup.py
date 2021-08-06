from setuptools import setup
from Cython.Build import cythonize

setup(
    name='algo',
    ext_modules=cythonize(["CustomAlgorithm.pyx", "CreateDataset.py"], annotate=True, language_level="3"),
    zip_safe=False,

)
