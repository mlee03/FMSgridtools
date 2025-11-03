from ctypes import CDLL, POINTER, c_int, c_double, c_bool, c_char_p
import numpy as np
import numpy.typing as npt

from pyfrenctools.utils.ctypes import (
    set_array,
    set_c_double,
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

def create_gnomonic_cubic_grid(
        grid_type: str,
        nlon: npt.NDArray,
        nlat: npt.NDArray,
        x: npt.NDArray,
        y: npt.NDArray,
        dx: npt.NDArray,
        dy: npt.NDArray,
        area: npt.NDArray,
        angle_dx: npt.NDArray,
        angle_dy: npt.NDArray,
        shift_fac: float,
        do_schmidt: int,
        do_cube_transform: int,
        stretch_factor: float,
        target_lon: float,
        target_lat: float,
        num_nest_grids: int,
        parent_tile: npt.NDArray,
        refine_ratio: npt.NDArray,
        istart_nest: npt.NDArray,
        iend_nest: npt.NDArray,
        jstart_nest: npt.NDArray,
        jend_nest: npt.NDArray,
        halo: int,
        output_length_angle: int,
):
    _create_gnomonic_cubic_grid = _lib.create_gnomonic_cubic_grid

    arglist = []
    set_c_str(grid_type, arglist)
    set_array(nlon, arglist)
    set_array(nlat, arglist)
    set_array(x, arglist)
    set_array(y, arglist)
    set_array(dx, arglist)
    set_array(dy, arglist)
    set_array(area, arglist)
    set_array(angle_dx, arglist)
    set_array(angle_dy, arglist)
    set_c_double(shift_fac, arglist)
    set_c_int(do_schmidt, arglist)
    set_c_int(do_cube_transform, arglist)
    set_c_double(stretch_factor, arglist)
    set_c_double(target_lon, arglist)
    set_c_double(target_lat, arglist)
    set_c_int(num_nest_grids, arglist)
    set_array(parent_tile, arglist)
    set_array(refine_ratio, arglist)
    set_array(istart_nest, arglist)
    set_array(iend_nest, arglist)
    set_array(jstart_nest, arglist)
    set_array(jend_nest, arglist)
    set_c_int(halo, arglist)
    set_c_int(output_length_angle, arglist)

    _create_gnomonic_cubic_grid.argtypes = [
        c_char_p,
        np.ctypeslib.ndpointer(dtype=nlon.dtype, ndim=nlon.ndim, shape=nlon.shape),
        np.ctypeslib.ndpointer(dtype=nlat.dtype, ndim=nlat.ndim, shape=nlat.shape),
        np.ctypeslib.ndpointer(dtype=x.dtype, ndim=x.ndim, shape=x.shape),
        np.ctypeslib.ndpointer(dtype=y.dtype, ndim=y.ndim, shape=y.shape),
        np.ctypeslib.ndpointer(dtype=dx.dtype, ndim=dx.ndim, shape=dx.shape),
        np.ctypeslib.ndpointer(dtype=dy.dtype, ndim=dy.ndim, shape=dy.shape),
        np.ctypeslib.ndpointer(dtype=area.dtype, ndim=area.ndim, shape=area.shape),
        np.ctypeslib.ndpointer(dtype=angle_dx.dtype, ndim=angle_dx.ndim, shape=angle_dx.shape),
        np.ctypeslib.ndpointer(dtype=angle_dy.dtype, ndim=angle_dy.ndim, shape=angle_dy.shape),
        c_double,
        c_int,
        c_int,
        c_double,
        c_double,
        c_double,
        c_int,
        np.ctypeslib.ndpointer(dtype=parent_tile.dtype, ndim=parent_tile.ndim, shape=parent_tile.shape),
        np.ctypeslib.ndpointer(dtype=refine_ratio.dtype, ndim=refine_ratio.ndim, shape=refine_ratio.shape),
        np.ctypeslib.ndpointer(dtype=istart_nest.dtype, ndim=istart_nest.ndim, shape=istart_nest.shape),
        np.ctypeslib.ndpointer(dtype=iend_nest.dtype, ndim=iend_nest.ndim, shape=iend_nest.shape),
        np.ctypeslib.ndpointer(dtype=jstart_nest.dtype, ndim=jstart_nest.ndim, shape=jstart_nest.shape),
        np.ctypeslib.ndpointer(dtype=jend_nest.dtype, ndim=jend_nest.ndim, shape=jend_nest.shape),
        c_int,
        c_int, 
    ]
    _create_gnomonic_cubic_grid.restype = None

    _create_gnomonic_cubic_grid(*arglist)

def create_gnomonic_cubic_grid_GR(
        grid_type: str,
        nlon: npt.NDArray,
        nlat: npt.NDArray,
        x: npt.NDArray,
        y: npt.NDArray,
        dx: npt.NDArray,
        dy: npt.NDArray,
        area: npt.NDArray,
        angle_dx: npt.NDArray,
        angle_dy: npt.NDArray,
        shift_fac: float,
        do_schmidt: int,
        do_cube_transform: int,
        stretch_factor: float,
        target_lon: float,
        target_lat: float,
        nest_grid: int,
        parent_tile: int,
        refine_ratio: int,
        istart_nest: int,
        iend_nest: int,
        jstart_nest: int,
        jend_nest: int,
        halo: int,
        output_length_angle: int,
):
    _create_gnomonic_cubic_grid_GR = _lib.create_gnomonic_cubic_grid_GR

    arglist = []
    set_c_str(grid_type, arglist)
    set_array(nlon, arglist)
    set_array(nlat, arglist)
    set_array(x, arglist)
    set_array(y, arglist)
    set_array(dx, arglist)
    set_array(dy, arglist)
    set_array(area, arglist)
    set_array(angle_dx, arglist)
    set_array(angle_dy, arglist)
    set_c_double(shift_fac, arglist)
    set_c_int(do_schmidt, arglist)
    set_c_int(do_cube_transform, arglist)
    set_c_double(stretch_factor, arglist)
    set_c_double(target_lon, arglist)
    set_c_double(target_lat, arglist)
    set_c_int(nest_grid, arglist)
    set_c_int(parent_tile, arglist)
    set_c_int(refine_ratio, arglist)
    set_c_int(istart_nest, arglist)
    set_c_int(iend_nest, arglist)
    set_c_int(jstart_nest, arglist)
    set_c_int(jend_nest, arglist)
    set_c_int(halo, arglist)
    set_c_int(output_length_angle, arglist)

    _create_gnomonic_cubic_grid_GR.argtypes = [
        c_char_p,
        np.ctypeslib.ndpointer(dtype=nlon.dtype, ndim=nlon.ndim, shape=nlon.shape),
        np.ctypeslib.ndpointer(dtype=nlat.dtype, ndim=nlat.ndim, shape=nlat.shape),
        np.ctypeslib.ndpointer(dtype=x.dtype, ndim=x.ndim, shape=x.shape),
        np.ctypeslib.ndpointer(dtype=y.dtype, ndim=y.ndim, shape=y.shape),
        np.ctypeslib.ndpointer(dtype=dx.dtype, ndim=dx.ndim, shape=dx.shape),
        np.ctypeslib.ndpointer(dtype=dy.dtype, ndim=dy.ndim, shape=dy.shape),
        np.ctypeslib.ndpointer(dtype=area.dtype, ndim=area.ndim, shape=area.shape),
        np.ctypeslib.ndpointer(dtype=angle_dx.dtype, ndim=angle_dx.ndim, shape=angle_dx.shape),
        np.ctypeslib.ndpointer(dtype=angle_dy.dtype, ndim=angle_dy.ndim, shape=angle_dy.shape),
        c_double,
        c_int,
        c_int,
        c_double,
        c_double,
        c_double,
        c_int,
        c_int,
        c_int,
        c_int,
        c_int,
        c_int,
        c_int,
        c_int,
        c_int, 
    ]
    _create_gnomonic_cubic_grid_GR.restype = None

    _create_gnomonic_cubic_grid_GR(*arglist)
