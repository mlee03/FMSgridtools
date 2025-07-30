from ctypes import CDLL, POINTER, c_double, c_int

import numpy as np
import numpy.typing as npt
import xarray as xr


_libpath = None
_lib = None

MAXXGRID = 10**6

def init(libpath: str, lib: type[CDLL]):

    global _libpath, _lib

    _libpath = libpath
    _lib = lib


def get_2dx2d_order1(src_nlon: int,
                     src_nlat: int,
                     tgt_nlon: int,
                     tgt_nlat: int,
                     src_lon: npt.NDArray[np.float64],
                     src_lat: npt.NDArray[np.float64],
                     tgt_lon: npt.NDArray[np.float64],
                     tgt_lat: npt.NDArray[np.float64],
                     src_mask: npt.NDArray[np.float64] = None,
                     tgt_mask: npt.NDArray[np.float64] = None):

    create_xgrid = _lib.create_xgrid_2dx2d_order1

    if src_mask is None: src_mask = np.ones((src_nlon*src_nlat), dtype=np.float64)
    if tgt_mask is None: tgt_mask = np.ones((tgt_nlon*tgt_nlat), dtype=np.float64)

    src_i = np.zeros(MAXXGRID, dtype=np.int32)
    src_j = np.zeros(MAXXGRID, dtype=np.int32)
    tgt_i = np.zeros(MAXXGRID, dtype=np.int32)
    tgt_j = np.zeros(MAXXGRID, dtype=np.int32)
    xarea = np.zeros(MAXXGRID, dtype=np.float64)

    arrayptr_int = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
    arrayptr_double = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")

    create_xgrid.restype = c_int
    create_xgrid.argtypes = [POINTER(c_int), #nlon_in
                             POINTER(c_int), #nlat_in
                             POINTER(c_int), #nlon_out
                             POINTER(c_int), #nlat_out
                             arrayptr_double, #lon_in
                             arrayptr_double, #lat_in
                             arrayptr_double, #lon_out
                             arrayptr_double, #lat_out
                             arrayptr_double, #src_mask
                             arrayptr_double, #tgt_mask
                             arrayptr_int, #i_in
                             arrayptr_int, #j_in
                             arrayptr_int, #i_out
                             arrayptr_int, #j_out
                             arrayptr_double] #xarea

    nxcells = create_xgrid(c_int(src_nlon), c_int(src_nlat),
                           c_int(tgt_nlon), c_int(tgt_nlat),
                           src_lon, src_lat, tgt_lon, tgt_lat, src_mask,
                           tgt_mask, src_i, src_j, tgt_i, tgt_j, xarea
    )
    
    return dict(nxcells=nxcells,
                src_i=src_i[:nxcells],
                src_j=src_j[:nxcells],
                tgt_i=tgt_i[:nxcells],
                tgt_j=tgt_j[:nxcells],
                xarea=xarea[:nxcells])


def transfer_data_gpu(nxcells: int, src_nlon: int, tgt_nlon: int):

    create_xgrid_transfer_data = _lib.create_xgrid_transfer_data

    arrayptr_int = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
    arrayptr_double = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")

    create_xgrid_transfer_data.restype = None
    create_xgrid_transfer_data.argtypes = [c_int,
                                           c_int,
                                           c_int,
                                           arrayptr_int,
                                           arrayptr_int,
                                           arrayptr_int,
                                           arrayptr_int, 
                                           arrayptr_double]

    src_i = np.zeros((nxcells), dtype=np.int32)
    src_j = np.zeros((nxcells), dtype=np.int32)
    tgt_i = np.zeros((nxcells), dtype=np.int32)
    tgt_j = np.zeros((nxcells), dtype=np.int32)
    xarea = np.zeros((nxcells), dtype=np.float64)    

    create_xgrid_transfer_data(c_int(nxcells), c_int(src_nlon), c_int(tgt_nlon),
                               src_i, src_j, tgt_i, tgt_j, xarea)

    return dict(nxcells=nxcells,
                src_i=src_i[:nxcells],
                src_j=src_j[:nxcells],
                tgt_i=tgt_i[:nxcells],
                tgt_j=tgt_j[:nxcells],
                xarea=xarea[:nxcells])


def get_2dx2d_order1_gpu(src_nlon: int,
                         src_nlat: int,
                         tgt_nlon: int,
                         tgt_nlat: int,
                         src_lon: npt.NDArray,
                         src_lat: npt.NDArray,
                         tgt_lon: npt.NDArray,
                         tgt_lat: npt.NDArray,
                         src_mask: npt.NDArray[np.float64] = None,
                         tgt_mask: npt.NDArray[np.float64] = None):

    create_xgrid_order1_gpu_wrapper = _lib.create_xgrid_order1_gpu_wrapper

    if src_mask is None: src_mask = np.ones((src_nlon*src_nlat), dtype=np.float64)
    if tgt_mask is None: tgt_mask = np.ones((tgt_nlon*tgt_nlat), dtype=np.float64)

    arrayptr_double = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")

    create_xgrid_order1_gpu_wrapper.restype = np.int32
    create_xgrid_order1_gpu_wrapper.argtypes = [c_int, #src_nlon
                                                c_int, #src_nlat
                                                c_int, #tgt_nlon
                                                c_int, #tgt_nlat
                                                arrayptr_double, #src_lon
                                                arrayptr_double, #src_lat
                                                arrayptr_double, #tgt_lon
                                                arrayptr_double, #tgt_lat
                                                arrayptr_double, #src_mask
                                                arrayptr_double] #tgt_mask

    nxcells = create_xgrid_order1_gpu_wrapper(c_int(src_nlon), c_int(src_nlat),
                                              c_int(tgt_nlon), c_int(tgt_nlat),
                                              src_lon, src_lat, tgt_lon, tgt_lat,
                                              src_mask, tgt_mask)
    
    return transfer_data_gpu(nxcells, src_nlon, tgt_nlon)
