import numpy as np
import pyfrenctools

def test_create_xgrid_gpu():

    cfrenctools = pyfrenctools.cfrenctools.LIB().lib

    nlon_src = 180
    nlat_src = 90
    nlon_tgt = nlon_src
    nlat_tgt = nlat_src

    lon_src, lat_src = [], []
    for i in range(nlat_src+1) : lon_src.extend([j for j in range(nlon_src+1)])
    for i in range(nlat_src+1) : lat_src.extend([-45+i]*(nlon_src+1))

    lon_src = np.deg2rad(np.array(lon_src, dtype=np.float64))
    lat_src = np.deg2rad(np.array(lat_src, dtype=np.float64))
    lon_tgt = lon_src
    lat_tgt = lat_src

    create_xgrid = pyfrenctools.CreateXgrid(cfrenctools)
    
    results = create_xgrid.get_2dx2d_order1_gpu(nlon_src, nlat_src, nlon_tgt, nlat_tgt,
                                                lon_src, lat_src, lon_tgt, lat_tgt)


    assert(results["nxgrid"]==nlon_src*nlat_src)
    assert(np.all(results["xgrid_ij1"]==results["xgrid_ij2"]))    

test_create_xgrid_gpu()
