from ctypes import POINTER, c_int, CDLL
import numpy as np
import numpy.typing as npt

_libpath = None
_lib = None

def init(libpath: str, lib: type[CDLL]):

    global _libpath, _lib

    _libpath = libpath
    _lib = lib


def get_grid_area(lon: npt.NDArray[np.float64],
                  lat: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    
    """
    Returns the cell areas of grids defined
    on lon and lat
    """

    _get_grid_area = _lib.get_grid_area

    _get_grid_area.argtypes = [POINTER(c_int), #nlon
                               POINTER(c_int), #nlat
                               np.ctypeslib.ndpointer(dtype=np.float64), #lon
                               np.ctypeslib.ndpointer(dtype=np.float64), #lat
                               np.ctypeslib.ndpointer(dtype=np.float64)] #area

    nlat, nlon = lon.shape 
    nlat, nlon = nlat-1, nlon-1
    area = np.zeros(nlon * nlat, dtype=np.float64)
    
    _get_grid_area(c_int(nlon), c_int(nlat), lon, lat, area)

    return area




