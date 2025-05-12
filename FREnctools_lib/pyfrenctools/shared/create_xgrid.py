from ctypes import c_int, c_double, POINTER, CDLL
import numpy.typing as npt
import numpy as np

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
                     mask_src: npt.NDArray[np.float64] = None):
    
    create_xgrid = _lib.create_xgrid_2dx2d_order1
    
    ngrid_src = (nlon_src+1)*(nlat_src+1)
    ngrid_tgt = (nlon_tgt+1)*(nlat_tgt+1)
    nlon_src_t = c_int
    nlat_src_t = c_int
    nlon_tgt_t = c_int
    nlat_tgt_t = c_int
    
    if mask_src is None: mask_src = np.ones((nlon_src*nlat_src), dtype=np.float64)
    i_src = np.zeros(MAXXGRID, dtype=np.int32)
    j_src = np.zeros(MAXXGRID, dtype=np.int32)
    i_tgt = np.zeros(MAXXGRID, dtype=np.int32)
    j_tgt = np.zeros(MAXXGRID, dtype=np.int32)
    xarea = np.zeros(MAXXGRID, dtype=np.float64)

    C = "C_CONTIGUOUS"
    create_xgrid.restype = c_int        
    create_xgrid.argtypes = [POINTER(nlon_src_t),
                             POINTER(nlat_src_t),
                             POINTER(nlon_tgt_t),
                             POINTER(nlat_tgt_t),
                             np.ctypeslib.ndpointer(dtype=np.float64, flags=C),
                             np.ctypeslib.ndpointer(dtype=np.float64, flags=C),
                             np.ctypeslib.ndpointer(dtype=np.float64, flags=C),
                             np.ctypeslib.ndpointer(dtype=np.float64, flags=C),
                             np.ctypeslib.ndpointer(dtype=np.float64, flags=C),
                             np.ctypeslib.ndpointer(dtype=np.int32, flags=C),
                             np.ctypeslib.ndpointer(dtype=np.int32, flags=C),
                             np.ctypeslib.ndpointer(dtype=np.int32, flags=C),
                             np.ctypeslib.ndpointer(dtype=np.int32, flags=C),
                             np.ctypeslib.ndpointer(dtype=np.float64, flags=C)]    
        
    nlon_src_c = nlon_src_t(nlon_src)
    nlat_src_c = nlat_src_t(nlat_src)
    nlon_tgt_c = nlon_tgt_t(nlon_tgt)
    nlat_tgt_c = nlat_tgt_t(nlat_tgt)
    nxcells = create_xgrid(nlon_src_c, nlat_src_c, nlon_tgt_c, nlat_tgt_c,
                           lon_src, lat_src, lon_tgt, lat_tgt, mask_src,
                           i_src, j_src, i_tgt, j_tgt, xarea)
    
    return dict(nxcells=nxcells,
                src_ij=j_src[:nxcells]*nlon_src + i_src[:nxcells],
                tgt_ij=j_tgt[:nxcells]*nlon_tgt + i_tgt[:nxcells],
                xarea=xarea[:nxcells])
                    

def transfer_data_gpu(nxcells: int):

    _create_xgrid_transfer_data = _lib.create_xgrid_transfer_data
    
    nxcells_t = c_int
    src_ij_t = np.ctypeslib.ndpointer(dtype=np.int32, shape=(nxcells))
    tgt_ij_t = np.ctypeslib.ndpointer(dtype=np.int32, shape=(nxcells))
    xarea_t = np.ctypeslib.ndpointer(dtype=np.float64, shape=(nxcells))
    
    _create_xgrid_transfer_data.restype = None
    _create_xgrid_transfer_data.argtypes = [nxcells_t,
                                            src_ij_t,
                                            tgt_ij_t,
                                            xarea_t]
    
    nxcells_c = nxcells_t(nxcells)
    src_ij = np.zeros((nxcells), dtype=np.int32)
    tgt_ij = np.zeros((nxcells), dtype=np.int32)
    xarea = np.zeros((nxcells), dtype=np.float64)
    
    _create_xgrid_transfer_data(nxcells, src_ij, tgt_ij, xarea)
    
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
                         mask_src: npt.NDArray[np.float64] = None):
    
    _create_xgrid_order1_gpu_wrapper = _lib.create_xgrid_order1_gpu_wrapper
    
    ngrid_src = (nlon_src+1)*(nlat_src+1)
    ngrid_tgt = (nlon_tgt+1)*(nlat_tgt+1)
    
    nlon_src_t = c_int
    nlat_src_t = c_int
    nlon_tgt_t = c_int
    nlat_tgt_t = c_int
    lon_src_t = np.ctypeslib.ndpointer(dtype=np.float64, shape=(ngrid_src), flags="C_CONTIGUOUS")
    lat_src_t = np.ctypeslib.ndpointer(dtype=np.float64, shape=(ngrid_src), flags="C_CONTIGUOUS")
    lon_tgt_t = np.ctypeslib.ndpointer(dtype=np.float64, shape=(ngrid_tgt), flags="C_CONTIGUOUS")
    lat_tgt_t = np.ctypeslib.ndpointer(dtype=np.float64, shape=(ngrid_tgt), flags="C_CONTIGUOUS")
    mask_t = np.ctypeslib.ndpointer(dtype=np.float64, shape=(nlon_src*nlat_src), flags="C_CONTIGUOUS")
    
    nlon_src_c = nlon_src_t(nlon_src)
    nlat_src_c = nlat_src_t(nlat_src)
    nlon_tgt_c = nlon_tgt_t(nlon_tgt)
    nlat_tgt_c = nlat_tgt_t(nlat_tgt)
    
    if mask_src is None: mask_src = np.ones((nlon_src*nlat_src), dtype=np.float64)
    
    _create_xgrid_order1_gpu_wrapper.restype = np.int32
    _create_xgrid_order1_gpu_wrapper.argtypes = [nlon_src_t,
                                                 nlat_src_t,
                                                 nlon_tgt_t,
                                                 nlat_tgt_t,
                                                 lon_src_t,
                                                 lat_src_t,
                                                 lon_tgt_t,
                                                 lat_tgt_t,
                                                 mask_t]
    
    nxcells = _create_xgrid_order1_gpu_wrapper(nlon_src_c, nlat_src_c,
                                               nlon_tgt_c, nlat_tgt_c,
                                               lon_src, lat_src,
                                               lon_tgt, lat_tgt, mask_src)
    
    return transfer_data_gpu(nxcells)
    

        
