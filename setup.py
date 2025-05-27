import os
import subprocess
from pathlib import Path
from typing import List

from setuptools import find_namespace_packages, setup
from setuptools.command.install import install

<<<<<<< HEAD

class CustomInstall(install):
    def run(self):
        with open("compile_log.txt", "w") as f:
            subprocess.run(
                ["cmake", ".."],
                cwd="./frenctools/cfrenctools/c_build",
                stdout=f,
                stderr=subprocess.STDOUT,
                check=True,
            )
            subprocess.run(
                ["make"],
                cwd="./frenctools/cfrenctools/c_build",
                stdout=f,
                stderr=subprocess.STDOUT,
                check=True,
            )
        install.run(self)
=======
def local_pkg(name: str, relative_path: str) -> str:
    """Returns an absolute path to a local package."""
    path = f"{name} @ file://{Path(os.path.abspath(__file__)).parent / relative_path}"
    return path
>>>>>>> origin/main

test_requirements = ["pytest", "coverage"]
develop_requirements = test_requirements + ["pre-commit"]

extras_requires = {
    "test": test_requirements,
    "develop": develop_requirements,
}

requirements = [
    "click",
    "gitpython",
    "h5netcdf",
    "h5py",
    "numpy",
    "xarray",
    "netCDF4",
    "pyfms @ git+https://github.com/NOAA-GFDL/pyFMS.git@main",
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
<<<<<<< HEAD
    packages=find_namespace_packages(include=["fmsgridtools", "fmsgridtools.*", "frencctools", "frenctools.pyfrenctools.*"]),
=======
    packages=find_namespace_packages(include=["FMSgridtools", "FMSgridtools.*"]),
>>>>>>> origin/main
    include_package_data=True,
    version="0.0.1",
    zip_safe=False,
    entry_points={
<<<<<<< HEAD
        "console_scripts": ["fmsgridtools = fmsgridtools.main:main"]
=======
        "console_scripts": [
            "make_hgrid = FMSgridtools.make_hgrid.make_hgrid:make_hgrid", # TODO fmsggridtools entrypoint
            "make_topog = FMSgridtools.make_topog.make_topog:make_topog", # TODO fmsgridtools entrypoint
        ]
>>>>>>> origin/main
    },
)
