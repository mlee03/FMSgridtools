"""
test functionalities in xgridobj
"""

from types import SimpleNamespace

import numpy as np
import pytest

import pyfms
import fmsgridtools

src = SimpleNamespace(
    ntiles=6,
    nx=12,
    ny=24,
    dxy=1,
    mosaicfile="src_mosaic.nc",
    gridfile="src_grid"
)
tgt = SimpleNamespace(
    ntiles=1,
    nx=24,
    ny=48,
    dxy=0.5,
    mosaicfile="tgt_mosaic.nc",
    gridfile="tgt_grid"
)

def get_answer():

    """
    get answer indices
    """

    xtimes = int(src.dxy/tgt.dxy)
    answers = {}
    for j in range(0, src.ny//2):
        answers[j] = {}
        for i in range(0, src.nx//2):
            answers[j][i] = [[2*i+ix, 2*j+jx] for jx in range(xtimes) for ix in range(xtimes)]
    return answers

nxgrid_per_tile = tgt.nx//2 * tgt.ny//2,
nxgrid = tgt.nx//2 * tgt.ny//2 * 6,
remapfile = "test_remap.nc"


def make_testfiles():

    """
    make mosaic and grid files for testing
    """

    # write mosaic
    for parent in [src, tgt]:
        fmsgridtools.MosaicObj(
            gridtiles=[f"tile{i}" for i in range(1, parent.ntiles+1)],
            gridfiles=[f"{parent.gridfile}.tile{i}.nc" for i in range(1, parent.ntiles+1)]
        ).write(parent.mosaicfile)

    # write grid
    for parent in [src, tgt]:
        for itile in range(1, parent.ntiles+1):
            x1 = np.array([i*parent.dxy for i in range(parent.nx+1)], dtype=np.float64)
            y1 = np.array([j*parent.dxy for j in range(parent.ny+1)], dtype=np.float64)
            x, y = np.meshgrid(x1, y1)
            fmsgridtools.GridObj(x=x, y=y).write(parent.gridfile + f".tile{itile}.nc")


@pytest.mark.parametrize("on_gpu", [False, True])
def test_xgridobj(on_gpu: bool):

    """
    tests generating the exchange grid
    tests reading and write exchange grid
    """

    make_testfiles()

    xgrid = fmsgridtools.XGridObj(
        src_mosaicfile=src.mosaicfile,
        tgt_mosaicfile=tgt.mosaicfile,
    )

    xgrid.get_parents()
    xgrid.get_interp()
    xgrid.write(outfile=remapfile)

    del xgrid

    pyfms.horiz_interp.end()

    xgrid = fmsgridtools.XGridObj(
        src_mosaicfile=src.mosaicfile,
        tgt_mosaicfile=tgt.mosaicfile,
        remapfile=remapfile)

    xgrid.get_parents()
    xgrid.read(remapfile=remapfile)

    errmsg = "tile {}: expected {} but got {}"
    area = fmsgridtools.GridObj(gridfile=tgt.gridfile + ".tile1.nc").read(center=True, radians=True).get_fms_area()
    for tile in xgrid.interps:

        interp = xgrid.interps[tile]
        i_src = interp.i_src
        j_src = interp.j_src
        i_dst = interp.i_dst
        j_dst = interp.j_dst

        assert interp.nxgrid == tgt.nx//2 * tgt.ny//2, errmsg.format(tile, tgt.nx//2 * tgt.ny//2, interp.nxgrid)

        answers = get_answer()

        for i in range(interp.nxgrid):
            idst, jdst = i_dst[i], j_dst[i]
            answerlist = answers[j_src[i]][i_src[i]]
            check_indices = [idst, jdst]
            check_area = area[int(jdst), int(idst)]
            np.testing.assert_almost_equal(
                interp.xgrid_area[i],
                check_area,
                decimal=5,
                err_msg=f"gridpoint {i} on tile {tile} ")
            try:
                answerlist.remove(check_indices)
            except ValueError:
                assert False, f"tile {tile}: xpoint {i}, {check} not found in answers {answerlist}, {i_src[i]}, {j_src[i]}"


if __name__ == "__main__":
    test_xgridobj(on_gpu=True)
