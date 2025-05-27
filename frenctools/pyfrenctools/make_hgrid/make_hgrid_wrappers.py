from ctypes import CDLL, POINTER, c_int, c_double, c_bool, c_char_p
import numpy as np
import numpy.typing as npt

from pyfrenctools.utils.ctypes import (
    set_array,
    set_c_int,
    set_c_str,
)

_libpath = None
_lib = None

def init(libpath: str, lib: type[CDLL]):

    global _libpath, _lib

    _libpath = libpath
    _lib = lib    

def create_regular_lonlat_grid(
    nxbnds: int,
    nybnds: int,
    xbnds: npt.NDArray,
    ybnds: npt.NDArray,
    nlon: npt.NDArray,
    nlat: npt.NDArray,
    dlon: npt.NDArray,
    dlat: npt.NDArray,
    use_legacy: int,
    isc: int,
    iec: int,
    jsc: int,
    jec: int,
    x: npt.NDArray,
    y: npt.NDArray,
    dx: npt.NDArray,
    dy: npt.NDArray,
    area: npt.NDArray,
    angle_dx: npt.NDArray,
    center: str,
    use_great_circle_algorithm: int
):
    _create_regular_lonlat_grid = _lib.create_regular_lonlat_grid
    arglist = []
    set_c_int(nxbnds, arglist)
    set_c_int(nybnds, arglist)
    set_array(xbnds, arglist)
    set_array(ybnds, arglist)
    set_array(nlon, arglist)
    set_array(nlat, arglist)
    set_array(dlon, arglist)
    set_array(dlat, arglist)
    set_c_int(use_legacy, arglist)
    set_c_int(isc, arglist)
    set_c_int(iec, arglist)
    set_c_int(jsc, arglist)
    set_c_int(jec, arglist)
    set_array(x, arglist)
    set_array(y, arglist)
    set_array(dx, arglist)
    set_array(dy, arglist)
    set_array(area, arglist)
    set_array(angle_dx, arglist)
    set_c_str(center, arglist)
    set_c_int(use_great_circle_algorithm, arglist)


    _create_regular_lonlat_grid.argtypes = [
        POINTER(c_int),
        POINTER(c_int),
        np.ctypeslib.ndpointer(dtype=xbnds.dtype, ndim=xbnds.ndim, shape=xbnds.shape),
        np.ctypeslib.ndpointer(dtype=ybnds.dtype, ndim=ybnds.ndim, shape=ybnds.shape),
        np.ctypeslib.ndpointer(dtype=nlon.dtype, ndim=nlon.ndim, shape=nlon.shape),
        np.ctypeslib.ndpointer(dtype=nlat.dtype, ndim=nlat.ndim, shape=nlat.ndim),
        np.ctypeslib.ndpointer(dtype=dlon.dtype, ndim=dlon.ndim, shape=dlon.shape),
        np.ctypeslib.ndpointer(dtype=dlat.dtype, ndim=dlat.ndim, shape=dlat.shape),
        c_int,
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_int),
        POINTER(c_int),
        np.ctypeslib.ndpointer(dtype=x.dtype, ndim=x.ndim, shape=x.shape),
        np.ctypeslib.ndpointer(dtype=y.dtype, ndim=y.ndim, shape=y.shape),
        np.ctypeslib.ndpointer(dtype=dx.dtype, ndim=dx.ndim, shape=dx.shape),
        np.ctypeslib.ndpointer(dtype=dy.dtype, ndim=dy.ndim, shape=dy.shape),
        np.ctypeslib.ndpointer(dtype=area.dtype, ndim=area.ndim, shape=area.shape),
        np.ctypeslib.ndpointer(dtype=angle_dx.dtype, ndim=angle_dx.ndim, shape=angle_dx.shape),
        c_char_p,
        c_int,
    ] 
    _create_regular_lonlat_grid.restype = None

    _create_regular_lonlat_grid(*arglist)
