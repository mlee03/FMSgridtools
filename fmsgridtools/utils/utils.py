import os
import sys
from time import ctime
from git import Repo
from pkg_resources import get_distribution
from typing import Optional
from subprocess import run

def check_file_is_there( check_file: str, debug: bool = False ) :

    if os.path.isfile( check_file ) :
        if debug : print(f"File \"{check_file}\" exists")
    else :
        raise FileNotFoundError(f"Cannot find file \"{check_file}\"")

def get_provenance_attrs(
    great_circle_algorithm: Optional[bool] = False,
    grid_version: Optional[str] = "0.2") -> dict:
    # returns a dictionary of provenance information to be added
    # as global attributes for output netcdf files
    repo = Repo(search_parent_directories=True)
    git_hash = repo.head.object.hexsha
    package_version = get_distribution("gridtools").version
    history = " ".join(sys.argv)
    hostname = run(["hostname"],capture_output=True,text=True).stdout
    g_attrs = {
        "grid_version": grid_version,
        "code_release_version": package_version,
        "git_hash": git_hash,
        "creationtime": str(ctime()),
        "hostname": hostname,
        "history": history,
        }
    # added conditionally
    if(great_circle_algorithm):
        g_attrs["great_circle_algorithm"] = "TRUE"
    return g_attrs
