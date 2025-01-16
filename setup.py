import os
from pathlib import Path
from typing import List

from setuptools import setup, find_namespace_packages

test_requirements = ["pytest", "coverage"]
develop_requirements = test_requirements + ["pre-commit"]

extras_requires = {
    "test": test_requirements,
    "develop": develop_requirements,
}

requirements: List[str] = [
    "click",
    "h5netcdf",
    "h5py",
    "numpy",
    "xarray",
    "netCDF4",
]

setup(
    author = "NOAA",
    python_requires=">3.11",
    classifiers="",
    install_requires=requirements,
    extras_require=extras_requires,
    name="fmsgridtools",
    license="",
    packages=find_namespace_packages(include=["FMSgridtools", "FMSgridtools.*"]),
    include_package_data=True,
    version="0.0.1",
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "fmsgridtools make_hgrid = fmgridtools.make_grid.hgrid.make_hgrid:main",
        ]
    },
)
