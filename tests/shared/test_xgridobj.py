import numpy as np
from types import SimpleNamespace
import pytest
import xarray as xr

import pyfms
import fmsgridtools

src = SimpleNamespace(
    ntiles = 6,
    nx = 12,
    ny = 24,
    dxy = 1,
    mosaicfile = "src_mosaic.nc",
    gridfile = "src_grid"
)
tgt = SimpleNamespace(
    ntiles = 1,
    nx = 24,
    ny = 48,
    dxy = 0.5,
    mosaicfile = "tgt_mosaic.nc",
    gridfile = "tgt_grid"
)

answers = SimpleNamespace(
    nxgrid_per_tile = tgt.nx//2 * tgt.ny//2,
    nxgrid = tgt.nx//2 * tgt.ny//2 * 6,
    remapfile = "test_remap.nc"
)


def make_testfiles(nx: int = 90, ny: int = 45, refine: int = 2):


    # write mosaic
    for parent in [src, tgt]:
        fmsgridtools.MosaicObj(
            gridtiles=[f"tile{i}" for i in range(1, parent.ntiles+1)],
            gridfiles=[f"{parent.gridfile}.tile{i}.nc" for i in range(1, parent.ntiles+1)]
        ).write(outfile=parent.mosaicfile)


    # write grid
    for parent in [src, tgt]:
        for itile in range(1,parent.ntiles+1):
            x1 = np.array([i*parent.dxy for i in range(parent.nx+1)], dtype=np.float64)
            y1 = np.array([j*parent.dxy for j in range(parent.ny+1)], dtype=np.float64)
            x, y = np.meshgrid(x1, y1)
            gridfile = parent.gridfile + f".tile{itile}.nc"
            fmsgridtools.GridObj(x=x, y=y).write(gridfile)


@pytest.mark.parametrize("on_gpu", [False, True])
def test_create_xgrid(on_gpu: bool):

    make_testfiles()

    xgrid = fmsgridtools.XGridObj(
        src_mosaicfile=src.mosaicfile,
        tgt_mosaicfile=tgt.mosaicfile,
    )

    xgrid.get_parents()
    xgrid.get_interp()

    xgrid.write(outfile=xgrid.remapfile)

    del xgrid

    pyfms.horiz_interp.end()

    xgrid = fmsgridtools.XGridObj(
         src_mosaicfile=src.mosaicfile,
         tgt_mosaicfile=tgt.mosaicfile,
         remapfile="test_remap.nc")
    xgrid.get_parents()

    xgrid.read()

    #check nxcells
    for tile in xgrid.interps:
        assert xgrid.interps[tile].nxgrid == answers.nxgrid_per_tile, f"nxgrid for tile {tile} incorrect, got {xgrid.interps[tile].nxgrid}, expected {answers.nxgrid_per_tile}"

    # assert xgrid.nxcells == nxcells

    # #check parent input cells
    # answer_i = [i+1 for i in range(nx) for ixcells in range(refine*refine)]*ny
    # answer_j = [j+1 for j in range(ny) for i in range(nx*refine) for ixcells in range(refine)]

    # src_i = [xgrid.src_cell[i][0] for i in range(nxcells)]
    # src_j = [xgrid.src_cell[i][1] for i in range(nxcells)]

    # assert src_i == answer_i
    # assert src_j == answer_j

    # #check parent output cells
    # answer_i = []
    # for j in range(ny):
    #     for i in range(nx):
    #         answer_i += [refine*i + ixcell + 1 for ixcell in range(refine)]*refine

    # answer_j = []
    # for j in range(ny):
    #     for i in range(nx):
    #         for ixcell in range(refine):
    #             answer_j += [j*refine + ixcell + 1]*refine

    # tgt_i = [xgrid.tgt_cell[i][0] for i in range(nxcells)]
    # tgt_j = [xgrid.tgt_cell[i][1] for i in range(nxcells)]

    # assert tgt_i == answer_i
    # assert tgt_j == answer_j

    # remove_mosaic()


if __name__ == "__main__":
    test_create_xgrid(on_gpu=False)

