import ctypes as ct
import numpy as np
import numpy.typing as npt
import xarray as xr
from dataclasses import dataclass

@dataclass
class CreateXgrid() :

    cFMS : ct.CDLL = None

    def __post_init__(self) :
        if self.cFMS is None : raise RunTimeError('cFMS library does not exist')


    def create_xgrid_2dx2d_order1(self,
                                  nlon_src : int = None, nlat_src : int = None,
                                  nlon_tgt : int = None, nlat_tgt : int = None,
                                  lon_src : npt.NDArray[np.float64] = None, lat_src : npt.NDArray[np.float64] = None,
                                  lon_tgt : npt.NDArray[np.float64] = None, lat_tgt : npt.NDArray[np.float64] = None,
                                  mask_src : npt.NDArray[np.float64] = None) \
                                  -> tuple[ npt.NDArray[np.int32], npt.NDArray[np.int32],
                                            npt.NDArray[np.int32], npt.NDArray[np.int32],
                                            npt.NDArray[np.float64]] :
        ngrid_src = nlon_src * nlat_src
        ngrid_tgt = nlon_tgt * nlat_tgt
        
        nlon_src_t, nlat_src_t = ct.c_int, ct.c_int
        nlon_tgt_t, nlat_tgt_t = ct.c_int, ct.c_int
        lon_src_ndp = np.ctypeslib.ndpointer(dtype=np.float64, shape=(ngrid_src), flags='C_CONTIGUOUS')
        lat_src_ndp = np.ctypeslib.ndpointer(dtype=np.float64, shape=(ngrid_src), flags='C_CONTIGUOUS')
        lon_tgt_ndp = np.ctypeslib.ndpointer(dtype=np.float64, shape=(ngrid_tgt), flags='C_CONTIGUOUS')
        lat_tgt_ndp = np.ctypeslib.ndpointer(dtype=np.float64, shape=(ngrid_tgt), flags='C_CONTIGUOUS')
        mask_src_ndp = np.ctypeslib.ndpointer(dtype=np.float64, shape=(ngrid_src), flags='C_CONTIGUOUS')
        i_src_ndp = np.ctypeslib.ndpointer(dtype=np.int32, shape=(200), flags='C_CONTIGUOUS')
        j_src_ndp = np.ctypeslib.ndpointer(dtype=np.int32, shape=(200), flags='C_CONTIGUOUS')
        i_tgt_ndp = np.ctypeslib.ndpointer(dtype=np.int32, shape=(200), flags='C_CONTIGUOUS')
        j_tgt_ndp = np.ctypeslib.ndpointer(dtype=np.int32, shape=(200), flags='C_CONTIGUOUS')
        xarea_ndp = np.ctypeslib.ndpointer(dtype=np.float64, shape=(200), flags='C_CONTIGUOUS')
        
        i_src_c = np.zeros(200, dtype=np.int32)
        j_src_c = np.zeros(200, dtype=np.int32)
        i_tgt_c = np.zeros(200, dtype=np.int32)
        j_tgt_c = np.zeros(200, dtype=np.int32)
        xarea_c = np.zeros(200, dtype=np.float64)
        
        self.cFMS.create_xgrid_2dx2d_order1.restype = ct.c_int
        
        self.cFMS.create_xgrid_2dx2d_order1.argtypes = [ ct.POINTER(nlon_src_t), ct.POINTER(nlat_src_t),
                                                         ct.POINTER(nlon_tgt_t), ct.POINTER(nlat_tgt_t),
                                                         lon_src_ndp, lat_src_ndp, lon_tgt_ndp, lat_tgt_ndp, mask_src_ndp,
                                                         i_src_ndp, j_src_ndp, i_tgt_ndp, j_tgt_ndp, xarea_ndp]

        nlon_src_c = ct.byref(nlon_src_t(nlon_src))
        nlat_src_c = ct.byref(nlat_src_t(nlat_src))
        nlon_tgt_c = ct.byref(nlon_tgt_t(nlon_tgt))
        nlat_tgt_c = ct.byref(nlat_tgt_t(nlat_tgt))        
        
        nxgrid = self.cFMS.create_xgrid_2dx2d_order1(nlon_src_c, nlat_src_c, nlon_tgt_c, nlat_tgt_c,
                                                     lon_src, lat_src, lon_tgt, lat_tgt, mask_src,
                                                     i_src_c, j_src_c, i_tgt_c, j_tgt_c, xarea_c)
        
fmslib = ct.cdll.LoadLibrary("./FMS/LIBFMS/lib/libFMS.so")
mytest = CreateXgrid(fmslib)

[nlon_src, nlat_src, nlon_tgt, nlat_tgt]  = [5] * 4

lon_src = np.array( [2.0*np.pi/5.0*i for i in range(5)]*5, dtype=np.float64)
lat_src = np.array( [-np.pi/2.0  + np.pi/5*i for i in range(5)]*5, dtype=np.float64)
lon_tgt, lat_tgt = lon_src, lat_src
mask_src = np.array([1.0]*nlon_src*nlat_src, dtype=np.float64)

mytest.create_xgrid_2dx2d_order1(nlon_src=nlon_src, nlat_src=nlat_src, nlon_tgt=nlon_tgt, nlat_tgt=nlat_tgt,
                                 lon_src=lon_src, lat_src=lat_src, lon_tgt=lon_tgt, lat_tgt=lat_tgt, mask_src=mask_src)

    


