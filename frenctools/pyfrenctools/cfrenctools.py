import ctypes
import os

from .shared import create_xgrid


_libpath = os.path.dirname(__file__) + "/../cfrenctools/c_build/clib.so"
_lib = ctypes.cdll.LoadLibrary(_libpath)

def init(libpath: str = None):

    global _libpath, _lib

    if libpath is not None:
        _libpath = libpath
        _lib = ctypes.cdll.LoadLibrary(_libpath)

    create_xgrid.init(_libpath, _lib)

def lib() -> type[ctypes.CDLL]:
    return _lib

def libpath() -> str:
    return _libpath
