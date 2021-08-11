from setuptools import setup
from Cython.Build import cythonize

setup(
    name='algo',
    ext_modules=cythonize(["CustomAlgorithm.pyx", "CreateDataset.py"],
<<<<<<< HEAD
                          annotate=True,
=======
                          # annotate=True,
>>>>>>> origin/master
                          language_level="3"),
    zip_safe=False,
)
