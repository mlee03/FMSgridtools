import ctypes
import os

from .shared import create_xgrid
from .make_mosaic import mosaic_util, mosaic_coupled_utils
from .make_hgrid import make_hgrid_wrappers

_libpath = os.path.dirname(__file__) + "/c_install/clib.so"
_lib = ctypes.cdll.LoadLibrary(_libpath)

def init(libpath: str = None):

    global _libpath, _lib

    if libpath is not None:
        _libpath = libpath
        _lib = ctypes.cdll.LoadLibrary(_libpath)

    create_xgrid.init(_libpath, _lib)
    mosaic_util.init(_libpath, _lib)
    mosaic_coupled_utils.init(_libpath, _lib)
    make_hgrid_wrappers.init(_libpath, _lib)

def lib() -> type[ctypes.CDLL]:
    return _lib

def libpath() -> str:
    return _libpath
