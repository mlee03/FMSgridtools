import os

import numpy as np
import pytest
import xarray as xr

import FMSgridtools


def generate_mosaic(nx: int = 90, ny: int = 45, refine: int = 2):

    xstart, xend = 0, 360
    ystart, yend = -45, 45

    x_src = np.linspace(xstart, xend, nx+1)
    y_src = np.linspace(ystart, yend, ny+1)
    x_src, y_src = np.meshgrid(x_src, y_src)

    x_tgt = np.linspace(xstart, xend, nx*refine+1)
    y_tgt = np.linspace(ystart, yend, ny*refine+1)
    x_tgt, y_tgt = np.meshgrid(x_tgt, y_tgt)

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

def remove_mosaic():
    os.remove("src_grid.nc")
    os.remove("tgt_grid.nc")
    os.remove("src_mosaic.nc")
    os.remove("tgt_mosaic.nc")
    os.remove("remap.nc")

@pytest.mark.parametrize("on_gpu", [False, True])
def test_create_xgrid(on_gpu) :

    nx, ny, refine = 45, 45, 2
    generate_mosaic(nx=nx, ny=ny, refine=refine)

    xgrid = FMSgridtools.XGridObj(src_mosaic="src_mosaic.nc",
                                  tgt_mosaic="tgt_mosaic.nc",
                                  on_gpu=on_gpu
    )

    xgrid.create_xgrid()
    xgrid.write()

    del xgrid

    xgrid = FMSgridtools.XGridObj(restart_remap_file="remap.nc")

    nxcells = nx * refine * ny * refine
    assert xgrid.nxcells == nxcells

    tile1_cells = np.repeat([i for i in range(nx*ny)],4)
    assert np.all(xgrid.src_ij==tile1_cells)

    tile2_cells = []
    for j in range(ny):
        for i in range(nx):
            base = (refine*j)*(refine*nx) + refine*i
            tile2_cells.extend([base, base+1, base+refine*nx, base+refine*nx+1])
    assert np.all(xgrid.tgt_ij==np.array(tile2_cells))

    remove_mosaic()
