import ctypes
import numpy as np
from typing import type, List
import xarray as xr

from fmsgridtools.shared.mosaicobj import MosaicObj

_libpath = None
_lib = None

def init(libpath: str, lib: type[CDLL]):

    global _libpath, _lib

    _libpath = libpath
    _lib = lib


class AtmComponent(ctypes.Structure): pass
class LndComponent(ctypes.Structure): pass
class OcnComponent(ctypes.Structure): pass

def set_component(mosaic: type[MosaicObj], Component: Union[type[AtmComponent], type[LndComponent], type[OcnComponent]],
                  mask: List[npt.NDArray[np.float64]] = None, area: List[npt.NDArray[np.float64]] = None):    
    
    Component._fields_ = [("itile", ctypes.c_int),
                          ("nx",  ctypes.c_int),
                          ("ny", ctypes.c_int),
                          ("x", ctypes.POINTER(ctypes.c_double)),
                          ("y", ctypes.POINTER(ctypes.c_double)),
                          ("mask", ctypes.POINTER(ctypes.c_double)),
                          ("area", ctypes.POINTER(ctypes.c_double))
    ]
    
    componentsxntiles = Component * mosaic.ntiles
    components = componentsxntiles()
        
    for itile in range(mosaic.ntiles):
        tile = mosaic.gridtiles[itile]
        igrid = mosaic.grid[tile]
        components[itile].itile = itile
        components[itile].nx = igrid.nx
        components[itile].ny = igrid.ny
        components[itile].x = igrid.x.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        components[itile].y = igrid.y.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        components[itile].area = area if area is None else area[itile].ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        thismask = np.ones(igrid.nx*igrid.ny, dtype=np.float64) if mask is None else mask[itile]
        components[itile].mask = thismask.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        
    return components, componentsxntiles


def extend_ocn_grid_south(ocn_mosaic: MosaicObj):

    tiny_value = 1.e-7
    min_atm_lat = np.radians(-90.0)
    
    if ocn_mosaic.grid['tile1'].y[0][0] > min_atm_lat + tiny_value:
        #extend
        for itile in ocn_mosaic.gridtiles:
            x = ocn_mosaic.grid[itile].x
            ocn_mosaic.grid[itile].x = np.concatenate(([x[0]], x))
            
            nxp = ocn_mosaic.grid[itile].nxp
            y = ocn_mosaic.grid[itile].y
            ocn_mosaic.grid[itile].y = np.concatenate(([np.full(nxp, min_atm_lat, dtype=np.float64)], y))
        ocn_mosaic.grid['tile1'].ny = ocn_mosaic.grid['tile1'].ny + 1
        ocn_mosaic.extended_south = 1
    else:
        ocn_mosaic.extended_south = 0


def get_ocn_mask(ocn_mosaic: type(MosaicObj), topog_file: str = None, sea_level: np.float64 = 0.0):

    nx = ocn_mosaic.grid['tile1'].nx 
    ny = ocn_mosaic.grid['tile1'].ny
    
    if topog_file is None:
        return np.ones((ny,nx), dtype=np.float64)
    else:
        topog = xr.load_dataset(topog_file)['depth'].values
        mask = np.where(topog>sea_level, 1.0, 0.0)
        if ocn_mosaic.extended_south > 0 :
            return np.concatenate(([np.zeros(nx)], mask))
        else :
            return mask

        
def make_coupler_mosaic(atm: type(MosaicObj), lnd: type(MosaicObj), ocn: type(MosaicObj), topogfile: str = None):

    atm, atm_argtype = set_component(mosaic=atm_mosaic, Component=AtmComponent)
    lnd, lnd_argtype = set_component(mosaic=lnd_mosaic, Component=LndComponent)

    extend_grid_south(ocn_mosaic)
    ocn_mask = [get_ocn_mask(ocn_mosaic, topogfile)]
    ocn, ocn_argtype = set_component(mosaic=ocn_mosaic, Component=OcnComponent, mask = ocn_mask)

    _lib.make_coupler_mosaic.restype = ctypes.c_int
    _lib.make_coupler_mosaic.argtypes = [ctypes.c_int, #ntile_atm
                                         ctypes.c_int, #ntile_lnd
                                         ctypes.c_int, #ntile_ocn
                                         ctypes.c_int, #ocn_south_ext
                                         ctypes.POINTER(atm_argtype), #lnd
                                         ctypes.POINTER(lnd_argtype), #lnd
                                         ctypes.POINTER(ocn_argtype),  #ocn
                                         ctypes.POINTER(atmxlnd), #atmxlnd exchange grid
                                         ctypes.POINTER(atmxocn)]  #atmxocn exchange grid

    _lib.make_coupler_mosaic(atm_mosaic.ntiles,
                             lnd_mosaic.ntiles,
                             ocn_mosaic.ntiles,
                             ocn_mosaic.extended_south,
                             ctypes.byref(atm),
                             ctypes.byref(lnd),
                             ctypes.byref(ocn)
    

    

