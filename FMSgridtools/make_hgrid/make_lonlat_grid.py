import numpy as np
import ctypes

from FMSgridtools.make_hgrid.hgridobj import HGridObj
from FMSgridtools.make_hgrid.make_hgrid_util import make_grid_info, grid_writer
import pyfrenctools

def make_lonlat_grid(
        nlon: int, 
        nlat: int, 
        xbnds: str = None,
        ybnds: str = None,
        dlon: str = None,
        dlat: str = None, 
        use_great_circle_algorithm: bool = False
):
    center = "none"
    grid_obj = HGridObj()
    
    if nlon is not None:
        nlon = np.fromstring(nlon, dtype=np.int32, sep=',')

    if nlat is not None:
        nlat = np.fromstring(nlat, dtype=np.int32, sep=',')

    if xbnds is not None:
        xbnds = np.fromstring(xbnds, dtype=np.float64, sep=',')
        nxbnds = xbnds.size
    else:
        xbnds = np.empty(shape=100, dtype=np.float64)
    
    if ybnds is not None:
        ybnds = np.fromstring(ybnds, dtype=np.float64, sep=',')
        nybnds = ybnds.size
    else:
        ybnds = np.empty(shape=100, dtype=np.float64)

    if dlon is not None:
        dx_bnds = np.fromstring(dlon, dtype=np.float64, sep=',')
    else:
        dx_bnds = np.zeros(shape=100, dtype=np.float64)
        
    if dlat is not None:
        dy_bnds = np.fromstring(dlat, dtype=np.float64, sep=',')
    else:
        dy_bnds = np.zeros(shape=100, dtype=np.float64)

    grid_info_dict = make_grid_info(
        grid_obj=grid_obj,
        nxbnds=nxbnds,
        nybnds=nybnds,
        nlon=nlon,
        nlat=nlat,
    )
    
    pyfrenctools.make_hgrid_wrappers.create_regular_lonlat_grid(
        nxbnds=nxbnds, 
        nybnds=nybnds, 
        xbnds=xbnds, 
        ybnds=ybnds, 
        nlon=nlon, 
        nlat=nlat, 
        dx_bnds=dx_bnds, 
        dy_bnds=dy_bnds, 
        isc=grid_info_dict['isc'], 
        iec=grid_info_dict['iec'], 
        jsc=grid_info_dict['jsc'], 
        jec=grid_info_dict['jec'], 
        x=grid_obj.x, 
        y=grid_obj.y, 
        dx=grid_obj.dx, 
        dy=grid_obj.dy, 
        area=grid_obj.area,
        angle_dx=grid_obj.angle_dx, 
        center=center,
        use_great_circle_algorithm=use_great_circle_algorithm,
    )

    grid_writer(
        grid_obj=grid_obj,
        info_dict=grid_info_dict,
    )


    

