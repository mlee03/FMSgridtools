import os

import numpy as np
import pytest
import xarray as xr

import fmsgridtools


def generate_mosaic(nx: int = 90, ny: int = 45, refine: int = 2):

    xstart, xend = 0, 180
    ystart, yend = -45, 45

    x_src = np.linspace(xstart, xend, nx+1)
    y_src = np.linspace(ystart, yend, ny+1)
    x_src, y_src = np.meshgrid(x_src, y_src)

    x_tgt = np.linspace(xstart, xend, nx*refine+1)
    y_tgt = np.linspace(ystart, yend, ny*refine+1)
    x_tgt, y_tgt = np.meshgrid(x_tgt, y_tgt)
    
    area_src = np.ones((ny, nx), dtype=np.float64)
    area_tgt = np.ones((ny*refine, nx*refine), dtype=np.float64)

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


    for (x, y, area, prefix) in [(x_src, y_src, area_src, "src"), (x_tgt, y_tgt, area_tgt, "tgt")]:
        xr.Dataset(data_vars=dict(x=(["nyp", "nxp"], x),
                                  y=(["nyp", "nxp"], y),
                                  area=(["ny", "nx"], area))
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

    xgrid = fmsgridtools.XGridObj(src_mosaic_file="src_mosaic.nc",
                                  tgt_mosaic_file="tgt_mosaic.nc",
                                  on_gpu=on_gpu,
                                  on_agrid=False
    )
    xgrid.create_xgrid()
    xgrid.write()

    del xgrid
    
    xgrid = fmsgridtools.XGridObj(restart_remap_file="remap.nc")

    #check nxcells
    nxcells = nx * refine * ny * refine
    assert xgrid.nxcells == nxcells

    #check parent input cells
    answer_i = [i+1 for i in range(nx) for ixcells in range(refine*refine)]*ny
    answer_j = [j+1 for j in range(ny) for i in range(nx*refine) for ixcells in range(refine)]

    src_i = [xgrid.src_ij[i][0] for i in range(nxcells)]
    src_j = [xgrid.src_ij[i][1] for i in range(nxcells)]
    
    assert src_i == answer_i
    assert src_j == answer_j

    #check parent output cells
    answer_i = []
    for j in range(ny):
        for i in range(nx):
            answer_i += [refine*i + ixcell + 1 for ixcell in range(refine)]*refine

    answer_j = []
    for j in range(ny):
        for i in range(nx):
            for ixcell in range(refine):
                answer_j += [j*refine + ixcell + 1]*refine
                
    tgt_i = [xgrid.tgt_ij[i][0] for i in range(nxcells)]
    tgt_j = [xgrid.tgt_ij[i][1] for i in range(nxcells)]

    assert tgt_i == answer_i
    assert tgt_j == answer_j

    remove_mosaic()


test_create_xgrid(on_gpu=False)
