import setuptools

# with open("./readme.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="dims_common",
    version="0.0.1",
    author="Mateusz Kojro",
    author_email="mateuszkojro@outlook.com",
    description="Package containing common python scripys for DIMS project",
    # long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    project_urls={
        # "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    # packages=["dims_common"],
    python_requires=">=3.6",
)