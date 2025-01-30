import pytest
import xarray as xr
import numpy as np
import pyfrenctools

def test_create_xgrid():

    cFMS_so = "/home/Mikyung.Lee/FMSgridtools-development/FMS/LIBFMS/lib/libFMS.so"
    frenctools = pyfrenctools.FRENCToolsObj(cFMS_so=cFMS_so)

    refine = 2
    lon_init = 0.
    lat_init = -np.pi/2.0      
    nlon_src = 10
    nlat_src = 10
    nlon_tgt = nlon_src*refine
    nlat_tgt = nlat_src*refine
    dlon_src = np.pi/nlon_src
    dlat_src = np.pi/nlat_src
    dlon_tgt = dlon_src/refine
    dlat_tgt = dlat_src/refine
        
    lon_src = np.array(
        [lon_init + (dlon_src*i) for i in range(nlon_src)]*nlat_src,
        dtype=np.float64
    )
    lat_src = np.array(
        [lat_init + (dlat_src*i) for i in range(nlat_src) for j in range(nlon_src)],
        dtype=np.float64
    )
    lon_tgt = np.array(
        [lon_init + (dlon_tgt*i) for i in range(nlon_tgt)]*nlat_tgt,
        dtype=np.float64
    )
    lat_tgt = np.array(
        [lat_init + (dlat_tgt*i) for i in range(nlat_tgt) for j in range(nlon_tgt)],
        dtype=np.float64
    )
    mask_src = np.ones(nlon_src*nlat_src, dtype=np.float64)

    print(frenctools.xgrid)
    
    #frenctools.xgrid.create_xgrid_2dx2d_order1(nlon_src=nlon_src,
    #                                           nlat_src=nlat_src,
    #                                           nlon_tgt=nlon_tgt,
    #                                           nlat_tgt=nlat_tgt,
    #                                           lon_src=lon_src,
    #                                           lat_src=lat_src,
    #                                           lon_tgt=lon_tgt,
    #                                           lat_tgt=lat_tgt,
    #                                           mask_src=mask_src)

test_create_xgrid()
