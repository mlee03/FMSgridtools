import os
import subprocess
from pathlib import Path
from typing import List

from setuptools import find_namespace_packages, setup
from setuptools.command.install import install

def local_pkg(name: str, relative_path: str) -> str:
    """Returns an absolute path to a local package."""
    path = f"{name} @ file://{Path(os.path.abspath(__file__)).parent / relative_path}"
    return path

test_requirements = ["pytest", "coverage"]
develop_requirements = test_requirements + ["pre-commit"]

extras_requires = {
    "test": test_requirements,
    "develop": develop_requirements,
}

requirements: List[str] = [
    "click",
    "gitpython",
    "h5netcdf",
    "h5py",
    "numpy",
    "xarray",
    "netCDF4",
    local_pkg("pyFMS", "pyFMS"),
    local_pkg("pyfrenctools", "FREnctools_lib")
]

setup(
    author = "NOAA",
    python_requires=">3.11",
    classifiers="",
    install_requires=requirements,
    extras_require=extras_requires,
    name="fmsgridtools",
    license="",
    packages=find_namespace_packages(include=["fmsgridtools", "fmsgridtools.*"]),
    include_package_data=True,
    version="0.0.1",
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "make_hgrid = fmsgridtools.make_hgrid.make_hgrid:make_hgrid", # TODO fmsggridtools entrypoint
            "make_topog = fmsgridtools.make_topog.make_topog:make_topog", # TODO fmsgridtools entrypoint
        ]
    },
)
