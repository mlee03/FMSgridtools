import os
from pathlib import Path
from typing import List
import subprocess

from setuptools import setup, find_namespace_packages
from setuptools.command.install import install

class CustomInstall(install):
    def run(self):
        with open("compile_log.txt", "w") as f:
            subprocess.run(
                ["cmake", ".."], 
                cwd="./FRENCTools_lib/cfrenctools/c_build", 
                stdout=f,
                stderr=subprocess.STDOUT,
            )
            subprocess.run(
                ["make"], 
                cwd="./FRENCTools_lib/cfrenctools/c_build", 
                stdout=f,
                stderr=subprocess.STDOUT,
            )
        install.run(self)

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
    packages=find_namespace_packages(include=["FMSgridtools", "FMSgridtools.*", "FRENCTools_lib", "FRENCTools_lib.pyfrenctools.*"]),
    include_package_data=True,
    version="0.0.1",
    zip_safe=False,
    cmdclass={'install': CustomInstall},
    entry_points={
        "console_scripts": [
            "fmsgridtools make_hgrid = fmsgridtools.make_grid.hgrid.make_hgrid:main",
            "fmsgridtools make_topog = fmsgridtools.make_topog.make_topog:make_topog",
        ]
    },
)
