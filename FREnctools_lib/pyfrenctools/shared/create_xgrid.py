from ctypes import CDLL, POINTER, c_double, c_int

import numpy as np
import numpy.typing as npt


_libpath = None
_lib = None

MAXXGRID = 10**6

def init(libpath: str, lib: type[CDLL]):

    global _libpath, _lib

    _libpath = libpath
    _lib = lib


def get_2dx2d_order1(nlon_src: int,
                     nlat_src: int,
                     nlon_tgt: int,
                     nlat_tgt: int,
                     lon_src: npt.NDArray[np.float64],
                     lat_src: npt.NDArray[np.float64],
                     lon_tgt: npt.NDArray[np.float64],
                     lat_tgt: npt.NDArray[np.float64],
                     mask_src: npt.NDArray[np.float64] = None,
                     mask_tgt: npt.NDArray[np.float64] = None):

    create_xgrid = _lib.create_xgrid_2dx2d_order1

    if mask_src is None: mask_src = np.ones((nlon_src*nlat_src), dtype=np.float64)
    if mask_tgt is None: mask_tgt = np.ones((nlon_src*nlat_src), dtype=np.float64)

    i_src = np.zeros(MAXXGRID, dtype=np.int32)
    j_src = np.zeros(MAXXGRID, dtype=np.int32)
    i_tgt = np.zeros(MAXXGRID, dtype=np.int32)
    j_tgt = np.zeros(MAXXGRID, dtype=np.int32)
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
                             arrayptr_double, #mask_src
                             arrayptr_double, #mask_tgt
                             arrayptr_int, #i_in
                             arrayptr_int, #j_in
                             arrayptr_int, #i_out
                             arrayptr_int, #j_out
                             arrayptr_double] #xarea

    nxcells = create_xgrid(c_int(nlon_src), c_int(nlat_src),
                           c_int(nlon_tgt), c_int(nlat_tgt),
                           lon_src, lat_src, lon_tgt, lat_tgt, mask_src,
                           mask_tgt, i_src, j_src, i_tgt, j_tgt, xarea
    )

    return dict(nxcells=nxcells,
                src_ij=j_src[:nxcells]*nlon_src + i_src[:nxcells],
                tgt_ij=j_tgt[:nxcells]*nlon_tgt + i_tgt[:nxcells],
                xarea=xarea[:nxcells]
    )


def transfer_data_gpu(nxcells: int):

    create_xgrid_transfer_data = _lib.create_xgrid_transfer_data

    arrayptr_int = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
    arrayptr_double = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")

    create_xgrid_transfer_data.restype = None
    create_xgrid_transfer_data.argtypes = [c_int,
                                           arrayptr_int,
                                           arrayptr_int,
                                           arrayptr_double]

    src_ij = np.ascontiguousarray(np.zeros((nxcells), dtype=np.int32))
    tgt_ij = np.ascontiguousarray(np.zeros((nxcells), dtype=np.int32))
    xarea = np.ascontiguousarray(np.zeros((nxcells), dtype=np.float64))

    create_xgrid_transfer_data(c_int(nxcells), src_ij, tgt_ij, xarea)

    return dict(src_ij=src_ij,
                tgt_ij=tgt_ij,
                xarea=xarea,
                nxcells=nxcells)

def get_2dx2d_order1_gpu(nlon_src: int,
                         nlat_src: int,
                         nlon_tgt: int,
                         nlat_tgt: int,
                         lon_src: npt.NDArray,
                         lat_src: npt.NDArray,
                         lon_tgt: npt.NDArray,
                         lat_tgt: npt.NDArray,
                         mask_src: npt.NDArray[np.float64] = None,
                         mask_tgt: npt.NDArray[np.float64] = None):

    create_xgrid_order1_gpu_wrapper = _lib.create_xgrid_order1_gpu_wrapper

    if mask_src is None: mask_src = np.ones((nlon_src*nlat_src), dtype=np.float64)
    if mask_tgt is None: mask_tgt = np.ones((nlon_src*nlat_src), dtype=np.float64)

    arrayptr_double = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")

    create_xgrid_order1_gpu_wrapper.restype = np.int32
    create_xgrid_order1_gpu_wrapper.argtypes = [c_int, #nlon_src
                                                c_int, #nlat_src
                                                c_int, #nlon_tgt
                                                c_int, #nat_tgt
                                                arrayptr_double, #lon_src
                                                arrayptr_double, #lat_src
                                                arrayptr_double, #lon_tgt
                                                arrayptr_double, #lat_tgt
                                                arrayptr_double, #mask_src
                                                arrayptr_double] #mask_tgt

    nxcells = create_xgrid_order1_gpu_wrapper(c_int(nlon_src), c_int(nlat_src),
                                              c_int(nlon_tgt), c_int(nlat_tgt),
                                              lon_src, lat_src, lon_tgt, lat_tgt,
                                              mask_src, mask_tgt)
    
    return transfer_data_gpu(nxcells)
