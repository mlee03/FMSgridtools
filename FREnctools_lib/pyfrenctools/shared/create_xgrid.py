import ctypes
import numpy.typing as npt
import numpy as np

class CreateXgrid():

    def __init__(self, clib: ctypes.CDLL =  None):
        self.clib = clib

    def create_xgrid_transfer_data(self, nxgrid: int):

        _create_xgrid_transfer_data = self.clib.create_xgrid_transfer_data

        nxgrid_t = ctypes.c_int
        xgrid_ij1_t = np.ctypeslib.ndpointer(dtype=np.int32, shape=(nxgrid))
        xgrid_ij2_t = np.ctypeslib.ndpointer(dtype=np.int32, shape=(nxgrid))
        xgrid_area_t = np.ctypeslib.ndpointer(dtype=np.float64, shape=(nxgrid))
        
        _create_xgrid_transfer_data.restype = None
        _create_xgrid_transfer_data.argtypes = [nxgrid_t,
                                                xgrid_ij1_t,
                                                xgrid_ij2_t,
                                                xgrid_area_t]

        nxgrid_c = nxgrid_t(nxgrid)
        xgrid_ij1 = np.zeros((nxgrid), dtype=np.int32)
        xgrid_ij2 = np.zeros((nxgrid), dtype=np.int32)
        xgrid_area = np.zeros((nxgrid), dtype=np.float64)

        _create_xgrid_transfer_data(nxgrid, xgrid_ij1, xgrid_ij2, xgrid_area)

        return dict(xgrid_ij1=xgrid_ij1,
                    xgrid_ij2=xgrid_ij2,
                    xgrid_area=xgrid_area,
                    nxgrid=nxgrid)
        
    def get_2dx2d_order1_gpu(self,
                             nlon_src: int,
                             nlat_src: int,
                             nlon_tgt: int,
                             nlat_tgt: int,
                             lon_src: npt.NDArray,
                             lat_src: npt.NDArray,
                             lon_tgt: npt.NDArray,
                             lat_tgt: npt.NDArray,
                             mask_src: npt.NDArray[np.float64] = None):

        _create_xgrid_order1_gpu_wrapper = self.clib.create_xgrid_order1_gpu_wrapper

        ngrid_src = (nlon_src+1)*(nlat_src+1)
        ngrid_tgt = (nlon_tgt+1)*(nlat_tgt+1)
        
        nlon_src_t = ctypes.c_int
        nlat_src_t = ctypes.c_int
        nlon_tgt_t = ctypes.c_int
        nlat_tgt_t = ctypes.c_int
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
    
        nxgrid = _create_xgrid_order1_gpu_wrapper(nlon_src_c, nlat_src_c,
                                                  nlon_tgt_c, nlat_tgt_c,
                                                  lon_src, lat_src,
                                                  lon_tgt, lat_tgt, mask_src)
        
        return self.create_xgrid_transfer_data(nxgrid)
    

        
