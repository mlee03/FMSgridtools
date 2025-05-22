import subprocess
from typing import List

from setuptools import find_namespace_packages, setup
from setuptools.command.build_py import build_py


class CustomBuild_Py(build_py):
    def run(self):
        with open("compile_log.txt", "w") as f:
            subprocess.run(
                ["mkdir", "-p","c_build"],
                cwd="./cfrenctools/",
                stdout=f,
                stderr=subprocess.STDOUT,
            )
            subprocess.run(
                ["cmake", ".."],
                cwd="./cfrenctools/c_build",
                stdout=f,
                stderr=subprocess.STDOUT,
            )
            subprocess.run(
                ["make"],
                cwd="./cfrenctools/c_build",
                stdout=f,
                stderr=subprocess.STDOUT,
            )
        build_py.run(self)

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
    name="pyfrenctools",
    license="",
    packages=find_namespace_packages(include=["pyfrenctools", "pyfrenctools.*"]),
    include_package_data=True,
    version="0.0.1",
    zip_safe=False,
    cmdclass={'build_py': CustomBuild_Py}
)
