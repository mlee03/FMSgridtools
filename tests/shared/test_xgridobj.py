import numpy as np
import os
import xarray as xr

import FMSgridtools

def generate_mosaic(nx: int = 360, ny:int = 90, refine: int = 1):

    xstart, xend = 0, 360
    ystart, yend = -45, 45
    nx_src, ny_src = nx, ny
    nxp_src, nyp_src = nx_src+1, ny_src+1
    dx_src = (xend-xstart)/(nxp_src-1)
    dy_src = (yend-ystart)/(nyp_src-1)

    nx_tgt, ny_tgt = nx_src*refine, ny_src*refine
    nxp_tgt, nyp_tgt = nx_tgt+1, ny_tgt+1
    dx_tgt = dx_src/refine
    dy_tgt = dy_src/refine
    
    x_src, y_src = [], []
    for j in range(nyp_src):
        x_src.append([xstart+i*dx_src for i in range(nxp_src)])
        y_src.append([ystart+j*dy_src]*nxp_src)

    x_tgt, y_tgt = [], []
    for j in range(nyp_tgt):
        x_tgt.append([xstart+i*dx_tgt for i in range(nxp_tgt)])
        y_tgt.append([ystart+j*dy_tgt]*nxp_tgt)

    for ifile in ("src", "tgt"):
        mosaicfile = ifile + "_mosaic.nc"
        gridfile = ifile + "_grid.nc"
        gridlocation = "./"
        gridtile = "tile1"
        xr.Dataset(data_vars=dict(mosaic=mosaicfile.encode(),
                                  gridlocation=gridlocation.encode(),
                                  gridfiles=(["ntiles"], [gridfile.encode()]),
                                  gridtiles=(["ntiles"], [gridtile.encode()]))
        ).to_netcdf(mosaicfile)
        

    for (x, y, prefix) in [(x_src, y_src, "src"), (x_tgt, y_tgt, "tgt")]:                                                 
        xr.Dataset(data_vars=dict(x=(["nyp", "nxp"], x),
                                  y=(["nyp", "nxp"], y))
        ).to_netcdf(prefix+"_grid.nc")

        
def test_create_xgrid() :

    nx, ny, refine = 180, 45, 2
    generate_mosaic(nx=nx, ny=ny, refine=refine)

    xgrid = FMSgridtools.XGridObj(src_mosaic="src_mosaic.nc", tgt_mosaic="tgt_mosaic.nc")
    xgrid.create_xgrid()
    xgrid.write()
    
    del xgrid
    
    xgrid = FMSgridtools.XGridObj(restart_remap_file="remap.nc").dataset

    nxgrid = nx * refine * ny * refine 
    assert(xgrid.sizes["nxcells"] == nxgrid)    

    tile1_cells = np.repeat([i for i in range(nx*ny)],4)
    assert(np.all(xgrid["src_ij"].values==tile1_cells))

    tile2_cells = []
    for j in range(ny):
        for i in range(nx):
            base = (refine*j)*(refine*nx) + refine*i
            tile2_cells.extend([base, base+1, base+refine*nx, base+refine*nx+1])
    assert(np.all(xgrid["tgt_ij"].values==np.array(tile2_cells)))
